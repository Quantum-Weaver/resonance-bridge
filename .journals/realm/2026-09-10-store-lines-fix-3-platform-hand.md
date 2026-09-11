# 2026-09-10 · store-lines · fix 3 · platform-hand

## What the work did

Mended the four polish defects a verifier found in team A's store lines and
census in `resonance-bridge`. Three files changed: `src/lines/play.ts`,
`src/census/tracks_census.ts`, `tests/tracks.test.ts`. `galaxy.ts`,
`microsoft.ts`, the fixtures, `src/server.ts`, `src/http.ts` and `package.json`
are as they were.

**The refusal in the note.** `playTrackRow`'s note per track is the track id,
the release status, the release lifecycle state and the release name. A
production track completed beside an alpha release Play rejected answers
`published` and the note reads `production completed 1.3.0 · alpha inProgress
REJECTED 1.5.0-alpha`. `043-the-beacons.sql:104` puts a refusal's reason in the
notes and `store_notes` is where rejections live.

**The 404 that read as an empty track.** `playReadTracksByRelease` returns
`{ tracks, answered, unanswered }`: a named track Play answered 404 for is named
in `unanswered`, a track that answered is named in `answered`, and only a track
carrying a release builds a `PlayTrack`. `playUnheld(packageName, trackIds)` is
the sentence for a package every named track answered 404 for.

**The row built from nothing.** `readPlay` writes no row for a package whose
`answered` is empty; it says `playUnheld`'s sentence and reads no reviews for
it. A package Play answers for with no release on any named track still builds
its row — `app_id` is then a read, not a guess. Twenty `play_app_id`s fill from
`src-tauri/tauri.conf.json`, and a realm Play holds nothing for no longer offers
one to the register.

**The gated edit.** The gate stands, the conductor's standing choice. Without
`open_edit`, `play_tracks` now reads Play's own named tracks — `qa`, `internal`,
`alpha`, `beta`, `production` — through `applications/{package}/tracks/{track}/
releases` with GETs alone and returns them beside `tracks_answered`,
`tracks_unanswered` and one sentence naming what only an edit reaches. With
`open_edit` it opens the edit, reads the whole list and deletes it in the same
breath, nothing committed. `play_testers` is unchanged: dry without `open_edit`,
minting no token, since Play serves tester groups only inside an edit.

**The proof script.** A stubbed `globalThis.fetch` that answers only the
androidpublisher root and throws on any other address feeds
`playReadTracksByRelease` the recorded `releases-list.json` for one track and
404 for the rest; the road's `answered`, `unanswered` and `tracks` are asserted,
and so is `playUnheld`'s sentence for a package no track answered for. Seven
assertions added, one changed.

## What stands

- `npm run check` (`tsc --noEmit`) — exit 0.
- `npx tsc --noEmit --ignoreConfig --module nodenext --moduleResolution nodenext
  --target es2022 --strict --skipLibCheck --types node tests/tracks.test.ts` —
  exit 0.
- `npx -y tsx tests/tracks.test.ts` — 146/146 assertions held.
- `python server_smoke.py` — `smoke complete — the server spoke, every line
  answered.`, exit 0.
- `npx tsx src/census/tracks_census.ts --dry` — the register read live through
  the anon door, twenty `play_app_id`s filled from disk, three shut doors named
  with their key and their click, no seed written.
- `organs_tools.read_line` parses all sixteen store tool name and description
  literals, one sentence each.
- Over an in-memory MCP client with no Play key on the ring, all five Play tools
  answer the shut-door sentence and make zero portal calls. With a key name
  present and every portal stubbed: `play_tracks` with no `open_edit` and with
  `open_edit` false make the token POST and five GETs and no other verb;
  `play_testers` with no `open_edit` answers the dry sentence and makes zero
  calls; `play_tracks` with `open_edit` true makes POST edits, GET tracks,
  DELETE edit. The proof file and its generated throwaway key were removed.

## What was short

- No store key is on the ring, so no store row has ever been read live. Every
  fixture is a docs shape, including `applications.tracks.releases.list`, on
  which the census's whole Play road rests.
- The census reads no Play testers and no custom Play track; both live inside
  the edit it does not open.
- `play.ts` still holds POST and DELETE against Play behind `open_edit`. Every
  other bridge line holds no write verb at all. Striking them takes `play_tracks`
  with `open_edit`, `play_testers`, `playEdit`, `withEdit`, `playReadTracks`,
  `playReadTesters`, `parsePlayTesters`, the `testers-get` fixture, the tester
  groups in the note and six assertions with it.
- `server_smoke.py` carries no store `whoami` call and `organs_tools.py`'s
  `ORDER` does not name `play`, `galaxy` or `microsoft`; both files are outside
  this hand's ground.
