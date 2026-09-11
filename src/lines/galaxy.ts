import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import {
  galaxyStatus,
  listingUrl,
  readKeys,
  samsungAccessToken,
  shutDoor,
  STORE_KEY_NAMES,
  type ReportRow,
  type TrackRow,
} from "./tracks.js";

// The Galaxy Store line — GETs only against the GSD API. The one store that
// hands over a beta link; no write verb is built here at all.

const API = "https://devapi.samsungapps.com";

function firstMissingKey(): string | null {
  return readKeys(STORE_KEY_NAMES.galaxy).missing[0] ?? null;
}

function shut(keyName: string) {
  return { content: [{ type: "text" as const, text: shutDoor("galaxy", keyName) }] };
}

function asText(data: unknown) {
  return { content: [{ type: "text" as const, text: JSON.stringify(data, null, 2) }] };
}

function serviceAccountId(): string {
  return process.env.SAMSUNG_GSD_SERVICE_ACCOUNT_ID ?? "";
}

export async function galaxyToken(): Promise<string> {
  return samsungAccessToken(serviceAccountId(), process.env.SAMSUNG_GSD_PRIVATE_KEY_PATH ?? "");
}

async function galaxyGet(
  bearer: string,
  path: string,
  params: Record<string, string | undefined> = {}
): Promise<any> {
  const url = new URL(API + path);
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== "") url.searchParams.set(k, v);
  }
  const res = await fetch(url, {
    headers: {
      Authorization: `Bearer ${bearer}`,
      "service-account-id": serviceAccountId(),
      "Content-Type": "application/json",
    },
  });
  if (!res.ok) throw new Error(`Galaxy Store ${res.status}: ${(await res.text()).slice(0, 300)}`);
  return res.json();
}

// ── The readings ───────────────────────────────────────────────────────────

export interface GalaxyApp {
  content_id: string;
  content_name: string | null;
  content_status: string | null;
  package_name: string | null;
  modified_at: string | null;
}

export interface GalaxyDetail {
  content_id: string;
  content_name: string | null;
  content_status: string | null;
  package_name: string | null;
  published_version: string | null;
  published_at: string | null;
}

export interface GalaxyBeta {
  content_id: string | null;
  state: string | null;
  testers: number | null;
  testing_url: string | null;
  testing_version: string | null;
}

export interface GalaxyComment {
  comment_id: string;
  author: string;
  said_at: string | null;
  rating: number | null;
  text: string;
}

// The GSD API answers a bare list or a list under a named field.
function list(data: any, ...fields: string[]): any[] {
  if (Array.isArray(data)) return data;
  for (const field of fields) {
    if (Array.isArray(data?.[field])) return data[field];
  }
  return [];
}

// The first name the portal actually wrote; a blank one is no name at all.
function author(...names: unknown[]): string {
  for (const name of names) {
    const said = String(name ?? "").trim();
    if (said !== "") return said;
  }
  return "";
}

// A Galaxy date is a day or a day and a clock; the seed carries ISO.
function isoFromGalaxy(value: any): string | null {
  const text = String(value ?? "").trim();
  if (text === "") return null;
  const stamp = Date.parse(text.includes("T") ? text : text.replace(" ", "T") + "Z");
  return Number.isFinite(stamp) ? new Date(stamp).toISOString() : null;
}

export function parseGalaxyApps(data: any): GalaxyApp[] {
  return list(data, "contentList", "list").map((c: any) => ({
    content_id: String(c?.contentId ?? ""),
    content_name: c?.contentName ?? c?.appTitle ?? null,
    content_status: c?.contentStatus ?? null,
    package_name: c?.packageName ?? c?.appId ?? null,
    modified_at: isoFromGalaxy(c?.modifyDate ?? c?.lastModifyDate),
  }));
}

export function parseGalaxyApp(data: any): GalaxyDetail | null {
  const c = Array.isArray(data) ? data[0] : (data?.contentInfo ?? data);
  if (!c || c.contentId === undefined) return null;
  const binaries = list(c, "binaryList");
  const last = binaries[binaries.length - 1];
  return {
    content_id: String(c.contentId),
    content_name: c?.contentName ?? c?.appTitle ?? null,
    content_status: c?.contentStatus ?? null,
    package_name: c?.packageName ?? c?.appId ?? null,
    published_version: last?.versionName ?? null,
    published_at: isoFromGalaxy(c?.startPublicationDate ?? c?.publicationDate),
  };
}

export function parseGalaxyBeta(data: any): GalaxyBeta {
  const b = Array.isArray(data) ? (data[0] ?? {}) : (data?.betaTest ?? data ?? {});
  const testers = Number(b?.testerCount ?? b?.testerNum);
  return {
    content_id: b?.contentId !== undefined ? String(b.contentId) : null,
    state: b?.betaTestStatus ?? b?.betaTestYN ?? null,
    testers: Number.isFinite(testers) ? testers : null,
    testing_url: b?.betaTestingUrl?.android ?? b?.betaTestingUrl?.web ?? null,
    testing_version: b?.versionName ?? null,
  };
}

export function parseGalaxyComments(data: any): GalaxyComment[] {
  return list(data, "commentList", "list")
    .map((c: any) => ({
      comment_id: String(c?.commentId ?? c?.id ?? ""),
      author: author(c?.userName, c?.userId, "a Galaxy Store user"),
      said_at: isoFromGalaxy(c?.createDate ?? c?.commentDate),
      rating: Number.isFinite(Number(c?.rating)) ? Number(c.rating) : null,
      text: c?.commentText ?? c?.comment ?? "",
    }))
    .filter((c: GalaxyComment) => c.comment_id !== "");
}

export async function galaxyReadApps(bearer: string): Promise<GalaxyApp[]> {
  return parseGalaxyApps(await galaxyGet(bearer, "/seller/contentList"));
}

export async function galaxyReadApp(bearer: string, contentId: string): Promise<GalaxyDetail | null> {
  return parseGalaxyApp(await galaxyGet(bearer, "/seller/contentInfo", { contentId }));
}

export async function galaxyReadBeta(bearer: string, contentId: string): Promise<GalaxyBeta> {
  return parseGalaxyBeta(await galaxyGet(bearer, "/seller/v2/content/betaTest", { contentId }));
}

export async function galaxyReadComments(bearer: string, contentId: string): Promise<GalaxyComment[]> {
  return parseGalaxyComments(await galaxyGet(bearer, "/seller/v2/content/comment", { contentId }));
}

// ── The seed row ───────────────────────────────────────────────────────────

export function galaxyTrackRow(
  slug: string,
  app: GalaxyDetail | GalaxyApp,
  beta: GalaxyBeta | null
): TrackRow {
  const detail = app as GalaxyDetail;
  const note = [app.content_status, beta?.state ? `beta ${beta.state}` : null]
    .filter(Boolean)
    .join(" · ");
  return {
    slug,
    channel: "galaxy",
    app_id: app.content_id,
    listing_url: app.package_name ? listingUrl("galaxy", app.package_name) : null,
    testing_url: beta?.testing_url ?? null,
    status: galaxyStatus(app.content_status, beta?.state ?? null),
    testing_version: beta?.testing_version ?? null,
    published_version: detail.published_version ?? null,
    published_at: detail.published_at ?? null,
    testers: beta?.testers ?? null,
    note,
  };
}

export function galaxyReportRows(slug: string, comments: GalaxyComment[]): ReportRow[] {
  return comments
    .filter((c) => c.text.trim() !== "")
    .map((c) => ({
      id: `galaxy:${c.comment_id}`,
      slug,
      kind: "review" as const,
      said_by: c.author,
      said_at: c.said_at ?? new Date(0).toISOString(),
      where: "galaxy review",
      text: c.text,
      link: null,
    }));
}

// ── The tools ──────────────────────────────────────────────────────────────

const CONTENT = z.string().describe("the content id, as galaxy_app_id holds it in the register");

export function registerGalaxy(server: McpServer) {
  server.tool(
    "galaxy_whoami",
    "Whether the Galaxy Store line can mint an access token for the service account on the ring, and which of its key names the ring holds. The line test — run it first; no key value is read out and the private key never leaves its file.",
    {},
    async () => {
      const name = firstMissingKey();
      if (name) return shut(name);
      let minted: string;
      try {
        await galaxyToken();
        minted = "a token was minted";
      } catch (e) {
        minted = (e as Error).message;
      }
      return asText({
        key_names: STORE_KEY_NAMES.galaxy,
        on_the_ring: readKeys(STORE_KEY_NAMES.galaxy).present,
        scopes: ["publishing", "gss"],
        token: minted,
      });
    }
  );

  server.tool(
    "galaxy_apps",
    "Every app the seller account holds in the Galaxy Store — content id, name, package name, the store's own content status and when it last moved.",
    {},
    async () => {
      const name = firstMissingKey();
      if (name) return shut(name);
      return asText({ apps: await galaxyReadApps(await galaxyToken()) });
    }
  );

  server.tool(
    "galaxy_app",
    "One app's detail — the content status, the package name, the version of its latest binary and when the store first published it.",
    { content_id: CONTENT },
    async ({ content_id }) => {
      const name = firstMissingKey();
      if (name) return shut(name);
      return asText({ content_id, app: await galaxyReadApp(await galaxyToken(), content_id) });
    }
  );

  server.tool(
    "galaxy_beta",
    "One app's beta test — its state, the number of testers the store counts, the version under test and the beta testing URL. Galaxy is the one store that hands the tester link over.",
    { content_id: CONTENT },
    async ({ content_id }) => {
      const name = firstMissingKey();
      if (name) return shut(name);
      return asText({ content_id, beta: await galaxyReadBeta(await galaxyToken(), content_id) });
    }
  );

  server.tool(
    "galaxy_comments",
    "The comments left on one app in the Galaxy Store, each writer's words VERBATIM with the rating and the date. Quote them, never silently summarize.",
    { content_id: CONTENT },
    async ({ content_id }) => {
      const name = firstMissingKey();
      if (name) return shut(name);
      return asText({ content_id, comments: await galaxyReadComments(await galaxyToken(), content_id) });
    }
  );
}
