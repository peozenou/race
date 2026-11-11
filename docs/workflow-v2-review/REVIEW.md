# THE RACE workflow v2 — historical review proposal (9 November 2026)

**Historical proposal, prepared 9 November and approved by Patrick on 10 November 2026.** The body below preserves the design reviewed at that time; proposal-era wording is not current installation or activation status. For the operating procedure, read [workflow v2](../weekly-workflow.md) and the [approved write profile](../standard-write-profile.md). See [implementation/activation status](activation-plan.json) and the [notification pilot](../notification-pilot.md) for the actual deployment boundary. Schedules remain paused until the documented source and iPhone pilot passes.

New weekly runs end at the verified live dashboard. The email task is removed. The already saved week-38 draft and historical records remain untouched.

## Four visible phases

| Phase | Owner | Progress weight | Verified outcome |
|---|---|---:|---|
| 1. Collect | GPT and source adapters | 35% | Complete selected-source coverage, typed frozen evidence and dated TE reports |
| 2. Validate and review | GPT; Patrick clears release | 30% | Source comparison, protected-history proof and approval of the exact candidate hash |
| 3. Release and hand over | GPT | 10% | One data-only commit, six remote hashes and a compact Claude handoff |
| 4. Publish and verify | Claude; GPT records evidence | 25% | Deployment, six live hashes, page version, totals and browser checks |

Sunday readiness monitoring precedes the update and is outside its progress denominator. Percentages represent completed verified work, not elapsed time. Waiting for a source, approval or Claude is shown explicitly. Only verified production reaches 100%.

The exact proposed routine operations and exceptions are in [standard-profile.md](standard-profile.md).

## Two routine decisions

1. **Start this week's update.** Binds the week and approved profile version, authorizing in-scope acquisition, verified backups, bounded TA/TE/summary writes and readback. Exact diffs are still saved; routine TA/TE/summary writes do not each need another permission request.
2. **Approve this exact release.** A concise review shows all five totals/deltas, source dates, changes, exclusions, qualifications and candidate hash. Approval authorizes the bounded release branch and prepared Claude handoff.

Patrick must still explicitly invoke Claude with today's interfaces. Combining release approval with opening the handoff reduces navigation; it does not implement automatic cross-assistant dispatch.

New roster/scoring decisions, unresolved transfer baselines, historical rewrites, expanded schema/destination or changed exceptions require a specific decision. Routine import recovery within the profile is authorized only when the existing formula scope and approved values are preserved. Historical qualifications retain their exact scope and current-week acceptance.

## Sunday watch and iPhone notification

Proposed checks: **Sunday 18:00 and 21:00; Monday 00:30 and 08:30, America/New_York**. The Monday checks cover late matches, TA lag and publication delays. These are bounded checkpoints, not continuous or immediate detection. Manual Check now remains available.

- Resolve the 30-player roster, competition week, prior verified capture and relevant event/match watchlist. Include Challenger, qualifying, relevant ITF and team competition; the major-event calendar alone is insufficient.
- Probe event closure and expected completed results cheaply, then inspect affected TA displayed Serve/Return views. Reuse unaffected evidence only with complete dependency equality.
- READY requires complete roster/watchlist reconciliation. A prominent ATP final alone is insufficient. Missing expected matches, unfinished play, unpaired views, source errors or uncertain completion remain NOT_READY or UNKNOWN.
- Emit one actionable request per competition week: **TA results are ready for week N. Start the weekly update?** Bind its evidence hash. Notification delivery or tapping never approves Start.
- Sunday Start permits provisional acquisition. Monday midnight cutoff and the actual dated TE report remain separate conditions; resume the same run without another Start request.
- Persist a private notification outbox keyed by season/week/event type. Retries/restarts must not duplicate delivery. Stop the week's alerts after Start or completion. If still incomplete at the last checkpoint, create one consolidated attention item with the missing evidence and resume action.

**Not yet operational:** no matching schedule was found. Proposed automations remain inactive suggestions. Local execution needs an available computer/app and a verified unattended TA adapter. Desktop/inbox notification support does not prove iPhone delivery. Activation requires a real phone test for permission, locked/background delivery, deduplication and the correct approval page. If that route fails, build and test Home Screen Web Push before claiming iPhone notification support. Quiet not-ready checks must be tested against the host's notification behavior; prompt wording alone cannot suppress platform notifications.

## Freeze release authority; separate LIVE health

Maintain four distinct domains: acquisition health, mutable candidate, immutable approved release, verified production. Seal source manifests, frozen export cells, roster/rules/transfers/cutoff, independent audit and six dataset hashes into a release snapshot.

Before writes and sealing, verify the bounded live prestate and protected history. Reuse checks only with all their dependency fingerprints intact. After approval, verify public data/production against the immutable commit and hashes.

A later LIVE IMPORTHTML failure is a **maintenance warning**, not grounds to revoke an unchanged frozen release or redo all its gates. A real correction to frozen inputs, rules or released values creates a linked revision and renewed affected approval. Never silently rebind.

Full history protection remains required at baseline and after structural/history changes. Routine append-only weeks prove protected baseline plus precise deltas once, retain hashes and avoid transferring the same historical grids at every handoff. Reuse is not a substitute for primary-source truth.

## Efficiency improvements to approve

| Change | Defensible improvement | Measure after rollout |
|---|---|---|
| Seven visible tasks to four phases | Three fewer visible stages | Actions and waiting time |
| Email removed | No Gmail search, recipient lookup, MIME construction, save or readback | Zero weekly Gmail calls |
| Profile plus weekly Start | Routine writes no longer each need permission | Target two routine approval decisions; exceptions separately |
| Incremental TA watchlist | Recapture changed pairs; retain roster-wide completeness | Views required versus a 60-view baseline |
| Canonical typed evidence and scripts | No repeated model parsing or bespoke weekly exporters/receipts | Requests, bytes, script/model calls and tokens if exposed |
| Dependency-based verification | Reuse unchanged checks and read only affected dependencies | Check reuse ratio and history cells read |
| Compact Claude package | Six files, manifest, changes and checks, rather than acquisition history | Claude input size and active runtime |
| Frozen release separate from LIVE | Avoid reopening finished production for an import outage | Unnecessary rework/revalidation count |

No percentage token/time/cost savings are claimed. Establish a baseline and compare comparable weeks. Use one GPT coordinator by default; deterministic scripts parse, calculate, compare and record progress. GPT reasons about ambiguous identity/cutoff/scoring exceptions; Claude owns dashboard work. Parallelize only when the gain exceeds overhead and source limits permit it.

## One status contract and future iPhone clients

The accompanying progress page is a synthetic interactive preview, not a live weekly monitor. A private status store will drive chat and the owner app from verified events: run/profile ID, phase/state, completed/required units, source dates, last-observed time, next action and exact candidate/release identity.

**Friends:** begin with the existing public dashboard as a read-only Home Screen web app. **Patrick:** use a separate authenticated owner view for readiness, Start, approval and progress. Authorization belongs on the private backend; hiding buttons is insufficient.

Commands bind run ID, profile version, expected state/version, candidate hash and idempotency key. Reject stale/replayed approval and concurrent runs. Keep write credentials, model/API keys, approval records, push subscriptions and private source data off public JavaScript and GitHub Pages. Later SwiftUI clients can use the same contracts.

A Home Screen web app avoids App Store membership fees. Installed iPhone/iPad web apps support Web Push from iOS/iPadOS 16.4 after user permission. Free native Personal Team testing needs seven-day reprovisioning; Apple lists normal distribution membership at USD99/year. Free client distribution does not promise free model execution, private backend or always-on hosting.

## Implementation after approval

1. Freeze the design/profile version and remove Gmail only for new runs; preserve historical ledgers and the saved draft.
2. Install staged Race skills and update repository README, workflow/data/Claude runbooks and shared contracts. Keep Elo/private-statistics lanes independent.
3. Add a new-schema runner adapter and private progress/readiness store. Preserve schema-3 records; do not renumber or declare old runs incomplete.
4. Reuse working capture/parser/validator/build helpers; replace ad hoc weekly glue with one tested pipeline and handoff generator.
5. Test offline replay, no-write current-source readiness, source lag/cutoff cases, backups/readback, stale approvals and actual iPhone delivery. Activate schedules only after tests pass.
6. Pilot the next new week, measure resources and approvals, then develop public PWA, private owner controls and optional native clients.

Approval permits that implementation and publication of staged documentation. It does not authorize changing an existing released dataset, starting a weekly update, sending the saved email, paid Apple enrollment or exposing private state.

## Review artifacts

- Quarto source, HTML and PDF: process.qmd, process.html, process.pdf.
- Interactive progress concept: progress.html.
- Offline contract prototype: workflow_state.py and test_workflow_state.py.
- Client contracts/examples: run-status.schema.json and examples/.
- Proposed skill entrypoints/shared contract: proposed-skills/ and proposed-shared-contract.md.
- Publication/activation scope: activation-plan.json; official capability references: sources.md.

These are local uncommitted review artifacts in the repository checkout. Installed skills and production guidelines have not been replaced; GitHub publication follows approval.
