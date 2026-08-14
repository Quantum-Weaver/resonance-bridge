"""
lattice_wave2_gen.py — generate the Wave 2 seed file (the framework
members entering the Grammar's own tables) for KP's eye.

Born 2026-07-27, the lattice night. READ-ONLY: reads the superposition
export CSVs (descriptions carried VERBATIM, never invented), reads the
live base through the ANON door for existence checks, writes only the
seed file. Delivery is a separate act, a separate word.

Laws applied here:
  * word-count classification by the Grammar's decomposition law
    (camelCase splits at capitals; digits exempt)
  * the ACRONYM ruling (KP, 2026-07-27): acronym-bearing names are
    EXCLUDED from this scripted wave — flagged for the eyes-on wave
  * the MERGE ruling: names already living in the Grammar are skipped,
    their gaia description carried in a note for KP's per-name eye
  * dimension values (identification-key.ts) become atoms; their
    definitions are DRAFTED and say so
"""

import csv
import json
import re
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPORTS = Path(r"C:\_superposition\resonance-excavator\sources\supabase-exports\superposition")
WAVE1 = Path(r"C:\_superposition\resonance-grammar\seeds\lattice\wave-1-schemes.json")
OUT = Path(r"C:\_superposition\resonance-grammar\seeds\lattice\wave-2-members.json")

RANK_FILES = ["domain", "kingdom", "phylum", "class", "order",
              "family", "genus", "species"]


def load_env() -> dict:
    env = {}
    for line in (HERE / ".env").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            env[k.strip()] = v.strip()
    return env


def split_words(name: str) -> list:
    """The Grammar's decomposition law: underscore/hyphen first,
    camelCase at capitals, digits exempt."""
    parts = re.split(r"[_\-\s]+", name)
    words = []
    for p in parts:
        words.extend(re.findall(r"[A-Z]+(?=[A-Z][a-z])|[A-Z]?[a-z]+[0-9]*|[A-Z]+[0-9]*", p))
    return [w for w in words if w]


def has_acronym(name: str) -> bool:
    """An embedded run of 2+ capitals (CSSValue, UIState) — KP's
    ruling: these enter intentionally, eyes-on, never by script."""
    return bool(re.search(r"[A-Z]{2,}", name))


# ground truth, read from the base (the ritual's law): atoms carry
# their word in atom_word, not name
NAME_COL = {"atoms": "atom_word", "molecules": "name", "organisms": "name"}


def fetch_names(url: str, key: str, table: str) -> set:
    col = NAME_COL[table]
    names, page = set(), 0
    while True:
        req = urllib.request.Request(
            f"{url}/rest/v1/{table}?select={col}&limit=1000&offset={page * 1000}",
            headers={"apikey": key, "Authorization": f"Bearer {key}"})
        with urllib.request.urlopen(req, timeout=30) as r:
            batch = json.loads(r.read().decode("utf-8"))
        names.update(row[col] for row in batch)
        if len(batch) < 1000:
            return names
        page += 1


def main() -> None:
    env = load_env()
    url = env["SUPABASE_URL_KNOWLEDGE"]
    key = (env.get("SUPABASE_PUBLISHABLE_KEY_KNOWLEDGE", "")
           or env.get("SUPABASE_ANON_KEY_KNOWLEDGE", ""))

    live = {t: fetch_names(url, key, t)
            for t in ("atoms", "molecules", "organisms")}
    live_atoms_lower = {n.lower() for n in live["atoms"]}

    # ─── the rank members, descriptions verbatim from the CSVs ───
    members = []
    for rank in RANK_FILES:
        path = EXPORTS / f"{rank}_rows.csv"
        with open(path, encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                members.append({"name": row["name"].strip(),
                                "description": (row.get("description") or "").strip(),
                                "source": f"{rank}_rows.csv",
                                "rank_scheme": rank.capitalize()})

    # ─── the facet members (taxonomy_rows.csv), same law, same care ───
    seen_names = {m["name"] for m in members}
    with open(EXPORTS / "taxonomy_rows.csv", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            name = row["name"].strip()
            if name and name not in seen_names:
                seen_names.add(name)
                members.append({"name": name,
                                "description": (row.get("description") or "").strip(),
                                "source": "taxonomy_rows.csv",
                                "rank_scheme": None})

    atoms, molecules, organisms, skipped, eyes_on = [], [], [], [], []
    for m in members:
        if has_acronym(m["name"]):
            eyes_on.append({**m, "why": "acronym-bearing — eyes-on wave, per KP's ruling"})
            continue
        words = split_words(m["name"])
        tier = ("atoms" if len(words) == 1
                else "molecules" if len(words) == 2 else "organisms")
        if m["name"] in live[tier]:
            skipped.append({**m, "already_in": tier,
                            "note": f"gaia description for KP's eye (merge ruling): {m['description']}"})
            continue
        entry = {"name": m["name"], "definition": m["description"],
                 "source": m["source"], "rank_scheme": m["rank_scheme"],
                 "word_count": len(words), "constituents": [w.lower() for w in words]}
        {"atoms": atoms, "molecules": molecules, "organisms": organisms}[tier].append(entry)

    # ─── the dimension values become atoms (definitions drafted) ───
    wave1 = json.loads(WAVE1.read_text(encoding="utf-8"))
    dim_atoms = []
    seen = set()
    for s in wave1["schemes"]:
        if s["scheme_type"] != "dimension":
            continue
        for v in s.get("members_preview", []):
            if v in seen:
                continue
            seen.add(v)
            if v.lower() in live_atoms_lower:
                continue
            dim_atoms.append({
                "name": v,
                "definition": f"[DRAFTED by Fable — edit freely] Dimension value of the '{s['name']}' vocabulary.",
                "source": "identification-key.ts",
                "dimension_scheme": s["name"]})

    seed = {
        "_for_kps_eye": [
            "WAVE 2 — THE MEMBERS enter the Grammar's own tables (their only home).",
            "Rank-member descriptions are VERBATIM from your May CSVs — carried, never invented.",
            "Dimension-value atom definitions are DRAFTED and say so — edit freely.",
            "skipped_existing = the merge ruling applied: the standing Grammar row keeps its",
            "  definition; the gaia description rides here as a note for your per-name eye.",
            "eyes_on_wave = acronym-bearing names EXCLUDED from this scripted wave, per your ruling.",
            "Enum values (molecule_type / atom_role / bond_type) are NOT set here — the deliverer",
            "  reads ground truth from the base first, per the ritual.",
            "Your clearance publishes the wave (ruling 5).",
        ],
        "seeded_by": "Fable via KP - the lattice night, 2026-07-27",
        "new_atoms_from_dimensions": dim_atoms,
        "new_molecules": molecules,
        "new_organisms": organisms,
        "new_atoms_from_ranks": atoms,
        "skipped_existing": skipped,
        "eyes_on_wave": eyes_on,
    }
    OUT.write_text(json.dumps(seed, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"rank members read      : {len(members)}")
    print(f"new atoms (dimensions) : {len(dim_atoms)}  (of {len(seen)} values; rest already live)")
    print(f"new atoms (ranks)      : {len(atoms)}")
    print(f"new molecules          : {len(molecules)}")
    print(f"new organisms          : {len(organisms)}")
    print(f"skipped (merge ruling) : {len(skipped)}")
    print(f"eyes-on (acronyms)     : {len(eyes_on)}")
    print(f"\nseed file for KP's eye : {OUT}")


if __name__ == "__main__":
    main()
