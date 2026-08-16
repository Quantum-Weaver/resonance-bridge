#!/usr/bin/env python3
"""Read one or more World of Warcraft characters from the Battle.net Game
Data / Profile APIs — a READING instrument, built ready ahead of need
(2026-08-15, KP's law: a ready-but-unused tool is correct, never premature).

KP holds a Battle.net subscription; the client id/secret already live on
this bridge's keyring (`.env`: BLIZZARD_CLIENT_ID, BLIZZARD_CLIENT_SECRET —
KP's own hand put them there). This tool waits on his character + realm
names; everything else is proven now.

WHAT THIS IS:
  - Client-credentials OAuth (`https://oauth.battle.net/token`) — an app
    talking to Blizzard about PUBLIC game data. No player ever consents to
    this app; there is nothing to consent to.
  - Given a realm + character name, reads that ONE character's public
    profile (level, class, race, faction, guild, last login) and its
    portrait media link.
  - `--realms` lists US realm names+slugs so KP can find his own realm's
    slug without guessing.

WHAT THIS IS NOT — engraved on purpose:
  Enumerating ALL characters on an ACCOUNT needs the user-consent OAuth
  flow (authorization-code grant, `wow.profile` scope) — Blizzard asking
  the account owner "let this app see your characters?" in a browser.
  That is KP's hand's flow, on his moment, and is NOT built here. This
  tool only reads characters whose realm+name he already supplies.

READ-ONLY ALWAYS: no writes to any base, no tables, no state kept between
runs. Nothing here mirrors, stores, or republishes character data beyond
the run that asked for it (or the file the caller names with --json).

Usage:
    python battlenet_character.py --realm area-52 --name Foobar
    python battlenet_character.py --realm area-52 --name Foobar --realm illidan --name Bazqux
    python battlenet_character.py --file characters.txt      # lines: realm,name
    python battlenet_character.py --realm area-52 --name Foobar --json out.json
    python battlenet_character.py --realms                   # list US realm slugs

Errors are read plainly: 404 says which realm/character was not found;
401/403 says the key was rejected and to check the keyring — the key
itself is never printed, echoed, or logged, here or anywhere.
"""
import argparse
import base64
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

# .env lives at the bridge repo root; this room is one level down
# (deepseek_message.py's pattern, copied exactly).
BRIDGE_ENV = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")

OAUTH_URL = "https://oauth.battle.net/token"
USER_AGENT = "resonance-bridge/battlenet_character"


def env_value(name, required=True):
    for line in open(BRIDGE_ENV, encoding="utf-8", errors="replace"):
        line = line.strip()
        if line.startswith(name + "="):
            return line.partition("=")[2].strip().strip('"').strip("'")
    if required:
        sys.exit(f"{name} not found in bridge .env")
    return None


def normalize_realm_slug(realm: str) -> str:
    """lowercase, spaces -> hyphens, apostrophes stripped."""
    s = realm.strip().lower().replace("'", "")
    s = re.sub(r"\s+", "-", s)
    return s


def normalize_character_name(name: str) -> str:
    return name.strip().lower()


def get_token(client_id: str, client_secret: str) -> str:
    """Client-credentials OAuth against oauth.battle.net. Returns the
    bearer token. Never prints client_id/client_secret."""
    creds = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    req = urllib.request.Request(
        OAUTH_URL,
        data=b"grant_type=client_credentials",
        headers={
            "Authorization": f"Basic {creds}",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": USER_AGENT,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            body = json.load(r)
    except urllib.error.HTTPError as e:
        if e.code in (401, 403):
            sys.exit("[battlenet] token request rejected (401/403) — check "
                      "BLIZZARD_CLIENT_ID / BLIZZARD_CLIENT_SECRET on the "
                      "keyring. (key value never printed)")
        sys.exit(f"[battlenet] token request failed: HTTP {e.code} {e.reason}")
    except urllib.error.URLError as e:
        sys.exit(f"[battlenet] could not reach {OAUTH_URL}: {e.reason}")
    token = body.get("access_token")
    if not token:
        sys.exit("[battlenet] token response had no access_token — "
                  f"response keys: {list(body.keys())}")
    return token


def api_get(url: str, token: str):
    """Returns (json_or_None, error_or_None). error is an HTTPError/URLError."""
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r), None
    except urllib.error.HTTPError as e:
        return None, e
    except urllib.error.URLError as e:
        return None, e


def describe_http_error(e, what: str) -> str:
    if isinstance(e, urllib.error.HTTPError):
        if e.code == 404:
            return f"[battlenet] not found: {what}"
        if e.code in (401, 403):
            return (f"[battlenet] key rejected (HTTP {e.code}) fetching {what} "
                     "— check the keyring. (key value never printed)")
        return f"[battlenet] HTTP {e.code} {e.reason} fetching {what}"
    return f"[battlenet] could not reach Battle.net fetching {what}: {getattr(e, 'reason', e)}"


def fetch_character(region: str, namespace_locale: tuple, token: str,
                     realm_slug: str, char_name: str):
    """Fetches the character profile + character-media. Returns
    (summary_dict_or_None, raw_dict_or_None, error_message_or_None)."""
    namespace, locale = namespace_locale
    host = f"https://{region}.api.blizzard.com"
    slug = normalize_realm_slug(realm_slug)
    name = normalize_character_name(char_name)

    profile_url = (f"{host}/profile/wow/character/{slug}/{name}"
                    f"?namespace={namespace}&locale={locale}")
    profile, err = api_get(profile_url, token)
    if err:
        return None, None, describe_http_error(
            err, f"character '{char_name}' on realm '{realm_slug}' (slug '{slug}')")

    media_url = (f"{host}/profile/wow/character/{slug}/{name}/character-media"
                 f"?namespace={namespace}&locale={locale}")
    media, media_err = api_get(media_url, token)
    portrait = None
    if media and not media_err:
        for asset in media.get("assets", []):
            if asset.get("key") == "avatar":
                portrait = asset.get("value")
                break
        if not portrait:
            for asset in media.get("assets", []):
                if asset.get("key") == "main":
                    portrait = asset.get("value")
                    break

    last_login = profile.get("last_login_timestamp")
    last_login_str = None
    if last_login:
        last_login_str = (datetime.fromtimestamp(last_login / 1000, tz=timezone.utc)
                           .strftime("%Y-%m-%d %H:%M UTC"))

    guild = profile.get("guild", {}).get("name") if profile.get("guild") else None

    summary = {
        "name": profile.get("name"),
        "realm": profile.get("realm", {}).get("name"),
        "realm_slug": profile.get("realm", {}).get("slug", slug),
        "level": profile.get("level"),
        "class": profile.get("character_class", {}).get("name"),
        "race": profile.get("race", {}).get("name"),
        "faction": profile.get("faction", {}).get("name"),
        "guild": guild,
        "last_login": last_login_str,
        "portrait": portrait,
    }
    raw = {"character": profile, "character_media": media}
    return summary, raw, None


def print_summary(s: dict) -> None:
    line1 = f"{s['name']} — {s['realm']} — level {s['level']} {s['race']} {s['class']} ({s['faction']})"
    print(line1)
    if s["guild"]:
        print(f"  guild: {s['guild']}")
    if s["last_login"]:
        print(f"  last login: {s['last_login']}")
    if s["portrait"]:
        print(f"  portrait: {s['portrait']}")
    print()


def fetch_realms(region: str, namespace_locale: tuple, token: str):
    namespace, locale = namespace_locale
    # realm index lives under the dynamic namespace, not profile
    dyn_namespace = f"dynamic-{region}"
    host = f"https://{region}.api.blizzard.com"
    url = f"{host}/data/wow/realm/index?namespace={dyn_namespace}&locale={locale}"
    body, err = api_get(url, token)
    if err:
        sys.exit(describe_http_error(err, "the realm index"))
    return body


def parse_pairs(args) -> list:
    pairs = []
    if args.realm or args.name:
        if len(args.realm) != len(args.name):
            sys.exit(f"[battlenet] {len(args.realm)} --realm value(s) but "
                      f"{len(args.name)} --name value(s) — give one of each, paired in order.")
        pairs.extend(zip(args.realm, args.name))
    if args.file:
        with open(args.file, encoding="utf-8") as f:
            for lineno, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "," not in line:
                    sys.exit(f"[battlenet] {args.file}:{lineno}: expected 'realm,name', got: {line!r}")
                realm, _, name = line.partition(",")
                pairs.append((realm.strip(), name.strip()))
    return pairs


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser(
        description="Read WoW character(s) from the Battle.net Profile API, "
                     "or list US realm slugs with --realms.")
    p.add_argument("--realm", action="append", default=[],
                    help="realm slug or name (repeatable, pairs in order with --name)")
    p.add_argument("--name", action="append", default=[],
                    help="character name (repeatable, pairs in order with --realm)")
    p.add_argument("--file", help="path to a file of lines 'realm,name'")
    p.add_argument("--json", metavar="OUTPATH", help="save raw API responses to this file")
    p.add_argument("--realms", action="store_true",
                    help="list US realm names+slugs from the Game Data realm index, then exit")
    p.add_argument("--region", default="us", help="API region code (default: us)")
    p.add_argument("--locale", default="en_US", help="locale (default: en_US)")
    args = p.parse_args()

    client_id = env_value("BLIZZARD_CLIENT_ID")
    client_secret = env_value("BLIZZARD_CLIENT_SECRET")
    token = get_token(client_id, client_secret)

    namespace_locale = (f"profile-{args.region}", args.locale)

    if args.realms:
        body = fetch_realms(args.region, namespace_locale, token)
        realms = sorted(body.get("realms", []), key=lambda r: r.get("name", ""))
        print(f"{len(realms)} realms ({args.region}):")
        for r in realms:
            print(f"  {r.get('name'):30s} {r.get('slug')}")
        if args.json:
            with open(args.json, "w", encoding="utf-8") as f:
                json.dump(body, f, indent=2)
            print(f"\nraw saved: {args.json}")
        return

    pairs = parse_pairs(args)
    if not pairs:
        sys.exit("[battlenet] nothing to read — give --realm/--name (paired), "
                  "--file, or --realms. See the docstring for usage.")

    raws = []
    any_ok = False
    for realm, name in pairs:
        summary, raw, error = fetch_character(args.region, namespace_locale, token, realm, name)
        if error:
            print(error)
            print()
            raws.append({"realm": realm, "name": name, "error": error})
            continue
        any_ok = True
        print_summary(summary)
        raws.append({"realm": realm, "name": name, **raw})

    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(raws, f, indent=2)
        print(f"raw saved: {args.json}")

    if not any_ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
