"""Shared visual language for every SVG on the profile: deep-space HUD."""

import random
from xml.sax.saxutils import escape

# ── palette ────────────────────────────────────────────────────────────────
BG_0 = "#05071A"  # void
BG_1 = "#0B1033"  # deep indigo
PANEL = "#0A0F2A"
LINE = "#1E2A5A"
CYAN = "#22D3EE"
VIOLET = "#A78BFA"
PINK = "#F472B6"
AMBER = "#FBBF24"
GREEN = "#34D399"
TEXT = "#F1F5FF"   # primary copy — always bright
SOFT = "#C3CEF0"   # secondary copy — still high contrast on the panels
MUTED = "#8B9BC4"  # decoration only (never body text)
DIM = "#5B6894"    # decoration only (lines, orbits)

MONO = "'JetBrains Mono','Fira Code','SFMono-Regular',Consolas,'Liberation Mono','DejaVu Sans Mono',monospace"
SANS = "'Segoe UI','Inter',Ubuntu,'Helvetica Neue',Arial,'DejaVu Sans',sans-serif"


def esc(s) -> str:
    return escape(str(s), {'"': "&quot;"})


def defs(uid: str) -> str:
    """Gradients reused by panels. `uid` keeps ids unique per file."""
    return f"""
  <linearGradient id="{uid}-bg" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{BG_0}"/><stop offset="1" stop-color="{BG_1}"/>
  </linearGradient>
  <linearGradient id="{uid}-edge" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{CYAN}"/><stop offset=".5" stop-color="{VIOLET}"/><stop offset="1" stop-color="{PINK}"/>
  </linearGradient>
  <radialGradient id="{uid}-nebA" cx=".5" cy=".5" r=".5">
    <stop offset="0" stop-color="{VIOLET}" stop-opacity=".35"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="{uid}-nebB" cx=".5" cy=".5" r=".5">
    <stop offset="0" stop-color="{CYAN}" stop-opacity=".22"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="{uid}-nebC" cx=".5" cy=".5" r=".5">
    <stop offset="0" stop-color="{PINK}" stop-opacity=".18"/><stop offset="1" stop-color="{PINK}" stop-opacity="0"/>
  </radialGradient>"""


def base_css() -> str:
    return f"""
  .mono {{ font-family: {MONO}; }}
  .sans {{ font-family: {SANS}; }}
  .tw {{ animation: tw 4s ease-in-out infinite; }}
  @keyframes tw {{ 0%,100% {{ opacity: .25; }} 50% {{ opacity: 1; }} }}
  @media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} }}"""


def stars(w: int, h: int, n: int, seed: int, twinkle: float = 0.25) -> str:
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        x, y = rnd.uniform(0, w), rnd.uniform(0, h)
        r = rnd.choice([0.5, 0.6, 0.7, 0.8, 1.0, 1.2, 1.5])
        col = rnd.choices([TEXT, CYAN, VIOLET, PINK], [8, 2, 2, 1])[0]
        op = rnd.uniform(0.25, 0.9)
        if rnd.random() < twinkle:
            d = rnd.uniform(0, 4)
            dur = rnd.uniform(2.5, 6)
            out.append(
                f'<circle class="tw" cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{col}" '
                f'style="animation-delay:{d:.2f}s;animation-duration:{dur:.2f}s"/>'
            )
        else:
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{col}" opacity="{op:.2f}"/>')
    return "\n    ".join(out)


def hud_corners(x: float, y: float, w: float, h: float, size: float = 14, color: str = CYAN, sw: float = 2) -> str:
    s = size
    return f"""<g fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="square">
    <path d="M{x} {y + s} V{y} H{x + s}"/>
    <path d="M{x + w - s} {y} H{x + w} V{y + s}"/>
    <path d="M{x + w} {y + h - s} V{y + h} H{x + w - s}"/>
    <path d="M{x + s} {y + h} H{x} V{y + h - s}"/>
  </g>"""


def panel(uid: str, w: int, h: int, seed: int, star_count: int = 60, nebula: bool = True) -> str:
    """Rounded deep-space panel with starfield, soft nebula and HUD corners."""
    neb = ""
    if nebula:
        rnd = random.Random(seed * 7)
        neb = (
            f'<ellipse cx="{w * rnd.uniform(.65, .9):.0f}" cy="{h * rnd.uniform(.1, .4):.0f}" rx="{w * .35:.0f}" ry="{h * .6:.0f}" fill="url(#{uid}-nebA)"/>'
            f'<ellipse cx="{w * rnd.uniform(.05, .3):.0f}" cy="{h * rnd.uniform(.6, .95):.0f}" rx="{w * .3:.0f}" ry="{h * .5:.0f}" fill="url(#{uid}-nebB)"/>'
        )
    return f"""<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="14" fill="url(#{uid}-bg)"/>
  <g clip-path="url(#{uid}-clip)">
    {neb}
    {stars(w, h, star_count, seed)}
  </g>
  <rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="14" fill="none" stroke="{LINE}" stroke-width="1.5"/>
  {hud_corners(8, 8, w - 16, h - 16, 14, CYAN, 1.6)}"""


def svg(w: int, h: int, uid: str, body: str, extra_css: str = "", title: str = "", pad_top: int = 0) -> str:
    """`pad_top` adds transparent space above the artwork — used by section
    headers so the README gets a consistent, compact gap between sections."""
    t = f"<title>{esc(title)}</title>" if title else ""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h + pad_top}" viewBox="0 {-pad_top} {w} {h + pad_top}" role="img">
{t}
<defs>{defs(uid)}
  <clipPath id="{uid}-clip"><rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="14"/></clipPath>
</defs>
<style>{base_css()}{extra_css}
</style>
{body}
</svg>
"""
