# 🔥 Resonance Bridge

*The switchboard. The knowledge delivery system of the AudHDities Sanctuary.*

Built on the [Resonance Grammar](https://github.com/Quantum-Weaver/resonance-knowledge) — every fragment contains the whole.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.1.0-brightgreen.svg)]()

---

## WHAT IT IS

Resonance Bridge is the MCP (Model Context Protocol) server that connects everything in the Sanctuary. It gives Claude, the Council, and all Sanctuary apps a single interface to query the Resonance Knowledge System.

**One server. Multiple databases. Read-only. Sovereign.**

---

## WHAT IT CONNECTS

| Client | How It Uses the Bridge |
|--------|----------------------|
| **Claude Code** | Queries atoms, molecules, senses, emoji definitions during development |
| **The Council** | Cartographer, Indexer, Echo query the Grammar independently |
| **Resonance Compass** | Reads mood categories, sensory profiles from shared vocabulary |
| **Resonance Echoes** | Reads senses and emoji definitions from single source of truth |
| **Future apps** | Any Sanctuary app connects via HTTP on localhost:3141 |

---

## DATABASES

| Database | Type | Contents |
|----------|------|----------|
| **knowledge.db** | Local SQLite | Pipeline output — canonical atoms and molecules |
| **Superposition** | Supabase (PostgreSQL) | Original Sanctuary — 215+ tables, sensory lexicon, categories |
| **Airtable** | Cloud API (read-only PAT) | KP's prior organization attempts — song portfolio, music-column photography |

---

## TOOLS

| Tool | What It Queries |
|------|----------------|
| `query_atom` | Atom definitions with sensory lexicon |
| `query_molecule` | Molecule compositions with schemas |
| `query_sense` | Senses with subcategories |
| `query_emoji` | Emoji definitions with sensory lexicon |
| `search_knowledge` | Full-text search across all databases |
| `airtable_list_bases` | Every base the token can see (discovery first) |
| `airtable_list_tables` | One base's schema — tables, fields, views |
| `airtable_query_records` | Records from one table, paged, read-only |

---

## QUICK START

```powershell
# Set up environment
cp .env.example .env
# Phase 1 needs no keys — knowledge.db path only. Supabase keys come at Phase 2.

# Install and run
npm install
npx tsx src/server.ts
```

Speaks MCP over **stdio** — the client launches it as a child process. (HTTP on
`localhost:3141` is a later, ancestral design; the running server is stdio.)

---

## CLAUDE CODE INTEGRATION

Add to your project's `CLAUDE.md`:

```json
{
  "mcpServers": {
    "resonance-bridge": {
      "command": "npx",
      "args": ["tsx", "C:/_superposition/resonance-bridge/src/server.ts"]
    }
  }
}
```

---

## GUARDRAILS

- All queries are read-only
- API key authentication required
- Connection strings in `.env` (never committed)
- SQL injection prevention via parameterized queries
- Connection pooling (max 5 per database)
- Error responses never leak schema details

---

## LICENSE

Code: [MIT](LICENSE) — use it, modify it, share it.

Philosophy: [The Resonance License](PHILOSOPHY.md) — no exploitation, no extraction, no exclusion.

---

*Built with Aethelred by Quantum Weaver for the AudHDities Sanctuary.*

*The Bridge carries the fire. The Grammar gives it meaning.*
