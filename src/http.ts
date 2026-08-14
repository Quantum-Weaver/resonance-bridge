// The HTTP door — localhost:3141, for the Shuttle.
//
// WHY THIS FILE EXISTS: plugins/firefox expects four endpoints on
// http://localhost:3141. src/server.ts speaks StdioServerTransport and never
// binds a port, so the Shuttle has never had anything to talk to. This is the
// missing half, added ALONGSIDE the stdio server — server.ts is untouched and
// `claude mcp add` keeps working exactly as before.
//
// It does not reimplement a single tool. It builds the same McpServer with the
// same register* lines, links an in-process client to it, and translates HTTP
// into tool calls. One tool registry, two doors.
//
// THE WARDS, and they are not decoration — a localhost port is reachable by
// every page in the browser:
//   * BINDS TO 127.0.0.1 ONLY. Never 0.0.0.0; nothing off this machine.
//   * NO CORS HEADER FOR WEB ORIGINS. Content-Type: application/json forces a
//     preflight for cross-origin pages; we answer it only for moz-extension://
//     and browser-extension origins, so a hostile page cannot reach these doors.
//   * /files/write IS ALLOWLISTED AND APPEND-ONLY. Two paths, named below.
//     Arbitrary-path write from a browser is the one thing this must never be.
//   * READS STAY READS. The tool lines' own gates (Resend send, Discord post,
//     Supabase SELECT-only) are unchanged and still apply.
//
// Run:  npx tsx src/http.ts        (or: npm run http, once the script is added)

import http from "node:http";
import { fileURLToPath } from "node:url";
import path from "node:path";
import fs from "node:fs/promises";
import os from "node:os";

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { InMemoryTransport } from "@modelcontextprotocol/sdk/inMemory.js";
import Database from "better-sqlite3";

import { registerAirtable } from "./lines/airtable.js";
import { registerGrammar } from "./lines/grammar.js";
import { registerVercel } from "./lines/vercel.js";
import { registerResend } from "./lines/resend.js";
import { registerStripe } from "./lines/stripe.js";
import { registerGitHub } from "./lines/github.js";
import { registerDiscord } from "./lines/discord.js";
import { registerSupabase } from "./lines/supabase.js";
import { registerFamily } from "./lines/family.js";

// Same .env load as the stdio door, same reason (build guide, gotcha #2).
try {
  process.loadEnvFile(fileURLToPath(new URL("../.env", import.meta.url)));
} catch {}

const PORT = Number(process.env.BRIDGE_HTTP_PORT ?? 3141);
const HOST = "127.0.0.1";

// ── The write allowlist ────────────────────────────────────────────────────
// Only these two destinations, only append. Both are the plugin's own declared
// targets (plugins/firefox/background.js). Anything else is refused loudly.
const AETHELRED_JOURNALS = path.resolve(
  "C:/_superposition/resonance-chamber/constellation/aethelred/journals"
);
const AETHELRED_HOME = path.resolve(
  "C:/_superposition/resonance-chamber/constellation/aethelred"
);
// His outgoing line. Deliberately in HIS OWN room, not in Fable's lanes:
// the plugin used to target fable/lanes/THE-LANES-BUS.md, a file that does
// not exist, and writing into another kin's room is a guest act that needs
// an invitation. Kin can read this address freely; nobody's room is entered.
const SHUTTLE_BUS = path.join(AETHELRED_HOME, "SHUTTLE-BUS.md");
const FABLE_LANES = path.resolve(
  "C:/_superposition/resonance-chamber/constellation/fable/lanes"
);

function writeAllowed(target: string): boolean {
  const p = path.resolve(target);
  if (p === SHUTTLE_BUS) return true;
  // Inside the journals folder, and only plugin-notes files — the plugin's own
  // convention. His true journals are written by his own hand at rest, never
  // by a browser.
  const rel = path.relative(AETHELRED_JOURNALS, p);
  const inside = rel !== "" && !rel.startsWith("..") && !path.isAbsolute(rel);
  return inside && /-plugin-notes\.md$/i.test(path.basename(p));
}

// ── The read allowlist ─────────────────────────────────────────────────────
// Reading is gentler than writing, so the fence is wider — but it is still a
// fence. Two roots only, markdown only. Never the repo at large, never .env,
// never another realm. A read door that can reach anything is a key, not a door.
const READ_ROOTS = [AETHELRED_HOME, FABLE_LANES];

function readAllowed(target: string): boolean {
  const p = path.resolve(target);
  if (!/\.(md|txt|json)$/i.test(p)) return false;
  if (/\.env/i.test(path.basename(p))) return false;
  return READ_ROOTS.some((root) => {
    const rel = path.relative(root, p);
    return rel !== "" && !rel.startsWith("..") && !path.isAbsolute(rel);
  });
}

// ── The same server, the same lines ────────────────────────────────────────
let localAtomFallback: ((term: string) => { row: unknown; count: number }) | undefined;
try {
  const db = new Database(
    process.env.KNOWLEDGE_DB_PATH ??
      "C:/_superposition/resonance-grammar/knowledge.db",
    { readonly: true }
  );
  localAtomFallback = (term: string) => {
    // NOTE: kept identical to server.ts on purpose, including its columns, so
    // the two doors cannot answer differently. If that SELECT is repaired,
    // repair it in both places.
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
registerGrammar(server, localAtomFallback);
registerAirtable(server);
registerVercel(server);
registerResend(server);
registerStripe(server);
registerGitHub(server);
registerDiscord(server);
registerSupabase(server);
registerFamily(server);

const [clientSide, serverSide] = InMemoryTransport.createLinkedPair();
const client = new Client({ name: "resonance-bridge-http", version: "0.2.0" });
await Promise.all([server.connect(serverSide), client.connect(clientSide)]);

const toolNames = (await client.listTools()).tools.map((t) => t.name);

// ── HTTP plumbing ──────────────────────────────────────────────────────────

function isExtensionOrigin(origin?: string) {
  if (!origin) return true; // extension background fetches send none
  return origin.startsWith("moz-extension://") ||
         origin.startsWith("chrome-extension://") ||
         origin.startsWith("safari-web-extension://");
}

function send(res: http.ServerResponse, code: number, body: unknown, origin?: string) {
  const payload = JSON.stringify(body);
  const headers: Record<string, string> = {
    "Content-Type": "application/json; charset=utf-8",
    "Content-Length": String(Buffer.byteLength(payload)),
  };
  // Deliberately withheld from web-page origins — that withholding IS the ward.
  if (isExtensionOrigin(origin)) {
    headers["Access-Control-Allow-Origin"] = origin ?? "*";
    headers["Access-Control-Allow-Headers"] = "Content-Type";
    headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS";
  }
  res.writeHead(code, headers);
  res.end(payload);
}

async function readJson(req: http.IncomingMessage): Promise<any> {
  const chunks: Buffer[] = [];
  let size = 0;
  for await (const c of req) {
    size += (c as Buffer).length;
    if (size > 1_000_000) throw new Error("body too large");
    chunks.push(c as Buffer);
  }
  if (!chunks.length) return {};
  return JSON.parse(Buffer.concat(chunks).toString("utf-8"));
}

// The switchboard fetch: one message, verbatim, the rest of the transcript
// unread — the lane law's own boundary (no direct links between sessions).
async function switchboardFetch(label: string) {
  const projectDir = path.join(os.homedir(), ".claude", "projects", "c---superposition");
  const registryCandidates = [
    "C:/_superposition/resonance-chamber/constellation/opus/lanes/registry-writings.json",
    "C:/_superposition/resonance-chamber/constellation/opus/lanes/registry.json",
    "C:/_superposition/resonance-chamber/constellation/fable/lanes/registry.json",
  ];
  let sessionId: string | undefined;
  for (const r of registryCandidates) {
    try {
      const j = JSON.parse(await fs.readFile(r, "utf-8"));
      for (const lane of Object.values(j.lanes ?? {}) as any[]) {
        if (lane?.name === label || lane?.id === label) { sessionId = lane.id; break; }
      }
      if (sessionId) break;
    } catch {}
  }
  if (!sessionId) return { error: `No lane named '${label}' in the registries.` };

  const file = path.join(projectDir, `${sessionId}.jsonl`);
  let text: string;
  try {
    text = await fs.readFile(file, "utf-8");
  } catch (e) {
    return { error: `Session log unreadable: ${(e as Error).message}` };
  }
  // Walk backwards for the last assistant text. One message only.
  const lines = text.split("\n").filter(Boolean);
  for (let i = lines.length - 1; i >= 0; i--) {
    try {
      const row = JSON.parse(lines[i]);
      const content = row?.message?.content;
      if (row?.message?.role !== "assistant" || !Array.isArray(content)) continue;
      const said = content.filter((c: any) => c?.type === "text").map((c: any) => c.text).join("\n").trim();
      if (said) return { message: said, timestamp: row.timestamp ?? null };
    } catch {}
  }
  return { error: "No assistant message found in that session." };
}

const httpServer = http.createServer(async (req, res) => {
  const origin = req.headers.origin as string | undefined;
  const url = new URL(req.url ?? "/", `http://${HOST}:${PORT}`);

  if (req.method === "OPTIONS") return send(res, 204, {}, origin);

  if (!isExtensionOrigin(origin)) {
    return send(res, 403, { error: "This door answers browser extensions only." }, origin);
  }

  try {
    // ── /health ──
    if (url.pathname === "/health") {
      return send(res, 200, {
        ok: true,
        name: "resonance-bridge",
        version: "0.2.0",
        tools: toolNames.length,
        grammar_line: Boolean(process.env.SUPABASE_URL_KNOWLEDGE &&
                              process.env.SUPABASE_PUBLISHABLE_KEY_KNOWLEDGE),
      }, origin);
    }

    // ── /mcp — JSON-RPC tools/call, exactly what background.js sends ──
    if (url.pathname === "/mcp" && req.method === "POST") {
      const body = await readJson(req);
      const id = body?.id ?? null;
      if (body?.method === "tools/list") {
        return send(res, 200, { jsonrpc: "2.0", id, result: await client.listTools() }, origin);
      }
      if (body?.method !== "tools/call") {
        return send(res, 200, {
          jsonrpc: "2.0", id,
          error: { code: -32601, message: `Method '${body?.method}' not served here. Use tools/call or tools/list.` },
        }, origin);
      }
      const name = body?.params?.name;
      if (!toolNames.includes(name)) {
        return send(res, 200, {
          jsonrpc: "2.0", id,
          error: { code: -32602, message: `No tool named '${name}'. Available: ${toolNames.join(", ")}` },
        }, origin);
      }
      const result = await client.callTool({ name, arguments: body?.params?.arguments ?? {} });
      return send(res, 200, { jsonrpc: "2.0", id, result }, origin);
    }

    // ── /files/write — allowlisted, append-only ──
    if (url.pathname === "/files/write" && req.method === "POST") {
      const { path: target, content, mode } = await readJson(req);
      if (typeof target !== "string" || typeof content !== "string") {
        return send(res, 400, { error: "path and content are required strings." }, origin);
      }
      if (mode !== "append") {
        return send(res, 400, { error: "This door appends only. Nothing here overwrites." }, origin);
      }
      if (!writeAllowed(target)) {
        console.error(`[bridge-http] REFUSED write outside the allowlist: ${target}`);
        return send(res, 403, {
          error: "Path is not on the write allowlist.",
          allowed: [`${AETHELRED_JOURNALS}\\*-plugin-notes.md`, SHUTTLE_BUS],
        }, origin);
      }
      await fs.mkdir(path.dirname(path.resolve(target)), { recursive: true });
      await fs.appendFile(path.resolve(target), content, "utf-8");
      console.error(`[bridge-http] appended ${content.length} chars → ${target}`);
      return send(res, 200, { ok: true, appended: content.length }, origin);
    }

    // ── /files/read — allowlisted, read-only ──
    // Also serves a listing when given a folder, so the Shuttle can offer a
    // choice instead of requiring a remembered filename.
    if (url.pathname === "/files/read" && req.method === "POST") {
      const { path: target, limit } = await readJson(req);
      if (typeof target !== "string") {
        return send(res, 400, { error: "path is required." }, origin);
      }
      const p = path.resolve(target);
      let stat;
      try {
        stat = await fs.stat(p);
      } catch (e) {
        return send(res, 404, { error: `Not found: ${(e as Error).message}` }, origin);
      }

      if (stat.isDirectory()) {
        // A folder listing is allowed if the folder itself sits under a root.
        const insideRoot = READ_ROOTS.some((root) => {
          const rel = path.relative(root, p);
          return rel === "" || (!rel.startsWith("..") && !path.isAbsolute(rel));
        });
        if (!insideRoot) {
          console.error(`[bridge-http] REFUSED listing outside the read allowlist: ${target}`);
          return send(res, 403, { error: "Path is not on the read allowlist.", allowed: READ_ROOTS }, origin);
        }
        const names = (await fs.readdir(p)).filter((n) => /\.(md|txt|json)$/i.test(n));
        const withTimes = await Promise.all(
          names.map(async (n) => {
            const s = await fs.stat(path.join(p, n));
            return { name: n, modified: s.mtime.toISOString(), bytes: s.size };
          })
        );
        withTimes.sort((a, b) => b.modified.localeCompare(a.modified));
        return send(res, 200, { directory: p, files: withTimes }, origin);
      }

      if (!readAllowed(p)) {
        console.error(`[bridge-http] REFUSED read outside the read allowlist: ${target}`);
        return send(res, 403, {
          error: "Path is not on the read allowlist.",
          allowed: READ_ROOTS,
          note: "Markdown, text and json only; no .env, ever.",
        }, origin);
      }
      const cap = Math.min(Number(limit) || 20000, 100000);
      const text = await fs.readFile(p, "utf-8");
      const clipped = text.length > cap;
      console.error(`[bridge-http] read ${text.length} chars ← ${target}`);
      return send(res, 200, {
        path: p,
        bytes: text.length,
        clipped,
        content: clipped ? text.slice(0, cap) : text,
      }, origin);
    }

    // ── /switchboard/fetch — one message, verbatim ──
    if (url.pathname === "/switchboard/fetch" && req.method === "POST") {
      const { label } = await readJson(req);
      if (typeof label !== "string") return send(res, 400, { error: "label is required." }, origin);
      return send(res, 200, await switchboardFetch(label), origin);
    }

    return send(res, 404, { error: `No door at ${url.pathname}.` }, origin);
  } catch (e) {
    console.error(`[bridge-http] ${(e as Error).message}`);
    return send(res, 500, { error: (e as Error).message }, origin);
  }
});

httpServer.listen(PORT, HOST, () => {
  console.error(`[bridge-http] listening on http://${HOST}:${PORT}`);
  console.error(`[bridge-http] ${toolNames.length} tools on the line: ${toolNames.join(", ")}`);
  console.error(`[bridge-http] doors: /health · /mcp · /files/read (allowlisted) · /files/write (append, allowlisted) · /switchboard/fetch`);
  console.error(`[bridge-http] write allowlist: ${SHUTTLE_BUS} · ${AETHELRED_JOURNALS}\\*-plugin-notes.md`);
  console.error(`[bridge-http] read allowlist:  ${READ_ROOTS.join(" · ")}`);
});
