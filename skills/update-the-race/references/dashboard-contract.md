# Dashboard data and release contract

The dashboard uses the existing six-file JSON data store in `2026/data/`. Google Sheets is the operational review surface; a public JSON release is a downstream export of a source-audited, frozen and approved release snapshot. A data refresh should preserve the consumed schemas and source meanings.

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

There are 30 active selections, six per team. Historical public datasets may contain more players or current-week contribution rows because outgoing earned credit is retained. A transfer does not authorize deletion of the outgoing player's matches, points or history. The current edition retains both Sinner/Lehecka and Engel/Blockx lineage; resolve its actual published membership from the approved registry/ledger, while the dashboard shows 30 lineup lines. Do not enforce a blanket 30-row limit on public files.

Maintain an explicit source-to-export identity and transfer mapping. Display names and labels such as “entered” or “left” are not a substitute for the approved ledger. Distinguish a player's raw TE points, outgoing credit kept by a team, incoming gains after entry and a deliberately held incoming contribution. An unknown entry baseline is not an observed zero. Keep the baseline unresolved and guard the dependent gains until verified.

Preserve frozen history when a slot changes identity. Do not recast an outgoing player's historical points as the incoming player's past performance. If a compatibility view uses slot history, document that lineage in private release evidence and preserve the established public representation deliberately.

### Replacement lines on the dashboard

The dashboard keeps six posts per team by showing an in-season replacement as one lineup line, labelled `outgoing/incoming` (for example **Sinner/Lehecka**). It builds that line from the exported data without a separate mapping file:

- **Pairing rule.** Exactly one outgoing and one incoming player of the same team share the same `transfer_date`. Their `short` labels end in ` (sorti)` and ` (entré)`. Any other combination (two out and one in, for instance) is shown as separate player lines.
- **Values.** The line's Race points, share, gains and post history add both players' credited JOUEURS contributions, and its duel points add both players' `duel_pts`. Record, titles, ranks and Elo are the incoming player's. The detail view switches between the two players' seasons. Tournament bubbles stay one per player.
- **Colours.** The outgoing player's part keeps the team colour from `team_colors.json`. The incoming player's part uses a darker shade of it, the team colour darkened one step (CHEF `#93c47d` becomes `#678958`). This applies to the team composition bar (one segment split in two, with a legend and per-player tooltip), the post chart in the detail (stacked bands), and the detail's player buttons and surface bars. No colour is added to `team_colors.json`.
- **Held incoming contribution.** While the incoming player's credited JOUEURS value is 0 under an unresolved entry baseline, the line shows his part as pending. It shows no gains and gives his darker segment no width, and notes that his raw TE Race points are not yet counted. The display switches off by itself once a cleared release credits him.

**Phase-3 export contract:** keep both player records, the ` (sorti)` / ` (entré)` labels and one shared `transfer_date` for the pair. Keep both players' JOUEURS rows. No schema change is involved.

Per-player display qualifications (a held incoming contribution, an approved Race adjustment such as Kouame's +24) are listed in the dashboard source (`RACE_QUAL` in `2026/source/dashboard.html`). When a release introduces a new hold or adjustment, the release handoff names it, so Claude can add it in phase 4.

Keep competition dates and actual ranking/rating publication dates separate. `hebdo.date` retains the approved workbook's competition/update-date meaning. Do not relabel a competition Monday to an earlier ranking publication date. `rankings_date` and `elo_date` retain the selected source dates. TA's `event_date` may be the tournament start date; it is not automatically the match's completion timestamp.

Keep a stable source-key mapping privately for contests and player perspectives. Export IDs such as `M0001` are display identifiers, not proof of a stable contest key. Two selected players can legitimately create two perspectives on one contest; duplicate the perspective neither within one file nor on rerun.

## Missing values and calculations

Preserve nulls and their source reasons in release evidence. Do not turn a failed lookup into zero or carry an older value forward as a new observation. If the dashboard cannot safely display an approved null, identify that compatibility issue rather than fabricate a value.

Prefer approved effective summary cells to a fresh calculation. When recomputation is needed, document eligibility, classification and denominators. Do not average displayed percentages to create a count-weighted rate without actual counts. Keep walkover/retirement handling, main-tour definitions, title/final criteria, surfaces, duel rules and transfer boundaries consistent with the cleared workbook. Missing opportunities yield an unavailable rate, not an invented percentage.

Reconcile each team's Race, Duels and any explicit adjustment to Total. An adjustment already included in Race must not be added again. Do not expect unadjusted current-player TE sums to equal a team total when retained transfer credit or approved offsets apply.

## Candidate sealing and phase-3 release

1. **Before sealing, verify source and operational state.** Use the approved Start/profile scope, fresh bounded prestate/readback and complete primary-source comparison. Establish protected-history baseline or verified routine deltas. A changed actual dependency invalidates only its affected checks.
2. **Read current repository state.** Inspect remote HEAD, schemas and concurrent dashboard/data work. Preserve unrelated changes.
3. **Seal one immutable candidate.** Include all six datasets and private source/roster/rules/transfers/cutoff manifests, frozen export-value cells, independent reconciliation, qualifications, backup proof and a candidate digest. Calendar/colors remain unchanged unless separately in scope.
4. **Obtain the exact release decision.** Patrick approves the concrete reviewed candidate hash. A required failed or unexamined scope cannot pass. Start authorization and final candidate approval remain separate.
5. **Commit coherently and read back.** Publish the six-file data state in one dedicated release-branch transaction where possible. Verify all six hashes at the resulting immutable commit and save release ID, branch/commit, counts, actual source dates and prior-version rollback reference.
6. **Prepare the Claude handoff.** Generate one compact brief from that manifest. Production remains awaiting Claude until the actual served release is verified. Patrick invokes Claude explicitly; no automatic assistant messaging is configured.

After sealing, approved source/release evidence is authoritative. Volatile LIVE IMPORTHTML health is separate: a later fetch outage does not revoke an unchanged frozen release or its production receipt. A real frozen-value/rule/output correction creates a linked candidate revision and renewed affected approval; never silently rebind.

Validation covers every exported field against independently source-derived expectations, unique grains, five teams, 30 active selections plus explicit outgoing membership, complete history/current contribution sets, correct dates, transfer/duel rules, null/type meanings and absence of private fields. The installed check_dashboard.py helper adds structure/internal checks; candidate equality alone does not prove source truth.

## Phase 4 — Claude build and live verification

Claude reads the approved six-file release and current production HEAD, preserves unrelated source/design/history/tutorial work, runs **python3 2026/tools/build.py**, and publishes the approved data with its necessary generated page/source changes through the configured Pages route. The builder also hashes the history/runtime inputs its current implementation reads; inspect that implementation rather than assuming an old build contract.

Read the [production runbook](production-contract.md). Verify successful deployment, the canonical URL, all six served dataset hashes, matching build/live version, competition week/date and five totals, source-date/qualification/transfer presentation and affected desktop/mobile browser behavior. A successful build, push or pending deployment is insufficient. Only verified production completes the weekly run; there is no email task afterward.

Keep these outcomes distinct: candidate staged; data commit verified; handoff prepared; dashboard built; production deployed; served release and UI verified. Documentation-only commits need no dashboard rebuild. Preview images/tutorial regeneration are separate optional tasks.

## Claude handoff and rollback

The handoff should state the release ID, target competition week/date, cutoff, true source dates, GitHub commit, changed files/counts, five totals, retained qualifications, transfer holds, schema/null/lineage considerations and build/live status. Include checks for team/player filters, history charts, table counts, replacement lines, source-date labels and preserved tutorial behavior. Name any new held contribution or approved Race adjustment the dashboard must qualify.

Keep the previous approved commit and release manifest. If publication is wrong, prepare a bounded revert or corrective revision from the verified previous state, record why it was superseded and repeat affected checks. Do not force-push or discard unrelated concurrent work.

## Public/private boundary

Publish only the approved professional-player datasets and intended dashboard assets/documentation. Keep private junior statistics, MatchTrack files, UTR observations, mail headers/addresses, credentials, personal filesystem paths, Sheet backup payloads and human approval records out of this repository. Mentioning the independent private workflow does not make its inputs public.

Record detailed source manifests, null reasons, checks, approval hashes, backup links, stable identity mappings and revision history in private run/release storage. A future public provenance format would require its own explicit schema and publication decision; it is not an automatic seventh dashboard dataset.
