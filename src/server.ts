import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import Database from "better-sqlite3";
import { fileURLToPath } from "node:url";
import { registerAirtable } from "./airtable.js";

// Load the repo-root .env by absolute path — the client launches us from ITS
// working directory, not ours (build guide, gotcha #2). Missing .env is fine.
try {
  process.loadEnvFile(fileURLToPath(new URL("../.env", import.meta.url)));
} catch {}

// Read-only, sovereign: this connection cannot write. The ward is code.
const db = new Database(
  process.env.KNOWLEDGE_DB_PATH ??
    "C:/_superposition/resonance-knowledge/knowledge.db",
  { readonly: true }
);

const server = new McpServer({ name: "resonance-bridge", version: "0.1.0" });

server.tool(
  "query_atom",
  "Look up a Resonance Grammar atom by term — definition, etymology, parent, and sensory lexicon (color, sound, texture, temperature).",
  { term: z.string().describe("atom term, lowercase single word, e.g. 'resonance'") },
  async ({ term }) => {
    const row = db
      .prepare(
        "SELECT term, display, definition, etymology, parent, color, sound, texture, temperature FROM atoms WHERE term = ?"
      )
      .get(term.toLowerCase());
    const count = (db.prepare("SELECT COUNT(*) AS n FROM atoms").get() as { n: number }).n;
    return {
      content: [{
        type: "text",
        text: row
          ? JSON.stringify(row, null, 2)
          : `No atom named '${term}'. The Grammar holds ${count}.`,
      }],
    };
  }
);

registerAirtable(server); // the Airtable line — KP's prior organizations of the chaos

const transport = new StdioServerTransport();
await server.connect(transport); // and now it waits, listening
