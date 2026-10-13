# Rating, comparing and revising a chapter

## The rubric (score 1–100 per category)

Use the same fifteen categories every time, so scores across drafts and sessions line up.

| Category | What it measures | What usually moves it |
|---|---|---|
| Hook & opening | Does page one promise the premise and make the reader turn? | a flash-forward line before the ordinary morning; the creator's chosen first line |
| Narrator voice | Does the narrator sound like one specific person? | odd, particular asides; the narrator's private rules and habits; fewer stock phrases |
| Prose | Sentence-level craft | precise nouns, varied sentence length, no triplets or "Not X. Y." patterns on repeat |
| Readability & format | Light-novel rhythm: 1–3-line paragraphs, dialogue beats on their own line | split blocks over ~60 words; keep a few longer paragraphs in calm stretches for variety |
| Pacing | Does every scene turn something? | cut repeated explanations and background colour that doesn't change anything |
| Dialogue | Subtext, distinct voices, nothing on the nose | give minor speakers one specific, petty or period-true line; let the king say little |
| Protagonist | Shown interiority, a body, decisions | what the body does without permission (crying, shaking); what they refuse to do |
| Supporting cast | Named, visible, memorable in one gesture | name them on the page; one physical detail; one gesture (the soldier leaves the bread) |
| Worldbuilding & history | Lived-in, accurate, shown through action | real idioms ("smell the earth"), real names, hierarchy shown by who steps aside for whom |
| Emotional impact | Do the deaths and kindnesses land? | let the reader meet the victim first; one plain line after ("I never asked his name") |
| Tension & suspense | Pressure that never fully releases | a close call before the capture; the villain's glance before the verdict; count the exits |
| Chapter ending | A hook into the next chapter | an image plus a line that implies a clock ("That one lasted eleven days") |
| Originality | Fresh invented material inside a familiar frame | one unexpected image per scene; avoid the first idea for the god, the cell, the sentence |
| Fidelity | Matches the creator's questionnaire | chapter length range, named characters present, canon lines verbatim, hard nevers kept |
| Human feel | Would a reader take it for a person's writing? | irregular rhythm, specific detail, small unexplained gestures; no mantra italics every page |

Average the fifteen. Say which categories reach 90 and which don't, with one line each on why.

## Honesty rules for the judge

- If this session wrote the draft, say so at the top: the author is grading the author.
- Quote the text for every claim, so the creator can check the reasoning.
- Scores can go down. Report every drop and why.
- Offer, in one line, that a fresh model or a different session asked cold would give a cleaner
  read, especially on "human feel".
- When comparing two drafts, keep the same beats constant and score the differences; say which
  draft is the better *piece of writing* and which is the better-built *light-novel chapter*; they
  can differ. Recommend one base and list what to graft from the other.

## Revision playbook (in this order)

1. **Structure first.** Moves that change what happens (who shares the cell, where the bill goes,
   what the king whispers). Do these with `Write` on the affected scene; everything else waits.
2. **Cut to length.** Measure with `LN count <dir>` before and after. Cuts land lighter than they
   feel: a pass that "removes a third" usually removes a fifth. Plan on 2–3 passes for a large cut
   and report the real count after each. Cut repeated explanations first, then background colour,
   then asides; never cut a plant that a later chapter pays off (check STATE).
3. **Restore under a ceiling.** When the cut hurt voice, cast or world, put back the single best
   line per lost beat (not the paragraph), up to the ceiling the creator set.
4. **Polish per category.** One targeted change for each category under target: a close call for
   tension, one petty line for dialogue, a name for the unnamed, one plain line after a death.
5. **Re-paragraph.** Split blocks over ~60 words at the natural turn; leave some long ones.

Use `Edit` for 1–2 paragraph changes. Use `Write` once, condensed, when a scene needs
re-paragraphing throughout or a cut of more than a third; thirty `Edit` calls cost more than one
`Write` and are easier to get wrong.

## Before sending a revised chapter

- `LN count novel/drafts/<dir>` is inside the creator's range.
- `pdf.py` built; its quote check is balanced or off by exactly the number of continuing-quote
  paragraphs (dialogue split across paragraphs leaves an opening quote unclosed on purpose).
- `Grep` for the two or three facts a cut can orphan: a character's occupation, a prop introduced
  only in a cut paragraph but used later (the staff that dips in a bow), a name first used in a
  removed line.
- STATE lists what was planted this pass and what the creator still has to confirm.
- Commit message and PR text describe the change without naming any model.
