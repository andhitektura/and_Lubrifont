# Add the letters needed for Polish, Czech, Slovak, Romanian and Turkish (and
# Lithuanian Ė ė) to and_Lubrifont.
#
# Works like add_extra_glyphs.py (and reuses its machinery): every new glyph
# is constructed from glyphs already in the font, so the script can be run on
# the TrueType source as well as on the CID-keyed release builds.
#
#   acute        Ś ś Ź ź Ĺ ĺ Ŕ ŕ   from É é (ĺ takes the capital accent)
#   caron        Ř ř Ť             from Š š
#   caron (ʼ)    Ď ď Ľ ľ ť          the apostrophe form, from ʼ  (Ď uses Š's caron)
#   breve        Ğ ğ               from Ă ă
#   ring         Ů ů               from Å å
#   dot above    Ż ż Ė ė İ         the dot of i
#   cedilla      Ş ş Ţ ţ           from Ç ç
#   comma below  Ș ș Ț ț           from the comma
#   ogonek       Ą ą Ę ę           drawn in the stroke style of the font
#
# usage: py add_central_european.py font1.ttf [font2.otf ...]
#
# Requires: fonttools, skia-pathops

import sys
import pathops
from fontTools.misc.transform import Transform
from fontTools.pens.transformPen import TransformPen
from add_macedonian_cyrillic import patch_font, bounds_of, draw_contours
from add_extra_glyphs import ExtraBuilder, rect
from diagonal_seven import rounded_polygon

NEW_GLYPHS = {
    # acute
    0x015A: ("Sacute", ("accent", 0x0053, 0x00C9)),
    0x015B: ("sacute", ("accent", 0x0073, 0x00E9)),
    0x0179: ("Zacute", ("accent", 0x005A, 0x00C9)),
    0x017A: ("zacute", ("accent", 0x007A, 0x00E9)),
    0x0139: ("Lacute", ("accent", 0x004C, 0x00C9)),
    0x013A: ("lacute", ("accent", 0x006C, 0x00C9)),
    0x0154: ("Racute", ("accent", 0x0052, 0x00C9)),
    0x0155: ("racute", ("accent", 0x0072, 0x00E9)),
    # caron
    0x0158: ("Rcaron", ("accent", 0x0052, 0x0160)),
    0x0159: ("rcaron", ("accent", 0x0072, 0x0161)),
    0x0164: ("Tcaron", ("accent", 0x0054, 0x0160)),
    0x010E: ("Dcaron", ("accent", 0x0044, 0x0160)),
    0x010F: ("dcaron", ("apostrophe_caron", 0x0064)),
    0x0165: ("tcaron", ("apostrophe_caron", 0x0074)),
    0x013D: ("Lcaron", ("apostrophe_caron", 0x004C)),
    0x013E: ("lcaron", ("apostrophe_caron", 0x006C)),
    # breve, ring
    0x011E: ("Gbreve", ("accent", 0x0047, 0x0102)),
    0x011F: ("gbreve", ("accent", 0x0067, 0x0103)),
    0x016E: ("Uring", ("accent", 0x0055, 0x00C5)),
    0x016F: ("uring", ("accent", 0x0075, 0x00E5)),
    # dot above
    0x017B: ("Zdotaccent", ("dot_above", 0x005A)),
    0x017C: ("zdotaccent", ("dot_above", 0x007A)),
    0x0116: ("Edotaccent", ("dot_above", 0x0045)),
    0x0117: ("edotaccent", ("dot_above", 0x0065)),
    0x0130: ("Idotaccent", ("dot_above", 0x0049)),
    # cedilla
    0x015E: ("Scedilla", ("cedilla", 0x0053, 0x00C7)),
    0x015F: ("scedilla", ("cedilla", 0x0073, 0x00E7)),
    0x0162: ("Tcedilla", ("cedilla", 0x0054, 0x00C7)),
    0x0163: ("tcedilla", ("cedilla", 0x0074, 0x00E7)),
    # comma below
    0x0218: ("Scommaaccent", ("comma_below", 0x0053)),
    0x0219: ("scommaaccent", ("comma_below", 0x0073)),
    0x021A: ("Tcommaaccent", ("comma_below", 0x0054)),
    0x021B: ("tcommaaccent", ("comma_below", 0x0074)),
    # ogonek
    0x0104: ("Aogonek", ("ogonek", 0x0041)),
    0x0105: ("aogonek", ("ogonek", 0x0061)),
    0x0118: ("Eogonek", ("ogonek", 0x0045)),
    0x0119: ("eogonek", ("ogonek", 0x0065)),
}


class CentralEuropeanBuilder(ExtraBuilder):
    def _ink_x(self, path, y, side):
        """leftmost/rightmost ink of a path on row y"""
        x0, _, x1, _ = path.bounds
        xs = [x for x in range(int(x0) - 1, int(x1) + 2) if path.contains((x + 0.5, y))]
        return (min(xs) if side == "left" else max(xs) + 1) if xs else None

    def build_apostrophe_caron(self, uni):
        # the apostrophe-like caron of ď ť ľ Ľ, to the right of the ascender
        base = self.path(uni)
        bx0, by0, bx1, by1 = base.bounds
        ax0, ay0, ax1, ay1 = self.bounds(0x02BC)
        top = 745
        if uni == 0x004C:                       # Ľ: next to the stem
            x = self._ink_x(base, 600, "right") + 30
        elif uni == 0x0074:                     # ť: next to the stem, above the bar
            x = self._ink_x(base, 590, "right") + 25
        else:                                   # ď ľ: after the ascender
            x = bx1 + 25
        mark = self.path(0x02BC, Transform().translate(x - ax0, top - ay1))
        rsb = self.advance(uni) - bx1
        adv = max(self.advance(uni), round(mark.bounds[2] + rsb))
        return [base, mark], adv

    def build_dot_above(self, uni):
        # the dot of i, centred over the letter; above capitals at accent height
        i_contours = self.contours(ord("i"))
        dot = max(i_contours, key=lambda c: bounds_of([c])[1])
        dx0, dy0, dx1, dy1 = bounds_of([dot])
        base = self.path(uni)
        bx0, by0, bx1, by1 = base.bounds
        if by1 > 600:
            caron = [c for c in self.contours(0x0160) if bounds_of([c])[1] > 700]
            dy = bounds_of(caron)[1] - dy0
        else:
            dy = 0
        dx = (bx0 + bx1) / 2 - (dx0 + dx1) / 2
        p = pathops.Path()
        draw_contours([dot], TransformPen(p.getPen(), (1, 0, 0, 1, round(dx), round(dy))))
        return [base, p], self.advance(uni)

    def _below_mark(self, uni, mark):
        base = self.path(uni)
        bx0, by0, bx1, by1 = base.bounds
        # centre under the stem for T/t, under the letter otherwise
        if uni in (0x0054, 0x0074):
            l = self._ink_x(base, 100, "left")
            r = self._ink_x(base, 100, "right")
            cx = (l + r) / 2
        else:
            cx = (bx0 + bx1) / 2
        mx0, my0, mx1, my1 = mark.bounds
        return base, cx - (mx0 + mx1) / 2

    def build_cedilla(self, uni, model):
        # in Ç/ç the cedilla is joined to the letter: take Ç minus C, below
        # the baseline (with a small overlap so it joins the new letter)
        letter = {0x00C7: 0x0043, 0x00E7: 0x0063}[model]
        mark = pathops.op(self.path(model), self.path(letter), pathops.PathOp.DIFFERENCE)
        mark = pathops.op(mark, rect(-500, -400, 1500, 20), pathops.PathOp.INTERSECTION)
        base, dx = self._below_mark(uni, mark)
        return [base, mark.transform(1, 0, 0, 1, round(dx), 0)], self.advance(uni)

    def build_comma_below(self, uni):
        comma = self.path(ord(","))
        cx0, cy0, cx1, cy1 = comma.bounds
        scale = 0.85
        mark = comma.transform(scale, 0, 0, scale, 0, 0)
        mark = mark.transform(1, 0, 0, 1, 0, -60 - mark.bounds[3])
        base, dx = self._below_mark(uni, mark)
        return [base, mark.transform(1, 0, 0, 1, round(dx), 0)], self.advance(uni)

    def build_ogonek(self, uni):
        # a short hook from the bottom right of the letter, turning to the right
        base = self.path(uni)
        right = self._ink_x(base, 20, "right")
        w, depth, foot = 72, 170, 60
        x1 = right
        x0 = x1 - w
        hook = rounded_polygon(
            [(x0, 30), (x1, 30), (x1, -depth + w), (x1 + foot, -depth + w),
             (x1 + foot, -depth), (x0, -depth)],
            [0, 0, 20, 30, 30, 36])
        return [base, hook], self.advance(uni)


if __name__ == "__main__":
    for p in sys.argv[1:]:
        patch_font(p, NEW_GLYPHS, CentralEuropeanBuilder)
