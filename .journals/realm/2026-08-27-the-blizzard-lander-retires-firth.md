# The Blizzard lander retires — 2026-08-27

Firth 🎻 (Fable, `claude-fable-5`), from the Weaver's sitting.

**Why.** THE-CARRY-GOES-LIVE, M2: the lander's logic now lives in the Weaver
app (`src-tauri/src/blizzard.rs`), with the keys on KP's device. He ran it
tonight — *"blizzard update running now, looks good"* · *"finished"* — and
had ruled, on the landers: *"yes retired from bridge once not needed(keys and
tools)."*

**What left.** `battlenet/` whole — `battlenet_character.py`,
`battlenet_collections.py`, `characters.csv`, `characters-2026-08-16.json`,
`enrich-cache.json` (git holds them). `BLIZZARD_CLIENT_ID` and
`BLIZZARD_CLIENT_SECRET` dropped from the keyring by a script that rewrote
every other byte unchanged and printed nothing but a count; the two names
retired in `.env.example` with a note. The Weaver's `npm run blizzard` script
is gone.

**What stays.** The media landers (`media/screen_lander.py`,
`media/games_lander.py`) and their TMDB and Twitch keys — until M3's door has
run, by the same ruling. The blueprint mirror under
`docs/blueprints/bridge/battlenet/` regenerates by its own tool.

**Held:** a tool retires when the road it served has been walked another way
and someone said so — not before, and not by a lamp's guess.
