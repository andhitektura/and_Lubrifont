# Two changes to the lowercase of and_Lubrifont:
#
# - l gets a short foot: the stem turns right into an arm along the
#   baseline, the arm of the r turned upside down (same rounded corner and
#   thickness). The arm reaches FOOT units right of the stem's left edge; the
#   advance grows so the space after the foot stays RSB. Applies to l ĺ ľ ł
#   (their accents keep their places). The bar of ł is redrawn longer and
#   steeper (SLASH_*): crossing nearly flat, with a foot it would read as t.
#   Capital Ł gets the same bar: it is rebuilt from L (so re-running is safe).
# - i j і ј get the tall rounded dot of the dotted zero (90 x 170) instead of
#   the round dot, centred on the stem, its bottom where the round dot's was.
#
# Fonts already changed are skipped, so the script can be re-run safely.
#
# usage: py l_foot_i_dot.py font1.otf [font2.ttf ...]
#        (then make_weights.py, make_italics.py and autohint.py)
#
# Requires: fonttools, skia-pathops

import sys
import pathops
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.boundsPen import BoundsPen
from add_macedonian_cyrillic import finalize
import math
from diagonal_seven import replace_glyph, rounded_polygon

FOOT = 140                       # arm end, from the stem's left edge
RSB = 30                         # right side bearing after the foot
L_LETTERS = (0x6C, 0x13A, 0x13E, 0x142)          # l ĺ ľ ł
SLASH_LENGTH, SLASH_ANGLE, SLASH_Y = 440, 40, 400   # the bar of ł: length, degrees, centre height
SLASH_WIDTH, CORNER = 90, 27     # its thickness and corner rounding (as the stems)
DOT_LETTERS = (0x69, 0x6A, 0x456, 0x458)         # i j і ј


def contours(name, gs):
    rec = RecordingPen()
    gs[name].draw(rec)
    out, cur = [], []
    for op in rec.value:
        cur.append(op)
        if op[0] in ("closePath", "endPath"):
            out.append(cur)
            cur = []
    return out


def bounds(contour):
    bp = BoundsPen(None)
    for op, pts in contour:
        getattr(bp, op)(*pts)
    return bp.bounds


def to_path(contour, fn=lambda x, y: (x, y)):
    path = pathops.Path()
    pen = path.getPen()
    for op, pts in contour:
        getattr(pen, op)(*[fn(x, y) for x, y in pts])
    return path


def r_contour(font, gs):
    """The r's outline, stem from x=0, arm cut to FOOT."""
    r = font.getBestCmap()[0x72]
    c = max(contours(r, gs), key=lambda c: bounds(c)[3] - bounds(c)[1])
    x0 = bounds(c)[0]
    reach = bounds(c)[2] - x0
    return c, x0, reach


def foot_path(font, gs, stem_left, top, bottom):
    c, x0, reach = r_contour(font, gs)
    rb = bounds(c)
    arm_shift = FOOT - reach     # shorten/lengthen the arm to FOOT
    def fn(x, y):
        x = x - x0
        if x > 121 and y >= 390:
            x += arm_shift
        # flip: the r's x-height arm becomes a baseline foot
        y2 = rb[3] + rb[1] - y               # 485 <-> -8
        if y2 > 200:
            y2 += top - rb[3]                # stem up to the l's top
        y2 += bottom - rb[1]
        return x + stem_left, y2
    return to_path(c, fn)


def slash(cx, cy):
    """The bar of ł: a rounded bar SLASH_LENGTH long, rising SLASH_ANGLE°."""
    a = math.radians(SLASH_ANGLE)
    ux, uy = math.cos(a), math.sin(a)                # along the bar
    vx, vy = -uy, ux                                 # across it
    h, w = SLASH_LENGTH / 2, SLASH_WIDTH / 2
    pts = [(cx + sx * h * ux + sy * w * vx, cy + sx * h * uy + sy * w * vy)
           for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    # start mid-edge: rounded_polygon needs an unrounded first point
    start = ((pts[0][0] + pts[1][0]) / 2, (pts[0][1] + pts[1][1]) / 2)
    return rounded_polygon([start] + pts[1:] + pts[:1], [0] + [CORNER] * 4)


def tall_dot(font, gs):
    zero = font.getBestCmap()[0x30]
    c = min(contours(zero, gs), key=lambda c: (bounds(c)[2] - bounds(c)[0]) * (bounds(c)[3] - bounds(c)[1]))
    return c, bounds(c)


def patch_font(path):
    font = TTFont(path)
    cmap = font.getBestCmap()
    gs = font.getGlyphSet()
    cff = "CFF " in font
    done = []
    dot, db = tall_dot(font, gs)
    l_stem = [c for c in contours(cmap[0x6C], gs) if bounds(c)[3] - bounds(c)[1] > 600][0]
    lb = bounds(l_stem)
    if lb[2] - lb[0] > 120:
        l_stem = None                                    # l already has its foot
    for uni in L_LETTERS:
        name = cmap.get(uni)
        if not name or l_stem is None:
            continue
        cs = contours(name, gs)
        stem = [c for c in cs if bounds(c)[3] - bounds(c)[1] > 600][0]
        # the stem's left edge at the top (ł: the slash makes the contour wider)
        left = min(x for _, pts in stem for x, y in pts if y > lb[3] - 60)
        old_stem = to_path(l_stem, lambda x, y: (x - lb[0] + left, y))
        rest = pathops.op(to_path(stem), old_stem, pathops.PathOp.DIFFERENCE)
        sb = (left, lb[1], left + lb[2] - lb[0], lb[3])
        if uni == 0x142:
            rest = slash((sb[0] + sb[2]) / 2, SLASH_Y)
        parts = [foot_path(font, gs, sb[0], sb[3], sb[1]), rest]
        parts += [to_path(c) for c in cs if c is not stem]
        rec = finalize(parts, clockwise=not cff)
        bp = BoundsPen(None)
        rec.replay(bp)
        if uni == 0x142:                                 # bar may reach past the old side bearings
            shift = RSB - bp.bounds[0]
            moved = RecordingPen()
            for op, pts in rec.value:
                moved.value.append((op, tuple((x + shift, y) for x, y in pts)))
            rec = moved
            adv = round(bp.bounds[2] + shift + RSB)
        else:
            adv = max(font["hmtx"][name][0], round(sb[0] + FOOT + RSB))
        replace_glyph(font, name, rec, adv)
        done.append(chr(uni))
    if 0x141 in cmap and 0x4C in cmap:                   # Ł = L + the same bar
        cap = cmap[0x141]
        cs = contours(cmap[0x4C], gs)
        stem = max(cs, key=lambda c: bounds(c)[3] - bounds(c)[1])
        left = min(x for _, pts in stem for x, y in pts if y > 650)
        parts = [to_path(c) for c in cs] + [slash(left + 45, SLASH_Y)]
        rec = finalize(parts, clockwise=not cff)
        bp = BoundsPen(None)
        rec.replay(bp)
        shift = RSB - bp.bounds[0]
        moved = RecordingPen()
        for op, pts in rec.value:
            moved.value.append((op, tuple((x + shift, y) for x, y in pts)))
        replace_glyph(font, cap, moved, round(font["hmtx"][cmap[0x4C]][0] + shift))
        done.append("Ł")
    for uni in DOT_LETTERS:
        name = cmap.get(uni)
        if not name:
            continue
        cs = contours(name, gs)
        dots = [c for c in cs if bounds(c)[1] > 500 and abs((bounds(c)[3] - bounds(c)[1]) - (bounds(c)[2] - bounds(c)[0])) < 10]
        if not dots:
            continue                                     # already a tall dot
        b = bounds(dots[0])
        cx = (b[0] + b[2]) / 2
        dx = cx - (db[0] + db[2]) / 2
        dy = b[1] - db[1]
        parts = [to_path(dot, lambda x, y: (x + dx, y + dy))]
        parts += [to_path(c) for c in cs if c is not dots[0]]
        rec = finalize(parts, clockwise=not cff)
        replace_glyph(font, name, rec, font["hmtx"][name][0])
        done.append(chr(uni))
    if done:
        font.save(path)
    print(f"{path}: {' '.join(done) if done else 'already changed'}")


if __name__ == "__main__":
    for p in sys.argv[1:]:
        patch_font(p)
