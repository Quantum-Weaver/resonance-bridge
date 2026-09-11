# The channels census, mended — 2026-09-10, round 2

## What the work did

`src/census/testing_channels_census.ts`, run as
`npx tsx src/census/testing_channels_census.ts [--dry]`.

- `heldRows` answers `{ rows, readable }`. An absent file is an empty seed and
  readable; a file that is present and will not read — a lock, a permission,
  bytes that are not JSON — is `readable: false` and carries no rows.
- `main` reads the held seed before the merge. When it is unreadable the run
  says one sentence naming the file, writes nothing and stops, in `--dry` and
  in the write alike. The seed's held rows are never replaced by this run's
  Discord rows alone.
- `tests/fixtures/discord/testing-reports-held.json` — a recorded reports seed
  of one `play:` row and one `discord:` row, so the merge and the held read are
  proven against a file and not memory alone.

## What was verified

- `npm run check` — `tsc --noEmit`, exit 0.
- `python server_smoke.py` — "smoke complete — the server spoke, every line
  answered.", exit 0.
- A scratchpad module run with `npx tsx` against the five fixtures:
  `25 checks, 0 failures` — the category and its channels, the three
  exclusions, the slug, the five glyph cases, three of five messages carried
  oldest first, the display name, the text equal to the message content, the
  jump url, a channel carrying nothing, the held seed read from the file, the
  merge keeping the `play:` row and rewriting one id, a rerun changing nothing,
  an absent seed readable and empty, a directory and a not-JSON file both
  `readable: false`.
- Live, reads only: `npx tsx src/census/testing_channels_census.ts --dry` —
  guild "The AudHDities Sanctuary" (1517902793288056852), 18 channels, no
  category named `testing`, 0 channels under it, 0 carried, nothing written.
- The refusal, live: a directory made at the seed path for the length of one
  run and removed after — "…testing-reports.json is present and unreadable —
  it is left whole and this run's rows are not written.", exit 1, nothing
  written.
- `DISCORD_BOT_TOKEN_BRIDGE= npx tsx …--dry` — one sentence naming the key and
  the click, exit 1.

## What is short

The slug is `resonance-` + the channel name without `-testing`, the rule as
sent. The register holds one flowing beacon whose slug carries no
`resonance-` prefix, `audhdities`; a row carried from `#audhdities-testing`
lands with slug `resonance-audhdities`, which no beacon holds. The naming rule
belongs to the plan, and the census reads no register to resolve it.

The guild holds no `testing` category, so no live message has been parsed; the
parsing stands on the fixtures. The census is not a `package.json` script and
not a registered tool.
