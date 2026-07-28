"""
lattice_wave6_gen.py — generate the Wave 6 seed (the enrichment
bridge) for KP's eye.

Born 2026-07-27, the lattice night. READ-ONLY. The laws it embodies,
all KP's, all ruled this sitting:
  * FILL-EMPTY-ONLY — May content enters only where this base is
    silent; collisions go to the conflict report, never overwritten
  * PRIMACY IS ATTACHMENT — an atom's sensory_id/etymology_id IS the
    primary telling; molecules/organisms designate theirs via
    sensory_override/etymology_id; extra tellings are folksonomy
  * the keywords table (exported by KP's own hand) is the spine:
    690 rows, 1:1 with the satellites — definitions fill-empty too
  * named-but-not-living members park WITH THEIR NAMES in the intake
    tail; nothing is silently dropped
"""

import csv
import json
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP = Path(r"C:\_superposition\resonance-excavator\sources\supabase-exports\superposition")
OUT = Path(r"C:\_superposition\resonance-grammar\seeds\lattice\wave-6-enrichment.json")

SENSORY_FIELDS = ["emoji", "color_hex", "color_name", "sound_description",
                  "sound_file_url", "sound_tone", "sound_pitch",
                  "sound_frequency", "sound_timbre", "temperature",
                  "texture", "shape", "movement", "taste", "smell"]
ETYM_FIELDS = ["root_word", "root_language", "historical_meaning",
               "evolution_notes", "prefix", "suffix", "combining_form",
               "etymon", "morpheme_breakdown", "sanctuary_meaning"]


def load_env() -> dict:
    env = {}
    for line in (HERE / ".env").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            env[k.strip()] = v.strip()
    return env


def read_csv(name):
    with open(EXP / name, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def main() -> None:
    env = load_env()
    url = env["SUPABASE_URL_KNOWLEDGE"]
    key = (env.get("SUPABASE_PUBLISHABLE_KEY_KNOWLEDGE", "")
           or env.get("SUPABASE_ANON_KEY_KNOWLEDGE", ""))

    def get_all(path):
        rows, page = [], 0
        while True:
            req = urllib.request.Request(
                f"{url}/rest/v1/{path}&limit=1000&offset={page*1000}",
                headers={"apikey": key, "Authorization": f"Bearer {key}"})
            with urllib.request.urlopen(req, timeout=60) as r:
                batch = json.loads(r.read().decode("utf-8"))
            rows.extend(batch)
            if len(batch) < 1000:
                return rows
            page += 1

    # ─── the May spine + satellites ───
    keywords = {r["id"]: r for r in read_csv("keywords_rows.csv")}
    may_sensory = {r["keyword_id"]: r for r in read_csv("sensory_lexicon_rows.csv")}
    may_etym = {r["keyword_id"]: r for r in read_csv("etymology_rows.csv")}

    # member name -> keyword_id (rank + taxonomy CSVs), then keyword
    # rows themselves fill any remainder via their own 'keyword' name
    name_to_kw = {}
    for f in ("domain", "kingdom", "phylum", "class", "order",
              "family", "genus", "species", "taxonomy"):
        for row in read_csv(f + "_rows.csv"):
            if row.get("keyword_id"):
                name_to_kw[row["name"].strip()] = row["keyword_id"]
    for kid, k in keywords.items():
        nm = (k.get("keyword") or "").strip()
        if nm and nm not in name_to_kw:
            name_to_kw[nm] = kid

    # ─── the living base ───
    atoms = {r["atom_word"]: r for r in get_all(
        "atoms?select=id,atom_word,definition,etymology_id,sensory_id")}
    mols = {r["name"]: r for r in get_all(
        "molecules?select=id,name,definition,etymology_id,sensory_override")}
    orgs = {r["name"]: r for r in get_all(
        "organisms?select=id,name,definition,etymology_id,sensory_override")}
    live_sensory = {r["id"]: r for r in get_all("sensory_lexicon?select=*")}
    live_etym = {r["id"]: r for r in get_all("etymology?select=*")}

    atom_fills, inserts, conflicts, parked = [], [], [], []

    def fills_for(live_row, may_row, fields):
        fill, clash = {}, {}
        for f in fields:
            mv = (may_row.get(f) or "").strip()
            if not mv:
                continue
            lv = live_row.get(f)
            lv = (str(lv).strip() if lv is not None else "")
            if not lv:
                fill[f] = mv
            elif lv != mv:
                clash[f] = {"live": lv, "may": mv}
        return fill, clash

    for name, kid in sorted(name_to_kw.items()):
        kw = keywords.get(kid, {})
        s_may, e_may = may_sensory.get(kid), may_etym.get(kid)

        if name in atoms:
            a = atoms[name]
            entry = {"tier": "atoms", "name": name, "atom_id": a["id"]}
            if not (a.get("definition") or "").strip() and (kw.get("definition") or "").strip():
                entry["definition_fill"] = kw["definition"].strip()
            if s_may and a.get("sensory_id") and a["sensory_id"] in live_sensory:
                fill, clash = fills_for(live_sensory[a["sensory_id"]], s_may, SENSORY_FIELDS)
                if fill:
                    entry["sensory_fill"] = {"row_id": a["sensory_id"], **fill}
                if clash:
                    conflicts.append({"tier": "atoms", "name": name,
                                      "table": "sensory_lexicon", "fields": clash})
            if e_may and a.get("etymology_id") and a["etymology_id"] in live_etym:
                fill, clash = fills_for(live_etym[a["etymology_id"]], e_may, ETYM_FIELDS)
                if fill:
                    entry["etymology_fill"] = {"row_id": a["etymology_id"], **fill}
                if clash:
                    conflicts.append({"tier": "atoms", "name": name,
                                      "table": "etymology", "fields": clash})
            if len(entry) > 3:
                atom_fills.append(entry)
            continue

        tier = "molecules" if name in mols else "organisms" if name in orgs else None
        if tier:
            m = (mols if tier == "molecules" else orgs)[name]
            entry = {"tier": tier, "name": name, "entity_id": m["id"]}
            s_content = {f: (s_may.get(f) or "").strip()
                         for f in SENSORY_FIELDS if s_may and (s_may.get(f) or "").strip()}
            e_content = {f: (e_may.get(f) or "").strip()
                         for f in ETYM_FIELDS if e_may and (e_may.get(f) or "").strip()}
            if s_content and not m.get("sensory_override"):
                entry["sensory_insert"] = s_content   # + attach as primary
            if e_content and not m.get("etymology_id"):
                entry["etymology_insert"] = e_content  # + attach as primary
            if not (m.get("definition") or "").strip() and (kw.get("definition") or "").strip():
                entry["definition_fill"] = kw["definition"].strip()
            if len(entry) > 3:
                inserts.append(entry)
            continue

        parked.append({"name": name, "keyword_id": kid,
                       "has_sensory": bool(s_may), "has_etymology": bool(e_may),
                       "definition": (kw.get("definition") or "").strip()[:120]})

    seed = {
        "_for_kps_eye": [
            "WAVE 6 — THE ENRICHMENT BRIDGE, under the fill-empty law.",
            "atom_fills: per-field fills into EXISTING shells (the attached primaries) —",
            "  only fields this base holds empty; collisions are in `conflicts`, untouched.",
            "inserts: NEW sensory/etymology rows for molecules & organisms, ATTACHED as",
            "  primary via sensory_override/etymology_id (primacy is attachment — your law).",
            "definition_fill: keyword definitions entering only where definitions are empty.",
            "parked: named members not yet living — the intake tail, with their keywords,",
            "  waiting whole. Nothing dropped, nothing dark anymore.",
            "Your clearance publishes the wave (ruling 5).",
        ],
        "seeded_by": "Fable via KP - the lattice night, 2026-07-27",
        "atom_fills": atom_fills,
        "inserts": inserts,
        "conflicts": conflicts,
        "parked": parked,
    }
    OUT.write_text(json.dumps(seed, ensure_ascii=False, indent=1),
                   encoding="utf-8")

    n_sf = sum(1 for e in atom_fills if "sensory_fill" in e)
    n_ef = sum(1 for e in atom_fills if "etymology_fill" in e)
    n_df = sum(1 for e in atom_fills + inserts if "definition_fill" in e)
    n_si = sum(1 for e in inserts if "sensory_insert" in e)
    n_ei = sum(1 for e in inserts if "etymology_insert" in e)
    print(f"atom shells to fill    : {len(atom_fills)}  (sensory {n_sf} | etymology {n_ef})")
    print(f"higher-tier inserts    : {len(inserts)}  (sensory {n_si} | etymology {n_ei})")
    print(f"definition fills       : {n_df}")
    print(f"conflicts (for KP)     : {len(conflicts)}")
    print(f"parked (intake tail)   : {len(parked)}")
    print(f"\nseed file for KP's eye : {OUT}")


if __name__ == "__main__":
    main()
