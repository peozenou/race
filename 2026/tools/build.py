#!/usr/bin/env python3
"""Build index.html for the THE RACE 2026 public dashboard.

Inputs (all inside the repository):
  source/dashboard.html  the dashboard page code exported from the Claude dashboard
  data/*.json            the weekly data files (hebdo, joueurs, players, matches,
                         calendar, team_colors)

Output:
  index.html             a stand-alone page that runs the dashboard code with
                         assets/runtime.js and the vendored d3 library.

Usage:  python3 tools/build.py
"""
import hashlib
import html
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE_URL = "https://peozenou.github.io/race/2026/"
DATA_FILES = ["hebdo", "joueurs", "players", "matches", "calendar", "team_colors"]


def data_version() -> str:
    h = hashlib.sha256()
    for name in DATA_FILES:
        h.update((ROOT / "data" / f"{name}.json").read_bytes())
    h.update((ROOT / "source" / "dashboard.html").read_bytes())
    return h.hexdigest()[:12]


def latest_week() -> tuple:
    rows = json.loads((ROOT / "data" / "hebdo.json").read_text(encoding="utf-8"))
    if isinstance(rows, dict):
        rows = rows.get("rows") or rows.get("data") or []
    last = max(rows, key=lambda r: r["week"])
    leader = max((r for r in rows if r["week"] == last["week"]), key=lambda r: r["total"])
    return last["week"], last["date"], leader["team"], leader["total"]


def main() -> None:
    fragment = (ROOT / "source" / "dashboard.html").read_text(encoding="utf-8")
    version = data_version()
    week, date, leader, total = latest_week()
    title = f"THE RACE 2026 — Bilan {week}e semaine"
    mois = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
            "septembre", "octobre", "novembre", "décembre"]
    y, m, d = (int(x) for x in date.split("-"))
    pts = f"{total:,}".replace(",", "\u202f")
    desc = f"Classement après la semaine {week} ({d} {mois[m - 1]} {y}) : {leader} en tête avec {pts} points."
    preview = (ROOT / "preview.png").exists()
    og_image = (
        f'  <meta property="og:image" content="{SITE_URL}preview.png?v={version}">\n'
        '  <meta property="og:image:width" content="1200">\n'
        '  <meta property="og:image:height" content="630">\n'
        if preview else ""
    )
    page = f"""<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noindex, nofollow">
  <meta name="data-version" content="{version}">
  <title>{html.escape(title)}</title>
  <meta name="description" content="{html.escape(desc)}">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{html.escape(title)}">
  <meta property="og:description" content="{html.escape(desc)}">
  <meta property="og:url" content="{SITE_URL}">
{og_image}  <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Ccircle cx='32' cy='32' r='28' fill='%23c8d94a'/%3E%3Cpath d='M10 22c14 6 30 6 44 0M10 42c14-6 30-6 44 0' stroke='%23fff' stroke-width='4' fill='none'/%3E%3C/svg%3E">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,500&display=swap">
  <link rel="stylesheet" href="assets/theme.css?v={version}">
  <script src="assets/d3.min.js"></script>
  <script src="assets/runtime.js?v={version}"></script>
</head>
<body>
<main class="site">
<div id="dash-root">
{fragment}
</div>
<footer class="site-foot"><a href="../" style="color:inherit">← Toutes les saisons</a> · THE RACE 2026 · mis à jour chaque semaine après validation du lundi · données Tennis Abstract et Tennis Explorer.</footer>
</main>
</body>
</html>
"""
    (ROOT / "index.html").write_text(page, encoding="utf-8")
    print(f"index.html written (data version {version}, semaine {week}, {date})")


if __name__ == "__main__":
    main()
