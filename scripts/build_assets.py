#!/usr/bin/env python3
"""Generate the static SVG artwork in ./assets (hero, buttons, panels, cards).

Run from the repo root:  python3 scripts/build_assets.py
Edit the CONTENT section below to update text, then re-run.

Sizing rule: every SVG is shown at roughly 0.7x on the GitHub profile page
(1200-unit canvas in a ~840px column), so body copy is >= 21 units and labels
are >= 16 units to stay readable after scaling.
"""

import base64
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from theme import (  # noqa: E402
    AMBER, CYAN, DIM, LINE, PINK, SOFT, TEXT, VIOLET,
    esc, hud_corners, panel, stars, svg,
)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets")

# ═════════════════════════════ CONTENT ═════════════════════════════
NAME = "NIMNA NIWARTHANA"
ROLES = ["Software Engineer", "AI / ML Developer", "Cybersecurity Specialist"]

CREW = [
    ("CALLSIGN", ["Nimna Niwarthana"]),
    ("ROLE", ["Software Engineer · AI/ML Developer · Cybersecurity"]),
    ("MISSION", ["Catalogie — full-stack & security engineering (live)"]),
    ("TRAINING", ["MSc Ethical Hacking · Abertay University",
                  "BSc (Hons) Computer Security · University of Plymouth"]),
    ("PUBLISHED", ["MalDitectist · book chapter, Taylor & Francis (2024)"]),
    ("ORBITS", ["Malware analysis · Pen testing · ML · Self-hosted infra"]),
]

STACK = [
    ("LANGUAGES", CYAN, ["Python", "TypeScript", "JavaScript", "C", "C#", "Dart", "SQL", "Bash"]),
    ("AI / ML", VIOLET, ["PyTorch", "TensorFlow", "Keras", "scikit-learn", "OpenCV", "NLP", "CNNs"]),
    ("WEB & API", PINK, ["React", "Node.js", "Express", "FastAPI", "Django", "Flutter", "PostgreSQL", "MongoDB"]),
    ("SECURITY", AMBER, ["Pen Testing", "Malware Analysis", "Forensics", "Ghidra", "Burp Suite", "Volatility", "Nmap"]),
    ("INFRA", CYAN, ["Docker", "Linux", "Git", "GitHub Actions", "Caddy", "Oracle Cloud", "Firebase"]),
]

PROJECTS = [
    dict(slug="catalogie", status="LIVE", color=CYAN, tag="FULL-STACK · SECURITY · 2026 → NOW",
         title="Catalogie",
         lines=["One library for films, TV, games & books.",
                "Self-hosted PERN stack · 91 REST endpoints."],
         chips=["React", "TypeScript", "Express", "PostgreSQL", "Caddy"]),
    dict(slug="malditectist", status="PUBLISHED", color=VIOLET, tag="AI/ML RESEARCH · TAYLOR & FRANCIS",
         title="MalDitectist",
         lines=["Ensemble malware detection — signature +",
                "anomaly models, 98.9% RF accuracy."],
         chips=["Python", "scikit-learn", "TensorFlow", "Django", "React"]),
    dict(slug="malscraper", status="TOOL", color=PINK, tag="MALWARE RESEARCH · DOCKER CLI",
         title="MalScraper",
         lines=["Turns raw Windows PE samples into",
                "ML-ready datasets: opcodes, n-grams."],
         chips=["Python", "Docker", "Capstone", "pefile", "pandas"]),
    dict(slug="agenttesla", status="REPORT", color=AMBER, tag="REVERSE ENGINEERING · .NET STEALER",
         title="AgentTesla Analysis",
         lines=["Static, dynamic, memory & code analysis",
                "of a reflectively loaded payload."],
         chips=["Ghidra", "dnSpy", "Volatility 3", "Wireshark"]),
]

SECTIONS = {
    "about": ("01", "MISSION PROFILE"),
    "stack": ("02", "ARSENAL"),
    "projects": ("03", "FEATURED MISSIONS"),
    "stats": ("04", "TELEMETRY"),
    "flight": ("05", "FLIGHT PATH"),
}

# Transparent space baked into the top of each section header. With GitHub's
# 16px paragraph margin this gives a ~30px gap between sections (was ~80px).
HEADER_GAP = 12

BUTTONS = [
    ("portfolio", "PORTFOLIO", "nimna-niwarthana.com", CYAN, "globe"),
    ("linkedin", "LINKEDIN", "let's connect", VIOLET, "in"),
    ("x", "X / TWITTER", "@niwarthananimna", PINK, "x"),
    ("coffee", "BUY ME A COFFEE", "fuel the rocket", AMBER, "cup"),
]


# ═════════════════════════════ HELPERS ═════════════════════════════
def write(name: str, content: str) -> None:
    path = os.path.join(OUT, name)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print(f"  wrote assets/{name}  ({len(content.encode()) / 1024:.1f} KB)")


def chip_w(text: str, size: float, pad: float) -> float:
    return len(text) * size * 0.6 + pad * 2


def chips(x: float, y: float, items, color: str, size: float, gap: float, h: float, pad: float) -> str:
    out = []
    for it in items:
        w = chip_w(it, size, pad)
        out.append(
            f'<g transform="translate({x:.1f},{y:.1f})">'
            f'<rect width="{w:.1f}" height="{h}" rx="{h / 2}" fill="{color}" fill-opacity=".14" stroke="{color}" stroke-opacity=".75" stroke-width="1.4"/>'
            f'<text x="{w / 2:.1f}" y="{h / 2 + size * 0.36:.1f}" text-anchor="middle" class="mono" font-size="{size}" font-weight="600" fill="{TEXT}">{esc(it)}</text>'
            f'</g>'
        )
        x += w + gap
    return "".join(out)


def planet(cx, cy, r, uid, c1=VIOLET, c2="#312E81", ring=True, spin_dur=40) -> str:
    ring_back = ring_front = ""
    if ring:
        ring_back = (f'<path d="M{cx - r * 1.75} {cy} A{r * 1.75} {r * .42} 0 0 1 {cx + r * 1.75} {cy}" '
                     f'transform="rotate(-12 {cx} {cy})" fill="none" stroke="{CYAN}" stroke-opacity=".35" stroke-width="5"/>')
        ring_front = (f'<path d="M{cx - r * 1.75} {cy} A{r * 1.75} {r * .42} 0 0 0 {cx + r * 1.75} {cy}" '
                      f'transform="rotate(-12 {cx} {cy})" fill="none" stroke="url(#{uid}-edge)" stroke-width="5"/>'
                      f'<path d="M{cx - r * 1.55} {cy} A{r * 1.55} {r * .34} 0 0 0 {cx + r * 1.55} {cy}" '
                      f'transform="rotate(-12 {cx} {cy})" fill="none" stroke="{VIOLET}" stroke-opacity=".5" stroke-width="2"/>')
    return f"""<defs>
    <radialGradient id="{uid}-pl" cx=".35" cy=".3" r=".8">
      <stop offset="0" stop-color="{c1}"/><stop offset=".55" stop-color="{c2}"/><stop offset="1" stop-color="#0B0A26"/>
    </radialGradient>
    <radialGradient id="{uid}-glow" cx=".5" cy=".5" r=".5">
      <stop offset=".55" stop-color="{c1}" stop-opacity=".35"/><stop offset="1" stop-color="{c1}" stop-opacity="0"/>
    </radialGradient>
    <clipPath id="{uid}-plc"><circle cx="{cx}" cy="{cy}" r="{r}"/></clipPath>
  </defs>
  <circle cx="{cx}" cy="{cy}" r="{r * 1.45}" fill="url(#{uid}-glow)"/>
  {ring_back}
  <circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#{uid}-pl)"/>
  <g clip-path="url(#{uid}-plc)" opacity=".35">
    <g>
      <animateTransform attributeName="transform" type="translate" from="0 0" to="{-r * 2} 0" dur="{spin_dur}s" repeatCount="indefinite"/>
      <path d="M{cx - r} {cy - r * .45} q{r * .5} {-r * .12} {r} 0 t{r} 0 t{r} 0 t{r} 0" fill="none" stroke="{PINK}" stroke-width="{r * .09}"/>
      <path d="M{cx - r} {cy + r * .05} q{r * .5} {r * .12} {r} 0 t{r} 0 t{r} 0 t{r} 0" fill="none" stroke="{CYAN}" stroke-width="{r * .06}"/>
      <path d="M{cx - r} {cy + r * .5} q{r * .5} {-r * .1} {r} 0 t{r} 0 t{r} 0 t{r} 0" fill="none" stroke="{VIOLET}" stroke-width="{r * .12}"/>
    </g>
  </g>
  <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{TEXT}" stroke-opacity=".12"/>
  {ring_front}"""


# ═════════════════════════════ HERO ═════════════════════════════
def hero() -> str:
    W, H, uid = 1200, 320, "hero"
    pcx, pcy, pr = 1064, 158, 74          # planet
    orx, ory = 150, 50                    # dashed orbit + satellite
    roles = []
    n = len(ROLES)
    for i, role in enumerate(ROLES):
        a = i / n
        b = a + 1.4 / (n * 3.2)
        d = (i + 1) / n
        c = d - 0.25 / (n * 3.2)
        kt = f"0;{a:.4f};{b:.4f};{c:.4f};{d:.4f};1"
        roles.append(f"""<clipPath id="r{i}"><rect x="96" y="214" height="56" width="0">
      <animate attributeName="width" values="0;0;700;700;0;0" keyTimes="{kt}" dur="{n * 3.2}s" repeatCount="indefinite"/>
    </rect></clipPath>
    <text x="100" y="254" class="mono" font-size="36" font-weight="600" fill="{CYAN}" clip-path="url(#r{i})"><tspan fill="{VIOLET}">▸ </tspan>{esc(role)}<tspan class="cur">_</tspan></text>""")
    css = f"""
  .cur {{ animation: blink 1s steps(1) infinite; }}
  @keyframes blink {{ 50% {{ opacity: 0; }} }}
  .shoot {{ animation: shoot 7s ease-in infinite; opacity: 0; }}
  .shoot.b {{ animation-delay: 3.6s; }}
  @keyframes shoot {{ 0% {{ transform: translate(0,0); opacity: 0; }} 3% {{ opacity: 1; }} 14% {{ transform: translate(-460px,230px); opacity: 0; }} 100% {{ opacity: 0; }} }}
  .scan {{ animation: scan 6s linear infinite; }}
  @keyframes scan {{ from {{ transform: translateY(-20px); }} to {{ transform: translateY({H + 20}px); }} }}"""
    body = f"""{panel(uid, W, H, seed=29, star_count=170)}
  <g clip-path="url(#{uid}-clip)">
    <ellipse cx="{pcx - 20}" cy="{pcy - 30}" rx="400" ry="210" fill="url(#{uid}-nebC)"/>
    <g class="shoot"><line x1="1150" y1="20" x2="1230" y2="-20" stroke="{TEXT}" stroke-width="2" stroke-linecap="round" opacity=".8"/></g>
    <g class="shoot b"><line x1="820" y1="10" x2="880" y2="-20" stroke="{CYAN}" stroke-width="1.6" stroke-linecap="round"/></g>
    <ellipse cx="{pcx}" cy="{pcy}" rx="{orx}" ry="{ory}" transform="rotate(-12 {pcx} {pcy})" fill="none" stroke="{DIM}" stroke-dasharray="3 7" opacity=".7"/>
    {planet(pcx, pcy, pr, uid)}
    <g transform="rotate(-12 {pcx} {pcy})">
      <circle r="5" fill="{AMBER}">
        <animateMotion dur="14s" repeatCount="indefinite" path="M{pcx - orx} {pcy} a{orx} {ory} 0 1 0 {orx * 2} 0 a{orx} {ory} 0 1 0 {-orx * 2} 0"/>
      </circle>
    </g>
    <circle cx="1148" cy="56" r="9" fill="#1F2A5C" stroke="{VIOLET}" stroke-opacity=".6"/>
    <rect class="scan" x="0" y="0" width="{W}" height="2" fill="{CYAN}" opacity=".06"/>
  </g>
  <text x="100" y="94" class="mono" font-size="26" fill="{SOFT}">nimna@orbit:~$ <tspan fill="{TEXT}" font-weight="700">whoami</tspan></text>
  <text x="96" y="182" class="sans" font-size="68" font-weight="800" letter-spacing="2" fill="url(#{uid}-edge)">{esc(NAME)}</text>
  {''.join(roles)}"""
    return svg(W, H, uid, body, css, f"{NAME} — " + " · ".join(ROLES))


# ═════════════════════════════ BUTTONS ═════════════════════════════
def icon(kind: str, color: str) -> str:
    s = f'stroke="{color}" stroke-width="2.2" fill="none" stroke-linecap="round" stroke-linejoin="round"'
    if kind == "globe":
        return f'<circle cx="12" cy="12" r="10" {s}/><ellipse cx="12" cy="12" rx="4.2" ry="10" {s}/><path d="M2 12h20M4 6.5h16M4 17.5h16" {s}/>'
    if kind == "in":
        return (f'<rect x="2" y="2" width="20" height="20" rx="4" {s}/>'
                f'<path d="M7 10v7M7 7v.01M11 17v-7M11 13.2c0-2 1.4-3.2 3-3.2s2.8 1.1 2.8 3.2V17" {s}/>')
    if kind == "x":
        return f'<path d="M4 3.5h4.5L20 20.5h-4.5z" {s}/><path d="M19.5 3.5l-6.3 7.1M4.5 20.5l6.3-7.1" {s}/>'
    if kind == "cup":
        return (f'<path d="M4 9h12v6a5 5 0 0 1-5 5H9a5 5 0 0 1-5-5z" {s}/><path d="M16 11h1.5a2.5 2.5 0 0 1 0 5H16" {s}/>'
                f'<path d="M8 2.5c-.8 1 .8 2 0 3.2M12 2.5c-.8 1 .8 2 0 3.2" {s}/>')
    return ""


def button(label, sub, color, kind, uid) -> str:
    W, H = 232, 58
    body = f"""<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="12" fill="url(#{uid}-bg)"/>
  <g clip-path="url(#{uid}-clip)">{stars(W, H, 12, sum(map(ord, uid)), twinkle=.4)}</g>
  <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="12" fill="none" stroke="{color}" stroke-opacity=".8" stroke-width="1.6"/>
  {hud_corners(5, 5, W - 10, H - 10, 8, color, 1.4)}
  <circle cx="30" cy="{H / 2}" r="18" fill="{color}" fill-opacity=".16" stroke="{color}" stroke-opacity=".7"/>
  <g transform="translate(18,{H / 2 - 12})">{icon(kind, color)}</g>
  <text x="57" y="26" class="mono" font-size="15.5" font-weight="800" letter-spacing="1" fill="{TEXT}">{esc(label)}</text>
  <text x="57" y="45" class="mono" font-size="13" font-weight="600" fill="{color}">{esc(sub)}</text>"""
    return svg(W, H, uid, body, title=f"{label} — {sub}").replace('rx="14"/></clipPath>', 'rx="12"/></clipPath>')


# ═════════════════════════════ SECTION HEADERS ═════════════════════════════
def header(num: str, title: str, uid: str) -> str:
    W, H = 1200, 76
    x2 = 104 + len(title) * (32 * 0.72 + 4) + 26
    body = f"""{panel(uid, W, H, seed=len(uid) * 5, star_count=40, nebula=False)}
  <defs><linearGradient id="{uid}-fade" x1="0" x2="1"><stop offset="0" stop-color="{CYAN}" stop-opacity=".9"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/></linearGradient></defs>
  <text x="34" y="48" class="mono" font-size="23" font-weight="700" fill="{CYAN}">//{num}</text>
  <text x="104" y="50" class="sans" font-size="32" font-weight="800" letter-spacing="4" fill="{TEXT}">{esc(title)}</text>
  <path d="M{x2 - 18:.0f} 32 l8 6 -8 6" fill="none" stroke="{CYAN}" stroke-width="2.2"/>
  <line x1="{x2:.0f}" y1="38" x2="{W - 52}" y2="38" stroke="url(#{uid}-fade)" stroke-width="2"/>
  <circle class="tw" cx="{W - 38}" cy="38" r="5" fill="{VIOLET}"/>"""
    return svg(W, H, uid, body, title=title, pad_top=HEADER_GAP)


# ═════════════════════════════ ABOUT / CREW CARD ═════════════════════════════
def about() -> str:
    W, uid = 1200, "about"
    top, row_h, line_h = 76, 54, 32
    rows_h = sum(row_h + (len(v) - 1) * line_h for _, v in CREW) - row_h
    H = int(top + rows_h + 52)
    with open(os.path.join(OUT, "src", "portrait.jpg"), "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    px, py, pr = 172, H / 2, 108
    rows, y = [], top
    for k, vals in CREW:
        rows.append(f'<text x="368" y="{y}" class="mono" font-size="17" font-weight="700" letter-spacing="2" fill="{CYAN}">{esc(k)}</text>')
        for j, v in enumerate(vals):
            rows.append(f'<text x="512" y="{y + j * line_h}" class="sans" font-size="24" font-weight="600" fill="{TEXT}">{esc(v)}</text>')
        y += row_h + (len(vals) - 1) * line_h
    css = """
  .spin { animation: spin 30s linear infinite; transform-origin: %dpx %dpx; }
  .spin.r { animation-direction: reverse; animation-duration: 45s; }
  @keyframes spin { to { transform: rotate(360deg); } }""" % (px, py)
    body = f"""{panel(uid, W, H, seed=7, star_count=90)}
  <defs><clipPath id="{uid}-face"><circle cx="{px}" cy="{py}" r="{pr}"/></clipPath></defs>
  <circle cx="{px}" cy="{py}" r="{pr + 10}" fill="none" stroke="url(#{uid}-edge)" stroke-width="3.5"/>
  <circle class="spin" cx="{px}" cy="{py}" r="{pr + 24}" fill="none" stroke="{CYAN}" stroke-opacity=".7" stroke-width="1.6" stroke-dasharray="2 10 40 10"/>
  <circle class="spin r" cx="{px}" cy="{py}" r="{pr + 36}" fill="none" stroke="{VIOLET}" stroke-opacity=".55" stroke-width="1.2" stroke-dasharray="80 30 4 30"/>
  <image href="data:image/jpeg;base64,{b64}" x="{px - pr}" y="{py - pr}" width="{pr * 2}" height="{pr * 2}" clip-path="url(#{uid}-face)" preserveAspectRatio="xMidYMid slice"/>
  <line x1="340" y1="40" x2="340" y2="{H - 40}" stroke="{LINE}" stroke-width="2"/>
  {''.join(rows)}"""
    return svg(W, H, uid, body, css, "Crew manifest — Nimna Niwarthana")


# ═════════════════════════════ STACK ═════════════════════════════
def stack() -> str:
    W, uid = 1200, "stack"
    row, top, chip_h = 66, 30, 44
    H = top + row * len(STACK) + 16
    parts = []
    for i, (label, color, items) in enumerate(STACK):
        y = top + i * row
        mid = y + chip_h / 2
        parts.append(f'<circle cx="44" cy="{mid}" r="5" fill="{color}"/>')
        parts.append(f'<text x="60" y="{mid + 6.5}" class="mono" font-size="18" font-weight="800" letter-spacing="2" fill="{color}">{esc(label)}</text>')
        parts.append(chips(192, y, items, color, size=19, gap=8, h=chip_h, pad=11))
        if i < len(STACK) - 1:
            parts.append(f'<line x1="40" y1="{y + row - 11}" x2="{W - 40}" y2="{y + row - 11}" stroke="{LINE}" stroke-dasharray="2 6"/>')
    body = panel(uid, W, H, seed=11, star_count=70) + "\n  " + "\n  ".join(parts)
    return svg(W, H, uid, body, title="Tech stack")


# ═════════════════════════════ PROJECT CARDS ═════════════════════════════
def project(p) -> str:
    W, H, uid = 590, 300, "p-" + p["slug"]
    c = p["color"]
    st_w = len(p["status"]) * (16 * 0.6 + 1.5) + 42
    lines = "".join(
        f'<text x="32" y="{184 + i * 30}" class="sans" font-size="22" font-weight="500" fill="{SOFT}">{esc(t)}</text>'
        for i, t in enumerate(p["lines"]))
    body = f"""{panel(uid, W, H, seed=len(p['slug']) * 13, star_count=45)}
  <g clip-path="url(#{uid}-clip)">{planet(W - 74, 64, 30, uid, c1=c, ring=False, spin_dur=24)}
    <ellipse cx="{W - 74}" cy="64" rx="54" ry="16" transform="rotate(-15 {W - 74} 64)" fill="none" stroke="{c}" stroke-opacity=".6" stroke-width="1.5"/>
  </g>
  <rect x="32" y="30" width="{st_w:.0f}" height="30" rx="15" fill="{c}" fill-opacity=".18" stroke="{c}" stroke-width="1.4"/>
  <circle class="tw" cx="49" cy="45" r="5" fill="{c}" style="animation-duration:1.6s"/>
  <text x="62" y="51" class="mono" font-size="16" font-weight="800" letter-spacing="1.5" fill="{c}">{esc(p['status'])}</text>
  <text x="30" y="108" class="sans" font-size="36" font-weight="800" fill="{TEXT}">{esc(p['title'])}</text>
  <text x="32" y="140" class="mono" font-size="17" font-weight="700" letter-spacing="1" fill="{c}">{esc(p['tag'])}</text>
  {lines}
  {chips(32, 234, p['chips'], c, size=17, gap=6, h=36, pad=9)}"""
    return svg(W, H, uid, body, title=f"{p['title']} — " + " ".join(p["lines"]))


# ═════════════════════════════ DIVIDER / FOOTER ═════════════════════════════
def divider() -> str:
    W, H, uid = 1200, 30, "div"
    body = f"""<defs><linearGradient id="{uid}-l" x1="0" x2="1">
    <stop offset="0" stop-color="{CYAN}" stop-opacity="0"/><stop offset=".5" stop-color="{VIOLET}"/><stop offset="1" stop-color="{PINK}" stop-opacity="0"/></linearGradient></defs>
  <line x1="40" y1="15" x2="{W - 40}" y2="15" stroke="url(#{uid}-l)" stroke-width="1.5"/>
  <circle cx="{W / 2}" cy="15" r="6" fill="{VIOLET}"/>
  <ellipse cx="{W / 2}" cy="15" rx="15" ry="4" fill="none" stroke="{CYAN}" stroke-width="1.5" transform="rotate(-15 {W / 2} 15)"/>
  <circle class="tw" cx="{W / 2 - 60}" cy="15" r="2" fill="{TEXT}"/><circle class="tw" cx="{W / 2 + 60}" cy="15" r="2" fill="{TEXT}" style="animation-delay:1.5s"/>"""
    return svg(W, H, uid, body)


def footer() -> str:
    W, H, uid = 1200, 210, "foot"
    rx = W - 150  # rocket x
    css = """
  .cur { animation: blink 1s steps(1) infinite; }
  @keyframes blink { 50% { opacity: 0; } }
  .rise { animation: rise 9s ease-in-out infinite; }
  @keyframes rise { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-6px); } }"""
    body = f"""{panel(uid, W, H, seed=3, star_count=110)}
  <defs><radialGradient id="{uid}-hz" cx=".5" cy="0" r=".7">
    <stop offset="0" stop-color="{VIOLET}" stop-opacity=".9"/><stop offset=".45" stop-color="#312E81"/><stop offset="1" stop-color="#0B0A26"/></radialGradient></defs>
  <g clip-path="url(#{uid}-clip)">
    <ellipse cx="{W / 2}" cy="{H + 560}" rx="900" ry="600" fill="url(#{uid}-hz)"/>
    <ellipse cx="{W / 2}" cy="{H + 560}" rx="900" ry="600" fill="none" stroke="url(#{uid}-edge)" stroke-width="3"/>
    <ellipse cx="{W / 2}" cy="{H + 560}" rx="910" ry="612" fill="none" stroke="{CYAN}" stroke-opacity=".25" stroke-width="10"/>
    <g class="rise">
      <path d="M{rx} 74 l12 -32 12 32 -5 0 0 17 -14 0 0 -17 z" fill="{TEXT}" opacity=".9"/>
      <path d="M{rx + 5} 106 l7 17 7 -17 z" fill="{AMBER}" class="tw" style="animation-duration:.4s"/>
    </g>
  </g>
  <text x="{W / 2}" y="82" text-anchor="middle" class="sans" font-size="40" font-weight="800" letter-spacing="1" fill="{TEXT}">Thanks for dropping by, traveller.</text>
  <text x="{W / 2}" y="128" text-anchor="middle" class="mono" font-size="24" font-weight="600" fill="{CYAN}">&gt; launch nimna-niwarthana.com<tspan class="cur">_</tspan></text>"""
    return svg(W, H, uid, body, css, "Thanks for dropping by — visit nimna-niwarthana.com")


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    write("hero.svg", hero())
    for slug, label, sub, color, kind in BUTTONS:
        write(f"btn-{slug}.svg", button(label, sub, color, kind, f"b-{slug}"))
    for key, (num, title) in SECTIONS.items():
        write(f"h-{key}.svg", header(num, title, f"h-{key}"))
    write("about.svg", about())
    write("stack.svg", stack())
    for p in PROJECTS:
        write(f"project-{p['slug']}.svg", project(p))
    write("divider.svg", divider())
    write("footer.svg", footer())


if __name__ == "__main__":
    main()
