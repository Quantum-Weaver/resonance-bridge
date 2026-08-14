import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

// The Supabase line — read-only, sovereign, and the most warded line on the
// board: SUPABASE_ACCESS_TOKEN is account-wide, the most powerful Supabase
// key in the house, so every guard here is CODE, not convention. Built to
// the supabase-expert's commission (2026-07-31, carried by KP ⚛).
//
// This line is different ground from grammar.ts: that line reads the
// KNOWLEDGE base's CONTENT through the anon door; this one reads the
// DASHBOARD ITSELF through the Management API (api.supabase.com/v1).
//
// The wards, named:
// - supabase_select: the query endpoint is technically write-capable — the
//   SELECT-only guard in code is the whole covenant of the tool.
// - supabase_get_auth_config: the payload can carry smtp_pass and hook/JWT
//   secrets — an ALLOWLIST decides what survives; smtp_pass is reduced to
//   set: true/false; everything unlisted dies before serialization.
// - Cloudflare blocks odd User-Agents at api.supabase.com (BASE-ACCESS-GUIDE
//   lesson 5) — every Management call sends a real one.
// - Left unbuilt on purpose: anything that writes — SQL mutations, config
//   changes, key rotation, project create/pause. KP's dashboard hands, forever.

const API = "https://api.supabase.com/v1";
const UA = "resonance-bridge/0.2.0 (MCP server; read-only line)";

const NO_LINE =
  "The Supabase management line is not connected. Add SUPABASE_ACCESS_TOKEN " +
  "to .env by your own hands (supabase.com → Account → Access Tokens), then " +
  "restart the Bridge.";

async function mgmtGet(path: string): Promise<any> {
  const res = await fetch(API + path, {
    headers: {
      Authorization: `Bearer ${process.env.SUPABASE_ACCESS_TOKEN}`,
      "User-Agent": UA,
    },
  });
  if (!res.ok) {
    const body = (await res.text()).slice(0, 300);
    throw new Error(`Supabase management ${res.status}: ${body}`);
  }
  return res.json();
}

async function mgmtQuery(ref: string, query: string): Promise<any> {
  const res = await fetch(`${API}/projects/${ref}/database/query`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${process.env.SUPABASE_ACCESS_TOKEN}`,
      "User-Agent": UA,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ query }),
  });
  if (!res.ok) {
    const body = (await res.text()).slice(0, 300);
    throw new Error(`Supabase query ${res.status}: ${body}`);
  }
  return res.json();
}

function asText(data: unknown) {
  return { content: [{ type: "text" as const, text: JSON.stringify(data, null, 2) }] };
}

function noLine() {
  return { content: [{ type: "text" as const, text: NO_LINE }] };
}

// The SELECT-only guard — the covenant of supabase_select, held in code.
const FORBIDDEN =
  /\b(insert|update|delete|drop|alter|create|truncate|grant|revoke|comment|vacuum|copy|call|merge|do|execute|prepare|deallocate|set|reset|refresh|reindex|cluster|lock|listen|notify|security|import)\b/i;

function selectGuard(sql: string): string | null {
  const q = sql.trim().replace(/;+\s*$/, "");
  if (q.includes(";")) return "one statement only — semicolons are refused";
  if (!/^(select|with)\b/i.test(q)) return "the statement must begin with SELECT or WITH";
  if (FORBIDDEN.test(q)) {
    return "a data-modifying or session keyword was found — this tool is SELECT-only by covenant";
  }
  return null;
}

const ROW_CAP = 200;

const REF = z.string().describe("project ref from supabase_list_projects");

export function registerSupabase(server: McpServer) {
  server.tool(
    "supabase_list_projects",
    "Every Supabase project the account holds — name, ref, region, STATUS (the free-tier pause-watch: ACTIVE_HEALTHY vs PAUSED), created date. The project shelf; run this first.",
    {},
    async () => {
      if (!process.env.SUPABASE_ACCESS_TOKEN) return noLine();
      const projects = (await mgmtGet("/projects")) as any[];
      return asText(
        projects.map((p) => ({
          name: p.name,
          ref: p.id,
          region: p.region,
          status: p.status,
          created_at: p.created_at,
        }))
      );
    }
  );

  server.tool(
    "supabase_get_auth_config",
    "One project's auth configuration through an ALLOWLIST — SMTP host/port/user/sender (password reduced to set:true/false), site URL, autoconfirm flags, password minimum, enabled external providers, hook URIs (secrets stripped). Answers 'is the Resend SMTP wire live?' without a dashboard walk.",
    { ref: REF },
    async ({ ref }) => {
      if (!process.env.SUPABASE_ACCESS_TOKEN) return noLine();
      const cfg = (await mgmtGet(`/projects/${ref}/config/auth`)) as Record<string, any>;
      // The allowlist ward: only what is named here survives.
      const providers = Object.entries(cfg)
        .filter(([k, v]) => /^external_.*_enabled$/i.test(k) && v === true)
        .map(([k]) => k.replace(/^external_/i, "").replace(/_enabled$/i, ""));
      const hooks = Object.entries(cfg)
        .filter(([k, v]) => /^hook_.*_(uri|enabled)$/i.test(k) && v !== null && v !== false && v !== "")
        .map(([k, v]) => ({ [k]: v }));
      return asText({
        site_url: cfg.site_url ?? null,
        smtp: {
          host: cfg.smtp_host ?? null,
          port: cfg.smtp_port ?? null,
          user: cfg.smtp_user ?? null,
          sender_name: cfg.smtp_sender_name ?? null,
          admin_email: cfg.smtp_admin_email ?? null,
          pass: { set: Boolean(cfg.smtp_pass) },
        },
        mailer_autoconfirm: cfg.mailer_autoconfirm ?? null,
        password_min_length: cfg.password_min_length ?? null,
        external_providers_enabled: providers,
        hooks_configured: hooks,
      });
    }
  );

  server.tool(
    "supabase_select",
    "Run ONE read-only SQL statement against a project's live database — SELECT/WITH only, enforced in code (data-modifying keywords refused, single statement, results capped at 200 rows). The house's 'probe the living base before any SQL claim' law, made an instrument.",
    {
      ref: REF,
      query: z.string().describe("a single SELECT (or WITH…SELECT) statement"),
    },
    async ({ ref, query }) => {
      if (!process.env.SUPABASE_ACCESS_TOKEN) return noLine();
      const refusal = selectGuard(query);
      if (refusal) return asText(`refused by the SELECT-only covenant: ${refusal}`);
      const rows = (await mgmtQuery(ref, query)) as any[];
      const capped = Array.isArray(rows) ? rows.slice(0, ROW_CAP) : rows;
      return asText({
        rows: capped,
        row_count: Array.isArray(rows) ? rows.length : undefined,
        truncated: Array.isArray(rows) && rows.length > ROW_CAP ? `capped at ${ROW_CAP}` : false,
      });
    }
  );

  server.tool(
    "supabase_list_tables",
    "Every table in a project's public-facing schemas with its RLS flag and policy count — THE FALSE-EMPTY DETECTOR: rls_enabled with zero policies is the []-that-lies, visible at a glance across all rooms.",
    { ref: REF },
    async ({ ref }) => {
      if (!process.env.SUPABASE_ACCESS_TOKEN) return noLine();
      const sql = `
        SELECT n.nspname AS schema, c.relname AS table,
               c.relrowsecurity AS rls_enabled,
               count(p.polname)::int AS policy_count
        FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        LEFT JOIN pg_policy p ON p.polrelid = c.oid
        WHERE c.relkind = 'r'
          AND n.nspname NOT IN ('pg_catalog','information_schema','extensions',
            'auth','storage','vault','realtime','supabase_functions','graphql',
            'graphql_public','pgsodium','pgsodium_masks','net','supabase_migrations')
        GROUP BY 1, 2, c.relrowsecurity
        ORDER BY 1, 2`;
      const rows = (await mgmtQuery(ref, sql)) as any[];
      return asText({
        tables: rows.map((r) => ({
          ...r,
          false_empty_risk: r.rls_enabled === true && Number(r.policy_count) === 0,
        })),
        table_count: rows.length,
        false_empty_count: rows.filter(
          (r) => r.rls_enabled === true && Number(r.policy_count) === 0
        ).length,
      });
    }
  );

  server.tool(
    "supabase_get_advisors",
    "The project's advisor lamps — security and performance lints by name and level. (House context rides along: the leaked-password-protection amber is ruled upsell here; don't re-alarm at it.) Degrades gracefully if the endpoint is not on this API surface yet.",
    { ref: REF },
    async ({ ref }) => {
      if (!process.env.SUPABASE_ACCESS_TOKEN) return noLine();
      async function advisors(kind: string) {
        try {
          const a = (await mgmtGet(`/projects/${ref}/advisors/${kind}`)) as any;
          const lints = a.lints ?? a;
          return Array.isArray(lints)
            ? lints.map((l: any) => ({
                name: l.name ?? l.title,
                title: l.title ?? null,
                level: l.level ?? l.severity ?? null,
              }))
            : lints;
        } catch (e) {
          return `endpoint not available (${(e as Error).message.slice(0, 60)})`;
        }
      }
      return asText({
        security: await advisors("security"),
        performance: await advisors("performance"),
      });
    }
  );

  server.tool(
    "supabase_list_functions",
    "The project's edge-function census — expected empty today; the map wants the emptiness VERIFIED, not presumed.",
    { ref: REF },
    async ({ ref }) => {
      if (!process.env.SUPABASE_ACCESS_TOKEN) return noLine();
      const fns = (await mgmtGet(`/projects/${ref}/functions`)) as any[];
      return asText({
        functions: fns.map((f) => ({
          slug: f.slug,
          name: f.name,
          status: f.status,
          created_at: f.created_at,
        })),
        count: fns.length,
      });
    }
  );

  server.tool(
    "supabase_list_buckets",
    "One base's storage-bucket census (expected empty; verified, not presumed) — name, public flag, created. Walks the base's own storage door with its secret key, both headers per the BASE-ACCESS-GUIDE.",
    { base: z.enum(["KNOWLEDGE", "SUPERPOSITION"]).describe("which base's storage to census") },
    async ({ base }) => {
      const url = process.env[`SUPABASE_URL_${base}`];
      const key = process.env[`SUPABASE_SECRET_KEY_${base}`];
      if (!url || !key) {
        return asText(
          `The ${base} storage door is not connected — SUPABASE_URL_${base} and ` +
            `SUPABASE_SECRET_KEY_${base} belong on the ring by KP's hands.`
        );
      }
      const res = await fetch(`${url}/storage/v1/bucket`, {
        headers: { apikey: key, Authorization: `Bearer ${key}` },
      });
      if (!res.ok) {
        const body = (await res.text()).slice(0, 200);
        throw new Error(`Supabase storage ${res.status}: ${body}`);
      }
      const buckets = (await res.json()) as any[];
      return asText({
        base,
        buckets: buckets.map((b) => ({ name: b.name, public: b.public, created_at: b.created_at })),
        count: buckets.length,
      });
    }
  );
}
