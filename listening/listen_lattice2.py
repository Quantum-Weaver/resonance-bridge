"""
listen_lattice2.py — the multi-parent census, through the anon door.

Opus (Claude), truly claude-opus-5[1m], 2026-07-27.
Round two of the shape sitting measured the CODE: nine members carry
more than one parent (kingdom 2 / phylum 2 / class 3 / order 2).
This asks the BUILT thing the same question.
"""

import json
import sys
import urllib.request
from collections import defaultdict
from pathlib import Path

BRIDGE = Path(r"C:\_superposition\resonance-bridge")


def load_env():
    env = {}
    for line in (BRIDGE / ".env").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            env[k.strip()] = v.strip()
    return env


def fetch(url, key, table, select="*"):
    rows, page = [], 0
    while True:
        req = urllib.request.Request(
            f"{url}/rest/v1/{table}?select={select}&limit=1000&offset={page*1000}",
            headers={"apikey": key, "Authorization": f"Bearer {key}"},
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            batch = json.loads(r.read().decode("utf-8"))
        rows.extend(batch)
        if len(batch) < 1000:
            return rows
        page += 1


def main():
    env = load_env()
    url = env.get("SUPABASE_URL_KNOWLEDGE", "")
    key = (env.get("SUPABASE_PUBLISHABLE_KEY_KNOWLEDGE", "")
           or env.get("SUPABASE_ANON_KEY_KNOWLEDGE", ""))

    names = {}
    tiers = {}
    for t, col in (("atoms", "atom_word"), ("molecules", "name"), ("organisms", "name")):
        for r in fetch(url, key, t, f"id,{col}"):
            names[r["id"]] = r[col]
            tiers[r["id"]] = t[:-1]

    schemes = {r["id"]: r for r in fetch(url, key, "schemes")}
    rel = fetch(url, key, "concept_relations")

    def side(r, which):
        for tier in ("atom", "molecule", "organism"):
            v = r.get(f"{which}_{tier}_id")
            if v:
                return v
        return None

    parents = defaultdict(list)
    for r in rel:
        if r["relation_type"] != "broader":
            continue
        s, o = side(r, "subject"), side(r, "object")
        parents[s].append((o, r.get("scheme_id")))

    multi = {s: ps for s, ps in parents.items() if len(ps) > 1}

    print(f"broader edges: {sum(len(v) for v in parents.values())}")
    print(f"distinct subjects carrying a parent: {len(parents)}")
    print(f"subjects with MORE THAN ONE parent: {len(multi)}\n")

    for s, ps in sorted(multi.items(), key=lambda kv: (-len(kv[1]), names.get(kv[0], ""))):
        sch = {schemes.get(sid, {}).get("name") for _, sid in ps}
        print(f"{names.get(s,'?'):34s} [{tiers.get(s,'?'):8s}] {len(ps)} parents"
              f"   scheme(s): {sorted(x for x in sch if x)}")
        for o, _ in sorted(ps, key=lambda p: names.get(p[0], "")):
            print(f"      -> {names.get(o,'?')}")
        print()

    # which schemes/dimensions do the multi-parent edges live in?
    by_scheme = defaultdict(int)
    for _, ps in multi.items():
        for _, sid in ps:
            by_scheme[schemes.get(sid, {}).get("name", "(none)")] += 1
    print("multi-parent edges by scheme:", dict(by_scheme))


if __name__ == "__main__":
    main()
