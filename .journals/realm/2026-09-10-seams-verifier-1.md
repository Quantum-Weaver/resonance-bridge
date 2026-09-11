# The tracks seam, read — 2026-09-10, round 1

## What was read

`src/lines/tracks.ts`, `docs/seeds/store-tracks.schema.json`,
`docs/seeds/testing-reports.schema.json`, `tests/fixtures/README.md`, the six
names on `.env.example`, and `resonance-grammar/docs/sql/150-the-testing-public.sql`,
against the sending and against THE TESTING TRACKS PLAN sections 2, 3, 4, 5.

## What stands

Every line of the sending is done or named short by the hand.

- The four seed types carry §4's fields, order and nullability whole;
  `DoorState` is `"read" | ` + backtick `unread: ${string}`.
- `BEACON_STATUSES` is the ten words of `043-the-beacons.sql:94-103`, in order.
- The three mappings are pure and total; over every input crossed
  (7 x 7 x 8, 6 x 6, 11 x 2) every return is inside `BEACON_STATUSES`.
- `rs256Jwt` signs with `crypto.createSign("RSA-SHA256")`; a 2048-bit throwaway
  key verifies with `crypto.verify` and a tampered payload is refused.
- `listingUrl` answers the three store addresses and `null` on an empty id.
- `readKeys` reads `process.env` at call time and returns names only; a set
  value never appears in the return. `shutDoor` is one sentence naming the key
  and the click, six of six.
- No key value can reach a log, an error, a seed or a return: one `process.env`
  read at `src/lines/tracks.ts:199`, no `console`, no file write, no path or
  body slice in any throw; a malformed PEM throws
  `error:1E08010C:DECODER routines::unsupported` and carries no key material.
- No write verb: `fetch` is called only with `method: "POST"` to the three token
  endpoints, `tokenPost` is not exported, there is no `argv`, no `--deliver`
  door, no fs write. `.env` is untouched (mtime 2026-09-06 19:27:28) and
  gitignored.
- Both schemas pass `Draft202012Validator.check_schema`; seeds built from the
  module's own types validate against them; a wrong status word, a wrong door,
  an extra property, a wrong kind, a wrong id prefix and a missing field are
  each refused.
- `150-the-testing-public.sql` follows `149`: header, the single
  `add column if not exists`, a `comment on column`, a VERIFY select with its
  expected answer. No UPDATE, DELETE, DROP, TRUNCATE or INSERT.

## The checks re-run

    npm run check   → tsc --noEmit, exit 0
    npm run build   → npm error Missing script: "build" (no such script in this repo)
    python server_smoke.py → smoke complete — the server spoke, every line answered. exit 0
    npx -y tsx <scratchpad>/proof.ts → 36 ok, 0 FAIL, "every proof stands"
    python <scratchpad>/schemas.py → both schemas lawful, both seeds validate, five refusals
    npx -y tsx <scratchpad>/mirror.ts | python <scratchpad>/mirror.py
        → the TypeScript-built seeds validate against both schemas

## What is short

- No fixture JSON stands under `tests/fixtures/`; the scope allowed only the
  README. The token-response parsing
  (`data.createdItem.accessToken ?? data.accessToken`,
  `data.access_token`) is therefore unproven against a recorded shape.
- Three branches sit beyond §4's letter, each named in the hand's return:
  `internal` beside `qa` (`src/lines/tracks.ts:104`), `Canceled` →
  `withdrawn` (`:148`), and `none` as the word for a store that said nothing
  (`:132`, `:150`). §3.3 binds the deliverer that reads them.
- The column comment in `150-the-testing-public.sql:9` carries a semicolon, so
  the seed chain's dry sheet counts four statements where three stand; the file
  is sent whole, so the run is unaffected.

## What was not verifiable

The three token endpoints and the Galaxy token's `createdItem` shape: no key is
on the ring, no live portal was called, and no fixture records them.
