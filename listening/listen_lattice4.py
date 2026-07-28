"""
listen_lattice4.py — what does scheme_id MEAN on a broader edge?

Suspicion (to be measured, not asserted): the ladder edges scope the
edge by the SUBJECT's rank, the May-anchor edges by the PARENT's rank.
If so, the Gatekeeper's N->N-1 write-time law has two different
referents in one column.

Opus (Claude), truly claude-opus-5[1m], 2026-07-27. Read-only, anon door.
"""

import json
import urllib.request
from collections import Counter
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
    rank_ids = {i for i, s in schemes.items() if s.get("scheme_type") == "rank"}

    member_rank, member_schemes = {}, {}
    for m in fetch(url, key, "scheme_memberships"):
        e = entity(m)
        sid = m.get("scheme_id")
        if not e:
            continue
        member_schemes.setdefault(e, set()).add(sid)
        if sid in rank_ids:
            member_rank[e] = sid

    tally = Counter()
    examples = {}
    order_deltas = Counter()
    for r in fetch(url, key, "concept_relations"):
        if r["relation_type"] != "broader":
            continue
        s, o, sid = entity(r, "subject_"), entity(r, "object_"), r.get("scheme_id")
        sr, orank = member_rank.get(s), member_rank.get(o)
        if sid is None:
            k = "no scheme on edge"
        elif sid == sr and sid == orank:
            k = "scheme == BOTH ranks (same rank both sides)"
        elif sid == sr:
            k = "scheme == SUBJECT's rank"
        elif sid == orank:
            k = "scheme == PARENT's rank"
        elif sid in member_schemes.get(s, set()):
            k = "scheme == a NON-rank scheme of the subject"
        else:
            k = "scheme matches neither side"
        tally[k] += 1
        examples.setdefault(k, f"{names.get(s,'?')} -> {names.get(o,'?')} "
                               f"[edge scheme: {schemes.get(sid,{}).get('name')}]")

        # sort_order delta, when both sides carry a rank
        if sr and orank:
            d = (schemes[sr].get("sort_order") or 0) - (schemes[orank].get("sort_order") or 0)
            order_deltas[d] += 1

    print("what scheme_id points at, across the 182 broader edges:\n")
    for k, n in tally.most_common():
        print(f"  {n:4d}  {k}")
        print(f"        e.g. {examples[k]}")
    print("\nsubject_rank.sort_order - parent_rank.sort_order "
          "(the Gatekeeper's N->N-1 law; 1 == lawful):")
    for d, n in sorted(order_deltas.items()):
        print(f"  delta {d:+d}: {n} edges")


if __name__ == "__main__":
    main()
