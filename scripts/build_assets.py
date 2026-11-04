#!/usr/bin/env python3
"""Generate the static SVG artwork in ./assets (hero, buttons, panels, cards).

Run from the repo root:  python3 scripts/build_assets.py
Edit the CONTENT section below to update text, then re-run.
"""

import base64
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from theme import (  # noqa: E402
    AMBER, CYAN, DIM, LINE, MONO, MUTED, PINK, SANS, TEXT, VIOLET,
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
    dict(slug="catalogie", status="LIVE", color=CYAN, tag="FULL-STACK · SECURITY · JUN 2026 → NOW",
         title="Catalogie",
         lines=["One library for films, TV, games and books.",
                "Self-hosted PERN stack · 91 REST endpoints."],
         chips=["React", "TypeScript", "Express", "PostgreSQL", "Caddy"]),
    dict(slug="malditectist", status="PUBLISHED", color=VIOLET, tag="AI/ML RESEARCH · TAYLOR & FRANCIS",
         title="MalDitectist",
         lines=["Ensemble malware detection: signature +",
                "anomaly models, 98.9% Random Forest accuracy."],
         chips=["Python", "scikit-learn", "TensorFlow", "Django", "React"]),
    dict(slug="malscraper", status="TOOL", color=PINK, tag="MALWARE RESEARCH · DOCKER CLI",
         title="MalScraper",
         lines=["Turns raw Windows PE samples into labelled,",
                "ML-ready datasets: headers, opcodes, n-grams."],
         chips=["Python", "Docker", "Capstone", "pefile", "pandas"]),
    dict(slug="agenttesla", status="REPORT", color=AMBER, tag="REVERSE ENGINEERING · .NET INFOSTEALER",
         title="AgentTesla Analysis",
         lines=["Static, dynamic, memory and code analysis of",
                "a payload loaded reflectively in memory."],
         chips=["Ghidra", "dnSpy", "Volatility 3", "Wireshark"]),
]

SECTIONS = {
    "about": ("01", "MISSION PROFILE"),
    "stack": ("02", "ARSENAL"),
    "projects": ("03", "FEATURED MISSIONS"),
    "stats": ("04", "TELEMETRY"),
    "flight": ("05", "FLIGHT PATH"),
}

BUTTONS = [
    ("portfolio", "PORTFOLIO", "nimna-niwarthana.com", CYAN, "globe"),
    ("linkedin", "LINKEDIN", "let's connect", VIOLET, "in"),
    ("x", "X / TWITTER", "@niwarthananimna", PINK, "x"),
    ("coffee", "BUY ME A COFFEE", "fuel the rocket", AMBER, "cup"),
]


# ═════════════════════════════ HELPERS ═════════════════════════════
def write(name: str, content: str) -> None:
    path = os.path.join(OUT, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  wrote assets/{name}  ({len(content.encode()) / 1024:.1f} KB)")


def chip_w(text: str, size: float = 13) -> float:
    return len(text) * size * 0.6 + 22


def chips(x: float, y: float, items, color: str, size: float = 13, gap: float = 8, h: float = 28) -> str:
    out = []
    for it in items:
        w = chip_w(it, size)
        out.append(
            f'<g transform="translate({x:.1f},{y:.1f})">'
            f'<rect width="{w:.1f}" height="{h}" rx="{h / 2}" fill="{color}" fill-opacity=".09" stroke="{color}" stroke-opacity=".55"/>'
            f'<text x="{w / 2:.1f}" y="{h / 2 + size * 0.36:.1f}" text-anchor="middle" class="mono" font-size="{size}" fill="{TEXT}">{esc(it)}</text>'
            f'</g>'
        )
        x += w + gap
    return "".join(out)


def planet(cx, cy, r, uid, c1=VIOLET, c2="#312E81", ring=True, spin_dur=40) -> str:
    ring_back = ring_front = ""
    if ring:
        ring_back = (f'<path d="M{cx - r * 1.75} {cy} A{r * 1.75} {r * .42} -12 0 1 {cx + r * 1.75} {cy}" '
                     f'transform="rotate(-12 {cx} {cy})" fill="none" stroke="{CYAN}" stroke-opacity=".35" stroke-width="5"/>')
        ring_front = (f'<path d="M{cx - r * 1.75} {cy} A{r * 1.75} {r * .42} -12 0 0 {cx + r * 1.75} {cy}" '
                      f'transform="rotate(-12 {cx} {cy})" fill="none" stroke="url(#{uid}-edge)" stroke-width="5"/>'
                      f'<path d="M{cx - r * 1.55} {cy} A{r * 1.55} {r * .34} -12 0 0 {cx + r * 1.55} {cy}" '
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
    W, H, uid = 1200, 400, "hero"
    roles = []
    n = len(ROLES)
    for i, role in enumerate(ROLES):
        a = i / n
        b = a + 1.4 / (n * 3.2)
        d = (i + 1) / n
        c = d - 0.25 / (n * 3.2)
        kt = f"0;{a:.4f};{b:.4f};{c:.4f};{d:.4f};1"
        roles.append(f"""<clipPath id="r{i}"><rect x="96" y="232" height="48" width="0">
      <animate attributeName="width" values="0;0;640;640;0;0" keyTimes="{kt}" dur="{n * 3.2}s" repeatCount="indefinite"/>
    </rect></clipPath>
    <text x="100" y="266" class="mono" font-size="30" fill="{CYAN}" clip-path="url(#r{i})"><tspan fill="{PINK}">▸ </tspan>{esc(role)}<tspan class="cur">_</tspan></text>""")
    css = f"""
  .cur {{ animation: blink 1s steps(1) infinite; }}
  @keyframes blink {{ 50% {{ opacity: 0; }} }}
  .shoot {{ animation: shoot 7s ease-in infinite; opacity: 0; }}
  .shoot.b {{ animation-delay: 3.6s; }}
  @keyframes shoot {{ 0% {{ transform: translate(0,0); opacity: 0; }} 3% {{ opacity: 1; }} 14% {{ transform: translate(-460px,230px); opacity: 0; }} 100% {{ opacity: 0; }} }}
  .pulse {{ animation: pulse 2s ease-in-out infinite; }}
  @keyframes pulse {{ 0%,100% {{ opacity: 1; }} 50% {{ opacity: .2; }} }}
  .scan {{ animation: scan 6s linear infinite; }}
  @keyframes scan {{ from {{ transform: translateY(-20px); }} to {{ transform: translateY({H + 20}px); }} }}"""
    body = f"""{panel(uid, W, H, seed=29, star_count=190)}
  <g clip-path="url(#{uid}-clip)">
    <ellipse cx="980" cy="120" rx="420" ry="220" fill="url(#{uid}-nebC)"/>
    <g class="shoot"><line x1="1150" y1="20" x2="1230" y2="-20" stroke="{TEXT}" stroke-width="2" stroke-linecap="round" opacity=".8"/></g>
    <g class="shoot b"><line x1="820" y1="10" x2="880" y2="-20" stroke="{CYAN}" stroke-width="1.6" stroke-linecap="round"/></g>
    <!-- orbit + satellite -->
    <ellipse cx="985" cy="215" rx="185" ry="62" transform="rotate(-12 985 215)" fill="none" stroke="{DIM}" stroke-dasharray="3 7" opacity=".7"/>
    {planet(985, 215, 92, uid)}
    <g transform="rotate(-12 985 215)">
      <circle r="5" fill="{AMBER}">
        <animateMotion dur="14s" repeatCount="indefinite" path="M800 215 a185 62 0 1 0 370 0 a185 62 0 1 0 -370 0"/>
      </circle>
    </g>
    <circle cx="1130" cy="95" r="9" fill="#1F2A5C" stroke="{VIOLET}" stroke-opacity=".6"/>
    <rect class="scan" x="0" y="0" width="{W}" height="2" fill="{CYAN}" opacity=".06"/>
  </g>

  <!-- left: transmission -->
  <circle class="pulse" cx="104" cy="74" r="5" fill="{CYAN}"/>
  <text x="118" y="79" class="mono" font-size="14" fill="{CYAN}" letter-spacing="3">INCOMING TRANSMISSION · SECTOR NN-29</text>
  <text x="100" y="132" class="mono" font-size="20" fill="{MUTED}">nimna@orbit:~$ <tspan fill="{TEXT}">whoami</tspan></text>
  <text x="96" y="208" class="sans" font-size="66" font-weight="800" letter-spacing="2" fill="url(#{uid}-edge)">{esc(NAME)}</text>
  {''.join(roles)}
  <line x1="100" y1="316" x2="700" y2="316" stroke="{LINE}" stroke-width="1.5"/>
  <text x="100" y="346" class="mono" font-size="14" fill="{DIM}" letter-spacing="1.5">STATUS <tspan fill="#34D399">● ONLINE</tspan>   //   ORBIT <tspan fill="{MUTED}">AI/ML × CYBERSECURITY</tspan>   //   v3.0</text>
  <text x="{W - 40}" y="{H - 30}" text-anchor="end" class="mono" font-size="12" fill="{DIM}" letter-spacing="2">SYS.NN29 ◢</text>"""
    return svg(W, H, uid, body, css, f"{NAME} — " + " · ".join(ROLES))


# ═════════════════════════════ BUTTONS ═════════════════════════════
def icon(kind: str, color: str) -> str:
    s = f'stroke="{color}" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"'
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
  <g clip-path="url(#{uid}-clip)">{stars(W, H, 14, sum(map(ord, uid)), twinkle=.4)}</g>
  <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="12" fill="none" stroke="{color}" stroke-opacity=".55" stroke-width="1.5"/>
  {hud_corners(5, 5, W - 10, H - 10, 8, color, 1.4)}
  <circle cx="33" cy="{H / 2}" r="19" fill="{color}" fill-opacity=".12" stroke="{color}" stroke-opacity=".5"/>
  <g transform="translate(21,{H / 2 - 12})">{icon(kind, color)}</g>
  <text x="62" y="26" class="mono" font-size="13.5" font-weight="700" letter-spacing="1.5" fill="{TEXT}">{esc(label)}</text>
  <text x="62" y="44" class="mono" font-size="11.5" fill="{MUTED}">{esc(sub)}</text>"""
    return svg(W, H, uid, body, title=f"{label} — {sub}").replace('rx="14"/></clipPath>', 'rx="12"/></clipPath>')


# ═════════════════════════════ SECTION HEADERS ═════════════════════════════
def header(num: str, title: str, uid: str) -> str:
    W, H = 1200, 64
    x2 = 118 + len(title) * 26 * 0.68 + 30
    body = f"""{panel(uid, W, H, seed=len(uid) * 5, star_count=40, nebula=False)}
  <defs><linearGradient id="{uid}-fade" x1="0" x2="1"><stop offset="0" stop-color="{CYAN}" stop-opacity=".8"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/></linearGradient></defs>
  <text x="34" y="40" class="mono" font-size="17" fill="{CYAN}">//{num}</text>
  <text x="96" y="41.5" class="sans" font-size="24" font-weight="800" letter-spacing="4" fill="{TEXT}">{esc(title)}</text>
  <path d="M{x2 - 16:.0f} 28 l6 4 -6 4" fill="none" stroke="{CYAN}" stroke-width="1.5"/>
  <line x1="{x2:.0f}" y1="32" x2="{W - 50}" y2="32" stroke="url(#{uid}-fade)" stroke-width="1.5"/>
  <circle class="tw" cx="{W - 36}" cy="32" r="4" fill="{PINK}"/>"""
    return svg(W, H, uid, body, title=title)


# ═════════════════════════════ ABOUT / CREW CARD ═════════════════════════════
def about() -> str:
    W, uid = 1200, "about"
    row_h, line_h = 44, 26
    rows_h = sum(row_h + (len(v) - 1) * line_h for _, v in CREW)
    H = max(rows_h + 120, 360)
    with open(os.path.join(OUT, "src", "portrait.jpg"), "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    px, py, pr = 190, H / 2, 112
    rows, y = [], 92
    for k, vals in CREW:
        rows.append(f'<text x="420" y="{y}" class="mono" font-size="14" letter-spacing="2" fill="{CYAN}">{esc(k)}</text>')
        for j, v in enumerate(vals):
            rows.append(f'<text x="560" y="{y + j * line_h}" class="sans" font-size="19" fill="{TEXT}">{esc(v)}</text>')
        y += row_h + (len(vals) - 1) * line_h
    css = """
  .spin { animation: spin 30s linear infinite; transform-origin: %dpx %dpx; }
  .spin.r { animation-direction: reverse; animation-duration: 45s; }
  @keyframes spin { to { transform: rotate(360deg); } }""" % (px, py)
    body = f"""{panel(uid, W, int(H), seed=7, star_count=90)}
  <defs><clipPath id="{uid}-face"><circle cx="{px}" cy="{py}" r="{pr}"/></clipPath></defs>
  <circle cx="{px}" cy="{py}" r="{pr + 10}" fill="none" stroke="url(#{uid}-edge)" stroke-width="3"/>
  <circle class="spin" cx="{px}" cy="{py}" r="{pr + 24}" fill="none" stroke="{CYAN}" stroke-opacity=".6" stroke-width="1.5" stroke-dasharray="2 10 40 10"/>
  <circle class="spin r" cx="{px}" cy="{py}" r="{pr + 36}" fill="none" stroke="{VIOLET}" stroke-opacity=".45" stroke-width="1" stroke-dasharray="80 30 4 30"/>
  <image href="data:image/jpeg;base64,{b64}" x="{px - pr}" y="{py - pr}" width="{pr * 2}" height="{pr * 2}" clip-path="url(#{uid}-face)" preserveAspectRatio="xMidYMid slice"/>
  <text x="420" y="52" class="mono" font-size="12" letter-spacing="3" fill="{DIM}">CREW MANIFEST · ID NN-29 · CLEARANCE ◆◆◆</text>
  <line x1="400" y1="66" x2="400" y2="{H - 40}" stroke="{LINE}" stroke-width="1.5"/>
  {''.join(rows)}"""
    return svg(W, int(H), uid, body, css, "Crew manifest — Nimna Niwarthana")


# ═════════════════════════════ STACK ═════════════════════════════
def stack() -> str:
    W, uid = 1200, "stack"
    row, top = 62, 58
    H = top + row * len(STACK) + 22
    parts = [f'<text x="40" y="40" class="mono" font-size="12" letter-spacing="3" fill="{DIM}">ONBOARD SYSTEMS · {sum(len(s[2]) for s in STACK)} MODULES LOADED</text>']
    for i, (label, color, items) in enumerate(STACK):
        y = top + i * row
        parts.append(f'<circle cx="46" cy="{y + 21}" r="4" fill="{color}"/>')
        parts.append(f'<text x="60" y="{y + 26}" class="mono" font-size="14" font-weight="700" letter-spacing="2" fill="{color}">{esc(label)}</text>')
        parts.append(chips(210, y + 6, items, color, size=14.5, gap=10, h=32))
        if i < len(STACK) - 1:
            parts.append(f'<line x1="40" y1="{y + row - 6}" x2="{W - 40}" y2="{y + row - 6}" stroke="{LINE}" stroke-dasharray="2 6"/>')
    body = panel(uid, W, H, seed=11, star_count=70) + "\n  " + "\n  ".join(parts)
    return svg(W, H, uid, body, title="Tech stack")


# ═════════════════════════════ PROJECT CARDS ═════════════════════════════
def project(p) -> str:
    W, H, uid = 590, 250, "p-" + p["slug"]
    c = p["color"]
    st_w = len(p["status"]) * (12 * 0.6 + 1.5) + 38
    lines = "".join(
        f'<text x="32" y="{124 + i * 26}" class="sans" font-size="17" fill="{MUTED}">{esc(t)}</text>'
        for i, t in enumerate(p["lines"]))
    body = f"""{panel(uid, W, H, seed=len(p['slug']) * 13, star_count=45)}
  <g clip-path="url(#{uid}-clip)">{planet(W - 70, 62, 30, uid, c1=c, ring=False, spin_dur=24)}
    <ellipse cx="{W - 70}" cy="62" rx="52" ry="16" transform="rotate(-15 {W - 70} 62)" fill="none" stroke="{c}" stroke-opacity=".5"/>
  </g>
  <rect x="32" y="30" width="{st_w:.0f}" height="24" rx="12" fill="{c}" fill-opacity=".15" stroke="{c}"/>
  <circle class="tw" cx="46" cy="42" r="4" fill="{c}" style="animation-duration:1.6s"/>
  <text x="56" y="46.5" class="mono" font-size="12" font-weight="700" letter-spacing="1.5" fill="{c}">{esc(p['status'])}</text>
  <text x="{32 + st_w + 12:.0f}" y="46.5" class="mono" font-size="11.5" letter-spacing="1" fill="{DIM}">{esc(p['tag'])}</text>
  <text x="30" y="94" class="sans" font-size="31" font-weight="800" fill="{TEXT}">{esc(p['title'])}</text>
  {lines}
  {chips(32, 186, p['chips'], c, size=12.5, gap=7, h=26)}
  <text x="{W - 32}" y="{H - 24}" text-anchor="end" class="mono" font-size="12" fill="{c}">LAUNCH ↗</text>"""
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
    W, H, uid = 1200, 220, "foot"
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
      <path d="M{W / 2 + 330} 70 l10 -26 10 26 -4 0 0 14 -12 0 0 -14 z" fill="{TEXT}" opacity=".85"/>
      <path d="M{W / 2 + 334} 98 l6 14 6 -14 z" fill="{AMBER}" class="tw" style="animation-duration:.4s"/>
    </g>
  </g>
  <text x="{W / 2}" y="58" text-anchor="middle" class="mono" font-size="13" letter-spacing="5" fill="{DIM}">END OF TRANSMISSION</text>
  <text x="{W / 2}" y="100" text-anchor="middle" class="sans" font-size="30" font-weight="800" letter-spacing="2" fill="{TEXT}">Thanks for dropping by, traveller.</text>
  <text x="{W / 2}" y="136" text-anchor="middle" class="mono" font-size="16" fill="{CYAN}">&gt; launch nimna-niwarthana.com<tspan class="cur">_</tspan></text>"""
    return svg(W, H, uid, body, css, "End of transmission — visit nimna-niwarthana.com")


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
