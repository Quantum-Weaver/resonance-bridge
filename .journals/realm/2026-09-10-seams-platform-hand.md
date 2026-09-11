# The tracks seam — 2026-09-10

## What is

`src/lines/tracks.ts` stands: a module with no tool registration, imported by
the three store lines and the tracks census.

- The seed shapes: `TracksSeed` · `TrackRow` · `ReportsSeed` · `ReportRow`,
  with `DoorState` — "read", or "unread: " and the sentence — `StoreChannel`,
  `ReportKind`, and `TRACKS_SOURCE` / `REPORTS_SOURCE`.
- The status words: `BEACON_STATUSES`, the ten of
  `resonance-grammar/docs/sql/043-the-beacons.sql`, and `BeaconStatus` derived
  from them.
- The mapping: `playStatus(trackId, release, lifecycle)`,
  `galaxyStatus(contentStatus, betaState)`,
  `microsoftStatus(submissionStatus, inFlight)` — pure, total, every branch a
  043 word.
- The ring: `PORTAL_CLICKS`, `STORE_KEY_NAMES`, `STORE_NAMES`,
  `readKeys(names)` returning present and missing NAMES, and
  `shutDoor(store, keyName, click)` — one sentence naming the key and the
  click.
- The addresses: `listingUrl(store, appId)` for Play, Galaxy and Microsoft;
  null on an empty id.
- The tokens: `rs256Jwt(header, payload, privateKeyPem)` over
  `crypto.createSign("RSA-SHA256")`, `googleServiceAccountToken(jsonPath)`,
  `samsungAccessToken(serviceAccountId, privateKeyPath)`,
  `microsoftToken(tenant, clientId, secret)`. A thrown error carries the
  portal, the HTTP status and the endpoint's own error code and nothing else;
  a token is returned to its caller and nowhere else. No npm dependency added.

`docs/seeds/store-tracks.schema.json` and `docs/seeds/testing-reports.schema.json`
mirror those types in draft 2020-12, `additionalProperties: false` throughout.

`tests/fixtures/README.md` states what the folder holds.

`.env.example` gains six names with the portal click each one earns:
`GOOGLE_PLAY_SERVICE_ACCOUNT_JSON` · `SAMSUNG_GSD_SERVICE_ACCOUNT_ID` ·
`SAMSUNG_GSD_PRIVATE_KEY_PATH` · `MS_STORE_TENANT_ID` · `MS_STORE_CLIENT_ID` ·
`MS_STORE_CLIENT_SECRET`. `.env` is untouched; no value was read or written.

## What was verified

- `npm run check` — `tsc --noEmit`, clean, exit 0. There is no `build` script
  in this repo.
- `python server_smoke.py` — "smoke complete — the server spoke, every line
  answered.", exit 0.
- A throwaway script under the session scratchpad, run with `npx -y tsx` and
  deleted after: 40 checks, 0 failures — `rs256Jwt` verified by
  `crypto.verify` against a 2048-bit key generated in the script and refused
  on a tampered payload; every named branch of the three mappings; every
  combination of the three mappings' inputs returning a word inside
  `BEACON_STATUSES`; the three listing addresses; `readKeys` naming a blank
  value as missing and carrying no value into its return; the six shut-door
  sentences.
- A second throwaway script built a `TracksSeed` and a `ReportsSeed` from the
  module's own types and constants; both validate against the two schemas
  (`jsonschema` 4.26.0, `Draft202012Validator`). Both schemas pass
  `check_schema`. A seeded status of `beta`, a door of `maybe`, an extra
  property, a kind of `praise` and an id of `slack:1` are each refused.

## What is short

No fixture JSON stands under `tests/fixtures/` — recorded portal responses
belong to the lines that parse them. No portal was called.
