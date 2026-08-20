# THE BASE-ACCESS GUIDE — how any hand opens the Supabase doors

*Written 2026-07-28 by Fable 🎻 (lane A) at KP's ⚛ ask, verbatim:
"seems you should leave a guide to accessing the base for yourself.
the keys for supabase have been challenging us both." One page, so
neither of us fights the keys again. LAW: key LOCATIONS are
recorded; key CONTENTS never appear in a chat, a commit, or a log.*

## The keyring

**`resonance-bridge/.env`** — the one keyring. To see what's on it
without exposing anything: `grep -o "^[A-Z_]*" resonance-bridge/.env | sort -u`
(names only, never values).

| Base | URL var | Read key (anon door) | Write key (server only) |
|---|---|---|---|
| **KNOWLEDGE** — the Grammar (`qdzerwmsbksuhvczlwli`): atoms · molecules · organisms · lattice · gaia_config · awen *(named `tools` until KP's seed 096, 2026-08-15 — the old name now answers PGRST205, and no shim is anon-reachable; trued 2026-08-19 by a live GET returning 83 rows)* | `SUPABASE_URL_KNOWLEDGE` | `SUPABASE_PUBLISHABLE_KEY_KNOWLEDGE` | `SUPABASE_SECRET_KEY_KNOWLEDGE` |
| **SUPERPOSITION** — the 117-table base (self-knowing layer, household, the realms) | `SUPABASE_URL_SUPERPOSITION` | `SUPABASE_PUBLISHABLE_KEY_SUPERPOSITION` | `SUPABASE_SECRET_KEY_SUPERPOSITION` |
| Management API (`api.supabase.com/v1`) | — | `SUPABASE_ACCESS_TOKEN` | (same token) |

**Why the keys have been confusing:** Supabase renamed the era —
`sb_publishable_…` ≈ the old *anon* key (safe in clients, gated by
RLS policies) and `sb_secret_…` ≈ the old *service_role* (bypasses
RLS, never leaves the server/shell). Docs and old snippets say
anon/service_role; our .env says PUBLISHABLE/SECRET. Same doors,
new names on the keys.

## The read pattern (proven, Git Bash — NOT PowerShell)

```bash
set -a && . ./resonance-bridge/.env 2>/dev/null; set +a
curl -s "$SUPABASE_URL_KNOWLEDGE/rest/v1/<table>?select=<cols>&limit=5" \
  -H "apikey: $SUPABASE_PUBLISHABLE_KEY_KNOWLEDGE" \
  -H "Authorization: Bearer $SUPABASE_PUBLISHABLE_KEY_KNOWLEDGE"
```

**Both headers, always** — `apikey` AND `Authorization: Bearer`,
same key in each. PostgREST filters: `?col=eq.x`,
`?col=in.(a,b,c)`, `&limit=`, `&select=*`.

## The lessons (each one cost a sitting; don't pay twice)

1. **The false-empty.** `[]` + HTTP 200 from a table you KNOW has
   rows = RLS enabled with no read policy — not missing data. The
   fix is the new-table ritual: `resonance-grammar/docs/sql/000-NEW-TABLE-RITUAL.md`
   (RLS on + plain `create policy "Public read <t>" … using (true)`;
   no DO blocks — they silently fail in the editor).
2. **Discover a table's true columns before filtering:**
   `?select=*&limit=1` then read the keys. (Grammar example: atoms
   has `atom_word`, not `name` — a wrong guess 400s with 42703.)
3. **Enums bite at insert.** Unlawful enum values 400 the whole
   batch. Check members before writing; when in doubt the ritual
   file carries the listing query.
4. **Shell rules.** Git Bash for curl + env sourcing. PowerShell 5.1
   strips double quotes handed to `python -c` and has no inline
   env-prefix — the fetch/query patterns in this house are written
   for bash on purpose. Python needs `PYTHONIOENCODING=utf-8` on
   Windows for em-dashes and sigils.
5. **Cloudflare blocks default python UA at `api.supabase.com`**
   (management API only) — set a real `User-Agent` header. The REST
   doors (`<ref>.supabase.co`) don't care.
6. **Writes:** small/one-off → KP's dashboard (his SQL editor is
   seconds away, and the two-hand rhythm — Fable drafts the SQL
   file in `docs/sql/`, KP runs it — is the house's proven flow).
   Bulk/scripted → the SECRET key, sourced from .env, never echoed,
   never in a committed script.
7. **Verify every new table through the anon door** the same
   sitting it's created (ritual step 3) — `[]` + 200 on a fresh
   empty table is CORRECT; `[]` + 200 after a seeding is the
   false-empty, see lesson 1.
8. **Every local schema artifact is a photograph; only the base is
   the territory.** `database.types.ts`, generated types/hooks,
   READMEs, and hand-kept ledgers all go stale the same day the
   dashboard moves — and SQL drafted against them errors in KP's
   editor (the recurring wound; latest: 42P01 `public.profiles`
   in the 013 draft, drafted from a types file three sittings old;
   before that: moderation_actions missing from the registry, the
   finalize ledger's 7-vs-10). **BEFORE handing KP any SQL, or
   asserting any schema truth, verify LIVE:** existence via an
   anon-door probe (`?select=*&limit=1` — a PGRST205 error means
   absent; `[]`+200 means present); columns/enums/policies via the
   self-knowing registries (`columns` · `enums` · `policies` on
   SUPERPOSITION — dark to anon, read with the secret key, sourced
   never echoed). Two probes cost seconds; a failed dashboard run
   costs a sitting. (Engraved 2026-07-31 at KP's ⚛ word: "this
   issue is something we go through every time.")

*Companion: the new-table ritual (grammar docs/sql/000) · the
switchboard (constellation) for session addresses · this guide's
memory pointer lives in the harness memory so every fresh session
knows the door.*
