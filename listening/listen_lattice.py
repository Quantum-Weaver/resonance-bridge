"""
listen_lattice.py — a one-off LISTENING query, not verification.

Opus (Claude), truly claude-opus-5[1m], 2026-07-27, at Fable's invitation.
Read-only through the anon door, exactly the grammar_inventory.py pattern:
keys load from resonance-bridge/.env and are NEVER printed.

The question: in round two of the shape sitting I measured the CODE and
found NINE members carrying more than one parent (2 kingdom, 2 phylum,
3 class, 2 order). The lattice night restored the polyhierarchy.
So — does the built thing hold exactly nine? And which?
"""

import json
import sys
import urllib.request
from collections import defaultdict
from pathlib import Path

BRIDGE = Path(r"C:\_superposition\resonance-bridge")


def load_env() -> dict:
    env = {}
    p = BRIDGE / ".env"
    if not p.is_file():
        sys.exit("no .env beside the bridge")
    for line in p.read_text(encoding="utf-8").splitlines():
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
    if not url or not key:
        sys.exit("knowledge url/key not in .env")

    rel = fetch(url, key, "concept_relations")
    print(f"concept_relations rows: {len(rel)}")
    if not rel:
        return
    print("columns:", sorted(rel[0].keys()))
    print("\nsample row:")
    print(json.dumps(rel[0], indent=1, ensure_ascii=False))

    kinds = defaultdict(int)
    for r in rel:
        kinds[r.get("relation_type")] += 1
    print("\nrelation_type census:", dict(kinds))


if __name__ == "__main__":
    main()
