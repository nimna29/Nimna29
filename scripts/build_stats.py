#!/usr/bin/env python3
"""Generate live GitHub telemetry cards (stats, languages, streak) as SVG.

Runs inside GitHub Actions - no third-party card services, so nothing can rate
limit or go offline. Uses the GitHub GraphQL API with GH_TOKEN.

  GH_TOKEN=... python3 scripts/build_stats.py --user nimna29 --out dist
  python3 scripts/build_stats.py --mock --out /tmp/preview      # sample data

If the API call fails, "signal lost" placeholder cards are written instead, so
the README never shows a broken image.
"""

import argparse
import datetime as dt
import json
import os
import random
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(__file__))
from theme import AMBER, CYAN, GREEN, LINE, MUTED, SOFT, TEXT, VIOLET, esc, panel, svg  # noqa: E402

API = "https://api.github.com/graphql"
EXCLUDE_LANGS = {s.strip() for s in os.environ.get("EXCLUDE_LANGS", "HTML,CSS,Jupyter Notebook").split(",") if s.strip()}


# ═════════════════════════════ DATA ═════════════════════════════
def gql(token: str, query: str, variables: dict) -> dict:
    req = urllib.request.Request(
        API,
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json",
                 "User-Agent": "profile-telemetry"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.load(r)
    if data.get("errors"):
        raise RuntimeError(data["errors"])
    return data["data"]


Q_USER = """
query($login: String!, $after: String) {
  user(login: $login) {
    createdAt
    followers { totalCount }
    pullRequests { totalCount }
    issues { totalCount }
    repositoriesContributedTo(contributionTypes: [COMMIT, PULL_REQUEST, ISSUE, REPOSITORY]) { totalCount }
    repositories(ownerAffiliations: OWNER, first: 100, after: $after) {
      totalCount
      pageInfo { hasNextPage endCursor }
      nodes {
        isFork
        stargazerCount
        languages(first: 12, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name color } }
        }
      }
    }
  }
}"""

Q_YEAR = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      totalCommitContributions
      restrictedContributionsCount
      contributionCalendar { weeks { contributionDays { date contributionCount } } }
    }
  }
}"""


def fetch(token: str, login: str) -> dict:
    repos, after, user = [], None, None
    while True:
        user = gql(token, Q_USER, {"login": login, "after": after})["user"]
        page = user["repositories"]
        repos += page["nodes"]
        if not page["pageInfo"]["hasNextPage"]:
            break
        after = page["pageInfo"]["endCursor"]

    now = dt.datetime.now(dt.timezone.utc)
    start = dt.datetime.fromisoformat(user["createdAt"].replace("Z", "+00:00"))
    days, commits, private = {}, 0, 0
    y = start.year
    while y <= now.year:
        f = max(start, dt.datetime(y, 1, 1, tzinfo=dt.timezone.utc))
        t = min(now, dt.datetime(y, 12, 31, 23, 59, 59, tzinfo=dt.timezone.utc))
        cc = gql(token, Q_YEAR, {"login": login, "from": f.isoformat(), "to": t.isoformat()})["user"]["contributionsCollection"]
        commits += cc["totalCommitContributions"]
        private += cc["restrictedContributionsCount"]
        for w in cc["contributionCalendar"]["weeks"]:
            for d in w["contributionDays"]:
                days[d["date"]] = d["contributionCount"]
        y += 1

    langs = {}
    for r in repos:
        if r["isFork"]:
            continue
        for e in r["languages"]["edges"]:
            n = e["node"]["name"]
            if n in EXCLUDE_LANGS:
                continue
            cur = langs.setdefault(n, {"size": 0, "color": e["node"]["color"] or MUTED})
            cur["size"] += e["size"]

    return {
        "stars": sum(r["stargazerCount"] for r in repos if not r["isFork"]),
        "repos": user["repositories"]["totalCount"],
        "followers": user["followers"]["totalCount"],
        "prs": user["pullRequests"]["totalCount"],
        "issues": user["issues"]["totalCount"],
        "contributed": user["repositoriesContributedTo"]["totalCount"],
        "commits": commits + private,
        "days": dict(sorted(days.items())),
        "langs": langs,
        "since": start.year,
    }


def mock() -> dict:
    rnd = random.Random(29)
    today = dt.date.today()
    days = {}
    for i in range(900, -1, -1):
        d = today - dt.timedelta(days=i)
        days[d.isoformat()] = 0 if rnd.random() < .35 else rnd.randint(1, 12)
    for i in range(9):
        days[(today - dt.timedelta(days=i)).isoformat()] = rnd.randint(1, 6)
    return {"stars": 48, "repos": 31, "followers": 57, "prs": 64, "issues": 19, "contributed": 12,
            "commits": 1342, "days": days, "since": 2020,
            "langs": {"Python": {"size": 900, "color": "#3572A5"}, "TypeScript": {"size": 640, "color": "#3178c6"},
                      "JavaScript": {"size": 380, "color": "#f1e05a"}, "C#": {"size": 160, "color": "#178600"},
                      "Dart": {"size": 120, "color": "#00B4AB"}, "Shell": {"size": 50, "color": "#89e051"},
                      "C": {"size": 40, "color": "#555555"}}}


def streaks(days: dict):
    items = list(days.items())
    today = dt.date.today()
    total = sum(c for _, c in items)
    longest, run, run_start, best = 0, 0, None, (None, None)
    for d, c in items:
        if c > 0:
            if run == 0:
                run_start = d
            run += 1
            if run > longest:
                longest, best = run, (run_start, d)
        else:
            run = 0
    # current streak: today counts if active, otherwise start from yesterday
    cur, cur_start, cur_end = 0, None, None
    rev = sorted(items, reverse=True)
    if rev and rev[0][0] == today.isoformat() and rev[0][1] == 0:
        rev = rev[1:]
    for d, c in rev:
        if c > 0:
            cur += 1
            cur_start = d
            cur_end = cur_end or d
        else:
            break
    return total, (cur, cur_start, cur_end), (longest, *best)


def fmt_date(s):
    if not s:
        return "-"
    d = dt.date.fromisoformat(s)
    out = f"{d:%b} {d.day}"
    return out if d.year == dt.date.today().year else f"{out}, {d.year}"


def k(n: int) -> str:
    return f"{n / 1000:.1f}k" if n >= 10000 else f"{n:,}"


# ═════════════════════════════ CARDS ═════════════════════════════
# Half-width cards are shown at ~0.7x on the profile page, so labels are
# >= 17 units and numbers >= 36 units to stay readable after scaling.
def title_row(text: str, color: str = CYAN, right: str = "") -> str:
    out = f'<text x="32" y="52" class="mono" font-size="21" font-weight="800" letter-spacing="3" fill="{color}">{esc(text)}</text>'
    if right:
        out += f'<text x="558" y="52" text-anchor="end" class="mono" font-size="18" font-weight="700" letter-spacing="1.5" fill="{SOFT}">{esc(right)}</text>'
    return out


def stats_card(d: dict) -> str:
    W, H, uid = 590, 300, "stats"
    metrics = [
        ("COMMITS", k(d["commits"]), CYAN), ("PULL REQUESTS", k(d["prs"]), VIOLET),
        ("STARS EARNED", k(d["stars"]), AMBER), ("ISSUES", k(d["issues"]), GREEN),
        ("FOLLOWERS", k(d["followers"]), CYAN), ("CONTRIBUTED TO", k(d["contributed"]), VIOLET),
    ]
    cells = []
    for i, (lab, val, c) in enumerate(metrics):
        x = 32 + (i % 2) * 190
        y = 78 + (i // 2) * 70
        cells.append(f'<rect x="{x}" y="{y}" width="4" height="58" rx="2" fill="{c}"/>'
                     f'<text x="{x + 16}" y="{y + 16}" class="mono" font-size="17" font-weight="700" letter-spacing="1" fill="{SOFT}">{lab}</text>'
                     f'<text x="{x + 16}" y="{y + 54}" class="sans" font-size="36" font-weight="800" fill="{TEXT}">{val}</text>')
    # radar ring: repositories in the core
    cx, cy, rr = 482, 160, 72
    rings = "".join(f'<circle cx="{cx}" cy="{cy}" r="{r:.1f}" fill="none" stroke="{LINE}" stroke-width="1.4"/>' for r in (rr * .4, rr * .7, rr))
    css = f"""
  .sweep {{ animation: sweep 5s linear infinite; transform-origin: {cx}px {cy}px; }}
  @keyframes sweep {{ to {{ transform: rotate(360deg); }} }}"""
    body = f"""{panel(uid, W, H, seed=41, star_count=40)}
  {title_row("SHIP LOG", right=f"SINCE {d['since']}")}
  {''.join(cells)}
  <defs><linearGradient id="{uid}-sw" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{CYAN}" stop-opacity="0"/><stop offset="1" stop-color="{CYAN}" stop-opacity=".55"/></linearGradient></defs>
  {rings}
  <path d="M{cx - rr} {cy} H{cx + rr} M{cx} {cy - rr} V{cy + rr}" stroke="{LINE}"/>
  <g class="sweep"><path d="M{cx} {cy} L{cx + rr} {cy} A{rr} {rr} 0 0 0 {cx + rr * .707:.1f} {cy - rr * .707:.1f} Z" fill="url(#{uid}-sw)"/></g>
  <circle cx="{cx + 34}" cy="{cy - 40}" r="3.5" fill="{VIOLET}" class="tw"/>
  <circle cx="{cx - 44}" cy="{cy + 22}" r="3" fill="{AMBER}" class="tw" style="animation-delay:1.2s"/>
  <text x="{cx}" y="{cy + 12}" text-anchor="middle" class="sans" font-size="36" font-weight="800" fill="{TEXT}">{k(d['repos'])}</text>
  <text x="{cx}" y="{cy + rr + 34}" text-anchor="middle" class="mono" font-size="17" font-weight="700" letter-spacing="2" fill="{SOFT}">REPOSITORIES</text>"""
    return svg(W, H, uid, body, css, "GitHub stats")


def langs_card(d: dict) -> str:
    W, H, uid = 590, 300, "langs"
    items = sorted(d["langs"].items(), key=lambda kv: -kv[1]["size"])[:6]
    total = sum(v["size"] for _, v in items) or 1
    bar_x, bar_y, bar_w, bar_h, x = 32, 80, W - 64, 16, 32.0
    segs = []
    for name, v in items:
        w = bar_w * v["size"] / total
        segs.append(f'<rect x="{x:.1f}" y="{bar_y}" width="{max(w - 2, 1):.1f}" height="{bar_h}" fill="{v["color"]}"/>')
        x += w
    rows = []
    for i, (name, v) in enumerate(items):
        cx = 32 + (i % 2) * 280
        cy = 150 + (i // 2) * 52
        pct = 100 * v["size"] / total
        name = name if len(name) <= 13 else name[:12] + "…"
        rows.append(f'<circle cx="{cx + 8}" cy="{cy - 7}" r="8" fill="{v["color"]}"/>'
                    f'<text x="{cx + 26}" y="{cy}" class="sans" font-size="23" font-weight="600" fill="{TEXT}">{esc(name)}</text>'
                    f'<text x="{cx + 250}" y="{cy}" text-anchor="end" class="mono" font-size="19" font-weight="700" fill="{SOFT}">{pct:.1f}%</text>')
    body = f"""{panel(uid, W, H, seed=53, star_count=40)}
  {title_row("FUEL MIX", VIOLET, right="TOP LANGUAGES")}
  <defs><clipPath id="{uid}-bar"><rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="{bar_h}" rx="{bar_h / 2}"/></clipPath></defs>
  <g clip-path="url(#{uid}-bar)"><rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="{bar_h}" fill="{LINE}"/>{''.join(segs)}</g>
  {''.join(rows)}"""
    return svg(W, H, uid, body, title="Top languages")


def days(n: int) -> str:
    return f"{n} day" if n == 1 else f"{n} days"


def icon_grid(cx: float, cy: float) -> str:
    """Mini contribution grid - icon for total contributions."""
    s, g = 9, 3
    shade = [[.3, .6, 1, .45, .8], [.6, 1, .35, 1, .55], [1, .4, .7, .3, 1]]
    x0, y0 = cx - (5 * s + 4 * g) / 2, cy - (3 * s + 2 * g) / 2
    return "".join(
        f'<rect x="{x0 + c * (s + g):.1f}" y="{y0 + r * (s + g):.1f}" width="{s}" height="{s}" rx="2" fill="{CYAN}" opacity="{o}"/>'
        for r, row in enumerate(shade) for c, o in enumerate(row))


def icon_trophy(cx: float, cy: float, uid: str) -> str:
    """Trophy - icon for longest streak."""
    return f"""<g transform="translate({cx} {cy})">
    <path d="M-14 -15 H-21 V-11 C-21 -3 -16 1 -11 1 M14 -15 H21 V-11 C21 -3 16 1 11 1" fill="none" stroke="{VIOLET}" stroke-width="3.5" stroke-linecap="round"/>
    <path d="M-14 -20 H14 V-8 C14 4 7 11 0 11 C-7 11 -14 4 -14 -8 Z" fill="url(#{uid}-tr)"/>
    <rect x="-3.5" y="10" width="7" height="8" fill="#7C3AED"/>
    <rect x="-12" y="17" width="24" height="7" rx="2.5" fill="url(#{uid}-tr)"/>
    <path d="M0 -14 l2.4 4.9 5.4 .8 -3.9 3.8 .9 5.4 -4.8 -2.5 -4.8 2.5 .9 -5.4 -3.9 -3.8 5.4 -.8z" fill="#F5F3FF" opacity=".9"/>
  </g>"""


def icon_flame(cx: float, cy: float, uid: str, lit: bool) -> str:
    """Layered vector flame - icon for current streak. Sways gently; dim when the streak is 0."""
    return f"""<circle class="glow" cx="{cx}" cy="{cy + 6}" r="50" fill="url(#{uid}-glow)" opacity="{'.75' if lit else '.2'}"/>
  <g transform="translate({cx} {cy}) scale(.92)" opacity="{'1' if lit else '.4'}">
    <g class="fl-outer"><path d="M0 -28 C6 -18 20 -10 20 6 C20 19 11 28 0 28 C-11 28 -20 19 -20 6 C-20 -4 -14 -10 -10 -16 C-9 -9 -6 -5 -2 -4 C-4 -12 -4 -21 0 -28 Z" fill="url(#{uid}-fo)"/></g>
    <g class="fl-mid"><path d="M1 -8 C5 -2 12 4 12 12 C12 20 6 25 0 25 C-6 25 -12 20 -12 12 C-12 5 -7 0 -4 -4 C-3 0 -1 2 1 2 C0 -2 -.5 -5 1 -8 Z" fill="{AMBER}"/></g>
    <g class="fl-core"><path d="M0 6 C3 10 6 14 6 18 C6 22 3 25 0 25 C-3 25 -6 22 -6 18 C-6 14 -3 10 0 6 Z" fill="#FEF3C7"/></g>
  </g>"""


def streak_card(d: dict) -> str:
    W, H, uid = 1200, 320, "streak"
    total, (cur, cs, ce), (lng, ls, le) = streaks(d["days"])
    # last 52 weeks as weekly bars; this week is highlighted amber
    vals = list(d["days"].values())[-364:]
    weeks = [sum(vals[i:i + 7]) for i in range(0, len(vals), 7)]
    mx = max(weeks) if weeks and max(weeks) else 1
    gx, gw, gh, gy = 40, W - 80, 56, H - 26
    bw = gw / max(len(weeks), 1)
    bars = "".join(
        f'<rect x="{gx + i * bw + 1:.1f}" y="{gy - max(gh * v / mx, 3):.1f}" width="{bw - 3:.1f}" height="{max(gh * v / mx, 3):.1f}" rx="2" '
        + (f'fill="{AMBER}"/>' if i == len(weeks) - 1 and v else f'fill="url(#{uid}-bar)" opacity="{.4 + .6 * v / mx:.2f}"/>')
        for i, v in enumerate(weeks))

    iy = 52  # icon row; numbers, labels and dates sit on shared baselines below

    def col(x, label, value, sub, color):
        return (f'<text x="{x}" y="138" text-anchor="middle" class="sans" font-size="56" font-weight="800" fill="{TEXT}">{value}</text>'
                f'<text x="{x}" y="174" text-anchor="middle" class="mono" font-size="20" font-weight="800" letter-spacing="2.5" fill="{color}">{label}</text>'
                f'<text x="{x}" y="203" text-anchor="middle" class="mono" font-size="18" font-weight="600" fill="{SOFT}">{esc(sub)}</text>')

    css = """
  .fl-outer, .fl-mid, .fl-core { transform-box: fill-box; transform-origin: 50% 100%; }
  .fl-outer { animation: sway 2.6s ease-in-out infinite; }
  .fl-mid { animation: sway 2.6s ease-in-out -.5s infinite; }
  .fl-core { animation: breathe 1.3s ease-in-out infinite; }
  .glow { animation: glow 2.6s ease-in-out infinite; }
  @keyframes sway { 0%,100% { transform: rotate(0deg) scale(1,1); } 30% { transform: rotate(-3deg) scale(.97,1.04); } 70% { transform: rotate(3deg) scale(1.02,.98); } }
  @keyframes breathe { 0%,100% { transform: scale(1,1); } 50% { transform: scale(.9,1.1); } }
  @keyframes glow { 0%,100% { opacity: .55; } 50% { opacity: .9; } }"""
    body = f"""{panel(uid, W, H, seed=61, star_count=90)}
  <defs>
    <linearGradient id="{uid}-bar" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="{VIOLET}"/><stop offset="1" stop-color="{CYAN}"/></linearGradient>
    <linearGradient id="{uid}-fo" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FCD34D"/><stop offset=".55" stop-color="#F97316"/><stop offset="1" stop-color="#EA580C"/></linearGradient>
    <linearGradient id="{uid}-tr" x1="0" x2="1"><stop offset="0" stop-color="#DDD6FE"/><stop offset=".5" stop-color="{VIOLET}"/><stop offset="1" stop-color="#6D28D9"/></linearGradient>
    <radialGradient id="{uid}-glow" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{AMBER}" stop-opacity=".55"/><stop offset="1" stop-color="{AMBER}" stop-opacity="0"/></radialGradient>
  </defs>
  <path d="M400 40 V206 M800 40 V206" stroke="{LINE}" stroke-width="1.5"/>
  {icon_grid(200, iy)}
  {icon_flame(600, iy - 2, uid, cur > 0)}
  {icon_trophy(1000, iy, uid)}
  {col(200, "TOTAL CONTRIBUTIONS", k(total), f"{d['since']} - present", CYAN)}
  {col(600, "CURRENT STREAK", days(cur), f"{fmt_date(cs)} - {fmt_date(ce)}" if cur else "ignition pending", AMBER)}
  {col(1000, "LONGEST STREAK", days(lng), f"{fmt_date(ls)} - {fmt_date(le)}", VIOLET)}
  <line x1="{gx}" y1="{gy + 1}" x2="{gx + gw}" y2="{gy + 1}" stroke="{LINE}" stroke-width="1.5"/>
  {bars}"""
    return svg(W, H, uid, body, css, f"Contribution streak - current {days(cur)}, longest {days(lng)}")


def placeholder(name: str, w: int, h: int) -> str:
    body = f"""{panel("ph", w, h, seed=w, star_count=40)}
  <text x="{w / 2}" y="{h / 2 - 6}" text-anchor="middle" class="mono" font-size="24" font-weight="800" letter-spacing="3" fill="{AMBER}">SIGNAL LOST</text>
  <text x="{w / 2}" y="{h / 2 + 28}" text-anchor="middle" class="mono" font-size="17" font-weight="600" fill="{SOFT}">{esc(name)} · re-syncing next orbit</text>"""
    return svg(w, h, "ph", body, title="Telemetry unavailable")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--user", default=os.environ.get("GITHUB_REPOSITORY_OWNER", "nimna29"))
    ap.add_argument("--out", default="dist")
    ap.add_argument("--mock", action="store_true")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    cards = {"stats.svg": (stats_card, 590, 300), "langs.svg": (langs_card, 590, 300),
             "streak.svg": (streak_card, 1200, 320)}
    try:
        data = mock() if a.mock else fetch(os.environ["GH_TOKEN"], a.user)
    except Exception as e:  # keep the README intact even if the API hiccups
        print(f"::warning::telemetry fetch failed: {e}")
        data = None
    for fname, (fn, w, h) in cards.items():
        content = fn(data) if data else placeholder(fname[:-4], w, h)
        with open(os.path.join(a.out, fname), "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
        print(f"wrote {a.out}/{fname}")


if __name__ == "__main__":
    main()
