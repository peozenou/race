# Dashboard data and release contract

The dashboard uses the existing six-file JSON data store in `2026/data/`. Google Sheets is the operational review surface; a public JSON release is a downstream export of a cleared workbook state. A data refresh should preserve the consumed schemas and source meanings.

## Source authority

| Source | Owns | Boundary |
|---|---|---|
| Tennis Abstract displayed Serve/Return | Player match statistics | Displayed blanks remain blank; hidden raw data must not fill them |
| Tennis Abstract complete Elo/yElo reports | Published rating snapshots | Keep separate publication dates, complete tables and historical pairs |
| Tennis Explorer | Race/ATP ranking snapshots | Verify actual publication, table/page coverage and unique identities |
| Approved league rules and transfer records | Fantasy points and retained credits | Preserve versioned rules, scoped exceptions, offsets and frozen history |
| Cleared workbook readback | Exported operational results | Bind public output to the same reviewed inputs and cutoff |

Race points can legitimately decrease in a published ranking. Investigate anomalies against dated source evidence; do not replace observations with a running maximum. Missing rows, missing statistics, genuine published zeros and approved league exceptions are different states.

## Datasets

| File | Grain and key fields | Export source |
|---|---|---|
| `hebdo.json` | Team × competition week: `week`, `date`, `team`, `race`, `duels`, `total` | Cleared HEBDO effective history, including the established week-0 baseline |
| `joueurs.json` | Player/contribution × week: `team`, `player`, `week`, `race` | Cleared JOUEURS history plus approved outgoing/incoming contribution mappings |
| `players.json` | Active and retained outgoing player summaries | Approved player/summary values, selected TE/Elo snapshots and transfer metadata |
| `matches.json` | Player perspective on a match | Approved current-season player inputs and documented perspective/contest mapping |
| `calendar.json` | Event schedule | Existing approved calendar unless an event update is separately in scope |
| `team_colors.json` | Team palette: `team`, `color` | Existing approved five-team palette |

The runtime accepts row arrays and supported row wrappers; preserve the actual current representation and complete key sets when exporting. Existing field names stay unchanged even though this documentation is English.

The current player summary schema includes identity/team/display labels; wins/losses, walkovers, tour-level and surface counts; titles/finals; duel statistics; serve/return metrics; best-win fields; ATP/Race rankings and points; Elo/surface Elo/yElo; age; `matches_through`, `rankings_date`, `elo_date` and `transfer_date`.

The match schema includes `mid`, `player`, `short`, `team`, `event_date`, `event`, `level`, `surface`, `round`, `result`, `walkover`, `opponent`, `opponent_team`, `opponent_rank` and `score`. Inspect actual keys before modifying an export. Do not add a field or change its meaning merely to simplify a new script.

## Identities, dates and transfers

There are 30 active selections, six per team. Historical public datasets may contain more players or current-week contribution rows because outgoing earned credit is retained. A transfer does not authorize deletion of the outgoing player's matches, points or history. The 2026 Sinner/Lehecka transfer illustrates this distinction: `players.json` holds 31 player records, while the dashboard shows 30 lineup lines. Do not enforce a blanket 30-row limit on public files.

Maintain an explicit source-to-export identity and transfer mapping. Display names and labels such as “entered” or “left” are not a substitute for the approved ledger. Distinguish a player's raw TE points, outgoing credit kept by a team, incoming gains after entry and a deliberately held incoming contribution. An unknown entry baseline is not an observed zero. Keep the baseline unresolved and guard the dependent gains until verified.

Preserve frozen history when a slot changes identity. Do not recast an outgoing player's historical points as the incoming player's past performance. If a compatibility view uses slot history, document that lineage in private release evidence and preserve the established public representation deliberately.

### Replacement lines on the dashboard

The dashboard keeps six posts per team by showing an in-season replacement as one lineup line, labelled `outgoing/incoming` (for example **Sinner/Lehecka**). It builds that line from the exported data without a separate mapping file:

- **Pairing rule.** Exactly one outgoing and one incoming player of the same team share the same `transfer_date`. Their `short` labels end in ` (sorti)` and ` (entré)`. Any other combination (two out and one in, for instance) is shown as separate player lines.
- **Values.** The line's Race points, share, gains and post history add both players' credited JOUEURS contributions, and its duel points add both players' `duel_pts`. Record, titles, ranks and Elo are the incoming player's. The detail view switches between the two players' seasons. Tournament bubbles stay one per player.
- **Colours.** The outgoing player's part keeps the team colour from `team_colors.json`. The incoming player's part uses a darker shade of it, the team colour darkened one step (CHEF `#93c47d` becomes `#678958`). This applies to the team composition bar (one segment split in two, with a legend and per-player tooltip), the post chart in the detail (stacked bands), and the detail's player buttons and surface bars. No colour is added to `team_colors.json`.
- **Held incoming contribution.** While the incoming player's credited JOUEURS value is 0 under an unresolved entry baseline, the line shows his part as pending. It shows no gains and gives his darker segment no width, and notes that his raw TE Race points are not yet counted. The display switches off by itself once a cleared release credits him.

**Export contract for step 5:** keep both player records, the ` (sorti)` / ` (entré)` labels and one shared `transfer_date` for the pair. Keep both players' JOUEURS rows. No schema change is involved.

Per-player display qualifications (a held incoming contribution, an approved Race adjustment such as Kouame's +24) are listed in the dashboard source (`RACE_QUAL` in `2026/source/dashboard.html`). When a release introduces a new hold or adjustment, the step-5 handoff names it, so Claude can add it in step 6.

Keep competition dates and actual ranking/rating publication dates separate. `hebdo.date` retains the approved workbook's competition/update-date meaning. Do not relabel a competition Monday to an earlier ranking publication date. `rankings_date` and `elo_date` retain the selected source dates. TA's `event_date` may be the tournament start date; it is not automatically the match's completion timestamp.

Keep a stable source-key mapping privately for contests and player perspectives. Export IDs such as `M0001` are display identifiers, not proof of a stable contest key. Two selected players can legitimately create two perspectives on one contest; duplicate the perspective neither within one file nor on rerun.

## Missing values and calculations

Preserve nulls and their source reasons in release evidence. Do not turn a failed lookup into zero or carry an older value forward as a new observation. If the dashboard cannot safely display an approved null, identify that compatibility issue rather than fabricate a value.

Prefer approved effective summary cells to a fresh calculation. When recomputation is needed, document eligibility, classification and denominators. Do not average displayed percentages to create a count-weighted rate without actual counts. Keep walkover/retirement handling, main-tour definitions, title/final criteria, surfaces, duel rules and transfer boundaries consistent with the cleared workbook. Missing opportunities yield an unavailable rate, not an invented percentage.

Reconcile each team's Race, Duels and any explicit adjustment to Total. An adjustment already included in Race must not be added again. Do not expect unadjusted current-player TE sums to equal a team total when retained transfer credit or approved offsets apply.

## Step-5 release procedure

1. **Confirm clearance and state.** Read Patrick's exact final review approval and its workbook/source/roster/rules/cutoff fingerprint. Freshly reread the relevant Sheet values before extraction. A changed dependency returns to its owning step for verification and renewed affected clearance.
2. **Read current repository state.** Check remote HEAD, current schemas and any concurrent data/dashboard changes. Build on that state; a local checkout can be stale.
3. **Prepare an immutable candidate.** Include all six datasets and a private manifest, source-to-export comparison and Claude handoff note. Preserve unchanged calendar/colors and the current source/dashboard design unless separately in scope.
4. **Validate all fields and coverage.** Compare exported values against independently prepared cleared-source evidence, not an expected file generated from the candidate itself. Run structural and internal checks as well as the source comparison.
5. **Review the bounded data diff.** Keep it to the six intended data files on a dedicated release branch. Detect concurrent edits. Prefer one commit for the complete data release; production publication and generated page output belong to Claude in step 6.
6. **Commit, read back and hand off.** Verify all six hashes at the release-branch commit. Save release ID/branch/commit, previous version, counts and the Claude handoff in the private receipt. Keep production pending until Claude completes step 6.
The step-5 handoff is not dashboard production. Pass the exact release to Claude for the required step 6 described below.

Required validation includes unique grains, five teams, 30 active selections, explicit archived membership, complete expected historical/current contribution sets, correct source dates, all five totals, consistent transfer rules, native types, missingness and no private fields. Exact public row counts come from the approved release contract rather than a hardcoded historical count.

The locally installed `check_dashboard.py` helper checks six-file structure/internal consistency against an independently prepared expectation contract. It does not read Sheets or establish source truth by itself. It is part of the Codex skill environment and is not assumed to exist after cloning this repository.

## Step 6 — Claude build, publication and live verification

Claude owns this production step. Read the [production runbook](claude-dashboard-production.md), the exact approved data release and current remote HEAD. Incorporate that release, make the data-driven dashboard update and run the existing builder from the repository root:

```sh
python3 2026/tools/build.py
```

The existing builder reads the six datasets and `2026/source/dashboard.html`, computes a data-version hash and writes `2026/index.html`. The generated page's metadata and asset/data cache version must match the release. Keep changes to Claude's dashboard source intentional; do not overwrite concurrent source, runtime, theme, tutorial or landing-page changes with a stale local copy.

Documentation-only commits do not need a dashboard rebuild. Social-preview generation and tutorial recording are optional separate work. Do not treat the removed weekly HEBDO/BILAN PNG step as a requirement to regenerate these existing site assets.

Track outcomes separately:

| Outcome | Evidence |
|---|---|
| Candidate staged | Complete local bundle and validation evidence |
| GitHub data export verified | Resulting commit and readback hashes of the intended data files |
| Claude handoff prepared | Release note with source/date/scope/check instructions |
| Dashboard rebuilt | Generated page and data-version match the intended release |
| Live verified | Served page and datasets match the recorded release/version |

Step 5 is complete at the verified release-branch export with its prepared handoff. Step 6 remains `awaiting_claude` until Claude publishes and verifies the updated live dashboard. Step 7 is blocked until that production receipt matches the approved release, then saves an unsent Gmail draft containing the verified live dashboard link. Do not contact another assistant automatically.

## Claude handoff and rollback

The handoff should state the release ID, target competition week/date, cutoff, true source dates, GitHub commit, changed files/counts, five totals, retained qualifications, transfer holds, schema/null/lineage considerations and build/live status. Include checks for team/player filters, history charts, table counts, replacement lines, source-date labels and preserved tutorial behavior. Name any new held contribution or approved Race adjustment the dashboard must qualify.

Keep the previous approved commit and release manifest. If publication is wrong, prepare a bounded revert or corrective revision from the verified previous state, record why it was superseded and repeat affected checks. Do not force-push or discard unrelated concurrent work.

## Public/private boundary

Publish only the approved professional-player datasets and intended dashboard assets/documentation. Keep private junior statistics, MatchTrack files, UTR observations, mail headers/addresses, credentials, personal filesystem paths, Sheet backup payloads and human approval records out of this repository. Mentioning the independent private workflow does not make its inputs public.

Record detailed source manifests, null reasons, checks, approval hashes, backup links, stable identity mappings and revision history in private run/release storage. A future public provenance format would require its own explicit schema and publication decision; it is not an automatic seventh dashboard dataset.
