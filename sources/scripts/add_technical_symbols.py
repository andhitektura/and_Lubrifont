# Add the remaining technical symbols for architectural and engineering
# documents to and_Lubrifont: math operators (⋅ ∡ ≅ ∼ ∓ ∂ ∇ ∛ ‱), rotation
# and double arrows, electrical / plan symbols (⊗ ⊕ ◯ ⌖ ⌂), notes and
# checklists (⚠ ☐ ☑ ☒ ✕ ♿ ℓ ℉ ℮), the GD&T tolerance symbols, more fractions,
# superscript / subscript ( ) = + − and an em space.
#
# Works like add_extra_glyphs.py (and reuses its machinery): every glyph is
# drawn from the font's own strokes and boxes (arrows and shapes on the 765
# unit symbol grid, math signs on the 662 unit math width and axis), so the
# script runs on the CJK fonts and the Regular alike. Glyphs already in a
# font are skipped, so it can be re-run safely.
#
# usage: py add_technical_symbols.py font1.otf [font2.ttf ...]
#        (then make_weights.py, make_italics.py and autohint.py)
#
# Requires: fonttools, skia-pathops

import math
import sys
import pathops
from fontTools.misc.transform import Transform
from add_macedonian_cyrillic import draw_contours, patch_font
from add_extra_glyphs import ExtraBuilder, rect, op

W = 88                    # stroke of the arrows and symbols
BOX = 765                 # advance of arrows and geometric shapes
MATH = 662                # advance of + − = ± ×
AXIS = 368                # math axis (centre of =)
MID = 361                 # centre of the symbol box (35..687)

NEW_GLYPHS = {
    # math
    0x22C5: ("dotmath", ("dot_operator",)),
    0x2221: ("measuredangle", ("measured_angle",)),
    0x223C: ("similar", ("tilde_operator",)),
    0x2245: ("congruent", ("congruent",)),
    0x2213: ("minusplus", ("mirror", 0x00B1, "y")),
    0x2202: ("partialdiff", ("partial",)),
    0x2207: ("gradient", ("mirror", 0x2206, "y")),
    0x221B: ("cuberoot", ("cube_root",)),
    0x2031: ("perthousandzero", ("basis_points",)),
    # arrows
    0x21D1: ("arrowdblup", ("rotate", 0x21D2, 90)),
    0x21D3: ("arrowdbldown", ("rotate", 0x21D2, -90)),
    0x21D5: ("arrowdblupdown", ("upright", 0x21D4)),
    0x21BA: ("anticlockwise", ("rotation", 1)),
    0x21BB: ("clockwise", ("rotation", -1)),
    0x2794: ("heavyarrow", ("heavy_arrow",)),
    # shapes and plan symbols
    0x25AA: ("blacksmallsquare", ("small_square",)),
    0x25CA: ("lozenge", ("lozenge",)),
    0x25EF: ("largecircle", ("copy", 0x25CB)),
    0x2295: ("circleplus", ("circled", "plus")),
    0x2297: ("circletimes", ("circled", "times")),
    0x2302: ("house", ("house",)),
    0x2316: ("position", ("position",)),
    # notes, checklists, units
    0x26A0: ("warning", ("warning",)),
    0x2610: ("ballotbox", ("copy", 0x25A1)),
    0x2611: ("ballotboxcheck", ("ballot", 0x2713)),
    0x2612: ("ballotboxx", ("ballot", 0x2717)),
    0x2715: ("multiplicationx", ("stroke", ((140, 160), (570, 590)), ((140, 590), (570, 160)))),
    0x267F: ("wheelchair", ("wheelchair",)),
    0x2113: ("litre", ("script_l",)),
    0x2109: ("degreefahrenheit", ("degree_letter", ord("F"))),
    0x212E: ("estimated", ("estimated",)),
    # GD&T (ISO 1101 / ASME Y14.5)
    0x2313: ("segment", ("segment",)),
    0x232D: ("cylindricity", ("cylindricity",)),
    0x232F: ("symmetry", ("lines", ((182, MID + 170), (582, MID + 170)), ((82, MID), (682, MID)),
                          ((182, MID - 170), (582, MID - 170)))),
    0x2330: ("totalrunout", ("total_runout",)),
    0x2331: ("dimensionorigin", ("dimension_origin",)),
    0x2332: ("conicaltaper", ("lines", ((92, MID), (673, MID)), ((150, 600), (620, 470)),
                              ((150, 122), (620, 252)))),
    0x2333: ("slope", ("closed", (100, 100), (665, 100), (100, 520))),
    0x2334: ("counterbore", ("lines", ((110, 610), (110, 110), (655, 110), (655, 610)))),
    0x2335: ("countersink", ("lines", ((110, 610), (382, 110), (655, 610)))),
    0x23E4: ("straightness", ("lines", ((92, MID), (673, MID)))),
    0x23E5: ("flatness", ("closed", (200, 200), (673, 200), (565, 520), (92, 520))),
    # fractions
    0x2155: ("onefifth", ("fraction", "1", "5")),
    0x2156: ("twofifths", ("fraction", "2", "5")),
    0x2157: ("threefifths", ("fraction", "3", "5")),
    0x2158: ("fourfifths", ("fraction", "4", "5")),
    0x2159: ("onesixth", ("fraction", "1", "6")),
    0x215A: ("fivesixths", ("fraction", "5", "6")),
    # superscript / subscript signs
    0x207C: ("equal.superior", ("superior_equal",)),
    0x207D: ("parenleft.superior", ("superior_sign", 0x0028)),
    0x207E: ("parenright.superior", ("superior_sign", 0x0029)),
    0x208A: ("plus.inferior", ("inferior_of", 0x207A)),
    0x208B: ("minus.inferior", ("inferior_of", 0x207B)),
    0x208C: ("equal.inferior", ("inferior_of", 0x207C)),
    0x208D: ("parenleft.inferior", ("inferior_of", 0x207D)),
    0x208E: ("parenright.inferior", ("inferior_of", 0x207E)),
    # spaces
    0x2003: ("emspace", ("space", 1000)),
}


def arc(cx, cy, r, a0, a1, steps=48):
    """Points along a circular arc, angles in degrees (counter-clockwise)."""
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / steps)),
             cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / steps))) for i in range(steps + 1)]


def disc(cx, cy, r):
    p = pathops.Path()
    pen = p.getPen()
    pts = arc(cx, cy, r, 0, 360, 96)[:-1]
    pen.moveTo(pts[0])
    for pt in pts[1:]:
        pen.lineTo(pt)
    pen.closePath()
    return p


class SymbolBuilder(ExtraBuilder):

    def lines(self, *polylines, width=W):
        return self._stroke(polylines, width)

    def _union(self, parts):
        out = parts[0]
        for p in parts[1:]:
            out = op(out, p, pathops.PathOp.UNION)
        return out

    def _ring(self, cx, cy, r, width=W):
        return op(disc(cx, cy, r + width / 2), disc(cx, cy, r - width / 2), pathops.PathOp.DIFFERENCE)

    # --- generic ------------------------------------------------------------

    def build_lines(self, *polylines):
        return [self.lines(*polylines)], BOX

    def build_closed(self, *pts):
        return [self.lines(list(pts) + [pts[0], pts[1]])], BOX

    def build_space(self, advance):
        return [pathops.Path()], advance

    # --- math ---------------------------------------------------------------

    def build_dot_operator(self):
        # the middle dot ·, centred on the math axis and width
        x0, y0, x1, y1 = self.bounds(0x00B7)
        t = Transform().translate(MATH / 2 - (x0 + x1) / 2, AXIS - (y0 + y1) / 2)
        return [self.path(0x00B7, t)], MATH

    def _wave(self, x0, x1, cy, amp):
        pts = [(x0 + (x1 - x0) * i / 40, cy + amp * math.sin(2 * math.pi * i / 40)) for i in range(41)]
        return self.lines(pts)

    def build_tilde_operator(self):
        return [self._wave(110, 552, AXIS, 62)], MATH

    def build_congruent(self):
        bars = [rect(65, 150, 596, 238, r=40), rect(65, 330, 596, 418, r=40)]
        return bars + [self._wave(110, 552, 560, 55)], MATH

    def build_measured_angle(self):
        angle, adv = self.path(0x2220), self.advance(0x2220)
        x0, y0, x1, y1 = self.bounds(0x2220)
        top = math.degrees(math.atan2(y1 - y0, x1 - x0))
        # keep the round ends of the arc clear of the baseline and the leg
        return [angle, self.lines(arc(x0, y0, 380, 9, top - 7))], adv

    def build_partial(self):
        # a d whose ascender bends back to the left at the top
        d = self.path(ord("d"))
        x0, y0, x1, y1 = self.bounds(ord("d"))
        stem_x0 = x1 - self.STEM
        hook = rect(stem_x0 - 170, y1 - 91, x1, y1, r=27)
        return [d, hook], self.advance(ord("d"))

    def build_cube_root(self):
        root = self.path(0x221A)
        x0, y0, x1, y1 = self.bounds(0x00B3)
        s = 0.72
        three = self.path(0x00B3, Transform().translate(30, 330).scale(s).translate(-x0, -y0))
        return [root, three], self.advance(0x221A)

    def build_basis_points(self):
        # ‰ with one more small zero after the last one
        contours = self.contours(0x2030)
        boxes = [(c, self.bounds_of_contour(c)) for c in contours]
        low = [b for c, b in boxes if b[3] < 350]
        last = max(low, key=lambda b: b[2])
        step = last[2] - last[0] + 40
        extra = [c for c, b in boxes if b[3] < 350 and b[0] >= last[0] - 1 and b[2] <= last[2] + 1]
        p = pathops.Path()
        draw_contours(extra, p.getPen())
        return [self.path(0x2030), pathops.simplify(p).transform(1, 0, 0, 1, step, 0)], self.advance(0x2030) + step

    def bounds_of_contour(self, c):
        from add_macedonian_cyrillic import bounds_of
        return bounds_of([c])

    # --- arrows -------------------------------------------------------------

    def build_upright(self, uni):
        # a horizontal arrow turned upright, centred in the ↑ box
        x0, y0, x1, y1 = self.bounds(uni)
        ux0, uy0, ux1, uy1 = self.bounds(0x2191)
        t = Transform().translate((ux0 + ux1) / 2, (uy0 + uy1) / 2).rotate(math.pi / 2).translate(-(x0 + x1) / 2, -(y0 + y1) / 2)
        return [self.path(uni, t)], self.advance(0x2191)

    def build_rotation(self, direction):
        # an open circle with an arrow head, ↺ (1) or ↻ (-1)
        cx, cy, r = BOX / 2, MID, 240
        # open at the top; the head sits at the end of the stroke and points
        # along it, over the gap (↻ is the mirror image)
        start, end = (120, 400) if direction == 1 else (60, -220)
        ring = self.lines(arc(cx, cy, r, start, end))
        a = math.radians(end)
        tip = (cx + r * math.cos(a), cy + r * math.sin(a))
        tangent = a + direction * math.pi / 2           # direction of travel
        head = 130
        wings = [(tip[0] - head * math.cos(tangent + s * math.radians(40)),
                  tip[1] - head * math.sin(tangent + s * math.radians(40))) for s in (1, -1)]
        return [ring, self.lines([wings[0], tip, wings[1]])], BOX

    def build_heavy_arrow(self):
        x0, y0, x1, y1 = self.bounds(0x2192)
        w = 130
        cy, h = (y0 + y1) / 2, w / 2
        tip = x1 - h
        reach = (y1 - y0) / 2 - h
        return [self.lines(((x0 + h, cy), (tip, cy)), ((tip - reach, cy + reach), (tip, cy), (tip - reach, cy - reach)),
                           width=w)], self.advance(0x2192)

    # --- shapes -------------------------------------------------------------

    def build_small_square(self):
        return [rect(220, MID - 163, 545, MID + 163, r=27)], BOX

    def build_lozenge(self):
        pts = [(382, 40), (612, MID), (382, 682), (152, MID)]
        return [self.lines(pts + pts[:2])], BOX

    def build_circled(self, kind):
        ring = self.path(0x25CB)
        x0, y0, x1, y1 = self.bounds(0x25CB)
        cx, cy, r = (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2
        if kind == "plus":
            cross = self.lines(((cx - r, cy), (cx + r, cy)), ((cx, cy - r), (cx, cy + r)))
        else:
            d = r / math.sqrt(2)
            cross = self.lines(((cx - d, cy - d), (cx + d, cy + d)), ((cx - d, cy + d), (cx + d, cy - d)))
        cross = op(cross, disc(cx, cy, r - 20), pathops.PathOp.INTERSECTION)
        return [ring, cross], self.advance(0x25CB)

    def build_house(self):
        pts = [(140, 60), (625, 60), (625, 400), (382, 640), (140, 400)]
        return [self.lines(pts + pts[:2])], BOX

    def build_position(self):
        cx, cy = BOX / 2, MID
        return [self._ring(cx, cy, 190),
                self.lines(((cx - 320, cy), (cx + 320, cy)), ((cx, cy - 320), (cx, cy + 320)))], BOX

    # --- notes and checklists -------------------------------------------------

    def build_warning(self):
        tri = self.path(0x25B3)
        x0, y0, x1, y1 = self.bounds(0x25B3)
        cx = (x0 + x1) / 2
        bar = rect(cx - 44, y0 + 210, cx + 44, y0 + 440, r=27)
        dot = rect(cx - 44, y0 + 95, cx + 44, y0 + 175, r=27)
        return [tri, bar, dot], self.advance(0x25B3)

    def build_ballot(self, mark):
        box = self.path(0x25A1)
        bx0, by0, bx1, by1 = self.bounds(0x25A1)
        mx0, my0, mx1, my1 = self.bounds(mark)
        s = 0.62
        cx, cy = (bx0 + bx1) / 2, (by0 + by1) / 2
        t = Transform().translate(cx, cy).scale(s).translate(-(mx0 + mx1) / 2, -(my0 + my1) / 2)
        m = self.path(mark, t)
        # the mark keeps the stroke weight: thicken it back after scaling
        outline = pathops.Path()
        m.draw(outline.getPen())
        outline.stroke(self.STEM * (1 - s), pathops.LineCap.ROUND_CAP, pathops.LineJoin.ROUND_JOIN, 4)
        outline.convertConicsToQuads()
        return [box, op(m, outline, pathops.PathOp.UNION)], self.advance(0x25A1)

    def build_wheelchair(self):
        w = 76
        head = disc(330, 625, 62)
        body = self.lines(((300, 520), (300, 300), (470, 300), (560, 80)), width=w)
        arm = self.lines(((300, 440), (450, 440)), width=w)
        wheel = self.lines(arc(300, 250, 190, 110, 400), width=w)
        return [head, body, arm, wheel], BOX

    def build_script_l(self):
        # a stem with a loop at the top, ending in a small turn to the right
        pts = [(340, 110), (300, 30), (240, 0), (190, 30), (170, 110), (170, 560), (200, 670),
               (260, 705), (320, 670), (330, 590), (290, 470), (170, 330)]
        return [self.lines(pts, width=82)], 420

    def build_degree_letter(self, letter):
        deg = self.path(0x00B0)
        d0, _, d1, _ = self.bounds(0x00B0)
        l0, _, _, _ = self.bounds(letter)
        shift = d1 + 30 - l0
        return [deg, self.path(letter, Transform().translate(shift, 0))], round(shift + self.advance(letter))

    def build_estimated(self):
        # ℮: an e drawn round and open, its bar running through to the right
        cx, cy, r = 360, 330, 280
        bowl = self.lines(arc(cx, cy, r, 0, 315))
        bar = self.lines(((cx - r, cy), (cx + r, cy)))
        return [bowl, bar], 720

    # --- GD&T -----------------------------------------------------------------

    def build_segment(self):
        cx, base, r = BOX / 2, 150, 290
        return [self.lines(arc(cx, base, r, 0, 180), ((cx - r, base), (cx + r, base)))], BOX

    def build_cylindricity(self):
        cx, cy, r = BOX / 2, MID, 165
        ring = self._ring(cx, cy, r)
        a = math.radians(60)
        dx, dy = math.cos(a), math.sin(a)
        nx, ny = -dy, dx
        off = r + 40 + W / 2
        lines = [((cx + s * off * nx - 330 * dx, cy + s * off * ny - 330 * dy),
                  (cx + s * off * nx + 330 * dx, cy + s * off * ny + 330 * dy)) for s in (1, -1)]
        return [ring, self.lines(*lines)], BOX

    def build_total_runout(self):
        head = 110
        def arrow(x0, y0, x1, y1):
            a = math.atan2(y1 - y0, x1 - x0)
            wings = [(x1 - head * math.cos(a + s * math.radians(40)), y1 - head * math.sin(a + s * math.radians(40)))
                     for s in (1, -1)]
            return [((x0, y0), (x1, y1)), (wings[0], (x1, y1), wings[1])]
        lines = arrow(110, 110, 330, 620) + arrow(410, 110, 630, 620) + [((110, 110), (410, 110))]
        return [self.lines(*lines)], BOX

    def build_dimension_origin(self):
        return [self._ring(200, MID, 110), self.lines(((310 + W / 2, MID), (673, MID)))], BOX

    # --- superiors / inferiors --------------------------------------------------

    def _scaled_superior(self, uni):
        # like the superior digits: scale into the box of ², then thicken back
        sx0, sy0, sx1, sy1 = self.bounds(0x00B2)
        dx0, dy0, dx1, dy1 = self.bounds(uni)
        top, bottom = sy1 + 60, sy0 - 60          # parentheses reach past the digits
        scale = (top - bottom) / (dy1 - dy0)
        grow = self.SUP_STROKE - self.STEM * scale
        t = Transform().translate(30, bottom + grow / 2).scale(scale * 1.15, scale - grow / (dy1 - dy0)).translate(-dx0, -dy0)
        p = self.path(uni, t)
        outline = pathops.Path()
        p.draw(outline.getPen())
        outline.stroke(grow, pathops.LineCap.BUTT_CAP, pathops.LineJoin.ROUND_JOIN, 4)
        outline.convertConicsToQuads()
        p = op(p, outline, pathops.PathOp.UNION)
        x0, _, x1, _ = p.bounds
        return p.transform(1, 0, 0, 1, 45 - x0, 0), round(x1 - x0 + 90)

    def build_superior_sign(self, uni):
        p, adv = self._scaled_superior(uni)
        return [p], adv

    def build_superior_equal(self):
        # two bars of ⁻, spaced like the bars of =
        x0, y0, x1, y1 = self.bounds(0x207B)
        cy, h = (y0 + y1) / 2, (y1 - y0) / 2
        gap = 85                      # bars as far apart as the arms of ⁺ reach
        return [rect(x0, cy + gap - h, x1, cy + gap + h, r=40), rect(x0, cy - gap - h, x1, cy - gap + h, r=40)], self.advance(0x207B)

    def build_inferior_of(self, sup):
        _, _, _, den_dy = self._fraction_layout()
        if sup in self.cmap:
            p, adv = self.path(sup), self.advance(sup)
        else:
            parts, adv = self.build(NEW_GLYPHS[sup][1])
            p = self._union(parts)
        return [p.transform(1, 0, 0, 1, 0, den_dy)], adv


if __name__ == "__main__":
    for p in sys.argv[1:]:
        patch_font(p, NEW_GLYPHS, SymbolBuilder)
