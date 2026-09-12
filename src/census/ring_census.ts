// The ring census — the whole keyring and every line the server carries, in one reading.
//
//   npx tsx src/census/ring_census.ts          print the census
//   npx tsx src/census/ring_census.ts --json   print it as one JSON object
//
// Read-only by construction: it holds no writing verb, opens no file for writing
// and needs no --dry. Key NAMES are read from the ring and from .env.example;
// no key value enters a reading, an error or a line of output. Every line is
// probed in this process — the line modules are imported and their tools called
// over an in-memory transport, never a spawned server. A shut line answers with
// its own sentence and the census carries on; a failed call is one line.

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { InMemoryTransport } from "@modelcontextprotocol/sdk/inMemory.js";
import { fileURLToPath, pathToFileURL } from "node:url";
import { readFile } from "node:fs/promises";

import { readKeys } from "../lines/tracks.js";
import { registerGrammar } from "../lines/grammar.js";
import { registerVercel } from "../lines/vercel.js";
import { registerResend } from "../lines/resend.js";
import { registerStripe } from "../lines/stripe.js";
import { registerGitHub } from "../lines/github.js";
import { registerDiscord } from "../lines/discord.js";
import { registerSupabase } from "../lines/supabase.js";
import { registerCloudflare } from "../lines/cloudflare.js";
import { registerPlay } from "../lines/play.js";
import { registerGalaxy } from "../lines/galaxy.js";
import { registerMicrosoft } from "../lines/microsoft.js";

// The bridge's own keyring by absolute path; an absent file leaves the ring empty.
const RING = fileURLToPath(new URL("../../.env", import.meta.url));
const MANIFEST = fileURLToPath(new URL("../../.env.example", import.meta.url));

try {
  process.loadEnvFile(RING);
} catch {}

const MINTED = "a token was minted";
const WIDTH = 96;

// ── The ring ───────────────────────────────────────────────────────────────

export interface RingName {
  name: string;
  stands: boolean;
}

export interface Ring {
  manifest: RingName[];
  unlisted: string[];
  readable: boolean;
}

// Names only: a line's name is what stands left of its first `=`, and no value
// is carried out of this function.
export function keyNames(text: string): Map<string, boolean> {
  const names = new Map<string, boolean>();
  for (const raw of text.split(/\r?\n/)) {
    const line = raw.trim();
    if (line === "" || line.startsWith("#")) continue;
    const at = line.indexOf("=");
    if (at < 1) continue;
    const name = line.slice(0, at).trim().replace(/^export\s+/, "");
    if (!/^[A-Za-z_][A-Za-z0-9_]*$/.test(name)) continue;
    const value = line
      .slice(at + 1)
      .replace(/\s+#.*$/, "")
      .trim();
    names.set(name, value !== "");
  }
  return names;
}

export function ringAgainstManifest(
  manifest: Map<string, boolean>,
  ring: Map<string, boolean>
): { manifest: RingName[]; unlisted: string[] } {
  const rows: RingName[] = [];
  for (const name of manifest.keys()) rows.push({ name, stands: ring.get(name) === true });
  const unlisted: string[] = [];
  for (const name of ring.keys()) if (!manifest.has(name)) unlisted.push(name);
  return { manifest: rows, unlisted };
}

async function readRing(): Promise<Ring> {
  let manifest = new Map<string, boolean>();
  let ring = new Map<string, boolean>();
  let readable = true;
  try {
    manifest = keyNames(await readFile(MANIFEST, "utf8"));
  } catch {
    readable = false;
  }
  try {
    ring = keyNames(await readFile(RING, "utf8"));
  } catch {
    readable = false;
  }
  return { ...ringAgainstManifest(manifest, ring), readable };
}

// ── The lines ──────────────────────────────────────────────────────────────

export type Standing = "live" | "shut" | "degraded";

export interface Reading {
  state: "live" | "degraded";
  say: string;
}

interface Probe {
  line: string;
  keys: readonly string[];
  // The names the line's own code tests before it opens the door.
  gate?: readonly string[];
  tool: string;
  owns: RegExp;
  read: (data: any) => Reading;
}

export interface LineRow {
  line: string;
  standing: Standing;
  say: string;
  tool: string;
  tools: number;
  stand: string[];
  absent: string[];
}

// One sentence out of whatever a tool answered with, no newline and no value.
function oneLine(text: string): string {
  return text.replace(/\s+/g, " ").trim().slice(0, 300);
}

function nameList(names: string[], keep = 4): string {
  const shown = names.slice(0, keep).join(", ");
  return names.length > keep ? `${shown} +${names.length - keep} more` : shown;
}

function plural(n: number, word: string): string {
  return `${n} ${word}${n === 1 ? "" : "s"}`;
}

function live(say: string): Reading {
  return { state: "live", say };
}

function degraded(say: string): Reading {
  return { state: "degraded", say: oneLine(say) };
}

// A store line names its own minting trouble in the token field.
function minted(data: any, say: string): Reading {
  return data?.token === MINTED ? live(say) : degraded(String(data?.token ?? data));
}

const PROBES: readonly Probe[] = [
  {
    line: "grammar",
    keys: ["SUPABASE_URL_KNOWLEDGE", "SUPABASE_PUBLISHABLE_KEY_KNOWLEDGE"],
    tool: "query_beacon",
    owns: /^(query_|search_)/,
    read: (d) =>
      Array.isArray(d) ? live(`${plural(d.length, "beacon")} in the register`) : degraded(String(d)),
  },
  {
    line: "vercel",
    keys: ["VERCEL_TOKEN"],
    tool: "vercel_list_projects",
    owns: /^vercel_/,
    read: (d) =>
      Array.isArray(d)
        ? live(`${plural(d.length, "project")} · ${nameList(d.map((p: any) => String(p.name)))}`)
        : degraded(String(d)),
  },
  {
    line: "resend",
    keys: ["RESEND_KEY_BRIDGE_ADMIN"],
    tool: "resend_list_domains",
    owns: /^resend_/,
    read: (d) =>
      Array.isArray(d)
        ? live(`${plural(d.length, "domain")} · ${nameList(d.map((x: any) => `${x.name} ${x.status}`))}`)
        : degraded(String(d)),
  },
  {
    line: "stripe",
    keys: ["STRIPE_RESTRICTED_KEY"],
    tool: "stripe_account",
    owns: /^stripe_/,
    read: (d) =>
      typeof d === "object" && d !== null && d.business_name
        ? live(String(d.business_name))
        : degraded(typeof d === "string" ? d : JSON.stringify(d)),
  },
  {
    line: "github",
    keys: ["HOUSE_GITHUB_PAT"],
    tool: "github_token_status",
    owns: /^github_/,
    read: (d) => (d?.login ? live(String(d.login)) : degraded(JSON.stringify(d))),
  },
  {
    line: "discord",
    keys: ["DISCORD_BOT_TOKEN_BRIDGE", "DISCORD_GUILD_ID"],
    gate: ["DISCORD_BOT_TOKEN_BRIDGE"],
    tool: "discord_whoami",
    owns: /^discord_/,
    read: (d) => (d?.bot?.username ? live(String(d.bot.username)) : degraded(JSON.stringify(d))),
  },
  {
    line: "supabase",
    keys: ["SUPABASE_ACCESS_TOKEN"],
    tool: "supabase_list_projects",
    owns: /^supabase_/,
    read: (d) =>
      Array.isArray(d)
        ? live(`${plural(d.length, "project")} · ${nameList(d.map((p: any) => String(p.name)))}`)
        : degraded(String(d)),
  },
  {
    line: "cloudflare",
    keys: ["CLOUDFLARE_API_TOKEN", "CLOUDFLARE_ACCOUNT_ID"],
    gate: ["CLOUDFLARE_API_TOKEN"],
    tool: "cloudflare_verify_token",
    owns: /^cloudflare_/,
    read: (d) =>
      d?.status && !d?.error ? live(`token ${d.status}`) : degraded(String(d?.error ?? d)),
  },
  {
    line: "play",
    keys: ["GOOGLE_PLAY_SERVICE_ACCOUNT_JSON"],
    tool: "play_whoami",
    owns: /^play_/,
    read: (d) => minted(d, String(d?.service_account ?? MINTED)),
  },
  {
    line: "galaxy",
    keys: ["SAMSUNG_GSD_SERVICE_ACCOUNT_ID", "SAMSUNG_GSD_PRIVATE_KEY_PATH"],
    tool: "galaxy_whoami",
    owns: /^galaxy_/,
    read: (d) => minted(d, MINTED),
  },
  {
    line: "microsoft",
    keys: ["MS_STORE_TENANT_ID", "MS_STORE_CLIENT_ID", "MS_STORE_CLIENT_SECRET"],
    tool: "ms_whoami",
    owns: /^ms_/,
    read: (d) => minted(d, MINTED),
  },
];

// ── The in-process door ────────────────────────────────────────────────────

async function openBridge(): Promise<Client> {
  const server = new McpServer({ name: "resonance-bridge", version: "0.2.0" });
  registerGrammar(server);
  registerVercel(server);
  registerResend(server);
  registerStripe(server);
  registerGitHub(server);
  registerDiscord(server);
  registerSupabase(server);
  registerCloudflare(server);
  registerPlay(server);
  registerGalaxy(server);
  registerMicrosoft(server);
  const [clientSide, serverSide] = InMemoryTransport.createLinkedPair();
  const client = new Client({ name: "ring-census", version: "0.2.0" });
  await Promise.all([server.connect(serverSide), client.connect(clientSide)]);
  return client;
}

// The text a tool answered with, and whether the tool called it an error.
async function callTool(
  client: Client,
  name: string
): Promise<{ text: string; failed: boolean }> {
  try {
    const result: any = await client.callTool({ name, arguments: {} });
    const text = (result?.content ?? [])
      .filter((c: any) => c?.type === "text")
      .map((c: any) => String(c.text))
      .join("\n");
    return { text, failed: result?.isError === true };
  } catch (e) {
    return { text: (e as Error).message, failed: true };
  }
}

async function readLine(client: Client, probe: Probe, tools: number): Promise<LineRow> {
  const seen = readKeys(probe.keys);
  const shut = readKeys(probe.gate ?? probe.keys).missing.length > 0;
  const base = {
    line: probe.line,
    tool: probe.tool,
    tools,
    stand: seen.present,
    absent: seen.missing,
  };
  // A shut line's own sentence comes back from the tool itself, before any call out.
  const { text, failed } = await callTool(client, probe.tool);
  if (shut) return { ...base, standing: "shut", say: oneLine(text) };
  if (failed) return { ...base, standing: "degraded", say: oneLine(text) };
  let data: unknown;
  try {
    data = JSON.parse(text);
  } catch {
    return { ...base, standing: "degraded", say: oneLine(text) };
  }
  // A reader that throws leaves the line degraded on that error's sentence; the run carries on.
  let reading: Reading;
  try {
    reading = probe.read(data);
  } catch (e) {
    reading = degraded(String((e as Error)?.message ?? e));
  }
  return { ...base, standing: reading.state, say: reading.say };
}

// ── The saying ─────────────────────────────────────────────────────────────

function say(line = ""): void {
  console.log(line);
}

// A long sentence broken at the spaces, every later part under the same indent.
function wrap(text: string, indent: string): string[] {
  const out: string[] = [];
  let row = "";
  for (const word of text.split(" ")) {
    if (row !== "" && (indent + row + " " + word).length > WIDTH) {
      out.push(indent + row);
      row = word;
      continue;
    }
    row = row === "" ? word : `${row} ${word}`;
  }
  if (row !== "") out.push(indent + row);
  return out;
}

function sayRing(ring: Ring): void {
  say("THE RING");
  say();
  if (!ring.readable) {
    say("  the ring or its manifest could not be read; what follows is only what read.");
    say();
  }
  for (const row of ring.manifest) {
    say(`  ${row.stands ? "present" : "missing"}  ${row.name}`);
  }
  const present = ring.manifest.filter((r) => r.stands).length;
  if (ring.unlisted.length > 0) {
    say();
    say("  on the ring, unlisted by the manifest");
    for (const name of ring.unlisted) say(`  unlisted  ${name}`);
  }
  say();
  say(
    `  ${ring.manifest.length} names in the manifest · ${present} present · ` +
      `${ring.manifest.length - present} missing · ${ring.unlisted.length} unlisted on the ring`
  );
  say();
}

function sayLines(rows: LineRow[], unplaced: string[]): void {
  say("THE LINES");
  say();
  for (const row of rows) {
    say(`  ${row.line} — ${row.standing}${row.standing === "shut" ? "" : ` — ${row.say}`}`);
    if (row.stand.length > 0) say(`      stand   ${row.stand.join(", ")}`);
    if (row.absent.length > 0) say(`      absent  ${row.absent.join(", ")}`);
    say(`      tools   ${row.tools} · read by ${row.tool}`);
    if (row.standing === "shut") {
      for (const part of wrap(row.say, "              ")) say(part);
    }
    say();
  }
  if (unplaced.length > 0) {
    say(`  tools this census places under no line: ${unplaced.join(", ")}`);
    say();
  }
}

function sayFoot(rows: LineRow[]): void {
  const count = (s: Standing) => rows.filter((r) => r.standing === s).length;
  say("THE FOOT");
  say();
  say(`  ${count("live")} lines live · ${count("shut")} shut · ${count("degraded")} degraded`);
  const shut = rows.filter((r) => r.standing === "shut");
  if (shut.length > 0) {
    say();
    say("  the click for each shut line");
    for (const row of shut) {
      say(`  ${row.line}`);
      for (const part of wrap(row.say, "      ")) say(part);
    }
  }
  const hurt = rows.filter((r) => r.standing === "degraded");
  if (hurt.length > 0) {
    say();
    say("  what each degraded line answered");
    for (const row of hurt) {
      say(`  ${row.line}`);
      for (const part of wrap(row.say, "      ")) say(part);
    }
  }
  say();
}

// ── The census ─────────────────────────────────────────────────────────────

async function main(): Promise<void> {
  const json = process.argv.includes("--json");
  const ring = await readRing();
  const client = await openBridge();
  const listed = (await client.listTools()).tools.map((t) => t.name);

  const rows: LineRow[] = [];
  for (const probe of PROBES) {
    rows.push(await readLine(client, probe, listed.filter((n) => probe.owns.test(n)).length));
  }
  const unplaced = listed.filter((n) => !PROBES.some((p) => p.owns.test(n)));

  await client.close();

  if (json) {
    const count = (s: Standing) => rows.filter((r) => r.standing === s).length;
    console.log(
      JSON.stringify(
        {
          read_at: new Date().toISOString(),
          ring: {
            manifest: ring.manifest,
            unlisted: ring.unlisted,
            present: ring.manifest.filter((r) => r.stands).length,
            missing: ring.manifest.filter((r) => !r.stands).length,
          },
          lines: rows,
          unplaced_tools: unplaced,
          live: count("live"),
          shut: count("shut"),
          degraded: count("degraded"),
        },
        null,
        1
      )
    );
    return;
  }

  say(`THE RING CENSUS — ${new Date().toISOString()}`);
  say(`  ring ${RING}`);
  say(`  manifest ${MANIFEST}`);
  say();
  sayRing(ring);
  sayLines(rows, unplaced);
  sayFoot(rows);
}

// The census runs when it is run; imported, it offers its parts and reads nothing.
if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  main().catch((e) => {
    console.error((e as Error).message);
    process.exitCode = 1;
  });
}
