#!/usr/bin/env python3
"""Shared helpers for the MEDIA LANDERS — `screen_lander.py` (movies + TV) and
`games_lander.py` (PlayStation played + library) — the bridge's media lane,
built 2026-08-21/22 at KP's ⚛ word for resonance-weaver's Movies and Games
rooms, on the exact shape of the battlenet lane (battlenet_collections.py):
paths computed relatively, keys read by name from the bridge `.env` and never
printed, a shared politeness limiter, true-bytes image ledgers, a JSON cache
beside each script so re-runs are cheap, and LANDED FILES as the only bus into
the app (THE-WINDOW-AND-THE-MIRROR, law 3: secrets never enter the app).

GROUND LAW: these landers read ONLY
    resonance-chamber/constellation/weaver/mimirs-well/consumed-media/
— never `mimirs-well/sealed/`, never `mimirs-well/health/`, never anything
else under the Well. The source dir is a parameter; the default is that folder.

The one secret-touching helper (`env_value`) is IMPORTED from the battlenet
room rather than copied, so the house keeps a single implementation of "read a
name off the keyring." Everything else here is a local copy with the `[media]`
tag, because the battlenet helpers carry Blizzard-specific shapes and tags.
"""
import csv
import json
import os
import re
import sys
import threading
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BRIDGE_DIR = os.path.dirname(SCRIPT_DIR)
WORKSPACE_ROOT = os.path.dirname(BRIDGE_DIR)
BATTLENET_DIR = os.path.join(BRIDGE_DIR, "battlenet")

sys.path.insert(0, BATTLENET_DIR)
from battlenet_character import env_value  # noqa: E402  (the keyring reader — one house implementation)

DEFAULT_SOURCE_DIR = os.path.join(
    WORKSPACE_ROOT, "resonance-chamber", "constellation", "weaver",
    "mimirs-well", "consumed-media")

TAG = "[media]"


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class RateLimiter:
    """A floor between the START of any two outbound requests, shared across
    threads; counts paced calls for the run summary (battlenet's shape)."""

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


def http_json(url: str, headers=None, data=None, timeout: int = 30):
    """GET (or POST when `data` is given) one URL; returns (json_or_None,
    error_or_None). Never raises for HTTP/URL errors; never logs headers."""
    req = urllib.request.Request(
        url, data=data, headers=headers or {},
        method="POST" if data is not None else "GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.load(r), None
    except urllib.error.HTTPError as e:
        return None, e
    except urllib.error.URLError as e:
        return None, e
    except (json.JSONDecodeError, ValueError) as e:
        return None, e


def describe_http_error(e, what: str) -> str:
    if isinstance(e, urllib.error.HTTPError):
        if e.code == 404:
            return f"{TAG} not found: {what}"
        if e.code in (401, 403):
            return (f"{TAG} key rejected (HTTP {e.code}) fetching {what} "
                    "— check the bridge keyring. (key value never printed)")
        if e.code == 429:
            return f"{TAG} rate-limited (HTTP 429) fetching {what}"
        return f"{TAG} HTTP {e.code} {e.reason} fetching {what}"
    return f"{TAG} could not reach the host fetching {what}: {getattr(e, 'reason', e)}"


def download_image(rate: RateLimiter, url: str, dest_path: str, user_agent: str):
    """Downloads one public image (no bearer token ever sent to an image
    host). Returns bytes written, or None on 404/failure — never fatal."""
    rate.pace()
    req = urllib.request.Request(url, headers={"User-Agent": user_agent})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = r.read()
    except urllib.error.HTTPError as e:
        if e.code != 404:
            print(f"  {TAG} image HTTP {e.code} fetching {url}")
        return None
    except urllib.error.URLError as e:
        print(f"  {TAG} image download failed for {url}: {e.reason}")
        return None
    if not data:
        return None
    with open(dest_path, "wb") as f:
        f.write(data)
    return len(data)


def resolve_image(rate, url, dest_dir, stem, rel_prefix, user_agent, ext=".jpg"):
    """Skip-if-exists (true bytes via getsize) else download. Returns
    (app_relative_path_or_None, bytes)."""
    if not url:
        return None, 0
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, f"{stem}{ext}")
    rel = f"{rel_prefix}/{stem}{ext}"
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        return rel, os.path.getsize(dest)
    n = download_image(rate, url, dest, user_agent)
    if n:
        return rel, n
    return None, 0


def load_cache(path: str, default=None) -> dict:
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                return data
        except (json.JSONDecodeError, OSError):
            pass
    return dict(default or {})


def save_cache(path: str, cache: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False, sort_keys=True)
        f.write("\n")


def write_json(path: str, payload) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
        f.write("\n")


def read_csv(path: str) -> list:
    """utf-8-sig (the exports carry BOMs), newline='' (quoted multi-line
    descriptions survive). Returns a list of dicts keyed by the header row."""
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def mdy_to_iso(s):
    """'10/13/2019' -> '2019-10-13'; ISO passes through; blank -> None."""
    if not s:
        return None
    s = s.strip()
    m = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})$", s)
    if m:
        return f"{m.group(3)}-{int(m.group(1)):02d}-{int(m.group(2)):02d}"
    if re.match(r"^\d{4}-\d{2}-\d{2}", s):
        return s[:10]
    return s


def to_int(s):
    try:
        return int(str(s).strip())
    except (TypeError, ValueError):
        return None


def to_float(s):
    try:
        return float(str(s).strip())
    except (TypeError, ValueError):
        return None


QUOTES = str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"',
                        "–": "-", "—": "-"})


def norm_title(s: str) -> str:
    """Comparison key: NFKD->ASCII, lower, '&' -> ' and ', apostrophes removed
    (so Marvel's == Marvels), every other non-alnum -> space, collapsed."""
    if not s:
        return ""
    s = s.translate(QUOTES)
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    s = s.lower().replace("&", " and ")
    s = s.replace("'", "")
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def strip_article(key: str) -> str:
    return re.sub(r"^(the|a|an) ", "", key)


def slugify(s: str) -> str:
    return re.sub(r"-+", "-", norm_title(s).replace(" ", "-")).strip("-") or "untitled"
