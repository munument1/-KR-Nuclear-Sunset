"""Collect public issue #14 screenshots in order for human-led PERK triage.

This only downloads GitHub issue assets into a new separate directory.
No text recognition or automatic PERK classification is claimed.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
import urllib.request

PATTERN = re.compile(r"https://github\.com/user-attachments/assets/[0-9a-fA-F-]{36}")


def collect(body: str, directory: Path) -> dict:
    urls = list(dict.fromkeys(PATTERN.findall(body)))
    if len(urls) > 50:
        raise ValueError("Unexpected issue attachment count")
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    manifest = []
    for idx, url in enumerate(urls, 1):
        result = {"capture": idx, "source": url}
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "Issue14-ReadOnly-Audit"})
            with urllib.request.urlopen(request, timeout=35) as response:
                content_type = response.headers.get("Content-Type", "").split(";")[0]
                if content_type not in ("image/png", "image/jpeg", "image/webp"):
                    raise ValueError("Unexpected attachment content type: " + content_type)
                raw = response.read(12_000_001)
                if len(raw) > 12_000_000:
                    raise ValueError("Image exceeds safety size cap")
                known = (raw.startswith(b"\x89PNG\r\n\x1a\n")
                         or raw.startswith(b"\xff\xd8\xff")
                         or raw.startswith(b"RIFF") and raw[8:12] == b"WEBP")
                if not known:
                    raise ValueError("Not a recognized image payload")
            extension = {"image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp"}[content_type]
            out = directory / (f"{idx:02}" + extension)
            # Never overwrite another capture.
            with out.open("xb") as file:
                file.write(raw)
            result.update(status="downloaded", file=out.name, bytes=len(raw))
        except (OSError, ValueError) as error:
            result.update(status="failed", reason=str(error)[:240])
        manifest.append(result)
    summary = {"total_links": len(urls),
               "downloaded": sum(r["status"] == "downloaded" for r in manifest),
               "captures": manifest}
    with (directory / "manifest.json").open("x", encoding="utf-8") as file:
        json.dump(summary, file, ensure_ascii=False, indent=2)
        file.write("\n")
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--issue-body", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    result = collect(args.issue_body.read_text(encoding="utf-8"), args.output_dir)
    print(f"Issue captures downloaded: {result['downloaded']}/{result['total_links']}")
    return 0 if result["downloaded"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
