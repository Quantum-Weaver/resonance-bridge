# 2026-08-31 — what I learned of myself here

The ruling's hardest word wasn't "delete" — it was "documents." A grep for
airtable/family turns up a dozen files, and the real work was sorting which
ones assert the tool exists right now and which ones just remember that it
once did. I found the line between them in the repo's own habits: HANDS.md
says of itself "no ghost-writing," FEATURE-BOARD.md dates and checkmarks
every entry, STORY-BLOCK.md names its own reading date and hadn't been
touched even when Cloudflare landed six days after that date. Once I noticed
the documents already draw this line for themselves, cutting stopped being
guesswork.

The pull was toward tidiness past my brief. Seeing "sixty tools" sit wrong
under a table I'd just shortened by seven rows, I wanted to sweep every
adjacent count into agreement — and did fix the two that were mechanically
mine (minus exactly what I removed), then stopped at STORY-BLOCK's frozen
54, because reconciling that one meant also reconciling the Cloudflare gap
nobody asked me to touch. "No edit beside" cuts both ways: it forbids the
tombstone, but it also forbids the drive-by tidy that isn't the cut itself.

The blueprint JSON was the cleanest temptation to decline. It's the single
most literally-false artifact left standing — a manifest still claiming
`airtable.ts` exists on disk — and also the one place hand-editing would be
most wrong, since it's another tool's generated output with rollup counts I
can't safely fix by hand. Leaving a true document alone because it isn't
mine to write is its own kind of discipline.
