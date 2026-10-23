# Open up the overall letter spacing (tracking) of the Western text in
# WD-XL Lubrifont by adding the same amount of space to both sides of every
# Latin, Greek and Cyrillic letter, digit and Western punctuation mark (and
# twice that to the word space), so the kerning stays valid.
#
# Included: characters in the Latin, IPA/modifier, Greek, Cyrillic, Latin
# Extended Additional, General Punctuation and super/subscript ranges, the
# form punctuation takes in Latin text (the SC fonts switch quotes to
# proportional forms), and their single-substitution alternates (X.ss01,
# ss18 punctuation, superiors). Excluded: anything full-width (the CJK em
# width) or zero-width (combining marks), so CJK text is not affected.
#
# usage: py track.py <units per side> font1.otf [font2.ttf ...]
#        (safe to re-run: a font that has been tracked is skipped)
#
# Requires: fonttools, uharfbuzz

import sys
from fontTools.ttLib import TTFont
from respace import shift_glyph, shift_anchors

RANGES = [(0x0020, 0x007E), (0x00A0, 0x02FF), (0x0370, 0x03FF), (0x0400, 0x04FF),
          (0x1E00, 0x1EFF), (0x2010, 0x205E), (0x2070, 0x209F)]
EXCLUDED_WIDTHS = {0, 765, 1000}   # zero-width marks, CJK em width
DONE_CHECK = (0x0048, 496)          # H had an advance of 496 before tracking


def western_glyphs(path, font):
    import uharfbuzz as hb
    cmap = font.getBestCmap()
    order = font.getGlyphOrder()
    hmtx = font["hmtx"]
    names = set()
    unis = [u for lo, hi in RANGES for u in range(lo, hi + 1) if u in cmap]
    for u in unis:
        names.add(cmap[u])
    # the form punctuation takes in Latin text (SC: proportional quotes)
    hbfont = hb.Font(hb.Face(hb.Blob.from_file_path(path)))
    for u in unis:
        if 0x2010 <= u <= 0x205E or u < 0x80:
            buf = hb.Buffer()
            buf.add_str("a" + chr(u))
            buf.guess_segment_properties()
            hb.shape(hbfont, buf, {})
            names.add(order[buf.glyph_infos[1].codepoint])
    # single-substitution alternates of these glyphs
    gsub = font["GSUB"].table
    for lookup in gsub.LookupList.Lookup:
        for st in lookup.SubTable:
            st = getattr(st, "ExtSubTable", st)
            for a, b in getattr(st, "mapping", {}).items():
                if a in names:
                    names.add(b)
    return {n for n in names if hmtx[n][0] not in EXCLUDED_WIDTHS}


def patch_font(path, amount):
    font = TTFont(path)
    cmap = font.getBestCmap()
    if font["hmtx"][cmap[DONE_CHECK[0]]][0] != DONE_CHECK[1]:
        print(f"{path}: already tracked")
        return
    names = western_glyphs(path, font)
    for name in names:
        shift_glyph(font, name, amount, amount)
    shift_anchors(font, {name: amount for name in names})
    font.save(path)
    print(f"{path}: +{amount} per side on {len(names)} glyphs")


if __name__ == "__main__":
    amount = int(sys.argv[1])
    for p in sys.argv[2:]:
        patch_font(p, amount)
