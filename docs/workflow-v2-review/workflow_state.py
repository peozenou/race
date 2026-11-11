"""Offline, synthetic Race readiness/progress contract prototype.

No scraper, credentials, scheduler, notification delivery or authorization service.
Production adapters must establish the truth/authenticity of normalized observations.
"""
from __future__ import annotations
import copy
import hashlib
import json
import re
from decimal import Decimal

PHASE_WEIGHTS = {"acquire": 35, "validate": 30, "release": 10, "production": 25}
HASH = re.compile(r"^[0-9a-f]{64}$")


def canonical_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def assess_readiness(observation, expected_context):
    """Fail closed; Sunday start eligibility is separate from release readiness."""
    problems, pending = [], []
    context = {k: observation.get(k) for k in ("season", "competition_week", "profile_hash", "roster_hash")}
    for key, wanted in expected_context.items():
        if context.get(key) != wanted:
            problems.append("context_mismatch:" + key)
    if type(context["season"]) is not int or type(context["competition_week"]) is not int:
        problems.append("missing_season_or_competition_week")
    if not all(HASH.fullmatch(str(context[k])) for k in ("profile_hash", "roster_hash")):
        problems.append("missing_profile_or_roster_fingerprint")
    expected = observation.get("expected_players", [])
    players = observation.get("players", [])
    ids = [p.get("player_id") for p in players]
    if len(expected) != 30 or len(set(expected)) != 30:
        problems.append("expected_roster_must_have_30_unique_players")
    if len(ids) != 30 or len(set(ids)) != 30 or set(ids) != set(expected):
        problems.append("missing_extra_or_duplicate_player_coverage")
    by_id = {p.get("player_id"): p for p in players}
    if observation.get("source_errors"):
        problems.append("source_error")
    if observation.get("event_scope_verified") is not True:
        problems.append("relevant_event_scope_unknown")
    if observation.get("watchlist_scope_verified") is not True:
        problems.append("watched_result_scope_unknown")
    for player in players:
        if player.get("serve_verified") is not True or player.get("return_verified") is not True:
            problems.append("paired_TA_views_unverified:" + str(player.get("player_id")))
    events = observation.get("relevant_events", [])
    if not events and observation.get("no_relevant_events_confirmed") is not True:
        problems.append("no_evidenced_event_scope")
    seen_events, seen_results = set(), set()
    for event in events:
        event_id = event.get("event_id")
        if not event_id or event_id in seen_events:
            problems.append("missing_or_duplicate_event_identity")
        seen_events.add(event_id)
        if event.get("closure") == "ONGOING":
            pending.append("event_unfinished:" + str(event_id))
        elif event.get("closure") != "COMPLETE":
            problems.append("event_closure_unknown:" + str(event_id))
        for result in event.get("watched_results", []):
            result_id = result.get("result_id")
            key = (event_id, result_id)
            if not result_id or key in seen_results:
                problems.append("missing_or_duplicate_result_identity")
            seen_results.add(key)
            selected = result.get("selected_players", [])
            if not selected or len(set(selected)) != len(selected) or not set(selected) <= set(expected):
                problems.append("watched_result_selection_unknown")
            if result.get("status") == "UNFINISHED":
                pending.append("result_unfinished:" + str(result_id))
            elif result.get("status") != "COMPLETED":
                problems.append("result_completion_unknown:" + str(result_id))
            else:
                for player_id in selected:
                    player = by_id.get(player_id, {})
                    for view in ("serve_result_ids", "return_result_ids"):
                        if result_id not in player.get(view, []):
                            pending.append("TA_lag:" + str(player_id) + ":" + str(result_id) + ":" + view)
    ready = not problems and not pending
    cutoff = observation.get("cutoff_recheck_verified") is True
    te = observation.get("dated_TE_release_verified") is True
    return {
        "status": "UNKNOWN" if problems else "NOT_READY" if pending else "READY_TO_START",
        "ready_to_start": ready,
        "release_sources_ready": ready and cutoff and te,
        "release_waits": ([] if cutoff else ["cutoff_recheck"]) + ([] if te else ["dated_TE_release"]),
        "problems": sorted(set(problems)),
        "pending": sorted(set(pending)),
        "readiness_hash": canonical_hash(observation),
        "context": context,
    }


def queue_start_request(readiness, outbox):
    """Return a synthetic outbox entry once per season/week/type; never approve."""
    result = copy.deepcopy(outbox)
    if not readiness["ready_to_start"]:
        return None, result
    context = readiness["context"]
    key = f"{context['season']}:w{context['competition_week']}:START_APPROVAL_REQUEST"
    for item in result:
        if item["dedupe_key"] != key:
            continue
        # Keep the weekly delivery key/state, but refresh an unapproved request.
        # The notification opens the current run, not a permanently stale payload.
        if item["approval_status"] == "PENDING" and item["readiness_hash"] != readiness["readiness_hash"]:
            item.setdefault("superseded_request_ids", []).append(item["request_id"])
            item["request_id"] = canonical_hash([key, readiness["readiness_hash"]])[:24]
            item["readiness_hash"] = readiness["readiness_hash"]
            item["context"] = context
        return None, result  # No second notification is emitted for this week.
    item = {"dedupe_key": key, "request_id": canonical_hash([key, readiness["readiness_hash"]])[:24],
            "readiness_hash": readiness["readiness_hash"], "context": context,
            "delivery_status": "NOT_DELIVERED_PROTOTYPE", "approval_status": "PENDING"}
    result.append(item)
    return item, result


def accept_start_approval(command, request, readiness):
    """Pure validation demonstration, NOT authentication or a real permission grant.

    A deployed backend must authenticate the owner before constructing this command.
    """
    if command.get("owner_authenticated") is not True or command.get("approved") is not True:
        raise ValueError("explicit authenticated owner approval required")
    if request.get("approval_status") != "PENDING":
        raise ValueError("request is not pending")
    if not readiness["ready_to_start"]:
        raise ValueError("source readiness no longer holds")
    if command.get("request_id") != request["request_id"]:
        raise ValueError("request identity differs")
    if command.get("readiness_hash") != readiness["readiness_hash"] or request["readiness_hash"] != readiness["readiness_hash"]:
        raise ValueError("stale candidate; refresh and explicitly approve the current request")
    if request["context"] != readiness["context"]:
        raise ValueError("approval context differs")
    return {"request_id": request["request_id"], "readiness_hash": readiness["readiness_hash"],
            "approved": True, "mode": "SYNTHETIC_VALIDATION_ONLY"}


def calculate_progress(run):
    """Weighted verified units, never an estimate of time or model effort."""
    phases = run["phases"]
    if list(phases) != list(PHASE_WEIGHTS):
        raise ValueError("phases must preserve the four-phase order")
    percent, unknown, earlier_complete = Decimal(0), False, True
    for name, weight in PHASE_WEIGHTS.items():
        phase = phases[name]
        verified, total = phase["verified"], phase["total"]
        if type(verified) is not int or verified < 0 or type(phase["workset_revision"]) is not int or phase["workset_revision"] < 1:
            raise ValueError("invalid verified count or workset revision")
        if total is not None and (type(total) is not int or total < 1 or verified > total):
            raise ValueError("invalid known total")
        if phase["status"] not in {"pending", "running", "waiting", "failed", "completed"}:
            raise ValueError("invalid phase status")
        if not earlier_complete and (verified or phase["status"] != "pending"):
            raise ValueError("phase order barrier violated")
        if phase["status"] == "completed" and (total is None or verified != total):
            raise ValueError("completed phase lacks all verified units")
        if name == "production" and total is not None and verified == total and run.get("production_verified") is not True:
            raise ValueError("final production proof required before 100 percent")
        if total is None:
            if phase["status"] != "pending":
                unknown = True
        else:
            percent += Decimal(weight) * Decimal(verified) / Decimal(total)
        earlier_complete = earlier_complete and phase["status"] == "completed"
    completed = earlier_complete and run.get("production_verified") is True
    if percent == 100 and not completed:
        raise ValueError("100 percent requires completed, verified production")
    return {"percent": None if unknown else float(round(percent, 2)),
            "verified_floor_percent": float(round(percent, 2)), "indeterminate": unknown,
            "complete": completed, "basis": "weighted verified work units, not elapsed time"}


def revise_workset(run, phase_name, new_total, reason):
    """Explicit denominator change; no silent count reset or hidden percentage jump."""
    result = copy.deepcopy(run)
    phase = result["phases"][phase_name]
    if not reason.strip() or phase["status"] == "completed":
        raise ValueError("explain a revision before completing this phase")
    if type(new_total) is not int or new_total < max(1, phase["verified"]):
        raise ValueError("revised total cannot discard verified work")
    result.setdefault("workset_events", []).append({"phase": phase_name,
        "old_revision": phase["workset_revision"], "new_revision": phase["workset_revision"] + 1,
        "old_total": phase["total"], "new_total": new_total, "reason": reason})
    phase["total"] = new_total
    phase["workset_revision"] += 1
    result["progress"] = calculate_progress(result)
    return result


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_json", help="Synthetic normalized run fixture; no live reads")
    args = parser.parse_args()
    with open(args.run_json) as source:
        run = json.load(source)
    print(json.dumps(calculate_progress(run), indent=2))
