# 2026-09-10 · store-lines · fix 2 · platform-hand

## What the work did

Mended the defects a verifier found in team A's store lines and census in
`resonance-bridge`. Nothing outside `src/lines/play.ts`, `galaxy.ts`,
`microsoft.ts`, `src/census/tracks_census.ts`, `tests/tracks.test.ts` and the
store fixtures was touched.

**The Play edit envelope.** `play_tracks` and `play_testers` are dry until
`open_edit` is passed. Without it each answers one sentence naming the exact
transport it holds back — the POST that opens the edit, the GET that reads its
tracks, the DELETE that removes it — and mints no token. The census no longer
opens an edit at all: `playReadTracksByRelease` reads each of `qa`, `internal`,
`alpha`, `beta` and `production` through
`applications/{package}/tracks/{track}/releases`, a GET, and keeps a track that
carries a release. A track Play does not hold answers 404 and is skipped; every
other refusal is raised. Custom closed tracks are named only inside an edit, so
the census does not see them, and it reads no testers.

**The author that could be empty.** `parsePlayReviews`, `parseGalaxyComments`
and `parseMsReviews` each take the first name the portal actually wrote and fall
to the store's own word for one who left none — `??` passed the empty string
through and `said_by` requires one character in
`docs/seeds/testing-reports.schema.json`. Three fixtures gained a recorded
review with a blank author and words in it; the proof script asserts every
report row carries a name.

**One word per channel.** `PLAY_REACH` orders the ten `043` words by how far a
package has reached on the store, published last, with a refusal or a withdrawal
below `in_review`. A production track completed beside an alpha release Play
rejected now answers `published`; a rejected track alone still answers
`rejected`. The proof script asserts `PLAY_REACH` holds every `043` word once.

**The disk fill.** The `beacon_type` filter on the missing `play_app_id` fill is
gone; every beacon whose `home` carries `src-tauri/tauri.conf.json` fills. Twenty
fills where there were fourteen.

**The Microsoft versions.** `parseMsSubmission` and `msReadSubmission` read a
submission itself — the application's or a flight's — for the package versions
it carries; `ms_submission` is the tool over them, sixteen store tools in all.
`microsoftTrackRow` fills `published_version` from the app's last published
submission and `testing_version` from the flight's, both null where no
submission was read. Two recorded fixtures,
`microsoft/application-submission.json` and `flight-submission.json`.

**The unproved fixture.** `parseEditId` is the edit id read, and
`play/edits-insert.json` is fed to it.

Tool descriptions that ran to three sentences are two, the shape `discord.ts`
carries.

## What stands

- `npm run check` (`tsc --noEmit`) — exit 0.
- `npx tsc --ignoreConfig --noEmit --target es2022 --module nodenext
  --moduleResolution nodenext --strict --skipLibCheck --types node
  tests/tracks.test.ts` — exit 0.
- `npx -y tsx tests/tracks.test.ts` — 139/139 assertions held.
- `python server_smoke.py` — green, 70 tools, the sixteen store tools among them.
- `npx tsx src/census/tracks_census.ts --dry` — the register read live through
  the anon door, twenty `play_app_id`s filled from disk, three shut doors named,
  no seed written.
- `organs_tools.read_line` parses all sixteen name and description literals, one
  sentence each.
- The rows the fixtures build validate against both `docs/seeds/*.schema.json`.
- With a key name present and the tool called, `play_tracks` and `play_testers`
  answer the dry sentence and reach no portal — proved over stdio against the
  real server with a key name pointing at a file that does not exist.

## What was short

- No store key is on the ring, so no store row has ever been read live. The
  shapes of `applications.tracks.releases.list`, the Galaxy `betaTest`,
  `contentInfo` and `comment`, and the Microsoft analytics and submission
  responses are the docs' shapes.
- The census reads no Play testers and no custom Play track; both live inside
  the edit it does not open.
- `server_smoke.py` carries no store `whoami` call and `organs_tools.py`'s
  `ORDER` does not name `play`, `galaxy` or `microsoft`; both files are outside
  this hand's ground.
