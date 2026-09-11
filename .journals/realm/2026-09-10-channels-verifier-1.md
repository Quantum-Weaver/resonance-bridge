# The channels census, read — 2026-09-10, round 1

Team B's sending, read against `src/census/testing_channels_census.ts` and
`tests/fixtures/discord/*.json`. Nothing was changed.

## The sending, line by line

- The census at the named path, run `npx tsx src/census/testing_channels_census.ts [--dry]` — done.
- `DISCORD_BOT_TOKEN_BRIDGE` and `DISCORD_GUILD_ID` from `process.env` at call time — done
  (`:80`, `:182`, `:186`); the bridge `.env` is loaded by absolute path (`:25-27`) and the
  environment still takes precedence, proven by an empty token answering the shut-door sentence.
- The guild's channels, the category named `testing`, every text channel under it ending
  `-testing` — done (`:102-118`).
- The slug `resonance-` + the name without the suffix — done as sent (`:97-99`). The register
  holds one beacon whose slug carries no `resonance-` prefix, `audhdities`; a row carried from
  `#audhdities-testing` would wear `resonance-audhdities`, a slug no beacon holds.
- The last 50 messages, 🐛 as `bug`, 📝 and 💡 as `note`, else not carried — done (`:36`, `:50-54`,
  `:89-95`).
- The rows into `resonance-nectere/seeds/testing-reports.json` with id, said_by, said_at, where,
  text and link — done (`:130-139`); the row and seed types come from `src/lines/tracks.ts` and
  match `docs/seeds/testing-reports.schema.json`.
- Merge by id, never dropping the stores' rows — done for an absent file and for a file that is
  not JSON (`:145-178`). A file that exists and cannot be read for any other reason is read as
  absent (`:167-169`), and the following write would carry only this run's rows.
  `src/census/tracks_census.ts:277-285` guards that case and refuses the write.
- `--dry` prints and writes nothing — done (`:227-230`), proven live.
- Its own GET helper with the line's headers and the line's ward — done (`:74-87`), the same
  shape as `src/lines/discord.ts:29-41`; `discord.ts` is untouched.
- Reads only — no method other than the default GET exists in the file.

## Re-run

- `npm run check` — `tsc --noEmit`, exit 0.
- `python server_smoke.py` — "smoke complete — the server spoke, every line answered.", exit 0.
- The hand's scratchpad proof against the four fixtures — 11 checks, 0 failures.
- `npx tsx src/census/testing_channels_census.ts --dry` — guild The AudHDities Sanctuary
  (1517902793288056852), 18 channels, no category named `testing`, 0 channels under it,
  0 carried, `testing-reports.json` not written. Word for word the hand's report.
- `DISCORD_BOT_TOKEN_BRIDGE= npx tsx src/census/testing_channels_census.ts --dry` — one sentence
  naming the key and the click, exit 1.

## What stands short

The seed file does not exist, so the merge is proven against fixtures only. The census is not a
`package.json` script and not a registered tool.
