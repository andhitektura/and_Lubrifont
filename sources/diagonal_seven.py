# Replace the narrow right-angled 7 of and_Lubrifont (it read like a
# mirrored Г / a 1) with a full-width 7 with a diagonal stem.
#
# The diagonal (about 73°) sits between the slants of N/И and A/V. The new 7
# is used for 7 and fullwidth ７; ⁷ ₇ and ⅞ are then rebuilt from it with the
# same recipes as add_extra_glyphs.py. Fonts whose 7 is already full width are
# left alone, so the script can be re-run safely.
#
# usage: py diagonal_seven.py font1.ttf [font2.otf ...]
#
# Requires: fonttools, skia-pathops

import sys
import math
import pathops
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from add_macedonian_cyrillic import finalize
from add_extra_glyphs import ExtraBuilder, NEW_GLYPHS

ADVANCE = 508            # same as 2, 3, 5 ...
LEFT, RIGHT = 50, 458    # side bearings of the other digits
TOP, BAR = 713, 622      # top bar of the old 7 (bar thickness 91)
SHOULDER = 600           # where the diagonal leaves the right edge
FOOT_RIGHT, FOOT_WIDTH = 270, 100


def rounded_polygon(pts, radii):
    """Closed polygon drawn in the font's corner style: on-curve points r units
    back along each edge, with the corner itself as the quadratic control."""
    path = pathops.Path()
    pen = path.getPen()

    def toward(a, b, r):
        dx, dy = b[0] - a[0], b[1] - a[1]
        length = math.hypot(dx, dy)
        k = min(r, length / 2) / length
        return (a[0] + dx * k, a[1] + dy * k)

    segments = []
    for i, cur in enumerate(pts):
        prev, nxt, r = pts[i - 1], pts[(i + 1) % len(pts)], radii[i]
        if r:
            segments.append((toward(cur, prev, r), cur, toward(cur, nxt, r)))
        else:
            segments.append((cur,))
    pen.moveTo(segments[0][0])
    for seg in segments[1:] + segments[:1]:
        pen.lineTo(seg[0])
        if len(seg) == 3:
            pen.qCurveTo(seg[1], seg[2])
    pen.closePath()
    return path


def seven_path():
    foot_left = FOOT_RIGHT - FOOT_WIDTH
    slope = (RIGHT - FOOT_RIGHT) / (SHOULDER + 8)
    inner_x = foot_left + slope * (BAR + 8)  # diagonal's left edge meets the bar
    return rounded_polygon(
        [(LEFT, BAR), (LEFT, TOP), (RIGHT, TOP), (RIGHT, SHOULDER),
         (FOOT_RIGHT, -8), (foot_left, -8), (inner_x, BAR)],
        [40, 40, 40, 30, 40, 40, 0])


def replace_glyph(font, name, rec, advance):
    bp = BoundsPen(None)
    rec.replay(bp)
    xmin, _, _, ymax = (round(v) for v in bp.bounds)
    if "CFF " in font:
        cff = font["CFF "].cff
        cs = font["CFF "].cff.topDictIndex[0].CharStrings
        private = cs[name].private
        width = None if advance == private.defaultWidthX else advance - private.nominalWidthX
        pen = T2CharStringPen(width, None)
        rec.replay(pen)
        cs.charStringsIndex[cs.charStrings[name]] = pen.getCharString(
            private=private, globalSubrs=cff.GlobalSubrs)
    else:
        pen = TTGlyphPen(None)
        rec.replay(Cu2QuPen(pen, max_err=1.0, reverse_direction=False))
        font["glyf"][name] = pen.glyph()
    font["hmtx"][name] = (advance, xmin)


def patch_font(path_in):
    font = TTFont(path_in)
    cmap = font.getBestCmap()
    seven = cmap[0x37]
    if font["hmtx"][seven][0] == ADVANCE:
        print(f"{path_in}: 7 already replaced")
        return
    cff = "CFF " in font
    vorigin = None
    if "vmtx" in font:
        bp = BoundsPen(font.getGlyphSet())
        font.getGlyphSet()[seven].draw(bp)
        vorigin = font["vmtx"][seven][1] + bp.bounds[3]

    def put(name, parts, advance):
        rec = finalize(parts, clockwise=not cff)
        replace_glyph(font, name, rec, advance)
        if vorigin is not None:
            bp = BoundsPen(None)
            rec.replay(bp)
            font["vmtx"][name] = (font["vmtx"][name][0], round(vorigin - bp.bounds[3]))

    put(seven, [seven_path()], ADVANCE)

    # fullwidth ７: the same 7, centred in its em box
    if 0xFF17 in cmap:
        name = cmap[0xFF17]
        adv = font["hmtx"][name][0]
        shift = round((adv - (RIGHT - LEFT)) / 2 - LEFT)
        put(name, [seven_path().transform(1, 0, 0, 1, shift, 0)], adv)

    # superior, inferior and ⅞ are rebuilt from the new 7
    builder = ExtraBuilder(font)
    # make ⁷ come from the new 7 rather than from the existing ⁷
    builder.cmap = {u: n for u, n in builder.cmap.items() if u != 0x2077}
    for uni in (0x2077, 0x2087, 0x215E):
        if uni in cmap:
            parts, adv = builder.build(NEW_GLYPHS[uni][1])
            put(cmap[uni], parts, adv)
    font.save(path_in)
    print(f"{path_in}: replaced 7 ７ ⁷ ₇ ⅞")


if __name__ == "__main__":
    for p in sys.argv[1:]:
        patch_font(p)
