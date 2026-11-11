# Weekly update workflow v2

**Approved 10 November 2026; applies to new runs.** Four visible phases replace the former seven-step routine. New runs end at verified live production. Preserve legacy ledgers, releases and existing email drafts; do not renumber historical evidence or create a new email task.

## Phases and decisions

| Phase | Owner and modules | Completion | Weight |
|---|---|---|---:|
| Collect | GPT: TA/TE acquisition and operational inputs | Primary evidence, cutoff/source coverage, bounded Sheet writes/readback | 35% |
| Validate and review | GPT summary/audit; Patrick release decision | Independent source/protection checks; exact candidate approved | 30% |
| Release and hand over | GPT export | One data-only release, six remote hashes and compact handoff | 10% |
| Publish and verify | Claude; GPT records returned evidence | Actual deployment/live hashes/version/totals and UI checks | 25% |

1. **Start:** Patrick names the week and approved profile version. This authorizes routine acquisition, verified backups, exact bounded TA/TE/summary writes and readback under the [write profile](standard-write-profile.md). Generate/save diffs without asking separately for each unchanged submodule.
2. **Approve release:** Patrick clears the concrete independent review and exact candidate hash, including explicit qualifications. Only that candidate can be released.

A changed roster/rule/transfer baseline, new material exception, historical rewrite or expanded schema/destination needs its own concrete decision. A Start, a source-ready alert or a model's PASS is not final release approval. Conversely, do not invent extra permission gates for listed routine operations already authorized by Start.

Patrick still passes the generated handoff to Claude. Handoff preparation is not automatic cross-assistant messaging or proof of production. See [Claude production](claude-dashboard-production.md).

## Contributors and handoff

GPT acquires primary sources, updates operational Sheets, independently verifies source truth and internal coherence, maintains private evidence/progress and exports the cleared six-file release. Claude reads current HEAD and that exact release, makes only release-driven dashboard changes, builds, publishes and verifies live. Patrick makes the two routine decisions and any consequential out-of-profile decisions.

Both contributors preserve concurrent repository work. A dashboard-side data/rule discrepancy returns to the owning data/audit work; it is not silently patched in presentation code. Detailed approvals, private fingerprints and junior data stay outside public handoff notes.

## Readiness watch, Sunday and Monday

Approved checkpoints: **Sunday 18:00/21:00 and Monday 00:30/08:30 America/New_York**. These are bounded checks, not continuous observation or a promised TA publication time. Manual Check now remains available.

Resolve the 30-player roster, competition week, prior verified source state and relevant event/match watchlist. Include Challenger, qualifying, relevant ITF and team competition. Cheap closure/result probes precede affected-player displayed Serve/Return checks. All roster/watchlist coverage must be reconciled; a headline ATP final alone is insufficient. Missing expected results, unpaired views, unfinished play, source blocks and uncertain completion remain NOT_READY or UNKNOWN.

Readiness offers **Start**, not release. Sunday acquisition is provisional. On Monday verify the exclusive completed-match cutoff and source updates, then wait for the actual dated TE ranking publication as needed. Resume the same authorized run without another Start decision. Event-start dates are not completion timestamps. No older publication is relabeled fresh; a proposed older-source carry-forward is an explicit release exception.

Emit at most one weekly actionable Start request, persisted privately by season/week/event type. A notification/tap is not approval. If readiness evidence changes before approval, refresh/supersede the pending payload and reject the stale request without another push. Stop that week's readiness alerts after Start/completion. At the final unresolved checkpoint, record one consolidated attention item and manual resume route rather than looping identical messages.

**Activation remains pending pilot.** The scheduler needs verified unattended source access, private state and an actual iPhone delivery/permission/deduplication test. A desktop/inbox alert is not proof of phone delivery. See [pilot acceptance](notification-pilot.md).

## Evidence, dates and scope

Resolve once: season, target Monday, competition week from workbook history (not ISO), exclusive Monday 00:00 America/New_York cutoff, workbook timezone, roster/identity and scoring/transfer versions. Keep publication, tournament-start, actual completion, capture and ingestion times separate.

Persist primary bytes and hashes before normalization. TA displayed evidence owns B:X inputs; hidden raw tables must not fill visible blanks. Preserve completed retirements/walkovers even where stats are missing; exclude unfinished/postcutoff rows explicitly. TE pagination/lookups must cover actual roster identities including required tails beyond a top-500 boundary. Errors/missing joins are not zero.

Resolve TEAMS or its real equivalent before reporting it. Use one verified weekly snapshot across HEBDO, JOUEURS, BILAN, TEAMS and derived blocks. Reconcile 30 player paths, +5 contest credits, incoming guards, retained outgoing credits and five Race/Duels/adjustment/Total paths without double counting.

## Lean verification and release authority

Maintain acquisition health, mutable candidate revision, immutable approved release and production as distinct domains. Reuse raw/parsed evidence and check results only when every source/parser/roster/rule/cutoff/protected-state dependency matches. Verify changed player pairs and retain complete roster coverage. Source truth is independent of a candidate matching its own payload.

Establish a full protected-history baseline initially and after structural/history changes. Routine weeks prove that baseline plus verified bounded deltas before sealing; use a full check whenever dependency coverage is insufficient. Do not repeatedly reread every historical grid at unaffected handoffs.

Seal source manifests, frozen operational/export-value scope, roster/rules/transfers/cutoff, audit checks/exceptions and six candidate dataset hashes. Review includes five totals/deltas, source dates, change/exclusion counts, backup evidence, holds and proposed public scope. Required FAIL/NOT_CHECKED/BLOCKED cannot earn clearance; bounded qualifications name their effect and are accepted for this exact release.

After approval, the frozen snapshot and immutable release commit/hashes are authoritative. A later LIVE IMPORTHTML failure is maintenance health only and does not erase unchanged approved/released work. In-profile one-attempt recovery is permitted with backup/prestate and exact recovered-value proof. A real frozen input/rule/output correction creates a linked revision and renewed affected approval; never silently rebind.

## Progress, runner and recovery

Use the [v2 runner](../tools/race_v2/README.md) for private checksummed state, evidence links, Start/release approval, immutable sealing, release/production binding and append-only events. Connector/source/write actions remain skills-owned; the runner does not authenticate a human or certify source truth from a boolean alone.

One progress view shows four phase weights 35/30/10/25, verified/required work units, current owner, source freshness, last observed time, exact blocker and next action. It is not an elapsed-time estimate. Unknown work totals remain indeterminate; a changed denominator requires an explicit workset revision. Approval is a work barrier; only verified production reaches 100%.

Use module names for new work rather than interpreting old step numbers as new phases. A request for one module ends at its verified outcome. Status is read-only; Continue resumes the exact identified run. If several runs are unresolved, resolve the ambiguity rather than choosing by folder timestamp.

Measure source requests/captures/bytes, retries, check reuse, writes/backups, model calls/tokens when available, approval decisions and active/wait times. No percentage token/time/cost saving is promised before comparable weeks are observed.

## Independent weekly lanes

**Elo + yElo:** check both complete TA reports weekly, preferably with the Sunday readiness work. Preserve each actual report date, verify all rows/fields independently and append a new extraction-date pair only when advanced. A verified unchanged pair is NO_SOURCE_ADVANCE with zero writes. A mixed-date pair is explicit, never fabricated. The Race candidate selects one frozen rating pair; a later independent update does not alter an already sealed release.

**Tiago UTR:** consolidate the request for the weekly user-supplied value/week meaning into the owner intake only if not already provided. A value is never scraped or carried forward as a new observation. Back up, deduplicate/upsert with provenance, read back protected private history and update the private dashboard. Exact measurement time/rating type stay unknown unless supplied. No user input means pending, not zero.

Consolidate one optional pending UTR value/week field into the Start request rather than sending another intake ping. A configured independent Elo append may proceed under Start only when its own private binding/scope is included in that profile; otherwise the scheduled check may acquire/stage read-only. Reuse direct same-scope authorization already given.

Show Elo, UTR and MatchTrack separately beneath the Race bar, outside its denominator. Missing UTR and unchanged/delayed independent Elo do not block Race. MatchTrack remains a separately requested genuine-export workflow. No private observations or junior data enter this repository, public dashboard or source bundles.

## Legacy migration

Schema-3 seven-step ledgers and older records remain immutable historical evidence. Use a read-only compatibility view; do not rewrite closed runs or make email absence a new failure. New runs use the v2 state contract and stop at phase 4. Preserve existing drafts unchanged; the deprecated email skill is explicit legacy-only and never automatically invoked. No installation or process approval authorizes sending mail.
