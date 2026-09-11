# The channels census, read — 2026-09-10, round 3

Team B's sending read against `src/census/testing_channels_census.ts` and
`tests/fixtures/discord/*.json`. Nothing was changed; every proof was run from
the scratchpad and every live call was a GET.

## The sending, line by line

- The census at the named path, run `npx tsx src/census/testing_channels_census.ts [--dry]` — done.
- `DISCORD_BOT_TOKEN_BRIDGE` and `DISCORD_GUILD_ID` from `process.env` at call time — done
  (`:117`, `:271`, `:275`); the bridge `.env` loads by absolute path (`:30-32`) and does not
  override an environment value, proven by an empty token answering the shut-door sentence.
- The guild's channels, the category named `testing`, every text channel under it ending
  `-testing` — done (`:182-205`); the voice channel, the bare `-testing` and the channel outside
  the category are all excluded in the fixture proof.
- The slug — done differently. `resonance-` + the name is now the fallback only; `readRegister()`
  (`:135-148`) reads `slug,beacon_type,status` of every beacon through the anon door,
  `channelNameOf` (`:151-154`) is the tender's namer, `slugByChannel` (`:162-172`) reads it
  backwards with a flowing app or game ranked first, and `slugOf` (`:174-179`) answers the map
  before the old rule. This is the round-2 defect mended and it holds: live, 40 beacons make 40
  channel names, `audhdities-testing -> audhdities`, and all 12 slugs the tender names a channel
  for read back to themselves and stand as `category_set` slugs in the base.
- The last 50 messages, 🐛 `bug`, 📝 and 💡 `note`, else not carried — done (`:41`, `:76-80`,
  `:126-132`).
- The rows into `resonance-nectere/seeds/testing-reports.json` — done (`:207-229`); every row
  satisfies `docs/seeds/testing-reports.schema.json`.
- Merge by id, never dropping the stores' rows — done (`:232-249`, `:252-267`, `:320-326`).
- `--dry` prints and writes nothing — done (`:333-336`), proven live.
- Its own GET helper with the line's headers and the line's ward — done (`:111-124`), the shape of
  `src/lines/discord.ts:29-41`; `discord.ts` untouched.
- Reads only — no `method:`, no POST/PUT/PATCH/DELETE anywhere in the file.
- A shut door is one plain sentence — four of them, each naming its key and its click
  (`:57-64`, `:67-73`), each proven.

## Re-run

- `npm run check` — `tsc --noEmit`, exit 0.
- `python server_smoke.py` — "smoke complete — the server spoke, every line answered.", exit 0.
- The verifier's own module against the six fixtures — `46 checks, 0 failures`.
- `npx tsx src/census/testing_channels_census.ts --dry` — guild The AudHDities Sanctuary
  (1517902793288056852), 18 channels, `register: 40 beacons · 40 channel names`, no category named
  `testing`, 0 channels under it, 0 carried, the seed not written, exit 0. Word for word the
  hand's report.
- `SUPABASE_URL_KNOWLEDGE=` and `SUPABASE_PUBLISHABLE_KEY_KNOWLEDGE=` — each its own sentence, the
  run carrying on, exit 0. `DISCORD_BOT_TOKEN_BRIDGE=` and `DISCORD_GUILD_ID=` — each its own
  sentence, exit 1.
- Live, reads only: 12 of 12 beacon slugs survive the namer and its inverse; no channel name reads
  to a slug no beacon holds; `python progenatrix.py sets beacon` holds all 12 and not
  `resonance-audhdities`.

## What stands short

No key value reaches a console, an error, a seed or a return: the token rides one `Authorization`
header (`:117`), the publishable key rides `apikey` and `Bearer` (`:142`), and the two error paths
carry a status and a clipped body only (`:121`, `:145`).

The guild holds no `testing` category, so no live message has been parsed; the parsing, the merge
and the unreadable-seed refusal stand on the fixtures. `seeds/testing-reports.json` does not exist.

The census is not a `package.json` script and not a registered tool.
