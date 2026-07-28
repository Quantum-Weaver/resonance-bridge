"""
lattice_wave5_gen.py — generate the Wave 5 seed (classification_paths
+ steps: the twelve authored tellings) for KP's eye.

Born 2026-07-27, the lattice night. READ-ONLY. Source:
classifier.ts LINNAEAN_ASSIGNMENTS — twelve complete 8-deep paths,
each becoming ONE authored claim (a telling ABOUT the lattice) with
eight ordered steps. QuantumWeaverPartner's claim carries the PREBUILT
confidence (0.95) and systemCoherence (0.92) — the only path the old
code scored; the others carry no invented numbers.

Depth-8 binds HERE and only here (the sitting's resolution): every
claim in this file proves all eight rungs or does not enter.
"""

import json
import re
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
GAIA = Path(r"C:\_superposition\resonance-ziggy\modules\cosmic\gaia")
OUT = Path(r"C:\_superposition\resonance-grammar\seeds\lattice\wave-5-paths.json")

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


def parse_assignments() -> dict:
    """{SpeciesName: {rank: member}} from LINNAEAN_ASSIGNMENTS."""
    text = (GAIA / "classifier.ts").read_text(encoding="utf-8")
    block = text.split("LINNAEAN_ASSIGNMENTS", 1)[1].split("// ===", 1)[0]
    out = {}
    for m in re.finditer(r"(\w+):\s*\{([^}]+)\}", block):
        species_key, body = m.group(1), m.group(2)
        entry = dict(re.findall(r"(\w+):\s*'([^']+)'", body))
        if len(entry) == 8:
            out[species_key] = entry
    return out


def main() -> None:
    env = load_env()
    url = env["SUPABASE_URL_KNOWLEDGE"]
    key = (env.get("SUPABASE_PUBLISHABLE_KEY_KNOWLEDGE", "")
           or env.get("SUPABASE_ANON_KEY_KNOWLEDGE", ""))
    live = set()
    for t in ("atoms", "molecules", "organisms"):
        live |= fetch_names(url, key, t)

    paths = parse_assignments()
    claims, incomplete = [], []
    for species, p in paths.items():
        steps = []
        missing = []
        for i, rank in enumerate(LADDER, start=1):
            member = p[rank]
            if member not in live:
                missing.append(member)
            steps.append({"position": i, "scheme": rank.capitalize(),
                          "member": member})
        if missing:
            incomplete.append({"subject": p["species"], "missing": missing})
            continue  # depth-8 binds here: no partial claims enter
        claim = {
            "subject": p["species"],
            "confidence": None,
            "system_coherence": None,
            "asserted_by": "gaia classifier.ts LINNAEAN_ASSIGNMENTS",
            "classifier_version": "SovereignSanctuary daw-2026-07-13 carry",
            "derivation": None,
            "status": "published",
            "steps": steps,
        }
        if p["species"] == "QuantumWeaverPartner":
            claim["confidence"] = 0.95
            claim["system_coherence"] = 0.92
            claim["derivation"] = ("PREBUILT_IDENTIFICATIONS.QuantumWeaver — "
                                   "matching traits: sovereign, multi-stream, "
                                   "quantum, collaborative, pattern-recognition")
        claims.append(claim)

    seed = {
        "_for_kps_eye": [
            "WAVE 5 — CLASSIFICATION_PATHS: the twelve authored tellings.",
            "Each claim is the classifier's own 8-deep path, all rungs proven living",
            "  (depth-8 binds here and only here — no partial claim enters).",
            "QuantumWeaverPartner carries the PREBUILT confidence 0.95 / coherence 0.92 —",
            "  the only path the old code scored; no other numbers are invented.",
            "asserted_by/classifier_version record the provenance: these are the code's",
            "  tellings, carried — not fresh judgments.",
            "Your clearance publishes the wave (ruling 5).",
        ],
        "seeded_by": "Fable via KP - the lattice night, 2026-07-27",
        "paths": claims,
        "incomplete": incomplete,
    }
    OUT.write_text(json.dumps(seed, ensure_ascii=False, indent=1),
                   encoding="utf-8")

    print(f"paths parsed   : {len(paths)}")
    print(f"claims staged  : {len(claims)}  (each with 8 steps)")
    print(f"incomplete     : {len(incomplete)}  (expected 0 — all members landed in Wave 2)")
    scored = [c for c in claims if c["confidence"] is not None]
    print(f"scored claims  : {len(scored)}  ({scored[0]['subject'] if scored else '-'})")
    print(f"\nseed file for KP's eye : {OUT}")


if __name__ == "__main__":
    main()
