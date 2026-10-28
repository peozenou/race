"""Convert THE RACE 2019-2025 workbooks into the 2026 dashboard data schema.

Usage: python3 -I build_history.py SRC_DIR OUT_DIR

SRC_DIR holds the native .xlsx exports (THE_RACE_YYYY.xlsx, RESULTATS-THE_RACE_YYYY.xlsx),
sackmann/ (atp_matches_YYYY.csv, atp_players.csv, atp_rankings_*.csv) and the 2022 Stata files.
OUT_DIR receives <season>/data/*.json in the 2026 schema plus history/data/*.json (stacked).
"""
import collections
import csv
import datetime as dt
import json
import re
import sys
from pathlib import Path

import openpyxl
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from common import (ROUND, ROUND_ORDER, SACKMANN_LEVEL, SURFACE, TEAM_ALIASES, TEAM_ORDER, Identity,  # noqa: E402
                    event_label, fold, iso, num, write_json)

SRC, OUT = Path(sys.argv[1]), Path(sys.argv[2])
IDS = Identity(SRC / "sackmann" / "atp_players.csv")
COLORS = [{"team": "PAT", "color": "#8e7cc3"}, {"team": "DOC", "color": "#f6b26b"},
          {"team": "CHAN", "color": "#6fa8dc"}, {"team": "CHEF", "color": "#93c47d"},
          {"team": "JULES", "color": "#999999"}]
NOTES = collections.defaultdict(list)       # season -> coverage / data-quality notes
CHECKS = collections.defaultdict(list)      # season -> reconciliation results


def wb(name):
    return openpyxl.load_workbook(SRC / name, data_only=True, read_only=True)


def rows(book, sheet, **kw):
    return list(book[sheet].iter_rows(values_only=True, **kw))


def team(code):
    code = str(code).strip()
    return TEAM_ALIASES.get(code, code.upper())


# --------------------------------------------------------------------------- rosters / ledger
class Roster:
    """Season membership: who was on which team, when, plus frozen credits for transfers."""

    def __init__(self, season):
        self.season, self.stints = season, []

    def add(self, team_code, name, start=None, end=None, slot=None, frozen=None, offset=None, frozen_duels=None,
            source_team=None, note=None):
        rec = IDS.resolve(name)
        lab = Identity.labels(rec, name)
        self.stints.append({
            "season": self.season, "team": team(team_code), "source_team": source_team or team_code,
            "player": lab["player"], "short": lab["short"], "full": lab["full"],
            "atp_id": rec["id"] if rec else None, "dob": rec["dob"] if rec else None,
            "start": start, "end": end, "slot": slot, "frozen_race": frozen, "frozen_duels": frozen_duels,
            "entry_offset": offset, "note": note})

    def team_on(self, atp_id, name_key, date):
        for s in self.stints:
            hit = (atp_id and s["atp_id"] == atp_id) or fold(s["full"]) == name_key or fold(s["player"]) == name_key
            if hit and (s["start"] is None or date >= s["start"]) and (s["end"] is None or date < s["end"]):
                return s
        return None

    def ids(self):
        return {s["atp_id"] for s in self.stints if s["atp_id"]}


# --------------------------------------------------------------------------- matches
def sackmann_matches(season, roster, lo, hi):
    out = []
    with open(SRC / "sackmann" / f"atp_matches_{season}.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            d = iso(r["tourney_date"])
            if not (lo <= d <= hi):
                continue
            for side, opp in (("winner", "loser"), ("loser", "winner")):
                pid = int(r[f"{side}_id"])
                st = roster.team_on(pid, fold(r[f"{side}_name"]), d)
                if not st:
                    continue
                ost = roster.team_on(int(r[f"{opp}_id"]), fold(r[f"{opp}_name"]), d)
                ev, lvl = event_label(r["tourney_name"], SACKMANN_LEVEL.get(r["tourney_level"], "ATP 500/250"))
                if r["tourney_level"] in SACKMANN_LEVEL and r["tourney_level"] not in "AD":
                    lvl = SACKMANN_LEVEL[r["tourney_level"]]
                rd = ROUND.get(r["round"], r["round"])
                score = r["score"].strip()
                out.append({"player": st["player"], "short": st["short"], "team": st["team"], "event_date": d,
                            "event": ev, "level": "Qualifications" if rd.startswith("Q") else lvl,
                            "surface": SURFACE.get(r["surface"].lower(), r["surface"] or None), "round": rd,
                            "result": "V" if side == "winner" else "D", "walkover": "W/O" in score.upper(),
                            "opponent": Identity.labels(IDS.by_id.get(int(r[f"{opp}_id"])), r[f"{opp}_name"])["full"],
                            "opponent_team": ost["team"] if ost and ost["team"] != st["team"] else "",
                            "opponent_rank": num(r[f"{opp}_rank"]), "score": score})
    NOTES[season].append("matches: Jeff Sackmann tennis_atp tour-level file (main draws, Davis Cup, team events); "
                         "Challengers, qualifying and ITF are not included for this season.")
    return out


SEED = re.compile(r"^\((?:\d+|WC|Q|LL|PR|SE|ALT|SR|IR|ITF)\)", re.I)


def ta_side(text):
    s = re.sub(r"\[[A-Z]{3}\]", "", str(text)).strip()
    while SEED.match(s):
        s = SEED.sub("", s).strip()
    return s


def ta_matches(season, book, roster, lo, hi, layout):
    """Per-player Tennis Abstract tabs (2024: DATE/ROUND/.. WINNER/LOSER; 2025: W/L, Date, Tournament ..)."""
    skip = {"BILAN", "JOUEURS", "TEAMS", "HEBDO", "LIVE", "DUELS-->>"}
    out, seen = [], set()
    duel_credit = []
    for sh in book.sheetnames:
        if sh in skip or sh[:1].isdigit() or sh.startswith("DUELS"):
            continue
        tab_team = sh.split("_")[1] if "_" in sh else None
        owner_name = sh.split("_")[0]
        data = rows(book, sh)
        hdr = [str(x or "") for x in data[0]] if data else []
        didx = next((i for i, h in enumerate(hdr) if h.upper().startswith("DUELS20") or h == "D_pts"), None)
        for r in data[1:]:
            if layout == 2025:
                if r[0] not in ("W", "L"):
                    continue
                d, tour, surf, rd_raw, opp_rank, text, score = iso(r[1]), r[2], r[3], r[4], r[6], r[7], r[8]
                won = r[0] == "W"
                left, _, right = str(text).partition(" d. ")
                opp_name = ta_side(right if won else left)
            else:
                if not isinstance(r[0], (dt.date, dt.datetime)):
                    continue
                d, rd_raw, tour, surf, text, score, winner, loser = iso(r[0]), r[1], r[3], r[4], r[5], r[6], r[7], r[8]
                won = fold(winner) == fold(owner_name) or fold(str(winner)).endswith(fold(owner_name))
                opp_name = loser if won else winner
                opp_rank = None
            if d is None or not (lo <= d <= hi):
                continue
            key_owner = fold(owner_name)
            st = None
            for s in roster.stints:
                if fold(s["short"]) == key_owner or fold(s["player"]).startswith(key_owner) or \
                        (owner_name == "Mpetshi Perricard" and "mpetshi" in fold(s["player"])):
                    if tab_team and s["team"] != team(tab_team):
                        continue
                    if (s["start"] is None or d >= s["start"]) and (s["end"] is None or d < s["end"]):
                        st = s
            if st is None:
                continue
            orec = IDS.resolve(opp_name)
            ost = roster.team_on(orec["id"] if orec else None, fold(opp_name), d)
            ev, lvl = event_label(tour)
            rd = ROUND.get(str(rd_raw).strip(), str(rd_raw).strip())
            k = (st["player"], d, ev, rd, fold(opp_name))
            if k in seen:
                continue
            seen.add(k)
            if didx is not None and didx < len(r):
                duel_credit.append((st["team"], st["player"], d, num(r[didx]) or 0))
            score = str(score or "").strip()
            out.append({"player": st["player"], "short": st["short"], "team": st["team"], "event_date": d,
                        "event": ev, "level": "Qualifications" if rd.startswith("Q") else lvl,
                        "surface": SURFACE.get(str(surf).lower(), surf), "round": rd,
                        "result": "V" if won else "D", "walkover": "W/O" in score.upper(),
                        "opponent": Identity.labels(orec, opp_name)["full"],
                        "opponent_team": ost["team"] if ost and ost["team"] != st["team"] else "",
                        "opponent_rank": num(opp_rank), "score": score})
    NOTES[season].append("matches: Tennis Abstract per-player tabs in the season workbook "
                         "(tour, Challenger, qualifying, ITF and team events as displayed by TA).")
    NOTES[season].append("players.duel_pts: league duel credit from each player tab's duel column "
                         "(DUELS2025 / D_pts), summed over the player's stint.")
    return out, duel_credit


def finalize_matches(ms):
    ms.sort(key=lambda m: (m["event_date"], m["event"], ROUND_ORDER.get(m["round"], 99), m["player"]))
    for i, m in enumerate(ms, 1):
        m["mid"] = f"M{i:04d}"
    keys = ["mid", "player", "short", "team", "event_date", "event", "level", "surface", "round", "result",
            "walkover", "opponent", "opponent_team", "opponent_rank", "score"]
    return [{k: m[k] for k in keys} for m in ms]


# --------------------------------------------------------------------------- rankings
def year_end_atp(season):
    """ATP rank/points at the last Sackmann ranking date of the season (Dec)."""
    files = ["atp_rankings_2010s.csv"] if season <= 2019 else ["atp_rankings_20s.csv"]
    best = {}
    for fn in files:
        with open(SRC / "sackmann" / fn, newline="") as f:
            for r in csv.DictReader(f):
                if r["ranking_date"][:4] != str(season):
                    continue
                pid = int(r["player"])
                if pid not in best or r["ranking_date"] > best[pid][0]:
                    best[pid] = (r["ranking_date"], int(r["rank"]), num(r["points"]))
    return best


def te_snapshot(book, sheet):
    """Race + ATP tables of a 2024/2025 dated tab: {folded name: (race_rank, race_pts, atp_rank, atp_pts)}."""
    out = collections.defaultdict(lambda: [None, None, None, None])
    for r in rows(book, sheet, min_row=3):
        if r[3] and num(r[1]) is not None:
            o = out[fold(r[3])]
            o[0], o[1] = num(r[1]), num(r[5])
        if len(r) > 12 and r[10] and num(r[8]) is not None:
            o = out[fold(r[10])]
            o[2], o[3] = num(r[8]), num(r[12])
    return out


# --------------------------------------------------------------------------- players summary
def summarize(season, roster, matches, final_credit, duel_pts, ranks, rankings_date, through, scoring):
    by = collections.defaultdict(list)
    for m in matches:
        by[(m["team"], m["player"])].append(m)
    out = []
    pairs = collections.Counter((s["team"], s["start"]) for s in roster.stints if s["start"])
    for s in roster.stints:
        ms = by.get((s["team"], s["player"]), [])
        W = [m for m in ms if m["result"] == "V"]
        L = [m for m in ms if m["result"] == "D"]
        main = [m for m in ms if m["level"] in ("Grand Chelem", "Masters 1000", "ATP 500/250", "ATP Finals")]
        finals = [m for m in ms if m["round"] == "F" and m["level"] not in ("Compétition par équipes",)]
        titles = [m for m in finals if m["result"] == "V"]
        duels = [m for m in ms if m["opponent_team"]]
        surf = lambda name, res: sum(1 for m in ms if m["surface"] == name and m["result"] == res and not m["walkover"])
        wins_ranked = [m for m in W if m["opponent_rank"] and not m["walkover"]]
        best = min(wins_ranked, key=lambda m: m["opponent_rank"]) if wins_ranked else None
        rk = ranks.get(s["atp_id"]) or ranks.get(fold(s["player"])) or ranks.get(fold(s["full"])) or {}
        label = s["short"]
        if s["start"] and pairs[(s["team"], s["start"])] and any(
                o["end"] == s["start"] and o["team"] == s["team"] for o in roster.stints):
            label = f"{s['short']} (entré)"
        elif s["end"] and any(o["start"] == s["end"] and o["team"] == s["team"] for o in roster.stints):
            label = f"{s['short']} (sorti)"
        age = None
        if s["dob"]:
            b = dt.date(int(s["dob"][:4]), int(s["dob"][4:6]), int(s["dob"][6:8]))
            age = round((dt.date.fromisoformat(through) - b).days / 365.25, 1) if through else None
        out.append({
            "team": s["team"], "player": s["player"], "short": label, "full": s["full"],
            "w": sum(1 for m in W if not m["walkover"]), "l": sum(1 for m in L if not m["walkover"]),
            "walkovers": sum(1 for m in ms if m["walkover"]),
            "main_tour_w": sum(1 for m in main if m["result"] == "V" and not m["walkover"]),
            "main_tour_l": sum(1 for m in main if m["result"] == "D" and not m["walkover"]),
            "titles": len(titles), "finals": len(finals), "title_events": ", ".join(m["event"] for m in titles),
            "duel_pts": duel_pts.get((s["team"], s["player"]),
                                     s["frozen_duels"] if s["end"] and s["frozen_duels"] is not None else None),
            "duel_w": sum(1 for m in duels if m["result"] == "V"), "duel_l": sum(1 for m in duels if m["result"] == "D"),
            "hard_w": surf("Dur", "V"), "hard_l": surf("Dur", "D"), "clay_w": surf("Terre battue", "V"),
            "clay_l": surf("Terre battue", "D"), "grass_w": surf("Gazon", "V"), "grass_l": surf("Gazon", "D"),
            "tpw": None, "rpw": None, "dr": None, "ace_pct": None, "first_won": None, "second_won": None,
            "best_win_opponent": best["opponent"] if best else None,
            "best_win_opp_rank": best["opponent_rank"] if best else None,
            "best_win_event": f"{best['event']}, {best['round']}" if best else None,
            "atp_rank": rk.get("atp_rank"), "atp_points": rk.get("atp_points"),
            "race_rank": rk.get("race_rank") if scoring == "race" else None,
            "race_points": rk.get("race_points") if scoring == "race" else None,
            "elo": None, "elo_rank": None, "hard_elo": None, "clay_elo": None, "grass_elo": None, "yelo": None,
            "age": age, "matches_through": through, "rankings_date": rankings_date, "elo_date": None,
            "transfer_date": s["start"] or s["end"],
        })
    return out


# --------------------------------------------------------------------------- weekly snapshot blocks (2024-25)
def snapshot_blocks(book, sheet, teams):
    """Team blocks (cols O:P) of a dated tab -> {team: ([(name, value), ...], total)}."""
    out, cur = {}, None
    for r in rows(book, sheet, min_col=15, max_col=16):
        name, val = r[0], r[1] if len(r) > 1 else None
        if isinstance(name, str) and name.strip() in teams:
            cur = name.strip()
            out[cur] = ([], None)
        elif cur and name and num(val) is not None:
            out[cur][0].append((name.strip(), num(val)))
        elif cur and name is None and num(val) is not None and out[cur][1] is None:
            out[cur] = (out[cur][0], num(val))
    return out


def credited_joueurs(season, roster, weekly_raw, hebdo_race):
    """weekly_raw: {week: {team: [(stint, value, kind)]}}.

    kind == "slot": value is the workbook's slot value (frozen credit of the replaced player + gains of the
    incoming one), so the incoming player's credit is value - frozen credit of the player he replaced.
    kind == "raw": value is the player's raw TE Race points; incoming credit is raw - entry offset.
    An outgoing player keeps his frozen credit in every week where he is no longer in the source block.
    """
    out, seen = [], collections.defaultdict(set)
    for w in sorted(weekly_raw):
        for tm, entries in weekly_raw[w].items():
            tot, present = 0, set()
            for st, val, kind in entries:
                if val is None:
                    continue
                present.add(id(st))
                seen[id(st)].add(w)
                prev = [o for o in roster.stints if o["team"] == tm and o["end"] and o["end"] == st["start"]]
                if st.get("force_zero"):
                    credit = 0
                elif st["start"] and kind == "slot":
                    credit = val - sum(o["frozen_race"] or 0 for o in prev)
                elif st["start"] and kind == "raw":
                    credit = val - (st["entry_offset"] or 0)
                else:
                    credit = val
                out.append({"team": tm, "player": st["player"], "week": w, "race": credit})
                tot += credit
            for o in roster.stints:
                if o["team"] != tm or not o["end"] or id(o) in present:
                    continue
                gone = (seen[id(o)] and w > max(seen[id(o)])) if kind_of(weekly_raw[w][tm]) == "slot" \
                    else (o["_end_week"] is not None and w >= o["_end_week"])
                if gone:
                    own = own_frozen(roster, o) if kind_of(weekly_raw[w][tm]) == "slot" else (o["frozen_race"] or 0)
                    out.append({"team": tm, "player": o["player"], "week": w, "race": own})
                    tot += own
            ref = hebdo_race.get((w, tm))
            if ref is not None:
                CHECKS[season].append(("joueurs_vs_hebdo", w, tm, tot, ref, tot == ref))
    return out


def own_frozen(roster, o):
    """Slot values carry the predecessor's credit; an outgoing player's own credit is net of it."""
    pred = [p for p in roster.stints if p["team"] == o["team"] and p["end"] and o["start"] and p["end"] == o["start"]]
    return (o["frozen_race"] or 0) - sum(p["frozen_race"] or 0 for p in pred)


def kind_of(entries):
    return entries[0][2] if entries else "slot"


def week_of(date, week_dates):
    """Map a calendar date to the competition week whose date is nearest (within 4 days)."""
    best = min(week_dates.items(), key=lambda kv: abs((dt.date.fromisoformat(kv[1]) - dt.date.fromisoformat(date)).days))
    return best[0] if abs((dt.date.fromisoformat(best[1]) - dt.date.fromisoformat(date)).days) <= 4 else None


def read_hebdo_race(book, teams, first_row=3, stop_week=None):
    hebdo = []
    for r in rows(book, "HEBDO", min_row=first_row):
        if not isinstance(r[1], (int, float)) or r[0] is None:
            continue
        w = int(r[1])
        if stop_week is not None and w > stop_week:
            continue
        if all(num(r[4 + 3 * k]) is None for k in range(len(teams))):
            continue
        for k, t in enumerate(teams):
            race, du, tot = num(r[2 + 3 * k]), num(r[3 + 3 * k]), num(r[4 + 3 * k])
            hebdo.append({"week": w, "date": iso(r[0]), "team": t, "race": race, "duels": du, "total": tot})
    return hebdo


# --------------------------------------------------------------------------- seasons 2024 / 2025
LEDGER = {
    2025: [  # (team, out, in, date, frozen_race_out, frozen_duels_out, entry_offset_in)
        ("PAT", "Juncheng Shang", "Hamad Medjedovic", "2025-04-21", 110, 0, 405),
        ("PAT", "Giovanni Mpetshi Perricard", "Justin Engel", "2025-06-23", 550, 10, 156),
        ("DOC", "Hubert Hurkacz", "Flavio Cobolli", "2025-06-23", 775, 15, 1210),
        ("JULES", "Arthur Cazaux", "Alexei Popyrin", "2025-06-23", 121, 0, 680),
    ],
    2024: [
        ("PAT", "Lorenzo Musetti", "Matteo Arnaldi", "2024-02-26", 150, None, 150),
        ("CHEF", "Matteo Arnaldi", "Lorenzo Musetti", "2024-02-26", 150, None, 150),
        ("CHEF", "Lorenzo Musetti", "Joao Fonseca", "2024-06-10", 700, None, 269),
        ("CHAN", "Frances Tiafoe", "Tommy Paul", "2024-06-10", 620, None, 1525),
        ("PAT", "Francisco Cerundolo", "Giovanni Mpetshi Perricard", "2024-06-10", 900, None, 630),
    ],
    2023: [
        ("PAT", "Taylor Fritz", "Ben Shelton", "2023-01-30", 395, 5, 540),
        ("DOC", "Ben Shelton", "Taylor Fritz", "2023-01-30", 540, 0, 395),
        ("CHEF", "Jenson Brooksby", "Arthur Fils", "2023-04-17", 0, 0, 354),
    ],
}


def apply_ledger(roster, season, initial):
    """initial: {team: [names]} at season start; LEDGER adds dated in/out stints."""
    events = LEDGER.get(season, [])
    spans = collections.defaultdict(list)  # (team, folded name) -> [start, end, frozen, frozen_duels, offset]
    for tm, names in initial.items():
        for n in names:
            spans[(tm, fold(Identity.labels(IDS.resolve(n), n)["full"]))].append([None, None, None, None, None, n])
    for tm, out_n, in_n, d, fr, frd, off in events:
        ko = (tm, fold(Identity.labels(IDS.resolve(out_n), out_n)["full"]))
        open_spans = [s for s in spans[ko] if s[1] is None]
        if open_spans:
            open_spans[-1][1], open_spans[-1][2], open_spans[-1][3] = d, fr, frd
        else:
            spans[ko].append([None, d, fr, frd, None, out_n])
        ki = (tm, fold(Identity.labels(IDS.resolve(in_n), in_n)["full"]))
        spans[ki].append([d, None, None, None, off, in_n])
    for (tm, _), lst in spans.items():
        for start, end, fr, frd, off, name in lst:
            roster.add(tm, name, start=start, end=end, frozen=fr, frozen_duels=frd, offset=off)


def season_blocks(season, fname, layout, teams, week_tabs_skip=(), last_valid_week=None):
    book = wb(fname)
    tabs = sorted([s for s in book.sheetnames if re.match(r"^\d{8}w\d+$", s)], key=lambda s: int(s.split("w")[1]))
    tabs = [t for t in tabs if t not in week_tabs_skip and (last_valid_week is None or int(t.split("w")[1]) <= last_valid_week)]
    first = snapshot_blocks(book, tabs[1] if tabs[0].endswith("w0") else tabs[0], teams)
    hebdo = read_hebdo_race(book, teams)
    if last_valid_week is not None:
        dropped = [h for h in hebdo if h["week"] > last_valid_week]
        if dropped:
            NOTES[season].append(f"hebdo: week(s) {sorted({h['week'] for h in dropped})} dropped (see data issues).")
        hebdo = [h for h in hebdo if h["week"] <= last_valid_week]
    week_dates = {h["week"]: h["date"] for h in hebdo}
    roster = Roster(season)
    # initial roster = earliest block, but undo ledger entries that already happened
    initial = {t: [n for n, _ in first[t][0]] for t in teams}
    for tm, out_n, in_n, d, *_ in LEDGER.get(season, []):
        names = [fold(Identity.labels(IDS.resolve(x), x)["full"]) for x in initial[tm]]
        if d <= week_dates.get(1, "9999") and fold(Identity.labels(IDS.resolve(in_n), in_n)["full"]) in names:
            pass
    apply_ledger(roster, season, initial)
    for s in roster.stints:
        s["_end_week"] = week_of(s["end"], week_dates) if s["end"] else None
    hebdo_race = {(h["week"], h["team"]): h["race"] for h in hebdo}
    weekly = {}
    for t in tabs:
        w = int(t.split("w")[1])
        if w == 0:
            continue
        date = week_dates.get(w)
        blocks = snapshot_blocks(book, t, teams)
        weekly[w] = {}
        for tm in teams:
            entries = []
            for name, val in blocks.get(tm, ([], None))[0]:
                rec = IDS.resolve(name)
                st = roster.team_on(rec["id"] if rec else None, fold(Identity.labels(rec, name)["full"]), date)
                if st is None or st["team"] != tm:
                    st = next((s for s in roster.stints if s["team"] == tm and fold(s["full"]) == fold(Identity.labels(rec, name)["full"])), None)
                if st is None:
                    NOTES[season].append(f"joueurs: unmapped block name {name!r} ({tm}, w{w})")
                    continue
                entries.append((st, val, "slot"))
            weekly[w][tm] = entries
            blk_total = blocks.get(tm, ([], None))[1]
            if blk_total is not None and hebdo_race.get((w, tm)) is not None:
                CHECKS[season].append(("block_total_vs_hebdo", w, tm, blk_total, hebdo_race[(w, tm)],
                                       blk_total == hebdo_race[(w, tm)]))
    joueurs = credited_joueurs(season, roster, weekly, hebdo_race)
    final_w = max(weekly)
    ranks_raw = te_snapshot(book, tabs[-1])
    ranks = {}
    for k, (rr, rp, ar, ap) in ranks_raw.items():
        rec = IDS.resolve(k)
        ranks[rec["id"] if rec else k] = {"race_rank": rr, "race_points": rp, "atp_rank": ar, "atp_points": ap}
    lo, hi = f"{season - 1}-12-24", f"{season}-12-31"
    raw_matches, credits = ta_matches(season, book, roster, lo, hi, layout)
    if layout == 2024:  # TA tabs carry no opponent rank: use the ATP table of that week's dated tab
        by_date = []
        for t in tabs:
            tab_date = iso(t[:8])
            ranks_t = {}
            for k, (_, _, ar, _) in te_snapshot(book, t).items():
                if ar is not None:
                    ranks_t[k] = ar
                    ranks_t[" ".join(k.split()[1:] + k.split()[:1])] = ar
            by_date.append((tab_date, ranks_t))
        filled = 0
        for m in raw_matches:
            if m["opponent_rank"] is None:
                prior = [r for d, r in by_date if d <= m["event_date"]] or [by_date[0][1]]
                key = fold(m["opponent"])
                rk = prior[-1].get(key)
                if rk is None:  # "first last" vs "last first" with compound surnames
                    toks = key.split()
                    rk = next((v for k2, v in prior[-1].items() if set(k2.split()) == set(toks)), None)
                if rk is not None:
                    m["opponent_rank"], filled = rk, filled + 1
        NOTES[season].append(f"matches.opponent_rank: filled for {filled} of {len(raw_matches)} matches from the ATP "
                             "table of the latest dated tab on or before the event date (TA tabs carry no ranks).")
    matches = finalize_matches(raw_matches)
    cut = week_dates[final_w]
    duel_pts = collections.Counter()
    for tm, pl, d, v in credits:
        if d < cut:
            duel_pts[(tm, pl)] += v
    NOTES[season].append(f"players.duel_pts: counts events starting before the final HEBDO week ({cut}), "
                         "matching the HEBDO duel total.")
    return book, roster, hebdo, joueurs, matches, duel_pts, ranks, week_dates[final_w], final_w


# --------------------------------------------------------------------------- 2023 (TE raw tabs)
def season_2023():
    season, teams = 2023, ["PAT", "DOC", "CHAN", "CHEF"]
    book = wb("THE_RACE_2023.xlsx")
    hebdo = read_hebdo_race(book, teams)
    week_dates = {h["week"]: h["date"] for h in hebdo}
    initial = {
        "PAT": ["Dominic Thiem", "Denis Shapovalov", "Taylor Fritz", "Casper Ruud", "Lorenzo Musetti", "Brandon Nakashima"],
        "DOC": ["Stefanos Tsitsipas", "Alexander Zverev", "Ben Shelton", "Hubert Hurkacz", "Diego Schwartzman", "Cameron Norrie"],
        "CHAN": ["Daniil Medvedev", "Holger Rune", "Carlos Alcaraz", "Juncheng Shang", "Sebastian Korda", "Frances Tiafoe"],
        "CHEF": ["Felix Auger Aliassime", "Jenson Brooksby", "Andrey Rublev", "Jack Draper", "Jannik Sinner", "Matteo Berrettini"],
    }
    roster = Roster(season)
    apply_ledger(roster, season, initial)
    for s in roster.stints:
        s["_end_week"] = week_of(s["end"], week_dates) if s["end"] else None
        if s["player"].startswith("Brooksby"):
            s["force_zero"] = True  # league credited the Brooksby slot 0 until Fils replaced him
    NOTES[season].append("joueurs: Jenson Brooksby's CHEF slot is credited 0 (HEBDO never counts his Race points); "
                         "Fils is credited from post-Monte-Carlo with a 354-point entry offset.")
    hebdo_race = {(h["week"], h["team"]): h["race"] for h in hebdo}
    weekly = {}
    tabs = sorted(s for s in book.sheetnames if re.match(r"^\d{8}$", s))
    for t in tabs:
        date = iso(t)
        w = week_of(date, week_dates)
        if w is None:
            NOTES[season].append(f"joueurs: TE tab {t} matches no HEBDO week")
            continue
        raw = {}
        for r in rows(book, t, min_row=6):
            if len(r) > 6 and r[3] and num(r[6]) is not None:
                rec = IDS.resolve(r[3])
                if rec:
                    raw[rec["id"]] = num(r[6])
        weekly[w] = {}
        for tm in teams:
            entries = []
            for s in roster.stints:
                if s["team"] != tm:
                    continue
                active = (s["start"] is None or week_dates[w] >= s["start"]) and (s["end"] is None or week_dates[w] < s["end"])
                if active:
                    entries.append((s, raw.get(s["atp_id"], 0), "raw"))
            weekly[w][tm] = entries
    joueurs = credited_joueurs(season, roster, weekly, hebdo_race)
    NOTES[season].append("joueurs: rebuilt from the dated Tennis Explorer Race tabs (raw points, minus entry offsets "
                         "for 2023 transfers); weeks without a dated tab have no player rows. Players absent from a "
                         "TE table are counted as 0 Race points.")
    matches = finalize_matches(sackmann_matches(season, roster, "2022-12-26", "2023-12-31"))
    duel_pts = {}
    blk = rows(book, "BILAN", min_row=22, max_row=27, max_col=9)
    for r in blk:
        for k, tm in enumerate(teams):
            name, pts = r[1 + 2 * k], r[2 + 2 * k]
            rec = IDS.resolve(name)
            lab = Identity.labels(rec, name)
            duel_pts[(tm, lab["player"])] = num(pts)
    last_tab = tabs[-1]
    ranks = {}
    for r in rows(book, last_tab, min_row=6):
        if len(r) > 6 and r[3] and num(r[1]) is not None:
            rec = IDS.resolve(r[3])
            if rec:
                ranks[rec["id"]] = {"race_rank": num(r[1]), "race_points": num(r[6])}
    ye = year_end_atp(season)
    for pid, (d, rk, pts) in ye.items():
        ranks.setdefault(pid, {}).update({"atp_rank": rk, "atp_points": pts})
    final_w = max(h["week"] for h in hebdo)
    return book, roster, hebdo, joueurs, matches, duel_pts, ranks, week_dates[final_w], final_w, iso(last_tab)


# --------------------------------------------------------------------------- 2022 (final standings only)
def season_2022():
    season, teams = 2022, ["PAT", "DOC", "CHAN", "CHEF"]
    book = wb("THE_RACE_2022.xlsx")
    r = rows(book, "BILAN ATP", max_row=11, max_col=16)
    roster = Roster(season)
    finals = {}
    for k, tm in enumerate(teams):
        c = 8 + 2 * k
        for i in range(1, 7):
            roster.add(tm, r[i][c])
        finals[tm] = {"race": num(r[7][c + 1]), "duels": num(r[8][c + 1]), "total": num(r[10][c + 1])}
    for s in roster.stints:
        s["_end_week"] = None
    player_race = {}
    for k, tm in enumerate(teams):
        c = 8 + 2 * k
        for i in range(1, 7):
            lab = Identity.labels(IDS.resolve(r[i][c]), r[i][c])
            player_race[(tm, lab["player"])] = num(r[i][c + 1])
    hebdo = [{"week": None, "date": None, "team": t, **finals[t]} for t in teams]
    joueurs = [{"team": tm, "player": p, "week": None, "race": v} for (tm, p), v in player_race.items()]
    for t in teams:
        s = sum(v for (tm, _), v in player_race.items() if tm == t)
        CHECKS[season].append(("players_vs_team_race", None, t, s, finals[t]["race"], s == finals[t]["race"]))
    matches = finalize_matches(sackmann_matches(season, roster, "2021-12-27", "2022-12-31"))
    duel_pts = collections.Counter()
    for m in matches:
        if m["opponent_team"] and m["result"] == "V":
            duel_pts[(m["team"], m["player"])] += 5
    for t in teams:
        s = sum(v for (tm, _), v in duel_pts.items() if tm == t)
        CHECKS[season].append(("computed_duels_vs_bilan", None, t, s, finals[t]["duels"], s == finals[t]["duels"]))
    ranks = {pid: {"atp_rank": rk, "atp_points": pts} for pid, (d, rk, pts) in year_end_atp(season).items()}
    for (tm, p), v in player_race.items():
        st = next(s for s in roster.stints if s["team"] == tm and s["player"] == p)
        ranks.setdefault(st["atp_id"], {})["race_points"] = v
    NOTES[season].append("hebdo/joueurs: only the end-of-season standings survive (THE RACE 2022 › BILAN ATP); "
                         "no weekly history was kept, so week and date are null.")
    NOTES[season].append("players.duel_pts: null — only team duel totals survive (BILAN ATP). duel_w/duel_l count "
                         "duel matches in the Sackmann file, which finds more duels than the league scored (see checks).")
    return book, roster, hebdo, joueurs, matches, {}, ranks, None, None, "2022-12-26"


# --------------------------------------------------------------------------- 2019-2021 (barème)
BAREME_DATES = {2019: ("THE_RACE_2019.xlsx", "PARTICIPATIONS"), 2020: ("THE_RACE_2020.xlsx", "PARTICIPATIONS"),
                2021: ("THE_RACE_2021.xlsx", "Participation")}


def season_bareme(season):
    fname, part = BAREME_DATES[season]
    book = wb(fname)
    hdr = rows(book, part, max_row=2)
    dates = [iso(v) for v in hdr[1][1:] if iso(v)]
    week_dates = {i + 1: d for i, d in enumerate(dates)}
    # HEBDO: col0 week, then (hebdo, cumul) per team
    H = rows(book, "HEBDO")
    teams = [team(str(H[1][c]).strip()) for c in range(2, len(H[1]), 2) if H[1][c]]
    hebdo = []
    for r in H[2:]:
        if not isinstance(r[0], (int, float)):
            continue
        w = int(r[0])
        vals = [num(r[2 + 2 * k]) for k in range(len(teams))]
        if all(v is None for v in vals) or (all(v == 0 for v in vals) and w > 1):
            continue
        for k, t in enumerate(teams):
            hebdo.append({"week": w, "date": week_dates.get(w), "team": t, "race": None, "duels": None, "total": vals[k]})
    # SCORES: right-hand per-team tables "TEAM X"
    S = rows(book, "SCORES")
    roster, player_pts, duel_pts, team_final = Roster(season), {}, {}, {}
    tags = {}
    for r in S[:9]:
        for c in range(1, 13, 3):
            if c < len(r) and r[c] and isinstance(r[c], str) and not r[c].startswith("TEAM"):
                tag = r[c + 1] if c + 1 < len(r) else None
                if tag:
                    tags[fold(r[c])] = tag
    for i, r in enumerate(S):
        for c, v in enumerate(r):
            if isinstance(v, str) and v.startswith("TEAM ") and c + 1 < len(r) and r[c + 1] == "ATP 250":
                tm = team(v.replace("TEAM ", "").strip())
                for j in range(1, 7):
                    pr = S[i + j]
                    name = pr[c]
                    roster.add(tm, name, slot=tags.get(fold(name)), source_team=v.replace("TEAM ", "").strip())
                    lab = roster.stints[-1]
                    tot, du = num(pr[c + 6]), num(pr[c + 5])
                    player_pts[(tm, lab["player"])] = (tot or 0) - (du or 0)
                    duel_pts[(tm, lab["player"])] = du
                team_final[tm] = {"duels": num(S[i + 7][c + 6]), "total": num(S[i + 8][c + 6])}
                dsum = sum(duel_pts[(tm, x["player"])] or 0 for x in roster.stints if x["team"] == tm)
                CHECKS[season].append(("player_duels_vs_team_duels", None, tm, dsum, team_final[tm]["duels"],
                                       dsum == team_final[tm]["duels"]))
    for s in roster.stints:
        s["_end_week"] = None
    final_w = max(h["week"] for h in hebdo)
    for t in teams:
        tf = team_final[t]
        tf["race"] = (tf["total"] or 0) - (tf["duels"] or 0)
        h = next(x for x in hebdo if x["week"] == final_w and x["team"] == t)
        CHECKS[season].append(("hebdo_final_vs_scores_total", final_w, t, h["total"], tf["total"], h["total"] == tf["total"]))
        if h["total"] == tf["total"]:
            h["race"], h["duels"] = tf["race"], tf["duels"]
    joueurs = [{"team": tm, "player": p, "week": final_w, "race": v} for (tm, p), v in player_pts.items()]
    lo, hi = f"{season - 1}-12-28", f"{season}-12-31"
    matches = finalize_matches(sackmann_matches(season, roster, lo, hi))
    ranks = {pid: {"atp_rank": rk, "atp_points": pts} for pid, (d, rk, pts) in year_end_atp(season).items()}
    NOTES[season].append("scoring: round-reached barème (BAREME tab) plus 5 points per duel; 'race' fields hold "
                         "barème points, not ATP Race points.")
    NOTES[season].append("hebdo: weekly cumulative team totals; the race/duels split is only known for the final "
                         "week (from SCORES) and only where SCORES matches HEBDO.")
    NOTES[season].append("joueurs: final-week barème points per player (SCORES, total minus duel points); "
                         "weekly per-player history was not kept.")
    return book, roster, hebdo, joueurs, matches, duel_pts, ranks, week_dates.get(final_w), final_w, f"{season}-12-30", teams, tags


# --------------------------------------------------------------------------- calendar
def calendar_from(matches, season):
    ev = {}
    city = {"Open d'Australie": "Melbourne", "Roland-Garros": "Paris", "Wimbledon": "Londres", "US Open": "New York",
            "Masters d'Indian Wells": "Indian Wells", "Masters de Miami": "Miami", "Masters de Monte-Carlo": "Monte-Carlo",
            "Masters de Madrid": "Madrid", "Masters de Rome": "Rome", "Masters du Canada": "Montréal/Toronto",
            "Masters de Cincinnati": "Cincinnati", "Masters de Shanghai": "Shanghai", "Masters de Paris": "Paris",
            "ATP Finals": "Londres" if season <= 2020 else "Turin"}
    short = {"Open d'Australie": ("Open d'Australie", "AO"), "Roland-Garros": ("Roland-Garros", "RG"),
             "Wimbledon": ("Wimbledon", "WIM"), "US Open": ("US Open", "USO"),
             "Masters d'Indian Wells": ("Indian Wells", "IW"), "Masters de Miami": ("Miami", "MIA"),
             "Masters de Monte-Carlo": ("Monte-Carlo", "MC"), "Masters de Madrid": ("Madrid", "MAD"),
             "Masters de Rome": ("Rome", "ROM"), "Masters du Canada": ("Canada", "CAN"),
             "Masters de Cincinnati": ("Cincinnati", "CIN"), "Masters de Shanghai": ("Shanghai", "SHA"),
             "Masters de Paris": ("Paris", "PAR"), "ATP Finals": ("ATP Finals", "FIN")}
    for m in matches:
        if m["event"] in short and m["level"] != "Qualifications":
            e = ev.setdefault(m["event"], {"start": m["event_date"], "surface": m["surface"], "level": m["level"]})
            e["start"] = min(e["start"], m["event_date"])
    out = []
    for name, e in sorted(ev.items(), key=lambda kv: kv[1]["start"]):
        lab, sh = short[name]
        start = dt.date.fromisoformat(e["start"])
        days = 14 if e["level"] == "Grand Chelem" else 11 if name in ("Masters d'Indian Wells", "Masters de Miami",
                                                                        "Masters de Madrid", "Masters de Rome",
                                                                        "Masters de Shanghai") else 7
        out.append({"event": lab, "short": sh, "level": e["level"], "start": e["start"],
                    "end": (start + dt.timedelta(days=days)).isoformat(), "surface": e["surface"], "city": city[name]})
    return out


# --------------------------------------------------------------------------- corrections
CORRECTIONS = []          # every change made to a recorded HEBDO value
PENDING = []              # corrections computed but not applied (need the league's agreement)


def set_hebdo(season, hebdo, week, tm, field, value, reason, evidence):
    h = next((x for x in hebdo if x["week"] == week and x["team"] == tm), None)
    if h is None or h[field] == value:
        return
    h.setdefault("_recorded", {k: h[k] for k in ("race", "duels", "total")})
    old = h[field]
    h[field] = value
    if field != "total" and h["race"] is not None and h["duels"] is not None:
        h["total"] = h["race"] + h["duels"]
    CORRECTIONS.append({"season": season, "week": week, "team": tm, "field": field, "recorded": old,
                        "corrected": value, "total_recorded": h["_recorded"]["total"], "total_corrected": h["total"],
                        "reason": reason, "evidence": evidence})


def rule_duels(matches, cut):
    """League rule: +5 for a win over a player rostered by another team at match date (tournament start < cut)."""
    c = collections.Counter()
    for m in matches:
        if m["opponent_team"] and m["result"] == "V" and m["event_date"] < cut:
            c[m["team"]] += 5
    return c


def finals_week_2025(book, roster, joueurs, hebdo, teams):
    """Rebuild week 35 (17 Nov 2025) = week 34 credited points + ATP Finals points (tab 20251117w35, col R 'TURIN')."""
    fin = {}
    cur = None
    for r in rows(book, "20251117w35", min_col=15, max_col=17):
        name = r[0]
        if isinstance(name, str) and name.strip() in teams:
            cur = name.strip()
        elif cur and name and len(r) > 2 and num(r[2]) is not None:
            rec = IDS.resolve(name)
            fin[(cur, Identity.labels(rec, name)["player"])] = num(r[2])
    NOTES[2025].append("Week 35 Finals points used: " + ", ".join(f"{p} {v}" for (_, p), v in sorted(fin.items()) if v))
    w34 = [j for j in joueurs if j["week"] == 34]
    for j in w34:
        joueurs.append({"team": j["team"], "player": j["player"], "week": 35,
                        "race": j["race"] + fin.get((j["team"], j["player"]), 0)})
    for tm in teams:
        prev = next(h for h in hebdo if h["week"] == 34 and h["team"] == tm)
        race = prev["race"] + sum(v for (t, _), v in fin.items() if t == tm)
        hebdo.append({"week": 35, "date": "2025-11-17", "team": tm, "race": race, "duels": None, "total": None,
                      "_recorded": {"race": None, "duels": None, "total": None}})
        CORRECTIONS.append({"season": 2025, "week": 35, "team": tm, "field": "race", "recorded": None, "corrected": race,
                            "total_recorded": None, "total_corrected": None,
                            "reason": "Week 35 rebuilt: the workbook tab carried the 2024 Race table. Value = week-34 "
                                      "credited Race + ATP Finals points of the team's players.",
                            "evidence": "tab 20251117w35 column Q (TURIN); Finals results in the player tabs"})
    return fin


def apply_corrections(season, hebdo, joueurs, matches, book, roster, teams):
    ok = lambda c: c[-1]
    if season in (2024, 2025):  # HEBDO cell errors: use the week's own team block total
        for chk, w, tm, val, ref, good in list(CHECKS[season]):
            if chk == "block_total_vs_hebdo" and not good:
                set_hebdo(season, hebdo, w, tm, "race", val,
                          "HEBDO cell does not match the week's team block (wrong cell reference or typed value).",
                          f"team block total in that week's dated tab = {val}")
    if season == 2025:
        finals_week_2025(book, roster, joueurs, hebdo, teams)
        for h in hebdo:  # duels rebuilt from the per-match rule, cumulative by week
            if h["week"] == 0:
                continue
            d = rule_duels(matches, h["date"])[h["team"]]
            if h["week"] == 35:
                h["duels"] = d
                h["total"] = h["race"] + d
                next(c for c in CORRECTIONS if c["season"] == 2025 and c["week"] == 35 and c["team"] == h["team"]
                     ).update({"total_corrected": h["total"]})
            else:
                set_hebdo(season, hebdo, h["week"], h["team"], "duels", d,
                          "HEBDO duel column drifted from the match record (e.g. CHEF stuck at 150-155 from June). "
                          "Rebuilt as +5 per win over another team's rostered player, events starting before the week date.",
                          "player-tab DUELS2025 flags agree with the rule on 1,527 of 1,529 matches")
    if season == 2023:
        w28 = sum(j["race"] for j in joueurs if j["week"] == 28 and j["team"] == "CHAN")
        for w in range(28, 33):
            set_hebdo(season, hebdo, w, "CHAN", "race", w28,
                      "CHAN was left out of the week-28 update and carried its week-27 value until week 33.",
                      "dated Tennis Explorer tab 20230717 (Alcaraz's Wimbledon title included)")
    if season == 2020:
        for h in hebdo:
            if h["team"] == "CHEF" and h["week"] >= 12:
                set_hebdo(season, hebdo, h["week"], "CHEF", "total", h["total"] + 20,
                          "ATP 500 tab, Hamburg row: CHEF formula counts finalists from columns G and K instead of "
                          "G and H, so Rublev's final (+20) was missed. Restores the SCORES total (430).",
                          "THE RACE 2020 › ATP 500 row 7; SCORES CHEF total 430")
        fin = next(h for h in hebdo if h["team"] == "CHEF" and h["week"] == max(x["week"] for x in hebdo))
        fin["race"], fin["duels"] = fin["total"] - 90, 90  # SCORES split, now that totals agree
        CHECKS[season].append(("corrected_hebdo_final_vs_scores_total", fin["week"], "CHEF", fin["total"], 430,
                               fin["total"] == 430))
        PENDING.append({"season": 2020, "team": "CHEF", "from_week": 16, "delta_total": 60,
                        "issue": "ATP 500 tab row 'Vienne' holds the Nur-Sultan results (Mannarino, Millman), so the "
                                 "Vienna 500 was never scored. Rublev won Vienna (SF 10 + F 20 + W 30 = 60 for CHEF); "
                                 "no other rostered player reached the semi-finals. Duels for that week were scored.",
                        "impact": "CHEF final 430 -> 490, moving CHEF from 4th to 3rd ahead of CHAN (435)."})
    if season == 2021:
        for h in hebdo:
            if h["team"] == "CHEF" and 17 <= h["week"] <= 28:
                delta = -40 if h["week"] <= 20 else -20
                set_hebdo(season, hebdo, h["week"], "CHEF", "total", h["total"] + delta,
                          "SLAM tab: CHEF formula skips quarter-finalists (Auger-Aliassime at Wimbledon, Berrettini "
                          "at the US Open); 60 was typed at Roland-Garros instead of 20 to compensate. Points moved to "
                          "the right weeks; season total unchanged.",
                          "THE RACE 2021 › SLAM rows 4-6 vs barème recomputation")
    # post-correction reconciliation
    hr = {(h["week"], h["team"]): h["race"] for h in hebdo}
    for w in sorted({j["week"] for j in joueurs if j["week"] is not None}):
        for tm in teams:
            tot = sum(j["race"] for j in joueurs if j["week"] == w and j["team"] == tm)
            if hr.get((w, tm)) is not None and season >= 2023:
                CHECKS[season].append(("joueurs_vs_corrected_hebdo", w, tm, tot, hr[(w, tm)], tot == hr[(w, tm)]))


# --------------------------------------------------------------------------- main
# Final placings stated by the league that the season workbook does not hold (no roster, no points).
LEAGUE_RECORD = {
    2019: [{"team": "CHEF", "rank": 4, "source": "Patrick, 28 Oct 2026",
            "note": "[league record] CHEF finished 4th in 2019; the workbook kept only PAT, REM (DOC) and CHAN, "
                    "so CHEF has no roster, points or weekly totals for 2019."}],
}

DATA_ISSUES = {  # status: "corrected" (see corrections.json) or "open"
    2025: ["[corrected] Tab 20251117w35 carried the 2024 Race table; week 35 rebuilt as week 34 + ATP Finals points.",
           "[corrected] HEBDO week-12 JULES Race typed 4,529; the week's team block sums to 4,579.",
           "[corrected] HEBDO duel column drifted from the match record; rebuilt from the per-match duel rule.",
           "[open] Kouame's Tennis Abstract tab is empty in the workbook, so he has no matches.",
           "[open] BILAN and LIVE are not used (BILAN reads LIVE)."],
    2024: ["[corrected] HEBDO week-2 CHEF read CHAN's cell (615 -> 820); week-24 CHEF read the week-25 tab (13,354 -> 13,023).",
           "[corrected] Player tabs carry no opponent ranking; ranks taken from the weekly ATP tables (28 of 1,557 matches still without).",
           "[open] Tab 20241118w39 and the LIVE/BILAN tabs hold live web imports that now return 2026 values; not used. "
           "The season ends at week 38 as recorded in HEBDO.",
           "[open] Final CHEF duel points: 240 in HEBDO vs 230 from the match record; HEBDO kept."],
    2023: ["[corrected] CHAN was left out of the week-28 update (carried 14,269 to week 32); set to the week-28 Tennis Explorer value.",
           "[open] 11 smaller week/team gaps between HEBDO and the dated Tennis Explorer tabs (update timing); HEBDO kept.",
           "[open] Player rows stop at week 37 (last dated tab); HEBDO runs to week 46. LIVE/BILAN Race columns are live formulas, not used."],
    2022: ["[open] Only the final standings survive (no weekly history, no per-player duel points). RACE2022data.dta holds "
           "weekly ATP ranking points, not Race points."],
    2021: ["[corrected] SLAM tab CHEF formula skipped quarter-finalists; 60 typed at Roland-Garros compensated. Points "
           "moved to Wimbledon/US Open weeks; season total unchanged."],
    2020: ["[corrected] ATP 500 Hamburg row: CHEF formula used column K instead of H for finalists (Rublev's final, +20). "
           "HEBDO now agrees with SCORES (CHEF 430).",
           "[pending your decision] The 'Vienne' row holds Nur-Sultan results, so Vienna (won by Rublev, +60 CHEF) was "
           "never scored; applying it would move CHEF from 4th to 3rd.",
           "[open] HEBDO stops at week 19 (15 Nov 2020); COVID suspension between weeks 7 and 8."],
    2019: ["[open] Auger-Aliassime's results before late June are excluded consistently in the tabs and SCORES "
           "(presumably a mid-season roster change); left as recorded."],
}


def build():
    out_hist = collections.defaultdict(list)
    seasons_meta = []
    team_rosters = []
    for season in (2019, 2020, 2021, 2022, 2023, 2024, 2025):
        tags = {}
        if season <= 2021:
            book, roster, hebdo, joueurs, matches, duel_pts, ranks, final_date, final_w, rk_date, teams, tags = season_bareme(season)
            scoring = "bareme"
        elif season == 2022:
            book, roster, hebdo, joueurs, matches, duel_pts, ranks, final_date, final_w, rk_date = season_2022()
            teams, scoring = ["PAT", "DOC", "CHAN", "CHEF"], "race"
        elif season == 2023:
            book, roster, hebdo, joueurs, matches, duel_pts, ranks, final_date, final_w, rk_date = season_2023()
            teams, scoring = ["PAT", "DOC", "CHAN", "CHEF"], "race"
        else:
            teams = ["PAT", "DOC", "CHAN", "CHEF"] + (["JULES"] if season == 2025 else [])
            res = season_blocks(season, f"THE_RACE_{season}.xlsx", season, teams,
                                last_valid_week=34 if season == 2025 else 38)
            if season == 2025:
                NOTES[season] = [n for n in NOTES[season] if not n.startswith("players.duel_pts")]
            book, roster, hebdo, joueurs, matches, duel_pts, ranks, final_date, final_w = res
            rk_date, scoring = final_date, "race"
        apply_corrections(season, hebdo, joueurs, matches, book, roster, teams)
        if season == 2025:
            final_w, final_date = 35, "2025-11-17"
            duel_pts = collections.Counter()
            for m in matches:
                if m["opponent_team"] and m["result"] == "V" and m["event_date"] < final_date:
                    duel_pts[(m["team"], m["player"])] += 5
            NOTES[season].append("players.duel_pts: +5 per win over another team's rostered player (rule), through "
                                 "the ATP Finals; replaces the player-tab flags, which missed two Djokovic wins in Geneva.")
        hebdo.sort(key=lambda h: (h["week"] if h["week"] is not None else -1, TEAM_ORDER.index(h["team"])))
        through = max((m["event_date"] for m in matches), default=None)
        # ranks keyed by atp id -> also make name keys available
        players = summarize(season, roster, matches, None, duel_pts, ranks, rk_date, through, scoring)
        # final credited league points per player
        fin = {}
        jw = max((j["week"] for j in joueurs if j["week"] is not None), default=None)
        for j in joueurs:
            if j["week"] == jw:
                fin[(j["team"], j["player"])] = j["race"]
        # outgoing players: frozen duel credit from the transfer ledger
        for st in roster.stints:
            if st["end"] and st.get("frozen_duels") is not None and (st["team"], st["player"]) in duel_pts:
                pass
        if season >= 2024:
            fw_h = {h["team"]: h["duels"] for h in hebdo if h["week"] == final_w}
            for tm in teams:
                dsum = sum(v for (t, _), v in duel_pts.items() if t == tm)
                CHECKS[season].append(("computed_duels_vs_hebdo", final_w, tm, dsum, fw_h.get(tm), dsum == fw_h.get(tm)))
        cal = calendar_from(matches, season)
        colors = [c for c in COLORS if c["team"] in teams]
        d = OUT / str(season) / "data"
        clean_hebdo = [{k: v for k, v in h.items() if not k.startswith("_")} for h in hebdo]
        for name, data in (("hebdo", clean_hebdo), ("joueurs", joueurs), ("players", players), ("matches", matches),
                           ("calendar", cal), ("team_colors", colors)):
            write_json(d / f"{name}.json", data)
        # final standings
        if final_w is None:
            final_rows = [h for h in hebdo]
        else:
            final_rows = [h for h in hebdo if h["week"] == final_w]
        standing = sorted(final_rows, key=lambda h: -(h["total"] or 0))
        seasons_meta.append({
            "season": season, "scoring_system": scoring, "teams": teams, "status": "complete",
            "final_week": final_w, "final_date": final_date, "weeks_recorded": len({h["week"] for h in hebdo if h["week"] is not None}),
            "players": len(players), "matches": len(matches),
            "final_standings": [{"rank": i + 1, "team": h["team"], "race": h["race"], "duels": h["duels"], "total": h["total"]}
                                for i, h in enumerate(standing)],
            "champion": standing[0]["team"] if standing and standing[0]["total"] is not None else None,
            "transfers": [{"team": tm, "out": o, "in": i_, "date": dte, "frozen_race_out": fr, "frozen_duels_out": frd,
                           "entry_offset_in": off} for tm, o, i_, dte, fr, frd, off in LEDGER.get(season, [])],
            "coverage_notes": sorted(set(NOTES[season])), "data_issues": DATA_ISSUES.get(season, []),
            "source_workbooks": sorted({f"THE RACE {season}", f"RESULTATS-THE RACE {season}"} if season <= 2022 else {f"THE RACE {season}"}),
        })
        for add in LEAGUE_RECORD.get(season, []):  # placings the league recorded outside the workbook
            meta = seasons_meta[-1]
            meta["teams"] = meta["teams"] + [add["team"]]
            meta["final_standings"].append({"rank": add["rank"], "team": add["team"], "race": None, "duels": None, "total": None})
            meta["final_standings"].sort(key=lambda f: f["rank"])
            meta["data_issues"] = meta["data_issues"] + [add["note"]]
            CORRECTIONS.append({"season": season, "week": None, "team": add["team"], "field": "rank", "recorded": None,
                                "corrected": add["rank"], "total_recorded": None, "total_corrected": None,
                                "reason": add["note"], "evidence": add["source"]})
        # stacked history
        weeks = collections.defaultdict(list)
        for h in hebdo:
            weeks[h["week"]].append(h)
        for w, hs in weeks.items():
            tot = sum(h["total"] or 0 for h in hs)
            ranked = sorted(hs, key=lambda h: -(h["total"] or 0))
            for h in hs:
                rec = h.get("_recorded")
                base = {k: v for k, v in h.items() if not k.startswith("_")}
                base.update({"corrected": rec is not None,
                             "race_recorded": rec["race"] if rec else h["race"],
                             "duels_recorded": rec["duels"] if rec else h["duels"],
                             "total_recorded": rec["total"] if rec else h["total"]})
                out_hist["hebdo"].append({"season": season, "scoring_system": scoring, **base,
                                          "rank": ranked.index(h) + 1 if h["total"] is not None else None,
                                          "share": round(h["total"] / tot, 4) if h["total"] is not None and tot else None})
        idmap = {(s["team"], s["player"]): s["atp_id"] for s in roster.stints}
        for j in joueurs:
            out_hist["joueurs"].append({"season": season, "scoring_system": scoring, **j, "atp_id": idmap.get((j["team"], j["player"]))})
        for p in players:
            out_hist["players"].append({"season": season, "scoring_system": scoring, "atp_id": idmap.get((p["team"], p["player"])),
                                        **p, "league_points": fin.get((p["team"], p["player"])),
                                        "slot": tags.get(fold(p["full"])) or tags.get(fold(p["player"]))})
        for m in matches:
            out_hist["matches"].append({"season": season, **m, "mid": f"{season}-{m['mid']}"})
        for s in roster.stints:
            team_rosters.append({k: s[k] for k in ("season", "team", "source_team", "player", "full", "atp_id", "start", "end",
                                                   "slot", "frozen_race", "frozen_duels", "entry_offset")})
        for c in cal:
            out_hist["calendar"].append({"season": season, **c})
    return out_hist, seasons_meta, team_rosters


def add_2026(out_hist, seasons_meta, team_rosters, repo_2026):
    """Append the live 2026 release (unchanged values) so the stacked history runs through today."""
    load = lambda n: json.loads((repo_2026 / f"{n}.json").read_text())
    hebdo, joueurs, players, matches, cal = (load(n) for n in ("hebdo", "joueurs", "players", "matches", "calendar"))
    weeks = collections.defaultdict(list)
    for h in hebdo:
        weeks[h["week"]].append(h)
    for w, hs in weeks.items():
        tot = sum(h["total"] for h in hs)
        ranked = sorted(hs, key=lambda h: -h["total"])
        for h in hs:
            out_hist["hebdo"].append({"season": 2026, "scoring_system": "race", **h, "corrected": False,
                                      "race_recorded": h["race"], "duels_recorded": h["duels"], "total_recorded": h["total"],
                                      "rank": ranked.index(h) + 1,
                                      "share": round(h["total"] / tot, 4) if tot else None})
    final_w = max(h["week"] for h in hebdo)
    fin = {(j["team"], j["player"]): j["race"] for j in joueurs if j["week"] == final_w}
    ids = {}
    for p in players:
        rec = IDS.resolve(p["full"])
        ids[(p["team"], p["player"])] = rec["id"] if rec else None
        out_hist["players"].append({"season": 2026, "scoring_system": "race", "atp_id": ids[(p["team"], p["player"])], **p,
                                    "league_points": fin.get((p["team"], p["player"])), "slot": None})
        team_rosters.append({"season": 2026, "team": p["team"], "source_team": p["team"], "player": p["player"],
                             "full": p["full"], "atp_id": ids[(p["team"], p["player"])],
                             "start": p["transfer_date"] if p["short"].endswith("(entré)") else None,
                             "end": p["transfer_date"] if p["short"].endswith("(sorti)") else None,
                             "slot": None, "frozen_race": None, "frozen_duels": None, "entry_offset": None})
    for j in joueurs:
        out_hist["joueurs"].append({"season": 2026, "scoring_system": "race", **j, "atp_id": ids.get((j["team"], j["player"]))})
    for m in matches:
        out_hist["matches"].append({"season": 2026, **m, "mid": f"2026-{m['mid']}"})
    for c in cal:
        out_hist["calendar"].append({"season": 2026, **c})
    last = sorted([h for h in hebdo if h["week"] == final_w], key=lambda h: -h["total"])
    seasons_meta.append({"season": 2026, "scoring_system": "race", "teams": [c["team"] for c in load("team_colors")],
                         "status": "in_progress", "final_week": final_w, "final_date": last[0]["date"],
                         "weeks_recorded": len(weeks), "players": len(players), "matches": len(matches),
                         "final_standings": [{"rank": i + 1, "team": h["team"], "race": h["race"], "duels": h["duels"],
                                              "total": h["total"]} for i, h in enumerate(last)],
                         "champion": None, "transfers": [], "coverage_notes": ["Copied unchanged from 2026/data (current published release)."],
                         "data_issues": [], "source_workbooks": ["THE RACE 2026"]})


if __name__ == "__main__":
    hist, meta, rosters = build()
    if len(sys.argv) > 3:
        add_2026(hist, meta, rosters, Path(sys.argv[3]))
    h = OUT / "history" / "data"
    for name, data in hist.items():
        write_json(h / f"{name}.json", data)
    write_json(h / "rosters.json", rosters)
    write_json(h / "seasons.json", meta)
    write_json(h / "corrections.json", {"applied": CORRECTIONS, "pending_confirmation": PENDING})
    write_json(h / "team_colors.json", COLORS)
    report = {str(s): {"checks": [dict(zip(("check", "week", "team", "value", "reference", "ok"), c)) for c in CHECKS[s]]}
              for s in sorted(CHECKS)}
    (OUT / "validation.json").write_text(json.dumps(report, indent=1, ensure_ascii=False))
    print("unresolved names:", sorted(IDS.unresolved))
    for s in sorted(CHECKS):
        bad = [c for c in CHECKS[s] if not c[-1]]
        print(s, "checks:", len(CHECKS[s]), "failed:", len(bad), bad[:6])
