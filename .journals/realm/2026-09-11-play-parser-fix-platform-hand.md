# 2026-09-11 · play parser fix · platform-hand

## What the work did

Four defects mended in the Google Play line. Files changed in this repo:
`src/lines/play.ts`, `src/lines/tracks.ts`, `tests/tracks.test.ts`,
`tests/fixtures/play/releases-list.json`,
`tests/fixtures/play/releases-list-qa.json`,
`tests/fixtures/play/releases-list-production.json`,
`tests/fixtures/play/releases-list-not-approved.json`, `README.md` (line 72).
`galaxy.ts`, `microsoft.ts`, `discord.ts`, `src/census/tracks_census.ts`,
`src/server.ts`, `src/http.ts`, `server_smoke.py`, `package.json`, `.env` and
the nectere seeds are as they were.

**The parser.** `release(r)` reads the `ReleaseSummary` fields of
`ListReleaseSummariesResponse` (androidpublisher v3 discovery document,
revision 20260910): `track`, `releaseName`, `releaseLifecycleState`, and
`activeArtifacts[].versionCode` — each version code stringified, blanks
dropped. `PlayRelease` is `{ track, name, lifecycle, version_codes }`;
`track` is new. `r.name`, `r.lifecycleState` and `r.versionCodes` are gone
from the parser.

**The lifecycle map.** `LIFECYCLE_RELEASE` is keyed on the enum members the
discovery document names: `RELEASE_LIFECYCLE_STATE_DRAFT` and
`_NOT_SENT_FOR_REVIEW` → `draft`, `_IN_REVIEW` and `_APPROVED_NOT_PUBLISHED`
→ `inProgress`, `_NOT_APPROVED` → `rejected`, `_PUBLISHED` → `completed`.
`_UNSPECIFIED` and any member not keyed answer `null`. `lifecycleWord` trims
and upper-cases and nothing else. `halted` is gone from the map and from
`STANDING`, which is now `inProgress` and `completed`.

**`playStatus`.** Signature is `playStatus(trackId, release)` — the third
`lifecycle` argument is gone, and the return is `TrackStatus`. A `null` or
unnamed release state answers `null`. `inProgress` → `in_review`, `rejected`
→ `rejected`, `draft` → `planned`, on any track. Only a `completed` release
reads the track id: `qa` and `internal` → `internal_testing`, `beta` →
`open_testing`, `production` → `published`, every other id →
`closed_testing`. `packaged()` and `PLAY_ACTIVE`, used by `playStatus` alone,
are removed. `word()` still serves `galaxyStatus` and `microsoftStatus`.

**The seed row.** `playTrackRow` filters the `null` words out before
`furthest`, so a track with no named state adds no word and an all-null
reading answers `status: null`. `releaseVersion(r)` gives `testing_version`,
`published_version` and the note the release name, or the version codes when
the release carries no name. The note carries the lifecycle member verbatim.

**The fixtures.** The four `releases-list*.json` files are
`ListReleaseSummariesResponse` bodies: `track`, `releaseName`,
`releaseLifecycleState`, `activeArtifacts[{ versionCode }]`. `releases-list`
is the beta track — `_IN_REVIEW` 1.5.0-beta code 13, `_PUBLISHED` 1.4.1 code
12. `releases-list-qa` is `_PUBLISHED` 1.4.1 code 12. `releases-list-production`
is `_DRAFT` 1.6.0 code 15 above `_PUBLISHED` 1.3.0 code 9.
`releases-list-not-approved` is the alpha track, `_NOT_APPROVED` 1.5.0-alpha
code 14.

**The proof.** `tests/tracks.test.ts` imports `playStatus`. One case per
documented `releaseLifecycleState` and one for a release with no lifecycle
state; `playStatus` across `qa`, `internal`, `alpha`, `beta`, `production`
and a custom id for each release word and for `null`; the discovery-shape
`ReleaseSummary` (a `_PUBLISHED` production release with one active artifact
and no release name) through `parsePlayReleases` and `playTrackRow`; a track
whose release carries no lifecycle state answering `status: null`. The note
assertions carry the prefixed members.

**README.** Line 72 reads SIXTY-EIGHT tools; `tools/list` over stdio returns
68.

## Verification

- `npm run check` — clean.
- `npx -y tsx tests/tracks.test.ts` — `167/167 assertions held`.
- `python server_smoke.py` — `smoke complete — the server spoke, every line
  answered`; `tools registered (68)`.
- `grep -n "method" src/lines/play.ts` — no line.
- The discovery-shape `ReleaseSummary` through `parsePlayReleases` and
  `playTrackRow` yields `status: "published"`, `published_version: "13"`.

Nothing committed, nothing pushed.
