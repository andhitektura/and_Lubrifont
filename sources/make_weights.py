# Build the Light and Bold weights of and_Lubrifont from the Regular of the
# light Latin / Cyrillic / Greek edition.
#
# Every outline is offset by OFFSET units on each edge: negative erodes
# (Light, strokes 92 -> 74), positive grows (Bold). SPACE units are then added
# to both sidebearings of every spacing glyph, so a Bold's letters widen by what
# their strokes gained and the gaps between letters stay as in the Regular.
# Kerning is kept; accent anchors move with the outlines.
#
# Offsetting also moves the outer edges, so the outlines are then stretched
# vertically, zone by zone, back onto the Regular's descender, baseline,
# x-height and cap height (zones()). Shapes above the caps (accents, brackets)
# are only shifted, so their gap to the letter stays as it was.
#
# Light installs as its own family "and_Lubrifont Light"; Bold is style-linked
# to the Regular, so an application's Bold button picks it up.
#
# usage: py make_weights.py   (run after make_latin_cyrillic.py;
#                              writes ../fonts/Latin-Cyrillic/andLubrifont-{Light,Bold}.*)
#
# Requires: fonttools, skia-pathops

import os
import pathops
from fontTools.ttLib import TTFont
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib.tables import otTables

HERE = os.path.dirname(os.path.abspath(__file__))
DIR = os.path.join(HERE, "..", "fonts", "Latin-Cyrillic")

FAMILY = "and_Lubrifont"
STEM = 92                # Regular stroke
WEIGHTS = {
    # style: offset per edge, extra sidebearing per side, usWeightClass
    "Light": dict(offset=-9, space=0, weight=300),     # stroke 74
    "Bold": dict(offset=12, space=12, weight=700),     # stroke 116
}


def zones(offset):
    """(offset y, target y) pairs: outer edges land back on the Regular's
    descender, baseline, x-height and cap height"""
    o = offset
    return [(-3000, -3000), (-220 - o, -220), (-9 - o, -9),
            (485 + o, 485), (710 + o, 710), (780, 780), (3000, 3000)]


def map_y(y, knots):
    for (e0, t0), (e1, t1) in zip(knots, knots[1:]):
        if y <= e1:
            return t0 + (y - e0) * (t1 - t0) / (e1 - e0)
    return y


class ZonePen:
    """moves every point by dx and maps its y through the zones (the outlines
    are almost all straight lines and quarter-round corners, so mapping the
    points is exact enough)"""
    def __init__(self, out, knots, dx=0):
        self.out, self.knots, self.dx = out, knots, dx

    def _map(self, pts):
        return [None if p is None else (p[0] + self.dx, map_y(p[1], self.knots)) for p in pts]

    def moveTo(self, pt): self.out.moveTo(*self._map([pt]))
    def lineTo(self, pt): self.out.lineTo(*self._map([pt]))
    def curveTo(self, *pts): self.out.curveTo(*self._map(pts))
    def qCurveTo(self, *pts): self.out.qCurveTo(*self._map(pts))
    def closePath(self): self.out.closePath()
    def endPath(self): self.out.endPath()


SPECK = 15   # к ж ќ κ carry 1-unit leftover contours that the Bold would enlarge


def _contours(glyph):
    p = pathops.Path()
    glyph.draw(p.getPen())
    return list(p.contours)


def offset_path(glyph, offset, clockwise=False):
    p = pathops.Path()
    pen = p.getPen()
    for contour in _contours(glyph):
        x0, y0, x1, y1 = contour.bounds
        if max(x1 - x0, y1 - y0) >= SPECK:
            contour.draw(pen)
    if p.bounds == (0, 0, 0, 0):
        return None
    p = pathops.simplify(p)
    edge = pathops.Path()
    p.draw(edge.getPen())
    edge.stroke(2 * abs(offset), pathops.LineCap.BUTT_CAP, pathops.LineJoin.MITER_JOIN, 4)
    edge.convertConicsToQuads()
    op = pathops.PathOp.UNION if offset > 0 else pathops.PathOp.DIFFERENCE
    return pathops.op(p, edge, op, clockwise=clockwise)


def shift_anchors(font, shifts):
    seen = set()
    for lookup in font["GPOS"].table.LookupList.Lookup:
        for st in lookup.SubTable:
            st = getattr(st, "ExtSubTable", st)
            if id(st) in seen or not isinstance(st, otTables.MarkBasePos):
                continue
            seen.add(id(st))
            for name, record in zip(st.BaseCoverage.glyphs, st.BaseArray.BaseRecord):
                if name in shifts:
                    for anchor in record.BaseAnchor:
                        if anchor is not None:
                            anchor.XCoordinate += shifts[name]


def rename(font, style, weight):
    ps_name = f"andLubrifont-{style}"
    version = f"Version {font['head'].fontRevision:.3f}"
    if style == "Bold":                 # style-linked to the Regular
        names = {1: FAMILY, 2: "Bold"}
    else:                               # its own family
        names = {1: f"{FAMILY} {style}", 2: "Regular", 16: FAMILY, 17: style}
    names.update({3: f"{version[8:]};NFSL;{ps_name}", 4: f"{FAMILY} {style}", 6: ps_name})
    table = font["name"]
    table.names = [r for r in table.names if r.nameID not in (1, 2, 3, 4, 6, 16, 17)]
    for nid, text in names.items():
        table.setName(text, nid, 3, 1, 0x409)
        if nid in (1, 2, 3, 4, 6):
            table.setName(text, nid, 1, 0, 0)
    os2 = font["OS/2"]
    os2.usWeightClass = weight
    bold = style == "Bold"
    os2.fsSelection = (os2.fsSelection & ~0b1100001) | (1 << 5 if bold else 1 << 6)
    font["head"].macStyle = 1 if bold else 0
    if "CFF " in font:
        cff = font["CFF "].cff
        cff.fontNames = [ps_name]
        top = cff.topDictIndex[0]
        top.FullName = f"{FAMILY} {style}"
        top.FamilyName = FAMILY
        top.Weight = style
        for fd in getattr(top, "FDArray", []):
            fd.FontName = ps_name


def build(src, dst, style, offset, space, weight):
    font = TTFont(src)
    gs = font.getGlyphSet()
    knots = zones(offset)
    cff = font["CFF "].cff if "CFF " in font else None
    shifts = {}
    for name in font.getGlyphOrder():
        adv = font["hmtx"][name][0]
        dx = space if adv else 0        # combining marks keep zero width
        new_adv = adv + 2 * dx
        shifts[name] = dx
        path = offset_path(gs[name], offset, clockwise=cff is None)   # TrueType: outer contours clockwise
        if cff:
            cs = cff.topDictIndex[0].CharStrings
            private = cs[name].private
            width = None if new_adv == private.defaultWidthX else new_adv - private.nominalWidthX
            pen = T2CharStringPen(width, None)
            if path is not None:
                path.draw(ZonePen(pen, knots, dx))
            cs.charStringsIndex[cs.charStrings[name]] = pen.getCharString(
                private=private, globalSubrs=cff.GlobalSubrs)
            b = BoundsPen(None)
            if path is not None:
                path.draw(ZonePen(b, knots, dx))
            font["hmtx"][name] = (new_adv, round(b.bounds[0]) if b.bounds else 0)
        else:
            glyf = font["glyf"]
            if path is not None:
                pen = TTGlyphPen(None)
                path.draw(ZonePen(Cu2QuPen(pen, 1.0, reverse_direction=False), knots, dx))
                glyf[name] = pen.glyph()
                glyf[name].recalcBounds(glyf)
            glyph = glyf[name]
            # lsb must equal xMin
            font["hmtx"][name] = (new_adv, glyph.xMin if glyph.numberOfContours else 0)
    if space:
        shift_anchors(font, shifts)
    if cff:
        top = cff.topDictIndex[0]
        for fd in getattr(top, "FDArray", [top]):
            priv = fd.Private
            if hasattr(priv, "StdVW"):
                priv.StdVW = STEM + 2 * offset
            if hasattr(priv, "StemSnapV"):
                priv.StemSnapV = [STEM + 2 * offset]
    font["OS/2"].recalcAvgCharWidth(font)
    rename(font, style, weight)
    font.save(dst)
    print(f"{dst}: {os.path.getsize(dst) // 1024} KB")


if __name__ == "__main__":
    for style, params in WEIGHTS.items():
        for ext in ("otf", "ttf"):
            build(os.path.join(DIR, f"andLubrifont-Regular.{ext}"),
                  os.path.join(DIR, f"andLubrifont-{style}.{ext}"), style, **params)
