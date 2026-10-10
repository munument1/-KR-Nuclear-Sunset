"use strict";
/**
 * Nuclear Sunset Korean MCM/Translations draft generator (unreleased).
 * Builds detached candidate files from literal seed translations; does not
 * modify installed MO2 or source files or translate technical keys.
 *
 * node tools/build_mcm_ini_review_output.js --workspace "D:\...\미번역_번역작업_20261010" --output "D:\...\MCM_DRAFT_OUT"
 * Reads seed JSON from patcher/.local. They remain local and never ship via Git.
 */
const fs=require("fs"),path=require("path"),crypto=require("crypto");
const argv=process.argv;
function arg(name){const i=argv.indexOf(name);return i>=0?argv[i+1]:undefined}
function check(ok,message){if(!ok)throw Error(message)}
const repo=path.resolve(__dirname,"..");
const ws=arg("--workspace"),out=arg("--output");
check(ws&&out,"Specify --workspace and --output");
const root=path.resolve(ws),output=path.resolve(out);
check(fs.existsSync(root)&&!fs.existsSync(output),"Workspace missing or output already exists");
const seeds=[
 "mcm_ini_translation_seed_20261010.json",
 "mcm_npcdodge_translation_seed_20261010.json",
 "mcm_five_mods_translation_seed_20261010.json"
];
const skey=x=>[x.file.toLowerCase(),x.source,x.ini_key||""].join("\0");
const dict=new Map(),seen=new Map();
for(const seed of seeds){
 const full=path.join(repo,".local",seed);
 const data=JSON.parse(fs.readFileSync(full,"utf8"));
 check(data.release_ready!==true&&data.translation_ready!==true,"Unsafe seed state");
 for(const seedRow of data.entries){
   const row={...seedRow,file:seedRow.file||data.source_file};
   check(typeof row.file==="string"&&row.file.length>0,"Missing MCM file in seed");
   const k=skey(row);
   if(dict.has(k)&&dict.get(k).dest!==row.dest)throw Error("Conflicting translation "+k);
   check(typeof row.source==="string"&&typeof row.dest==="string"&&row.source!==row.dest,
         "Invalid or unchanged draft "+k);
   dict.set(k,row);seen.set(k,0);
 }
}
function protect(s){
 return (s.match(/%%|%[-+# 0-9.]*[A-Za-z]|\{[^{}\r\n]+\}|<[^<>\r\n]+>|&[A-Za-z0-9]+;|#\d+\|/g)||[]).sort();
}
function safe(original,translated){
 check(translated&&!/[\r\n]/.test(translated),"Multiline translation forbidden");
 check(JSON.stringify(protect(original))===JSON.stringify(protect(translated)),
       "Protected token changed: "+original.slice(0,80));
}
function sourcePath(file){
 check(file.startsWith("MCM/")||file.startsWith("config/"),"Bad virtual path "+file);
 check(!file.includes("..")&&!file.includes("\\")&&file.split("/").every(x=>x&&!/[<>:"|?*\x00-\x1f]/.test(x)),
       "Unsafe path "+file);
 const first=file.startsWith("MCM/Translations/")?"06_Translations_INI/":
             file.startsWith("config/")?"06_Translations_INI/":"05_MCM_JSON/";
 return path.join(root,...(first+file).split("/"));
}
function readFile(f){const b=fs.readFileSync(f);let enc="utf8";
 if(b[0]===0xff&&b[1]===0xfe)enc="utf16le-bom";
 else if(b[0]===0xef&&b[1]===0xbb&&b[2]===0xbf)enc="utf8-bom";
 else check(!(b[0]===0xfe&&b[1]===0xff),"UTF-16BE unsupported");
 const raw=enc==="utf16le-bom"?b.subarray(2).toString("utf16le"):b.toString("utf8").replace(/^\uFEFF/,"");
 return {raw,enc,before:crypto.createHash("sha256").update(b).digest("hex")};
}
function bytes(s,enc){
 if(enc==="utf16le-bom")return Buffer.concat([Buffer.from([0xff,0xfe]),Buffer.from(s,"utf16le")]);
 if(enc==="utf8-bom")return Buffer.concat([Buffer.from([0xef,0xbb,0xbf]),Buffer.from(s,"utf8")]);
 return Buffer.from(s,"utf8");
}
function modifyJson(obj,file){
 let changed=0;
 const display=new Set(["displayName","description","listTitle","pageTitle","title","mouse","strings","suffix"]);
 function walk(v,key){
  if(Array.isArray(v))return v.map(x=>walk(x,key));
  if(v&&typeof v==="object")return Object.fromEntries(Object.entries(v).map(([k,x])=>[k,walk(x,k)]));
  if(typeof v==="string"&&display.has(key)&&!v.startsWith("$")){
   const k=skey({file,source:v});
   if(dict.has(k)){const entry=dict.get(k);safe(v,entry.dest);seen.set(k,seen.get(k)+1);changed++;return entry.dest}
  }
  return v;
 }
 return {obj:walk(obj,""),changed};
}
function modifyIni(raw,file){
 let changed=0,section="";
 const lines=raw.split(/(?<=\r\n|\n)/);
 for(let i=0;i<lines.length;i++){
  const text=lines[i],newline=text.endsWith("\r\n")?"\r\n":text.endsWith("\n")?"\n":"";
  const body=newline?text.slice(0,-newline.length):text;
  const v=body.trim();
  if(v.startsWith("[")&&v.endsWith("]"))section=v;
  if(!v||/^[#;\[]/.test(v)||!body.includes("="))continue;
  const eq=body.indexOf("="),lhs=body.slice(0,eq),rhs=body.slice(eq+1),name=lhs.trim();
  const value=rhs.trim(),quoted=value.length>=2&&value.startsWith('"')&&value.endsWith('"');
  const source=quoted?value.slice(1,-1):value;
  const k=skey({file,source,ini_key:name});
  if(!dict.has(k))continue;
  const item=dict.get(k);
  check(!item.section||item.section===section,"INI section mismatch "+file+" "+name);
  safe(source,item.dest);
  const leading=rhs.slice(0,rhs.length-rhs.trimStart().length);
  const trailing=rhs.slice(rhs.trimEnd().length);
  lines[i]=lhs+"="+leading+(quoted?JSON.stringify(item.dest):item.dest)+trailing+newline;
  seen.set(k,seen.get(k)+1);changed++;
 }
 return {raw:lines.join(""),changed};
}
const files=[...new Set([...dict.values()].map(x=>x.file))].sort(),results=[],pendingWrites=[];
for(const file of files){
 const src=sourcePath(file),original=readFile(src);
 let updated,changed;
 if(file.endsWith(".json")){
  const obj=JSON.parse(original.raw);
  const result=modifyJson(obj,file);
  updated=JSON.stringify(result.obj,null,2)+"\n";changed=result.changed;
  check(JSON.stringify(Object.keys(result.obj))===JSON.stringify(Object.keys(obj)),
        "JSON top-level keys changed");
 }else{
  const result=modifyIni(original.raw,file);
  updated=result.raw;changed=result.changed;
  check(updated.split(/\r?\n/).length===original.raw.split(/\r?\n/).length,
        "INI line count changed");
 }
 check(changed>0,"No translated content in "+file);
 const dest=path.join(output,...file.split("/"));
 pendingWrites.push({dest,buffer:bytes(updated,original.enc)});
 results.push({file,changed,source_sha256:original.before,original_unchanged:true,
    candidate_sha256:crypto.createHash("sha256").update(bytes(updated,original.enc)).digest("hex")});
}
const missing=[...seen].filter(([k,num])=>num===0).map(([k])=>k);
check(!missing.length,"Unmatched draft entries: "+JSON.stringify(missing.slice(0,15)));
fs.mkdirSync(output,{recursive:false});
for(const item of pendingWrites){
 fs.mkdirSync(path.dirname(item.dest),{recursive:true});
 fs.writeFileSync(item.dest,item.buffer);
}
const report={type:"unreleased_mcm_and_ini_translation_draft",translation_ready:false,
  applied_to_game:false,review_required:true,source_files:files.length,
  translated_occurrences:results.reduce((a,b)=>a+b.changed,0),
  translated_unique_source_keys:dict.size,files:results,
  limitations:"Not verified in game; catalog integration and untouched source identity must be rechecked."};
fs.writeFileSync(path.join(output,"00_REVIEW_STATUS.json"),JSON.stringify(report,null,2)+"\n");
console.log(JSON.stringify({files:files.length,translated:report.translated_occurrences,
  unique:dict.size,output,release_ready:false}));
