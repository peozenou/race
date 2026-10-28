"""Audit 2019-2021 tournament tabs (QF/SF/F/W names) against Sackmann results."""
import csv, datetime as dt, json, sys
from pathlib import Path
import openpyxl
sys.path.insert(0, str(Path(__file__).parent))
from common import fold, iso

SRC = Path(sys.argv[1])
FILES = {2019: ("THE_RACE_2019.xlsx", "PARTICIPATIONS"), 2020: ("THE_RACE_2020.xlsx", "PARTICIPATIONS"),
         2021: ("THE_RACE_2021.xlsx", "Participation")}
LEVEL = {"ATP 250": "A", "ATP 500": "A", "ATP 1000": "M", "SLAM": "G"}

def last(n):
    return fold(n).split()[-1] if n else ""

def tournaments(year):
    T = {}
    for f in (year - 1, year) if year == 2019 else (year,):
        p = SRC / "sackmann" / f"atp_matches_{f}.csv"
        if not p.exists(): continue
        for r in csv.DictReader(open(p, encoding="utf-8")):
            t = T.setdefault(r["tourney_id"], {"name": r["tourney_name"], "date": iso(r["tourney_date"]), "lvl": r["tourney_level"],
                                               "QF": set(), "SF": set(), "F": set(), "W": None})
            rd = r["round"]
            if rd in ("QF", "SF", "F"):
                t[rd] |= {fold(r["winner_name"]), fold(r["loser_name"])}
            if rd == "F":
                t["W"] = fold(r["winner_name"])
    return T

out = []
for year, (fn, part) in FILES.items():
    wb = openpyxl.load_workbook(SRC / fn, data_only=True, read_only=True)
    hdr = list(wb[part].iter_rows(max_row=2, values_only=True))
    dates = [iso(v) for v in hdr[1][1:] if iso(v)]
    T = tournaments(year)
    for sh in ("ATP 250", "ATP 500", "ATP 1000", "SLAM"):
        rows = list(wb[sh].iter_rows(values_only=True))
        H = [str(x) if x else "" for x in rows[1]]
        for i, r in enumerate(rows[2:], 3):
            name = r[H.index("Tournoi") if "Tournoi" in H else 1] if len(r) > 1 else None
            if not name or not isinstance(r[0] if sh != "SLAM" or True else r[1], (int, float, type(None))):
                pass
            wk = r[0]
            if not name or str(name).startswith("TOTAL"):
                continue
            def col(lbl):
                return [r[j] for j, h in enumerate(H) if h == lbl and j < len(r)]
            qf = [x for k in range(1, 9) for x in col(f"Q{k}") if x]
            sf = [x for k in range(1, 5) for x in col(f"D{k}") if x]
            fi = [x for k in (1, 2) for x in col(f"F{k}") if x]
            w = (col("V") or [None])[0]
            if not (sf or fi or w):
                continue
            d = dates[int(wk) - 1] if isinstance(wk, (int, float)) and 0 < int(wk) <= len(dates) else None
            # best Sackmann candidate: same level family, nearest date, most overlap
            best, score = None, -1
            for tid, t in T.items():
                if t["lvl"] not in ("A", "M", "G", "F"): continue
                if d and abs((dt.date.fromisoformat(t["date"]) - dt.date.fromisoformat(d)).days) > 21: continue
                s = len({last(x) for x in sf} & {last(x) for x in t["SF"]}) + len({last(x) for x in fi} & {last(x) for x in t["F"]}) \
                    + (2 if w and t["W"] and last(w) == last(t["W"]) else 0) + (3 if fold(name)[:5] in fold(t["name"]) else 0)
                if s > score: best, score = t, s
            issues = []
            if best:
                if w and best["W"] and last(w) != last(best["W"]): issues.append(f"winner {w} vs {best['W']}")
                if fi and {last(x) for x in fi} != {last(x) for x in best["F"]}: issues.append(f"finalists {fi} vs {sorted(best['F'])}")
                if sf and {last(x) for x in sf} != {last(x) for x in best["SF"]}: issues.append(f"semis {sf} vs {sorted(best['SF'])}")
                if qf and {last(x) for x in qf} != {last(x) for x in best["QF"]}: issues.append(f"quarters {sorted(qf)} vs {sorted(best['QF'])}")
            else:
                issues.append("no Sackmann match")
            if issues:
                out.append({"season": year, "tab": sh, "row": i, "week": wk, "tournament": name,
                            "sackmann": best["name"] if best else None, "issues": issues})
print(json.dumps(out, indent=1, ensure_ascii=False))

# ---- pass 2: names, team-column arithmetic, missing events
FR = {"vienne": "vienna", "pekin": "beijing", "londres": "tour finals", "london": "tour finals", "anvers": "antwerp",
      "bale": "basel", "moscou": "moscow", "stokholm": "stockholm", "hertogenbosch": "hertogenbosch", "baastad": "bastad",
      "hambourg": "hamburg", "sardaigne": "sardinia", "melbourne": "australian open", "paris": "", "new york": "us open",
      "indianwells": "indian wells", "ind wells": "indian wells", "monte carlo": "monte carlo", "geneve": "geneva",
      "queens": "queen", "st petersburg": "st petersburg", "st peters": "st petersburg", "winston salem": "winston salem",
      "cologne2": "cologne 2", "cologne": "cologne", "delray": "delray beach", "rome": "rome", "barcelone": "barcelona",
      "sao paolo": "sao paulo", "flushing": "us open"}
BAREME = {2019: {"ATP 250": (0, 5, 10, 15), "ATP 500": (0, 10, 20, 30), "ATP 1000": (0, 15, 30, 45), "SLAM": (20, 35, 50, 60)},
          2020: {"ATP 250": (0, 5, 10, 15), "ATP 500": (0, 10, 20, 30), "ATP 1000": (0, 15, 30, 45), "SLAM": (20, 35, 50, 70)},
          2021: {"ATP 250": (0, 5, 10, 15), "ATP 500": (0, 10, 20, 30), "ATP 1000": (0, 15, 30, 45), "SLAM": (20, 35, 50, 70)}}
out2 = []
for year, (fn, part) in FILES.items():
    wb = openpyxl.load_workbook(SRC / fn, data_only=True, read_only=True)
    # read barème from the workbook itself
    B = {}
    for r in wb["BAREME"].iter_rows(min_row=2, max_row=5, values_only=True):
        if r[0]:
            B[str(r[0]).strip()] = tuple((float(x) if isinstance(x, (int, float)) else 0) for x in r[1:5])
    S = list(wb["SCORES"].iter_rows(values_only=True))
    roster = {}
    for i, r in enumerate(S):
        for c, v in enumerate(r):
            if isinstance(v, str) and v.startswith("TEAM ") and c + 1 < len(r) and r[c + 1] == "ATP 250":
                tm = v.replace("TEAM ", "").strip()
                for j in range(1, 7):
                    roster[last(S[i + j][c])] = tm
    teams_order = []
    for sh in ("ATP 250", "ATP 500", "ATP 1000", "SLAM"):
        rows = list(wb[sh].iter_rows(values_only=True))
        H = [str(x) if x else "" for x in rows[1]]
        bl = B["SLAM" if sh == "SLAM" else sh]
        # first team block: the 4/3 columns after the first empty column following "V"
        vpos = H.index("V")
        tcols = [j for j in range(vpos + 2, len(H)) if H[j] in ("P", "R", "C", "T", "F")]
        first = tcols[: len(tcols) // 2]
        ncol = next(j for j, h in enumerate(H) if h in ("Tournoi", "SLAM", "ATP 500", "ATP 1000"))
        for i, r in enumerate(rows[2:], 3):
            name = r[ncol] if len(r) > ncol else None
            if not name or str(name).upper().startswith("TOTAL"):
                continue
            def col(lbl):
                return [last(r[j]) for j, h in enumerate(H) if h == lbl and j < len(r) and r[j]]
            pts = {}
            for tm in set(roster.values()):
                pts[tm] = 0
            for p, tm in roster.items():
                q = sum(1 for k in range(1, 9) for x in col(f"Q{k}") if x == p)
                s = sum(1 for k in range(1, 5) for x in col(f"D{k}") if x == p)
                f = sum(1 for k in (1, 2) for x in col(f"F{k}") if x == p)
                w = sum(1 for x in col("V") if x == p)
                pts[tm] += q * bl[0] + s * bl[1] + f * bl[2] + w * bl[3]
            tab = {H[j]: r[j] for j in first if j < len(r)}
            letters = {"P": "PAT", "R": "REM", "C": "CHAN", "T": "CHAN", "F": "CHEF"}
            diffs = {letters[k]: (v, pts.get(letters[k] if letters[k] != "CHEF" else "CHEF", 0)) for k, v in tab.items()
                     if isinstance(v, (int, float)) and abs(v - pts.get(letters[k], 0)) > 0.01}
            if diffs:
                out2.append({"season": year, "tab": sh, "row": i, "tournament": name, "team_points_tab_vs_recomputed": diffs})
print("ARITH", json.dumps(out2, ensure_ascii=False, default=str))
