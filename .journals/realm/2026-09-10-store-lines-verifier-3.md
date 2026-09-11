# 2026-09-10 · store-lines · verifier · round 3

## What the work did

Read team A's fix-3 hand — `src/lines/play.ts`, `src/census/tracks_census.ts`,
`tests/tracks.test.ts` — against its sending, plan §§2-5 and the round-3 defect
list. `galaxy.ts`, `microsoft.ts`, the fixtures, `src/server.ts`, `src/http.ts`
and `package.json` carry the round-1 and round-2 hours and no new ones; file
times and `git diff` agree with the return.

Checks re-run, every output matching the return:

- `npm run check` (`tsc --noEmit`) — exit 0. No `build` script exists here.
- `npx -y tsx tests/tracks.test.ts` — `146/146 assertions held`, exit 0.
- `npx tsc --noEmit --ignoreConfig --module nodenext --moduleResolution nodenext
  --target es2022 --strict --skipLibCheck --types node tests/tracks.test.ts` —
  exit 0. Without `--ignoreConfig` it is `error TS5112`, tsconfig's own doing.
- `python server_smoke.py` — `tools registered (70)` with the sixteen store
  names among them; `smoke complete — the server spoke, every line answered.`
- `npx tsx src/census/tracks_census.ts --dry` — twenty `play_app_id`s filled
  from `src-tauri/tauri.conf.json`, three shut doors each naming its key and its
  click, both seeds printed, neither written; `resonance-nectere/seeds/` holds
  no `store-tracks.json` and no `testing-reports.json`.
- `organs_tools.read_line` on the three lines — sixteen names and first
  sentences parse, every standing `live`.
- Rows built from the fixtures by a verifier-side script validate against
  `docs/seeds/store-tracks.schema.json` (5 rows) and
  `testing-reports.schema.json` (6 rows), format checker on, zero errors.
- The sixteen tool handlers called with the ring holding none of the six store
  names: each answers one shut sentence matching `The <store> line is shut:
  <KEY> is not on the bridge's ring — <click>.`, `portal calls made: 0`.
- With a Play key name present and no file: `play_testers` answers the dry
  sentence with `open_edit` absent and with `open_edit false`, zero calls.
- `playReadTracksByRelease` against a recording stub: five requests, all `GET`,
  `answered=["beta"] unanswered=["qa","internal","alpha","production"]`,
  one track built.

## What stands

- The three round-3 mends hold: the note carries the release lifecycle
  (`play.ts:348-353`), a 404 lands in `unanswered` and never as an empty track
  (`play.ts:263-292`), and a package no named track answered for writes no row
  and reads no reviews (`tracks_census.ts:174-178`).
- No `process.env` value reaches a return, a log, a seed or an error. Eight
  reads: `play.ts:54`, `galaxy.ts:32,36`, `microsoft.ts:34-36`,
  `tracks_census.ts:93-94`; each feeds a header, a `readFile` or a token mint.
  The ring holds none of the six store names.
- `POST` and `DELETE` exist in one place, `play.ts:107,125,130`, reached only
  through `open_edit`. The census imports no edit road. `--deliver` appears
  nowhere in this ground.
- Scope held: `src/server.ts` and `src/http.ts` carry three import lines and
  three register lines each, `package.json` one script. Nothing was committed;
  `HEAD` is `1d1265d`, 2026-09-09, and nothing is staged.

## What was short

- `tracks_census.ts:344` — `--dry` returns before the held-seed readability
  check at `:354`, so a dry sheet drawn over an unreadable
  `testing-reports.json` shows the held rows gone though the write refuses.
- `galaxy.ts:200` — `listing_url` falls back to the content id where the portal
  names no package name; `store_tracks_deliverer.py:108-116` writes a non-empty
  `listing_url` over the register's cell.
- `play.ts:379`, `galaxy.ts:219`, `microsoft.ts:313` — a review with no date is
  seeded `1970-01-01T00:00:00.000Z`, and `testing_reports_deliverer.py:59` puts
  `said_at` into the open item's words.
- The Play edit stands behind `open_edit`, the conductor's standing choice, and
  the sending's own `play_tracks` line names `edits.insert` and `edits.delete`.
  The hand names it in its return and its journal.
- `ms_submission` is a sixth Microsoft tool the sending did not name; plan §5
  allows four to six.
- `tests/tracks.test.ts` is edited by a hand whose SCOPE list names only
  `tests/fixtures/{play,galaxy,microsoft}/*.json`; THE TASK names the proof
  script. On the record since round 2.
- Outside this ground and unchanged: `server_smoke.py` carries no store
  `whoami` call; `resonance-progenatrix/scripts/organs_tools.py:26` `ORDER`
  names eight lines, so the sixteen store tools do not reach the `tool` table;
  `tsconfig.json` includes `src/**/*.ts` only, so `npm run check` does not reach
  the proof script.
