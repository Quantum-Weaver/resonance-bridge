# The lines table, the tool roster, the play-track skill — 2026-09-10

## What is

`resonance-bridge/README.md` carries three new rows in the DATABASES table —
Google Play, Galaxy Store, Microsoft Store, in the registration order of
`src/server.ts` (after Cloudflare, before Superposition) — and sixteen new
rows in the TOOLS table, after `cloudflare_list_rulesets` and before the
Standalone scripts heading: `play_whoami` · `play_tracks` · `play_testers` ·
`play_releases` · `play_reviews`, `galaxy_whoami` · `galaxy_apps` ·
`galaxy_app` · `galaxy_beta` · `galaxy_comments`, `ms_whoami` · `ms_apps` ·
`ms_flights` · `ms_submission_status` · `ms_submission` · `ms_reviews`. Each
row's wording is drawn from that tool's own description in `src/lines/play.ts`,
`galaxy.ts` and `microsoft.ts`. The three DATABASES rows state each line's
transport, what it reads, the tool count, and that the line is shut until its
key names are on the ring — none of the six store keys stands on
`resonance-bridge/.env` today.

`resonance-chamber/.claude/skills/play-track/SKILL.md` gains one section,
`## THE API ROAD`, after the existing sections: the service account is a user
the Console invites, quoted verbatim from `src/lines/tracks.ts:163-166`; the
six key names and their address on `resonance-bridge/.env.example:55-60`
(names only); the census command
(`npx tsx resonance-bridge/src/census/tracks_census.ts [--dry]` /
`npm run census:tracks`); the deliverer command
(`python resonance-nectere/hands/store_tracks_deliverer.py <seed>
[--deliver]`) and that `--deliver` is KP's word alone; the register's eight
columns per store, cited to `resonance-grammar/docs/sql/043-the-beacons.sql:108-148`;
and that the Play tester link is not in the API and is placed into
`play_testing_url` by hand.

## What was verified

- `git diff --stat` on both files: README.md +19 lines, SKILL.md +34 lines —
  additions only, nothing else in either file touched.
- Every address cited was re-read against the file it names before being
  written: `src/lines/tracks.ts:163-166` (the click path, concatenated to
  confirm it reads as quoted), `.env.example:55-60` (the six store key
  lines), `package.json` (`census:tracks` script), `src/census/tracks_census.ts:4-5`
  (the two run lines), `hands/store_tracks_deliverer.py:3-4` (the two run
  lines), `043-the-beacons.sql:108-148` (the eight per-channel columns and
  `store_notes`).
- The sixteen tool rows' wording checked word-for-word against each tool's
  `server.tool(...)` description in `play.ts`, `galaxy.ts`, `microsoft.ts`.
- Nothing committed; no other file read for editing.

## What is short

The TOOLS table's intro line above the table still reads "the server
registers FIFTY-FOUR tools" — true of the table before this hand's sixteen
rows, false of it after. Correcting the count would mean either rewriting a
dated claim ("recounted 2026-09-02... FIFTY-FOUR tools") to say something
that recount did not find, or adding a new dated claim of my own — both
outside a document line that only states what is, and outside this hand's
named scope (three rows in the lines table and the tool roster). Left
untouched; the line and the file are named here so the count is not read as
settled.
