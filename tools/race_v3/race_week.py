#!/usr/bin/env python3
"""THE RACE weekly pipeline v3: one command, six critical progress points.

    collect  -> compute -> check -> (approval) -> publish -> verify

Each subcommand reads and writes plain directories so the same code runs in
GitHub Actions, locally, or when ChatGPT/Claude drive it through the API
(see docs/race-v3-api.md). Standard library only; the optional Sheet export
imports google-auth lazily.

Subcommands
  pilot        check that the TA/TE source pages are reachable from this runner
  collect      gather this week's players.json + matches.json into a directory
  compute      derive hebdo/joueurs for the new week and write a six-file release
  check        run the release checks (also run by compute)
  stage        copy a checked release into <season>/data
  verify-live  compare the live site with the release manifest
  export-sheet write the release tables to the Google Sheet (output only)

Progress: every critical point is emitted as a JSON line (PROGRESS_FILE), a
GitHub annotation (visible live through the public Actions API) and a line in
the job summary.
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import gzip
import hashlib
import json
import os
import pathlib
import shutil
import sys
import time
import urllib.error
import urllib.request

DATA_FILES = ["hebdo", "joueurs", "players", "matches", "calendar", "team_colors"]
# Byte format of each released file (json.dumps(indent=0, ensure_ascii=...) + "\n").
ENSURE_ASCII = {"hebdo": True, "joueurs": True, "players": False, "matches": False}
DUEL_POINTS = 5
TEAMS_EXPECTED = 5
ACTIVE_PER_TEAM = 6
SITE = "https://peozenou.github.io/race/"
UA = "THE-RACE-pipeline/3 (+https://github.com/peozenou/race)"


class CheckFailure(Exception):
    """A release check failed; the run must stop before approval."""


# ---------------------------------------------------------------- progress
def progress(point: str, status: str, detail: str = "", **data) -> None:
    """Record one critical progress point (start/ok/warn/fail)."""
    event = {"at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
             "point": point, "status": status, "detail": detail, **data}
    path = os.environ.get("PROGRESS_FILE")
    if path:
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(event, ensure_ascii=False) + "\n")
    if os.environ.get("GITHUB_ACTIONS"):
        level = {"fail": "error", "warn": "warning"}.get(status, "notice")
        msg = detail.replace("%", "%25").replace("\n", "%0A")
        print(f"::{level} title={point} · {status}::{msg}")
        summary = os.environ.get("GITHUB_STEP_SUMMARY")
        if summary:
            icon = {"ok": "✅", "fail": "❌", "warn": "⚠️"}.get(status, "▶️")
            with open(summary, "a", encoding="utf-8") as fh:
                fh.write(f"- {icon} **{point}** — {detail}\n")
    else:
        print(f"[{point}] {status}: {detail}", file=sys.stderr)


# ---------------------------------------------------------------- io helpers
def load(path: pathlib.Path):
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: pathlib.Path, name: str, rows) -> None:
    path.write_text(json.dumps(rows, indent=0, ensure_ascii=ENSURE_ASCII[name]) + "\n", encoding="utf-8")


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_release(d: pathlib.Path) -> dict:
    return {n: load(d / f"{n}.json") for n in DATA_FILES if (d / f"{n}.json").exists()}


def load_baseline(src: pathlib.Path) -> dict:
    """Previous release: a data directory or a gzipped fixture bundle."""
    if src.is_file():
        with gzip.open(src, "rt", encoding="utf-8") as fh:
            return json.load(fh)
    rel = load_release(src)
    rel["match_ids"] = [m["mid"] for m in rel.pop("matches")]
    return rel


def fetch(url: str, timeout: int = 30) -> tuple[int, bytes]:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Cache-Control": "no-cache"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read() or b""
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        return 0, str(e).encode()


def competition_monday(today: dt.date | None = None) -> dt.date:
    today = today or dt.datetime.now(dt.timezone(dt.timedelta(hours=-5))).date()
    return today - dt.timedelta(days=today.weekday())


# ---------------------------------------------------------------- compute
def key(row) -> tuple:
    return (row["team"], row["player"])


def duel_points(matches, cutoff: str) -> collections.Counter:
    """5 points per win (walkovers included) over a player of another team, before the cutoff."""
    pts = collections.Counter()
    for m in matches:
        if m["opponent_team"] and m["result"] == "V" and m["event_date"] < cutoff:
            pts[(m["team"], m["player"])] += DUEL_POINTS
    return pts


def compute(base: dict, players: list, matches: list, monday: str) -> tuple[list, list, dict]:
    """Append the new week's JOUEURS and HEBDO rows.

    Credited Race moves by each player's change in TE Race points since the
    previous release, so approved transfer baselines and adjustments carry over
    unchanged. A player absent from the previous release is a roster change and
    needs an explicit decision (not part of a routine week).
    """
    hebdo, joueurs = base["hebdo"], base["joueurs"]
    prev_week = max(r["week"] for r in hebdo)
    prev_date = next(r["date"] for r in hebdo if r["week"] == prev_week)
    if monday <= prev_date:
        raise CheckFailure(f"Monday {monday} is not after the last released week ({prev_date}).")
    week = prev_week + 1
    prev_pts = {key(p): p["race_points"] for p in base["players"]}
    prev_rows = [r for r in joueurs if r["week"] == prev_week]
    credited = {key(r): r["race"] for r in prev_rows}
    now = {key(p): p for p in players}
    new_ids = set(now) - set(credited)
    if new_ids:
        raise CheckFailure(f"Roster change needs a decision: {sorted(p for _, p in new_ids)}")
    missing = set(credited) - set(now)
    if missing:
        raise CheckFailure(f"Players missing from collected data: {sorted(p for _, p in missing)}")
    new_rows = []
    for r in prev_rows:
        k = key(r)
        delta = now[k]["race_points"] - prev_pts[k]
        new_rows.append({"team": r["team"], "player": r["player"], "week": week, "race": r["race"] + delta})
    race = collections.Counter()
    for r in new_rows:
        race[r["team"]] += r["race"]
    duels = collections.Counter()
    for (team, _), v in duel_points(matches, monday).items():
        duels[team] += v
    prev_team_rows = [r for r in hebdo if r["week"] == prev_week]
    new_hebdo = [{"week": week, "date": monday, "team": r["team"], "race": race[r["team"]],
                  "duels": duels[r["team"]], "total": race[r["team"]] + duels[r["team"]]} for r in prev_team_rows]
    info = {"week": week, "monday": monday, "previous_week": prev_week,
            "totals": {r["team"]: r["total"] for r in new_hebdo},
            "weekly_change": {r["team"]: r["total"] - p["total"] for r, p in zip(new_hebdo, prev_team_rows)},
            "new_matches": len([m for m in matches if m["mid"] not in set(base["match_ids"])])}
    return hebdo + new_hebdo, joueurs + new_rows, info


# ---------------------------------------------------------------- checks
def run_checks(base: dict, rel: dict, monday: str) -> list[str]:
    """Return warnings; raise CheckFailure on a blocking problem."""
    errors, warnings = [], []
    hebdo, joueurs, players, matches = rel["hebdo"], rel["joueurs"], rel["players"], rel["matches"]
    week = max(r["week"] for r in hebdo)
    # history is append-only
    if hebdo[:len(base["hebdo"])] != base["hebdo"]:
        errors.append("HEBDO history changed")
    if joueurs[:len(base["joueurs"])] != base["joueurs"]:
        errors.append("JOUEURS history changed")
    old = set(base["match_ids"])
    ids = [m["mid"] for m in matches]
    if len(ids) != len(set(ids)):
        errors.append("duplicate match ids")
    if not old <= set(ids):
        errors.append("previously released matches are missing")
    late = [m["mid"] for m in matches if m["mid"] not in old and m["event_date"] >= monday]
    if late:
        errors.append(f"matches on/after the cutoff {monday}: {late[:5]}")
    # roster
    teams = sorted({p["team"] for p in players})
    if len(teams) != TEAMS_EXPECTED:
        errors.append(f"expected {TEAMS_EXPECTED} teams, found {teams}")
    active = [p for p in players if p["rankings_date"] == max(q["rankings_date"] for q in players)]
    per_team = collections.Counter(p["team"] for p in active)
    if any(v != ACTIVE_PER_TEAM for v in per_team.values()) or len(active) != ACTIVE_PER_TEAM * TEAMS_EXPECTED:
        errors.append(f"active selections per team: {dict(per_team)}")
    if len({p["player"] for p in active}) != len(active):
        errors.append("a player is selected twice")
    # totals
    this = [r for r in hebdo if r["week"] == week]
    jsum = collections.Counter()
    for r in joueurs:
        if r["week"] == week:
            jsum[r["team"]] += r["race"]
    for r in this:
        if r["race"] + r["duels"] != r["total"]:
            errors.append(f"{r['team']}: race + duels != total")
        if jsum[r["team"]] != r["race"]:
            errors.append(f"{r['team']}: JOUEURS sum {jsum[r['team']]} != HEBDO race {r['race']}")
    pdu = collections.Counter()
    for p in players:
        pdu[p["team"]] += p["duel_pts"]
    for r in this:
        if pdu[r["team"]] != r["duels"]:
            errors.append(f"{r['team']}: players duel_pts {pdu[r['team']]} != HEBDO duels {r['duels']}")
    prev = {r["team"]: r for r in hebdo if r["week"] == week - 1}
    for r in this:
        p = prev.get(r["team"])
        if p and r["race"] < p["race"]:
            warnings.append(f"{r['team']}: Race fell by {p['race'] - r['race']} (TE correction?)")
        if p and r["duels"] < p["duels"]:
            errors.append(f"{r['team']}: duels decreased")
    if errors:
        raise CheckFailure("; ".join(errors))
    return warnings


# ---------------------------------------------------------------- commands
def cmd_pilot(a) -> int:
    """Reachability of each source from this runner; no writes, no parsing claims."""
    urls = {
        "TA player page": "https://www.tennisabstract.com/cgi-bin/player.cgi?p=AlexanderZverev",
        "TA Elo report": "https://www.tennisabstract.com/reports/atp_elo_ratings.html",
        "TA yElo report": "https://www.tennisabstract.com/reports/atp_season_yelo_ratings.html",
        "TE Race": "https://www.tennisexplorer.com/ranking/atp-men/?t=race",
        "TE ranking": "https://www.tennisexplorer.com/ranking/atp-men/",
    }
    results = {}
    for name, url in urls.items():
        code, body = fetch(url)
        ok = code == 200 and len(body) > 5000
        results[name] = {"url": url, "status": code, "bytes": len(body), "reachable": ok}
        progress("Pilot", "ok" if ok else "warn", f"{name}: HTTP {code}, {len(body)} bytes")
        time.sleep(2)
    pathlib.Path(a.out).write_text(json.dumps(results, indent=1) + "\n", encoding="utf-8")
    return 0 if all(r["reachable"] for r in results.values()) else 3


def cmd_collect(a) -> int:
    out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
    progress("1 Collecte", "start", f"source={a.source}")
    if a.source.startswith("replay:"):
        src = pathlib.Path(a.source.split(":", 1)[1])
        for n in ("players", "matches"):
            shutil.copyfile(src / f"{n}.json", out / f"{n}.json")
    else:
        # Live adapters: port the reviewed TA displayed Serve/Return capture and the
        # TE Race/ranking parser here (see docs/race-v3-design.md, "Source adapters").
        progress("1 Collecte", "fail", "adaptateurs live TA/TE pas encore branchés : utiliser replay ou lancer le pilote")
        return 2
    p, m = load(out / "players.json"), load(out / "matches.json")
    progress("1 Collecte", "ok", f"{len(p)} fiches joueurs, {len(m)} matchs",
             players=len(p), matches=len(m))
    return 0


def cmd_compute(a) -> int:
    base = load_baseline(pathlib.Path(a.baseline))
    col = pathlib.Path(a.collected)
    players, matches = load(col / "players.json"), load(col / "matches.json")
    monday = a.monday or competition_monday().isoformat()
    progress("2 Calcul", "start", f"semaine suivant la {max(r['week'] for r in base['hebdo'])}e, coupure {monday}")
    try:
        hebdo, joueurs, info = compute(base, players, matches, monday)
    except CheckFailure as e:
        progress("2 Calcul", "fail", str(e)); return 1
    out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
    dump(out / "hebdo.json", "hebdo", hebdo)
    dump(out / "joueurs.json", "joueurs", joueurs)
    shutil.copyfile(col / "players.json", out / "players.json")
    shutil.copyfile(col / "matches.json", out / "matches.json")
    for n in ("calendar", "team_colors"):
        src = pathlib.Path(a.static) / f"{n}.json"
        shutil.copyfile(src, out / f"{n}.json")
    ranking = sorted(info["totals"].items(), key=lambda kv: -kv[1])
    progress("2 Calcul", "ok", f"semaine {info['week']}: " + " · ".join(f"{t} {v:,}" for t, v in ranking),
             **info)
    try:
        warnings = run_checks(base, load_release(out), monday)
    except CheckFailure as e:
        progress("3 Contrôles", "fail", str(e)); return 1
    for w in warnings:
        progress("3 Contrôles", "warn", w)
    manifest = {"week": info["week"], "monday": monday, "cutoff": f"{monday}T00:00:00-05:00",
                "totals": info["totals"], "weekly_change": info["weekly_change"],
                "new_matches": info["new_matches"], "warnings": warnings,
                "rankings_date": max(p["rankings_date"] for p in players),
                "elo_date": max(p["elo_date"] for p in players if p.get("elo_date")),
                "sha256": {n: sha256(out / f"{n}.json") for n in DATA_FILES}}
    (out / "release.json").write_text(json.dumps(manifest, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    progress("3 Contrôles", "ok", f"tous les contrôles passent ({len(warnings)} alerte(s)) ; release prête pour la validation")
    return 0


def cmd_check(a) -> int:
    base = load_baseline(pathlib.Path(a.baseline))
    rel = load_release(pathlib.Path(a.release))
    try:
        for w in run_checks(base, rel, a.monday):
            progress("3 Contrôles", "warn", w)
    except CheckFailure as e:
        progress("3 Contrôles", "fail", str(e)); return 1
    progress("3 Contrôles", "ok", "tous les contrôles passent")
    return 0


def cmd_stage(a) -> int:
    rel = pathlib.Path(a.release)
    manifest = load(rel / "release.json")
    dest = pathlib.Path(a.dest)
    for n in DATA_FILES:
        if sha256(rel / f"{n}.json") != manifest["sha256"][n]:
            progress("4 Publication", "fail", f"{n}.json changed after approval"); return 1
        shutil.copyfile(rel / f"{n}.json", dest / f"{n}.json")
    progress("4 Publication", "start", f"semaine {manifest['week']} installée dans {dest}")
    return 0


def cmd_verify_live(a) -> int:
    manifest = load(pathlib.Path(a.release) / "release.json")
    base = a.site.rstrip("/") + "/"
    deadline = time.time() + a.timeout
    while True:
        got = {n: hashlib.sha256(fetch(f"{base}data/{n}.json?nocache={time.time()}")[1]).hexdigest()
               for n in DATA_FILES}
        bad = [n for n in DATA_FILES if got[n] != manifest["sha256"][n]]
        code, page = fetch(f"{base}?nocache={time.time()}")
        live_week = f"Bilan {manifest['week']}e semaine" in page.decode("utf-8", "replace")
        if not bad and live_week:
            progress("5 Vérification", "ok", f"le site en ligne sert la semaine {manifest['week']} avec les six fichiers approuvés")
            return 0
        if time.time() > deadline:
            progress("5 Vérification", "fail", f"after {a.timeout}s: mismatched {bad or 'none'}, title ok={live_week}")
            return 1
        time.sleep(20)


def cmd_export_sheet(a) -> int:
    """Write the released HEBDO/JOUEURS tables to an EXPORT tab (the Sheet is output only)."""
    creds_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    if not creds_json or not a.spreadsheet:
        progress("6 Export Sheet", "warn", "ignoré : compte de service ou Sheet non configuré")
        return 0
    from google.oauth2 import service_account  # pip install google-auth
    from google.auth.transport.requests import AuthorizedSession
    creds = service_account.Credentials.from_service_account_info(
        json.loads(creds_json), scopes=["https://www.googleapis.com/auth/spreadsheets"])
    s = AuthorizedSession(creds)
    rel = load_release(pathlib.Path(a.release))
    weeks = sorted({r["week"] for r in rel["hebdo"]})
    teams = [r["team"] for r in rel["hebdo"] if r["week"] == weeks[-1]]
    by = {(r["week"], r["team"]): r for r in rel["hebdo"]}
    rows = [["Semaine", "Date"] + [f"{t} {c}" for t in teams for c in ("Race", "Duels", "Total")]]
    for w in weeks:
        first = by[(w, teams[0])]
        rows.append([w, first["date"]] + [by[(w, t)][c] for t in teams for c in ("race", "duels", "total")])
    url = (f"https://sheets.googleapis.com/v4/spreadsheets/{a.spreadsheet}/values/"
           f"{a.tab}!A1?valueInputOption=RAW")
    r = s.put(url, json={"values": rows})
    if r.status_code != 200:
        progress("6 Export Sheet", "fail", f"HTTP {r.status_code}: {r.text[:200]}"); return 1
    progress("6 Export Sheet", "ok", f"{len(rows) - 1} semaines écrites dans {a.tab}")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("pilot"); p.add_argument("--out", default="pilot.json"); p.set_defaults(f=cmd_pilot)
    p = sub.add_parser("collect"); p.add_argument("--source", default="live"); p.add_argument("--out", required=True)
    p.set_defaults(f=cmd_collect)
    p = sub.add_parser("compute")
    p.add_argument("--baseline", required=True, help="previous release directory or .json.gz bundle")
    p.add_argument("--collected", required=True); p.add_argument("--static", required=True,
                                                                  help="directory with calendar/team_colors")
    p.add_argument("--monday", help="competition Monday (YYYY-MM-DD); default: this week")
    p.add_argument("--out", required=True); p.set_defaults(f=cmd_compute)
    p = sub.add_parser("check"); p.add_argument("--baseline", required=True); p.add_argument("--release", required=True)
    p.add_argument("--monday", required=True); p.set_defaults(f=cmd_check)
    p = sub.add_parser("stage"); p.add_argument("--release", required=True); p.add_argument("--dest", required=True)
    p.set_defaults(f=cmd_stage)
    p = sub.add_parser("verify-live"); p.add_argument("--release", required=True)
    p.add_argument("--site", default=SITE + "2026/"); p.add_argument("--timeout", type=int, default=900)
    p.set_defaults(f=cmd_verify_live)
    p = sub.add_parser("export-sheet"); p.add_argument("--release", required=True)
    p.add_argument("--spreadsheet", default=os.environ.get("RACE_SPREADSHEET_ID"))
    p.add_argument("--tab", default="EXPORT"); p.set_defaults(f=cmd_export_sheet)
    a = ap.parse_args(argv)
    return a.f(a)


if __name__ == "__main__":
    sys.exit(main())
