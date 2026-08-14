"""
lattice_wave3_gen.py — generate the Wave 3 seed (scheme_memberships)
for KP's eye.

Born 2026-07-27, the lattice night. READ-ONLY: parses the gaia organs'
own type unions (the source of truth for which member belongs to which
vocabulary), checks entity existence through the ANON door, writes only
the seed file. Every membership names its scheme and its entity by
name; the deliverer resolves names to ids at delivery.

is_primary (KP's ruling: per scheme):
  * rank memberships: true (the rank dimension is a member's defining home)
  * all others: false at seed time — flips are KP's hand, per scheme
Entities not yet living in the base are NOT seeded — they are reported
as the intake/shuttle tail, per the no-silent-tails law.
"""

import json
import re
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
GAIA = Path(r"C:\_superposition\resonance-ziggy\modules\cosmic\gaia")
WAVE1 = Path(r"C:\_superposition\resonance-grammar\seeds\lattice\wave-1-schemes.json")
OUT = Path(r"C:\_superposition\resonance-grammar\seeds\lattice\wave-3-memberships.json")

RANKS = ["Domain", "Kingdom", "Phylum", "Class", "Order", "Family",
         "Genus", "Species"]
NAME_COL = {"atoms": "atom_word", "molecules": "name", "organisms": "name"}


def load_env() -> dict:
    env = {}
    for line in (HERE / ".env").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            env[k.strip()] = v.strip()
    return env


def parse_unions(path: Path, suffix: str) -> dict:
    """{VocabName: [members]} from `export type <X><suffix> = | 'a' ...`.
    Alias unions (= SomeOtherType;) return an alias marker instead."""
    text = path.read_text(encoding="utf-8")
    out = {}
    for m in re.finditer(
            rf"export type (\w+){suffix} =\s*([^;]+);", text):
        name, body = m.group(1), m.group(2)
        members = re.findall(r"'([^']+)'", body)
        if members:
            out[name] = members
        else:
            alias = re.search(r"(\w+)\s*$", body.strip())
            out[name] = {"alias": alias.group(1)} if alias else []
    return out


def fetch_names(url, key, table) -> set:
    col = NAME_COL[table]
    names, page = set(), 0
    while True:
        req = urllib.request.Request(
            f"{url}/rest/v1/{table}?select={col}&limit=1000&offset={page*1000}",
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
    all_live = live["atoms"] | live["molecules"] | live["organisms"]

    # ─── the organs' own unions ───
    ranks = parse_unions(GAIA / "linnaean.ts", "Type")     # Digital<Rank>Type
    facets = parse_unions(GAIA / "taxonomy.ts", "TaxonomyType")
    axes = parse_unions(GAIA / "ontology.ts", "OntologyType")

    memberships, missing = [], []

    def add(scheme, member, primary, source):
        if member in all_live:
            memberships.append({"scheme": scheme, "entity": member,
                                "is_primary": primary, "source": source,
                                "status": "published"})
        else:
            missing.append({"scheme": scheme, "entity": member,
                            "source": source})

    # 1. rank memberships (is_primary true — the defining home)
    for rank in RANKS:
        u = ranks.get(f"Digital{rank}")
        if isinstance(u, list):
            for member in u:
                add(rank, member, True, "linnaean.ts")

    # 2. facet memberships (aliases resolved: DomainTaxonomy -> the domains)
    for facet, u in facets.items():
        if facet == "":  # the aggregate TaxonomyType union parses empty
            continue
        scheme = f"{facet}Taxonomy"
        if isinstance(u, dict) and "alias" in u:
            target = u["alias"].replace("Digital", "").replace("Type", "")
            u = ranks.get(f"Digital{target}", [])
        if isinstance(u, list):
            for member in u:
                add(scheme, member, False, "taxonomy.ts")

    # 3. axis memberships (only for entities already living; the rest
    #    are the intake's tail)
    for axis, u in axes.items():
        if axis == "":
            continue
        scheme = f"{axis}Ontology"
        if isinstance(u, list):
            for member in u:
                add(scheme, member, False, "ontology.ts")

    # 4. dimension-value memberships
    wave1 = json.loads(WAVE1.read_text(encoding="utf-8"))
    for s in wave1["schemes"]:
        if s["scheme_type"] == "dimension":
            for v in s.get("members_preview", []):
                add(s["name"], v, False, "identification-key.ts")

    # dedupe (same scheme+entity may arrive from two organs)
    seen, unique = set(), []
    for m in memberships:
        k = (m["scheme"], m["entity"])
        if k not in seen:
            seen.add(k)
            unique.append(m)

    by_kind = {}
    for m in unique:
        by_kind[m["source"]] = by_kind.get(m["source"], 0) + 1

    seed = {
        "_for_kps_eye": [
            "WAVE 3 — SCHEME_MEMBERSHIPS: every living member into its dimensions.",
            "Sources are the gaia organs' own type unions — the code's own word on who belongs where.",
            "is_primary: TRUE on rank memberships only (per-scheme ruling); flips are your hand.",
            "missing_entities = union members not yet living in the base: the intake/shuttle tail,",
            "  reported, never silently dropped. They get memberships when they get rows.",
            "Your clearance publishes the wave (ruling 5).",
        ],
        "seeded_by": "Fable via KP - the lattice night, 2026-07-27",
        "memberships": unique,
        "missing_entities": missing,
    }
    OUT.write_text(json.dumps(seed, ensure_ascii=False, indent=1),
                   encoding="utf-8")

    print(f"memberships staged : {len(unique)}")
    for src, n in sorted(by_kind.items()):
        print(f"  from {src:24s} {n}")
    print(f"primary (rank)     : {sum(1 for m in unique if m['is_primary'])}")
    print(f"missing entities   : {len(missing)}  (the intake/shuttle tail, listed in the seed)")
    print(f"\nseed file for KP's eye : {OUT}")


if __name__ == "__main__":
    main()
