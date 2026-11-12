# First monitored weekend run

The first v2 run is prepared for **Sunday 15 November 2026**, targeting **Monday 16 November, competition week 39**. Native HEBDO history and the published week-38 baseline agree. Preparation is read-only with respect to Sheets, production and source sites; it does not authorize weekly writes or certify future results.

## Prepared implementation

The private run contains native sheet IDs for the 30 active selections and six operational tabs, the approved write profile, roster/scoring/transfer hashes, prior five-team totals, all six published baseline files, a 30-player paired-view worklist, an incomplete readiness template, checkpoint plan and actual PROGRESS.html. Nothing from that private packet is committed here.

The preparation command refuses conflicting prior totals, missing or archived native tabs, an existing target snapshot, skipped-week assumptions, changed prepared inputs and storage inside a Git checkout. Transfer display labels are joined through approved full identities rather than parsed as names. Both weekly rating reports and optional supplied UTR remain separate lanes.

Run from the repository root, supplying actual private paths:

    python3 tools/race_v2/weekend.py --run-dir PRIVATE_RUN --target-monday 2026-11-16 --context PRIVATE_CONTEXT --metadata NATIVE_METADATA_JSON --hebdo NATIVE_HEBDO_JSON --transfers NATIVE_TRANSFERS_JSON --baseline-dir VERIFIED_DATA_DIR --baseline-commit VERIFIED_COMMIT --scoring REVIEWED_SCORING_CONTRACT

The source inputs are native connector readbacks, not hand-written assertions. Reconcile the current GitHub commit and six baseline hashes before preparation. Recheck native roster/rules/transfer/profile bindings when Start is offered; if changed, preserve the prepared attempt and make a linked revision. A changed private profile is never silently rebound to a prior Start.

## Sunday and Monday sequence

| New York time | Work | Required outcome |
|---|---|---|
| Sunday 15 November, 18:00 | Resolve current relevant events and outstanding results for all 30 selections; inspect affected displayed TA pairs | READY, NOT_READY or UNKNOWN with primary evidence |
| Sunday, 21:00 | Recheck unresolved/changed source scope | Refresh a pending request without another push |
| Monday 16 November, 00:30 | Reconcile the exclusive midnight cutoff and actual completions | Continue the same approved run; never infer completion from tournament-start dates |
| Monday, 08:30 | Recheck dated TE publication and remaining gaps | Continue, or persist one consolidated attention item |

These checkpoints are prepared schedule definitions. They are not proof of unattended execution or iPhone delivery. Actual recurring tasks must remain paused until the source-access, state and phone pilots pass. The earlier phone pilot did not establish delivery; do not activate by treating a calendar setting as notification evidence. Manage real tasks with the supported automation action, not local cron files.

## Execution and approvals

1. GPT performs readiness reads and saves primary bytes, paired views, event closure evidence and their hashes. Populate a new observation from readiness-observation.template.json; unverified event scope and missing evidence must stay unknown. Record it through race_run.py readiness. Do not mark a whole season verified from a final-row probe.
2. Offer one weekly Start for this exact week/profile, including the optional UTR value/week field if still pending. An owner reply is required; opening a notification or preparing the packet does not approve writes. Direct manual Start remains available in this chat, separately from any push route.
3. After Start, GPT acquires, backs up once, applies bounded writes and independently reads back changes/history. Sunday inputs remain provisional until Monday cutoff and dated TE checks. Update actual work units and separate Elo/UTR lane states in the private runner.
4. GPT validates source truth and frozen outputs, seals the candidate and presents one concrete review for exact release approval. Exceptions and historical qualifications retain their meanings and require acceptance for this candidate.
5. GPT releases the approved six-file data branch, reads back all hashes and generates the compact Claude brief. Patrick passes that brief to Claude.
6. Claude builds, deploys and verifies the actual live release. Only the bound production receipt completes the bar at 100%. No email follows.

## Current limits

The run preparer and evidence runner are implemented and tested. The actual source acquisition, connector writes and browser verification remain GPT/Claude operations; this is not a new unattended scraper or hosted owner service. The source pilot and actual iPhone delivery are still open activation conditions. Until they pass, the prepared packet supports a monitored run, with honest pending states rather than a promise of automatic Sunday execution.
