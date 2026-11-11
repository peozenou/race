---
name: race-check-ready
description: "Run the proposed low-cost Sunday/Monday Race readiness check and notify Patrick once when TA coverage permits offering weekly Start approval."
---

# Race v2 readiness watcher — staged proposal

Read the [proposed shared contract](../../proposed-shared-contract.md). This prephase is read-only and does not launch an update. Proposed slots are Sunday 18:00/21:00 and Monday 00:30/08:30 America/New_York. Activation requires Patrick's revision approval plus a successful unattended source-access/state/notification pilot; no active scheduler or iPhone delivery is asserted by this file.

Load the approved roster/event watchlist and persisted week state. Use lightweight changed-result probes first. Confirm relevant completed final results are actually displayed on TA and selected-player/event coverage has no unfinished, missing, blocked or ambiguous item. A prominent ATP final alone is insufficient. Fail closed to NOT_READY/UNKNOWN and respect cooldown/backoff; do not run 60 full-season captures at every poll.

Persist source identities, actual observations and a season/week readiness digest. When READY and no weekly Start has been approved or notified, emit one weekly readiness notification asking Patrick to approve Start under the versioned bounded write profile. Record notification idempotency. Delivery or a preselected button is not approval. Source changes update evidence without repeated readiness prompts.

Sunday readiness means safe to begin provisional acquisition. Monday cutoff and actual dated TE publication remain separate run dependencies. After explicit Start, later scheduled slots resume that same run as authorized sources become ready; do not ask for another Start. Stop at a defined source block and report truthful state, not fabricated completion.
