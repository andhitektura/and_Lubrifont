# Builds the two release downloads from the fonts in the repository:
#
#   and_Lubrifont-<version>.zip      the six styles (.ttf, otf/, woff2/)
#   and_Lubrifont-CJK-<version>.zip  SC, TC, JP S, JP N (.ttf, otf/) and the .ttc
#
# each with OFL.txt and an INSTALL.txt made from sources/release/. Also
# writes notes.md, the release text: the version's section of UPDATES.md.
#
# The version is read from the fonts, and every font must carry the same
# one (so a release can't mix versions). The zips are reproducible: files in
# a fixed order with a fixed date, so the same fonts give the same zip.
#
# usage: py make_release.py OUTDIR [VERSION]   (VERSION, e.g. from a tag, must
#                                                match the fonts)
# Used by .github/workflows/release.yml; runs locally the same way.
#
# Requires: fonttools

import glob
import os
import re
import sys
import zipfile
from fontTools.ttLib import TTFont

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
DATE = (2020, 1, 1, 0, 0, 0)

PACKAGES = {
    "and_Lubrifont": ("INSTALL.txt", [
        ("", "fonts/and_Lubrifont/*.ttf"),
        ("otf/", "fonts/and_Lubrifont/otf/*.otf"),
        ("woff2/", "fonts/and_Lubrifont/woff2/*.woff2"),
    ]),
    "and_Lubrifont-CJK": ("INSTALL-CJK.txt", [
        ("", "fonts/and_Lubrifont-CJK/*.ttf"),
        ("", "fonts/and_Lubrifont-CJK/*.ttc"),
        ("otf/", "fonts/and_Lubrifont-CJK/otf/*.otf"),
    ]),
}


def font_version(path):
    if path.endswith(".ttc"):
        from fontTools.ttLib import TTCollection
        fonts = TTCollection(path).fonts
    else:
        fonts = [TTFont(path, lazy=True)]
    versions = set()
    for font in fonts:
        versions.add(f"{font['head'].fontRevision:.3f}")
        name5 = font["name"].getDebugName(5) or ""
        versions.update(re.findall(r"\d+\.\d{3}", name5)[:1])
    return versions


def release_notes(version):
    text = open(os.path.join(ROOT, "UPDATES.md"), encoding="utf-8").read()
    m = re.search(rf"^## Ver {re.escape(version)};.*?\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    if not m:
        sys.exit(f"UPDATES.md has no section '## Ver {version}; ...'")
    return m.group(1).strip() + "\n"


def write_zip(out_dir, package, version, install, groups):
    folder = f"{package}-{version}"
    files = []
    for sub, pattern in groups:
        for path in sorted(glob.glob(os.path.join(ROOT, pattern))):
            files.append((f"{folder}/{sub}{os.path.basename(path)}", open(path, "rb").read()))
    files.append((f"{folder}/OFL.txt", open(os.path.join(ROOT, "OFL.txt"), "rb").read()))
    text = open(os.path.join(ROOT, "sources", "release", install), encoding="utf-8").read()
    title = text.splitlines()[0].replace("{version}", version)
    text = text.replace("{version}", version).replace("{underline}", "=" * len(title))
    # Windows line endings, as most downloads are opened on Windows
    text = text.replace("\r\n", "\n").replace("\n", "\r\n")
    files.append((f"{folder}/INSTALL.txt", text.encode("utf-8")))

    zip_path = os.path.join(out_dir, f"{folder}.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        dirs = sorted({name.rsplit("/", 1)[0] + "/" for name, _ in files})
        for d in dirs:
            info = zipfile.ZipInfo(d, DATE)
            info.external_attr = 0o40755 << 16
            z.writestr(info, b"")
        for name, data in sorted(files):
            info = zipfile.ZipInfo(name, DATE)
            info.external_attr = 0o644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, data, compresslevel=9)
    print(f"{zip_path}: {len(files)} files, {os.path.getsize(zip_path):,} bytes")


def main():
    out_dir = sys.argv[1]
    os.makedirs(out_dir, exist_ok=True)
    paths = [p for _, (_, groups) in PACKAGES.items() for _, pat in groups
             for p in glob.glob(os.path.join(ROOT, pat)) if not p.endswith(".woff2")]
    found = {}
    for p in paths:
        for v in font_version(p):
            found.setdefault(v, []).append(os.path.relpath(p, ROOT))
    if len(found) != 1:
        sys.exit("fonts carry different versions:\n" + "\n".join(
            f"  {v}: {', '.join(sorted(set(ps)))}" for v, ps in sorted(found.items())))
    version = next(iter(found))
    if len(sys.argv) > 2 and sys.argv[2] and sys.argv[2].lstrip("v") != version:
        sys.exit(f"requested version {sys.argv[2]} but the fonts are {version}")
    notes = release_notes(version)
    for package, (install, groups) in PACKAGES.items():
        write_zip(out_dir, package, version, install, groups)
    with open(os.path.join(out_dir, "notes.md"), "w", encoding="utf-8") as f:
        f.write(notes)
    with open(os.path.join(out_dir, "version.txt"), "w") as f:
        f.write(version + "\n")
    print(f"version {version}; release text from UPDATES.md in notes.md")


if __name__ == "__main__":
    main()
