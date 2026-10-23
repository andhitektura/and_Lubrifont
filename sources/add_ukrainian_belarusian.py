# Add the Cyrillic letters needed for Ukrainian (Є є І і Ї ї Ґ ґ) and
# Belarusian (Ў ў, plus І і) to WD-XL Lubrifont.
#
# Works like add_extra_glyphs.py (and reuses its machinery): every new glyph
# is constructed from glyphs already in the font, so the script can be run on
# the TrueType source as well as on the CID-keyed release builds.
#
# usage: py add_ukrainian_belarusian.py font1.ttf [font2.otf ...]
#
# Requires: fonttools, skia-pathops

import sys
from add_macedonian_cyrillic import patch_font
from add_extra_glyphs import ExtraBuilder, rect

NEW_GLYPHS = {
    0x0404: ("Eukrcyr", ("mirror", 0x042D, "x")),      # Є = mirrored Э
    0x0454: ("eukrcyr", ("mirror", 0x044D, "x")),      # є = mirrored э
    0x0406: ("Iukrcyr", ("copy", 0x0049)),             # І = I
    0x0456: ("iukrcyr", ("copy", 0x0069)),             # і = i
    0x0407: ("Yicyr", ("copy", 0x00CF)),               # Ї = Ï
    0x0457: ("yicyr", ("copy", 0x00EF)),               # ї = ï
    0x0490: ("Gheupturncyr", ("ghe_upturn", 0x0413)),  # Ґ = Г + upturn
    0x0491: ("gheupturncyr", ("ghe_upturn", 0x0433)),  # ґ = г + upturn
    0x040E: ("Ushortcyr", ("accent", 0x0423, 0x016C)), # Ў = У + ˘ (from Ŭ)
    0x045E: ("ushortcyr", ("accent", 0x0443, 0x016D)), # ў = у + ˘ (from ŭ)
}


class UkrainianBuilder(ExtraBuilder):
    # height of the upturn above the top bar, relative to the letter height
    UPTURN = 0.18

    def build_ghe_upturn(self, uni):
        # a stem-wide stroke rising from the right end of the top bar
        x0, y0, x1, y1 = self.bounds(uni)
        top = round(y1 + (y1 - y0) * self.UPTURN)
        stroke = rect(x1 - self.STEM, y1 - self.STEM, x1, top, r=40)
        return [self.path(uni), stroke], self.advance(uni)


if __name__ == "__main__":
    for p in sys.argv[1:]:
        patch_font(p, NEW_GLYPHS, UkrainianBuilder)
