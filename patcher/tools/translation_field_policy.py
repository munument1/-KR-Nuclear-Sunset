"""Conservative signature+subrecord exclusion for non-visible FalloutNV metadata.

Never omit ALL text from signatures like INFO, DIAL, BOOK, QUST or TERM.
This file is authoritative for JSON API omission and output QA screening.
"""
from __future__ import annotations
from collections import Counter
from pathlib import Path
import re

NON_DISPLAY_SIGNATURES = {
    "BPTD": "Body-part geometry, gore model names and bone identifiers",
    "MSET": "Music set labels and asset paths",
    "ALOC": "Audio location editor metadata",
}
NON_DISPLAY_SIG_FIELDS = {
    ("INFO","NAM2"): "Dialogue script notes for voice actors, not game dialogue",
    ("INFO","NAM3"): "Dialogue edit notes, not game dialogue",
    ("WRLD","XNAM"): "Water texture asset path",
    ("CELL","XNAM"): "Water texture asset path",
    ("WTHR","CNAM"): "Weather sky texture asset path",
    ("PROJ","NAM1"): "Projectile mesh asset path",
    ("WEAP","NNAM"): "Weapon node identifier",
}
# Known asset-path types that are never player-facing in technical data fields.
ASSET_SUFFIX=re.compile(r"\.(?:dds|nif|kf|hkx|wav|xwm|ogg|mp3|lip|bik|bgsm|bgem|tga|png|xml|fx)(?:\s*)$",re.I)
TECHNICAL_PATH_FIELDS={"XNAM","NAM2","NAM3","NAM4","NAM1","CNAM","NNAM","SNAM"}
def skip_reason(signature:str,field:str,source:str)->str:
    sig=(signature or "").upper()
    fld=(field or "").upper()
    if sig in NON_DISPLAY_SIGNATURES:return NON_DISPLAY_SIGNATURES[sig]
    if (sig,fld) in NON_DISPLAY_SIG_FIELDS:return NON_DISPLAY_SIG_FIELDS[(sig,fld)]
    if fld in TECHNICAL_PATH_FIELDS and ASSET_SUFFIX.search((source or "").strip()):
        # Only physical paths: no dialogue/notes containing plain extension narrative.
        if sig not in {"INFO","DIAL","QUST","NOTE","BOOK","TERM","MESG"}:
            return "Asset/model/audio file path in technical subrecord"
    return ""
def is_translatable(signature:str,field:str,source:str)->bool:
    return not skip_reason(signature,field,source)
if __name__=="__main__":
    assert skip_reason("INFO","NAM2","semi-sarcastic")
    assert skip_reason("WRLD","XNAM",r"Data\Textures\Water\water.dds")
    assert skip_reason("MSET","NAM2","radio.mp3")
    assert skip_reason("BPTD","NAM4","Bip01")
    assert not skip_reason("INFO","NAM1","I'm heading out")
    assert not skip_reason("NOTE","TNAM","Go to the bunker")
    assert not skip_reason("NPC_","FULL","Jack")
    print("RECORD_TRANSLATION_POLICY_SELF_TEST_OK")
