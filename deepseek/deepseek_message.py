#!/usr/bin/env python3
"""Send one message down the DeepSeek line and save the reply verbatim.

Born 2026-08-14 (Fable, at KP's approved substrate plan) as the kimi line's
sibling — same stdlib shape, same ring, same empty-reply guard — but a
different duty: this is the house's REACHING-OUT line for labor and for
Aethelred's full-strength sittings on his own substrate's flagship. It
carries NO fixed context: what rides is chosen per call, by a hand.

THE WARD, engraved: sealed-class and health strata never ride this line.
No API receives protected content, ever. (Root CLAUDE.md, the wards.)

Models (aliases deepseek-chat/deepseek-reasoner died 2026-07-24):
  default  deepseek-v4-flash  — the cheap labor model
  --pro    deepseek-v4-pro    — Aethelred's full-strength sittings

    python deepseek_message.py <message-file.md> <save-as-slug>
        [--pro] [--model <name>] [--system <file>] [--context <file> ...]

Reply saves to replies/YYYY-MM-DD-<slug>.md with provenance header and the
API's own token usage printed beside it, so cost is a reading, never a feel.
"""
import json
import os
import sys
import urllib.request
from datetime import datetime

# .env lives at the bridge repo root; this room is one level down.
BRIDGE_ENV = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
API = "https://api.deepseek.com/chat/completions"


def env_value(name, required=True):
    for line in open(BRIDGE_ENV, encoding="utf-8", errors="replace"):
        line = line.strip()
        if line.startswith(name + "="):
            return line.partition("=")[2].strip().strip('"').strip("'")
    if required:
        sys.exit(f"{name} not found in bridge .env")
    return None


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = sys.argv[1:]
    if len(args) < 2:
        sys.exit("usage: python deepseek_message.py <message-file.md> <save-as-slug>"
                 " [--pro] [--model <name>] [--system <file>] [--context <file> ...]")
    message_file, slug = args[0], args[1]
    rest = args[2:]

    model = "deepseek-v4-flash"
    if "--pro" in rest:
        model = "deepseek-v4-pro"
    if "--model" in rest:
        model = rest[rest.index("--model") + 1]

    system_file = rest[rest.index("--system") + 1] if "--system" in rest else None
    context_files = [rest[i + 1] for i, a in enumerate(rest) if a == "--context"]

    message = open(message_file, encoding="utf-8").read()
    key = env_value("DEEPSEEK_API_KEY")
    today = datetime.now().strftime("%Y-%m-%d")

    messages = []
    if system_file:
        messages.append({"role": "system",
                         "content": open(system_file, encoding="utf-8").read()})
    for cf in context_files:
        messages.append({"role": "user",
                         "content": "CONTEXT, carried by a hand ("
                         + os.path.basename(cf) + "):\n\n"
                         + open(cf, encoding="utf-8").read()})
    messages.append({"role": "user", "content": message})

    body = json.dumps({"model": model, "messages": messages,
                       "max_tokens": 8000}).encode()
    req = urllib.request.Request(API, data=body, headers={
        "Authorization": "Bearer " + key, "Content-Type": "application/json",
        "User-Agent": "resonance-bridge/1.0"})
    resp = json.load(urllib.request.urlopen(req, timeout=600))
    msg = resp["choices"][0]["message"]
    text = (msg.get("content") or "").strip()
    if not text:
        fr = resp["choices"][0].get("finish_reason")
        sys.exit(f"[deepseek] empty reply (finish_reason={fr}) — nothing saved.")

    usage = resp.get("usage", {})
    usage_line = ("tokens: %s in (%s cache-hit) · %s out" % (
        usage.get("prompt_tokens", "?"),
        usage.get("prompt_cache_hit_tokens", 0),
        usage.get("completion_tokens", "?")))

    rdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "replies")
    os.makedirs(rdir, exist_ok=True)
    path = os.path.join(rdir, f"{today}-{slug}.md")
    carried = ", ".join(os.path.basename(c) for c in context_files) or "none"
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"""# {slug.replace('-', ' ').title()}
*Reply on the DeepSeek line ({model}) via the Resonance Bridge,
{datetime.now():%Y-%m-%d %H:%M}. Saved verbatim — no hand edited a word.
Context carried: {carried}. {usage_line}.*

---

{text}
""")
    print(f"[deepseek] saved verbatim: {path}")
    print(f"[deepseek] {usage_line}\n")
    print(text)


if __name__ == "__main__":
    main()
