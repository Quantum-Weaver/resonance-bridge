import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import Database from "better-sqlite3";
import { fileURLToPath } from "node:url";
import { registerGrammar } from "./lines/grammar.js";
import { registerVercel } from "./lines/vercel.js";
import { registerResend } from "./lines/resend.js";
import { registerStripe } from "./lines/stripe.js";
import { registerGitHub } from "./lines/github.js";
import { registerDiscord } from "./lines/discord.js";
import { registerSupabase } from "./lines/supabase.js";
import { registerCloudflare } from "./lines/cloudflare.js";

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
registerVercel(server); // the Vercel line — a read-only window on the hosting
registerResend(server); // the Resend line — reads only; a send is a consent gate, never a tool
registerStripe(server); // the Stripe line — ten windows on the merchant account, live-mode, GETs forever
registerGitHub(server); // the GitHub line — seven windows; HOUSE_GITHUB_PAT, deliberate or not at all
registerDiscord(server); // the Discord line — reads only; a post is outward speech, gated forever
registerSupabase(server); // the Supabase line — the dashboard itself; SELECT-only, allowlist-warded
registerCloudflare(server); // the Cloudflare line — a read-only window on the DNS ground, GETs forever

const transport = new StdioServerTransport();
await server.connect(transport);
