# THE RACE pipeline v3 — design

Status, 24 November 2026: **skeleton implemented and tested offline; not yet in weekly use.** Workflow v2 stays the operating process until the steps under "Path to the first live week" are done, which should be before the 2027 season starts.

## Goal

The weekly update becomes one button, one approval and a live progress page. The same code runs whether Patrick, ChatGPT or Claude presses the button. Choices made by Patrick on 24 November 2026:

- The pipeline runs on GitHub Actions; there is no server to host.
- The Google Sheet becomes an output only. Totals come from the pipeline, not from Sheet formulas.
- One human approval, before publication.

## What changes from v2

| | v2 (2026 season) | v3 |
|---|---|---|
| Start | Patrick approves a Start in chat | One button (live page, GitHub app, ChatGPT or Claude) |
| Data work | GPT reads sources, writes the Sheet, reads totals back, prepares a release | `race_week.py` collects, computes and checks in one run |
| Approvals | Start + exact release | One: publication of the computed totals |
| Hand-over | GPT writes a brief; Patrick pastes it into Claude | None: the approved job publishes |
| Publication | Claude builds, pushes and checks the live site | Jobs 4 and 5 do the same steps |
| Progress | Private runner page | Public live page from the Actions API; six points |
| Sheet | Master; formulas compute totals | Copy written after publication |
| Assistants | GPT phases 1–3, Claude phase 4 | Either one operates the whole run through the same API |

## Architecture

```
button / ChatGPT / Claude
        │  POST workflow_dispatch
        ▼
GitHub Actions: race-week.yml
  1 Collecte ──► 2 Calcul et contrôles ──► 3 Validation ──► 4 Publication ──► 5 Vérification ──► 6 Export Sheet
   sources        compute + checks          Patrick taps     stage, build,     live hashes        EXPORT tab
                  release.json manifest      Approve          push main         and title
        │ annotations (public)
        ▼
https://peozenou.github.io/race/run/   (polls the Actions API, ETag-cached)
```

The pipeline is one standard-library file, [tools/race_v3/race_week.py](../tools/race_v3/race_week.py). Each subcommand reads and writes plain folders, so every step can also be run by hand.

## Scoring, as the code now states it

- **Credited Race.** A player's credited Race for the new week is last week's credited value plus the change in his Tennis Explorer Race points. Approved transfer baselines (Lehecka from 2,055) and adjustments (Kouame +24) carry over without being restated. Outgoing players keep their retained snapshot.
- **Duels.** 5 points per win, walkovers included, over a player of another team, for matches before the Monday cutoff.
- **Team totals.** Race = sum of credited Race; Total = Race + duels.
- **Roster changes.** A player not in the previous release stops the run with "Roster change needs a decision". Transfers stay a deliberate decision.

Replaying from the git history of releases reproduces weeks 38, 39 and 40 (both r1 and r2) byte for byte, with every check passing. Week 37 contained the Engel→Blockx transfer correction, and the pipeline correctly stops there.

## Checks before approval

The new week is blocked if any of the following hold:

- HEBDO or JOUEURS history changed
- a released match disappeared, or a match id is duplicated
- a match is dated on or after the cutoff
- there are not 5 teams × 6 active players, or a player is selected twice
- Race + duels ≠ Total for a team
- a team's JOUEURS sum ≠ its HEBDO Race
- players' duel points ≠ HEBDO duels
- a team's duels decreased

A team whose Race fell is shown as a warning.

`stage` refuses any file whose hash changed after approval. `verify-live` compares all six served files and the page title with the approved manifest.

## Source adapters (the remaining build)

The skeleton's `collect` supports `replay:<dir>`. Live collection must port the reviewed v2 helpers:

1. **Tennis Explorer.** Race and ranking tables give `race_points`, `race_rank`, `atp_points`, `atp_rank` and the publication date. TE owns Race.
2. **Tennis Abstract.**
   - Each player's displayed Serve/Return tables give match records and statistics. Hidden raw data never fills a displayed blank.
   - The complete Elo and yElo reports give ratings and their true date.
3. **Matches.** New matches get the next `M` ids. Opponent team is resolved through the roster registry.

Run the source pilot first. If Tennis Abstract refuses GitHub's servers, switch `collect` to a self-hosted runner on Patrick's Mac (`runs-on: [self-hosted, macOS]`); every other job stays on GitHub.

## Outside this pipeline

- **Tiago UTR and MatchTrack** stay private and never enter this public repository.
- **Season set-up** (2027 folder, rosters after the draft, rules) is a one-off change reviewed by Patrick.
- **Dashboard design changes** remain Claude's normal work.

## Path to the first live week

| Step | Status |
|---|---|
| Pipeline, checks, manifest and progress events | Implemented; 9 tests pass; weeks 38–40 replay exactly |
| Workflow with approval gate, publication and live verification | Implemented; actionlint clean; the job chain was run locally against the live site |
| Live progress page and API (OpenAPI for ChatGPT, `gh` for Claude) | Implemented; page checked at desktop and mobile widths |
| Merge to main, create the `race-release` environment, run a dry run on GitHub | Pending Patrick's review |
| Source pilot from GitHub runners | Pending (needs the merge) |
| Live TA/TE adapters ported from the v2 helpers | Not started |
| 2027 season folder and roster | After the draft |
| Sheet export with a service account | Optional; code ready, secret not configured |
| First real week: run v3 alongside v2 and compare totals before switching | 2027 week 1 |
