# Specimen image for the README: documentation/specimen.png (1600 x 1000),
# set in the and_Lubrifont .ttf fonts with kerning (Pillow with libraqm).
# It names no version number, so it does not go out of date with a release.
#
# usage: py make_specimen.py
#
# Requires: Pillow (with libraqm)

import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "..", "..", "fonts", "and_Lubrifont")
OUT = os.path.join(HERE, "..", "..", "documentation", "specimen.png")

BG, INK, GREY, RULE = "#f8f8f5", "#151515", "#808080", "#c8c8c4"
X = 72


def font(style, size):
    return ImageFont.truetype(os.path.join(FONTS, f"andLubrifont-{style}.ttf"), size,
                              layout_engine=ImageFont.Layout.RAQM)


def main():
    img = Image.new("RGB", (1600, 1000), BG)
    d = ImageDraw.Draw(img)
    d.text((X, 40), "and_Lubrifont", font=font("Regular", 150), fill=INK)
    d.text((X, 240), "Studio ANDhitektura edition of WD-XL Lubrifont", font=font("Regular", 30), fill=GREY)
    d.line((X, 305, 1528, 305), fill=RULE, width=2)
    y = 335
    x = X
    for style, label in (("Light", "Light"), ("LightItalic", "Italic"), ("Regular", "Regular"),
                         ("Italic", "Italic"), ("Bold", "Bold"), ("BoldItalic", "Italic")):
        f = font(style, 64)
        d.text((x, y), label, font=f, fill=INK)
        x += d.textlength(label, font=f) + (28 if "Italic" not in style else 64)
    lines = [
        ("Regular", 64, "ФАЗА#A - АРХИТЕКТУРА — Технички опис", 450),
        ("LightItalic", 52, "Ground floor plan  ·  Level ±0,00  ·  Scale 1:100", 545),
        ("Regular", 52, "Ѓ Ќ Ѕ Љ Њ Џ Ђ Ћ Є Ї Ґ Ў  ·  Ć Č Đ Ą Ę Ś Ż Ř Ů Ș Ț Ğ İ", 625),
        ("Bold", 52, "0123456789  ·  ½ ⅜  ·  m²  ·  CO₂  ·  ⌀12  ·  ∆h  ·  ↔ ⇒ ✓", 705),
    ]
    for style, size, text, ly in lines:
        d.text((X, ly), text, font=font(style, size), fill=INK)
    d.text((X, 805), "Македонски  ·  Српски  ·  Українська  ·  Беларуская  ·  Polski  ·  Čeština  ·  Română  ·  Türkçe",
           font=font("Regular", 32), fill=GREY)
    d.text((X, 905), "SIL Open Font License 1.1  ·  github.com/andhitektura/and_Lubrifont",
           font=font("Regular", 26), fill=GREY)
    img.save(OUT, optimize=True)
    print(OUT)


if __name__ == "__main__":
    main()
