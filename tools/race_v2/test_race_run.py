"""Relationship/state tests with synthetic private fixtures; no external calls."""
import copy
import csv
import hashlib
import json
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

import race_run as r


class Fixture:
    def __init__(self):
        self.clock = patch.object(r, "now", return_value="2026-11-16T23:30:00+00:00")
        self.clock.start()
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.put("profile.json", {"profile_version": "test-v2", "scope": "synthetic bounded weekly writes"})
        with (self.root / "roster.csv").open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["team", "sheet_name", "tennis_abstract_slug", "active"])
            w.writeheader()
            w.writerows({"team": team, "sheet_name": f"Player{i:02}", "tennis_abstract_slug": f"Player{i:02}", "active": "TRUE"}
                        for i, team in enumerate(t for t in ("PAT", "DOC", "CHAN", "CHEF", "JULES") for _ in range(6)))
        self.config = {"season": 2026, "target_monday": "2026-11-16", "competition_week": 39,
                       "competition_week_evidence": "synthetic prior league week 38",
                       "cutoff": "2026-11-16T00:00:00-05:00", "workflow_timezone": "America/New_York",
                       "profile_version": "test-v2", "profile_file": "profile.json",
                       "roster_version": "synthetic-roster", "roster_file": "roster.csv",
                       "scoring_version": "synthetic-rule", "repository": "example/race",
                       "production_branch": "main", "dashboard_url": "https://example.test/race/2026/"}
        self.put("input-config.json", self.config)
        self.state = r.init(self.root, self.root / "input-config.json")
        self.put("proof.json", {"mode": "synthetic test evidence"})
        self.put("start.txt", "Synthetic human message: Start this named week/profile.")
        self.put("approve.txt", "Synthetic human message: approve the exact reviewed release.")

    def put(self, path, data):
        p = self.root / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(data if isinstance(data, str) else json.dumps(data, indent=2) + "\n")
        return path

    def ref(self, path, **extra):
        return {**r.artifact(self.root, path), **extra}

    def start(self):
        r.start(self.root, self.state, "start.txt", self.state["profile_sha256"], self.state["revision"], "start-1", manual=True)

    def receipt(self, name, checks, **extra):
        return self.put(name, {"run_id": self.state["run_id"], "summary": "Synthetic state relationship proof",
                              "dependencies": [self.ref("proof.json")],
                              "checks": [{"id": n, "status": "PASS", "evidence": ["proof.json"],
                                          "counts": {"checked": 1, "missing": 0, "unexamined": 0}} for n in checks],
                              **extra})

    def collect_validate(self):
        self.start()
        self.receipt("acquire.json", r.ACQUIRE_CHECKS, state="verified",
                     units={"verified": 4, "total": 4}, source_counts={"active_players": 30, "te_joins": 60},
                     source_publication_dates={"race": "2026-11-16", "atp": "2026-11-16"},
                     cutoff_observed_at="2026-11-16T08:00:00-05:00")
        r.record(self.root, self.state, "acquire", "acquire.json")
        self.receipt("validate.json", r.VALIDATE_CHECKS, state="review_ready", units={"verified": 5, "total": 6})
        r.record(self.root, self.state, "validate", "validate.json")

    def bundle(self):
        teams = ["PAT", "DOC", "CHAN", "CHEF", "JULES"]
        players = [f"Player{i:02}" for i in range(30)]
        tables = {
            "hebdo": [{"week": 39, "date": "2026-11-16", "team": t, "race": 6, "duels": 0, "total": 6} for t in teams],
            "joueurs": [{"week": 39, "player": p, "team": teams[i // 6], "race": 1} for i, p in enumerate(players)],
            "players": [{"player": p, "team": teams[i // 6], "rankings_date": "2026-11-16", "elo_date": "2026-11-09",
                         **dict.fromkeys(("tpw", "rpw", "ace_pct", "first_won", "second_won"))}
                        for i, p in enumerate(players)],
            "matches": [], "calendar": [{"event": "Synthetic event"}],
            "team_colors": [{"team": t, "color": "#123456"} for t in teams]}
        for name, value in tables.items():
            self.put("candidate/" + name + ".json", value)
        self.put("expected-tables.json", tables)
        self.put("expected-contract.json", {"target_week": 39, "target_date": "2026-11-16", "teams": teams,
            "active_players": players, "archived_players": [], "published_players": players,
            "current_week_players": players, "team_totals": {t: {"race": 6, "duels": 0, "total": 6} for t in teams},
            "expected_rows": {n: len(v) for n, v in tables.items()},
            "expected_columns": {n: list(v[0]) if v else ["mid", "player", "event_date", "event", "round", "opponent", "score"]
                                 for n, v in tables.items()},
            "source_dates": {"rankings_date": "2026-11-16", "elo_date": "2026-11-09"},
            "field_reconciliation_passed": True})
        deps = []
        for role in ("primary_source", "frozen_values", "roster", "rules", "cutoff", "independent_audit"):
            p = "frozen/" + role + ".json"
            self.put(p, {"mode": "synthetic evidence", "role": role})
            deps.append(self.ref(p, role=role, domain="frozen"))
        self.put("manifest.json", {"run_id": self.state["run_id"], "release_id": "synthetic-2026-w39-r1",
                  "frozen_scope": "synthetic primary evidence and reviewed frozen values",
                  "exceptions": [], "frozen_dependencies": deps,
                  "data_files": {n: "candidate/" + n + ".json" for n in r.DATASETS},
                  "expected_tables_file": "expected-tables.json", "expected_contract_file": "expected-contract.json"})

    def seal(self):
        self.collect_validate(); self.bundle()
        r.seal(self.root, self.state, "manifest.json")

    def approve(self):
        self.seal()
        r.approve_release(self.root, self.state, self.state["candidate"]["sha256"], "approve.txt",
                          self.state["revision"], "approve-1")

    def release(self):
        self.approve()
        c = self.state["candidate"]
        for name, item in c["data_files"].items():
            p = self.root / ("remote/" + name + ".json")
            p.parent.mkdir(exist_ok=True); p.write_bytes((self.root / item["path"]).read_bytes())
        self.put("remote-metadata.json", {"commit_sha": "a" * 40, "branch_head_sha": "a" * 40})

        self.receipt("release.json", {"github-readback", "concurrency", "release-scope"},
            release_id=c["release_id"], candidate_sha256=c["sha256"], data_commit_sha="a" * 40,
            data_sha256=c["data_sha256"], release_branch="codex/data/synthetic-week39",
            readback_files={n: "remote/" + n + ".json" for n in r.DATASETS},
            readback_metadata_file="remote-metadata.json", handoff_file="handoff.md")
        r.handoff(self.root, self.state, "release.json", "handoff.md")
        r.release(self.root, self.state, "release.json")

    def production_receipt(self):
        self.release()
        c = self.state["candidate"]
        for n, item in c["data_files"].items():
            p = self.root / ("live/" + n + ".json")
            p.parent.mkdir(exist_ok=True); p.write_bytes((self.root / item["path"]).read_bytes())
        base = {"owner": "Claude", "production_status": "LIVE_DASHBOARD_VERIFIED",
            "release_id": c["release_id"], "data_commit_sha": "a" * 40, "dashboard_commit_sha": "b" * 40,
            "candidate_sha256": c["sha256"], "live_week": 39, "dashboard_url": self.config["dashboard_url"],
            "build_data_version": "test-version", "live_data_version": "test-version",
            "live_data_sha256": c["data_sha256"], "live_verified_at": "2026-11-16T18:00:00-05:00"}
        self.put("claude.json", base)
        self.put("deployment.json", {"status": "success", "commit_sha": "b" * 40, "url": "https://example.test/deployment", "completed_at": "2026-11-16T17:55:00-05:00"})
        self.put("live-page.html", '<html><meta name="data-version" content="test-version"></html>')
        self.put("ui.json", {"dashboard_url": self.config["dashboard_url"], "dashboard_commit_sha": "b" * 40,
                             "data_version": "test-version", "week": 39, "observed_at": "2026-11-16T17:59:00-05:00",
                             "covered_scopes": sorted(r.UI_SCOPES), "failed": 0, "console_errors": 0,
                             "checks": {n: {"pass": True} for n in r.UI_SCOPES}})
        self.put("built-page.html", (self.root / "live-page.html").read_text())
        self.put("page-metadata.json", {"url": self.config["dashboard_url"], "http_status": 200,
                                      "sha256": self.ref("live-page.html")["sha256"], "observed_at": "2026-11-16T17:59:00-05:00"})
        self.receipt("production.json", {"deployment", "live-hashes", "live-page", "browser-ui"}, **base,
             built_page_file="built-page.html", live_page_metadata_file="page-metadata.json",
             live_data_files={n: "live/" + n + ".json" for n in r.DATASETS}, live_page_file="live-page.html",
             ui_evidence_file="ui.json", claude_completion_evidence_file="claude.json",
             deployment_evidence_file="deployment.json")

    def readiness(self, partial=False):
        roster = [f"Player{i:02}" for i in range(30)]
        ta_key = ["9-Nov-2026", "Synthetic event", "Hard", "F", "Player00 d. Opponent", "6-0 6-0"]
        row = [*ta_key[:4], "1", "2", *ta_key[4:]]
        self.put("watch.json", {"synthetic_watchlist": ta_key})
        refs = [self.ref("watch.json")]
        players = []
        for slug in roster:
            p = {"player_id": slug}
            if not partial or slug == roster[0]:
                for view in ("Serve", "Return"):
                    path = "captures/" + slug + "-" + view + ".json"
                    headers = ["Date", "Tournament", "Surface", "Rd", "Rk", "vRk", "", "Score",
                               "BPSvd" if view == "Serve" else "BPCnv"]
                    self.put(path, {"url": "https://www.tennisabstract.com/cgi-bin/player.cgi?p=" + slug,
                         "view_requested": view, "automatic_scope_check": {"year_control_selected": True, "other_active_filters": []},
                         "tables": [{"id": "matches", "rows": [[{"text": x} for x in rr] for rr in [headers, row + ["0/0"]]]}]})
                    refs.append(self.ref(path))
                    p[view.lower() + "_evidence_path"] = path
            players.append(p)
        self.put("readiness.json", {"season": 2026, "competition_week": 39,
            "profile_hash": self.state["profile_sha256"], "roster_hash": self.state["configuration_artifacts"][1]["sha256"],
            "expected_players": roster, "players": players, "evidence": refs, "source_errors": [],
            "event_scope_verified": True, "watchlist_scope_verified": True, "watchlist_evidence": ["watch.json"],
            "relevant_events": [{"event_id": "synthetic-event", "closure": "COMPLETE", "closure_evidence": ["watch.json"],
                "watched_results": [{"result_id": "synthetic-final", "status": "COMPLETED",
                                    "selected_players": ["Player00"], "ta_key": ta_key}]}],
            "cutoff_recheck_verified": False, "dated_TE_release_verified": False})


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.f = Fixture()

    def tearDown(self):
        self.f.tmp.cleanup(); self.f.clock.stop()

    def test_complete_pipeline_only_reaches_100_after_actual_evidence_relationships(self):
        f = self.f; f.production_receipt()
        self.assertEqual(r.status(f.state)["percent"], 75)
        r.production(f.root, f.state, "production.json")
        self.assertEqual(r.status(r.load(f.root))["percent"], 100)
        self.assertEqual(r.status(f.state)["phase"], "complete")
        log = [json.loads(x) for x in (f.root / "events.jsonl").read_text().splitlines()]
        self.assertEqual(log, r.load(f.root)["events"])

    def test_no_work_before_start_and_no_duplicate_start(self):
        f = self.f
        with self.assertRaisesRegex(r.Refused, "Start"):
            r.record(f.root, f.state, "acquire", "absent.json")
        f.start()
        with self.assertRaisesRegex(r.Refused, "already recorded"):
            f.start()

    def test_approval_profile_revision_and_command_replay(self):
        f = self.f
        with self.assertRaisesRegex(r.Refused, "revision"):
            r.start(f.root, f.state, "start.txt", f.state["profile_sha256"], -1, "x")
        with self.assertRaisesRegex(r.Refused, "profile"):
            r.start(f.root, f.state, "start.txt", "0" * 64, f.state["revision"], "x")
        f.start()
        f.seal = None
        with self.assertRaisesRegex(r.Refused, "replayed"):
            r.verify_command(f.state, f.state["revision"], "start-1")

    def test_waiting_source_resumes_same_start_without_progress_reset(self):
        f = self.f; f.start()
        f.receipt("wait.json", [], state="waiting_source", units={"verified": 2, "total": 4})
        r.record(f.root, f.state, "acquire", "wait.json")
        self.assertEqual(r.status(f.state)["percent"], 17.5)
        self.assertIsNotNone(f.state["start_approval"])
        f.receipt("ready.json", r.ACQUIRE_CHECKS, state="verified", units={"verified": 4, "total": 4},
                  source_counts={"active_players": 30, "te_joins": 60},
                  source_publication_dates={"race": "2026-11-16", "atp": "2026-11-16"},
                     cutoff_observed_at="2026-11-16T08:00:00-05:00")
        r.record(f.root, f.state, "acquire", "ready.json")
        self.assertEqual(r.status(f.state)["percent"], 35)

    def test_missing_required_check_and_unexamined_scope_refuse_completion(self):
        f = self.f; f.start()
        f.receipt("bad.json", {"ta-source"}, state="verified", units={"verified": 1, "total": 1})
        with self.assertRaisesRegex(r.Refused, "coverage"):
            r.record(f.root, f.state, "acquire", "bad.json")
        d = r.read(f.root / "bad.json"); d["checks"][0]["counts"]["unexamined"] = 1
        f.put("bad.json", d)
        with self.assertRaises(r.Refused):
            r.checked_receipt(f.root, f.state, "bad.json", {"ta-source"})

    def test_changed_source_dependency_is_not_reused(self):
        f = self.f; f.collect_validate(); f.bundle()
        f.put("proof.json", {"changed": True})
        with self.assertRaisesRegex(r.Refused, "Evidence changed"):
            r.seal(f.root, f.state, "manifest.json")

    def test_candidate_cannot_depend_on_volatile_live(self):
        f = self.f; f.collect_validate(); f.bundle()
        manifest = r.read(f.root / "manifest.json")
        manifest["frozen_dependencies"][1]["domain"] = "volatile"
        f.put("manifest.json", manifest)
        with self.assertRaisesRegex(r.Refused, "Volatile"):
            r.seal(f.root, f.state, "manifest.json")

    def test_every_candidate_field_is_compared_with_independent_expectations(self):
        f = self.f; f.collect_validate(); f.bundle()
        expected = r.read(f.root / "expected-tables.json")
        expected["players"][0]["tpw"] = 0.5
        f.put("expected-tables.json", expected)
        with self.assertRaisesRegex(r.Refused, "field reconciliation"):
            r.seal(f.root, f.state, "manifest.json")

    def test_seal_and_approval_are_distinct_and_changed_candidate_refuses(self):
        f = self.f; f.seal()
        self.assertEqual(r.status(f.state)["percent"], 60)
        with self.assertRaisesRegex(r.Refused, "current frozen"):
            r.approve_release(f.root, f.state, "0" * 64, "approve.txt", f.state["revision"], "bad")
        f.put("frozen/frozen_values.json", {"changed": True})
        with self.assertRaisesRegex(r.Refused, "Evidence changed"):
            r.approve_release(f.root, f.state, f.state["candidate"]["sha256"], "approve.txt", f.state["revision"], "bad")

    def test_post_release_live_outage_does_not_invalidate_release_or_approval(self):
        f = self.f; f.release()
        approval = copy.deepcopy(f.state["release_approval"]); candidate = f.state["candidate"]["sha256"]
        f.put("live-health.json", {"status": "FAIL", "summary": "Synthetic transient import outage"})
        r.health(f.root, f.state, "LIVE", "live-health.json")
        self.assertEqual(f.state["release_approval"], approval)
        self.assertEqual(f.state["candidate"]["sha256"], candidate)
        self.assertEqual(r.status(f.state)["percent"], 75)
        self.assertEqual(r.status(f.state)["health"]["LIVE"], "FAIL")
        r.require_clearance(f.root, f.state)

    def test_tampered_github_readback_is_rejected(self):
        f = self.f; f.approve()
        # Build publication evidence without replacing the approved state.
        for n, x in f.state["candidate"]["data_files"].items():
            f.put("remote/" + n + ".json", r.read(f.root / x["path"]))
        f.put("remote/players.json", [])
        f.put("remote-metadata.json", {"commit_sha": "a" * 40, "branch_head_sha": "a" * 40})
        f.put("handoff.md", "Synthetic handoff")
        f.receipt("release.json", {"github-readback", "concurrency", "release-scope"},
            release_id=f.state["candidate"]["release_id"], candidate_sha256=f.state["candidate"]["sha256"],
            data_commit_sha="a" * 40, data_sha256=f.state["candidate"]["data_sha256"], release_branch="codex/data/test",
            readback_files={n: "remote/" + n + ".json" for n in r.DATASETS},
            readback_metadata_file="remote-metadata.json", handoff_file="handoff.md")
        with self.assertRaisesRegex(r.Refused, "Evidence changed"):
            r.release(f.root, f.state, "release.json")

    def test_wrong_live_hashes_page_or_owner_cannot_complete(self):
        f = self.f; f.production_receipt()
        original = r.read(f.root / "production.json")
        for field, value in (("owner", "GPT"), ("live_week", 38), ("live_data_version", "older")):
            d = copy.deepcopy(original); d[field] = value; f.put("production.json", d)
            with self.assertRaises(r.Refused):
                r.production(f.root, f.state, "production.json")
        f.put("production.json", original)
        f.put("live-page.html", '<meta name="data-version" content="wrong">')
        with self.assertRaises(r.Refused):
            r.production(f.root, f.state, "production.json")

    def test_changed_ui_coverage_or_failed_deployment_cannot_complete(self):
        f = self.f; f.production_receipt()
        ui = r.read(f.root / "ui.json"); ui["covered_scopes"] = ["filters"]; f.put("ui.json", ui)
        with self.assertRaisesRegex(r.Refused, "Browser UI"):
            r.production(f.root, f.state, "production.json")

    def test_path_escape_checksum_and_lock_protection(self):
        f = self.f
        with self.assertRaisesRegex(r.Refused, "inside"):
            r.artifact(f.root, "../escape")
        envelope = r.read(f.root / "run-state.json"); envelope["payload"]["revision"] += 1
        f.put("run-state.json", envelope)
        with self.assertRaisesRegex(r.Refused, "checksum"):
            r.load(f.root)
        with r.locked(f.root):
            with self.assertRaisesRegex(r.Refused, "lock"):
                with r.locked(f.root):
                    pass

    def test_partial_readiness_pilot_is_unknown_and_queues_nothing(self):
        f = self.f; f.readiness(partial=True)
        r.observe_readiness(f.root, f.state, "readiness.json")
        self.assertEqual(f.state["readiness"]["assessment"]["status"], "UNKNOWN")
        self.assertFalse(r.request_start(f.root, f.state))
        self.assertEqual(f.state["outbox"], [])

    def test_complete_readiness_binds_real_capture_rows_and_dedupes(self):
        f = self.f; f.readiness()
        r.observe_readiness(f.root, f.state, "readiness.json")
        self.assertTrue(f.state["readiness"]["assessment"]["ready_to_start"])
        self.assertFalse(f.state["readiness"]["assessment"]["release_sources_ready"])
        self.assertTrue(r.request_start(f.root, f.state))
        self.assertFalse(r.request_start(f.root, f.state))
        self.assertEqual(len(f.state["outbox"]), 1)
        self.assertIsNone(f.state["start_approval"])
        self.assertEqual(f.state["outbox"][0]["delivery_status"], "PENDING_DELIVERY")

    def test_readiness_does_not_trust_asserted_paired_view_boolean(self):
        f = self.f; f.readiness(partial=True)
        d = r.read(f.root / "readiness.json")
        for player in d["players"]:
            player.update(serve_verified=True, return_verified=True, serve_result_ids=["synthetic-final"],
                          return_result_ids=["synthetic-final"])
        f.put("readiness.json", d)
        r.observe_readiness(f.root, f.state, "readiness.json")
        self.assertEqual(f.state["readiness"]["assessment"]["status"], "UNKNOWN")

    def test_wrong_player_capture_and_modified_capture_refused(self):
        f = self.f; f.readiness()
        capture = r.read(f.root / "captures/Player00-Serve.json")
        capture["url"] = "https://www.tennisabstract.com/cgi-bin/player.cgi?p=Other"
        f.put("captures/Player00-Serve.json", capture)
        observation = r.read(f.root / "readiness.json")
        for item in observation["evidence"]:
            if item["path"] == "captures/Player00-Serve.json":
                item["sha256"] = f.ref(item["path"])["sha256"]
        f.put("readiness.json", observation)
        with self.assertRaisesRegex(r.Refused, "player URL"):
            r.observe_readiness(f.root, f.state, "readiness.json")

    def test_legacy_status_is_read_only_and_preserves_old_numbering(self):
        f = self.f
        legacy = {"schema_version": 3, "run_id": "old-run", "steps": {"7": {"name": "Gmail draft", "status": "done"}}}
        f.put("progress.json", {"payload": legacy, "sha256": r.digest(legacy)})
        before = (f.root / "progress.json").read_bytes()
        report = r.legacy_status(f.root)
        self.assertTrue(report["legacy_read_only"]); self.assertIn("7", report["steps"])
        self.assertEqual((f.root / "progress.json").read_bytes(), before)

    def test_independent_lane_does_not_change_race_percent(self):
        f = self.f; f.start()
        f.put("elo-lane.json", {"state": "no_source_advance", "summary": "Synthetic unchanged dated reports",
                               "dependencies": [f.ref("proof.json")]})
        r.lane(f.root, f.state, "elo", "elo-lane.json")
        self.assertIsNone(r.status(f.state)["percent"])
        self.assertEqual(f.state["independent_lanes"]["elo"]["state"], "no_source_advance")

    def test_notification_start_rejects_stale_request_then_accepts_refreshed_without_second_push(self):
        f = self.f; f.readiness()
        r.observe_readiness(f.root, f.state, "readiness.json")
        self.assertTrue(r.request_start(f.root, f.state))
        old = copy.deepcopy(f.state["outbox"][0])
        capture = r.read(f.root / "captures/Player00-Serve.json")
        capture["captured_at"] = "2026-11-16T17:00:00-05:00"
        f.put("captures/Player00-Serve.json", capture)
        observation = r.read(f.root / "readiness.json")
        observation["evidence"] = [f.ref(x["path"]) for x in observation["evidence"]]
        f.put("readiness.json", observation)
        r.observe_readiness(f.root, f.state, "readiness.json")
        self.assertFalse(r.request_start(f.root, f.state))
        current = f.state["outbox"][0]
        self.assertNotEqual(current["request_id"], old["request_id"])
        with self.assertRaisesRegex(r.Refused, "stale"):
            r.start(f.root, f.state, "start.txt", f.state["profile_sha256"], f.state["revision"], "start-current",
                    old["request_id"], old["readiness_hash"])
        r.start(f.root, f.state, "start.txt", f.state["profile_sha256"], f.state["revision"], "start-current",
                current["request_id"], current["readiness_hash"])
        self.assertEqual(f.state["start_approval"]["mode"], "readiness-request")
        self.assertEqual(len(f.state["outbox"]), 1)

    def test_two_selected_players_match_their_own_displayed_perspectives(self):
        f = self.f; f.readiness()
        observation = r.read(f.root / "readiness.json")
        result = observation["relevant_events"][0]["watched_results"][0]
        keys = {
            "Player00": ["9-Nov-2026", "Synthetic event", "Hard", "F", "Player00 d. (2)Player01 [USA]", "6-0 6-0"],
            "Player01": ["9-Nov-2026", "Synthetic event", "Hard", "F", "(1)Full Player00 [FRA] d. Player01", "6-0 6-0"]}
        result["selected_players"] = list(keys)
        result.pop("ta_key")
        result["ta_keys_by_player"] = keys
        for slug, key in keys.items():
            for view in ("Serve", "Return"):
                path = "captures/" + slug + "-" + view + ".json"
                capture = r.read(f.root / path)
                capture["tables"][0]["rows"][1] = [{"text": x} for x in key[:4] + ["1", "2"] + key[4:] + ["0/0"]]
                f.put(path, capture)
        observation["evidence"] = [f.ref(x["path"]) for x in observation["evidence"]]
        f.put("readiness.json", observation)
        r.observe_readiness(f.root, f.state, "readiness.json")
        self.assertEqual(f.state["readiness"]["assessment"]["status"], "READY_TO_START")

    def test_validation_checkpoint_cannot_bypass_the_approval_unit(self):
        f = self.f; f.collect_validate()
        f.receipt("blocked-validation.json", [], state="blocked", units={"verified": 6, "total": 6})
        with self.assertRaisesRegex(r.Refused, "approval"):
            r.record(f.root, f.state, "validate", "blocked-validation.json")

    def test_calculable_cutoff_and_future_source_dates_cannot_be_bypassed_by_pass(self):
        f = self.f; f.start()
        base = {"state": "verified", "units": {"verified": 4, "total": 4},
                "source_counts": {"active_players": 30, "te_joins": 60},
                "source_publication_dates": {"race": "2026-11-16", "atp": "2026-11-16"},
                "cutoff_observed_at": "2026-11-15T23:59:00-05:00"}
        f.receipt("early.json", r.ACQUIRE_CHECKS, **base)
        with self.assertRaisesRegex(r.Refused, "cutoff"):
            r.record(f.root, f.state, "acquire", "early.json")
        base["cutoff_observed_at"] = "2026-11-16T08:00:00-05:00"
        base["source_publication_dates"]["race"] = "2026-11-23"
        f.receipt("future.json", r.ACQUIRE_CHECKS, **base)
        with self.assertRaisesRegex(r.Refused, "future"):
            r.record(f.root, f.state, "acquire", "future.json")

    def test_stale_ui_and_future_production_cannot_pass(self):
        f = self.f; f.production_receipt()
        ui = r.read(f.root / "ui.json")
        ui["dashboard_commit_sha"] = "c" * 40
        f.put("ui.json", ui)
        with self.assertRaisesRegex(r.Refused, "stale production"):
            r.production(f.root, f.state, "production.json")
        p = r.read(f.root / "production.json"); p["live_verified_at"] = "2026-11-23T18:00:00-05:00"
        f.put("production.json", p)
        with self.assertRaisesRegex(r.Refused, "future"):
            r.production(f.root, f.state, "production.json")

    def test_actual_private_progress_page_escapes_text_and_flags_changed_evidence(self):
        f = self.f; f.production_receipt(); r.production(f.root, f.state, "production.json")
        self.assertTrue((f.root / "PROGRESS.html").is_file())
        self.assertIn("100.0% verified work", (f.root / "PROGRESS.html").read_text())
        f.put("proof.json", {"changed": "<script>alert('unsafe')</script>"})
        report = r.checked_status(f.root, f.state)
        self.assertIsNone(report["percent"])
        self.assertEqual(report["last_recorded_percent"], 100)
        r.write_progress_html(f.root / "attention.html", report)
        self.assertIn("Progress needs verification", (f.root / "attention.html").read_text())
        self.assertNotIn("<script>alert", (f.root / "attention.html").read_text())

    def test_generated_handoff_uses_release_values_and_excludes_private_candidate_paths(self):
        f = self.f; f.release()
        body = (f.root / "handoff.md").read_text()
        self.assertIn("a" * 40, body)
        self.assertIn(f.state["candidate"]["data_sha256"]["players"], body)
        self.assertNotIn(str(f.root), body)
        self.assertNotIn(f.state["candidate"]["sha256"], body)
        self.assertNotIn("frozen_values.json", body)


if __name__ == "__main__":
    unittest.main()
