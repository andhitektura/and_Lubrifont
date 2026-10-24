# WOFF2 web fonts of and_Lubrifont: compresses the (hinted) .ttf of each
# style (three weights and their italics) into fonts/and_Lubrifont/woff2/. The CJK fonts are left out: at
# 10+ MB each they are too large to serve whole on a website.
#
# usage: py make_woff2.py   (run after autohint.py)
#
# Requires: fonttools, brotli

import os
from fontTools.ttLib import TTFont

HERE = os.path.dirname(os.path.abspath(__file__))
DIR = os.path.join(HERE, "..", "..", "fonts", "and_Lubrifont")

if __name__ == "__main__":
    os.makedirs(os.path.join(DIR, "woff2"), exist_ok=True)
    for style in ("Light", "LightItalic", "Regular", "Italic", "Bold", "BoldItalic"):
        font = TTFont(os.path.join(DIR, f"andLubrifont-{style}.ttf"))
        font.flavor = "woff2"
        dst = os.path.join(DIR, "woff2", f"andLubrifont-{style}.woff2")
        font.save(dst)
        print(f"{dst}: {os.path.getsize(dst) // 1024} KB")
