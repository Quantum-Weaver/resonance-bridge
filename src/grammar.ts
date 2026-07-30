import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

// The Grammar line — read-only, sovereign. Serves the LIVING Resonance
// Grammar: the seeded Supabase knowledge base (atoms · molecules · organisms ·
// sensory canon · thesaurus · folksonomies). The door is the publishable
// (anon) key gated by RLS public-read policies — the same door a stranger
// would use; the secret key never enters this file or this process's needs.
// GET requests only; the ward is code.

const NO_LINE =
  "The Grammar line is not connected. Add SUPABASE_URL_KNOWLEDGE and " +
  "SUPABASE_PUBLISHABLE_KEY_KNOWLEDGE to .env by your own hands (read door " +
  "only — never the secret key), then restart the Bridge. The local " +
  "knowledge.db line awaits canon repopulation and cannot answer yet.";

function line() {
  const url = process.env.SUPABASE_URL_KNOWLEDGE;
  const key = process.env.SUPABASE_PUBLISHABLE_KEY_KNOWLEDGE;
  return url && key ? { url, key } : null;
}

async function grammarGet(path: string, params: Record<string, string> = {}) {
  const l = line();
  if (!l) throw new Error(NO_LINE);
  const url = new URL(`${l.url}/rest/v1/${path}`);
  for (const [k, v] of Object.entries(params)) url.searchParams.set(k, v);
  const res = await fetch(url, {
    headers: { apikey: l.key, Authorization: `Bearer ${l.key}` },
  });
  if (!res.ok) {
    const body = (await res.text()).slice(0, 300);
    throw new Error(`Grammar line ${res.status}: ${body}`);
  }
  return res.json();
}

function asText(data: unknown) {
  return { content: [{ type: "text" as const, text: JSON.stringify(data, null, 2) }] };
}

function noLine() {
  return { content: [{ type: "text" as const, text: NO_LINE }] };
}

// The sensory columns worth carrying with an atom — the lexicon's channels.
const SENSORY_EMBED =
  "sensory_lexicon(emoji,color_hex,sound_description,sound_tone,texture,temperature,shape,movement,taste,smell)";

export function registerGrammar(
  server: McpServer,
  localAtomFallback?: (term: string) => { row: unknown; count: number }
) {
  server.tool(
    "query_atom",
    "Look up a Resonance Grammar atom by its word — definition, type, weight, state, and the full sensory lexicon (emoji, color, sound, texture, temperature). Served from the living Grammar (Supabase).",
    { term: z.string().describe("atom word, lowercase single word, e.g. 'resonance'") },
    async ({ term }) => {
      if (!line()) {
        // The local knowledge.db line answers only when the canon repopulation
        // has landed; until then it reports its own emptiness honestly.
        if (localAtomFallback) {
          const { row, count } = localAtomFallback(term.toLowerCase());
          return asText(
            row ?? `No atom named '${term}' in local knowledge.db (holds ${count}).`
          );
        }
        return noLine();
      }
      const rows = (await grammarGet("atoms", {
        atom_word: `eq.${term.toLowerCase()}`,
        select: `atom_word,definition,atom_type,weight,state,category_name,status,created_by,${SENSORY_EMBED}`,
      })) as unknown[];
      if (rows.length > 0) return asText(rows.length === 1 ? rows[0] : rows);
      return asText(`No atom named '${term}' in the living Grammar.`);
    }
  );

  server.tool(
    "query_sense",
    "Look up the sensory canon row for an atom word — every sensory channel the Grammar holds for it: emoji, color, sound (description/tone/pitch/frequency/timbre), temperature, texture, shape, movement, taste, smell.",
    { term: z.string().describe("atom word the sensory row belongs to, e.g. 'focus'") },
    async ({ term }) => {
      if (!line()) return noLine();
      const rows = (await grammarGet("sensory_lexicon", {
        atom_word: `eq.${term.toLowerCase()}`,
        select: "*",
      })) as unknown[];
      return asText(
        rows.length > 0 ? (rows.length === 1 ? rows[0] : rows)
          : `No sensory row for '${term}' — the canon grows at KP's word.`
      );
    }
  );

  server.tool(
    "query_emoji",
    "Look up thesaurus definitions by emoji or word — an emotion's emoji, word, definition, colors, sensory profile, and its link into the sensory canon. Optionally scoped to one app's folksonomy (Echoes, Compass, Hearth).",
    {
      emoji: z.string().optional().describe("the emoji itself, e.g. '🎯'"),
      word: z.string().optional().describe("the feeling word, e.g. 'Focused' (case-insensitive)"),
      folksonomy: z.string().optional().describe("optional app scope: Echoes | Compass | Hearth"),
    },
    async ({ emoji, word, folksonomy }) => {
      if (!line()) return noLine();
      if (!emoji && !word) return asText("Give an emoji or a word — one is enough.");
      const params: Record<string, string> = {
        select: `emoji,word,definition,color_hex,sensory_color,sensory_sound,sensory_texture,sensory_temperature,folksonomy_type,sensory_lexicon(atom_word,emoji,color_hex)`,
        order: "folksonomy_type",
      };
      if (emoji) params.emoji = `eq.${emoji}`;
      if (word) params.word = `ilike.${word}`;
      if (folksonomy) params.folksonomy_type = `eq.${folksonomy}`;
      const rows = (await grammarGet("thesaurus", params)) as unknown[];
      return asText(rows.length > 0 ? rows : "No thesaurus row matches — the twins are sovereign; try the other app's set, or no scope.");
    }
  );

  server.tool(
    "query_folksonomy",
    "With no arguments: list the named folksonomies (name, purpose, status). With an app name: deliver that app's WHOLE mood lexicon in one call — the set intended and nothing else — each row linked to the sensory canon.",
    { app: z.string().optional().describe("folksonomy name: Echoes | Compass | Hearth (omit to list all)") },
    async ({ app }) => {
      if (!line()) return noLine();
      if (!app) {
        return asText(await grammarGet("folksonomies", { select: "name,purpose,status,notes", order: "name" }));
      }
      const rows = (await grammarGet("thesaurus", {
        folksonomy_type: `eq.${app}`,
        select: `emoji,word,definition,color_hex,sensory_color,sensory_sound,sensory_texture,sensory_temperature,sensory_lexicon(atom_word)`,
        order: "word",
      })) as unknown[];
      return asText(rows.length > 0 ? rows : `No folksonomy named '${app}' has rows yet. query_folksonomy with no arguments lists what stands.`);
    }
  );

  server.tool(
    "query_molecule",
    "Look up a Resonance Grammar molecule by name — definition, type, constituent atom words, bond type, functional group, domain, and weight. Case-insensitive.",
    { name: z.string().describe("molecule name, e.g. 'ResonanceBridge' or any coined compound") },
    async ({ name }) => {
      if (!line()) return noLine();
      const rows = (await grammarGet("molecules", {
        name: `ilike.${name}`,
        select: "name,molecule_type,definition,atom_words,derived_name,bond_type,functional_group,domain,total_weight,status,created_by",
      })) as unknown[];
      return asText(rows.length > 0 ? (rows.length === 1 ? rows[0] : rows) : `No molecule named '${name}' in the living Grammar.`);
    }
  );

  server.tool(
    "query_organism",
    "Look up a Resonance Grammar organism by name — definition, type, domain, habitat, and lifecycle. Case-insensitive.",
    { name: z.string().describe("organism name") },
    async ({ name }) => {
      if (!line()) return noLine();
      const rows = (await grammarGet("organisms", {
        name: `ilike.${name}`,
        select: "name,organism_type,definition,domain,habitat,lifecycle,status,created_by",
      })) as unknown[];
      return asText(rows.length > 0 ? (rows.length === 1 ? rows[0] : rows) : `No organism named '${name}' in the living Grammar.`);
    }
  );

  server.tool(
    "search_knowledge",
    "Full-text search across the living Grammar — atoms, molecules, organisms, and the thesaurus — matching words/names and definitions. Returns per-table matches, labeled.",
    {
      query: z.string().describe("search term, matched case-insensitively inside words, names, and definitions"),
      limit: z.number().min(1).max(25).optional().describe("max rows per table, default 5"),
    },
    async ({ query, limit }) => {
      if (!line()) return noLine();
      const n = String(limit ?? 5);
      const q = query.replaceAll(",", " ").trim();
      const [atoms, molecules, organisms, thesaurus] = await Promise.all([
        grammarGet("atoms", {
          or: `(atom_word.ilike.*${q}*,definition.ilike.*${q}*)`,
          select: "atom_word,definition,atom_type", limit: n,
        }),
        grammarGet("molecules", {
          or: `(name.ilike.*${q}*,definition.ilike.*${q}*)`,
          select: "name,definition,molecule_type", limit: n,
        }),
        grammarGet("organisms", {
          or: `(name.ilike.*${q}*,definition.ilike.*${q}*)`,
          select: "name,definition,organism_type", limit: n,
        }),
        grammarGet("thesaurus", {
          or: `(word.ilike.*${q}*,definition.ilike.*${q}*)`,
          select: "emoji,word,definition,folksonomy_type", limit: n,
        }),
      ]);
      return asText({ atoms, molecules, organisms, thesaurus });
    }
  );
}
