# 2026-09-11 · play reads only · platform-hand

## What the work did

Removed the edit road from the Google Play line. Five files changed in this
repo — `src/lines/play.ts`, `src/census/tracks_census.ts`,
`tests/tracks.test.ts`, `tests/fixtures/play/**`, `README.md` — and one file
written in `resonance-progenatrix`:
`migrations/180-the-play-line-reads-only.sql`. `tracks.ts`, `galaxy.ts`,
`microsoft.ts`, `discord.ts`, `src/server.ts`, `src/http.ts`,
`server_smoke.py`, `package.json` and the nectere seeds are as they were.

**What is gone from `play.ts`.** `playEdit` (the `POST`/`DELETE` transport),
`withEdit`, `parseEditId`, `playReadTracks`, `playReadTesters`,
`parsePlayTesters`, `parsePlayTracks`, `playReadReleases`, the `DRY_TESTERS`
sentence and `dry()`, the `OPEN_EDIT` argument, and the `play_testers` and
`play_releases` tools. `grep -n "POST\|DELETE\|PATCH\|PUT" src/lines/play.ts`
returns nothing.

**What stands.** Three tools: `play_whoami`, `play_tracks`, `play_reviews`.
`play_tracks` reads `GET /applications/{package}/tracks/{track}/releases` once
per track — `qa`, `internal`, `alpha`, `beta`, `production` by default, or only
the track ids its `tracks` argument names, which is the read `play_releases`
made. It answers `tracks`, `tracks_answered`, `tracks_unanswered`, a sentence
naming what a custom closed track needs, and the tester sentence. `play_reviews`
is `GET /applications/{package}/reviews`. The token mint in `tracks.ts:298`
is the only POST any Play read still makes.

**The lifecycle mapping.** `PlayRelease` is `{ name, lifecycle, version_codes }`
— the door hands over `lifecycleState`, not a release status.
`LIFECYCLE_RELEASE` carries each ReleaseSummary lifecycle word and the release
word it stands for: `DRAFT` and `NOT_SENT_FOR_REVIEW` → `draft`, `IN_REVIEW` and
`APPROVED_NOT_PUBLISHED` → `inProgress`, `NOT_APPROVED` → `rejected`,
`PUBLISHED` → `completed`, `HALTED` → `halted`. `releaseState(release)` is that
lookup, and `playTrackRow` hands its answer and the raw lifecycle to
`tracks.ts`'s `playStatus`, which maps them onto the 043 words. A production
release whose lifecycle is `PUBLISHED` fills `published_version`.

**The seed row.** `playTrackRow(slug, packageName, tracks, testingUrl)` — the
tester-count argument is gone. `testers` is `null` and the note ends
`tester lists are inside an edit; not read by the bridge`. The census calls it
with four arguments and reads Play through `playReadTracksByRelease` and
`playReadReviews` alone.

**The fixtures.** `edits-insert.json`, `testers-get.json`, `tracks-list.json`
and `tracks-list-rejected.json` are deleted — no line parses those shapes now.
`releases-list-qa.json`, `releases-list-production.json` and
`releases-list-not-approved.json` are added beside `releases-list.json` and
`reviews-list.json`, all in the releases shape the GET road answers.

**The proof.** The Play cases in `tests/tracks.test.ts` are rebuilt on that
road: the six lifecycle words through `releaseState`, the stubbed portal
answering `qa`, `beta` and `production` and 404 for the rest, the whole row
from `playReadTracksByRelease`'s tracks, a single-track read, a refused alpha
beside a published production, and the reviews and report rows unchanged.
147/147 assertions hold.

**The count.** `organs_tools.py --count` reads `play 3`, `total 68`; a live
`tools/list` over stdio registers 68 and names `play_whoami, play_tracks,
play_reviews`. `README.md`'s Play rows carry three tools and the lifecycle
words; no other row was touched. `server_smoke.py` names no tool count and its
Play line is `play_whoami`, unchanged.

## What is left

- `migrations/180-the-play-line-reads-only.sql` is written and not applied. The
  `tool` table still holds `play_testers` and `play_releases` until it is run.
- `README.md`'s TOOLS heading says the server registers FIFTY-FOUR tools. It
  registers 68. The line is outside this task's Play-rows scope.
