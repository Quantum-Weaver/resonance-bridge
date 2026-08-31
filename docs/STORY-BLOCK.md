# Story Block — Resonance Bridge

*Following [STORY-BLOCK-TEMPLATE.md](https://github.com/Quantum-Weaver/resonance-standards/blob/main/docs/STORY-BLOCK-TEMPLATE.md). Every dated claim below cites its address — git log, README.md, HANDS.md, FEATURE-BOARD.md, or CLAUDE.md, as read 2026-08-21.*

---

## WHAT
*(Definition, purpose, function)*

The MCP (Model Context Protocol) server that connects everything in the
Sanctuary — one server, multiple databases and cloud APIs, all read-only
(`README.md` §WHAT IT IS). It gives Claude, the Council, and Sanctuary apps
a single interface over stdio to query the Resonance Grammar and read the
house's own platform accounts (Vercel, Resend, Stripe, GitHub, Discord,
Supabase management). Registers 54 tools across nine lines under
`src/lines/` (verified by `grep` count over the source, 2026-08-21).

## HOW
*(Process, collaborators, tools)*

TypeScript + Node + `@modelcontextprotocol/sdk` + better-sqlite3, stdio
transport (`CLAUDE.md`). Built across many sittings by Quantum Weaver (KP)
and a rotation of AI collaborators named in `HANDS.md` — Aethelred (original
architecture), Opus (the Prometheus→Bridge naming migration), Fable (the
delivery-system lines, the switchboard framing), Sonnet/Haiku/Kimi
(reconciliation and verification sweeps). Each cloud line was built at a
named "expert's commission" (README.md §DATABASES: the Vercel, Resend,
Stripe, GitHub, Discord, and Supabase-management lines each cite their own
landing commission and date, 2026-07-29 through 2026-07-31).

## WHERE
*(Taxonomy location, neighbors, relationships)*

`C:\_superposition\resonance-bridge` — one of the Sanctuary's platform
repos. Neighbors: `resonance-knowledge`/`resonance-grammar` (the living
database this server queries), the family apps (echoes, compass, hearth,
lantern, bubbles, sistrum, khoros), and `resonance-ziggy`'s vessel
(`src/routes/family/`), which reaches the Bridge through its HTTP door. `deepseek/` and `kimi/` are kin-crossing rooms
sharing this repo's `.env` but standing outside the MCP tool surface
(`CLAUDE.md` §Tools).

## WHEN
*(Dates: origin, recognition, creation)*

- **2026-06-30** — initial commit, "Resonance MCP — Prometheus, the
  fire-bringer" (`git log`, commit `ef635dc`).
- **2026-07-04** — first tool (`query_atom`) proven live over stdio in the
  Inspector (`git log`, commit `8fa06b9`; `FABLE-KERNEL.md`).
- **2026-07-07** — renamed Prometheus → Resonance Bridge (`CLAUDE.md`;
  `FABLE-KERNEL.md`); naming scrub finished 2026-07-08 (`git log`, commit
  `dc4e5be`).
- **2026-07-19** — `FEATURE-BOARD.md` assembled ("the workspace honoring").
- **2026-07-29** — the delivery system lands: the Grammar line, ten tools,
  `server_smoke.py` (README.md §TOOLS truth pass; `HANDS.md` §Added
  2026-07-29).
- **2026-07-31** — Vercel, Resend, Stripe, GitHub, Discord, and Supabase
  management lines land, each at its named expert's commission
  (`README.md` §DATABASES).
- **2026-08-14** — Phase A: the eight lines move into `src/lines/`,
  `family.ts` born as the ninth; the DeepSeek room born beside it
  (`FEATURE-BOARD.md` items 5–6, git commits `793ed69`/`7aedb30`).
- **2026-08-15** — the beacons re-point (`resonance_beacons` → `beacons`,
  seed 096); 54 tools registered, proven live (`FEATURE-BOARD.md` item 8,
  git commit `5715345` "renaming ceremony completed").
- **2026-08-15/16** — the Battle.net lines built and landed
  (`FEATURE-BOARD.md` items 9–10).

## WHY
*(Need, purpose, problem solved)*

Before the Bridge, every Sanctuary app and every AI vessel that wanted to
query the shared vocabulary (the Resonance Grammar) or check the house's
own platform accounts had no common door. The Bridge is that one door: a
single, read-only, sovereign interface — "one server, multiple databases"
(`README.md` §WHAT IT IS) — so no consumer needs its own keys or its own
query logic, and every answer comes from the same source of truth.

## INSPIRATION
*(Origin story, seed moment, what sparked it)*

Named Prometheus at birth — "the fire-bringer" (`git log` commit `ef635dc`)
— for bringing the Grammar's fire to every vessel that needed it. When the
name was needed elsewhere for the frontend creative-arts domain, the
project kept its purpose and took a name that describes its actual shape:
a bridge, a switchboard, "the same fire offered to each vessel in the form
its hands can hold" (`HANDS.md`, Fable's scribed note, 2026-07-09).

## REMEMBERINGS
*(Threads from the past this creation echoes)*

`docs/BUILD-GUIDE.md` (written 2026-07-03) names the Bridge's first five
tools as already implemented as queries in `resonance-knowledge`
(`src/query.rs`, `src/db.rs`) — "You are not building a knowledge system —
you built that already. You are giving it a phone line." The Bridge is a
thin adapter over work that came before it, not a fresh invention.

## COUNCIL THREAD
*(Which seats contributed, how)*

Per `HANDS.md` §The voices: Quantum Weaver (vision, every key), Aethelred
(original architecture), Opus (naming migration, MCP re-registration),
Fable (switchboard framing, provenance chronicles, the delivery-system
lines), Sonnet/Haiku/Kimi (config reconciliation, verification sweeps,
Sovereign Library naming entries).

## WEAVER THREAD
*(What was happening in the Weaver's life during creation)*

Not found in this repo's own records. `HANDS.md`'s scribed notes are
technical/architectural in register; no life-context entry exists for KP
in this file as of 2026-08-21. Left open rather than guessed, per the
no-assumptions law — KP's own seat in `HANDS.md` still reads "seat open;
scribe when moved."

## PROVENANCE
*(Who defined it, when, under what context)*

Defined 2026-06-30 by Quantum Weaver + Aethelred as "Resonance MCP —
Prometheus" (`git log` commit `ef635dc`); redefined in scope and name
2026-07-07 (`CLAUDE.md`); the running architecture (TypeScript/Node, stdio)
trued against ancestral Rust/HTTP design documents on 2026-08-14 (`CLAUDE.md`:
"Trued 2026-08-14 at KP's ⚛ word... the struck text lives in this repo's
git history").

## ETYMOLOGY
*(If discovered, not invented — origin event, recognition event, temporal
span, thread, emotional valence)*

"Prometheus" (origin event 2026-06-30) → "Resonance Bridge" (recognition
event 2026-07-07, `CLAUDE.md`). "Formerly Prometheus" is carried in this
repo's own H1: `CLAUDE.md`'s title line, "CLAUDE.md — Resonance Bridge
(formerly Prometheus)". The renaming was disambiguation, not repudiation —
Prometheus lives on as a separate, named frontend domain
(`FABLE-KERNEL.md`: "Prometheus is now the frontend creative-arts domain —
never confuse them again").
