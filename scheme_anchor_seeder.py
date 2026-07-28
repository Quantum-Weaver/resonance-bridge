"""
scheme_anchor_seeder.py — deliver the derived scheme_anchor backfill.

Born 2026-07-27, the sitting 012 ran at KP's hand. Sibling of
emoji_wave_seeder.py, same consent gate: SUPABASE_SECRET_KEY_KNOWLEDGE
writes ONLY at KP's explicit word with --deliver; default is a dry run.

THE LAW OF THIS SEED: every value is DERIVED, never chosen — subject-
in-scheme → 'subject', object-in-scheme → 'object' (the identification
key's contracts make this total on broader edges). The 5 non-
hierarchical edges (related/use_for) stay null by design. Fill-empty
only: a scheme_anchor already set is never overwritten. Verified
through the public door after.

Usage:
  python scheme_anchor_seeder.py <seed-file.json>            # dry run
  python scheme_anchor_seeder.py <seed-file.json> --deliver  # at KP's word
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
        return json.loads(raw) if raw else None


def fetch_all(url, key, table, query):
    rows, page = [], 0
    while True:
        batch = req(url, key, "GET",
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
    print(f"seed: {seed_path.name} · {len(rows)} derived anchors "
          f"({seed.get('counts')})")

    live = fetch_all(url, anon, "concept_relations",
                     "select=id,scheme_anchor")
    live_by_id = {r["id"]: r for r in live}
    to_send, skipped_filled, skipped_missing = [], 0, 0
    for r in rows:
        cur = live_by_id.get(r["id"])
        if cur is None:
            skipped_missing += 1
            continue
        if cur.get("scheme_anchor"):
            skipped_filled += 1
            continue
        to_send.append(r)
    print(f"live edges: {len(live)} · would deliver: {len(to_send)} · "
          f"skipped filled: {skipped_filled} · skipped missing: "
          f"{skipped_missing}")

    if not deliver:
        print("\nDRY RUN — nothing written. Deliver at KP's word with --deliver.")
        return

    print("\ndelivering at KP's word …")
    for i, r in enumerate(to_send, 1):
        req(url, secret, "PATCH",
            f"concept_relations?id=eq.{r['id']}&scheme_anchor=is.null",
            {"scheme_anchor": r["scheme_anchor"]}, prefer="return=minimal")
        if i % 50 == 0:
            print(f"  {i}/{len(to_send)}")
    print(f"  {len(to_send)}/{len(to_send)} delivered")

    after = fetch_all(url, anon, "concept_relations",
                      "select=id,scheme_anchor,relation_type")
    subj = sum(1 for r in after if r.get("scheme_anchor") == "subject")
    obj = sum(1 for r in after if r.get("scheme_anchor") == "object")
    nul = sum(1 for r in after if not r.get("scheme_anchor"))
    print(f"\nVERIFIED through the anon door: {len(after)} edges · "
          f"{subj} subject · {obj} object · {nul} null")


if __name__ == "__main__":
    main()
