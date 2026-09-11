# 2026-09-10 · joining · fix-3 · platform-hand

## What the work did

Three files changed in this repo, one seam trued across them.

**The register door has one definition and both censuses read it.**
`src/lines/tracks.ts` gains `REGISTER_KEY_NAMES`, `REGISTER_CLICKS` and
`registerDoor(keyName, until)` beside `PORTAL_CLICKS` and `shutDoor`: one sentence
naming the register key that is off the ring, the click that earns it, and what is
read until then.

`src/census/testing_channels_census.ts` drops its own `REGISTER_KEYS`,
`REGISTER_CLICKS` and `noRegister`, imports the two from `../lines/tracks.js`, and
keeps its own tail as `REGISTER_UNTIL`. Its sentence is unchanged, character for
character.

`src/census/tracks_census.ts` answered *"The register is unread:
SUPABASE_URL_KNOWLEDGE and SUPABASE_PUBLISHABLE_KEY_KNOWLEDGE are the anon door,
both on the bridge ring by your own hands."* — two keys, no click. It now reads the
first missing name through `readKeys(REGISTER_KEY_NAMES)` and answers
`registerDoor(missing, REGISTER_UNTIL)`, with its own tail: *"no store is read
without the register's app ids, and this census stops here."*

## What was verified

- `npm run check` → `tsc --noEmit`, exit 0. `npm run build` → `npm error Missing
  script: "build"`, exit 1; this repo's scripts are `dev check smoke census:tracks
  register`, and `check` is the check.
- `python server_smoke.py` → `handshake OK: resonance-bridge v0.2.0`, `tools
  registered (70)`, `play_whoami` / `galaxy_whoami` / `ms_whoami` each answering one
  shut-door sentence naming its key and its click, `smoke complete — the server
  spoke, every line answered.`, exit 0.
- `SUPABASE_URL_KNOWLEDGE= npx tsx src/census/tracks_census.ts --dry` → *"The
  register is unread: SUPABASE_URL_KNOWLEDGE is not on the bridge's ring — Supabase →
  the knowledge project → Project Settings → Data API → copy the Project URL → into
  resonance-bridge/.env by your own hands; no store is read without the register's app
  ids, and this census stops here."*
- `SUPABASE_PUBLISHABLE_KEY_KNOWLEDGE= npx tsx src/census/tracks_census.ts --dry` →
  the same shape naming that key and the API Keys click.
- `SUPABASE_URL_KNOWLEDGE= npx tsx src/census/testing_channels_census.ts --dry` and
  the same with the publishable key emptied → each one sentence naming that key, its
  click, and *"a channel's slug is read as resonance- and its name until then."*, and
  the census carries on, exit 0.
- `npx tsx src/census/tracks_census.ts --dry` → twenty `play_app_id` fills from
  `src-tauri/tauri.conf.json`, the register read live through the anon door, the three
  store doors one sentence each, both seeds printed with `"rows": []`, neither
  written, exit 0.
- `npx tsx src/census/testing_channels_census.ts --dry` → `guild: The AudHDities
  Sanctuary (1517902793288056852)`, `channels: 18 in the guild`, `register: 40 beacons
  · 40 channel names`, `no category named testing in the guild`, `0 channels under
  testing`, exit 0. No message text was read or printed; the guild holds no testing
  channel.
- `npx tsx src/census/tracks_census.ts` and `npx tsx src/census/testing_channels_census.ts`
  without `--dry` → the two seed files in `resonance-nectere/seeds/`, 0 rows each.
  `writeFile` in either census reaches only a seed path.
- Keys: the bridge's `.env` was read by path, never edited — mtime 2026-09-06
  19:27:28. None of the six store names stands on it. Twenty-nine ring values of eight
  characters or more were searched for in the two seeds and the three dry sheets: none
  appears.
- `grep -nE 'method: "(POST|PUT|PATCH|DELETE)"|--deliver'` over both censuses → no
  match. No hand passed `--deliver` anywhere.

## What is short

- `src/lines/play.ts:107` still holds a POST and a DELETE against androidpublisher
  behind the `open_edit` tool argument, reached from `play_tracks` and `play_testers`.
  Plan §2's portals table names `edits.insert → edits.tracks.list → edits.delete` as
  the only road to Play's tracks and §5 names `testers` among team A's tools; Play
  serves testers only inside an edit. Keeping it contradicts no line of the plan;
  striking it deletes a tool §5 names. It is the conductor's word, asked four rounds
  now. Unreachable today: no Play key is on the ring and all five Play tools answer
  the shut sentence in the smoke, with zero portal calls.
- `src/lines/play.ts:379`, `galaxy.ts:219`, `microsoft.ts:313`: a review the portal
  gave no time for is seeded `1970-01-01T00:00:00.000Z`. Mending it wants a nullable
  `said_at` in `docs/seeds/testing-reports.schema.json`, the three lines and
  `testing_reports_deliverer.py` together — five files in three repos, and a change to
  §4's row shape. Unreachable today; not taken.
- `src/lines/tracks.ts:25`, `:102`, `:131`: the three items §7 gives the lamps —
  `TrackStatus = BeaconStatus | null` widening §4's written row shape, Play's
  `internal` beside `qa`, and the Galaxy beta denylist answering `closed_testing` for
  an unknown beta word where an unknown content status answers `null`. Each is one
  line or one word from them; none is a hand's.
