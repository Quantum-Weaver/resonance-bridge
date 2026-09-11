# The channels census — 2026-09-10

## What stands

`src/census/testing_channels_census.ts`, run as
`npx tsx src/census/testing_channels_census.ts [--dry]`.

- The ring: `DISCORD_BOT_TOKEN_BRIDGE` and `DISCORD_GUILD_ID` from
  `process.env` at call time, the bridge's `.env` loaded by absolute path with
  `process.loadEnvFile` as `src/server.ts` and `src/http.ts` load it. An absent
  token or guild id answers one sentence naming the key and the click and stops.
- Its own `discordGet`: the same `Bot` header and the same ward as the Discord
  line's — the token rides the header alone, an error carries the status, the
  route and 300 characters of the body. `src/lines/discord.ts` is untouched.
- The ground: the category named `testing`, then every text channel under it
  whose name ends `-testing`; the slug is `resonance-` and the name without the
  suffix. A voice channel, a channel of another category and a channel named
  only `-testing` are not ground.
- The rows: the last 50 messages of each channel; a message opening with 🐛 is
  a `bug`, with 📝 or 💡 a `note`, and nothing else is carried. Each row is
  `discord:<message id>` · slug · kind · the author's display name · the
  message timestamp · `#<channel>` · the content whole · the jump url. Rows are
  the `ReportRow` of `src/lines/tracks.ts`, and `REPORTS_SOURCE` is the seed's
  source; no shape is redefined here.
- The merge: `resonance-nectere/seeds/testing-reports.json` is read first,
  every held row keeps its place, a fresh row rewrites its own id or joins the
  end, and no row of another source is dropped. A file that is not JSON stops
  the run before anything is written. `--dry` writes nothing.
- The console carries the guild name, the channel counts, and each carried
  row's id, kind and time. Message text reaches the seed only.

`tests/fixtures/discord/` holds four recorded-shape responses: `guild.json`,
`guild-channels.json`, `echoes-testing-messages.json`,
`sirens-testing-messages.json`. No key value is in them.

## What was verified

- `npm run check` — `tsc --noEmit`, exit 0. This repo has no `build` script.
- `python server_smoke.py` — "smoke complete — the server spoke, every line
  answered.", exit 0.
- A scratchpad script run with `npx tsx` against the four fixtures: 11 checks,
  0 failures — the category and its channels, the three exclusions, the slug,
  the five glyph cases, three of five messages carried oldest first, the text
  equal to the message content, the jump url, a channel carrying nothing, the
  merge keeping a `play:` row and rewriting by id, and a rerun changing nothing.
- Live, reads only: `npx tsx src/census/testing_channels_census.ts --dry` —
  guild "The AudHDities Sanctuary", 18 channels, no category named `testing`,
  0 channels under it, 0 messages carried, nothing written.

## What is short

The guild holds no `testing` category yet, so no live message has been parsed —
the parsing stands on the fixtures. The census is not a `package.json` script
and not a registered tool; it runs by its path.
