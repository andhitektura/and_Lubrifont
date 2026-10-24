# Fixes for and_Lubrifont v2.402 (font files; the build sources carry the
# same values for future builds):
#
# - Line metrics: typo and hhea ascender/descender 945/-235, line gap 0, in
#   every font, so the .otf and .ttf of a font set text with the same line
#   spacing (1180 units, as the .ttf always had) in every application; USE_TYPO_METRICS set so applications that honour it
#   use these values.
# - Windows clipping box: usWinAscent/usWinDescent at least the font's
#   highest and lowest point (accented capitals Ѓ Ќ Ѐ Ѝ Ў Č Ř Š ... reach
#   1168), so Windows clips nothing.
# - PostScript names without the underscore (andLubrifontSC-Regular, ...);
#   the visible family name stays "and_Lubrifont".
# - OS/2 Unicode ranges and code pages for the added languages: Latin
#   Extended-A/B, punctuation, super/subscripts, arrows, math operators;
#   code pages 1250 (Central European), 1253 (Greek), 1254 (Turkish).
# - Copyright notice: "Modifications Copyright 2026 Studio ANDhitektura."
#   added after the original notice (which is kept, as the OFL requires),
#   in every language, and the same notice in the CFF table (which had
#   carried a stray Adobe notice from the AFDKO CID template).
# - Vendor: Studio ANDhitektura (OS/2 vendor code ANDH, name ID 8, vendor
#   URL in name ID 11 and the unique ID in name ID 3), so applications do
#   not present the original author as vendor of this modified version. The
#   original designers stay credited in name ID 9, followed by this edition.
#
# usage: py release_fixes.py font1.otf [font2.ttf ...]   (safe to re-run)

import sys
from fontTools.ttLib import TTFont

ASCENT, DESCENT = 945, -235
USE_TYPO_METRICS = 1 << 7
UNICODE_BITS = [2, 3, 31, 32, 37, 38]
CODEPAGE_BITS = [1, 3, 4]   # 1250, 1253, 1254
CREDIT = "Modifications Copyright 2026 Studio ANDhitektura."
VENDOR_ID = "ANDH"
MANUFACTURER = "Studio ANDhitektura"
VENDOR_URL = "https://github.com/andhitektura/and_Lubrifont"
DESIGNER_CREDIT = ("[and_Lubrifont] Studio ANDhitektura - Cyrillic and Central European "
                   "extension, spacing, kerning, weights and italics")


def ps_name(s):
    return s.replace("and_Lubrifont", "andLubrifont")


def set_bits(os2, prefix, bits):
    for b in bits:
        attr = f"{prefix}{b // 32 + 1}"
        setattr(os2, attr, getattr(os2, attr) | (1 << (b % 32)))


def patch_font(path):
    font = TTFont(path)
    os2 = font["OS/2"]
    os2.sTypoAscender, os2.sTypoDescender, os2.sTypoLineGap = ASCENT, DESCENT, 0
    hhea = font["hhea"]
    hhea.ascent, hhea.descent, hhea.lineGap = ASCENT, DESCENT, 0
    head = font["head"]
    os2.usWinAscent = max(os2.usWinAscent, head.yMax)
    os2.usWinDescent = max(os2.usWinDescent, -head.yMin)
    os2.fsSelection |= USE_TYPO_METRICS
    set_bits(os2, "ulUnicodeRange", UNICODE_BITS)
    set_bits(os2, "ulCodePageRange", CODEPAGE_BITS)
    os2.achVendID = VENDOR_ID
    name = font["name"]
    for record in name.names:
        text = record.toUnicode()
        new = text
        if record.nameID in (3, 6):
            new = ps_name(text).replace(";NFSL;", f";{VENDOR_ID};")
        elif record.nameID == 0 and CREDIT not in text:
            new = f"{text} {CREDIT}"
        elif record.nameID == 9 and record.langID == 0x409 and DESIGNER_CREDIT not in text:
            new = f"{text}; {DESIGNER_CREDIT}"
        elif record.nameID == 11:
            new = VENDOR_URL
        if new != text:
            record.string = new
    name.setName(MANUFACTURER, 8, 3, 1, 0x409)
    name.setName(VENDOR_URL, 11, 3, 1, 0x409)
    if "CFF " in font:
        cff = font["CFF "].cff
        cff.fontNames = [ps_name(n) for n in cff.fontNames]
        top = cff.topDictIndex[0]
        top.Notice = name.getName(0, 3, 1, 0x409).toUnicode()
        for fd in getattr(cff.topDictIndex[0], "FDArray", []):
            if hasattr(fd, "FontName"):
                fd.FontName = ps_name(fd.FontName)
    font.save(path)
    print(f"{path}: {font['name'].getDebugName(6)}, winAscent {os2.usWinAscent}")


if __name__ == "__main__":
    for p in sys.argv[1:]:
        patch_font(p)
