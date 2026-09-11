# The tracks seam, third hand — 2026-09-10

## What is

`src/lines/tracks.ts` carries five mends.

- `TrackStatus = BeaconStatus | null` is the seam's word for a row, and
  `TrackRow.status` carries it. A portal that named none answers `null`; the
  register keeps the value it holds. No mapping answers `none` any more.
- `galaxyStatus` reads the beta state before the content status:
  `FOR_SALE` beside a running beta answers `closed_testing`. `FOR_SALE`,
  `UNDER_CONTENT_REVIEW` and `REGISTERING` answer `published`, `in_review`
  and `building` where the beta is off; anything else answers `null`.
- `microsoftStatus` reads the flight before the submission: `inFlight` — the
  app has a flight carrying a submission — answers `closed_testing` whatever
  the app's own submission says. `Published`, `CertificationFailed`,
  `Certification` · `PendingPublication` · `Release`, `PendingCommit` ·
  `CommitStarted` · `CommitFailed` and `Canceled` · `Cancelled` answer
  `published`, `rejected`, `in_review`, `building` and `planned`; anything
  else answers `null`.
- `packaged` tests Play's own release word `statusUnspecified`; it had tested
  `statusNotSpecified`, which the portal does not say.
- `tokenPost` wraps the fetch: a transport failure answers
  `The <portal> token endpoint could not be reached.`

`docs/seeds/store-tracks.schema.json` takes `null` in the status enum, its
description naming what a null leaves standing.

`playStatus`, the ring, the shut-door sentences, the listing addresses, the
four token helpers and `testing-reports.schema.json` are unchanged.
`tests/fixtures/` is unchanged, six recorded shapes, every token value
`FIXTURE-not-a-key`. `.env.example` is unchanged and `.env` is untouched —
mtime 2026-09-06 19:27:28, and none of the six names stands on it.

## What was verified

- `npm run check` — `tsc --noEmit`, exit 0. This repo has no `build` script.
- `python server_smoke.py` — "smoke complete — the server spoke, every line
  answered.", exit 0.
- A module written under the session scratchpad, run with `npx -y tsx` and
  deleted after: `checks 146 · pass 146 · fail 0`. `rs256Jwt` verified by
  `crypto.verify` against a 2048-bit key generated in the run and refused on a
  tampered payload; 19 Play cases, 11 Galaxy, 14 Microsoft, and a matrix of
  640 Play · 42 Galaxy · 16 Microsoft readings in which every answer is a word
  of `BEACON_STATUSES` or `null` and none is `none`; the three listing
  addresses and three empty ids; `readKeys` naming a blank value as missing
  and carrying no value into its return; the six shut-door sentences whole.
- The same run stubbed `fetch` and served the six fixtures: each token
  function returned the fixture's token from the right endpoint by POST, the
  Google assertion and the Galaxy JWT both verifying against the run's public
  key, the Google claims carrying the androidpublisher scope and an hour's
  life. The Google error fixture threw `The Google Play token endpoint
  answered 400 (invalid_grant).`; the Microsoft error fixture threw `The
  Microsoft Store token endpoint answered 401 (invalid_client).` with no
  `AADSTS` text, no tenant and no secret; a thrown transport error gave
  exactly `The Microsoft Store token endpoint could not be reached.`; a
  missing key file, a half service account, a non-JSON body and a body with no
  token each gave one plain sentence carrying neither body nor path.
- A Python run under the scratchpad, deleted after: `checks 41 · pass 41 ·
  fail 0`. Both schemas pass `Draft202012Validator.check_schema`; the tracks
  seed the module itself built — one read row, one row whose status is `null`,
  one shut door — validates; all ten 043 words and `null` are taken; a status
  of `testing`, an empty status, a missing status, a door of `shut`, an
  `unread: ` with no sentence, an extra property, a channel of `audhdities`, a
  tester count of −1 and an empty app id are each refused; the reports seed
  takes its three kinds and four id prefixes and refuses a kind of `idea`, an
  id with no source, an empty text, a null text, a missing time and a count.

No portal was called. No `--deliver` was passed. Nothing was committed.

## What is short

- `playStatus` reads `internal` as Play's internal track beside `qa`. The
  portals table names only `qa`; androidpublisher answers `internal`. Both
  answer `internal_testing`.
- `playStatus` answers no `null`: every track it is given exists, and a track
  with no release answers `planned`.
- Where a testing container and a live release stand together the word names
  the testing state — a `qa` track, a running Galaxy beta and a Microsoft
  flight each answer ahead of the release. `published_version`,
  `published_at` and `note` carry the rest of what the portal said.
- No mapping says `withdrawn`. No read the three lines make names a takedown.
- The fixtures cover the token endpoints, the module's only portal-shape
  parsing. The store read shapes belong to the lines that parse them.
