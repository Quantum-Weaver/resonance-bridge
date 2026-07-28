"""One listening question through the anon door, 2026-07-27.

Not a verification. Fable asking the built thing something no journal
answered: WHO IN THE LATTICE CARRIES THE MOST PARENTS — the deepest
polyhierarchy node — and what does the lattice hold for 'folksonomy'?
Keys load from resonance-bridge/.env and are never printed (house law).
One-off; not a reusable tool.
"""

import json
import sys
import urllib.request
from collections import Counter
from pathlib import Path

BRIDGE = Path(r"C:\_superposition\resonance-bridge")

env = {}
for line in (BRIDGE / ".env").read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, _, v = line.partition("=")
        env[k.strip()] = v.strip()

URL = env.get("SUPABASE_URL_KNOWLEDGE", "")
KEY = (env.get("SUPABASE_PUBLISHABLE_KEY_KNOWLEDGE", "")
       or env.get("SUPABASE_ANON_KEY_KNOWLEDGE", ""))
if not URL or not KEY:
    sys.exit("anon door closed: missing url/key names in .env")


def fetch(table, query="select=*"):
    rows, page = [], 0
    while True:
        req = urllib.request.Request(
            f"{URL}/rest/v1/{table}?{query}&limit=1000&offset={page * 1000}",
            headers={"apikey": KEY, "Authorization": f"Bearer {KEY}"},
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            batch = json.loads(r.read().decode("utf-8"))
        rows.extend(batch)
        if len(batch) < 1000:
            return rows
        page += 1


edges = fetch("concept_relations")
print(f"edges through the public door: {len(edges)}")
if edges:
    print("edge columns:", sorted(edges[0].keys()))

# name maps for every tier
names = {}
for table in ("atoms", "molecules", "organisms"):
    for row in fetch(table):
        label = (row.get("name") or row.get("label") or row.get("term")
                 or row.get("title") or "?")
        names[row["id"]] = (table[:-1], label)

REL_KEYS = [k for k in (edges[0].keys() if edges else [])
            if "relation" in k or "type" in k or "kind" in k]
print("relation-ish columns:", REL_KEYS)

rel_col = REL_KEYS[0] if REL_KEYS else None
if rel_col:
    print("relation kinds:", Counter(e.get(rel_col) for e in edges))

# count broader-edges per subject (subject → object where relation is
# broader/parent-ish; if kinds are unclear, count all edges per subject)
parent_count = Counter()
for e in edges:
    kind = str(e.get(rel_col, "")).lower() if rel_col else ""
    if rel_col and ("broad" not in kind and "parent" not in kind):
        continue
    subj = (e.get("subject_atom_id") or e.get("subject_molecule_id")
            or e.get("subject_organism_id"))
    if subj:
        parent_count[subj] += 1

print("\nTHE MOST-PARENTED (deepest polyhierarchy nodes):")
for cid, n in parent_count.most_common(5):
    tier, label = names.get(cid, ("?", cid))
    print(f"  {n} parents · {label} ({tier})")

# and folksonomy — the night's last row
print("\nFOLKSONOMY, as the lattice holds it:")
for table in ("atoms", "molecules", "organisms"):
    for h in fetch(table):
        if "folksonomy" in json.dumps(h, ensure_ascii=False).lower():
            keep = {k: v for k, v in h.items() if not k.endswith("_id")
                    and k not in ("id", "created_at", "updated_at")}
            print(f"  [{table}] {json.dumps(keep, ensure_ascii=False)[:400]}")

ety = fetch("etymology")
if ety:
    cols = ety[0].keys()
    print("  etymology columns:", sorted(cols))
    for row in ety:
        blob = json.dumps(row, ensure_ascii=False).lower()
        if "folksonomy" in blob or "folc" in blob or "nomia" in blob:
            keep = {k: v for k, v in row.items() if not k.endswith("id")
                    and k not in ("created_at", "updated_at")}
            print(" ", json.dumps(keep, ensure_ascii=False)[:400])
