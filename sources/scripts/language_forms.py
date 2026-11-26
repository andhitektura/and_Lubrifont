# Language-specific letter forms (`locl`) for and_Lubrifont, added in v2.604.
#
# The font now declares language systems besides the default, so that an
# application which knows the language of the text (Word, InDesign, a browser
# with lang="bg") can pick the right forms automatically:
#
#   Bulgarian (cyrl BGR)   the modern Bulgarian lowercase: в with a closed
#                          ascender, д like g, ж and к with ascenders, и й ѝ
#                          like u ŭ ù, л like an upside-down v, п like n, т like
#                          m, ъ ь ю with ascenders. (ц ш щ already have the
#                          Bulgarian shape in this design; г and з keep theirs.)
#   Romanian (latn ROM, MOL)  Ş ş Ţ ţ typed with a cedilla appear with the
#                          comma below (Ș ș Ț ț), as Romanian requires.
#
# The Bulgarian glyphs are unencoded alternates built from the font's own
# letters; they get mark anchors (for combining stress accents) like the
# letters they come from. Text in other languages is unchanged.
#
# usage: py language_forms.py font1.otf [font2.ttf ...]   (safe to re-run)
#        (run on the CJK fonts and the Regular, then make_weights.py,
#        make_italics.py and autohint.py)
#
# Requires: fonttools, skia-pathops

import copy
import sys
import pathops
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables import otTables
from fontTools.otlLib import builder as otl
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.boundsPen import BoundsPen
from add_macedonian_cyrillic import finalize, draw_contours, bounds_of
from add_extra_glyphs import ExtraBuilder, rect, op
from number_features import append_glyph

STEM = 91
ASCENDER = 710
XHEIGHT = 485

# Bulgarian forms: Cyrillic letter -> recipe
BULGARIAN = {
    0x0432: ("ve", ()),                        # в
    0x0434: ("copy", (ord("g"),)),             # д
    0x0436: ("zhe", ()),                       # ж
    0x0438: ("copy", (ord("u"),)),             # и
    0x0439: ("copy", (0x016D,)),               # й  (ŭ)
    0x045D: ("copy", (0x00F9,)),               # ѝ  (ù)
    0x043A: ("copy", (ord("k"),)),             # к
    0x043B: ("el", ()),                        # л
    0x043F: ("copy", (ord("n"),)),             # п
    0x0442: ("copy", (ord("m"),)),             # т
    0x044A: ("raise_stem", (0x044A,)),         # ъ
    0x044C: ("raise_stem", (0x044C,)),         # ь
    0x044E: ("raise_stem", (0x044E,)),         # ю
}
# where a form takes its mark anchor from (the letter it is built from)
ANCHOR_FROM = {0x0434: ord("g"), 0x0438: ord("u"), 0x0439: ord("u"), 0x045D: ord("u"),
               0x043A: ord("k"), 0x043F: ord("n"), 0x0442: ord("m"), 0x043B: ord("v")}

ROMANIAN = {0x015E: 0x0218, 0x015F: 0x0219, 0x0162: 0x021A, 0x0163: 0x021B}

LANGUAGES = {
    "cyrl": {"BGR ": "bulgarian"},
    "latn": {"ROM ": "romanian", "MOL ": "romanian"},
}


class FormBuilder(ExtraBuilder):

    def build_copy(self, uni):
        return [self.path(uni)], self.advance(uni), 0

    def build_el(self):
        # ʌ: v turned upside down within the x-height
        x0, y0, x1, y1 = self.bounds(ord("v"))
        lo, hi = max(y0, 0), min(y1, XHEIGHT)
        p = self.path(ord("v")).transform(1, 0, 0, -1, 0, lo + hi)
        return [p], self.advance(ord("v")), 0

    def build_zhe(self):
        # к of the Bulgarian form is k; ж is k and its mirror image sharing
        # the ascending stem
        k = self.path(ord("k"))
        x0, y0, x1, y1 = self.bounds(ord("k"))
        c = x0 + STEM / 2
        mirror = k.transform(-1, 0, 0, 1, 2 * c, 0)
        left = 2 * c - x1                       # ink starts here
        dx = x0 - left
        parts = [k.transform(1, 0, 0, 1, dx, 0), mirror.transform(1, 0, 0, 1, dx, 0)]
        rsb = self.advance(ord("k")) - x1
        return parts, round(x1 + dx + rsb), dx

    def build_raise_stem(self, uni):
        # the left stem (with the flag of ъ) lengthened to the ascender
        contours = self.contours(uni)
        x0, y0, x1, y1 = bounds_of(contours)
        lift = ASCENDER - y1
        stem_right = x0 + STEM + 5
        rec = RecordingPen()
        for contour in contours:
            for opname, args in contour:
                pts = [(x, y + lift) if (y > 350 and (uni != 0x044E or x <= stem_right)) else (x, y)
                       for x, y in args]
                getattr(rec, opname)(*pts)
        p = pathops.Path()
        rec.replay(p.getPen())
        return [pathops.simplify(p)], self.advance(uni), 0

    def build_ve(self):
        # b with its ascender closed into a loop down to the bowl
        b = self.path(ord("b"))
        x0, y0, x1, y1 = self.bounds(ord("b"))
        h = STEM / 2
        right = x0 + STEM + 140                   # loop narrower than the bowl
        loop = self._stroke([[(x0 + h, y1 - h), (right - h, y1 - h), (right - h, XHEIGHT - h)]], STEM)
        loop = op(loop, rect(x0, XHEIGHT - STEM, x1, y1), pathops.PathOp.INTERSECTION)
        return [b, loop], self.advance(ord("b")), 0


def has_language(font, tag):
    for srec in font["GSUB"].table.ScriptList.ScriptRecord:
        for lrec in srec.Script.LangSysRecord:
            if lrec.LangSysTag == tag:
                return True
    return False


def mark_base_subtables(font):
    gpos = font["GPOS"].table
    seen = set()
    for record in gpos.FeatureList.FeatureRecord:
        if record.FeatureTag != "mark":
            continue
        for index in record.Feature.LookupListIndex:
            for st in gpos.LookupList.Lookup[index].SubTable:
                st = getattr(st, "ExtSubTable", st)
                if isinstance(st, otTables.MarkBasePos) and st.Format == 1 and id(st) not in seen:
                    seen.add(id(st))
                    yield st


def glyph_bounds(font, name):
    bp = BoundsPen(font.getGlyphSet())
    font.getGlyphSet()[name].draw(bp)
    return bp.bounds


def add_anchor(font, new, model):
    """give `new` the mark anchors of `model`, re-centred on the new outline
    (and raised to its top if it is taller)"""
    bm, bn = glyph_bounds(font, model), glyph_bounds(font, new)
    top_model, top_new = bm[3], bn[3]
    dx = (bn[0] + bn[2]) / 2 - (bm[0] + bm[2]) / 2
    for st in mark_base_subtables(font):
        glyphs = st.BaseCoverage.glyphs
        if model not in glyphs or new in glyphs:
            continue
        record = copy.deepcopy(st.BaseArray.BaseRecord[glyphs.index(model)])
        for anchor in record.BaseAnchor:
            if anchor is None:
                continue
            anchor.XCoordinate = round(anchor.XCoordinate + dx)
            if top_new > top_model + 50:
                anchor.YCoordinate = round(anchor.YCoordinate + top_new - top_model)
        # new glyphs are appended, so they sort last in the coverage
        glyphs.append(new)
        st.BaseArray.BaseRecord.append(record)
        st.BaseArray.BaseCount = len(st.BaseArray.BaseRecord)


def add_language_systems(font, lookups):
    """add the language systems of LANGUAGES to GSUB and GPOS; in GSUB each
    gets the script's default features plus a `locl` feature with its
    lookup. lookups: {"bulgarian": lookup index, ...}"""
    for table_tag in ("GSUB", "GPOS"):
        table = font[table_tag].table
        records = list(table.FeatureList.FeatureRecord)
        scripts = {s.ScriptTag: s for s in table.ScriptList.ScriptRecord}
        new_langs = []          # (script record, tag, kind)
        for script, langs in LANGUAGES.items():
            if script not in scripts:
                continue
            for tag, kind in langs.items():
                new_langs.append((scripts[script], tag, kind))
        added = []
        if table_tag == "GSUB":
            # one locl feature record per new language system, inserted after
            # the features that sort before "locl"
            insert_at = sum(1 for r in records if r.FeatureTag <= "locl")
            remap = {i: (i if i < insert_at else i + len(new_langs)) for i in range(len(records))}
            for srec in table.ScriptList.ScriptRecord:
                langsyses = ([srec.Script.DefaultLangSys] if srec.Script.DefaultLangSys else []) + \
                    [l.LangSys for l in srec.Script.LangSysRecord]
                for ls in langsyses:
                    ls.FeatureIndex = [remap[i] for i in ls.FeatureIndex]
                    if ls.ReqFeatureIndex != 0xFFFF:
                        ls.ReqFeatureIndex = remap[ls.ReqFeatureIndex]
            for n, (_, tag, kind) in enumerate(new_langs):
                r = otTables.FeatureRecord()
                r.FeatureTag = "locl"
                r.Feature = otTables.Feature()
                r.Feature.FeatureParams = None
                r.Feature.LookupListIndex = [lookups[kind]]
                r.Feature.LookupCount = 1
                added.append(r)
            records = records[:insert_at] + added + records[insert_at:]
            table.FeatureList.FeatureRecord = records
            table.FeatureList.FeatureCount = len(records)
        for n, (srec, tag, kind) in enumerate(new_langs):
            default = srec.Script.DefaultLangSys
            ls = otTables.LangSys()
            ls.LookupOrder = None
            ls.ReqFeatureIndex = 0xFFFF
            ls.FeatureIndex = list(default.FeatureIndex) if default else []
            if table_tag == "GSUB":
                ls.FeatureIndex = sorted(ls.FeatureIndex + [insert_at + n])
            ls.FeatureCount = len(ls.FeatureIndex)
            lrec = otTables.LangSysRecord()
            lrec.LangSysTag = tag
            lrec.LangSys = ls
            srec.Script.LangSysRecord.append(lrec)
            srec.Script.LangSysRecord.sort(key=lambda r: r.LangSysTag)
            srec.Script.LangSysCount = len(srec.Script.LangSysRecord)


def merge_locl(font):
    """A language system must have only one `locl`: shapers use the first.
    The CJK fonts' default language systems already have one (the regional
    Chinese / Japanese forms), so in each new language system that one is
    folded into the new `locl`, keeping all lookups. Safe to re-run."""
    gsub = font["GSUB"].table
    records = gsub.FeatureList.FeatureRecord
    new_tags = {tag for langs in LANGUAGES.values() for tag in langs}
    changed = False
    for srec in gsub.ScriptList.ScriptRecord:
        default = set(srec.Script.DefaultLangSys.FeatureIndex) if srec.Script.DefaultLangSys else set()
        for lrec in srec.Script.LangSysRecord:
            if lrec.LangSysTag not in new_tags:
                continue
            ls = lrec.LangSys
            locl = [i for i in ls.FeatureIndex if records[i].FeatureTag == "locl"]
            if len(locl) < 2:
                continue
            ours = [i for i in locl if i not in default][0]
            lookups = set()
            for i in locl:
                lookups.update(records[i].Feature.LookupListIndex)
            records[ours].Feature.LookupListIndex = sorted(lookups)
            records[ours].Feature.LookupCount = len(lookups)
            ls.FeatureIndex = [i for i in ls.FeatureIndex if i not in locl or i == ours]
            ls.FeatureCount = len(ls.FeatureIndex)
            changed = True
    return changed


def add_lookup(font, mapping):
    gsub = font["GSUB"].table
    lookup = otl.buildLookup([otl.buildSingleSubstSubtable(mapping)])
    gsub.LookupList.Lookup.append(lookup)
    gsub.LookupList.LookupCount = len(gsub.LookupList.Lookup)
    return len(gsub.LookupList.Lookup) - 1


def patch_font(path):
    font = TTFont(path)
    if has_language(font, "BGR "):
        if merge_locl(font):
            font.save(path)
            print(f"{path}: regional locl folded into the new language systems")
        else:
            print(f"{path}: already has the language forms")
        return
    cmap = font.getBestCmap()
    builder = FormBuilder(font)
    is_cff = "CFF " in font
    bulgarian = {}
    for uni, (kind, args) in BULGARIAN.items():
        parts, advance, dx = getattr(builder, "build_" + kind)(*args)
        rec = finalize(parts, clockwise=not is_cff)
        if not is_cff:
            q = RecordingPen()
            rec.replay(Cu2QuPen(q, max_err=1.0, reverse_direction=False))
            rec = q
        name = append_glyph(font, rec, advance, f"uni{uni:04X}.loclBGR")
        bulgarian[cmap[uni]] = name
        model = cmap[ANCHOR_FROM.get(uni, uni)]
        add_anchor(font, name, model)
    romanian = {cmap[a]: cmap[b] for a, b in ROMANIAN.items()}
    lookups = {"bulgarian": add_lookup(font, bulgarian), "romanian": add_lookup(font, romanian)}
    add_language_systems(font, lookups)
    merge_locl(font)
    font.save(path)
    print(f"{path}: Bulgarian forms ({len(bulgarian)} glyphs) and Romanian comma below")


if __name__ == "__main__":
    for p in sys.argv[1:]:
        patch_font(p)
