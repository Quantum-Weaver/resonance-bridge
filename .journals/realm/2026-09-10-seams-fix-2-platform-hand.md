# The tracks seam, second hand — 2026-09-10

## What is

`src/lines/tracks.ts` carries three mends.

- `playStatus` reads the track id before the release lifecycle: `qa` and
  `internal` answer `internal_testing` whatever the lifecycle says. The
  lifecycle words `inReview` · `rejected` · `notApproved` · `denied` still
  overlay `beta`, `production` and every custom track.
- `microsoftStatus` answers `planned` for a `Canceled` or `Cancelled`
  submission, and the flight check now stands ahead of it, so a canceled
  submission with a flight answers `closed_testing`. No mapping answers
  `withdrawn`.
- The two fall-through returns of `none` — `galaxyStatus` and
  `microsoftStatus` — each carry one line stating that a word the portal does
  not name reads `none`.

`tests/fixtures/` holds six recorded-shape JSON responses of the token
endpoints the module parses: `play-token.json` · `play-token-error.json` ·
`galaxy-token.json` · `galaxy-token-flat.json` · `microsoft-token.json` ·
`microsoft-token-error.json`. Every token value in them reads
`FIXTURE-not-a-key`; no key, no path, no real value is recorded there.

`.env.example`, `docs/seeds/store-tracks.schema.json` and
`docs/seeds/testing-reports.schema.json` are unchanged. `.env` is untouched.

## What was verified

- `npm run check` — `tsc --noEmit`, exit 0. There is no `build` script in this
  repo.
- `python server_smoke.py` — "smoke complete — the server spoke, every line
  answered.", exit 0.
- A throwaway module under the session scratchpad, run with `npx -y tsx` and
  deleted after: 111 checks, 0 failures. `rs256Jwt` verified by
  `crypto.verify` against a 2048-bit key generated in the run and refused on a
  tampered input; 43 mapping cases across the three portals, every answer a
  word of `BEACON_STATUSES`; the three listing addresses and the two null
  cases; `readKeys` naming a blank value as missing and carrying no value into
  its return; the six shut-door sentences printed whole.
- The same run stubbed `fetch` and served the six fixtures: each token
  function returned the fixture's token from the right endpoint by POST; the
  Google error fixture threw `The Google Play token endpoint answered 400
  (invalid_grant).` with no `error_description` and no file path; the
  Microsoft error fixture threw `The Microsoft Store token endpoint answered
  401 (invalid_client).` with no `AADSTS` text and no secret; a non-JSON body,
  a body with no token and an unreadable key file each threw one plain
  sentence carrying neither body nor path.
- A throwaway Python run under the scratchpad: both schemas pass
  `Draft202012Validator.check_schema`; a tracks seed and a reports seed built
  from the module's own words validate; a status of `beta`, a door of `maybe`,
  an extra property, a kind of `praise`, an id of `slack:1` and a missing
  `note` are each refused.

No portal was called. Nothing was committed.

## What is short

- No mapping says `withdrawn`; no store read the three lines make names a
  takedown.
- `TrackRow.status` carries no word for unknown: an unnamed or absent portal
  word reads `none`, which is also the 043 word for not pursued.
- The fixtures cover the token endpoints, the module's only portal-shape
  parsing. The store read shapes belong to the lines that parse them.
