# Step 6 — Claude dashboard production

**Owner: Claude.** Update, build, publish and verify the Race dashboard from the exact data release handed off at step 5. Gmail drafting is step 7 and waits for verified production.

The sequence is: **steps 1–4 and Patrick's clearance → step-5 data release/handoff → Claude production (6) → Gmail draft with the updated dashboard link (7)**.

## Required handoff

Before starting, obtain the step-5 handoff through Patrick or the agreed repository release context:

- Release ID and dedicated data-release branch/commit.
- SHA-256 hashes for all six approved JSON files: hebdo, joueurs, players, matches, calendar and team_colors.
- Target season, competition week/date, match cutoff and actual ranking/rating source dates.
- Five approved team totals, retained transfer credit/holds, missingness and source qualifications.
- Previous production commit/version, actual public season URL and the requested dashboard checks.
- Confirmation that Patrick cleared this same data state; detailed approval evidence and private run fingerprints stay in private run storage.

Read the latest [weekly workflow](weekly-workflow.md), [data contract](data-and-releases.md), repository instructions and current remote HEAD. Verify the release's file hashes and preserve concurrent dashboard/source/tutorial changes. A stale local checkout is not a safe production baseline.

The current public season URL is [THE RACE 2026](https://peozenou.github.io/race/2026/). Resolve the correct URL and compatible build/data contract before publishing another season.

## Update and build

Incorporate the exact six-file approved release. Update the dashboard as needed to reflect that release, including current week/date, source labels, transfer state, tables and charts. Preserve the established French interface, existing design and unrelated work unless Patrick requests a broader change. A routine weekly production task does not authorize an unrelated redesign.

Do not silently modify cleared league data or scoring rules to make the presentation agree. If a data/identity/transfer issue is discovered, return it to the owning data/audit step and wait for the affected state to be verified and cleared again.

From the repository root, run the existing builder:

```sh
python3 2026/tools/build.py
```

The builder reads the six JSON files and `2026/source/dashboard.html`, then writes `2026/index.html` with the data-version token and current metadata. Verify the built page references the intended release/version. Do not regenerate the optional preview image or tutorial, or change assets/source unrelated to the release, without a separate need or request.

## Publish

Check current production HEAD immediately before publishing. Incorporate the approved data and required generated page/source changes together into the production commit, preserving concurrent changes. Keep the release commit traceable in the production note. Use the repository's actual configured GitHub Pages publication route; do not invent a deployment workflow or assume a fixed completion delay.

A successful commit, push or build is an intermediate result. If deployment is still running, failed or serving cached older files, record the exact status and resume point. Do not claim production complete or unblock Gmail until the actual served result is checked. No background monitor is configured merely by this runbook.

## Verify the live dashboard

Verify the canonical public dashboard URL in a browser and compare it with the release and production commits:

1. All six served JSON datasets match the approved step-5 hashes. Confirm that a mixture of old/new cached files is not being served.
2. The served page's data-version token matches the verified build, and the page loads without release-related errors.
3. The intended competition week/date and all five team totals match the approved release. Preserve true source dates separately from the competition Monday.
4. Player/team filters, ranking/statistics tables, player history and team-history charts work with the actual active/archived transfer representation.
5. Approved source qualifications, retained outgoing credit, incoming holds and null meanings are represented accurately. Missing data is not silently presented as an observed zero.
6. Existing navigation, tooltip and tutorial behavior remains intact within the affected scope.

Save actual verification time and evidence. A cache-busting request can help diagnose stale publication, but the Gmail draft must use the verified canonical public dashboard link. A stale or wrong release is a failed/pending production check, not an acceptable freshness qualification.

## Completion handoff to ChatGPT/Codex

Return a concrete completion note to Patrick/the coordinator. Include:

| Field | Meaning |
|---|---|
| `owner` | `Claude` |
| `production_status` | `LIVE_DASHBOARD_VERIFIED` only after the checks above |
| `release_id`, `data_commit_sha` | The exact approved step-5 data release |
| `dashboard_commit_sha` | The actual production build/publication commit |
| `dashboard_url` | The verified canonical public season URL to include in Gmail |
| `live_data_sha256` | All six served dataset hashes matching the approved release |
| `build_data_version`, `live_data_version` | Matching built and served versions |
| `live_week` | The verified competition week |
| `ui_checks_verified` | Actual browser-check result, not a build-only assertion |
| `live_verified_at` | Timezone-aware timestamp of the real live observation |
| Evidence references | Claude completion, production/deployment details and served data/browser checks |

Claude also saves a public copy of the completion note, without the workbook fingerprint or approval records, with its live evidence under `docs/production/<season>/<release_id>/` (for example [2026-10-19-w35-r1](production/2026/2026-10-19-w35-r1/HANDOVER.md)).

The private coordinator receipt also binds the same cleared workbook fingerprint, saves Claude's actual completion evidence and records the immutable receipt hash. Do not upload private approvals, junior data or personal account details merely to supply that evidence. A receipt's assertion is not a substitute for inspecting the real result.

After verification, step 6 becomes done (or a specifically accepted bounded qualification with the correct live release). Step 7 can then create the unsent Gmail draft with that exact updated dashboard URL and bind it to this production receipt/commit. Optional draft validation and permission to send remain separate.

If production changes after verification, invalidate steps 6–7 and reverify before drafting/reusing a draft. If the cleared data changes, invalidate the earliest affected data stage and obtain the required renewed clearance. Preserve previous commits, completion notes and draft history.

## Ownership and invocation

Patrick explicitly invokes Claude for this production task. Preparing a handoff does not automatically message, start or impersonate Claude. ChatGPT/Codex's `$race-publish-dashboard` skill prepares the handoff, tracks `awaiting_claude`, checks the returned evidence and updates the shared progress record. It does not substitute a Codex-run build for the Claude-owned production stage.

Example request to Claude:

> Run step 6 using the approved step-5 release identified in this handoff. Follow `docs/claude-dashboard-production.md`: update, build, publish and verify the Race dashboard, preserve concurrent work, and return the production commit, verified dashboard URL, data/version evidence and completion note for step 7.
