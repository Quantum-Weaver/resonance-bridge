# The shelf leaves — 2026-09-09

## What is

`resonance-bridge/seeding/` does not exist. Its nineteen files stand at
`resonance-nectere/chains/`; git holds the bridge's history of them.

At the repo root the standalone scripts are `grammar_inventory.py`,
`verify_terms.py`, `knowledge_sql.py`, `repos_snapshot.py`, and
`THE-TRAIL-seed.md` beside them.

Documents changed:

- `README.md` — the standalone-scripts table drops its `seeding/atoms_dump.py`
  and `seeding/` rows.
- `MOVED.md` — the seeding-shelf row is gone; `generate_blueprint.py` stands.
- `FEATURE-BOARD.md` — the kimi room, the DeepSeek room, the seeding
  root-tidy, the two Battle.net items and the media lane are gone; the
  numbering closes at 5.
- `.env.example` — `DEEPSEEK_API_KEY`, `KIMI_CODE_API_KEY` and
  `MOONSHOT_API_KEY` comments say what the key is for; the TMDB/Twitch
  block is gone.

`HANDS.md` is untouched: it carries hands in their own words.

## What was verified

- `npm run check` — `tsc --noEmit`, clean.
- `python server_smoke.py` — "smoke complete — the server spoke, every
  line answered."
- `grep -rn "seeding/"` across this repo returns `HANDS.md` and
  `docs/blueprints/`, both untouched.
