"""
grammar_wipe_seeded.py — remove the excavator season's FIRST-PASS rows
from the resonance-knowledge Supabase, returning the base to its
curated state.

Run 2026-07-23 night at KP's explicit word ("yes please continue"),
after his inspection ruled the first pass a wash (atom_word law:
single word, lowercase, no markers — the pass predated it).

Surgical by provenance, FK-ordered:
1. organism_molecules where role = 'identifier'      (ours alone)
2. molecule_atoms of molecules defined "The name '…" (ours alone)
3. atoms defined "Word discovered…"                  (ours alone)
   (+ their trigger-born etymology/sensory rows if FK requires)
4. molecules defined "The name '…"
5. organisms created_by 'excavator season…'
Curated rows carry none of these markers. Everything deleted is
re-derivable from the lighthouse logs; nothing unique is lost.
"""

import json
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load_env() -> dict:
    env = {}
    for line in (HERE / ".env").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            env[k.strip()] = v.strip()
    return env


ENV = load_env()
URL = ENV["SUPABASE_URL_KNOWLEDGE"]
KEY = ENV["SUPABASE_SECRET_KEY_KNOWLEDGE"]


def req(method: str, path: str, headers=None):
    h = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}
    h.update(headers or {})
    r = urllib.request.Request(f"{URL}/rest/v1/{path}", headers=h, method=method)
    with urllib.request.urlopen(r, timeout=120) as resp:
        return resp.headers.get("Content-Range"), resp.read().decode()


def delete(path: str) -> str:
    cr, _ = req("DELETE", path, {"Prefer": "count=exact"})
    return (cr or "?").split("/")[-1]


def fetch_ids(table: str, flt: str) -> list:
    ids, page = [], 0
    while True:
        _, body = req("GET", f"{table}?select=id&{flt}&limit=1000&offset={page*1000}")
        batch = json.loads(body)
        ids.extend(r["id"] for r in batch)
        if len(batch) < 1000:
            return ids
        page += 1


def main() -> None:
    like_mol = urllib.parse.quote("The name '*")
    like_atom = urllib.parse.quote("Word discovered*")
    like_org = urllib.parse.quote("excavator season*")

    print("1. organism_molecules (role=identifier):",
          delete("organism_molecules?role=eq.identifier"))

    mol_ids = fetch_ids("molecules", f"definition=like.{like_mol}")
    print(f"2. molecule_atoms of {len(mol_ids)} seeded molecules:", end=" ")
    n = 0
    for i in range(0, len(mol_ids), 100):
        chunk = ",".join(mol_ids[i:i + 100])
        n += int(delete(f"molecule_atoms?molecule_id=in.({chunk})"))
    print(n)

    atom_ids = fetch_ids("atoms", f"definition=like.{like_atom}")
    print(f"3. seeded atoms ({len(atom_ids)}):", end=" ")
    try:
        print(delete(f"atoms?definition=like.{like_atom}"))
    except urllib.error.HTTPError:
        # FK from trigger-born etymology/sensory — clear those first
        for tbl in ("etymology", "sensory_lexicon"):
            m = 0
            for i in range(0, len(atom_ids), 100):
                chunk = ",".join(atom_ids[i:i + 100])
                m += int(delete(f"{tbl}?atom_id=in.({chunk})"))
            print(f"\n   cleared {tbl}: {m}", end="")
        print("\n   atoms:", delete(f"atoms?definition=like.{like_atom}"))

    print("4. seeded molecules:", delete(f"molecules?definition=like.{like_mol}"))
    print("5. seeded organisms:", delete(f"organisms?created_by=like.{like_org}"))


if __name__ == "__main__":
    main()
