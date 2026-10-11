// Preserve the original Docusaurus site while changing Korean-facing metadata.
const fs = require('fs');
const path = require('path');
const root = path.resolve(process.argv[2] || 'upstream');
function patch(file, operations) {
  const target = path.join(root,file);
  let content = fs.readFileSync(target,'utf8');
  for(const [before,after] of operations){
    if(!content.includes(before)) throw new Error('Upstream changed: '+file+' / '+before);
    content = content.replace(before,after);
  }
  fs.writeFileSync(target,content,'utf8');
}
patch('docusaurus.config.js',[
  ["title: 'Nuclear Sunset'", "title: 'Nuclear Sunset 한국어판'"],
  ["tagline: 'A Hardcore TTW Modlist'", "tagline: '하드코어 TTW 모드 목록 · 비공식 한국어 번역'"],
  ["url: 'https://nuclearsunset.com'", "url: 'https://munument1.github.io'"],
  ["baseUrl: '/'", "baseUrl: '/-KR-Nuclear-Sunset/'"],
  ["organizationName: 'anonymoussynon'", "organizationName: 'munument1'"],
  ["projectName: 'Nuclear-Sunset'", "projectName: '-KR-Nuclear-Sunset'"],
  ["defaultLocale: 'en'", "defaultLocale: 'ko'"],
  ["locales: ['en']", "locales: ['ko']"],
  ['https://github.com/anonymoussynon/Nuclear-Sunset/edit/main/', 'https://github.com/munument1/-KR-Nuclear-Sunset/tree/main/translations/'],
  ['https://github.com/anonymoussynon/Nuclear-Sunset/tree/main/', 'https://github.com/munument1/-KR-Nuclear-Sunset/'],
  ["label: 'Setup'", "label: '설치 안내'"],
  ['label: "FAQ"', 'label: "자주 묻는 질문"'],
  ['label: "Gallery"', 'label: "갤러리"'],
  ['label: "Changelog"', 'label: "변경 이력"'],
  ['label: "Resources"', 'label: "자료실"'],
  ['label: "Donate"', 'label: "원작자 후원"'],
  ['label: "Help"', 'label: "지원"'],
  ["title: 'Community'", "title: '커뮤니티'"],
]);
let configFile=path.join(root,'docusaurus.config.js');
let config=fs.readFileSync(configFile,'utf8');
config=config.replace(/copyright: `Copyright © \$\{new Date\(\)\.getFullYear\(\)\} Nuclear Sunset Team`,/,"copyright: '비공식 한국어 번역 · 원작 Nuclear Sunset Team · 번역 및 운영 munument1',");
fs.writeFileSync(configFile,config,'utf8');
patch('src/pages/index.js',[
  ['Click Here to Learn About Nuclear Sunset','뉴클리어 선셋 소개 및 설치 안내'],
  ['description="A Hardcore TTW Modlist"','description="Nuclear Sunset 하드코어 TTW 모드 목록 비공식 한국어 번역"']
]);
patch('sidebars.js',[
  ["'main/setup',", "'main/setup',\n    'main/korean-patch',"],
]);
const srcDocs=path.join(root,'docs');
const translatedDocs=path.join(process.cwd(),'korean','translations','docs');
function visit(folder){
 for(const entry of fs.readdirSync(folder,{withFileTypes:true})){
  const file=path.join(folder,entry.name);
  if(entry.isDirectory())visit(file);
  else if(/\.mdx?$/.test(file)){
   const rel=path.relative(srcDocs,file);
   if(fs.existsSync(path.join(translatedDocs,rel))){
    const c=fs.readFileSync(file,'utf8').replaceAll('https://nuclearsunset.com/docs/','https://munument1.github.io/-KR-Nuclear-Sunset/docs/');
    fs.writeFileSync(file,c,'utf8');
   }
  }
 }
}
visit(srcDocs);
for(const name of ['CNAME','static/CNAME']){const f=path.join(root,name);if(fs.existsSync(f))fs.unlinkSync(f);}
console.log('Korean Nuclear Sunset configured.');
