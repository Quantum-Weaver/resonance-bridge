# 2026-09-10 · joining · verifier-3

## What was read

`src/lines/tracks.ts`, `src/census/tracks_census.ts` and
`src/census/testing_channels_census.ts` — the three files this round changed here —
against the joining's sending and plan §§2-5, and the ground the road runs on:
`src/lines/play.ts`, `galaxy.ts`, `microsoft.ts`, `server_smoke.py`,
`docs/seeds/*.schema.json`, `tests/`.

## What was verified

- `npm run check` -> `tsc --noEmit`, exit 0. `npm run build` -> `npm error Missing
  script: "build"`, exit 1; this repo's scripts are `dev check smoke census:tracks
  register`.
- `npx -y tsx tests/tracks.test.ts` -> `146/146 assertions held`, exit 0.
- `python server_smoke.py` -> `handshake OK: resonance-bridge v0.2.0`, `tools
  registered (70)`, `play_whoami` / `galaxy_whoami` / `ms_whoami` each one shut-door
  sentence naming its key and its click, `smoke complete — the server spoke, every
  line answered.`, exit 0. The three lines are added to `checks` in the
  `discord_whoami` shape; `git diff server_smoke.py` is those three lines and nothing
  else.
- `npx tsx src/census/tracks_census.ts --dry` -> twenty `play_app_id` fills, the
  register read live through the anon door, the three shut doors one sentence each,
  both seeds printed with `"rows": []`, neither written, exit 0.
- `SUPABASE_URL_KNOWLEDGE=` and `SUPABASE_PUBLISHABLE_KEY_KNOWLEDGE=` against the
  tracks census -> one sentence naming that key, its click and *"no store is read
  without the register's app ids, and this census stops here."*, exit 1. The same two
  against the channels census -> that key, that click and *"a channel's slug is read
  as resonance- and its name until then."*, and the census carries on, exit 0. The
  channels sentence is character for character what stood before the refactor.
- `npx tsx src/census/testing_channels_census.ts --dry` -> `guild: The AudHDities
  Sanctuary (1517902793288056852)`, `channels: 18 in the guild`, `register: 40 beacons
  · 40 channel names`, `no category named testing in the guild`, `0 channels under
  testing`, exit 0. No message text reaches the console: the per-row line carries the
  id, the kind and the time (`:302`).
- Keys: `process.env` is read at `tracks.ts:206` (into `readKeys`, names only),
  `tracks_census.ts:103-104` and `testing_channels_census.ts:104,125-126,258,262` —
  each into a request header, a URL or a truthiness test. `registerDoor` carries a key
  NAME and a click, never a value. Every ring value of eight characters or more was
  searched for in the two seeds and the three dry sheets: none appears.
- Writes: `grep -rnE 'method:\s*"(POST|PUT|PATCH|DELETE)"' src/` answers three lines —
  the token POST at `tracks.ts:298`, `playEdit` at `play.ts:107`, and the standing
  supabase line. Neither census holds a non-GET; every fs write in either reaches a
  seed path.
- `.env` mtime 2026-09-06 19:27:28, gitignored, and none of the six store names stands
  on it. Nothing staged or committed; HEAD 1d1265d.

## What is short

- `src/lines/play.ts:107` holds a POST and a DELETE against androidpublisher behind
  the `open_edit` tool argument. Unreachable today — no Play key on the ring, all five
  Play tools answer the shut sentence in the smoke with zero portal calls — and it
  becomes a live write door with no `--deliver` the day the key lands. Named by five
  hands; the conductor's ruling.
- `play.ts:379`, `galaxy.ts:219`, `microsoft.ts:313` still seed
  `1970-01-01T00:00:00.000Z` for a review the portal gave no time for.
- `tracks.ts:25`, `:102`, `:131` stand as five rounds left them; plan §7 gives the
  status mapping and the seed shapes to the lamps.

Nothing was changed, staged or committed here. No `--deliver` was passed; no store
portal was called.
