"""Reviewed runtime display overrides; identifiers and name-search patterns stay."""
# old display text, translated display text, compiled/display encoding.
COMPILED={
 ('taleoftwowastelands.esm','DialogueRivetCityScript'):[
  ('Diego Family Door','디에고의 문','utf-8')],
 ('vangraffoverhaul.esm','VGOFScript'):[('Mercenary','용병','utf-8')],
 ('edge ttw.esm','SCPTEDGEOnRestartStuff'):[('Fortified Tunnels','요새 터널','utf-8')],
 ('dmt _dead money tweaks_.esm','SCPTDMTConfigValuesOnRestart'):[("Police Chief's Magnum",'서장의 매그넘','utf-8')],
 ('big town extensions.esm','SCPTBigTownMerchantEnabler'):[("Galina's Little Big Supply",'갈리나 보급소','utf-8')],
 ('tweaksttw.esm','TTTQscript'):[],
 ('tweaksttw.esm','TTTDaveActivateUDF'):[],
 ('harder new vegas strip access.esm','HNVSAMainSCRIPT'):[
  ("I'll submit to the credit check. <", '신용 조회를 받겠어. <','utf-8'),
  ('I want to buy a passport. <','여권을 사겠어. <','utf-8'),
  (' caps required.>',' 캡 필요.>','utf-8')],
 ('brotherhoodleaves.esm','BOSQscript'):[('I convinced the Brotherhood to leave the Mojave.','브라더후드에 철수를 설득했어.','utf-8')],
 ('brotherhoodleaves.esm','BOSDeployQScript'):[('I convinced the Brotherhood to leave the Mojave.','브라더후드에 철수를 설득했어.','utf-8')],
 ('aid addon.esp','SCPTIconChoices'):[('Med-X Syrette','메드-X 주사','cp949')],
 ('ns.esm','TTTGameRestartScript'):[('Prototype Power Armor','시제 파워 아머','utf-8')],
 ('ns.esm','BRWCrossHairEvent'):[('Purchase','구매','utf-8')],
 ('s6s base game perks redux.esp','sssSCPTBaseGamePerksStartup'):[('Extracurricular Knowledge','과외 지식','cp949')],
}
for key in [('tweaksttw.esm','TTTQscript'),('tweaksttw.esm','TTTDaveActivateUDF')]:
 COMPILED[key]=[
  ('Democracy of Rosie Capitol Building','로지 민주국 의사당','utf-8'),
  ("Democracy of Rosie Men's Quarters",'로지 민주국 남성관','utf-8'),
  ("Democracy of Rosie Women's Quarters",'로지 민주국 여성관','utf-8'),
  ('Kingdom of Bob Capitol Building','밥 왕국 의사당','utf-8'),
  ("Kingdom of Bob Men's Quarters",'밥 왕국 남성관','utf-8'),
  ("Kingdom of Bob Women's Quarters",'밥 왕국 여성관','utf-8')]

CCC=[
 ('#0|This lock cannot be picked.','#0|열쇠가 필요합니다.','utf-8'),
 ('#0|This terminal cannot be hacked.','#0|해킹할 수 없습니다.','utf-8'),
 ('#5|Cannot heal/repair hostile targets.','#5|적 치료·수리 불가.','utf-8'),
 ('#0|%n is in another cell and cannot be given commands.','#0|%n: 다른 지역에 있어 명령 불가.','utf-8'),
 ('#0|%n is too far and cannot be given commands.','#0|%n: 너무 멀어 명령 불가.','utf-8'),
 ('#0|%n is unconscious and cannot be given commands.','#0|%n: 의식불명, 명령 불가.','utf-8'),
 ('#0|%n is too far to share items with.','#0|%n: 너무 멀어 거래 불가.','utf-8'),
 ('#0|%n cannot be healed.','#0|%n 치료 불가.','utf-8'),
 ('#0|%n is too far and cannot heal itself.','#0|%n: 멀어서 자가치료 불가.','utf-8'),
 ('#5|Cannot start conversation during combat.','#5|전투 중 대화 불가.','utf-8'),
 ('#5|%n is too far to start conversation with.','#5|%n: 너무 멀어 대화 불가.','utf-8'),
 ('#5|%n does not carry any Bobby Pins.','#5|%n: 머리핀 없음.','utf-8')]
for file in ('jip companions command & control.esp','dsjipcccanims.esp'):
 COMPILED[(file,'JIPCCCUIScript')]=CCC

# provider, virtual path, [(old,new,encoding)]; only display operands on
# name-setting commands are eligible, except the two explicit rank prefixes.
LOOSE=[
 ('[ALT] - Misc Items and Crafting Tweaks','nvse/plugins/scripts/gr_p20MICbooknames.txt',[
  ('Ruined Book, Small Burned','망가진 책(소형, 불탐)','cp949'),
  ('Ruined Book, Small','망가진 책(소형)','cp949'),
  ('Ruined Book, Small Scorched','망가진 책(소형, 그을림)','cp949'),
  ('Ruined Book, Small Destroyed','망가진 책(소형, 파손)','cp949'),
  ('Ruined Book, Large Burned','망가진 책(대형, 불탐)','cp949'),
  ('Ruined Book, Large','망가진 책(대형)','cp949'),
  ('Ruined Book, Large Scorched','망가진 책(대형, 그을림)','cp949'),
  ('Ruined Book, Large Destroyed','망가진 책(대형, 파손)','cp949'),
  ('Pre-War Book, Small Teal','전쟁 전 책(소형, 청록)','cp949'),
  ('Pre-War Book, Small Black','전쟁 전 책(소형, 검정)','cp949'),
  ('Pre-War Book, Small Brown','전쟁 전 책(소형, 갈색)','cp949'),
  ('Pre-War Book, Small Blue','전쟁 전 책(소형, 파랑)','cp949'),
  ('Pre-War Book, Large Teal','전쟁 전 책(대형, 청록)','cp949'),
  ('Pre-War Book, Large Black','전쟁 전 책(대형, 검정)','cp949'),
  ('Pre-War Book, Large Brown','전쟁 전 책(대형, 갈색)','cp949'),
  ('Pre-War Book, Large Blue','전쟁 전 책(대형, 파랑)','cp949')]),
 ('[ALT] - Misc Items and Crafting Tweaks','nvse/plugins/scripts/gr_p20MICrecipeloop.txt',[
  ('Return','뒤로','utf-8'),('Poisons','독','utf-8'),('Darts','다트','utf-8'),('Drinks','음료','utf-8')]),
 ('[ALT] - Misc Items and Crafting Tweaks','nvse/plugins/scripts/gr_p20MICrecipetincan.txt',[('Unbend Tin Can','깡통 펴기','utf-8')]),
 ('TTW Burke House Ownership Transfer','nvse/plugins/scripts/ln_BurkeHouseOwnershipTransfer.txt',[('Vacant House','빈집','utf-8')]),
 ('TTW Burke House Ownership Transfer','nvse/user_defined_functions/BurkeDiedLmao.gek',[('Vacant House','빈집','utf-8')]),
 ('TTW Burke House Ownership Transfer','nvse/user_defined_functions/SimmsToldLmao.gek',[('Vacant House','빈집','utf-8')]),
 ('[MG] - A Smoke Before The Storm - Tweaks','nvse/plugins/scripts/gr_SmokeOnTheStorm.txt',[('Nicotine Withdrawal','니코틴 금단','cp949')]),
 ('[OP] - Fiend Helmet - Revamped Fiend Headgear','nvse/plugins/scripts/gr_FiendHelmetsRenamer.txt',[
  ('Fiendish Battle Headdress','핀드 전투 머리장식','utf-8'),('Fiendish Warrior Helmet','핀드 전사 투구','utf-8'),('Fiendish Hood','핀드 두건','utf-8')]),
 ('TYPE4 (T4) - Compatibility Version','nvse/plugins/scripts/gr_zzz_Type4.txt',[
  ('Sin City Vixen','신 시티의 요부','utf-8'),('Bunny Outfit','토끼 의상','utf-8'),('Peacock Queen','공작 여왕','utf-8')]),
 ('[OP] - Consistent Pip-Boy Icons - Dynamicon','NVSE/plugins/scripts/ln_SinclairsOutfit.txt',[
  ("Sinclair's Outfit",'싱클레어의 의상','utf-8'),("Vera's Outfit",'베라의 의상','utf-8')]),
 ('[#] [INF] - Nuclear Sunset Master Patches','nvse/plugins/Scripts/gr_p20MICingestibleloop.txt',[
  ('%z, Fresh','%z, 신선함','cp949'),('%z, Ice Cold','%z, 차가움','cp949'),('%z, Irradiated','%z, 방사능 오염','cp949')]),
 ('[#] [INF] - Nuclear Sunset Master Patches','nvse/plugins/Scripts/gr_zzzzz_Dark_Armor.txt',[
  ('Legion Recruit Decanus Helmet','군단 신병 데카누스 투구','utf-8'),('Legion Prime Decanus Helmet','군단 정예병 데카누스 투구','utf-8')]),
 ('[#] [INF] - Nuclear Sunset Master Patches','nvse/plugins/Scripts/gr_zzzzz_Dark_Weapons.txt',[
  ('25mm G. APW Holo Sights','25mm 유탄기관총 홀로 조준기','utf-8')]),
 ('Generic NPC Namer','NVSE/user_defined_functions/GenNPC/Namers/GenNPCOutcast.txt',[
  ('Protector ','수호자 ','utf-8'),('Defender ','수비병 ','utf-8')]),
 ('Generic NPC Namer','NVSE/user_defined_functions/GenNPC/Namers/GenNPCTTWAnchorage.txt',[
  ('Specialist ','특기병 ','utf-8'),('Private ','이등병 ','utf-8')]),
]
ENGINE_LOCK=('This lock cannot be picked. It requires a key to open.','열쇠가 있어야 열 수 있습니다.')

# The master copy can supply these setters in profiles without the NS override.
from nskr_compiled_scpt import HEADHUNTER_KO
from nskr_perk_display import REPLACEMENTS as PERK_REPLACEMENTS
from tools.audit_issue11_compiled_scripts import CASES as PERK_CASES
COMPILED[('s6s perks.esp','SCPTPatchForJBT')]=[
 (PERK_CASES[0]['source_en'].replace('Bullet Time','V.A.T.S.'),HEADHUNTER_KO.replace('%','%%'),'cp949'),
 (*PERK_REPLACEMENTS[('ns.esp','SCPTPatchForJBT','sssPerkCoiledSnake')],'cp949')]
