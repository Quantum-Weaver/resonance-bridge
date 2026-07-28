"""
listen_lattice3.py — decomposing the 57.

A member with two parents is NOT automatically a polyhierarchy fork.
If both parents sit at the SAME rank, that is a fork (the thing the May
tree could not hold). If they sit at DIFFERENT ranks, that is one
path fragment stored as two edges — a chain, not a fork.

Opus (Claude), truly claude-opus-5[1m], 2026-07-27. Read-only, anon door.
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


def entity(row, prefix=""):
    for tier in ("atom", "molecule", "organism"):
        v = row.get(f"{prefix}{tier}_id")
        if v:
            return v
    return None


def main():
    env = load_env()
    url = env.get("SUPABASE_URL_KNOWLEDGE", "")
    key = (env.get("SUPABASE_PUBLISHABLE_KEY_KNOWLEDGE", "")
           or env.get("SUPABASE_ANON_KEY_KNOWLEDGE", ""))

    names = {}
    for t, col in (("atoms", "atom_word"), ("molecules", "name"), ("organisms", "name")):
        for r in fetch(url, key, t, f"id,{col}"):
            names[r["id"]] = r[col]

    schemes = {r["id"]: r for r in fetch(url, key, "schemes")}
    ranks = {sid: s for sid, s in schemes.items() if s.get("scheme_type") == "rank"} \
        or {sid: s for sid, s in schemes.items() if s.get("sort_order")}

    # member -> its rank scheme (from scheme_memberships)
    member_rank = {}
    mem = fetch(url, key, "scheme_memberships")
    print("scheme_type values:", sorted({s.get('scheme_type') for s in schemes.values()}))
    for m in mem:
        sch = schemes.get(m.get("scheme_id"), {})
        if sch.get("id") in ranks:
            e = entity(m)
            if e:
                member_rank[e] = sch.get("name")

    rel = fetch(url, key, "concept_relations")
    parents = defaultdict(list)
    for r in rel:
        if r["relation_type"] != "broader":
            continue
        parents[entity(r, "subject_")].append(entity(r, "object_"))

    multi = {s: ps for s, ps in parents.items() if len(ps) > 1}
    forks, chains, unknown = [], [], []
    for s, ps in multi.items():
        prank = {member_rank.get(p) for p in ps}
        if None in prank:
            unknown.append((s, ps, prank))
        elif len(prank) == 1:
            forks.append((s, ps, prank))
        else:
            chains.append((s, ps, prank))

    print(f"\nmulti-parent subjects: {len(multi)}")
    print(f"  TRUE FORKS  (all parents at ONE rank): {len(forks)}")
    print(f"  CHAIN FRAGMENTS (parents at different ranks): {len(chains)}")
    print(f"  unresolved parent rank: {len(unknown)}")

    print("\n--- the forks (the polyhierarchy proper) ---")
    for s, ps, prank in sorted(forks, key=lambda x: (-len(x[1]), names.get(x[0], ""))):
        print(f"{names.get(s,'?'):30s} {len(ps)} parents @ {list(prank)[0]}: "
              f"{', '.join(sorted(names.get(p,'?') for p in ps))}")

    if unknown:
        print("\n--- unresolved (parent has no rank membership) ---")
        for s, ps, prank in unknown[:10]:
            print(f"{names.get(s,'?'):30s} -> {[names.get(p,'?') for p in ps]} ranks={prank}")


if __name__ == "__main__":
    main()
