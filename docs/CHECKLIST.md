# RESONANCE BRIDGE — MASTER CHECKLIST

*Created 2026-08-21 per the repo-tender sending — this repo had none. Note:
`CLAUDE.md` currently states "This realm keeps no CHECKLIST. Enter by
`FEATURE-BOARD.md` + `docs/BUILD-GUIDE.md`" — that line predates this file
and is flagged for KP rather than silently overridden. `FEATURE-BOARD.md`
remains the fuller, first-person record of each sitting; this ledger
restates its phases in the standard's shape and is the append-only log of
what was done, not a replacement for it.*

## LEGEND
- ✅ Complete
- ⚠️ In Progress
- 🔴 Broken
- ⬜ Pending

---

## PHASE STATUS

### Phase 0: Prometheus, the fire-bringer ✅ (2026-06-30 → 2026-07-04)
- [x] Initial commit — `Resonance MCP — Prometheus, the fire-bringer` (git log `ef635dc`)
- [x] First tool (`query_atom`) live over stdio (git log `8fa06b9`: "proven in Inspector")
- [ ] **Tested:** ⚠️ — the commit message itself claims an Inspector run; no preserved output/artifact found, and not re-run this sitting (network-touching; out of this sitting's law). Claimed, not independently verified.

### Phase 1: The rename — Prometheus → Resonance Bridge ✅ (2026-07-07/08)
- [x] Repo, MCP registration, and docs renamed; naming scrub of lingering Prometheus claims (git log `dc4e5be`; `CLAUDE.md` H1)
- [x] `HANDS.md` opened per THE-HANDS standard (git log `f707d02`)
- [x] `FABLE-KERNEL.md` written for session continuity (git log `fe85f54`)
- [x] **Tested:** ✅ — `FABLE-KERNEL.md` §State (2026-07-09) records a state-check, not just a commit: "MCP registered `resonance-bridge`, `✔ Connected`. Naming scrub verified complete."

### Phase 2: The delivery system — the Grammar line ✅ (2026-07-29)
- [x] `src/grammar.ts` — seven read-only tools over the living Supabase Grammar, anon door (`HANDS.md` §Added 2026-07-29)
- [x] `server_smoke.py` — the acceptance breath, real MCP over stdio (README.md §TOOLS)
- [x] **Tested:** ✅ — `HANDS.md:82`, a recorded full-smoke pass naming the Grammar line's own tool count: "Server at 28 tools, five lines, smoke whole" (2026-07-31, the first whole-smoke breath after Grammar+Vercel+Resend+Stripe landed).

### Phase 3: The platform lines ✅ (2026-07-31)
- [x] Vercel, Resend, Stripe, GitHub, Discord, Supabase-management lines — each landed at a named expert's commission (README.md §DATABASES rows)
- [x] Airtable line retired at KP's word, key off the ring (README.md §DATABASES)
- [x] **Tested:** ✅ — each line's own first-run result is recorded in `HANDS.md:63-109`, not merely its commit: Vercel's "first live census answered the map's wiring-mode question"; Resend's first run "closed the map's last Resend ground truth"; Stripe's first run found "account live..., zero webhook endpoints" + "Server at 28 tools, five lines, smoke whole"; GitHub's first run "CLOSED F7: token live... expires 2026-10-02..., Server at 35 tools, six lines"; Discord's "all seven Discord windows answered live... Server at 42 tools, seven lines"; Supabase's first runs found "both projects ACTIVE_HEALTHY... 29 tables, ZERO risks."

### Phase 4: The Family Table ✅ (2026-08-14)
- [x] Eight lines moved whole into `src/lines/` by `git mv`, history intact (`FEATURE-BOARD.md` item 6; git commit `793ed69`)
- [x] `src/lines/family.ts` born — the ninth line, four family-app tools (`family_status`, `family_checklist`, `family_beacons`, `family_releases`) — verified live in source this sitting, `grep -c "server.tool(" src/lines/family.ts` = 4
- [x] DeepSeek room born (`deepseek/deepseek_message.py`), key probed live and funded (`FEATURE-BOARD.md` item 5)
- [x] Seeding root-tidy — 17 one-shots moved to `seeding/`, history intact (`FEATURE-BOARD.md` item 7)
- [x] **Tested:** ✅ — `FEATURE-BOARD.md` item 6 records a type pass surfacing and fixing a real bug ("the sitting's first true type pass" caught the `LANES_BUS`/`SHUTTLE_BUS` ReferenceError); item 7 records the same-day closing gate: "tsc clean on both doors, the smoke breathing."

### Phase 5: The true names — beacons re-point ✅ (2026-08-15)
- [x] `resonance_beacons` → `beacons` followed at the base (seed 096); `query_beacon`, `listen_beacons.py`, `family.ts` re-pointed (`FEATURE-BOARD.md` item 8)
- [x] `query_beacon` verified live in source this sitting (`src/lines/grammar.ts`, tool registration confirmed by grep)
- [x] **Tested:** ✅ — `FEATURE-BOARD.md` item 8, verbatim: "Proof: tsc clean on both doors, 54 tools registered, every line answered, and `family_beacons` returned `register: \"beacons\"` · 28 rows."

### Phase 6: Battle.net lines ✅ (2026-08-15/16)
- [x] `battlenet/battlenet_character.py` — client-credentials OAuth, named-character reads, token+realm index probed live (`FEATURE-BOARD.md` item 9)
- [x] `battlenet/battlenet_collections.py` — account-wide collections + `--enrich` icons/details (`FEATURE-BOARD.md` item 10)
- [x] **Tested:** ✅ — `FEATURE-BOARD.md` items 9-10, specific live-run outputs: token+realm calls "PROBED LIVE and PASSED (345 US realms listed...)"; collections run landed "213 mounts · 213 pets... 117 toys · 889 achievements... 18 characters landed, 5 not found" — real counts against a live account, not an assertion.

### Phase 7: Planned, not yet built ⬜
- [ ] SPIKE-001: the Weave Handshake (LAN device pairing) — verified absent: no `spike-handshake/` directory on disk (`FEATURE-BOARD.md` §Planned item 1)
- [ ] LAN binding for the Home Doorway (host allowlist + token) — no evidence found in `src/http.ts` beyond the existing Shuttle bind (`FEATURE-BOARD.md` §Planned item 2)
- [ ] Meta/Facebook read-only line — **gated on TJ's consent**, not KP's alone ("i will ask her permission... sovereignty to all", `FEATURE-BOARD.md` §Planned item 3); verified absent: no `src/facebook.ts` or `src/lines/facebook.ts` on disk
- [ ] **Tested:** ⬜ (nothing to test — none built)

---

## KNOWN BUGS
| ID | Description | Status |
|----|-------------|--------|
| B1 | `http.ts` referenced undefined `LANES_BUS` on the refused-write path | Fixed 2026-08-15, corrected to `SHUTTLE_BUS` (`FEATURE-BOARD.md` item 8) |
| B2 | Version number split — `package.json` said 1.0.0, running code said 0.1.0 (`HANDS.md`, Sonnet's 2026-07-20 note) | Since reconciled — `package.json` now reads `0.2.0`; README badge trued to match 2026-08-21. `package.json`'s own `license` field still says `ISC` though `LICENSE` is MIT — open, see CONFUSIONS |

## SESSION LOG
| Date | What Was Done |
|------|---------------|
| 2026-06-30 | Initial commit — Prometheus, first tool `query_atom` |
| 2026-07-07 | Renamed Prometheus → Resonance Bridge |
| 2026-07-29 | The delivery system lands — Grammar line, ten tools, `server_smoke.py` |
| 2026-07-31 | Vercel, Resend, Stripe, GitHub, Discord, Supabase-management lines land |
| 2026-08-14 | Phase A — nine lines under `src/lines/`, family.ts born, DeepSeek room born |
| 2026-08-15 | Beacons re-point (54 tools registered); Battle.net character line built |
| 2026-08-16 | Battle.net collections lane built and landed live, `--enrich` amendment |
| 2026-08-21 | Repo-tender sitting: `docs/CHECKLIST.md` and `docs/STORY-BLOCK.md` created (both absent); README badges trued (version 1.0.0→0.2.0 to match `package.json`), THE STORY section added, TOOLS table's 5 missing rows added (`query_beacon`, `family_status`, `family_checklist`, `family_beacons`, `family_releases` — verified present in `src/lines/*.ts` but absent from the table), truth-pass tool count corrected 10→54 |
