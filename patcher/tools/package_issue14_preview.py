"""Package a v1.0.6 issue #14 data hotfix from checked official releases.

Copies v1.0.5 installer executables unchanged; updates only the two
TranslationData ZIP members already independently audited in the one-GMST
candidate. Does not publish, mutate existing releases, or touch game files.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import shutil
import zipfile
from pathlib import Path

CATALOG="TranslationData/catalog.json"
VERSION="v1.0.6"


def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def digest_file(path: Path) -> str:
    d=hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b""):
            d.update(chunk)
    return d.hexdigest()


def members(archive: zipfile.ZipFile) -> dict[str, zipfile.ZipInfo]:
    result={}
    normalized=set()
    for member in archive.infolist():
        name=member.filename
        if (not name or name.startswith("/") or "\\" in name or ":" in name
                or ".." in Path(name).parts or not name.startswith((
                  "TranslationData/", "Licenses-and-Source/",
                  "_internal/", "worker-runtime/", "Backend/"))
                and "/" in name and not member.is_dir()):
            raise ValueError("Unsafe member name: "+name)
        fold=name.casefold()
        if fold in normalized:raise ValueError("Case-fold duplicate in ZIP: "+name)
        normalized.add(fold)
        if not member.is_dir():result[name]=member
    return result


def load(archive: zipfile.ZipFile) -> tuple[dict, str]:
    catalog=json.loads(archive.read(CATALOG))
    if (catalog.get("schema_version")!=1 or
            catalog.get("target_modlist")!="nuclear-sunset-ttw"):
        raise ValueError("Unexpected TranslationData schema/target")
    specs=[x for m in catalog.get("runtime_mods",[])
           if m.get("mod")=="Nuclear Sunset - Korean UI Strings"
           for x in m.get("files",[])
           if x.get("path","").casefold()=="nskr ui strings.esp"]
    if len(specs)!=1:raise ValueError("Expected one UI Strings payload")
    entry=specs[0]
    name="TranslationData/"+entry["payload"]
    if digest_bytes(archive.read(name))!=entry["payload_sha256"]:
        raise ValueError("Catalog SHA mismatch for UI Strings ESP")
    return catalog,name


def assert_diff_only(source: zipfile.ZipFile, other: zipfile.ZipFile,
                     expected: set[str]) -> None:
    a,b=members(source),members(other)
    if a.keys()!=b.keys():raise ValueError("Unrelated ZIP members added/removed")
    changes={key for key in a if source.read(key)!=other.read(key)}
    if changes!=expected:
        raise ValueError(f"Unexpected member changes: {sorted(changes)}")


def build(installer_zip: Path, data_zip: Path, candidate_zip: Path,
          output: Path) -> dict:
    if output.exists():raise FileExistsError(output)
    if (installer_zip.name!="NuclearSunset-Korean-Patcher-v1.0.5.zip"
            or data_zip.name!="NuclearSunset-TranslationData-v1.0.5.zip"
            or candidate_zip.name!="NuclearSunset-TranslationData-v1.0.5-issue14-CANDIDATE.zip"):
        raise ValueError("Unexpected source archive filenames")
    with (zipfile.ZipFile(installer_zip) as original,
          zipfile.ZipFile(data_zip) as data,
          zipfile.ZipFile(candidate_zip) as candidate):
        old_catalog,old_esp=load(data)
        new_catalog,new_esp=load(candidate)
        original_catalog,original_esp=load(original)
        if (old_esp!=new_esp or original_esp!=old_esp or
                original_catalog!=old_catalog or
                original.read(old_esp)!=data.read(old_esp)):
            raise ValueError("Official executable and TranslationData mismatch")
        if old_catalog.get("version")!="1.0.5" or new_catalog.get("version")!="1.0.5":
            raise ValueError("Only v1.0.5-internal compatibility is supported")
        changes={CATALOG,old_esp}
        assert_diff_only(data,candidate,changes)
        original_files=members(original)
        source_files=members(data)
        if not source_files.keys() <= original_files.keys():
            raise ValueError("Missing TranslationData in original installer")
        for name in source_files:
            if original.read(name)!=data.read(name):
                raise ValueError("Installer and standalone TranslationData differ: "+name)
        output.mkdir(parents=True)
        new_installer=output/f"NuclearSunset-Korean-Patcher-{VERSION}.zip"
        new_data=output/f"NuclearSunset-TranslationData-{VERSION}.zip"
        with zipfile.ZipFile(new_installer,"x") as patched:
            for member in original.infolist():
                name=member.filename
                payload=(candidate.read(name) if name in changes else
                         original.read(name))
                patched.writestr(copy.copy(member),payload)
        shutil.copyfile(candidate_zip,new_data)
    # Fully verify both generated ZIPs against originals; keep all binary
    # executables, license/source files and unrelated output unchanged.
    with (zipfile.ZipFile(installer_zip) as original,
          zipfile.ZipFile(new_installer) as changed,
          zipfile.ZipFile(new_data) as standalone):
        assert_diff_only(original,changed,changes)
        cat,esp=load(changed)
        standalone_cat,standalone_esp=load(standalone)
        if cat!=standalone_cat or esp!=standalone_esp:
            raise ValueError("Full package and standalone catalog mismatch")
        for name in members(standalone):
            if changed.read(name)!=standalone.read(name):
                raise ValueError("Full package / standalone payload differs: "+name)
        needed=["NuclearSunsetKoreanPatcher.exe","NSKRXEditWorker.exe",
                "_internal/_bz2.pyd","worker-runtime/_bz2.pyd",
                "Backend/XEditLib.dll"]
        missing=[name for name in needed if name not in members(changed)]
        if missing:raise ValueError("Missing required installer binary: "+repr(missing))
        if (cat.get("version"),cat.get("packaging"))!=("1.0.5","folder"):
            raise ValueError("Unsupported internal folder catalog")
        if changed.testzip() is not None or standalone.testzip() is not None:
            raise ValueError("Archive CRC failure")
    checksums=(f"{digest_file(p)}  {p.name}\n" for p in (new_installer,new_data))
    (output/"SHA256SUMS.txt").write_text("".join(checksums),encoding="ascii")
    result=dict(status="OFFICIAL_RELEASE_GAMEPLAY_VERIFICATION_NEEDED",release_tag=VERSION,
                internal_installer_version="v1.0.5",
                changed_zip_members=sorted(changes),
                installer_sha256=digest_file(new_installer),
                data_sha256=digest_file(new_data),
                installer_bytes=new_installer.stat().st_size,
                data_bytes=new_data.stat().st_size)
    (output/"BUILD-MANIFEST.json").write_text(
        json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return result


def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--installer",type=Path,required=True)
    ap.add_argument("--translation-data",type=Path,required=True)
    ap.add_argument("--candidate",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args(argv)
    build(args.installer,args.translation_data,args.candidate,args.output)
    return 0

if __name__=="__main__":
    raise SystemExit(main())
