# TrueType hinting for the and_Lubrifont .ttf fonts, with ttfautohint.
#
# Hinting snaps stems, x-height, cap height and baseline to whole pixels at
# small sizes, so text stays sharp and even on screen below about 20 px. Latin, Cyrillic and
# Greek are hinted; CJK glyphs are left unhinted (ttfautohint has no CJK
# support). -W (Windows compatibility) keeps glyphs inside usWinAscent and
# usWinDescent, so GDI clips nothing.
#
# Any existing hinting is removed first, so the script is safe to re-run.
# The .otf fonts (CFF) are not touched.
#
# usage: py autohint.py font1.ttf [font2.ttf ...]   (run last, after make_weights.py)
#
# Requires: fonttools, ttfautohint-py

import io
import sys
from fontTools.ttLib import TTFont

HINT_TABLES = ("fpgm", "prep", "cvt ", "gasp", "hdmx", "LTSH", "VDMX", "TSI0", "TSI1", "TSI2", "TSI3", "TSI5")


def dehint(font):
    for tag in HINT_TABLES:
        if tag in font:
            del font[tag]
    glyf = font["glyf"]
    for name in font.getGlyphOrder():
        glyph = glyf[name]
        if hasattr(glyph, "program"):
            glyph.program.fromBytecode(b"")
    maxp = font["maxp"]
    for attr in ("maxZones", "maxTwilightPoints", "maxStorage", "maxFunctionDefs",
                 "maxInstructionDefs", "maxStackElements", "maxSizeOfInstructions"):
        setattr(maxp, attr, 1 if attr == "maxZones" else 0)


def autohint(path):
    font = TTFont(path)
    dehint(font)
    name = font["name"]
    version = name.getName(5, 3, 1, 0x409).toUnicode().split(";")[0]
    name.setName(version, 5, 3, 1, 0x409)        # drop an earlier ttfautohint note
    from ttfautohint import ttfautohint
    buf = io.BytesIO()
    font.save(buf)
    hinted = ttfautohint(in_buffer=buf.getvalue(), default_script="latn",
                         windows_compatibility=True, hint_composites=True)
    font = TTFont(io.BytesIO(hinted))
    font["head"].flags |= 1 << 3    # integer ppem: required for hinted fonts
    font.save(path)
    print(f"{path}: hinted")


if __name__ == "__main__":
    for p in sys.argv[1:]:
        autohint(p)
