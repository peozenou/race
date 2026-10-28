"""Shared helpers for converting historical THE RACE workbooks to the 2026 dashboard schema."""
import csv
import datetime as dt
import json
import re
import unicodedata
from pathlib import Path

TEAM_ORDER = ["PAT", "DOC", "CHAN", "CHEF", "JULES"]
TEAM_ALIASES = {"REM": "DOC", "JUL": "JULES", "Pat": "PAT", "Rem": "DOC", "Chan": "CHAN", "Chef": "CHEF"}

SURFACE = {"hard": "Dur", "clay": "Terre battue", "grass": "Gazon", "carpet": "Moquette"}
ROUND = {"R128": "1/64", "R64": "1/32", "R32": "1/16", "R16": "1/8", "QF": "1/4", "SF": "1/2",
         "F": "F", "RR": "Poule", "Q1": "Q1", "Q2": "Q2", "Q3": "Q3", "Q4": "Q4", "BR": "Bronze", "ER": "Tour préliminaire"}
ROUND_ORDER = {"Q1": 0, "Q2": 1, "Q3": 2, "Q4": 3, "Poule": 4, "Tour préliminaire": 4, "1/64": 5, "1/32": 6,
               "1/16": 7, "1/8": 8, "1/4": 9, "1/2": 10, "Bronze": 11, "F": 12}

# Event labels used by the 2026 dashboard (French), keyed by normalized source names.
EVENT_LABELS = {
    "australian open": ("Open d'Australie", "Grand Chelem"),
    "roland garros": ("Roland-Garros", "Grand Chelem"),
    "wimbledon": ("Wimbledon", "Grand Chelem"),
    "us open": ("US Open", "Grand Chelem"),
    "indian wells masters": ("Masters d'Indian Wells", "Masters 1000"),
    "indian wells": ("Masters d'Indian Wells", "Masters 1000"),
    "miami masters": ("Masters de Miami", "Masters 1000"),
    "miami": ("Masters de Miami", "Masters 1000"),
    "monte carlo masters": ("Masters de Monte-Carlo", "Masters 1000"),
    "monte carlo": ("Masters de Monte-Carlo", "Masters 1000"),
    "madrid masters": ("Masters de Madrid", "Masters 1000"),
    "madrid": ("Masters de Madrid", "Masters 1000"),
    "rome masters": ("Masters de Rome", "Masters 1000"),
    "rome": ("Masters de Rome", "Masters 1000"),
    "canada masters": ("Masters du Canada", "Masters 1000"),
    "montreal masters": ("Masters du Canada", "Masters 1000"),
    "toronto masters": ("Masters du Canada", "Masters 1000"),
    "cincinnati masters": ("Masters de Cincinnati", "Masters 1000"),
    "cincinnati": ("Masters de Cincinnati", "Masters 1000"),
    "shanghai masters": ("Masters de Shanghai", "Masters 1000"),
    "shanghai": ("Masters de Shanghai", "Masters 1000"),
    "paris masters": ("Masters de Paris", "Masters 1000"),
    "tour finals": ("ATP Finals", "ATP Finals"),
    "atp finals": ("ATP Finals", "ATP Finals"),
    "nitto atp finals": ("ATP Finals", "ATP Finals"),
    "masters cup": ("ATP Finals", "ATP Finals"),
    "next gen finals": ("Next Gen Finals", "Exhibition"),
    "united cup": ("United Cup", "Compétition par équipes"),
    "atp cup": ("ATP Cup", "Compétition par équipes"),
    "laver cup": ("Laver Cup", "Compétition par équipes"),
}
SACKMANN_LEVEL = {"G": "Grand Chelem", "M": "Masters 1000", "A": "ATP 500/250", "F": "ATP Finals",
                  "D": "Compétition par équipes", "O": "Jeux Olympiques", "C": "Challenger", "S": "ITF"}


def fold(s):
    """ASCII-fold, lowercase, drop punctuation, collapse spaces."""
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-zA-Z ]", " ", s.replace("-", " ").replace("'", ""))
    return re.sub(r"\s+", " ", s).strip().lower()


def iso(d):
    if d is None or d == "":
        return None
    if isinstance(d, dt.datetime):
        return d.date().isoformat()
    if isinstance(d, dt.date):
        return d.isoformat()
    s = str(d).strip().replace("‑", "-").replace("‐", "-")
    for fmt in ("%Y%m%d", "%Y-%m-%d", "%d-%b-%Y", "%Y-%m-%d %H:%M:%S"):
        try:
            return dt.datetime.strptime(s.split(".")[0] if fmt == "%Y%m%d" else s, fmt).date().isoformat()
        except ValueError:
            pass
    return None


def num(v):
    if v is None or v == "" or (isinstance(v, str) and v.strip() in {"-", ".", "#N/A", "#DIV/0!"}):
        return None
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return int(f) if f == int(f) else round(f, 2)


class Identity:
    """Resolve the many spellings in the workbooks to one ATP (Sackmann) identity."""

    MANUAL = {  # workbook spelling (folded) -> canonical "first last" (folded)
        "karen kachanov": "karen khachanov", "fils arthur": "arthur fils", "arthur fils": "arthur fils",
        "juncheng shang": "juncheng shang", "shang juncheng": "juncheng shang",
        "tsitsipas stefan": "stefanos tsitsipas", "alex de minaur": "alex de minaur", "de minaur alex": "alex de minaur",
        "mpetshi perricard giovanni": "giovanni mpetshi perricard", "gmp": "giovanni mpetshi perricard",
        "thiago seyboth wild": "thiago seyboth wild", "cazaux arthur": "arthur cazaux",
        "auger aliassime felix": "felix auger aliassime", "auger aliassime": "felix auger aliassime",
        "felix auger aliassime": "felix auger aliassime", "kouame moise": "moise kouame",
        "jiri lehecka": "jiri lehecka", "lehecka jiri": "jiri lehecka", "richard gasquet": "richard gasquet",
        "frances tiafoe": "frances tiafoe", "nikoloz basilashvili": "nikoloz basilashvili",
    }

    def __init__(self, players_csv):
        self.by_key, self.by_id = {}, {}
        with open(players_csv, newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                dob = r["dob"][:8] if r["dob"] else ""
                if dob and dob < "19700101":
                    continue  # current-era players only; avoids namesake collisions
                pid = int(r["player_id"])
                first, last = r["name_first"].strip(), r["name_last"].strip()
                rec = {"id": pid, "first": first, "last": last, "dob": dob or None, "ioc": r["ioc"]}
                self.by_id[pid] = rec
                for key in (fold(f"{first} {last}"), fold(f"{last} {first}")):
                    self.by_key.setdefault(key, rec)
        # players missing from the bundled atp_players.csv vintage
        for first, last, dob in (("Moise", "Kouame", "20090101"),):
            rec = {"id": None, "first": first, "last": last, "dob": None, "ioc": None}
            for key in (fold(f"{first} {last}"), fold(f"{last} {first}")):
                self.by_key.setdefault(key, rec)
        self.unresolved = set()

    def resolve(self, name):
        if name is None:
            return None
        raw = re.sub(r"^[✓\s]+", "", str(name)).strip()
        key = fold(raw)
        key = self.MANUAL.get(key, key)
        rec = self.by_key.get(key)
        if rec is None:  # tolerate truncated first names, e.g. "Tsitsipas Stefan"
            toks = key.split()
            cands = [r for k, r in self.by_key.items() if toks and k.startswith(key)]
            if len({c["id"] for c in cands}) == 1:
                rec = cands[0]
        if rec is None:
            self.unresolved.add(raw)
        return rec

    @staticmethod
    def labels(rec, fallback):
        if rec is None:
            parts = str(fallback).split()
            return {"player": fallback, "short": parts[0] if parts else fallback, "full": fallback}
        first = fold(rec["first"]).title() if not rec["first"].isascii() else rec["first"]
        last = unicodedata.normalize("NFKD", rec["last"]).encode("ascii", "ignore").decode().replace("-", " ")
        first = unicodedata.normalize("NFKD", rec["first"]).encode("ascii", "ignore").decode().replace("-", " ")
        return {"player": f"{last} {first}", "short": last, "full": f"{first} {last}"}


def event_label(name, level_hint=None):
    key = fold(name)
    if key in EVENT_LABELS:
        return EVENT_LABELS[key]
    if key.startswith("davis cup"):
        return (re.sub(r"(?i)^davis cup", "Coupe Davis", str(name).strip()), "Compétition par équipes")
    if re.search(r"\bch$", key) or key.endswith(" ch"):
        return (str(name).strip(), "Challenger")
    if re.match(r"^m\d{2}\b", key) or re.search(r"\bf\d+$", key):
        return (str(name).strip(), "ITF")
    if "olympics" in key:
        return ("Jeux Olympiques", "Jeux Olympiques")
    return (str(name).strip(), level_hint or "ATP 500/250")


def write_json(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rows, ensure_ascii=False, indent=0, separators=(",", ": ")) + "\n", encoding="utf-8")
