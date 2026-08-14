"""
emoji_wave_seeder.py — deliver the emoji wave into sensory_lexicon.

Born 2026-07-27, the sitting after the showing, at KP's ask: "i would
like to get the emoji column filled in on every row so each atom has
an emoji" — the ground the folksonomies build on after.

Sibling of lattice_seeder.py, bound by the same consent gate: uses
SUPABASE_SECRET_KEY_KNOWLEDGE (service role, bypasses RLS) and
therefore WRITES ONLY AT KP'S EXPLICIT WORD, with --deliver. Without
the flag it is a dry run: reads the seed file, reads the live base,
reports exactly what WOULD travel, writes nothing.

THE LAWS THIS SEEDER KEEPS:
- FILL-EMPTY ONLY: a shell whose emoji is already non-empty is never
  touched — the 87 Wave-6 emoji are sacred, as is anything KP fills
  by hand between seed and delivery. The live base is re-read at
  delivery time; the seed never overwrites a filled cell.
- KP'S EYE (ruling 5): the seed file this reads must have cleared his
  review. The seeder trusts the file only because his eye ruled it.
- VERIFY THROUGH THE PUBLIC DOOR: after delivery, counts are re-read
  with the anon key — what apps and strangers see is the result.

Seed file shape (resonance-grammar/seeds/emoji/emoji-wave.json):
  {"convention": "...", "rows": [{"id": "<sensory_lexicon.id>",
    "atom_word": "...", "emoji": "..."}, ...]}

Usage:
  python emoji_wave_seeder.py <seed-file.json>            # dry run
  python emoji_wave_seeder.py <seed-file.json> --deliver  # at KP's word
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


def req(url, key, method, path, body=None, prefer=None):
    h = {"apikey": key, "Authorization": f"Bearer {key}",
         "Content-Type": "application/json"}
    if prefer:
        h["Prefer"] = prefer
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(f"{url}/rest/v1/{path}", data=data,
                               headers=h, method=method)
    with urllib.request.urlopen(r, timeout=30) as resp:
        raw = resp.read().decode("utf-8")
        return (json.loads(raw) if raw else None), resp.headers


def fetch_all(url, key, table, query):
    rows, page = [], 0
    while True:
        batch, _ = req(url, key, "GET",
                       f"{table}?{query}&limit=1000&offset={page * 1000}")
        rows.extend(batch)
        if len(batch) < 1000:
            return rows
        page += 1


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    seed_path = Path(sys.argv[1])
    deliver = "--deliver" in sys.argv[2:]

    env = load_env()
    url = env.get("SUPABASE_URL_KNOWLEDGE", "")
    secret = env.get("SUPABASE_SECRET_KEY_KNOWLEDGE", "")
    anon = (env.get("SUPABASE_PUBLISHABLE_KEY_KNOWLEDGE", "")
            or env.get("SUPABASE_ANON_KEY_KNOWLEDGE", ""))
    if not url or not anon or (deliver and not secret):
        sys.exit("keys missing from .env — they enter by KP's own hands")

    seed = json.loads(seed_path.read_text(encoding="utf-8"))
    rows = seed["rows"]
    print(f"seed file: {seed_path.name} · {len(rows)} rows")

    # live state through the public door — fill-empty is judged NOW,
    # not at seed-generation time
    live = fetch_all(url, anon, "sensory_lexicon", "select=id,atom_word,emoji")
    live_by_id = {r["id"]: r for r in live}
    filled_before = sum(1 for r in live if (r.get("emoji") or "").strip())

    to_send, skipped_filled, skipped_missing = [], 0, 0
    for r in rows:
        cur = live_by_id.get(r["id"])
        if cur is None:
            skipped_missing += 1
            continue
        if (cur.get("emoji") or "").strip():
            skipped_filled += 1          # sacred — never overwritten
            continue
        if not (r.get("emoji") or "").strip():
            continue
        to_send.append(r)

    print(f"live shells: {len(live)} · already filled: {filled_before}")
    print(f"would deliver: {len(to_send)} · skipped (already filled): "
          f"{skipped_filled} · skipped (id not in base): {skipped_missing}")

    if not deliver:
        print("\nDRY RUN — nothing written. Deliver at KP's word with --deliver.")
        return

    print("\ndelivering at KP's word …")
    done = 0
    for r in to_send:
        req(url, secret, "PATCH",
            f"sensory_lexicon?id=eq.{r['id']}&emoji=is.null",
            {"emoji": r["emoji"]}, prefer="return=minimal")
        done += 1
        if done % 200 == 0:
            print(f"  {done}/{len(to_send)}")
    print(f"  {done}/{len(to_send)} delivered")

    # verify through the public door
    after = fetch_all(url, anon, "sensory_lexicon", "select=id,emoji")
    filled_after = sum(1 for r in after if (r.get("emoji") or "").strip())
    empty_after = len(after) - filled_after
    print(f"\nVERIFIED through the anon door: {len(after)} shells · "
          f"{filled_after} emoji filled · {empty_after} empty")


if __name__ == "__main__":
    main()
