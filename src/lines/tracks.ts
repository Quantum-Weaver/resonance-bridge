// The tracks seam the store lines and the census share: the two seed shapes, the 043 status
// words and the mapping onto them, the tokens, the listing addresses, the ring, the shut door.

import { createSign } from "node:crypto";
import { readFile } from "node:fs/promises";

// ── The words ──────────────────────────────────────────────────────────────

export const BEACON_STATUSES = [
  "none",
  "planned",
  "building",
  "internal_testing",
  "closed_testing",
  "open_testing",
  "in_review",
  "published",
  "rejected",
  "withdrawn",
] as const;

export type BeaconStatus = (typeof BEACON_STATUSES)[number];

// A row's word: a 043 word, or null where the portal named none.
export type TrackStatus = BeaconStatus | null;

export const STORE_CHANNELS = ["play", "galaxy", "microsoft"] as const;

export type StoreChannel = (typeof STORE_CHANNELS)[number];

export const REPORT_KINDS = ["bug", "note", "review"] as const;

export type ReportKind = (typeof REPORT_KINDS)[number];

export const TRACKS_SOURCE = "play · galaxy · microsoft";

export const REPORTS_SOURCE = "discord · play · galaxy · microsoft";

// ── The seeds ──────────────────────────────────────────────────────────────

export type DoorState = "read" | `unread: ${string}`;

export interface TrackRow {
  slug: string;
  channel: StoreChannel;
  app_id: string;
  listing_url: string | null;
  testing_url: string | null;
  status: TrackStatus;
  testing_version: string | null;
  published_version: string | null;
  published_at: string | null;
  testers: number | null;
  note: string;
}

export interface TracksSeed {
  source: string;
  read_at: string;
  doors: Record<StoreChannel, DoorState>;
  rows: TrackRow[];
}

export interface ReportRow {
  id: string;
  slug: string;
  kind: ReportKind;
  said_by: string;
  said_at: string;
  where: string;
  text: string;
  link: string | null;
}

export interface ReportsSeed {
  source: string;
  read_at: string;
  rows: ReportRow[];
}

// ── The mapping ────────────────────────────────────────────────────────────

// A store's word, lowercased with every separator dropped.
function word(value: string | null | undefined): string {
  return (value ?? "").toLowerCase().replace(/[^a-z0-9]/g, "");
}

// The release state names the word; the track id only says how far a standing release
// reaches. qa and internal are Play's internal track; every other id is a custom track.
export function playStatus(trackId: string, release: string | null): TrackStatus {
  const rel = word(release);
  if (rel === "inprogress") return "in_review";
  if (rel === "rejected") return "rejected";
  if (rel === "draft") return "planned";
  // A release state the portal did not name leaves the register holding what it holds.
  if (rel !== "completed") return null;

  const track = (trackId ?? "").trim().toLowerCase();
  if (track === "qa" || track === "internal") return "internal_testing";
  if (track === "beta") return "open_testing";
  if (track === "production") return "published";
  return "closed_testing";
}

const GALAXY_BETA_OFF = new Set([
  "",
  "none",
  "n",
  "no",
  "off",
  "terminated",
  "ended",
  "end",
  "stopped",
]);

export function galaxyStatus(
  contentStatus: string | null,
  betaState: string | null
): TrackStatus {
  if (!GALAXY_BETA_OFF.has(word(betaState))) return "closed_testing";
  const content = word(contentStatus);
  if (content === "forsale") return "published";
  if (content === "undercontentreview") return "in_review";
  if (content === "registering") return "building";
  // A content status the portal does not name answers null.
  return null;
}

// inFlight: the app has a flight carrying a submission.
export function microsoftStatus(
  submissionStatus: string | null,
  inFlight: boolean
): TrackStatus {
  if (inFlight) return "closed_testing";
  const state = word(submissionStatus);
  if (state === "published") return "published";
  if (state === "certificationfailed") return "rejected";
  if (state === "certification" || state === "pendingpublication" || state === "release") {
    return "in_review";
  }
  if (state === "pendingcommit" || state === "commitstarted" || state === "commitfailed") {
    return "building";
  }
  if (state === "canceled" || state === "cancelled") return "planned";
  // A submission status the portal does not name answers null.
  return null;
}

// ── The ring ───────────────────────────────────────────────────────────────

export const PORTAL_CLICKS: Readonly<Record<string, string>> = {
  GOOGLE_PLAY_SERVICE_ACCOUNT_JSON:
    "Play Console → Setup → API access → link a Cloud project, create the service account, " +
    "grant it View app information (read-only), download its JSON key, and put the file's " +
    "path on the ring by your own hands",
  SAMSUNG_GSD_SERVICE_ACCOUNT_ID:
    "Seller Portal → Assistance → API Service → create a service account and put the Service " +
    "Account ID it shows on the ring by your own hands",
  SAMSUNG_GSD_PRIVATE_KEY_PATH:
    "Seller Portal → Assistance → API Service → download the private key beside that service " +
    "account and put the file's path on the ring by your own hands",
  MS_STORE_TENANT_ID:
    "Partner Center → Account settings → Tenants → create or associate an Entra tenant and put " +
    "its directory id on the ring by your own hands",
  MS_STORE_CLIENT_ID:
    "Partner Center → Account settings → User management → Entra applications → add an " +
    "application with the Manager role and put its application id on the ring by your own hands",
  MS_STORE_CLIENT_SECRET:
    "the Azure portal → that Entra application → Certificates & secrets → New client secret, " +
    "on the ring by your own hands",
};

export const STORE_KEY_NAMES: Readonly<Record<StoreChannel, readonly string[]>> = {
  play: ["GOOGLE_PLAY_SERVICE_ACCOUNT_JSON"],
  galaxy: ["SAMSUNG_GSD_SERVICE_ACCOUNT_ID", "SAMSUNG_GSD_PRIVATE_KEY_PATH"],
  microsoft: ["MS_STORE_TENANT_ID", "MS_STORE_CLIENT_ID", "MS_STORE_CLIENT_SECRET"],
};

export const STORE_NAMES: Readonly<Record<StoreChannel, string>> = {
  play: "Google Play",
  galaxy: "Galaxy Store",
  microsoft: "Microsoft Store",
};

export interface KeyReading {
  present: string[];
  missing: string[];
}

// Names only; no value enters the return.
export function readKeys(names: readonly string[]): KeyReading {
  const present: string[] = [];
  const missing: string[] = [];
  for (const name of names) {
    const value = process.env[name];
    if (value !== undefined && value.trim() !== "") present.push(name);
    else missing.push(name);
  }
  return { present, missing };
}

export function shutDoor(
  store: StoreChannel,
  keyName: string,
  click: string = PORTAL_CLICKS[keyName] ?? ""
): string {
  const opening = `The ${STORE_NAMES[store]} line is shut: ${keyName} is not on the bridge's ring`;
  const door = click.trim().replace(/\.+$/, "");
  return door === "" ? `${opening}.` : `${opening} — ${door}.`;
}

export const REGISTER_KEY_NAMES = [
  "SUPABASE_URL_KNOWLEDGE",
  "SUPABASE_PUBLISHABLE_KEY_KNOWLEDGE",
] as const;

export const REGISTER_CLICKS: Readonly<Record<string, string>> = {
  SUPABASE_URL_KNOWLEDGE:
    "Supabase → the knowledge project → Project Settings → Data API → copy the Project URL",
  SUPABASE_PUBLISHABLE_KEY_KNOWLEDGE:
    "Supabase → the knowledge project → Project Settings → API Keys → copy the publishable key",
};

// One sentence naming the register key, the click that earns it, and what is read until then.
export function registerDoor(keyName: string, until: string): string {
  const opening = `The register is unread: ${keyName} is not on the bridge's ring`;
  const click = (REGISTER_CLICKS[keyName] ?? "").trim().replace(/\.+$/, "");
  const door =
    click === ""
      ? opening
      : `${opening} — ${click} → into resonance-bridge/.env by your own hands`;
  return `${door}; ${until}`;
}

// ── The addresses ──────────────────────────────────────────────────────────

const LISTING: Readonly<Record<StoreChannel, (appId: string) => string>> = {
  play: (id) => `https://play.google.com/store/apps/details?id=${encodeURIComponent(id)}`,
  galaxy: (id) => `https://galaxystore.samsung.com/detail/${encodeURIComponent(id)}`,
  microsoft: (id) => `https://apps.microsoft.com/detail/${encodeURIComponent(id)}`,
};

export function listingUrl(store: StoreChannel, appId: string | null): string | null {
  const id = (appId ?? "").trim();
  return id === "" ? null : LISTING[store](id);
}

// ── The tokens ─────────────────────────────────────────────────────────────

const GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token";
const GOOGLE_PLAY_SCOPE = "https://www.googleapis.com/auth/androidpublisher";
const GOOGLE_JWT_GRANT = "urn:ietf:params:oauth:grant-type:jwt-bearer";
const SAMSUNG_TOKEN_URL = "https://devapi.samsungapps.com/auth/accessToken";
const MICROSOFT_LOGIN = "https://login.microsoftonline.com";
const MICROSOFT_RESOURCE = "https://manage.devcenter.microsoft.com";

function b64url(text: string): string {
  return Buffer.from(text, "utf8").toString("base64url");
}

export function rs256Jwt(
  header: Record<string, unknown>,
  payload: Record<string, unknown>,
  privateKeyPem: string
): string {
  const signingInput = `${b64url(JSON.stringify(header))}.${b64url(JSON.stringify(payload))}`;
  const signer = createSign("RSA-SHA256");
  signer.update(signingInput);
  let signature: Buffer;
  try {
    signature = signer.sign(privateKeyPem);
  } catch {
    throw new Error("The private key named on the ring is not an RSA private key node can sign with.");
  }
  return `${signingInput}.${signature.toString("base64url")}`;
}

// The error code an endpoint names, and nothing else of its body.
function errorCode(body: string): string {
  const match = /"error"\s*:\s*"([A-Za-z0-9_.-]+)"/.exec(body);
  return match ? ` (${match[1]})` : "";
}

async function tokenPost(portal: string, url: string, init: RequestInit): Promise<any> {
  let res: Response;
  try {
    res = await fetch(url, { method: "POST", ...init });
  } catch {
    throw new Error(`The ${portal} token endpoint could not be reached.`);
  }
  const raw = await res.text();
  if (!res.ok) {
    throw new Error(`The ${portal} token endpoint answered ${res.status}${errorCode(raw)}.`);
  }
  try {
    return JSON.parse(raw);
  } catch {
    throw new Error(
      `The ${portal} token endpoint answered ${res.status} with a body that is not JSON.`
    );
  }
}

function seconds(): number {
  return Math.floor(Date.now() / 1000);
}

export async function googleServiceAccountToken(jsonPath: string): Promise<string> {
  let account: { client_email?: string; private_key?: string };
  try {
    account = JSON.parse(await readFile(jsonPath, "utf8"));
  } catch {
    throw new Error(
      "The Google Play service account file named on the ring could not be read as JSON."
    );
  }
  if (!account.client_email || !account.private_key) {
    throw new Error(
      "The Google Play service account file carries no client_email or no private_key."
    );
  }
  const now = seconds();
  const assertion = rs256Jwt(
    { alg: "RS256", typ: "JWT" },
    {
      iss: account.client_email,
      scope: GOOGLE_PLAY_SCOPE,
      aud: GOOGLE_TOKEN_URL,
      iat: now,
      exp: now + 3600,
    },
    account.private_key
  );
  const data = await tokenPost("Google Play", GOOGLE_TOKEN_URL, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ grant_type: GOOGLE_JWT_GRANT, assertion }),
  });
  const token = data?.access_token;
  if (typeof token !== "string" || token === "") {
    throw new Error("The Google Play token endpoint returned no access_token.");
  }
  return token;
}

export async function samsungAccessToken(
  serviceAccountId: string,
  privateKeyPath: string
): Promise<string> {
  let pem: string;
  try {
    pem = await readFile(privateKeyPath, "utf8");
  } catch {
    throw new Error("The Galaxy Store private key file named on the ring could not be read.");
  }
  const now = seconds();
  const jwt = rs256Jwt(
    { alg: "RS256", typ: "JWT" },
    { iss: serviceAccountId, scopes: ["publishing", "gss"], iat: now, exp: now + 1200 },
    pem
  );
  const data = await tokenPost("Galaxy Store", SAMSUNG_TOKEN_URL, {
    headers: {
      Authorization: `Bearer ${jwt}`,
      "service-account-id": serviceAccountId,
      "Content-Type": "application/json",
    },
  });
  const token = data?.createdItem?.accessToken ?? data?.accessToken;
  if (typeof token !== "string" || token === "") {
    throw new Error("The Galaxy Store token endpoint returned no accessToken.");
  }
  return token;
}

export async function microsoftToken(
  tenant: string,
  clientId: string,
  secret: string
): Promise<string> {
  const data = await tokenPost(
    "Microsoft Store",
    `${MICROSOFT_LOGIN}/${encodeURIComponent(tenant)}/oauth2/token`,
    {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        grant_type: "client_credentials",
        client_id: clientId,
        client_secret: secret,
        resource: MICROSOFT_RESOURCE,
      }),
    }
  );
  const token = data?.access_token;
  if (typeof token !== "string" || token === "") {
    throw new Error("The Microsoft Store token endpoint returned no access_token.");
  }
  return token;
}
