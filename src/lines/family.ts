import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import fs from "node:fs/promises";
import path from "node:path";

// The Family line — read-only, sovereign. Four windows over the seven family
// apps (echoes · compass · hearth · lantern · bubbles · sistrum · khoros):
// their repos on this disk, their checklists, their rows in the living
// beacons register, and the release tally the rack-tender keeps.
//
// SAID PLAINLY, HERE AND ON EVERY TOOL: the apps' DEVICE DATA — what a
// phone's own SQLite holds, the echoes and moments and takes on KP's
// devices — is UNREACHABLE from this line. That is the apps' sovereignty
// working as designed, not a gap. This line reads repos, documents, and
// the register; never a person's data.
//
// family_beacons walks the anon door of the KNOWLEDGE base (publishable
// key gated by RLS, the same door a stranger would use — the secret key
// never enters this file). The register's table is `beacons`; a shim view
// still answers to the old name `resonance_beacons`, so the name is resolved
// at read time, never assumed.
//
// family_releases reads THE-GROUND-TALLY.md and echoes that file's own
// stamp — the rack-tender's logic is never duplicated here. Its file says
// it best: regenerating it is how it stays true.

const ROOT = process.env.SANCTUARY_ROOT ?? "C:/_superposition";

const FAMILY = [
  "echoes",
  "compass",
  "hearth",
  "lantern",
  "bubbles",
  "sistrum",
  "khoros",
] as const;

const APP = z
  .enum(FAMILY)
  .describe("one of the seven family apps, e.g. 'echoes' (repo resonance-echoes)");

// The checklists' own legend, counted as written — the five glyphs every
// family CHECKLIST.md declares at its top.
const GLYPHS: Record<string, string> = {
  "✅": "complete",
  "⚠️": "in_progress",
  "🔴": "broken",
  "⬜": "pending",
  "🔵": "ready_for_test",
};

const GROUND_TALLY = path.join(
  ROOT,
  "resonance-chamber/desk/realm-boards/THE-GROUND-TALLY.md"
);

// The register's possible names, in today's order of truth. Resolved at
// read time; a missing table is a finding, not a crash.
const REGISTER_NAMES = ["beacons", "resonance_beacons"];

const NO_BEACON_LINE =
  "The beacons window is not connected. Add SUPABASE_URL_KNOWLEDGE and " +
  "SUPABASE_PUBLISHABLE_KEY_KNOWLEDGE to .env by your own hands (read door " +
  "only — never the secret key), then restart the Bridge.";

function asText(data: unknown) {
  return { content: [{ type: "text" as const, text: JSON.stringify(data, null, 2) }] };
}

function repoOf(app: (typeof FAMILY)[number]): string {
  return path.join(ROOT, `resonance-${app}`);
}

async function readJsonFile(p: string): Promise<any | null> {
  try {
    return JSON.parse(await fs.readFile(p, "utf-8"));
  } catch {
    return null;
  }
}

async function readTextFile(p: string): Promise<string | null> {
  try {
    return await fs.readFile(p, "utf-8");
  } catch {
    return null;
  }
}

function tallyGlyphs(text: string): Record<string, number> {
  const tally: Record<string, number> = {};
  for (const [glyph, meaning] of Object.entries(GLYPHS)) {
    tally[`${glyph} ${meaning}`] = text.split(glyph).length - 1;
  }
  return tally;
}

async function statusOf(app: (typeof FAMILY)[number]) {
  const repo = repoOf(app);
  const tauri = await readJsonFile(path.join(repo, "src-tauri/tauri.conf.json"));
  const pkg = await readJsonFile(path.join(repo, "package.json"));
  const checklist = await readTextFile(path.join(repo, "docs/CHECKLIST.md"));
  return {
    app,
    repo: `resonance-${app}`,
    product_name: tauri?.productName ?? null,
    identifier: tauri?.identifier ?? null,
    tauri_version: tauri?.version ?? "no src-tauri/tauri.conf.json readable — stated plainly, not alarmed at",
    package_version: pkg?.version ?? "no package.json readable — stated plainly, not alarmed at",
    checklist: checklist
      ? { glyph_tally: tallyGlyphs(checklist), bytes: checklist.length }
      : "no docs/CHECKLIST.md readable — stated plainly, not alarmed at",
  };
}

async function beaconGet(table: string, params: Record<string, string>) {
  const url = new URL(
    `${process.env.SUPABASE_URL_KNOWLEDGE}/rest/v1/${table}`
  );
  for (const [k, v] of Object.entries(params)) url.searchParams.set(k, v);
  const key = process.env.SUPABASE_PUBLISHABLE_KEY_KNOWLEDGE as string;
  const res = await fetch(url, {
    headers: { apikey: key, Authorization: `Bearer ${key}` },
  });
  const body = await res.text();
  if (!res.ok) {
    // PGRST205 = table absent under this name — the rename question,
    // answered by the base itself, never presumed.
    if (body.includes("PGRST205")) return { absent: true as const };
    throw new Error(`beacons register ${res.status}: ${body.slice(0, 300)}`);
  }
  return { absent: false as const, rows: JSON.parse(body) as any[] };
}

export function registerFamily(server: McpServer) {
  server.tool(
    "family_status",
    "Every family app's versions and checklist state, read from the repos on THIS disk — tauri.conf.json and package.json versions plus the CHECKLIST.md glyph tally (✅ ⚠️ 🔴 ⬜ 🔵). Honest limit: the apps' device data (what a phone holds) is unreachable from here — sovereignty by design, not a gap.",
    {},
    async () => {
      const apps = await Promise.all(FAMILY.map(statusOf));
      return asText({
        family: apps,
        read_from: ROOT,
        device_data: "unreachable from this line — the apps are sovereign; nothing here reads a person's data",
      });
    }
  );

  server.tool(
    "family_checklist",
    "One family app's docs/CHECKLIST.md, whole and verbatim — the app's own single source of build truth. Honest limit: this reads the repo's document on this disk, never the app's device data (that is unreachable from here, by the apps' own sovereign design).",
    { app: APP },
    async ({ app }) => {
      const p = path.join(repoOf(app), "docs/CHECKLIST.md");
      const text = await readTextFile(p);
      if (text === null) {
        return asText(`No checklist readable at ${p} — stated plainly; the repo outranks this window.`);
      }
      return asText({ app, path: p, bytes: text.length, content: text });
    }
  );

  server.tool(
    "family_beacons",
    "The family's rows in the living beacons register — name, slug, type, status, version, store columns — read through the KNOWLEDGE base's anon door (RLS public-read, the stranger's door; no secret key). The table name is resolved at read time (beacons today — the rename ran at KP's hand 2026-08-15, seed 096; a shim view still answers to resonance_beacons until seed 097 drops it). Honest limit: this reads the register's word about the apps, never the apps' device data — that is unreachable from here.",
    {
      app: APP.optional().describe(
        "optionally narrow to one family app's row; omitted, the whole register answers"
      ),
    },
    async ({ app }) => {
      if (
        !process.env.SUPABASE_URL_KNOWLEDGE ||
        !process.env.SUPABASE_PUBLISHABLE_KEY_KNOWLEDGE
      ) {
        return asText(NO_BEACON_LINE);
      }
      const params: Record<string, string> = {
        select:
          "name,slug,beacon_type,status,version,is_public,icon_emoji,home,repo_url," +
          "play_status,play_testing_version,play_published_version,updated_at",
        order: "name.asc",
        limit: "100",
      };
      if (app) params.slug = `eq.resonance-${app}`;
      for (const table of REGISTER_NAMES) {
        const answer = await beaconGet(table, params);
        if (answer.absent) continue;
        return asText({
          register: table,
          note:
            table === "beacons"
              ? "the true name answered — the rename ran 2026-08-15 (seed 096)"
              : "the TRUE name `beacons` did not answer; this came through the `resonance_beacons` shim view, which seed 097 will drop — read the base before believing the shim outlives it",
          row_count: answer.rows.length,
          rows: answer.rows,
          false_empty_reminder:
            answer.rows.length === 0
              ? "[] + 200 from a register known to hold rows is the false-empty (BASE-ACCESS-GUIDE lesson 1) — check RLS before believing emptiness"
              : undefined,
        });
      }
      return asText(
        `Neither ${REGISTER_NAMES.join(" nor ")} answers on the KNOWLEDGE base — a missing table is a finding, not a crash. The base outranks this window; probe it before believing this.`
      );
    }
  );

  server.tool(
    "family_releases",
    "The family's release shelves as the rack-tender last measured them — read whole from THE-GROUND-TALLY.md, echoing that file's own stamp. This tool NEVER re-walks the shelves or duplicates the tender's logic; to refresh the ground truth, run the rack-tender's --tally by hand. Honest limit: release artifacts on this disk, never the apps' device data (unreachable from here).",
    {
      app: APP.optional().describe(
        "optionally narrow to one family app's shelf; omitted, all seven answer"
      ),
    },
    async ({ app }) => {
      const text = await readTextFile(GROUND_TALLY);
      if (text === null) {
        return asText(
          `THE-GROUND-TALLY.md is not readable at ${GROUND_TALLY} — the rack-tender has not run here, or the desk moved. Nothing is invented in its absence.`
        );
      }
      const stamp =
        text.match(/Read from the disk itself ([0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2})/)?.[1] ??
        "stamp not found — read the file itself";
      const shelves = text.split(/^## /m).find((s) => s.startsWith("2. Release shelves")) ?? "";
      const wanted = app ? [app] : [...FAMILY];
      const sections: Record<string, string> = {};
      for (const a of wanted) {
        const m = shelves.split(/^### /m).find((s) => s.startsWith(`\`resonance-${a}\``));
        sections[`resonance-${a}`] = m
          ? m.trim()
          : "no section in the tally — the tender's file outranks this window; regenerate it and read again";
      }
      return asText({
        source: GROUND_TALLY,
        tally_stamp: stamp,
        refreshed_by: "python resonance-ziggy/modules/rack-tender/rack_tender.py --tally (by hand — never from here)",
        shelves: sections,
      });
    }
  );
}
