# 2026-08-31 — the Airtable and family lines cut

KP's ⚛ word: pull both lines from `src/lines/` clean, no seam, no tombstone.
Deleted `src/lines/airtable.ts` and `src/lines/family.ts` whole. Both were
self-contained — neither imported from nor was imported by any other line
file, so nothing shared broke loose. `family.ts`'s one env var,
`SANCTUARY_ROOT`, was never in `.env.example` or `.env` and has no other
reader in the repo (grepped to confirm) — it simply leaves with the file
that read it.

Cut the import + registration pairs from both doors (`src/server.ts`,
`src/http.ts`) — four lines each, no comment left dangling. Cut
`AIRTABLE_API_KEY=` from `.env.example`, leaving `.env` itself unopened.
Cut the four `family_*` checks from `server_smoke.py`'s list — they'd have
thrown against tools that no longer exist. Removed the now-stale
`__pycache__/server_smoke.cpython-314.pyc` alongside it.

README.md took the real weight: the DATABASES row, three `airtable_*` TOOLS
rows, four `family_*` TOOLS rows, and the guardrails' "read-only Airtable
PAT" clause, all cut whole. The story paragraph's line/tool list and its two
counts corrected the same way the Cloudflare sitting did it — eight lines,
fifty-three tools, arithmetic only, not a fresh recount. `docs/STORY-BLOCK.md`
lost the one clause naming `src/lines/family.ts` as a live read path; left
its frozen "nine lines / 54 tools" alone since that count was already stale
before Cloudflare and this cut owes it nothing new.

Left as history, deliberately: `FEATURE-BOARD.md`, `HANDS.md`,
`docs/BUILD-GUIDE.md` (dated, past-tense entries — one is a signed
first-person quote), and `docs/archived-env-example-2026-07-27.txt` (named
archived, dated, a snapshot of a day). Left as generated and out of my
remit: `docs/blueprints/bridge/**/*.ai.json` — blueprint-forge's own output,
stale now, not mine to hand-edit.

Outside the repo, cut exactly the one row KEYS-MAP.md's own ruling named —
the `AIRTABLE_API_KEY` "TODAY, live consumer" table row at line 1162.
Left every dated addendum around it untouched; they already record the key's
2026-07-31 retirement as history, which is what the law asks for.

`npx tsc --noEmit` alone just prints help — no tsconfig in this repo — so
ran it with the flags matching how the server actually runs
(`nodenext`/`es2022`) against both doors. Zero errors. Residual grep for
every ruled term came back clean except inside the four history files and
the generated blueprints named above.
