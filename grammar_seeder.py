"""
grammar_seeder.py — deliver the staged seed from the lighthouse shelf
into the resonance-knowledge Supabase.

THE CONSENT-GATED WRITE TOOL the bridge's .env notes anticipated: uses
SUPABASE_SECRET_KEY_KNOWLEDGE (service role, bypasses RLS) and
therefore RUNS ONLY AT KP'S EXPLICIT WORD, with --deliver. Without the
flag it is a dry run: reads the shelf, reads the live base, reports
exactly what WOULD travel, writes nothing.

Order per KP's ruling (THE-ALCHEMY-SPEC): full syntax (organisms,
definitions included) → molecules → atoms → junctions. Idempotent by
construction: everything existing in the base is skipped, never
updated — the curated rows are sacred. Provenance rides every row.
Delivery manifest lands in lighthouse/delivered/.
"""

import json
import sys
import urllib.request
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
SHELF = Path(r"C:\_superposition\resonance-excavator\lighthouse")
KNOWLEDGE = SHELF / "knowledge"
BATCH = 500


def load_env() -> dict:
    env = {}
    for line in (HERE / ".env").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            env[k.strip()] = v.strip()
    return env


class Base:
    def __init__(self, url: str, key: str):
        self.url, self.key = url, key

    def _req(self, method: str, path: str, body=None, headers=None):
        h = {"apikey": self.key, "Authorization": f"Bearer {self.key}",
             "Content-Type": "application/json"}
        h.update(headers or {})
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(f"{self.url}/rest/v1/{path}",
                                     data=data, headers=h, method=method)
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read().decode()
            return json.loads(raw) if raw else None

    def fetch_all(self, table: str, select: str) -> list:
        rows, page = [], 0
        while True:
            batch = self._req(
                "GET", f"{table}?select={select}&limit=1000&offset={page * 1000}")
            rows.extend(batch)
            if len(batch) < 1000:
                return rows
            page += 1

    def insert(self, table: str, rows: list, write: bool) -> int:
        if not write or not rows:
            return len(rows)
        for i in range(0, len(rows), BATCH):
            self._req("POST", table, rows[i:i + BATCH],
                      {"Prefer": "return=minimal"})
        return len(rows)


def read_stage(name: str) -> list:
    with open(KNOWLEDGE / name, encoding="utf-8") as f:
        return [json.loads(l) for l in f]


def main() -> None:
    write = "--deliver" in sys.argv
    env = load_env()
    base = Base(env["SUPABASE_URL_KNOWLEDGE"],
                env["SUPABASE_SECRET_KEY_KNOWLEDGE"])
    mode = "DELIVERY" if write else "DRY RUN (pass --deliver at KP's word)"
    print(f"mode: {mode}\n")
    manifest = {"date": date.today().isoformat(), "mode": mode, "stages": {}}

    # ── live-state maps (skip-existing is the sacredness guarantee) ──
    cats = {c["name"]: c["id"] for c in base.fetch_all("categories", "id,name")}
    have_atoms = {a["atom_word"].lower(): a["id"]
                  for a in base.fetch_all("atoms", "id,atom_word")}
    have_mols = {m["name"]: m["id"]
                 for m in base.fetch_all("molecules", "id,name")}
    have_orgs = {(o["name"], o.get("organism_type")): o["id"]
                 for o in base.fetch_all("organisms", "id,name,organism_type")}

    # ── 1. FULL SYNTAX FIRST — organisms, definitions included ──
    orgs = [o for o in read_stage("1-organisms.seed.jsonl")
            if (o["name"], o["organism_type"]) not in have_orgs]
    n = base.insert("organisms", orgs, write)
    print(f"organisms:          {n} new (existing skipped)")
    manifest["stages"]["organisms"] = n

    # ── 2. molecules ──
    mols = []
    for m in read_stage("2-molecules.seed.jsonl"):
        if m["name"] in have_mols:
            continue
        if not m.get("naming_convention"):
            m["naming_convention"] = "snake_case"
        mols.append(m)
    n = base.insert("molecules", mols, write)
    print(f"molecules:          {n} new")
    manifest["stages"]["molecules"] = n

    # ── 3. atoms — sparse, curated rows never touched ──
    atoms = []
    for a in read_stage("3-atoms.seed.jsonl"):
        if a["atom_word"].lower() in have_atoms:
            continue
        a["category"] = cats.get(a.pop("category_name", "system"))
        # atoms.created_by is a uuid (auth user), unlike organisms' text —
        # provenance for these rows lives in the definition string
        a.pop("created_by", None)
        atoms.append(a)
    n = base.insert("atoms", atoms, write)
    print(f"atoms:              {n} new (curated untouched)")
    manifest["stages"]["atoms"] = n

    # ── 4. junctions — need fresh id maps after the inserts ──
    if write:
        have_atoms = {a["atom_word"].lower(): a["id"]
                      for a in base.fetch_all("atoms", "id,atom_word")}
        have_mols = {m["name"]: m["id"]
                     for m in base.fetch_all("molecules", "id,name")}
        have_orgs = {(o["name"], o.get("organism_type")): o["id"]
                     for o in base.fetch_all("organisms", "id,name,organism_type")}
        have_ma = {(r["molecule_id"], r["atom_id"]) for r in
                   base.fetch_all("molecule_atoms", "molecule_id,atom_id")}
        have_om = {(r["organism_id"], r["molecule_id"]) for r in
                   base.fetch_all("organism_molecules", "organism_id,molecule_id")}

        ma_rows = []
        for j in read_stage("4-molecule_atoms.seed.jsonl"):
            mid = have_mols.get(j["molecule_name"])
            aid = have_atoms.get(j["atom_word"].lower())
            if mid and aid and (mid, aid) not in have_ma:
                have_ma.add((mid, aid))
                ma_rows.append({"molecule_id": mid, "atom_id": aid,
                                "position": j["position"], "role": j["role"],
                                "bond_strength": j["bond_strength"]})
        n = base.insert("molecule_atoms", ma_rows, write)
        print(f"molecule_atoms:     {n} bonds")
        manifest["stages"]["molecule_atoms"] = n

        om_rows = []
        for j in read_stage("5-organism_molecules.seed.jsonl"):
            oid = have_orgs.get((j["organism_name"], j["organism_type"]))
            mid = have_mols.get(j["molecule_name"])
            if oid and mid and (oid, mid) not in have_om:
                have_om.add((oid, mid))
                om_rows.append({"organism_id": oid, "molecule_id": mid,
                                "position": j["position"], "role": j["role"],
                                "bond_type": j["bond_type"],
                                "bond_strength": j["bond_strength"]})
        n = base.insert("organism_molecules", om_rows, write)
        print(f"organism_molecules: {n} bonds")
        manifest["stages"]["organism_molecules"] = n
    else:
        print("molecule_atoms:     (junctions resolve at delivery — ids "
              "exist only after the tiers land)")

    if write:
        out = SHELF / "delivered" / f"seed-manifest-{date.today().isoformat()}.json"
        out.write_text(json.dumps(manifest, indent=1), encoding="utf-8")
        print(f"\nmanifest: {out}")


if __name__ == "__main__":
    main()
