# 2026-09-10 · joining · platform-hand

## What the work did

Four files changed in this repo: `server_smoke.py`, `src/census/tracks_census.ts`,
`src/lines/galaxy.ts`, `src/lines/tracks.ts`.

**The smoke calls the three store lines.** `server_smoke.py`'s `checks` list gains
`("play_whoami", {})`, `("galaxy_whoami", {})` and `("ms_whoami", {})` after
`supabase_list_projects`, in the shape of the `discord_whoami` line above it and in
the registration order of `src/server.ts:62-64`. Each answers its shut-door sentence;
the breath stays green.

**A dry sheet says what the write path would refuse.** `tracks_census.ts` held the
unreadable-held-seed sentence in the write path only, so `--dry` printed a reports
seed with the held rows gone and said nothing. The sentence now stands once, as
`UNREADABLE_REPORTS` beside `dry`, and both paths say it: the dry run prints the
tracks seed, names the unreadable file, and stops before printing a reports seed it
would not write.

**A Galaxy listing address is a listing address or nothing.** `galaxyTrackRow`'s
`listing_url` fell back to the content id when the portal named no package name,
which is not a listing address and which `store_tracks_deliverer.py` would write over
the register's cell. It is now `app.package_name ? listingUrl("galaxy", app.package_name) : null`.

**A malformed key answers in the house's voice.** `rs256Jwt` let OpenSSL's own words
out of `signer.sign` — `error:1E08010C:DECODER routines::unsupported`. The sign is
wrapped and answers one sentence: *The private key named on the ring is not an RSA
private key node can sign with.* It carries no key material and no path.

## What was verified

- `npm run check` -> `tsc --noEmit`, exit 0. `npm run build` -> `npm error Missing
  script: "build"`, exit 1; this repo has no build script and `check` is the check.
- `python server_smoke.py` -> `handshake OK: resonance-bridge v0.2.0`, `tools
  registered (70)`, the three store whoami calls each answering one shut-door
  sentence, `smoke complete — the server spoke, every line answered.`, exit 0.
- `npx -y tsx tests/tracks.test.ts` -> `146/146 assertions held`, exit 0.
- `npx tsx src/census/tracks_census.ts --dry` -> twenty `play_app_id` fills, the three
  shut doors one sentence each, both seeds printed, `rows: []`, nothing written, exit 0.
- `npx tsx src/census/testing_channels_census.ts --dry` -> `guild: The AudHDities
  Sanctuary (1517902793288056852)`, `channels: 18 in the guild`, `register: 40 beacons
  · 40 channel names`, `no category named testing in the guild`, `0 channels under
  testing`, `0 carried · 0 new · 0 rewritten · 0 rows in the seed`, exit 0.
- `npx tsx src/census/tracks_census.ts` and `... testing_channels_census.ts` without
  `--dry` wrote `resonance-nectere/seeds/store-tracks.json` (0 rows) and
  `testing-reports.json` (0 rows). Both validate against `docs/seeds/*.schema.json`
  under `Draft202012Validator` with the format checker: 0 errors each.
- The dry mend proved: with an unreadable `testing-reports.json` in place, the dry run
  ends `G:/materia/resonance-nectere/seeds/testing-reports.json is present and
  unreadable as JSON — it is left whole and this run's store rows are not written.`
  The file was restored from a copy and the census wrote nothing.
- The two line mends proved by a scratchpad module: galaxy `listing_url` with a package
  name -> `https://galaxystore.samsung.com/detail/com.audhdities.echoes`, with none ->
  `null`; a malformed key -> the one house sentence, carrying no key body.

## What is short

- No store key is on the ring, so no parser has met a live portal. Every store road is
  proved against recorded shapes only.
- `play.ts:379`, `galaxy.ts:219` and `microsoft.ts:313` still answer
  `1970-01-01T00:00:00.000Z` for a review the portal gave no time for, and the reports
  deliverer puts `said_at` verbatim into the item's words. Mending it wants a nullable
  `said_at` in `docs/seeds/testing-reports.schema.json`, the three lines and the
  deliverer's line together — five files in three repos.
- `playStatus` reads `internal` beside `qa`, and `galaxyStatus` answers `closed_testing`
  for a beta word it does not know while an unknown content status answers `null`.
