# 🔥 Resonance Bridge

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

Born 2026-06-30 as **Prometheus, the fire-bringer** — the Sanctuary's first
MCP server, `query_atom` proven live over stdio in the Inspector days later.
Renamed 2026-07-07 to **Resonance Bridge** once "Prometheus" was needed
elsewhere (it now names the frontend creative-arts domain) — the switchboard
framing held, the fire carried forward under a new name. What started as one
tool over one local database grew, sitting by sitting, into eight read-only
lines under `src/lines/` (Grammar, Vercel, Resend, Stripe, GitHub,
Discord, Supabase management, and Cloudflare) and fifty-three tools registered — every one of them
a window, never a hand.

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
| **Superposition** | Supabase (PostgreSQL) | Original Sanctuary — 117 tables, self-knowing layer | 🐍 Python workbench (.env keys), not yet a server line |

---

## TOOLS

*Truth pass 2026-07-29 (the delivery-system sitting), recounted
2026-08-21 against the code (`grep` over `src/lines/*.ts`): the server
registers FIFTY-THREE tools, all live, smoke-proven over real MCP stdio
(`server_smoke.py`). The Grammar line serves the living Supabase
base through the anon door — the same door a stranger would use.*

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
| `discord_server_overview` | Name, owner, counts, boosts — the ownership answer | ✅ live (awaits guild id) |
| `discord_list_channels` · `discord_list_roles` | The server's street map and its roles | ✅ live (awaits guild id) |
| `discord_list_webhooks` | Webhooks by true name — token/url STRIPPED in code | ✅ live (awaits guild id) |
| `discord_emoji_sticker_census` | Emoji/sticker names vs the free caps | ✅ live (awaits guild id) |
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

### Standalone scripts (beside the server, same `.env`, all read-only)

| Script | What it does |
|--------|-------------|
| `grammar_inventory.py` | Counts + dated full export of the Grammar tables through the anon door — the new-table ritual's verify step |
| `seeding/atoms_dump.py` | Atom-table dump for merge planning (on the seeding shelf since 2026-08-14) |
| `verify_terms.py` | Checks a set of coined names against the Grammar (atoms/molecules/organisms by word-count class + constituent words) — born 2026-07-27 for the cosmic carries, reusable for any carry |
| `seeding/` | The seeding era's shelf — seeders, wave generators, wipe/purge hands, the beacon-verify pair; one-shots kept whole, run by hand in their day (`seeding/README.md`; shelved 2026-08-14 at KP's ⚛ "tidy now") |

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
      "args": ["tsx", "C:/_superposition/resonance-bridge/src/server.ts"]
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
