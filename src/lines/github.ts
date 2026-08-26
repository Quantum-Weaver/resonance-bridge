import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

// The GitHub line — read-only, sovereign. Seven windows, GET only — issues,
// releases-as-writes, and dispatches stay unbuilt until KP gates them.
//
// The key is HOUSE_GITHUB_PAT: GitHub RESERVES the name GITHUB_TOKEN inside
// Actions, and many SDKs auto-read it from any environment — the house name
// means the key is consumed deliberately or not at all.
//
// Laws in code: webhook config URLs are redacted to scheme+host
// (a webhook URL can itself be a bearer secret — Discord's form); Actions
// secrets come back as NAMES only (GitHub's API never returns values — the
// law holds by construction); scope-blind sub-reads degrade to a plain
// sentence instead of hiding the rest.

const API = "https://api.github.com";

const NO_LINE =
  "The GitHub line is not connected. Mint a fine-grained PAT (GitHub → " +
  "Settings → Developer settings → Fine-grained tokens; scope it to the " +
  "house's repos, read permissions, 90-day expiry — and note the expiry " +
  "date somewhere your eye returns to), then add it to .env by your own " +
  "hands as HOUSE_GITHUB_PAT and restart the Bridge.";

function headers() {
  return {
    Authorization: `Bearer ${process.env.HOUSE_GITHUB_PAT}`,
    Accept: "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
  };
}

class GhError extends Error {
  status: number;
  constructor(status: number, body: string) {
    super(`GitHub ${status}: ${body}`);
    this.status = status;
  }
}

async function ghGet(path: string, params: Record<string, string | undefined> = {}): Promise<any> {
  const url = new URL(API + path);
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== "") url.searchParams.set(k, v);
  }
  const res = await fetch(url, { headers: headers() });
  if (!res.ok) throw new GhError(res.status, (await res.text()).slice(0, 200));
  return res.json();
}

// A sub-read that the token's scopes may not cover: degrade to a sentence,
// never an error that hides the rest.
async function sub(fn: () => Promise<unknown>): Promise<unknown> {
  try {
    return await fn();
  } catch (e) {
    if (e instanceof GhError && (e.status === 403 || e.status === 404)) {
      return "not visible to this token's scopes";
    }
    throw e;
  }
}

function asText(data: unknown) {
  return { content: [{ type: "text" as const, text: JSON.stringify(data, null, 2) }] };
}

function noLine() {
  return { content: [{ type: "text" as const, text: NO_LINE }] };
}

// Redact a webhook URL to scheme + host only — the path may be the secret.
function redactUrl(u?: string) {
  if (!u) return null;
  try {
    const p = new URL(u);
    return `${p.protocol}//${p.host}/… (path redacted — a webhook URL can be a bearer secret)`;
  } catch {
    return "(unparseable url, redacted whole)";
  }
}

const OWNER = z.string().optional().describe("repo owner, default 'Quantum-Weaver'");

export function registerGitHub(server: McpServer) {
  server.tool(
    "github_token_status",
    "The token's own health — which login it belongs to, its EXPIRY DATE (the F7 watch: a fine-grained PAT dies silently at 90 days), and rate-limit remaining. Run this first, and whenever the line acts strange.",
    {},
    async () => {
      if (!process.env.HOUSE_GITHUB_PAT) return noLine();
      const res = await fetch(API + "/user", { headers: headers() });
      if (!res.ok) throw new GhError(res.status, (await res.text()).slice(0, 200));
      const user = (await res.json()) as any;
      const expiry = res.headers.get("github-authentication-token-expiration");
      const rate = (await ghGet("/rate_limit")) as any;
      return asText({
        login: user.login,
        token_expires: expiry ?? "(no expiry header — classic PAT or no expiration set)",
        rate_limit_remaining: rate.resources?.core?.remaining,
        rate_limit_total: rate.resources?.core?.limit,
      });
    }
  );

  server.tool(
    "github_list_repos",
    "Every repo the token's login owns — name, VISIBILITY (the public/private census, the Free-plan question made visible), when it was born, default branch, archived, fork, last push, open issues. This is the census the reckoner reads for `is_public` on every sending, and the whole of what `repos_snapshot.json` holds.",
    {},
    async () => {
      if (!process.env.HOUSE_GITHUB_PAT) return noLine();
      // Paged: the house passed 30 repos in August and a single page silently
      // truncates at 100 — a census that stops short is worse than none.
      const repos: any[] = [];
      for (let page = 1; ; page++) {
        const batch = (await ghGet("/user/repos", {
          per_page: "100",
          affiliation: "owner",
          sort: "pushed",
          page: String(page),
        })) as any[];
        repos.push(...batch);
        if (batch.length < 100) break;
      }
      return asText(
        repos.map((r) => ({
          name: r.name,
          full_name: r.full_name,
          visibility: r.visibility,
          private: r.private,
          created_at: r.created_at,
          default_branch: r.default_branch,
          archived: r.archived,
          fork: r.fork,
          pushed_at: r.pushed_at,
          open_issues: r.open_issues_count,
        }))
      );
    }
  );

  server.tool(
    "github_repo_status",
    "One repo, deep — its profile, latest release, Pages state, and default-branch protection. Sub-reads the token can't see degrade to a plain sentence instead of failing the whole.",
    { owner: OWNER, repo: z.string().describe("repository name") },
    async ({ owner, repo }) => {
      if (!process.env.HOUSE_GITHUB_PAT) return noLine();
      const o = owner ?? "Quantum-Weaver";
      const r = (await ghGet(`/repos/${o}/${repo}`)) as any;
      const [latest_release, pages, protection] = await Promise.all([
        sub(async () => {
          const rel = (await ghGet(`/repos/${o}/${repo}/releases/latest`)) as any;
          return { tag: rel.tag_name, name: rel.name, published_at: rel.published_at };
        }),
        sub(async () => {
          const p = (await ghGet(`/repos/${o}/${repo}/pages`)) as any;
          return { status: p.status, url: p.html_url };
        }),
        sub(async () => {
          const b = (await ghGet(
            `/repos/${o}/${repo}/branches/${r.default_branch}/protection`
          )) as any;
          return { enforced: true, required_reviews: b.required_pull_request_reviews ? true : false };
        }),
      ]);
      return asText({
        name: r.full_name,
        visibility: r.visibility,
        default_branch: r.default_branch,
        archived: r.archived,
        pushed_at: r.pushed_at,
        open_issues: r.open_issues_count,
        latest_release,
        pages,
        default_branch_protection: protection,
      });
    }
  );

  server.tool(
    "github_list_actions",
    "One repo's Actions surface — workflow names and Actions-secret NAMES (values never exist in the API's answers). The ring-5 audit: today every repo should answer none · none.",
    { owner: OWNER, repo: z.string().describe("repository name") },
    async ({ owner, repo }) => {
      if (!process.env.HOUSE_GITHUB_PAT) return noLine();
      const o = owner ?? "Quantum-Weaver";
      const [workflows, secrets] = await Promise.all([
        sub(async () => {
          const w = (await ghGet(`/repos/${o}/${repo}/actions/workflows`)) as any;
          return w.workflows?.map((x: any) => ({ name: x.name, path: x.path, state: x.state })) ?? [];
        }),
        sub(async () => {
          const s = (await ghGet(`/repos/${o}/${repo}/actions/secrets`)) as any;
          return s.secrets?.map((x: any) => ({ name: x.name, updated_at: x.updated_at })) ?? [];
        }),
      ]);
      return asText({ workflows, secret_names: secrets });
    }
  );

  server.tool(
    "github_list_webhooks",
    "One repo's webhooks — events, active state, last-delivery status. URLs are REDACTED to scheme + host in code: a webhook URL can itself be a bearer secret.",
    { owner: OWNER, repo: z.string().describe("repository name") },
    async ({ owner, repo }) => {
      if (!process.env.HOUSE_GITHUB_PAT) return noLine();
      const o = owner ?? "Quantum-Weaver";
      const hooks = (await sub(async () => {
        const h = (await ghGet(`/repos/${o}/${repo}/hooks`)) as any[];
        return h.map((x: any) => ({
          id: x.id,
          url: redactUrl(x.config?.url),
          events: x.events,
          active: x.active,
          last_response: x.last_response?.status ?? null,
        }));
      })) as unknown;
      return asText({ webhooks: hooks });
    }
  );

  server.tool(
    "github_list_releases",
    "One repo's releases — tag, name, date, draft/prerelease, and each asset's name with its DOWNLOAD COUNT. The give-it-away shelf's window: who is receiving the gift.",
    { owner: OWNER, repo: z.string().describe("repository name") },
    async ({ owner, repo }) => {
      if (!process.env.HOUSE_GITHUB_PAT) return noLine();
      const o = owner ?? "Quantum-Weaver";
      const rels = (await ghGet(`/repos/${o}/${repo}/releases`, { per_page: "20" })) as any[];
      return asText(
        rels.map((r) => ({
          tag: r.tag_name,
          name: r.name,
          published_at: r.published_at,
          draft: r.draft,
          prerelease: r.prerelease,
          assets: r.assets?.map((a: any) => ({ name: a.name, downloads: a.download_count })) ?? [],
        }))
      );
    }
  );

  server.tool(
    "github_repo_traffic",
    "One repo's two-week traffic — views and clones with unique counts. Needs Administration read on the token; degrades to a plain sentence if ungranted.",
    { owner: OWNER, repo: z.string().describe("repository name") },
    async ({ owner, repo }) => {
      if (!process.env.HOUSE_GITHUB_PAT) return noLine();
      const o = owner ?? "Quantum-Weaver";
      const [views, clones] = await Promise.all([
        sub(() => ghGet(`/repos/${o}/${repo}/traffic/views`)),
        sub(() => ghGet(`/repos/${o}/${repo}/traffic/clones`)),
      ]);
      return asText({ views, clones });
    }
  );
}
