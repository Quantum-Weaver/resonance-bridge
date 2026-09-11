import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { readFile } from "node:fs/promises";
import {
  googleServiceAccountToken,
  listingUrl,
  playStatus,
  readKeys,
  shutDoor,
  STORE_KEY_NAMES,
  type BeaconStatus,
  type ReportRow,
  type TrackRow,
} from "./tracks.js";

// The Google Play line — reads only. Every transport is a GET: each named
// track's releases, and the reviews.

const API = "https://androidpublisher.googleapis.com/androidpublisher/v3";

// What the GET-only track road cannot reach.
const CUSTOM_TRACKS =
  "These are Play's own named tracks, read with GETs. A custom closed track is named " +
  "only inside an edit, which this line does not open.";

// What Play serves only inside an edit, and the bridge therefore never counts.
const TESTERS_UNREAD = "tester lists are inside an edit; not read by the bridge";

function firstMissingKey(): string | null {
  return readKeys(STORE_KEY_NAMES.play).missing[0] ?? null;
}

function shut(keyName: string) {
  return { content: [{ type: "text" as const, text: shutDoor("play", keyName) }] };
}

function asText(data: unknown) {
  return { content: [{ type: "text" as const, text: JSON.stringify(data, null, 2) }] };
}

function keyPath(): string {
  return process.env.GOOGLE_PLAY_SERVICE_ACCOUNT_JSON ?? "";
}

export async function playToken(): Promise<string> {
  return googleServiceAccountToken(keyPath());
}

// The account's own name and project; the private key never leaves the file.
export async function serviceAccount(
  jsonPath: string
): Promise<{ client_email: string | null; project_id: string | null }> {
  let account: { client_email?: string; project_id?: string };
  try {
    account = JSON.parse(await readFile(jsonPath, "utf8"));
  } catch {
    throw new Error(
      "The Google Play service account file named on the ring could not be read as JSON."
    );
  }
  return { client_email: account.client_email ?? null, project_id: account.project_id ?? null };
}

// True when the body holds nothing but whitespace.
function emptyBody(text: string): boolean {
  return text.trim() === "";
}

async function playGet(
  bearer: string,
  path: string,
  params: Record<string, string | undefined> = {}
): Promise<any> {
  const url = new URL(API + path);
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== "") url.searchParams.set(k, v);
  }
  const res = await fetch(url, { headers: { Authorization: `Bearer ${bearer}` } });
  const text = await res.text();
  if (!res.ok) throw new Error(`Google Play ${res.status}: ${text.slice(0, 300)}`);
  return emptyBody(text) ? {} : JSON.parse(text);
}

// A track Play does not hold answers 404; every other refusal is raised.
async function playGetOrNull(
  bearer: string,
  path: string,
  params: Record<string, string | undefined> = {}
): Promise<any | null> {
  const url = new URL(API + path);
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== "") url.searchParams.set(k, v);
  }
  const res = await fetch(url, { headers: { Authorization: `Bearer ${bearer}` } });
  if (res.status === 404) return null;
  const text = await res.text();
  if (!res.ok) throw new Error(`Google Play ${res.status}: ${text.slice(0, 300)}`);
  return emptyBody(text) ? {} : JSON.parse(text);
}

// ── The readings ───────────────────────────────────────────────────────────

export interface PlayRelease {
  track: string | null;
  name: string | null;
  lifecycle: string | null;
  version_codes: string[];
}

export interface PlayTrack {
  track: string;
  releases: PlayRelease[];
}

export interface PlayReview {
  review_id: string;
  author: string;
  said_at: string | null;
  star_rating: number | null;
  app_version: string | null;
  device: string | null;
  text: string;
}

// A ReleaseSummary: its track, its release name, its lifecycle state, and the version
// code of each active artifact.
function release(r: any): PlayRelease {
  return {
    track: r?.track ?? null,
    name: r?.releaseName ?? null,
    lifecycle: r?.releaseLifecycleState ?? null,
    version_codes: (r?.activeArtifacts ?? [])
      .map((a: any) => String(a?.versionCode ?? ""))
      .filter((code: string) => code !== ""),
  };
}

export function parsePlayReleases(data: any): PlayRelease[] {
  return (data?.releases ?? []).map(release);
}

// The first name the portal actually wrote; a blank one is no name at all.
function author(...names: unknown[]): string {
  for (const name of names) {
    const said = String(name ?? "").trim();
    if (said !== "") return said;
  }
  return "";
}

// A Play timestamp is seconds and nanos; the seed carries ISO.
function isoFromTimestamp(stamp: any): string | null {
  const secs = Number(stamp?.seconds);
  if (!Number.isFinite(secs)) return null;
  return new Date(secs * 1000).toISOString();
}

export function parsePlayReviews(data: any): PlayReview[] {
  const out: PlayReview[] = [];
  for (const r of data?.reviews ?? []) {
    const comment = (r?.comments ?? []).find((c: any) => c?.userComment)?.userComment;
    if (!comment) continue;
    out.push({
      review_id: String(r?.reviewId ?? ""),
      author: author(r?.authorName, "a Google user"),
      said_at: isoFromTimestamp(comment?.lastModified),
      star_rating: typeof comment?.starRating === "number" ? comment.starRating : null,
      app_version: comment?.appVersionName ?? null,
      device: comment?.device ?? null,
      text: comment?.text ?? "",
    });
  }
  return out;
}

// Play's own track ids; a custom closed track is named only inside an edit.
export const PLAY_TRACK_IDS = ["qa", "internal", "alpha", "beta", "production"] as const;

export interface PlayTracksReading {
  tracks: PlayTrack[];
  answered: string[];
  unanswered: string[];
}

// The track road: each named track's releases, one GET apiece.
// A track that answered 404 is named unanswered, never read as an empty track.
export async function playReadTracksByRelease(
  bearer: string,
  packageName: string,
  trackIds: readonly string[] = PLAY_TRACK_IDS
): Promise<PlayTracksReading> {
  const app = encodeURIComponent(packageName);
  const tracks: PlayTrack[] = [];
  const answered: string[] = [];
  const unanswered: string[] = [];
  for (const track of trackIds) {
    const path = `/applications/${app}/tracks/${encodeURIComponent(track)}/releases`;
    const data = await playGetOrNull(bearer, path);
    if (data === null) {
      unanswered.push(track);
      continue;
    }
    answered.push(track);
    const releases = parsePlayReleases(data);
    if (releases.length > 0) tracks.push({ track, releases });
  }
  return { tracks, answered, unanswered };
}

// What a package Play answered 404 for on every named track leaves to say.
export function playUnheld(packageName: string, trackIds: readonly string[]): string {
  return (
    `Google Play answered 404 for every named track of ${packageName} — ` +
    `${trackIds.join(", ")}. No track was read and no row is written.`
  );
}

export async function playReadReviews(bearer: string, packageName: string): Promise<PlayReview[]> {
  const app = encodeURIComponent(packageName);
  return parsePlayReviews(await playGet(bearer, `/applications/${app}/reviews`, { maxResults: "100" }));
}

// ── The seed row ───────────────────────────────────────────────────────────

// Each releaseLifecycleState a ReleaseSummary carries, and the release word it stands
// for; RELEASE_LIFECYCLE_STATE_UNSPECIFIED and any member not named here answer null.
const LIFECYCLE_RELEASE: Record<string, string> = {
  RELEASE_LIFECYCLE_STATE_DRAFT: "draft",
  RELEASE_LIFECYCLE_STATE_NOT_SENT_FOR_REVIEW: "draft",
  RELEASE_LIFECYCLE_STATE_IN_REVIEW: "inProgress",
  RELEASE_LIFECYCLE_STATE_APPROVED_NOT_PUBLISHED: "inProgress",
  RELEASE_LIFECYCLE_STATE_NOT_APPROVED: "rejected",
  RELEASE_LIFECYCLE_STATE_PUBLISHED: "completed",
};

// The enum member as Play writes it: trimmed, upper case.
function lifecycleWord(value: string | null): string {
  return (value ?? "").trim().toUpperCase();
}

export function releaseState(r: PlayRelease): string | null {
  return LIFECYCLE_RELEASE[lifecycleWord(r.lifecycle)] ?? null;
}

const STANDING = new Set(["inProgress", "completed"]);

// The 043 words ordered by how far a package has reached on the store; a refusal
// or a withdrawal never outranks a track that stands.
export const PLAY_REACH: readonly BeaconStatus[] = [
  "none",
  "planned",
  "building",
  "withdrawn",
  "rejected",
  "in_review",
  "internal_testing",
  "closed_testing",
  "open_testing",
  "published",
];

// The register holds one word per channel: the furthest the tracks have reached.
export function furthest(words: BeaconStatus[]): BeaconStatus | null {
  let best: BeaconStatus | null = null;
  for (const word of words) {
    if (best === null || PLAY_REACH.indexOf(word) > PLAY_REACH.indexOf(best)) best = word;
  }
  return best;
}

function standingRelease(track: PlayTrack): PlayRelease | undefined {
  return track.releases.find((r) => STANDING.has(releaseState(r) ?? "")) ?? track.releases[0];
}

// The version a release stands under: the release name Play wrote, else its version codes.
function releaseVersion(r: PlayRelease | undefined): string | null {
  if (r === undefined) return null;
  const name = (r.name ?? "").trim();
  if (name !== "") return name;
  return r.version_codes.length > 0 ? r.version_codes.join(", ") : null;
}

export function playTrackRow(
  slug: string,
  packageName: string,
  tracks: PlayTrack[],
  testingUrl: string | null
): TrackRow {
  const words: BeaconStatus[] = tracks
    .map((t) => {
      const live = standingRelease(t);
      return playStatus(t.track, live ? releaseState(live) : null);
    })
    .filter((w): w is BeaconStatus => w !== null);
  const production = tracks.find((t) => t.track === "production");
  const published = production?.releases.find((r) => releaseState(r) === "completed");
  const testing = tracks
    .filter((t) => t.track !== "production")
    .map(standingRelease)
    .find((r) => r !== undefined);
  const spoken = tracks.map((t) => {
    const live = standingRelease(t);
    return [t.track, live?.lifecycle ?? null, releaseVersion(live)].filter(Boolean).join(" ");
  });
  spoken.push(TESTERS_UNREAD);
  return {
    slug,
    channel: "play",
    app_id: packageName,
    listing_url: listingUrl("play", packageName),
    testing_url: testingUrl,
    status: furthest(words),
    testing_version: releaseVersion(testing),
    published_version: releaseVersion(published),
    published_at: null,
    testers: null,
    note: spoken.join(" · "),
  };
}

export function playReportRows(slug: string, reviews: PlayReview[]): ReportRow[] {
  return reviews
    .filter((r) => r.text.trim() !== "")
    .map((r) => ({
      id: `play:${r.review_id}`,
      slug,
      kind: "review" as const,
      said_by: r.author,
      said_at: r.said_at ?? new Date(0).toISOString(),
      where: "play review",
      text: r.text,
      link: null,
    }));
}

// ── The tools ──────────────────────────────────────────────────────────────

const PACKAGE = z.string().describe("the package name, as play_app_id holds it in the register");

const TRACKS = z
  .array(z.string())
  .optional()
  .describe("track ids to read; default qa, internal, alpha, beta, production");

export function registerPlay(server: McpServer) {
  server.tool(
    "play_whoami",
    "The Google Play service account this line stands as, its Cloud project, and whether a token can be minted for it. The line test — run it first; the private key never leaves its file.",
    {},
    async () => {
      const name = firstMissingKey();
      if (name) return shut(name);
      const account = await serviceAccount(keyPath());
      let minted: string;
      try {
        await playToken();
        minted = "a token was minted";
      } catch (e) {
        minted = (e as Error).message;
      }
      return asText({
        key_name: "GOOGLE_PLAY_SERVICE_ACCOUNT_JSON",
        service_account: account.client_email,
        cloud_project: account.project_id,
        scope: "https://www.googleapis.com/auth/androidpublisher",
        token: minted,
      });
    }
  );

  server.tool(
    "play_tracks",
    "Play's own named tracks for one package — qa, internal, alpha, beta, production, or only the tracks named — each with its releases, their version codes and their lifecycle state: draft, not sent for review, in review, approved not published, not approved, published. Read with GETs alone; a track Play answers 404 for is named unanswered, and a custom closed track is named only inside an edit this line does not open.",
    { package_name: PACKAGE, tracks: TRACKS },
    async ({ package_name, tracks }) => {
      const name = firstMissingKey();
      if (name) return shut(name);
      const reading = await playReadTracksByRelease(await playToken(), package_name, tracks);
      return asText({
        package_name,
        tracks: reading.tracks,
        tracks_answered: reading.answered,
        tracks_unanswered: reading.unanswered,
        custom_tracks: CUSTOM_TRACKS,
        testers: TESTERS_UNREAD,
      });
    }
  );

  server.tool(
    "play_reviews",
    "The reviews Play still holds for one package — the last week of them — each reviewer's words VERBATIM with the star rating, app version and device. Quote them, never silently summarize.",
    { package_name: PACKAGE },
    async ({ package_name }) => {
      const name = firstMissingKey();
      if (name) return shut(name);
      return asText({ package_name, reviews: await playReadReviews(await playToken(), package_name) });
    }
  );
}
