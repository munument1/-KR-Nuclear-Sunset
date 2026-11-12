"""Collect linked public issue screenshots to a temporary CI artifact.

The sources are the actual issue bodies. Limit downloads to GitHub attachment
URLs, never save them in Git or alter any installed game files.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from urllib.request import Request, urlopen

ALLOWED = re.compile(r"https://github[.]com/user-attachments/assets/[0-9a-f-]{36}")
REPO = "munument1/-KR-Nuclear-Sunset"


def download(url, headers):
    with urlopen(Request(url, headers=headers), timeout=45) as response:
        data = response.read(12_000_001)
        if len(data) > 12_000_000:
            raise ValueError("Screenshot size limit exceeded")
        return data


def main(out):
    out.mkdir(parents=True, exist_ok=True)
    token = os.environ.get("GH_TOKEN", "")
    headers = {"User-Agent": "NSKR-source-backed-issue-audit",
               "Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = "Bearer " + token
    manifest = []
    for issue in (20, 22):
        api = "https://api.github.com/repos/" + REPO + "/issues/" + str(issue)
        body = json.loads(download(api, headers))["body"]
        urls = ALLOWED.findall(body)
        for i, url in enumerate(urls, 1):
            name = f"issue{issue}_{i}.png"
            # The assets are public GitHub-hosted uploads, not arbitrary URLs.
            try:
                data = download(url, {"User-Agent": headers["User-Agent"]})
            except Exception as e:
                manifest.append({"issue": issue, "source": url,
                                 "status": "unavailable", "detail": type(e).__name__})
                continue
            (out / name).write_bytes(data)
            manifest.append({"issue": issue, "source": url, "name": name,
                             "sha256": hashlib.sha256(data).hexdigest(),
                             "bytes": len(data), "status": "downloaded"})
    (out / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    if not any(e["status"] == "downloaded" for e in manifest):
        raise RuntimeError("No issue screenshots accessible")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
