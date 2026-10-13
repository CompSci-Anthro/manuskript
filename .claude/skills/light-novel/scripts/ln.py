#!/usr/bin/env python3
"""Bookkeeping for the light-novel skill, so the model spends no tokens on it.

Usage (from the repo root):
  ln.py init "Title"        scaffold novel/ from templates
  ln.py context             print bible + state + recent summaries + current beats
  ln.py status              word counts and next empty scene
  ln.py new-chapter N S     create chapters/chNN with S empty scene files
  ln.py export              build a Manuskript project in novel-export/
"""
import os
import re
import shutil
import sys

ROOT = os.getcwd()
NOVEL = os.path.join(ROOT, "novel")
SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES = os.path.join(SKILL, "templates")
SAMPLE = os.path.join(ROOT, "sample-projects", "book-of-acts")


def die(msg):
    print(msg)
    sys.exit(1)


def read(path):
    try:
        with open(path, encoding="utf8") as f:
            return f.read()
    except FileNotFoundError:
        return ""


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf8") as f:
        f.write(text)


def strip_comments(text):
    return re.sub(r"<!--.*?-->", "", text, flags=re.S)


def words(text):
    return len(strip_comments(text).split())


def title():
    m = re.match(r"#\s*(.+?)\s+—", read(os.path.join(NOVEL, "BIBLE.md")))
    return m.group(1).strip() if m else "Light Novel"


def chapters():
    """[(num, dir, [scene paths])], sorted."""
    base = os.path.join(NOVEL, "chapters")
    if not os.path.isdir(base):
        return []
    out = []
    for d in sorted(os.listdir(base)):
        m = re.fullmatch(r"ch(\d+)", d)
        if not m:
            continue
        p = os.path.join(base, d)
        scenes = sorted(os.path.join(p, f) for f in os.listdir(p) if re.fullmatch(r"s\d+\.md", f))
        out.append((int(m.group(1)), p, scenes))
    return out


def next_empty():
    for num, _, scenes in chapters():
        for s in scenes:
            if words(read(s)) < 50:
                return num, s
    return None, None


def need_novel():
    if not os.path.isdir(NOVEL):
        die("No novel/ yet. Run: ln.py init \"Title\"")


def cmd_init(args):
    if os.path.exists(NOVEL):
        die("novel/ already exists; not overwriting.")
    t = args[0] if args else "Untitled"
    for name in ("BIBLE.md", "STATE.md", "outline.md"):
        write(os.path.join(NOVEL, name), read(os.path.join(TEMPLATES, name)).replace("{title}", t))
    os.makedirs(os.path.join(NOVEL, "summaries"), exist_ok=True)
    os.makedirs(os.path.join(NOVEL, "chapters"), exist_ok=True)
    print("Created novel/ (BIBLE.md, STATE.md, outline.md). Fill BIBLE.md next.")


def outline_section(num):
    text = read(os.path.join(NOVEL, "outline.md"))
    m = re.search(r"^##\s*Ch0*%d\b.*?(?=^##\s|\Z)" % num, text, flags=re.M | re.S)
    return m.group(0).strip() if m else ""


def cmd_context(args):
    need_novel()
    parts = []
    for name in ("BIBLE.md", "STATE.md"):
        parts.append(strip_comments(read(os.path.join(NOVEL, name))).strip())

    sums_dir = os.path.join(NOVEL, "summaries")
    sums = sorted(f for f in os.listdir(sums_dir) if f.endswith(".md")) if os.path.isdir(sums_dir) else []
    for f in sums[-2:]:
        parts.append("## Summary %s\n%s" % (f[:-3], read(os.path.join(sums_dir, f)).strip()))

    num, scene = next_empty()
    if num is None:
        chs = chapters()
        num = chs[-1][0] + 1 if chs else 1
    beats = outline_section(num)
    parts.append(beats or "## Ch%02d — no beats yet (plan it in outline.md)" % num)
    parts.append("NEXT: " + (os.path.relpath(scene, ROOT) if scene else "plan Ch%02d, then ln.py new-chapter %d <scenes>" % (num, num)))
    print("\n\n".join(p for p in parts if p))


def cmd_status(args):
    need_novel()
    total = 0
    for num, _, scenes in chapters():
        counts = [words(read(s)) for s in scenes]
        total += sum(counts)
        print("Ch%02d  %6d  [%s]" % (num, sum(counts), " ".join(str(c) for c in counts)))
    print("Total %d words" % total)
    _, scene = next_empty()
    print("Next: " + (os.path.relpath(scene, ROOT) if scene else "all scenes drafted"))


def cmd_new_chapter(args):
    need_novel()
    if len(args) != 2:
        die("Usage: ln.py new-chapter N SCENES")
    n, s = int(args[0]), int(args[1])
    d = os.path.join(NOVEL, "chapters", "ch%02d" % n)
    made = []
    for i in range(1, s + 1):
        p = os.path.join(d, "s%02d.md" % i)
        if not os.path.exists(p):
            write(p, "")
            made.append(os.path.relpath(p, ROOT))
    print("Created: " + (", ".join(made) or "nothing (already exist)"))


def cmd_export(args):
    need_novel()
    t = title()
    slug = re.sub(r"[^\w-]+", "_", t).strip("_") or "novel"
    out_dir = os.path.join(ROOT, "novel-export")
    proj = os.path.join(out_dir, slug)
    if os.path.exists(proj):
        shutil.rmtree(proj)
    os.makedirs(proj)

    write(os.path.join(out_dir, slug + ".msk"), "1")
    write(os.path.join(proj, "MANUSKRIPT"), "1")
    for name in ("settings.txt", "labels.txt", "status.txt"):
        src = os.path.join(SAMPLE, name)
        if os.path.exists(src):
            shutil.copy(src, os.path.join(proj, name))
    write(os.path.join(proj, "infos.txt"), "Title:          %s\n" % t)
    write(os.path.join(proj, "summary.txt"), "")
    write(os.path.join(proj, "plots.xml"), "<?xml version='1.0' encoding='UTF-8'?>\n<root/>\n")
    write(os.path.join(proj, "world.opml"), "<?xml version='1.0' encoding='UTF-8'?>\n<opml version=\"1.0\">\n  <body/>\n</opml>\n")
    os.makedirs(os.path.join(proj, "characters"))

    next_id = 1
    for i, (num, _, scenes) in enumerate(chapters()):
        cdir = os.path.join(proj, "outline", "%d-Chapter_%d" % (i, num))
        summary = " ".join(read(os.path.join(NOVEL, "summaries", "ch%02d.md" % num)).split())
        head = "title:          Chapter %d\nID:             %d\ntype:           folder\ncompile:        2\n" % (num, next_id)
        if summary:
            head += "summaryFull:    %s\n" % summary
        write(os.path.join(cdir, "folder.txt"), head + "\n\n")
        next_id += 1
        for j, s in enumerate(scenes):
            body = read(s).strip()
            write(os.path.join(cdir, "%d-Scene_%d.md" % (j, j + 1)),
                  "title:          Scene %d\nID:             %d\ntype:           md\ncompile:        2\n\n\n%s\n"
                  % (j + 1, next_id, body))
            next_id += 1
    print("Exported to %s (open %s.msk in Manuskript)" % (os.path.relpath(proj, ROOT), slug))


COMMANDS = {"init": cmd_init, "context": cmd_context, "status": cmd_status,
            "new-chapter": cmd_new_chapter, "export": cmd_export}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        die(__doc__)
    COMMANDS[sys.argv[1]](sys.argv[2:])
