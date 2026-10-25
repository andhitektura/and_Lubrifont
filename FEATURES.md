**and_Lubrifont**

# OpenType features

and_Lubrifont has set up multiple OpenType features, which are listed as follows.

> [!NOTE] 
> The version of font for this document is v2.603 (20261025).

## `vert` / `vrt2` — Vertical Alternates

This font has designed and set up vertical typesetting punctuations including:

Shared by SC/TC: `–—―‥…〈〉《》「」『』【】〓〔〕〖〗（）－＝［］｛｝～`  
SC only: `、。‘’“”！，：；？ㄧ`

## `ccmp` — Glyph Composition/Decomposition

This font has designed characters needed for [Hanyu Pinyin](https://en.wikipedia.org/wiki/Pinyin), [Taiwan Minnanyu Luomazi Pinyin Fang'an (or Tâi-lô)](https://en.wikipedia.org/wiki/T%C3%A2i-u%C3%A2n_L%C3%B4-m%C3%A1-j%C4%AB_Phing-im_Hong-%C3%A0n) and [Pe̍h-ōe-jī](https://en.wikipedia.org/wiki/Pe%CC%8Dh-%C5%8De-j%C4%AB). As Tâi-lô and Pe̍h-ōe-jī use some characters that are not included in Unicode, glyph composition/decomposition `ccmp` is used to compose the characters. Hanyu Pinyin has some overlapping characters with Tâi-lô and Pe̍h-ōe-jī, thus the `ccmp` feature also covers Hanyu Pinyin characters (e.g. Ề, Ǚ, Ẑ).

This font also auto-composes the Chinese dash with `ccmp`. Chinese dashes should be ⸺ `U+2E3A TWO-EM DASH` and ⸻ `U+2E3B THREE-EM DASH` (which are two and three *hanzi* wide respectively); however, as these characters are difficult to type with normal input methods, two — `U+2014 EM DASH` are commonly used in their place. Chinese dashes are spaced apart from adjacent characters but stay connected inside, which requires composing multiple em-dash glyphs. The font decomposes `U+2E3A` and `U+2E3B` into single-*hanzi*-wide `U+2014`, and then replaces them with joined glyphs. Users may input any combination of the dashes and the font will join them correctly; this feature also works in vertical typesetting.

| Character | Decomposition |
| --- | :-- |
| ⸺ `U+2E3A TWO-EM DASH` | U+2014 U+2014 |
| ⸻ `U+2E3B THREE-EM DASH` | U+2014 U+2014 U+2014 |

This feature is turned on automatically; users do not need to set anything up.

## `kern` — Kerning

Since v2.300, Latin and Cyrillic letters and the common punctuation are kerned, so pairs such as `Та`, `Гл`, `ГА`, `LT`, `AV`, `Yo` and `P.` close up. Kerning applies within each script (Latin with Latin, Cyrillic with Cyrillic) and with punctuation; digits are not kerned, so numbers stay aligned in tables and drawings.

This feature is on by default in most software and in browsers. Some word processors apply it only after it is switched on in the font or character settings, and some technical text engines do not apply kerning at all; there the even letter spacing of the font itself applies.

## `tnum` — Tabular Figures

By default the digits are proportional (the `1` is narrower). With `tnum` all digits have the same width, so columns of numbers line up in tables, schedules and title blocks:

| Default | `tnum` |
| --- | --- |
| `1 111,18` — narrow 1 | every digit 532 units wide |

The math signs `+ − = < > ± × ÷ ¬` always share one width (662 units).

## `frac` — Fractions

Typing `3/8`, `5/16` or `12/25` with `frac` on gives proper fractions, laid out like the built-in `½ ¼ ¾`. Note that it applies to any digits around a slash (e.g. dates), so turn it on only for the fractions.

## `sups`, `subs` / `sinf`, `numr`, `dnom` — Superscripts and Subscripts

* `sups`: superscript digits and `+ −` (e.g. select `2` in `m2` → `m²`, `-5` in `10-5` → `10⁻⁵`)
* `subs` / `sinf`: subscript digits (`CO2` → `CO₂`)
* `numr` / `dnom`: the numerator and denominator digits used by `frac`

These features are switched on in the application's OpenType or typography settings, or in CSS with `font-feature-settings` (e.g. `"tnum"`). Where an application has no such settings, use the precomposed characters `½ ⅓ ¼ ⅛ ² ³ ₂` directly.

## `mark` / `mkmk` — Mark Positioning

Combining accents (U+0300–U+036F) are positioned above Latin letters and, since v2.200, above all Cyrillic letters (including `Ґґ`) and `ĆćČčĐđ`. This lets stress marks typed as a letter followed by a combining accent, such as Macedonian or Russian `е́ о́ и́`, sit correctly above the letter.

This feature is turned on automatically.

## `chws`/`vchw` — (Vertical) Contextual Half-width Spacing

This font follows professional Chinese typesetting practice and implements contextual punctuation spacing adjustment. This reduces the space between punctuation marks so that the text appears more compact, which is most noticeable between pairs of ending punctuation and opening brackets (e.g. combinations like `。（` or `：「`). The font compresses empty space between punctuation marks following subtractive rules, but does not compress lone punctuation. Currently only cornered punctuation (such as Simplified Chinese and Japanese comma and period) and brackets are compressed by this feature; centered punctuation (such as the interpunct and Traditional Chinese comma and period) is not compressed.

This feature is on by default in Chromium browsers version 123 and above, but needs to be turned on manually in other environments. In web environments, you may use the CSS `text-spacing-trim` property or turn on `chws`/`vchw` manually.

## `ss01` — Stylistic Set 01 (Alternate X)

To match the design of other characters, another glyph is designed for `X`.

![Sample of ss01](./documentation/ss01.png)

Users need to find “Stylistic set” in their software and turn on `ss01`.

## `ss18` — Stylistic Set 18 (Western Punctuations)

The font has reserved `ss18` for Western punctuation. This feature provides Western proportional-width styles for the characters below:

* … `U+2026 HORIZONTAL ELLIPSIS` (at bottom)
* · `U+00B7 MIDDLE DOT` (or interpunct, proportional width)
* ‘ `U+2018 LEFT SINGLE QUOTATION MARK` (proportional width)
* ’ `U+2019 RIGHT SINGLE QUOTATION MARK` (proportional width)
* “ `U+201C LEFT DOUBLE QUOTATION MARK` (proportional width)
* ” `U+201D RIGHT DOUBLE QUOTATION MARK` (proportional width)

## `ss19` — Stylistic Set 19 (Cornered/SC Punctuation)

Starting from version 2.000, the font merges the SC and TC versions into one `.ttc` font file, and some glyphs are shared between these fonts. The font has reserved `ss19` for the cornered (bottom-left) punctuation style used in Simplified Chinese in mainland China. This feature changes the following punctuation:

* 、 `U+3001 IDEOGRAPHIC COMMA`
* 。 `U+3002 IDEOGRAPHIC FULL STOP`
* ！ `U+FF01 FULLWIDTH EXCLAMATION MARK`
* ， `U+FF0C FULLWIDTH COMMA`
* ： `U+FF1A FULLWIDTH COLON`
* ； `U+FF1B FULLWIDTH SEMICOLON`
* ？ `U+FF1F FULLWIDTH QUESTION MARK`
* … `U+2026 HORIZONTAL ELLIPSIS` (centered)
* ‘ `U+2018 LEFT SINGLE QUOTATION MARK` (full-width)
* ’ `U+2019 RIGHT SINGLE QUOTATION MARK` (full-width)
* “ `U+201C LEFT DOUBLE QUOTATION MARK` (full-width)
* ” `U+201D RIGHT DOUBLE QUOTATION MARK` (full-width)

> ． `U+FF0E FULLWIDTH FULL STOP` has no centered form for typesetting reasons, so it does not need to be switched.

In addition, the following characters are punctuation marks that are used differently in mainland China and Taiwan and are stored separately in the SC and TC versions, so this feature switches them as well:

* ˉ `U+02C9 MODIFIER LETTER MACRON` (Bopomofo 1st tone)
* ˊ `U+02CA MODIFIER LETTER ACUTE ACCENT` (Bopomofo 2nd tone)
* ˇ `U+02C7 CARON` (Bopomofo 3rd tone)
* ˋ `U+02CB MODIFIER LETTER GRAVE ACCENT` (Bopomofo 4th tone)
* ˙ `U+02D9 DOT ABOVE` (Bopomofo neutral tone)

## `ss20` — Stylistic Set 20 (Centered/TC Punctuation)

The font has reserved `ss20` for the centered punctuation style used in Traditional Chinese in Taiwan. This feature changes the following punctuation:

* 、 `U+3001 IDEOGRAPHIC COMMA`
* 。 `U+3002 IDEOGRAPHIC FULL STOP`
* ！ `U+FF01 FULLWIDTH EXCLAMATION MARK`
* ， `U+FF0C FULLWIDTH COMMA`
* ： `U+FF1A FULLWIDTH COLON`
* ； `U+FF1B FULLWIDTH SEMICOLON`
* ？ `U+FF1F FULLWIDTH QUESTION MARK`
* … `U+2026 HORIZONTAL ELLIPSIS` (centered)
* ‘ `U+2018 LEFT SINGLE QUOTATION MARK` (proportional width)
* ’ `U+2019 RIGHT SINGLE QUOTATION MARK` (proportional width)
* “ `U+201C LEFT DOUBLE QUOTATION MARK` (proportional width)
* ” `U+201D RIGHT DOUBLE QUOTATION MARK` (proportional width)

> ． `U+FF0E FULLWIDTH FULL STOP` has no centered form for typesetting reasons, so it is not included.

In addition, the following characters are punctuation marks that are used differently in mainland China and Taiwan and are stored separately in the SC and TC versions, so this feature switches them as well:

* ˉ `U+02C9 MODIFIER LETTER MACRON` (Bopomofo 1st tone)
* ˊ `U+02CA MODIFIER LETTER ACUTE ACCENT` (Bopomofo 2nd tone)
* ˇ `U+02C7 CARON` (Bopomofo 3rd tone)
* ˋ `U+02CB MODIFIER LETTER GRAVE ACCENT` (Bopomofo 4th tone)
* ˙ `U+02D9 DOT ABOVE` (Bopomofo neutral tone)

## `liga` — Ligatures

| Character | Combination |
| --- | :-- |
| Special feature (easter egg) | WD-XLlogo; |

Users need to find “Standard ligatures” in their software and turn it on.

## `dlig` — Discretionary Ligatures

This font also provides several shorthand forms used in Hanyu Pinyin, such as `ng` → ŋ `U+014B LATIN SMALL LETTER ENG` and `zh` → ẑ `U+1E91 LATIN SMALL LETTER Z WITH CIRCUMFLEX`. To avoid clashing with other languages, they are set up as discretionary ligatures:

| Character | Combination |
| --- | :-- |
| Ŋ `U+014A LATIN CAPITAL LETTER ENG` | NG |
| ŋ `U+014B LATIN SMALL LETTER ENG` | ng |
| Ẑ `U+1E90 LATIN CAPITAL LETTER Z WITH CIRCUMFLEX` | ZH/Zh |
| ẑ `U+1E91 LATIN SMALL LETTER Z WITH CIRCUMFLEX` | zh |
| Ĉ `U+0108 LATIN CAPITAL LETTER C WITH CIRCUMFLEX` | CH/Ch |
| ĉ `U+0109 LATIN SMALL LETTER C WITH CIRCUMFLEX` | ch |
| Ŝ `U+015C LATIN CAPITAL LETTER S WITH CIRCUMFLEX` | SH/Sh |
| ŝ `U+015D LATIN SMALL LETTER S WITH CIRCUMFLEX` | sh |

Users need to find “Historical and discretionary ligatures” in their software and turn it on.

## `smpl` / `trad` — Simplified/Traditional forms

This font includes a few technical tests, including Simplified/Traditional form exchange. This feature lets users convert Simplified characters to Traditional characters (`trad`) or Traditional characters to Simplified characters (`smpl`). One-to-many characters are not swapped automatically; users need to change those characters manually. **Warning: the feature modifies the information stored in documents; please save the original file in a safe location before testing.** [(Source)](https://docs.microsoft.com/en-us/typography/opentype/spec/features_pt)

Most software does not support this feature; browsers can set it through CSS.

## `locl` — Localized Forms

This font includes a feature for testing: localized forms based on region. The SC, TC and JP versions are merged into one font file, which allows character glyphs to be switched from one region's form to another's. This feature is mainly used to change glyphs that differ between SC, TC and JP, such as the top of “骨”.

Currently some software supports this feature: if the software can tag the language of the text, the feature is likely available and is applied automatically when changing languages. In browsers, adding the language attribute `lang="zh-cn"`, `lang="zh-tw"` or `lang="ja"` to the elements turns on this feature.

## `aalt` — Access All Alternates

All the features above (except `liga` and `dlig`) can be accessed through `aalt`, so the character choices from `smpl`/`trad` can still be used in software that offers a glyph or alternates panel.

## Extra: Variation Selector

This font includes preset Variation Selectors for Chinese punctuation, which can be used to choose the preferred form of a punctuation mark. The characters in the tables below can be copied and pasted directly.

| Character | Cornered (`U+FE00`) | Centered (`U+FE01`) |
| :-- | --- | --- |
| 、 `U+3001 IDEOGRAPHIC COMMA` | 、︀ | 、︁ |
| 。 `U+3002 IDEOGRAPHIC FULL STOP` | 。︀ | 。︁ |
| ！ `U+FF01 FULLWIDTH EXCLAMATION MARK` | ！︀ | ！︁ |
| ， `U+FF0C FULLWIDTH COMMA` | ，︀ | ，︁ |
| ． `U+FF0E FULLWIDTH FULL STOP` | ．︀ | ．︁ |
| ： `U+FF1A FULLWIDTH COLON` | ：︀ | ：︁ |
| ； `U+FF1B FULLWIDTH SEMICOLON` | ；︀ | ；︁ |
| ？ `U+FF1F FULLWIDTH QUESTION MARK` | ？︀ | ？︁ |


| Character | Proportional (`U+FE00`) | Full-width (`U+FE01`) |
| :-- | --- | --- |
| ‘ `U+2018 LEFT SINGLE QUOTATION MARK` | ‘︀ | ‘︁ |
| ’ `U+2019 RIGHT SINGLE QUOTATION MARK` | ’︀ | ’︁ |
| “ `U+201C LEFT DOUBLE QUOTATION MARK` | “︀ | “︁ |
| ” `U+201D RIGHT DOUBLE QUOTATION MARK` | ”︀ | ”︁ |
