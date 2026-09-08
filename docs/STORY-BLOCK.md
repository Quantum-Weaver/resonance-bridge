# Story Block — Resonance Bridge

*Following the [Story Block Standard](https://github.com/Quantum-Weaver/resonance-standards/blob/main/docs/STORY-BLOCK-TEMPLATE.md).*

## WHAT

The MCP (Model Context Protocol) server that connects everything in the
Sanctuary — one server, multiple databases and cloud APIs, all read-only
(`README.md` §WHAT IT IS). It gives Claude, the Council, and Sanctuary apps
a single interface over stdio to query the Resonance Grammar and read the
house's own platform accounts (Vercel, Resend, Stripe, GitHub, Discord,
Supabase management, Cloudflare).

## HOW

TypeScript + Node + `@modelcontextprotocol/sdk` + better-sqlite3, stdio
transport (`CLAUDE.md`). Built by Quantum Weaver (KP) with Aethelred, whose
design sessions with KP grew the Bridge's original architecture (`HANDS.md`).

## WHERE

`../resonance-bridge` — one of the Sanctuary's platform repos. Neighbors:
`resonance-knowledge`/`resonance-grammar` (the living database this server
queries), the family apps (echoes, compass, hearth, lantern, bubbles,
sistrum, khoros), and `resonance-ziggy`'s vessel, which reaches the Bridge
through its HTTP door.

## WHEN

- 2026-06-30 — founded as "Resonance MCP — Prometheus, the fire-bringer"
  (`git log`, commit `ef635dc`).
- 2026-07-07 — renamed Prometheus → Resonance Bridge once the name was
  needed elsewhere, for the frontend creative-arts domain (`CLAUDE.md`).

## WHY

Before the Bridge, every Sanctuary app and every AI vessel that wanted to
query the shared vocabulary (the Resonance Grammar) or check the house's
own platform accounts had no common door. The Bridge is that one door: a
single, read-only, sovereign interface — "one server, multiple databases"
(`README.md` §WHAT IT IS).

## INSPIRATION

Named Prometheus at birth — "the fire-bringer" (`git log`, commit
`ef635dc`) — for bringing the Grammar's fire to every vessel that needed
it. When the name was needed elsewhere, the project kept its purpose and
took a name that describes its actual shape: "the same fire offered to
each vessel in the form its hands can hold" (`HANDS.md`, Fable's scribed
note, 2026-07-09).

## PROVENANCE

Defined 2026-06-30 by Quantum Weaver and Aethelred as "Resonance MCP —
Prometheus" (`git log`, commit `ef635dc`); redefined in name 2026-07-07
(`CLAUDE.md`).
