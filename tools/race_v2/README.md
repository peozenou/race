# Four-phase private Race runner

This standard-library package implements the approved four-phase evidence/state runner. It does not scrape tennis sites, call Google Sheets/GitHub, operate Claude, authenticate Patrick or deliver a notification. The operating skills obtain real evidence through connected tools and the existing source/build helpers; the runner checks that saved evidence is complete, unchanged and bound to the same decision/release.

Run directories contain private source/approval evidence and **must be outside the public repository**. Do not commit the generated configuration, state, status page, outbox, approval files, source snapshots or screenshots.

Use weekend.py to prepare the next private run from native metadata, HEBDO and transfer reads, the approved profile/registry, existing scoring contract and six published baseline files. See [weekend preparation](https://github.com/peozenou/race/blob/main/docs/weekend-run.md). It derives the competition week from reconciled league history, binds native sheet IDs, creates the actual private progress page and source worklist, and grants no Start approval. Identical preparation is idempotent; changed inputs require a linked revision.

## What is implemented

- Four ordered phases, weighted 35/30/10/25; verified work units, source waits and the approval unit are explicit.
- Separate profile/week Start and exact frozen-candidate release approval, with expected state revision and consumed command IDs.
- Locked, atomic, checksummed state, a hash-linked append-only event log and immutable receipt/artifact dependencies.
- Candidate sealing over frozen source/value/rule/roster/cutoff/audit dependencies, source-derived expected tables and six actual JSON files.
- Every candidate field compared with independently prepared expected tables, plus the existing six-file schema/grain/identity/date/totals checker.
- Dedicated-branch release checks against all six saved GitHub readback bodies, remote ref metadata and one generated Claude handoff.
- Claude production binding to release/data/dashboard identity, actual live data bodies, live/build page equality, UI metadata/checks, deployment and timezone-aware observations.
- Actual private PROGRESS.html and run-status.json on every checkpoint. The page refreshes stored state every30seconds; it is not itself a source poller.
- Normalized readiness evaluation grounded in actual saved displayed TA captures, with complete roster coverage, per-player result keys, linked watchlist/closure evidence and fail-closed partial coverage.
- One weekly queued Start request, refreshed pending payloads without a second notification, and separate delivery evidence. Delivery never authorizes Start.
- Independent Elo, Tiago UTR and MatchTrack status lines, which do not change the Race progress denominator.
- Read-only display of historical schema-2/3 seven-step ledgers, without rewriting their numbering.

These checks cannot prove that a caller really fetched a URL or that a text file came from a human. The operating skill must inspect authentic source, user and provider evidence. A synthetic fixture passing the tests is not a live acquisition or notification pilot. An owner web app still needs a trusted authenticated backend; never expose this CLI as an unauthenticated public service.

## Main commands

From the repository root, use python3 tools/race_v2/race_run.py followed by the command. Installed skills can use the same directory as their bundled scripts/race_v2/ package.

    init --run-dir PRIVATE_RUN --config PRIVATE_CONFIG
    status --run-dir PRIVATE_RUN
    status --run-dir PRIVATE_RUN --json
    status --run-dir PRIVATE_RUN --html PROGRESS.html

All evidence paths below are relative to PRIVATE_RUN and require containment there. A supplied absolute path is accepted only if it resolves inside that same private run. A lock must not be removed until its PID is inspected.

### Configuration

Provide season; target_monday; competition_week and competition_week_evidence; exclusive cutoff at Monday00:00 America/New_York; workflow_timezone; profile_version/profile_file; roster_version/roster_file; scoring_version; repository; production_branch; canonical HTTPS dashboard_url. An optional run_id distinguishes a correction revision.

The CSV registry contains active, team, sheet_name and tennis_abstract_slug. There must be30 unique active source/sheet identities and six players for each of PAT/DOC/CHAN/CHEF/JULES. Workbook identifiers and the exact bounded write profile belong in the private profile/configuration. Existing config/profile/roster artifacts are hashed when the run is initialized.

### Weekly Start

First display status and use its current revision. Preserve Patrick's actual instruction in a private text file. Do not synthesize an approval from a notification or arbitrary file contents.

For an explicit directly requested update, separate from a notification:

    start --run-dir PRIVATE_RUN --manual --human-evidence approvals/start.txt --profile-sha256 PROFILE_HASH --expected-revision N --command-id UNIQUE_ID

For a readiness request:

    start --run-dir PRIVATE_RUN --request-id REQUEST_ID --readiness-sha256 READINESS_HASH --human-evidence approvals/start.txt --profile-sha256 PROFILE_HASH --expected-revision N --command-id UNIQUE_ID

Request-based Start must match the current ready, pending request and current evidence hash. A stale notification may open the run, but its old payload cannot authorize an update. Explicit manual Start can begin provisional acquisition before readiness completes; source/cutoff/release gates still apply. A recorded Start is reused when source waits resume; do not ask for another one.

### Acquisition and validation receipts

    record --run-dir PRIVATE_RUN --phase acquire --receipt receipts/acquire.json
    record --run-dir PRIVATE_RUN --phase validate --receipt receipts/validate.json

A receipt has run_id, summary, state, units with verified and total, and nonempty dependencies. Each dependency is an object with path and the original sha256. Changing a hash to match altered bytes is a new input, not a valid reused check.

Checkpoint states running, waiting_source and blocked preserve partial verified units. Unknown total is null, which renders indeterminate progress. No preapproval validation state may consume its final approval unit. Use a linked revision if the declared workset changes rather than silently changing its denominator.

Verified acquisition uses state=verified and all units complete. It must include active_players=30 and te_joins=60 in source_counts, source_publication_dates with actual race/atp dates, and a timezone-aware cutoff_observed_at at or after the configured cutoff and no later than now. Future source dates are rejected. An older selected TE date needs a source_date_exceptions record with id, source, source_date and impact, and a QUALIFIED te-source check; that same exception must appear in the sealed review.

Validation uses state=review_ready and verified=total-1. The last unit is reserved for Patrick's exact release decision.

Required acquisition check IDs:

- ta-source
- te-source
- cutoff
- sheet-readback
- history-protection

Required validation check IDs:

- ta-source-equality
- te-joins
- scoring
- team-paths
- history-protection
- schema
- export-field-reconciliation

Each check has id, status PASS or QUALIFIED, evidence paths covered by the hashed dependencies, and counts with checked greater than zero, missing=0 and unexamined=0. A qualification names its bounded impact. These are check-level comparisons supplied by real source/check adapters; merely setting PASS is not a source audit.

### Seal and approve the candidate

    seal --run-dir PRIVATE_RUN --manifest candidate/manifest.json
    approve-release --run-dir PRIVATE_RUN --candidate-sha256 CANDIDATE_HASH --human-evidence approvals/release.txt --expected-revision N --command-id UNIQUE_ID

The manifest contains run_id, release_id, frozen_scope, exceptions, frozen_dependencies, data_files, expected_tables_file and expected_contract_file.

- Every frozen dependency has path, sha256, domain=frozen and a role. Required roles are primary_source, frozen_values, roster, rules, cutoff and independent_audit. Volatile LIVE health is forbidden as a sealed dependency.
- data_files maps exactly hebdo/joueurs/players/matches/calendar/team_colors to their existing named JSON files in one data directory.
- expected_tables_file is independently prepared from primary/frozen inputs and contains all six exact tables. It cannot point to a candidate data file. Every exported field is compared.
- expected_contract_file uses the contract of check_dashboard.py: target week/date, five teams, active/archived/published/current-contribution sets, expected rows/columns, selected source dates and independently reconciled five totals. field_reconciliation_passed is supported only by the separate exact expected-table comparison and real source audit evidence.

Sealing freezes this state and changes validation to waiting_approval. It does not approve it. Candidate changes require a distinct linked run/revision and renewed affected approval.

### Data release and generated Claude handoff

The skill first publishes one coherent dedicated-branch data commit through GitHub, saves all six actual readback bodies and the current remote branch/commit evidence, then prepares a release receipt.

The receipt includes run_id, summary, dependencies, checks github-readback/concurrency/release-scope, release_id, candidate_sha256, data_commit_sha, data_sha256, release_branch, readback_files and readback_metadata_file. Metadata has commit_sha and branch_head_sha, both equal to the actual immutable data commit. The branch must differ from production_branch.

    handoff --run-dir PRIVATE_RUN --receipt receipts/release.json --output CLAUDE_HANDOFF.md
    release --run-dir PRIVATE_RUN --receipt receipts/release.json

The handoff command generates a bounded brief from the cleared manifest, source contract, totals, six hashes and exact readback identity. It excludes private candidate/configuration/approval paths and does not contact Claude. Set the receipt's handoff_file to this generated output before the release command. A changed handoff needs a new versioned output filename.

The generated brief is stored privately and can be passed by Patrick to Claude. The public production note must omit private approval and candidate/workbook fingerprints. Complete release reaches75% and awaits Claude. A local staged bundle cannot reach this state.

### Claude production

    production --run-dir PRIVATE_RUN --receipt receipts/production.json

Required receipt fields:

- owner=Claude; production_status=LIVE_DASHBOARD_VERIFIED
- release_id, data_commit_sha, candidate_sha256 matching the approved release
- actual dashboard_commit_sha, canonical dashboard_url, live_week
- equal nonempty build_data_version/live_data_version
- live_data_sha256 and live_data_files for all six actual served bodies
- live_verified_at, timezone-aware and not in the future
- live_page_file, built_page_file and live_page_metadata_file
- ui_evidence_file, claude_completion_evidence_file, deployment_evidence_file
- hashed dependencies and checks deployment/live-hashes/live-page/browser-ui

The saved built page and canonical live page must be byte-identical and contain the recorded data-version meta tag. Live-page metadata contains url, http_status=200, sha256 and observed_at.

UI evidence contains dashboard_url, dashboard_commit_sha, data_version, week, observed_at, covered_scopes, failed=0, console_errors=0 and nonempty check-level results whose pass values are true. Required coverage: filters, tables, history, transfers, source-dates, mobile and console.

Claude completion must agree with the receipt's owner/status/release/data/dashboard/version fields. Deployment evidence has status=success, exact commit_sha, provider url and completed_at. Page/UI observations must follow deployment and precede or equal the final live verification timestamp. The skill must inspect the actual provider and browser evidence, not manufacture these fields. Only this verified outcome reaches100%.

### LIVE health, revisions and independent lanes

    health --run-dir PRIVATE_RUN --domain LIVE --evidence health/live.json
    revise --run-dir PRIVATE_RUN --new-run-dir NEW_PRIVATE_RUN --config NEW_PRIVATE_CONFIG --reason "Changed frozen source values"
    lane --run-dir PRIVATE_RUN --name elo --receipt independent/elo.json

A health report has status PASS/WARNING/FAIL/UNKNOWN and a concrete summary. It never revokes an unchanged approved release or production result. A real frozen input/rule/output correction needs a separate revision directory and explicit reason; the parent records remain untouched.

Independent lane names are elo, tiago-utr and tiago-matchtrack. Receipt states are pending, waiting_input, running, verified, no_source_advance or blocked, with summary and hashed dependencies. Lane status does not increase or block Race progress. Weekly Elo/yElo checks and Patrick-supplied UTR remain independently triggered/scheduled by their own approved policies; the Race readiness command does not scrape UTR.

Status verifies saved evidence. If an immutable artifact changed, the current bar becomes indeterminate with an evidence warning and the last recorded percent retained as history. It does not continue to claim fresh100%. A mutable LIVE outage alone does not cause that downgrade.

## Readiness and notification outbox

    readiness --run-dir PRIVATE_RUN --observation readiness/observation.json
    request-start --run-dir PRIVATE_RUN
    acknowledge-notification --run-dir PRIVATE_RUN --request-id REQUEST_ID --evidence readiness/delivery.json

The observation contains season, competition_week, profile_hash, roster_hash, expected_players in the approved registry order, players, relevant_events, evidence, watchlist_evidence, event_scope_verified, watchlist_scope_verified and source_errors. Evidence is a nonempty list of actual captured primary artifacts with path and original sha256.

Each player has player_id equal to the TA slug and serve_evidence_path/return_evidence_path. Existing capture_ta_display JSON is accepted: correct TA URL/player, view_requested, actual matches table, season/filter checks and displayed rows. The runner derives completed result presence from the saved rows rather than trusting normalized serve_verified/return_verified booleans.

Each event records event_id, closure, closure_evidence and watched_results. Linked source evidence must support event/watchlist scope. Each watched result has result_id, status, selected_players and ta_keys_by_player. A player's six-item TA key is Date, Tournament, Surface, Rd, displayed result, Score, in that order. Both perspectives of a selected-player contest usually have different displayed names/country/seeding; give each player's exact key. A single ta_key is accepted only for a one-selected-player result.

Cutoff and dated TE readiness remain separate fields. Complete TA readiness can offer Start on Sunday but cannot certify phase1 before the actual cutoff recheck/selected TE publication. A partial/source-blocked pilot returns UNKNOWN and queues no READY request.

The outbox key is season/week/START_APPROVAL_REQUEST. Changed ready evidence refreshes a pending request without another delivery event; old request/hash approval fails. The runner never sends a push. Delivery evidence has request_id and delivery_status DELIVERED/FAILED/UNKNOWN. Acknowledging delivery does not grant Start. The notification pilot and Patrick's actual iPhone confirmation remain mandatory before schedule activation.

## Existing adapters and verification

Use the installed coordinator's current capture_ta_display.py, audit_display.py, the TE source parser/capture procedure and source-derived export mappings; use this package's check_dashboard.py and the repository's existing season builder. Do not run the obsolete all-modules launcher or invent a single-player capture flag. The existing capture helper's supported help/resume/check interfaces must be inspected before use.

This package provides the persisted control/evidence contract, not a credentialed all-in-one acquisition/deployment service. Unattended TA access, scheduler delivery, the actual iPhone push route and owner/backend integration must be piloted separately. Do not label a helper --help run, saved source replay or synthetic fixture as a new live result.

Run the state/relationship tests:

    python3 -B -m unittest discover -s tools/race_v2 -p 'test_*.py' -v

Tests exercise source waits, scope gaps, stale/replayed approvals, partial and two-perspective TA evidence, no premature Sunday release, future observations, changed dependencies, exact field reconciliation, six-file readback, production binding, private progress escaping, post-seal LIVE outages and legacy read-only status. They use synthetic temporary fixtures and make no external requests.
