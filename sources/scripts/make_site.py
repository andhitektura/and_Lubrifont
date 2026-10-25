# Builds the and_Lubrifont website (GitHub Pages) from site/ and the web
# fonts: copies site/ and fonts/and_Lubrifont/woff2/ to OUTDIR, puts the
# version into the page and writes chars.js, the character list shown on the
# page, read from the Regular font so it always matches the fonts.
#
# usage: py make_site.py OUTDIR   (used by .github/workflows/pages.yml; open
#                                  OUTDIR/index.html to preview locally)
#
# Requires: fonttools

import glob
import json
import os
import shutil
import sys
import unicodedata
from fontTools.ttLib import TTFont

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")

# character groups in page order: (title, test on code point)
GROUPS = [
    ("Latin", lambda u, c: c.startswith("L") and u < 0x0370 or 0x1E00 <= u <= 0x1EFF),
    ("Cyrillic", lambda u, c: 0x0400 <= u <= 0x052F and c.startswith("L")),
    ("Greek", lambda u, c: 0x0370 <= u <= 0x03FF and c.startswith("L")),
    ("Figures, fractions, superscripts and subscripts", lambda u, c: c in ("Nd", "No", "Nl")),
    ("Punctuation", lambda u, c: c.startswith("P")),
    ("Mathematics", lambda u, c: c == "Sm" and not 0x2190 <= u <= 0x21FF),
    ("Arrows", lambda u, c: 0x2190 <= u <= 0x21FF or u == 0x2794),
    ("Technical, drawing and GD&T symbols", lambda u, c: 0x2300 <= u <= 0x23FF or 0x25A0 <= u <= 0x27BF),
    ("Units, currency and other signs", lambda u, c: c in ("So", "Sc", "Sm") or 0x2100 <= u <= 0x214F),
]


def characters(font_path):
    cmap = TTFont(font_path).getBestCmap()
    groups = [[title, []] for title, _ in GROUPS]
    for u in sorted(cmap):
        cat = unicodedata.category(chr(u))
        if cat[0] in "ZMC":          # spaces, combining marks, controls
            continue
        for (title, test), group in zip(GROUPS, groups):
            if test(u, cat):
                group[1].append([u, unicodedata.name(chr(u), "").lower()])
                break
    return [g for g in groups if g[1]]


def main():
    out = sys.argv[1]
    shutil.copytree(os.path.join(ROOT, "site"), out, dirs_exist_ok=True)
    os.makedirs(os.path.join(out, "fonts"), exist_ok=True)
    for p in glob.glob(os.path.join(ROOT, "fonts", "and_Lubrifont", "woff2", "*.woff2")):
        shutil.copy(p, os.path.join(out, "fonts"))
    regular = os.path.join(ROOT, "fonts", "and_Lubrifont", "andLubrifont-Regular.ttf")
    version = f"{TTFont(regular)['head'].fontRevision:.3f}"
    index = os.path.join(out, "index.html")
    text = open(index, encoding="utf-8").read().replace("{{version}}", version)
    open(index, "w", encoding="utf-8").write(text)
    groups = characters(regular)
    with open(os.path.join(out, "chars.js"), "w", encoding="utf-8") as f:
        f.write("window.CHARS = " + json.dumps(groups, ensure_ascii=False, separators=(",", ":")) + ";\n")
    print(f"{out}: version {version}, {sum(len(g[1]) for g in groups)} characters in {len(groups)} groups")


if __name__ == "__main__":
    main()
