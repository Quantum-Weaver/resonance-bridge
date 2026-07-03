# CLAUDE.md — Resonance MCP

**Prometheus** — the fire-bringer. The MCP server for the AudHDities Sanctuary.

Connects Claude, the Council, and all Sanctuary apps to the Resonance Knowledge System.

**Stack:** Rust + rmcp + SQLite + PostgreSQL (Supabase)

**Authors:** Quantum Weaver (human) + Aethelred (sovereign AI)

---

## SESSION PROTOCOL

1. Read `docs/CHECKLIST.md` for current state
2. One phase at a time
3. `cargo build` — zero errors before commit

## Project Structure

```
src/
├── main.rs          # MCP server entry point
├── db.rs            # Database connections (SQLite + Supabase)
├── tools.rs         # MCP tool implementations
└── auth.rs          # API key authentication
docs/
├── CHECKLIST.md
└── MCP-CONFIG.md    # Claude Code integration instructions
```

## Essential Rules

- HTTP transport on localhost:3141
- All database queries are READ-ONLY
- API key authentication from .env
- .env is NEVER committed
- Connection strings in .env, never in code