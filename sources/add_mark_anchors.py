# Add base anchors for the mark-to-base (`mark`) feature to Cyrillic letters
# and to the added Latin letters (Ć ć Č č Đ đ, Polish, Czech, Romanian ...),
# so that combining accents (e.g. Macedonian / Russian stress marks typed as
# е + U+0301) sit above the letter instead of colliding with it.
#
# Anchors follow the convention of the existing ones (A: 266,710; a: 214,485):
# horizontally centred on the outline, at the top of the letter body.
# Glyphs that already have an anchor are left alone.
#
# usage: py add_mark_anchors.py font1.ttf [font2.otf ...]

import sys
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables import otTables
from fontTools.pens.boundsPen import BoundsPen

TARGETS = list(range(0x0400, 0x0460)) + [0x0490, 0x0491, 0x0106, 0x0107, 0x010C, 0x010D, 0x0110, 0x0111]
# Polish, Czech, Slovak, Romanian, Turkish letters (add_central_european.py)
TARGETS += [0x0104, 0x0105, 0x010E, 0x010F, 0x0116, 0x0117, 0x0118, 0x0119, 0x011E,
            0x011F, 0x0130, 0x0139, 0x013A, 0x013D, 0x013E, 0x0154, 0x0155, 0x0158,
            0x0159, 0x015A, 0x015B, 0x015E, 0x015F, 0x0162, 0x0163, 0x0164, 0x0165,
            0x016E, 0x016F, 0x0179, 0x017A, 0x017B, 0x017C, 0x0218, 0x0219, 0x021A,
            0x021B]


def mark_base_subtables(font):
    gpos = font["GPOS"].table
    for record in gpos.FeatureList.FeatureRecord:
        if record.FeatureTag != "mark":
            continue
        for index in record.Feature.LookupListIndex:
            lookup = gpos.LookupList.Lookup[index]
            for st in lookup.SubTable:
                st = getattr(st, "ExtSubTable", st)
                if isinstance(st, otTables.MarkBasePos) and st.Format == 1:
                    yield st


def patch_font(path_in):
    font = TTFont(path_in)
    cmap = font.getBestCmap()
    glyphset = font.getGlyphSet()
    order = {name: i for i, name in enumerate(font.getGlyphOrder())}
    added = set()
    seen = set()
    for st in mark_base_subtables(font):
        if id(st) in seen:
            continue
        seen.add(id(st))
        records = dict(zip(st.BaseCoverage.glyphs, st.BaseArray.BaseRecord))
        # base glyphs in this subtable are anchored above (mark anchors y > 0)
        for uni in TARGETS:
            name = cmap.get(uni)
            if name is None or name in records:
                continue
            bp = BoundsPen(glyphset)
            glyphset[name].draw(bp)
            if bp.bounds is None:
                continue
            x0, _, x1, y1 = bp.bounds
            rec = otTables.BaseRecord()
            rec.BaseAnchor = []
            for _ in range(st.ClassCount):
                anchor = otTables.Anchor()
                anchor.Format = 1
                anchor.XCoordinate = round((x0 + x1) / 2)
                anchor.YCoordinate = round(y1)
                rec.BaseAnchor.append(anchor)
            records[name] = rec
            added.add(chr(uni))
        names = sorted(records, key=order.__getitem__)
        st.BaseCoverage.glyphs = names
        st.BaseArray.BaseRecord = [records[n] for n in names]
        st.BaseArray.BaseCount = len(names)
    if added:
        font.save(path_in)
    print(f"{path_in}: anchors added for {len(added)} glyphs")


if __name__ == "__main__":
    for p in sys.argv[1:]:
        patch_font(p)
