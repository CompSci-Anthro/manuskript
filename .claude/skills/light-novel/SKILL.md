---
name: light-novel
description: Write, plan, or revise the light novel in novel/ with a low-token workflow (compact story bible, rolling chapter summaries, one-shot scene drafting, helper script for all bookkeeping). Use whenever the user asks to plan, outline, draft, continue, revise, compare drafts of, rate, or make a PDF of the light novel, or to build its bible from the questionnaire artifact.
---

# Light novel: low-token writing workflow

Credits go mostly to **input tokens re-read every turn** and **output tokens that get thrown away**. This workflow keeps both small: you never re-read old chapters, you draft each scene once, and a script does the bookkeeping.

`LN` below means `python3 .claude/skills/light-novel/scripts/ln.py` (run it from the repo root). `PDF` means `python3 .claude/skills/light-novel/scripts/pdf.py`.

## Hard rules (these save the most)

1. **Never read finished chapters.** Continuity comes from `BIBLE.md`, `STATE.md` and the chapter summaries. Read a past scene only if the user names it, and then use `Grep` for the exact line, not the whole file. The one exception is a rating or comparison the user asks for: then read the draft once, score it, and don't read it again.
2. **Load context in one call: `LN context`.** It prints the bible, state, the last 2 chapter summaries and the current chapter's beats. Don't follow it with separate `Read` calls for the same files.
3. **Draft each scene in one `Write` call, straight into the scene file.** Don't draft in chat, don't write an outline of the scene first, and don't re-read the file afterward to check it.
4. **Revise with `Edit` for one or two paragraphs.** Use one condensed `Write` when a scene needs re-paragraphing throughout or a cut of more than a third; thirty `Edit` calls cost more than one `Write` and are easier to get wrong. Never rewrite a scene to change one line.
5. **Keep chat replies short.** Never paste prose into chat. After a scene, reply in at most 2 lines: file, word count (from `LN status`), and anything the user needs to decide. A rating or comparison the user asked for is the deliverable, so that one goes in chat in full.
6. **Use the script for all bookkeeping:** word counts, new files, alternate drafts, finding the next scene, exporting. Don't count words or list directories yourself.
7. **No subagents, no web search, no reading the Manuskript app source or `sample-projects/`.** None of it is needed for writing.
8. **Keep reasoning short.** The beats are already planned, so write from them. Spend thinking on structure only when planning a new chapter.
9. **Keep the memory files within their caps:** `BIBLE.md` ≤ 1,500 words, `STATE.md` ≤ 250 words, each summary ≤ 120 words. When something is added, cut something else. These files are read every session, so each extra word there costs again every time.
10. **Batch work.** If the user says "write chapter 3", write all its scenes in a row (one `Write` each), then update the summary and state once at the end, not after every scene.
11. **Measure, don't estimate.** After every cut or restore run `LN count <dir>` and report the real number. Cuts land lighter than they feel; a large cut takes 2–3 passes.
12. **No model names in the repository.** Not in file names, PDF labels, commits or PR text. Alternate drafts are "Draft A", "Draft B"; tell the user in chat which model wrote which.

## Files

```
novel/
  BIBLE.md          premise, cast (voice + speech tics), world rules, style sheet
  STATE.md          where we are, open threads, plants, what the creator must confirm, next action
  outline.md        one line per chapter; scene beats only for planned chapters
  summaries/chNN.md ≤120-word summary of each finished chapter
  chapters/chNN/sNN.md       the canonical prose, one file per scene
  drafts/chNN-draft-<x>/     alternate takes of a chapter, until one is promoted
  pdf/                       reading copies ("ChNN - Title.pdf", or "(Draft X)" for alternates)
```

## Commands

| Command | What it does |
|---|---|
| `LN init "Title"` | Create `novel/` from the templates (first time only) |
| `LN context` | Print everything needed to write the next scene |
| `LN status` | Word counts per chapter and scene, total, and the next empty scene |
| `LN count [PATH…]` | Prose words (no headers, breaks or comments) for any folder or file; use it on `drafts/` and after every cut |
| `LN new-chapter N S` | Create chapter N with S empty scene files |
| `LN draft N b S` | Create `drafts/chNN-draft-b/` with S empty scenes for an alternate take |
| `LN promote N b` | Make that draft the canonical `chapters/chNN`; the old chapter moves to `drafts/` |
| `LN export` | Build a Manuskript project at `novel-export/<title>.msk` + folder |
| `PDF N --volume "Volume 1: …" --author "…"` | Typeset chapter N as a 5.5 × 8.25 in reading-copy PDF in `novel/pdf/` (title page, chapter opener, running heads, bookmarks, tagged). `--watermark "Advance copy"` for early readers; `--src novel/drafts/<dir> --label "Draft B"` for an alternate. Needs Node + Playwright |
| `digest.py build DIR OUT` / `digest.py slice OUT s060-s069` | Compact the questionnaire artifact's answers and read a slice (see `references/questionnaire.md`) |

## Workflows

**Start from the questionnaire artifact** (the usual case): follow `references/questionnaire.md`. One artifact read, one `ArtifactData` dump, one digest, then read slices by part. `Write` `BIBLE.md`, `outline.md` and `STATE.md` once each. Put every contradictory or missing answer you resolved under "Confirm with creator" in STATE and in your report.

**Start without one:** run `LN init "Title"`, then ask the user in a single message for the premise, the main cast, the tone and the target length.

**Plan a chapter:** run `LN context`. In `outline.md`, add 3–6 beats per scene under that chapter's heading (one short line each: who, what changes, the closing hook). The chapter sections of the questionnaire often already hold this; copy, don't re-plan. Then `LN new-chapter N S`.

**Write (the main loop):**
1. Run `LN context` once at the start of the session.
2. For each scene in the chapter, `Write` `novel/chapters/chNN/sNN.md` from its beats.
3. When the chapter is done, `Write` `summaries/chNN.md` and update `STATE.md`: open threads, what was planted this chapter (so later chapters can pay it off), what the creator must confirm. Add new permanent facts to `BIBLE.md`.
4. Run `LN status` and give the user a one-line report.
5. If the user wants a reading copy, run `PDF N` and send the file with `SendUserFile`. Rebuild and resend after every revision pass. Don't render or re-read the PDF to proofread prose; check one page image only if the layout code changed.

**Alternate drafts (comparing voices or models):** `LN draft N b S`, then write the scenes from the same beats and bible, making different invented choices from the first draft (opening line, the god's realm, who shares the cell, the king's private line). Typeset with `--src … --label "Draft B"`, rename the first PDF "(Draft A)". In STATE, list where the drafts differ, one line per difference, so the winner can be folded into the bible without rereading both. When the user picks, `LN promote N b`.

**Rate or compare:** use the fifteen categories in `references/review-rubric.md`, same ones every time. Score, average, list which categories reach the target, quote the text for each claim, and say up front when this session wrote the draft it is grading. Keep the table in chat.

**Revise to a target:** follow the playbook in `references/review-rubric.md`: structure first, then cut to length (measure each pass), then restore the best single lines under the creator's ceiling, then one targeted change per weak category, then re-paragraph. Run the pre-send checklist, rebuild the PDF, update STATE, commit without model names.

**Continue in a new session:** run `LN context`, then do what `STATE.md` says is next. That's the whole startup cost.

## Light novel style defaults

Override any of these in the `BIBLE.md` style sheet.
- First-person or close third, with a strong voice. Short paragraphs: 1–3 sentences, with a line break for every beat of dialogue; keep a few longer paragraphs in calm stretches so the short ones keep their force.
- Dialogue carries most scenes, and the inner monologue reacts to it.
- Each scene is 1,200–2,500 words and ends on a hook or a reversal. A chapter is 3–5 scenes. Use the creator's chapter range (questionnaire Part 2) as the hard limit; a debut chapter may sit at its top.
- Keep each character's verbal tics and forms of address consistent, as the bible defines them. Name every character the plan says appears; readers can't meet "the Commander".
- Plant small objects early and pay them off inside the chapter (the shirt label that scratches, then tears away in the chase; the bread he ran for, left on his mat).
- Use `*text*` for emphasis and inner thoughts, `**Place. Time.**` on its own line when place or time jumps, and `***` for a scene break inside a file.
