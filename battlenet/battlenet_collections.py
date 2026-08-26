#!/usr/bin/env python3
"""Read one WoW character's ACCOUNT-WIDE collections + the character census —
W1 of THE WINDOW AND THE MIRROR (resonance-weaver/docs/THE-WINDOW-AND-THE-MIRROR.md),
built 2026-08-16 on top of the proven `battlenet_character.py` sibling in this
same room (same .env, same client-credentials OAuth, same plain-error style).
EXTENDED 2026-08-16 (build hand B1) with a detail+media ENRICH pass and local
icon downloads — schema v2 — so every collection item can open as a card with
description/source and a locally-hosted image (KP's ⚛ words: icons offline
was the lean, and "being able to open the items as cards to see details
would be ideal").

WHAT THIS IS:
  - Pulls, through ONE visible character (`--source realm/name`, default
    `azshara/scwaunchy`), the account-wide collections exposed on that
    character's profile: `/collections/mounts`, `/collections/pets`,
    `/collections/toys`, `/achievements` (summary only: total_quantity,
    total_points), `/collections/transmogs` (appearance_sets).
  - Resolves every item's NAME + whatever else the Profile API already embeds
    on the collection entry itself — HARVESTED, no extra call: pet
    level/quality/breed_id per pet INSTANCE (an account can own several
    instances of the same species at different levels/breeds).
  - `--enrich` (implied automatically by `--land`) runs a second pass, one
    Game-Data detail call per UNIQUE mount / pet species / toy (never per pet
    instance — multiple instances of the same species share one detail +
    icon fetch), plus the follow-on media call each family actually needs:
      * mounts:  GET /data/wow/mount/{id} -> description, source.name,
                 faction/requirements if present, creature_displays[0].id
                 -> GET /data/wow/media/creature-display/{id} -> render URL
                 (asset key is `zoom`, not `icon` — the CDN's actual shape).
      * pets:    GET /data/wow/pet/{speciesId} -> description,
                 battle_pet_type.name, source.name, AND an `icon` field
                 already embedded as a full render URL — NO separate media
                 call needed for pets (recount: the plan assumed one was;
                 the live payload already carries it, so it's skipped).
      * toys:    GET /data/wow/toy/{id} -> source.name + `source_description`
                 (recount: toy detail has NO top-level `description` field on
                 this API version — `source_description` is used as the
                 description, falling back to a literal `description` key
                 if Blizzard ever adds one) -> item.id
                 -> GET /data/wow/media/item/{id} -> render URL.
      * transmog (appearance) sets: probed ONCE at build time against the
        profile payload's own `key.href`
        (`/data/wow/item-appearance/set/{id}`) — it returns `set_name`
        (redundant with the name the profile payload already gives) and a
        list of appearance ids, with NO media in that one hop. Per this
        room's own fallback rule ("if a clean name+media exists, use it,
        else sets stay name-only"), transmog sets are landed name-only,
        `icon` always null, no per-set API calls spent chasing it further.
  - Icons download to `resonance-weaver/static/blizzard/icons/{mounts|pets|
    toys}/{id}.{ext}` (extension follows whatever the CDN actually serves,
    usually .jpg) straight from Blizzard's public render CDN — no bearer
    token is sent there (it isn't needed, and the token stays off any host
    but Blizzard's API proper). A 404 on either the detail or the media call
    marks that field/icon `null` and moves on; nothing here ever aborts the
    whole harvest for one bad id.
  - Politeness: every outbound enrichment request (detail, media, AND image
    download) passes through one shared rate limiter (~50ms floor between
    starts, shared across an 8-worker thread pool) and is cached by id in
    `enrich-cache.json` beside this script, so re-runs after the first are
    near-instant for anything already on disk.
  - `--land` mode ALSO reads the character census over `characters.csv`
    (realm,name per line — the sibling's proven road; profile+media calls
    reused via `import battlenet_character`) and writes three JSON files
    into `resonance-weaver/static/blizzard/`: `characters.json`,
    `collections.json` (schema v2, enriched), `meta.json` — the fixed
    contract W2 (the window's Svelte side) builds against sight-unseen.

WHAT THIS IS NOT: no writes to any base; no enumeration of collections for
characters other than the one `--source` names (account-wide collections are
the same for every character on the account, so one visible character is
enough — Blizzard's own API shape).

SECRETS LAW: BLIZZARD_CLIENT_ID / BLIZZARD_CLIENT_SECRET load from the
bridge's `.env` (via the sibling's `env_value`) and the bearer token stay
in memory only — neither is ever printed, logged, or written to any file
here, directly or indirectly. The bearer token is never sent to the image
CDN host (only to *.api.blizzard.com).

Usage:
    python battlenet_collections.py                       # pull + print, no files
    python battlenet_collections.py --enrich               # + detail/media pass, no files
    python battlenet_collections.py --source azshara/scwaunchy --land
    python battlenet_collections.py --land --out-dir X --census-file Y.csv

Errors are read plainly (404 says what wasn't found; 401/403 says the key
was rejected — its value never printed) and exit nonzero on failure. Per-item
enrichment errors are printed but never fatal — one bad id doesn't stop the
harvest.
"""
import argparse
import concurrent.futures
import json
import os
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

# battlenet_character.py lives beside this file; Python puts a script's own
# directory on sys.path[0] automatically, so this import resolves regardless
# of the caller's cwd.
import battlenet_character as bc

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BRIDGE_DIR = os.path.dirname(SCRIPT_DIR)
WORKSPACE_ROOT = os.path.dirname(BRIDGE_DIR)

DEFAULT_CENSUS_FILE = os.path.join(SCRIPT_DIR, "characters.csv")
DEFAULT_OUT_DIR = os.path.join(WORKSPACE_ROOT, "resonance-weaver", "static", "blizzard")
DEFAULT_CACHE_FILE = os.path.join(SCRIPT_DIR, "enrich-cache.json")

TOOL_NAME = "battlenet_collections.py"
DOWNLOAD_USER_AGENT = "resonance-bridge/battlenet_collections-icons"

ENRICH_WORKERS = 8
ENRICH_MIN_INTERVAL = 0.05  # ~50ms floor between outbound requests, shared


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def iso_from_ms(ts_ms):
    if not ts_ms:
        return None
    return (datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)
            .isoformat().replace("+00:00", "Z"))


def api_json(url: str, token: str, what: str) -> dict:
    """Fetches one URL via the sibling's api_get; exits plainly on error.
    Used only for the small set of calls this tool treats as load-bearing
    (source character + its five account-wide collection endpoints)."""
    body, err = bc.api_get(url, token)
    if err:
        sys.exit(bc.describe_http_error(err, what))
    return body


def fetch_mounts(host, namespace, locale, token, slug, name) -> list:
    url = (f"{host}/profile/wow/character/{slug}/{name}/collections/mounts"
           f"?namespace={namespace}&locale={locale}")
    body = api_json(url, token, f"mounts collection for '{name}' on '{slug}'")
    items = []
    for entry in body.get("mounts", []):
        m = entry.get("mount", {})
        if m.get("id") is not None and m.get("name"):
            items.append({"id": m["id"], "name": m["name"]})
    return items


def fetch_pets(host, namespace, locale, token, slug, name) -> list:
    url = (f"{host}/profile/wow/character/{slug}/{name}/collections/pets"
           f"?namespace={namespace}&locale={locale}")
    body = api_json(url, token, f"pets collection for '{name}' on '{slug}'")
    items = []
    for entry in body.get("pets", []):
        species = entry.get("species", {})
        # the per-item id here is the PET INSTANCE id (an account can own
        # several instances of the same species at different levels/breeds);
        # that is why the raw count (~213) exceeds the unique-species count
        # (~180). level/quality/breed_id are ALREADY on this same payload —
        # harvested here, no extra call spent to get them.
        if entry.get("id") is not None and species.get("name"):
            quality = entry.get("quality") or {}
            stats = entry.get("stats") or {}
            items.append({
                "id": entry["id"],
                "species_id": species.get("id"),
                "name": species["name"],
                "level": entry.get("level"),
                "quality": quality.get("name"),
                "breed": stats.get("breed_id"),
            })
    return items


def fetch_toys(host, namespace, locale, token, slug, name) -> list:
    url = (f"{host}/profile/wow/character/{slug}/{name}/collections/toys"
           f"?namespace={namespace}&locale={locale}")
    body = api_json(url, token, f"toys collection for '{name}' on '{slug}'")
    items = []
    for entry in body.get("toys", []):
        t = entry.get("toy", {})
        if t.get("id") is not None and t.get("name"):
            items.append({"id": t["id"], "name": t["name"]})
    return items


def fetch_transmog_sets(host, namespace, locale, token, slug, name) -> list:
    url = (f"{host}/profile/wow/character/{slug}/{name}/collections/transmogs"
           f"?namespace={namespace}&locale={locale}")
    body = api_json(url, token, f"transmogs collection for '{name}' on '{slug}'")
    items = []
    for entry in body.get("appearance_sets", []):
        if entry.get("id") is not None and entry.get("name"):
            items.append({"id": entry["id"], "name": entry["name"]})
    return items


def fetch_achievements_summary(host, namespace, locale, token, slug, name):
    url = (f"{host}/profile/wow/character/{slug}/{name}/achievements"
           f"?namespace={namespace}&locale={locale}")
    body = api_json(url, token, f"achievements summary for '{name}' on '{slug}'")
    return body.get("total_quantity", 0), body.get("total_points", 0)


def by_name(items):
    return sorted(items, key=lambda x: (x["name"] or "").lower())


def pull_collections(region, namespace, locale, token, source_realm, source_name):
    """Resolves the source character (for its canonical name/realm_slug),
    then pulls its five account-wide collection endpoints. Exits plainly if
    the source character itself can't be read."""
    host = f"https://{region}.api.blizzard.com"
    namespace_locale = (namespace, locale)
    summary, _raw, error = bc.fetch_character(region, namespace_locale, token,
                                               source_realm, source_name)
    if error:
        sys.exit(f"[battlenet] --source character unreadable: {error}")

    slug = summary["realm_slug"]
    name = bc.normalize_character_name(summary["name"])

    mounts = by_name(fetch_mounts(host, namespace, locale, token, slug, name))
    pets = by_name(fetch_pets(host, namespace, locale, token, slug, name))
    toys = by_name(fetch_toys(host, namespace, locale, token, slug, name))
    transmog_sets = by_name(fetch_transmog_sets(host, namespace, locale, token, slug, name))
    achievements_completed, achievement_points = fetch_achievements_summary(
        host, namespace, locale, token, slug, name)

    counts = {
        "mounts": len(mounts),
        "pets": len(pets),
        "toys": len(toys),
        "achievements_completed": achievements_completed,
        "achievement_points": achievement_points,
        "transmog_sets": len(transmog_sets),
    }
    source_character = {"name": summary["name"], "realm_slug": slug}
    return source_character, counts, mounts, pets, toys, transmog_sets


# The enrich pass: per-unique-id Game-Data detail + media, icon downloads,
# a shared politeness/rate limiter, and a disk cache so re-runs are cheap.

class RateLimiter:
    """Enforces a floor between the START of any two outbound requests this
    tool makes during the enrich pass, shared across every worker thread.
    Also counts total paced calls (reported in the run summary)."""

    def __init__(self, min_interval: float):
        self.min_interval = min_interval
        self._lock = threading.Lock()
        self._last = 0.0
        self.calls = 0

    def pace(self):
        with self._lock:
            now = time.monotonic()
            wait = self._last + self.min_interval - now
            if wait > 0:
                time.sleep(wait)
            self._last = time.monotonic()
            self.calls += 1


def load_cache(path: str) -> dict:
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                for kind in ("mount", "pet", "toy"):
                    data.setdefault(kind, {})
                return data
        except (json.JSONDecodeError, OSError):
            pass
    return {"mount": {}, "pet": {}, "toy": {}}


def save_cache(path: str, cache: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)
        f.write("\n")


def icon_ext_from_url(url: str) -> str:
    path = urllib.parse.urlsplit(url).path
    ext = os.path.splitext(path)[1].lower()
    if ext not in (".jpg", ".jpeg", ".png", ".gif"):
        ext = ".jpg"
    return ext


def enrich_api_get(rate: RateLimiter, url: str, token: str, what: str):
    """Non-fatal Game-Data GET for the enrich pass: prints a plain warning
    and returns None on error instead of exiting, so one bad id never stops
    the harvest of ~550 others."""
    rate.pace()
    body, err = bc.api_get(url, token)
    if err:
        print("  " + bc.describe_http_error(err, what))
        return None
    return body


def download_icon(rate: RateLimiter, url: str, dest_path: str):
    """Downloads one image from Blizzard's public render CDN (no bearer
    token sent — not needed, and the token never leaves *.api.blizzard.com).
    Returns bytes written, or None on 404/failure (never fatal)."""
    rate.pace()
    req = urllib.request.Request(url, headers={"User-Agent": DOWNLOAD_USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = r.read()
    except urllib.error.HTTPError as e:
        if e.code != 404:
            print(f"  [battlenet] icon HTTP {e.code} fetching {url}")
        return None
    except urllib.error.URLError as e:
        print(f"  [battlenet] icon download failed for {url}: {e.reason}")
        return None
    with open(dest_path, "wb") as f:
        f.write(data)
    return len(data)


_cache_write_lock = threading.Lock()


def _resolve_icon(rate, icon_url, icons_dir, item_id, result):
    """Shared tail end for mount/pet/toy enrichment: given a render URL,
    reuse the on-disk file if the cache already has it, else download it."""
    if not icon_url:
        return
    ext = icon_ext_from_url(icon_url)
    dest = os.path.join(icons_dir, f"{item_id}{ext}")
    rel = f"/blizzard/icons/{os.path.basename(icons_dir)}/{item_id}{ext}"
    if os.path.exists(dest):
        result["icon"] = rel
        result["icon_bytes"] = os.path.getsize(dest)
        return
    n = download_icon(rate, icon_url, dest)
    if n:
        result["icon"] = rel
        result["icon_bytes"] = n


def enrich_mount(rate, region, locale, token, mount_id, icons_dir, sub_cache):
    key = str(mount_id)
    cached = sub_cache.get(key)
    if cached is not None:
        return cached
    result = {"description": None, "source": None, "icon": None, "icon_bytes": 0}
    try:
        host = f"https://{region}.api.blizzard.com"
        namespace = f"static-{region}"
        detail = enrich_api_get(
            rate, f"{host}/data/wow/mount/{mount_id}?namespace={namespace}&locale={locale}",
            token, f"mount detail {mount_id}")
        if detail:
            result["description"] = detail.get("description")
            result["source"] = (detail.get("source") or {}).get("name")
            displays = detail.get("creature_displays") or []
            if displays and displays[0].get("id") is not None:
                disp_id = displays[0]["id"]
                media = enrich_api_get(
                    rate,
                    f"{host}/data/wow/media/creature-display/{disp_id}"
                    f"?namespace={namespace}&locale={locale}",
                    token, f"mount creature-display media {disp_id}")
                if media:
                    icon_url = None
                    for asset in media.get("assets", []):
                        if asset.get("key") in ("icon", "zoom"):
                            icon_url = asset.get("value")
                            if asset.get("key") == "icon":
                                break
                    _resolve_icon(rate, icon_url, icons_dir, mount_id, result)
    except Exception as e:  # one bad id never stops the other ~550
        print(f"  [battlenet] mount {mount_id} enrichment error: {e}")
    with _cache_write_lock:
        sub_cache[key] = result
    return result


def enrich_pet(rate, region, locale, token, species_id, icons_dir, sub_cache):
    key = str(species_id)
    cached = sub_cache.get(key)
    if cached is not None:
        return cached
    result = {"type": None, "description": None, "source": None, "icon": None, "icon_bytes": 0}
    try:
        host = f"https://{region}.api.blizzard.com"
        namespace = f"static-{region}"
        detail = enrich_api_get(
            rate, f"{host}/data/wow/pet/{species_id}?namespace={namespace}&locale={locale}",
            token, f"pet detail {species_id}")
        if detail:
            result["description"] = detail.get("description")
            result["type"] = (detail.get("battle_pet_type") or {}).get("name")
            result["source"] = (detail.get("source") or {}).get("name")
            # pet detail already embeds a full render URL under
            # `icon` — no separate /data/wow/media/pet/{id} call is spent.
            _resolve_icon(rate, detail.get("icon"), icons_dir, species_id, result)
    except Exception as e:
        print(f"  [battlenet] pet species {species_id} enrichment error: {e}")
    with _cache_write_lock:
        sub_cache[key] = result
    return result


def enrich_toy(rate, region, locale, token, toy_id, icons_dir, sub_cache):
    key = str(toy_id)
    cached = sub_cache.get(key)
    if cached is not None:
        return cached
    result = {"description": None, "source": None, "icon": None, "icon_bytes": 0}
    try:
        host = f"https://{region}.api.blizzard.com"
        namespace = f"static-{region}"
        detail = enrich_api_get(
            rate, f"{host}/data/wow/toy/{toy_id}?namespace={namespace}&locale={locale}",
            token, f"toy detail {toy_id}")
        if detail:
            # this API version has no top-level `description` on
            # toy detail — `source_description` is the real field; a literal
            # `description` is preferred if Blizzard ever adds one.
            result["description"] = detail.get("description") or detail.get("source_description")
            result["source"] = (detail.get("source") or {}).get("name")
            item_id = (detail.get("item") or {}).get("id")
            if item_id is not None:
                media = enrich_api_get(
                    rate,
                    f"{host}/data/wow/media/item/{item_id}?namespace={namespace}&locale={locale}",
                    token, f"toy item media {item_id}")
                if media:
                    icon_url = None
                    for asset in media.get("assets", []):
                        if asset.get("key") == "icon":
                            icon_url = asset.get("value")
                            break
                    _resolve_icon(rate, icon_url, icons_dir, toy_id, result)
    except Exception as e:
        print(f"  [battlenet] toy {toy_id} enrichment error: {e}")
    with _cache_write_lock:
        sub_cache[key] = result
    return result


def run_enrichment(region, locale, token, out_dir, mounts, pets, toys, transmog_sets):
    """Harvests detail+media for every UNIQUE mount / pet species / toy
    (never per pet instance), downloads icons locally, and returns the
    schema-v2 mounts/pets/toys/transmog_sets lists plus a coverage-stats
    dict for the run summary + meta.json."""
    cache = load_cache(DEFAULT_CACHE_FILE)
    icons_root = os.path.join(out_dir, "icons")
    mounts_dir = os.path.join(icons_root, "mounts")
    pets_dir = os.path.join(icons_root, "pets")
    toys_dir = os.path.join(icons_root, "toys")
    for d in (mounts_dir, pets_dir, toys_dir):
        os.makedirs(d, exist_ok=True)

    unique_mount_ids = sorted({m["id"] for m in mounts})
    unique_species_ids = sorted({p["species_id"] for p in pets if p.get("species_id") is not None})
    unique_toy_ids = sorted({t["id"] for t in toys})

    print(f"enriching {len(unique_mount_ids)} unique mounts, "
          f"{len(unique_species_ids)} unique pet species, "
          f"{len(unique_toy_ids)} unique toys "
          f"({ENRICH_WORKERS} workers, ~{int(ENRICH_MIN_INTERVAL * 1000)}ms floor)...")

    rate = RateLimiter(ENRICH_MIN_INTERVAL)
    mount_results, pet_results, toy_results = {}, {}, {}

    with concurrent.futures.ThreadPoolExecutor(max_workers=ENRICH_WORKERS) as ex:
        futs = {}
        for mid in unique_mount_ids:
            futs[ex.submit(enrich_mount, rate, region, locale, token, mid,
                            mounts_dir, cache["mount"])] = ("mount", mid)
        for sid in unique_species_ids:
            futs[ex.submit(enrich_pet, rate, region, locale, token, sid,
                            pets_dir, cache["pet"])] = ("pet", sid)
        for tid in unique_toy_ids:
            futs[ex.submit(enrich_toy, rate, region, locale, token, tid,
                            toys_dir, cache["toy"])] = ("toy", tid)
        total = len(futs)
        done = 0
        for fut in concurrent.futures.as_completed(futs):
            kind, ident = futs[fut]
            try:
                r = fut.result()
            except Exception as e:
                print(f"  [battlenet] {kind} {ident} worker error: {e}")
                r = {"description": None, "source": None, "icon": None, "icon_bytes": 0}
            (mount_results if kind == "mount" else
             pet_results if kind == "pet" else toy_results)[ident] = r
            done += 1
            if done % 100 == 0 or done == total:
                print(f"  ...{done}/{total}")

    save_cache(DEFAULT_CACHE_FILE, cache)

    mounts_out = []
    for m in mounts:
        r = mount_results.get(m["id"], {})
        mounts_out.append({
            "id": m["id"], "name": m["name"],
            "description": r.get("description"),
            "source": r.get("source"),
            "icon": r.get("icon"),
        })

    pets_out = []
    for p in pets:
        r = pet_results.get(p.get("species_id"), {})
        pets_out.append({
            "id": p["id"], "species_id": p.get("species_id"), "name": p["name"],
            "level": p.get("level"), "quality": p.get("quality"), "breed": p.get("breed"),
            "type": r.get("type"),
            "description": r.get("description"),
            "source": r.get("source"),
            "icon": r.get("icon"),
        })

    toys_out = []
    for t in toys:
        r = toy_results.get(t["id"], {})
        toys_out.append({
            "id": t["id"], "name": t["name"],
            "description": r.get("description"),
            "source": r.get("source"),
            "icon": r.get("icon"),
        })

    # Transmog (appearance) sets stay name-only cards — see the module
    # docstring's recount note on item-appearance/set/{id}.
    transmog_out = [{"id": s["id"], "name": s["name"], "icon": None} for s in transmog_sets]

    def coverage(merged, results):
        return {
            "total": len(merged),
            "with_description": sum(1 for x in merged if x.get("description")),
            "with_icon": sum(1 for x in merged if x.get("icon")),
            "icon_bytes": sum(r.get("icon_bytes", 0) for r in results.values()),
        }

    stats = {
        "calls_total": rate.calls,
        "mounts": coverage(mounts_out, mount_results),
        "pets": coverage(pets_out, pet_results),
        "toys": coverage(toys_out, toy_results),
        "transmog_sets": {"total": len(transmog_out), "with_description": 0,
                           "with_icon": 0, "icon_bytes": 0, "name_only": True},
    }

    return mounts_out, pets_out, toys_out, transmog_out, stats


def read_census_pairs(census_file: str) -> list:
    pairs = []
    with open(census_file, encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "," not in line:
                sys.exit(f"[battlenet] {census_file}:{lineno}: expected 'realm,name', got: {line!r}")
            realm, _, name = line.partition(",")
            pairs.append((realm.strip(), name.strip()))
    return pairs


def land_characters(region, namespace, locale, token, census_file: str):
    """Reads the character census over characters.csv via the sibling's own
    fetch_character (profile + character-media, same road as
    battlenet_character.py --file). Returns (characters, not_found)."""
    namespace_locale = (namespace, locale)
    pairs = read_census_pairs(census_file)
    characters = []
    not_found = []
    for realm, name in pairs:
        summary, raw, error = bc.fetch_character(region, namespace_locale, token, realm, name)
        if error:
            print(error)
            not_found.append({"name": name, "realm_slug": bc.normalize_realm_slug(realm)})
            continue
        profile = (raw or {}).get("character", {}) or {}
        characters.append({
            "name": summary["name"],
            "realm": summary["realm"],
            "realm_slug": summary["realm_slug"],
            "level": summary["level"],
            "class": summary["class"],
            "race": summary["race"],
            "faction": summary["faction"],
            "guild": summary["guild"],
            "last_login": iso_from_ms(profile.get("last_login_timestamp")),
            "portrait_url": summary["portrait"],
        })

    characters.sort(key=lambda c: ((c["realm"] or ""), -(c["level"] or 0)))
    return characters, not_found


def write_json(path: str, payload: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
        f.write("\n")


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser(
        description="Read one WoW character's account-wide collections "
                     "(mounts/pets/toys/achievements/transmog sets); "
                     "--enrich (implied by --land) adds detail+media+local "
                     "icons; --land also lands the character census + all "
                     "three static JSON files for resonance-weaver's "
                     "/blizzard window.")
    p.add_argument("--source", default="azshara/scwaunchy",
                    help="realm/name of the visible character to pull collections "
                         "through (default: azshara/scwaunchy)")
    p.add_argument("--enrich", action="store_true",
                    help="run the detail+media enrichment pass and download icons "
                         "locally (implied automatically by --land)")
    p.add_argument("--land", action="store_true",
                    help="also read the character census and write the three "
                         "static JSON files into resonance-weaver/static/blizzard/ "
                         "(implies --enrich)")
    p.add_argument("--census-file", default=DEFAULT_CENSUS_FILE,
                    help=f"path to the realm,name census file (default: {DEFAULT_CENSUS_FILE})")
    p.add_argument("--out-dir", default=DEFAULT_OUT_DIR,
                    help=f"where --land/--enrich write (default: {DEFAULT_OUT_DIR})")
    p.add_argument("--region", default="us", help="API region code (default: us)")
    p.add_argument("--locale", default="en_US", help="locale (default: en_US)")
    args = p.parse_args()

    if "/" not in args.source:
        sys.exit(f"[battlenet] --source must be 'realm/name', got: {args.source!r}")
    source_realm, _, source_name = args.source.partition("/")
    source_realm, source_name = source_realm.strip(), source_name.strip()
    if not source_realm or not source_name:
        sys.exit(f"[battlenet] --source must be 'realm/name', got: {args.source!r}")

    client_id = bc.env_value("BLIZZARD_CLIENT_ID")
    client_secret = bc.env_value("BLIZZARD_CLIENT_SECRET")
    token = bc.get_token(client_id, client_secret)  # never printed

    namespace = f"profile-{args.region}"
    landed_at = iso_now()

    source_character, counts, mounts, pets, toys, transmog_sets = pull_collections(
        args.region, namespace, args.locale, token, source_realm, source_name)

    print(f"source: {source_character['name']} @ {source_character['realm_slug']}")
    print(f"  mounts: {counts['mounts']}")
    print(f"  pets: {counts['pets']}")
    print(f"  toys: {counts['toys']}")
    print(f"  achievements: {counts['achievements_completed']} "
          f"({counts['achievement_points']} pts)")
    print(f"  transmog sets: {counts['transmog_sets']}")

    do_enrich = args.enrich or args.land
    enrich_stats = None
    if do_enrich:
        os.makedirs(args.out_dir, exist_ok=True)
        print()
        t0 = time.monotonic()
        mounts, pets, toys, transmog_sets, enrich_stats = run_enrichment(
            args.region, args.locale, token, args.out_dir,
            mounts, pets, toys, transmog_sets)
        elapsed = time.monotonic() - t0
        print(f"enrichment: {enrich_stats['calls_total']} outbound calls in {elapsed:.1f}s")
        for kind in ("mounts", "pets", "toys"):
            s = enrich_stats[kind]
            mb = s["icon_bytes"] / (1024 * 1024)
            print(f"  {kind}: {s['with_description']}/{s['total']} with description, "
                  f"{s['with_icon']}/{s['total']} with icon, {mb:.2f} MB icons on disk")
        print(f"  transmog sets: {enrich_stats['transmog_sets']['total']} "
              "name-only cards (item-appearance/set/{id} carries no media in "
              "one hop — icon stays null by design, see docstring)")

    if not args.land:
        return

    characters, not_found = land_characters(
        args.region, namespace, args.locale, token, args.census_file)

    os.makedirs(args.out_dir, exist_ok=True)

    characters_payload = {
        "landed_at": landed_at,
        "characters": characters,
        "not_found": not_found,
    }
    collections_payload = {
        "landed_at": landed_at,
        "source_character": source_character,
        "counts": counts,
        "mounts": mounts,
        "pets": pets,
        "toys": toys,
        "transmog_sets": transmog_sets,
    }
    total_icon_bytes = sum(enrich_stats[k]["icon_bytes"] for k in
                            ("mounts", "pets", "toys", "transmog_sets"))
    meta_payload = {
        "landed_at": landed_at,
        "source_character": source_character,
        "counts": counts,
        "tool": TOOL_NAME,
        "enriched": True,
        "icons": {
            "mounts": {"count": enrich_stats["mounts"]["with_icon"],
                       "bytes": enrich_stats["mounts"]["icon_bytes"]},
            "pets": {"count": enrich_stats["pets"]["with_icon"],
                     "bytes": enrich_stats["pets"]["icon_bytes"]},
            "toys": {"count": enrich_stats["toys"]["with_icon"],
                     "bytes": enrich_stats["toys"]["icon_bytes"]},
            "transmog_sets": {"count": 0, "bytes": 0, "name_only": True},
            "total_bytes": total_icon_bytes,
        },
    }

    characters_path = os.path.join(args.out_dir, "characters.json")
    collections_path = os.path.join(args.out_dir, "collections.json")
    meta_path = os.path.join(args.out_dir, "meta.json")

    write_json(characters_path, characters_payload)
    write_json(collections_path, collections_payload)
    write_json(meta_path, meta_payload)

    print()
    print(f"landed {len(characters)} characters, {len(not_found)} not found -> {characters_path}")
    print(f"landed collections (schema v2, enriched) -> {collections_path}")
    print(f"landed meta -> {meta_path}")

    if not characters:
        sys.exit(1)


if __name__ == "__main__":
    main()
