#!/usr/bin/env python3
"""Generate the static artwork for the Observation Deck README design.

Run from the repo root:  python scripts/deck_assets.py
Output goes to ./assets/deck. Copy lives in scripts/deck_content.py.

Sizing rule: every SVG is drawn on a 1200-unit canvas and shown at roughly 0.7x
in GitHub's ~840px column, so body copy is >= 21 units where it matters and
labels are >= 16 units.
"""
import base64
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from deck_content import (  # noqa: E402
    CURRENTLY, EDUCATION, FUN_FACT, HEADINGS, LINKS, MONOGRAM, NAME, PASSIONS, PROJECTS, ROLES, SITE, STACK, TAGLINE,
)
from deck_kit import (  # noqa: E402
    CORE, ELECTRIC, FAINT, GOLD, GOLD2, GREEN, ICE, MUTED, ROOT, TEXT, M, T, TP, brand, chamfer, chip, clip, frame, icon,
    kicker, lin, mw, plate, rad, rr, spark, stars, svg, tab, tab_w, tw, uid, write,
)

OUT = os.path.join(ROOT, "assets", "deck")
C30 = math.cos(math.radians(30))


# ═════════════════════════════ ISOMETRIC ART ═════════════════════════════
class Iso:
    """Tiny isometric projector: x runs down-right, y down-left, z up."""

    def __init__(self, ox, oy, sc):
        self.ox, self.oy, self.sc = ox, oy, sc

    def p(self, x, y, z=0.0):
        return self.ox + (x - y) * C30 * self.sc, self.oy + (x + y) * .5 * self.sc - z * self.sc

    def poly(self, pts, fill, extra=""):
        d = " ".join(f"{a:.1f},{b:.1f}" for a, b in (self.p(*q) for q in pts))
        return f'<polygon points="{d}" fill="{fill}" stroke="{fill}" stroke-width="1.2" stroke-linejoin="round" {extra}/>'

    def box(self, x, y, z, w, d, h, top, left, right):
        return (self.poly([(x, y + d, z + h), (x + w, y + d, z + h), (x + w, y + d, z), (x, y + d, z)], left)
                + self.poly([(x + w, y, z + h), (x + w, y + d, z + h), (x + w, y + d, z), (x + w, y, z)], right)
                + self.poly([(x, y, z + h), (x + w, y, z + h), (x + w, y + d, z + h), (x, y + d, z + h)], top))

    def disc(self, x, y, z, r, fill, extra=""):
        cx, cy = self.p(x, y, z)
        return f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{r * self.sc * 1.2247:.1f}" ry="{r * self.sc * .7071:.1f}" fill="{fill}" {extra}/>'


def rocket(bx, by, k=1.0, flame=False):
    """Upright rocket, base centre at (bx, by), 150 units tall before scaling."""
    body = lin([(0, "#ffffff"), (.5, "#dfe9f8"), (1, "#8196c2")])
    fin = lin([(0, "#5aa2f0"), (1, "#1d3f86")])
    nose = lin([(0, "#f6dfa6"), (.5, GOLD), (1, "#8a6525")])
    win = rad([(0, "#c8ecff"), (.5, ELECTRIC), (1, "#123a7a")], .35, .35, .75)
    bp = "M0 -150C14 -134 20 -104 20 -70L18 -12Q18 -6 12 -6H-12Q-18 -6 -18 -12L-20 -70C-20 -104 -14 -134 0 -150Z"
    bc = clip(f'<path d="{bp}"/>')
    fl = ""
    if flame:
        fo = lin([(0, "#fff7d6"), (.35, GOLD), (1, "#f97316", 0)], 0, 0, 0, 1)
        fi = lin([(0, "#ffffff"), (1, "#fde68a", 0)], 0, 0, 0, 1)
        fl = (f'<g class="dk-flame"><path d="M-13 0C-14 30 -6 70 0 124C6 70 14 30 13 0Z" fill="{fo}"/>'
              f'<path d="M-7 0C-7 20 -3 44 0 76C3 44 7 20 7 0Z" fill="{fi}"/></g>')
    return (f'<g transform="translate({bx:.1f} {by:.1f}) scale({k})">{fl}'
            f'<path d="M-18 -44C-32 -34 -36 -16 -34 4L-17 -10Z M18 -44C32 -34 36 -16 34 4L17 -10Z" fill="{fin}"/>'
            f'<path d="M-10 -7H10L13 3H-13Z" fill="#26375f"/><path d="{bp}" fill="{body}"/>'
            f'<g clip-path="{bc}"><rect x="-24" y="-154" width="48" height="40" fill="{nose}"/><rect x="-24" y="-40" width="48" height="7" fill="{nose}"/></g>'
            f'<circle cx="0" cy="-88" r="11" fill="#eef3fc" stroke="#6d7aa8" stroke-width="1.5"/><circle cx="0" cy="-88" r="7.5" fill="{win}"/>'
            f'<circle class="dk-glint" cx="-2.6" cy="-90.600" r="2.4" fill="#fff"/>'
            f'<path d="M-13 -116C-16 -100 -17 -80 -16 -60" stroke="#fff" stroke-width="2.5" stroke-linecap="round" fill="none" opacity=".7"/></g>')


def planet(cx, cy, r):
    f = rad([(0, "#d9efff"), (.4, "#63b0f5"), (.8, "#1f4c9c"), (1, "#0b1f4a")], .32, .28, .85)
    ring = f'transform="rotate(-18 {cx} {cy})" fill="none" stroke="{GOLD}" stroke-width="4"'
    return (f'<g class="dk-bob"><path d="M{cx - r * 1.8:.1f} {cy} A{r * 1.8:.1f} {r * .5:.1f} 0 0 1 {cx + r * 1.8:.1f} {cy}" {ring} stroke-opacity=".5"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{f}"/>'
            f'<path d="M{cx - r * 1.8:.1f} {cy} A{r * 1.8:.1f} {r * .5:.1f} 0 0 0 {cx + r * 1.8:.1f} {cy}" {ring} stroke-linecap="round"/></g>')


def satellite(cx, cy, rot=-18):
    return (f'<g class="dk-sat"><g transform="rotate({rot} {cx} {cy})">' + rr(cx - 46, cy - 9, 30, 18, 3, fill=ELECTRIC) + rr(cx + 16, cy - 9, 30, 18, 3, fill=ELECTRIC)
            + f'<path d="M{cx - 36} {cy - 9} v18 M{cx - 26} {cy - 9} v18 M{cx + 26} {cy - 9} v18 M{cx + 36} {cy - 9} v18" stroke="#0b2a57" stroke-width="1.5"/>'
            + rr(cx - 13, cy - 13, 26, 26, 6, fill="#e6eefb") + rr(cx - 13, cy + 3, 26, 10, 4, fill="#a9bddf")
            + f'<circle class="dk-node" cx="{cx}" cy="{cy - 3}" r="4.5" fill="{GOLD}"/></g></g>')


def diorama(ox, oy, sc):
    """Isometric launch pad: rocket, radar dish, server rack, payload crate."""
    I = Iso(ox, oy, sc)
    o = f'<ellipse class="dk-shadow" cx="{ox}" cy="{oy + sc * 10 + 58:.1f}" rx="{sc * 8.2:.1f}" ry="19" fill="#000" opacity=".4"/>'
    o += '<g class="dk-float">'
    o += f'<ellipse class="dk-glow" cx="{ox}" cy="{oy + sc * 10 + 32:.1f}" rx="{sc * 9:.1f}" ry="34" fill="{rad([(0, ELECTRIC, .4), (1, ELECTRIC, 0)])}"/>'
    # platform
    o += I.box(0, 0, 0, 10, 10, .9, "#22407a", "#122550", "#0b1838")
    o += I.poly([(0, 0, .9), (10, 0, .9), (10, 10, .9), (0, 10, .9)], lin([(0, "#2c519a"), (1, "#1a3266")], 0, 0, 1, 1))
    grid = ""
    for v in (2.5, 5, 7.5):
        (a, b), (c, d) = I.p(v, .4, .9), I.p(v, 9.6, .9)
        (e, f), (g, h) = I.p(.4, v, .9), I.p(9.6, v, .9)
        grid += f"M{a:.1f} {b:.1f} L{c:.1f} {d:.1f}M{e:.1f} {f:.1f} L{g:.1f} {h:.1f}"
    o += f'<path d="{grid}" stroke="#fff" stroke-opacity=".07"/>'
    for n, t in enumerate((1.5, 3.5, 5.5, 7.5, 9)):
        for q in ((t, 10, .45), (10, t, .45)):
            px, py = I.p(*q)
            o += f'<circle class="dk-tw" cx="{px:.1f}" cy="{py:.1f}" r="2.2" fill="{GOLD}" style="animation-delay:{n * .35:.2f}s;animation-duration:2.8s"/>'
    # launch pad + rocket
    o += I.disc(3.4, 3.4, .9, 2.5, "#0d1d42") + I.disc(3.4, 3.4, 1.15, 2.5, "#2f55a0")
    o += I.disc(3.4, 3.4, 1.15, 2.0, "#1a3570", f'class="dk-march" stroke="{GOLD}" stroke-width="2" stroke-dasharray="7 6"')
    bx, by = I.p(3.4, 3.4, 1.15)
    o += f'<ellipse cx="{bx:.1f}" cy="{by:.1f}" rx="22" ry="10" fill="#081530" opacity=".7"/>'
    for i, cls in enumerate(("dk-steam-l", "dk-steam-r", "dk-steam-l", "dk-steam-r")):
        o += f'<circle class="{cls}" cx="{bx + (-12 if i % 2 == 0 else 12):.1f}" cy="{by - 2:.1f}" r="8" fill="#dfe9f8" style="animation-delay:{i * .8}s"/>'
    o += rocket(bx, by + 2, sc / 20)
    # server rack with blinking LEDs
    o += I.box(6.6, 1.4, .9, 1.9, 1.9, 3.3, "#4d79c9", "#213f7c", "#142a58")
    for k in range(4):
        z = 1.35 + k * .7
        o += I.poly([(6.8, 3.3, z + .42), (8.3, 3.3, z + .42), (8.3, 3.3, z), (6.8, 3.3, z)], "#0a1630")
        for j, col in enumerate((ELECTRIC, GOLD if k % 2 else "#35d07f", ELECTRIC)):
            px, py = I.p(7.1 + j * .45, 3.3, z + .21)
            o += (f'<circle class="dk-led" cx="{px:.1f}" cy="{py:.1f}" r="2.3" fill="{col}" '
                  f'style="animation-delay:{(k * 3 + j) * .37 % 2.3:.2f}s;animation-duration:{1.3 + (k + j) % 3 * .5:.1f}s"/>')
    # radar dish
    px, py = I.p(2.3, 7.4, .9)
    dg = lin([(0, "#f4f9ff"), (1, "#8fb3e6")], 0, 0, 1, 1)
    arcs = "".join(
        f'<path class="dk-sig" style="animation-delay:{i * .35:.2f}s" d="M{px - 12 - i * 8:.1f} {py - 92 - i * 9:.1f} Q{px:.1f} {py - 106 - i * 13:.1f} {px + 12 + i * 8:.1f} {py - 92 - i * 9:.1f}" '
        f'fill="none" stroke="{ELECTRIC}" stroke-width="2.5" stroke-linecap="round"/>' for i in range(3))
    o += (f'<ellipse cx="{px:.1f}" cy="{py:.1f}" rx="17" ry="8" fill="#0d1d42"/><path d="M{px - 5:.1f} {py:.1f} L{px - 2:.1f} {py - 40:.1f} H{px + 2:.1f} L{px + 5:.1f} {py:.1f} Z" fill="#8196c2"/>'
          f'<g class="dk-dish" style="transform-origin:{px:.1f}px {py - 44:.1f}px"><g transform="rotate(-32 {px:.1f} {py - 48:.1f})">'
          f'<ellipse cx="{px:.1f}" cy="{py - 48:.1f}" rx="32" ry="15" fill="#5f7cb0"/><ellipse cx="{px:.1f}" cy="{py - 52:.1f}" rx="32" ry="15" fill="{dg}"/>'
          f'<ellipse cx="{px:.1f}" cy="{py - 52:.1f}" rx="22" ry="9" fill="#b7cdee"/><path d="M{px:.1f} {py - 52:.1f} V{py - 78:.1f}" stroke="#eaf2ff" stroke-width="2.5"/>'
          f'<circle cx="{px:.1f}" cy="{py - 80:.1f}" r="4.5" fill="{GOLD}"/>{arcs}</g></g>')
    # payload crate
    o += I.box(6.7, 6.7, .9, 1.7, 1.7, 1.4, "#f3d590", GOLD, "#9c742b")
    o += I.poly([(7.35, 6.7, 2.31), (7.75, 6.7, 2.31), (7.75, 8.4, 2.31), (7.35, 8.4, 2.31)], "#a67c2e")
    o += I.poly([(7.35, 8.4, 2.3), (7.75, 8.4, 2.3), (7.75, 8.4, .9), (7.35, 8.4, .9)], "#8a6525")
    # beacon
    px, py = I.p(9.2, .8, .9)
    o += (f'<path d="M{px:.1f} {py:.1f} V{py - 44:.1f}" stroke="#8196c2" stroke-width="3"/>'
          f'<circle class="dk-beacon" cx="{px:.1f}" cy="{py - 46:.1f}" r="12" fill="{ELECTRIC}"/><circle cx="{px:.1f}" cy="{py - 46:.1f}" r="5" fill="{CORE}"/>')
    return o + "</g>"


# ═════════════════════════════ CARD MINIATURES ═════════════════════════════
def _cyl(I, x, y, z, r, h, top):
    """Upright cylinder standing on (x, y, z)."""
    cx, cb = I.p(x, y, z)
    _, ct = I.p(x, y, z + h)
    rx, ry = r * I.sc * 1.2247, r * I.sc * .7071
    return (f'<ellipse cx="{cx:.1f}" cy="{cb:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="#1d3f86"/>'
            f'<rect x="{cx - rx:.1f}" y="{ct:.1f}" width="{rx * 2:.1f}" height="{cb - ct:.1f}" fill="{lin([(0, "#5aa2f0"), (1, "#1d3f86")])}"/>'
            f'<ellipse cx="{cx:.1f}" cy="{ct:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="{top}"/>')


def _art_library(I):
    """Stack of books with a spinning disc on top - catalogues, media, docs."""
    o = I.box(.6, .8, .45, 2.8, 2.2, .5, "#3f7fd6", "#eef4ff", "#1d3f86")
    o += I.box(.9, 1.0, .95, 2.4, 1.9, .45, "#f3d590", "#f4f8ff", "#9c742b")
    o += I.box(.7, .7, 1.4, 2.5, 2.1, .4, "#63b0f5", "#eef4ff", "#1f4c9c")
    o += I.disc(1.95, 1.75, 1.82, .8, "#dfe9f8", f'class="dk-march" stroke="{GOLD}" stroke-width="2" stroke-dasharray="7 6"')
    o += I.disc(1.95, 1.75, 1.82, .24, GOLD)
    sx, sy = I.p(1.95, 1.75, 3.5)
    return o + spark(round(sx, 1), round(sy, 1), 8, GOLD, 0)


def _art_scanner(I):
    """A sample cube inside a scan frame, swept by a light plane - detection, analysis."""
    def post(x, y):
        (a, b), (c, d) = I.p(x, y, .45), I.p(x, y, 2.75)
        return f'<path d="M{a:.1f} {b:.1f} L{c:.1f} {d:.1f}" stroke="#8196c2" stroke-width="2.2" stroke-linecap="round"/>'
    ring = " ".join(f"{a:.1f},{b:.1f}" for a, b in (I.p(x, y, 2.75) for x, y in ((.5, .5), (3.5, .5), (3.5, 3.5), (.5, 3.5))))
    o = post(.5, .5) + post(3.5, .5) + post(.5, 3.5)
    o += I.box(1.2, 1.2, .45, 1.6, 1.6, 1.5, "#4d79c9", "#213f7c", "#142a58")
    o += I.poly([(.5, .5, .75), (3.5, .5, .75), (3.5, 3.5, .75), (.5, 3.5, .75)], ELECTRIC, 'class="dk-scanp" fill-opacity=".28" stroke-opacity=".9"')
    o += post(3.5, 3.5) + f'<polygon points="{ring}" fill="none" stroke="#8196c2" stroke-width="1.6" stroke-linejoin="round"/>'
    px, py = I.p(3.5, 3.5, 2.75)
    return o + f'<circle class="dk-led" cx="{px:.1f}" cy="{py:.1f}" r="3.4" fill="#35d07f"/>'


def _art_database(I):
    """Data blocks dropping into a three-tier store - datasets, pipelines, tooling."""
    o = "".join(_cyl(I, 2, 2, .45 + n * .85, 1.15, .7, top) for n, top in enumerate(("#8fc4f8", "#bfe3ff", "#f3d590")))
    for d, cols in ((0, ("#9fd4ff", ELECTRIC, "#2a70c6")), (1.3, ("#f3d590", GOLD, "#9c742b"))):
        o += f'<g class="dk-drop" style="animation-delay:{d}s">{I.box(1.75, 1.75, 3.05, .5, .5, .5, *cols)}</g>'
    return o


def _art_chip(I):
    """A microchip under a roving magnifier - reverse engineering, research."""
    o = I.box(.7, .7, .45, 2.6, 2.6, .42, "#1c3a72", "#0d1d42", "#0a1630")
    o += I.poly([(1.3, 1.3, .88), (2.7, 1.3, .88), (2.7, 2.7, .88), (1.3, 2.7, .88)], "#3b66b5")
    o += I.poly([(1.65, 1.65, .89), (2.35, 1.65, .89), (2.35, 2.35, .89), (1.65, 2.35, .89)], ELECTRIC, 'class="dk-glow"')
    for t in (1.05, 1.65, 2.25, 2.85):
        o += I.box(t - .13, 3.3, .45, .26, .32, .16, "#f3d590", GOLD, "#9c742b") + I.box(3.3, t - .13, .45, .32, .26, .16, "#f3d590", GOLD, "#9c742b")
    lx, ly = I.p(2, 2, 2.5)
    return o + (f'<g class="dk-lens"><path d="M{lx + 11:.1f} {ly + 11:.1f} l13 13" stroke="{GOLD}" stroke-width="5" stroke-linecap="round"/>'
                f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="15" fill="{ELECTRIC}" fill-opacity=".16" stroke="#eef4ff" stroke-width="3.5"/>'
                f'<path d="M{lx - 8.5:.1f} {ly - 2:.1f} A9 9 0 0 1 {lx - 2:.1f} {ly - 8.5:.1f}" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" opacity=".8"/></g>')


def _art_rocket(I):
    """Rocket on its pad - launches, products, anything shipped."""
    bx, by = I.p(2, 2, .45)
    return (I.disc(2, 2, .45, 1.3, "#16305f", f'class="dk-march" stroke="{GOLD}" stroke-width="2" stroke-dasharray="7 6"')
            + rocket(bx, by + 2, I.sc / 30))


def _art_planet(I):
    """Ringed planet hovering over a pad - the neutral default."""
    bx, by = I.p(2, 2, .45)
    return I.disc(2, 2, .45, 1.15, "#16305f") + planet(round(bx, 1), round(by - 42, 1), 19)


ART = {"library": _art_library, "scanner": _art_scanner, "database": _art_database,
       "chip": _art_chip, "rocket": _art_rocket, "planet": _art_planet}


def miniature(kind, cx, cy, sc=14, delay=0.0):
    """Small isometric scene on a floating 4x4 slab; (cx, cy) is the slab's back corner."""
    if kind not in ART:
        raise SystemExit(f"unknown card art {kind!r} - pick one of: {', '.join(ART)}")
    I = Iso(cx, cy, sc)
    o = f'<ellipse class="dk-shadow" cx="{cx}" cy="{cy + sc * 4 + 17:.1f}" rx="{sc * 3.1:.1f}" ry="7" fill="#000" opacity=".4" style="animation-delay:{delay}s"/>'
    o += f'<g class="dk-hover" style="animation-delay:{delay}s">'
    o += I.box(0, 0, 0, 4, 4, .45, "#22407a", "#122550", "#0b1838")
    o += I.poly([(0, 0, .45), (4, 0, .45), (4, 4, .45), (0, 4, .45)], lin([(0, "#2c519a"), (1, "#1a3266")], 0, 0, 1, 1))
    for n, q in enumerate(((1, 4, .22), (3, 4, .22), (4, 1, .22), (4, 3, .22))):
        px, py = I.p(*q)
        o += f'<circle class="dk-tw" cx="{px:.1f}" cy="{py:.1f}" r="1.8" fill="{GOLD}" style="animation-delay:{n * .5}s;animation-duration:2.8s"/>'
    return o + ART[kind](I) + "</g>"


ART_CSS = """
.dk-float{animation:dk-float 7s ease-in-out infinite}
.dk-bob{animation:dk-float 5.5s ease-in-out -2s infinite}
@keyframes dk-float{0%,100%{transform:translateY(0)}50%{transform:translateY(-7px)}}
.dk-shadow{transform-box:fill-box;transform-origin:center;animation:dk-shadow 7s ease-in-out infinite}
@keyframes dk-shadow{0%,100%{transform:scale(1);opacity:.4}50%{transform:scale(.88);opacity:.26}}
.dk-glow{animation:dk-glow 3.5s ease-in-out infinite}
@keyframes dk-glow{0%,100%{opacity:.55}50%{opacity:1}}
.dk-march{animation:dk-march 2.6s linear infinite}
@keyframes dk-march{to{stroke-dashoffset:-26}}
.dk-led{animation:dk-led 1.6s steps(1) infinite}
@keyframes dk-led{0%,62%{opacity:1}63%,100%{opacity:.18}}
.dk-sig{opacity:0;animation:dk-sig 2.4s ease-out infinite}
@keyframes dk-sig{0%{opacity:0}18%{opacity:.95}60%,100%{opacity:0}}
.dk-dish{animation:dk-dish 9s ease-in-out infinite}
@keyframes dk-dish{0%,100%{transform:rotate(-5deg)}50%{transform:rotate(6deg)}}
.dk-beacon{transform-box:fill-box;transform-origin:center;animation:dk-beacon 2s ease-out infinite}
@keyframes dk-beacon{0%{transform:scale(.4);opacity:.75}100%{transform:scale(2);opacity:0}}
.dk-sat{animation:dk-sat 13s ease-in-out infinite}
@keyframes dk-sat{0%,100%{transform:translate(0,0)}50%{transform:translate(-24px,10px)}}
.dk-glint{animation:dk-node 2.4s ease-in-out infinite}
.dk-steam-l,.dk-steam-r{transform-box:fill-box;transform-origin:center;opacity:0;animation:dk-steam-l 3.2s ease-out infinite}
.dk-steam-r{animation-name:dk-steam-r}
@keyframes dk-steam-l{0%{transform:translate(0,0) scale(.3);opacity:0}15%{opacity:.5}100%{transform:translate(-38px,-5px) scale(1.5);opacity:0}}
@keyframes dk-steam-r{0%{transform:translate(0,0) scale(.3);opacity:0}15%{opacity:.5}100%{transform:translate(38px,-5px) scale(1.5);opacity:0}}
.dk-shoot{opacity:0;animation:dk-shoot 8s ease-in infinite}
@keyframes dk-shoot{0%{transform:translate(0,0);opacity:0}3%{opacity:1}13%{transform:translate(-380px,190px);opacity:0}100%{opacity:0}}
.dk-status{animation:dk-node 1.8s ease-in-out infinite}
.dk-scan{animation:dk-scan 5s ease-in-out infinite}
@keyframes dk-scan{0%,100%{transform:translateX(0)}50%{transform:translateX(320px)}}
.dk-hover{animation:dk-hover 7s ease-in-out infinite}
@keyframes dk-hover{0%,100%{transform:translateY(0)}50%{transform:translateY(-4px)}}
.dk-scanp{animation:dk-scanp 3.2s ease-in-out infinite}
@keyframes dk-scanp{0%,100%{transform:translateY(0)}50%{transform:translateY(-24px)}}
.dk-drop{opacity:0;animation:dk-drop 2.6s ease-in infinite}
@keyframes dk-drop{0%{transform:translateY(-24px);opacity:0}20%{opacity:1}75%{transform:translateY(0);opacity:1}100%{transform:translateY(0);opacity:0}}
.dk-lens{animation:dk-lens 5s ease-in-out infinite}
@keyframes dk-lens{0%,100%{transform:translate(-9px,3px)}50%{transform:translate(10px,-3px)}}
.dk-rise{animation:dk-rise 5s ease-in-out infinite}
@keyframes dk-rise{0%,100%{transform:translateY(8px)}50%{transform:translateY(-8px)}}
.dk-shake{animation:dk-shake .16s linear infinite}
@keyframes dk-shake{0%,100%{transform:translateX(-.7px)}50%{transform:translateX(.7px)}}
.dk-flame{transform-box:fill-box;transform-origin:50% 0%;animation:dk-flame .14s ease-in-out infinite alternate}
@keyframes dk-flame{from{transform:scale(1,1)}to{transform:scale(.84,1.16)}}
.dk-puff{transform-box:fill-box;transform-origin:50% 100%;animation:dk-puff 2.4s ease-in-out infinite alternate}
@keyframes dk-puff{from{transform:scale(.86)}to{transform:scale(1.14)}}
.dk-streak{opacity:0;animation:dk-streak 1.3s linear infinite}
@keyframes dk-streak{0%{transform:translateY(-16px);opacity:0}30%{opacity:.7}100%{transform:translateY(34px);opacity:0}}"""


# ═════════════════════════════ HERO ═════════════════════════════
def hero():
    W, oy, H = 1200, 14, 430
    cp = clip(f'<path d="{chamfer(0, oy, W, H, 30)}"/>')
    o = frame(0, oy, W, H, 30, "IDENT // NN-29")
    o += (f'<g clip-path="{cp}">{stars(W, H, 130, 29, y0=oy)}'
          f'<ellipse cx="972" cy="{oy + 230}" rx="330" ry="260" fill="{rad([(0, "#2a66c4", .32), (1, "#2a66c4", 0)])}"/>'
          f'<ellipse cx="160" cy="{oy}" rx="420" ry="200" fill="{rad([(0, ELECTRIC, .12), (1, ELECTRIC, 0)])}"/>'
          f'<g class="dk-shoot"><path d="M700 {oy + 30} l56 -28" stroke="{TEXT}" stroke-width="2" stroke-linecap="round"/></g></g>')
    # copy
    kw = mw("WELCOME ABOARD", 16, 5)
    o += M(104, oy + 86, 16, "WELCOME ABOARD", ELECTRIC, ls=5, w=600, op=.9)
    o += f'<path d="M64 {oy + 81} h28 M{104 + kw + 12:.1f} {oy + 81} h28" stroke="{ELECTRIC}" stroke-opacity=".55"/>'
    o += TP(62, oy + 174, 76, NAME, fill=lin([(0, TEXT), (.3, TEXT), (.75, GOLD), (1, GOLD2)]))
    o += T(64, oy + 222, 22.5, TAGLINE, "ui4", MUTED)
    x = 64
    for r in ROLES:
        c, w = chip(x, oy + 256, r)
        o += c
        x += w + 12
    ticks = "".join(f"M{64 + i * 8} {oy + 362} v{-10 if i % 5 == 0 else -5}" for i in range(41))
    o += f'<path d="{ticks}" stroke="{ELECTRIC}" stroke-opacity=".4"/>'
    o += f'<path class="dk-scan" d="M64 {oy + 366} l-5 7 h10 z" fill="{GOLD}"/>'
    o += f'<circle class="dk-status" cx="412" cy="{oy + 356}" r="4" fill="{GREEN}"/>' + M(424, oy + 361, 14, "ALL SYSTEMS NOMINAL", MUTED, ls=3)
    # art
    o += diorama(972, oy + 152, 18.5)
    o += planet(836, oy + 84, 27) + satellite(1108, oy + 96)
    o += spark(770, oy + 176, 9, GOLD, 0) + spark(1150, oy + 222, 7, ICE, 1.1) + spark(905, oy + 40, 6, ICE, 2) + spark(1040, oy + 46, 8, GOLD, .6) + spark(806, oy + 282, 6, ICE, 1.7)
    return svg(W, H + oy + 6, o, ART_CSS, f"{NAME} - " + " · ".join(ROLES))


# ═════════════════════════════ LINKS ═════════════════════════════
def link(i, kick, title, sub, ic):
    """Four of these sit edge to edge at 25% width each, so the 16-unit gutters
    are baked in: every file is a 300-unit slot with its button offset inside."""
    W, H, bw = 300, 88, 288
    x = i * (W - bw) / 3
    col = GOLD if i % 2 else ELECTRIC
    o = frame(x + .75, .75, bw - 1.5, H - 1.5, 14, nodes=False, brk=False, ring=.5)
    o += plate(x + 16, 18, 52, ic, col) + M(x + 84, 32, 13, kick.upper(), GOLD, ls=3, w=600)
    o += T(x + 84, 58, 23, title, "ui6", TEXT) + T(x + 84, 77, 15, sub, "ui4", MUTED) + icon("arrow", x + bw - 34, 14, 18, ELECTRIC)
    return svg(W, H, o, title=f"{title} - {sub}")


# ═════════════════════════════ CREW PROFILE ═════════════════════════════
def crew():
    W, oy, H = 1200, 14, 462
    o = frame(0, oy, W, H, 24, "CREW PROFILE")
    with open(os.path.join(ROOT, "assets", "src", "portrait.jpg"), "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    px, py, pw, ph = 40, oy + 44, 196, 236
    cp = clip(f'<path d="{chamfer(px, py, pw, ph, 18)}"/>')
    o += f'<image href="data:image/jpeg;base64,{b64}" x="{px}" y="{py}" width="{pw}" height="{ph}" preserveAspectRatio="xMidYMid slice" clip-path="{cp}"/>'
    o += f'<path d="{chamfer(px, py, pw, ph, 18)}" fill="none" stroke="{GOLD}" stroke-opacity=".85" stroke-width="1.5"/>'
    o += T(px + pw / 2, oy + 316, 20, NAME, "ui6", TEXT, "middle")
    duty = "NN-29 // ON DUTY"
    o += (f'<circle class="dk-status" cx="{px + pw / 2 + 8 - mw(duty, 12.5, 2) / 2 - 12:.1f}" cy="{oy + 337.5}" r="4" fill="{GREEN}"/>'
          + M(px + pw / 2 + 8, oy + 342, 12.5, duty, GOLD, "middle", 2, 600))
    o += f'<path d="M270 {oy + 40} V{oy + 372}" stroke="{ELECTRIC}" stroke-opacity=".3" stroke-dasharray="6 6"/>'
    x0, x1 = 306, 1160

    def sub(y, label):
        return (M(x0, y, 13, label, GOLD, ls=3, w=600)
                + f'<path d="M{x0 + mw(label, 13, 3) + 16:.1f} {y - 4} H{x1}" stroke="{ELECTRIC}" stroke-opacity=".4" stroke-dasharray="6 6"/>')

    o += sub(oy + 54, "EDUCATION")
    for i, (title, org, period) in enumerate(EDUCATION):
        x, y = x0 + i * 436, oy + 74
        o += plate(x, y, 60, "cap", GOLD)
        o += T(x + 78, y + 22, 24, title[0], "display", TEXT) + T(x + 78, y + 50, 24, title[1], "display", TEXT)
        o += T(x + 78, y + 76, 17, org, "ui4", MUTED) + M(x + 78, y + 97, 13, period, FAINT, ls=1)
    o += sub(oy + 204, "CURRENTLY")
    for i, (ic, kick, title, s) in enumerate(CURRENTLY):
        x, y = x0 + i * 436, oy + 224
        o += plate(x, y, 60, ic, ELECTRIC) + M(x + 78, y + 12, 12.5, kick.upper(), GOLD, ls=3, w=600)
        o += T(x + 78, y + 41, 26, title, "display", TEXT) + T(x + 78, y + 65, 17, s, "ui4", MUTED)
    o += sub(oy + 318, "PASSIONATE ABOUT")
    cw = (x1 - x0 - 3 * 14) / 4
    for i, (ic, label) in enumerate(PASSIONS):
        x, y = x0 + i * (cw + 14), oy + 336
        col = GOLD if i in (1, 2) else ELECTRIC
        w = tw(label, 18.5, "ui5") + 32
        o += f'<path d="{chamfer(x, y, cw, 46, 10)}" fill="{col}" fill-opacity=".08" stroke="{col}" stroke-opacity=".55" stroke-width="1.2"/>'
        o += icon(ic, x + (cw - w) / 2, y + 12, 22, col) + T(x + (cw - w) / 2 + 32, y + 29.5, 18.5, label, "ui5", TEXT)
    fy = oy + H - 34
    o += f'<path d="M40 {fy - 26} H{x1}" stroke="{ELECTRIC}" stroke-opacity=".3" stroke-dasharray="6 6"/>'
    o += icon("bolt", 40, fy - 15, 20, GOLD) + M(68, fy, 13, "FUN FACT", GOLD, ls=3, w=600)
    fs = min(17.5, 17.5 * (x1 - 172) / tw(FUN_FACT, 17.5, "ui4"))
    o += T(172, fy, fs, FUN_FACT, "ui4", MUTED)
    return svg(W, H + oy + 6, o, ".dk-status{animation:dk-node 1.8s ease-in-out infinite}", "Crew profile - " + NAME)


# ═════════════════════════════ TECH ARSENAL ═════════════════════════════
def stack():
    W, cols, gap = 1200, 8, 16
    tw_, th = (W - (cols - 1) * gap) / cols, 98
    o, y = "", 1.0
    for label, tools in STACK:
        if len(tools) % cols:
            raise SystemExit(f"stack category {label!r} has {len(tools)} tools - keep it a multiple of {cols}")
        lab = label.upper()
        units = f"{len(tools):02d} UNITS"
        o += tab(0.75, y, lab) + f'<path d="M{tab_w(lab) + 14:.1f} {y + 13} H{W - mw(units, 12.5, 2) - 14:.1f}" stroke="{ELECTRIC}" stroke-opacity=".55" stroke-dasharray="6 6"/>'
        o += M(W, y + 17.5, 12.5, units, "#3d8fd9", "end", 2, 600)
        y += 26 + 12
        for i, (name, key) in enumerate(tools):
            x, ty = (i % cols) * (tw_ + gap), y + (i // cols) * (th + 14)
            o += frame(x + .75, ty, tw_ - 1.5, th, 12, nodes=False, brk=False, ring=.4)
            b = brand(key, x + tw_ / 2 - 21, ty + 13, 42)
            if not b:
                mono = MONOGRAM.get(name, name[:2].upper())
                b = (f'<path d="{chamfer(x + tw_ / 2 - 21, ty + 13, 42, 42, 8)}" fill="{GOLD}" fill-opacity=".1" stroke="{GOLD}" stroke-opacity=".6"/>'
                     + T(x + tw_ / 2, ty + 40.5, 18, mono, "ui7", GOLD, "middle", 1))
            fs = min(16, 16 * (tw_ - 14) / tw(name, 16, "ui5"))
            o += b + T(x + tw_ / 2, ty + 82, fs, name, "ui5", TEXT, "middle")
        y += (len(tools) // cols) * (th + 14) - 14 + 28
    return svg(W, int(y - 28 + 3), o, title="Tech arsenal - " + "; ".join(f"{l}: " + ", ".join(n for n, _ in t) for l, t in STACK))


# ═════════════════════════════ HEADINGS ═════════════════════════════
def heading(kick, title, light=False):
    """Section heading on a transparent ground - one file per GitHub theme."""
    W, H = 1200, 100
    o = kicker(600, 30, kick, "#1f6fc2" if light else ELECTRIC) + T(600, 82, 44, title, "display", "#0b1a38" if light else TEXT, "middle")
    return svg(W, H, o, title=title)


# ═════════════════════════════ PROJECT CARDS ═════════════════════════════
ART_ROOM = 424  # widest a description line may be before it touches the miniature


def project(i, p):
    """Shown two-up at 50% width with no space between, so the gutter is baked
    in: a 600-unit slot holding a 592-unit card, pushed left or right."""
    W, H, cw = 600, 246, 592
    ox = (i % 2) * (W - cw)
    o = frame(ox + .75, 6, cw - 1.5, H - 12, 18, brk=False, ring=.55)
    st = p["status"].upper()
    sw = mw(st, 13, 2) + 26
    o += f'<path d="{chamfer(ox + 28, 30, sw, 26, 6)}" fill="{GOLD}" fill-opacity=".1" stroke="{GOLD}" stroke-opacity=".6"/>'
    if st == "LIVE":
        o += f'<circle class="dk-node" cx="{ox + 28 + sw + 14}" cy="43" r="4" fill="{GREEN}"/>'
    o += M(ox + 41, 48, 13, st, GOLD, ls=2, w=600) + M(ox + cw - 28, 48, 14, f"NN-0{i + 1}", FAINT, "end", 2)
    o += T(ox + 28, 104, 34, p["title"], "display", TEXT) + M(ox + 28, 129, 13, p["tag"], ELECTRIC, ls=1.5, w=600)
    for j, ln in enumerate(p["lines"]):
        if tw(ln, 19.5, "ui4") > ART_ROOM:
            raise SystemExit(f"project {p['slug']!r}: line {ln!r} runs into the card art - shorten it by "
                             f"{tw(ln, 19.5, 'ui4') - ART_ROOM:.0f} units")
        o += T(ox + 28, 160 + j * 26, 19.5, ln, "ui4", MUTED)
    x = ox + 28
    for c in p["chips"]:
        cc, w = chip(x, 200, c, 15, 28, 12)
        o += cc
        x += w + 8
    if x - 8 - ox > 28 + ART_ROOM + 20:
        raise SystemExit(f"project {p['slug']!r}: the chip row runs under the card art - drop a chip")
    # the miniature owns the right-hand 130 units of every card; `art` in deck_content.py picks it
    o += miniature(p.get("art", "planet"), ox + 508, 112, 14, delay=i * .9)
    return svg(W, H, o, ART_CSS, title=f"{p['title']} - " + " ".join(p["lines"]))


# ═════════════════════════════ FOOTER ═════════════════════════════
def footer():
    W, H = 1200, 250
    cp = clip(f'<path d="{chamfer(0, 1, W, H - 2, 26)}"/>')
    o = frame(0, 1, W, H - 2, 26)
    rx, ry = 160, 150
    clouds = "".join(
        f'<circle class="dk-puff" cx="{x}" cy="{y}" r="{r}" fill="#dfe9f8" opacity="{op}" style="animation-delay:{d}s"/>'
        for x, y, r, op, d in ((92, 250, 34, .4, 0), (160, 262, 44, .75, .5), (232, 252, 36, .5, 1), (40, 262, 28, .3, 1.4), (286, 264, 28, .3, .8), (128, 240, 24, .5, 1.8), (200, 240, 22, .5, .3)))
    streaks = "".join(f'<path class="dk-streak" style="animation-delay:{d}s" d="M{x} {y} v{l}" stroke="{TEXT}" stroke-width="2" stroke-linecap="round"/>'
                      for x, y, l, d in ((112, 60, 24, 0), (208, 84, 20, .45), (96, 118, 16, .9), (222, 30, 22, .25)))
    o += (f'<g clip-path="{cp}">{stars(W, H, 110, 9)}'
          f'<ellipse cx="{rx}" cy="{H}" rx="230" ry="120" fill="{rad([(0, GOLD, .28), (1, GOLD, 0)])}"/>'
          f'{streaks}<g class="dk-rise"><g class="dk-shake">{rocket(rx, ry, .86, flame=True)}</g></g>{clouds}'
          + planet(1078, 132, 42) + satellite(968, 58, 14)
          + spark(880, 176, 8, GOLD, 0) + spark(1150, 44, 7, ICE, 1.2) + spark(330, 50, 6, ICE, .5) + "</g>")
    o += T(600, 100, 42, "Thanks for stopping by the deck.", "display", TEXT, "middle")
    bt = "LAUNCH  " + SITE.upper()
    bw = mw(bt, 16, 3) + 60
    o += f'<path d="{chamfer(600 - bw / 2, 132, bw, 48, 12)}" fill="#0c2a52" stroke="{ELECTRIC}" stroke-opacity=".85" stroke-width="1.4"/>'
    o += M(600, 162, 16, bt, CORE, "middle", 3, 600)
    return svg(W, H, o, ART_CSS, f"Thanks for stopping by - visit {SITE}")


def main():
    print("Observation Deck assets:")
    write(os.path.join(OUT, "hero.svg"), hero())
    for i, (slug, kick, title, sub, ic) in enumerate(LINKS):
        write(os.path.join(OUT, f"link-{slug}.svg"), link(i, kick, title, sub, ic))
    write(os.path.join(OUT, "crew.svg"), crew())
    write(os.path.join(OUT, "arsenal.svg"), stack())
    for key, (kick, title) in HEADINGS.items():
        write(os.path.join(OUT, f"h-{key}-dark.svg"), heading(kick, title))
        write(os.path.join(OUT, f"h-{key}-light.svg"), heading(kick, title, light=True))
    for i, p in enumerate(PROJECTS):
        write(os.path.join(OUT, f"project-{p['slug']}.svg"), project(i, p))
    write(os.path.join(OUT, "footer.svg"), footer())


if __name__ == "__main__":
    main()
