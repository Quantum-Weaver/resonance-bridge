"""
atom_wave_seeder.py — seed one atom wave from resonance-grammar/seeds/atoms/
into the resonance-knowledge Supabase, with the 1:1:1 shells and THE CASE LAW.

Born 2026-08-07 for the library carry's Wave A-1 (KP's ⚛ words: "can we
begin with the atoms" · "i would be honored if you would be my hands
through this process"). Kin to grammar_seeder.py: SECRET key, consent-
gated — dry run by default, writes ONLY with --deliver, at KP's word
(standing or spoken). Idempotent: existing atoms are skipped, never
updated; modifier merges only APPEND suffixes, never remove.

What one seed row becomes (the laws engraved in the wave file):
  atoms row        status='submitted' (editorial law — KP's eye publishes)
                   + snake/screaming/pascal case columns (THE CASE LAW, 062)
                   + modifiers array (plural ruling, Wave 0 #3)
  etymology row    shell: atom_id + atom_word + completion_progress=0
  sensory row      shell: atom_id + atom_word
  atoms PATCH      etymology_id + sensory_id (the 1:1:1 kept whole)

Usage:
  python atom_wave_seeder.py <wave.json> [--updates <resolution.json>] [--deliver]
"""

import json
import sys
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
            with urllib.request.urlopen(r, timeout=60) as resp:
                raw = resp.read().decode()
                return json.loads(raw) if raw else None
        except urllib.error.HTTPError as e:
            # speak the body — a swallowed reason hides the real failure
            raise RuntimeError(f"{method} {path} -> {e.code}: "
                               f"{e.read().decode()[:300]}") from None


def main():
    args = sys.argv[1:]
    deliver = "--deliver" in args
    updates_path = None
    if "--updates" in args:
        updates_path = Path(args[args.index("--updates") + 1])
    wave_path = Path(args[0])
    wave = json.loads(wave_path.read_text(encoding="utf-8"))

    env = load_env()
    read = Base(env["SUPABASE_URL_KNOWLEDGE"], env["SUPABASE_PUBLISHABLE_KEY_KNOWLEDGE"])
    write = Base(env["SUPABASE_URL_KNOWLEDGE"], env["SUPABASE_SECRET_KEY_KNOWLEDGE"]) if deliver else None
    signed = wave.get("signed", "KP + Fable (lane F, the Serenade lamp)")

    # ---- gather existing atoms (idempotence + modifier merge ground).
    # Read with the WRITE key when delivering: submitted rows are dark to
    # the anon door by Ruling 8, and an invisible row is a 409 waiting
    reader = write if deliver else read
    existing = {}
    off = 0
    while True:
        rows = reader.req("GET", f"atoms?select=atom_word,modifiers&limit=1000&offset={off}")
        if not rows:
            break
        for r in rows:
            existing[r["atom_word"]] = r["modifiers"] or []
        off += 1000

    # ---- the seeds
    to_seed = [s for s in wave["seeds"] if s["word"] not in existing]
    skipped = [s["word"] for s in wave["seeds"] if s["word"] in existing]

    # ---- modifier updates: wave's manual adds + optional resolution file
    mod_plan = {}
    for m in wave.get("manual_modifier_adds", []):
        mod_plan.setdefault(m["atom_word"], set()).update(m["add"])
    if updates_path:
        res = json.loads(updates_path.read_text(encoding="utf-8"))
        for atom, spec in res.get("modifier_updates", {}).items():
            mod_plan.setdefault(atom, set()).update(spec["add"])
    mod_todo = {}
    for atom, adds in sorted(mod_plan.items()):
        have = set(existing.get(atom, []))
        need = sorted(adds - have)
        if atom in existing and need:
            mod_todo[atom] = need

    print(f"wave: {wave['wave']} · seeds in file: {len(wave['seeds'])} · "
          f"to seed: {len(to_seed)} · already present (skipped): {len(skipped)}")
    if skipped:
        print("  skipped:", ", ".join(skipped))
    print(f"modifier updates planned: {len(mod_todo)} atoms")
    if not deliver:
        print("\nDRY RUN — nothing written. Re-run with --deliver at KP's word.")
        return

    # ---- deliver: seeds (per-row honesty — one refusal never strands
    # the wave; failures reported at the end, never silently)
    failures = []
    for s in to_seed:
        w = s["word"]
        try:
            atom = write.req("POST", "atoms", body={
            "atom_word": w,
            "definition": s["definition"],
            "atom_type": "root",
            "weight": 5, "affinity": 5, "valence": 1, "state": "static",
            "modifiers": s.get("modifiers") or None,
            "status": "submitted",
            # created_by/submitted_by are uuid columns (auth refs) — left
            # null as every prior seed did; provenance lives in the wave
            # file itself, which is the committed record.
            "snake_case": w.lower(),
            "screaming_case": w.upper(),
            "pascal_case": w[:1].upper() + w[1:].lower(),
        }, prefer="return=representation")[0]
        # THE 1:1:1 IS THE TRIGGER'S: on_atom_insert births the etymology
        # and sensory shells AND links them into the atom; an explicit shell
        # POST 409s against the trigger's work. The atom POST is the whole seed.
            print(f"  seeded: {w} (shells born by trigger: "
                  f"ety {bool(atom.get('etymology_id')) or 'pending'} · "
                  f"sen {bool(atom.get('sensory_id')) or 'pending'})")
        except Exception as e:
            failures.append((w, str(e)))
            print(f"  REFUSED: {w} -> {e}")

    # ---- deliver: modifier merges (append-only)
    merged_n = 0
    for atom, need in mod_todo.items():
        try:
            merged = sorted(set(existing[atom]) | set(need))
            write.req("PATCH", f"atoms?atom_word=eq.{atom}", body={"modifiers": merged})
            merged_n += 1
        except Exception as e:
            failures.append((atom, str(e)))
            print(f"  REFUSED modifier merge: {atom} -> {e}")

    print(f"\nDELIVERED: {len(to_seed) - sum(1 for f in failures if f[0] in [s['word'] for s in to_seed])} "
          f"atoms seeded (status=submitted) · {merged_n}/{len(mod_todo)} modifier merges."
          f"\nfailures: {len(failures)}" + ("" if not failures else " — " + "; ".join(f"{w}: {m[:80]}" for w, m in failures)))
    print("Note: submitted rows are DARK to the anon door by Ruling 8 — "
          "verify with the reading of the secret key or at KP's dashboard.")


if __name__ == "__main__":
    main()
