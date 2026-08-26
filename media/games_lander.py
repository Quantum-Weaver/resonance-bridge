#!/usr/bin/env python3
"""THE GAMES LANDER — KP's PlayStation record (the hours witnessed + the
purchase library), enriched through IGDB (via Twitch client credentials, KP's
⚛ choice), landed as static files for resonance-weaver's /games room (the Games
door; tabs Played · Library). Built 2026-08-21/22 at KP's ⚛ word ("limited
metadata for games") on the battlenet lane's shape — keys on the bridge
keyring, never printed; a cache beside the script; true-bytes cover ledger;
LANDED FILES as the only bus into the app; refresh `npm run games` at his hand.

WHAT THIS READS (consumed-media ONLY — never mimirs-well/sealed or /health):
  - games/playstation-gameplay.csv      167 session rows; `total` = PlayStation's
                                        own hours per row; `session` = seconds
  - games/playstation-transactions.csv  592 purchases; `price` is USD CENTS
  Both sheets carry a header-echo first data row (the export's own human
  header survived the parse) — skipped by its literal first value.

WHAT IT DOES:
  1. PLAYED — groups the sessions into works (GTA V's PS4 + PS5 rows are one
     work with per-platform hours; ESO's two SKUs are one work), sums
     PlayStation's own hours, counts sessions, keeps first/last played.
  2. LIBRARY — groups the purchases by game: products (DLC, passes, currency),
     purchase dates, platforms, spend in cents (the one Refund negated),
     subscription/service flags.
  3. IGDB — one search per distinct game name (exact normalized name first,
     else the best-known candidate; `match` rides into the JSON), bringing
     cover · release date · genres · platforms · summary · developer ·
     publisher · rating; covers downloaded to static/games/covers/.
  4. `--land` writes games.json + meta.json into resonance-weaver/static/games/.

Caches beside this script: igdb-cache.json · igdb-overrides.json (hand-kept:
{"search name": igdb_id}).

Usage:
    python games_lander.py --report            # parse + print, no files, no keys
    python games_lander.py --land --no-igdb    # land without enrichment (no keys)
    python games_lander.py --land              # land + IGDB + covers (the npm script)

SECRETS LAW: TWITCH_CLIENT_ID / TWITCH_CLIENT_SECRET load from the bridge
.env by name; the bearer token stays in memory; nothing is printed or written.
"""
import argparse
import os
import re
import sys
import time
import urllib.error
import urllib.parse
from datetime import datetime, timezone

import _common as C

TOOL_NAME = "games_lander.py"
USER_AGENT = "resonance-bridge/games_lander"

DEFAULT_OUT_DIR = os.path.join(C.WORKSPACE_ROOT, "resonance-weaver", "static", "games")
IGDB_CACHE = os.path.join(C.SCRIPT_DIR, "igdb-cache.json")
OVERRIDES_FILE = os.path.join(C.SCRIPT_DIR, "igdb-overrides.json")

TWITCH_TOKEN_URL = "https://id.twitch.tv/oauth2/token"
IGDB_GAMES_URL = "https://api.igdb.com/v4/games"
IGDB_IMG = "https://images.igdb.com/igdb/image/upload/"
IGDB_FIELDS = ("name,slug,url,cover.image_id,first_release_date,genres.name,platforms.name,"
               "summary,storyline,total_rating,total_rating_count,"
               "involved_companies.company.name,involved_companies.developer,"
               "involved_companies.publisher")
IGDB_MIN_INTERVAL = 0.26  # IGDB allows 4 requests/s

WORK_MERGE = {
    "The Elder Scrolls Online: Tamriel Unlimited": "The Elder Scrolls Online",
}
SERVICE_RE = re.compile(
    r"playstation (?:plus|vue|now|network|store|music|video)|ps plus|ps now|amazon|netflix|"
    r"hulu|apple tv|spotify|crunchyroll|disney|twitch|youtube|funimation|ea play|ea access|"
    r"ubisoft\+|hbo|peacock|paramount|vudu|pandora|tidal|sling", re.I)


def read_ps_csv(path, first_col, echo_value):
    """Reads one PlayStation sheet; skips the header-echo row by its literal
    first value; returns (rows, skipped_echo)."""
    if not os.path.exists(path):
        sys.exit(f"{C.TAG} source missing: {path}")
    rows = C.read_csv(path)
    skipped = 0
    if rows and (rows[0].get(first_col) or "").strip() == echo_value:
        rows = rows[1:]
        skipped = 1
    else:
        print(f"  {C.TAG} note: no header-echo row found in {os.path.basename(path)} "
              f"(expected first {first_col!r} == {echo_value!r})")
    return rows, skipped


def clean_game_name(raw: str):
    """-> (display, platform_or_None, search_name)."""
    s = (raw or "").translate(C.QUOTES)
    s = s.replace("™", "").replace("®", "").replace("©", "")
    s = re.sub(r"\s+", " ", s).strip()
    platform = None
    m = re.search(r"\((PS[345])\)\s*$", s, re.I)
    if m:
        platform = m.group(1).upper()
        s = s[:m.start()].strip()
    display = WORK_MERGE.get(s, s)
    search = re.sub(r"\s*\([^)]*\)\s*$", "", display)
    search = re.sub(r"\s+console edition$", "", search, flags=re.I)
    # "PS4 & PS5", "PS4 and PS5", "PS4/PS5", a bare "PS5" — the storefront's
    # platform tails, never part of the work's name.
    search = re.sub(r"\s*(?:ps[345]\s*(?:&|and|/)\s*)*ps[345]\s*$", "", search, flags=re.I)
    search = search.strip(" &-:").strip()
    return display, platform, search or display


def price_cents(s):
    s = (s or "").strip()
    if not s:
        return 0
    if "." in s:
        f = C.to_float(s)
        return int(round(f * 100)) if f is not None else 0
    return C.to_int(s) or 0


def build_played(rows):
    works = {}
    for r in rows:
        display, platform, search = clean_game_name(r.get("game"))
        date = C.mdy_to_iso(r.get("date"))
        hours = C.to_int(r.get("total")) or 0
        seconds = C.to_int(r.get("session")) or 0
        w = works.setdefault(display, {
            "id": C.slugify(display), "work": display, "search_name": search,
            "source_names": [], "platforms": {}, "hours_total": 0, "seconds_total": 0,
            "sessions": 0, "first_played": None, "last_played": None,
        })
        raw = (r.get("game") or "").strip()
        if raw and raw not in w["source_names"]:
            w["source_names"].append(raw)
        pkey = platform or "PlayStation"
        pl = w["platforms"].setdefault(pkey, {"platform": pkey, "hours": 0, "seconds": 0,
                                              "sessions": 0, "first": None, "last": None})
        pl["hours"] += hours
        pl["seconds"] += seconds
        pl["sessions"] += 1
        if date:
            pl["first"] = min(pl["first"], date) if pl["first"] else date
            pl["last"] = max(pl["last"], date) if pl["last"] else date
            w["first_played"] = min(w["first_played"], date) if w["first_played"] else date
            w["last_played"] = max(w["last_played"], date) if w["last_played"] else date
        w["hours_total"] += hours
        w["seconds_total"] += seconds
        w["sessions"] += 1
    out = []
    for w in works.values():
        w["platforms"] = sorted(w["platforms"].values(), key=lambda x: -x["hours"])
        out.append(w)
    out.sort(key=lambda x: (-x["hours_total"], x["work"].lower()))
    return out


def build_library(rows):
    # Grouped by NORMALIZED name: PlayStation's export spells one work two
    # ways ("Grand Theft Auto V" / "GRAND THEFT AUTO V"); the first-seen
    # casing is the display name, every spelling is kept in `source_names`.
    games = {}
    used_ids = {}
    for r in rows:
        display, platform_in_name, search = clean_game_name(r.get("game"))
        if not display:
            continue
        gkey = C.norm_title(display)
        g = games.setdefault(gkey, {
            "id": None, "game": display, "search_name": search, "source_names": [], "products": [],
            "product_count": 0, "spend_cents": 0, "first": None, "last": None,
            "platforms": [], "subscription": False, "service": bool(SERVICE_RE.search(display)),
        })
        if display not in g["source_names"]:
            g["source_names"].append(display)
        txtype = (r.get("txtype") or "").strip()
        cents = price_cents(r.get("price"))
        if txtype.lower() == "refund":
            cents = -abs(cents)
        date = C.mdy_to_iso(r.get("date"))
        platform = (r.get("platform") or "").strip() or platform_in_name
        g["products"].append({
            "date": date,
            "product": (r.get("product") or "").strip() or display,
            "platform": platform or None,
            "txtype": txtype or None,
            "price_cents": cents,
            "qty": C.to_int(r.get("qty")) if C.to_int(r.get("qty")) is not None else 1,
        })
        g["spend_cents"] += cents
        if date:
            g["first"] = min(g["first"], date) if g["first"] else date
            g["last"] = max(g["last"], date) if g["last"] else date
        if platform and platform not in g["platforms"]:
            g["platforms"].append(platform)
    out = []
    for g in games.values():
        g["products"].sort(key=lambda x: x["date"] or "")
        g["product_count"] = len(g["products"])
        g["subscription"] = bool(g["products"]) and all(
            (p["txtype"] or "").lower() == "subscription purchase" for p in g["products"])
        base = C.slugify(g["game"])
        n = used_ids.get(base, 0) + 1
        used_ids[base] = n
        g["id"] = base if n == 1 else f"{base}-{n}"
        out.append(g)
    out.sort(key=lambda x: (-x["spend_cents"], x["game"].lower()))
    return out


# IGDB via Twitch
def twitch_token(client_id, client_secret):
    data = urllib.parse.urlencode({"client_id": client_id, "client_secret": client_secret,
                                   "grant_type": "client_credentials"}).encode()
    body, err = C.http_json(TWITCH_TOKEN_URL, headers={
        "User-Agent": USER_AGENT, "Content-Type": "application/x-www-form-urlencoded"}, data=data)
    if err:
        if isinstance(err, urllib.error.HTTPError) and err.code in (400, 401, 403):
            sys.exit(f"{C.TAG} Twitch token request rejected (HTTP {err.code}) — check "
                     "TWITCH_CLIENT_ID / TWITCH_CLIENT_SECRET on the bridge keyring. "
                     "(values never printed)")
        sys.exit(C.describe_http_error(err, "the Twitch token"))
    tok = (body or {}).get("access_token")
    if not tok:
        sys.exit(f"{C.TAG} Twitch token response had no access_token — keys: {list((body or {}).keys())}")
    return tok


def igdb_query(rate, token, client_id, body_text, what):
    headers = {"Client-ID": client_id, "Authorization": f"Bearer {token}",
               "Accept": "application/json", "Content-Type": "text/plain", "User-Agent": USER_AGENT}
    for attempt in (1, 2):
        rate.pace()
        res, err = C.http_json(IGDB_GAMES_URL, headers=headers, data=body_text.encode("utf-8"))
        if not err:
            return res if isinstance(res, list) else []
        if isinstance(err, urllib.error.HTTPError) and err.code in (401, 403):
            sys.exit(C.describe_http_error(err, "IGDB " + what))
        if isinstance(err, urllib.error.HTTPError) and err.code == 429 and attempt == 1:
            time.sleep(1.0)
            continue
        print("  " + C.describe_http_error(err, "IGDB " + what))
        return None


def shape_igdb(g, match):
    companies = g.get("involved_companies") or []
    dev = next((c.get("company", {}).get("name") for c in companies if c.get("developer")), None)
    pub = next((c.get("company", {}).get("name") for c in companies if c.get("publisher")), None)
    rel = g.get("first_release_date")
    release = (datetime.fromtimestamp(rel, tz=timezone.utc).strftime("%Y-%m-%d") if rel else None)
    rating = g.get("total_rating")
    return {
        "id": g.get("id"), "name": g.get("name"), "slug": g.get("slug"), "url": g.get("url"),
        "release": release,
        "genres": [x.get("name") for x in (g.get("genres") or []) if x.get("name")],
        "platforms": [x.get("name") for x in (g.get("platforms") or []) if x.get("name")],
        "summary": g.get("summary"), "storyline": g.get("storyline"),
        "developer": dev, "publisher": pub,
        "rating": round(rating, 1) if isinstance(rating, (int, float)) else None,
        "rating_count": g.get("total_rating_count"),
        "cover_image_id": (g.get("cover") or {}).get("image_id"),
        "match": match,
    }


def igdb_lookup(rate, token, client_id, search_name, overrides, cache):
    key = search_name
    if key in cache:
        return cache[key]
    ov = overrides.get(search_name)
    if ov:
        body = f"where id = {int(ov)}; fields {IGDB_FIELDS}; limit 1;"
    else:
        safe = search_name.replace("\\", "").replace('"', '\\"')
        body = f'search "{safe}"; fields {IGDB_FIELDS}; limit 5;'
    res = igdb_query(rate, token, client_id, body, f"search {search_name!r}")
    if res is None:
        return None  # transient — not cached, retried next run
    want = C.norm_title(search_name)
    exact = [g for g in res if C.norm_title(g.get("name") or "") == want]
    if ov and res:
        chosen, match = res[0], "override"
    elif exact:
        chosen, match = exact[0], "exact"
    elif res:
        chosen = max(res, key=lambda g: (g.get("total_rating_count") or 0))
        match = "best"
    else:
        chosen, match = None, "none"
    cache[key] = shape_igdb(chosen, match) if chosen else None
    return cache[key]


def fmt_mb(n):
    return f"{n / (1024 * 1024):.2f} MB"


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser(description="Parse KP's PlayStation sheets (played hours + purchase "
                                            "library), enrich via IGDB, and land static JSON for "
                                            "resonance-weaver's /games room.")
    p.add_argument("--land", action="store_true", help="write games.json + meta.json (+ covers) into --out-dir")
    p.add_argument("--out-dir", default=DEFAULT_OUT_DIR)
    p.add_argument("--source-dir", default=C.DEFAULT_SOURCE_DIR, help="consumed-media folder (reads ONLY this folder)")
    p.add_argument("--no-igdb", action="store_true", help="land without IGDB enrichment (no keys needed)")
    p.add_argument("--no-images", action="store_true", help="enrich, but download no covers")
    p.add_argument("--cover-size", choices=["t_cover_small_2x", "t_cover_big", "t_cover_big_2x"],
                   default="t_cover_small_2x", help="IGDB cover size (default t_cover_small_2x, 180x256)")
    p.add_argument("--report", action="store_true", help="print the per-work / per-game tables")
    args = p.parse_args()

    landed_at = C.iso_now()
    t_start = time.monotonic()
    gp_path = os.path.join(args.source_dir, "games", "playstation-gameplay.csv")
    tx_path = os.path.join(args.source_dir, "games", "playstation-transactions.csv")
    gp_rows, gp_skipped = read_ps_csv(gp_path, "game", "Name")
    tx_rows, tx_skipped = read_ps_csv(tx_path, "date", "Transaction Date")
    print(f"sources: gameplay {len(gp_rows)} rows (echo skipped {gp_skipped}) · "
          f"transactions {len(tx_rows)} rows (echo skipped {tx_skipped})")

    played = build_played(gp_rows)
    library = build_library(tx_rows)
    lib_by_search = {C.norm_title(g["search_name"]): g for g in library}
    for w in played:
        g = lib_by_search.get(C.norm_title(w["search_name"]))
        w["library_id"] = g["id"] if g else None

    # --- IGDB ----------------------------------------------------------
    igdb_enabled = bool(args.land) and not args.no_igdb
    igdb_stats = {"enabled": igdb_enabled, "exact": 0, "best": 0, "override": 0, "none": 0, "calls": 0,
                  "skipped_services": 0}
    cover_stats = {"size": args.cover_size, "played": 0, "library": 0, "bytes": 0, "total_bytes": 0}
    cache = C.load_cache(IGDB_CACHE)
    overrides = C.load_cache(OVERRIDES_FILE)
    covers_dir = os.path.join(args.out_dir, "covers")
    if igdb_enabled:
        client_id = C.env_value("TWITCH_CLIENT_ID", required=False)
        client_secret = C.env_value("TWITCH_CLIENT_SECRET", required=False)
        if not client_id or not client_secret:
            sys.exit(f"{C.TAG} TWITCH_CLIENT_ID / TWITCH_CLIENT_SECRET not found in the bridge .env — "
                     "run with --no-igdb to land without enrichment")
        token = twitch_token(client_id, client_secret)  # in memory only, never printed
        rate = C.RateLimiter(IGDB_MIN_INTERVAL)
        names = []
        for w in played:
            names.append(w["search_name"])
        for g in library:
            if g["service"]:
                igdb_stats["skipped_services"] += 1
                continue
            names.append(g["search_name"])
        uniq = []
        for n in names:
            if n not in uniq:
                uniq.append(n)
        print(f"IGDB: {len(uniq)} distinct names to resolve ({len(cache)} cached)...")
        resolved = {}
        done = 0
        for n in uniq:
            try:
                resolved[n] = igdb_lookup(rate, token, client_id, n, overrides, cache)
            except SystemExit:
                raise
            except Exception as e:  # one name never stops the others
                print(f"  {C.TAG} IGDB error for {n!r}: {e}")
                resolved[n] = None
            done += 1
            if done % 50 == 0 or done == len(uniq):
                print(f"  ...{done}/{len(uniq)}")
        C.save_cache(IGDB_CACHE, cache)
        igdb_stats["calls"] = rate.calls

        def attach(entry, bucket):
            r = resolved.get(entry["search_name"])
            entry["igdb"] = r
            entry["cover"] = None
            if r:
                igdb_stats[r["match"]] = igdb_stats.get(r["match"], 0) + 1
                if r.get("cover_image_id") and not args.no_images:
                    url = f"{IGDB_IMG}{args.cover_size}/{r['cover_image_id']}.jpg"
                    rel, n = C.resolve_image(rate, url, covers_dir, str(r["id"]), "/games/covers", USER_AGENT)
                    if rel:
                        entry["cover"] = rel
                        cover_stats[bucket] += 1
                        cover_stats["bytes"] += n
            else:
                igdb_stats["none"] += 1

        for w in played:
            attach(w, "played")
        for g in library:
            if g["service"]:
                g["igdb"] = None
                g["cover"] = None
            else:
                attach(g, "library")
        cover_stats["total_bytes"] = cover_stats["bytes"]
        print(f"IGDB: exact {igdb_stats['exact']} · best {igdb_stats['best']} · override {igdb_stats['override']} · "
              f"none {igdb_stats['none']} · services skipped {igdb_stats['skipped_services']} · "
              f"{igdb_stats['calls']} paced calls")
        print(f"covers: played {cover_stats['played']} · library {cover_stats['library']} · {fmt_mb(cover_stats['bytes'])}")
    else:
        for e in played + library:
            e["igdb"] = None
            e["cover"] = None

    # --- counts + report ----------------------------------------------
    played_hours = sum(w["hours_total"] for w in played)
    spend_total = sum(g["spend_cents"] for g in library)
    counts = {
        "played_works": len(played), "played_hours": played_hours,
        "played_sessions": sum(w["sessions"] for w in played),
        "library_games": len(library), "library_products": sum(g["product_count"] for g in library),
        "spend_total_cents": spend_total,
        "igdb_matched": sum(1 for e in played + library if e.get("igdb")),
        "covers": cover_stats["played"] + cover_stats["library"],
    }
    gp_dates = sorted(d for d in (C.mdy_to_iso(r.get("date")) for r in gp_rows) if d)
    tx_dates = sorted(d for d in (C.mdy_to_iso(r.get("date")) for r in tx_rows) if d)
    print()
    print(f"played: {len(played)} works · {played_hours} h (PlayStation's own count) · "
          f"{counts['played_sessions']} sessions · {gp_dates[0] if gp_dates else '-'} → {gp_dates[-1] if gp_dates else '-'}")
    for w in played:
        plat = ", ".join(f"{pl['platform']} {pl['hours']}h" for pl in w["platforms"])
        print(f"  {w['hours_total']:4d} h  {w['work']}  [{plat}]  {w['sessions']} sessions  "
              f"{w['first_played']} → {w['last_played']}" + (f"  igdb:{w['igdb']['match']}" if w.get("igdb") else ""))
    print(f"library: {len(library)} games · {counts['library_products']} products · "
          f"${spend_total / 100:,.2f} · {tx_dates[0] if tx_dates else '-'} → {tx_dates[-1] if tx_dates else '-'}")
    if args.report:
        for g in library:
            print(f"  ${g['spend_cents'] / 100:8,.2f}  {g['product_count']:3d}  {g['game']}"
                  + ("  [service]" if g["service"] else "") + ("  [subscription]" if g["subscription"] else "")
                  + (f"  igdb:{g['igdb']['match']}" if g.get("igdb") else ""))
    if igdb_enabled:
        none_list = [e["search_name"] for e in played + library if not e.get("service") and not e.get("igdb")]
        if none_list:
            print(f"  IGDB none ({len(none_list)}): " + " | ".join(none_list))

    if not args.land:
        print(f"\n(no files written — pass --land) · {time.monotonic() - t_start:.0f}s")
        return

    os.makedirs(args.out_dir, exist_ok=True)
    payload = {
        "landed_at": landed_at,
        "source": {
            "gameplay_rows": len(gp_rows), "transaction_rows": len(tx_rows),
            "gameplay_range": [gp_dates[0], gp_dates[-1]] if gp_dates else None,
            "transactions_range": [tx_dates[0], tx_dates[-1]] if tx_dates else None,
        },
        "counts": counts,
        "played": played, "library": library,
    }
    meta = {
        "landed_at": landed_at, "tool": TOOL_NAME,
        "sources": {"gameplay_csv": gp_path, "transactions_csv": tx_path,
                    "header_echo_skipped": gp_skipped + tx_skipped},
        "counts": counts, "igdb": igdb_stats, "covers": cover_stats,
    }
    C.write_json(os.path.join(args.out_dir, "games.json"), payload)
    C.write_json(os.path.join(args.out_dir, "meta.json"), meta)
    print(f"\nlanded {len(played)} played works + {len(library)} library games -> {os.path.join(args.out_dir, 'games.json')}")
    print(f"landed meta -> {os.path.join(args.out_dir, 'meta.json')} · {time.monotonic() - t_start:.0f}s")
    if not played and not library:
        sys.exit(1)


if __name__ == "__main__":
    main()
