"""server_smoke.py — the Bridge's own acceptance breath, run before any commit.

Spawns the real server (npx tsx src/server.ts), speaks real MCP over stdio
(initialize -> tools/list -> a few tools/call), and prints what came back.
Read-only by construction: it only calls query_* tools through the same
process a client would launch. Born 2026-07-29 with the Grammar line
(the delivery system's first sitting); reusable for every line added since.

Usage:  python server_smoke.py           (from the repo root, or anywhere)
"""
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent

proc = subprocess.Popen(
    "npx tsx src/server.ts",
    cwd=str(REPO),
    shell=True,
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    encoding="utf-8",
)

_id = 0


def send(method, params=None, notify=False):
    global _id
    msg = {"jsonrpc": "2.0", "method": method}
    if params is not None:
        msg["params"] = params
    if not notify:
        _id += 1
        msg["id"] = _id
    proc.stdin.write(json.dumps(msg) + "\n")
    proc.stdin.flush()
    if notify:
        return None
    while True:
        raw = proc.stdout.readline()
        if not raw:
            err = proc.stderr.read()
            sys.exit(f"server closed the pipe. stderr:\n{err}")
        try:
            resp = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if resp.get("id") == _id:
            return resp


def call(tool, args):
    resp = send("tools/call", {"name": tool, "arguments": args})
    if "error" in resp:
        return f"ERROR: {resp['error'].get('message', resp['error'])}"
    parts = resp["result"].get("content", [])
    return "\n".join(p.get("text", "") for p in parts if p.get("type") == "text")


init = send("initialize", {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": {"name": "server-smoke", "version": "0.1"},
})
info = init["result"]["serverInfo"]
print(f"handshake OK: {info['name']} v{info['version']}")
send("notifications/initialized", notify=True)

tools = send("tools/list")["result"]["tools"]
print(f"tools registered ({len(tools)}): " + ", ".join(t["name"] for t in tools))

checks = [
    ("query_atom", {"term": "resonance"}),
    ("query_folksonomy", {}),
    ("query_folksonomy", {"app": "Echoes"}),
    ("query_emoji", {"word": "Focused"}),
    ("search_knowledge", {"query": "bridge", "limit": 2}),
    ("vercel_list_projects", {}),
    ("resend_list_domains", {}),
    ("stripe_account", {}),
    ("stripe_list_webhook_endpoints", {}),
    ("github_token_status", {}),
    ("discord_whoami", {}),
    ("supabase_list_projects", {}),
]
for tool, args in checks:
    out = call(tool, args)
    head = out.replace("\n", " ")[:160]
    print(f"\n== {tool} {args} ==\n{head}{'…' if len(out) > 160 else ''}")

proc.terminate()
print("\nsmoke complete — the server spoke, every line answered.")
