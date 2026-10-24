# Sets the version of the fonts: head.fontRevision, the version in name IDs
# 3 and 5 (all languages; a ttfautohint note after ";" is kept) and the CFF
# version. Run it before a release, then rebuild the .ttc and make_woff2.py.
#
# usage: py set_version.py 2.501 font1.otf [font2.ttf ...]
#
# Requires: fonttools

import re
import sys
from fontTools.ttLib import TTFont

VERSION = re.compile(r"\d+\.\d{3}")


def set_version(path, version):
    font = TTFont(path)
    font["head"].fontRevision = float(version)
    for record in font["name"].names:
        if record.nameID in (3, 5):
            text = record.toUnicode()
            record.string = VERSION.sub(version, text, count=1)
    if "CFF " in font:
        font["CFF "].cff.topDictIndex[0].version = version
    font.save(path)
    print(f"{path}: {font['name'].getDebugName(5)}")


if __name__ == "__main__":
    for p in sys.argv[2:]:
        set_version(p, sys.argv[1])
