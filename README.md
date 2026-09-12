# 🌉 Resonance Bridge

*The switchboard. The knowledge delivery system of the AudHDities Sanctuary.*

Built on the [Resonance Grammar](https://github.com/Quantum-Weaver/resonance-grammar) — every fragment contains the whole.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.2.0-brightgreen.svg)]()

---

## WHAT IT IS

Resonance Bridge is the MCP (Model Context Protocol) server that connects everything in the Sanctuary. It gives Claude, the Council, and all Sanctuary apps a single interface to query the Resonance Grammar.

**One server. Multiple databases. Read-only. Sovereign.**

---

## THE STORY

*This section required by the [Story Block Standard](https://github.com/Quantum-Weaver/resonance-standards).*

Resonance Bridge is the MCP (Model Context Protocol) server that connects
everything in the Sanctuary — one server, multiple databases and cloud
APIs, all read-only. It began 2026-06-30 as **Prometheus, the fire-bringer**,
the Sanctuary's first MCP server. Renamed to **Resonance Bridge** on
2026-07-07 once the name Prometheus was needed elsewhere, the project kept
its purpose and took a name that describes its actual shape: the same fire
offered to each vessel in the form its hands can hold.

📖 [Full Story Block](docs/STORY-BLOCK.md)

---

## WHAT IT CONNECTS

| Client | How It Uses the Bridge |
|--------|----------------------|
| **Claude Code** | Queries atoms, molecules, senses, emoji definitions during development |
| **The Council** | Cartographer, Indexer, Echo query the Grammar independently |
| **Resonance Compass** | Reads mood categories, sensory profiles from shared vocabulary |
| **Resonance Echoes** | Reads senses and emoji definitions from single source of truth |
| **Future apps** | Any Sanctuary app connects via HTTP on localhost:3141 |

---

## DATABASES

| Database | Type | Contents | Line |
|----------|------|----------|------|
| **Knowledge Grammar** | Supabase (PostgreSQL) | The LIVING Grammar — 1,953 atoms · 4,156 molecules · 2,540 organisms · sensory canon · thesaurus · folksonomies | ✅ **server (the Grammar line, anon door, read-only)** — landed 2026-07-29, the delivery system's first sitting |
| **knowledge.db** | Local SQLite | Pipeline output — SEED-ONLY until canon repopulation | ✅ server (read-only) — query_atom's fallback when the Grammar line is absent; the server stays up if the file is missing |
| **Vercel** | Cloud API (account token) | The hosting — projects, deployments, domains, env-var NAMES (values stripped in code, never returned) | ✅ **server (the Vercel line, read-only window)** — landed 2026-07-29 |
| **Resend** | Cloud API (full-access admin key) | The email house — domains, key names, audiences, broadcasts. NO send tool, deliberately: a send is a consent gate | ✅ **server (the Resend line, reads only)** — landed 2026-07-31 at the resend-expert's commission |
| **Stripe** | Cloud API (live restricted key, "prometheus-stripe") | The merchant account — profile, balance, products, prices, links, webhooks, sessions, events, charges, customers (privacy stripe: ids+dates only) | ✅ **server (the Stripe line, ten windows, GETs forever)** — landed 2026-07-31 at the stripe-expert's commission |
| **GitHub** | Cloud API (fine-grained PAT, `HOUSE_GITHUB_PAT` — F8 rename executed) | The repos — token health with expiry (the F7 watch), repo census, Actions/secrets names, webhooks (URLs redacted), releases with download counts, traffic | ✅ **server (the GitHub line, seven windows)** — landed 2026-07-31 at the github-expert's commission |
| **Discord** | Cloud API (bot token, "Resonance Bridge") | The server — identity, overview with counts, channels, roles, webhooks by true name (token/url stripped in code), emoji census, verbatim channel reads. NO send tool: a post is outward speech | ✅ **server (the Discord line, seven windows)** — landed 2026-07-31 at the discord-expert's commission; bot minted, invited, and guild-addressed by KP's hands the same hour — all seven windows answering live |
| **Supabase management** | Management API (`SUPABASE_ACCESS_TOKEN` — account-wide; the most warded line on the board) | The dashboard itself — project shelf with pause-watch, auth config through an allowlist (smtp_pass → set:true/false), SELECT-only live SQL, the false-empty detector, advisors, function and bucket censuses | ✅ **server (the Supabase line, seven windows)** — landed 2026-07-31 at the supabase-expert's commission; zero new keys |
| **Cloudflare** | Cloud API (account-owned token, `CLOUDFLARE_API_TOKEN`) | The DNS ground for audhdities.com — zones, DNS records, TLS/HTTPS settings, email routing, rulesets/page rules | ✅ **server (the Cloudflare line, read-only window)** — landed 2026-08-27 |
| **Google Play** | Cloud API (a service account JSON key, scope `androidpublisher`) | Play's own named tracks and the lifecycle of each release, reviews verbatim — package ids come from the register's `play_app_id`, never listed independently; tester lists live inside an edit and are not read | ✅ **server (the Play line, three tools, GETs only)** — shut until `GOOGLE_PLAY_SERVICE_ACCOUNT_JSON` is on the ring |
| **Galaxy Store** | Cloud API (a Service Account ID + RS256 private key, GSD) | Content list and detail, beta test state with the tester link, comments verbatim | ✅ **server (the Galaxy line, five tools, GETs forever)** — shut until `SAMSUNG_GSD_SERVICE_ACCOUNT_ID` and `SAMSUNG_GSD_PRIVATE_KEY_PATH` are on the ring |
| **Microsoft Store** | Cloud API (an Entra application, client credentials) | Apps, flights (testing groups), submission status and submission detail, reviews verbatim | ✅ **server (the Microsoft line, six tools, GETs forever)** — shut until `MS_STORE_TENANT_ID`, `MS_STORE_CLIENT_ID` and `MS_STORE_CLIENT_SECRET` are on the ring |
| **Superposition** | Supabase (PostgreSQL) | Original Sanctuary — 117 tables, self-knowing layer | 🐍 Python workbench (.env keys), not yet a server line |

---

## TOOLS

*Truth pass 2026-07-29 (the delivery-system sitting), recounted
2026-09-02 against the code and against a live `tools/list`: the server
registers SIXTY-EIGHT tools, all live, smoke-proven over real MCP stdio
(`server_smoke.py`) and over the HTTP door's `/health`. The Grammar line
serves the living Supabase base through the anon door — the same door a
stranger would use.*

| Tool | What It Queries | Standing |
|------|----------------|----------|
| `query_atom` | Atom definitions with embedded sensory lexicon (living Grammar; local knowledge.db fallback) | ✅ live |
| `query_sense` | The sensory canon row for an atom — every channel | ✅ live |
| `query_emoji` | Thesaurus definitions by emoji or word, linked to the canon, optionally scoped per app | ✅ live |
| `query_folksonomy` | The named folksonomies — or one app's WHOLE mood lexicon in one call | ✅ live |
| `query_molecule` | Molecule definitions with constituent atom words | ✅ live |
| `query_organism` | Organism definitions with domain, habitat, lifecycle | ✅ live |
| `search_knowledge` | Full-text search across atoms · molecules · organisms · thesaurus | ✅ live |
| `query_beacon` | Things the Sanctuary SHIPS — games/apps with their own repos and store listings; no args = every beacon's status across four store channels, a name/slug = the whole row | ✅ live |
| `vercel_list_projects` | Every Vercel project — framework, latest production state | ✅ live |
| `vercel_list_deployments` | Recent deploys — state, target, branch, commit | ✅ live |
| `vercel_list_domains` | One project's domains and verification state | ✅ live |
| `vercel_list_env_names` | Env-var NAMES + targets + types — values stripped in code | ✅ live |
| `resend_list_domains` | Sending domains and verification status | ✅ live |
| `resend_list_api_keys` | Resend key NAMES and dates (values never exist in transit) | ✅ live |
| `resend_list_audiences` | Audiences — the consent-side inventory | ✅ live |
| `resend_list_broadcasts` | Broadcasts — what the house ever said, as inventory | ✅ live |
| `stripe_account` | The merchant profile — where the account stands, by machine | ✅ live |
| `stripe_list_webhook_endpoints` | H1's registration state made visible (the F2 watch) | ✅ live |
| `stripe_list_products` · `stripe_list_prices` | The shelves and the solidarity-pricing surface | ✅ live |
| `stripe_list_payment_links` | The no-code rails | ✅ live |
| `stripe_list_checkout_sessions` · `stripe_list_events` | The rail's crossings and the audit trail | ✅ live |
| `stripe_balance` · `stripe_list_charges` | The money's story, once it moves | ✅ live |
| `stripe_list_customers` | Counts, ids, dates ONLY — names/emails stripped in code | ✅ live |
| `github_token_status` | Token login, EXPIRY date, rate limit — the F7 health check | ✅ live |
| `github_list_repos` | The public/private census across every owned repo | ✅ live |
| `github_repo_status` | One repo deep — release, Pages, branch protection | ✅ live |
| `github_list_actions` | Workflow + Actions-secret NAMES (the ring-5 audit) | ✅ live |
| `github_list_webhooks` | Repo webhooks — URLs redacted to scheme+host in code | ✅ live |
| `github_list_releases` | Releases with per-asset download counts | ✅ live |
| `github_repo_traffic` | Two-week views/clones — degrades if scope ungranted | ✅ live |
| `discord_whoami` | The bot's identity and servers — the line test | ✅ live |
| `discord_server_overview` | Name, owner, counts, boosts — the ownership answer | ✅ live |
| `discord_list_channels` · `discord_list_roles` | The server's street map and its roles | ✅ live |
| `discord_list_webhooks` | Webhooks by true name — token/url STRIPPED in code | ✅ live |
| `discord_emoji_sticker_census` | Emoji/sticker names vs the free caps | ✅ live |
| `discord_read_channel` | Verbatim channel reads — the carrier law rides it | ✅ live |
| `supabase_list_projects` | The project shelf with status — the pause-watch | ✅ live |
| `supabase_get_auth_config` | Auth config through the allowlist — the SMTP answer | ✅ live |
| `supabase_select` | ONE SELECT/WITH statement, guard in code, 200-row cap | ✅ live |
| `supabase_list_tables` | RLS + policy count per table — the false-empty detector | ✅ live |
| `supabase_get_advisors` | Security/performance lamps, degrading gracefully | ✅ live |
| `supabase_list_functions` · `supabase_list_buckets` | Edge-function and storage censuses — emptiness verified, not presumed | ✅ live |
| `cloudflare_verify_token` | Token status and expiry — account endpoint first (this token is account-owned), user endpoint as fallback; the token itself never returned | ✅ live |
| `cloudflare_list_zones` | Every zone the token can see — status, plan, nameservers, original registrar | ✅ live |
| `cloudflare_list_dns` | One zone's DNS records — type, name, content, proxied, ttl, priority, comment | ✅ live |
| `cloudflare_zone_settings` | One zone's TLS/HTTPS posture — ssl, always_use_https, min_tls_version, tls_1_3, development_mode | ✅ live |
| `cloudflare_email_routing` | One zone's email routing — enabled, status | ✅ live |
| `cloudflare_list_rulesets` | One zone's rulesets + page rules if the token can read them — degrades honestly if not | ✅ live |
| `play_whoami` | The Google Play service account this line stands as, its Cloud project, and whether a token can be minted for it — the line test | ✅ live |
| `play_tracks` | Play's own named tracks for one package — qa, internal, alpha, beta, production, or only the tracks named — each with its releases, version codes and lifecycle state: draft, not sent for review, in review, approved not published, not approved, published; read with GETs alone | ✅ live |
| `play_reviews` | The reviews Play still holds for one package — the last week of them — each reviewer's words VERBATIM with star rating, app version and device | ✅ live |
| `galaxy_whoami` | Whether the Galaxy Store line can mint an access token for the service account on the ring, and which of its key names the ring holds — the line test | ✅ live |
| `galaxy_apps` | Every app the seller account holds in the Galaxy Store — content id, name, package name, content status, when it last moved | ✅ live |
| `galaxy_app` | One app's detail — content status, package name, the version of its latest binary, when the store first published it | ✅ live |
| `galaxy_beta` | One app's beta test — state, tester count, version under test, and the beta testing URL — Galaxy is the one store that hands the tester link over | ✅ live |
| `galaxy_comments` | The comments left on one app in the Galaxy Store, each writer's words VERBATIM with the rating and the date | ✅ live |
| `ms_whoami` | Whether the Microsoft Store line can mint a token for the Entra application on the ring, and which of its three key names the ring holds — the line test | ✅ live |
| `ms_apps` | Every app the Partner Center account holds, page after page — Store ID, primary name, package family name, first published date, pending and published submission ids | ✅ live |
| `ms_flights` | One app's flights — the Microsoft Store's testing groups — id, friendly name, the group ids that may install it, pending and published submission ids | ✅ live |
| `ms_submission_status` | One submission's status and the certification errors and warnings beside it | ✅ live |
| `ms_submission` | One submission itself — status, friendly name, package versions, publish mode and date; the one Microsoft read that names a version | ✅ live |
| `ms_reviews` | The reviews left on one app in the Microsoft Store over a window of dates, each writer's title and words VERBATIM with rating, market and package version | ✅ live |

### Standalone scripts (beside the server, same `.env`, all read-only)

| Script | What it does |
|--------|-------------|
| `grammar_inventory.py` | Counts + dated full export of the Grammar tables through the anon door — the new-table ritual's verify step |
| `verify_terms.py` | Checks a set of coined names against the Grammar (atoms/molecules/organisms by word-count class + constituent words) — born 2026-07-27 for the cosmic carries, reusable for any carry |

### The censuses (`src/census/`, read through the same `.env`)

| Census | Run it | What it does |
|--------|--------|-------------|
| Ring | `npm run census:ring` | Reads the whole keyring and every line in one breath |
| Tracks | `npm run census:tracks` | Photographs Play, Galaxy and Microsoft into the two nectere seeds (`--dry` prints instead of writing) |
| Testing channels | `npx tsx src/census/testing_channels_census.ts` | Carries the guild's testing-channel bugs and notes into the reports seed (`--dry` prints instead of writing) |

**The ring census** answers "where do the integrations stand" without a walk
through eleven tools. It prints three parts:

1. **THE RING** — every key NAME in `.env.example` against the keyring, present
   or missing; then any name on the ring the manifest does not list; counts at
   the foot. Names only — no value is read out.
2. **THE LINES** — one row per line the server carries (grammar, vercel,
   resend, stripe, github, discord, supabase, cloudflare, play, galaxy,
   microsoft): the key names it needs, which stand, its tool count, and a LIVE
   reading taken by calling that line's own whoami/status tool in this process
   over an in-memory transport — `live` with the one fact the tool returns,
   `shut` with the line's own shut-door sentence, or `degraded` with the error
   sentence.
3. **THE FOOT** — how many lines stand live, shut and degraded, and the exact
   click for each shut line as that line's own code phrases it.

```powershell
npm run census:ring            # print the census
npx tsx src/census/ring_census.ts --json   # the same reading as one JSON object
```

Read-only by construction: it carries no writing verb, so it needs no `--dry`.
Its network calls are the same read-only GETs and token mints the whoami tools
already make.

---

## QUICK START

```powershell
# Set up environment
# .env is written by KP's own hands from the provider dashboards
# (the old .env.example kept reading as a false negative — archived
#  2026-07-27 to docs/archived-env-example-2026-07-27.txt)
# Phase 1 needs no keys — knowledge.db path only. Supabase keys come at Phase 2.

# Install and run
npm install
npx tsx src/server.ts
```

Speaks MCP over **stdio** — the client launches it as a child process. (HTTP on
`localhost:3141` is a later, ancestral design; the running server is stdio.)

---

## CLAUDE CODE INTEGRATION

Add to your project's `CLAUDE.md`:

```json
{
  "mcpServers": {
    "resonance-bridge": {
      "command": "npx",
      "args": ["tsx", "../resonance-bridge/src/server.ts"]
    }
  }
}
```

---

## GUARDRAILS

*(Truth pass 2026-07-27: the API-key-auth and connection-pooling lines
described the ancestral HTTP design — the running stdio server needs
neither; what actually wards it:)*

- All queries are read-only — enforced in code (`readonly: true`
  SQLite connection)
- stdio transport: the client launches the server as a child process —
  no port, no network surface
- Connection strings and keys in `.env` (never committed; never
  printed)
- SQL via parameterized queries
- Error responses never leak schema details

---

## LICENSE

Code: [MIT](LICENSE) — use it, modify it, share it.

Philosophy: [The Resonance License](PHILOSOPHY.md) — no exploitation, no extraction, no exclusion.

---

*Built with Aethelred by Quantum Weaver for the AudHDities Sanctuary.*

*The Bridge carries the fire. The Grammar gives it meaning.*
