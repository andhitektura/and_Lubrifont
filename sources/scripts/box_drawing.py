# Box drawing (U+2500-257F) and block elements (U+2580-259F) for and_Lubrifont,
# drawn on the grid of the box drawings the CJK fonts already have: a cell
# 765 units wide from -120 to 880, light lines 60 units (61 vertical), heavy
# lines 120 (121), and every corner rounded with a radius of 30 except where
# a line runs out of the cell (so lines join up with the next character).
# Double lines are two light lines 100 units apart.
#
# Used by add_box_currency.py; `py box_drawing.py <cjk font>` compares the
# generated glyphs with the font's own box drawings.

import math
import unicodedata
import pathops
from fontTools.pens.recordingPen import RecordingPen

W, BOTTOM, TOP = 765, -120, 880
CX, CY = 382.5, 380
R = 30
# x ranges of vertical strokes, y ranges of horizontal strokes (Regular)
VX0 = {"L": (352, 413), "H": (322, 443), "D": ((272, 333), (432, 493))}
HY0 = {"L": (350, 410), "H": (320, 440), "D": ((270, 330), (430, 490))}
VX, HY = VX0, HY0
GROW = 0                  # added to each edge of a line (make_weights.py)


def set_weight(grow):
    """lines `grow` units thicker on each edge (negative: thinner), for the
    Light and Bold; the cell, the line centres and the gaps of the dashes
    stay as in the Regular, so the characters still join up"""
    global VX, HY, GROW
    g = lambda r: (r[0] - grow, r[1] + grow)
    VX = {"L": g(VX0["L"]), "H": g(VX0["H"]), "D": (g(VX0["D"][0]), g(VX0["D"][1]))}
    HY = {"L": g(HY0["L"]), "H": g(HY0["H"]), "D": (g(HY0["D"][0]), g(HY0["D"][1]))}
    GROW = grow

DIRS = ("UP", "RIGHT", "DOWN", "LEFT")
WEIGHT_WORDS = {"LIGHT": "L", "HEAVY": "H", "SINGLE": "L", "DOUBLE": "D"}


def parse_arms(name):
    """'BOX DRAWINGS UP HEAVY AND RIGHT DOWN LIGHT' -> {UP: H, RIGHT: L, DOWN: L}"""
    words = name.replace("BOX DRAWINGS ", "").split(" AND ")
    arms, weight = {}, None
    for seg in words:
        toks = seg.split()
        w = [WEIGHT_WORDS[t] for t in toks if t in WEIGHT_WORDS]
        if w:
            weight = w[0]
        # "LIGHT LEFT AND HEAVY RIGHT": a weight word belongs to the
        # directions that follow it in its own segment
        cur = weight
        for t in toks:
            if t in WEIGHT_WORDS:
                cur = WEIGHT_WORDS[t]
            elif t == "VERTICAL":
                arms["UP"] = arms["DOWN"] = cur
            elif t == "HORIZONTAL":
                arms["LEFT"] = arms["RIGHT"] = cur
            elif t in DIRS:
                arms[t] = cur
    return arms


def rect(x0, y0, x1, y1):
    p = pathops.Path()
    pen = p.getPen()
    pen.moveTo((x0, y0)); pen.lineTo((x0, y1)); pen.lineTo((x1, y1)); pen.lineTo((x1, y0))
    pen.closePath()
    return p


def union(paths):
    out = pathops.Path()
    for p in paths:
        out = pathops.op(out, p, pathops.PathOp.UNION)
    return out


def _cover(ranges):
    """outer extent of several stroke ranges"""
    flat = []
    for r in ranges:
        flat += list(r) if isinstance(r[0], tuple) else [r]
    return min(a for a, b in flat), max(b for a, b in flat)


def lines_for(arms):
    """rectangles of a box drawing character given its four arms"""
    rects = []
    for arm, w in arms.items():
        horizontal = arm in ("LEFT", "RIGHT")
        if horizontal:
            perp = {d: arms[d] for d in ("UP", "DOWN") if d in arms}
            opposite = "LEFT" if arm == "RIGHT" else "RIGHT"
            stroke, perp_ranges = HY, VX
        else:
            perp = {d: arms[d] for d in ("LEFT", "RIGHT") if d in arms}
            opposite = "DOWN" if arm == "UP" else "UP"
            stroke, perp_ranges = VX, HY
        centre = CX if horizontal else CY
        # the edge of the cell this arm runs to, and which end is "near"
        far = (W if arm == "RIGHT" else 0) if horizontal else (TOP if arm == "UP" else BOTTOM)
        sign = 1 if far > centre else -1          # +1: arm grows towards larger coords
        # perpendicular arms on the side the arm comes from / goes to are irrelevant
        # in a single sense: what matters is which perpendicular arms exist
        pa, pb = (("UP", "DOWN") if horizontal else ("RIGHT", "LEFT"))
        # pa: perpendicular arm on the "high" side of this arm's line(s)

        def near_end_single():
            if opposite in arms and arms[opposite] != "D":
                if w == "H" and arms[opposite] == "L":
                    # light into heavy: the step sits at the edge of a light line
                    lo, hi = perp_ranges["L"]
                    return lo if sign > 0 else hi
                return centre
            doubles = [d for d in perp if perp[d] == "D"]
            if doubles:
                lo, hi = perp_ranges["D"]
                if opposite in arms:                   # crossing a double line
                    return centre
                if len(doubles) == 2:                  # attach to the nearer line
                    return (hi[0] if sign > 0 else lo[1])
                return (lo[0] if sign > 0 else hi[1])  # corner: to the outer line
            if perp:
                lo, hi = _cover([perp_ranges[w2] for w2 in perp.values()])
                return lo if sign > 0 else hi
            lo, hi = perp_ranges[w]                    # half line
            return lo if sign > 0 else hi

        if w != "D":
            a = near_end_single()
            lo, hi = stroke[w]
            seg = sorted((a, far))
            rects.append(rect(seg[0], lo, seg[1], hi) if horizontal else rect(lo, seg[0], hi, seg[1]))
            continue

        # double arm: two lines; each ends according to the perpendicular arm
        # on its own side ("same") and on the other side ("other")
        (l0, l1), (h0, h1) = stroke["D"]
        plo, phi = perp_ranges["D"]
        for line, same, other in (((h0, h1), pa, pb), ((l0, l1), pb, pa)):
            ps, po = arms.get(same), arms.get(other)
            if ps == "D":                 # inner corner with that double arm
                a = phi[0] if sign > 0 else plo[1]
            elif ps:                      # single arm on this side: meet it
                rng = perp_ranges[ps]
                a = rng[0] if sign > 0 else rng[1]
            elif po == "D":               # outer corner
                a = plo[0] if sign > 0 else phi[1]
            elif po:
                rng = perp_ranges[po]
                a = rng[0] if sign > 0 else rng[1]
            else:
                a = centre
            seg = sorted((a, far))
            rects.append(rect(seg[0], line[0], seg[1], line[1]) if horizontal
                         else rect(line[0], seg[0], line[1], seg[1]))
    return rects


def round_corners(path, r=R):
    """Replace every corner of a straight-edged outline by a quadratic curve
    with its control point on the corner (radius r, or half the shorter
    neighbouring edge), except corners on the edge of the cell."""
    rec = RecordingPen()
    path.draw(rec)
    contours, cur = [], []
    for op, args in rec.value:
        if op == "moveTo":
            cur = [args[0]]
        elif op == "lineTo":
            cur.append(args[0])
        elif op in ("closePath", "endPath"):
            contours.append(cur)
            cur = []
        else:
            raise ValueError("round_corners expects straight lines: " + op)
    out = RecordingPen()
    for pts in contours:
        # drop repeated and collinear points
        clean = []
        for p in pts:
            if clean and abs(p[0] - clean[-1][0]) < 1e-6 and abs(p[1] - clean[-1][1]) < 1e-6:
                continue
            clean.append(p)
        if len(clean) > 1 and clean[0] == clean[-1]:
            clean.pop()
        changed = True
        while changed and len(clean) > 2:
            changed = False
            for i in range(len(clean)):
                a, b, c = clean[i - 1], clean[i], clean[(i + 1) % len(clean)]
                if abs((b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0])) < 1e-6:
                    del clean[i]
                    changed = True
                    break
        n = len(clean)

        def on_edge(p):
            return p[0] in (0, W) or p[1] in (BOTTOM, TOP)

        segs = []
        for i in range(n):
            a, b, c = clean[i - 1], clean[i], clean[(i + 1) % n]
            if on_edge(b):
                segs.append(("pt", b))
                continue
            la = math.dist(a, b)
            lc = math.dist(b, c)
            ra = min(r, la / 2 if not on_edge(a) else la)
            rc = min(r, lc / 2 if not on_edge(c) else lc)
            rr = min(ra, rc)
            p0 = (b[0] + (a[0] - b[0]) * rr / la, b[1] + (a[1] - b[1]) * rr / la)
            p1 = (b[0] + (c[0] - b[0]) * rr / lc, b[1] + (c[1] - b[1]) * rr / lc)
            segs.append(("curve", p0, b, p1))
        first = segs[0]
        start = first[1] if first[0] == "pt" else first[3]
        out.moveTo(start)
        for s in segs[1:] + [first]:
            if s[0] == "pt":
                out.lineTo(s[1])
            else:
                out.lineTo(s[1])
                out.qCurveTo(s[2], s[3])
        out.closePath()
    p = pathops.Path()
    out.replay(p.getPen())
    return p


def stroke_path(points, width, closed=False):
    p = pathops.Path()
    pen = p.getPen()
    pen.moveTo(points[0])
    for pt in points[1:]:
        pen.lineTo(pt)
    pen.endPath()
    p.stroke(width, pathops.LineCap.BUTT_CAP, pathops.LineJoin.ROUND_JOIN, 4)
    p.convertConicsToQuads()
    return p


def clip_cell(p):
    return pathops.op(p, rect(0, BOTTOM, W, TOP), pathops.PathOp.INTERSECTION)


def dashed(uni, name):
    n = {"DOUBLE": 2, "TRIPLE": 3, "QUADRUPLE": 4}[name.split()[3]]
    w = "H" if "HEAVY" in name else "L"
    vertical = name.endswith("VERTICAL")
    length = (TOP - BOTTOM) if vertical else W
    start = BOTTOM if vertical else 0
    # gaps as in the existing ┄ ┈ ╌: 60 units, centred on the cell joins
    gap = (60 if not vertical else 60.5) - 2 * GROW
    piece = (length - (n - 1) * gap) / n
    rects = []
    for i in range(n):
        a = round(start + i * (piece + gap))
        b = round(start + i * (piece + gap) + piece)
        if vertical:
            lo, hi = VX[w]
            rects.append(rect(lo, a, hi, b))
        else:
            lo, hi = HY[w]
            rects.append(rect(a, lo, b, hi))
    return [round_corners(r) for r in rects]


def arc_glyph(name):
    # LIGHT ARC DOWN AND RIGHT etc.: the two lines joined by a quarter circle
    # (radius 200 on the centre line), drawn for ╭ and mirrored for the others
    k = 0.5523
    ra, hx, hy = 200, 30.5 + GROW, 30 + GROW   # vertical line 61, horizontal 60 units
    cx, cy = CX + ra, CY - ra
    ro_x, ro_y, ri_x, ri_y = ra + hx, ra + hy, ra - hx, ra - hy
    p = pathops.Path()
    pen = p.getPen()
    pen.moveTo((CX - hx, BOTTOM))
    pen.lineTo((CX - hx, cy))
    pen.curveTo((CX - hx, cy + k * ro_y), (cx - k * ro_x, CY + hy), (cx, CY + hy))
    pen.lineTo((W, CY + hy))
    pen.lineTo((W, CY - hy))
    pen.lineTo((cx, CY - hy))
    pen.curveTo((cx - k * ri_x, CY - hy), (CX + hx, cy + k * ri_y), (CX + hx, cy))
    pen.lineTo((CX + hx, BOTTOM))
    pen.closePath()
    words = name.split()
    sx = -1 if "LEFT" in words else 1
    sy = -1 if "UP" in words else 1
    if sx < 0 or sy < 0:
        p = p.transform(sx, 0, 0, sy, W if sx < 0 else 0, (2 * CY) if sy < 0 else 0)
    return [pathops.simplify(p)]


def diagonal_glyph(name):
    w = 60 + 2 * GROW
    up_right = ((-W / 2, BOTTOM - 500), (W * 1.5, TOP + 500))
    k = (TOP - BOTTOM) / W
    l1 = [(-100, BOTTOM - 100 * k), (W + 100, TOP + 100 * k)]       # lower left to upper right
    l2 = [(-100, TOP + 100 * k), (W + 100, BOTTOM - 100 * k)]
    parts = []
    if "CROSS" in name or "UPPER RIGHT TO LOWER LEFT" in name:
        parts.append(clip_cell(stroke_path(l1, w)))
    if "CROSS" in name or "UPPER LEFT TO LOWER RIGHT" in name:
        parts.append(clip_cell(stroke_path(l2, w)))
    return parts


def box_glyph(uni):
    """list of pathops paths and the advance width"""
    name = unicodedata.name(chr(uni))
    if "DASH" in name:
        return dashed(uni, name), W
    if " ARC " in name:
        return arc_glyph(name), W
    if "DIAGONAL" in name:
        return diagonal_glyph(name), W
    arms = parse_arms(name)
    return [round_corners(union(lines_for(arms)))], W


# --- block elements ---------------------------------------------------------

def block_glyph(uni):
    H = TOP - BOTTOM
    if 0x2581 <= uni <= 0x2588:                 # lower n/8 blocks
        return [rect(0, BOTTOM, W, BOTTOM + H * (uni - 0x2580) / 8)], W
    if 0x2589 <= uni <= 0x258F:                 # left n/8 blocks
        return [rect(0, BOTTOM, W * (0x2590 - uni) / 8, TOP)], W
    simple = {
        0x2580: [(0, .5, 1, 1)], 0x2590: [(.5, 0, 1, 1)],
        0x2594: [(0, 7 / 8, 1, 1)], 0x2595: [(7 / 8, 0, 1, 1)],
        0x2596: [(0, 0, .5, .5)], 0x2597: [(.5, 0, 1, .5)],
        0x2598: [(0, .5, .5, 1)], 0x259D: [(.5, .5, 1, 1)],
        0x2599: [(0, 0, .5, 1), (.5, 0, 1, .5)],
        0x259A: [(0, .5, .5, 1), (.5, 0, 1, .5)],
        0x259B: [(0, .5, 1, 1), (0, 0, .5, .5)],
        0x259C: [(0, .5, 1, 1), (.5, 0, 1, .5)],
        0x259E: [(.5, .5, 1, 1), (0, 0, .5, .5)],
        0x259F: [(.5, 0, 1, 1), (0, 0, .5, .5)],
    }
    if uni in simple:
        return [rect(W * a, BOTTOM + H * b, W * c, BOTTOM + H * d) for a, b, c, d in simple[uni]], W
    if uni in (0x2591, 0x2592, 0x2593):         # shades: a grid of the font's square dots
        cols, rows = 6, 8
        cw, ch = W / cols, H / rows
        size = {0x2591: 0.36, 0x2592: 0.56, 0x2593: 0.78}[uni]
        parts = []
        for i in range(cols):
            for j in range(rows):
                s = size * min(cw, ch)
                x = cw * (i + .5) + (cw / 4 if j % 2 else -cw / 4) * 0
                y = BOTTOM + ch * (j + .5)
                parts.append(round_corners(rect(x - s / 2, y - s / 2, x + s / 2, y + s / 2), r=min(20, s / 4)))
        return parts, W
    raise KeyError(hex(uni))


if __name__ == "__main__":
    import sys
    from fontTools.ttLib import TTFont
    font = TTFont(sys.argv[1])
    cmap, gs = font.getBestCmap(), font.getGlyphSet()
    worst = []
    for u in range(0x2500, 0x2580):
        if u not in cmap:
            continue
        mine = union(box_glyph(u)[0])
        ref = pathops.Path()
        gs[cmap[u]].draw(ref.getPen())
        ref = pathops.simplify(ref)
        diff = pathops.op(mine, ref, pathops.PathOp.XOR)
        rec = RecordingPen(); diff.draw(rec)
        from fontTools.pens.areaPen import AreaPen
        ap = AreaPen(); diff.draw(ap)
        worst.append((abs(ap.value), chr(u), hex(u)))
    worst.sort(reverse=True)
    for w in worst[:25]:
        print(w)
    print("total", len(worst), "max", worst[0][0])
