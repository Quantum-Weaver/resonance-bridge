# The media landers retire — 2026-08-28

Firth 🎻 (Fable, `claude-fable-5`), from the Weaver's sitting, after M3 and M4
ran.

**Why.** THE-CARRY-GOES-LIVE M3 — a title typed by hand, fetched at the moment
with the keys on KP's device — ran: *"the game i just added was purchased on
Steam to play on PC"* · *"Once Human"* · *"i trust the test with games to be a
test for the adding a movie."* M4, the Steam library, ran the same night:
*"steam update successful."* His ruling on the landers stood from the day
before: *"yes retired from bridge once not needed(keys and tools)."*

**What left.** `media/` whole — `screen_lander.py`, `games_lander.py`,
`_common.py`, and the caches and overrides that were theirs (`igdb-cache.json`,
`igdb-overrides.json`, `imdb-match-cache.json`, `imdb-overrides.csv`,
`poster-cache.json`, `review-fuzzy.csv`); git holds them. `TMDB_API_KEY`,
`TMDB_READ_ACCESS_TOKEN`, `TWITCH_CLIENT_ID`, `TWITCH_CLIENT_SECRET` dropped
from the keyring by the same byte-preserving script as the Blizzard pair; the
four names retired in `.env.example` with a note; a dated line on the feature
board beside the lane. The Weaver's `npm run movies` and `npm run games` are
gone; its `static/movies` and `static/games` stay as the base layer the landers
wrote last.

**What stays.** Nothing of the three landers. The Bridge's keyring is smaller by
six names since yesterday; the Weaver's carries eight.

**Held:** the same rule as the day before — a tool retires when the road it
served has been walked another way and someone said so.

**And a file that must not live anywhere.** KP added Google Search Console
to the keyring and asked where its downloaded `client_secret` JSON should
live: *"i put most of what is in the json file in the env, but not all,
where should that file live?"* Nowhere. Its two secret-bearing fields
(`client_id`, `client_secret`) were already on the keyring with the project
id; its other four fields are Google's constants. Git did not ignore it — the
next sync would have carried a client secret. Deleted; `.gitignore` now
refuses `*client_secret*.json`, `*_secret*.json`, service-account keys,
`token.json` and `*.credentials.json` outright; `.env.example` names the
refresh token the consent flow will yield, so it lands on the keyring too,
never in a token file. The ward, applied: secrets stay pointers.

**The consent ran.** *"let us get the GOOGLE_SEARCH_REFRESH_TOKEN while we are
discussing it."* A local callback on `localhost:8765`, the consent page in his
browser, the code exchanged with the client id and secret read by path, the
refresh token appended to the keyring — nothing printed. Two walls first, both
Google's: `redirect_uri_mismatch` (the web client had no redirect URI
registered — the deleted JSON had carried none, so it would not have helped;
he added `http://localhost:8765/callback`), then `403 access_denied` for an
account that was not a tester of the app in Testing mode (*"had to add my own
email"*). Proven read-only: the token refreshes, scope
`webmasters.readonly`, and the consenting account is siteOwner of
`sc-domain:audhdities.com`. A Search Console line is a window to build at his
word; the keys it needs are all on the keyring now.
