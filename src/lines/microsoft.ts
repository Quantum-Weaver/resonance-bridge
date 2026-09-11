import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import {
  listingUrl,
  microsoftStatus,
  microsoftToken,
  readKeys,
  shutDoor,
  STORE_KEY_NAMES,
  type ReportRow,
  type TrackRow,
} from "./tracks.js";

// The Microsoft Store line — GETs only against the Store submission API and
// the analytics API beside it, never the CSP Partner Center API. No submission
// is created, committed or cancelled here.

const API = "https://manage.devcenter.microsoft.com/v1.0/my";

function firstMissingKey(): string | null {
  return readKeys(STORE_KEY_NAMES.microsoft).missing[0] ?? null;
}

function shut(keyName: string) {
  return { content: [{ type: "text" as const, text: shutDoor("microsoft", keyName) }] };
}

function asText(data: unknown) {
  return { content: [{ type: "text" as const, text: JSON.stringify(data, null, 2) }] };
}

export async function msToken(): Promise<string> {
  return microsoftToken(
    process.env.MS_STORE_TENANT_ID ?? "",
    process.env.MS_STORE_CLIENT_ID ?? "",
    process.env.MS_STORE_CLIENT_SECRET ?? ""
  );
}

async function msGet(
  bearer: string,
  path: string,
  params: Record<string, string | undefined> = {}
): Promise<any> {
  const url = new URL(API + path);
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== "") url.searchParams.set(k, v);
  }
  const res = await fetch(url, {
    headers: { Authorization: `Bearer ${bearer}`, "Content-Type": "application/json" },
  });
  if (!res.ok) throw new Error(`Microsoft Store ${res.status}: ${(await res.text()).slice(0, 300)}`);
  return res.json();
}

// ── The readings ───────────────────────────────────────────────────────────

export interface MsApp {
  id: string;
  primary_name: string | null;
  package_family_name: string | null;
  first_published_at: string | null;
  pending_submission_id: string | null;
  published_submission_id: string | null;
}

export interface MsFlight {
  flight_id: string;
  friendly_name: string | null;
  group_ids: string[];
  pending_submission_id: string | null;
  published_submission_id: string | null;
}

export interface MsSubmissionStatus {
  status: string | null;
  errors: string[];
  warnings: string[];
}

export interface MsSubmission {
  id: string;
  flight_id: string | null;
  friendly_name: string | null;
  status: string | null;
  version: string | null;
  package_versions: string[];
  target_publish_mode: string | null;
  target_publish_date: string | null;
}

export interface MsReview {
  review_id: string;
  author: string;
  said_at: string | null;
  rating: number | null;
  market: string | null;
  package_version: string | null;
  title: string;
  text: string;
}

// The submission API answers value, the analytics API answers Value.
function values(data: any): any[] {
  if (Array.isArray(data)) return data;
  if (Array.isArray(data?.value)) return data.value;
  if (Array.isArray(data?.Value)) return data.Value;
  return [];
}

function submissionId(node: any): string | null {
  const id = node?.id;
  return id === undefined || id === null || id === "" ? null : String(id);
}

// The first name the portal actually wrote; a blank one is no name at all.
function author(...names: unknown[]): string {
  for (const name of names) {
    const said = String(name ?? "").trim();
    if (said !== "") return said;
  }
  return "";
}

function iso(value: any): string | null {
  const text = String(value ?? "").trim();
  if (text === "") return null;
  const stamp = Date.parse(text);
  return Number.isFinite(stamp) ? new Date(stamp).toISOString() : null;
}

export function parseMsApps(data: any): MsApp[] {
  return values(data).map((a: any) => ({
    id: String(a?.id ?? ""),
    primary_name: a?.primaryName ?? null,
    package_family_name: a?.packageFamilyName ?? null,
    first_published_at: iso(a?.firstPublishedDate),
    pending_submission_id: submissionId(a?.pendingApplicationSubmission),
    published_submission_id: submissionId(a?.lastPublishedApplicationSubmission),
  }));
}

export function parseMsFlights(data: any): MsFlight[] {
  return values(data).map((f: any) => ({
    flight_id: String(f?.flightId ?? f?.id ?? ""),
    friendly_name: f?.friendlyName ?? null,
    group_ids: (f?.groupIds ?? []).map((g: any) => String(g)),
    pending_submission_id: submissionId(f?.pendingFlightSubmission),
    published_submission_id: submissionId(f?.lastPublishedFlightSubmission),
  }));
}

export function parseMsSubmissionStatus(data: any): MsSubmissionStatus {
  const details = data?.statusDetails ?? {};
  const say = (rows: any) => (rows ?? []).map((r: any) => String(r?.details ?? r?.code ?? r));
  return {
    status: data?.status ?? null,
    errors: say(details?.errors),
    warnings: say(details?.warnings),
  };
}

export function parseMsReviews(data: any): MsReview[] {
  return values(data)
    .map((r: any) => ({
      review_id: String(r?.reviewId ?? ""),
      author: author(r?.reviewerName, "a Microsoft Store user"),
      said_at: iso(r?.updatedDate ?? r?.date),
      rating: Number.isFinite(Number(r?.rating)) ? Number(r.rating) : null,
      market: r?.market ?? null,
      package_version: r?.packageVersion ?? null,
      title: r?.reviewTitle ?? "",
      text: r?.reviewText ?? "",
    }))
    .filter((r: MsReview) => r.review_id !== "");
}

// An application submission carries applicationPackages, a flight's carries flightPackages.
export function parseMsSubmission(data: any): MsSubmission | null {
  if (!data || data.id === undefined || data.id === null || data.id === "") return null;
  const packages = Array.isArray(data?.applicationPackages)
    ? data.applicationPackages
    : Array.isArray(data?.flightPackages)
      ? data.flightPackages
      : [];
  const versions: string[] = [];
  for (const p of packages) {
    const version = String(p?.version ?? "").trim();
    if (version !== "" && !versions.includes(version)) versions.push(version);
  }
  return {
    id: String(data.id),
    flight_id: data?.flightId === undefined || data?.flightId === null ? null : String(data.flightId),
    friendly_name: data?.friendlyName ?? null,
    status: data?.status ?? null,
    version: versions[0] ?? null,
    package_versions: versions,
    target_publish_mode: data?.targetPublishMode ?? null,
    target_publish_date: iso(data?.targetPublishDate),
  };
}

export async function msReadApps(bearer: string): Promise<MsApp[]> {
  const out: MsApp[] = [];
  let skip = 0;
  for (;;) {
    const page = await msGet(bearer, "/applications", { top: "100", skip: String(skip) });
    const rows = parseMsApps(page);
    out.push(...rows);
    if (rows.length < 100 || !page?.["@nextLink"]) break;
    skip += rows.length;
  }
  return out;
}

export async function msReadFlights(bearer: string, applicationId: string): Promise<MsFlight[]> {
  const app = encodeURIComponent(applicationId);
  return parseMsFlights(await msGet(bearer, `/applications/${app}/listflights`));
}

export async function msReadSubmissionStatus(
  bearer: string,
  applicationId: string,
  submission: string
): Promise<MsSubmissionStatus> {
  const app = encodeURIComponent(applicationId);
  const id = encodeURIComponent(submission);
  return parseMsSubmissionStatus(await msGet(bearer, `/applications/${app}/submissions/${id}/status`));
}

// A flight id names a flight's submission; without one the app's own is read.
export async function msReadSubmission(
  bearer: string,
  applicationId: string,
  submission: string,
  flightId: string | null = null
): Promise<MsSubmission | null> {
  const app = encodeURIComponent(applicationId);
  const id = encodeURIComponent(submission);
  const path =
    flightId === null || flightId === ""
      ? `/applications/${app}/submissions/${id}`
      : `/applications/${app}/flights/${encodeURIComponent(flightId)}/submissions/${id}`;
  return parseMsSubmission(await msGet(bearer, path));
}

// The last seven days, the window the reviews read defaults to.
export function reviewWindow(): { start_date: string; end_date: string } {
  const now = Date.now();
  return {
    start_date: new Date(now - 7 * 86400000).toISOString().slice(0, 10),
    end_date: new Date(now).toISOString().slice(0, 10),
  };
}

export async function msReadReviews(
  bearer: string,
  applicationId: string,
  startDate: string,
  endDate: string
): Promise<MsReview[]> {
  return parseMsReviews(
    await msGet(bearer, "/analytics/reviews", {
      applicationId,
      startDate,
      endDate,
      top: "100",
    })
  );
}

// ── The seed row ───────────────────────────────────────────────────────────

export function microsoftTrackRow(
  slug: string,
  app: MsApp,
  flights: MsFlight[],
  submission: MsSubmissionStatus | null,
  published: MsSubmission | null = null,
  testing: MsSubmission | null = null
): TrackRow {
  const inFlight = flights.some(
    (f) => f.pending_submission_id !== null || f.published_submission_id !== null
  );
  const note = [
    submission?.status ?? null,
    flights.length > 0 ? `flights: ${flights.map((f) => f.friendly_name ?? f.flight_id).join(", ")}` : null,
  ]
    .filter(Boolean)
    .join(" · ");
  return {
    slug,
    channel: "microsoft",
    app_id: app.id,
    listing_url: listingUrl("microsoft", app.id),
    testing_url: null,
    status: microsoftStatus(submission?.status ?? null, inFlight),
    testing_version: testing?.version ?? null,
    published_version: published?.version ?? null,
    published_at: app.first_published_at,
    testers: null,
    note,
  };
}

export function microsoftReportRows(slug: string, reviews: MsReview[]): ReportRow[] {
  return reviews
    .map((r) => ({
      id: `microsoft:${r.review_id}`,
      slug,
      kind: "review" as const,
      said_by: r.author,
      said_at: r.said_at ?? new Date(0).toISOString(),
      where: "microsoft review",
      text: [r.title, r.text].filter((part) => part.trim() !== "").join("\n"),
      link: null,
    }))
    .filter((r) => r.text.trim() !== "");
}

// ── The tools ──────────────────────────────────────────────────────────────

const APP_ID = z.string().describe("the Store ID, as microsoft_app_id holds it in the register");

export function registerMicrosoft(server: McpServer) {
  server.tool(
    "ms_whoami",
    "Whether the Microsoft Store line can mint a token for the Entra application on the ring, and which of its three key names the ring holds. The line test — run it first; no key value is read out of the ring.",
    {},
    async () => {
      const name = firstMissingKey();
      if (name) return shut(name);
      let minted: string;
      try {
        await msToken();
        minted = "a token was minted";
      } catch (e) {
        minted = (e as Error).message;
      }
      return asText({
        key_names: STORE_KEY_NAMES.microsoft,
        on_the_ring: readKeys(STORE_KEY_NAMES.microsoft).present,
        resource: "https://manage.devcenter.microsoft.com",
        token: minted,
      });
    }
  );

  server.tool(
    "ms_apps",
    "Every app the Partner Center account holds, page after page — Store ID, primary name, package family name, when it was first published, and the ids of its pending and last published submissions.",
    {},
    async () => {
      const name = firstMissingKey();
      if (name) return shut(name);
      return asText({ apps: await msReadApps(await msToken()) });
    }
  );

  server.tool(
    "ms_flights",
    "One app's flights — the Microsoft Store's testing groups — with each flight's id, friendly name, the group ids that may install it, and its pending and published submission ids.",
    { application_id: APP_ID },
    async ({ application_id }) => {
      const name = firstMissingKey();
      if (name) return shut(name);
      return asText({ application_id, flights: await msReadFlights(await msToken(), application_id) });
    }
  );

  server.tool(
    "ms_submission_status",
    "One submission's status and the certification errors and warnings beside it, read from the Store submission API.",
    {
      application_id: APP_ID,
      submission_id: z.string().describe("a submission id from ms_apps"),
    },
    async ({ application_id, submission_id }) => {
      const name = firstMissingKey();
      if (name) return shut(name);
      const status = await msReadSubmissionStatus(await msToken(), application_id, submission_id);
      return asText({ application_id, submission_id, status });
    }
  );

  server.tool(
    "ms_submission",
    "One submission itself — its status, its friendly name, the package versions it carries, and when and how it is set to publish. The one Microsoft read that names a version, for the register's testing and published version columns.",
    {
      application_id: APP_ID,
      submission_id: z.string().describe("a submission id from ms_apps or ms_flights"),
      flight_id: z.string().optional().describe("a flight id from ms_flights, for a flight's submission"),
    },
    async ({ application_id, submission_id, flight_id }) => {
      const name = firstMissingKey();
      if (name) return shut(name);
      const submission = await msReadSubmission(
        await msToken(),
        application_id,
        submission_id,
        flight_id ?? null
      );
      return asText({ application_id, submission_id, flight_id: flight_id ?? null, submission });
    }
  );

  server.tool(
    "ms_reviews",
    "The reviews left on one app in the Microsoft Store over a window of dates, each writer's title and words VERBATIM with the rating, market and package version. Quote them, never silently summarize.",
    {
      application_id: APP_ID,
      start_date: z.string().optional().describe("the window's first day, YYYY-MM-DD, default seven days back"),
      end_date: z.string().optional().describe("the window's last day, YYYY-MM-DD, default today"),
    },
    async ({ application_id, start_date, end_date }) => {
      const name = firstMissingKey();
      if (name) return shut(name);
      const window = reviewWindow();
      const from = start_date ?? window.start_date;
      const to = end_date ?? window.end_date;
      const reviews = await msReadReviews(await msToken(), application_id, from, to);
      return asText({ application_id, start_date: from, end_date: to, reviews });
    }
  );
}
