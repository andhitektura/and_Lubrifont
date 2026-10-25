# Three corrections to and_Lubrifont:
#
# - Round dots become the dot of the period: the dots of ! ? ¡ ¿, the
#   diaeresis and dot accents (ä ё ï ė ż İ, also the combining marks), ÷ ∴ ∵
#   ∶ ∷ ※ ˙ ¨ and the bullet were round, unlike the period's rounded square.
#   Each round dot (a small filled contour, about as wide as tall, filling
#   less of its box than the period does) is replaced by the period's dot,
#   centred on it; a dot on the baseline keeps its bottom, and the bullet
#   keeps its size. Rings (° ˚ Å) and the symbols in KEEP keep their shapes.
# - % ‰ ‱: the two rings of % were joined to the slash. They are rebuilt as
#   separate rings (the ring of ‰) at least GAP units from the slash; the
#   glyph widens accordingly and the further rings of ‰ ‱ move with it.
# - Ø ∅ ⌀ get SIDE units of space at each side (Ø had its slash reaching
#   53 units past its advance, into the next character).
#
# Fonts already changed are skipped, so the script can be re-run safely.
#
# usage: py dots_percent_diameter.py font1.otf [font2.ttf ...]
#        (CJK fonts and the Regular; then make_weights.py, make_italics.py,
#        autohint.py, and re-measure the kerning)
#
# Requires: fonttools, skia-pathops

import sys
import pathops
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen
from add_macedonian_cyrillic import finalize
from diagonal_seven import replace_glyph

GAP = 60                          # % rings to slash (Bold keeps about 36)
SIDE = 80                         # space each side of Ø ∅ ⌀
KEEP = set(map(ord, "♿⊙◌⌖°˚"))    # round shapes that are not dots
DIAMETERS = (0xD8, 0x2205, 0x2300)    # Ø ∅ ⌀
PERCENT = 0x25
PER_MILLE = (0x2030, 0x2031)      # ‰ ‱


class PathPen(BasePen):
    """Draws a glyph into a pathops Path; BasePen expands TrueType
    contours that have no on-curve point."""
    def __init__(self, glyphset=None):
        super().__init__(glyphset)
        self.path = pathops.Path()
        self.pen = self.path.getPen()

    def _moveTo(self, pt): self.pen.moveTo(pt)
    def _lineTo(self, pt): self.pen.lineTo(pt)
    def _curveToOne(self, a, b, c): self.pen.curveTo(a, b, c)
    def _qCurveToOne(self, a, b): self.pen.qCurveTo(a, b)
    def _closePath(self): self.pen.closePath()
    def _endPath(self): self.pen.endPath()


def glyph_contours(gs, name):
    pen = PathPen(gs)
    gs[name].draw(pen)
    return list(pen.path.contours)


def size(c):
    x0, y0, x1, y1 = c.bounds
    return x1 - x0, y1 - y0


def moved(c, dx, dy, scale=1.0):
    return c.transform(scale, 0, 0, scale, dx, dy)


def combined(contours):
    """one path of several contours, keeping their directions (holes)"""
    p = pathops.Path()
    for c in contours:
        p.addPath(c)
    return p


def is_round_dot(c, others):
    w, h = size(c)
    if not (80 <= w <= 140 and 80 <= h <= 140 and abs(w - h) <= 15):
        return False
    if not 0.68 <= abs(c.area) / (w * h) <= 0.82:      # period: 0.92
        return False
    def inside(a, b):
        return a.bounds[0] > b.bounds[0] and a.bounds[2] < b.bounds[2] \
            and a.bounds[1] > b.bounds[1] and a.bounds[3] < b.bounds[3]
    # not a ring (holding a hole) and not the hole of one
    return not any(o is not c and (inside(o, c) or inside(c, o)) for o in others)


def square_dots(font, gs, cmap, cff, put):
    period = glyph_contours(gs, cmap[0x2E])[0]
    px0, py0, px1, py1 = period.bounds
    done = []
    for uni, name in sorted(cmap.items()):
        if uni >= 0x2E80 or uni in KEEP or 0x2300 <= uni <= 0x23FF or uni == 0x2E:
            continue
        cs = glyph_contours(gs, name)
        dots = [c for c in cs if is_round_dot(c, cs)]
        if not dots:
            continue
        parts = [combined(c for c in cs if c not in dots)]
        for d in dots:
            x0, y0, x1, y1 = d.bounds
            scale = (x1 - x0) / (px1 - px0) if uni == 0x2022 else 1.0
            pw, ph = (px1 - px0) * scale, (py1 - py0) * scale
            cx = (x0 + x1) / 2
            bottom = y0 if y0 < 20 else (y0 + y1) / 2 - ph / 2
            parts.append(moved(period, cx - pw / 2 - px0 * scale, bottom - py0 * scale, scale))
        put(name, parts, font["hmtx"][name][0])
        done.append(chr(uni))
    return done


def slash_band(contour):
    """The slash of %: the area between the lines of its two long edges."""
    segs = []
    pts = None
    for verb, p in contour.segments:
        if verb == "moveTo":
            pts = p[0]
        elif verb == "lineTo":
            segs.append((pts, p[0]))
            pts = p[0]
        elif p:
            pts = p[-1]
    longest = sorted(segs, key=lambda s: -abs(s[1][1] - s[0][1]))[:2]
    def x_at(seg, y):
        (xa, ya), (xb, yb) = seg
        return xa + (xb - xa) * (y - ya) / (yb - ya)
    left, right = sorted(longest, key=lambda s: x_at(s, 300))
    band = pathops.Path()
    pen = band.getPen()
    lo, hi = -400, 1200
    pen.moveTo((x_at(left, lo), lo))
    pen.lineTo((x_at(right, lo), lo))
    pen.lineTo((x_at(right, hi), hi))
    pen.lineTo((x_at(left, hi), hi))
    pen.closePath()
    return band


def touches(a, b):
    return bool(list(pathops.op(a, b, pathops.PathOp.INTERSECTION).contours))


def grown(path, by):
    """path plus everything within `by` units of it"""
    outline = pathops.Path(path)
    outline.stroke(2 * by, pathops.LineCap.ROUND_CAP, pathops.LineJoin.ROUND_JOIN, 4)
    outline.convertConicsToQuads()
    return pathops.op(path, outline, pathops.PathOp.UNION)


def separate_percent(font, gs, cmap, put):
    """Returns the shift of the second ring, or None if already separate."""
    cs = glyph_contours(gs, cmap[PERCENT])
    main = max(cs, key=lambda c: size(c)[1])
    if size(main)[0] < 330:                    # rebuilt: the slash alone is the tallest
        return None
    lsb_old = main.bounds[0]
    rsb_old = font["hmtx"][cmap[PERCENT]][0] - main.bounds[2]
    holes = sorted((c for c in cs if c is not main), key=lambda c: c.bounds[0])
    pm = glyph_contours(gs, cmap[0x2030])
    ring = [c for c in pm if size(c)[1] < 400 and size(c)[0] > 150][0]   # outer ring of ‰
    rw, rh = size(ring)

    band = slash_band(main)
    slash = pathops.op(main, band, pathops.PathOp.INTERSECTION)
    # ring outlines at the places of the old ones (counters kept)
    a_hole, b_hole = holes
    def ring_at(hole):
        hx = (hole.bounds[0] + hole.bounds[2]) / 2
        hy = (hole.bounds[1] + hole.bounds[3]) / 2
        rx = (ring.bounds[0] + ring.bounds[2]) / 2
        ry = (ring.bounds[1] + ring.bounds[3]) / 2
        return moved(ring, hx - rx, hy - ry)
    ring_a, ring_b = ring_at(a_hole), ring_at(b_hole)
    shift_a = lsb_old - ring_a.bounds[0]                  # keep the left side bearing
    ring_a, a_hole = moved(ring_a, shift_a, 0), moved(a_hole, shift_a, 0)

    ds = 0
    while touches(grown(moved(slash, ds, 0), GAP), ring_a):
        ds += 2
    slash = moved(slash, ds, 0)
    db = 0
    while touches(grown(slash, GAP), moved(ring_b, db, 0)):
        db += 2
    while db > -200 and not touches(grown(slash, GAP), moved(ring_b, db - 2, 0)):
        db -= 2
    ring_b, b_hole = moved(ring_b, db, 0), moved(b_hole, db, 0)

    def glyph(extra_dx=0, extra=()):
        outer = finalize([ring_a, slash, ring_b] + list(extra), clockwise=True)
        p = pathops.Path()
        outer.replay(p.getPen())
        for hole in [a_hole, b_hole]:
            p = pathops.op(p, hole, pathops.PathOp.DIFFERENCE)
        return p
    new = glyph()
    put(cmap[PERCENT], [new], round(new.bounds[2] + rsb_old))

    # ‰ ‱: the same, with their further rings moved by as much as the second ring
    b_shift = ring_b.bounds[0] - (main.bounds[2] - rw)
    for uni in PER_MILLE:
        if uni not in cmap:
            continue
        name = cmap[uni]
        cs = glyph_contours(gs, name)
        further = [c for c in cs if c.bounds[0] > main.bounds[2] - 5]
        p = pathops.Path(new)
        outers = [c for c in further if size(c)[0] > 150]
        holes_f = [c for c in further if size(c)[0] <= 150]
        for c in outers:
            p = pathops.op(p, moved(c, b_shift, 0), pathops.PathOp.UNION)
        for c in holes_f:
            p = pathops.op(p, moved(c, b_shift, 0), pathops.PathOp.DIFFERENCE)
        put(name, [p], round(font["hmtx"][name][0] + b_shift))
    return b_shift


def diameter_space(font, gs, cmap, put):
    done = []
    for uni in DIAMETERS:
        name = cmap.get(uni)
        if not name:
            continue
        cs = glyph_contours(gs, name)
        x0 = min(c.bounds[0] for c in cs)
        x1 = max(c.bounds[2] for c in cs)
        adv = font["hmtx"][name][0]
        if abs(x0 - SIDE) <= 2 and abs(adv - x1 - SIDE) <= 2:
            continue
        put(name, [moved(combined(cs), SIDE - x0, 0)], round(x1 - x0 + 2 * SIDE))
        done.append(chr(uni))
    return done


def patch_font(path):
    font = TTFont(path)
    cmap = font.getBestCmap()
    gs = font.getGlyphSet()
    cff = "CFF " in font

    def put(name, parts, advance):
        rec = finalize(parts, clockwise=not cff)
        replace_glyph(font, name, rec, advance)

    done = square_dots(font, gs, cmap, cff, put)
    report = [f"{len(done)} glyphs with square dots"] if done else []
    gs = font.getGlyphSet()
    if separate_percent(font, gs, cmap, put) is not None:
        report.append("% ‰ ‱ rings separated")
    gs = font.getGlyphSet()
    d = diameter_space(font, gs, cmap, put)
    if d:
        report.append(f"{' '.join(d)} spaced")
    if report:
        font.save(path)
    print(f"{path}: {'; '.join(report) if report else 'already changed'}")


if __name__ == "__main__":
    for p in sys.argv[1:]:
        patch_font(p)
