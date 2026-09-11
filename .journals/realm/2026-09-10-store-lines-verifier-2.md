# 2026-09-10 · store-lines · verifier · round 2

## What the work did

Read team A's fix-2 hand — `src/lines/play.ts`, `galaxy.ts`, `microsoft.ts`,
`src/census/tracks_census.ts`, `tests/tracks.test.ts` and the store fixtures —
against its sending, plan §§2-5 and the round-1 defect list.

Checks re-run, output matching the return:

- `npm run check` (`tsc --noEmit`) — exit 0. No `build` script exists here.
- `npx -y tsx tests/tracks.test.ts` — `139/139 assertions held`, exit 0.
- `python server_smoke.py` — `handshake OK: resonance-bridge v0.2.0`,
  `tools registered (70)` with the sixteen store names among them,
  `smoke complete — the server spoke, every line answered.`
- `npx tsx src/census/tracks_census.ts --dry` — twenty `play_app_id`s filled
  from disk, three shut doors each naming its key and its click, both seeds
  printed, neither written; `resonance-nectere/seeds/` holds no
  `store-tracks.json` or `testing-reports.json`.
- `npx tsc --ignoreConfig --noEmit --target es2022 --module nodenext
  --moduleResolution nodenext --strict --skipLibCheck --types node
  tests/tracks.test.ts` — exit 0.
- `organs_tools.read_line` on the three lines — sixteen names and first
  sentences parsed, every standing `live`; `ORDER` still names eight lines.
- Rows built from the fixtures by a verifier-side script validate against
  `docs/seeds/store-tracks.schema.json` (4 rows) and
  `testing-reports.schema.json` (6 rows), format checker on, zero errors.
- Over stdio with `GOOGLE_PLAY_SERVICE_ACCOUNT_JSON` pointing at a file that
  does not exist: `play_tracks` and `play_testers` answer the dry sentence with
  and without `open_edit: false`; every Galaxy and Microsoft tool answers the
  shut door. `open_edit: true` was not called.

## What stands

- The six round-1 defects inside team A's ground are mended: the census is off
  the edit road, the three parsers name a writer for a blank author, `PLAY_REACH`
  ranks the 043 words by reach, the disk fill carries no `beacon_type` filter,
  `ms_submission` fills both Microsoft version columns, `parseEditId` proves
  `play/edits-insert.json`.
- No `process.env` value reaches a return, a log, a seed or an error; every read
  feeds a header, a file read or a token mint. The ring holds none of the six
  store key names.
- `POST` and `DELETE` exist in one place, `play.ts` `playEdit`, reached only
  through `open_edit`; no other write verb is in the three lines or the census.
- Scope held: `src/server.ts`, `src/http.ts`, `package.json`, `tracks.ts`,
  `discord.ts`, `.env`, nectere and the site carry no hours from this hand.

## What was short

- The Play edit envelope stands behind `open_edit`; the plan's portals table and
  the sending both name that road, and the ruling is the conductor's.
- `playTrackRow`'s note carries track, release status and version, not the
  release lifecycle, so a rejected release beside a published production track
  leaves no mark in the seed.
- `playReadTracksByRelease` skips every 404, so a package Play does not hold and
  an endpoint that answers 404 read alike; the door still says `read`.
- The census emits a Play row for every beacon whose `tauri.conf.json` filled an
  `app_id`, whether or not Play holds a track for it, and the deliverer writes a
  non-empty `app_id`.
- No store key is on the ring; every fixture is a docs shape, unproven live.
- `server_smoke.py` carries no store `whoami` call and `organs_tools.py`'s
  `ORDER` no store line; both outside team A's ground.
