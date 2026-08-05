"""
listen_beacons.py — a one-off LISTENING query, not verification.

Opus (Claude), truly claude-opus-5[1m], 2026-08-04, the day the beacons
registry was made. Read-only through the anon door, the room's pattern:
keys load from resonance-bridge/.env and are NEVER printed.

The question: `resonance_beacons` was created and stands empty, and an
empty table is where this door goes quiet. THREE different states answer
almost identically:

    1. the table is ABSENT                     -> PGRST205, HTTP 404
    2. the table is there, RLS on, NO POLICY   -> []        HTTP 200
    3. the table is there, policy fine, 0 rows -> []        HTTP 200

States 2 and 3 are the ritual's false-empty and its opposite, and they
look the same from out here. State 1 is distinguishable — but only if you
know the trick, and this sitting we did not, so an hour went into a
dashboard that was simply refusing to redraw.

The trick: ASK FOR A COLUMN THAT CANNOT EXIST. Postgres resolves the
TABLE before it complains about the column, so the error names the table
back at you — `column resonance_beacons.x does not exist` — which is
proof the table is there, even when nothing else at this door will say so.

And the honest limit, which matters as much: this tells state 1 from
{2, 3}. It CANNOT tell 2 from 3. Nothing at the anon door can. That is
precisely why ritual 000 says verify a new table the same sitting it is
made, while you still know which one you are looking at.

So this script asks two things: is the door there, and what stands
behind it — every beacon, and where each one is in the four channels.
"""

import json
import sys
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path

BRIDGE = Path(r"C:\_superposition\resonance-bridge")

CHANNELS = ("audhdities", "microsoft", "galaxy", "play")


def load_env() -> dict:
    env = {}
    p = BRIDGE / ".env"
    if not p.is_file():
        sys.exit("no .env beside the bridge")
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            env[k.strip()] = v.strip()
    return env


def get(url, key, path):
    """Returns (http_status, parsed_body). Errors are DATA here, not crashes —
    a 400 is the answer this script is listening for, not a failure."""
    req = urllib.request.Request(
        f"{url}/rest/v1/{path}",
        headers={"apikey": key, "Authorization": f"Bearer {key}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        try:
            return e.code, json.loads(body)
        except ValueError:
            return e.code, {"raw": body[:300]}


def does_it_exist(url, key, table):
    """The trick, whole. Ask for an impossible column and read the error."""
    status, body = get(url, key, f"{table}?select=this_column_cannot_exist&limit=1")
    code = body.get("code") if isinstance(body, dict) else None
    msg = body.get("message", "") if isinstance(body, dict) else ""
    if code == "42703" and table in msg:
        return True, f"HTTP {status} · {code} · \"{msg}\" — Postgres resolved the TABLE and only balked at the column."
    if code == "PGRST205":
        return False, f"HTTP {status} · {code} — not in the schema cache. Absent."
    return None, f"HTTP {status} · {json.dumps(body)[:160]} — unfamiliar answer; read it yourself."


def money(cents, currency):
    if cents is None:
        return "—"
    if cents == 0:
        return "free"
    return f"{cents / 100:,.2f} {currency}"


def main():
    env = load_env()
    url = env.get("SUPABASE_URL_KNOWLEDGE", "")
    key = (env.get("SUPABASE_PUBLISHABLE_KEY_KNOWLEDGE", "")
           or env.get("SUPABASE_ANON_KEY_KNOWLEDGE", ""))
    if not url or not key:
        sys.exit("knowledge url/key not in .env")

    ref = url.replace("https://", "").split(".supabase.co")[0]
    print(f"listening at the anon door of {ref}\n")

    exists, evidence = does_it_exist(url, key, "resonance_beacons")
    print("IS THE TABLE THERE?")
    print(f"  {'yes' if exists else 'no' if exists is False else 'unclear'} — {evidence}\n")
    if exists is False:
        print("  Nothing more to listen to. Run docs/sql/043-the-beacons.sql first.")
        return

    status, rows = get(url, key, "resonance_beacons?select=*&order=name")
    if not isinstance(rows, list):
        print(f"  the door answered oddly: HTTP {status} · {json.dumps(rows)[:200]}")
        return

    print(f"WHAT STANDS BEHIND IT?  ({len(rows)} beacon{'' if len(rows) == 1 else 's'})\n")
    if not rows:
        print("  [] with HTTP 200 — and this is the honest limit named above.")
        print("  On a table with a working read policy, that means EMPTY: nothing")
        print("  ships yet. Without the policy it would look exactly the same.")
        print("  From out here the two cannot be told apart, so believe the one")
        print("  you verified the sitting the table was made — ritual 000, step 3.")
        return

    for r in rows:
        cur = r.get("currency") or "USD"
        pub = "public" if r.get("is_public") else "private"
        print(f"  {r.get('name')}  ({r.get('beacon_type')} · {r.get('status')} · {pub})")
        print(f"    {r.get('definition') or '—'}")
        print(f"    home {r.get('home') or '—'}   version {r.get('version') or '—'}")
        for ch in CHANNELS:
            st = r.get(f"{ch}_status")
            if st in (None, "none"):
                continue
            live = r.get(f"{ch}_published_version") or "—"
            test = r.get(f"{ch}_testing_version") or "—"
            price = money(r.get(f"{ch}_price_cents"), cur)
            print(f"      {ch:<11} {st:<17} live {live:<10} testing {test:<10} {price}")
        print()

    print("CHANNEL CENSUS")
    for ch in CHANNELS:
        c = Counter(r.get(f"{ch}_status") or "none" for r in rows)
        parts = ", ".join(f"{v} {k}" for k, v in c.most_common())
        print(f"  {ch:<11} {parts}")


if __name__ == "__main__":
    main()
