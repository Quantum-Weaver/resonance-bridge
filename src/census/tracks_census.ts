// The tracks census — photographs Google Play, the Galaxy Store and the
// Microsoft Store into the two seeds nectere delivers.
//
//   npx tsx src/census/tracks_census.ts          write both seeds
//   npx tsx src/census/tracks_census.ts --dry    print both seeds, write nothing
//
// Reads only, GETs only — no edit is opened on Play. Every key is read from the
// bridge's ring by name at call time and no value is printed. A shut door is
// named and the census carries on.

import { fileURLToPath, pathToFileURL } from "node:url";
import path from "node:path";
import { readFile, writeFile, mkdir } from "node:fs/promises";

import {
  REGISTER_KEY_NAMES,
  REPORTS_SOURCE,
  STORE_CHANNELS,
  STORE_KEY_NAMES,
  TRACKS_SOURCE,
  readKeys,
  registerDoor,
  shutDoor,
  type DoorState,
  type ReportRow,
  type ReportsSeed,
  type StoreChannel,
  type TrackRow,
  type TracksSeed,
} from "../lines/tracks.js";
import {
  playReadReviews,
  playReadTracksByRelease,
  playReportRows,
  playToken,
  playTrackRow,
  playUnheld,
  type PlayTracksReading,
} from "../lines/play.js";
import {
  galaxyReadApp,
  galaxyReadApps,
  galaxyReadBeta,
  galaxyReadComments,
  galaxyReportRows,
  galaxyToken,
  galaxyTrackRow,
} from "../lines/galaxy.js";
import {
  microsoftReportRows,
  microsoftTrackRow,
  msReadApps,
  msReadFlights,
  msReadReviews,
  msReadSubmission,
  msReadSubmissionStatus,
  msToken,
  reviewWindow,
  type MsFlight,
} from "../lines/microsoft.js";

try {
  process.loadEnvFile(fileURLToPath(new URL("../../.env", import.meta.url)));
} catch {}

const HOUSE = fileURLToPath(new URL("../../../", import.meta.url));
const SEEDS = path.join(HOUSE, "resonance-nectere", "seeds");
const TRACKS_SEED = path.join(SEEDS, "store-tracks.json");
const REPORTS_SEED = path.join(SEEDS, "testing-reports.json");

const dry = process.argv.includes("--dry");

const UNREADABLE_REPORTS = `${REPORTS_SEED} is present and unreadable as JSON — it is left whole and this run's store review rows do not reach it.`;

function say(line: string) {
  console.log(line);
}

// ── The register, through the anon door ────────────────────────────────────

interface Beacon {
  slug: string;
  name: string;
  home: string | null;
  beacon_type: string;
  status: string;
  play_app_id: string | null;
  galaxy_app_id: string | null;
  microsoft_app_id: string | null;
  play_testing_url: string | null;
}

const COLUMNS =
  "slug,name,home,beacon_type,status,play_app_id,galaxy_app_id,microsoft_app_id,play_testing_url";

// What the census can read while the register is unread.
const REGISTER_UNTIL =
  "no store is read without the register's app ids, and this census stops here.";

async function readRegister(): Promise<Beacon[]> {
  const missing = readKeys(REGISTER_KEY_NAMES).missing[0];
  if (missing) throw new Error(registerDoor(missing, REGISTER_UNTIL));
  const url = process.env.SUPABASE_URL_KNOWLEDGE ?? "";
  const key = process.env.SUPABASE_PUBLISHABLE_KEY_KNOWLEDGE ?? "";
  const res = await fetch(`${url}/rest/v1/beacons?select=${COLUMNS}&order=slug`, {
    headers: { apikey: key, Authorization: `Bearer ${key}` },
  });
  if (!res.ok) {
    throw new Error(`The register answered ${res.status}: ${(await res.text()).slice(0, 200)}`);
  }
  return res.json();
}

// A packaged beacon names its own package in its Tauri config.
async function tauriIdentifier(home: string | null): Promise<string | null> {
  if (!home) return null;
  const file = path.join(HOUSE, home, "src-tauri", "tauri.conf.json");
  try {
    const conf = JSON.parse(await readFile(file, "utf8"));
    const id = conf?.identifier;
    return typeof id === "string" && id.trim() !== "" ? id.trim() : null;
  } catch {
    return null;
  }
}

// The Android build writes the Tauri identifier's hyphens as underscores.
export function androidPackage(identifier: string): string {
  return identifier.replace(/-/g, "_");
}

async function fillPlayIds(beacons: Beacon[]): Promise<void> {
  for (const b of beacons) {
    if (b.play_app_id) continue;
    const id = await tauriIdentifier(b.home);
    if (id) {
      const pkg = androidPackage(id);
      b.play_app_id = pkg;
      say(`${b.slug}: play_app_id from ${b.home}/src-tauri/tauri.conf.json — ${pkg}`);
    }
  }
}

// ── The doors ──────────────────────────────────────────────────────────────

type Minter = () => Promise<string>;

const MINTERS: Record<StoreChannel, Minter> = {
  play: playToken,
  galaxy: galaxyToken,
  microsoft: msToken,
};

async function openDoor(store: StoreChannel): Promise<{ door: DoorState; token: string | null }> {
  const missing = readKeys(STORE_KEY_NAMES[store]).missing[0];
  if (missing) return { door: `unread: ${shutDoor(store, missing)}`, token: null };
  try {
    return { door: "read", token: await MINTERS[store]() };
  } catch (e) {
    return { door: `unread: ${(e as Error).message}`, token: null };
  }
}

// ── The store readings ─────────────────────────────────────────────────────

interface Reading {
  rows: TrackRow[];
  reports: ReportRow[];
}

async function readPlay(token: string, beacons: Beacon[]): Promise<Reading> {
  const rows: TrackRow[] = [];
  const reports: ReportRow[] = [];
  for (const b of beacons) {
    const pkg = b.play_app_id;
    if (!pkg) continue;
    let reading: PlayTracksReading;
    try {
      // Each named track's releases, one GET apiece.
      reading = await playReadTracksByRelease(token, pkg);
    } catch (e) {
      say(`play · ${b.slug} · ${pkg} · unread: ${(e as Error).message}`);
      continue;
    }
    // A package no named track answered for is said, never written as an empty row.
    if (reading.answered.length === 0) {
      say(`play · ${b.slug} · ${playUnheld(pkg, reading.unanswered)}`);
      continue;
    }
    rows.push(playTrackRow(b.slug, pkg, reading.tracks, b.play_testing_url));
    say(`play · ${b.slug} · ${pkg}`);
    try {
      reports.push(...playReportRows(b.slug, await playReadReviews(token, pkg)));
    } catch (e) {
      say(`play · ${b.slug} · reviews unread: ${(e as Error).message}`);
    }
  }
  return { rows, reports };
}

async function readGalaxy(token: string, beacons: Beacon[]): Promise<Reading> {
  const rows: TrackRow[] = [];
  const reports: ReportRow[] = [];
  const bySlug = new Map<string, Beacon>();
  for (const b of beacons) if (b.galaxy_app_id) bySlug.set(b.galaxy_app_id, b);
  if (bySlug.size === 0) return { rows, reports };
  const apps = await galaxyReadApps(token);
  for (const app of apps) {
    const b = bySlug.get(app.content_id);
    if (!b) continue;
    try {
      const detail = (await galaxyReadApp(token, app.content_id)) ?? app;
      const beta = await galaxyReadBeta(token, app.content_id).catch(() => null);
      rows.push(galaxyTrackRow(b.slug, detail, beta));
      say(`galaxy · ${b.slug} · ${app.content_id}`);
    } catch (e) {
      say(`galaxy · ${b.slug} · ${app.content_id} · unread: ${(e as Error).message}`);
      continue;
    }
    try {
      reports.push(...galaxyReportRows(b.slug, await galaxyReadComments(token, app.content_id)));
    } catch (e) {
      say(`galaxy · ${b.slug} · comments unread: ${(e as Error).message}`);
    }
  }
  return { rows, reports };
}

async function readMicrosoft(token: string, beacons: Beacon[]): Promise<Reading> {
  const rows: TrackRow[] = [];
  const reports: ReportRow[] = [];
  const bySlug = new Map<string, Beacon>();
  for (const b of beacons) if (b.microsoft_app_id) bySlug.set(b.microsoft_app_id, b);
  if (bySlug.size === 0) return { rows, reports };
  const apps = await msReadApps(token);
  const window = reviewWindow();
  for (const app of apps) {
    const b = bySlug.get(app.id);
    if (!b) continue;
    try {
      const flights: MsFlight[] = await msReadFlights(token, app.id).catch(() => []);
      const submission = app.pending_submission_id ?? app.published_submission_id;
      const status = submission
        ? await msReadSubmissionStatus(token, app.id, submission).catch(() => null)
        : null;
      const published = app.published_submission_id
        ? await msReadSubmission(token, app.id, app.published_submission_id).catch(() => null)
        : null;
      // The versions live on the submissions, not on the app or its status.
      const flight = flights.find(
        (f) => f.published_submission_id !== null || f.pending_submission_id !== null
      );
      const flightSubmissionId = flight
        ? (flight.published_submission_id ?? flight.pending_submission_id)
        : null;
      const testing =
        flight && flightSubmissionId
          ? await msReadSubmission(token, app.id, flightSubmissionId, flight.flight_id).catch(
              () => null
            )
          : null;
      rows.push(microsoftTrackRow(b.slug, app, flights, status, published, testing));
      say(`microsoft · ${b.slug} · ${app.id}`);
    } catch (e) {
      say(`microsoft · ${b.slug} · ${app.id} · unread: ${(e as Error).message}`);
      continue;
    }
    try {
      const reviews = await msReadReviews(token, app.id, window.start_date, window.end_date);
      reports.push(...microsoftReportRows(b.slug, reviews));
    } catch (e) {
      say(`microsoft · ${b.slug} · reviews unread: ${(e as Error).message}`);
    }
  }
  return { rows, reports };
}

const READERS: Record<StoreChannel, (token: string, beacons: Beacon[]) => Promise<Reading>> = {
  play: readPlay,
  galaxy: readGalaxy,
  microsoft: readMicrosoft,
};

// ── The reports seed, merged ───────────────────────────────────────────────

// Rows already in the file keep their place and their words; a re-read row
// replaces itself by id; a row from a source this run did not read is kept.
export function mergeReports(existing: ReportRow[], fresh: ReportRow[]): ReportRow[] {
  const incoming = new Map(fresh.map((r) => [r.id, r]));
  const out: ReportRow[] = [];
  for (const row of existing) {
    const replacement = incoming.get(row.id);
    out.push(replacement ?? row);
    incoming.delete(row.id);
  }
  for (const row of fresh) {
    const still = incoming.get(row.id);
    if (still) {
      out.push(still);
      incoming.delete(row.id);
    }
  }
  return out;
}

async function existingReports(): Promise<{ rows: ReportRow[]; readable: boolean }> {
  try {
    const seed = JSON.parse(await readFile(REPORTS_SEED, "utf8"));
    return { rows: Array.isArray(seed?.rows) ? seed.rows : [], readable: true };
  } catch (e) {
    if ((e as NodeJS.ErrnoException).code === "ENOENT") return { rows: [], readable: true };
    return { rows: [], readable: false };
  }
}

function render(seed: unknown): string {
  return JSON.stringify(seed, null, 1) + "\n";
}

// ── The census ─────────────────────────────────────────────────────────────

async function main(): Promise<void> {
  const beacons = await readRegister();
  await fillPlayIds(beacons);

  const doors = {} as Record<StoreChannel, DoorState>;
  const rows: TrackRow[] = [];
  const fresh: ReportRow[] = [];

  for (const store of STORE_CHANNELS) {
    const { door, token } = await openDoor(store);
    doors[store] = door;
    say(`${store}: ${door}`);
    if (door !== "read" || token === null) continue;
    try {
      const reading = await READERS[store](token, beacons);
      rows.push(...reading.rows);
      fresh.push(...reading.reports);
    } catch (e) {
      doors[store] = `unread: ${(e as Error).message}`;
      say(`${store}: ${doors[store]}`);
    }
  }

  const readAt = new Date().toISOString();
  const tracks: TracksSeed = { source: TRACKS_SOURCE, read_at: readAt, doors, rows };

  const held = await existingReports();
  const reports: ReportsSeed = {
    source: REPORTS_SOURCE,
    read_at: readAt,
    rows: mergeReports(held.rows, fresh),
  };

  if (dry) {
    say(`\n--dry: ${TRACKS_SEED} not written\n${render(tracks)}`);
    if (!held.readable) {
      say(UNREADABLE_REPORTS);
      return;
    }
    say(`--dry: ${REPORTS_SEED} not written\n${render(reports)}`);
    return;
  }

  await mkdir(SEEDS, { recursive: true });
  await writeFile(TRACKS_SEED, render(tracks), "utf8");
  say(`\nwrote ${TRACKS_SEED} — ${rows.length} rows`);

  if (!held.readable) {
    say(UNREADABLE_REPORTS);
    return;
  }
  await writeFile(REPORTS_SEED, render(reports), "utf8");
  say(`wrote ${REPORTS_SEED} — ${reports.rows.length} rows`);
}

// The census runs when it is run; imported, it offers its parts and reads nothing.
if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  main().catch((e) => {
    console.error((e as Error).message);
    process.exitCode = 1;
  });
}
