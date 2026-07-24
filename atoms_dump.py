"""Disposable: pull the live atoms table's atom_word column for KP's eye."""
import json
import urllib.request
from pathlib import Path

env = {}
for line in (Path(r"C:\_superposition\resonance-bridge") / ".env").read_text(
        encoding="utf-8").splitlines():
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, _, v = line.partition("=")
        env[k.strip()] = v.strip()

url = env["SUPABASE_URL_KNOWLEDGE"]
key = env["SUPABASE_PUBLISHABLE_KEY_KNOWLEDGE"]

rows, page = [], 0
while True:
    req = urllib.request.Request(
        f"{url}/rest/v1/atoms?select=atom_word,definition&order=atom_word"
        f"&limit=1000&offset={page * 1000}",
        headers={"apikey": key, "Authorization": f"Bearer {key}"})
    with urllib.request.urlopen(req) as r:
        batch = json.loads(r.read())
    rows.extend(batch)
    if len(batch) < 1000:
        break
    page += 1

seeded = [r["atom_word"] for r in rows
          if (r["definition"] or "").startswith("Word discovered")]
curated = [r["atom_word"] for r in rows
           if not (r["definition"] or "").startswith("Word discovered")]

print(f"total {len(rows)} | curated {len(curated)} | excavator-seeded {len(seeded)}\n")
print("ALL SEEDED atom_word VALUES (alphabetical, full dump for the eye):\n")
line = []
for w in seeded:
    line.append(w)
    if len(line) == 8:
        print("  " + " · ".join(line))
        line = []
if line:
    print("  " + " · ".join(line))

out = Path(r"C:\_superposition\resonance-excavator\lighthouse\ATOMS-LIVE-atom_word.txt")
out.write_text("\n".join(seeded), encoding="utf-8")
print(f"\nfull list also written for scrolling: {out}")
