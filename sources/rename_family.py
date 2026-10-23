# Rename the font family of these fonts from WD-XL Lubrifont to and_Lubrifont
# and shorten the version string to "Version X.XXX".
#
# Changed: family / full / unique / PostScript names (name IDs 1, 3, 4, 6,
# all languages, including the localized "WD-XL 滑油字" names), the version
# string (name ID 5), and the CFF font names. The copyright notice and the
# designer credits (name IDs 0, 9 ...) are left as they are: the original
# work is credited there, as the SIL Open Font License requires.
#
# usage: py rename_family.py font1.otf [font2.ttf ...]   (safe to re-run)

import sys
from fontTools.ttLib import TTFont

RENAME_IDS = {1, 3, 4, 6, 16, 17, 21, 22}
REPLACEMENTS = [("WD-XLLubrifont", "and_Lubrifont"),
                ("WDXLLubrifont", "and_Lubrifont"),
                ("WD-XL Lubrifont", "and_Lubrifont"),
                ("WD-XL 滑油字", "and_Lubrifont")]


def renamed(s):
    for a, b in REPLACEMENTS:
        s = s.replace(a, b)
    return s


def patch_font(path):
    font = TTFont(path)
    version = f"Version {font['head'].fontRevision:.3f}"
    for record in font["name"].names:
        text = record.toUnicode()
        if record.nameID in RENAME_IDS:
            new = renamed(text)
        elif record.nameID == 5:
            new = version
        else:
            continue
        if new != text:
            record.string = new
    if "CFF " in font:
        cff = font["CFF "].cff
        cff.fontNames = [renamed(n) for n in cff.fontNames]
        top = cff.topDictIndex[0]
        for key in ("FullName", "FamilyName"):
            if hasattr(top, key):
                setattr(top, key, renamed(getattr(top, key)))
        for fd in getattr(top, "FDArray", []):
            if hasattr(fd, "FontName"):
                fd.FontName = renamed(fd.FontName)
    font.save(path)
    print(f"{path}: {font['name'].getDebugName(4)} / {font['name'].getDebugName(6)} / {version}")


if __name__ == "__main__":
    for p in sys.argv[1:]:
        patch_font(p)
