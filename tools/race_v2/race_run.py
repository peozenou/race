#!/usr/bin/env python3
"""Private four-phase Race evidence ledger; no external writes or notifications.

An operator/skill obtains real source, Sheet, GitHub, Claude and live-browser
evidence. This runner verifies immutable artifacts and their relationships; it
cannot authenticate a human speaker, establish source truth, or deliver push.
"""
from __future__ import annotations
import argparse
import copy
import csv
import hashlib
import html
import json
import os
import re
import tempfile
from contextlib import contextmanager
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit, parse_qs
from zoneinfo import ZoneInfo

try:
    from . import check_dashboard, readiness
except ImportError:
    import check_dashboard
    import readiness

SCHEMA = 4
PHASES = ("acquire", "validate", "release", "production")
WEIGHTS = dict(zip(PHASES, (35, 30, 10, 25)))
DATASETS = ("hebdo", "joueurs", "players", "matches", "calendar", "team_colors")
HASH = re.compile(r"^[0-9a-f]{64}$")
COMMIT = re.compile(r"^(?!0{40}$)[0-9a-f]{40}$")
ACQUIRE_CHECKS = {"ta-source", "te-source", "cutoff", "sheet-readback", "history-protection"}
VALIDATE_CHECKS = {"ta-source-equality", "te-joins", "scoring", "team-paths",
                   "history-protection", "schema", "export-field-reconciliation"}
UI_SCOPES = {"filters", "tables", "history", "transfers", "source-dates", "mobile", "console"}


class Refused(ValueError):
    """A missing, stale or inconsistent prerequisite."""


def now():
    return datetime.now(timezone.utc).isoformat()



def observed_time(value):
    observed = datetime.fromisoformat(value)
    current = datetime.fromisoformat(now())
    if observed.tzinfo is None or observed > current:
        raise Refused("Observation must be timezone-aware and cannot be in the future.")
    return observed


def encode(value):
    return (json.dumps(value, sort_keys=True, ensure_ascii=False, indent=2,
                       allow_nan=False) + "\n").encode()


def digest(value):
    return hashlib.sha256(encode(value)).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def inside(root, value):
    p = (root / value).resolve()
    if not p.is_relative_to(root.resolve()):
        raise Refused("Artifacts must remain inside the private run directory.")
    return p


def artifact(root, value, expected=None):
    p = inside(root, value)
    if not p.is_file():
        raise Refused("Missing evidence: " + str(value))
    actual = hashlib.sha256(p.read_bytes()).hexdigest()
    if expected is not None and actual != expected:
        raise Refused("Evidence changed: " + str(value))
    return {"path": str(p.relative_to(root.resolve())), "sha256": actual}


def artifacts(root, values):
    """Require declared hashes; never silently refresh a stale dependency."""
    if not isinstance(values, list) or not values:
        raise Refused("Nonempty hashed artifact dependencies are required.")
    result = []
    for x in values:
        if not isinstance(x, dict) or not HASH.fullmatch(str(x.get("sha256", ""))):
            raise Refused("Each dependency needs a path and original SHA-256.")
        item = artifact(root, x["path"], x["sha256"])
        result.append({**item, **{k: v for k, v in x.items() if k not in item}})
    if len({x["path"] for x in result}) != len(result):
        raise Refused("Duplicate artifact dependency path.")
    return result


def atomic(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".race-", dir=path.parent)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "wb") as f:
            f.write(encode(value)); f.flush(); os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


@contextmanager
def locked(root):
    root.mkdir(parents=True, exist_ok=True)
    p = root / ".race-v2.lock"
    try:
        fd = os.open(p, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as exc:
        raise Refused("Run lock exists; inspect its PID before recovering it.") from exc
    try:
        with os.fdopen(fd, "w") as f:
            f.write(str(os.getpid()))
        yield
    finally:
        p.unlink(missing_ok=True)


def event(state, action, detail):
    previous = state["events"][-1]["sha256"] if state["events"] else None
    record = {"sequence": len(state["events"]) + 1, "at": now(),
              "action": action, "detail": detail, "previous_sha256": previous}
    state["events"].append({**record, "sha256": digest(record)})
    state["revision"] += 1


def _verify_events(state):
    previous = None
    for i, entry in enumerate(state["events"], 1):
        raw = {k: v for k, v in entry.items() if k != "sha256"}
        if entry["sequence"] != i or entry["previous_sha256"] != previous or digest(raw) != entry["sha256"]:
            raise Refused("Event chain changed.")
        previous = entry["sha256"]


def save(root, state):
    state["updated_at"] = now()
    atomic(root / "run-state.json", {"payload": state, "sha256": digest(state)})
    # The state is authoritative if interrupted before appending the log.
    log = root / "events.jsonl"
    existing = [json.loads(x) for x in log.read_text().splitlines()] if log.exists() else []
    if existing != state["events"][:len(existing)]:
        raise Refused("Event log is not a prefix of the authoritative ledger.")
    with log.open("a") as f:
        for entry in state["events"][len(existing):]:
            f.write(json.dumps(entry, sort_keys=True, ensure_ascii=False) + "\n")
        f.flush(); os.fsync(f.fileno())
    report = checked_status(root, state)
    atomic(root / "run-status.json", report)
    write_progress_html(root / "PROGRESS.html", report)


def load(root):
    envelope = read(root / "run-state.json")
    state = envelope["payload"]
    if state.get("schema_version") != SCHEMA or envelope["sha256"] != digest(state):
        raise Refused("State schema/checksum differs. Preserve and reconcile it.")
    _verify_events(state)
    for item in state["configuration_artifacts"]:
        artifact(root, item["path"], item["sha256"])
    return state


def verify_refs(root, refs):
    for item in refs:
        artifact(root, item["path"], item["sha256"])


def check_config(root, config):
    monday = date.fromisoformat(config["target_monday"])
    if monday.weekday() != 0 or monday.year != config["season"]:
        raise Refused("Target must be a Monday in the configured season.")
    cutoff = datetime.fromisoformat(config["cutoff"])
    if cutoff.tzinfo is None:
        raise Refused("Cutoff must be timezone-aware.")
    local = cutoff.astimezone(ZoneInfo("America/New_York"))
    if local.date() != monday or (local.hour, local.minute, local.second, local.microsecond) != (0, 0, 0, 0):
        raise Refused("Cutoff must be exclusive Monday midnight America/New_York.")
    if config.get("workflow_timezone") != "America/New_York":
        raise Refused("Resolve the New York workflow timezone.")
    if type(config.get("competition_week")) is not int or config["competition_week"] < 1 or not config.get("competition_week_evidence"):
        raise Refused("Resolve competition week from league evidence, not ISO week.")
    for name in ("profile_version", "scoring_version", "roster_version"):
        if not config.get(name):
            raise Refused("Missing configuration: " + name)
    with inside(root, config["roster_file"]).open(newline="", encoding="utf-8-sig") as f:
        roster = [r for r in csv.DictReader(f) if r.get("active", "").upper() == "TRUE"]
    ids = [r["tennis_abstract_slug"] for r in roster]
    if len(roster) != 30 or len(set(ids)) != 30 or len({r["sheet_name"] for r in roster}) != 30:
        raise Refused("Roster must have 30 unique active source/sheet identities.")
    teams = {"PAT", "DOC", "CHAN", "CHEF", "JULES"}
    if {r["team"] for r in roster} != teams or any(sum(r["team"] == t for r in roster) != 6 for t in teams):
        raise Refused("Roster requires six players per team.")
    u = urlsplit(config["dashboard_url"])
    if u.scheme != "https" or not u.hostname or u.username or u.password or u.query or u.fragment:
        raise Refused("Configure the canonical HTTPS dashboard URL.")
    if not config.get("repository") or not config.get("production_branch"):
        raise Refused("Configure repository and production branch.")
    return roster


def init(root, config_file, parent=None):
    if (root / "run-state.json").exists() or (root / "progress.json").exists():
        raise Refused("A run already exists. Legacy runs are read-only.")
    config = read(config_file)
    check_config(root, config)
    cfg = root / "config.json"
    if cfg.exists() and read(cfg) != config:
        raise Refused("Existing configuration differs.")
    if not cfg.exists():
        atomic(cfg, config)
    refs = [artifact(root, "config.json"), artifact(root, config["roster_file"]),
            artifact(root, config["profile_file"])]
    state = {"schema_version": SCHEMA, "run_id": config.get("run_id", config["target_monday"] + "-w" + str(config["competition_week"])),
             "config": config, "configuration_artifacts": refs,
             "profile_sha256": refs[2]["sha256"], "revision": 0, "created_at": now(),
             "events": [], "start_approval": None, "candidate": None, "release_approval": None,
             "release": None, "production": None, "parent_revision": parent,
             "phases": {n: {"state": "pending", "verified": 0, "total": None, "receipt": None} for n in PHASES},
             "health": {}, "readiness": None, "outbox": [], "consumed_commands": [],
             "independent_lanes": {"elo": {"state": "pending"}, "tiago-utr": {"state": "pending"},
                                   "tiago-matchtrack": {"state": "pending"}}}
    event(state, "init", {"parent_revision": parent})
    save(root, state)
    return state


def verify_command(state, expected_revision, command_id):
    if expected_revision is None or expected_revision != state["revision"]:
        raise Refused("State revision changed; reread before approving.")
    if not command_id or command_id in state["consumed_commands"]:
        raise Refused("Missing or replayed command ID.")


def human_artifact(root, path):
    item = artifact(root, path)
    if not inside(root, path).read_text().strip():
        raise Refused("Human evidence is empty.")
    return item


def start(root, state, human_evidence, profile_sha256, expected_revision, command_id, request_id=None, readiness_sha256=None, manual=False):
    if state["start_approval"]:
        raise Refused("Start already recorded; resume this run without another approval.")
    verify_command(state, expected_revision, command_id)
    if profile_sha256 != state["profile_sha256"]:
        raise Refused("Approval does not bind the installed profile hash.")
    if manual:
        if request_id or readiness_sha256:
            raise Refused("Choose explicit manual Start or a request-bound Start, not both.")
    else:
        if not request_id or not readiness_sha256 or not state["readiness"]:
            raise Refused("Start needs --manual or the current request ID/readiness hash.")
        observed = state["readiness"]
        verify_refs(root, [observed["observation"]] + observed["dependencies"])
        assessment = observed["assessment"]
        requests = [x for x in state["outbox"] if x["request_id"] == request_id]
        if (not assessment["ready_to_start"] or assessment["readiness_hash"] != readiness_sha256 or
                len(requests) != 1 or requests[0]["readiness_hash"] != readiness_sha256 or
                requests[0]["approval_status"] != "PENDING"):
            raise Refused("Start request is stale, superseded, not ready or already consumed.")
    approval = {"human_evidence": human_artifact(root, human_evidence), "profile_sha256": profile_sha256,
                "mode": "manual" if manual else "readiness-request", "request_id": request_id,
                "readiness_sha256": readiness_sha256,
                "profile_version": state["config"]["profile_version"], "run_id": state["run_id"], "at": now()}
    state["start_approval"] = approval
    state["consumed_commands"].append(command_id)
    state["phases"]["acquire"]["state"] = "running"
    for request in state["outbox"]:
        request["approval_status"] = "STARTED"
    event(state, "start", approval)
    save(root, state)


def require_start(root, state):
    if not state["start_approval"]:
        raise Refused("Weekly Start is missing.")
    ref = state["start_approval"]["human_evidence"]
    artifact(root, ref["path"], ref["sha256"])


def checked_receipt(root, state, path, required_checks):
    receipt_ref = artifact(root, path)
    receipt = read(inside(root, path))
    if receipt.get("run_id") != state["run_id"] or not receipt.get("summary"):
        raise Refused("Receipt identity/summary differs.")
    dependencies = artifacts(root, receipt.get("dependencies"))
    checks = receipt.get("checks")
    if not isinstance(checks, list):
        raise Refused("Receipt needs check-level evidence.")
    by_id = {x.get("id"): x for x in checks}
    if len(by_id) != len(checks) or not required_checks <= set(by_id):
        raise Refused("Required check coverage is incomplete or duplicated.")
    linked = {x["path"] for x in dependencies}
    for check in checks:
        if check.get("status") not in {"PASS", "QUALIFIED"}:
            raise Refused("Failed or unexamined required check: " + str(check.get("id")))
        if not check.get("evidence") or not set(check["evidence"]) <= linked:
            raise Refused("Check evidence is not bound by declared hashes.")
        counts = check.get("counts", {})
        if type(counts.get("checked")) is not int or counts["checked"] < 1 or counts.get("missing") != 0 or counts.get("unexamined") != 0:
            raise Refused("Check must report performed coverage and zero required gaps.")
        if check["status"] == "QUALIFIED" and not check.get("qualification"):
            raise Refused("Qualified check needs its bounded impact.")
    return receipt, [receipt_ref] + dependencies


def record(root, state, phase, path):
    require_start(root, state)
    if phase not in {"acquire", "validate"}:
        raise Refused("Use release/production for external publication receipts.")
    if state["candidate"]:
        raise Refused("Candidate is sealed; changed input needs a linked revision.")
    if phase == "validate" and state["phases"]["acquire"]["state"] != "verified":
        raise Refused("Acquire must be verified first.")
    raw = read(inside(root, path))
    if raw.get("state") in {"running", "waiting_source", "blocked"}:
        # Checkpoint is evidence-linked but cannot certify phase completion.
        refs = [artifact(root, path)] + artifacts(root, raw.get("dependencies"))
        if raw.get("run_id") != state["run_id"] or not raw.get("summary"):
            raise Refused("Checkpoint identity/summary differs.")
        receipt = raw
    else:
        receipt, refs = checked_receipt(root, state, path, ACQUIRE_CHECKS if phase == "acquire" else VALIDATE_CHECKS)
        if receipt.get("state") != ("verified" if phase == "acquire" else "review_ready"):
            raise Refused("Acquisition verifies; validation waits for the final approval unit.")
    units = receipt.get("units", {})
    done, total = units.get("verified"), units.get("total")
    if type(done) is not int or done < 0 or (total is not None and (type(total) is not int or total < 1 or done > total)):
        raise Refused("Invalid verified work units.")
    if total is not None and phase == "validate" and done >= total:
        raise Refused("Reserve the last validation unit for Patrick's release approval.")
    if total is not None and phase == "acquire" and receipt.get("state") != "verified" and done >= total:
        raise Refused("Unverified acquisition cannot claim every required unit.")
    previous = state["phases"][phase]
    if done < previous["verified"]:
        raise Refused("Verified work cannot disappear; create a linked revision.")
    if previous["total"] is not None and total != previous["total"]:
        raise Refused("Workset total changed; use a linked revision with its reason.")
    if phase == "acquire" and receipt.get("state") == "verified":
        if total is None or done != total:
            raise Refused("Acquisition has unverified work.")
        if receipt.get("source_counts", {}).get("active_players") != 30 or receipt.get("source_counts", {}).get("te_joins") != 60:
            raise Refused("Acquisition must account for 30 active players and 60 selected ranking joins.")
        dates = receipt.get("source_publication_dates", {})
        if not {"race", "atp"} <= set(dates):
            raise Refused("Record both actual TE source publication dates.")
        cutoff_observed = observed_time(receipt.get("cutoff_observed_at", ""))
        if cutoff_observed < datetime.fromisoformat(state["config"]["cutoff"]):
            raise Refused("Exclusive Monday cutoff has not been rechecked yet.")
        exceptions = receipt.get("source_date_exceptions", [])
        exception_by_source = {x.get("source"): x for x in exceptions}
        for name in ("race", "atp"):
            published = date.fromisoformat(dates[name])
            if published > datetime.fromisoformat(now()).astimezone(ZoneInfo("America/New_York")).date():
                raise Refused("Source publication date is in the future.")
            if published < date.fromisoformat(state["config"]["target_monday"]):
                exception = exception_by_source.get(name, {})
                if (exception.get("source_date") != dates[name] or not exception.get("id") or
                        not exception.get("impact")):
                    raise Refused("Older TE publication requires an exact disclosed source-date exception.")
                te_check = next(x for x in receipt["checks"] if x["id"] == "te-source")
                if te_check["status"] != "QUALIFIED":
                    raise Refused("Older TE source cannot receive an unqualified source PASS.")
    if phase == "validate" and receipt.get("state") == "review_ready":
        if total is None or total < 2 or done != total - 1:
            raise Refused("Reserve the last validation unit for Patrick's release approval.")
    state["phases"][phase] = {"state": receipt["state"], "verified": done, "total": total,
                              "receipt": receipt, "artifacts": refs, "updated_at": now()}
    event(state, "record", {"phase": phase, "receipt_sha256": refs[0]["sha256"]})
    save(root, state)


def require_phase(root, state, phase, expected):
    p = state["phases"][phase]
    if p["state"] not in expected:
        raise Refused(phase + " is " + p["state"])
    verify_refs(root, p["artifacts"])


def seal(root, state, manifest_file):
    require_start(root, state)
    require_phase(root, state, "acquire", {"verified"})
    require_phase(root, state, "validate", {"review_ready"})
    if state["candidate"]:
        raise Refused("Candidate already sealed; do not replace its meaning.")
    manifest = read(inside(root, manifest_file))
    if manifest.get("run_id") != state["run_id"] or not manifest.get("release_id"):
        raise Refused("Resolve manifest run/release identity.")
    refs = artifacts(root, manifest.get("frozen_dependencies"))
    roles = {x.get("role") for x in refs}
    if not {"primary_source", "frozen_values", "roster", "rules", "cutoff", "independent_audit"} <= roles:
        raise Refused("Frozen candidate dependency roles are incomplete.")
    if any(x.get("domain") != "frozen" for x in refs):
        raise Refused("Volatile health is not a frozen release dependency.")
    if not manifest.get("frozen_scope") or not isinstance(manifest.get("exceptions"), list):
        raise Refused("Name the exact frozen scope and explicit exception set.")
    ids = {x if isinstance(x, str) else x.get("id") for x in manifest["exceptions"]}
    required_exceptions = {x["id"] for x in state["phases"]["acquire"]["receipt"].get("source_date_exceptions", [])}
    if not required_exceptions <= ids:
        raise Refused("Frozen candidate omitted a selected older-source exception.")
    if observed_time(state["phases"]["acquire"]["receipt"]["cutoff_observed_at"]) < datetime.fromisoformat(state["config"]["cutoff"]):
        raise Refused("Do not seal before the exclusive cutoff recheck.")
    dataset_paths = manifest.get("data_files", {})
    if set(dataset_paths) != set(DATASETS):
        raise Refused("The existing six datasets are required.")
    data = {name: artifact(root, path) for name, path in dataset_paths.items()}
    if len({x["path"] for x in data.values()}) != 6:
        raise Refused("Data files are not distinct.")
    expected_ref = artifact(root, manifest["expected_tables_file"])
    expected = read(inside(root, expected_ref["path"]))
    if set(expected) != set(DATASETS):
        raise Refused("Independent expected tables must cover all six datasets.")
    if expected_ref["path"] in {x["path"] for x in data.values()}:
        raise Refused("The candidate cannot be its own expectation contract.")
    field_count = 0
    for name, item in data.items():
        actual = read(inside(root, item["path"]))
        if actual != expected[name]:
            raise Refused("Source-derived field reconciliation differs: " + name)
        field_count += sum(len(row) for row in actual)
    contract_ref = artifact(root, manifest["expected_contract_file"])
    contract = read(inside(root, contract_ref["path"]))
    if contract.get("target_week") != state["config"]["competition_week"] or contract.get("target_date") != state["config"]["target_monday"]:
        raise Refused("Source contract targets a different week/date.")
    # This existing independent structural checker also enforces identities,
    # source dates, grains, private-field exclusion, totals and null semantics.
    dirs = {inside(root, x["path"]).parent for x in data.values()}
    if len(dirs) != 1 or any(inside(root, x["path"]).name != n + ".json" for n, x in data.items()):
        raise Refused("Place all six existing named files in one candidate data directory.")
    validation = check_dashboard.check(next(iter(dirs)), contract)
    if validation["problems"]:
        raise Refused("Six-file validation failed: " + "; ".join(validation["problems"][:5]))
    candidate = {"manifest": artifact(root, manifest_file), "release_id": manifest["release_id"],
                 "run_id": state["run_id"], "frozen_scope": manifest["frozen_scope"],
                 "exceptions": manifest["exceptions"], "dependencies": refs,
                 "data_files": data, "data_sha256": {n: x["sha256"] for n, x in data.items()},
                 "expected_tables": expected_ref, "expected_contract": contract_ref,
                 "profile_sha256": state["profile_sha256"], "config_sha256": state["configuration_artifacts"][0]["sha256"],
                 "audit_artifacts": state["phases"]["validate"]["artifacts"],
                 "reconciled_field_count": field_count}
    candidate["sha256"] = digest(candidate)
    candidate["sealed_at"] = now()
    state["candidate"] = candidate
    state["phases"]["validate"]["state"] = "waiting_approval"
    event(state, "seal", {"candidate_sha256": candidate["sha256"], "release_id": candidate["release_id"]})
    save(root, state)


def verify_candidate(root, state):
    candidate = state.get("candidate")
    if not candidate:
        raise Refused("Frozen candidate is missing.")
    raw = {k: v for k, v in candidate.items() if k not in {"sha256", "sealed_at"}}
    if digest(raw) != candidate["sha256"]:
        raise Refused("Candidate checksum changed.")
    verify_refs(root, [candidate["manifest"], candidate["expected_tables"], candidate["expected_contract"]]
                + candidate["dependencies"] + list(candidate["data_files"].values()) + candidate["audit_artifacts"])
    return candidate


def approve_release(root, state, sha256, human_evidence, expected_revision, command_id):
    verify_command(state, expected_revision, command_id)
    candidate = verify_candidate(root, state)
    if state["release_approval"]:
        raise Refused("Release approval already recorded; resume without another prompt.")
    if sha256 != candidate["sha256"]:
        raise Refused("Approval does not bind the current frozen candidate.")
    approval = {"candidate_sha256": sha256, "human_evidence": human_artifact(root, human_evidence),
                "at": now(), "run_id": state["run_id"]}
    state["release_approval"] = approval
    state["consumed_commands"].append(command_id)
    phase = state["phases"]["validate"]
    phase["verified"], phase["state"] = phase["total"], "verified"
    state["phases"]["release"]["state"] = "running"
    event(state, "approve-release", approval)
    save(root, state)


def require_clearance(root, state):
    candidate = verify_candidate(root, state)
    approval = state["release_approval"]
    if not approval or approval["candidate_sha256"] != candidate["sha256"]:
        raise Refused("Exact candidate release clearance is missing.")
    verify_refs(root, [approval["human_evidence"]])
    return candidate


def check_commit(value):
    if not COMMIT.fullmatch(str(value)):
        raise Refused("An actual 40-character commit SHA is required.")


def handoff(root, state, receipt_file, output="CLAUDE_HANDOFF.md"):
    """Generate a bounded brief from the approved candidate and exact readback."""
    candidate = require_clearance(root, state)
    receipt, refs = checked_receipt(root, state, receipt_file, {"github-readback", "concurrency", "release-scope"})
    check_commit(receipt.get("data_commit_sha"))
    if (receipt.get("release_id") != candidate["release_id"] or
            receipt.get("candidate_sha256") != candidate["sha256"] or
            receipt.get("data_sha256") != candidate["data_sha256"]):
        raise Refused("Handoff release differs from the approved candidate.")
    if not receipt.get("release_branch") or receipt["release_branch"] == state["config"]["production_branch"]:
        raise Refused("Handoff needs the exact dedicated data branch.")
    files = receipt.get("readback_files", {})
    if set(files) != set(DATASETS):
        raise Refused("Handoff needs all six real readback files.")
    for name, path in files.items():
        refs.append(artifact(root, path, candidate["data_sha256"][name]))
    metadata = read(inside(root, receipt["readback_metadata_file"]))
    if metadata.get("commit_sha") != receipt["data_commit_sha"] or metadata.get("branch_head_sha") != receipt["data_commit_sha"]:
        raise Refused("Handoff commit/ref differs from the verified remote state.")
    contract = read(inside(root, candidate["expected_contract"]["path"]))
    config = state["config"]
    lines = [
        "# Claude dashboard production handoff",
        "",
        "Update, build, publish and verify THE RACE from this exact approved data release.",
        "Read the repository production/data runbooks and current remote HEAD; preserve concurrent work.",
        "",
        "- Repository: " + config["repository"],
        "- Release: " + candidate["release_id"],
        "- Branch: " + receipt["release_branch"],
        "- Data commit: " + receipt["data_commit_sha"],
        "- Season/week: " + str(config["season"]) + " / " + str(config["competition_week"]),
        "- Competition Monday: " + config["target_monday"],
        "- Exclusive completion cutoff: " + config["cutoff"],
        "- Canonical dashboard: " + config["dashboard_url"],
        "",
        "## Approved six-file hashes",
        "",
    ]
    lines.extend("- " + name + ".json: " + candidate["data_sha256"][name] for name in DATASETS)
    lines.extend(["", "## Approved team totals", "", "| Team | Race | Duels | Total |", "|---|---:|---:|---:|"])
    for team, values in contract["team_totals"].items():
        lines.append("| " + team + " | " + str(values["race"]) + " | " + str(values["duels"]) + " | " + str(values["total"]) + " |")
    lines.extend(["", "Source dates: " + json.dumps(contract["source_dates"], sort_keys=True), "",
                  "Row counts: " + json.dumps(contract["expected_rows"], sort_keys=True), "",
                  "## Qualifications", ""])
    for item in candidate["exceptions"]:
        if isinstance(item, str):
            lines.append("- " + item)
        else:
            lines.append("- " + str(item["id"]) + ": " + str(item.get("public_impact", item.get("impact", "See Patrick's reviewed qualification."))))
    if not candidate["exceptions"]:
        lines.append("No release qualifications were recorded.")
    lines.extend(["", "## Production checks", "",
        "Incorporate these data unmodified, run the existing season builder and publish through the configured route.",
        "Preserve the French interface, transfer lineage, null meanings, source dates, historical charts, mobile behavior, tooltips and tutorial.",
        "Do not patch cleared league data, redesign or regenerate optional previews/tutorials without a separate request.",
        "Verify successful exact-commit deployment, canonical served page bytes/version, all six live data hashes, week/date/five totals and browser behavior.",
        "UI evidence must cover filters, tables, history, transfers, source-dates, mobile and console, and bind URL, dashboard commit, data version, week and observed timestamp.",
        "Return Claude completion with release/data/dashboard commits, versions, live week, six hashes, timezone-aware observation, deployment result and browser evidence.",
        "Save a public sanitized production note; private approvals, candidate/workbook fingerprints, local paths and private observations stay private.",
        "Publication is incomplete while deployment/cache/UI checks are pending or failed. No email phase follows.",
        "",
        "Patrick invokes Claude explicitly; this file does not start another assistant.",
    ])
    path = inside(root, output)
    body = "\n".join(lines) + "\n"
    if path.exists() and path.read_text() != body:
        raise Refused("Existing handoff differs; use a new versioned output path.")
    path.write_text(body)
    os.chmod(path, 0o600)
    state["handoff"] = {"file": artifact(root, output), "candidate_sha256": candidate["sha256"],
                         "data_commit_sha": receipt["data_commit_sha"]}
    event(state, "handoff", {"data_commit_sha": receipt["data_commit_sha"], "file": state["handoff"]["file"]["path"]})
    save(root, state)


def release(root, state, receipt_file):
    candidate = require_clearance(root, state)
    if state["release"]:
        raise Refused("Release receipt is immutable.")
    receipt, refs = checked_receipt(root, state, receipt_file, {"github-readback", "concurrency", "release-scope"})
    check_commit(receipt.get("data_commit_sha"))
    if receipt.get("release_id") != candidate["release_id"] or receipt.get("candidate_sha256") != candidate["sha256"]:
        raise Refused("Released identity differs from clearance.")
    if receipt.get("data_sha256") != candidate["data_sha256"]:
        raise Refused("Released hashes differ from the sealed six-file bundle.")
    branch = receipt.get("release_branch")
    if not branch or branch == state["config"]["production_branch"]:
        raise Refused("Use a dedicated data-release branch.")
    files = receipt.get("readback_files", {})
    if set(files) != set(DATASETS):
        raise Refused("All six actual GitHub readback files are required.")
    for name, path in files.items():
        refs.append(artifact(root, path, candidate["data_sha256"][name]))
    metadata = read(inside(root, receipt["readback_metadata_file"]))
    refs.append(artifact(root, receipt["readback_metadata_file"]))
    if metadata.get("commit_sha") != receipt["data_commit_sha"] or metadata.get("branch_head_sha") != receipt["data_commit_sha"]:
        raise Refused("Remote branch and immutable readback commit differ.")
    generated = state.get("handoff")
    if (not generated or generated["candidate_sha256"] != candidate["sha256"] or
            generated["data_commit_sha"] != receipt["data_commit_sha"] or
            generated["file"]["path"] != receipt["handoff_file"]):
        raise Refused("Generate the exact manifest-derived handoff before completing release.")
    refs.append(artifact(root, receipt["handoff_file"], generated["file"]["sha256"]))
    state["release"] = {"receipt": receipt, "artifacts": refs, "recorded_at": now()}
    state["phases"]["release"] = {"state": "verified", "verified": 1, "total": 1}
    state["phases"]["production"]["state"] = "awaiting_claude"
    event(state, "release", {"commit_sha": receipt["data_commit_sha"], "release_id": candidate["release_id"]})
    save(root, state)


def production(root, state, receipt_file):
    candidate = require_clearance(root, state)
    if not state["release"] or state["production"]:
        raise Refused("A verified data release is needed; production receipt is immutable.")
    verify_refs(root, state["release"]["artifacts"])
    export = state["release"]["receipt"]
    receipt, refs = checked_receipt(root, state, receipt_file, {"deployment", "live-hashes", "live-page", "browser-ui"})
    if receipt.get("owner") != "Claude" or receipt.get("production_status") != "LIVE_DASHBOARD_VERIFIED":
        raise Refused("Actual Claude completion and verified live status are required.")
    for key, expected in (("release_id", export["release_id"]), ("data_commit_sha", export["data_commit_sha"]),
                          ("candidate_sha256", candidate["sha256"]), ("live_week", state["config"]["competition_week"]),
                          ("dashboard_url", state["config"]["dashboard_url"])):
        if receipt.get(key) != expected:
            raise Refused("Production binding differs: " + key)
    check_commit(receipt.get("dashboard_commit_sha"))
    if not receipt.get("build_data_version") or receipt.get("live_data_version") != receipt["build_data_version"]:
        raise Refused("Built and served data versions differ.")
    if receipt.get("live_data_sha256") != candidate["data_sha256"]:
        raise Refused("Served datasets differ from the approved release.")
    when = observed_time(receipt.get("live_verified_at", ""))
    files = receipt.get("live_data_files", {})
    if set(files) != set(DATASETS):
        raise Refused("Save all six actual served dataset bodies.")
    for name, path in files.items():
        refs.append(artifact(root, path, candidate["data_sha256"][name]))
    page_ref = artifact(root, receipt["live_page_file"])
    refs.append(page_ref)
    built_ref = artifact(root, receipt["built_page_file"], page_ref["sha256"])
    refs.append(built_ref)
    page = inside(root, receipt["live_page_file"]).read_text()
    page_metadata = read(inside(root, receipt["live_page_metadata_file"]))
    refs.append(artifact(root, receipt["live_page_metadata_file"]))
    if (page_metadata.get("url") != receipt["dashboard_url"] or page_metadata.get("http_status") != 200 or
            page_metadata.get("sha256") != page_ref["sha256"]):
        raise Refused("Served page metadata is not bound to the canonical URL/bytes.")
    observed_page = observed_time(page_metadata.get("observed_at", ""))
    if observed_page.tzinfo is None or observed_page > when:
        raise Refused("Page observation timestamp is invalid or later than completion.")
    match = re.search(r'<meta\s+name=["\']data-version["\']\s+content=["\']([^"\']+)', page)
    if not match or match[1] != receipt["build_data_version"]:
        raise Refused("Actual served page does not contain the verified build version.")
    ui = read(inside(root, receipt["ui_evidence_file"]))
    refs.append(artifact(root, receipt["ui_evidence_file"]))
    for key, expected in (("dashboard_url", receipt["dashboard_url"]),
                          ("dashboard_commit_sha", receipt["dashboard_commit_sha"]),
                          ("data_version", receipt["live_data_version"]), ("week", receipt["live_week"])):
        if ui.get(key) != expected:
            raise Refused("Browser UI evidence has a stale production binding: " + key)
    observed_ui = observed_time(ui.get("observed_at", ""))
    if observed_ui.tzinfo is None or observed_ui > when:
        raise Refused("UI observation timestamp is invalid or later than completion.")
    if not UI_SCOPES <= set(ui.get("covered_scopes", [])) or ui.get("failed") != 0 or ui.get("console_errors") != 0:
        raise Refused("Browser UI evidence lacks required coverage or has unresolved failures.")
    if not ui.get("checks") or not all(x.get("pass") is True for x in ui["checks"].values()):
        raise Refused("Browser check-level evidence did not pass.")
    for key in ("claude_completion_evidence_file", "deployment_evidence_file"):
        refs.append(artifact(root, receipt[key]))
    claude = read(inside(root, receipt["claude_completion_evidence_file"]))
    for key in ("owner", "production_status", "release_id", "data_commit_sha", "dashboard_commit_sha", "live_data_version"):
        if claude.get(key) != receipt[key]:
            raise Refused("Saved Claude evidence differs: " + key)
    deployment = read(inside(root, receipt["deployment_evidence_file"]))
    if deployment.get("status") != "success" or deployment.get("commit_sha") != receipt["dashboard_commit_sha"] or not deployment.get("url"):
        raise Refused("Deployment evidence lacks successful exact-commit publication.")
    deployed = observed_time(deployment.get("completed_at", ""))
    if deployed.tzinfo is None or deployed > min(observed_ui, observed_page):
        raise Refused("Live/UI evidence predates successful deployment.")
    state["production"] = {"receipt": receipt, "artifacts": refs, "recorded_at": now()}
    state["phases"]["production"] = {"state": "verified", "verified": 1, "total": 1}
    event(state, "production", {"dashboard_commit_sha": receipt["dashboard_commit_sha"], "live_verified_at": receipt["live_verified_at"]})
    save(root, state)


def health(root, state, domain, evidence):
    """Mutable operational health never rewrites immutable release authority."""
    item = artifact(root, evidence)
    report = read(inside(root, evidence))
    if report.get("status") not in {"PASS", "WARNING", "FAIL", "UNKNOWN"} or not report.get("summary"):
        raise Refused("Health report needs explicit status and summary.")
    state["health"][domain] = {"report": report, "evidence": item, "observed_at": now()}
    event(state, "health", {"domain": domain, "status": report["status"]})
    save(root, state)


def _ta_key(row):
    return tuple(" ".join(str(row[i]).split()) for i in (0, 1, 2, 3, 6, 7))


def inspect_ta_capture(root, path, slug, view, season, linked):
    if path not in linked:
        raise Refused("TA capture is not bound to the readiness evidence manifest.")
    capture = read(inside(root, path))
    url = urlsplit(capture.get("url", ""))
    if url.hostname not in {"tennisabstract.com", "www.tennisabstract.com"} or parse_qs(url.query).get("p") != [slug]:
        raise Refused("Readiness capture player URL differs from the approved roster.")
    if capture.get("view_requested") != view:
        raise Refused("Readiness capture has the wrong displayed view.")
    scope = capture.get("automatic_scope_check", {})
    if scope.get("other_active_filters") or not (scope.get("year_control_selected") or scope.get("career_checked_for_absent_year")):
        raise Refused("TA capture season/filter scope is not established.")
    tables = [t for t in capture.get("tables", []) if t.get("id") == "matches"]
    if len(tables) != 1:
        raise Refused("One displayed TA matches table is required.")
    rows = [[" ".join(str(c.get("text") or "").split()) for c in row] for row in tables[0].get("rows", [])]
    if not rows or rows[0][:4] != ["Date", "Tournament", "Surface", "Rd"] or ("BPSvd" if view == "Serve" else "BPCnv") not in rows[0]:
        raise Refused("Displayed TA table schema differs.")
    completed = []
    for row in rows[1:]:
        if len(row) >= 8 and row[0].endswith(str(season)) and row[7] and " d. " in row[6]:
            completed.append(_ta_key(row))
    if len(set(completed)) != len(completed):
        raise Refused("Duplicate displayed TA result identity.")
    return set(completed)


def observe_readiness(root, state, observation_file):
    observation = read(inside(root, observation_file))
    refs = artifacts(root, observation.get("evidence"))
    linked = {x["path"] for x in refs}
    expected = {"season": state["config"]["season"], "competition_week": state["config"]["competition_week"],
                "profile_hash": state["profile_sha256"], "roster_hash": state["configuration_artifacts"][1]["sha256"]}
    with inside(root, state["config"]["roster_file"]).open(newline="", encoding="utf-8-sig") as f:
        roster = [r["tennis_abstract_slug"] for r in csv.DictReader(f) if r.get("active", "").upper() == "TRUE"]
    if observation.get("expected_players") != roster:
        raise Refused("Readiness expected players must equal the actual approved roster order.")
    normalized = copy.deepcopy(observation)
    scoped = observation.get("watchlist_evidence", [])
    if not scoped or not set(scoped) <= linked:
        normalized["watchlist_scope_verified"] = False
    for event_scope in normalized.get("relevant_events", []):
        if not event_scope.get("closure_evidence") or not set(event_scope["closure_evidence"]) <= linked:
            event_scope["closure"] = "UNKNOWN"
    for player in normalized.get("players", []):
        slug = player.get("player_id")
        if slug not in roster:
            continue
        for view in ("Serve", "Return"):
            prefix = view.lower()
            path = player.get(prefix + "_evidence_path")
            player[prefix + "_verified"] = False
            player[prefix + "_result_ids"] = []
            if not path:
                continue
            found = inspect_ta_capture(root, path, slug, view, expected["season"], linked)
            player[prefix + "_verified"] = True
            for event_scope in normalized.get("relevant_events", []):
                for result in event_scope.get("watched_results", []):
                    selected = result.get("selected_players", [])
                    key = result.get("ta_keys_by_player", {}).get(slug)
                    if key is None and selected == [slug]:
                        key = result.get("ta_key")
                    if slug not in selected:
                        continue
                    if not isinstance(key, list) or len(key) != 6:
                        result["status"] = "UNKNOWN"
                    elif tuple(" ".join(str(x).split()) for x in key) in found:
                        player[prefix + "_result_ids"].append(result["result_id"])
    assessment = readiness.assess_readiness(normalized, expected)
    assessment["offer_start"] = bool(assessment["ready_to_start"] and not state["start_approval"])
    # The readiness hash binds actual capture bytes, not just asserted booleans.
    assessment["readiness_hash"] = digest({"normalized": normalized, "evidence": refs})
    state["readiness"] = {"assessment": assessment, "observation": artifact(root, observation_file),
                          "dependencies": refs, "observed_at": now()}
    event(state, "readiness", {"status": assessment["status"], "readiness_hash": assessment["readiness_hash"]})
    save(root, state)


def request_start(root, state):
    if state["start_approval"]:
        raise Refused("Start already accepted; continue the existing run.")
    if not state["readiness"]:
        raise Refused("No actual readiness observation exists.")
    item = state["readiness"]
    verify_refs(root, [item["observation"]] + item["dependencies"])
    assessment = item["assessment"]
    notification, outbox = readiness.queue_start_request(assessment, state["outbox"])
    # Replace prototype delivery label; this runner queues only, never sends.
    for record in outbox:
        if record["delivery_status"] == "NOT_DELIVERED_PROTOTYPE":
            record["delivery_status"] = "PENDING_DELIVERY"
    state["outbox"] = outbox
    event(state, "request-start", {"new_notification_queued": notification is not None,
                                  "weekly_key": outbox[-1]["dedupe_key"] if outbox else None})
    save(root, state)
    return notification is not None


def acknowledge_notification(root, state, request_id, evidence_file):
    report = read(inside(root, evidence_file))
    if report.get("request_id") != request_id or report.get("delivery_status") not in {"DELIVERED", "FAILED", "UNKNOWN"}:
        raise Refused("Delivery evidence differs from request.")
    records = [x for x in state["outbox"] if x["request_id"] == request_id]
    if len(records) != 1:
        raise Refused("Unknown or superseded request ID.")
    records[0]["delivery_status"] = report["delivery_status"]
    records[0]["delivery_evidence"] = artifact(root, evidence_file)
    event(state, "notification-delivery", {"request_id": request_id, "status": report["delivery_status"]})
    save(root, state)


def lane(root, state, name, receipt_file):
    report = read(inside(root, receipt_file))
    if report.get("state") not in {"pending", "waiting_input", "running", "verified", "no_source_advance", "blocked"}:
        raise Refused("Unknown independent-lane state.")
    refs = [artifact(root, receipt_file)] + artifacts(root, report.get("dependencies"))
    if not report.get("summary"):
        raise Refused("Independent lane needs a concrete summary.")
    state["independent_lanes"][name] = {"state": report["state"], "summary": report["summary"], "artifacts": refs}
    event(state, "independent-lane", {"lane": name, "state": report["state"]})
    save(root, state)


def status(state):
    percent, indeterminate = 0.0, False
    for name, weight in WEIGHTS.items():
        p = state["phases"][name]
        if p["total"] is not None:
            percent += weight * p["verified"] / p["total"]
        elif p["state"] not in {"pending", "awaiting_claude"}:
            indeterminate = True
    if percent >= 100 and not state["production"]:
        raise Refused("100% requires verified production evidence.")
    current = next((n for n in PHASES if state["phases"][n]["state"] != "verified"), "complete")
    current_receipt = state["phases"][current].get("receipt", {}) if current != "complete" else {}
    current_receipt = current_receipt or {}
    owner = ("Patrick" if current == "validate" and state["phases"][current]["state"] == "waiting_approval"
             else "Claude" if current == "production" else "GPT" if current != "complete" else None)
    return {"schema_version": SCHEMA, "run_id": state["run_id"], "revision": state["revision"],
            "phase": current, "state": "verified" if current == "complete" else state["phases"][current]["state"],
            "owner": owner,
            "blocker": current_receipt.get("summary") if current_receipt.get("state") in {"waiting_source", "blocked"} else None,
            "percent": None if indeterminate else round(percent, 2),
            "verified_floor_percent": round(percent, 2), "weights": WEIGHTS,
            "phases": {n: {k: v for k, v in state["phases"][n].items() if k not in {"receipt", "artifacts"}} for n in PHASES},
            "candidate_sha256": state["candidate"]["sha256"] if state["candidate"] else None,
            "release_id": state["candidate"]["release_id"] if state["candidate"] else None,
            "health": {n: x["report"]["status"] for n, x in state["health"].items()},
            "readiness": state["readiness"]["assessment"] if state["readiness"] else None,
            "independent_lanes": state["independent_lanes"],
            "source_dates": (state["phases"]["acquire"].get("receipt") or {}).get("source_publication_dates", {}),
            "updated_at": state.get("updated_at"), "basis": "verified work; not elapsed time",
            "next_action": current_receipt.get("next_action") or {"acquire": "Acquire/verify required sources; resume source waits under the same Start.",
                            "validate": "Validate source-derived candidate, seal it, then obtain exact release approval.",
                            "release": "Publish and read back the approved dedicated data release.",
                            "production": "Patrick invokes Claude; record actual deployment/live/browser evidence.",
                            "complete": "Verified production complete. No email phase."}[current]}


def checked_status(root, state):
    report = status(state)
    if not state['start_approval']:
        ready = bool(state.get('readiness') and state['readiness']['assessment'].get('ready_to_start'))
        report.update(state='waiting_start_approval' if ready else 'waiting_readiness',
                      owner='Patrick' if ready else 'GPT',
                      blocker='Weekly Start has not been approved.' if ready else 'Read-only source readiness has not been verified.',
                      next_action='Ask Patrick to approve the exact week/profile; optional UTR may be supplied together.' if ready
                      else 'Complete the read-only readiness check, then offer Start. Preparation is not approval.')
    errors = []
    refs = []
    if state["start_approval"]:
        refs.append(state["start_approval"]["human_evidence"])
    if state["release_approval"]:
        refs.append(state["release_approval"]["human_evidence"])
    for phase in state["phases"].values():
        refs.extend(phase.get("artifacts", []))
    for key in ("release", "production"):
        if state[key]:
            refs.extend(state[key]["artifacts"])
    for item in {x["path"]: x for x in refs}.values():
        try:
            artifact(root, item["path"], item["sha256"])
        except Refused as exc:
            errors.append(str(exc))
    if state["candidate"]:
        try:
            verify_candidate(root, state)
        except Refused as exc:
            errors.append(str(exc))
    report["evidence_errors"] = sorted(set(errors))
    report["evidence_checked_at"] = now()
    if errors:
        report["last_recorded_percent"] = report["percent"]
        report["percent"] = None
        report["state"] = "evidence_warning"
        report["next_action"] = "Reconcile changed immutable evidence; do not claim fresh completion or silently rebind."
    return report


def write_progress_html(path, report):
    """Generate a private, escaped monitor from actual ledger state, not fixtures."""
    e = lambda value: html.escape(str(value))
    pct = report.get("percent")
    bar = '<progress max="100" aria-label="Verified work"></progress>' if pct is None else (
        '<progress max="100" value="' + str(pct) + '" aria-label="Verified work"></progress>')
    label = "Progress needs verification" if report.get("evidence_errors") else (
        "Verified work total not yet known" if pct is None else str(pct) + "% verified work")
    phase_rows = "".join("<tr><td>" + e(name) + "</td><td>" + e(item["state"]) + "</td><td>" +
                         e(item["verified"]) + " / " + e(item["total"] if item["total"] is not None else "unknown") +
                         "</td></tr>" for name, item in report["phases"].items())
    lanes = "".join("<li>" + e(name) + ": " + e(item["state"]) + " " + e(item.get("summary", "")) + "</li>"
                    for name, item in report["independent_lanes"].items())
    warnings = "".join("<li>" + e(item) + "</li>" for item in report.get("evidence_errors", []))
    health_text = ", ".join(name + "=" + value for name, value in report["health"].items()) or "No reported health warnings."
    body = """<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="refresh" content="30">
<meta name="robots" content="noindex,nofollow"><title>THE RACE private progress</title>
<style>body{font:17px/1.5 system-ui,sans-serif;background:#f5f3ed;color:#172b3b;margin:0}
main{max-width:850px;padding:28px 20px;margin:auto}h1{line-height:1.15}progress{width:100%;height:28px;accent-color:#28785c}
table{width:100%;border-collapse:collapse}td,th{text-align:left;padding:12px 6px;border-bottom:1px solid #ccd4cf}
aside{padding:12px 0;color:#7a4415}pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:13px}
.private{font-weight:650;color:#28785c}.muted{color:#536267}</style><main>
<p class="private">PRIVATE · Actual recorded run state</p><h1>""" + e(report["run_id"]) + """</h1>
<h2>""" + e(label) + "</h2>" + bar + "<p>Phase: " + e(report["phase"]) + " · State: " + e(report["state"]) + (
        " · Needed: " + e(report["owner"]) if report["owner"] else "") + "</p><p>" + e(report["next_action"]) + "</p>" + (
        "<aside>Blocker: " + e(report["blocker"]) + "</aside>" if report.get("blocker") else "") + (
        "<aside><ul>" + warnings + "</ul></aside>" if warnings else "") + """
<table><thead><tr><th>Phase</th><th>State</th><th>Verified / required</th></tr></thead><tbody>""" + phase_rows + """</tbody></table>
<h2>Independent lanes</h2><ul>""" + lanes + "</ul><h2>Operational health</h2><p>" + e(health_text) + """</p>
<p class="muted">Operational LIVE health is separate from an unchanged sealed release. This page refreshes the stored status every30seconds;
it does not poll sources, approve actions or deliver notifications. Percent is verified work, not elapsed time.</p>
<p class="muted">Last ledger update: """ + e(report.get("updated_at")) + " · Evidence checked: " + e(report.get("evidence_checked_at")) + """</p>
<details><summary>Recorded status</summary><pre>""" + e(json.dumps(report, indent=2, ensure_ascii=False)) + "</pre></details></main></html>"
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".progress-", dir=path.parent)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w") as f:
            f.write(body); f.flush(); os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def legacy_status(root):
    """Only read a historical checksummed ledger; never migrate or rewrite it."""
    envelope = read(root / "progress.json")
    state = envelope["payload"]
    if envelope["sha256"] != digest(state):
        raise Refused("Legacy ledger checksum differs.")
    return {"schema_version": state.get("schema_version"), "legacy_read_only": True,
            "run_id": state.get("run_id"), "steps": {k: {"name": v.get("name"), "status": v.get("status")}
                                                    for k, v in state.get("steps", {}).items()},
            "note": "Historical numbering retained. New runs use four phases; this ledger was not rewritten."}


def summary(report):
    if report.get("legacy_read_only"):
        return json.dumps(report, indent=2)
    pct = "indeterminate" if report["percent"] is None else str(report["percent"]) + "%"
    text = [f"THE RACE · {report['run_id']} · {pct} verified work", "",
            "| Phase | State | Verified / required |", "|---|---|---|"]
    for name, p in report["phases"].items():
        text.append(f"| {name} | {p['state']} | {p['verified']} / {p['total'] if p['total'] is not None else 'unknown'} |")
    text.extend(["", report["next_action"], "Independent lanes: " + ", ".join(
        n + "=" + v["state"] for n, v in report["independent_lanes"].items())])
    return "\n".join(text)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    for cmd in ("init", "status", "start", "record", "seal", "approve-release", "handoff", "release",
                "production", "health", "readiness", "request-start", "acknowledge-notification", "lane", "revise"):
        q = sub.add_parser(cmd); q.add_argument("--run-dir", type=Path, required=True)
        if cmd in {"init", "revise"}: q.add_argument("--config", type=Path, required=True)
        if cmd in {"start", "approve-release"}:
            q.add_argument("--human-evidence", required=True)
            q.add_argument("--expected-revision", type=int, required=True)
            q.add_argument("--command-id", required=True)
        if cmd == "start":
            q.add_argument("--profile-sha256", required=True)
            q.add_argument("--manual", action="store_true")
            q.add_argument("--request-id"); q.add_argument("--readiness-sha256")
        if cmd == "approve-release": q.add_argument("--candidate-sha256", required=True)
        if cmd in {"record", "handoff", "release", "production", "lane"}: q.add_argument("--receipt", required=True)
        if cmd == "handoff": q.add_argument("--output", default="CLAUDE_HANDOFF.md")
        if cmd == "record": q.add_argument("--phase", choices=("acquire", "validate"), required=True)
        if cmd == "seal": q.add_argument("--manifest", required=True)
        if cmd == "health": q.add_argument("--domain", required=True)
        if cmd in {"health", "acknowledge-notification"}: q.add_argument("--evidence", required=True)
        if cmd == "readiness": q.add_argument("--observation", required=True)
        if cmd == "acknowledge-notification": q.add_argument("--request-id", required=True)
        if cmd == "lane": q.add_argument("--name", choices=("elo", "tiago-utr", "tiago-matchtrack"), required=True)
        if cmd == "revise":
            q.add_argument("--new-run-dir", type=Path, required=True); q.add_argument("--reason", required=True)
        if cmd == "status":
            q.add_argument("--json", action="store_true")
            q.add_argument("--html", help="Write a private status page inside the run directory")
    a = p.parse_args(argv); root = a.run_dir.resolve()
    try:
        if a.command == "status" and not (root / "run-state.json").exists() and (root / "progress.json").exists():
            result = legacy_status(root)
        elif a.command == "status":
            state = load(root); result = checked_status(root, state)
            if a.html:
                write_progress_html(inside(root, a.html), result)
        else:
            with locked(root):
                if a.command == "init":
                    state = init(root, a.config)
                else:
                    state = load(root)
                    if a.command == "start": start(root, state, a.human_evidence, a.profile_sha256, a.expected_revision, a.command_id,
                                                        a.request_id, a.readiness_sha256, a.manual)
                    elif a.command == "record": record(root, state, a.phase, a.receipt)
                    elif a.command == "seal": seal(root, state, a.manifest)
                    elif a.command == "approve-release": approve_release(root, state, a.candidate_sha256, a.human_evidence, a.expected_revision, a.command_id)
                    elif a.command == "handoff": handoff(root, state, a.receipt, a.output)
                    elif a.command == "release": release(root, state, a.receipt)
                    elif a.command == "production": production(root, state, a.receipt)
                    elif a.command == "health": health(root, state, a.domain, a.evidence)
                    elif a.command == "readiness": observe_readiness(root, state, a.observation)
                    elif a.command == "request-start": request_start(root, state)
                    elif a.command == "acknowledge-notification": acknowledge_notification(root, state, a.request_id, a.evidence)
                    elif a.command == "lane": lane(root, state, a.name, a.receipt)
                    elif a.command == "revise":
                        if not a.reason.strip(): raise Refused("Explain the changed frozen scope.")
                        newroot = a.new_run_dir.resolve()
                        if newroot == root: raise Refused("Revision needs a distinct private directory.")
                        with locked(newroot):
                            child = init(newroot, a.config, {"run_id": state["run_id"],
                                "candidate_sha256": state["candidate"]["sha256"] if state["candidate"] else None,
                                "reason": a.reason})
                        result = status(child)
                if a.command != "revise": result = checked_status(root, state)
        print(json.dumps(result, indent=2, ensure_ascii=False) if getattr(a, "json", False) else summary(result))
        return 0
    except (Refused, KeyError, ValueError, OSError) as exc:
        print("Stopped: " + str(exc))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
