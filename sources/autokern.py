# Kerning for the Latin and Cyrillic letters of WD-XL Lubrifont.
#
# The original font has no kern feature, so pairs such as Та, Гл, LT, AV, Yo,
# P. or r, show large gaps. This script measures the outlines and writes the
# kerning to a text file, and applies that file to font files as a `kern`
# feature (a new GPOS lookup; existing GPOS lookups are untouched).
#
#   py autokern.py measure ../fonts/OTF/WD-XLLubrifontTC-Regular.otf kerning.txt
#   py autokern.py apply kerning.txt font1.otf [font2.ttf ...]
#   py autokern.py replace kerning.txt font1.otf [...]   (replaces an existing kern)
#
# Punctuation is measured and kerned in the form it takes in Latin/Cyrillic
# text: the SC fonts switch ‘ ’ “ ” to their proportional forms there, which
# the TC fonts use by default, so kerning is measured from a TC font. When
# applying, each character is resolved with HarfBuzz in Latin context; a
# punctuation mark whose resolved form has a different width from the
# measured one (the full-width quotes of the JP fonts) is not kerned.
#
# Measuring: every glyph is rendered at 1 unit = 1 pixel and its left and
# right profiles (distance from the advance box edge to the ink) are taken
# every 5 units of height. For a pair, the white gap is averaged over the
# heights where both glyphs have ink (each row clipped at CLIP units), and
# compared with the gap of two straight letters (нн / НН / nn). FACTOR of the
# difference is applied, but the two shapes are never brought closer than
# MIN_GAP units at any height (accents and descenders included). Values are
# rounded to 5 units and adjustments below KEEP units are dropped.
#
# The result is stored as kerning classes plus exceptions: base letters are
# grouped by similar kerning, accented letters join their base letter's
# class, a class pair gets the least tight value of its base letters, and any
# pair whose own value differs from its class (usually an accent that would
# clash) gets an exception that overrides the class.
#
# Pairs are only kerned within a script (Latin with Latin, Cyrillic with
# Cyrillic) plus punctuation. Digits are not kerned, so numbers stay aligned.
#
# Requires: fonttools, freetype-py, uharfbuzz, numpy

import sys
import unicodedata
import numpy as np

STEP = 5
Y0, Y1 = -300, 1000
CLIP = 300
FACTOR = 0.6
MIN_GAP = 40
MIN_KERN = 10
KEEP = 20           # adjustments below this are not kept
CLASS_TOL = 10      # base letters within this of each other share a class
EXCEPTION_TOL = 15  # a pair further than this from its class gets its own value
TRACKING = 12       # space added to each side by track.py; measured as if absent,
                    # so the kerning is the same as before tracking was added
REFERENCE = "нн"   # нн

PUNCT = [ord(c) for c in ".,:;'\"‘’“”‚„«»‹›-–—()[]/?!ʼ"]


def script_of(uni):
    if 0x0400 <= uni <= 0x04FF:
        return "cyrl"
    if unicodedata.category(chr(uni)).startswith("L") and uni < 0x0250 or 0x1E00 <= uni <= 0x1EFF:
        return "latn"
    if uni in PUNCT:
        return "punct"
    return None


def kerning_glyphs(cmap):
    out = {}
    for uni in cmap:
        s = script_of(uni)
        if s and (s == "punct" or unicodedata.category(chr(uni))[0] == "L"):
            out[uni] = s
    return out


def resolve(path, unis):
    """glyph used for each character in Latin/Cyrillic text"""
    import uharfbuzz as hb
    from fontTools.ttLib import TTFont
    font = TTFont(path)
    cmap = font.getBestCmap()
    order = font.getGlyphOrder()
    hbfont = hb.Font(hb.Face(hb.Blob.from_file_path(path)))
    names = {}
    for uni in unis:
        if uni not in cmap:
            continue
        if uni not in PUNCT:
            names[uni] = cmap[uni]
            continue
        buf = hb.Buffer()
        buf.add_str("a" + chr(uni))
        buf.guess_segment_properties()
        hb.shape(hbfont, buf, {})
        names[uni] = order[buf.glyph_infos[1].codepoint]
    return names


# ------------------------------------------------------------------ measure
def profiles(path, unis):
    import freetype
    from fontTools.ttLib import TTFont
    font = TTFont(path)
    names = resolve(path, unis)
    order = font.getGlyphOrder()
    face = freetype.Face(path)
    face.set_char_size(font["head"].unitsPerEm * 64)
    rows = np.arange(Y0, Y1, STEP)
    prof = {}
    for uni in unis:
        name = names[uni]
        adv = font["hmtx"][name][0]
        face.load_glyph(order.index(name), freetype.FT_LOAD_NO_HINTING | freetype.FT_LOAD_RENDER)
        bm = face.glyph.bitmap
        ink = np.array(bm.buffer, dtype=np.uint8).reshape(bm.rows, bm.width) > 127
        left = np.full(len(rows), np.nan)
        right = np.full(len(rows), np.nan)
        for i, y in enumerate(rows):
            r = face.glyph.bitmap_top - y - 1
            if 0 <= r < ink.shape[0]:
                band = ink[r:r + STEP].any(axis=0) if r + STEP <= ink.shape[0] else ink[r]
                xs = np.nonzero(band)[0]
                if len(xs):
                    left[i] = face.glyph.bitmap_left + xs[0]
                    right[i] = adv - (face.glyph.bitmap_left + xs[-1] + 1)
        prof[uni] = (left, right, adv)
    return prof


def pair_kern(right_of_first, left_of_second, ref):
    gap = right_of_first + left_of_second - 2 * TRACKING
    both = ~np.isnan(gap)
    if not both.any():
        return 0
    avg = np.minimum(gap[both], CLIP).mean()
    k = FACTOR * (ref - avg)
    k = max(k, MIN_GAP - gap[both].min())     # never closer than MIN_GAP
    k = 5 * round(k / 5)
    return k if abs(k) >= MIN_KERN else 0


def is_base(uni):
    return len(unicodedata.normalize("NFD", chr(uni))) == 1


def base_of(uni):
    return ord(unicodedata.normalize("NFD", chr(uni))[0])


def cluster(vectors, keys, tol):
    """greedy clustering of kerning vectors; every member is within tol of
    every other member"""
    classes = []
    for key in sorted(keys, key=lambda k: -np.abs(vectors[k]).sum()):
        v = vectors[key]
        for c in classes:
            if np.abs(v - c["hi"]).max() <= tol and np.abs(v - c["lo"]).max() <= tol:
                c["members"].append(key)
                c["hi"] = np.maximum(c["hi"], v)
                c["lo"] = np.minimum(c["lo"], v)
                break
        else:
            classes.append({"members": [key], "hi": v.copy(), "lo": v.copy()})
    return [c["members"] for c in classes]


def measure(font_path, out_path):
    from fontTools.ttLib import TTFont
    cmap = TTFont(font_path).getBestCmap()
    glyphs = kerning_glyphs(cmap)
    prof = profiles(font_path, glyphs)
    n = ord(REFERENCE[0])
    ref_prof = profiles(font_path, [n])[n]
    ref = np.nanmean(ref_prof[1] + ref_prof[0]) - 2 * TRACKING

    # every pair, measured glyph by glyph
    unis = sorted(glyphs)
    idx = {u: i for i, u in enumerate(unis)}
    M = np.zeros((len(unis), len(unis)), dtype=int)
    for a in unis:
        for b in unis:
            sa, sb = glyphs[a], glyphs[b]
            if ("punct" not in (sa, sb) and sa != sb) or sa == sb == "punct":
                continue
            k = pair_kern(prof[a][1], prof[b][0], ref)
            if abs(k) >= KEEP:
                M[idx[a], idx[b]] = k

    # classes from base letters; accented letters join their base's class
    bases = [u for u in unis if is_base(u)]
    bcols = [idx[u] for u in bases]
    left = cluster({u: M[idx[u], bcols] for u in bases}, bases, CLASS_TOL)
    right = cluster({u: M[bcols, idx[u]] for u in bases}, bases, CLASS_TOL)
    lcls = {u: i for i, c in enumerate(left) for u in c}
    rcls = {u: i for i, c in enumerate(right) for u in c}
    for u in unis:
        b = base_of(u)
        if u not in lcls:
            lcls[u] = lcls.get(b, None)
            if lcls[u] is None:
                lcls[u] = len(left); left.append([])
            left[lcls[u]].append(u)
        if u not in rcls:
            rcls[u] = rcls.get(b, None)
            if rcls[u] is None:
                rcls[u] = len(right); right.append([])
            right[rcls[u]].append(u)

    # class value: the least tight of the base members (never tighter than
    # any of them), measured on base letters only
    V = np.zeros((len(left), len(right)), dtype=int)
    for i, lc in enumerate(left):
        for j, rc in enumerate(right):
            lb = [idx[u] for u in lc if is_base(u)] or [idx[u] for u in lc]
            rb = [idx[u] for u in rc if is_base(u)] or [idx[u] for u in rc]
            V[i, j] = M[np.ix_(lb, rb)].max()
    # exceptions: pairs whose own value is not within EXCEPTION_TOL of the class
    exceptions = []
    for a in unis:
        for b in unis:
            own, cls = M[idx[a], idx[b]], V[lcls[a], rcls[b]]
            if own != cls and (abs(own - cls) > EXCEPTION_TOL or own > cls):
                exceptions.append((a, b, own))

    def name(u):
        return f"U+{u:04X}"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("# kerning measured by autokern.py\n")
        f.write("# @L<n>/@R<n>: classes of first/second glyphs; pos: class pairs;\n")
        f.write("# exception: glyph pairs that override their classes\n\n")
        for i, c in enumerate(left):
            f.write(f"@L{i} = {' '.join(name(u) for u in c)}  # {''.join(chr(u) for u in c)}\n")
        for j, c in enumerate(right):
            f.write(f"@R{j} = {' '.join(name(u) for u in c)}  # {''.join(chr(u) for u in c)}\n")
        f.write("\n")
        count = 0
        for i in range(len(left)):
            for j in range(len(right)):
                if V[i, j]:
                    f.write(f"pos @L{i} @R{j} {V[i, j]:+d}\n"); count += 1
        f.write("\n")
        f.write("\n")
        for u in sorted(u for u in unis if u in PUNCT):
            f.write(f"advance {name(u)} {prof[u][2]}  # {chr(u)} as measured\n")
        f.write("\n")
        for a, b, k in exceptions:
            f.write(f"exception {name(a)} {name(b)} {k:+d}  # {chr(a)}{chr(b)}\n")
    print(f"{out_path}: {len(left)} left / {len(right)} right classes, "
          f"{count} class pairs, {len(exceptions)} exceptions (reference gap {ref:.0f})")


# -------------------------------------------------------------------- apply
def read_kerning(path):
    classes, class_pairs, exceptions, advances = {}, [], [], {}
    for line in open(path, encoding="utf-8"):
        line = line.split("#")[0].split()
        if not line:
            continue
        if line[0].startswith("@"):
            classes[line[0]] = [int(t[2:], 16) for t in line[2:]]
        elif line[0] == "pos":
            class_pairs.append((line[1], line[2], int(line[3])))
        elif line[0] == "exception":
            exceptions.append((int(line[1][2:], 16), int(line[2][2:], 16), int(line[3])))
        elif line[0] == "advance":
            advances[int(line[1][2:], 16)] = int(line[2])
    return classes, class_pairs, exceptions, advances


def remove_kern(font):
    """remove the kern feature added by apply() (its lookup is the last one)"""
    gpos = font["GPOS"].table
    records = gpos.FeatureList.FeatureRecord
    kern_idx = [i for i, r in enumerate(records) if r.FeatureTag == "kern"]
    if not kern_idx:
        return
    lookups = {l for i in kern_idx for l in records[i].Feature.LookupListIndex}
    last = len(gpos.LookupList.Lookup) - 1
    assert lookups == {last}, "kern lookup is not the last lookup; not touching it"
    remap = {}
    for i in range(len(records)):
        if i not in kern_idx:
            remap[i] = len(remap)
    for srec in gpos.ScriptList.ScriptRecord:
        langsyses = ([srec.Script.DefaultLangSys] if srec.Script.DefaultLangSys else []) + \
            [l.LangSys for l in srec.Script.LangSysRecord]
        for ls in langsyses:
            ls.FeatureIndex = [remap[i] for i in ls.FeatureIndex if i in remap]
            ls.FeatureCount = len(ls.FeatureIndex)
    gpos.FeatureList.FeatureRecord = [r for i, r in enumerate(records) if i not in kern_idx]
    gpos.FeatureList.FeatureCount = len(gpos.FeatureList.FeatureRecord)
    del gpos.LookupList.Lookup[last]
    gpos.LookupList.LookupCount = len(gpos.LookupList.Lookup)


def apply(kern_path, font_paths, replace=False):
    from fontTools.ttLib import TTFont
    from fontTools.ttLib.tables import otTables
    from fontTools.otlLib.builder import (buildPairPosGlyphsSubtable,
                                          buildPairPosClassesSubtable, buildValue)

    classes, class_pairs, exceptions, advances = read_kerning(kern_path)
    all_unis = {u for v in classes.values() for u in v}
    for path in font_paths:
        font = TTFont(path)
        if replace:
            remove_kern(font)
        gpos = font["GPOS"].table
        if any(r.FeatureTag == "kern" for r in gpos.FeatureList.FeatureRecord):
            print(f"{path}: already has kern")
            continue
        # glyph used in Latin/Cyrillic text; punctuation in another form
        # (different width) than the one measured is left out
        cmap = {u: g for u, g in resolve(path, all_unis).items()
                if u not in advances or font["hmtx"][g][0] == advances[u]}
        glyph_map = font.getReverseGlyphMap()
        names = {k: tuple(sorted((cmap[u] for u in v if u in cmap), key=glyph_map.get))
                 for k, v in classes.items()}
        # exceptions first: in a lookup the first subtable that matches wins
        ex = {(cmap[a], cmap[b]): (buildValue({"XAdvance": k}), None)
              for a, b, k in exceptions if a in cmap and b in cmap}
        cl = {(names[l], names[r]): (buildValue({"XAdvance": k}), None)
              for l, r, k in class_pairs if names[l] and names[r]}
        subtables = []
        if ex:
            subtables.append(buildPairPosGlyphsSubtable(ex, glyph_map, valueFormat1=0x0004))
        subtables.append(buildPairPosClassesSubtable(cl, glyph_map, valueFormat1=0x0004))
        lookup = otTables.Lookup()
        lookup.LookupType = 2
        lookup.LookupFlag = 0x0008   # ignore marks
        lookup.SubTable = subtables
        lookup.SubTableCount = len(subtables)
        gpos.LookupList.Lookup.append(lookup)
        gpos.LookupList.LookupCount = len(gpos.LookupList.Lookup)
        kern_lookup = len(gpos.LookupList.Lookup) - 1

        # one kern feature record per language system, like the other
        # features, keeping the feature list sorted by tag
        feature = otTables.Feature()
        feature.FeatureParams = None
        feature.LookupListIndex = [kern_lookup]
        feature.LookupCount = 1
        old = list(gpos.FeatureList.FeatureRecord)
        insert_at = sum(1 for r in old if r.FeatureTag < "kern")
        langsyses = []
        for srec in gpos.ScriptList.ScriptRecord:
            if srec.Script.DefaultLangSys:
                langsyses.append(srec.Script.DefaultLangSys)
            langsyses += [l.LangSys for l in srec.Script.LangSysRecord]
        new_records = old[:insert_at] + [None] * len(langsyses) + old[insert_at:]
        remap = {i: (i if i < insert_at else i + len(langsyses)) for i in range(len(old))}
        for n, ls in enumerate(langsyses):
            r = otTables.FeatureRecord()
            r.FeatureTag = "kern"
            r.Feature = feature
            new_records[insert_at + n] = r
            ls.FeatureIndex = sorted([remap[i] for i in ls.FeatureIndex] + [insert_at + n])
            ls.FeatureCount = len(ls.FeatureIndex)
        gpos.FeatureList.FeatureRecord = new_records
        gpos.FeatureList.FeatureCount = len(new_records)
        font.save(path)
        print(f"{path}: kern feature with {len(cl)} class pairs and {len(ex)} exceptions")


if __name__ == "__main__":
    if sys.argv[1] == "measure":
        measure(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == "apply":
        apply(sys.argv[2], sys.argv[3:])
    elif sys.argv[1] == "replace":
        apply(sys.argv[2], sys.argv[3:], replace=True)
