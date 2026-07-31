import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

// The Stripe line — read-only, sovereign, LIVE-MODE: STRIPE_RESTRICTED_KEY is
// a live restricted key (stripe-expert's probe, 2026-07-31: every read door
// opens; writes untested and unwanted). Built to the stripe-expert's
// commission, same covenant as vercel.ts — GET only, the key sourced from
// the ring and never echoed, writes unbuilt until KP gates them on purpose.
//
// Two commission laws enforced in code:
// 1. A 403 from Stripe means the restricted key lacks that read scope — the
//    tool reports "scope not granted" as a FINDING, never a crash.
// 2. stripe_list_customers carries a privacy stripe: counts, ids, and created
//    dates only — emails and names are stripped in code before anything
//    reaches a reply, same as the env-value stripping in the Vercel line.

const API = "https://api.stripe.com/v1";

const NO_LINE =
  "The Stripe line is not connected. Add STRIPE_RESTRICTED_KEY to .env by " +
  "your own hands (Stripe dashboard → Developers → API keys → restricted, " +
  "read-only scopes), then restart the Bridge.";

class StripeHttpError extends Error {
  status: number;
  constructor(status: number, body: string) {
    super(`Stripe ${status}: ${body}`);
    this.status = status;
  }
}

async function stripeGet(
  path: string,
  params: Record<string, string | undefined> = {}
): Promise<any> {
  const url = new URL(API + path);
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== "") url.searchParams.set(k, v);
  }
  const res = await fetch(url, {
    headers: { Authorization: `Bearer ${process.env.STRIPE_RESTRICTED_KEY}` },
  });
  if (!res.ok) throw new StripeHttpError(res.status, (await res.text()).slice(0, 300));
  return res.json();
}

function asText(data: unknown) {
  return { content: [{ type: "text" as const, text: JSON.stringify(data, null, 2) }] };
}

function noLine() {
  return { content: [{ type: "text" as const, text: NO_LINE }] };
}

// Commission law 1: a 403 is a finding about the key's scopes, not a failure.
async function scoped(fn: () => Promise<{ content: any }>) {
  try {
    return await fn();
  } catch (e) {
    if (e instanceof StripeHttpError && e.status === 403) {
      return asText(
        "scope not granted on the restricted key — a finding, not a failure. " +
          "If this door is wanted, the key is re-cut with the read scope at " +
          "KP's dashboard, his hands."
      );
    }
    throw e;
  }
}

function money(amount: number | null, currency?: string) {
  return amount == null ? null : `${(amount / 100).toFixed(2)} ${currency ?? ""}`.trim();
}

function when(unix?: number) {
  return unix ? new Date(unix * 1000).toISOString() : undefined;
}

const LIMIT = z.number().min(1).max(100).optional().describe("max rows, default 10");

export function registerStripe(server: McpServer) {
  server.tool(
    "stripe_account",
    "The merchant account's own profile — business name, type and structure, charges/payouts enabled, country, currency, and which mode the key serves. Answers 'where does the account stand' by machine, forever.",
    {},
    async () => {
      if (!process.env.STRIPE_RESTRICTED_KEY) return noLine();
      return scoped(async () => {
        const a = await stripeGet("/account");
        return asText({
          business_name: a.business_profile?.name ?? a.settings?.dashboard?.display_name,
          business_type: a.business_type,
          structure: a.company?.structure ?? null,
          charges_enabled: a.charges_enabled,
          payouts_enabled: a.payouts_enabled,
          details_submitted: a.details_submitted,
          country: a.country,
          default_currency: a.default_currency,
        });
      });
    }
  );

  server.tool(
    "stripe_list_webhook_endpoints",
    "Webhook endpoints registered with Stripe — url, status, enabled events. H1's registration state made visible; Stripe never returns signing secrets here, the keys law enforced by the API itself.",
    {},
    async () => {
      if (!process.env.STRIPE_RESTRICTED_KEY) return noLine();
      return scoped(async () => {
        const r = await stripeGet("/webhook_endpoints");
        return asText({
          webhook_endpoints: r.data.map((w: any) => ({
            id: w.id,
            url: w.url,
            status: w.status,
            enabled_events: w.enabled_events,
          })),
          count: r.data.length,
        });
      });
    }
  );

  server.tool(
    "stripe_list_products",
    "The shop's shelves — products with id, name, active state, description, default price id.",
    { limit: LIMIT, active: z.boolean().optional().describe("filter to active products only") },
    async ({ limit, active }) => {
      if (!process.env.STRIPE_RESTRICTED_KEY) return noLine();
      return scoped(async () => {
        const r = await stripeGet("/products", {
          limit: String(limit ?? 10),
          active: active === undefined ? undefined : String(active),
        });
        return asText({
          products: r.data.map((p: any) => ({
            id: p.id,
            name: p.name,
            active: p.active,
            description: p.description?.slice(0, 120) ?? null,
            default_price: p.default_price ?? null,
          })),
          has_more: r.has_more,
        });
      });
    }
  );

  server.tool(
    "stripe_list_prices",
    "Prices — amount, currency, one-time vs recurring, parent product, active state. Products and prices together are the solidarity-pricing surface.",
    { limit: LIMIT, product: z.string().optional().describe("optional product id to scope to") },
    async ({ limit, product }) => {
      if (!process.env.STRIPE_RESTRICTED_KEY) return noLine();
      return scoped(async () => {
        const r = await stripeGet("/prices", { limit: String(limit ?? 10), product });
        return asText({
          prices: r.data.map((p: any) => ({
            id: p.id,
            product: p.product,
            amount: money(p.unit_amount, p.currency),
            recurring: p.recurring?.interval ?? null,
            nickname: p.nickname ?? null,
            active: p.active,
          })),
          has_more: r.has_more,
        });
      });
    }
  );

  server.tool(
    "stripe_list_payment_links",
    "Payment links — the no-code sellable URLs, with active state.",
    { limit: LIMIT, active: z.boolean().optional().describe("filter to active links only") },
    async ({ limit, active }) => {
      if (!process.env.STRIPE_RESTRICTED_KEY) return noLine();
      return scoped(async () => {
        const r = await stripeGet("/payment_links", {
          limit: String(limit ?? 10),
          active: active === undefined ? undefined : String(active),
        });
        return asText({
          payment_links: r.data.map((l: any) => ({ id: l.id, url: l.url, active: l.active })),
          has_more: r.has_more,
        });
      });
    }
  );

  server.tool(
    "stripe_list_checkout_sessions",
    "Checkout sessions — status, payment status, mode, amount, created time. The sandbox rehearsal becomes visible here.",
    { limit: LIMIT },
    async ({ limit }) => {
      if (!process.env.STRIPE_RESTRICTED_KEY) return noLine();
      return scoped(async () => {
        const r = await stripeGet("/checkout/sessions", { limit: String(limit ?? 10) });
        return asText({
          sessions: r.data.map((s: any) => ({
            id: s.id,
            status: s.status,
            payment_status: s.payment_status,
            mode: s.mode,
            amount_total: money(s.amount_total, s.currency),
            created: when(s.created),
          })),
          has_more: r.has_more,
        });
      });
    }
  );

  server.tool(
    "stripe_list_events",
    "The account's own audit trail — event type and time, newest first, including webhook delivery attempts. The single best debugging window. Optionally filtered by type (e.g. 'checkout.session.completed').",
    { limit: LIMIT, type: z.string().optional().describe("optional event type filter") },
    async ({ limit, type }) => {
      if (!process.env.STRIPE_RESTRICTED_KEY) return noLine();
      return scoped(async () => {
        const r = await stripeGet("/events", { limit: String(limit ?? 10), type });
        return asText({
          events: r.data.map((e: any) => ({ id: e.id, type: e.type, created: when(e.created) })),
          has_more: r.has_more,
        });
      });
    }
  );

  server.tool(
    "stripe_balance",
    "The account balance — available vs pending by currency. The payout story once money moves.",
    {},
    async () => {
      if (!process.env.STRIPE_RESTRICTED_KEY) return noLine();
      return scoped(async () => {
        const b = await stripeGet("/balance");
        return asText({
          available: b.available?.map((x: any) => money(x.amount, x.currency)),
          pending: b.pending?.map((x: any) => money(x.amount, x.currency)),
        });
      });
    }
  );

  server.tool(
    "stripe_list_charges",
    "Charges — amount, status, paid, created. Empty today; becomes the reconciliation window later.",
    { limit: LIMIT },
    async ({ limit }) => {
      if (!process.env.STRIPE_RESTRICTED_KEY) return noLine();
      return scoped(async () => {
        const r = await stripeGet("/charges", { limit: String(limit ?? 10) });
        return asText({
          charges: r.data.map((c: any) => ({
            id: c.id,
            amount: money(c.amount, c.currency),
            status: c.status,
            paid: c.paid,
            created: when(c.created),
          })),
          has_more: r.has_more,
        });
      });
    }
  );

  server.tool(
    "stripe_list_customers",
    "Customers — COUNT, ids, and created dates ONLY. The privacy stripe is code: names and emails are stripped before anything reaches a reply (commission law 2).",
    { limit: LIMIT },
    async ({ limit }) => {
      if (!process.env.STRIPE_RESTRICTED_KEY) return noLine();
      return scoped(async () => {
        const r = await stripeGet("/customers", { limit: String(limit ?? 10) });
        // The privacy stripe: only these fields survive; name/email die here.
        return asText({
          count: r.data.length,
          customers: r.data.map((c: any) => ({ id: c.id, created: when(c.created) })),
          has_more: r.has_more,
        });
      });
    }
  );
}
