# Lengthen the arm of the small r (r ŕ ř) by EXTEND units: the arm of the
# original ended only 75 units right of the stem and looked stunted. The
# advance width grows by the same amount, so the space after r stays as it
# was and the kerning stays valid; the accents of ŕ ř and the r's top accent
# anchor move right by half of it, to stay centred over the wider letter.
# Fullwidth ｒ is left alone. Fonts whose r is already lengthened are skipped,
# so the script can be re-run safely.
#
# usage: py r_arm.py font1.otf [font2.ttf ...]
#        (then make_weights.py, make_italics.py and autohint.py)
#
# Requires: fonttools

import sys
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen
from diagonal_seven import replace_glyph

EXTEND = 50
ARM_Y = 390          # arm points: at or above the underside of the arm (394)
ARM_X = 121          # ... and this far right of the stem's left edge
LETTERS = (0x72, 0x155, 0x159)   # r ŕ ř


def contours(rec):
    out, cur = [], []
    for op in rec.value:
        cur.append(op)
        if op[0] in ("closePath", "endPath"):
            out.append(cur)
            cur = []
    return out


def points(contour):
    return [pt for _, pts in contour for pt in pts]


def lengthen(font, name):
    rec = RecordingPen()
    font.getGlyphSet()[name].draw(rec)
    new = RecordingPen()
    for contour in contours(rec):
        pts = points(contour)
        ys = [y for _, y in pts]
        if min(ys) < 0 and max(ys) >= 480:          # the r itself
            stem = min(x for x, _ in pts)
            if max(x for x, _ in pts) - stem > 190:
                return False                       # already lengthened
            shift = lambda x, y: (x + EXTEND, y) if x >= stem + ARM_X and y >= ARM_Y else (x, y)
        else:                                      # accent
            shift = lambda x, y: (x + EXTEND / 2, y)
        for op, pts in contour:
            new.value.append((op, tuple(shift(x, y) for x, y in pts)))
    replace_glyph(font, name, new, font["hmtx"][name][0] + EXTEND)
    return True


def shift_top_anchor(font, name):
    for lookup in font["GPOS"].table.LookupList.Lookup:
        for st in lookup.SubTable:
            if lookup.LookupType == 9:
                st = st.ExtSubTable
            if type(st).__name__ == "MarkBasePos" and name in st.BaseCoverage.glyphs:
                rec = st.BaseArray.BaseRecord[st.BaseCoverage.glyphs.index(name)]
                for anchor in rec.BaseAnchor:
                    if anchor is not None and anchor.YCoordinate > 300:
                        anchor.XCoordinate += EXTEND // 2


def patch_font(path):
    font = TTFont(path)
    cmap = font.getBestCmap()
    done = []
    for uni in LETTERS:
        name = cmap.get(uni)
        if name and lengthen(font, name):
            shift_top_anchor(font, name)
            done.append(chr(uni))
    if done:
        font.save(path)
    print(f"{path}: {' '.join(done) if done else 'r already lengthened'}")


if __name__ == "__main__":
    for p in sys.argv[1:]:
        patch_font(p)
