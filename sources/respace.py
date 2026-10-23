# Respace the Latin and Cyrillic letters of WD-XL Lubrifont.
#
# The spacing (side bearings) of the original font was uneven: diagonal and
# open capitals (А Ж Х У A X Z ...) and several lowercase letters (д т f t s
# ...) were too loose, a few sides were too tight (Я, ї), and straight Latin
# lowercase (n m u: 60) did not match Cyrillic (н п и: 50).
#
# The corrections below were measured optically: for each letter, the
# average white space between its outline and the edge of its advance box
# across the letter body (x-height for lowercase, cap height for capitals),
# counting at most 60 units into open sides, compared with the straight
# letters н п и (lowercase) and Н П И H N U (capitals). Differences under 5
# units were ignored, open sides were not taken below 10 units, and 70% of
# each correction was applied (full correction for the clear errors д, Я, є,
# ї, ï). Pair-specific gaps (Та, LT, AV ...) are left to the kern feature.
#
# Accented letters follow their base letter (Ć follows C, Ѓ follows Г, ...),
# X.ss01 follows X, and mark-attachment anchors move with the outlines.
# Digits and CJK glyphs are not changed.
#
# usage: py respace.py font1.ttf [font2.otf ...]   (safe to re-run)

import sys
import unicodedata
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables import otTables
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.t2CharStringPen import T2CharStringPen

# unicode: (change of left side bearing, change of right side bearing)
DELTAS = {
    0x0041: (-14, -14),  # A
    0x0042: (+0, -6),  # B
    0x0043: (-4, -15),  # C
    0x0044: (+0, -4),  # D
    0x0045: (+0, -20),  # E
    0x0046: (+0, -21),  # F
    0x0047: (-4, -9),  # G
    0x0049: (-7, -7),  # I
    0x004A: (-25, +0),  # J
    0x004B: (+0, -13),  # K
    0x004C: (+0, -21),  # L
    0x004F: (-4, -4),  # O
    0x0050: (+0, -11),  # P
    0x0051: (-6, -6),  # Q
    0x0052: (+0, -6),  # R
    0x0053: (-11, -11),  # S
    0x0056: (+0, +4),  # V
    0x0058: (-21, -21),  # X
    0x005A: (-27, -27),  # Z
    0x0061: (-13, -8),  # a
    0x0062: (+0, -4),  # b
    0x0063: (-4, -12),  # c
    0x0064: (-4, +0),  # d
    0x0065: (-4, -10),  # e
    0x0066: (-14, -7),  # f
    0x0067: (-6, -5),  # g
    0x0069: (-6, -6),  # i
    0x006A: (+0, -5),  # j
    0x006D: (-8, -8),  # m
    0x006E: (-8, -8),  # n
    0x006F: (-4, -4),  # o
    0x0070: (-5, -6),  # p
    0x0071: (-6, -5),  # q
    0x0072: (-8, +0),  # r
    0x0073: (-13, -15),  # s
    0x0074: (-14, -5),  # t
    0x0075: (-8, -8),  # u
    0x0076: (-8, -8),  # v
    0x0077: (-10, -9),  # w
    0x0079: (+4, +0),  # y
    0x007A: (-7, -6),  # z
    0x00EF: (+20, +19),  # ï
    0x0131: (-6, -6),  # ı
    0x0402: (+0, -15),  # Ђ
    0x0404: (-4, -20),  # Є
    0x0405: (-12, -10),  # Ѕ
    0x0406: (-7, -7),  # І
    0x0408: (-25, +0),  # Ј
    0x0409: (-14, -16),  # Љ
    0x040A: (+0, -16),  # Њ
    0x040B: (+0, -15),  # Ћ
    0x0410: (-14, -14),  # А
    0x0411: (+0, -19),  # Б
    0x0412: (+0, -6),  # В
    0x0413: (+0, -7),  # Г
    0x0414: (-22, -22),  # Д
    0x0415: (+0, -20),  # Е
    0x0416: (-20, -20),  # Ж
    0x0417: (-21, -6),  # З
    0x041A: (+0, -13),  # К
    0x041B: (-14, +0),  # Л
    0x041E: (-4, -4),  # О
    0x0420: (+0, -11),  # Р
    0x0421: (-4, -15),  # С
    0x0423: (-21, -21),  # У
    0x0424: (-20, -20),  # Ф
    0x0425: (-21, -21),  # Х
    0x0426: (+0, -22),  # Ц
    0x0427: (-18, +0),  # Ч
    0x0429: (+0, -22),  # Щ
    0x042A: (+0, -16),  # Ъ
    0x042C: (+0, -16),  # Ь
    0x042D: (-20, -4),  # Э
    0x042E: (+0, -4),  # Ю
    0x042F: (-21, +21),  # Я
    0x0430: (-13, -8),  # а
    0x0431: (+0, -4),  # б
    0x0433: (+0, -14),  # г
    0x0434: (-26, -83),  # д
    0x0435: (-4, -10),  # е
    0x0436: (-10, -10),  # ж
    0x0437: (-5, +0),  # з
    0x043A: (+6, -4),  # к
    0x043B: (-18, +0),  # л
    0x043E: (-4, -4),  # о
    0x0440: (-5, -6),  # р
    0x0441: (-4, -12),  # с
    0x0442: (-14, -14),  # т
    0x0443: (+4, +0),  # у
    0x0446: (+0, -19),  # ц
    0x0449: (+0, -19),  # щ
    0x044A: (-14, -17),  # ъ
    0x044C: (+0, -17),  # ь
    0x044D: (-8, -4),  # э
    0x044E: (-6, -4),  # ю
    0x044F: (-6, +0),  # я
    0x0454: (+14, -31),  # є
    0x0455: (-13, -15),  # ѕ
    0x0456: (-6, -6),  # і
    0x0457: (+20, +19),  # ї
    0x0458: (+0, -5),  # ј
    0x0459: (-18, -17),  # љ
    0x045A: (+0, -17),  # њ
    0x045E: (+4, +0),  # ў
    0x0490: (+0, -7),  # Ґ
    0x0491: (+0, -14),  # ґ
}

DONE_CHECK = (0x0434, 623)   # д had an advance of 623 before respacing


def expanded_deltas(cmap):
    """DELTAS plus precomposed letters, which follow their base letter."""
    deltas = dict(DELTAS)
    for uni in cmap:
        if uni in deltas or not (0x00C0 <= uni <= 0x024F or 0x1E00 <= uni <= 0x1EFF
                                 or 0x0400 <= uni <= 0x04FF):
            continue
        nfd = unicodedata.normalize("NFD", chr(uni))
        if len(nfd) > 1 and ord(nfd[0]) in DELTAS and all(
                unicodedata.category(ch) == "Mn" for ch in nfd[1:]):
            deltas[uni] = DELTAS[ord(nfd[0])]
    return deltas


def alternates(font, tags=("ss01",)):
    """glyph -> alternate glyph for single substitutions in the given features"""
    out = {}
    gsub = font["GSUB"].table
    for record in gsub.FeatureList.FeatureRecord:
        if record.FeatureTag not in tags:
            continue
        for index in record.Feature.LookupListIndex:
            for st in gsub.LookupList.Lookup[index].SubTable:
                st = getattr(st, "ExtSubTable", st)
                out.update(getattr(st, "mapping", {}))
    return out


def shift_glyph(font, name, dl, dr):
    glyphset = font.getGlyphSet()
    adv, _ = font["hmtx"][name]
    new_adv = adv + dl + dr
    if "CFF " in font:
        cff = font["CFF "].cff
        cs = cff.topDictIndex[0].CharStrings
        private = cs[name].private
        width = None if new_adv == private.defaultWidthX else new_adv - private.nominalWidthX
        pen = T2CharStringPen(width, None)
        glyphset[name].draw(TransformPen(pen, (1, 0, 0, 1, dl, 0)))
        cs.charStringsIndex[cs.charStrings[name]] = pen.getCharString(
            private=private, globalSubrs=cff.GlobalSubrs)
        bp = BoundsPen(None)
        font.getGlyphSet()[name].draw(bp)
        font["hmtx"][name] = (new_adv, round(bp.bounds[0]) if bp.bounds else 0)
    else:
        # TrueType: hmtx lsb must equal the glyph's xMin (renderers position
        # the outline from it), so take it from the moved outline itself
        glyph = font["glyf"][name]
        if glyph.numberOfContours > 0:
            glyph.coordinates.translate((dl, 0))
            glyph.recalcBounds(font["glyf"])
        font["hmtx"][name] = (new_adv, glyph.xMin if glyph.numberOfContours else 0)


def shift_anchors(font, shifts):
    if "GPOS" not in font:
        return
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


def patch_font(path_in):
    font = TTFont(path_in)
    cmap = font.getBestCmap()
    if font["hmtx"][cmap[DONE_CHECK[0]]][0] != DONE_CHECK[1]:
        print(f"{path_in}: already respaced")
        return
    deltas = {}
    for uni, d in expanded_deltas(cmap).items():
        if uni in cmap:
            deltas[cmap[uni]] = d
    for base, alt in alternates(font).items():
        if base in deltas and alt not in deltas:
            deltas[alt] = deltas[base]
    for name, (dl, dr) in deltas.items():
        shift_glyph(font, name, dl, dr)
    shift_anchors(font, {name: dl for name, (dl, dr) in deltas.items() if dl})
    font.save(path_in)
    print(f"{path_in}: respaced {len(deltas)} glyphs")


if __name__ == "__main__":
    for p in sys.argv[1:]:
        patch_font(p)
