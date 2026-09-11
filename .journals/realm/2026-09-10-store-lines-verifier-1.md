# 2026-09-10 · store-lines · verifier · round 1

## What the work did

Read team A's build — `src/lines/play.ts`, `galaxy.ts`, `microsoft.ts`,
`src/census/tracks_census.ts`, the three registrations on `src/server.ts` and
`src/http.ts`, the one `census:tracks` script, thirteen fixtures and
`tests/tracks.test.ts` — against its sending, plan §§2-5 and `tracks.ts`.

Checks re-run, output matching the return:

- `npm run check` (`tsc --noEmit`) — green. No `build` script exists in this
  repo; the return names that.
- `npx -y tsx tests/tracks.test.ts` — `80/80 assertions held`.
- `python server_smoke.py` — `handshake OK: resonance-bridge v0.2.0`,
  `tools registered (69)` with the fifteen new names among them,
  `smoke complete — the server spoke, every line answered.`
- `npx tsx src/census/tracks_census.ts --dry` — fourteen `play_app_id`s filled
  from disk, three shut doors, both seeds printed, neither written
  (`resonance-nectere/seeds/` holds no `store-tracks.json` or
  `testing-reports.json`).
- `organs_tools.read_line` on the three lines — fifteen names and first
  sentences parsed, every standing `live`. `ORDER` still names eight lines.
- The ring holds none of the six store key names; no store portal was called.

## What stands

- All fifteen tools open with the key check and answer `shutDoor(...)`.
- No `process.env` value reaches a return, a log, a seed or an error; every
  read feeds a header, a file read or a token mint.
- Seed rows carry exactly the field sets `docs/seeds/*.schema.json` require;
  statuses are 043 words or null; the reports merge keeps a Discord row in
  place, replaces a re-read row by id and appends what is new.
- The scope held: only the named files carry this hand's hours.

## What was short

- `playEdit` (`src/lines/play.ts:73`) is a POST and a DELETE against Play,
  called by `withEdit` for `play_tracks` and `play_testers`. The sending both
  commands `edits.insert`/`edits.delete` and forbids a write verb; plan §2's
  portals table names the same road. The conductor's ruling.
- `said_by` is the empty string when a store answers an empty author name —
  `play.ts:161`, `galaxy.ts:152`, `microsoft.ts:147` all use `??`, which does
  not catch `""`. The reports schema requires `minLength: 1`; the microsoft
  fixture itself records `"reviewerName": ""`.
- `furthest` (`play.ts:215`) reads the 043 vocabulary as a rank, so a rejected
  side-track release outranks a completed production release: an app live on
  Play with one rejected alpha reports `rejected`.
- The census fills `play_app_id` from disk only for `beacon_type` `app` or
  `game`; plan §4 sets no such filter. Named in the return.
- `microsoft_published_version` never fills: no tool in the sending's list
  reads a submission's package version.
- `tsconfig.json` includes `src/**/*.ts` only, so `tsc --noEmit` does not
  type-check `tests/tracks.test.ts`.
- `server_smoke.py` still carries no store `whoami` call and `organs_tools.py`'s
  `ORDER` no store line; both outside team A's ground and both named.
