# 2026-09-06 — old-house paths made relative

Realm journal · `resonance-bridge` · 2026-09-06 · Fable (`claude-fable-5-1`).

Every hardcoded old-house path in the repo's code now resolves from the file's
own location. No drive letter remains in code.

## Anchoring

- TypeScript (`src/`): `const HOUSE = fileURLToPath(new URL("../../", import.meta.url))`
  — the folder that contains the realms. `src/http.ts` also defines
  `CONSTELLATION = path.join(HOUSE, "resonance-chamber", "constellation")`.
- Python at the repo root: `HOUSE = Path(__file__).resolve().parents[1]`.
- Python in `listening/` and `seeding/`: `HOUSE = Path(__file__).resolve().parents[2]`;
  every former absolute path is `HOUSE / "<realm>" / ...`.
- `package.json` `register` script: `../resonance-bridge/src/server.ts`, resolved
  from any realm root.

## Files changed

- `src/http.ts` — HOUSE, CONSTELLATION; AETHELRED_JOURNALS, AETHELRED_HOME,
  FABLE_LANES, the knowledge.db default, the three registry candidates.
- `src/server.ts` — `import path`; HOUSE; the knowledge.db default.
- `package.json` — the `register` script.
- `grammar_inventory.py` — HOUSE; `out_dir`.
- `listening/ask_the_lattice.py`, `emoji_census.py`, `listen_beacons.py`,
  `listen_lattice.py`, `listen_lattice2.py`, `listen_lattice3.py`,
  `listen_lattice4.py`, `no_rungs_census.py`, `sonnet_asks_the_lattice.py`
  — HOUSE; `BRIDGE = HOUSE / "resonance-bridge"`.
- `seeding/atoms_dump.py` — HOUSE; the `.env` read; `out`.
- `seeding/dailies_scramble_gen.py` — HOUSE; EXPORTS, DEFAULT_OUT.
- `seeding/grammar_seeder.py` — HOUSE; SHELF.
- `seeding/lattice_wave2_gen.py` — HOUSE; EXPORTS, WAVE1, OUT.
- `seeding/lattice_wave3_gen.py` — HOUSE; GAIA, WAVE1, OUT.
- `seeding/lattice_wave4_gen.py` — HOUSE; GAIA, EXPORTS, OUT.
- `seeding/lattice_wave5_gen.py` — HOUSE; GAIA, OUT.
- `seeding/lattice_wave6_gen.py` — HOUSE; EXP, OUT.

## Left as is

- `src/http.ts` `switchboardFetch`: the Claude projects folder `c---superposition`
  is the session store's own slug for the old house; the logs it holds still
  stand under that name.
- `superposition` without the underscore names the Supabase project
  (`src/lines/supabase.ts`, the `seeding/lattice_wave2_gen.py` docstring, the
  `supabase-exports/superposition` folder).
- `docs/`, `.journals/`, and `.md`/`.txt`/`.html` files are documents, not code;
  not changed here.
