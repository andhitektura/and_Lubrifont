# Fixes for and_Lubrifont v2.402 (font files; the build sources carry the
# same values for future builds):
#
# - Windows line metrics: usWinAscent raised to 1030 so accented capitals
#   (Ѓ Ќ Ѐ Ѝ Ў Č Ř Š Ž Ś Ź Ń Ů Å ..., up to 1022 units) are not clipped by
#   Windows, and the USE_TYPO_METRICS flag set so applications that honour it
#   keep the line spacing given by the typo metrics.
# - PostScript names without the underscore (andLubrifontSC-Regular, ...);
#   the visible family name stays "and_Lubrifont".
# - OS/2 Unicode ranges and code pages for the added languages: Latin
#   Extended-A/B, punctuation, super/subscripts, arrows, math operators;
#   code pages 1250 (Central European), 1253 (Greek), 1254 (Turkish).
# - Copyright notice: "Modifications Copyright 2026 Studio ANDhitektura."
#   added after the original notice (which is kept, as the OFL requires).
#
# usage: py release_fixes.py font1.otf [font2.ttf ...]   (safe to re-run)

import sys
from fontTools.ttLib import TTFont

WIN_ASCENT = 1030
USE_TYPO_METRICS = 1 << 7
UNICODE_BITS = [2, 3, 31, 32, 37, 38]
CODEPAGE_BITS = [1, 3, 4]   # 1250, 1253, 1254
CREDIT = "Modifications Copyright 2026 Studio ANDhitektura."


def ps_name(s):
    return s.replace("and_Lubrifont", "andLubrifont")


def set_bits(os2, prefix, bits):
    for b in bits:
        attr = f"{prefix}{b // 32 + 1}"
        setattr(os2, attr, getattr(os2, attr) | (1 << (b % 32)))


def patch_font(path):
    font = TTFont(path)
    os2 = font["OS/2"]
    os2.usWinAscent = max(os2.usWinAscent, WIN_ASCENT)
    os2.fsSelection |= USE_TYPO_METRICS
    set_bits(os2, "ulUnicodeRange", UNICODE_BITS)
    set_bits(os2, "ulCodePageRange", CODEPAGE_BITS)
    for record in font["name"].names:
        text = record.toUnicode()
        new = text
        if record.nameID in (3, 6):
            new = ps_name(text)
        elif record.nameID == 0 and record.langID == 0x409 and CREDIT not in text:
            new = f"{text} {CREDIT}"
        if new != text:
            record.string = new
    if "CFF " in font:
        cff = font["CFF "].cff
        cff.fontNames = [ps_name(n) for n in cff.fontNames]
        for fd in getattr(cff.topDictIndex[0], "FDArray", []):
            if hasattr(fd, "FontName"):
                fd.FontName = ps_name(fd.FontName)
    font.save(path)
    print(f"{path}: {font['name'].getDebugName(6)}, winAscent {os2.usWinAscent}")


if __name__ == "__main__":
    for p in sys.argv[1:]:
        patch_font(p)
