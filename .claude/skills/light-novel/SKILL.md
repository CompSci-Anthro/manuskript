---
name: light-novel
description: Write, plan, or revise the light novel in novel/ with a low-token workflow (compact story bible, rolling chapter summaries, one-shot scene drafting, helper script for all bookkeeping). Use whenever the user asks to plan, outline, draft, continue, revise, or check progress on the light novel.
---

# Light novel: low-token writing workflow

Credits go mostly to **input tokens re-read every turn** and **output tokens that get thrown away**. This workflow keeps both small: you never re-read old chapters, you draft each scene once, and a script does the bookkeeping.

`LN` below means `python3 .claude/skills/light-novel/scripts/ln.py` (run it from the repo root).

## Hard rules (these save the most)

1. **Never read finished chapters.** Continuity comes from `BIBLE.md`, `STATE.md` and the chapter summaries. Read a past scene only if the user names it, and then use `Grep` for the exact line, not the whole file.
2. **Load context in one call: `LN context`.** It prints the bible, state, the last 2 chapter summaries and the current chapter's beats. Don't follow it with separate `Read` calls for the same files.
3. **Draft each scene in one `Write` call, straight into the scene file.** Don't draft in chat, don't write an outline of the scene first, and don't re-read the file afterward to check it.
4. **Revise with `Edit`, never a full rewrite.** Change only the paragraphs that need it. A full rewrite costs as much as writing the scene again.
5. **Keep chat replies short.** Never paste prose into chat. After a scene, reply in at most 2 lines: file, word count (from `LN status`), and anything the user needs to decide.
6. **Use the script for all bookkeeping:** word counts, new files, finding the next scene, exporting. Don't count words or list directories yourself.
7. **No subagents, no web search, no reading the Manuskript app source or `sample-projects/`.** None of it is needed for writing.
8. **Keep reasoning short.** The beats are already planned, so write from them. Spend thinking on structure only when planning a new chapter.
9. **Keep the memory files within their caps:** `BIBLE.md` ≤ 1,500 words, `STATE.md` ≤ 250 words, each summary ≤ 120 words. When something is added, cut something else. These files are read every session, so each extra word there costs again every time.
10. **Batch work.** If the user says "write chapter 3", write all its scenes in a row (one `Write` each), then update the summary and state once at the end, not after every scene.

## Files

```
novel/
  BIBLE.md          premise, cast (voice + speech tics), world rules, style sheet
  STATE.md          where we are, open threads, the next action
  outline.md        one line per chapter; scene beats only for planned chapters
  summaries/chNN.md ≤120-word summary of each finished chapter
  chapters/chNN/sNN.md  the prose, one file per scene
```

## Commands

| Command | What it does |
|---|---|
| `LN init "Title"` | Create `novel/` from the templates (first time only) |
| `LN context` | Print everything needed to write the next scene |
| `LN status` | Word counts per chapter and scene, total, and the next empty scene |
| `LN new-chapter N S` | Create chapter N with S empty scene files |
| `LN export` | Build a Manuskript project at `novel-export/<title>.msk` + folder, so the user can open it in the app |

## Workflows

**Start a new novel** (only when `novel/` doesn't exist): run `LN init "Title"`, then ask the user in a single message for the premise, the main cast, the tone and the target length. Fill in `BIBLE.md` and the chapter list in `outline.md` with one `Write` each.

**Plan a chapter:** run `LN context`. In `outline.md`, add 3–6 beats per scene under that chapter's heading (one short line each: who, what changes, the closing hook). Then run `LN new-chapter N S`.

**Write (the main loop):**
1. Run `LN context` once at the start of the session.
2. For each scene in the chapter, `Write` `novel/chapters/chNN/sNN.md` from its beats.
3. When the chapter is done, `Write` `summaries/chNN.md` and update `STATE.md`. Add any new permanent facts (names, rules, promises made on the page) to `BIBLE.md`.
4. Run `LN status` and give the user a one-line report.

**Revise:** `Grep` for the passage, `Edit` that passage only, and reply in one line. If the change affects continuity, also update the summary or bible line it touches.

**Continue in a new session:** run `LN context`, then do what `STATE.md` says is next. That's the whole startup cost.

## Light novel style defaults

Override any of these in the `BIBLE.md` style sheet.
- First-person or close third, with a strong voice. Short paragraphs: 1–3 sentences, with a line break for every beat of dialogue.
- Dialogue carries most scenes, and the inner monologue reacts to it (comic asides, tsukkomi).
- Each scene is 1,200–2,500 words and ends on a hook or a reversal. A chapter is 3–5 scenes.
- Keep each character's verbal tics and forms of address consistent, as the bible defines them.
- Use `*text*` for emphasis and inner thoughts, and `***` for a scene break inside a file.
