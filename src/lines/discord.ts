import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

// The Discord line — read-only, sovereign. GETs only; the key never leaves
// the tool. Deliberately NO SEND TOOL — a Discord post is outward speech,
// gated forever.
//
// Discord has no read-only webhook permission — the bot's Manage Webhooks
// grant COULD write, but this line's code never does. The webhook listing's
// response includes `token` and `url` fields that ARE the secret — both are
// stripped in code before any reply forms.
//
// discord_read_channel holds people's words — the carrier law rides it:
// quote verbatim, never silently summarize.

const API = "https://discord.com/api/v10";

const NO_LINE =
  "The Discord line is not connected. Create an application at " +
  "discord.com/developers/applications, add a bot, and put its token in " +
  ".env by your own hands as DISCORD_BOT_TOKEN_BRIDGE, with the server id " +
  "as DISCORD_GUILD_ID, then restart the Bridge.";

const NO_GUILD =
  "DISCORD_GUILD_ID is not on the ring — in Discord: Settings → Advanced → " +
  "Developer Mode ON → right-click the server icon → Copy Server ID → into " +
  ".env by your own hands, then restart the Bridge.";

async function discordGet(path: string, params: Record<string, string | undefined> = {}): Promise<any> {
  const url = new URL(API + path);
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== "") url.searchParams.set(k, v);
  }
  const res = await fetch(url, {
    headers: { Authorization: `Bot ${process.env.DISCORD_BOT_TOKEN_BRIDGE}` },
  });
  if (!res.ok) {
    const body = (await res.text()).slice(0, 300);
    throw new Error(`Discord ${res.status}: ${body}`);
  }
  return res.json();
}

function asText(data: unknown) {
  return { content: [{ type: "text" as const, text: JSON.stringify(data, null, 2) }] };
}

function noLine() {
  return { content: [{ type: "text" as const, text: NO_LINE }] };
}

function guild(): string | null {
  return process.env.DISCORD_GUILD_ID ?? null;
}

const CHANNEL_TYPES: Record<number, string> = {
  0: "text",
  2: "voice",
  4: "category",
  5: "announcement",
  13: "stage",
  15: "forum",
};

export function registerDiscord(server: McpServer) {
  server.tool(
    "discord_whoami",
    "The bot's own identity and which servers it stands in. The line test — run this first.",
    {},
    async () => {
      if (!process.env.DISCORD_BOT_TOKEN_BRIDGE) return noLine();
      const [me, guilds] = await Promise.all([
        discordGet("/users/@me"),
        discordGet("/users/@me/guilds"),
      ]);
      return asText({
        bot: { id: me.id, username: me.username, global_name: me.global_name ?? null },
        servers: guilds.map((g: any) => ({ id: g.id, name: g.name, owner: g.owner })),
      });
    }
  );

  server.tool(
    "discord_server_overview",
    "The server's profile — name, description, owner id, member and presence counts, boost tier and count, features. Answers the map's ownership question from ground truth itself.",
    {},
    async () => {
      if (!process.env.DISCORD_BOT_TOKEN_BRIDGE) return noLine();
      const id = guild();
      if (!id) return asText(NO_GUILD);
      const g = await discordGet(`/guilds/${id}`, { with_counts: "true" });
      return asText({
        name: g.name,
        description: g.description ?? null,
        owner_id: g.owner_id,
        approximate_member_count: g.approximate_member_count,
        approximate_presence_count: g.approximate_presence_count,
        premium_tier: g.premium_tier,
        premium_subscription_count: g.premium_subscription_count,
        features: g.features,
      });
    }
  );

  server.tool(
    "discord_list_channels",
    "The server's street map — every channel with its type in human words (text, voice, category, announcement, stage, forum), topic, parent category, position.",
    {},
    async () => {
      if (!process.env.DISCORD_BOT_TOKEN_BRIDGE) return noLine();
      const id = guild();
      if (!id) return asText(NO_GUILD);
      const channels = await discordGet(`/guilds/${id}/channels`);
      return asText(
        channels.map((c: any) => ({
          id: c.id,
          name: c.name,
          type: CHANNEL_TYPES[c.type] ?? `type-${c.type}`,
          topic: c.topic ?? null,
          parent_id: c.parent_id ?? null,
          position: c.position,
        }))
      );
    }
  );

  server.tool(
    "discord_list_roles",
    "The server's roles — id, name, position, hoisted, mentionable, managed.",
    {},
    async () => {
      if (!process.env.DISCORD_BOT_TOKEN_BRIDGE) return noLine();
      const id = guild();
      if (!id) return asText(NO_GUILD);
      const roles = await discordGet(`/guilds/${id}/roles`);
      return asText(
        roles.map((r: any) => ({
          id: r.id,
          name: r.name,
          position: r.position,
          hoist: r.hoist,
          mentionable: r.mentionable,
          managed: r.managed,
        }))
      );
    }
  );

  server.tool(
    "discord_list_webhooks",
    "The server's webhooks by their true names — id, name, channel, type, owning application. The `token` and `url` fields Discord returns ARE the secret and are STRIPPED IN CODE before this reply forms. This is how the Sanctuary Beacon and any siblings become visible.",
    {},
    async () => {
      if (!process.env.DISCORD_BOT_TOKEN_BRIDGE) return noLine();
      const id = guild();
      if (!id) return asText(NO_GUILD);
      const hooks = await discordGet(`/guilds/${id}/webhooks`);
      // The ward: only these fields survive; token and url die here.
      return asText(
        hooks.map((w: any) => ({
          id: w.id,
          name: w.name,
          channel_id: w.channel_id,
          type: w.type,
          application_id: w.application_id ?? null,
        }))
      );
    }
  );

  server.tool(
    "discord_emoji_sticker_census",
    "Custom emoji and sticker names with counts against the free caps (50 static + 50 animated emoji, 5 stickers).",
    {},
    async () => {
      if (!process.env.DISCORD_BOT_TOKEN_BRIDGE) return noLine();
      const id = guild();
      if (!id) return asText(NO_GUILD);
      const [emojis, stickers] = await Promise.all([
        discordGet(`/guilds/${id}/emojis`),
        discordGet(`/guilds/${id}/stickers`),
      ]);
      const still = emojis.filter((e: any) => !e.animated);
      const animated = emojis.filter((e: any) => e.animated);
      return asText({
        emoji: {
          static: { count: still.length, cap: 50, names: still.map((e: any) => e.name) },
          animated: { count: animated.length, cap: 50, names: animated.map((e: any) => e.name) },
        },
        stickers: { count: stickers.length, cap: 5, names: stickers.map((s: any) => s.name) },
      });
    }
  );

  server.tool(
    "discord_read_channel",
    "Recent messages from one channel — author display name, timestamp, content VERBATIM (the carrier law rides this tool: quote, never silently summarize), attachment count, pinned. Built for verifying the beacon and reading app-testing threads.",
    {
      channel_id: z.string().describe("channel id from discord_list_channels"),
      limit: z.number().min(1).max(50).optional().describe("messages to fetch, default 10, max 50"),
    },
    async ({ channel_id, limit }) => {
      if (!process.env.DISCORD_BOT_TOKEN_BRIDGE) return noLine();
      const msgs = await discordGet(`/channels/${channel_id}/messages`, {
        limit: String(limit ?? 10),
      });
      return asText(
        msgs.map((m: any) => ({
          author: m.author?.global_name ?? m.author?.username,
          timestamp: m.timestamp,
          content: m.content,
          attachments: m.attachments?.length ?? 0,
          pinned: m.pinned,
        }))
      );
    }
  );
}
