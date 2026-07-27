# CLAUDE.md — Resonance Bridge (formerly Prometheus)

**Resonance Bridge** — the switchboard. The MCP server for the AudHDities Sanctuary.
*(Renamed 2026-07-07 from "Prometheus" — Prometheus is a separate project.)*

Connects Claude, the Council, and all Sanctuary apps to the Resonance Knowledge System.

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
└── airtable.ts      # Airtable connector
docs/
└── BUILD-GUIDE.md   # build path + phase notes
*.py                 # workbench instruments at root: grammar_seeder/
                     # inventory/purge (the Grammar's seeding hands),
                     # knowledge_sql, kimi_crossing/message, atoms_dump
FEATURE-BOARD.md · THE-TRAIL-seed.md · HANDS.md
```

Registration: `claude mcp add resonance-bridge -- npx tsx C:/_superposition/resonance-bridge/src/server.ts`

## Essential Rules

- stdio transport (registered with Claude Code; no HTTP port — the
  HTTP-for-apps door is a Phase 2 future, see BUILD-GUIDE)
- All database queries are READ-ONLY
- .env is NEVER committed; connection strings in .env, never in code