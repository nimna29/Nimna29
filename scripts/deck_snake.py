#!/usr/bin/env python3
"""Mount the contribution snake inside an Observation Deck panel.

Platane/snk writes a bare, transparent snake SVG. This re-themes it to the deck
palette (gold snake on a blue contribution ramp) and embeds it in a HUD frame,
so the README shows one self-contained, animated panel.

  python scripts/deck_snake.py dist/github-contribution-grid-snake-dark.svg dist/deck-snake.svg

If the snake file is missing or unreadable, a placeholder panel is written.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from deck_kit import GOLD, TEXT, M, T, frame, svg, write  # noqa: E402

# snk's CSS variables: snake, empty cell, cell border, and the four levels
THEME = {"cs": GOLD, "ce": "#122448", "cb": "#ffffff0d", "c0": "#122448",
         "c1": "#1b4a94", "c2": "#2a70c6", "c3": "#4db8ff", "c4": "#eaf6ff"}


def wrap(src):
    m = re.match(r'\s*<svg[^>]*viewBox="([^"]+)"[^>]*>(.*)</svg>\s*$', src, re.S)
    if not m:
        raise ValueError("not a snk svg")
    vb, inner = m.group(1), m.group(2)
    _, _, vw, vh = (float(v) for v in vb.split())
    inner = re.sub(r"--(c[sbe0-4]):[^;}]+", lambda v: f"--{v.group(1)}:{THEME[v.group(1)]}", inner)
    W, oy, pad = 1200, 14, 44
    w = W - pad * 2
    h = w * vh / vw
    H = h + 46
    o = frame(0, oy, W, H, 22, "FLIGHT PATH // LAST 12 MONTHS")
    o += f'<svg x="{pad}" y="{oy + 30}" width="{w}" height="{h:.1f}" viewBox="{vb}">{inner}</svg>'
    return svg(W, int(H + oy + 6), o, title="Snake eating my contribution graph")


def placeholder():
    o = frame(0, 14, 1200, 200, 22, "FLIGHT PATH // LAST 12 MONTHS")
    o += T(600, 110, 30, "Flight path is being plotted", "display", TEXT, "middle") + M(600, 144, 15, "back after the next orbit", GOLD, "middle", 2)
    return svg(1200, 220, o, title="Contribution snake unavailable")


def main():
    src, out = sys.argv[1], sys.argv[2]
    try:
        with open(src, encoding="utf-8") as f:
            content = wrap(f.read())
    except Exception as e:
        print(f"::warning::deck snake not built from {src}: {e}")
        content = placeholder()
    write(os.path.abspath(out), content)


if __name__ == "__main__":
    main()
