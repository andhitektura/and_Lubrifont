# Number features for and_Lubrifont:
#
#   tnum   tabular (equal-width) figures: 1 3 4 8 get alternates centred in
#          the width of the other digits, so columns of numbers line up
#   frac   fractions: 3/8 -> numerator, slash, denominator, laid out like ¾
#   numr   numerators (superior digits)     dnom  denominators (inferior digits)
#   sups   superscript digits, + and − (adds 0 4-9 + − to the existing 1 2 3)
#   subs / sinf   subscript digits
#
# and gives the math signs + − = < > ± × ÷ ¬ one common width, so they align in
# tables. Proportional figures stay the default; the features are switched on
# in the application (Rhino, Affinity, Adobe, Word, CSS font-feature-settings).
#
# The features are compiled with feaLib into a scratch copy of the font and
# merged into the existing GSUB (existing lookups and features are untouched).
#
# usage: py number_features.py font1.otf [font2.ttf ...]   (safe to re-run)
#
# Requires: fonttools

import sys
import copy
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables import otTables
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from respace import shift_glyph

DIGITS = [0x30 + i for i in range(10)]
SUPERIORS = [0x2070, 0x00B9, 0x00B2, 0x00B3, 0x2074, 0x2075, 0x2076, 0x2077, 0x2078, 0x2079]
INFERIORS = [0x2080 + i for i in range(10)]
FRACTION_SLASH = 0x2044
MATH = [0x002B, 0x2212, 0x003D, 0x003C, 0x003E, 0x00B1, 0x00D7, 0x00F7, 0x00AC]
NEW_FEATURES = ["tnum", "frac", "numr", "dnom", "sups", "subs", "sinf"]


# ----------------------------------------------------------- new glyphs
def append_glyph(font, rec, advance, name_hint):
    """append a glyph (outline in a RecordingPen) and return its name"""
    order = list(font.getGlyphOrder())
    is_cff = "CFF " in font
    is_cid = order[-1].startswith("cid") or (is_cff and hasattr(font["CFF "].cff.topDictIndex[0], "ROS"))
    name = f"cid{len(order):05d}" if is_cid else name_hint
    bp = BoundsPen(None)
    rec.replay(bp)
    xmin, _, _, ymax = (round(v) for v in bp.bounds)
    if is_cff:
        cff = font["CFF "].cff
        td = cff.topDictIndex[0]
        private = td.FDArray[0].Private if is_cid else td.Private
        width = None if advance == private.defaultWidthX else advance - private.nominalWidthX
        pen = T2CharStringPen(width, None)
        rec.replay(pen)
        cs = td.CharStrings
        cs.charStringsIndex.append(pen.getCharString(private=private, globalSubrs=cff.GlobalSubrs))
        cs.charStrings[name] = len(cs.charStringsIndex) - 1
        td.charset.append(name)
        if is_cid:
            td.FDSelect.gidArray.append(0)
            td.CIDCount = len(order) + 1
    else:
        pen = TTGlyphPen(None)
        rec.replay(pen)
        font["glyf"][name] = pen.glyph()
    order.append(name)
    font["hmtx"][name] = (advance, xmin)
    if "vmtx" in font:
        ref = font.getBestCmap()[0x30]
        vadv, tsb = font["vmtx"][ref]
        rb = BoundsPen(font.getGlyphSet())
        font.getGlyphSet()[ref].draw(rb)
        font["vmtx"][name] = (vadv, round(tsb + rb.bounds[3] - ymax))
    font.setGlyphOrder(order)
    if is_cff:
        font["CFF "].cff.topDictIndex[0].charset = order
    else:
        font["glyf"].glyphOrder = order
    if "post" in font and font["post"].formatType == 2.0:
        font["post"].extraNames = []
    font["maxp"].numGlyphs = len(order)
    if "GDEF" in font and font["GDEF"].table.GlyphClassDef:
        font["GDEF"].table.GlyphClassDef.classDefs[name] = 1
    return name


def tabular_figures(font):
    """alternates centred in the common digit width; returns {digit: alt}"""
    cmap = font.getBestCmap()
    widths = [font["hmtx"][cmap[u]][0] for u in DIGITS]
    width = max(set(widths), key=widths.count)
    glyphset = font.getGlyphSet()
    alts = {}
    for u in DIGITS:
        name = cmap[u]
        adv = font["hmtx"][name][0]
        if adv == width:
            continue
        bp = BoundsPen(glyphset)
        glyphset[name].draw(bp)
        x0, _, x1, _ = bp.bounds
        dx = round((width - (x1 - x0)) / 2 - x0)
        rec = RecordingPen()
        glyphset[name].draw(TransformPen(rec, (1, 0, 0, 1, dx, 0)))
        if "glyf" in font:   # TrueType needs quadratic outlines
            from fontTools.pens.cu2quPen import Cu2QuPen
            q = RecordingPen()
            rec.replay(Cu2QuPen(q, max_err=1.0, reverse_direction=False))
            rec = q
        alts[name] = append_glyph(font, rec, width, f"{name}.tf")
    return alts


def fraction_slash(font):
    """the slash of ½ as a glyph for the frac feature, placed so that a typed
    fraction (superior digits, slash, inferior digits) reproduces the layout
    of ¾; it overlaps its neighbours, like the slash inside ½"""
    cmap = font.getBestCmap()
    glyphset = font.getGlyphSet()
    half = RecordingPen()
    glyphset[cmap[0x00BD]].draw(half)
    from add_macedonian_cyrillic import split_contours, bounds_of
    contours = split_contours(half.value)
    slash = max(contours, key=lambda c: (lambda b: b[3] - b[1])(bounds_of([c])))
    # in ¾: numerator ³ starts at the left of the glyph like the superior ³,
    # the denominator starts where the inferior digits are placed in ½
    sup3 = BoundsPen(glyphset); glyphset[cmap[0x00B3]].draw(sup3)
    num_adv = font["hmtx"][cmap[0x00B3]][0]
    den = bounds_of([c for c in contours if bounds_of([c])[3] < 400])
    inf = BoundsPen(glyphset); glyphset[cmap[0x2082]].draw(inf)
    advance = round(den[0] - inf.bounds[0] - num_adv)
    rec = RecordingPen()
    from add_macedonian_cyrillic import draw_contours
    draw_contours([slash], TransformPen(rec, (1, 0, 0, 1, -num_adv, 0)))
    if "glyf" in font:
        from fontTools.pens.cu2quPen import Cu2QuPen
        q = RecordingPen()
        rec.replay(Cu2QuPen(q, max_err=1.0, reverse_direction=False))
        rec = q
    return append_glyph(font, rec, advance, "fraction.frac")


def equal_math_widths(font):
    cmap = font.getBestCmap()
    names = [cmap[u] for u in MATH if u in cmap]
    width = max(font["hmtx"][n][0] for n in names)
    for n in names:
        extra = width - font["hmtx"][n][0]
        if extra:
            shift_glyph(font, n, extra // 2, extra - extra // 2)


# ------------------------------------------------------------- features
def existing_mapping(font, tag):
    """single substitutions of an existing GSUB feature"""
    gsub = font["GSUB"].table
    out = {}
    for record in gsub.FeatureList.FeatureRecord:
        if record.FeatureTag == tag:
            for index in record.Feature.LookupListIndex:
                for st in gsub.LookupList.Lookup[index].SubTable:
                    out.update(getattr(getattr(st, "ExtSubTable", st), "mapping", {}))
    return out


def feature_code(font, tnum, old_sups, frac_slash):
    cmap = font.getBestCmap()
    g = lambda us: " ".join(cmap[u] for u in us)
    figures, numr, dnom = g(DIGITS), g(SUPERIORS), g(INFERIORS)
    slash, fraction = cmap[0x2F], frac_slash
    tnum_rules = "\n".join(f"  sub {a} by {b};" for a, b in tnum.items())
    digit_names = {cmap[u] for u in DIGITS}
    sups_extra = "\n".join(f"  sub {a} by {b};" for a, b in old_sups.items()
                           if a not in digit_names)
    return f"""
languagesystem DFLT dflt;
@figures = [{figures}];
@numr = [{numr}];
@dnom = [{dnom}];
feature tnum {{
{tnum_rules}
}} tnum;
feature numr {{ sub @figures by @numr; }} numr;
feature dnom {{ sub @figures by @dnom; }} dnom;
feature sups {{
  sub @figures by @numr;
  sub {cmap[0x2D]} by {cmap[0x207B]};
  sub {cmap[0x2212]} by {cmap[0x207B]};
  sub {cmap[0x2B]} by {cmap[0x207A]};
{sups_extra}
}} sups;
feature subs {{ sub @figures by @dnom; }} subs;
feature sinf {{ sub @figures by @dnom; }} sinf;
feature frac {{
  lookup FRAC_BAR {{ sub @figures {slash}' @figures by {fraction}; }} FRAC_BAR;
  lookup FRAC_NUMR {{ rsub @figures' [{fraction} @numr] by @numr; }} FRAC_NUMR;
  lookup FRAC_DNOM {{ sub [{fraction} @dnom] @figures' by @dnom; }} FRAC_DNOM;
}} frac;
"""


def merge_features(font, path, fea):
    """compile fea into a scratch copy and merge its GSUB into font's GSUB"""
    scratch = copy.deepcopy(font)
    del scratch["GSUB"]
    addOpenTypeFeaturesFromString(scratch, fea, tables=["GSUB"])
    new = scratch["GSUB"].table
    gsub = font["GSUB"].table
    offset = len(gsub.LookupList.Lookup)
    for lookup in new.LookupList.Lookup:
        for st in lookup.SubTable:
            st = getattr(st, "ExtSubTable", st)
            for attr in ("SubstLookupRecord", "SubstLookupRecords"):
                for rec in getattr(st, attr, None) or []:
                    rec.LookupListIndex += offset
            for rs in getattr(st, "ChainSubRuleSet", None) or []:
                for rule in rs.ChainSubRule:
                    for rec in rule.SubstLookupRecord:
                        rec.LookupListIndex += offset
        gsub.LookupList.Lookup.append(lookup)
    gsub.LookupList.LookupCount = len(gsub.LookupList.Lookup)
    # one feature record per language system, keeping the list sorted by tag
    langsyses = []
    for srec in gsub.ScriptList.ScriptRecord:
        if srec.Script.DefaultLangSys:
            langsyses.append(srec.Script.DefaultLangSys)
        langsyses += [l.LangSys for l in srec.Script.LangSysRecord]
    records = list(gsub.FeatureList.FeatureRecord)
    for nrec in sorted(new.FeatureList.FeatureRecord, key=lambda r: r.FeatureTag):
        feature = nrec.Feature
        feature.LookupListIndex = [i + offset for i in feature.LookupListIndex]
        insert_at = sum(1 for r in records if r.FeatureTag <= nrec.FeatureTag)
        remap = {i: (i if i < insert_at else i + len(langsyses)) for i in range(len(records))}
        added = []
        for n, ls in enumerate(langsyses):
            r = otTables.FeatureRecord()
            r.FeatureTag = nrec.FeatureTag
            r.Feature = feature
            added.append(r)
        for n, ls in enumerate(langsyses):
            ls.FeatureIndex = sorted([remap[i] for i in ls.FeatureIndex] + [insert_at + n])
            ls.FeatureCount = len(ls.FeatureIndex)
        records = records[:insert_at] + added + records[insert_at:]
    gsub.FeatureList.FeatureRecord = records
    gsub.FeatureList.FeatureCount = len(records)


def drop_feature(font, tag):
    """remove an existing feature (its lookups stay; they are just unused)"""
    gsub = font["GSUB"].table
    records = gsub.FeatureList.FeatureRecord
    keep = [i for i, r in enumerate(records) if r.FeatureTag != tag]
    remap = {old: new for new, old in enumerate(keep)}
    for srec in gsub.ScriptList.ScriptRecord:
        langsyses = ([srec.Script.DefaultLangSys] if srec.Script.DefaultLangSys else []) + \
            [l.LangSys for l in srec.Script.LangSysRecord]
        for ls in langsyses:
            ls.FeatureIndex = [remap[i] for i in ls.FeatureIndex if i in remap]
            ls.FeatureCount = len(ls.FeatureIndex)
    gsub.FeatureList.FeatureRecord = [records[i] for i in keep]
    gsub.FeatureList.FeatureCount = len(keep)


def patch_font(path):
    font = TTFont(path)
    tags = {r.FeatureTag for r in font["GSUB"].table.FeatureList.FeatureRecord}
    if "tnum" in tags:
        print(f"{path}: already has number features")
        return
    tnum = tabular_figures(font)
    frac_slash = fraction_slash(font)
    equal_math_widths(font)
    # the new sups covers all digits and keeps the letters of the old one
    # (N O n), which it replaces
    old_sups = existing_mapping(font, "sups")
    drop_feature(font, "sups")
    merge_features(font, path, feature_code(font, tnum, old_sups, frac_slash))
    font.save(path)
    print(f"{path}: tabular figures for {len(tnum)} digits; features {' '.join(NEW_FEATURES)}")


if __name__ == "__main__":
    for p in sys.argv[1:]:
        patch_font(p)
