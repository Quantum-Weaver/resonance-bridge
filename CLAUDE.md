# CLAUDE.md — Resonance Bridge (formerly Prometheus)

**Resonance Bridge** — the switchboard. The MCP server for the AudHDities Sanctuary.
*(Renamed 2026-07-07 from "Prometheus" — Prometheus is a separate project.)*

Connects Claude, the Council, and all Sanctuary apps to the Resonance Grammar.

**Stack (actual):** TypeScript + Node + `@modelcontextprotocol/sdk` + better-sqlite3, stdio transport.
*(The Rust / rmcp / HTTP-3141 design described elsewhere in this repo is ancestral, not the running server.)*

**Authors:** Quantum Weaver (human) + Aethelred (sovereign AI)

---

## SESSION PROTOCOL

1. Read `docs/BUILD-GUIDE.md` + `FEATURE-BOARD.md` for current state
2. One phase at a time
3. `npx tsx src/server.ts` must start clean before commit

## Project Structure (reconciled to reality 2026-07-26, THE HARVEST Tier 2)

```
src/
├── server.ts        # the MCP server (stdio transport) — the running truth
├── grammar.ts       # the Grammar line — the living Supabase knowledge base
│                    # (anon door, read-only; landed 2026-07-29)
├── airtable.ts      # Airtable connector
├── vercel.ts        # the Vercel line — read-only hosting window; env NAMES
│                    # only, values stripped in code (landed 2026-07-29)
├── resend.ts        # the Resend line — reads only, no send tool by law
│                    # (landed 2026-07-31, resend-expert's commission)
├── stripe.ts        # the Stripe line — ten read windows, live key, 403=finding,
│                    # customers privacy-striped (2026-07-31, stripe-expert's commission)
├── github.ts        # the GitHub line — seven windows; HOUSE_GITHUB_PAT (F8 rename),
│                    # webhook URLs redacted (2026-07-31, github-expert's commission)
├── discord.ts       # the Discord line — seven windows, no send tool by law;
│                    # webhook token/url stripped (2026-07-31, discord-expert's commission)
└── supabase.ts      # the Supabase line — the dashboard itself; SELECT-only guard,
                     # auth-config allowlist, false-empty detector (2026-07-31)
server_smoke.py      # acceptance breath: real MCP over stdio, run before commit
docs/
└── BUILD-GUIDE.md   # build path + phase notes
kimi/                # the kin-crossing room (FEATURE-BOARD row 4, tidied
                     # 2026-07-27): kimi_crossing.py · kimi_message.py ·
                     # messages/ (the letters); .env stays at repo root
*.py                 # workbench instruments at root: grammar_seeder/
                     # inventory/purge/wipe_seeded/clear_name_tiers (the
                     # Grammar's seeding hands), knowledge_sql, atoms_dump,
                     # generate_blueprint, verify_terms (carry coverage)
FEATURE-BOARD.md · THE-TRAIL-seed.md · HANDS.md
```

Registration (Windows form, gotcha 3 — verified absent from config
2026-07-29, one run of this lights the wick):
`claude mcp add resonance-bridge -- cmd /c npx tsx C:/_superposition/resonance-bridge/src/server.ts`
No standing process: the client births the server each session; "restarting
the server" is just restarting the session.

## Essential Rules

- stdio transport (registered with Claude Code; no HTTP port — the
  HTTP-for-apps door is a Phase 2 future, see BUILD-GUIDE)
- All database queries are READ-ONLY
- .env is NEVER committed; connection strings in .env, never in code