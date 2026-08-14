"""
grammar_purge_all.py — full purge of the Grammar tables in the
resonance-knowledge Supabase, before the lawful re-seed.

Run 2026-07-23 night at KP's word: "i would like to purge the data
from the knowledge supabase before seeding again. i exported
everything earlier." The curated content is preserved in:
  resonance-excavator/sources/export-supabase/ (both CSV sets)
  resonance-knowledge/exports/grammar-export-2026-07-23.json
  the backup drives' copies.
KEPT: categories (structural lookup) · gaia_config (KP's own removal).
FK order: junctions first, then tiers, then the atom triple.
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

# not_is.null on id matches every row — a full-table delete PostgREST allows
ORDER = ["organism_molecules", "molecule_atoms", "organisms", "molecules",
         "etymology", "sensory_lexicon", "atoms"]

for table in ORDER:
    req = urllib.request.Request(
        f"{URL}/rest/v1/{table}?id=not.is.null",
        headers={"apikey": KEY, "Authorization": f"Bearer {KEY}",
                 "Prefer": "count=exact"},
        method="DELETE")
    with urllib.request.urlopen(req, timeout=120) as r:
        n = (r.headers.get("Content-Range") or "?").split("/")[-1]
    print(f"{table:22s} purged {n}")
