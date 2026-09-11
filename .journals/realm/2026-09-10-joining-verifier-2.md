# 2026-09-10 · joining · verifier-2

## What was read

`src/census/tracks_census.ts` — the one file this round changed in this repo — against
the joining's sending, and the bridge ground the whole road runs on:
`src/lines/tracks.ts`, `play.ts`, `galaxy.ts`, `microsoft.ts`,
`src/census/testing_channels_census.ts`, `server_smoke.py`, `docs/seeds/*.schema.json`.

## What was verified

- `npm run check` -> `tsc --noEmit`, exit 0. `npm run build` -> `npm error Missing
  script: "build"`, exit 1; this repo's scripts are `dev check smoke census:tracks
  register`.
- `npx -y tsx tests/tracks.test.ts` -> `146/146 assertions held`, exit 0.
- `python server_smoke.py` -> 70 tools registered; `play_whoami`, `galaxy_whoami` and
  `ms_whoami` each answer their shut-door sentence; `smoke complete — the server spoke,
  every line answered.`, exit 0.
- `npx tsx src/census/tracks_census.ts --dry` -> twenty play_app_id fills, the three shut
  doors one sentence each, both seeds printed with `rows: []`, neither written, exit 0.
- `npx tsx src/census/testing_channels_census.ts --dry` -> guild The AudHDities Sanctuary
  (1517902793288056852), 18 channels, register 40 beacons · 40 channel names, no category
  named testing, 0 channels under testing, nothing written, exit 0. No message text
  reached the console.
- `UNREADABLE_REPORTS` at `:71` reads *"…it is left whole and this run's store review
  rows do not reach it."* — one definition, said at `:349` on the dry path and `:361` on
  the write path, and true on both: the write path writes `store-tracks.json` at `:357`
  and holds back only the review rows bound for `testing-reports.json`.
- The register, read once through the anon door: `select=slug,testing_public` answers
  `400 {"code":"42703", … "message":"column beacons.testing_public does not exist"}`; the
  unflagged select answers 40 rows. Six beacons stand in a store, every one of type `app`
  or `game`; beacons of another type standing in a store: 0.
- Keys: eight `process.env` reads across the lines and censuses (`tracks.ts:206`,
  `play.ts:54`, `galaxy.ts:32,36`, `microsoft.ts:34-36`, `tracks_census.ts:95-96`,
  `testing_channels_census.ts:117,138-139,271,275`), each into a header, a `readFile`
  path or a token mint. `readKeys` returns names only. No value reaches a print, an
  error, a seed or a return. `.env` mtime 2026-09-06 19:27:28; none of the six store
  names on it.
- Writes: every `fetch` in both censuses is a default GET; every fs write is a seed file.
  Two non-GET verbs in this repo — the token POST at `tracks.ts:275`, and `playEdit`'s
  POST and DELETE at `play.ts:107`, reached from `withEdit` under the `open_edit` tool
  argument.

## What is short

- `play.ts:107` holds a POST and a DELETE against Play behind an MCP tool argument, not
  behind `--deliver`. Unreachable today: no Play key is on the ring and all five Play
  tools answer the shut sentence. Named by four hands; the conductor's ruling.
- `tracks_census.ts:98-100` names two keys and no click and ends the run, where
  `testing_channels_census.ts:67-73` names one key, its click, and carries on. Two shapes
  at one seam.
- `play.ts:379`, `galaxy.ts:219` and `microsoft.ts:313` still seed
  `1970-01-01T00:00:00.000Z` for a review the portal gave no time.
- `tracks.ts:102`, `:131` and the `TrackStatus` null at `:25` stand as four rounds left
  them.

Nothing was changed, staged or committed here. No `--deliver`, no store portal called.
