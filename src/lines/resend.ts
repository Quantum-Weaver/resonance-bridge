import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

// The Resend line — read-only, sovereign. Commissioned by the resend-expert
// (2026-07-31, via KP's ⚛ carried fetch) with its law stated in the
// commission itself: GETs only, the key never leaves the tool, and
// DELIBERATELY NO SEND TOOL — an email is outward speech; a send is a
// consent gate, never a convenience. If a send tool is ever wanted, it is
// its own commission with KP's word on it.
//
// Key: RESEND_KEY_BRIDGE_ADMIN (full access, minted for this consumer by
// KP's hands) — NOT RESEND_API_KEY, which is sending-only and stays that
// way; a sending-only key cannot read, and this line only reads.
//
// Honest note, per the commission's own ask: Resend's public API offers no
// LIST-sent-emails endpoint (only retrieve-by-id, GET /emails/:id) — send
// history is dashboard-only. The map should say so rather than guess; this
// comment is that plain saying. If Resend ships a list endpoint someday,
// `resend_list_emails` joins this file then.

const API = "https://api.resend.com";

const NO_LINE =
  "The Resend admin line is not connected. Mint a Full-access key in the " +
  "Resend dashboard (API Keys → Create) and add it to .env by your own " +
  "hands as RESEND_KEY_BRIDGE_ADMIN, then restart the Bridge. " +
  "(RESEND_API_KEY is sending-only and cannot read — it stays as it is.)";

async function resendGet(path: string): Promise<unknown> {
  const res = await fetch(API + path, {
    headers: { Authorization: `Bearer ${process.env.RESEND_KEY_BRIDGE_ADMIN}` },
  });
  if (!res.ok) {
    const body = (await res.text()).slice(0, 300);
    throw new Error(`Resend ${res.status}: ${body}`);
  }
  return res.json();
}

function asText(data: unknown) {
  return { content: [{ type: "text" as const, text: JSON.stringify(data, null, 2) }] };
}

function noLine() {
  return { content: [{ type: "text" as const, text: NO_LINE }] };
}

export function registerResend(server: McpServer) {
  server.tool(
    "resend_list_domains",
    "List the Resend sending domains — name, verification status, region, created date. The email house's ground truth: an unverified domain means no send can truly leave.",
    {},
    async () => {
      if (!process.env.RESEND_KEY_BRIDGE_ADMIN) return noLine();
      const data = (await resendGet("/domains")) as { data: Array<Record<string, any>> };
      return asText(
        data.data.map((d) => ({
          name: d.name,
          status: d.status,
          region: d.region,
          created_at: d.created_at,
        }))
      );
    }
  );

  server.tool(
    "resend_list_api_keys",
    "List the Resend API keys by NAME and creation date only — the API never returns key values, and this tool keeps it that way in its output too. The key census for the keys map.",
    {},
    async () => {
      if (!process.env.RESEND_KEY_BRIDGE_ADMIN) return noLine();
      const data = (await resendGet("/api-keys")) as { data: Array<Record<string, any>> };
      return asText(
        data.data.map((k) => ({ name: k.name, created_at: k.created_at }))
      );
    }
  );

  server.tool(
    "resend_list_audiences",
    "List the Resend audiences — id, name, created date. The consent-side inventory: who has said yes to hearing from the house.",
    {},
    async () => {
      if (!process.env.RESEND_KEY_BRIDGE_ADMIN) return noLine();
      const data = (await resendGet("/audiences")) as { data: Array<Record<string, any>> };
      return asText(
        data.data.map((a) => ({ id: a.id, name: a.name, created_at: a.created_at }))
      );
    }
  );

  server.tool(
    "resend_list_broadcasts",
    "List the Resend broadcasts — id, name, audience, status, created/sent dates. What the house has ever said to its audiences, as inventory.",
    {},
    async () => {
      if (!process.env.RESEND_KEY_BRIDGE_ADMIN) return noLine();
      const data = (await resendGet("/broadcasts")) as { data: Array<Record<string, any>> };
      return asText(
        data.data.map((b) => ({
          id: b.id,
          name: b.name,
          audience_id: b.audience_id,
          status: b.status,
          created_at: b.created_at,
          sent_at: b.sent_at ?? null,
        }))
      );
    }
  );
}
