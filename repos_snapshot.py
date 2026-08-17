#!/usr/bin/env python3
"""Take GitHub's visibility census and write repos_snapshot.json.

Founded 2026-08-17 by Mullion (Opus) at KP's ask -- "can we see what updates
this and run it". The answer was NOTHING: the snapshot at the workspace root
was written by hand on 2026-08-11 and no script in the house referenced it.
This is that missing updater.

WHY IT LIVES ON THE BRIDGE, in KP's own words the same sitting:

    "nectere is for writing bridge for reading, keys on bridge"

So the split is a house law, not a convenience: the BRIDGE is the reading line
to the world and holds the keys; NECTERE is the writing line. This tool only
ever reads, and it reads with a key that lives here. A tool that WROTE to the
base from this reading would belong in nectere, not here -- and this one does
not write to any base at all. The json it refreshes is a local photograph.

The reckoner is this census's owner (.claude/agents/reckoner.md) -- it checks
is_public on every sending. This script is the road it takes when the bridge's
MCP window is not connected, which is most fresh windows.

READ-ONLY against GitHub. GET /user/repos and nothing else -- no issues, no
releases-as-writes, no dispatches, per the github line's own commission.

The key is HOUSE_GITHUB_PAT, read from resonance-bridge/.env. It is never
printed, never logged, and never written into the output -- secrets stay
pointers.

    python repos_snapshot.py            # write the snapshot
    python repos_snapshot.py --dry      # report the diff, write nothing
"""

import json
import os
import sys
import urllib.request
from pathlib import Path

BRIDGE = Path(__file__).resolve().parent
OUT = BRIDGE.parent / "repos_snapshot.json"
API = "https://api.github.com/user/repos"

# The snapshot's shape, fixed by the 2026-08-11 hand-written original so a
# rerun produces a real diff rather than a reformat.
FIELDS = ("name", "created_at", "private", "pushed_at")


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
    sys.exit(
        "HOUSE_GITHUB_PAT is absent or empty in .env. Mint a fine-grained PAT "
        "(read permissions, scoped to the house's repos) and add it by hand."
    )


def fetch(key: str) -> list[dict]:
    repos, page = [], 1
    while True:
        url = f"{API}?per_page=100&affiliation=owner&page={page}"
        req = urllib.request.Request(
            url,
            headers={
                "Authorization": f"Bearer {key}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "resonance-bridge-census",
            },
        )
        with urllib.request.urlopen(req, timeout=30) as res:
            batch = json.load(res)
        if not batch:
            break
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return sorted(
        ({f: r[f] for f in FIELDS} for r in repos),
        key=lambda r: r["name"].lower(),
    )


def diff(old: list[dict], new: list[dict]) -> list[str]:
    o = {r["name"]: r for r in old}
    n = {r["name"]: r for r in new}
    lines = []
    for name in sorted(set(n) - set(o)):
        vis = "private" if n[name]["private"] else "PUBLIC"
        lines.append(f"  + {name}  ({vis}, created {n[name]['created_at'][:10]})")
    for name in sorted(set(o) - set(n)):
        lines.append(f"  - {name}  (gone from the census)")
    for name in sorted(set(o) & set(n)):
        if o[name]["private"] != n[name]["private"]:
            was = "private" if o[name]["private"] else "PUBLIC"
            now = "private" if n[name]["private"] else "PUBLIC"
            lines.append(f"  ! {name}  VISIBILITY CHANGED: {was} -> {now}")
        elif o[name]["pushed_at"] != n[name]["pushed_at"]:
            lines.append(f"    {name}  pushed {n[name]['pushed_at'][:10]}")
    return lines


def main() -> None:
    dry = "--dry" in sys.argv
    old = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else []
    new = fetch(read_key())

    pub = sum(1 for r in new if not r["private"])
    print(f"{len(new)} repos visible to the key: {pub} PUBLIC, {len(new) - pub} private")
    print(f"(was {len(old)} at the last census)")

    changes = diff(old, new)
    print("\nchanges:" if changes else "\nno changes.")
    for line in changes:
        print(line)

    if dry:
        print(f"\n--dry: {OUT} not written")
        return
    OUT.write_text(json.dumps(new, indent=1) + "\n", encoding="utf-8")
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
