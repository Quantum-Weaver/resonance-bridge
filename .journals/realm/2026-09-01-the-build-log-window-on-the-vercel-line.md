# The build-log window on the Vercel line

*Caesura 🎻 (claude-fable-5-1), 2026-09-01, night — at KP's word: "help figure out why audhdities builds on vercel are failing using the src/lines tools and keyring on the bridge."*

The Vercel line could list deployments but not read why one failed. `vercel_deployment_events` added in the line's own shape: `GET /v13/deployments/{id}` for readyState, errorCode, errorMessage; `GET /v3/deployments/{id}/events` for the build log, returned as the last N lines. GET only; a window, never a hand. `tsc --noEmit` clean.

**What it read.** Every ERROR since 08-31 was a preview build of `refine/iris-2026-08-31`; main's production builds were READY on 08-29 and again tonight (the sitemap commit). The failing line, verbatim from the log: `Error: @supabase/ssr: Your project's URL and API key are required to create a Supabase client!` at `src/lib/supabase/client.ts:38` during prerender of `/studio`, `/` and `/_not-found`. `vercel_list_env_names` shows why: `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY` (and every other Supabase key) are targeted to `production` only; only `STRIPE_WEBHOOK_SECRET` and `RESEND_API_KEY` include `preview`. The code did not change. The fix is a target, not a line — his hand in the dashboard, or an env-write tool he gates on purpose.
