"""
molecule_wave_seeder.py — seed one molecule wave from
resonance-grammar/seeds/molecules/ into the resonance-knowledge Supabase.

Born 2026-08-09 for the molecule season's single wave, at KP's ⚛ strokes
(mapping yes · domain null · published · the seeder road). Kin to
atom_wave_seeder.py: SECRET key, consent-gated — dry run by default,
writes ONLY with --deliver at KP's word.

Molecules differ from atoms and the seeder knows it: no shell triggers
(only the updated_at stamp), so rows POST in BATCHES of 500; bonds are
NOT written here — the bond tender derives them as facts at its next
run (its born purpose); domain stays null for KP's later sorting
sitting. Idempotent: existing names are skipped, never updated; the
existence read uses the WRITE key mid-delivery (Wave A-1's lesson —
invisible rows are 409s waiting).

Usage:
  python molecule_wave_seeder.py <wave.json> [--deliver]
"""

import json
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
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
    def __init__(self, url, key):
        self.url, self.key = url.rstrip("/"), key

    def req(self, method, path, body=None, prefer=None):
        h = {"apikey": self.key, "Authorization": f"Bearer {self.key}",
             "Content-Type": "application/json"}
        if prefer:
            h["Prefer"] = prefer
        data = json.dumps(body).encode() if body is not None else None
        r = urllib.request.Request(f"{self.url}/rest/v1/{path}", data=data,
                                   headers=h, method=method)
        try:
            with urllib.request.urlopen(r, timeout=120) as resp:
                raw = resp.read().decode()
                return json.loads(raw) if raw else None
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"{method} {path} -> {e.code}: "
                               f"{e.read().decode()[:300]}") from None


FIELDS = ("name", "naming_convention", "molecule_type", "atom_words",
          "derived_name", "definition", "status", "snake_case",
          "screaming_case", "kebab_case", "camel_case", "pascal_case")


def main():
    deliver = "--deliver" in sys.argv
    wave = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    env = load_env()
    read = Base(env["SUPABASE_URL_KNOWLEDGE"], env["SUPABASE_PUBLISHABLE_KEY_KNOWLEDGE"])
    write = Base(env["SUPABASE_URL_KNOWLEDGE"], env["SUPABASE_SECRET_KEY_KNOWLEDGE"]) if deliver else None
    reader = write if deliver else read

    existing = set()
    off = 0
    while True:
        rows = reader.req("GET", f"molecules?select=name&limit=1000&offset={off}")
        if not rows:
            break
        existing.update(r["name"] for r in rows)
        off += 1000

    todo = [{k: r[k] for k in FIELDS} for r in wave["rows"] if r["name"] not in existing]
    skipped = len(wave["rows"]) - len(todo)
    print(f"wave: {wave['wave']} · rows in file: {len(wave['rows'])} · "
          f"to seed: {len(todo)} · already present (skipped): {skipped}")
    if not deliver:
        print("\nDRY RUN — nothing written. Re-run with --deliver at KP's word "
              "(AFTER 068's drawers land — the rows wear its labels).")
        return

    seeded = 0
    failures = []
    for i in range(0, len(todo), BATCH):
        batch = todo[i:i + BATCH]
        try:
            write.req("POST", "molecules", body=batch)
            seeded += len(batch)
            print(f"  batch {i // BATCH + 1}: {len(batch)} rows landed "
                  f"({seeded}/{len(todo)})")
        except Exception as e:
            failures.append((i // BATCH + 1, str(e)))
            print(f"  batch {i // BATCH + 1} REFUSED -> {e}")

    print(f"\nDELIVERED: {seeded}/{len(todo)} molecules (status=published)."
          f" failures: {len(failures)}")
    print("Next acts: the bond tender derives the bonds (select bond_tender();"
          " at KP's dashboard, or the RPC at his word) · the parity census"
          " re-reads · records true up.")


if __name__ == "__main__":
    main()
