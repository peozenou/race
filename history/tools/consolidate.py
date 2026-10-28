"""Consolidate history/data/*.json into one SQLite database plus one CSV per table.

Usage (from the repository root): python3 -I history/tools/consolidate.py

Writes history/race_history.sqlite and history/csv/<table>.csv. Re-running replaces both.
"""
import csv
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "history" / "data"
DB = ROOT / "history" / "race_history.sqlite"
CSV_DIR = ROOT / "history" / "csv"


def load(name):
    return json.loads((DATA / f"{name}.json").read_text(encoding="utf-8"))


def person_key(row):
    """Stable player key: Sackmann ATP id when known, else the 'Last First' label."""
    return f"atp:{row['atp_id']}" if row.get("atp_id") else f"name:{row['player']}"


SCHEMA = """
CREATE TABLE seasons (
  season INTEGER PRIMARY KEY, scoring_system TEXT NOT NULL, status TEXT NOT NULL,
  n_teams INTEGER, final_week INTEGER, final_date TEXT, weeks_recorded INTEGER,
  n_players INTEGER, n_matches INTEGER, champion TEXT,
  coverage_notes TEXT, data_issues TEXT, source_workbooks TEXT);
CREATE TABLE teams (team TEXT PRIMARY KEY, color TEXT);
CREATE TABLE season_teams (season INTEGER, team TEXT, PRIMARY KEY (season, team));
CREATE TABLE final_standings (
  season INTEGER, rank INTEGER, team TEXT, race INTEGER, duels INTEGER, total INTEGER,
  PRIMARY KEY (season, team));
CREATE TABLE people (
  person_key TEXT PRIMARY KEY, atp_id INTEGER, player TEXT, full_name TEXT,
  first_season INTEGER, last_season INTEGER, n_seasons INTEGER, teams TEXT);
CREATE TABLE rosters (
  season INTEGER, team TEXT, source_team TEXT, person_key TEXT, player TEXT, full_name TEXT,
  atp_id INTEGER, start_date TEXT, end_date TEXT, slot TEXT,
  frozen_race INTEGER, frozen_duels INTEGER, entry_offset INTEGER);
CREATE TABLE transfers (
  season INTEGER, team TEXT, player_out TEXT, player_in TEXT, transfer_date TEXT,
  frozen_race_out INTEGER, frozen_duels_out INTEGER, entry_offset_in INTEGER);
CREATE TABLE hebdo (
  season INTEGER, scoring_system TEXT, week INTEGER, date TEXT, team TEXT,
  race INTEGER, duels INTEGER, total INTEGER, rank INTEGER, share REAL,
  corrected INTEGER, race_recorded INTEGER, duels_recorded INTEGER, total_recorded INTEGER);
CREATE TABLE joueurs (
  season INTEGER, scoring_system TEXT, week INTEGER, team TEXT, person_key TEXT, player TEXT,
  atp_id INTEGER, race INTEGER);
CREATE TABLE players (
  season INTEGER, scoring_system TEXT, team TEXT, person_key TEXT, atp_id INTEGER,
  player TEXT, short TEXT, full_name TEXT, league_points INTEGER, slot TEXT,
  w INTEGER, l INTEGER, walkovers INTEGER, main_tour_w INTEGER, main_tour_l INTEGER,
  titles INTEGER, finals INTEGER, title_events TEXT,
  duel_pts INTEGER, duel_w INTEGER, duel_l INTEGER,
  hard_w INTEGER, hard_l INTEGER, clay_w INTEGER, clay_l INTEGER, grass_w INTEGER, grass_l INTEGER,
  tpw REAL, rpw REAL, dr REAL, ace_pct REAL, first_won REAL, second_won REAL,
  best_win_opponent TEXT, best_win_opp_rank INTEGER, best_win_event TEXT,
  atp_rank INTEGER, atp_points INTEGER, race_rank INTEGER, race_points INTEGER,
  elo REAL, elo_rank INTEGER, hard_elo REAL, clay_elo REAL, grass_elo REAL, yelo REAL,
  age REAL, matches_through TEXT, rankings_date TEXT, elo_date TEXT, transfer_date TEXT,
  PRIMARY KEY (season, team, player));
CREATE TABLE matches (
  season INTEGER, mid TEXT PRIMARY KEY, team TEXT, person_key TEXT, player TEXT, short TEXT,
  event_date TEXT, event TEXT, level TEXT, surface TEXT, round TEXT, result TEXT, walkover INTEGER,
  opponent TEXT, opponent_team TEXT, opponent_rank INTEGER, score TEXT);
CREATE TABLE calendar (
  season INTEGER, event TEXT, short TEXT, level TEXT, start_date TEXT, end_date TEXT,
  surface TEXT, city TEXT);
CREATE TABLE corrections (
  status TEXT, season INTEGER, week INTEGER, team TEXT, field TEXT,
  recorded INTEGER, corrected INTEGER, total_recorded INTEGER, total_corrected INTEGER,
  reason TEXT, evidence TEXT);

CREATE UNIQUE INDEX hebdo_key ON hebdo(season, week, team);
CREATE UNIQUE INDEX joueurs_key ON joueurs(season, week, team, player);
CREATE INDEX joueurs_person ON joueurs(person_key);
CREATE INDEX players_person ON players(person_key);
CREATE INDEX matches_person ON matches(person_key);
CREATE INDEX matches_season_team ON matches(season, team);
CREATE INDEX rosters_person ON rosters(person_key);

-- One row per team and season: final position, totals and roster size.
CREATE VIEW v_team_seasons AS
SELECT f.season, s.scoring_system, f.team, f.rank, f.race, f.duels, f.total,
       ROUND(1.0 * f.total / (SELECT SUM(total) FROM final_standings x WHERE x.season = f.season), 4) AS share,
       (SELECT COUNT(*) FROM rosters r WHERE r.season = f.season AND r.team = f.team) AS roster_stints,
       f.team = s.champion AS champion
FROM final_standings f JOIN seasons s USING (season);

-- League honours by team across all completed seasons.
CREATE VIEW v_team_honours AS
SELECT team, COUNT(*) AS seasons_played, SUM(rank = 1) AS titles, SUM(rank = 2) AS runner_up,
       ROUND(AVG(rank), 2) AS avg_rank, ROUND(AVG(share), 4) AS avg_share
FROM v_team_seasons JOIN seasons USING (season) WHERE seasons.status = 'complete'
GROUP BY team;

-- Career of every rostered player across editions.
CREATE VIEW v_player_careers AS
SELECT p.person_key, MAX(p.full_name) AS full_name, COUNT(*) AS seasons,
       GROUP_CONCAT(p.season || ':' || p.team, ', ') AS season_teams,
       SUM(p.w) AS w, SUM(p.l) AS l, SUM(p.titles) AS titles,
       SUM(CASE WHEN p.scoring_system = 'race' THEN p.league_points END) AS race_league_points,
       SUM(CASE WHEN p.scoring_system = 'bareme' THEN p.league_points END) AS bareme_league_points,
       SUM(p.duel_pts) AS duel_pts
FROM players p GROUP BY p.person_key;

-- Head-to-head duels between league teams (one row per duel match, winner's perspective).
CREATE VIEW v_duels AS
SELECT season, event_date, event, round, team AS winner_team, player AS winner,
       opponent_team AS loser_team, opponent AS loser, score
FROM matches WHERE opponent_team <> '' AND result = 'V';
"""


def main():
    seasons, rosters, hebdo, joueurs = load("seasons"), load("rosters"), load("hebdo"), load("joueurs")
    players, matches, calendar = load("players"), load("matches"), load("calendar")
    colors, corr = load("team_colors"), load("corrections")

    keys = {}
    for r in rosters + players:
        keys[(r["season"], r["team"], r["player"])] = person_key(r)

    def pk(r):
        return keys.get((r["season"], r["team"], r["player"])) or person_key(r)

    if DB.exists():
        DB.unlink()
    con = sqlite3.connect(DB)
    con.executescript(SCHEMA)
    ins = lambda t, rows: rows and con.executemany(
        f"INSERT INTO {t} VALUES ({','.join('?' * len(rows[0]))})", rows)

    ins("seasons", [(s["season"], s["scoring_system"], s["status"], len(s["teams"]), s["final_week"], s["final_date"],
                     s["weeks_recorded"], s["players"], s["matches"], s["champion"],
                     "\n".join(s["coverage_notes"]), "\n".join(s["data_issues"]), ", ".join(s["source_workbooks"]))
                    for s in seasons])
    ins("teams", [(c["team"], c["color"]) for c in colors])
    ins("season_teams", [(s["season"], t) for s in seasons for t in s["teams"]])
    ins("final_standings", [(s["season"], f["rank"], f["team"], f["race"], f["duels"], f["total"])
                            for s in seasons for f in s["final_standings"]])
    ins("transfers", [(s["season"], t["team"], t["out"], t["in"], t["date"], t["frozen_race_out"],
                       t["frozen_duels_out"], t["entry_offset_in"]) for s in seasons for t in s["transfers"]])
    ins("rosters", [(r["season"], r["team"], r["source_team"], pk(r), r["player"], r["full"], r["atp_id"], r["start"],
                     r["end"], r["slot"], r["frozen_race"], r["frozen_duels"], r["entry_offset"]) for r in rosters])
    ins("hebdo", [(h["season"], h["scoring_system"], h["week"], h["date"], h["team"], h["race"], h["duels"], h["total"],
                   h["rank"], h["share"], int(h["corrected"]), h["race_recorded"], h["duels_recorded"],
                   h["total_recorded"]) for h in hebdo])
    ins("joueurs", [(j["season"], j["scoring_system"], j["week"], j["team"], pk(j), j["player"], j["atp_id"], j["race"])
                    for j in joueurs])
    pcols = ["w", "l", "walkovers", "main_tour_w", "main_tour_l", "titles", "finals", "title_events", "duel_pts",
             "duel_w", "duel_l", "hard_w", "hard_l", "clay_w", "clay_l", "grass_w", "grass_l", "tpw", "rpw", "dr",
             "ace_pct", "first_won", "second_won", "best_win_opponent", "best_win_opp_rank", "best_win_event",
             "atp_rank", "atp_points", "race_rank", "race_points", "elo", "elo_rank", "hard_elo", "clay_elo",
             "grass_elo", "yelo", "age", "matches_through", "rankings_date", "elo_date", "transfer_date"]
    ins("players", [(p["season"], p["scoring_system"], p["team"], pk(p), p["atp_id"], p["player"], p["short"], p["full"],
                     p["league_points"], p["slot"], *[p.get(c) for c in pcols]) for p in players])
    ins("matches", [(m["season"], m["mid"], m["team"], keys.get((m["season"], m["team"], m["player"])), m["player"],
                     m["short"], m["event_date"], m["event"], m["level"], m["surface"], m["round"], m["result"],
                     int(m["walkover"]), m["opponent"], m["opponent_team"], m["opponent_rank"], m["score"])
                    for m in matches])
    ins("calendar", [(c["season"], c["event"], c["short"], c["level"], c["start"], c["end"], c["surface"], c["city"])
                     for c in calendar])
    ins("corrections", [("applied", c["season"], c["week"], c["team"], c["field"], c["recorded"], c["corrected"],
                         c["total_recorded"], c["total_corrected"], c["reason"], c["evidence"]) for c in corr["applied"]]
        + [("pending", c["season"], c["from_week"], c["team"], "total", None, None, None, None,
            f"{c['issue']} Impact: {c['impact']}", f"delta_total {c['delta_total']}")
           for c in corr["pending_confirmation"]])
    con.execute("""INSERT INTO people
        SELECT person_key, MAX(atp_id), MAX(player), MAX(full_name), MIN(season), MAX(season),
               COUNT(DISTINCT season), GROUP_CONCAT(DISTINCT team) FROM rosters GROUP BY person_key""")
    con.commit()

    CSV_DIR.mkdir(parents=True, exist_ok=True)
    tables = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type IN ('table','view') ORDER BY type, name")]
    for t in tables:
        cur = con.execute(f"SELECT * FROM {t}")
        with open(CSV_DIR / f"{t}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow([d[0] for d in cur.description])
            w.writerows(cur)
    con.execute("VACUUM")
    con.close()
    print(f"wrote {DB.relative_to(ROOT)} and {len(tables)} CSV files")


if __name__ == "__main__":
    main()
