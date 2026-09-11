# 2026-09-10 · store-lines · platform-hand

## What the work did

Built team A of the testing-tracks plan in `resonance-bridge`: three store read
lines, their registration on both doors, the tracks census, recorded fixtures
and a proof script.

- `src/lines/play.ts` — `registerPlay`, five tools: `play_whoami`,
  `play_tracks`, `play_testers`, `play_releases`, `play_reviews`. Key
  `GOOGLE_PLAY_SERVICE_ACCOUNT_JSON`, read by name at call time. Exports the
  parsers, the readers and `playTrackRow` / `playReportRows`.
- `src/lines/galaxy.ts` — `registerGalaxy`, five tools: `galaxy_whoami`,
  `galaxy_apps`, `galaxy_app`, `galaxy_beta`, `galaxy_comments`. Keys
  `SAMSUNG_GSD_SERVICE_ACCOUNT_ID` and `SAMSUNG_GSD_PRIVATE_KEY_PATH`.
- `src/lines/microsoft.ts` — `registerMicrosoft`, five tools: `ms_whoami`,
  `ms_apps`, `ms_flights`, `ms_submission_status`, `ms_reviews`. Keys
  `MS_STORE_TENANT_ID`, `MS_STORE_CLIENT_ID`, `MS_STORE_CLIENT_SECRET`.
- `src/server.ts` and `src/http.ts` — three imports and three `register*` calls
  each, in the shape of `registerDiscord`. Nothing else in either file.
- `src/census/tracks_census.ts` — reads `public.beacons` through the anon door,
  fills a missing `play_app_id` from `<home>/src-tauri/tauri.conf.json` on disk
  for beacons of type `app` or `game`, opens each store's door, and writes
  `resonance-nectere/seeds/store-tracks.json` and the stores' reviews into
  `resonance-nectere/seeds/testing-reports.json`, merging by id so rows already
  in that file keep their place and their words. `--dry` prints both and writes
  nothing. A shut door names its key and its click and the census carries on.
- `package.json` — one script, `census:tracks`.
- `tests/fixtures/play|galaxy|microsoft/*.json` — thirteen recorded-shape
  responses; `tests/tracks.test.ts` feeds every parser its fixtures and asserts
  the seed rows against the words of `043-the-beacons.sql`.

Every tool opens with the key check and returns `shutDoor(...)` from
`tracks.ts` when a name is absent. Transport is GET everywhere but one place:
Play serves no track outside an edit, so `playEdit` opens an ephemeral edit and
deletes it in the same breath around each track and tester read; nothing is
committed and nothing on a store changes. No `process.env` value reaches any
output — `play_whoami` names the service account email out of the key file, the
other two name only which of their key names the ring holds.

## What stands

- `npm run check` (`tsc --noEmit`) green.
- `npx -y tsx tests/tracks.test.ts` — 80/80 assertions held.
- `python server_smoke.py` green, 69 tools registered, the fifteen new ones
  among them.
- `npx tsx src/census/tracks_census.ts --dry` reads the register live (40 rows),
  fills fourteen `play_app_id`s from disk, and names three shut doors.
- `organs_tools.read_line` parses all fifteen name and description literals.
- The rows the fixtures produce validate against `docs/seeds/*.schema.json`.

## What was short

- No store key is on the ring, so all three doors are shut and no store row has
  ever been read live. The `applications.tracks.releases.list` shape, the Galaxy
  `betaTest` and `comment` shapes and the Microsoft analytics shapes are the
  docs' recorded shapes, unproven against a live portal.
- The census was run `--dry` only; writing the two seeds lands in
  `resonance-nectere`, outside this hand's ground.
- `server_smoke.py` carries no store `whoami` call; the file is outside this
  hand's ground.
- `organs_tools.py`'s `ORDER` does not yet name `play`, `galaxy` or `microsoft`;
  the file is outside this hand's ground.
