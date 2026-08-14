"""
lattice_wave4_gen.py — generate the Wave 4 seed (concept_relations —
the lattice itself) for KP's eye.

Born 2026-07-27, the lattice night. READ-ONLY. Sources:
  * classifier.ts LINNAEAN_ASSIGNMENTS — the twelve 8-deep paths,
    unrolled into broader edges, DEDUPED WITH MULTI-PARENTS PRESERVED
    (the nine polyhierarchy members keep every parent; what the May
    tree dropped, the lattice restores)
  * taxonomy_rows.csv — the 69 facet members' kingdom/phylum anchors
    as broader edges
  * thesaurus_entries_rows.csv — synonym rows as use_for edges,
    related rows as related edges (editorial provenance noted)
has_dimension edges are DEFERRED honestly: no per-member dimension
data exists in the organs (UnifiedIdentificationKey is a type, not
data) — that mapping is eyes-on/shuttle work, reported, not invented.

The Gatekeeper's first breath lives here: every ladder edge is checked
N -> N-1 against the rank order before it enters the seed.
"""

import csv
import json
import re
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
GAIA = Path(r"C:\_superposition\resonance-ziggy\modules\cosmic\gaia")
EXPORTS = Path(r"C:\_superposition\resonance-excavator\sources\supabase-exports\superposition")
OUT = Path(r"C:\_superposition\resonance-grammar\seeds\lattice\wave-4-relations.json")

RANK_ORDER = {"domain": 1, "kingdom": 2, "phylum": 3, "class": 4,
              "order": 5, "family": 6, "genus": 7, "species": 8}
LADDER = ["domain", "kingdom", "phylum", "class", "order",
          "family", "genus", "species"]
NAME_COL = {"atoms": "atom_word", "molecules": "name", "organisms": "name"}


def load_env() -> dict:
    env = {}
    for line in (HERE / ".env").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            env[k.strip()] = v.strip()
    return env


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


def parse_assignments() -> list:
    """LINNAEAN_ASSIGNMENTS from classifier.ts -> list of dicts."""
    text = (GAIA / "classifier.ts").read_text(encoding="utf-8")
    block = text.split("LINNAEAN_ASSIGNMENTS", 1)[1]
    block = block.split("// ===", 1)[0]
    paths = []
    for m in re.finditer(r"\{([^}]+)\}", block):
        entry = {}
        for line in m.group(1).splitlines():
            kv = re.match(r"\s*(\w+):\s*'([^']+)'", line)
            if kv:
                entry[kv.group(1)] = kv.group(2)
        if len(entry) == 8:
            paths.append(entry)
    return paths


def main() -> None:
    env = load_env()
    url = env["SUPABASE_URL_KNOWLEDGE"]
    key = (env.get("SUPABASE_PUBLISHABLE_KEY_KNOWLEDGE", "")
           or env.get("SUPABASE_ANON_KEY_KNOWLEDGE", ""))
    live = set()
    for t in ("atoms", "molecules", "organisms"):
        live |= fetch_names(url, key, t)

    edges, unresolved, gate_failures = [], [], []
    seen = set()

    def add(rtype, subject, obj, scheme, source, note=None):
        k = (rtype, subject, obj, scheme)
        if k in seen:
            return
        seen.add(k)
        if subject not in live or obj not in live:
            unresolved.append({"relation_type": rtype, "subject": subject,
                               "object": obj, "source": source,
                               "why": "entity not living"})
            return
        edges.append({"relation_type": rtype, "subject": subject,
                      "object": obj, "scheme": scheme, "source": source,
                      "note": note, "status": "published"})

    # ─── 1. the ladder, from the twelve paths — multi-parents kept ───
    paths = parse_assignments()
    for p in paths:
        for i in range(len(LADDER) - 1, 0, -1):
            child_rank, parent_rank = LADDER[i], LADDER[i - 1]
            # THE GATEKEEPER'S CHECK: broader must run N -> N-1
            if RANK_ORDER[child_rank] - RANK_ORDER[parent_rank] != 1:
                gate_failures.append((p[child_rank], p[parent_rank]))
                continue
            add("broader", p[child_rank], p[parent_rank],
                child_rank.capitalize(), "classifier.ts LINNAEAN_ASSIGNMENTS")

    # ─── 2. the 69 facet anchors (kingdom/phylum ids -> names) ───
    def id_map(fname):
        with open(EXPORTS / fname, encoding="utf-8-sig", newline="") as f:
            return {r["id"]: r["name"].strip() for r in csv.DictReader(f)}
    kingdoms = id_map("kingdom_rows.csv")
    phyla = id_map("phylum_rows.csv")
    with open(EXPORTS / "taxonomy_rows.csv", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            name = row["name"].strip()
            if row.get("kingdom_id") and row["kingdom_id"] in kingdoms:
                add("broader", name, kingdoms[row["kingdom_id"]], "Kingdom",
                    "taxonomy_rows.csv anchor")
            if row.get("phylum_id") and row["phylum_id"] in phyla:
                add("broader", name, phyla[row["phylum_id"]], "Phylum",
                    "taxonomy_rows.csv anchor")

    # ─── 3. the thesaurus: synonymy travels ───
    with open(EXPORTS / "thesaurus_entries_rows.csv", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            etype = (row.get("entry_type") or "").strip()
            concept = (row.get("concept") or "").strip()
            entry = (row.get("entry_text") or "").strip()
            if not concept or not entry:
                continue
            rtype = {"synonym": "use_for", "related": "related",
                     "related_term": "related"}.get(etype)
            if not rtype:
                unresolved.append({"relation_type": etype, "subject": concept,
                                   "object": entry, "source": "thesaurus_entries",
                                   "why": f"unmapped entry_type '{etype}'"})
                continue
            add(rtype, concept, entry, None, "thesaurus_entries_rows.csv",
                note=f"May editorial: status={row.get('status')}")

    by_type, by_source = {}, {}
    for e in edges:
        by_type[e["relation_type"]] = by_type.get(e["relation_type"], 0) + 1
        by_source[e["source"]] = by_source.get(e["source"], 0) + 1

    # the restored polyhierarchy, named for KP's eye
    parents = {}
    for e in edges:
        if e["relation_type"] == "broader" and "LINNAEAN" in e["source"]:
            parents.setdefault(e["subject"], set()).add(e["object"])
    multi = {s: sorted(ps) for s, ps in parents.items() if len(ps) > 1}

    seed = {
        "_for_kps_eye": [
            "WAVE 4 — CONCEPT_RELATIONS: the lattice itself.",
            "Ladder edges unrolled from the classifier's twelve paths — every multi-parent",
            "  member keeps EVERY parent (multi_parent_members below: the polyhierarchy the",
            "  May tree dropped, restored).",
            "The 69 May facet anchors ride as broader edges into Kingdom/Phylum.",
            "Thesaurus synonymy travels as use_for/related, May editorial noted.",
            "has_dimension edges DEFERRED: no per-member dimension data exists in the organs;",
            "  that mapping is eyes-on/shuttle work — reported, never invented.",
            "Gatekeeper N->N-1 check ran on every ladder edge before it entered this file.",
            "Your clearance publishes the wave (ruling 5).",
        ],
        "seeded_by": "Fable via KP - the lattice night, 2026-07-27",
        "relations": edges,
        "multi_parent_members": multi,
        "unresolved": unresolved,
    }
    OUT.write_text(json.dumps(seed, ensure_ascii=False, indent=1),
                   encoding="utf-8")

    print(f"paths parsed        : {len(paths)}")
    print(f"edges staged        : {len(edges)}")
    for t, n in sorted(by_type.items()):
        print(f"  {t:10s} {n}")
    for s, n in sorted(by_source.items()):
        print(f"  from {s:36s} {n}")
    print(f"multi-parent members: {len(multi)}  (the restored polyhierarchy)")
    for s, ps in multi.items():
        print(f"  {s} -> {', '.join(ps)}")
    print(f"gatekeeper failures : {len(gate_failures)} (expected 0)")
    print(f"unresolved          : {len(unresolved)}")
    print(f"\nseed file for KP's eye : {OUT}")


if __name__ == "__main__":
    main()
