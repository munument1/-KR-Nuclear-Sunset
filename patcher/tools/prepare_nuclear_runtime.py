"""Stage user-provided TTW UI/radio ESP and the open-source caption runtime."""
import argparse
import json
from pathlib import Path
import shutil
import struct
import sys
import zlib

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import nskr
from tools.tes4_text_scan import masters, subrecords


def write_ui_gmst_plugin(source, target):
    """Keep only string GMST records; never copy radio INFO/scripts/references."""
    data = source.read_bytes()
    if data[:4] != b"TES4":
        raise ValueError("Missing TES4 header")
    header_end = 24 + struct.unpack_from("<I", data, 4)[0]
    header = bytearray(data[:header_end])
    records = []
    group_header = None
    owner_index = len(masters(source))
    next_id = 0x800

    def walk(start, end, depth=0):
        nonlocal group_header, next_id
        if depth > 64:
            raise ValueError("Excessive plugin group nesting")
        pos = start
        while pos < end:
            if end - pos < 24:
                raise ValueError("Truncated record header")
            sig, size = struct.unpack_from("<4sI", data, pos)
            if sig == b"GRUP":
                if size < 24 or pos + size > end:
                    raise ValueError("Invalid group boundary")
                if data[pos + 8:pos + 12] == b"GMST":
                    group_header = bytearray(data[pos:pos + 24])
                walk(pos + 24, pos + size, depth + 1)
                pos += size
                continue
            stop = pos + 24 + size
            if stop > end:
                raise ValueError("Invalid record boundary")
            if sig == b"GMST":
                flags, fid = struct.unpack_from("<II", data, pos + 8)
                body = data[pos + 24:stop]
                if flags & 0x40000:
                    decoded = zlib.decompress(body[4:])
                    if len(decoded) != struct.unpack_from("<I", body)[0]:
                        raise ValueError("Compressed GMST size mismatch")
                    body = decoded
                fields = list(subrecords(body))
                if [x[0] for x in fields] != ["EDID", "DATA"]:
                    raise ValueError("Unexpected GMST data layout")
                edid, text = fields[0][1], fields[1][1]
                if not edid.startswith(b"s") or not edid.endswith(b"\0") or not text.endswith(b"\0"):
                    raise ValueError("Only string GMST records are allowed")
                text[:-1].decode("utf-8")
                if fid >> 24 > owner_index:
                    raise ValueError("GMST record owner exceeds the master list")
                if fid >> 24 == owner_index:
                    next_id = max(next_id, (fid & 0xffffff) + 1)
                records.append(data[pos:stop])
            pos = stop

    walk(header_end, len(data))
    if not records or group_header is None:
        raise ValueError("No string GMST group")
    pos = 24
    found = 0
    while pos < header_end:
        sig, size = struct.unpack_from("<4sH", header, pos)
        pos += 6
        if sig == b"HEDR":
            if size != 12:
                raise ValueError("Invalid HEDR size")
            struct.pack_into("<II", header, pos + 4, len(records) + 1, next_id)
            found += 1
        pos += size
    if found != 1 or pos != header_end:
        raise ValueError("Invalid TES4 subrecord layout")
    struct.pack_into("<I", group_header, 4, 24 + sum(map(len, records)))
    with target.open("xb") as stream:
        stream.write(header)
        stream.write(group_header)
        for record in records:
            stream.write(record)
    return len(records)


def prepare(ttw, radio, installation, output):
    if output.exists():
        raise FileExistsError(output)
    plugin = ttw / "TTW KOR Radio + UI.esp"
    required = masters(plugin)
    if not {x.casefold() for x in required}.issubset(installation.active_keys):
        raise ValueError("TTW UI/radio plugin requires masters absent from the selected profile")
    snapshot = nskr.read_json(radio / "snapshot.json")
    radio_root = radio / "mods" / snapshot["mod"]
    output.mkdir(parents=True)
    clean_plugin = output / "NSKR UI Strings.esp"
    source_hash = nskr.sha256(plugin)
    record_count = write_ui_gmst_plugin(plugin, clean_plugin)
    if nskr.sha256(plugin) != source_hash:
        raise ValueError("Provided TTW UI/radio source changed")
    specs = [
        {"mod": "Nuclear Sunset - Korean UI Strings",
         "review_status": "validated_gmst_only_candidate",
         "plugins": [clean_plugin.name], "required_masters": required,
         "files": [{"path": clean_plugin.name, "source": clean_plugin}]},
        {"mod": "Nuclear Sunset - Radio Captions",
         "review_status": "snapshot_verified_caption_candidate",
         "plugins": [], "required_masters": [],
         "files": [{"path": x["path"], "source": nskr.contained(radio_root, x["path"]),
                    "expected_sha256": x["sha256"]} for x in snapshot["files"]]},
    ]
    for spec in specs:
        for entry in spec["files"]:
            source = entry.pop("source")
            digest = nskr.sha256(source)
            expected = entry.pop("expected_sha256", digest)
            if digest != expected:
                raise ValueError(f"Radio runtime differs from its snapshot: {source}")
            relative = f"runtime/{spec['mod']}/{entry['path']}"
            target = nskr.contained(output, relative)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
            if nskr.sha256(target) != digest or nskr.sha256(source) != digest:
                raise ValueError("Runtime source/copy hash mismatch")
            entry.update(payload=relative, payload_sha256=digest)
    catalog = {"schema_version": 1, "translation_ready": False,
               "game_validation": "not_run", "runtime_mods": specs}
    nskr.write_json(output / "catalog.json", catalog)
    return {"output": str(output), "runtime_mods": len(specs),
            "files": sum(len(x["files"]) for x in specs), "ui_radio_records": record_count,
            "profile_modified": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ttw", type=Path, required=True)
    parser.add_argument("--radio", type=Path, required=True)
    parser.add_argument("--mo2", type=Path, required=True)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(prepare(args.ttw, args.radio, nskr.Installation(args.mo2, args.profile),
                             args.output), ensure_ascii=False))
