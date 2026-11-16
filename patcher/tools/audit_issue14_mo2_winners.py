"""Read-only selected-profile MO2 provider snapshot for Nuclear Sunset issue #14.

Answers *which physical file would win by MO2 loose-file priority*,
not what a running game process actually loaded. Writes to stdout by default
and never changes the MO2 installation, profiles, game, or saves.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

import nskr

WATCHED = (
    "Menus/levelup_menu.xml",
    "NVSE/plugins/tnvse.dll",
    "NVSE/plugins/tnvse.ini",
    "NVSE/plugins/tnvse_fonts.xml",
    "NVSE/plugins/tnvse_dictionary.xml",
    "NVSE/plugins/scripts/gr_BulletTimePerkDesc.txt",
    "NVSE/plugins/scripts/gr_TagPerkDescriptionSetter.txt",
    "FalloutNV.esm",
    "S6S Perks.esp",
    "S6S Base Game Perks Redux.esp",
    "NS.esp",
    "Sweet Consumables.esp",
)


def digest(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            sha.update(chunk)
    return sha.hexdigest()



def selection_text_tile(path: Path) -> dict:
    """Extract only bounded display metadata; the game may use BSA fallbacks."""
    if path.stat().st_size > 2_000_000:
        return {"status": "too_large"}
    text = path.read_bytes().decode("utf-8-sig", errors="replace")
    matches = re.findall(
        r'<text\b[^>]*\bname\s*=\s*["\']LUM_SelectionText["\'][^>]*>(.*?)</text\s*>',
        text, re.IGNORECASE | re.DOTALL,
    )
    if len(matches) != 1:
        return {"status": "not_found" if not matches else "ambiguous_multiple_tiles",
                "match_count": len(matches)}
    tile = matches[0]
    def trait(name: str) -> str | None:
        match = re.search(
            r'<' + name + r'\b[^>]*>(.*?)</' + name + r'\s*>',
            tile, re.IGNORECASE | re.DOTALL,
        )
        if not match:
            return None
        return " ".join(match.group(1).split())[:180]
    font_expr = trait("font")
    return {
        "status": "found",
        "font_expression": font_expr,
        "font_id_literal": (int(font_expr)
                            if font_expr and re.fullmatch(r"\d+", font_expr) else None),
        "tile_id": trait("id"),
        "zoom": trait("zoom"),
        "tile_fragment_sha256": hashlib.sha256(tile.encode("utf-8")).hexdigest(),
    }



def summarize(installation) -> dict:
    if getattr(installation, "all_installed", False):
        raise ValueError("A selected profile is required, not all_installed")
    paths = []
    for wanted in WATCHED:
        chain = installation.providers.get(wanted.casefold(), [])
        rows = []
        for record in chain:
            source = Path(record["physical"])
            if not source.is_file():
                raise ValueError("Provider file disappeared: " + str(source))
            rows.append({
                "provider": record["provider"],
                "physical_path": str(source),
                "sha256": digest(source),
                "bytes": source.stat().st_size,
                **({"selection_text_tile": selection_text_tile(source)}
                   if wanted.casefold() == "menus/levelup_menu.xml" else {}),
            })
        paths.append({
            "virtual_path": wanted,
            "winning_provider_by_offline_priority": rows[-1]["provider"] if rows else None,
            "winning_sha256": rows[-1]["sha256"] if rows else None,
            "providers_low_to_high": rows,
            "plugin_active_in_profile": (
                wanted.casefold() in installation.active_keys
                if wanted.casefold().endswith((".esp", ".esm"))
                else None
            ),
        })
    likely_extra = [
        provider for provider in installation.mods_enabled
        if ("perk" in provider.casefold() and "korean" in provider.casefold())
        or "nskr test" in provider.casefold()
        or "korean perk runtime" in provider.casefold()
    ]
    return {
        "profile": installation.profile,
        "mo2_root": str(installation.root),
        "evidence_scope": "offline_loose_file_provider_precedence_only",
        "limitations": [
            "Does not check the running game's loaded DLLs, injected code or resolved plugin record overrides.",
            "Does not prove JIP Script Runner execution order, actual game encoding or rendered UI text.",
            "BSA and root-builder virtual files may not be reflected in this scan.",
            "A filename alone does not prove an older experimental overlay is stale.",
        ],
        "notes": list(installation.warnings),
        "possible_previous_test_mods": likely_extra,
        "watched_paths": paths,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mo2-root", required=True, type=Path)
    parser.add_argument("--profile", help="Defaults to selected_profile in ModOrganizer.ini")
    parser.add_argument("--output", type=Path,
                        help="New JSON outside MO2/game folders (stdout if omitted)")
    args = parser.parse_args(argv)
    installation = nskr.Installation(args.mo2_root, args.profile)
    report = summarize(installation)
    text = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        target = args.output.resolve()
        for protected in (installation.root, installation.game, installation.base):
            if target.is_relative_to(protected.resolve()):
                parser.error("Refusing to write into MO2, game or installation storage")
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("x", encoding="utf-8") as handle:
            handle.write(text)
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
