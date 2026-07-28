"""
lattice_seeder.py — deliver lattice seed waves into resonance-knowledge.

Born 2026-07-27, the lattice night, sibling of grammar_seeder.py and
bound by the same consent gate: uses SUPABASE_SECRET_KEY_KNOWLEDGE
(service role, bypasses RLS) and therefore WRITES ONLY AT KP'S EXPLICIT
WORD, with --deliver. Without the flag it is a dry run: reads the seed
file, reads the live base, reports exactly what WOULD travel, writes
nothing.

Wave 1 (schemes): two passes — insert all schemes first, then patch the
rank rows' contract FKs (ontology_axis / taxonomy_facet / dimension) by
name lookup. Idempotent by name: existing schemes are skipped, never
updated — published rows are sacred. Status rides from the seed file
(ruling 5: KP's eye on the seed file clears the wave to 'published';
shuttle drafts will always say 'submitted').

Usage:
  python lattice_seeder.py <seed-file.json>            # dry run
  python lattice_seeder.py <seed-file.json> --deliver  # at KP's word
"""

import json
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent

# fields in the seed file that are for KP's eye only — never sent
REVIEW_ONLY = {"members_preview"}
# seed-file fields resolved to FK columns in pass two
CONTRACT = {
    "ontology_axis_scheme": "ontology_axis_scheme_id",
    "taxonomy_facet_scheme": "taxonomy_facet_scheme_id",
    "dimension_scheme": "dimension_scheme_id",
}


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
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                raw = r.read().decode()
                return json.loads(raw) if raw else None
        except urllib.error.HTTPError as e:
            msg = e.read().decode()[:500]
            print(("\n%d from PostgREST: %s" % (e.code, msg))
                  .encode("ascii", "backslashreplace").decode("ascii"))
            raise

    def existing_schemes(self) -> dict:
        """name -> id for every scheme already in the base (any status)."""
        rows = self._req("GET", "schemes?select=id,name&limit=1000") or []
        return {r["name"]: r["id"] for r in rows}

    def insert(self, rows: list) -> list:
        return self._req("POST", "schemes", body=rows,
                         headers={"Prefer": "return=representation"}) or []

    def patch_scheme(self, scheme_id: str, body: dict) -> None:
        self._req("PATCH", f"schemes?id=eq.{scheme_id}", body=body,
                  headers={"Prefer": "return=minimal"})


NAME_COL = {"atoms": "atom_word", "molecules": "name", "organisms": "name"}
BATCH = 500


def deliver_members(base, seed, provenance, deliver: bool) -> None:
    """Wave 2: the framework members enter the Grammar's own tables.
    Entity rows only — bonds await their own wave (constituent atoms
    are not yet complete; the intake/shuttle owns that tail)."""
    tiers = [
        ("atoms",     seed.get("new_atoms_from_dimensions", [])
                      + seed.get("new_atoms_from_ranks", [])),
        ("molecules", seed.get("new_molecules", [])),
        ("organisms", seed.get("new_organisms", [])),
    ]
    for table, entries in tiers:
        col = NAME_COL[table]
        live = set()
        page = 0
        while True:
            rows = base._req("GET", f"{table}?select={col}&limit=1000&offset={page*1000}") or []
            live.update(r[col] for r in rows)
            if len(rows) < 1000:
                break
            page += 1
        new = [e for e in entries if e["name"] not in live]
        print(f"{table:10s} seed {len(entries):4d} | live {len(live):5d} | "
              f"to insert {len(new):4d} | skip {len(entries) - len(new)}")
        if not deliver or not new:
            continue
        # triad created_by is uuid (auth id), unlike the lattice tables'
        # text — provenance lives in the seed file, not the row.
        # atoms.atom_type is NOT NULL; ground truth read live 2026-07-27:
        # every living dimension-value atom is 'root' (census: root 1613 ·
        # modifier 263 · joiner 50 · prefix 8 · suffix 1 — no 'acronym'
        # label yet; the eyes-on wave will need one, noted for 008).
        payload = [{col: e["name"],
                    "definition": e.get("definition") or None} for e in new]
        if table == "atoms":
            for p in payload:
                p["atom_type"] = "root"
        # molecules.molecule_type is NOT NULL; ground truth read live
        # 2026-07-27: the framework's own collision rows
        # (ArchitectureDomain, ConsciousnessDomain) are composite_type /
        # PascalCase — the new framework names are the same kind.
        if table == "molecules":
            for p in payload:
                p["molecule_type"] = "composite_type"
                p["naming_convention"] = "PascalCase"
        done = 0
        for i in range(0, len(payload), BATCH):
            base._req("POST", table, body=payload[i:i + BATCH],
                      headers={"Prefer": "return=minimal"})
            done += len(payload[i:i + BATCH])
        print(f"{'':10s} inserted {done}")
    if not deliver:
        print("\nDRY RUN — nothing written. Deliver with --deliver at KP's word.")
    else:
        print("\nDelivered. Verify through the PUBLIC door now: "
              "python grammar_inventory.py")


def fetch_id_map(base, table: str) -> dict:
    """name -> id for a whole table (service key: sees every status)."""
    col = NAME_COL.get(table, "name")
    out, page = {}, 0
    while True:
        rows = base._req("GET", f"{table}?select=id,{col}&limit=1000&offset={page*1000}") or []
        for r in rows:
            out[r[col]] = r["id"]
        if len(rows) < 1000:
            return out
        page += 1


def deliver_memberships(base, seed, provenance, deliver: bool) -> None:
    """Wave 3: entity ∈ scheme. Names resolve to ids here; an entity
    found in more than one tier is a conflict for KP's eye, skipped."""
    schemes = base.existing_schemes()
    tiers = {t: fetch_id_map(base, t) for t in ("atoms", "molecules", "organisms")}
    col_for = {"atoms": "atom_id", "molecules": "molecule_id",
               "organisms": "organism_id"}

    # already-home memberships: (scheme_id, entity ids) triplets
    have = set()
    page = 0
    while True:
        rows = base._req("GET", "scheme_memberships?select=scheme_id,atom_id,"
                         f"molecule_id,organism_id&limit=1000&offset={page*1000}") or []
        for r in rows:
            have.add((r["scheme_id"], r["atom_id"], r["molecule_id"], r["organism_id"]))
        if len(rows) < 1000:
            break
        page += 1

    payload, conflicts, unresolved, skips = [], [], [], 0
    for m in seed["memberships"]:
        sid = schemes.get(m["scheme"])
        if not sid:
            unresolved.append({**m, "why": "scheme not found"})
            continue
        hits = [(t, ids[m["entity"]]) for t, ids in tiers.items()
                if m["entity"] in ids]
        if not hits:
            unresolved.append({**m, "why": "entity not living"})
            continue
        if len(hits) > 1:
            conflicts.append({**m, "tiers": [h[0] for h in hits]})
            continue
        tier, eid = hits[0]
        row = {"scheme_id": sid, "atom_id": None, "molecule_id": None,
               "organism_id": None, col_for[tier]: eid,
               "is_primary": m.get("is_primary", False),
               "status": m.get("status", "submitted"),
               "submitted_by": provenance, "created_by": provenance}
        key = (sid, row["atom_id"], row["molecule_id"], row["organism_id"])
        if key in have:
            skips += 1
            continue
        have.add(key)
        payload.append(row)

    print(f"memberships in seed : {len(seed['memberships'])}")
    print(f"to insert           : {len(payload)}")
    print(f"already home        : {skips}")
    print(f"unresolved          : {len(unresolved)}")
    print(f"tier conflicts      : {len(conflicts)}"
          + (f"  !! for KP's eye: {[c['entity'] for c in conflicts][:10]}" if conflicts else ""))
    if not deliver:
        print("\nDRY RUN — nothing written. Deliver with --deliver at KP's word.")
        return
    done = 0
    for i in range(0, len(payload), BATCH):
        base._req("POST", "scheme_memberships", body=payload[i:i + BATCH],
                  headers={"Prefer": "return=minimal"})
        done += len(payload[i:i + BATCH])
    print(f"\ninserted {done}. Verify through the PUBLIC door now: "
          "python grammar_inventory.py")


def deliver_relations(base, seed, provenance, deliver: bool) -> None:
    """Wave 4: the typed edges — the lattice itself. Subject and object
    resolve by name across the three tiers; a name living in more than
    one tier is a conflict for KP's eye, skipped, never guessed."""
    schemes = base.existing_schemes()
    tiers = {t: fetch_id_map(base, t) for t in ("atoms", "molecules", "organisms")}
    subj_col = {"atoms": "subject_atom_id", "molecules": "subject_molecule_id",
                "organisms": "subject_organism_id"}
    obj_col = {"atoms": "object_atom_id", "molecules": "object_molecule_id",
               "organisms": "object_organism_id"}

    have = set()
    page = 0
    while True:
        rows = base._req(
            "GET", "concept_relations?select=relation_type,subject_atom_id,"
            "subject_molecule_id,subject_organism_id,object_atom_id,"
            f"object_molecule_id,object_organism_id,scheme_id&limit=1000&offset={page*1000}") or []
        for r in rows:
            have.add((r["relation_type"], r["subject_atom_id"],
                      r["subject_molecule_id"], r["subject_organism_id"],
                      r["object_atom_id"], r["object_molecule_id"],
                      r["object_organism_id"], r["scheme_id"]))
        if len(rows) < 1000:
            break
        page += 1

    def resolve(name):
        hits = [(t, ids[name]) for t, ids in tiers.items() if name in ids]
        return hits

    payload, conflicts, unresolved, skips = [], [], [], 0
    for rel in seed["relations"]:
        s_hits, o_hits = resolve(rel["subject"]), resolve(rel["object"])
        if not s_hits or not o_hits:
            unresolved.append({**rel, "why": "entity not living"})
            continue
        if len(s_hits) > 1 or len(o_hits) > 1:
            conflicts.append({**rel,
                              "subject_tiers": [h[0] for h in s_hits],
                              "object_tiers": [h[0] for h in o_hits]})
            continue
        sid = schemes.get(rel["scheme"]) if rel.get("scheme") else None
        if rel.get("scheme") and sid is None:
            unresolved.append({**rel, "why": "scheme not found"})
            continue
        row = {"relation_type": rel["relation_type"],
               "subject_atom_id": None, "subject_molecule_id": None,
               "subject_organism_id": None, "object_atom_id": None,
               "object_molecule_id": None, "object_organism_id": None,
               "scheme_id": sid, "note": rel.get("note"),
               "status": rel.get("status", "submitted"),
               "submitted_by": provenance, "created_by": provenance}
        row[subj_col[s_hits[0][0]]] = s_hits[0][1]
        row[obj_col[o_hits[0][0]]] = o_hits[0][1]
        key = (row["relation_type"], row["subject_atom_id"],
               row["subject_molecule_id"], row["subject_organism_id"],
               row["object_atom_id"], row["object_molecule_id"],
               row["object_organism_id"], row["scheme_id"])
        if key in have:
            skips += 1
            continue
        have.add(key)
        payload.append(row)

    print(f"relations in seed : {len(seed['relations'])}")
    print(f"to insert         : {len(payload)}")
    print(f"already home      : {skips}")
    print(f"unresolved        : {len(unresolved)}")
    print(f"tier conflicts    : {len(conflicts)}"
          + (f"  !! {[c['subject'] + '->' + c['object'] for c in conflicts][:6]}" if conflicts else ""))
    if not deliver:
        print("\nDRY RUN — nothing written. Deliver with --deliver at KP's word.")
        return
    done = 0
    for i in range(0, len(payload), BATCH):
        base._req("POST", "concept_relations", body=payload[i:i + BATCH],
                  headers={"Prefer": "return=minimal"})
        done += len(payload[i:i + BATCH])
    print(f"\ninserted {done}. Verify through the PUBLIC door now: "
          "python grammar_inventory.py")


def deliver_paths(base, seed, provenance, deliver: bool) -> None:
    """Wave 5: authored claims + their eight ordered steps. Depth-8 is
    re-proven at delivery: a claim missing any rung's entity does not
    fly, and says so."""
    schemes = base.existing_schemes()
    tiers = {t: fetch_id_map(base, t) for t in ("atoms", "molecules", "organisms")}
    ecol = {"atoms": "atom_id", "molecules": "molecule_id",
            "organisms": "organism_id"}
    scol = {"atoms": "subject_atom_id", "molecules": "subject_molecule_id",
            "organisms": "subject_organism_id"}
    mcol = {"atoms": "member_atom_id", "molecules": "member_molecule_id",
            "organisms": "member_organism_id"}

    def resolve(name):
        return [(t, ids[name]) for t, ids in tiers.items() if name in ids]

    # existing claims: (subject ids, asserted_by) — idempotency key
    have = set()
    rows = base._req("GET", "classification_paths?select=subject_atom_id,"
                     "subject_molecule_id,subject_organism_id,asserted_by"
                     "&limit=1000") or []
    for r in rows:
        have.add((r["subject_atom_id"], r["subject_molecule_id"],
                  r["subject_organism_id"], r["asserted_by"]))

    ready, problems, skips = [], [], 0
    for c in seed["paths"]:
        s_hits = resolve(c["subject"])
        if len(s_hits) != 1:
            problems.append({"subject": c["subject"],
                             "why": "subject unresolved or multi-tier"})
            continue
        step_rows, broken = [], []
        for st in c["steps"]:
            m_hits = resolve(st["member"])
            sid = schemes.get(st["scheme"])
            if len(m_hits) != 1 or not sid:
                broken.append(st["member"])
                continue
            row = {"position": st["position"], "scheme_id": sid,
                   "member_atom_id": None, "member_molecule_id": None,
                   "member_organism_id": None}
            row[mcol[m_hits[0][0]]] = m_hits[0][1]
            step_rows.append(row)
        if broken or len(step_rows) != 8:
            problems.append({"subject": c["subject"],
                             "why": f"depth-8 unproven: {broken}"})
            continue
        subj = {"subject_atom_id": None, "subject_molecule_id": None,
                "subject_organism_id": None}
        subj[scol[s_hits[0][0]]] = s_hits[0][1]
        key = (subj["subject_atom_id"], subj["subject_molecule_id"],
               subj["subject_organism_id"], c.get("asserted_by"))
        if key in have:
            skips += 1
            continue
        ready.append((c, subj, step_rows))

    print(f"claims in seed : {len(seed['paths'])}")
    print(f"ready to fly   : {len(ready)}  (8 proven rungs each)")
    print(f"already home   : {skips}")
    print(f"problems       : {len(problems)}"
          + (f"  !! {problems[:3]}" if problems else ""))
    if not deliver:
        print("\nDRY RUN — nothing written. Deliver with --deliver at KP's word.")
        return
    for c, subj, step_rows in ready:
        body = {**subj,
                "confidence": c.get("confidence"),
                "system_coherence": c.get("system_coherence"),
                "asserted_by": c.get("asserted_by"),
                "classifier_version": c.get("classifier_version"),
                "derivation": c.get("derivation"),
                "status": c.get("status", "submitted"),
                "submitted_by": provenance, "created_by": provenance}
        inserted = base._req("POST", "classification_paths", body=[body],
                             headers={"Prefer": "return=representation"})
        pid = inserted[0]["id"]
        for row in step_rows:
            row["path_id"] = pid
        base._req("POST", "classification_path_steps", body=step_rows,
                  headers={"Prefer": "return=minimal"})
    print(f"\ninserted {len(ready)} claims x 8 steps. Verify through the "
          "PUBLIC door now: python grammar_inventory.py")


def deliver_enrichment(base, seed, provenance, deliver: bool) -> None:
    """Wave 6: fill-empty PATCHes into attached shells; insert-and-
    attach for molecules/organisms (primacy is attachment — KP's law).
    Re-checks emptiness at delivery: the fill-empty law is enforced
    against the base as it IS, not as the seed remembered it."""
    fills = seed.get("atom_fills", [])
    inserts = seed.get("inserts", [])

    # ground truth read live 2026-07-27: this base's enrichment tables
    # are LEANER than May's — no color_name on sensory; etymology keeps
    # only root_word/root_language/historical_meaning/sanctuary_meaning.
    # May-only fields are dropped and counted, never guessed into place.
    LIVE_COLS = {
        "sensory_lexicon": {"emoji", "color_hex", "sound_description",
                            "sound_file_url", "sound_tone", "sound_pitch",
                            "sound_frequency", "sound_timbre", "temperature",
                            "texture", "shape", "movement", "taste", "smell"},
        # root_language EXCLUDED for now: it is a Postgres enum
        # ('language') whose labels cannot be learned from data (all
        # 1,949 live shells are null) — and May's compound values
        # ("Latin + Old English") likely outrun it. Parked pending
        # KP's pg_enum listing; a follow-up patch delivers what fits.
        "etymology": {"root_word", "historical_meaning",
                      "sanctuary_meaning"},
    }
    n_dropped = 0

    n_patched, n_skipped_fields, n_attached, n_blocked = 0, 0, 0, 0
    if not deliver:
        n_sf = sum(1 for e in fills if "sensory_fill" in e)
        n_ef = sum(1 for e in fills if "etymology_fill" in e)
        n_si = sum(1 for e in inserts if "sensory_insert" in e)
        n_ei = sum(1 for e in inserts if "etymology_insert" in e)
        print(f"atom shell fills : {len(fills)} (sensory {n_sf} | etymology {n_ef})")
        print(f"insert-and-attach: {len(inserts)} (sensory {n_si} | etymology {n_ei})")
        print("\nDRY RUN — nothing written. Deliver with --deliver at KP's word.")
        return

    # ─── fills: re-verify emptiness field by field, then PATCH ───
    for e in fills:
        for kind, table in (("sensory_fill", "sensory_lexicon"),
                            ("etymology_fill", "etymology")):
            f = e.get(kind)
            if not f:
                continue
            row_id = f["row_id"]
            live = base._req("GET", f"{table}?id=eq.{row_id}&select=*")
            if not live:
                continue
            live = live[0]
            allowed = LIVE_COLS[table]
            body = {k: v for k, v in f.items() if k != "row_id"
                    and k in allowed
                    and not (str(live.get(k)).strip()
                             if live.get(k) is not None else "")}
            n_dropped += sum(1 for k in f if k != "row_id" and k not in allowed)
            n_skipped_fields += (len(f) - 1) - len(body)
            if body:
                base._req("PATCH", f"{table}?id=eq.{row_id}", body=body,
                          headers={"Prefer": "return=minimal"})
                n_patched += 1

    # ─── inserts: new enrichment rows, attached as primary ───
    att_col = {"sensory_insert": ("sensory_lexicon", "sensory_override"),
               "etymology_insert": ("etymology", "etymology_id")}
    for e in inserts:
        table_entity = e["tier"]  # molecules | organisms
        for kind, (table, attach) in att_col.items():
            content = e.get(kind)
            if not content:
                continue
            # re-check: attachment still empty?
            ent = base._req("GET", f"{table_entity}?id=eq.{e['entity_id']}"
                            f"&select=id,{attach}")
            if not ent or ent[0].get(attach):
                continue
            allowed = LIVE_COLS[table]
            n_dropped += sum(1 for k in content if k not in allowed)
            content = {k: v for k, v in content.items() if k in allowed}
            if not content:
                continue
            try:
                made = base._req("POST", table, body=[content],
                                 headers={"Prefer": "return=representation"})
            except urllib.error.HTTPError:
                # atom_id NOT NULL: this base's enrichment tables are
                # atom-bound; higher-tier rows wait on KP's ruling
                # (make atom_id nullable, or another home). Blocked,
                # counted, never forced.
                n_blocked += 1
                continue
            base._req("PATCH", f"{table_entity}?id=eq.{e['entity_id']}",
                      body={attach: made[0]["id"]},
                      headers={"Prefer": "return=minimal"})
            n_attached += 1

    print(f"shells patched      : {n_patched}")
    print(f"fields skipped (now non-empty): {n_skipped_fields}")
    print(f"May-only fields dropped (no live column): {n_dropped}")
    print(f"rows inserted+attached as primary: {n_attached}")
    print(f"higher-tier rows BLOCKED (atom_id NOT NULL — awaits KP's ruling): {n_blocked}")
    print("\nDelivered. Verify through the PUBLIC door now: "
          "python grammar_inventory.py")


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit("usage: python lattice_seeder.py <seed-file.json> [--deliver]")
    deliver = "--deliver" in sys.argv

    seed_path = Path(args[0])
    seed = json.loads(seed_path.read_text(encoding="utf-8"))
    provenance = seed.get("seeded_by", "lattice_seeder")

    env = load_env()
    base = Base(env["SUPABASE_URL_KNOWLEDGE"],
                env["SUPABASE_SECRET_KEY_KNOWLEDGE"])

    if "atom_fills" in seed:
        deliver_enrichment(base, seed, provenance, deliver)
        return
    if "paths" in seed:
        deliver_paths(base, seed, provenance, deliver)
        return
    if "relations" in seed:
        deliver_relations(base, seed, provenance, deliver)
        return
    if "memberships" in seed:
        deliver_memberships(base, seed, provenance, deliver)
        return
    if "schemes" not in seed:
        deliver_members(base, seed, provenance, deliver)
        return

    schemes = seed["schemes"]
    have = base.existing_schemes()

    new = [s for s in schemes if s["name"] not in have]
    skip = [s for s in schemes if s["name"] in have]
    print(f"seed file : {seed_path.name} ({len(schemes)} schemes)")
    print(f"live base : {len(have)} schemes already present")
    print(f"to insert : {len(new)}   to skip (already home): {len(skip)}")
    by_type = {}
    for s in new:
        by_type[s["scheme_type"]] = by_type.get(s["scheme_type"], 0) + 1
    for t, n in sorted(by_type.items()):
        print(f"            {t}: {n}")

    if not deliver:
        print("\nDRY RUN — nothing written. Deliver with --deliver at KP's word.")
        return

    # ─── pass one: the rows themselves (contract refs held back) ───
    # PostgREST bulk inserts demand identical key sets across rows —
    # normalize: every row carries the union of keys, absent ones null.
    payload = []
    for s in new:
        row = {k: v for k, v in s.items()
               if k not in REVIEW_ONLY and k not in CONTRACT}
        row["created_by"] = provenance
        payload.append(row)
    all_keys = set().union(*(r.keys() for r in payload)) if payload else set()
    payload = [{k: r.get(k) for k in sorted(all_keys)} for r in payload]
    if payload:
        inserted = base.insert(payload)
        print(f"\npass one: {len(inserted)} schemes inserted")
        for r in inserted:
            have[r["name"]] = r["id"]

    # ─── pass two: the rank contract, resolved by name ───
    patched = 0
    for s in schemes:
        refs = {col: have.get(s[field])
                for field, col in CONTRACT.items() if s.get(field)}
        if not refs:
            continue
        missing = [f for f in CONTRACT if s.get(f) and have.get(s[f]) is None]
        if missing:
            print(f"  !! {s['name']}: unresolved contract refs {missing} — left null")
            continue
        base.patch_scheme(have[s["name"]], refs)
        patched += 1
    print(f"pass two: contract FKs patched on {patched} rank schemes")
    print("\nDelivered. Verify through the PUBLIC door now: "
          "python grammar_inventory.py  (schemes should read 41)")


if __name__ == "__main__":
    main()
