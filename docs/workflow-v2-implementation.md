# Workflow v2 implementation status

10 November 2026: the design, bounded write profile and checkpoint times are approved. The revised instructions and runner are implemented and installed. **Notification activation remains pending the real pilot.**

## Delivered

- Thirteen installed skill entrypoints cover Race, readiness, independent Elo/yElo and private UTR, with the old email entrypoint restricted to explicit legacy work.
- Four visible phases replace seven routine steps. The two ordinary decisions are scoped Start and approval of the exact release. Patrick still passes the prepared brief to Claude.
- The standard-library runner records checksummed private state, immutable evidence, separate approvals, dedicated data releases and bound production receipts. It generates the compact Claude brief and a private progress page from actual run state.
- README and workflow/data/Claude guidelines describe the new operating procedure. The approved profile and migration guide define routine writes, exceptions and historical protection.
- The Quarto reference deck is available as [HTML](workflow-v2-review/process.html), [PDF](workflow-v2-review/process.pdf) and editable [source](workflow-v2-review/process.qmd). It contains 15 slides/pages.

The installed package was backed up and independently read back: 52 supplied files match, and 28 other existing files were preserved. Source helpers and historical ledgers were not replaced. Private installation/approval evidence remains outside this repository.

## Validation performed

Twenty-seven runner tests pass, including an independent review of stale/replayed approvals, Sunday cutoff protection, per-player TA evidence, reserved approval progress, immutable releases, maintenance health and bound live-production evidence. Seventeen review-prototype tests also pass. All thirteen skill frontmatters/interface files and relative links were checked. The regenerated HTML has no browser exceptions; all fifteen PDF pages were visually inspected.

These are code and artifact checks. They do not prove live unattended acquisition, human authentication or phone delivery. The public progress demonstration remains synthetic; real weekly progress is generated privately by the installed runner.

## Pilot boundary

| Check | Observed state |
|---|---|
| Current TA displayed Serve/Return access | Passed for one selected-player pair; matching displayed result identity |
| Complete unattended roster/event readiness | Pending; one pair is insufficient |
| Private queue restart, refresh and stale/replay handling | Passed in isolated tests |
| iPhone account/device connection and locked/background delivery | Pending |
| Correct-run opening and explicit owner action | Real device test pending |
| Platform quiet checks and duplicate-notification behavior | Real delivery test pending |
| Recurring schedule activation | Off |

The approved checkpoints remain Sunday 18:00/21:00 and Monday 00:30/08:30 America/New_York. Earlier paused automation suggestions were review cards, not active schedules. Complete the [notification pilot](notification-pilot.md), record the supported route and independently read back schedule configuration before activation. Notification opening never approves Start.

## Efficiency and future apps

Routine per-module permission loops and weekly email preparation are removed. Reusable parsers/checks, dependency-verified source reuse, bounded recovery, one weekly backup and one generated handoff reduce repeated work. Measure source requests, model usage and retries on comparable runs before claiming numerical savings.

Weekly complete Elo/yElo checks and manually supplied private UTR remain independent of Race progress. Missing UTR or unchanged ratings do not hold Race. Future owner controls can use the same versioned state and approval contracts through a private authenticated service; friends' mobile views read only approved public releases. No owner backend, push service or Apple app is deployed by this change.

This workflow release changes instructions, tooling and reference artifacts. Current weekly datasets, dashboard source/page, history, tutorial and existing email drafts are outside its mutation scope.
