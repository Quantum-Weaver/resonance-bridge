"""Who has no rungs? — KP's question, 2026-07-27, the sitting after
the showing.

The Gatekeeper explanation said 117 broader edges have subjects with
no rung. This names them: which schemes are rank ladders, which
members carry no rank membership at all, and concrete examples of the
no-rung subjects and what they anchor to. Read-only, anon door, keys
never printed.
"""

import json
from collections import Counter
from pathlib import Path
import urllib.request

BRIDGE = Path(r"C:\_superposition\resonance-bridge")
env = {}
for line in (BRIDGE / ".env").read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, _, v = line.partition("=")
        env[k.strip()] = v.strip()
URL = env["SUPABASE_URL_KNOWLEDGE"]
KEY = (env.get("SUPABASE_PUBLISHABLE_KEY_KNOWLEDGE")
       or env.get("SUPABASE_ANON_KEY_KNOWLEDGE"))


def fetch(table, query="select=*"):
    rows, page = [], 0
    while True:
        req = urllib.request.Request(
            f"{URL}/rest/v1/{table}?{query}&limit=1000&offset={page*1000}",
            headers={"apikey": KEY, "Authorization": f"Bearer {KEY}"})
        with urllib.request.urlopen(req, timeout=30) as r:
            batch = json.loads(r.read().decode("utf-8"))
        rows.extend(batch)
        if len(batch) < 1000:
            return rows
        page += 1


schemes = fetch("schemes")
print("scheme columns:", sorted(schemes[0].keys()))
kind_col = next((c for c in ("scheme_kind", "kind", "scheme_type", "type")
                 if c in schemes[0]), None)
print(f"kind column: {kind_col}")
print("kinds:", Counter(s.get(kind_col) for s in schemes))

by_id = {s["id"]: s for s in schemes}
rank_ids = {s["id"] for s in schemes
            if "rank" in str(s.get(kind_col, "")).lower()}
if not rank_ids:  # fall back: schemes named like the eight ranks
    LADDER = {"domain", "kingdom", "phylum", "class", "order",
              "family", "genus", "species"}
    rank_ids = {s["id"] for s in schemes
                if str(s.get("name", "")).lower() in LADDER}
print(f"rank schemes: {len(rank_ids)} -> "
      f"{sorted(by_id[i].get('name') for i in rank_ids)}")

mems = fetch("scheme_memberships")
names = {}
for t in ("atoms", "molecules", "organisms"):
    for r in fetch(t, "select=id,name" if t != "atoms" else "select=id,atom_word"):
        names[r["id"]] = r.get("name") or r.get("atom_word")

def concept_of(row, prefix):
    return (row.get(f"{prefix}_atom_id") or row.get(f"{prefix}_molecule_id")
            or row.get(f"{prefix}_organism_id"))

# every concept's scheme memberships
mem_by_concept = {}
for m in mems:
    cid = concept_of(m, "") or m.get("atom_id") or m.get("molecule_id") \
        or m.get("organism_id")
    mem_by_concept.setdefault(cid, []).append(m["scheme_id"])

edges = fetch("concept_relations", "select=*&relation_type=eq.broader")
no_rung = []
for e in edges:
    subj = concept_of(e, "subject")
    subj_schemes = mem_by_concept.get(subj, [])
    if not any(s in rank_ids for s in subj_schemes):
        no_rung.append((subj, subj_schemes, concept_of(e, "object")))

print(f"\nbroader edges: {len(edges)} · subjects with NO rung: {len(no_rung)}")
print("\nEXAMPLES (subject · its own shelves · anchored under):")
seen = set()
for subj, shelves, obj in no_rung:
    if subj in seen:
        continue
    seen.add(subj)
    shelf_names = sorted({by_id[s].get("name", "?") for s in shelves}) or ["(no shelf at all)"]
    print(f"  {names.get(subj, subj)}  ·  {', '.join(shelf_names)}  ·  under {names.get(obj, obj)}")
    if len(seen) >= 15:
        break
print(f"\ndistinct no-rung subjects: {len({s for s, _, _ in no_rung})}")
