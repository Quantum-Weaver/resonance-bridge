# The tracks seam, read — 2026-09-10, round 2

## What was read

`src/lines/tracks.ts`, `docs/seeds/store-tracks.schema.json`,
`docs/seeds/testing-reports.schema.json`, `tests/fixtures/` (the README and the
six JSON responses), the six names on `.env.example`, and
`resonance-grammar/docs/sql/150-the-testing-public.sql`, against the second
sending and THE TESTING TRACKS PLAN sections 2, 3, 4, 5.

## What stands

- `playStatus` reads the track id first: `qa` and `internal` answer
  `internal_testing` whatever the lifecycle says (`src/lines/tracks.ts:99`).
  The lifecycle words still overlay `beta`, `production` and custom tracks.
- `microsoftStatus` answers `planned` for `Canceled` and `Cancelled`, with the
  flight check ahead of it (`:150-151`). No mapping answers `withdrawn`.
- The two fall-through returns of `none` each carry one line (`:133`, `:152`).
- Six fixtures under `tests/fixtures/`; every token value reads
  `FIXTURE-not-a-key`; no key, no path, no live value is recorded.
- `150-the-testing-public.sql:9` carries a comma; `statement_count` answers 3.
- One `process.env` read (`:202`), names only in the return; no `console`, no
  `argv`, no fs write, no `PATCH`/`PUT`/`DELETE`; one `fetch`, `POST` to the
  three token endpoints (`:263`). `.env` untouched, mtime 2026-09-06 19:27:28,
  and the six names are not on it.

## The checks re-run

    npm run check                 → tsc --noEmit, exit 0
    npm run build                 → npm error Missing script: "build"
    python server_smoke.py        → smoke complete, exit 0
    npx -y tsx <scratchpad>/proof.mts → checks: 123 - failures: 0
    python <scratchpad>/schemas.py    → both schemas lawful, both seeds validate,
                                        seven refusals
    statement_count 150 → 3 · 149 → 25

The proof stubbed `fetch` and served the six fixtures; each token function
returned the fixture token by `POST` to its own endpoint; the two error
fixtures threw the status and the slug only, with no description, no `AADSTS`
text, no secret and no path.

## What is short

- `TrackRow.status` has no word for a portal that named nothing: an unnamed
  answer reads `none`, which is also the 043 word for not pursued
  (`src/lines/tracks.ts:134`, `:153`). §3.3's "an empty read never erases"
  rests wholly on the tracks deliverer.
- `internal` stands beside `qa` (`:99`), a superset of §2's "the internal track
  is `qa`".
- The fixtures record the token endpoints; the store read shapes are unrecorded.
- `tests/fixtures/*.json` stand beyond the scope's file list and inside the
  sending's VERIFICATION.
