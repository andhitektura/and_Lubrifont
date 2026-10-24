# Build the italics of and_Lubrifont from the three upright weights:
# Light Italic, Italic and Bold Italic.
#
# The italic is an oblique: every outline is slanted by ANGLE degrees, with
# the upright letter shapes kept (also in Cyrillic, so it suits every
# language). The slant pivots at half the x-height, so each letter stays
# centred in its unchanged advance width; kerning is kept and accent anchors
# are slanted with the outlines.
#
# Finally all six fonts get a STAT table (weight and italic axes), so
# applications can group them as one family.
#
# Naming follows the uprights: Italic and Bold Italic are style-linked to the
# Regular ("and_Lubrifont"), so an application's italic button picks them up;
# Light Italic belongs to "and_Lubrifont Light".
#
# usage: py make_italics.py   (run after make_weights.py, then autohint.py
#                              on all six .ttf)
#
# Requires: fonttools

import math
import os
from fontTools.ttLib import TTFont
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.otlLib.builder import buildStatTable
from autohint import dehint

HERE = os.path.dirname(os.path.abspath(__file__))
DIR = os.path.join(HERE, "..", "..", "fonts", "and_Lubrifont")

FAMILY = "and_Lubrifont"
ANGLE = 9
X_HEIGHT = 485
SLANT = math.tan(math.radians(ANGLE))
SHIFT = -SLANT * X_HEIGHT / 2          # pivot at half the x-height

STYLES = {
    # upright: (italic style name, family, subfamily, typographic family/subfamily or None)
    "Light": ("LightItalic", f"{FAMILY} Light", "Italic", (FAMILY, "Light Italic")),
    "Regular": ("Italic", FAMILY, "Italic", None),
    "Bold": ("BoldItalic", FAMILY, "Bold Italic", None),
}


def slant(x, y):
    return x + SLANT * y + SHIFT, y


def slant_outlines(font):
    gs = font.getGlyphSet()
    matrix = (1, 0, SLANT, 1, SHIFT, 0)
    if "CFF " in font:
        cff = font["CFF "].cff
        cs = cff.topDictIndex[0].CharStrings
        new = {}
        for name in font.getGlyphOrder():
            rec = DecomposingRecordingPen(gs)
            gs[name].draw(rec)
            private = cs[name].private
            adv = font["hmtx"][name][0]
            width = None if adv == private.defaultWidthX else adv - private.nominalWidthX
            pen = T2CharStringPen(width, None)
            rec.replay(TransformPen(pen, matrix))
            new[name] = pen.getCharString(private=private, globalSubrs=cff.GlobalSubrs)
        for name, charstring in new.items():
            cs.charStringsIndex[cs.charStrings[name]] = charstring
        for name in font.getGlyphOrder():
            bounds = cs[name].calcBounds(cs)
            font["hmtx"][name] = (font["hmtx"][name][0], round(bounds[0]) if bounds else 0)
    else:
        glyf = font["glyf"]
        new = {}
        for name in font.getGlyphOrder():
            rec = DecomposingRecordingPen(gs)
            gs[name].draw(rec)
            pen = TTGlyphPen(None)
            rec.replay(TransformPen(pen, matrix))
            new[name] = pen.glyph()
        for name, glyph in new.items():
            glyf[name] = glyph
            glyph.recalcBounds(glyf)
            font["hmtx"][name] = (font["hmtx"][name][0], glyph.xMin if glyph.numberOfContours else 0)


def slant_anchor(anchor):
    if anchor is not None:
        x, y = slant(anchor.XCoordinate, anchor.YCoordinate)
        anchor.XCoordinate = round(x)


def slant_anchors(font):
    for lookup in font["GPOS"].table.LookupList.Lookup:
        for st in lookup.SubTable:
            if lookup.LookupType == 9:
                st = st.ExtSubTable
            kind = type(st).__name__
            if kind in ("MarkBasePos", "MarkLigPos"):
                for rec in st.MarkArray.MarkRecord:
                    slant_anchor(rec.MarkAnchor)
            if kind == "MarkBasePos":
                for rec in st.BaseArray.BaseRecord:
                    for a in rec.BaseAnchor:
                        slant_anchor(a)
            elif kind == "MarkMarkPos":
                for rec in st.Mark1Array.MarkRecord:
                    slant_anchor(rec.MarkAnchor)
                for rec in st.Mark2Array.Mark2Record:
                    for a in rec.Mark2Anchor:
                        slant_anchor(a)
            elif kind == "MarkLigPos":
                for lig in st.LigatureArray.LigatureAttach:
                    for comp in lig.ComponentRecord:
                        for a in comp.LigatureAnchor:
                            slant_anchor(a)
            elif kind == "CursivePos":
                for rec in st.EntryExitRecord:
                    slant_anchor(rec.EntryAnchor)
                    slant_anchor(rec.ExitAnchor)


def rename(font, upright):
    ps_style, family, sub, typo = STYLES[upright]
    ps_name = f"andLubrifont-{ps_style}"
    full = f"{FAMILY} {'Italic' if upright == 'Regular' else upright + ' Italic'}"
    version = f"{font['head'].fontRevision:.3f}"
    names = {1: family, 2: sub, 3: f"{version};ANDs;{ps_name}", 4: full, 6: ps_name}
    if typo:
        names.update({16: typo[0], 17: typo[1]})
    table = font["name"]
    table.names = [r for r in table.names if r.nameID not in (1, 2, 3, 4, 6, 16, 17)]
    for nid, text in names.items():
        table.setName(text, nid, 3, 1, 0x409)
    os2 = font["OS/2"]
    bold = upright == "Bold"
    os2.fsSelection = (os2.fsSelection & ~0b1100001) | 1 | (1 << 5 if bold else 0)
    font["head"].macStyle = (1 if bold else 0) | 2
    font["post"].italicAngle = -ANGLE
    hhea = font["hhea"]
    hhea.caretSlopeRise, hhea.caretSlopeRun = 1000, round(1000 * SLANT)
    if "CFF " in font:
        cff = font["CFF "].cff
        cff.fontNames = [ps_name]
        top = cff.topDictIndex[0]
        top.FullName = full
        top.ItalicAngle = -ANGLE
        for fd in getattr(top, "FDArray", []):
            fd.FontName = ps_name
    return ps_name


WEIGHT_VALUES = {
    "Light": dict(value=300, name="Light"),
    "Regular": dict(value=400, name="Regular", flags=0x2, linkedValue=700),
    "Bold": dict(value=700, name="Bold"),
}
ITAL_VALUES = [dict(value=0, name="Roman", flags=0x2, linkedValue=1), dict(value=1, name="Italic")]


def add_stat(path, upright, italic):
    """STAT with the axis values of this font only (as for static fonts)."""
    font = TTFont(path)
    # drop an earlier STAT and its names (IDs 256+), and any Mac name records
    if "STAT" in font:
        del font["STAT"]
    font["name"].names = [r for r in font["name"].names
                          if r.platformID == 3 and r.nameID < 256]
    axes = [dict(tag="wght", name="Weight", values=[WEIGHT_VALUES[upright]]),
            dict(tag="ital", name="Italic", values=[ITAL_VALUES[italic]])]
    buildStatTable(font, axes, elidedFallbackName="Regular", macNames=False)
    font.save(path)


def build(src, dst_dir, upright, ext):
    font = TTFont(src)
    if "glyf" in font:
        dehint(font)    # the upright's hinting does not fit slanted outlines; run autohint.py after
    slant_outlines(font)
    slant_anchors(font)
    ps_name = rename(font, upright)
    dst = os.path.join(dst_dir, f"{ps_name}.{ext}")
    font.save(dst)
    print(f"{dst}: {os.path.getsize(dst) // 1024} KB")


if __name__ == "__main__":
    for upright in STYLES:
        for sub in ("otf", ""):   # OTF in otf/, TTF at the top
            ext = sub or "ttf"
            build(os.path.join(DIR, sub, f"andLubrifont-{upright}.{ext}"),
                  os.path.join(DIR, sub), upright, ext)
    for upright in STYLES:
        for sub in ("otf", ""):
            ext = sub or "ttf"
            for italic, style in enumerate((upright, STYLES[upright][0])):
                add_stat(os.path.join(DIR, sub, f"andLubrifont-{style}.{ext}"), upright, italic)
