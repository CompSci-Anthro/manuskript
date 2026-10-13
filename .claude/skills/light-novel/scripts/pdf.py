#!/usr/bin/env python3
"""Build a light-novel reading-copy PDF of one chapter (5.5 x 8.25 in paperback).

Usage (from the repo root):
  python3 .claude/skills/light-novel/scripts/pdf.py N [--volume "Volume 1: ..."] [--author "Name"] [--watermark "Advance copy"]

Reads novel/chapters/chNN/sNN.md, the chapter titles in novel/outline.md and the book
title in novel/BIBLE.md. Writes novel/pdf/ChNN - <Chapter title>.pdf. Needs Node with
Playwright and its Chromium (used to typeset the HTML and print it with bookmarks and tags).
"""
import argparse
import datetime
import html
import json
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.getcwd()
NOVEL = os.path.join(ROOT, "novel")


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def chapter_titles():
    titles = {}
    for m in re.finditer(r"^##\s*Ch(\d+)\s*—\s*(.+?)(?:\s+—\s+.*)?$", read(os.path.join(NOVEL, "outline.md")), re.M):
        titles[int(m.group(1))] = m.group(2).strip()
    return titles


def book_title():
    m = re.match(r"#\s*(.+?)\s+—", read(os.path.join(NOVEL, "BIBLE.md")))
    return m.group(1) if m else "Untitled"


def smart(text):
    """Curly quotes for straight ones; the prose is drafted with plain quotes."""
    text = re.sub(r'(^|[\s(\[*])"(?=\S)', "\\1\u201c", text)
    text = text.replace('"', "\u201d")
    return text.replace("'", "\u2019")


def inline(text):
    text = smart(html.escape(text, quote=False))
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    return text.replace("\n", " ")


def scene_html(md):
    out, first = [], True
    md = re.sub(r"<!--.*?-->", "", md, flags=re.S)
    for block in re.split(r"\n\s*\n", md.strip()):
        block = block.strip()
        if not block:
            continue
        if block == "***":
            out.append('<div class="break" aria-hidden="true">&#9670;</div>')
            first = True
            continue
        m = re.fullmatch(r"\*\*([^*]+)\*\*", block)
        if m and first:  # place/time header at the start of a scene or section
            out.append('<p class="place">%s</p>' % inline(m.group(1)))
            continue
        out.append('<p%s>%s</p>' % (' class="first"' if first else "", inline(block)))
        first = False
    return "\n".join(out)


CSS = """
@page { size: 5.5in 8.25in; margin: 0.72in 0.58in 0.78in 0.78in; }
@page :left { margin-left: 0.58in; margin-right: 0.78in;
  @bottom-left { content: counter(page); font: 8.5pt "Caladea"; color: #444; vertical-align: top; padding-top: 12pt; } }
@page :right {
  @bottom-right { content: counter(page); font: 8.5pt "Caladea"; color: #444; vertical-align: top; padding-top: 12pt; } }
@page plain { @bottom-left { content: none; } @bottom-right { content: none; } }
html { font-family: "Caladea", "Liberation Serif", serif; font-size: 10.6pt; line-height: 1.5; color: #111; }
body { margin: 0; }
.front { page: plain; break-after: page; height: 6.7in; display: flex; flex-direction: column; align-items: center; text-align: center; }
.front .series { margin-top: 1.55in; font-size: 25pt; letter-spacing: .14em; text-transform: uppercase; line-height: 1.15; font-weight: 700; }
.front .rule { width: 1.1in; border-top: 1px solid #111; margin: 16pt 0 13pt; }
.front .vol { font-size: 11pt; font-style: italic; }
.front .author { margin-top: auto; font-size: 10.5pt; letter-spacing: .2em; text-transform: uppercase; }
.front .note { margin-top: 10pt; font: 7.5pt "Inter"; letter-spacing: .12em; text-transform: uppercase; color: #777; }
.verso { page: plain; break-after: page; height: 6.7in; display: flex; flex-direction: column; justify-content: flex-end; font-size: 8pt; line-height: 1.45; color: #555; }
.verso p { margin: 0 0 6pt; }
.chapter { break-before: right; }
.chapter header { padding-top: 1.05in; margin-bottom: .42in; text-align: center; }
.chapter .num { font: 600 8pt "Inter"; letter-spacing: .32em; text-transform: uppercase; color: #5c0701; }
.chapter h2 { font-size: 19pt; line-height: 1.2; font-weight: 700; margin: 10pt auto 0; max-width: 3.4in; }
.chapter .orn { margin-top: 12pt; font-family: "DejaVu Serif"; font-size: 7pt; letter-spacing: .6em; color: #5c0701; }
p { margin: 0; text-indent: 1.3em; text-align: justify; hyphens: auto; orphans: 2; widows: 2; }
p.first, p.place + p { text-indent: 0; }
p.place { text-indent: 0; text-align: center; font: 600 7.6pt "Inter"; letter-spacing: .2em; text-transform: uppercase; color: #5c0701; margin: 2pt 0 10pt; }
.break { text-align: center; font-family: "DejaVu Serif"; font-size: 7pt; color: #5c0701; margin: 11pt 0; break-after: avoid; }
strong { font-weight: 700; letter-spacing: .04em; }
.end { break-inside: avoid; text-align: center; margin-top: 26pt; }
.end .orn { font-family: "DejaVu Serif"; font-size: 7pt; letter-spacing: .6em; color: #5c0701; }
.end .label { margin-top: 8pt; font: 600 7.6pt "Inter"; letter-spacing: .24em; text-transform: uppercase; }
.end .next { margin-top: 6pt; font-size: 9.5pt; font-style: italic; color: #444; }
.wm { position: fixed; top: 46%; left: 0; right: 0; text-align: center; transform: rotate(-30deg); font: 700 34pt "Inter"; letter-spacing: .1em; text-transform: uppercase; color: rgba(92, 7, 1, .08); }
"""

PRINT_JS = """
const { chromium } = require('playwright');
(async () => {
  const [src, out] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('file://' + src, { waitUntil: 'load' });
  await page.pdf({ path: out, preferCSSPageSize: true, printBackground: true, outline: false, tagged: true });
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("chapter", type=int)
    ap.add_argument("--volume", default="")
    ap.add_argument("--author", default="")
    ap.add_argument("--watermark", default="")
    a = ap.parse_args()

    cdir = os.path.join(NOVEL, "chapters", "ch%02d" % a.chapter)
    scenes = sorted(f for f in os.listdir(cdir) if re.fullmatch(r"s\d+\.md", f)) if os.path.isdir(cdir) else []
    if not scenes:
        sys.exit("No scenes in %s" % cdir)
    titles, book = chapter_titles(), book_title()
    title = titles.get(a.chapter, "Chapter %d" % a.chapter)
    nxt = titles.get(a.chapter + 1)

    body = "\n".join(scene_html(read(os.path.join(cdir, f))) for f in scenes)
    today = datetime.date.today().strftime("%B %Y")
    vol = '<div class="vol">%s</div>' % html.escape(a.volume) if a.volume else ""
    author = html.escape(a.author)
    doc = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>%(book)s — Chapter %(n)d: %(title)s</title><style>%(css)s</style></head><body>
%(wm)s
<section class="front"><h1 class="series">%(book)s</h1><div class="rule"></div>%(vol)s
<div class="author">%(author)s</div><div class="note">Reading copy · Chapter %(n)d draft · %(today)s</div></section>
<section class="verso"><p>%(book)s%(volsep)s</p><p>Chapter %(n)d draft reading copy, %(today)s. Illustrations not yet included.</p>
<p>Text &copy; %(year)d %(author)s. All rights reserved.</p></section>
<section class="chapter"><header><div class="num">Chapter %(n)d</div><h2>%(title)s</h2>
<div class="orn" aria-hidden="true">&#9670; &#9670; &#9670;</div></header>
%(body)s
<div class="end"><div class="orn" aria-hidden="true">&#9670; &#9670; &#9670;</div><div class="label">End of Chapter %(n)d</div>%(next)s</div>
</section></body></html>""" % {
        "book": html.escape(book), "n": a.chapter, "title": html.escape(title), "vol": vol,
        "volsep": (" · " + html.escape(a.volume)) if a.volume else "", "author": author,
        "today": today, "year": datetime.date.today().year, "body": body,
        "css": CSS,
        "wm": '<div class="wm" aria-hidden="true">%s</div>' % html.escape(a.watermark) if a.watermark else "",
        "next": '<div class="next">Next: Chapter %d · %s</div>' % (a.chapter + 1, html.escape(nxt)) if nxt else "",
    }

    outdir = os.path.join(NOVEL, "pdf")
    os.makedirs(outdir, exist_ok=True)
    safe = re.sub(r'[\\/:*?"<>|]', "", title)
    out = os.path.join(outdir, "Ch%02d - %s.pdf" % (a.chapter, safe))
    with tempfile.TemporaryDirectory() as tmp:
        src = os.path.join(tmp, "chapter.html")
        with open(src, "w", encoding="utf-8") as f:
            f.write(doc)
        js = os.path.join(tmp, "print.js")
        with open(js, "w", encoding="utf-8") as f:
            f.write(PRINT_JS)
        subprocess.run(["node", js, src, out], check=True)

    finish(out, book, title, a)
    print(json.dumps({"pdf": os.path.relpath(out, ROOT)}))


def running_head(text, right, font):
    """One-page PDF holding a running head: book title on left pages, chapter title on right."""
    import io
    from reportlab.pdfgen import canvas
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(5.5 * 72, 8.25 * 72))
    text, size, space = text.upper(), 7.2, 1.15
    width = c.stringWidth(text, font, size) + space * (len(text) - 1)
    x = 5.5 * 72 - 0.58 * 72 - width if right else 0.58 * 72
    t = c.beginText(x, 8.25 * 72 - 0.72 * 72 + 15)
    t.setFont(font, size)
    t.setCharSpace(space)
    t.setFillColorRGB(0.42, 0.42, 0.42)
    t.textOut(text)
    c.drawText(t)
    c.save()
    buf.seek(0)
    return buf


def finish(out, book, title, a):
    """Running heads after the chapter opener, bookmarks and document metadata."""
    try:
        from pypdf import PdfReader, PdfWriter
    except ImportError:
        return
    w = PdfWriter(clone_from=PdfReader(out))
    opener = 2  # title page, verso, then the chapter opener on a right-hand page
    try:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        path = subprocess.run(["fc-match", "-f", "%{file}", "Caladea"], capture_output=True, text=True).stdout
        pdfmetrics.registerFont(TTFont("Head", path))
        heads = {False: PdfReader(running_head(book, False, "Head")).pages[0],
                 True: PdfReader(running_head(title, True, "Head")).pages[0]}
        for i, page in enumerate(w.pages):
            if i > opener:
                page.merge_page(heads[i % 2 == 0])  # index 4 = page 5, a right-hand page
    except Exception as e:  # running heads are optional; keep the PDF usable without them
        print("running heads skipped: %s" % e, file=sys.stderr)
    w.add_outline_item(book, 0)
    w.add_outline_item("Chapter %d: %s" % (a.chapter, title), opener)
    w.page_mode = "/UseOutlines"
    w.add_metadata({"/Title": "%s — Chapter %d: %s" % (book, a.chapter, title), "/Author": a.author,
                    "/Subject": a.volume or book})
    with open(out, "wb") as f:
        w.write(f)


if __name__ == "__main__":
    main()
