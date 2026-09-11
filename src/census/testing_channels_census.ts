// The channels census — the guild's testing channels photographed into the reports seed.
//
//   npx tsx src/census/testing_channels_census.ts          write the seed
//   npx tsx src/census/testing_channels_census.ts --dry    print it, write nothing
//
// Reads only. DISCORD_BOT_TOKEN_BRIDGE and DISCORD_GUILD_ID are read from
// process.env at call time; the token rides one header and enters no output.
// A channel's slug is the slug the register holds for that channel's name,
// read through the anon door; an unread register is said in one sentence and
// the slug is read as `resonance-` and the name.
// Every message opening with a bug or note glyph in a channel of the `testing`
// category becomes one row of resonance-nectere/seeds/testing-reports.json,
// merged by id: a held row is rewritten by its id or kept, and no row of
// another source is dropped. A seed that is present and will not read stops the
// run whole. Message text reaches the seed, never the console.

import { fileURLToPath } from "node:url";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";

import {
  REGISTER_KEY_NAMES,
  REPORTS_SOURCE,
  readKeys,
  registerDoor,
  type ReportKind,
  type ReportRow,
  type ReportsSeed,
} from "../lines/tracks.js";

// The bridge's own keyring by absolute path; an absent file leaves the ring empty.
try {
  process.loadEnvFile(fileURLToPath(new URL("../../.env", import.meta.url)));
} catch {}

const API = "https://discord.com/api/v10";
const HOUSE = fileURLToPath(new URL("../../../", import.meta.url));
const SEED = path.join(HOUSE, "resonance-nectere", "seeds", "testing-reports.json");

const CATEGORY = "testing";
const SUFFIX = "-testing";
const SLUG_PREFIX = "resonance-";
const MESSAGE_LIMIT = 50;
const CATEGORY_TYPE = 4;
const TEXT_TYPE = 0;
const REGISTER_TABLE = "beacons";
const REGISTER_COLUMNS = "slug,beacon_type,status";
const REGISTER_TYPES = ["app", "game"];
const FLOWING = "flowing";
const NO_TOKEN =
  "The Discord line is not connected: DISCORD_BOT_TOKEN_BRIDGE is not on the bridge's ring — " +
  "create the application and its bot at discord.com/developers/applications, then put the bot " +
  "token in resonance-bridge/.env by your own hands.";

const NO_GUILD =
  "DISCORD_GUILD_ID is not on the bridge's ring — Discord → Settings → Advanced → Developer Mode " +
  "on → right-click the server icon → Copy Server ID → into resonance-bridge/.env by your own hands.";

// What a channel's slug is read as while the register is unread.
const REGISTER_UNTIL = `a channel's slug is read as ${SLUG_PREFIX} and its name until then.`;

// A message's opening glyph and the kind it names.
const GLYPHS: ReadonlyArray<readonly [string, ReportKind]> = [
  ["🐛", "bug"],
  ["📝", "note"],
  ["💡", "note"],
];

export interface RegisterBeacon {
  slug: string;
  beacon_type: string;
  status: string;
}

export interface TestingChannel {
  id: string;
  name: string;
  slug: string;
}

export interface TestingGround {
  category: { id: string; name: string } | null;
  channels: TestingChannel[];
}

export interface Merge {
  rows: ReportRow[];
  added: number;
  rewritten: number;
}

export interface Held {
  rows: ReportRow[];
  readable: boolean;
}

// The token rides the Authorization header alone; no error carries it.
async function discordGet(route: string, params: Record<string, string> = {}): Promise<any> {
  const url = new URL(API + route);
  for (const [k, v] of Object.entries(params)) {
    if (v !== "") url.searchParams.set(k, v);
  }
  const res = await fetch(url, {
    headers: { Authorization: `Bot ${process.env.DISCORD_BOT_TOKEN_BRIDGE}` },
  });
  if (!res.ok) {
    const body = (await res.text()).slice(0, 300);
    throw new Error(`Discord ${res.status} on ${route}: ${body}`);
  }
  return res.json();
}

export function kindOf(content: string): ReportKind | null {
  const text = content.trimStart();
  for (const [glyph, kind] of GLYPHS) {
    if (text.startsWith(glyph)) return kind;
  }
  return null;
}

// Every beacon's slug through the anon door, both key names read at call time.
export async function readRegister(): Promise<RegisterBeacon[]> {
  const missing = readKeys(REGISTER_KEY_NAMES).missing[0];
  if (missing) throw new Error(registerDoor(missing, REGISTER_UNTIL));
  const url = process.env.SUPABASE_URL_KNOWLEDGE ?? "";
  const key = process.env.SUPABASE_PUBLISHABLE_KEY_KNOWLEDGE ?? "";
  const res = await fetch(
    `${url}/rest/v1/${REGISTER_TABLE}?select=${REGISTER_COLUMNS}&order=slug`,
    { headers: { apikey: key, Authorization: `Bearer ${key}` } }
  );
  if (!res.ok) {
    throw new Error(`The register answered ${res.status}: ${(await res.text()).slice(0, 200)}`);
  }
  return res.json();
}

// The tender's namer: a beacon's channel is its slug without the prefix.
export function channelNameOf(slug: string): string {
  const short = slug.startsWith(SLUG_PREFIX) ? slug.slice(SLUG_PREFIX.length) : slug;
  return (short + SUFFIX).toLowerCase();
}

// A flowing app or game names its channel before any other beacon does.
function asks(beacon: RegisterBeacon): number {
  return REGISTER_TYPES.includes(beacon.beacon_type) && beacon.status === FLOWING ? 0 : 1;
}

// Each channel name against the slug that names it, the namer read backwards.
export function slugByChannel(beacons: RegisterBeacon[]): Map<string, string> {
  const known = new Map<string, string>();
  const ranked = beacons
    .slice()
    .sort((a, b) => asks(a) - asks(b) || a.slug.localeCompare(b.slug));
  for (const beacon of ranked) {
    const name = channelNameOf(beacon.slug);
    if (!known.has(name)) known.set(name, beacon.slug);
  }
  return known;
}

export function slugOf(
  channelName: string,
  known: ReadonlyMap<string, string> = new Map()
): string {
  return known.get(channelName) ?? SLUG_PREFIX + channelName.slice(0, -SUFFIX.length);
}

// The testing category and every text channel under it whose name ends -testing.
export function testingGround(
  channels: any[],
  known: ReadonlyMap<string, string> = new Map()
): TestingGround {
  const found = channels.find(
    (c) => c?.type === CATEGORY_TYPE && String(c?.name ?? "").toLowerCase() === CATEGORY
  );
  if (!found) return { category: null, channels: [] };
  const under = channels
    .filter(
      (c) =>
        c?.type === TEXT_TYPE &&
        String(c?.parent_id ?? "") === String(found.id) &&
        String(c?.name ?? "").endsWith(SUFFIX) &&
        String(c?.name ?? "").length > SUFFIX.length
    )
    .map((c) => ({
      id: String(c.id),
      name: String(c.name),
      slug: slugOf(String(c.name), known),
    }))
    .sort((a, b) => a.name.localeCompare(b.name));
  return { category: { id: String(found.id), name: String(found.name) }, channels: under };
}

export function rowsFromMessages(
  guildId: string,
  channel: TestingChannel,
  messages: any[]
): ReportRow[] {
  const rows: ReportRow[] = [];
  for (const m of messages) {
    const content = typeof m?.content === "string" ? m.content : "";
    const kind = kindOf(content);
    if (kind === null) continue;
    rows.push({
      id: `discord:${m.id}`,
      slug: channel.slug,
      kind,
      said_by: m.author?.global_name ?? m.author?.username ?? String(m.author?.id ?? "unknown"),
      said_at: String(m.timestamp),
      where: `#${channel.name}`,
      text: content,
      link: `https://discord.com/channels/${guildId}/${channel.id}/${m.id}`,
    });
  }
  return rows.sort((a, b) => a.said_at.localeCompare(b.said_at));
}

// A held row keeps its place; a fresh row rewrites its own id or joins the end.
export function merge(held: ReportRow[], fresh: ReportRow[]): Merge {
  const rows = held.slice();
  const at = new Map(rows.map((row, i) => [row.id, i]));
  let added = 0;
  let rewritten = 0;
  for (const row of fresh) {
    const seat = at.get(row.id);
    if (seat === undefined) {
      at.set(row.id, rows.length);
      rows.push(row);
      added += 1;
      continue;
    }
    if (JSON.stringify(rows[seat]) !== JSON.stringify(row)) rewritten += 1;
    rows[seat] = row;
  }
  return { rows, added, rewritten };
}

// An absent file is an empty seed; a file that will not read is not one.
export async function heldRows(file: string): Promise<Held> {
  let raw: string;
  try {
    raw = await readFile(file, "utf8");
  } catch (e) {
    if ((e as NodeJS.ErrnoException).code === "ENOENT") return { rows: [], readable: true };
    return { rows: [], readable: false };
  }
  let seed: ReportsSeed;
  try {
    seed = JSON.parse(raw) as ReportsSeed;
  } catch {
    return { rows: [], readable: false };
  }
  return { rows: Array.isArray(seed.rows) ? seed.rows : [], readable: true };
}

async function main(): Promise<void> {
  const dry = process.argv.includes("--dry");
  if (!process.env.DISCORD_BOT_TOKEN_BRIDGE) {
    console.error(NO_TOKEN);
    process.exit(1);
  }
  const guildId = process.env.DISCORD_GUILD_ID ?? "";
  if (guildId === "") {
    console.error(NO_GUILD);
    process.exit(1);
  }

  const guild = await discordGet(`/guilds/${guildId}`);
  const channels = await discordGet(`/guilds/${guildId}/channels`);
  console.log(`guild: ${guild.name} (${guildId})`);
  console.log(`channels: ${channels.length} in the guild`);

  let known: ReadonlyMap<string, string> = new Map();
  try {
    const beacons = await readRegister();
    known = slugByChannel(beacons);
    console.log(`register: ${beacons.length} beacons · ${known.size} channel names`);
  } catch (e) {
    console.log((e as Error).message);
  }

  const ground = testingGround(channels, known);
  if (ground.category === null) {
    console.log(`no category named ${CATEGORY} in the guild`);
  }
  console.log(`${ground.channels.length} channels under ${CATEGORY}`);

  const fresh: ReportRow[] = [];
  for (const channel of ground.channels) {
    const messages = await discordGet(`/channels/${channel.id}/messages`, {
      limit: String(MESSAGE_LIMIT),
    });
    const rows = rowsFromMessages(guildId, channel, messages);
    fresh.push(...rows);
    const bugs = rows.filter((r) => r.kind === "bug").length;
    const unnamed = known.size > 0 && !known.has(channel.name) ? " · no beacon of this name" : "";
    console.log(
      `#${channel.name} -> ${channel.slug} · ${messages.length} read · ${rows.length} carried ` +
        `(${bugs} bug, ${rows.length - bugs} note)${unnamed}`
    );
    for (const row of rows) {
      console.log(`    ${row.id} ${row.kind} ${row.said_at}`);
    }
  }
  fresh.sort((a, b) => a.said_at.localeCompare(b.said_at));

  const held = await heldRows(SEED);
  if (!held.readable) {
    console.error(
      `${SEED} is present and unreadable — it is left whole and this run's rows are not written.`
    );
    process.exit(1);
  }
  const { rows, added, rewritten } = merge(held.rows, fresh);
  console.log(
    `\n${fresh.length} carried · ${added} new · ${rewritten} rewritten · ` +
      `${rows.length} rows in the seed`
  );

  if (dry) {
    console.log(`--dry: ${SEED} not written`);
    return;
  }
  const seed: ReportsSeed = {
    source: REPORTS_SOURCE,
    read_at: new Date().toISOString(),
    rows,
  };
  await mkdir(path.dirname(SEED), { recursive: true });
  await writeFile(SEED, JSON.stringify(seed, null, 1) + "\n", "utf8");
  console.log(`wrote ${SEED}`);
}

const entry = process.argv[1] ? path.resolve(process.argv[1]) : "";
if (entry === fileURLToPath(import.meta.url)) {
  main().catch((e: unknown) => {
    console.error((e as Error).message);
    process.exit(1);
  });
}
