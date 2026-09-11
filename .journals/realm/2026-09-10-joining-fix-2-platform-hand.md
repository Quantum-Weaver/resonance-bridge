# 2026-09-10 · joining · fix-2 · platform-hand

## What the work did

One file changed in this repo: `src/census/tracks_census.ts`.

**The held-seed sentence says what is on both paths.** `UNREADABLE_REPORTS` read
*"…it is left whole and this run's store rows are not written."* On the write path the
store rows are written one line earlier, at `store-tracks.json`; only the store review
rows bound for `testing-reports.json` are held back. The sentence is now *"…it is left
whole and this run's store review rows do not reach it."* — one definition, true on the
dry path and on the write path.

## What was verified

- `npm run check` -> `tsc --noEmit`, exit 0. `npm run build` -> `npm error Missing
  script: "build"`, exit 1; this repo's scripts are `dev check smoke census:tracks
  register` and `check` is the check.
- `npx -y tsx tests/tracks.test.ts` -> `146/146 assertions held`, exit 0.
- `python server_smoke.py` -> `handshake OK: resonance-bridge v0.2.0`, `tools
  registered (70)`, `play_whoami`, `galaxy_whoami` and `ms_whoami` each answering one
  shut-door sentence, `smoke complete — the server spoke, every line answered.`, exit 0.
- `npx tsx src/census/tracks_census.ts --dry` -> twenty `play_app_id` fills from
  `src-tauri/tauri.conf.json`, the register read live through the anon door, the three
  doors one sentence each naming the key and the click, both seeds printed with
  `"rows": []`, neither written, exit 0.
- `npx tsx src/census/testing_channels_census.ts --dry` -> `guild: The AudHDities
  Sanctuary (1517902793288056852)`, `channels: 18 in the guild`, `register: 40 beacons ·
  40 channel names`, `no category named testing in the guild`, `0 channels under
  testing`, `0 carried · 0 new · 0 rewritten · 0 rows in the seed`, exit 0. No message
  text printed; there were none to read.
- Both censuses without `--dry` wrote `resonance-nectere/seeds/store-tracks.json` (0
  rows) and `testing-reports.json` (0 rows); both validate against
  `docs/seeds/*.schema.json` under `Draft202012Validator` with the format checker, 0
  errors each.
- The mend proved: with `testing-reports.json` holding `not json at all`, the dry run
  ends on the sentence and prints no reports seed; the write path says `wrote …
  store-tracks.json — 0 rows` and then the same sentence. The file was read back
  unchanged (`not json at all`), restored, and both seeds rewritten clean.
- The four store lines' write verbs: `POST` and `DELETE` stand only at `src/lines/play.ts`
  :107, :125, :130 behind `open_edit`; the census imports `playReadTracksByRelease` and
  no edit road. No `--deliver` in this repo's ground; none was passed.

## What is short

- No store key is on the ring, so no parser has met a live portal; every store road is
  proved against recorded shapes.
- `play.ts:379`, `galaxy.ts:219` and `microsoft.ts:313` still answer
  `1970-01-01T00:00:00.000Z` for a review the portal gave no time for. Mending it wants
  a nullable `said_at` in `docs/seeds/testing-reports.schema.json`, the three lines and
  `resonance-nectere/hands/testing_reports_deliverer.py:59` together — five files in
  three repos, and a change to the seam's row shape.
- `tracks.ts:102` reads `internal` beside `qa`; `tracks.ts:131` answers `closed_testing`
  for a Galaxy beta word it does not know while an unknown content status answers
  `null`; `tracks.ts:25` widens the plan's written row shape with `TrackStatus =
  BeaconStatus | null`. The status mapping is the lamps' (plan §7).
- `play.ts` holds the only write verbs in `src/lines/`, behind `open_edit`.
