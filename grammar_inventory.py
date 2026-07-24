"""
grammar_inventory.py — discover what lives in the resonance-knowledge
Grammar tables, and export it for merge planning.

Founded 2026-07-23 at KP's word: "let us discover what is in the base,
potentially export it to be merged if needed" — the step before the
excavator season's first seed (order ruled the same hour: full syntax
first, breakdown pieces after, junction tables properly included).

READ-ONLY by construction: uses the ANON key through the public read
policies (004-rls-policies-organisms.sql healed the last two). Keys are
loaded from .env beside this file and are never printed — the house
rule stands: no real key enters any chat, ever.

Output: counts to stdout + a dated full export at
  ../resonance-knowledge/exports/grammar-export-<date>.json
"""

import json
import sys
import urllib.request
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent

# gaia_config intentionally absent — slated for removal (KP, 2026-07-23)
GRAMMAR_TABLES = [
    "categories", "atoms", "etymology", "sensory_lexicon",
    "molecules", "molecule_atoms", "organisms", "organism_molecules",
]


def load_env() -> dict:
    env = {}
    env_path = HERE / ".env"
    if not env_path.is_file():
        sys.exit("no .env beside this script — copy .env.example and fill by hand")
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            env[k.strip()] = v.strip()
    return env


def fetch(url: str, key: str, table: str) -> list:
    """Paged fetch — PostgREST clamps any single response to 1000 rows."""
    rows, page = [], 0
    while True:
        req = urllib.request.Request(
            f"{url}/rest/v1/{table}?select=*&limit=1000&offset={page * 1000}",
            headers={"apikey": key, "Authorization": f"Bearer {key}"},
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            batch = json.loads(r.read().decode("utf-8"))
        rows.extend(batch)
        if len(batch) < 1000:
            return rows
        page += 1


def main() -> None:
    env = load_env()
    url = env.get("SUPABASE_URL_KNOWLEDGE", "")
    # publishable = the anon key's modern name; accept either spelling
    key = (env.get("SUPABASE_PUBLISHABLE_KEY_KNOWLEDGE", "")
           or env.get("SUPABASE_ANON_KEY_KNOWLEDGE", ""))
    if not url or not key:
        sys.exit("SUPABASE_URL_KNOWLEDGE / SUPABASE_PUBLISHABLE_KEY_KNOWLEDGE "
                 "not set in .env — fill them by your own hands, then rerun")

    export = {"exported": date.today().isoformat(),
              "source": "resonance-knowledge Supabase (anon key, read-only)",
              "tables": {}}
    print(f"{'table':22s} {'rows':>6s}")
    for t in GRAMMAR_TABLES:
        try:
            rows = fetch(url, key, t)
        except Exception as e:  # table absent or unreadable — say so, keep going
            print(f"{t:22s} {'—':>6s}  ({type(e).__name__}: {e})")
            export["tables"][t] = {"error": str(e)}
            continue
        export["tables"][t] = rows
        print(f"{t:22s} {len(rows):>6d}")

    out_dir = Path(r"C:\_superposition\resonance-knowledge\exports")
    out_dir.mkdir(exist_ok=True)
    out = out_dir / f"grammar-export-{date.today().isoformat()}.json"
    out.write_text(json.dumps(export, ensure_ascii=False, indent=1),
                   encoding="utf-8")
    print(f"\nexport written: {out}")


if __name__ == "__main__":
    main()
