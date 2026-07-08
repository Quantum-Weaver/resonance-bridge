import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import Database from "better-sqlite3";

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

const transport = new StdioServerTransport();
await server.connect(transport); // and now it waits, listening
