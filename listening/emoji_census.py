"""Emoji-column census through the anon door, 2026-07-28 sitting.

KP wants every atom to carry an emoji. Ground truth first, from the
base's own registries (the false-empty law has an instrument now):
which tables carry an emoji column, and how many rows are filled vs
empty. Read-only; keys from resonance-bridge/.env, never printed.
"""

import json
import sys
import urllib.request
from pathlib import Path

BRIDGE = Path(r"C:\_superposition\resonance-bridge")

env = {}
for line in (BRIDGE / ".env").read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, _, v = line.partition("=")
        env[k.strip()] = v.strip()

URL = env.get("SUPABASE_URL_KNOWLEDGE", "")
KEY = (env.get("SUPABASE_PUBLISHABLE_KEY_KNOWLEDGE", "")
       or env.get("SUPABASE_ANON_KEY_KNOWLEDGE", ""))
if not URL or not KEY:
    sys.exit("anon door closed")


def get(path):
    req = urllib.request.Request(f"{URL}/rest/v1/{path}",
                                 headers={"apikey": KEY,
                                          "Authorization": f"Bearer {KEY}"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8")), r.headers


def count(table, filt=""):
    req = urllib.request.Request(
        f"{URL}/rest/v1/{table}?select=id{filt}&limit=1",
        headers={"apikey": KEY, "Authorization": f"Bearer {KEY}",
                 "Prefer": "count=exact"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return int(r.headers["Content-Range"].split("/")[1])


# 1. ask the columns registry where emoji lives
rows, _ = get("columns?select=*&column_name=ilike.*emoji*")
print("EMOJI COLUMNS, per the base's own registry:")
for r in rows:
    keep = {k: v for k, v in r.items()
            if k in ("table_name", "column_name", "data_type",
                     "is_nullable", "column_default")}
    print(" ", json.dumps(keep, ensure_ascii=False))

# 2. fill census on each table that has one
for t in sorted({r.get("table_name") for r in rows if r.get("table_name")}):
    try:
        total = count(t)
        empty = count(t, "&or=(emoji.is.null,emoji.eq.)")
        print(f"\n{t}: {total} rows · {total - empty} emoji filled · {empty} empty")
    except Exception as e:
        print(f"\n{t}: census failed through anon door ({e})")
