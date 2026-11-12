"""GitHub data for the live telemetry cards - standard library only.

Pulls everything from the GitHub GraphQL API with one token:
  GH_TOKEN  - GITHUB_TOKEN works; a classic PAT with `read:user` + `repo`
              (the METRICS_TOKEN secret) also counts private contributions.
"""
import datetime as dt
import json
import os
import random
import urllib.request

API = "https://api.github.com/graphql"
# Markup and notebooks inflate the language bar without saying much, so they are left out.
EXCLUDE_LANGS = {s.strip() for s in os.environ.get("EXCLUDE_LANGS", "HTML,CSS,Jupyter Notebook").split(",") if s.strip()}
FALLBACK_COLOR = "#8b9bc4"


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

    # the contribution calendar only spans one year per query, so walk the account's lifetime
    now = dt.datetime.now(dt.timezone.utc)
    start = dt.datetime.fromisoformat(user["createdAt"].replace("Z", "+00:00"))
    days, y = {}, start.year
    while y <= now.year:
        f = max(start, dt.datetime(y, 1, 1, tzinfo=dt.timezone.utc))
        t = min(now, dt.datetime(y, 12, 31, 23, 59, 59, tzinfo=dt.timezone.utc))
        cc = gql(token, Q_YEAR, {"login": login, "from": f.isoformat(), "to": t.isoformat()})["user"]["contributionsCollection"]
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
            cur = langs.setdefault(n, {"size": 0, "color": e["node"]["color"] or FALLBACK_COLOR})
            cur["size"] += e["size"]

    return {
        "stars": sum(r["stargazerCount"] for r in repos if not r["isFork"]),
        "repos": user["repositories"]["totalCount"],
        "followers": user["followers"]["totalCount"],
        "prs": user["pullRequests"]["totalCount"],
        "issues": user["issues"]["totalCount"],
        "contributed": user["repositoriesContributedTo"]["totalCount"],
        "days": dict(sorted(days.items())),
        "langs": langs,
        "since": start.year,
    }


def mock() -> dict:
    """Sample data for local previews (`--mock`)."""
    rnd = random.Random(29)
    today = dt.date.today()
    days = {}
    for i in range(900, -1, -1):
        d = today - dt.timedelta(days=i)
        days[d.isoformat()] = 0 if rnd.random() < .35 else rnd.randint(1, 12)
    for i in range(9):
        days[(today - dt.timedelta(days=i)).isoformat()] = rnd.randint(1, 6)
    return {"stars": 48, "repos": 31, "followers": 57, "prs": 64, "issues": 19, "contributed": 12,
            "days": days, "since": 2020,
            "langs": {"Python": {"size": 900, "color": "#3572A5"}, "TypeScript": {"size": 640, "color": "#3178c6"},
                      "JavaScript": {"size": 380, "color": "#f1e05a"}, "C#": {"size": 160, "color": "#178600"},
                      "Dart": {"size": 120, "color": "#00B4AB"}, "Shell": {"size": 50, "color": "#89e051"}}}


def streaks(days: dict):
    """-> total, (current, start, end), (longest, start, end)."""
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
    # current streak: today counts if active, otherwise it runs back from yesterday
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
