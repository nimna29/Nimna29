#!/usr/bin/env python3
"""Live telemetry cards for the Observation Deck README design.

Reuses the GitHub GraphQL fetch from build_stats.py and writes:
  deck-stats.svg     lifetime contributions + six counters
  deck-activity.svg  streak ring + top languages

  GH_TOKEN=... python scripts/deck_stats.py --user nimna29 --out dist
  python scripts/deck_stats.py --mock --out dist        # sample data

If the API call fails, "signal lost" placeholders are written instead, so the
README never shows a broken image.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from build_stats import fetch, fmt_date, k, mock, streaks  # noqa: E402
from deck_kit import (  # noqa: E402
    ELECTRIC, FAINT, GOLD, MUTED, TEXT, M, T, TP, arc, frame, lin, plate, rr, svg, tw, write,
)

CSS = """
.dk-bar{transform-box:fill-box;transform-origin:50% 100%;animation:dk-bar 2.8s ease-in-out infinite}
@keyframes dk-bar{0%,100%{transform:scaleY(1)}50%{transform:scaleY(.72)}}
.dk-ring{stroke-dasharray:var(--len) 999;animation:dk-ring 1.8s ease-out both}
@keyframes dk-ring{from{stroke-dasharray:0 999}}
.dk-fill{transform-box:fill-box;transform-origin:0 50%;animation:dk-fill 1.4s ease-out both}
@keyframes dk-fill{from{transform:scaleX(0)}}"""


def stats_card(d):
    W, oy = 1200, 14
    total = sum(d["days"].values())
    o = frame(0, oy, 392, 250, 20, "LIFETIME CONTRIBUTIONS")
    txt = k(total)
    size = min(88, 88 * 290 / tw(txt, 88, "display"))
    nw = tw(txt, size, "display")
    o += TP(48, oy + 150, size, txt, fill=lin([(0, TEXT), (.5, TEXT), (1, GOLD)]))
    o += f'<path d="M40 {oy + 70} h-10 v100 h10 M{56 + nw:.1f} {oy + 70} h10 v100 h-10" fill="none" stroke="{ELECTRIC}" stroke-opacity=".6" stroke-width="1.5"/>'
    o += T(32, oy + 204, 17, f"since {d['since']} · weekly activity below", "ui4", MUTED)
    vals = list(d["days"].values())[-245:]
    weeks = [sum(vals[i:i + 7]) for i in range(0, len(vals), 7)] or [0]
    mx = max(weeks) or 1
    for i, v in enumerate(weeks[-35:]):
        hh = 3 + 15 * v / mx
        o += (f'<rect class="dk-bar" style="animation-delay:{i * .08:.2f}s" x="{32 + i * 9.4:.1f}" y="{oy + 238 - hh:.1f}" width="6" height="{hh:.1f}" '
              f'fill="{GOLD if i == len(weeks[-35:]) - 1 else ELECTRIC}" opacity="{.3 + .7 * v / mx:.2f}"/>')
    cells = [("Pull requests", d["prs"], "pr"), ("Issues", d["issues"], "issue"), ("Stars earned", d["stars"], "star"),
             ("Repositories", d["repos"], "repo"), ("Followers", d["followers"], "users"), ("Contributed to", d["contributed"], "pulse")]
    cw, ch = (W - 408 - 32) / 3, 117
    for i, (lab, val, ic) in enumerate(cells):
        x, y = 408 + (i % 3) * (cw + 16), oy + (i // 3) * (ch + 16)
        o += frame(x, y, cw, ch, 12, nodes=False, brk=False, ring=.42)
        o += plate(x + 16, y + 16, 38, ic, GOLD if i in (2, 3) else ELECTRIC)
        o += T(x + 66, y + 41, 18, lab, "ui5", MUTED) + T(x + 18, y + 98, 46, k(val), "ui7", TEXT)
    return svg(W, 250 + oy + 6, o, CSS, f"GitHub stats - {k(total)} contributions since {d['since']}")


def activity_card(d):
    W, oy, H = 1200, 14, 240
    total, (cur, cs, ce), (best, bs, be) = streaks(d["days"])
    o = frame(0, oy, 592, H, 20, "STREAK")
    cx, cy, r = 296, oy + 112, 60
    frac = min(cur / best, 1) if best else 0
    o += f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#12264d" stroke-width="10"/>'
    if frac > 0:
        o += (f'<path class="dk-ring" style="--len:{2 * 3.14159 * r * min(frac, .999):.0f}" d="{arc(cx, cy, r, -90, -90 + 359.9 * frac)}" '
              f'fill="none" stroke="{GOLD}" stroke-width="10" stroke-linecap="round"/>')
    o += T(cx, cy + 18, 54 if cur < 100 else 40, str(cur), "display", TEXT, "middle")
    o += T(cx, oy + 206, 14, "DAY STREAK", "ui6", GOLD, "middle", 4)
    o += M(cx, oy + 225, 12.5, f"{fmt_date(cs)} - {fmt_date(ce)}" if cur else "ignition pending", FAINT, "middle")
    for x, v, lab, s in ((104, k(total), "Contributions", f"since {d['since']}"),
                         (488, str(best), "Best streak", f"{fmt_date(bs)} - {fmt_date(be)}")):
        o += T(x, cy + 6, 40, v, "ui7", TEXT, "middle") + T(x, cy + 34, 17, lab, "ui5", ELECTRIC, "middle") + M(x, cy + 56, 12.5, s, FAINT, "middle")
    o += frame(608, oy, 592, H, 20, "LANGUAGES")
    items = sorted(d["langs"].items(), key=lambda kv: -kv[1]["size"])[:6]
    tot = sum(v["size"] for _, v in items) or 1
    top = max((v["size"] for _, v in items), default=1) or 1
    for i, (name, v) in enumerate(items):
        y = oy + 56 + i * 30
        name = name if len(name) <= 14 else name[:13] + "."
        o += f'<circle cx="644" cy="{y - 6}" r="6" fill="{v["color"]}"/>' + T(662, y, 18, name, "ui5", TEXT)
        o += rr(810, y - 11, 270, 9, 0, fill="#12264d")
        o += f'<rect class="dk-fill" style="animation-delay:{i * .12:.2f}s" x="810" y="{y - 11}" width="{max(270 * v["size"] / top, 3):.1f}" height="9" fill="{v["color"]}"/>'
        o += M(1166, y, 15, f"{100 * v['size'] / tot:.1f}%", MUTED, "end")
    return svg(W, H + oy + 6, o, CSS, f"Contribution streak - current {cur} days, best {best} days - and top languages")


def placeholder(name, h):
    o = frame(0, 14, 1200, h, 20, "SIGNAL LOST")
    o += T(600, 14 + h / 2 - 4, 30, "Telemetry link dropped", "display", TEXT, "middle")
    o += M(600, 14 + h / 2 + 30, 15, f"{name} · re-syncing next orbit", GOLD, "middle", 2)
    return svg(1200, h + 20, o, title="Telemetry unavailable")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--user", default=os.environ.get("GITHUB_REPOSITORY_OWNER", "nimna29"))
    ap.add_argument("--out", default="dist")
    ap.add_argument("--mock", action="store_true")
    a = ap.parse_args()
    try:
        data = mock() if a.mock else fetch(os.environ["GH_TOKEN"], a.user)
    except Exception as e:  # keep the README intact even if the API hiccups
        print(f"::warning::deck telemetry fetch failed: {e}")
        data = None
    for fname, fn, h in (("deck-stats.svg", stats_card, 250), ("deck-activity.svg", activity_card, 240)):
        write(os.path.join(os.path.abspath(a.out), fname), fn(data) if data else placeholder(fname[5:-4], h))


if __name__ == "__main__":
    main()
