# Weekly update workflow

Process version: 18 October 2026.

The weekly Race update consists of seven ordered tasks. Each task has a specific owner, a completion record and an individual skill trigger. Elo and private player development statistics run independently. A failed source blocks the output that depends on it; it does not undo verified work in unrelated modules.

## Sequence and write ownership

| Step | Skill | Owns | Complete when |
|---|---|---|---|
| 1 | `$race-update-ta` | Current-season player statistics from displayed TA Serve/Return tables | All 30 selected players, eligible inputs, cutoff, types and protected history are verified |
| 2 | `$race-update-te` | Raw Race/ATP ranking tables in LIVE and the dated frozen weekly snapshot | Actual source dates, saved ranking values and all 60 selected-player Race/ATP joins are verified |
| 3 | `$race-update-summary` | Derived team blocks in LIVE/snapshot; HEBDO, TEAMS, JOUEURS and BILAN | Formulas, five team totals, transfer rules, week alignment and historical protection are verified |
| 4 | `$race-audit` | Independent external/internal checks and the final review packet | Required checks support the release and Patrick clears that exact reviewed state |
| 5 | `$race-export-dashboard` | The cleared professional-player data release in this repository | The full source-to-export comparison and GitHub commit readback are verified; the Claude handoff is prepared |
| 6 | Claude — `$race-publish-dashboard` coordinates the handoff/result | Update, build, publish and verify the live Race dashboard from step 5 | Claude completion/deployment evidence and live data/version match the approved release; production URL is verified |
| 7 | `$race-draft-email` | One unsent Gmail draft linking the updated dashboard | Step-6 production is verified and the saved draft's dashboard link, recipients, body and unsent status have been read back |

The order is **1 → 2 → 3 → 4 → Patrick's clearance → 5 → Claude production (6) → Gmail draft (7)**. Read-only preparation may overlap, but publication follows that sequence. Copying a prior snapshot's derived team blocks during step 2 does not make those calculations current; step 3 owns them.

TEAMS may be a worksheet, named table or equivalent team block in the actual workbook. Resolve that mapping before claiming it was updated. Do not create an assumed tab solely to match the process label.

## Contributors and handoff

**ChatGPT/Codex and Claude are both contributors.** Their primary responsibilities are complementary:

| Contributor | Responsibility |
|---|---|
| ChatGPT / Codex | Prepare and verify source data, update Google Sheets, maintain progress and evidence, perform the audit, export the cleared GitHub release and prepare the unsent Gmail draft. Also handle the independent Elo and private-statistics tasks. |
| Claude | Own step 6: update/build the dashboard from the exact approved release, publish it to production and verify the live data, version and presentation before Gmail drafting. |
| Patrick | Clear the final reviewed data state, decide roster/scoring changes and explicitly authorize any email sending. |

The Codex skills implement the task sequence in Patrick's installed environment. ChatGPT can contribute to planning, review and analysis using the access available in its session; contributor roles do not imply that every assistant has the same tools or private-data access.

GitHub provides the shared, versioned handoff. After Patrick clears step 4, the step-5 handoff identifies the verified data commit, source dates, scope and remaining dashboard checks. Claude uses that identified release for the mandatory step-6 production stage. The coordinator records `awaiting_claude` and keeps step 7 pending until the production completion evidence is verified. Preparing the handoff does not automatically notify or start Claude; Patrick explicitly triggers the next contributor. No automatic ChatGPT/Codex–Claude communication is configured.

Before editing or publishing, either contributor checks the current remote HEAD and the latest relevant documentation, then preserves the other's concurrent changes. Both can update repository documentation and make scoped technical fixes when asked. Dashboard work does not silently change cleared data or league rules: a discovered data issue returns to the owning update/audit step, with affected clearance and release status reviewed again.

Patrick's step-4 clearance, Claude's step-6 production verification, step-7 draft validation and email-sending authorization remain separate records. Keep private junior information and detailed approval evidence outside the public handoff.

## Coordinator and individual triggers

Use `$update-the-race` to identify the run, display progress or continue an overall weekly update. Use a task's own skill to perform only that task. A one-step request stops at that step's verified result and progress summary. An overall update continues in order through the existing approval boundaries.

Examples:

| Request | Expected action |
|---|---|
| “Start this week's Race update.” | Resolve one target Monday and competition week, show progress and begin the next authorized step |
| “Run step 2 only for the same run.” | Verify step 1's completion; run the TE module without silently executing other steps |
| “Show the weekly progress.” | Show all seven steps and exact blockers; do not repeat writes |
| “Continue.” | Resume the identified run from its first incomplete step using verified evidence and unchanged approvals |
| “Audit the update.” | Execute step 4 and present the exact state for Patrick's clearance |
| “Continue after clearance.” | Prepare the step-5 release/handoff, await Claude's verified step-6 production, then prepare step 7 |
| “Run dashboard production in Claude.” | Give Claude the exact release and [step-6 runbook](claude-dashboard-production.md); return its completion evidence to the coordinator |

If more than one run is unresolved, identify the candidates before resuming. Do not choose a run from a folder timestamp alone. These skills are local Codex capabilities; the documentation does not install them into another assistant's environment.

## Sunday and Monday

Step 1 can start on Sunday once relevant completed results are available. Capture both full-season displayed views for each selected player, preserve their timestamps and record ongoing or unplayed relevant matches in a watchlist. Sunday work remains provisional until the required cutoff recheck is complete.

On Monday, check the watchlist, newly completed results and changed source rows against the approved exclusive match-completion cutoff. Reuse unchanged verified captures and collect supplements for affected players. Do not recapture all 30 solely because the calendar date changed. TA's displayed tournament date is not, by itself, proof of actual match completion before the cutoff.

After step 1 is complete, step 2 uses the actual TE publication. If the new ranking has not been published, record the last check and retained source date and hold dependent publication. Step 3's formula preview may be prepared read-only. Elo and the private statistics workflow remain available independently.

Patrick may explicitly approve a qualified release using an older published ranking for that week. Record both the target competition Monday and the actual publication date. Never turn an older observation into a true transfer entry-date baseline or carry that approval into a future week automatically.

## Intake and evidence

Resolve these once per run and reuse confirmed answers:

- Season, target Monday, competition week and the previous completed run.
- Exclusive completed-match cutoff and the `America/New_York` workflow timezone, preserving each workbook's own timezone.
- Confirmed roster, unique player identities, scoring version and approved transfer ledger.
- Actual source and destination access, current worksheet headers, formulas and table boundaries.

Competition weeks are workbook competition weeks, not ISO weeks. Keep publication date, event/tournament date, actual match-completion time, capture timestamp and as-of cutoff separate. The snapshot naming convention is `YYYYMMDDwNN`; the date in its name does not prove the source was published that day.

Create a fresh durable folder each week. Save original raw sources before normalization, retain hashes and explicit null reasons, and preserve correction revisions. Resume only the exact verified run with unchanged input/configuration/roster/code fingerprints and valid checkpoints. Respect persisted source cooldowns and retry limits.

Private run folders contain source inventories, previews, approvals, backup receipts, native Sheet readbacks, audit evidence and progress. They are not uploaded wholesale to this public repository.

## Sheet writes and final clearance

The established write procedure is: prepare an exact-range preview, reuse or obtain approval for that scope, check for edits since the preview, verify a backup, apply bounded changes and independently read them back. Preserve unrelated cells, formats, formulas, previous-season data and frozen history.

Step 1 writes verified current-season B:X inputs. Preserve A, Y and Z:AD. Keep breakpoint fractions as text, percentages numeric and displayed missing statistics or durations blank. Insert rows at the lower season boundary and verify formula propagation. Completed retirements/walkovers are retained even when statistics are unavailable; unfinished or postcutoff records are separately withheld.

Step 2 validates TE table selectors, pagination, source dates and identities. Lookup ranges must cover the entire saved ranking table needed for the roster, including players beyond a top-500 boundary. A failed or missing lookup is not a published zero.

Step 3 uses one verified weekly snapshot across all summaries. Recompute qualifying +5 duel credit under the approved roster and transfer rules. Preserve retained outgoing credit, offsets and frozen history. Guard incoming gains when an entry baseline is unresolved. Report all five Race/Duels/adjustment/Total paths without double-counting adjustments.

Step 4 performs separate external source comparisons and internal coherence checks. A successful write or comparison with its own payload is insufficient. The review packet includes source dates/cutoff, counts, changes and exclusions, all five totals/deltas, workbook/backup links, formula/history checks, transfer holds, exceptions and the proposed public export scope.

Use PASS only for checked evidence, QUALIFIED for an explicit bounded exception, FAIL for a failed requirement, and NOT_CHECKED/BLOCKED for unperformed or unavailable checks. Required failed or unexamined scopes cannot earn clearance. An approved historical exception does not become a general missing-equals-zero policy.

**Patrick's explicit clearance is required after this final review.** Earlier approval to write a preview, an audit PASS or “continue” without that final review does not supply it. Reuse existing clearance only for the unchanged reviewed state. Record the exact human instruction and the review/workbook fingerprint.

## Progress and recovery

Every stage completion, blocker, review and resume shows the same seven-row table. Include the verified completed count out of seven, actual source/capture dates, current step, exact next action and resume location. Independent tasks appear separately and do not change the denominator.

| Status | Meaning |
|---|---|
| Pending | Not yet performed |
| Provisional | Sunday or cutoff-dependent work awaiting its recheck |
| Staged | Evidence or a concrete preview prepared; dependent publication incomplete |
| Awaiting write approval | Exact Sheet preview ready for Patrick |
| Blocked | Named missing input, source or failed check prevents the dependent action |
| Awaiting review | Step-4 audit packet ready; Patrick's clearance pending |
| Awaiting Claude | Step-5 handoff ready; Claude's step-6 production or its live verification is pending |
| Done / qualified | Named completion criteria verified, with any bounded qualification explicit |
| Stale | A changed upstream dependency invalidates the previous result |

A staged local export is not a GitHub export. A local email preview is not a Gmail draft. Step 4 is complete only after clearance; step 6 is complete only after Claude's production is verified live; step 7 is complete when the draft containing that verified dashboard link is saved and read back. Optional draft validation and sending remain separate outcomes.

When a source, roster, rule or affected workbook value changes, invalidate the owning step and its dependents, preserve earlier receipts and review the affected scope again. Fresh Sheet reads before export and drafting detect edits outside the run. Local receipt hashes alone cannot detect external changes. A previously published release or saved draft remains a historical artifact and is deliberately superseded; invalidation does not erase it.

## Independent tasks

**Elo — `$tennis-update-elo`.** Import both complete men's Elo/yElo reports, with each report's own publication date and full row/field comparison. Preserve previous dated pairs. Verified unchanged reports produce an explicit no-source-advance outcome with zero writes. A later Elo update does not silently replace the frozen rating snapshot chosen for an already cleared Race release.

**Private statistics — `$tiago-update-data`.** MatchTrack imports and user-supplied UTR observations have separate statuses and destinations. Validate real export schemas, scoring progression, final scores, duplicates, revisions and partial coverage. Missing observations stay missing. An unresolved match record does not block the supplied-UTR submodule or any Race/Elo task. Keep all junior measurements, raw files, observations and private run evidence outside this repository and the league email.

## Data export, Claude production and email

After clearance, step 5 freshly verifies that the reviewed source state is unchanged, prepares all six existing JSON files and reconciles every exported field. Export the data to a dedicated release branch and verify the exact release commit/hashes; production publication belongs to Claude in step 6. Start from current remote HEAD rather than a potentially stale local checkout. Preserve transfer lineage and unrelated dashboard changes. See the [data and release contract](data-and-releases.md).

The handoff to Claude identifies the cleared release ID/branch/commit, source dates/cutoff, all six data hashes, changed counts, five totals, qualifications, transfer holds, previous production version and required dashboard checks. Preparing the handoff does not automatically message or start Claude; Patrick explicitly triggers that contributor.

**Step 6 is production owned by Claude.** Follow [Claude dashboard production](claude-dashboard-production.md). Claude incorporates the exact approved data, performs the release-driven dashboard update, runs the existing build, publishes the data and required generated page/source changes together to production, then verifies the live URL, all six data hashes, build/data version, competition week/date, totals and UI behavior. Preserve unrelated source/design/tutorial changes. Data/rule discrepancies return to the owning data/audit step for revised clearance.

A successful build, commit or deployment still in progress does not complete step 6. Record `awaiting_claude` or the exact production blocker until the served dashboard matches. The coordinator requires Claude's actual completion evidence, production commit/URL, live version/hashes, verification timestamp and browser checks. A stale/wrong release cannot pass under a freshness qualification.

Step 7 locates the previous relevant sent league email for actual recipient headers and style, preserves intended multiple addresses, checks for an existing current-run draft and saves one unsent draft. Use only cleared facts and include the updated live dashboard link verified in step 6. Recheck the production version before saving. If production is pending, stale or failed, keep drafting blocked; an export-only link or disclosure of an old dashboard does not satisfy this step. Exclude junior information and stale attachments. Draft validation is separate from authorization to send.

Routine PNG production and automatic image replacement are outside this weekly process. Preserve historical images. Skill installation and these documents do not create a scheduler, source-specific one-click launcher or proof that a live weekly run has occurred.


## Migrating earlier progress records

New runs use seven steps. Existing six-step ledgers retain a byte-for-byte legacy backup and their earlier Gmail result as history: old step 6 is not evidence of Claude production. The explicit `race_run.py migrate-seven` operation preserves verified steps 1–5 and unchanged audit clearance, inserts pending Claude production as step 6 and pending Gmail as step 7. Recheck any existing draft after production before reusing it. Missing legacy release/hash metadata is reverified in a new step-5 receipt without unnecessary Sheet writes.

Production-only changes invalidate steps 6–7 while preserving the unchanged cleared data/export. Changes to actual source data, rules or workbook values invalidate the owning earlier stage and affected clearance. Completed historical weeks are not reopened or relabeled automatically.
