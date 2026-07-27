"""
grammar_clear_name_tiers.py — clear the NAME tiers of the
resonance-knowledge Grammar (molecules, organisms, their junctions),
leaving the atom triple and categories standing.

Born 2026-07-26 at KP's word: "the atoms are great, but we need to
clear the rest out and properly audit the data in the name columns
before re-seeding." The audit-and-reseed loop may run more than once;
this is its clearing hand. FK order: junctions first, then tiers.
Never touches: atoms, etymology, sensory_lexicon, categories.
"""

import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
env = {}
for line in (HERE / ".env").read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, _, v = line.partition("=")
        env[k.strip()] = v.strip()
URL = env["SUPABASE_URL_KNOWLEDGE"]
KEY = env["SUPABASE_SECRET_KEY_KNOWLEDGE"]

ORDER = ["organism_atoms", "organism_molecules", "molecule_atoms",
         "organisms", "molecules"]

for table in ORDER:
    req = urllib.request.Request(
        f"{URL}/rest/v1/{table}?id=not.is.null",
        headers={"apikey": KEY, "Authorization": f"Bearer {KEY}",
                 "Prefer": "count=exact"},
        method="DELETE")
    with urllib.request.urlopen(req, timeout=120) as r:
        n = (r.headers.get("Content-Range") or "?").split("/")[-1]
    print(f"{table:22s} cleared {n}")
