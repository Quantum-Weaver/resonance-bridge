# The channels census, mended — 2026-09-10, round 3

*Nothing committed. Nothing delivered. No key value left a header.*

## What the work did

`src/census/testing_channels_census.ts`, run as
`npx tsx src/census/testing_channels_census.ts [--dry]`.

- A channel's slug is now the slug the register holds for that channel's name.
  `readRegister()` reads `slug,beacon_type,status` of every beacon through the
  anon door, `SUPABASE_URL_KNOWLEDGE` and `SUPABASE_PUBLISHABLE_KEY_KNOWLEDGE`
  read from `process.env` at call time, the key riding `apikey` and `Bearer`
  alone.
- `channelNameOf(slug)` is the tender's namer — the slug without the
  `resonance-` prefix and `-testing` after it. `slugByChannel(beacons)` reads
  that namer backwards into a map of channel name to slug, a flowing app or
  game claiming a name before any other beacon does. `slugOf(name, known)`
  answers the map, and `resonance-` and the name when the map does not hold it.
- `testingGround(channels, known)` carries the map into every channel's slug,
  and a channel no beacon names is said so in its own console line.
- An unread register is one sentence naming the key, the click that earns it,
  and the slug read until then; the run carries on with the Discord keys alone,
  and a later run rewrites those rows by their ids.
- `tests/fixtures/discord/register-beacons.json` — a recorded register read of
  six rows: a slug with no `resonance-` prefix, two slugs that make one channel
  name, and a beacon that is not flowing.

## What was verified

- `npm run check` — `tsc --noEmit`, exit 0.
- `python server_smoke.py` — "smoke complete — the server spoke, every line
  answered.", exit 0.
- A scratchpad module run with `npx tsx` against the six fixtures:
  `44 checks, 0 failures` — the map's five names, `audhdities-testing` reading
  `audhdities`, `echoes-testing` reading the flowing `resonance-echoes` over
  the imagined `echoes`, a beacon not flowing still naming its channel, an
  empty register naming nothing, every flowing slug surviving the round trip
  through the namer and back, the fallback for a channel no beacon names, the
  category and its two channels with the three exclusions, the five glyph
  cases, three of five messages carried oldest first, the display name, the
  text equal to the message content, the jump url, the held seed read from a
  file, the merge keeping the `play:` row and rewriting one id, a rerun
  changing nothing, an absent seed readable and empty, a folder and bytes that
  are not JSON both `readable: false`.
- Live, reads only: `npx tsx src/census/testing_channels_census.ts --dry` —
  guild "The AudHDities Sanctuary" (1517902793288056852), 18 channels,
  `register: 40 beacons · 40 channel names`, no category named `testing`, 0
  channels under it, 0 carried, nothing written.
- Live, reads only: the map against the register — `audhdities-testing ->
  audhdities`, `echoes-testing -> resonance-echoes`, the slugs with no prefix
  being `audhdities, aethelred-cello, quantum-weaver`; and of the 12 beacons
  the tender names a channel for, 12 read back to their own slug. All 12 stand
  as `category_set` slugs in `progenatrix.db`; `resonance-audhdities` does not.
- `SUPABASE_URL_KNOWLEDGE=` and `SUPABASE_PUBLISHABLE_KEY_KNOWLEDGE=` each
  answered its own sentence with its click and the run carried on, exit 0.
- `DISCORD_BOT_TOKEN_BRIDGE=` and `DISCORD_GUILD_ID=` each answered its own
  sentence with its click, exit 1, no socket opened.

## What is short

The guild holds no `testing` category, so no live message has been parsed; the
message parsing stands on the fixtures.

A channel whose name no beacon holds reads as `resonance-` and its name, and a
row carried from it names a slug the base may not hold; the run says which
channel that is.

The census is not a `package.json` script and not a registered tool.
