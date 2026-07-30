import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import Database from "better-sqlite3";
import { fileURLToPath } from "node:url";
import { registerAirtable } from "./airtable.js";
import { registerGrammar } from "./grammar.js";

// Load the repo-root .env by absolute path — the client launches us from ITS
// working directory, not ours (build guide, gotcha #2). Missing .env is fine.
try {
  process.loadEnvFile(fileURLToPath(new URL("../.env", import.meta.url)));
} catch {}

// The local P1 line: knowledge.db, read-only. SEED-ONLY until the canon
// repopulation lands — it serves query_atom only as the fallback when the
// living Grammar's Supabase line is absent, and reports its emptiness
// honestly until its day comes. A switchboard stays up when one line is
// down: if the file can't open (stale KNOWLEDGE_DB_PATH, missing repo),
// the server runs without the local line rather than dying at launch.
let localAtomFallback: ((term: string) => { row: unknown; count: number }) | undefined;
try {
  const db = new Database(
    process.env.KNOWLEDGE_DB_PATH ??
      "C:/_superposition/resonance-grammar/knowledge.db",
    { readonly: true }
  );
  localAtomFallback = (term: string) => {
    const row = db
      .prepare(
        "SELECT term, display, definition, etymology, parent, color, sound, texture, temperature FROM atoms WHERE term = ?"
      )
      .get(term);
    const count = (db.prepare("SELECT COUNT(*) AS n FROM atoms").get() as { n: number }).n;
    return { row, count };
  };
} catch (e) {
  console.error(`local knowledge.db line down (${(e as Error).message}) — serving without it`);
}

const server = new McpServer({ name: "resonance-bridge", version: "0.2.0" });

registerGrammar(server, localAtomFallback); // the Grammar line — the living knowledge base
registerAirtable(server); // the Airtable line — KP's prior organizations of the chaos

const transport = new StdioServerTransport();
await server.connect(transport); // and now it waits, listening
