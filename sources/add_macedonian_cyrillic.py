# Add the Cyrillic letters required for Macedonian (plus the stressed
# Ѐ ѐ Ѝ ѝ used in Macedonian/Serbian/Bulgarian) to WD-XL Lubrifont.
#
# All new glyphs are constructed from glyphs already present in each font,
# so the same script works on the TrueType sources (named glyphs) as well as
# on the CID-keyed OTF / TTF release builds (new CIDs are appended at the end,
# existing CIDs and OpenType features are left untouched).
#
# usage: py add_macedonian_cyrillic.py font1.ttf [font2.otf ...]
#
# Requires: fonttools, skia-pathops

import sys
import pathops
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.t2CharStringPen import T2CharStringPen

# unicode: (production name, recipe)
#   ("copy", base)                     identical outline (Latin lookalikes)
#   ("accent", base, accented_latin)   base + accent taken from accented_latin
#   ("ligature", left, right)          left + right (Ь bowl) sharing the stem
#   ("dzhe", pe, tse)                  flipped П + centred descender from Ц
NEW_GLYPHS = {
    0x0403: ("Gjecyr", ("accent", 0x0413, 0x00C9)),   # Ѓ = Г + ´
    0x0453: ("gjecyr", ("accent", 0x0433, 0x00E9)),   # ѓ = г + ´
    0x0405: ("Dzecyr", ("copy", 0x0053)),             # Ѕ = S
    0x0455: ("dzecyr", ("copy", 0x0073)),             # ѕ = s
    0x0408: ("Jecyr", ("copy", 0x004A)),              # Ј = J
    0x0458: ("jecyr", ("copy", 0x006A)),              # ј = j
    0x0409: ("Ljecyr", ("ligature", 0x041B, 0x042C)), # Љ = Л + Ь
    0x0459: ("ljecyr", ("ligature", 0x043B, 0x044C)), # љ = л + ь
    0x040A: ("Njecyr", ("ligature", 0x041D, 0x042C)), # Њ = Н + Ь
    0x045A: ("njecyr", ("ligature", 0x043D, 0x044C)), # њ = н + ь
    0x040C: ("Kjecyr", ("accent", 0x041A, 0x00C9)),   # Ќ = К + ´
    0x045C: ("kjecyr", ("accent", 0x043A, 0x00E9)),   # ќ = к + ´
    0x040F: ("Dzhecyr", ("dzhe", 0x041F, 0x0426)),    # Џ
    0x045F: ("dzhecyr", ("dzhe", 0x043F, 0x0446)),    # џ
    0x0400: ("Iegravecyr", ("accent", 0x0415, 0x00C8)), # Ѐ = Е + `
    0x0450: ("iegravecyr", ("accent", 0x0435, 0x00E8)), # ѐ = е + `
    0x040D: ("Igravecyr", ("accent", 0x0418, 0x00C8)),  # Ѝ = И + `
    0x045D: ("igravecyr", ("accent", 0x0438, 0x00E8)),  # ѝ = и + `
}


def split_contours(rec):
    """Split a RecordingPen value list into a list of contours."""
    contours, cur = [], []
    for op, args in rec:
        cur.append((op, args))
        if op in ("closePath", "endPath"):
            contours.append(cur)
            cur = []
    return contours


def contour_bounds(contour):
    bp = BoundsPen(None)
    for op, args in contour:
        getattr(bp, op)(*args)
    return bp.bounds


def draw_contours(contours, pen):
    for contour in contours:
        for op, args in contour:
            getattr(pen, op)(*args)


def bounds_of(contours):
    bp = BoundsPen(None)
    draw_contours(contours, bp)
    return bp.bounds


class Builder:
    def __init__(self, font):
        self.font = font
        self.cmap = font.getBestCmap()
        self.glyphset = font.getGlyphSet()
        self.hmtx = font["hmtx"]

    def name(self, uni):
        return self.cmap[uni]

    def contours(self, uni):
        rec = RecordingPen()
        self.glyphset[self.name(uni)].draw(rec)
        return split_contours(rec.value)

    def advance(self, uni):
        return self.hmtx[self.name(uni)][0]

    def build(self, recipe):
        """Return (list of pathops.Path parts to be unioned, advance width)."""
        kind = recipe[0]
        if kind == "copy":
            path = pathops.Path()
            draw_contours(self.contours(recipe[1]), path.getPen())
            return [path], self.advance(recipe[1])

        if kind == "accent":
            base, accented = recipe[1], recipe[2]
            base_contours = self.contours(base)
            base_top = bounds_of(base_contours)[3]
            # accent = contours of the accented Latin glyph that sit above the
            # letter body; the remainder is its base letter
            acc_contours, body_contours = [], []
            for c in self.contours(accented):
                (acc_contours if contour_bounds(c)[1] > base_top else body_contours).append(c)
            body = bounds_of(body_contours)
            acc = bounds_of(acc_contours)
            target = bounds_of(base_contours)
            # keep the accent's offset from the body centre of the Latin model
            dx = (target[0] + target[2]) / 2 - (body[0] + body[2]) / 2
            base_path, acc_path = pathops.Path(), pathops.Path()
            draw_contours(base_contours, base_path.getPen())
            draw_contours(acc_contours, TransformPen(acc_path.getPen(), (1, 0, 0, 1, round(dx), 0)))
            return [base_path, acc_path], self.advance(base)

        if kind == "ligature":
            left, right = recipe[1], recipe[2]
            left_contours = self.contours(left)
            right_contours = self.contours(right)
            # the right stem of the left letter becomes the stem of Ь
            left_xmax = bounds_of(left_contours)[2]
            right_xmin = bounds_of(right_contours)[0]
            stem = self._stem_width(right_contours, right_xmin)
            shift = round(left_xmax - stem - right_xmin)
            left_path, right_path = pathops.Path(), pathops.Path()
            draw_contours(left_contours, left_path.getPen())
            draw_contours(right_contours, TransformPen(right_path.getPen(), (1, 0, 0, 1, shift, 0)))
            return [left_path, right_path], shift + self.advance(right)

        if kind == "dzhe":
            pe, tse = recipe[1], recipe[2]
            pe_contours = self.contours(pe)
            xmin, ymin, xmax, ymax = bounds_of(pe_contours)
            # flip П vertically within its own bbox -> stems on top, bar at base
            flipped = pathops.Path()
            draw_contours(pe_contours, TransformPen(flipped.getPen(), (1, 0, 0, -1, 0, ymin + ymax)))
            # descender of Ц: the contour part below the baseline bar
            tse_contours = self.contours(tse)
            t_bounds = bounds_of(tse_contours)
            desc_bottom = t_bounds[1]
            stem = self._stem_width(tse_contours, t_bounds[0])
            radius = 40
            cx = (xmin + xmax) / 2
            x0, x1 = round(cx - stem / 2), round(cx - stem / 2) + stem
            top = ymin + radius  # overlap into the bar, removed by union
            descender = pathops.Path()
            pen = descender.getPen()
            pen.moveTo((x0, top))
            pen.lineTo((x0, desc_bottom + radius))
            pen.qCurveTo((x0, desc_bottom), (x0 + radius, desc_bottom))
            pen.lineTo((x1 - radius, desc_bottom))
            pen.qCurveTo((x1, desc_bottom), (x1, desc_bottom + radius))
            pen.lineTo((x1, top))
            pen.closePath()
            return [flipped, descender], self.advance(pe)

        raise ValueError(kind)

    @staticmethod
    def _stem_width(contours, x_left):
        """Width of the left vertical stem, measured at 3/4 of the glyph
        height (above the bowl of Ь and the bar of Ц)."""
        xmin, ymin, xmax, ymax = bounds_of(contours)
        mid = ymin + (ymax - ymin) * 0.75
        # cast a horizontal ray through the glyph and take the first run
        p = pathops.Path()
        draw_contours(contours, p.getPen())
        x = x_left
        while p.contains((x + 0.5, mid)) and x < xmax:
            x += 1
        return round(x - x_left)


def _ymax(glyph):
    bp = BoundsPen(None)
    glyph.draw(bp)
    return bp.bounds[3]


def finalize(parts, clockwise):
    """Union the parts (each normalised on its own, so contour directions
    cannot cancel out) and return a RecordingPen with the result."""
    path = pathops.simplify(parts[0], clockwise=clockwise)
    for part in parts[1:]:
        path = pathops.op(path, pathops.simplify(part, clockwise=clockwise),
                          pathops.PathOp.UNION, clockwise=clockwise)
    path = pathops.simplify(path, keep_starting_points=False, clockwise=clockwise)
    rec = RecordingPen()
    path.draw(rec)
    return rec


def patch_font(path_in, new_glyphs=NEW_GLYPHS, builder_class=Builder):
    font = TTFont(path_in, lazy=False)
    cmap = font.getBestCmap()
    todo = {u: v for u, v in new_glyphs.items() if u not in cmap}
    if not todo:
        print(f"{path_in}: nothing to add")
        return
    builder = builder_class(font)
    is_cff = "CFF " in font
    is_cid = is_cff and hasattr(font["CFF "].cff.topDictIndex[0], "ROS")
    if not is_cff:
        is_cid = font.getGlyphOrder()[-1].startswith("cid")
    order = list(font.getGlyphOrder())

    built = {}
    for uni, (prod_name, recipe) in sorted(todo.items()):
        p, adv = builder.build(recipe)
        # TrueType: clockwise outer contours; CFF: counter-clockwise
        built[uni] = (prod_name, finalize(p, clockwise=not is_cff), adv)

    if is_cff:
        cff = font["CFF "].cff
        td = cff.topDictIndex[0]
        cs = td.CharStrings
    else:
        glyf = font["glyf"]

    if "vmtx" in font:
        # vertical origin as used by the existing Cyrillic (reference: А)
        ref = cmap[0x0410]
        vadvance, ref_tsb = font["vmtx"][ref]
        vorigin = ref_tsb + _ymax(builder.glyphset[ref])

    new_names = {}
    for uni, (prod_name, rec, adv) in sorted(built.items()):
        gname = f"cid{len(order):05d}" if is_cid else prod_name
        assert gname not in order, gname
        new_names[uni] = gname
        bp = BoundsPen(None)
        rec.replay(bp)
        xmin, ymin, xmax, ymax = (round(v) for v in bp.bounds)

        if is_cff:
            private = td.FDArray[0].Private if is_cid else td.Private
            width = None if adv == private.defaultWidthX else adv - private.nominalWidthX
            pen = T2CharStringPen(width, None)
            rec.replay(pen)
            charstring = pen.getCharString(private=private, globalSubrs=cff.GlobalSubrs)
            cs.charStringsIndex.append(charstring)
            cs.charStrings[gname] = len(cs.charStringsIndex) - 1
            td.charset.append(gname)
            if is_cid:
                td.FDSelect.gidArray.append(0)
        else:
            pen = TTGlyphPen(None)
            rec.replay(Cu2QuPen(pen, max_err=1.0, reverse_direction=False))
            glyf[gname] = pen.glyph()

        order.append(gname)
        font["hmtx"][gname] = (adv, xmin)
        if "vmtx" in font:
            font["vmtx"][gname] = (vadvance, vorigin - ymax)
        for table in font["cmap"].tables:
            if table.isUnicode():
                if table.format == 4 and uni > 0xFFFF:
                    continue
                table.cmap[uni] = gname
        if "GDEF" in font and font["GDEF"].table.GlyphClassDef:
            font["GDEF"].table.GlyphClassDef.classDefs[gname] = 1

    font.setGlyphOrder(order)
    if is_cff:
        if is_cid:
            td.CIDCount = len(order)
        td.charset = order
    else:
        glyf.glyphOrder = order
    if "post" in font and font["post"].formatType == 2.0:
        font["post"].extraNames = []
    font["maxp"].numGlyphs = len(order)
    font.save(path_in)
    print(f"{path_in}: added " + " ".join(f"{chr(u)}={n}" for u, n in sorted(new_names.items())))


if __name__ == "__main__":
    for p in sys.argv[1:]:
        patch_font(p)
