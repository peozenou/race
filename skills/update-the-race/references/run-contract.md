# Race v2 operating contract

Approved by Patrick on 10 November 2026. Apply to new runs after installation validation; preserve completed legacy records and existing drafts. Notification activation remains PENDING_PILOT.

## Four phases and two decisions

Read the exact run state and this contract before using a module. The readiness watcher precedes the progress bar. The numbered phases are:

| Phase | Owner | Weight | Verified outcome |
|---|---|---:|---|
| 1. Acquire | GPT | 35% | Primary TA and dated TE evidence with identity/cutoff coverage |
| 2. Validate and review | GPT | 30% | Source-audited Sheet state and exact six-file candidate approved after review |
| 3. Release and hand over | GPT | 10% | Approved candidate committed and read back; Claude handoff ready |
| 4. Publish and verify | Claude | 25% | Correct production deployment, served data/version and browser checks |

Patrick makes two routine decisions: **Start** under the approved versioned write profile, then **approve the exact candidate release hash** after review. Until an authenticated orchestration service is separately built and approved, Patrick must also invoke Claude using the prepared handoff. That manual handoff is not implemented automation. New roster/rule decisions and material exceptions remain explicit decisions when they arise.

## Run identity, evidence and date meanings

Resolve season, competition week, target Monday, exclusive Monday 00:00 America/New_York cutoff, roster, scoring and transfer versions once. Preserve workbook timezones. Do not equate competition week with ISO week. Keep actual publication dates, tournament-start dates, actual completion evidence, capture time and ingestion time separate.

Persist immutable primary bytes and hashes before parsing. TA displayed Serve/Return owns match statistics; TE owns Race/ATP ranking publications; the approved ledger owns league scoring. Independent Elo remains a deliberately selected dated snapshot. Private UTR/MatchTrack is outside Race and never public. Missing values, errors, published zero and approved adjustments are different states.

Sunday acquisition is provisional until the exclusive cutoff and affected-player recheck are satisfied. TE publication is an independent readiness condition. Wait for its actual dated report and resume the same run; do not silently publish an older ranking or request another routine Start. Any proposed older-source carry-forward is a disclosed release exception requiring Patrick's decision.

## Approved bounded write profile

Read the [approved bounded scope](standard-profile.md).

Start records the exact approved `profile_version`, run configuration and authorization scope. In-profile actions may proceed without separate TA, TE or summary approvals: save source evidence; generate and retain exact diffs; verify a whole-workbook or complete protected-scope backup; update current-season mapped TA inputs; publish dated ranking values and a frozen weekly snapshot; append the ordinary weekly JOUEURS column/HEBDO row and extend their established table/formula ranges; calculate the five teams; and independently read back all affected and protected scopes. Writes remain idempotent, bounded, backed up and conditional on unchanged prestate.

The profile also permits one ordinary clear/restore recovery per failing LIVE import anchor when the final formula, source identity, selected publication and recovered values must equal the approved expected state. Save the recovery diff and before/after evidence. Stop after that bounded attempt if the source is still unavailable or values differ. Do not coerce errors to zero or try alternate external write routes.

A changed roster, scoring rule, transfer baseline, new exception, unexpected schema/structural change, or retroactive historical repair falls outside this profile. Stop only affected work, prepare a concrete reviewed diff and ask Patrick for the missing decision. Routine new-week row/column/table extensions listed above are already inside the profile; do not manufacture another approval gate.

## Candidate and release authority

Before sealing, source/value changes invalidate only checks whose actual dependency digests changed. Reuse a check only when every relevant source, parser, roster, rule, cutoff and protected-state dependency is identical. A matching write payload is not a primary-source audit. All 30 active players, 60 selected TE joins, complete eligible TA fields/types/order/duplicates, +5 duel identities, five team totals, native formula/table extent and protected history remain covered.

Create an immutable `release_snapshot_id` over primary source manifests, the frozen reviewed export-value scope, roster/rules/transfers/cutoff, audit checks, explicit exceptions and all six candidate dataset hashes. Present the exact diff, counts/dates, five totals/deltas, qualifications, backup references and hash to Patrick. Only explicit approval of this exact candidate authorizes phase 3. Changed candidate hashes require renewed affected review; an approval is never inferred from a notification.

**After sealing, approved frozen release evidence is the authority. LIVE import health is a separate operational diagnostic.** A subsequent volatile LIVE fetch failure does not revoke an unchanged approved release, published dashboard or production receipt. It may trigger the bounded profile maintenance action or a warning. A real correction to frozen source values, scoring, transfer state or released data creates a linked candidate revision and renewed approval; never silently rebind or relabel an existing release.

## Lean evidence and model use

Use deterministic existing capture/parser/comparison/export/build helpers; do not ask a model to recalculate every row. Cache raw evidence and parsed typed source objects once per source epoch. Track changed-player watchlists and reuse unchanged full-season pairs with roster-wide completeness checks. Use lightweight readiness probes before full capture; respect source cooldowns and persist bounded backoff. Fetch enough TE pages for actual identities and required tails, not a fixed top-500 boundary.

Establish a full protected-history baseline initially and after structural/history changes. On routine weeks, prove preservation using that baseline and verified bounded deltas before sealing; perform a full check whenever dependency coverage is insufficient. During unaffected later handoffs compare immutable digests and bounded live release evidence rather than repeatedly acquiring every historical cell. Independent source parsing and internal coherence remain distinct checks. GPT reasons about exceptions; Claude receives one small release manifest and changed-data summary, not acquisition history.

Record actual source requests, captures, bytes, check-cache reuse, retries, write batches, model use when available, approval count and active/wait time. Do not claim a token, cost or duration percentage saving before comparable runs are measured.

## Sunday readiness and notifications

Approved check slots are Sunday 18:00 and 21:00, with Monday 00:30 and 08:30 fallbacks, all America/New_York. They are approved settings, not evidence of an active scheduler. A pilot must prove unattended TA access, saved state, no duplicate notification and actual iPhone delivery before the workflow is advertised as operational.

Build the relevant event/player watchlist from the approved roster. Verify the relevant final completed results are present in TA; a prominent ATP final alone does not establish Challenger/ITF roster coverage. Any unfinished, missing, blocked or ambiguous coverage is NOT_READY or UNKNOWN, never READY. Readiness is permission to offer acquisition, not proof that Monday cutoff or TE publication has occurred.

Deduplicate READY by season/week plus notification state. Send at most one weekly READY approval request, with material source changes recorded as superseding evidence rather than repeated prompts. Delivery does not approve Start. Once Start is approved, later slots only resume the same authorized run as sources permit. Existing local Mac browser capture is not automatically available to a hosted scheduler; deployment must prove the chosen adapter's access. Scheduler push and iPhone notification permissions are separate capabilities to verify.

## One truthful progress view

One private versioned `run-status.json` and append-only events drive chat, review page and the future owner app. Include run ID, phase, state, verified work units, last observed time, next action, source dates, profile and candidate/release IDs, evidence digests and approval status. Use planned stable work units within phase weights 35/30/10/25. Percent means verified work, not elapsed time. Freeze the bar while waiting for a source, Patrick, Claude or deployment and show that dependency. Only verified live production reaches 100%.

The control schema must distinguish `waiting_source`, `waiting_approval`, `running`, `blocked`, `awaiting_claude` and `verified`. Serialize approval commands with run ID, exact candidate digest, action idempotency key and expected state revision. Reject replayed, stale or unauthorized commands. No owner-control or approval records belong in the public dashboard data.

## GPT release and Claude production

GPT owns acquisition, calculations, primary-source audit, bounded Sheet writes and the six-file release. Preserve `hebdo`, `joueurs`, `players`, `matches`, `calendar` and `team_colors` schemas, transfer lineage, archived outgoing rows and null meanings. Public player counts come from the current registry/ledger, not the obsolete assumption of 31. Calendar/colors remain byte-identical unless separately in scope. Validate against independently source-derived expectations, commit atomically to a dedicated release branch, detect concurrent edits and verify all six remote hashes.

Claude owns build, publication and live verification of that exact release. Preserve current French interface, approved wording, source dates, replacement lines, history figures, mobile behavior, assets and tutorial. Use the existing builder. Completion records the actual data/dashboard commits, six served hashes, matching build/live version, week/date/totals, deployment result and targeted desktop/mobile browser checks. No automatic redesign, preview/tutorial regeneration or email work is included.

## Runner, legacy records and installation

Use the installed scripts/race_v2/race_run.py with its own README. Its public source/receipt contracts are at tools/race_v2/ in the repository. Commands cover init/status, explicit Start, acquire/validate records, candidate sealing/release approval, verified release/production, health, readiness/outbox and linked revision. Supply actual human evidence; a file or boolean does not authenticate a human. Keep private state outside the public repository.

Keep schema-3 and older ledgers, audit decisions, releases, production records and drafts immutable. Use the read-only legacy compatibility view, not in-place renumbering. New runs finish with production; race-draft-email is deprecated for new runs and never automatically invoked. No workflow approval authorizes mail sending.

Installed source helpers remain available. Read adapters.md for exact existing interfaces and bounds; a clone of this public repository does not grant private service access. The v2 runner records evidence/progress, not automatic TA scraping, Sheets credentials or Claude execution.

## Independent weekly lanes and future clients

Read independent-lanes.md for weekly complete Elo/yElo checks and supplied private UTR. Show their separate statuses outside Race progress; do not wait for private input before public Race work. A later Elo import does not replace the snapshot frozen into a sealed candidate.

Future owner controls require an authenticated private service for Start/release approval and idempotent commands; the public companion reads only approved professional-player releases. No credentials, subscriptions, private source/approval data or personal filesystem paths are published. Free client distribution does not promise free model/backend operation.
