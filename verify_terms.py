"""
verify_terms.py — check whether a set of coined names is present in the
resonance-knowledge Grammar (Supabase), through the PUBLIC anon door.

Born 2026-07-27 at KP's word on the two cosmic pull-ins (Continuity Beam
system + primitives vocabulary): "we should verify the terminology within
is found in our resonance-knowledge supabase, if not plot bringing it in
after the ziggy move." Reusable for any future carry: feed it names, it
reports Grammar coverage.

READ-ONLY by construction, same posture as grammar_inventory.py: anon key
from .env beside this file, never printed.

The Grammar's own law (KP's rulings, 2026-07-26): a name decomposes by
camelCase/underscore split, digits exempt; 1 word = atom (atoms.atom_word,
lowercase) · 2 words = molecule (molecules.name, as coined) · 3+ words =
organism (organisms.name, as coined). Constituent words are also checked
against atoms, since molecules/organisms bond from them.

Usage:
  python verify_terms.py <names.json>     # {"cards":[{"card":...},...]} or ["Name", ...]
  python verify_terms.py <names.txt>      # one name per line
Output: coverage to stdout + a dated report JSON beside the input file.
"""

import json
import re
import sys
import urllib.request
import urllib.parse
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load_env() -> dict:
    env = {}
    env_path = HERE / ".env"
    if not env_path.is_file():
        sys.exit("no .env beside this script — copy .env.example and fill by hand")
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            env[k.strip()] = v.strip()
    return env


def split_words(name: str) -> list:
    """The Grammar's decomposition: underscores/hyphens divide first; an
    all-caps segment is ONE word (SCREAMING_CASE convention); mixed-case
    segments split at capitals. Digits exempt."""
    words = []
    for seg in re.split(r"[_-]", name):
        if not seg:
            continue
        if seg.isupper():
            words.append(seg.lower())
        else:
            words.extend(w.lower() for w in re.split(r"(?=[A-Z])", seg) if w)
    return [w for w in words if not w.isdigit()]


def fetch_in(base: str, key: str, table: str, column: str, values: list) -> set:
    """Which of `values` exist in table.column — batched in.() queries."""
    found = set()
    headers = {"apikey": key, "Authorization": f"Bearer {key}"}
    for i in range(0, len(values), 80):
        batch = values[i : i + 80]
        quoted = ",".join('"' + v.replace('"', '') + '"' for v in batch)
        q = urllib.parse.quote(f"in.({quoted})", safe="in.(),\"")
        url = f"{base}/rest/v1/{table}?select={column}&{column}={q}&limit=1000"
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as r:
            for row in json.loads(r.read().decode("utf-8")):
                found.add(row[column])
    return found


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    src = Path(sys.argv[1])
    raw = src.read_text(encoding="utf-8")
    if src.suffix == ".json":
        data = json.loads(raw)
        names = [c["card"] for c in data["cards"]] if isinstance(data, dict) else list(data)
    else:
        names = [l.strip() for l in raw.splitlines() if l.strip()]
    names = sorted(set(names))

    env = load_env()
    base = env.get("SUPABASE_URL_KNOWLEDGE", "").rstrip("/")
    key = env.get("SUPABASE_PUBLISHABLE_KEY_KNOWLEDGE", "") or env.get("SUPABASE_ANON_KEY_KNOWLEDGE", "")
    if not base or not key:
        sys.exit("SUPABASE_URL_KNOWLEDGE / SUPABASE_PUBLISHABLE_KEY_KNOWLEDGE missing from .env")

    by_class = {"atom": [], "molecule": [], "organism": []}
    all_words = set()
    for n in names:
        words = split_words(n)
        all_words.update(words)
        cls = "atom" if len(words) == 1 else "molecule" if len(words) == 2 else "organism"
        by_class[cls].append(n)

    atom_names_lower = sorted({split_words(n)[0] for n in by_class["atom"]})
    found_atom_names = fetch_in(base, key, "atoms", "atom_word", atom_names_lower)
    found_molecules = fetch_in(base, key, "molecules", "name", by_class["molecule"])
    found_organisms = fetch_in(base, key, "organisms", "name", by_class["organism"])
    words_sorted = sorted(all_words)
    found_words = fetch_in(base, key, "atoms", "atom_word", words_sorted)

    missing = {
        "atoms_names": sorted(w for w in atom_names_lower if w not in found_atom_names),
        "molecules": sorted(n for n in by_class["molecule"] if n not in found_molecules),
        "organisms": sorted(n for n in by_class["organism"] if n not in found_organisms),
        "constituent_words": sorted(w for w in words_sorted if w not in found_words),
    }
    report = {
        "verified": date.today().isoformat(),
        "door": "anon (public read policies)",
        "input": src.name,
        "names_total": len(names),
        "coverage": {
            "atom-class names": f"{len(found_atom_names)}/{len(atom_names_lower)}",
            "molecule-class names": f"{len(found_molecules)}/{len(by_class['molecule'])}",
            "organism-class names": f"{len(found_organisms)}/{len(by_class['organism'])}",
            "constituent words in atoms": f"{len(found_words)}/{len(words_sorted)}",
        },
        "missing": missing,
    }
    out = src.with_name(f"{src.stem}-grammar-verify-{date.today().isoformat()}.json")
    out.write_text(json.dumps(report, indent=1), encoding="utf-8")
    for k, v in report["coverage"].items():
        print(f"{k}: {v}")
    print(f"report: {out}")


if __name__ == "__main__":
    main()
