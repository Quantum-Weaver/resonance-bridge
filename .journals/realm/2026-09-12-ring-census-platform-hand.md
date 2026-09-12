# 2026-09-12 · ring census · platform-hand

## What the work did

One census added: `src/census/ring_census.ts`. Files changed in this repo:
`src/census/ring_census.ts` (new), `package.json` (one script), `README.md`
(one section). `.env`, `.env.example`, `src/server.ts`, every file under
`src/lines/`, `server_smoke.py`, `src/census/tracks_census.ts` and
`src/census/testing_channels_census.ts` are as they were.

**What it is.** A whole-ring reading in one command: `npm run census:ring`, or
`npx tsx src/census/ring_census.ts`, or `--json` for the same reading as one
JSON object. It carries no writing verb — no file is opened for writing and no
`--dry` flag exists.

**THE RING.** `.env` and `.env.example` are read by absolute path through
`fileURLToPath(new URL("../../.env", import.meta.url))`. `keyNames(text)`
returns a name and a stands/blank flag per line: the name is what stands left
of the first `=`, comment lines and lines without a name are dropped. Every
manifest name prints `present` or `missing`; every ring name the manifest does
not list prints `unlisted`; the counts close the part. No value is printed.

**THE LINES.** Eleven probes — grammar, vercel, resend, stripe, github,
discord, supabase, cloudflare, play, galaxy, microsoft. Each names the key
names its line needs, the names it gates on, the tool that reads it, and the
regex that claims its tool names. `openBridge()` builds an `McpServer`, calls
the eleven `registerX` functions from `src/lines/`, and connects a `Client`
over `InMemoryTransport.createLinkedPair()` — the tools are called in this
process; no server is spawned. `readKeys` from `src/lines/tracks.ts` decides
shut: a line with a gate name absent prints `shut` and the sentence its own
tool returns before any call leaves the machine. A line whose keys stand is
read live: the tool's text is parsed and one fact taken — beacon count, project
names, domain names, business name, login, bot username, token status, service
account, or `a token was minted`. A result the tool marked an error, text that
is not JSON, or a `token` field that is not `a token was minted` prints
`degraded` with that sentence, collapsed to one line and cut at 300 characters.
Tool counts come from `client.listTools()`; a tool no probe's regex claims is
named under the lines.

**THE FOOT.** Live, shut and degraded counts; then the shut-door sentence for
each shut line and the answer for each degraded one, as the line's own code
phrases them.

**What it read today.** 35 names in the manifest · 32 present · 3 missing
(`KNOWLEDGE_DB_PATH`, `SAMSUNG_GSD_SERVICE_ACCOUNT_ID`,
`SAMSUNG_GSD_PRIVATE_KEY_PATH`) · 3 on the ring the manifest does not list
(`TABLES_NEXT_PUBLIC_SUPABASE_URL`, `TABLES_NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY`,
`TABLES_SECRET_KEY_SUPABASE`). 10 lines live, 1 shut, 0 degraded. grammar 40
beacons in the register · vercel 1 project, audhdities · resend 1 domain,
audhdities.com verified · stripe AUDHDITIES LLC · github Quantum-Weaver ·
discord Resonance Bridge · supabase 2 projects, Superposition and
resonance-knowledge · cloudflare token active · play the service account
`play_whoami` names · microsoft a token was minted · galaxy shut on
`SAMSUNG_GSD_SERVICE_ACCOUNT_ID`. The eleven probes claim all 68 registered
tool names; none went unplaced.

**README.** A `The censuses` section under the standalone scripts table: the
three censuses in one table, then what the ring census prints and how to run
it.

**Not done.** `HANDS.md` carries no roster of the bridge's scripts, so no row
was added there. The whoami and status functions of grammar, vercel, resend,
stripe, github, discord, supabase and cloudflare are not exported from their
line modules — only `registerX` is — so the census reaches them through the
registered tool over an in-memory transport rather than by direct import. No
line file was edited to export them.

## Verification

- `npx tsc --noEmit` — clean.
- `npm run census:ring` — ran end to end; three parts and the foot printed.
- `npx tsx src/census/ring_census.ts --json` — one JSON object; `live 10`,
  `shut 1`, `degraded 0`.
- `python server_smoke.py` — `smoke complete — the server spoke, every line
  answered`.
- `grep -c "=" ` on the census output — `0`; no output line carries an `=` at
  all.
- `git status --short` — ` M README.md`, ` M package.json`,
  `?? src/census/ring_census.ts`.

Nothing committed, nothing pushed.

`readLine` guards `probe.read(data)` in its own try beside the `JSON.parse` one: a reader that throws returns that line as `degraded` carrying the error's message through `oneLine`, and the run goes on to the next line and reaches the foot.
