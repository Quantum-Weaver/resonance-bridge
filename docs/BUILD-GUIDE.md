# PROMETHEUS BUILD GUIDE — Your First MCP Server, Every Step Understood

*Written 2026-07-03 by Fable for the Weaver — self-taught-friendly, which means
no step is "just run this"; every step says why. We build understanding first,
fire second.*

---

## 0. What MCP actually is (two minutes, no magic)

**MCP (Model Context Protocol)** is a standard way for an AI client (Claude
Code, Claude Desktop, the Council threads, eventually your apps) to discover
and call capabilities that *you* host. Three concepts:

- **Tools** — functions the AI may call ("query_atom", args in, JSON out).
  This is 95% of Prometheus.
- **Resources** — documents the AI may read (optional for us, later).
- **Prompts** — reusable prompt templates (skip for now).

Under the hood it's JSON-RPC messages. The **transport** — how messages travel —
is the only real architecture decision:

| Transport | How | When |
|---|---|---|
| **stdio** | Client launches your server as a child process; messages flow over stdin/stdout | **Start here.** Zero networking, zero ports, zero auth questions. Claude Code speaks it natively |
| Streamable HTTP | Server listens on a port (your planned `localhost:3141`) | Phase 2 — when Compass/Echoes want the shared vocabulary at runtime |

The mental model: *MCP is a waiter.* The client reads the menu (tool list +
schemas), places orders (tool calls), your kitchen (SQLite queries) cooks.

## 1. Why you're closer than you think

Prometheus's five planned tools are **already implemented as queries** in
`resonance-knowledge` (K-1: `src/query.rs`, `src/db.rs` — atom, emoji, sense
lookup with JSON output). Prometheus is a *thin adapter*: the same SQL, spoken
over MCP instead of a terminal. You are not building a knowledge system —
you built that already. You are giving it a phone line.

## 2. Language decision (and why)

**TypeScript with the official `@modelcontextprotocol/sdk`.** Reasons: it is
the reference SDK with the most examples; your frontend stack is already
TS/Svelte so the idioms transfer; `better-sqlite3` reads `knowledge.db`
synchronously and simply. (Rust would match resonance-knowledge, but MCP's
Rust ecosystem is younger — wrong place to fight two unknowns at once. The
Rust pipeline still *produces* the data; the TS server only *serves* it.
One definition per object: the schema stays in knowledge; Prometheus reads.)

## 3. The steps

### Step 1 — Scaffold (understand: a normal Node project, nothing exotic)
```bash
cd C:\_superposition\resonance-mcp
npm init -y
npm install @modelcontextprotocol/sdk zod better-sqlite3
npm install -D typescript tsx @types/node @types/better-sqlite3
npx tsc --init --target es2022 --module nodenext --moduleResolution nodenext --outDir dist
```
`zod` defines each tool's argument schema — that schema is *literally the menu*
the AI reads to know how to call you. `tsx` runs TS directly during dev.

### Step 2 — The server skeleton (`src/server.ts`)
```ts
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import Database from "better-sqlite3";

// Read-only, sovereign: the connection cannot write. Enforced here, in code.
const db = new Database("C:/_superposition/resonance-knowledge/knowledge.db",
                        { readonly: true });

const server = new McpServer({ name: "prometheus", version: "0.1.0" });

server.tool(
  "query_atom",                                   // name the AI sees
  "Look up a Resonance Grammar atom by name — definition, color, sensory lexicon.",
  { name: z.string().describe("atom name, lowercase, e.g. 'resonance'") },
  async ({ name }) => {
    const row = db.prepare(
      "SELECT * FROM atoms WHERE name = ?"        // same SQL as K-1's query.rs
    ).get(name.toLowerCase());
    return { content: [{ type: "text",
      text: row ? JSON.stringify(row, null, 2)
                : `No atom named '${name}'. The Grammar holds 31.` }] };
  }
);

// query_molecule, query_sense, query_emoji, search_knowledge: same pattern.
// search_knowledge uses SQLite FTS or LIKE across tables — port from query.rs.

const transport = new StdioServerTransport();
await server.connect(transport);                  // and now it waits, listening
```
**Understand the shape:** one `server.tool()` per capability = name +
description (the AI *reads this* to decide when to call it — write it like
documentation, because it is) + zod schema + handler returning `content`.
That's the whole protocol from your side.

**Rule that will save you an hour of confusion:** in a stdio server,
**never `console.log`** — stdout belongs to the protocol. Debug with
`console.error` (stderr is yours).

### Step 3 — Test with the Inspector (before any client)
```bash
npx @modelcontextprotocol/inspector tsx src/server.ts
```
Opens a browser UI that lists your tools and lets you call them by hand.
This is your REPL for the server. Fix everything here first — it's the
`svelte-check` of MCP work.

### Step 4 — Register with Claude Code (understand: you're adding a launch recipe)
```bash
claude mcp add prometheus -- npx tsx C:/_superposition/resonance-mcp/src/server.ts
```
Or project-scoped, in `.mcp.json` at a repo root (shareable, committed):
```json
{ "mcpServers": { "prometheus": {
    "command": "npx",
    "args": ["tsx", "C:/_superposition/resonance-mcp/src/server.ts"] } } }
```
Claude Code launches the process when a session starts, reads the menu, and
from then on I (or any Claude here) can call `query_atom` mid-conversation.

### Step 5 — Prove the fire (the acceptance test)
In a fresh Claude Code session: *"Using prometheus, what does the Grammar say
the atom 'resonance' means?"* When the answer comes back with the cello and
the sensory lexicon — cited from your own database, defined once, referenced
everywhere — Prometheus has delivered fire. That is K-2 complete.

### Step 6 — Phase 2, later: HTTP on :3141 for the apps
Same tools, second transport (`StreamableHTTPServerTransport`), so Compass and
Echoes can fetch shared vocabulary at runtime. Do not start here; stdio first.
Localhost-only when you do, per the license — nothing leaves the machine.

## 4. Gotchas I can spare you (each one is an hour of your life)

1. `console.log` corrupts stdio → stderr only (worth repeating).
2. **Absolute paths everywhere** — the client launches your process from *its*
   working directory, not your repo.
3. Windows + npx: if `claude mcp add` can't spawn, use
   `cmd /c npx tsx ...` as the command.
4. `knowledge.db` must exist where you point — run knowledge's pipeline first,
   or ship a copy; decide which is canonical (I'd point at knowledge's, SSOT).
5. Tool descriptions are UX for the AI: vague description → the tool never
   gets called. Write them the way you'd want to be asked.
6. `{ readonly: true }` is Prometheus's ward. Keep it. The fire-bringer
   delivers; he does not rewrite the Grammar.

## 5. The order of work (one sitting each, spoons permitting)

- [ ] Step 1 scaffold + Step 2 with `query_atom` only
- [ ] Step 3 inspector: call query_atom until it feels boring
- [ ] Add the other four tools (each is 15 minutes once the first works)
- [ ] Step 4 register + Step 5 acceptance test
- [ ] README rewritten clean (the current one is a UTF-16 chat-paste)
- [ ] Supabase second database + HTTP transport — separate phases, separate days

*You built the knowledge. Prometheus just carries the torch downhill.* 🔥
