# Give the zeros of WD-XL Lubrifont a centre dot so that 0 cannot be
# mistaken for O / О (in this design they were otherwise near-identical).
#
# Applies to 0, ⁰, ₀ and fullwidth ０. The dot is a rounded bar centred in the
# counter, sized in proportion to the counter. Glyphs that already have a dot
# (three contours) are left alone, so the script can be re-run safely.
#
# usage: py dotted_zero.py font1.ttf [font2.otf ...]
#
# Requires: fonttools, skia-pathops

import sys
import pathops
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from add_macedonian_cyrillic import split_contours, bounds_of
from add_extra_glyphs import rect

ZEROS = (0x0030, 0x2070, 0x2080, 0xFF10)

# dot of the full-size 0, relative to its counter (226 x 540 units)
DOT_WIDTH = 90 / 226
DOT_HEIGHT = 170 / 540
DOT_RADIUS = 40 / 90


def dotted(contours, clockwise):
    # counter = the contour with the smallest bounding box
    counter = min((bounds_of([c]) for c in contours), key=lambda b: (b[2] - b[0]) * (b[3] - b[1]))
    cx0, cy0, cx1, cy1 = counter
    w = round((cx1 - cx0) * DOT_WIDTH)
    h = round((cy1 - cy0) * DOT_HEIGHT)
    x0 = round((cx0 + cx1 - w) / 2)
    y0 = round((cy0 + cy1 - h) / 2)
    path = pathops.Path()
    pen = path.getPen()
    for c in contours:
        for op, args in c:
            getattr(pen, op)(*args)
    dot = rect(x0, y0, x0 + w, y0 + h, r=round(w * DOT_RADIUS))
    result = pathops.op(pathops.simplify(path, clockwise=clockwise), dot,
                        pathops.PathOp.UNION, clockwise=clockwise)
    rec = RecordingPen()
    result.draw(rec)
    return rec


def patch_font(path_in):
    font = TTFont(path_in)
    cmap = font.getBestCmap()
    glyphset = font.getGlyphSet()
    is_cff = "CFF " in font
    changed = []
    for uni in ZEROS:
        name = cmap.get(uni)
        if name is None:
            continue
        rec = RecordingPen()
        glyphset[name].draw(rec)
        contours = split_contours(rec.value)
        if len(contours) != 2:
            continue  # already dotted (or an unexpected shape): leave it
        new = dotted(contours, clockwise=not is_cff)
        if is_cff:
            cff = font["CFF "].cff
            td = cff.topDictIndex[0]
            cs = td.CharStrings
            private = cs[name].private
            adv = font["hmtx"][name][0]
            width = None if adv == private.defaultWidthX else adv - private.nominalWidthX
            pen = T2CharStringPen(width, None)
            new.replay(pen)
            charstring = pen.getCharString(private=private, globalSubrs=cff.GlobalSubrs)
            cs.charStringsIndex[cs.charStrings[name]] = charstring
        else:
            pen = TTGlyphPen(None)
            new.replay(Cu2QuPen(pen, max_err=1.0, reverse_direction=False))
            font["glyf"][name] = pen.glyph()
        changed.append(chr(uni))
    if changed:
        font.save(path_in)
    print(f"{path_in}: dotted {' '.join(changed) or 'nothing'}")


if __name__ == "__main__":
    for p in sys.argv[1:]:
        patch_font(p)
