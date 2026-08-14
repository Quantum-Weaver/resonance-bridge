import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

// The Airtable line — read-only, sovereign. Serves KP's own bases: the
// earlier attempts at organizing the chaos, the song portfolio, the music
// column's photography. GET requests only; the ward is code.

const API = "https://api.airtable.com/v0";

const NO_LINE =
  "The Airtable line is not connected. Add AIRTABLE_API_KEY to .env by your " +
  "own hands (see .env.example — read-only scopes only), then restart the Bridge.";

async function airtableGet(
  path: string,
  params: Record<string, string | undefined> = {}
): Promise<unknown> {
  const url = new URL(API + path);
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== "") url.searchParams.set(k, v);
  }
  const res = await fetch(url, {
    headers: { Authorization: `Bearer ${process.env.AIRTABLE_API_KEY}` },
  });
  if (!res.ok) {
    const body = (await res.text()).slice(0, 300);
    throw new Error(`Airtable ${res.status}: ${body}`);
  }
  return res.json();
}

function asText(data: unknown) {
  return { content: [{ type: "text" as const, text: JSON.stringify(data, null, 2) }] };
}

function noLine() {
  return { content: [{ type: "text" as const, text: NO_LINE }] };
}

export function registerAirtable(server: McpServer) {
  server.tool(
    "airtable_list_bases",
    "List every Airtable base the Bridge's token can see — id, name, permission level. Start here to discover KP's prior organization attempts.",
    {},
    async () => {
      if (!process.env.AIRTABLE_API_KEY) return noLine();
      const bases: unknown[] = [];
      let offset: string | undefined;
      do {
        const page = (await airtableGet("/meta/bases", { offset })) as {
          bases: unknown[];
          offset?: string;
        };
        bases.push(...page.bases);
        offset = page.offset;
      } while (offset);
      return asText(bases);
    }
  );

  server.tool(
    "airtable_list_tables",
    "List a base's tables with their fields and views — the schema of one organization attempt. Call airtable_list_bases first for base ids.",
    { baseId: z.string().describe("base id, e.g. 'appXXXXXXXXXXXXXX'") },
    async ({ baseId }) => {
      if (!process.env.AIRTABLE_API_KEY) return noLine();
      return asText(await airtableGet(`/meta/bases/${baseId}/tables`));
    }
  );

  server.tool(
    "airtable_query_records",
    "Read records from one table (read-only). Returns a page plus an offset token for the next page. Supports Airtable filterByFormula and named views.",
    {
      baseId: z.string().describe("base id from airtable_list_bases"),
      table: z.string().describe("table id or exact table name"),
      pageSize: z.number().min(1).max(100).optional()
        .describe("records per page, default 20, max 100"),
      view: z.string().optional().describe("optional view name — inherits its filters/sort"),
      filterByFormula: z.string().optional()
        .describe("optional Airtable formula, e.g. \"{Status}='Published'\""),
      offset: z.string().optional().describe("offset token from a previous page"),
    },
    async ({ baseId, table, pageSize, view, filterByFormula, offset }) => {
      if (!process.env.AIRTABLE_API_KEY) return noLine();
      return asText(
        await airtableGet(`/${baseId}/${encodeURIComponent(table)}`, {
          pageSize: String(pageSize ?? 20),
          view,
          filterByFormula,
          offset,
        })
      );
    }
  );
}
