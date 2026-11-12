"""Shared toolkit for the Observation Deck README design.

Visual language = the portfolio's HUD (nimna-niwarthana/src/styles): chamfered
glass panels whose 1px ring runs electric blue into warm gold, label tabs that
straddle the top line, terminal nodes on the cut corners.

Text is drawn from pre-extracted glyph outlines (scripts/deck_data/glyphs.json),
so every viewer gets Calistoga + Space Grotesk without a webfont. Standard
library only - safe to run in GitHub Actions with no pip install.

All CSS class / keyframe names are prefixed `dk-` so they can never collide with
the snake SVG that deck_snake.py embeds.
"""
import json
import math
import os
import random
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# ── palette: portfolio tokens (src/styles/tokens.css) ────────────────────────
VOID, ELEV = "#030913", "#08142c"
ELECTRIC, CORE = "#4db8ff", "#eaf6ff"
GOLD, GOLD2 = "#cf9d43", "#b08432"
TEXT, MUTED, FAINT = "#e8f0fc", "#a3b5d6", "#6d81a8"
ICE, GREEN = "#bfe3ff", "#2fbf71"
MONO = "ui-monospace,'Cascadia Mono','SFMono-Regular','Segoe UI Mono',Consolas,'Liberation Mono','DejaVu Sans Mono',monospace"

_GLYPHS = json.load(open(os.path.join(HERE, "deck_data", "glyphs.json"), encoding="utf8"))
_ICONS = json.load(open(os.path.join(HERE, "deck_data", "icons.json"), encoding="utf8"))


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


# ───────────────────────────── document state ─────────────────────────────
class Doc:
    """Collects the glyphs and <defs> one SVG file needs."""

    def __init__(self):
        self.glyphs, self.defs, self.n, self.paints = {}, [], 0, {}

    def uid(self, p="u"):
        self.n += 1
        return f"{p}{self.n}"

    def glyph(self, font, ch):
        k = (font, ch)
        if k not in self.glyphs:
            self.glyphs[k] = f"{font[0]}{font[-1]}{len(self.glyphs)}"
        return self.glyphs[k]


D = Doc()


def uid(p="u"):
    return D.uid(p)


# ───────────────────────────── text ─────────────────────────────
def _g(font, ch):
    t = _GLYPHS[font]["g"]
    return t.get(ch) or t[" "]


def tw(txt, s, font="ui5", ls=0.0):
    """Exact rendered width of outlined text."""
    return sum(_g(font, c)[0] for c in txt) * s / _GLYPHS[font]["upm"] + ls * max(len(txt) - 1, 0)


def _start(x, txt, s, font, ls, anchor):
    w = tw(txt, s, font, ls)
    return x - w / 2 if anchor == "middle" else x - w if anchor == "end" else x


def T(x, y, s, txt, font="ui5", fill=TEXT, anchor="start", ls=0.0, op=None):
    """Outlined text as <use> references to shared glyph paths."""
    k = s / _GLYPHS[font]["upm"]
    x = _start(x, txt, s, font, ls, anchor)
    cx, out = 0.0, []
    for ch in txt:
        if ch != " " and ch in _GLYPHS[font]["g"]:
            out.append(f'<use href="#{D.glyph(font, ch)}" x="{cx:.0f}"/>')
        cx += _g(font, ch)[0] + ls / k
    o = f' opacity="{op}"' if op is not None else ""
    return f'<g transform="translate({x:.1f} {y:.1f}) scale({k:.5f} {-k:.5f})" fill="{fill}"{o}>{"".join(out)}</g>'


_TOK = re.compile(r"([MLHVQCZ])([^MLHVQCZ]*)")


def _shift(d, dx):
    out = []
    for c, args in _TOK.findall(d):
        n = [float(v) for v in args.split()]
        if c in "MLQC":
            n = [v + dx if i % 2 == 0 else v for i, v in enumerate(n)]
        elif c == "H":
            n = [v + dx for v in n]
        out.append(c + " ".join(f"{v:.0f}" for v in n))
    return "".join(out)


def TP(x, y, s, txt, font="display", fill=TEXT, anchor="start", ls=0.0):
    """Outlined text merged into ONE path, so a gradient can span the whole run."""
    k = s / _GLYPHS[font]["upm"]
    x = _start(x, txt, s, font, ls, anchor)
    cx, d = 0.0, []
    for ch in txt:
        adv, path = _g(font, ch)
        if ch != " ":
            d.append(_shift(path, cx))
        cx += adv + ls / k
    return f'<path transform="translate({x:.1f} {y:.1f}) scale({k:.5f} {-k:.5f})" d="{"".join(d)}" fill="{fill}"/>'


def mw(txt, s, ls=0.0):
    """Width reserved for a console label; M() pins the text to exactly this."""
    return len(txt) * s * 0.6 + ls * max(len(txt) - 1, 0)


def M(x, y, s, txt, fill=MUTED, anchor="start", ls=0.0, w=500, op=None):
    """Live console text (the portfolio's kicker face). textLength pins its
    width, so the layout is identical whichever monospace font a system has."""
    o = f' opacity="{op}"' if op is not None else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{MONO}" font-size="{s}" font-weight="{w}" text-anchor="{anchor}" '
            f'textLength="{mw(txt, s, ls):.1f}" lengthAdjust="spacing" fill="{fill}"{o}>{esc(txt)}</text>')


# ───────────────────────────── paint servers ─────────────────────────────
def _stops(stops):
    return "".join(f'<stop offset="{o}" stop-color="{c}"' + (f' stop-opacity="{a[0]}"' if a else "") + "/>" for o, c, *a in stops)


def _paint(tag, attrs, stops):
    """Gradients are bounding-box relative, so identical ones are shared."""
    key = (tag, attrs, _stops(stops))
    if key not in D.paints:
        i = uid("p")
        D.defs.append(f'<{tag} id="{i}" {attrs}>{key[2]}</{tag}>')
        D.paints[key] = f"url(#{i})"
    return D.paints[key]


def lin(stops, x1=0, y1=0, x2=1, y2=0):
    return _paint("linearGradient", f'x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"', stops)


def rad(stops, cx=.5, cy=.5, r=.5):
    return _paint("radialGradient", f'cx="{cx}" cy="{cy}" r="{r}"', stops)


def clip(inner):
    i = uid("c")
    D.defs.append(f'<clipPath id="{i}">{inner}</clipPath>')
    return f"url(#{i})"


# ───────────────────────────── primitives ─────────────────────────────
def rr(x, y, w, h, r, **kw):
    a = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in kw.items())
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{r}" {a}/>'


def chamfer(x, y, w, h, c):
    """The portfolio's HUD shape: top-left and bottom-right corners cut."""
    return f"M{x:.1f} {y + c:.1f} L{x + c:.1f} {y:.1f} H{x + w:.1f} V{y + h - c:.1f} L{x + w - c:.1f} {y + h:.1f} H{x:.1f} Z"


def pol(cx, cy, r, deg):
    a = math.radians(deg)
    return cx + r * math.cos(a), cy + r * math.sin(a)


def arc(cx, cy, r, a0, a1):
    x0, y0 = pol(cx, cy, r, a0)
    x1, y1 = pol(cx, cy, r, a1)
    return f"M{x0:.1f} {y0:.1f} A{r} {r} 0 {1 if abs(a1 - a0) > 180 else 0} {1 if a1 > a0 else 0} {x1:.1f} {y1:.1f}"


def stars(w, h, n, seed, x0=0, y0=0, cols=(TEXT, TEXT, TEXT, ELECTRIC, GOLD), twinkle=.22, rmax=1.5):
    r = random.Random(seed)
    out = []
    for _ in range(n):
        x, y = x0 + r.uniform(0, w), y0 + r.uniform(0, h)
        rad_, col = r.choice([.5, .6, .7, .8, 1, 1.2, rmax]), r.choice(cols)
        if r.random() < twinkle:
            out.append(f'<circle class="dk-tw" cx="{x:.1f}" cy="{y:.1f}" r="{rad_}" fill="{col}" '
                       f'style="animation-delay:{r.uniform(0, 4):.1f}s;animation-duration:{r.uniform(2.5, 6):.1f}s"/>')
        else:
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rad_}" fill="{col}" opacity="{r.uniform(.2, .85):.2f}"/>')
    return "".join(out)


def spark(cx, cy, r, fill=ICE, delay=None):
    """Four-point star; twinkles when given a delay."""
    p = (f'<path d="M{cx} {cy - r} Q{cx} {cy} {cx + r} {cy} Q{cx} {cy} {cx} {cy + r} Q{cx} {cy} {cx - r} {cy} Q{cx} {cy} {cx} {cy - r} Z" fill="{fill}"'
         + (f' class="dk-spark" style="animation-delay:{delay}s"' if delay is not None else "") + "/>")
    return p


# ───────────────────────────── HUD components ─────────────────────────────
def frame(x, y, w, h, c=20, label=None, nodes=True, brk=True, ring=.6):
    """Chamfered glass panel. With `label`, leave 14 units of room above `y`."""
    glass = lin([(0, "#0c1c3c"), (1, "#050d1f")], 0, 0, 0, 1)
    line = lin([(0, ELECTRIC, ring), (.55, ELECTRIC, ring * .8), (1, GOLD, min(ring + .15, 1))], 0, 0, 1, 1)
    shine = lin([(0, "#fff", .06), (.22, "#fff", 0)], 0, 0, 0, 1)
    p = chamfer(x, y, w, h, c)
    o = f'<path d="{p}" fill="{glass}"/><path d="{p}" fill="{shine}"/><path d="{p}" fill="none" stroke="{line}" stroke-width="1.5"/>'
    if brk:
        b = min(26, h / 4)
        o += (f'<path d="M{x + w - b:.1f} {y} H{x + w:.1f} V{y + b:.1f} M{x + b:.1f} {y + h} H{x} V{y + h - b:.1f}" fill="none" '
              f'stroke="{ELECTRIC}" stroke-opacity=".8" stroke-width="2.5"/>')
    if nodes:
        for i, (nx, ny) in enumerate(((x + c, y), (x + w - c, y + h))):
            o += (f'<circle cx="{nx}" cy="{ny}" r="5" fill="{VOID}" stroke="{ELECTRIC}" stroke-width="1.2"/>'
                  f'<circle class="dk-node" cx="{nx}" cy="{ny}" r="2.4" fill="{ELECTRIC}" style="animation-delay:{i * 1.5}s"/>')
    if label:
        o += tab(x + c + 22, y - 13, label)
    return o


def tab(x, y, label, s=14):
    """Label tab with the clipped nose - opaque, so it reads on any page colour."""
    lw = mw(label, s, 3) + 36
    fill = lin([(0, "#12406f"), (1, "#0b2040")])
    return (f'<path d="M{x:.1f} {y} H{x + lw:.1f} L{x + lw - 10:.1f} {y + 26} H{x:.1f} Z" fill="{fill}" stroke="{ELECTRIC}" stroke-opacity=".6"/>'
            + M(x + 13, y + 18, s, label, CORE, ls=3, w=600))


def tab_w(label, s=14):
    return mw(label, s, 3) + 36


def chip(x, y, txt, s=19, h=40, pad=18, col=ELECTRIC, font="ui5", fill=TEXT, w=None):
    cw = w or tw(txt, s, font) + pad * 2
    return (f'<path d="{chamfer(x, y, cw, h, min(9, h * .26))}" fill="{col}" fill-opacity=".07" stroke="{col}" stroke-opacity=".5" stroke-width="1.2"/>'
            + T(x + cw / 2, y + h / 2 + s * .35, s, txt, font, fill, "middle")), cw


def plate(x, y, s, name, col=ELECTRIC):
    return (f'<path d="{chamfer(x, y, s, s, s * .17)}" fill="{col}" fill-opacity=".09" stroke="{col}" stroke-opacity=".5" stroke-width="1.2"/>'
            + icon(name, x + s * .25, y + s * .25, s * .5, col))


def kicker(cx, y, txt, col=ELECTRIC, s=15):
    w = mw(txt, s, 5)
    return (M(cx, y, s, txt, col, "middle", 5, 600, .9)
            + f'<path d="M{cx - w / 2 - 44:.1f} {y - 5} h30 M{cx + w / 2 + 14:.1f} {y - 5} h30" stroke="{col}" stroke-opacity=".55"/>')


ICONS = {
    "globe": '<circle cx="12" cy="12" r="9.5"/><ellipse cx="12" cy="12" rx="4" ry="9.5"/><path d="M2.5 12h19M4.5 7h15M4.5 17h15"/>',
    "in": '<rect x="2.5" y="2.5" width="19" height="19" rx="4"/><path d="M7 10.5V17M7 7v.01M11 17v-6.5M11 13.4c0-1.9 1.3-3 2.9-3s2.7 1 2.7 3V17"/>',
    "x": '<path d="M4 3.5h4.5L20 20.5h-4.5z"/><path d="M19.5 3.5l-6.3 7.1M4.5 20.5l6.3-7.1"/>',
    "cup": '<path d="M4 9h12v6a5 5 0 0 1-5 5H9a5 5 0 0 1-5-5z"/><path d="M16 11h1.5a2.5 2.5 0 0 1 0 5H16"/><path d="M8 2.5c-.8 1 .8 2 0 3.2M12 2.5c-.8 1 .8 2 0 3.2"/>',
    "rocket": '<path d="M12 2C15.5 5 17 9 16.5 14.5H7.5C7 9 8.5 5 12 2Z"/><circle cx="12" cy="9" r="1.8"/><path d="M7.6 12L4.5 17l3.6-.7M16.4 12l3.1 5-3.6-.7M10 17.5l2 4 2-4"/>',
    "cap": '<path d="M2 9l10-5 10 5-10 5z"/><path d="M6 11.2V16c0 1.6 2.8 3 6 3s6-1.4 6-3v-4.8M22 9v6"/>',
    "shield": '<path d="M12 2.5l8 3V11c0 5-3.5 8.5-8 10.5C7.5 19.5 4 16 4 11V5.5z"/><path d="M8.8 12l2.2 2.2 4.2-4.4"/>',
    "pr": '<circle cx="6" cy="5.5" r="2.2"/><circle cx="6" cy="18.5" r="2.2"/><circle cx="18" cy="18.5" r="2.2"/><path d="M6 7.7v8.6M18 16.300V11c0-2.800-1.800-4.500-4.500-4.500H11M13.5 4L11 6.500 13.500 9"/>',
    "issue": '<circle cx="12" cy="12" r="9.5"/><path d="M12 7v6.5M12 16.800v.01"/>',
    "star": '<path d="M12 3l2.7 5.600 6.100.800-4.500 4.300 1.100 6.100-5.400-2.900-5.400 2.900 1.100-6.100L3.200 9.400l6.100-.800z"/>',
    "repo": '<path d="M6.5 3.500H19V17H6.500a1.750 1.750 0 0 0 0 3.500H19"/><path d="M6.500 3.500A1.800 1.800 0 0 0 4.700 5.300v13.400M9.500 8h6"/>',
    "users": '<circle cx="9" cy="8" r="3.3"/><path d="M2.500 20c0-3.800 2.700-6 6.500-6s6.500 2.200 6.500 6"/><circle cx="17.500" cy="9" r="2.500"/><path d="M17.800 14c2.400.2 3.700 2 3.700 5"/>',
    "pulse": '<path d="M2.500 12H7l2.500-7 5 14 2.500-7h4.500"/>',
    "arrow": '<path d="M7 17L17 7M9 7h8v8"/>',
    "chip": '<rect x="6" y="6" width="12" height="12" rx="2"/><rect x="9.500" y="9.500" width="5" height="5" rx=".8"/><path d="M9 2.500v3.500M15 2.500v3.500M9 18v3.500M15 18v3.500M2.500 9H6M2.500 15H6M18 9h3.500M18 15h3.500"/>',
    "layers": '<path d="M12 3l9 4.500-9 4.500-9-4.500z"/><path d="M3 12l9 4.500 9-4.500M3 16.500L12 21l9-4.500"/>',
    "chart": '<path d="M4 3.500V20h16.500"/><path d="M8.500 16v-4M12.500 16V8M16.500 16v-6"/>',
    "bolt": '<path d="M13 2.500L5 13.500h5.500L9.500 21.500l8.500-11.500h-5.500z"/>',
}


def icon(name, x, y, size, color, sw=1.8):
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({size / 24:.3f})" fill="none" stroke="{color}" stroke-width="{sw}" '
            f'stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</g>')


# Marks whose official artwork is too dark for the glass get their dark-mode colours.
RECOLOR = {
    "devicon:amazonwebservices": {"#252f3e": "#eef4ff"},
    "devicon:pandas": {"#130754": "#eef4ff"},
    "devicon:bash": {"#293138": "#56698f"},
}


def brand(key, x, y, size):
    """Full-colour brand mark (scripts/deck_data/icons.json), or None."""
    ic = _ICONS.get(key or "")
    if not ic:
        return None
    vb = [float(v) for v in ic["viewBox"].split()]
    sc = size / max(vb[2], vb[3])
    ox, oy = x + (size - vb[2] * sc) / 2, y + (size - vb[3] * sc) / 2
    body = ic["body"]
    for a, b in RECOLOR.get(key, {}).items():
        body = body.replace(a, b)
    if ic.get("lift"):  # near-black silhouettes are lifted to white on the dark glass
        body = re.sub(r'fill="#[0-9a-fA-F]{3,8}"', 'fill="#eef4ff"', body)
        body = f'<g fill="#eef4ff" color="#eef4ff">{body}</g>'
    n = uid("b")  # namespace ids so two marks never share a gradient id
    body = re.sub(r'id="([^"]+)"', lambda m: f'id="{n}{m.group(1)}"', body)
    body = re.sub(r"url\(#([^)]+)\)", lambda m: f"url(#{n}{m.group(1)})", body)
    body = re.sub(r'href="#([^"]+)"', lambda m: f'href="#{n}{m.group(1)}"', body)
    return f'<g transform="translate({ox:.1f} {oy:.1f}) scale({sc:.4f}) translate({-vb[0]:g} {-vb[1]:g})">{body}</g>'


# ───────────────────────────── file output ─────────────────────────────
BASE_CSS = """
.dk-tw{animation:dk-tw 4s ease-in-out infinite}
@keyframes dk-tw{0%,100%{opacity:.2}50%{opacity:1}}
.dk-node{animation:dk-node 3s ease-in-out infinite}
@keyframes dk-node{0%,100%{opacity:1}50%{opacity:.35}}
.dk-spark{transform-box:fill-box;transform-origin:center;animation:dk-spark 3.2s ease-in-out infinite}
@keyframes dk-spark{0%,100%{transform:scale(.5);opacity:.35}50%{transform:scale(1.1);opacity:1}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}"""


def svg(w, h, body, css="", title=""):
    """Wrap `body` into a complete SVG file and start a fresh document."""
    global D
    gl = "".join(f'<path id="{gid}" d="{_GLYPHS[font]["g"][ch][1]}"/>' for (font, ch), gid in D.glyphs.items())
    t = f"<title>{esc(title)}</title>" if title else ""
    out = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img">{t}'
           f'<defs>{gl}{"".join(D.defs)}</defs><style>{BASE_CSS}{css}</style>{body}</svg>\n')
    D = Doc()
    return out


def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    try:
        shown = os.path.relpath(path, ROOT).replace(os.sep, "/")
    except ValueError:  # Windows: output on another drive than the repo
        shown = path
    print(f"  wrote {shown}  ({len(content.encode()) / 1024:.1f} KB)")
