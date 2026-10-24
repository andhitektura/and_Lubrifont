# Build the light Latin / Cyrillic / Greek edition of and_Lubrifont.
#
# The full fonts carry ~18,000 Chinese and Japanese glyphs (6 MB OTF, 12 MB
# TTF). This edition keeps only the Western scripts, punctuation, numbers and
# technical symbols, with their kerning, accent positioning and number
# features, and installs as a single family "and_Lubrifont" (PostScript name
# andLubrifont-Regular), next to the full SC/TC/JP fonts without clashing.
#
# It is cut from the TC fonts, whose quotation marks are the proportional
# Western forms by default.
#
# usage: py make_latin_cyrillic.py   (writes ../../fonts/and_Lubrifont/)
#
# Requires: fonttools

import os
from fontTools import subset
from fontTools.ttLib import TTFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "..", "..", "fonts")
CJK = os.path.join(FONTS, "and_Lubrifont-CJK")
OUT = os.path.join(FONTS, "and_Lubrifont")

UNICODES = [
    (0x0020, 0x02FF),   # Latin, IPA, spacing modifiers
    (0x0300, 0x036F),   # combining accents
    (0x0370, 0x03FF),   # Greek
    (0x0400, 0x052F),   # Cyrillic
    (0x1E00, 0x1EFF),   # Latin Extended Additional
    (0x2000, 0x206F),   # punctuation
    (0x2070, 0x209F),   # superscripts / subscripts
    (0x20A0, 0x20CF),   # currency
    (0x2100, 0x214F),   # letterlike (№ ℃ ...)
    (0x2150, 0x218F),   # number forms (⅓ ...)
    (0x2190, 0x21FF),   # arrows
    (0x2200, 0x22FF),   # math operators
    (0x2300, 0x23FF),   # technical (⌀)
    (0x25A0, 0x25FF),   # geometric shapes (▲ ▼)
    (0x2700, 0x27BF),   # dingbats (✓ ✗)
]
# CJK-only features are left out
FEATURES = ["aalt", "ccmp", "dlig", "liga", "salt", "ss01", "ss18", "sups", "subs",
            "sinf", "numr", "dnom", "frac", "tnum", "kern", "mark", "mkmk"]

FAMILY = "and_Lubrifont"
PS_NAME = "andLubrifont-Regular"


def rename(font):
    name = font["name"]
    version = f"Version {font['head'].fontRevision:.3f}"
    keep = []
    for r in name.names:
        if r.platformID == 3 and r.langID != 0x409 and r.nameID in (1, 2, 4, 16, 17):
            continue                       # localized SC/TC names do not apply
        text = r.toUnicode()
        if r.nameID in (1, 4):
            r.string = FAMILY
        elif r.nameID == 3:
            r.string = f"{version[8:]};NFSL;{PS_NAME}"
        elif r.nameID == 6:
            r.string = PS_NAME
        elif r.nameID == 5:
            r.string = version
        keep.append(r)
    name.names = keep
    if "CFF " in font:
        cff = font["CFF "].cff
        cff.fontNames = [PS_NAME]
        top = cff.topDictIndex[0]
        top.FullName = FAMILY
        top.FamilyName = FAMILY
        for fd in getattr(top, "FDArray", []):
            fd.FontName = PS_NAME
    # CJK code pages no longer apply
    os2 = font["OS/2"]
    for bit in (17, 18, 19, 20, 21):   # 932 Japanese, 936, 949, 950, 1361
        os2.ulCodePageRange1 &= ~(1 << bit)


def build(src, dst):
    options = subset.Options()
    options.layout_features = FEATURES
    options.name_IDs = ["*"]
    options.name_languages = ["*"]
    options.notdef_outline = True
    options.glyph_names = False
    options.drop_tables += ["vhea", "vmtx", "VORG", "BASE", "meta"]
    options.prune_unicode_ranges = True
    font = TTFont(src)
    unicodes = [u for lo, hi in UNICODES for u in range(lo, hi + 1)]
    sub = subset.Subsetter(options)
    sub.populate(unicodes=unicodes)
    sub.subset(font)
    rename(font)
    font.save(dst)
    print(f"{dst}: {len(font.getGlyphOrder())} glyphs, {os.path.getsize(dst) // 1024} KB")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    build(os.path.join(CJK, "otf", "andLubrifontTC-Regular.otf"),
          os.path.join(OUT, "otf", f"{PS_NAME}.otf"))
    build(os.path.join(CJK, "andLubrifontTC-Regular.ttf"),
          os.path.join(OUT, f"{PS_NAME}.ttf"))
