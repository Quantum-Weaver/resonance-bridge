import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

// The Cloudflare line — read-only, sovereign. A window on the DNS ground for
// audhdities.com: token health, zones, DNS records, TLS/HTTPS settings,
// email routing, and rulesets/page rules. GET requests only; DNS writes
// (create/update/delete records) are hands, not windows, and stay unbuilt
// until KP gates them on purpose. CLOUDFLARE_API_TOKEN is ACCOUNT-OWNED: it
// verifies at /accounts/{CLOUDFLARE_ACCOUNT_ID}/tokens/verify, not
// /user/tokens/verify — cloudflare_verify_token tries the account door
// first and only falls back to the user door. The token itself never
// crosses this line in any reply.

const API = "https://api.cloudflare.com/client/v4";

const NO_LINE =
  "The Cloudflare line is not connected. Add CLOUDFLARE_API_TOKEN to .env by " +
  "your own hands (Dashboard → Manage Account → API Tokens; scope it to " +
  "Zone.Zone:Read + Zone.DNS:Read), and CLOUDFLARE_ACCOUNT_ID beside it " +
  "(this token is account-owned), then restart the Bridge.";

// Cloudflare answers {success, errors, messages, result} on every call, and
// can say success:false even on a 200 (an invalid-token check, for one) —
// so both the HTTP status and the body's own success flag are checked here,
// once, for every tool below.
async function get(path: string, params: Record<string, string | undefined> = {}): Promise<any> {
  const url = new URL(API + path);
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== "") url.searchParams.set(k, v);
  }
  const res = await fetch(url, {
    headers: { Authorization: `Bearer ${process.env.CLOUDFLARE_API_TOKEN}` },
  });
  const body = await res.text();
  let data: any = null;
  try {
    data = JSON.parse(body);
  } catch {
    // non-JSON body — fall through, the slice below still reports it
  }
  if (!res.ok || !data?.success) {
    const detail = data?.errors?.length
      ? data.errors.map((e: any) => e.message).join("; ")
      : body.slice(0, 300);
    throw new Error(`Cloudflare ${res.status}: ${detail}`);
  }
  return data;
}

function asText(data: unknown) {
  return { content: [{ type: "text" as const, text: JSON.stringify(data, null, 2) }] };
}

function noLine() {
  return { content: [{ type: "text" as const, text: NO_LINE }] };
}

const ZONE = z
  .string()
  .describe("zone name (e.g. audhdities.com) or zone id from cloudflare_list_zones");

// Shared by tools 3-6: a zone argument may already be an id (32-char hex)
// or a name that needs one lookup to resolve.
async function resolveZoneId(zone: string): Promise<string> {
  if (/^[0-9a-f]{32}$/i.test(zone)) return zone;
  const data = await get("/zones", { name: zone });
  const found = data.result as Array<{ id: string }>;
  if (!found?.length) throw new Error(`Cloudflare: no zone found named "${zone}"`);
  return found[0].id;
}

const ZONE_SETTINGS = [
  "ssl",
  "always_use_https",
  "automatic_https_rewrites",
  "min_tls_version",
  "tls_1_3",
  "development_mode",
];

export function registerCloudflare(server: McpServer) {
  server.tool(
    "cloudflare_verify_token",
    "The token's own health — status and expiry, checked at the account endpoint first (this token is account-owned) and falling back to the user endpoint only if that fails. Never returns the token itself. Run this first, and whenever the line acts strange.",
    {},
    async () => {
      if (!process.env.CLOUDFLARE_API_TOKEN) return noLine();
      const shape = (r: any) => ({
        status: r.status,
        expires_on: r.expires_on ?? null,
        not_before: r.not_before ?? null,
        id: r.id,
      });
      const accountId = process.env.CLOUDFLARE_ACCOUNT_ID;
      if (accountId) {
        try {
          const data = await get(`/accounts/${accountId}/tokens/verify`);
          return asText(shape(data.result));
        } catch {
          // account door failed — fall through to the user door below
        }
      }
      try {
        const data = await get("/user/tokens/verify");
        return asText(shape(data.result));
      } catch (e) {
        return asText({
          error: (e as Error).message,
          note: accountId
            ? "Both the account and user verify endpoints failed."
            : "CLOUDFLARE_ACCOUNT_ID is not set, so only the user endpoint was tried — " +
              "and this token is account-owned, which fails there by design. " +
              "Add CLOUDFLARE_ACCOUNT_ID to .env for the correct check.",
        });
      }
    }
  );

  server.tool(
    "cloudflare_list_zones",
    "Every zone the token can see — name, id, status, paused, plan, Cloudflare nameservers, original nameservers, original registrar. Start here to discover the DNS ground.",
    {},
    async () => {
      if (!process.env.CLOUDFLARE_API_TOKEN) return noLine();
      const data = await get("/zones", { per_page: "50" });
      const zones = data.result as Array<Record<string, any>>;
      return asText(
        zones.map((z) => ({
          name: z.name,
          id: z.id,
          status: z.status,
          paused: z.paused,
          plan: z.plan?.name,
          name_servers: z.name_servers,
          original_name_servers: z.original_name_servers ?? null,
          original_registrar: z.original_registrar ?? null,
        }))
      );
    }
  );

  server.tool(
    "cloudflare_list_dns",
    "All DNS records for one zone, sorted by type then name — type, name, content, proxied, ttl ('auto' for 1), priority, comment. DNS is public ground; TXT contents may be returned whole.",
    { zone: ZONE },
    async ({ zone }) => {
      if (!process.env.CLOUDFLARE_API_TOKEN) return noLine();
      const zoneId = await resolveZoneId(zone);
      const data = await get(`/zones/${zoneId}/dns_records`, { per_page: "200" });
      const records = data.result as Array<Record<string, any>>;
      return asText(
        records
          .map((r) => ({
            type: r.type,
            name: r.name,
            content: r.content,
            proxied: r.proxied ?? false,
            ttl: r.ttl === 1 ? "auto" : r.ttl,
            priority: r.priority ?? null,
            comment: r.comment ?? null,
          }))
          .sort((a, b) => a.type.localeCompare(b.type) || a.name.localeCompare(b.name))
      );
    }
  );

  server.tool(
    "cloudflare_zone_settings",
    "One zone's TLS/HTTPS posture, read one setting at a time — ssl, always_use_https, automatic_https_rewrites, min_tls_version, tls_1_3, development_mode.",
    { zone: ZONE },
    async ({ zone }) => {
      if (!process.env.CLOUDFLARE_API_TOKEN) return noLine();
      const zoneId = await resolveZoneId(zone);
      const settings: Record<string, unknown> = {};
      for (const name of ZONE_SETTINGS) {
        try {
          const data = await get(`/zones/${zoneId}/settings/${name}`);
          settings[name] = data.result?.value;
        } catch (e) {
          settings[name] = `not readable: ${(e as Error).message}`;
        }
      }
      return asText(settings);
    }
  );

  server.tool(
    "cloudflare_email_routing",
    "One zone's email routing state — enabled, status.",
    { zone: ZONE },
    async ({ zone }) => {
      if (!process.env.CLOUDFLARE_API_TOKEN) return noLine();
      const zoneId = await resolveZoneId(zone);
      const data = await get(`/zones/${zoneId}/email/routing`);
      return asText({ enabled: data.result?.enabled, status: data.result?.status });
    }
  );

  server.tool(
    "cloudflare_list_rulesets",
    "One zone's rulesets — phase, name, kind — plus page rules if this token can read them. Many tokens can't (no permission); that comes back as an honest sentence, not a crash.",
    { zone: ZONE },
    async ({ zone }) => {
      if (!process.env.CLOUDFLARE_API_TOKEN) return noLine();
      const zoneId = await resolveZoneId(zone);
      const rulesetsData = await get(`/zones/${zoneId}/rulesets`);
      const rulesets = (rulesetsData.result as Array<Record<string, any>>).map((r) => ({
        phase: r.phase,
        name: r.name,
        kind: r.kind,
      }));
      let pageRules: unknown;
      try {
        const prData = await get(`/zones/${zoneId}/pagerules`);
        pageRules =
          prData.result === null
            ? "not readable with this token (no permission)"
            : (prData.result as Array<Record<string, any>>).map((p) => ({
                targets: p.targets,
                status: p.status,
                priority: p.priority,
              }));
      } catch (e) {
        pageRules = `not readable: ${(e as Error).message}`;
      }
      return asText({ rulesets, page_rules: pageRules });
    }
  );
}
