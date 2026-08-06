"""
knowledge_sql.py — run a SQL statement against the resonance-knowledge
Supabase via the Management API (schema changes REST cannot express).

Born 2026-07-26 for KP's molecule-field ask (atom_words + derived_name).
CONSENT-GATED like every write tool on this bridge: runs only at KP's
explicit word, and prints the SQL it is about to run before running it.
Uses SUPABASE_ACCESS_TOKEN from .env; the token never prints.

Usage: python knowledge_sql.py "ALTER TABLE ..."
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


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit("usage: knowledge_sql.py \"<sql>\"")
    sql = sys.argv[1]
    env = load_env()
    token = env["SUPABASE_ACCESS_TOKEN"]
    ref = env["SUPABASE_URL_KNOWLEDGE"].split("//")[1].split(".")[0]
    print(f"project: {ref}\nsql:\n{sql}\n")
    req = urllib.request.Request(
        f"https://api.supabase.com/v1/projects/{ref}/database/query",
        data=json.dumps({"query": sql}).encode(),
        headers={"Authorization": f"Bearer {token}",
                 "Content-Type": "application/json",
                 # Cloudflare blocks python's default UA at api.supabase.com
                 # (BASE-ACCESS-GUIDE lesson 5); a named agent passes.
                 "User-Agent": "resonance-bridge/knowledge_sql"},
        method="POST")
    with urllib.request.urlopen(req, timeout=60) as r:
        body = r.read().decode()
    print("result:", body if body.strip() else "(ok, no rows)")


if __name__ == "__main__":
    main()
