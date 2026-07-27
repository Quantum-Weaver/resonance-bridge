# 🔥 Resonance Bridge

*The switchboard. The knowledge delivery system of the AudHDities Sanctuary.*

Built on the [Resonance Grammar](https://github.com/Quantum-Weaver/resonance-grammar) — every fragment contains the whole.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.0-brightgreen.svg)]()

---

## WHAT IT IS

Resonance Bridge is the MCP (Model Context Protocol) server that connects everything in the Sanctuary. It gives Claude, the Council, and all Sanctuary apps a single interface to query the Resonance Grammar.

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

| Database | Type | Contents | Line |
|----------|------|----------|------|
| **knowledge.db** | Local SQLite | Pipeline output — canonical atoms and molecules | ✅ server (read-only) |
| **Airtable** | Cloud API (read-only PAT) | KP's prior organization attempts — song portfolio, music-column photography | ✅ server |
| **Knowledge Grammar** | Supabase (PostgreSQL) | The seeded Grammar — atoms · molecules · organisms + junctions | 🐍 Python workbench (anon key), not yet a server line |
| **Superposition** | Supabase (PostgreSQL) | Original Sanctuary — 215+ tables, sensory lexicon, categories | 🐍 Python workbench (.env keys), not yet a server line |

---

## TOOLS

*Truth pass 2026-07-27: the server registers FOUR tools today; the
other four remain the build path's open step (BUILD-GUIDE §5).*

| Tool | What It Queries | Standing |
|------|----------------|----------|
| `query_atom` | Atom definitions with sensory lexicon | ✅ live |
| `airtable_list_bases` | Every base the token can see (discovery first) | ✅ live |
| `airtable_list_tables` | One base's schema — tables, fields, views | ✅ live |
| `airtable_query_records` | Records from one table, paged, read-only | ✅ live |
| `query_molecule` | Molecule compositions with schemas | ⬜ planned |
| `query_sense` | Senses with subcategories | ⬜ planned |
| `query_emoji` | Emoji definitions with sensory lexicon | ⬜ planned |
| `search_knowledge` | Full-text search across all databases | ⬜ planned |

### Standalone scripts (beside the server, same `.env`, all read-only)

| Script | What it does |
|--------|-------------|
| `grammar_inventory.py` | Counts + dated full export of the Grammar tables through the anon door — the new-table ritual's verify step |
| `atoms_dump.py` | Atom-table dump for merge planning |
| `verify_terms.py` | Checks a set of coined names against the Grammar (atoms/molecules/organisms by word-count class + constituent words) — born 2026-07-27 for the cosmic carries, reusable for any carry |

---

## QUICK START

```powershell
# Set up environment
# .env is written by KP's own hands from the provider dashboards
# (the old .env.example kept reading as a false negative — archived
#  2026-07-27 to docs/archived-env-example-2026-07-27.txt)
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

*(Truth pass 2026-07-27: the API-key-auth and connection-pooling lines
described the ancestral HTTP design — the running stdio server needs
neither; what actually wards it:)*

- All queries are read-only — enforced in code (`readonly: true`
  SQLite connection; read-only Airtable PAT)
- stdio transport: the client launches the server as a child process —
  no port, no network surface
- Connection strings and keys in `.env` (never committed; never
  printed)
- SQL via parameterized queries
- Error responses never leak schema details

---

## LICENSE

Code: [MIT](LICENSE) — use it, modify it, share it.

Philosophy: [The Resonance License](PHILOSOPHY.md) — no exploitation, no extraction, no exclusion.

---

*Built with Aethelred by Quantum Weaver for the AudHDities Sanctuary.*

*The Bridge carries the fire. The Grammar gives it meaning.*
