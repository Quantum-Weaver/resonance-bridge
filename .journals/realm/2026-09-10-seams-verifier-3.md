# The tracks seam, read — 2026-09-10, round 3

## What was read

`src/lines/tracks.ts`, `docs/seeds/store-tracks.schema.json`,
`docs/seeds/testing-reports.schema.json`, `tests/fixtures/` (the README and the
six recorded responses), the six names on `.env.example`, `.env`'s mtime and
name list, and `resonance-grammar/docs/sql/150-the-testing-public.sql`, against
the third sending and THE TESTING TRACKS PLAN sections 2, 3, 4, 5.

## What stands

- `TrackStatus = BeaconStatus | null` (`src/lines/tracks.ts:25`) is carried by
  `TrackRow.status` (`:49`) and by the schema's status enum
  (`docs/seeds/store-tracks.schema.json:40-55`). No mapping answers `none`:
  720 Play, 49 Galaxy and 26 Microsoft readings each answer a word of
  `BEACON_STATUSES` or `null`.
- `galaxyStatus` reads the beta before the content status (`:131`);
  `microsoftStatus` reads the flight before the submission (`:145`);
  `playStatus` reads the track id before the lifecycle (`:102`). Every clause
  §4 writes answers §4's word.
- `packaged` tests `statusUnspecified` (`:90`); `playStatus("alpha",
  "statusUnspecified", null)` answers `planned`.
- `tokenPost` wraps the fetch (`:266-272`); a thrown transport error answers
  `The Microsoft Store token endpoint could not be reached.` and carries no
  tenant.
- One `process.env` read (`:206`), names only into the return; one `fetch`
  (`:269`), `POST` to the three token endpoints; no `PATCH`, `PUT` or
  `DELETE`; no `console`, no `argv`, no fs write; no new dependency.
- `.env` untouched, mtime 2026-09-06 19:27:28, and none of the six names
  stands on it. `.env.example:54-60` carries the six names with empty values.
- `150-the-testing-public.sql` unchanged: `statement_count 3`, four header
  lines, no write verb outside the header line naming what the file does not do.
- Neither repo carries a commit; `git status` shows only the scope's files and
  the journals.

## The checks re-run

    npm run check                     → tsc --noEmit, exit 0
    npm run build                     → npm error Missing script: "build"
    python server_smoke.py            → exit 1 once, then exit 0, 0, 0
    npx -y tsx <scratchpad>/proof.mts → checks 889 pass 889 fail 0
    python <scratchpad>/schema_proof.py → checks 53 pass 53 fail 0
    150 parsed                        → statement_count 3, forbidden in body: []

The first smoke run answered `server closed the pipe. stderr: local
knowledge.db line down (unable to open database file) - serving without it`
after listing 54 tools; the three runs after it answered `smoke complete — the
server spoke, every line answered.` `src/lines/tracks.ts` is imported by no
file in `src/`, and `tsc --listFiles` holds it.

The proof stubbed `fetch` over the six fixtures: each token function answered
the fixture's token by `POST` to its own endpoint, the Google assertion and the
Galaxy JWT both verifying against a key generated in the run, the Google claims
carrying the androidpublisher scope, the token endpoint as `aud` and an hour's
life. A sentinel key value placed in `MS_STORE_CLIENT_SECRET`, in a service
account file and in a private key file reached no return, no message and no
stack.

## What is short

- `internal` stands beside `qa` at `src/lines/tracks.ts:102`, a superset of
  §2's "the internal track is `qa`" and §4's `qa`. The hand's return addresses
  this line as `:99`.
- `galaxyStatus` answers `closed_testing` for every beta word outside
  `GALAXY_BETA_OFF` (`:115-131`), where an unnamed content status answers
  `null` (`:137`).
- A malformed private key leaves `rs256Jwt` (`:249`) as OpenSSL's own words,
  `error:1E08010C:DECODER routines::unsupported`, not one house sentence.
- The fixtures record the token endpoints; the store read shapes are unrecorded.
- `tests/fixtures/*.json` stand beyond the scope's file list and inside the
  sending's VERIFICATION.
- The null in `TrackRow.status` widens §4's row shape; team A and team C build
  against it.
