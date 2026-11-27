"""Tests for the v3 weekly pipeline. Run: python3 -m unittest discover -s tools/race_v3"""
import copy
import gzip
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE))
import race_week as rw  # noqa: E402

FIXTURE = HERE / "fixtures" / "2026-w39-baseline.json.gz"
DATA = ROOT / "2026" / "data"
MONDAY = "2026-11-23"
# Approved release 2026-11-23-w40-r2 (data commit db44c9f)
EXPECTED = {
    "hebdo": "93909b7ec455a04f3632bcc513d1ae1b180ee630d06367f628482b9f0c181405",
    "joueurs": "96d05e917a4db3cf000e473f3c75e3d817038aa81ab66ef5bfca4cd612b20510",
    "players": "7f7b2b10d4d96ebd36a8b52f4f1e2aad7d3573da56adfc154965b080970c5d87",
    "matches": "2084d9376b5794813f033cbb6a8ff866e82f3b6fa77cc709f80b3a7752de4c1b",
    "calendar": "a5b40cae611cf05229e6b7b572c035e7f19ec081a881804c64b611cdc7c9ba1a",
    "team_colors": "3ee69192269cf441b532cbeb47432effae3f202e1d02707ede686718ab315ca7",
}


def baseline():
    with gzip.open(FIXTURE, "rt", encoding="utf-8") as fh:
        return json.load(fh)


class ReplayWeek40(unittest.TestCase):
    def test_cli_reproduces_approved_release_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = dict(os.environ, PROGRESS_FILE=str(pathlib.Path(tmp) / "p.jsonl"))
            env.pop("GITHUB_ACTIONS", None)
            r = subprocess.run([sys.executable, str(HERE / "race_week.py"), "compute", "--baseline", str(FIXTURE),
                                "--collected", str(DATA), "--static", str(DATA), "--monday", MONDAY,
                                "--out", str(pathlib.Path(tmp) / "rel")], env=env, capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            manifest = json.loads((pathlib.Path(tmp) / "rel" / "release.json").read_text())
            self.assertEqual(manifest["sha256"], EXPECTED)
            self.assertEqual(manifest["totals"], {"PAT": 14623, "DOC": 18156, "CHAN": 19010, "CHEF": 19334, "JULES": 11912})
            points = [json.loads(l)["point"] for l in (pathlib.Path(tmp) / "p.jsonl").read_text().splitlines()]
            self.assertEqual(points, ["2 Calcul", "2 Calcul", "3 Contrôles"])


class Rules(unittest.TestCase):
    def setUp(self):
        self.base = baseline()
        self.players = json.loads((DATA / "players.json").read_text(encoding="utf-8"))
        self.matches = json.loads((DATA / "matches.json").read_text(encoding="utf-8"))

    def test_new_player_needs_decision(self):
        players = copy.deepcopy(self.players)
        players[0]["player"] = "Nouveau Joueur"
        with self.assertRaisesRegex(rw.CheckFailure, "Roster change"):
            rw.compute(self.base, players, self.matches, MONDAY)

    def test_monday_must_advance(self):
        with self.assertRaisesRegex(rw.CheckFailure, "not after"):
            rw.compute(self.base, self.players, self.matches, "2026-11-16")

    def test_duel_counts_only_wins_against_other_teams_before_cutoff(self):
        m = [{"team": "PAT", "player": "A", "opponent_team": "DOC", "result": "V", "event_date": "2026-11-20"},
             {"team": "PAT", "player": "A", "opponent_team": "", "result": "V", "event_date": "2026-11-20"},
             {"team": "PAT", "player": "A", "opponent_team": "DOC", "result": "D", "event_date": "2026-11-20"},
             {"team": "PAT", "player": "A", "opponent_team": "DOC", "result": "V", "event_date": "2026-11-23"}]
        self.assertEqual(rw.duel_points(m, MONDAY)[("PAT", "A")], 5)

    def _release(self):
        h, j, _ = rw.compute(self.base, self.players, self.matches, MONDAY)
        return {"hebdo": h, "joueurs": j, "players": self.players, "matches": self.matches}

    def test_checks_pass_on_approved_week(self):
        self.assertEqual(rw.run_checks(self.base, self._release(), MONDAY), [])

    def test_history_edit_blocks(self):
        rel = self._release()
        rel["hebdo"] = copy.deepcopy(rel["hebdo"]); rel["hebdo"][5]["race"] += 1
        with self.assertRaisesRegex(rw.CheckFailure, "HEBDO history changed"):
            rw.run_checks(self.base, rel, MONDAY)

    def test_match_after_cutoff_blocks(self):
        rel = self._release()
        rel["matches"] = copy.deepcopy(rel["matches"]); rel["matches"][-1]["event_date"] = MONDAY
        with self.assertRaisesRegex(rw.CheckFailure, "cutoff"):
            rw.run_checks(self.base, rel, MONDAY)

    def test_duplicate_selection_blocks(self):
        rel = self._release()
        rel["players"] = copy.deepcopy(rel["players"])
        active = [p for p in rel["players"] if p["rankings_date"] == MONDAY]
        active[1]["player"] = active[0]["player"]
        with self.assertRaisesRegex(rw.CheckFailure, "selected twice"):
            rw.run_checks(self.base, rel, MONDAY)

    def test_stage_refuses_changed_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            rel, dest = pathlib.Path(tmp) / "rel", pathlib.Path(tmp) / "dest"
            rel.mkdir(); dest.mkdir()
            for n in rw.DATA_FILES:
                (rel / f"{n}.json").write_bytes((DATA / f"{n}.json").read_bytes())
            (rel / "release.json").write_text(json.dumps({"week": 40, "sha256": EXPECTED}))
            self.assertEqual(rw.main(["stage", "--release", str(rel), "--dest", str(dest)]), 0)
            (rel / "hebdo.json").write_text("[]\n")
            self.assertEqual(rw.main(["stage", "--release", str(rel), "--dest", str(dest)]), 1)


if __name__ == "__main__":
    unittest.main()
