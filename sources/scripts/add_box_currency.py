# Characters added in v2.604:
#
#   ẞ            capital sharp s (German capitals: STRAẞE)
#   ₽ ₴ ₸ ₺ ₿ ₹  rouble, hryvnia, tenge, Turkish lira, bitcoin, rupee
#   U+2500-257F  box drawing: the 92 the CJK fonts already have, now also in
#                the Latin / Cyrillic / Greek edition, plus the 36 double
#                lines, arcs and diagonals that were missing
#   U+2580-259F  block elements and shades
#
# Every glyph is built from the font's own letters and strokes (P, B, T, L,
# S, ß and the 80-unit bars of ¥), the box drawings on the grid of the
# existing ones (box_drawing.py). Glyphs already in a font are skipped, so the
# script can be re-run safely.
#
# usage: py add_box_currency.py font1.otf [font2.ttf ...]
#        (run on the CJK fonts and the Regular, then make_weights.py,
#        make_italics.py and autohint.py)
#
# Requires: fonttools, skia-pathops

import sys
import pathops
from fontTools.misc.transform import Transform
from add_macedonian_cyrillic import patch_font, bounds_of
from add_extra_glyphs import rect, op
from add_technical_symbols import SymbolBuilder
import box_drawing

BAR = 80          # currency bars, as in ¥
STEM = 91

NEW_GLYPHS = {
    0x1E9E: ("Germandbls", ("sharp_s_cap",)),
    0x20BD: ("ruble", ("ruble",)),
    0x20B4: ("hryvnia", ("hryvnia",)),
    0x20B8: ("tenge", ("tenge",)),
    0x20BA: ("lira", ("lira",)),
    0x20BF: ("bitcoin", ("bitcoin",)),
    0x20B9: ("rupeeindian", ("rupee",)),
}
for u in range(0x2500, 0x2580):
    NEW_GLYPHS[u] = (f"uni{u:04X}", ("box", u))
for u in range(0x2580, 0x25A0):
    NEW_GLYPHS[u] = (f"uni{u:04X}", ("block", u))


def bar(x0, x1, cy, h=BAR):
    return rect(x0, cy - h / 2, x1, cy + h / 2, r=h / 2)


class CurrencyBuilder(SymbolBuilder):

    def clip(self, path, x0, y0, x1, y1):
        return op(path, rect(x0, y0, x1, y1), pathops.PathOp.INTERSECTION)

    def build_box(self, uni):
        return box_drawing.box_glyph(uni)

    def build_block(self, uni):
        return box_drawing.block_glyph(uni)

    # --- ẞ ------------------------------------------------------------------

    def build_sharp_s_cap(self):
        # stem and flat top of B, a straight diagonal from the top right down
        # to the middle bar, and the lower bowl of ß (its bottom part, with
        # the bottom-right corner mirrored up to the middle bar)
        ss = self.path(0x00DF)
        x0, y0, x1, y1 = self.bounds(0x00DF)            # 62 -9 484 709
        top, mid_top, mid_bot = y1, 392, 301
        lower = self.clip(ss, 180, y0 - 10, x1 + 10, 150)
        mirror = lower.transform(1, 0, 0, -1, 0, y0 + mid_top)
        right = rect(x1 - STEM - (x1 - 394 - STEM), 140, x1, 250)
        stem = rect(x0, y0, x0 + STEM, top, r=40)
        diag_end = (240, (mid_top + mid_bot) / 2)
        upper = self.lines([(x0 + STEM / 2, top - STEM / 2), (418, top - STEM / 2), diag_end], width=STEM)
        upper = self.clip(upper, x0, y0, x1, top)
        return [stem, upper, lower, mirror, right], self.advance(0x00DF)

    # --- currency -----------------------------------------------------------

    def build_ruble(self):
        # P moved right, with a bar through the stem below the bowl
        x0, y0, x1, y1 = self.bounds(ord("P"))
        dx = 40
        p = self.path(ord("P"), Transform().translate(dx, 0))
        return [p, bar(x0 + dx - 70, x0 + dx + 260, 175)], self.advance(ord("P")) + dx

    def build_hryvnia(self):
        # a reversed S with a diagonal spine (the S of this font has a
        # horizontal one, which the bars would hide), crossed by two bars
        x0, y0, x1, y1 = self.bounds(ord("S"))
        adv = self.advance(ord("S"))
        h = STEM / 2
        l, r, t, b = x0 + h, x1 - h, y1 - h, y0 + h
        s = self.lines([(l, 590), (l, t), (r, t), (r, 480), (l, 240), (l, b), (r, b), (r, 120)], width=STEM)
        return [s, bar(x0 - 30, x1 + 30, 300, 70), bar(x0 - 30, x1 + 30, 420, 70)], adv

    def build_tenge(self):
        # two bars of T, the stem hanging from the lower one
        x0, y0, x1, y1 = self.bounds(ord("T"))
        t = self.path(ord("T"))
        top_bar = self.clip(t, x0 - 5, y1 - STEM, x1 + 5, y1 + 5)
        gap = 75
        second = top_bar.transform(1, 0, 0, 1, 0, -(STEM + gap))
        stem = self.clip(t, x0 - 5, y0 - 5, x1 + 5, y1 - STEM - gap)
        return [top_bar, second, stem], self.advance(ord("T"))

    def build_lira(self):
        # the stem of L with its foot turned up into an arc, crossed by two
        # rising bars
        x0, y0, x1, y1 = self.bounds(ord("L"))
        sx = x0 + 70                                  # room for the bars on the left
        stem = rect(sx, y0, sx + STEM, y1, r=40)
        foot = self.lines([(sx + STEM / 2, y0 + STEM / 2), (x1 + 10 - STEM / 2, y0 + STEM / 2),
                           (x1 + 10 - STEM / 2, 260)], width=STEM)
        foot = self.clip(foot, sx, y0, x1 + 20, 400)
        bars = [self.lines([(x0 - 20, y), (sx + STEM + 130, y + 95)], width=BAR) for y in (300, 450)]
        return [stem, foot] + bars, self.advance(ord("L")) + 20

    def build_bitcoin(self):
        # B with two strokes through the top and bottom
        x0, y0, x1, y1 = self.bounds(ord("B"))
        b = self.path(ord("B"))
        w = 60
        strokes = []
        for cx in (x0 + 75, x0 + 215):
            strokes.append(rect(cx - w / 2, y1 - 40, cx + w / 2, y1 + 90, r=w / 2))
            strokes.append(rect(cx - w / 2, y0 - 90, cx + w / 2, y0 + 40, r=w / 2))
        return [b] + strokes, self.advance(ord("B"))

    def build_rupee(self):
        # two bars on top, a bowl closing at the middle and the leg of R
        x0, y0, x1, y1 = self.bounds(ord("P"))
        left, right = 40, 450
        top = y1
        bars = [rect(left, top - BAR, right, top, r=40), rect(left, 470, right, 470 + BAR, r=40)]
        bowl = self.lines([(300, top - BAR / 2), (300, 330), (left + BAR / 2, 330)], width=STEM)
        bowl = self.clip(bowl, left, 240, right, top - BAR / 2)
        leg = self.lines([(left + 60, 330), (right - 30, y0 + 40)], width=STEM + 10)
        leg = self.clip(leg, left, y0, right + 40, 330)
        return bars + [bowl, leg], 490


if __name__ == "__main__":
    for p in sys.argv[1:]:
        patch_font(p, NEW_GLYPHS, CurrencyBuilder)
