import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

// The Vercel line — read-only, sovereign. A window on the hosting: projects,
// deployments, domains, and env-var NAMES. The keys-map law rides this file:
// key/env CONTENTS never cross this line — vercel_list_env_names strips
// values in code before anything reaches a reply. GET requests only; deploy
// triggers and env writes are hands, not windows, and stay unbuilt until
// KP gates them on purpose. VERCEL_TOKEN's first consumer (keys-map §keyring).

const API = "https://api.vercel.com";

const NO_LINE =
  "The Vercel line is not connected. Add VERCEL_TOKEN to .env by your own " +
  "hands (Account Settings → Tokens; scope it and set an expiry), then " +
  "restart the Bridge.";

async function vercelGet(
  path: string,
  params: Record<string, string | undefined> = {}
): Promise<unknown> {
  const url = new URL(API + path);
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== "") url.searchParams.set(k, v);
  }
  const res = await fetch(url, {
    headers: { Authorization: `Bearer ${process.env.VERCEL_TOKEN}` },
  });
  if (!res.ok) {
    const body = (await res.text()).slice(0, 300);
    throw new Error(`Vercel ${res.status}: ${body}`);
  }
  return res.json();
}

function asText(data: unknown) {
  return { content: [{ type: "text" as const, text: JSON.stringify(data, null, 2) }] };
}

function noLine() {
  return { content: [{ type: "text" as const, text: NO_LINE }] };
}

export function registerVercel(server: McpServer) {
  server.tool(
    "vercel_list_projects",
    "List every Vercel project the token can see — name, id, framework, node version, latest production deployment state and URL. Start here to discover the hosting.",
    {},
    async () => {
      if (!process.env.VERCEL_TOKEN) return noLine();
      const data = (await vercelGet("/v10/projects", { limit: "100" })) as {
        projects: Array<Record<string, any>>;
      };
      return asText(
        data.projects.map((p) => ({
          name: p.name,
          id: p.id,
          framework: p.framework,
          nodeVersion: p.nodeVersion,
          updatedAt: p.updatedAt ? new Date(p.updatedAt).toISOString() : undefined,
          latestProduction: p.targets?.production
            ? {
                state: p.targets.production.readyState,
                url: p.targets.production.url,
                createdAt: p.targets.production.createdAt
                  ? new Date(p.targets.production.createdAt).toISOString()
                  : undefined,
              }
            : null,
        }))
      );
    }
  );

  server.tool(
    "vercel_list_deployments",
    "List recent deployments — state (READY/ERROR/BUILDING/CANCELED), target (production/preview), URL, branch and commit message, created time. Optionally scoped to one project.",
    {
      project: z.string().optional().describe("project id or name from vercel_list_projects"),
      limit: z.number().min(1).max(50).optional().describe("max deployments, default 10"),
      target: z.string().optional().describe("optional filter: production | preview"),
    },
    async ({ project, limit, target }) => {
      if (!process.env.VERCEL_TOKEN) return noLine();
      const data = (await vercelGet("/v6/deployments", {
        app: project,
        limit: String(limit ?? 10),
        target,
      })) as { deployments: Array<Record<string, any>> };
      return asText(
        data.deployments.map((d) => ({
          state: d.readyState ?? d.state,
          target: d.target,
          url: d.url,
          project: d.name,
          branch: d.meta?.githubCommitRef,
          commit: d.meta?.githubCommitMessage?.slice(0, 80),
          created: d.createdAt ? new Date(d.createdAt).toISOString() : undefined,
          uid: d.uid,
        }))
      );
    }
  );

  server.tool(
    "vercel_list_domains",
    "List the domains Vercel knows for one project — name, verification state, redirect target if any. The DNS ground truth from the hosting's side.",
    { project: z.string().describe("project id or name from vercel_list_projects") },
    async ({ project }) => {
      if (!process.env.VERCEL_TOKEN) return noLine();
      const data = (await vercelGet(`/v9/projects/${encodeURIComponent(project)}/domains`)) as {
        domains: Array<Record<string, any>>;
      };
      return asText(
        data.domains.map((d) => ({
          name: d.name,
          verified: d.verified,
          redirect: d.redirect ?? null,
          gitBranch: d.gitBranch ?? null,
          createdAt: d.createdAt ? new Date(d.createdAt).toISOString() : undefined,
        }))
      );
    }
  );

  server.tool(
    "vercel_list_env_names",
    "List a project's environment-variable NAMES with their targets (production/preview/development) and types — VALUES ARE STRIPPED IN CODE AND NEVER RETURNED. This is the keys-map's names-only census, done through the API instead of a dashboard walk.",
    { project: z.string().describe("project id or name from vercel_list_projects") },
    async ({ project }) => {
      if (!process.env.VERCEL_TOKEN) return noLine();
      const data = (await vercelGet(`/v10/projects/${encodeURIComponent(project)}/env`)) as {
        envs: Array<Record<string, any>>;
      };
      // The ward: only these fields survive. `value` (and anything else the
      // API sends) dies here, before serialization.
      return asText(
        data.envs.map((e) => ({
          key: e.key,
          target: e.target,
          type: e.type,
          gitBranch: e.gitBranch ?? null,
          updatedAt: e.updatedAt ? new Date(e.updatedAt).toISOString() : undefined,
        }))
      );
    }
  );
}
