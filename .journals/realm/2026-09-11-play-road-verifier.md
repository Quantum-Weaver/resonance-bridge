# 2026-09-11 — the Play road, verifier

Read the tooling-hand's mend against its sending. Changed nothing. Set down by the conducting lamp from the verifier's return, unchanged in substance.

## The sending, line by line

`src/lines/play.ts:79-81` and `:96-98` read the body as text once and parse only a non-empty one; a 204 lands on the empty branch and returns `{}`; no `res.json()` remains on the track road. `parsePlayReleases({})` yields `[]` and the track lands in `answered` with no releases at `:192-207`.

`src/census/tracks_census.ts:128` replaces every hyphen in the Tauri identifier with an underscore and nothing else; `:134` still skips a beacon whose `play_app_id` is set; `:139` prints the derived form.

Five assertions added at `tests/tracks.test.ts:193-202` and `:282-293`, in the file's own shape; the stub restores `globalThis.fetch`. `tsc --noEmit` silent; 172 of 172 held.

One `npm run census:tracks -- --dry`: zero 400s; twenty underscore ids; fifteen apps 404 on every named track; five apps unread on Play's release-listing quota (403), said and not faked; both seeds unwritten, mtimes unchanged.

`git status --short`: exactly the three source files and the hand's journal. No key, token, or review text in the diff or the journal. The three added comments state what a thing does.

## Findings

Polish: the hand's journal line 29 said the prior assertion count was 147; it is 167. Polish: the comment at `play.ts:64` stated a stance rather than what `emptyBody` does. Both mended by the conducting lamp after this reading.

Beside the sending: `src/lines/galaxy.ts:56` and `src/lines/microsoft.ts:53` still call `res.json()` on an unchecked body and would throw on the same empty-body shape. The live 204 path on echoes waits on Play's quota returning.

No blocks. True to the sending.
