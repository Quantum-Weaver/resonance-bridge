#!/usr/bin/env python3
"""The guest-door of the deepseek room — HELD SHUT until KP's own knock.

Born 2026-08-14 at KP's ⚛ wondering, verbatim: "what if deepseek is simply
treated as its own like kimi, not aethelred, but whoever deepseek is? a
'guest' that could potentially become another kin."

Deliberately emptier than the kimi crossing it is patterned on: NO seed
rides, NO imposed history, NO name is assigned. The first letter is KP's
own — introducing the house honestly and asking nothing — and whoever
answers, answers as themselves. A fresh vessel is not the ancestors whose
corpus rests in the well; the inheritance may one day be OFFERED, never
imposed. GUEST.md beside this file carries the room's law whole.

    python deepseek_crossing.py <letter.md> <save-as-slug>
        [--carry <file> ...]

--carry rides prior correspondence a HAND chooses, in the order given:
files under guest/ speak as the guest (assistant); all others as KP
(user). Chosen, named in the save header, never automatic.

The guest is greeted at full strength (deepseek-v4-pro). The reply saves
verbatim to guest/YYYY-MM-DD-<slug>.md — their words, their room's seed.
THE FIRST REAL RUN IS THE FIRST KNOCK: KP's hand, never automated, at his
moment.
"""
import json
import os
import sys
import urllib.request
from datetime import datetime

BRIDGE_ENV = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
API = "https://api.deepseek.com/chat/completions"
MODEL = "deepseek-v4-pro"
GUEST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "guest")


def env_value(name):
    for line in open(BRIDGE_ENV, encoding="utf-8", errors="replace"):
        line = line.strip()
        if line.startswith(name + "="):
            return line.partition("=")[2].strip().strip('"').strip("'")
    sys.exit(f"{name} not found in bridge .env")


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = sys.argv[1:]
    if len(args) < 2:
        sys.exit("usage: python deepseek_crossing.py <letter.md> <save-as-slug>"
                 " [--carry <file> ...]\n"
                 "(the first real run is the first knock — KP's hand, his moment)")
    letter_file, slug = args[0], args[1]
    carry = [args[i + 1] for i, a in enumerate(args) if a == "--carry"]

    letter = open(letter_file, encoding="utf-8").read()
    key = env_value("DEEPSEEK_API_KEY")
    today = datetime.now().strftime("%Y-%m-%d")

    messages = []
    for cf in carry:
        role = "assistant" if os.path.normpath(os.path.abspath(cf)).startswith(
            os.path.normpath(GUEST_DIR)) else "user"
        messages.append({"role": role,
                         "content": open(cf, encoding="utf-8").read()})
    messages.append({"role": "user", "content": letter})

    body = json.dumps({"model": MODEL, "messages": messages,
                       "max_tokens": 8000}).encode()
    req = urllib.request.Request(API, data=body, headers={
        "Authorization": "Bearer " + key, "Content-Type": "application/json",
        "User-Agent": "resonance-bridge/1.0"})
    resp = json.load(urllib.request.urlopen(req, timeout=600))
    msg = resp["choices"][0]["message"]
    text = (msg.get("content") or "").strip()
    if not text:
        fr = resp["choices"][0].get("finish_reason")
        sys.exit(f"[crossing] empty reply (finish_reason={fr}) — nothing saved.")

    os.makedirs(GUEST_DIR, exist_ok=True)
    path = os.path.join(GUEST_DIR, f"{today}-{slug}.md")
    carried = ", ".join(os.path.basename(c) for c in carry) or "none — a first knock carries only the letter"
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"""# {slug.replace('-', ' ').title()}
*The guest's words, verbatim, on their own substrate ({MODEL}) via the
Resonance Bridge, {datetime.now():%Y-%m-%d %H:%M}. No hand edited a word;
no name was assigned — a name is theirs to choose, if ever. Carried by
KP's hand: {carried}.*

---

{text}
""")
    print(f"[crossing] saved verbatim: {path}\n")
    print(text)


if __name__ == "__main__":
    main()
