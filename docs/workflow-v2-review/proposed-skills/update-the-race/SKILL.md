---
name: update-the-race
description: "Coordinate the proposed four-phase Race workflow after approval: GPT acquires and validates, Patrick approves the candidate, and Claude publishes and verifies."
---

# Race v2 coordinator — staged proposal

Read the [proposed shared contract](../../proposed-shared-contract.md) and exact run state. This package is not active until Patrick approves and installation validation passes. Preserve legacy run histories.

A readiness watcher precedes four phases: Acquire (GPT,35%), Validate and review (GPT,30%), Release and hand over (GPT,10%), Publish and verify (Claude,25%). New runs end at verified live production. There is no Gmail phase; leave existing drafts untouched.

Offer two routine decisions: Start under the versioned bounded write profile, then approval of the exact source-audited candidate hash. Continue authorized work without per-module approvals. Ask only about an out-of-profile change or unresolved material exception. Patrick still invokes Claude explicitly using the prepared handoff; do not claim a background cross-assistant service exists.

Resolve one run/roster/rules/cutoff and reuse it. Sunday acquisition remains provisional until the Monday cutoff and actual TE publication checks pass; source waits resume the same authorized run. Show one weighted verified-work progress bar, current owner, last check, blocker and next action. Do not represent waiting time as completion.

Seal an immutable release snapshot. Later volatile LIVE failures affect acquisition health, not an unchanged approved release or production result. Real frozen input/rule/output corrections require a linked revision and renewed affected approval. Route acquisition/summary/audit/export work to the compatible modules below; do not load irrelevant references. Elo/Tiago remain independent.
