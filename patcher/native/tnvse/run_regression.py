"""Build Win32 tests from the actual patched conversion and composition functions."""
import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SRC=ROOT/'Src'
OUT=ROOT/'tests';OUT.mkdir(exist_ok=True)

def extract(path,signature):
    text=path.read_text(encoding='utf-8-sig');start=text.index(signature);brace=text.index('{',start);depth=0
    for i in range(brace,len(text)):
        if text[i]=='{':depth+=1
        elif text[i]=='}':
            depth-=1
            if depth==0:return text[start:i+1]
    raise ValueError(signature)
def literal(text,encoding='utf-8'):
    raw=text.encode(encoding) if isinstance(text,str) else text
    return 'std::string("'+''.join(chr(92)+'x%02x'%b for b in raw)+'",'+str(len(raw))+')'

signatures={
 'font/encoding.cpp':['bool IsValidUTF8With3ByteMin(', 'void TraceEncodingConversionFailure(',
    'bool TryUTF8ToMultiByteStr(', 'std::string UTF8ToMultiByteStr('],
 'font/encoding.h':['inline bool ShouldConvertUTF8(', 'inline bool ConvertToMultiByte('],
 'font/text_hooks.cpp':['std::string GetDoorStructuralParticle(', 'const char* SafeCString(',
    'std::string NormalizeDoorUiPiece(', 'const char* TranslateDoorPiece(',
    'const char* TranslateDoorToPiece(', 'std::string BuildDoorPromptCHS(',
    'std::string BuildDoorPromptKOR('],
 'dictionary/dictionary_translate.cpp':['bool TryTranslateEngineLockPrefix(']}
functions=[extract(SRC/path,signature) for path,names in signatures.items() for signature in names]
fixtures={
 'sentence':'화술: 감옥도 그렇게 나쁘진 않아.', 'cell':'굿스프링스', 'door':'문', 'to':'로 ',
 'particle':'의', 'emoji':'한글😀', 'greek':'α', 'punctuation':'한글\u00a0설명',
 'utf8_actor_cp949_message':'베로니카',
}
constants='\n'.join('const std::string '+key+'='+literal(value)+';\nconst std::string '+key+'_cp='+
    literal(value,'cp949')+';' for key,value in fixtures.items() if key not in ('emoji','punctuation'))
constants+='\nconst std::string emoji='+literal(fixtures['emoji'])+';'
constants+='\nconst std::string punctuation='+literal(fixtures['punctuation'])+';'
head=r'''#define NOMINMAX
#include <windows.h>
#include <string>
#include <string_view>
#include <atomic>
#include <limits>
#include <iostream>
#include <vector>
#include <fstream>
#include <cstdint>
#include <cstring>
using UInt8=std::uint8_t;using UInt32=std::uint32_t;
bool g_bEnableUTF8=true;
UInt32 g_usingWinEncoding=949;
bool IsEastAsianUiMode(){return true;}
unsigned logCount=0;
struct FakeLog{template<typename... Args>void FormattedMessage(const char*,Args...){++logCount;}}gLog;
std::string g_sOptionalStructuralParticle;
bool TranslateText(const char* source,std::string& result);
bool TryTranslateExactText(const std::string& source,std::string& result,int depth);
bool exactAvailable=true;
'''
main=r'''
unsigned tests=0,failures=0;
void check(bool value,const char* name){
  ++tests;if(!value){++failures;std::cout<<"FAIL "<<name<<'\n';}
}
bool TranslateText(const char* source,std::string& result){
  if(std::string(source)=="Door"){result=door_cp;return true;}
  if(std::string(source)=="Cell"){result=cell;return true;}
  return false;
}
bool TryTranslateExactText(const std::string& source,std::string& result,int){
  if(!exactAvailable||source!="This lock cannot be picked. It requires a key to open.")return false;
  result=__LOCK_CP949__;return true;
}
int main(int argc,char**){
  const bool withParticle=argc>1;
  if(withParticle)g_sOptionalStructuralParticle=particle;
  check(IsValidUTF8With3ByteMin(sentence.c_str()),"valid Korean UTF8");
  check(!IsValidUTF8With3ByteMin(sentence_cp.c_str()),"CP949 not misclassified fixture");
  check(!IsValidUTF8With3ByteMin("ASCII"),"ASCII legacy behavior");
  check(!IsValidUTF8With3ByteMin(nullptr),"null pointer");
  check(!IsValidUTF8With3ByteMin(greek.c_str()),"two-byte legacy heuristic");
  const std::vector<std::string> invalid={
    std::string("\xe0\x80\x80",3),std::string("\xed\xa0\x80",3),
    std::string("\xf4\x90\x80\x80",4),std::string("\xc0\xaf",2),
    std::string("\xf5\x80\x80\x80",4),std::string("\xe3\x80",2),
    std::string("\xf0\x90\x80",3),std::string("\x80",1)};
  for(auto& value:invalid){
    check(!IsValidUTF8With3ByteMin(value.c_str()),"invalid UTF8 gate");
    std::string result="unchanged";
    check(!TryUTF8ToMultiByteStr(value,949,result)&&result=="unchanged","invalid conversion no mutation");
    check(UTF8ToMultiByteStr(value,949)==value,"invalid wrapper preserves bytes");
  }
  std::string converted="sentinel";
  check(TryUTF8ToMultiByteStr(sentence,949,converted)&&converted==sentence_cp,"lossless Korean conversion");
  check(TryUTF8ToMultiByteStr(greek,949,converted)&&converted==greek_cp,"explicit two-byte UTF8");
  converted="sentinel";
  check(!TryUTF8ToMultiByteStr(emoji,949,converted)&&converted=="sentinel","unrepresentable preserves destination");
  check(UTF8ToMultiByteStr(emoji,949)==emoji,"unrepresentable wrapper preserves input");
  converted="sentinel";
  check(!TryUTF8ToMultiByteStr(punctuation,949,converted)&&converted=="sentinel","best-fit disabled");
  check(TryUTF8ToMultiByteStr(__EMDASH_UTF8__,949,converted)&&converted==__BAR_CP949__,"reviewed dash alias");
  check(UTF8ToMultiByteStr(__EMDASH_UTF8__,949)==__BAR_CP949__,"dash alias wrapper");
  check(TryUTF8ToMultiByteStr(emoji,CP_UTF8,converted)&&converted==emoji,"UTF8 output Unicode roundtrip");
  std::string src=sentence,storage;
  const char* pointer=src.c_str();
  check(ConvertToMultiByte(pointer,storage,true)&&std::string(pointer)==sentence_cp,"UI conversion");
  check(src==sentence,"input is immutable in helper");
  pointer=sentence_cp.c_str();
  check(!ConvertToMultiByte(pointer,storage,true)&&pointer==sentence_cp.c_str(),"already CP949 unchanged");
  pointer=sentence.c_str();
  check(!ConvertToMultiByte(pointer,storage,false)&&pointer==sentence.c_str(),"font gate");
  pointer=emoji.c_str();storage="sentinel";
  check(!ConvertToMultiByte(pointer,storage,true)&&pointer==emoji.c_str()&&storage=="sentinel","no pointer switch on loss");
  const std::string extraParticle=withParticle?particle_cp:std::string();
  const std::string expectedKOR=cell_cp+to_cp+extraParticle+door_cp;
  const std::string expectedCHS=to_cp+cell_cp+extraParticle+door_cp;
  const std::string expectedDictionary=withParticle?cell_cp+particle_cp+door_cp:expectedKOR;
  check(BuildDoorPromptKOR(door.c_str(),to_cp.c_str(),cell.c_str(),false)==expectedKOR,"KOR mixed pieces");
  check(BuildDoorPromptKOR(door_cp.c_str(),to.c_str(),cell_cp.c_str(),false)==expectedKOR,"KOR inverse mixed pieces");
  check(BuildDoorPromptKOR(door.c_str(),to.c_str(),cell.c_str(),false)==expectedKOR,"KOR all UTF8");
  check(BuildDoorPromptKOR(door_cp.c_str(),to_cp.c_str(),cell_cp.c_str(),false)==expectedKOR,"KOR all CP949");
  check(BuildDoorPromptCHS(door.c_str(),to_cp.c_str(),cell.c_str(),false)==expectedCHS,"CHS mixed pieces");
  check(BuildDoorPromptKOR("Door",to.c_str(),"Cell",true)==expectedDictionary,"dictionary returns different encodings");
  check(BuildDoorPromptKOR(nullptr,nullptr,nullptr,false)==(withParticle?particle_cp:std::string()),"null pieces");
  check(src==sentence&&cell==__CELL_UTF8__&&door==__DOOR_UTF8__,"source pieces unmodified");
  if(!withParticle){
    g_bEnableUTF8=false;
    check(BuildDoorPromptKOR(door.c_str(),to.c_str(),cell.c_str(),false)==cell+to+door,"UTF8 disabled preserves inputs");
    pointer=sentence.c_str();
    check(!ConvertToMultiByte(pointer,storage,true),"UTF8 disabled helper");
    g_bEnableUTF8=true;
  }
  // Place truncated strings immediately before an inaccessible page.
  SYSTEM_INFO info{};GetSystemInfo(&info);
  char* memory=static_cast<char*>(VirtualAlloc(nullptr,info.dwPageSize*2,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE));
  check(memory!=nullptr,"guard-page allocation");
  if(memory){
    DWORD oldProtect=0;
    const bool protectedPage=VirtualProtect(memory+info.dwPageSize,info.dwPageSize,PAGE_NOACCESS,&oldProtect)!=0;
    check(protectedPage,"guard-page protection");
    if(protectedPage)for(auto& value:invalid){
      char* input=memory+info.dwPageSize-value.size()-1;
      std::memcpy(input,value.data(),value.size());input[value.size()]=0;
      check(!IsValidUTF8With3ByteMin(input),"truncated gate no overread");
    }
    VirtualFree(memory,0,MEM_RELEASE);
  }
  for(int i=0;i<20;++i){std::string out;TryUTF8ToMultiByteStr(emoji,949,out);}
  check(logCount==8,"bounded diagnostics");
  const std::string engine="This lock cannot be picked. It requires a key to open.";
  const std::string lockHead=__LOCK_CP949__;
  std::string message;
  check(TryTranslateEngineLockPrefix(engine.c_str(),message)&&message==lockHead,"engine sentence alone");
  check(TryTranslateEngineLockPrefix((engine+" "+cell).c_str(),message)&&message==lockHead+" "+cell_cp,"engine UTF8 key suffix");
  check(TryTranslateEngineLockPrefix((engine+" "+cell_cp).c_str(),message)&&message==lockHead+" "+cell_cp,"engine CP949 key suffix");
  check(TryTranslateEngineLockPrefix((engine+"\n"+cell).c_str(),message)&&message==lockHead+"\n"+cell_cp,"engine suffix separators");
  check(!TryTranslateEngineLockPrefix((engine+"not a suffix").c_str(),message),"engine prefix boundary");
  check(!TryTranslateEngineLockPrefix("Other engine text",message),"unrelated engine text");
  exactAvailable=false;message="sentinel";
  check(!TryTranslateEngineLockPrefix(engine.c_str(),message)&&message=="sentinel","missing exact entry preserves text");
  exactAvailable=true;
  if(!withParticle){
    std::ifstream input("dictionary-targets.bin",std::ios::binary);
    check(input.good(),"active dictionary fixture available");
    unsigned checked=0,rejected=0;std::uint32_t bytes=0;
    while(input.read(reinterpret_cast<char*>(&bytes),sizeof(bytes))){
      std::string text(bytes,'\0');
      if(!input.read(text.data(),bytes)){++rejected;break;}
      std::string result;
      if(!TryUTF8ToMultiByteStr(text,949,result))++rejected;
      ++checked;
    }
    check(checked>0&&rejected==0,"all active dictionary targets representable");
    std::cout<<"DICTIONARY checked="<<checked<<" rejected="<<rejected<<'\n';
  }
  std::cout<<"RESULT tests="<<tests<<" failures="<<failures<<" particle="<<withParticle<<'\n';
  return failures?1:0;
}
'''
main=main.replace('__CELL_UTF8__',literal(fixtures['cell'])).replace('__DOOR_UTF8__',literal(fixtures['door']))
main=main.replace('__EMDASH_UTF8__',literal('한글—설명')).replace('__BAR_CP949__',literal('한글―설명','cp949'))
main=main.replace('__LOCK_CP949__',literal('열쇠가 있어야 열 수 있습니다.','cp949'))
dictionary=Path(r'C:\Modlists\NuclearSunset\mods\Nuclear Sunset - Korean UI Runtime Translations\NVSE\plugins\NSKR_UI_Translations.json')
import struct
if len(sys.argv)>1:dictionary=Path(sys.argv[1])
data=json.loads(dictionary.read_text(encoding='utf-8-sig'))
with (OUT/'dictionary-targets.bin').open('wb') as stream:
    for row in data:
        if isinstance(row.get('translation'),str):
            raw=row['translation'].encode('utf-8')
            stream.write(struct.pack('<I',len(raw))+raw)
(OUT/'regression.cpp').write_text(head+'\n\n'.join(functions)+'\n'+constants+'\n'+main,encoding='utf-8')
vswhere=Path(r'C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe')
vs=subprocess.check_output([str(vswhere),'-latest','-products','*','-requires','Microsoft.VisualStudio.Component.VC.Tools.x86.x64','-property','installationPath'],text=True).strip()
batch='@echo off\ncall "'+str(Path(vs)/'VC/Auxiliary/Build/vcvars32.bat')+'" >nul\nif errorlevel 1 exit /b 1\ncl /nologo /std:c++17 /EHsc /utf-8 regression.cpp /Fe:regression.exe\n'
(OUT/'build-tests.cmd').write_text(batch,encoding='ascii')
build=subprocess.run(['cmd.exe','/d','/c','build-tests.cmd'],cwd=OUT,capture_output=True,text=True)
(OUT/'build.log').write_text(build.stdout+build.stderr,encoding='utf-8')
if build.returncode:raise RuntimeError(build.stdout+build.stderr)
results=[]
for args in ([],['--particle']):
    run=subprocess.run([str(OUT/'regression.exe'),*args],cwd=OUT,capture_output=True,text=True)
    results.append({'arguments':args,'exit_code':run.returncode,'output':run.stdout+run.stderr})
(OUT/'results.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
for row in results:print(row['output'])
if any(row['exit_code'] for row in results):raise RuntimeError('Win32 regression failed')
