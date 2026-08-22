#!/usr/bin/env python3
"""THE SCREEN LANDER — KP's movie + TV library, matched to IMDb LOCALLY and
landed as static files for resonance-weaver's /movies room (the Movies door;
tabs Movies · TV). Built 2026-08-21/22 at KP's ⚛ word ("we are going to bring
in the games and movies details we have... no cover images for movies") on the
battlenet lane's shape: a bridge lander pulls, enriches, and LANDS; the app only
reads its own bundle; refresh is `npm run movies` at his hand, never scheduled.

WHAT THIS READS (consumed-media ONLY — never mimirs-well/sealed or /health):
  - media-metadata.csv            the 2026-07-16 catalog ↔ IMDb join (447 rows)
  - media-library/20260508_vuducatalog_mymovies.csv  (405)  the Vudu catalogs,
  - media-library/20260508_vuducatalog_mytv.csv      (42)   his own browser-
                                                             plugin harvest
  - media-library/20260508_macatalog.csv             (284)  Movies Anywhere
  - the IMDb non-commercial datasets, LOCAL, on the Codex mirror (KP's ⚛ word):
    title.basics.tsv.gz + title.ratings.tsv.gz — read in ONE streaming pass,
    never loaded whole; they carry no images.

WHAT IT DOES:
  1. Re-matches every title against the local IMDb datasets with honest tiers
     — override · exact · normalized · fuzzy · title-only · unmatched — so the
     112 previously-unmatched rows (edition suffixes, `and`↔`&`, season packs,
     subtitle-only Star Wars, `Marvel's` prefixes) are recovered where the data
     allows, and NEVER silently guessed: `match` rides into the JSON, the room
     badges it, and every fuzzy candidate lands in review-fuzzy.csv for KP's eye.
  2. Joins the Vudu catalog row (description, MPAA rating, studio, RT %,
     community rating, content id, MA flag) and the Movies Anywhere row (URL,
     retailer, quality, purchase date) onto each title.
  3. Resolves a POSTER per title via a pluggable provider — `--posters tmdb`
     (KP's ⚛ choice; TMDB_READ_ACCESS_TOKEN or TMDB_API_KEY on the bridge
     keyring, values never printed; lookup by IMDb id, title+year search as
     fallback) · `--posters wiki` (no key: Wikidata P345 → enwiki summary
     thumbnail) · `--posters none` — downloading images to
     static/movies/posters/ with true-bytes accounting.
  4. `--land` writes movies.json + meta.json into resonance-weaver/static/movies/.

Caches beside this script (committed like battlenet/enrich-cache.json):
  imdb-match-cache.json · poster-cache.json · review-fuzzy.csv ·
  imdb-overrides.csv (hand-kept: library_title,tconst,note).

Usage:
    python screen_lander.py --report                 # match + join, print, no files
    python screen_lander.py --land --posters none    # land JSON, no images
    python screen_lander.py --land --posters tmdb    # land JSON + posters (the npm script)

Errors read plainly; per-item failures never stop the run; keys never printed.
"""
import argparse
import csv
import difflib
import gzip
import os
import re
import sys
import time
import urllib.error
import urllib.parse

import _common as C

TOOL_NAME = "screen_lander.py"
USER_AGENT = "resonance-bridge/screen_lander"

DEFAULT_OUT_DIR = os.path.join(C.WORKSPACE_ROOT, "resonance-weaver", "static", "movies")
DEFAULT_IMDB_DIR = r"D:\ResonanceWell-Mirror\imdb-datasets-2026-07-16"
MATCH_CACHE = os.path.join(C.SCRIPT_DIR, "imdb-match-cache.json")
POSTER_CACHE = os.path.join(C.SCRIPT_DIR, "poster-cache.json")
OVERRIDES_FILE = os.path.join(C.SCRIPT_DIR, "imdb-overrides.csv")
REVIEW_FILE = os.path.join(C.SCRIPT_DIR, "review-fuzzy.csv")

TMDB_API = "https://api.themoviedb.org/3"
TMDB_IMG = "https://image.tmdb.org/t/p/"
WIKIDATA_API = "https://www.wikidata.org/w/api.php"
WIKI_SUMMARY = "https://en.wikipedia.org/api/rest_v1/page/summary/"

MOVIE_TYPES = {"movie", "tvMovie", "video", "short"}
TV_TYPES = {"tvSeries", "tvMiniSeries"}
KEEP_TYPES = MOVIE_TYPES | TV_TYPES
FUZZY_RATIO = 0.92
FUZZY_MIN_VOTES = 1000
ROMAN = {1: "i", 2: "ii", 3: "iii", 4: "iv", 5: "v", 6: "vi", 7: "vii",
         8: "viii", 9: "ix", 10: "x"}
ROMAN_INV = {v: str(k) for k, v in ROMAN.items()}

# ---------------------------------------------------------------------------
# Title cleaning — the retail suffixes Vudu appends, the prefixes IMDb drops.
# ---------------------------------------------------------------------------
EXTRA_RE = re.compile(r"featurette|deleted scene|gag reel|music video|bonus|"
                      r"behind the scenes|making of|select featurettes", re.I)
YEAR_PARENS = re.compile(r"\s*\((\d{4})\)\s*$")
PART_PARENS = re.compile(r"\s*\((part\s+\w+)\)\s*$", re.I)
PARENS_STRIP = re.compile(
    r"\s*\((?:unrated(?: edition)?|theatrical(?: version| edition)?|short|"
    r"alternate ending|extended(?: edition| version)?|special edition|"
    r"uncensored director'?s cut|director'?s cut|english dubbed|english|"
    r"dubbed|subtitled|(?:the )?complete series|featurette|uncut|rated|"
    r"remastered|ultimate edition|collector'?s edition|anniversary edition|"
    r"imax|3d|4k)\)\s*$", re.I)
CUT_SUFFIX = re.compile(
    r"\s*[-:]\s*(?:extended|editor'?s|director'?s|ultimate|final|theatrical|"
    r"unrated|special)\s+(?:cut|edition|version)\s*$", re.I)
SERIES_SUFFIX = re.compile(
    r"\s*:\s*(?:the complete series|complete series|event series|"
    r"the complete first season|limited series|the series)\s*$", re.I)
SEASON_SUFFIX = re.compile(
    r"\s*[:,-]?\s*(?:season\s+\d+(?:\s*,?\s*(?:volume|vol\.?|part)\s+\d+)?|"
    r"volume\s+\d+|part\s+\d+\s+of\s+\d+|the (?:first|second|third|fourth|"
    r"fifth|sixth|seventh|final) season)\s*$", re.I)
PREFIX_RE = re.compile(
    r"^(?:marvel'?s|marvel studios'?|saban'?s|disney'?s|tyler perry'?s|"
    r"dreamworks'?|pixar'?s|walt disney'?s)\s+", re.I)


def clean_library_title(title: str, kind: str):
    """Returns (base, info). Strips to a fixpoint; records what was stripped."""
    info = {"extra": False, "season_stripped": False, "short": False,
            "year_hint": None, "edition": None}
    base = (title or "").translate(C.QUOTES).strip()
    if EXTRA_RE.search(base):
        info["extra"] = True
    for _ in range(8):
        before = base
        m = YEAR_PARENS.search(base)
        if m:
            info["year_hint"] = int(m.group(1))
            base = base[:m.start()]
        m = PART_PARENS.search(base)
        if m:
            base = base[:m.start()] + " " + m.group(1)
        m = PARENS_STRIP.search(base)
        if m:
            tag = m.group(0).strip().strip("()").strip().lower()
            if tag == "short":
                info["short"] = True
            info["edition"] = info["edition"] or tag
            base = base[:m.start()]
        m = CUT_SUFFIX.search(base)
        if m:
            info["edition"] = info["edition"] or m.group(0).strip(" -:").lower()
            base = base[:m.start()]
        m = SERIES_SUFFIX.search(base)
        if m:
            info["season_stripped"] = True
            base = base[:m.start()]
        if kind == "tv":
            m = SEASON_SUFFIX.search(base)
            if m:
                info["season_stripped"] = True
                base = base[:m.start()]
        m = PREFIX_RE.match(base)
        if m:
            base = base[m.end():]
        base = base.strip(" :-,")
        if base == before:
            break
    return base, info


def candidate_keys(base: str) -> list:
    k = C.norm_title(base)
    keys = []

    def add(x):
        x = (x or "").strip()
        if x and x not in keys:
            keys.append(x)

    add(k)
    add(C.strip_article(k))
    toks = k.split()
    for i, t in enumerate(toks):
        if t.isdigit() and 1 <= int(t) <= 10:
            r = toks[:]
            r[i] = ROMAN[int(t)]
            add(" ".join(r))
            add(C.strip_article(" ".join(r)))
        elif t in ROMAN_INV and i > 0:
            r = toks[:]
            r[i] = ROMAN_INV[t]
            add(" ".join(r))
    pk = re.sub(r"\bpart \w+$", "", k).strip()
    if pk and pk != k:
        add(pk)
    return keys


def block_pair(key: str):
    toks = C.strip_article(key).split()
    if len(toks) >= 2:
        return f"{toks[0]} {toks[1]}"
    return toks[0] if toks else None


# ---------------------------------------------------------------------------
# The IMDb index — one streaming pass, only the rows the catalog could want.
# ---------------------------------------------------------------------------
class ImdbIndex:
    def __init__(self):
        self.by_key = {}      # norm key -> [row]
        self.pool = {}        # block pair -> [row]   (fuzzy candidates)
        self.by_tconst = {}   # tconst -> row
        self.rows = []        # every kept row (for the ratings pass)


def make_row(tconst, ttype, primary, original, start, end, runtime, genres, key):
    return {
        "tconst": tconst, "type": ttype, "primary": primary, "original": original,
        "year": C.to_int(start), "end_year": C.to_int(end),
        "runtime": C.to_int(runtime),
        "genres": [g for g in (genres or "").split(",") if g and g != r"\N"],
        "rating": None, "votes": None, "key": key,
    }


FIRST_TOK = re.compile(r"[a-z0-9]+")
EPISODE_RE = re.compile(r"\bepisode [ivx]+\b ?")


def build_index(imdb_dir, wanted_keys, block_pairs, wanted_tconsts):
    basics = os.path.join(imdb_dir, "title.basics.tsv.gz")
    ratings = os.path.join(imdb_dir, "title.ratings.tsv.gz")
    for p in (basics, ratings):
        if not os.path.exists(p):
            sys.exit(f"{C.TAG} IMDb dataset missing: {p} — pass --imdb-dir, or set "
                     "IMDB_DATASETS_DIR in the bridge .env, or run from the match cache")

    first_tokens = set()
    for k in wanted_keys:
        ft = k.split()[0] if k else None
        if ft:
            first_tokens.add(ft)
    for pair in block_pairs:
        first_tokens.add(pair.split()[0])

    idx = ImdbIndex()
    t0 = time.monotonic()
    n = 0
    print(f"scanning {os.path.basename(basics)} (one streaming pass)...")
    with gzip.open(basics, "rt", encoding="utf-8", errors="replace") as f:
        next(f)  # header
        for line in f:
            n += 1
            if n % 2_000_000 == 0:
                print(f"  ...{n:,} lines, {len(idx.rows):,} kept, {time.monotonic() - t0:.0f}s")
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 9:
                continue
            tconst, ttype, primary, original, _adult, start, end, runtime, genres = parts[:9]
            if ttype not in KEEP_TYPES:
                continue
            want = tconst in wanted_tconsts
            if not want:
                cand = False
                for s in (primary.lower(), original.lower()):
                    m = FIRST_TOK.search(s)
                    if not m:
                        continue
                    tok = m.group(0)
                    if tok in first_tokens:
                        cand = True
                        break
                    if tok in ("the", "a", "an"):
                        m2 = FIRST_TOK.search(s, m.end())
                        if m2 and m2.group(0) in first_tokens:
                            cand = True
                            break
                if not cand:
                    continue
            kp = C.norm_title(primary)
            ko = C.norm_title(original)
            keys = {kp, ko, C.strip_article(kp), C.strip_article(ko)}
            ep = EPISODE_RE.sub("", kp).strip()
            if ep != kp:
                keys.add(ep)
                keys.add(C.strip_article(ep))
            keys.discard("")
            hit_keys = [k for k in keys if k in wanted_keys]
            row = None
            if hit_keys or want:
                row = make_row(tconst, ttype, primary, original, start, end, runtime, genres, kp)
                idx.rows.append(row)
            for k in hit_keys:
                idx.by_key.setdefault(k, []).append(row)
            if want:
                idx.by_tconst[tconst] = row
            pair = block_pair(kp)
            if pair and pair in block_pairs:
                yrs = block_pairs[pair]
                y = C.to_int(start)
                if (y is None or None in yrs or any(abs(y - yy) <= 1 for yy in yrs if yy is not None)):
                    if row is None:
                        row = make_row(tconst, ttype, primary, original, start, end, runtime, genres, kp)
                        idx.rows.append(row)
                    idx.pool.setdefault(pair, []).append(row)
    print(f"  scanned {n:,} titles in {time.monotonic() - t0:.0f}s; kept {len(idx.rows):,} candidate rows")

    kept = {r["tconst"]: r for r in idx.rows}
    print(f"reading {os.path.basename(ratings)}...")
    with gzip.open(ratings, "rt", encoding="utf-8", errors="replace") as f:
        next(f)
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 3:
                continue
            r = kept.get(parts[0])
            if r is not None:
                r["rating"] = C.to_float(parts[1])
                r["votes"] = C.to_int(parts[2])
    return idx


# ---------------------------------------------------------------------------
# Matching — tiers, first hit wins; never silently guess.
# ---------------------------------------------------------------------------
def year_rule(row, year, season_stripped):
    if year is None or row["year"] is None:
        return True
    if abs(row["year"] - year) <= 1:
        return True
    if season_stripped:
        end = row["end_year"] or 9999
        return row["year"] - 1 <= year <= end
    return False


def year_score(row, year):
    if year is None or row["year"] is None:
        return 2
    d = abs(row["year"] - year)
    return 0 if d == 0 else (1 if d == 1 else 3)


def types_for(kind):
    return TV_TYPES if kind == "tv" else MOVIE_TYPES


def pick(rows, year, kind, season_stripped, require_year=True):
    prim = [r for r in rows if r["type"] in types_for(kind)]
    alt = [r for r in rows if r["type"] not in types_for(kind)]
    for cands in (prim, alt):
        ok = [r for r in cands if (not require_year) or year_rule(r, year, season_stripped)]
        if ok:
            ok.sort(key=lambda r: (year_score(r, year), -(r["votes"] or 0)))
            return ok[0]
    return None


def result_from(row, match):
    return {
        "tconst": row["tconst"], "imdb_title": row["primary"],
        "imdb_type": row["type"], "year": row["year"], "end_year": row["end_year"],
        "runtime_min": row["runtime"], "genres": row["genres"],
        "imdb_rating": row["rating"], "votes": row["votes"], "match": match,
    }


UNMATCHED = {"tconst": None, "imdb_title": None, "imdb_type": None, "year": None,
             "end_year": None, "runtime_min": None, "genres": [], "imdb_rating": None,
             "votes": None, "match": "unmatched"}


def match_title(item, idx, overrides, review_rows):
    t = item["library_title"]
    ov = overrides.get(t)
    if ov:
        if ov in idx.by_tconst:
            return result_from(idx.by_tconst[ov], "override")
        print(f"  {C.TAG} override tconst {ov} for {t!r} not found in the datasets — ignored")
    if item["existing_match"] == "title+year" and item["existing_tconst"] in idx.by_tconst:
        return result_from(idx.by_tconst[item["existing_tconst"]], "exact")

    season = item["info"]["season_stripped"]
    if not item["info"]["extra"]:
        for key in item["keys"]:
            rows = idx.by_key.get(key)
            if rows:
                r = pick(rows, item["year"], item["kind"], season)
                if r:
                    return result_from(r, "normalized")
        # An exact-title hit whose year disagrees outranks any fuzzy guess at a
        # DIFFERENT title (the Paranormal Activity lesson: the 2007 film's
        # 2009 wide-release year pushed it past ±1 and a fuzzy tier would have
        # handed it to the sequel). Labelled honestly: title-only.
        for key in item["keys"]:
            rows = idx.by_key.get(key)
            if rows:
                r = pick(rows, item["year"], item["kind"], season, require_year=False)
                if r:
                    return result_from(r, "title-only")
        # TV season packs named "<Series> <Arc>" (Sailor Moon R / S / SuperS):
        # drop trailing tokens one at a time down to two and look for the
        # series itself; labelled `series` so the room can say so.
        if item["kind"] == "tv" and season:
            toks = item["keys"][0].split()
            while len(toks) > 2:
                toks = toks[:-1]
                k = " ".join(toks)
                for variant in (k, C.strip_article(k)):
                    rows = idx.by_key.get(variant)
                    if rows:
                        r = pick([x for x in rows if x["type"] in TV_TYPES], item["year"], "tv", True)
                        if r:
                            return result_from(r, "series")
        pool = idx.pool.get(item["pair"], [])
        if pool and item["keys"]:
            scored = []
            k0 = item["keys"][0]
            for r in pool:
                ratio = difflib.SequenceMatcher(None, k0, r["key"]).ratio()
                scored.append((ratio, r))
            scored.sort(key=lambda x: (-x[0], -(x[1]["votes"] or 0)))
            top = scored[:3]
            accepted = None
            for ratio, r in top:
                if (ratio >= FUZZY_RATIO and year_rule(r, item["year"], season)
                        and (r["votes"] or 0) >= FUZZY_MIN_VOTES
                        and r["type"] in types_for(item["kind"])):
                    accepted = r
                    break
            for ratio, r in top:
                review_rows.append({
                    "library_title": t, "kind": item["kind"], "year": item["year"],
                    "candidate_tconst": r["tconst"], "candidate_title": r["primary"],
                    "candidate_year": r["year"], "candidate_type": r["type"],
                    "votes": r["votes"], "ratio": f"{ratio:.3f}",
                    "accepted": "yes" if r is accepted else "no",
                })
            if accepted:
                return result_from(accepted, "fuzzy")
    if item["existing_tconst"] and item["existing_tconst"] in idx.by_tconst:
        return result_from(idx.by_tconst[item["existing_tconst"]], "title-only")
    return dict(UNMATCHED)


# ---------------------------------------------------------------------------
# Sources + joins
# ---------------------------------------------------------------------------
def load_overrides():
    ov = {}
    if os.path.exists(OVERRIDES_FILE):
        for r in C.read_csv(OVERRIDES_FILE):
            t = (r.get("library_title") or "").strip()
            tc = (r.get("tconst") or "").strip()
            if t and tc and not t.startswith("#"):
                ov[t] = tc
    return ov


def load_sources(source_dir):
    paths = {
        "metadata": os.path.join(source_dir, "media-metadata.csv"),
        "vudu_movies": os.path.join(source_dir, "media-library", "20260508_vuducatalog_mymovies.csv"),
        "vudu_tv": os.path.join(source_dir, "media-library", "20260508_vuducatalog_mytv.csv"),
        "ma": os.path.join(source_dir, "media-library", "20260508_macatalog.csv"),
    }
    for name, p in paths.items():
        if not os.path.exists(p):
            sys.exit(f"{C.TAG} source missing ({name}): {p}")
    return paths, {k: C.read_csv(p) for k, p in paths.items()}


def vudu_lookup_table(rows):
    table = {}
    for r in rows:
        table.setdefault((r.get("Movie") or "").strip(), []).append(r)
    return table


def vudu_pick(table, title, year):
    rows = table.get(title) or []
    if not rows:
        return None
    if len(rows) == 1 or year is None:
        return rows[0]
    rows = sorted(rows, key=lambda r: abs((C.to_int(r.get("Release Year")) or 0) - year))
    return rows[0]


def ma_key(title: str) -> str:
    base, _ = clean_library_title(title, "movie")
    k = C.norm_title(base)
    toks = []
    for t in k.split():
        if t == "part":
            continue
        toks.append(ROMAN_INV.get(t, t))
    return " ".join(toks)


def rt_percent(s):
    s = (s or "").strip().rstrip("%")
    return C.to_int(s)


def vudu_block(v):
    if not v:
        return None
    return {
        "description": (v.get("Description") or "").strip() or None,
        "genre": (v.get("Genre") or "").strip() or None,
        "rating": (v.get("Rating") or "").strip() or None,
        "studio": (v.get("Studio") or "").strip() or None,
        "quality": (v.get("Own") or "").strip() or None,
        "release_year": C.to_int(v.get("Release Year")),
        "release_date": C.mdy_to_iso(v.get("Release Date")),
        "runtime_min": C.to_int(v.get("Runtime (Minutes)")),
        "rt_rating": rt_percent(v.get("Rotten Tomatoes Rating")),
        "community_rating": C.to_float(v.get("Community Rating")),
        "content_id": (v.get("Content ID") or "").strip() or None,
        "ma": (v.get("MA") or "").strip().lower() == "yes",
    }


# ---------------------------------------------------------------------------
# Posters — one signature, three providers.
# ---------------------------------------------------------------------------
def tmdb_creds():
    tok = C.env_value("TMDB_READ_ACCESS_TOKEN", required=False)
    key = C.env_value("TMDB_API_KEY", required=False)
    if not tok and not key:
        sys.exit(f"{C.TAG} TMDB_READ_ACCESS_TOKEN / TMDB_API_KEY not found in the bridge .env "
                 "— run with --posters none to land without images")
    return tok, key


def tmdb_get(rate, path, params, creds):
    tok, key = creds
    q = dict(params)
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    if tok:
        headers["Authorization"] = f"Bearer {tok}"
    else:
        q["api_key"] = key
    url = TMDB_API + path + "?" + urllib.parse.urlencode(q)
    rate.pace()
    body, err = C.http_json(url, headers=headers)
    if err:
        if isinstance(err, urllib.error.HTTPError) and err.code in (401, 403):
            sys.exit(C.describe_http_error(err, "TMDb " + path))
        print("  " + C.describe_http_error(err, "TMDb " + path))
        return None
    return body


def resolve_poster_tmdb(rate, item, creds, cache):
    ck = item["tconst"] or f"v{item['content_id'] or C.slugify(item['library_title'])}"
    if ck in cache:
        return cache[ck]
    kind = item["kind"]
    path = None
    if item["tconst"]:
        body = tmdb_get(rate, f"/find/{item['tconst']}", {"external_source": "imdb_id"}, creds)
        if body:
            lists = [body.get("movie_results"), body.get("tv_results")]
            if kind == "tv":
                lists.reverse()
            for lst in lists:
                if lst and lst[0].get("poster_path"):
                    path = lst[0]["poster_path"]
                    break
    if not path and not item["info"]["extra"] and item["base"]:
        ep = "/search/tv" if kind == "tv" else "/search/movie"
        params = {"query": item["base"], "include_adult": "false"}
        if item["year"]:
            params["first_air_date_year" if kind == "tv" else "year"] = item["year"]
        body = tmdb_get(rate, ep, params, creds)
        want = C.norm_title(item["base"])
        for r in (body or {}).get("results", [])[:5]:
            names = [r.get("title"), r.get("name"), r.get("original_title"), r.get("original_name")]
            if any(C.norm_title(x) == want for x in names if x) and r.get("poster_path"):
                path = r["poster_path"]
                break
    cache[ck] = {"provider": "tmdb", "poster_path": path} if path else None
    return cache[ck]


def resolve_poster_wiki(rate, item, cache):
    tconst = item["tconst"]
    if not tconst:
        return None
    if tconst in cache:
        return cache[tconst]
    headers = {"User-Agent": USER_AGENT + " (+https://github.com/Quantum-Weaver/resonance-bridge)"}
    url = None
    try:
        rate.pace()
        q = urllib.parse.urlencode({"action": "query", "list": "search",
                                    "srsearch": f"haswbstatement:P345={tconst}",
                                    "srlimit": 1, "format": "json"})
        body, err = C.http_json(f"{WIKIDATA_API}?{q}", headers=headers)
        hits = ((body or {}).get("query") or {}).get("search") or []
        if hits:
            qid = hits[0]["title"]
            rate.pace()
            q2 = urllib.parse.urlencode({"action": "wbgetentities", "ids": qid, "props": "sitelinks",
                                         "sitefilter": "enwiki", "format": "json"})
            body2, _ = C.http_json(f"{WIKIDATA_API}?{q2}", headers=headers)
            title = ((((body2 or {}).get("entities") or {}).get(qid) or {}).get("sitelinks") or {}).get("enwiki", {}).get("title")
            if title:
                rate.pace()
                body3, _ = C.http_json(WIKI_SUMMARY + urllib.parse.quote(title.replace(" ", "_")), headers=headers)
                if body3:
                    url = ((body3.get("thumbnail") or {}).get("source")
                           or (body3.get("originalimage") or {}).get("source"))
    except Exception as e:  # one bad title never stops the others
        print(f"  {C.TAG} wiki poster error for {tconst}: {e}")
    cache[tconst] = {"provider": "wiki", "url": url} if url else None
    return cache[tconst]


def poster_url(entry, size):
    if not entry:
        return None
    if entry.get("provider") == "tmdb" and entry.get("poster_path"):
        return TMDB_IMG + size + entry["poster_path"]
    return entry.get("url")


# ---------------------------------------------------------------------------
def fmt_mb(n):
    return f"{n / (1024 * 1024):.2f} MB"


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser(description="Match KP's movie/TV library to the local IMDb datasets, "
                                            "join the Vudu/Movies Anywhere catalogs, resolve posters, "
                                            "and land static JSON for resonance-weaver's /movies room.")
    p.add_argument("--land", action="store_true", help="write movies.json + meta.json (+ posters) into --out-dir")
    p.add_argument("--out-dir", default=DEFAULT_OUT_DIR)
    p.add_argument("--source-dir", default=C.DEFAULT_SOURCE_DIR,
                   help="consumed-media folder (reads ONLY this folder)")
    p.add_argument("--imdb-dir", default=None,
                   help=f"folder holding title.basics.tsv.gz + title.ratings.tsv.gz (default: "
                        f"IMDB_DATASETS_DIR in the bridge .env, else {DEFAULT_IMDB_DIR})")
    p.add_argument("--posters", choices=["tmdb", "wiki", "none"], default="none")
    p.add_argument("--poster-size", choices=["w185", "w342", "w500"], default="w185",
                   help="TMDb poster width (default w185)")
    p.add_argument("--no-images", action="store_true", help="resolve nothing; land no images")
    p.add_argument("--rematch", action="store_true", help="ignore the match cache; re-scan the datasets")
    p.add_argument("--report", action="store_true", help="print the per-title table")
    args = p.parse_args()

    imdb_dir = args.imdb_dir or C.env_value("IMDB_DATASETS_DIR", required=False) or DEFAULT_IMDB_DIR
    landed_at = C.iso_now()
    t_start = time.monotonic()

    paths, src = load_sources(args.source_dir)
    metadata = src["metadata"]
    vudu_m = vudu_lookup_table(src["vudu_movies"])
    vudu_t = vudu_lookup_table(src["vudu_tv"])
    ma_rows = src["ma"]
    overrides = load_overrides()
    print(f"sources: metadata {len(metadata)} · vudu movies {len(src['vudu_movies'])} · "
          f"vudu tv {len(src['vudu_tv'])} · movies anywhere {len(ma_rows)} · overrides {len(overrides)}")

    # --- the items, pre-match ------------------------------------------
    items = []
    for m in metadata:
        kind = (m.get("kind") or "movie").strip()
        title = (m.get("library_title") or "").strip()
        vrow = vudu_pick(vudu_t if kind == "tv" else vudu_m, title, C.to_int(m.get("year")))
        release_year = C.to_int(vrow.get("Release Year")) if vrow else None
        base, info = clean_library_title(title, kind)
        year = release_year or C.to_int(m.get("year")) or info["year_hint"]
        keys = candidate_keys(base)
        items.append({
            "library_title": title, "kind": kind, "base": base, "info": info,
            "keys": keys, "pair": block_pair(keys[0]) if keys else None,
            "year": year, "existing_tconst": (m.get("tconst") or "").strip() or None,
            "existing_match": (m.get("match") or "").strip(),
            "purchased": C.mdy_to_iso(m.get("purchased")),
            "vudu": vudu_block(vrow), "content_id": (vrow or {}).get("Content ID", "").strip() or None,
            "cache_key": f"{kind}|{title}|{year}",
        })

    # --- the match (cache-first; one dataset scan otherwise) ------------
    cache = {} if args.rematch else C.load_cache(MATCH_CACHE)
    review_rows = []
    need = [it for it in items if it["cache_key"] not in cache]
    if need:
        wanted_keys = set()
        block_pairs = {}
        wanted_tconsts = set(overrides.values())
        for it in need:
            wanted_keys.update(it["keys"])
            if it["kind"] == "tv" and it["info"]["season_stripped"] and it["keys"]:
                toks = it["keys"][0].split()
                while len(toks) > 2:
                    toks = toks[:-1]
                    wanted_keys.add(" ".join(toks))
                    wanted_keys.add(C.strip_article(" ".join(toks)))
            if it["existing_tconst"]:
                wanted_tconsts.add(it["existing_tconst"])
            if it["pair"]:
                block_pairs.setdefault(it["pair"], set()).add(it["year"])
        idx = build_index(imdb_dir, wanted_keys, block_pairs, wanted_tconsts)
        for it in need:
            try:
                cache[it["cache_key"]] = match_title(it, idx, overrides, review_rows)
            except Exception as e:  # one title never stops the others
                print(f"  {C.TAG} match error for {it['library_title']!r}: {e}")
                cache[it["cache_key"]] = dict(UNMATCHED)
        C.save_cache(MATCH_CACHE, cache)
        with open(REVIEW_FILE, "w", encoding="utf-8", newline="") as f:
            cols = ["library_title", "kind", "year", "candidate_tconst", "candidate_title",
                    "candidate_year", "candidate_type", "votes", "ratio", "accepted"]
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            for r in review_rows:
                w.writerow(r)
        print(f"match cache written ({len(need)} matched this run); review-fuzzy.csv ({len(review_rows)} rows)")
    else:
        print(f"match cache covers all {len(items)} titles (pass --rematch to re-scan the datasets)")
    for it in items:
        it["imdb"] = cache[it["cache_key"]]
        it["tconst"] = it["imdb"]["tconst"]

    # --- Movies Anywhere join ----------------------------------------
    ma_table = {}
    for r in ma_rows:
        ma_table.setdefault(ma_key(r.get("Movie") or ""), []).append(r)
    ma_used = set()
    for it in items:
        it["ma"] = None
        v = it["vudu"]
        if not v or not v["ma"]:
            continue
        k = ma_key(it["library_title"])
        rows = ma_table.get(k) or []
        if not rows:
            continue
        exact = C.norm_title(rows[0].get("Movie") or "") == C.norm_title(it["library_title"])
        r = rows[0]
        if len(rows) > 1 and it["year"]:
            rows = sorted(rows, key=lambda x: abs((C.to_int(x.get("Release Year")) or 0) - it["year"]))
            r = rows[0]
        ma_used.add(id(r))
        it["ma"] = {
            "url": (r.get("URL") or "").strip() or None,
            "retailer": (r.get("Retailer") or "").strip() or None,
            "quality": (r.get("Quality") or "").strip() or None,
            "purchase_date": C.mdy_to_iso(r.get("Purchase Date")),
            "content_id": (r.get("Content ID") or "").strip() or None,
            "match": "exact" if exact else "normalized",
        }
    ma_unjoined = [r.get("Movie") for r in ma_rows if id(r) not in ma_used]

    # --- posters -------------------------------------------------------
    provider = "none" if args.no_images else args.posters
    posters_dir = os.path.join(args.out_dir, "posters")
    pcache = C.load_cache(POSTER_CACHE)
    poster_count, poster_bytes = 0, 0
    if provider != "none":
        rate = C.RateLimiter(0.05 if provider == "tmdb" else 1.0)
        creds = tmdb_creds() if provider == "tmdb" else None
        print(f"resolving posters via {provider}...")
        done = 0
        for it in items:
            it["poster"] = None
            try:
                entry = (resolve_poster_tmdb(rate, it, creds, pcache) if provider == "tmdb"
                         else resolve_poster_wiki(rate, it, pcache))
                url = poster_url(entry, args.poster_size)
                if url and args.land:
                    stem = it["tconst"] or f"v{it['content_id'] or C.slugify(it['library_title'])}"
                    rel, n = C.resolve_image(rate, url, posters_dir, stem, "/movies/posters", USER_AGENT)
                    if rel:
                        it["poster"] = rel
                        poster_count += 1
                        poster_bytes += n
                elif url:
                    it["poster"] = url  # report mode: the URL stands in for the file
                    poster_count += 1
            except SystemExit:
                raise
            except Exception as e:
                print(f"  {C.TAG} poster error for {it['library_title']!r}: {e}")
            done += 1
            if done % 100 == 0:
                print(f"  ...{done}/{len(items)}")
        C.save_cache(POSTER_CACHE, pcache)
        print(f"posters: {poster_count}/{len(items)} resolved via {provider}, {fmt_mb(poster_bytes)} on disk, "
              f"{rate.calls} paced calls")
    else:
        for it in items:
            it["poster"] = None

    # --- build the landed shape ---------------------------------------
    def out_item(it):
        i = it["imdb"]
        v = it["vudu"] or {}
        return {
            "id": f"v{it['content_id']}" if it["content_id"] else C.slugify(it["library_title"]),
            "library_title": it["library_title"], "kind": it["kind"],
            "purchased": it["purchased"],
            "tconst": i["tconst"], "imdb_title": i["imdb_title"], "imdb_type": i["imdb_type"],
            "year": i["year"] or v.get("release_year"),
            "runtime_min": i["runtime_min"] or v.get("runtime_min"),
            "genres": i["genres"] or [g.strip() for g in (v.get("genre") or "").split(",") if g.strip()],
            "imdb_rating": i["imdb_rating"], "votes": i["votes"],
            "match": i["match"], "extra": it["info"]["extra"], "edition": it["info"]["edition"],
            "vudu": it["vudu"], "ma": it["ma"],
            "poster": it["poster"],
            "imdb_url": f"https://www.imdb.com/title/{i['tconst']}/" if i["tconst"] else None,
        }

    movies = sorted((out_item(it) for it in items if it["kind"] != "tv"), key=lambda x: x["library_title"].lower())
    tv = sorted((out_item(it) for it in items if it["kind"] == "tv"), key=lambda x: x["library_title"].lower())
    tiers = {}
    for it in items:
        tiers[it["imdb"]["match"]] = tiers.get(it["imdb"]["match"], 0) + 1
    matched = sum(1 for it in items if it["tconst"])
    extras = sum(1 for it in items if it["info"]["extra"])
    counts = {"movies": len(movies), "tv": len(tv), "matched": matched,
              "unmatched": len(items) - matched, "extras": extras, "posters": poster_count}

    # --- the report ----------------------------------------------------
    print()
    print(f"titles: {len(items)} ({counts['movies']} movies · {counts['tv']} tv) · matched on IMDb {matched} · "
          f"unmatched {counts['unmatched']} · extras {extras}")
    print("  tiers: " + " · ".join(f"{k} {v}" for k, v in sorted(tiers.items())))
    ma_joined = sum(1 for it in items if it["ma"])
    print(f"  movies anywhere: {ma_joined} joined · {len(ma_unjoined)} MA rows unjoined")
    unmatched_titles = [it["library_title"] for it in items if not it["tconst"]]
    if unmatched_titles:
        print(f"  unmatched ({len(unmatched_titles)}): " + " | ".join(unmatched_titles))
    fuzzy = [f"{it['library_title']} -> {it['imdb']['imdb_title']} ({it['imdb']['year']})"
             for it in items if it["imdb"]["match"] == "fuzzy"]
    if fuzzy:
        print(f"  fuzzy accepted ({len(fuzzy)}): " + " | ".join(fuzzy))
    if args.report:
        print()
        print(f"{'kind':5} | {'library_title':50} | {'match':10} | {'tconst':10} | {'year':4} | imdb_title | poster")
        for it in items:
            i = it["imdb"]
            print(f"{it['kind']:5} | {it['library_title'][:50]:50} | {i['match']:10} | "
                  f"{(i['tconst'] or '-'):10} | {str(i['year'] or '-'):4} | {i['imdb_title'] or '-'} | "
                  f"{'yes' if it['poster'] else '-'}")
    if ma_unjoined and args.report:
        print(f"  MA rows unjoined: " + " | ".join(ma_unjoined))

    if not args.land:
        print(f"\n(no files written — pass --land) · {time.monotonic() - t_start:.0f}s")
        return

    os.makedirs(args.out_dir, exist_ok=True)
    payload = {
        "landed_at": landed_at,
        "source": {"catalog_date": "2026-05-08", "imdb_datasets": os.path.basename(imdb_dir.rstrip("\\/"))},
        "counts": counts,
        "movies": movies, "tv": tv,
    }
    meta = {
        "landed_at": landed_at, "tool": TOOL_NAME,
        "sources": {**paths, "imdb_dir": imdb_dir},
        "counts": counts,
        "match": {**tiers, "extras": extras, "ma_joined": ma_joined, "ma_unjoined": len(ma_unjoined)},
        "posters": {"provider": provider, "size": args.poster_size if provider == "tmdb" else None,
                    "count": poster_count, "bytes": poster_bytes, "total_bytes": poster_bytes},
        "review_file": os.path.relpath(REVIEW_FILE, C.BRIDGE_DIR).replace("\\", "/"),
    }
    C.write_json(os.path.join(args.out_dir, "movies.json"), payload)
    C.write_json(os.path.join(args.out_dir, "meta.json"), meta)
    print(f"\nlanded {len(movies)} movies + {len(tv)} tv -> {os.path.join(args.out_dir, 'movies.json')}")
    print(f"landed meta -> {os.path.join(args.out_dir, 'meta.json')} · {time.monotonic() - t_start:.0f}s")
    if not items:
        sys.exit(1)


if __name__ == "__main__":
    main()
