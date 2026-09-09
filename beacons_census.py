#!/usr/bin/env python3
"""Read GitHub's account of every repo the key owns and write the beacons seed.

    python beacons_census.py            # write resonance-nectere/seeds/beacons-github.json
    python beacons_census.py --dry      # print the census, write nothing

Per repo: name, slug, html_url, description, private, archived, pushed_at, the
README's first heading split into glyph and title, and the version read from
package.json, src-tauri/tauri.conf.json, src-tauri/Cargo.toml or Cargo.toml,
first found. Archived repos are excluded. Reads only. The key is HOUSE_GITHUB_PAT in resonance-bridge/.env
and is never printed.
"""

import base64
import json
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BRIDGE = Path(__file__).resolve().parent
OUT = BRIDGE.parent / "resonance-nectere" / "seeds" / "beacons-github.json"
API = "https://api.github.com"
VERSION_FILES = (
    ("package.json", r'"version"\s*:\s*"([^"]+)"'),
    ("src-tauri/tauri.conf.json", r'"version"\s*:\s*"([^"]+)"'),
    ("src-tauri/Cargo.toml", r'^version\s*=\s*"([^"]+)"'),
    ("Cargo.toml", r'^version\s*=\s*"([^"]+)"'),
)
HEADING = re.compile(r"^#\s+(?P<glyph>[^\w\[]*?)\s*(?P<title>[\w\[].*?)\s*$")


def read_key() -> str:
    env = BRIDGE / ".env"
    if not env.exists():
        sys.exit(f"no .env at {env} -- the GitHub line is not connected")
    for line in env.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("HOUSE_GITHUB_PAT="):
            key = line.split("=", 1)[1].strip().strip('"').strip("'")
            if key:
                return key
    sys.exit("HOUSE_GITHUB_PAT is absent or empty in .env")


def get(key: str, path: str):
    req = urllib.request.Request(
        API + path,
        headers={
            "Authorization": f"Bearer {key}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "resonance-bridge-beacons-census",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            return json.load(res)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def repos(key: str) -> list[dict]:
    out, page = [], 1
    while True:
        batch = get(key, f"/user/repos?per_page=100&affiliation=owner&page={page}")
        if not batch:
            break
        out.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return out


def file_text(key: str, full_name: str, path: str) -> str | None:
    body = get(key, f"/repos/{full_name}/contents/{path}")
    if not body or "content" not in body:
        return None
    return base64.b64decode(body["content"]).decode("utf-8", "replace")


def readme_heading(key: str, full_name: str) -> tuple[str | None, str | None]:
    body = get(key, f"/repos/{full_name}/readme")
    if not body or "content" not in body:
        return None, None
    text = base64.b64decode(body["content"]).decode("utf-8", "replace")
    for line in text.splitlines():
        if line.startswith("# "):
            m = HEADING.match(line)
            if not m:
                return None, line[2:].strip()
            return (m.group("glyph") or None), m.group("title")
    return None, None


def version(key: str, full_name: str) -> tuple[str | None, str | None]:
    for path, pattern in VERSION_FILES:
        text = file_text(key, full_name, path)
        if text is None:
            continue
        m = re.search(pattern, text, re.M)
        if m:
            return m.group(1), path
    return None, None


def main() -> None:
    dry = "--dry" in sys.argv
    key = read_key()
    rows = []
    archived = []
    for r in sorted(repos(key), key=lambda r: r["name"].lower()):
        if r.get("archived"):
            archived.append(r["name"])
            continue
        full = r["full_name"]
        glyph, title = readme_heading(key, full)
        ver, ver_src = version(key, full)
        rows.append({
            "name": r["name"],
            "slug": r["name"].lower(),
            "html_url": r["html_url"],
            "description": r.get("description"),
            "private": bool(r["private"]),
            "pushed_at": r.get("pushed_at"),
            "readme_glyph": glyph,
            "readme_title": title,
            "version": ver,
            "version_source": ver_src,
        })
        print(f"{r['name']:24s} {'private' if r['private'] else 'PUBLIC ':7s} "
              f"v={ver or '-':7s} {glyph or '-':4s} {title or '-'}")

    seed = {
        "source": "github · /user/repos · /readme · version files",
        "read_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "rows": rows,
    }
    print(f"\n{len(rows)} repos · {sum(1 for r in rows if not r['private'])} public")
    if dry:
        print(f"--dry: {OUT} not written")
        return
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(seed, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
