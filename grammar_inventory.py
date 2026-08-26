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
  ../resonance-grammar/exports/grammar-export-<date>.json
"""

import json
import sys
import urllib.request
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent

# The five lattice tables' anon reads show ONLY status='published' rows by
# design, so zero here means "nothing published yet", never "dark".
GRAMMAR_TABLES = [
    "gaia_config",
    "categories", "atoms", "etymology", "sensory_lexicon",
    "molecules", "molecule_atoms", "organisms", "organism_molecules",
    "organism_atoms",
    "schemes", "scheme_memberships", "concept_relations",
    "classification_paths", "classification_path_steps",
    # the self-aware layer: registry class — plain public read,
    # steward-synced against pg_catalog
    "templates", "policies", "functions", "triggers",
    "indexes", "enums", "composite_types",
    "scripts", "columns",  # 010/011 — the MDL reborn
    # The base names its own tables through gaia_config (discover_tables below);
    # this list is the backstop for the day that read fails.
    "thesaurus", "folksonomies", "relationships", "views", "roles",
    "beacons", "pantheon", "awen",
]


def load_env() -> dict:
    env = {}
    env_path = HERE / ".env"
    if not env_path.is_file():
        sys.exit("no .env beside this script — the keys enter by KP's own hands from the dashboard")
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            env[k.strip()] = v.strip()
    return env


def discover_tables(url: str, key: str) -> list:
    """Ask the base what it holds — gaia_config is its own registry.

    Added 2026-08-24 at KP's word ("we have an entire database to export
    again"): a hand-kept table list had gone four tables stale twice, so the
    export silently omitted them. The registry is the truth; GRAMMAR_TABLES
    is the backstop, and anything the registry names that the list forgot is
    reported rather than dropped in silence.
    """
    try:
        req = urllib.request.Request(
            f"{url}/rest/v1/gaia_config?select=table_name&order=table_name&limit=1000",
            headers={"apikey": key, "Authorization": f"Bearer {key}"},
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            named = [row["table_name"] for row in json.loads(r.read().decode("utf-8"))]
    except Exception as e:
        print(f"gaia_config unreadable ({type(e).__name__}) — falling back to the static list")
        return list(GRAMMAR_TABLES)
    if not named:
        return list(GRAMMAR_TABLES)
    unlisted = [t for t in named if t not in GRAMMAR_TABLES]
    forgotten = [t for t in GRAMMAR_TABLES if t not in named]
    print(f"gaia_config names {len(named)} tables"
          + (f"; {len(unlisted)} not in the static list: {', '.join(unlisted)}" if unlisted else ""))
    if forgotten:
        print(f"in the static list but unnamed by the registry: {', '.join(forgotten)}")
    # union, registry order first — nothing the old list knew is ever dropped
    return named + forgotten


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
    tables = discover_tables(url, key)
    print()
    print(f"{'table':26s} {'rows':>7s}")
    for t in tables:
        try:
            rows = fetch(url, key, t)
        except Exception as e:  # table absent or unreadable — say so, keep going
            print(f"{t:26s} {'—':>7s}  ({type(e).__name__}: {e})")
            export["tables"][t] = {"error": str(e)}
            continue
        export["tables"][t] = rows
        print(f"{t:26s} {len(rows):>7d}")

    out_dir = Path(r"C:\_superposition\resonance-grammar\exports")
    out_dir.mkdir(exist_ok=True)
    out = out_dir / f"grammar-export-{date.today().isoformat()}.json"
    out.write_text(json.dumps(export, ensure_ascii=False, indent=1),
                   encoding="utf-8")
    print(f"\nexport written: {out}")


if __name__ == "__main__":
    main()
