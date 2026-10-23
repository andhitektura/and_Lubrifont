# Add Croatian / Bosnian / Serbian Latin letters, Serbian Cyrillic letters and
# a set of technical symbols to WD-XL Lubrifont.
#
# Works like add_macedonian_cyrillic.py (and reuses its machinery): every new
# glyph is constructed from glyphs already in the font, so the script can be
# run on the TrueType source as well as on the CID-keyed release builds.
#
# usage: py add_extra_glyphs.py font1.ttf [font2.otf ...]
#
# Requires: fonttools, skia-pathops

import sys
import pathops
from fontTools.pens.transformPen import TransformPen
from fontTools.misc.transform import Transform
from add_macedonian_cyrillic import Builder, bounds_of, draw_contours, patch_font

SUPERIOR = {"0": 0x2070, "1": 0x00B9, "2": 0x00B2, "3": 0x00B3, "4": 0x2074,
            "5": 0x2075, "6": 0x2076, "7": 0x2077, "8": 0x2078, "9": 0x2079}

NEW_GLYPHS = {
    # Croatian, Bosnian, Serbian Latin, Slovenian, Montenegrin
    0x0106: ("Cacute", ("accent", 0x0043, 0x00C9)),   # Ć = C + ´
    0x0107: ("cacute", ("accent", 0x0063, 0x00E9)),   # ć = c + ´
    0x010C: ("Ccaron", ("accent", 0x0043, 0x0160)),   # Č = C + ˇ (from Š)
    0x010D: ("ccaron", ("accent", 0x0063, 0x0161)),   # č = c + ˇ (from š)
    0x0110: ("Dcroat", ("copy", 0x00D0)),             # Đ = Ð
    0x0111: ("dcroat", ("dcroat",)),                  # đ = d + bar
    # Serbian Cyrillic
    0x040B: ("Tshecyr", ("tshe",)),                   # Ћ = Т + h body
    0x045B: ("tshecyr", ("tshe_lc",)),                # ћ = h + bar
    0x0402: ("Djecyr", ("dje", 0x040B)),              # Ђ = Ћ with hooked leg
    0x0452: ("djecyr", ("dje", 0x045B)),              # ђ = ћ with hooked leg
    # technical symbols
    0x2300: ("diameter", ("spaced_copy", 0x00D8)),    # ⌀ = Ø
    0x2205: ("emptyset", ("spaced_copy", 0x00D8)),    # ∅ = Ø
    0x2206: ("increment", ("copy", 0x0394)),          # ∆ = Δ
    0x2194: ("arrowboth", ("arrow_both", "x")),      # ↔
    0x2195: ("arrowupdn", ("arrow_both", "y")),      # ↕
    0x2196: ("uni2196", ("rotate", 0x2191, 45)),      # ↖
    0x2197: ("uni2197", ("rotate", 0x2191, -45)),     # ↗
    0x2198: ("uni2198", ("rotate", 0x2193, 45)),      # ↘
    0x2199: ("uni2199", ("rotate", 0x2193, -45)),     # ↙
    0x21D0: ("arrowdblleft", ("dblarrow", "left")),   # ⇐
    0x21D2: ("arrowdblright", ("dblarrow", "right")), # ⇒
    0x21D4: ("arrowdblboth", ("dblarrow", "both")),   # ⇔
    0x2713: ("uni2713", ("stroke", ((130, 380), (290, 190), (610, 640)))),  # ✓
    0x2717: ("uni2717", ("stroke", ((150, 170), (560, 620)), ((150, 620), (560, 170)))),  # ✗
    0x25BC: ("uni25BC", ("mirror", 0x25B2, "y")),     # ▼
    0x25BD: ("uni25BD", ("mirror", 0x25B3, "y")),     # ▽
    # superscripts and subscripts
    0x2070: ("zero.superior", ("superior", "0")),
    0x2075: ("five.superior", ("superior", "5")),
    0x2076: ("six.superior", ("superior", "6")),
    0x2077: ("seven.superior", ("superior", "7")),
    0x2078: ("eight.superior", ("superior", "8")),
    0x2079: ("nine.superior", ("superior", "9")),
    0x207B: ("minus.superior", ("superior_minus",)),       # ⁻ (matches ⁺)
    # fractions
    0x2153: ("onethird", ("fraction", "1", "3")),
    0x2154: ("twothirds", ("fraction", "2", "3")),
    0x215B: ("oneeighth", ("fraction", "1", "8")),
    0x215C: ("threeeighths", ("fraction", "3", "8")),
    0x215D: ("fiveeighths", ("fraction", "5", "8")),
    0x215E: ("seveneighths", ("fraction", "7", "8")),
}
for d in "0123456789":
    NEW_GLYPHS[0x2080 + int(d)] = (f"{'zero one two three four five six seven eight nine'.split()[int(d)]}.inferior",
                                   ("inferior", d))


def rect(x0, y0, x1, y1, r=0):
    """Rectangle (optionally with rounded corners, as drawn in this font)."""
    p = pathops.Path()
    pen = p.getPen()
    if not r:
        pen.moveTo((x0, y0)); pen.lineTo((x0, y1)); pen.lineTo((x1, y1)); pen.lineTo((x1, y0))
    else:
        pen.moveTo((x0, y0 + r))
        pen.lineTo((x0, y1 - r)); pen.qCurveTo((x0, y1), (x0 + r, y1))
        pen.lineTo((x1 - r, y1)); pen.qCurveTo((x1, y1), (x1, y1 - r))
        pen.lineTo((x1, y0 + r)); pen.qCurveTo((x1, y0), (x1 - r, y0))
        pen.lineTo((x0 + r, y0)); pen.qCurveTo((x0, y0), (x0, y0 + r))
    pen.closePath()
    return p


def op(a, b, operator):
    return pathops.op(a, b, operator, fix_winding=True)


class ExtraBuilder(Builder):
    STEM = 91          # vertical stem of capitals / lowercase in this design
    ARROW_STROKE = 88  # stroke of the existing ← ↑ → ↓
    SUP_STROKE = 64    # stroke of the existing ¹ ² ³ ⁴

    def path(self, uni, transform=None):
        p = pathops.Path()
        pen = p.getPen()
        if transform is not None:
            pen = TransformPen(pen, transform)
        draw_contours(self.contours(uni), pen)
        return pathops.simplify(p)

    def bounds(self, uni):
        return bounds_of(self.contours(uni))

    def build(self, recipe):
        kind = recipe[0]
        method = getattr(self, "build_" + kind, None)
        if method is None:
            return super().build(recipe)
        return method(*recipe[1:])

    # --- Latin / Cyrillic ---------------------------------------------------

    def build_dcroat(self):
        # bar across the ascender of d, weight of the crossbar in Ð
        d = self.path(ord("d"))
        xmin, ymin, xmax, ymax = self.bounds(ord("d"))
        stem_x0 = xmax - self.STEM
        bar = rect(stem_x0 - 125, 562, xmax + 35, 642, r=40)
        return [d, bar], self.advance(ord("d")) + 35

    def _h_with_bar_on_top(self):
        # Ћ: the bar of Т on top of an h body whose stem sits under the Т stem
        tx0, _, tx1, _ = self.bounds(0x0422)
        hx0, _, _, _ = self.bounds(ord("h"))
        t_stem_centre = (tx0 + tx1) / 2
        shift = round(t_stem_centre - (hx0 + self.STEM / 2))
        te = self.path(0x0422)
        h = self.path(ord("h"), Transform().translate(shift, 0))
        return [te, h], self.advance(ord("h")) + shift

    def build_tshe(self):
        return self._h_with_bar_on_top()

    def build_tshe_lc(self):
        # ћ: h with a bar through the ascender (Serbian form, like ħ)
        h = self.path(ord("h"))
        hx0, _, _, _ = self.bounds(ord("h"))
        bar = rect(hx0 - 40, 562, hx0 + self.STEM + 140, 642, r=40)
        return [h, bar], self.advance(ord("h"))

    def build_dje(self, tshe_uni):
        # Ђ / ђ: Ћ / ћ with the right leg ending in the hook of ј
        parts, adv = self.build(NEW_GLYPHS[tshe_uni][1])
        body = parts[0]
        for p in parts[1:]:
            body = op(body, p, pathops.PathOp.UNION)
        bx0, by0, bx1, by1 = body.bounds
        leg_x0 = bx1 - self.STEM
        # remove the bottom of the right leg ...
        body = op(body, rect(leg_x0 - 5, by0 - 5, bx1 + 5, 100), pathops.PathOp.DIFFERENCE)
        # ... and replace it with the descender of ј aligned to the leg
        jx0, jy0, jx1, jy1 = self.bounds(0x0458)
        j = self.path(0x0458, Transform().translate(round(bx1 - jx1), 0))
        tail = op(j, rect(bx1 - 400, jy0 - 5, bx1 + 5, 150), pathops.PathOp.INTERSECTION)
        return [body, tail], adv

    # --- symbols ------------------------------------------------------------

    def _centre(self, uni):
        x0, y0, x1, y1 = self.bounds(uni)
        return (x0 + x1) / 2, (y0 + y1) / 2

    def build_mirror(self, uni, axis):
        cx, cy = self._centre(uni)
        t = Transform(-1, 0, 0, 1, 2 * cx, 0) if axis == "x" else Transform(1, 0, 0, -1, 0, 2 * cy)
        return [self.path(uni, t)], self.advance(uni)

    def build_spaced_copy(self, uni):
        # Ø's slash overhangs its advance; give the symbol room on both sides
        x0, _, x1, _ = self.bounds(uni)
        p = self.path(uni)
        return [p], round(x1 + x0)

    # a double-headed arrow needs a longer shaft than the single arrows,
    # otherwise the two heads meet in the middle
    BOTH_EXTRA = 300

    def build_arrow_both(self, axis):
        x0, y0, x1, y1 = self.bounds(0x2192)
        h = self.ARROW_STROKE / 2
        cy = (y0 + y1) / 2
        head = (y1 - y0) / 2 - h
        a, b = x0 + h, x1 - h + self.BOTH_EXTRA
        lines = [((a, cy), (b, cy)),
                 ((a + head, cy + head), (a, cy), (a + head, cy - head)),
                 ((b - head, cy + head), (b, cy), (b - head, cy - head))]
        p = self._stroke(lines, self.ARROW_STROKE)
        if axis == "x":
            return [p], self.advance(0x2192) + self.BOTH_EXTRA
        # vertical: rotate about the centre of the arrow box, keep ↑'s advance
        mx = (a + b) / 2
        ux0, uy0, ux1, uy1 = self.bounds(0x2191)
        t = Transform().translate((ux0 + ux1) / 2, (uy0 + uy1) / 2).rotate(1.5707963267948966).translate(-mx, -cy)
        return [p.transform(*t)], self.advance(0x2191)

    def build_rotate(self, uni, angle):
        import math
        cx, cy = self._centre(uni)
        t = Transform().translate(cx, cy).rotate(math.radians(angle)).translate(-cx, -cy)
        return [self.path(uni, t)], self.advance(uni)

    def _stroke(self, polylines, width):
        p = pathops.Path()
        pen = p.getPen()
        for line in polylines:
            pen.moveTo(line[0])
            for pt in line[1:]:
                pen.lineTo(pt)
            pen.endPath()
        p.stroke(width, pathops.LineCap.ROUND_CAP, pathops.LineJoin.ROUND_JOIN, 4)
        p.convertConicsToQuads()
        return p

    def build_stroke(self, *polylines):
        return [self._stroke(polylines, self.STEM)], 710

    def build_dblarrow(self, direction):
        # same box and stroke as the existing single arrows (→ is 49..701 x 77..645)
        x0, y0, x1, y1 = self.bounds(0x2192)
        w = self.ARROW_STROKE
        h = w / 2
        cy = (y0 + y1) / 2
        gap = 95                           # half distance between the shafts
        head = (y1 - y0) / 2 - h           # reach of the arrow head
        left_tip, right_tip = x0 + h, x1 - h
        lines = []
        if direction == "both":
            right_tip += self.BOTH_EXTRA
        sx0 = left_tip + gap if direction in ("left", "both") else left_tip
        sx1 = right_tip - gap if direction in ("right", "both") else right_tip
        lines += [((sx0, cy + gap), (sx1, cy + gap)), ((sx0, cy - gap), (sx1, cy - gap))]
        if direction in ("right", "both"):
            lines.append(((right_tip - head, cy + head), (right_tip, cy), (right_tip - head, cy - head)))
        if direction in ("left", "both"):
            lines.append(((left_tip + head, cy + head), (left_tip, cy), (left_tip + head, cy - head)))
        return [self._stroke(lines, w)], self.advance(0x2192) + (self.BOTH_EXTRA if direction == "both" else 0)

    # --- superiors, inferiors, fractions -------------------------------------

    def _superior_path(self, digit):
        uni = SUPERIOR[digit]
        if uni in self.cmap:
            return self.path(uni), self.advance(uni)
        # scale the full-size digit into the box of ², then thicken it to the
        # stroke weight of the existing superiors
        sx0, sy0, sx1, sy1 = self.bounds(0x00B2)
        dx0, dy0, dx1, dy1 = self.bounds(ord(digit))
        grow = self.SUP_STROKE - self.STEM * (sy1 - sy0) / (dy1 - dy0)
        scale_x = (sx1 - sx0 - grow) / (dx1 - dx0)
        scale_y = (sy1 - sy0 - grow) / (dy1 - dy0)
        t = Transform().translate(sx0 + grow / 2, sy0 + grow / 2).scale(scale_x, scale_y).translate(-dx0, -dy0)
        p = self.path(ord(digit), t)
        outline = pathops.Path()
        p.draw(outline.getPen())
        outline.stroke(grow, pathops.LineCap.BUTT_CAP, pathops.LineJoin.ROUND_JOIN, 4)
        outline.convertConicsToQuads()
        return op(p, outline, pathops.PathOp.UNION), self.advance(0x00B2)

    def _fraction_layout(self):
        # ½ = ¹ shifted + fraction slash + ² shifted down/right
        contours = self.contours(0x00BD)
        num_x0 = self.bounds(0x00B9)[0]
        slash, denom = None, None
        for c in contours:
            b = bounds_of([c])
            if b[1] > 300:
                num_dx = b[0] - num_x0
            elif b[3] < 400:
                denom = b
            else:
                slash = c
        den_dx = denom[0] - self.bounds(0x00B2)[0]
        den_dy = denom[1] - self.bounds(0x00B2)[1]
        return slash, num_dx, den_dx, den_dy

    def build_superior(self, digit):
        p, adv = self._superior_path(digit)
        return [p], adv

    def build_superior_minus(self):
        # the horizontal arm of the existing ⁺, as a rounded bar
        x0, y0, x1, y1 = self.bounds(0x207A)
        plus = self.path(0x207A)
        x = x0 + (x1 - x0) * 0.15  # clear of the rounded arm end
        ys = [y for y in range(round(y0), round(y1)) if plus.contains((x, y + 0.5))]
        b0, b1 = ys[0], ys[-1] + 1
        r = min(40, (b1 - b0) // 2)
        return [rect(x0, b0, x1, b1, r=r)], self.advance(0x207A)

    def build_inferior(self, digit):
        _, _, _, den_dy = self._fraction_layout()
        p, adv = self._superior_path(digit)
        p = p.transform(1, 0, 0, 1, 0, den_dy)
        return [p], adv

    def build_fraction(self, num, den):
        slash, num_dx, den_dx, den_dy = self._fraction_layout()
        n, _ = self._superior_path(num)
        if num == "1":  # ¹ is narrower; keep the position used in ½ ¼
            n = n.transform(1, 0, 0, 1, num_dx, 0)
        d, _ = self._superior_path(den)
        d = d.transform(1, 0, 0, 1, den_dx, den_dy)
        s = pathops.Path()
        draw_contours([slash], s.getPen())
        return [n, pathops.simplify(s), d], self.advance(0x00BD)


if __name__ == "__main__":
    for p in sys.argv[1:]:
        patch_font(p, NEW_GLYPHS, ExtraBuilder)
