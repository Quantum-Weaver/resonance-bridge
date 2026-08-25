"""
dailies_scramble_gen.py - build athena's daily WORD SCRAMBLE puzzles from
the live Resonance Grammar.

Founded 2026-08-24 by Kerf (Opus) at KP's word - the dailies sitting the
conducting line reserved ("i will open a fresh window for Opus to create
the daily games"). His roster, verbatim, 2026-07-30:

    "we also want to offer crossword, word find, word scramble, even
     sudoku if possible, although it is numbers, the reast should be
     derivable from the resonance grammar. word games were my warm
     place, but i like words, not everyone is a poet, so i think we
     find a way to blend all the comfort game concepts."

The Grammar's own molecule says what this form IS (102-the-molecules.sql):
    WordScramble - "One word disarranged, its definition standing as the hint."

READ-ONLY on every base. It writes ONE thing and only when asked: a DRAFT
.sql file for KP to run at his own dashboard. A lamp never runs it.

THE LAWS THIS SERVES (they are why the filters exist, not decoration):
  - The clue may never contain its own answer. 39.4% of the corpus does.
  - A scramble with two lawful answers is not a puzzle. Anagram collisions
    are removed as a pool, not as a preference.
  - No streaks, no dates, no counting. There is no puzzle_date column by
    design: a number has no "today", so nobody can be late for #47.
  - The vessel is never recorded. This file emits puzzle CONTENT only.

Usage:
    python dailies_scramble_gen.py                    # review, writes nothing
    python dailies_scramble_gen.py --categories consciousness,creation
    python dailies_scramble_gen.py --emit 60 --categories consciousness
"""

import argparse
import json
import random
import re
import sys
import urllib.request
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
BRIDGE = HERE.parent
EXPORTS = Path(r"C:\_superposition\resonance-grammar\exports")
DEFAULT_OUT = Path(r"C:\_superposition\AudHDities\docs\sql")

MIN_LEN, MAX_LEN = 4, 9
MASK = "\u2014\u2014\u2014"


def load_env() -> dict:
    env = {}
    p = BRIDGE / ".env"
    if not p.is_file():
        return env
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def fetch_live(url, key, table, select="*"):
    rows, page = [], 0
    while True:
        req = urllib.request.Request(
            f"{url}/rest/v1/{table}?select={select}&limit=1000&offset={page * 1000}",
            headers={"apikey": key, "Authorization": f"Bearer {key}"},
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            batch = json.loads(r.read().decode("utf-8"))
        rows.extend(batch)
        if len(batch) < 1000:
            return rows
        page += 1


def load_corpus():
    """Live first; the newest dated export is the fallback. Says which it used."""
    env = load_env()
    url = env.get("SUPABASE_URL_KNOWLEDGE", "")
    key = (env.get("SUPABASE_PUBLISHABLE_KEY_KNOWLEDGE", "")
           or env.get("SUPABASE_ANON_KEY_KNOWLEDGE", ""))
    if url and key:
        try:
            atoms = fetch_live(
                url, key, "atoms",
                "id,atom_word,category_name,atom_type,status,definition")
            sens = fetch_live(url, key, "sensory_lexicon", "atom_word,emoji")
            print(f"corpus: LIVE base - {len(atoms)} atoms")
            return atoms, {s["atom_word"]: s.get("emoji") for s in sens}
        except Exception as e:
            print(f"live read failed ({type(e).__name__}) - falling back to export")
    snaps = sorted(EXPORTS.glob("grammar-export-*.json"))
    if not snaps:
        sys.exit("no live base and no export on disk")
    d = json.loads(snaps[-1].read_text(encoding="utf-8"))
    atoms = d["tables"]["atoms"]
    sens = d["tables"].get("sensory_lexicon", [])
    print(f"corpus: {snaps[-1].name} - {len(atoms)} atoms")
    return atoms, {s["atom_word"]: s.get("emoji") for s in sens}


MAX_CLUE = 180


def first_sentence(text):
    """The shortest honest cut. A definition written for a dictionary can run
    three clauses deep; a clue that long stops being comfort and starts being
    homework. Colons and dashes end a thought as truly as full stops do -
    lodestone's whole clue is "The stone that points", and everything after
    the colon is the house's own engineering."""
    t = " ".join((text or "").split())
    cuts = [i for i in (t.find(sep) for sep in (". ", "; ", ": ", " \u2014 ", " - "))
            if i >= 18]
    if cuts:
        return t[:min(cuts)].rstrip(" \u2014-;:,").strip() + "."
    return t


def stem(w):
    return w[:max(4, len(w) - 2)]


def mask_clue(word, definition):
    """Mask the answer and any same-family token. Belt AND braces: the pool
    already rejects a definition containing the answer, but 'pausing' does
    not contain 'pause' and would still hand the word over."""
    s = first_sentence(definition)
    st = stem(word)
    out, hits = [], 0
    for tok in re.split(r"(\W+)", s):
        if tok.isalpha() and tok.lower().startswith(st):
            out.append(MASK)
            hits += 1
        else:
            out.append(tok)
    return "".join(out), hits


def scramble(word, seed):
    """Deterministic, never the identity, and the most-displaced of 40 tries
    so the puzzle is not one swap from solved."""
    rng = random.Random(f"athena-dailies::{seed}")
    letters = list(word)
    best, best_score = None, -1
    for _ in range(40):
        cand = letters[:]
        rng.shuffle(cand)
        if "".join(cand) == word:
            continue
        score = sum(1 for a, b in zip(cand, letters) if a != b)
        if score > best_score:
            best, best_score = cand[:], score
    return "".join(best) if best else "".join(reversed(letters))


def build(atoms, emoji, categories=None):
    pool, rejected = [], Counter()
    for a in atoms:
        w = (a.get("atom_word") or "").strip()
        d = (a.get("definition") or "").strip()
        cat = a.get("category_name") or "(none)"
        if not w.isalpha() or not w.islower():
            rejected["not a plain lowercase word"] += 1
            continue
        if not (MIN_LEN <= len(w) <= MAX_LEN):
            rejected[f"length outside {MIN_LEN}-{MAX_LEN}"] += 1
            continue
        if a.get("status") != "published":
            rejected["not published"] += 1
            continue
        if not d or "[DRAFTED" in d:
            rejected["no real definition"] += 1
            continue
        if w in d.lower():
            rejected["clue contains its own answer"] += 1
            continue
        if categories and cat not in categories:
            rejected["category not chosen"] += 1
            continue
        clue, _ = mask_clue(w, d)
        if len(clue) < 22:
            rejected["clue too short to be a clue"] += 1
            continue
        if len(clue) > MAX_CLUE:
            rejected["clue too long to be comfort"] += 1
            continue
        pool.append({"id": a.get("id"), "word": w, "category": cat,
                     "atom_type": a.get("atom_type"), "clue": clue,
                     "emoji": emoji.get(w)})

    by_sig = defaultdict(list)
    for p in pool:
        by_sig["".join(sorted(p["word"]))].append(p)
    collisions = {s for s, v in by_sig.items() if len(v) > 1}
    clean = [p for p in pool if "".join(sorted(p["word"])) not in collisions]
    rejected["anagram collision (two lawful answers)"] = len(pool) - len(clean)

    for p in clean:
        p["scrambled"] = scramble(p["word"], p["word"])
    clean.sort(key=lambda p: (p["category"], p["word"]))
    return clean, rejected


def sql_escape(s):
    return (s or "").replace("'", "''")


HEADER = """-- 022-the-dailies-DRAFT.sql - athena's first daily: WORD SCRAMBLE
-- Generated {today} by resonance-bridge/seeding/dailies_scramble_gen.py
-- Corpus: {corpus}
--
-- KP's roster, verbatim (e4-the-play-study-bus.md:1275-1279):
--   "crossword, word find, word scramble, even sudoku if possible...
--    word games were my warm place, but i like words, not everyone is a
--    poet, so i think we find a way to blend all the comfort game concepts."
--
-- The form is named by the Grammar's own molecule, WordScramble:
--   "One word disarranged, its definition standing as the hint."
-- puzzle_form values are the four molecules' kebab_case renderings -
-- referenced from canon, never forked: word-scramble, word-find,
-- cross-word, wordoku.
--
-- RUN THIS BY YOUR OWN HAND, one step at a time. No lamp runs it.

-- ---------------------------------------------------------------
-- STEP 1 - the table
-- ---------------------------------------------------------------
create table if not exists public.daily_puzzles (
  id            uuid primary key default gen_random_uuid(),
  slug          text not null unique,
  puzzle_form   text not null default 'word-scramble',
  display_order integer not null default 0,
  solution      text not null,
  scrambled     text not null,
  clue          text not null,
  atom_word     text not null,
  atom_id       uuid,
  source_emoji  text,
  payload       jsonb,
  status        public.content_status not null default 'draft',
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now()
);

comment on table public.daily_puzzles is
  'Athena''s dailies - puzzle CONTENT only. Nothing vessel-scoped may ever be
   added to this table, and no companion vessel_* table may be born from it:
   what a vessel solved is device-local and has no row anywhere. There is
   deliberately NO date column - a number has no today, so nobody can be late
   for a puzzle. Play study round 3, 2026-07-30: a daily is a gift when it
   keeps, does not count you, and is complete in itself; the ledger unbuilt,
   not merely hidden.';

comment on column public.daily_puzzles.clue is
  'DERIVED from the Grammar atom''s definition, not a copy of it: first
   sentence, with the answer and its word-family masked. The Grammar keeps one
   definition per object; this is a puzzle artifact that REFERENCES it through
   atom_word and atom_id.';

comment on column public.daily_puzzles.display_order is
  'Ordering only. Never a date, never a sequence a vessel can be behind on.';

-- ---------------------------------------------------------------
-- STEP 2 - the doors. GRANT before RLS; the policy takes NO "to" clause.
-- The false-empty that seed 009 healed across seven tables came from a
-- policy whose role list said {{authenticated}}. Do not add one.
-- ---------------------------------------------------------------
grant select on public.daily_puzzles to anon, authenticated;
alter table public.daily_puzzles enable row level security;
drop policy if exists "daily_puzzles are readable by anyone" on public.daily_puzzles;
create policy "daily_puzzles are readable by anyone"
  on public.daily_puzzles for select
  using (status = 'published');

-- ---------------------------------------------------------------
-- STEP 3 - tell gaia what this table is, and that it is READ-ONLY.
-- The write verbs false means the POST/PUT/DELETE route files are never
-- generated: the ledger is impossible, not merely absent.
-- ---------------------------------------------------------------
update public.gaia_config
   set deity_group = 'athena-gamification',
       generation_flags = coalesce(generation_flags, '{{}}'::jsonb) || jsonb_build_object(
         'generateApiGetList',   true,
         'generateApiGetSingle', true,
         'generateApiPost',      false,
         'generateApiPut',       false,
         'generateApiDelete',    false)
 where table_name = 'daily_puzzles';

insert into public.gaia_config (table_name, deity_group, generation_flags)
select 'daily_puzzles', 'athena-gamification', jsonb_build_object(
         'generateApiGetList',   true,
         'generateApiGetSingle', true,
         'generateApiPost',      false,
         'generateApiPut',       false,
         'generateApiDelete',    false)
 where not exists (select 1 from public.gaia_config where table_name = 'daily_puzzles');

-- ---------------------------------------------------------------
-- STEP 4 - let the base see its own new table
-- ---------------------------------------------------------------
select public.gaia_sync('daily_puzzles');

-- ---------------------------------------------------------------
-- STEP 5 - the puzzles ({count} of them), in batches of 50.
-- One unlawful enum label 400s a whole batch, so they are kept small.
-- ---------------------------------------------------------------"""

FOOTER = """
-- ---------------------------------------------------------------
-- STEP 6 - verify. The last one is the one that matters: run it through
-- the ANON key, not the dashboard, or a false-empty hides in plain sight.
-- ---------------------------------------------------------------
select count(*) as puzzles from public.daily_puzzles;

select count(*) as leaks from public.daily_puzzles
 where position(lower(solution) in lower(clue)) > 0;    -- must be 0

select count(*) as identities from public.daily_puzzles
 where scrambled = solution;                            -- must be 0

select slug, solution, scrambled, clue
  from public.daily_puzzles order by display_order limit 10;
"""


def emit_sql(rows, out_path, corpus_note):
    parts = [HEADER.format(today=date.today().isoformat(),
                           corpus=corpus_note, count=len(rows))]
    cols = ("slug, puzzle_form, display_order, solution, scrambled, clue, "
            "atom_word, atom_id, source_emoji, status")
    for start in range(0, len(rows), 50):
        chunk = rows[start:start + 50]
        vals = []
        for i, r in enumerate(chunk, start=start + 1):
            atom_id = "'%s'::uuid" % r["id"] if r.get("id") else "null"
            em = "'%s'" % sql_escape(r["emoji"]) if r.get("emoji") else "null"
            vals.append(
                "  ('scramble-%s', 'word-scramble', %d, '%s', '%s', '%s', "
                "'%s', %s, %s, 'published'::public.content_status)"
                % (sql_escape(r["word"]), i, sql_escape(r["word"]),
                   sql_escape(r["scrambled"]), sql_escape(r["clue"]),
                   sql_escape(r["word"]), atom_id, em))
        parts.append("\ninsert into public.daily_puzzles (%s) values\n%s\non conflict (slug) do nothing;"
                     % (cols, ",\n".join(vals)))
    parts.append(FOOTER)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(parts), encoding="utf-8")
    return out_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--categories", default="",
                    help="comma-separated category_name allow-list")
    ap.add_argument("--emit", type=int, default=0,
                    help="write the DRAFT sql with this many puzzles")
    ap.add_argument("--out", default=str(DEFAULT_OUT / "022-the-dailies-DRAFT.sql"))
    ap.add_argument("--show", type=int, default=14,
                    help="sample puzzles printed per category")
    args = ap.parse_args()

    cats = {c.strip() for c in args.categories.split(",") if c.strip()} or None
    atoms, emoji = load_corpus()
    corpus_note = "%d atoms, read %s" % (len(atoms), date.today().isoformat())
    clean, rejected = build(atoms, emoji, cats)

    print("\nrejected, and why:")
    for k, v in rejected.most_common():
        if v:
            print("  %6d  %s" % (v, k))
    print("\nCLEAN POOL: %d puzzles" % len(clean))

    bycat = Counter(p["category"] for p in clean)
    print("\nby category:")
    for c, n in bycat.most_common():
        print("  %5d  %s" % (n, c))

    print("\n--- the puzzles, as a vessel would meet them ---")
    seen = Counter()
    for p in clean:
        if seen[p["category"]] >= args.show:
            continue
        seen[p["category"]] += 1
        if seen[p["category"]] == 1:
            print("\n=== %s ===" % p["category"])
        tiles = " ".join(sorted(p["word"].upper()))
        em = " %s" % p["emoji"] if p["emoji"] else ""
        print("  %s   [%d]%s" % (tiles, len(p["word"]), em))
        print("      %s" % p["clue"])

    if args.emit:
        chosen = clean[:args.emit]
        out = emit_sql(chosen, Path(args.out), corpus_note)
        print("\nDRAFT written: %s" % out)
        print("  %d puzzles. KP runs it at his own dashboard; no lamp does." % len(chosen))
    else:
        print("\n(review only - nothing written. --emit N to draft the SQL.)")


if __name__ == "__main__":
    main()
