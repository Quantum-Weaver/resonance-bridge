# 2026-09-10 · joining · verifier-1

## What was read

The joining's four bridge files against its sending: `server_smoke.py`,
`src/census/tracks_census.ts`, `src/lines/galaxy.ts`, `src/lines/tracks.ts`.

## What was verified

- `npm run check` -> `tsc --noEmit`, exit 0. `npm run build` -> `Missing script: "build"`,
  exit 1; this repo carries dev, check, smoke, census:tracks, register.
- `python server_smoke.py` -> 70 tools registered; `play_whoami`, `galaxy_whoami` and
  `ms_whoami` each answer their shut-door sentence; `smoke complete — the server spoke,
  every line answered.`, exit 0.
- `npx tsx tests/tracks.test.ts` -> `146/146 assertions held`, exit 0.
- `npx tsx src/census/tracks_census.ts --dry` -> twenty play_app_id fills, the three shut
  doors verbatim, both seeds printed with `rows: []` and neither written, exit 0.
- `npx tsx src/census/testing_channels_census.ts --dry` -> guild The AudHDities Sanctuary
  (1517902793288056852), 18 channels, register 40 beacons · 40 channel names, no category
  named testing, 0 channels under testing, 0 rows, nothing written, exit 0. No message text
  reached the console.
- The two mends proved from a scratchpad module: `galaxyTrackRow` answers `null` for a
  content id with no package name and the listing address with one; `rs256Jwt` on a
  malformed key answers *The private key named on the ring is not an RSA private key node
  can sign with.* — no key body in the message, none in the stack, no OpenSSL words.
- `UNREADABLE_REPORTS` stands once at `src/census/tracks_census.ts:71` and is said on both
  the dry path (:349) and the write path (:361).
- Keys: eight `process.env` reads across the new lines and censuses, each into a header, a
  `readFile` path or a token mint; `readKeys` returns names only; `play_whoami` returns
  `key_name` and the account's own email. No value reaches a print, an error, a seed or a
  return. `.env` mtime 2026-09-06 19:27:28, none of the six store names on it.
- Writes: every `fetch` in the two censuses is a default GET; every fs write is a seed
  file. The only non-GET in the seam is the token POST at `src/lines/tracks.ts:275`.

## What is short

- `npm run build` does not exist here; `npm run check` is the check.
- `play.ts:379`, `galaxy.ts:219` and `microsoft.ts:313` still seed
  `1970-01-01T00:00:00.000Z` for a review the portal gave no time.
- `src/lines/tracks.ts:102,131` and the `TrackStatus` null at `:25` stand as three rounds
  left them; plan §7 holds the status mapping.

Nothing was changed, staged or committed here. No `--deliver`, no store portal called.
