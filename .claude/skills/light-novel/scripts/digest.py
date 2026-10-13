#!/usr/bin/env python3
"""Turn the questionnaire artifact's answer documents into one compact, greppable digest.

Build:  digest.py build ANSWERS_DIR OUT.txt
Slice:  digest.py slice OUT.txt SECTIONS [--cols N]      e.g. s001-s024,s133  (default 400 cols)

ANSWERS_DIR holds the JSON files that ArtifactData writes with action "list",
collection "answers" and an out_dir. Each sNNN.json is one questionnaire section:
  {"answers": {"qNNNN": {"n": 1835, "q": "question", "a": answer, "x": "other text",
                          "d": delegated?, "t": type}}}
Each digest line is:  n|sNNN| question => answer [+other]
Answers that are lists join with "; "; dicts (mixes, splits) print as JSON.
"""
import glob
import json
import os
import re
import sys


def build(src, out):
    lines, total, delegated = [], 0, 0
    for path in sorted(glob.glob(os.path.join(src, "s*.json"))):
        with open(path, encoding="utf8") as f:
            doc = json.load(f)
        sec = os.path.basename(path)[:-5]
        for _, v in sorted(doc.get("answers", {}).items()):
            total += 1
            if v.get("d"):
                delegated += 1
                continue
            a = v.get("a")
            if a in (None, "", [], {}):
                continue
            if isinstance(a, list):
                a = "; ".join(str(x) for x in a)
            elif isinstance(a, dict):
                a = json.dumps(a, ensure_ascii=False)
            extra = v.get("x") or ""
            lines.append("%s|%s| %s => %s%s" % (v.get("n"), sec, v.get("q"), a, (" [+%s]" % extra) if extra else ""))
    with open(out, "w", encoding="utf8") as f:
        f.write("\n".join(lines))
    print("%d questions; %d delegated to Claude; %d answered -> %s" % (total, delegated, len(lines), out))


def wanted(spec):
    ids = set()
    for part in spec.split(","):
        part = part.strip()
        m = re.fullmatch(r"s(\d+)-s(\d+)", part)
        if m:
            ids.update("s%03d" % i for i in range(int(m.group(1)), int(m.group(2)) + 1))
        elif part:
            ids.add(part)
    return ids


def slice_(digest, spec, cols):
    ids = wanted(spec)
    with open(digest, encoding="utf8") as f:
        for line in f:
            parts = line.rstrip("\n").split("|", 2)
            if len(parts) == 3 and parts[1] in ids:
                print((parts[1] + "|" + parts[2])[:cols])


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) >= 3 and args[0] == "build":
        build(args[1], args[2])
    elif len(args) >= 3 and args[0] == "slice":
        cols = int(args[args.index("--cols") + 1]) if "--cols" in args else 400
        slice_(args[1], args[2], cols)
    else:
        print(__doc__)
        sys.exit(1)
