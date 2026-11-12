#!/usr/bin/env python3
"""Dev-only: rebuild scripts/deck_data/{glyphs,icons}.json from the portfolio.

The Observation Deck SVGs draw their text as outlined glyphs, so GitHub shows
the portfolio's own typefaces (Calistoga, Space Grotesk - both SIL OFL) without
loading a webfont. This script lifts those outlines, and the brand marks the
tech arsenal uses, out of the portfolio repo into two small JSON files. The
normal build scripts then need nothing but the Python standard library.

  pip install fonttools brotli
  python scripts/deck_extract.py [path/to/nimna-niwarthana]
"""
import json
import os
import sys

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

sys.path.insert(0, os.path.dirname(__file__))
from deck_content import STACK  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
PORT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "..", "nimna-niwarthana")
NM = os.path.join(PORT, "node_modules")
OUT = os.path.join(HERE, "deck_data")

CHARS = "".join(chr(c) for c in range(32, 127)) + "·°"
SG = os.path.join(NM, "@fontsource-variable", "space-grotesk", "files", "space-grotesk-latin-wght-normal.woff2")
FONTS = {
    "display": (os.path.join(NM, "@fontsource", "calistoga", "files", "calistoga-latin-400-normal.woff2"), None),
    "ui4": (SG, 400), "ui5": (SG, 500), "ui6": (SG, 600), "ui7": (SG, 700),
}


def glyphs():
    out = {}
    for key, (path, wght) in FONTS.items():
        f = TTFont(path)
        if wght is not None:
            f = instancer.instantiateVariableFont(f, {"wght": wght})
        gs, cmap = f.getGlyphSet(), f.getBestCmap()
        table = {}
        for ch in CHARS:
            g = cmap.get(ord(ch))
            if g is None:
                continue
            pen = SVGPathPen(gs, ntos=lambda v: f"{v:.0f}")
            gs[g].draw(pen)
            table[ch] = [f["hmtx"][g][0], pen.getCommands()]
        out[key] = {"upm": f["head"].unitsPerEm, "g": table}
    return out


def icons():
    src = open(os.path.join(PORT, "src", "pages", "About", "AboutSectionThree", "stackIcons.ts"), encoding="utf8").read()
    allicons, _ = json.JSONDecoder().raw_decode(src[src.index("= {") + 2:])
    want = sorted({key for _, tools in STACK for _, key in tools if key})
    missing = [k for k in want if k not in allicons]
    if missing:
        raise SystemExit(f"not in the portfolio's stackIcons.ts: {missing}")
    return {k: allicons[k] for k in want}


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, data in (("glyphs.json", glyphs()), ("icons.json", icons())):
        p = os.path.join(OUT, name)
        with open(p, "w", encoding="utf8", newline="\n") as fh:
            json.dump(data, fh, ensure_ascii=False, separators=(",", ":"))
        print(f"wrote scripts/deck_data/{name}  ({os.path.getsize(p) / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
