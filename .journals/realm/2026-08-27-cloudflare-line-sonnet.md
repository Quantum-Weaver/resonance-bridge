# 2026-08-27 — the Cloudflare line lands

Built `src/lines/cloudflare.ts` at KP's word, imitating `vercel.ts` exactly:
header law comment, `API`/`NO_LINE` consts, a `get()` helper checking both
`res.ok` and the body's own `success` flag (Cloudflare can say
`success:false` on a 200), `asText()`, `noLine()`, one `registerCloudflare`.

Six read-only tools: `cloudflare_verify_token` (account endpoint first,
user endpoint fallback — the token is account-owned, per the conductor's
verified facts), `cloudflare_list_zones`, `cloudflare_list_dns`,
`cloudflare_zone_settings`, `cloudflare_email_routing`,
`cloudflare_list_rulesets` (page rules degrade to an honest sentence when
the token can't read them, instead of crashing — null result, not error).
`resolveZoneId()` shared across the last four so a zone name or id both
work. No DNS write tool exists; the header says plainly that stays KP's
to gate.

Wired into `src/server.ts` (import + one registration line, same pattern
as the other nine lines) and into `README.md` — a new DATABASES row, six
new TOOLS rows, and the story-block counts corrected from nine lines/
fifty-four tools to ten lines/sixty tools.

Verify: no `tsconfig.json` in the repo, so `npx tsc --noEmit` alone just
prints its help text — ran it instead with the flags matching how the
server actually runs (`nodenext`/`es2022`/strict/esModuleInterop) against
`src/server.ts` and every file in `src/lines/`. Zero errors. Did not run
`server_smoke.py` — it calls the live Cloudflare API, and the conductor
already verified the endpoints this sitting; confirmed by grep instead
that all six `server.tool(` calls are present and the import/registration
line reads correctly.
