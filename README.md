# THE RACE

THE RACE is a fantasy tennis league with five teams. This repository holds the public season dashboards and the approved professional-player data they use.

[All seasons](https://peozenou.github.io/race/) · [2026 dashboard](https://peozenou.github.io/race/2026/)

Repository documentation is maintained in English. Existing worksheet names, JSON field names and the dashboard's French interface retain their established names.

## Start here

- [Weekly update workflow](docs/weekly-workflow.md): the six-step sequence, individual skill triggers, Sunday/Monday handoff, audit clearance and progress tracking.
- [Dashboard data and release contract](docs/data-and-releases.md): the six JSON datasets, source authority, transfer history, validation and the handoff to Claude.

## Contributors and responsibilities

ChatGPT/Codex and Claude contribute to the process, with Patrick making the final decisions.

| Contributor | Main responsibilities |
|---|---|
| ChatGPT / Codex | Source acquisition, Google Sheets updates, audits, progress tracking, cleared GitHub data exports and unsent Gmail drafts; independent Elo and private-statistics workflows |
| Claude | Dashboard development and updates using the approved GitHub data release, including the dashboard source, presentation and release checks |
| Patrick | Final data clearance, roster/scoring decisions and explicit email-sending authorization |

GitHub is the shared handoff point. Each contributor checks the latest repository state and preserves the other's changes. Handoffs are explicitly triggered; automatic communication between ChatGPT/Codex and Claude is not configured. See [contributors and handoff](docs/weekly-workflow.md#contributors-and-handoff) for the collaboration contract.

## Weekly process

The Race update runs in this order:

| Step | Task | Codex skill |
|---|---|---|
| 1 | Update player statistics from Tennis Abstract's displayed Serve/Return tables | `$race-update-ta` |
| 2 | Update Tennis Explorer ranking tables in LIVE and the frozen weekly snapshot | `$race-update-te` |
| 3 | Update HEBDO, TEAMS, JOUEURS, BILAN and derived team calculations | `$race-update-summary` |
| 4 | Verify steps 1–3 and obtain Patrick's clearance of the reviewed state | `$race-audit` |
| 5 | Export the cleared data to this repository's existing JSON data store | `$race-export-dashboard` |
| 6 | Prepare and verify an unsent weekly Gmail draft | `$race-draft-email` |

`$update-the-race` coordinates the sequence, displays all six steps and resumes the first incomplete step of the identified run. Each step can also be triggered separately. Step 5 waits for Patrick's explicit clearance at step 4.

Two tasks run independently of that sequence and each other:

- `$tennis-update-elo`: update the separate Elo-Import workbook from both complete Tennis Abstract Elo/yElo reports. Unchanged reports do not hold up Race.
- `$tiago-update-data`: maintain private MatchTrack statistics and user-supplied UTR observations. Its two submodules have separate outcomes; their data stays outside this public repository.

Step 1 can begin provisionally on Sunday. Monday's cutoff and pending-result recheck completes it before steps 2–6 proceed. These are on-demand workflows; documenting them does not configure a schedule. Routine HEBDO/BILAN PNG production has been removed.

The skills and local progress helpers are installed in Patrick's Codex environment. This repository documents their operating contract; cloning it does not install skills or grant access to Sheets, Gmail or private data.

## Repository layout

| Path | Purpose |
|---|---|
| `index.html` | Season landing page |
| `2026/` | Published 2026 dashboard |
| `2026/data/` | Approved JSON data for the dashboard |
| `2026/source/dashboard.html` | Dashboard source maintained with Claude |
| `2026/assets/` | Data-loading runtime, theme and vendored d3 v7.9.0 |
| `2026/tools/build.py` | Build `2026/index.html` and its data-version token |
| `2026/tools/preview.py` | Optional social-preview image generation |
| `2026/tools/tutorial.py` | Optional tutorial recording |
| `2026/tutoriel.mp4` | Dashboard navigation tutorial |
| `docs/` | Workflow and data-release documentation |

A historical season can have its own directory, such as `2025/`, and a corresponding landing-page entry. Resolve its actual workbook and data contract before adding it. Current acquisition adapters are season-specific.

## Publish an approved data release

After steps 1–4 and Patrick's clearance, step 5 prepares a complete candidate release from the reviewed workbook state, validates all six JSON datasets and checks the current repository head. It commits only the intended release files and any necessary generated page output, then verifies them from GitHub.

When data or dashboard source changes, rebuild the generated page from the repository root:

```sh
python3 2026/tools/build.py
```

The builder reads all six JSON files and `2026/source/dashboard.html`. It updates the generated page's metadata and cache-version token. A documentation-only change does not require this build. Preview images and tutorial recordings are separate, optional tasks.

Keep three outcomes distinct: **data exported to GitHub**, **dashboard rebuilt**, and **live dashboard verified**. Check the served data and page version before claiming the live site contains a release. Step 6 may prepare the email after a verified data export while a dashboard refresh is pending, provided the draft describes that state accurately. A saved or validated draft is not authorization to send it.

## Sources and history

Tennis Abstract's displayed player tables own match statistics; its complete Elo/yElo reports own ratings. Tennis Explorer owns Race/ATP ranking snapshots. Approved league rules and transfer records own fantasy scoring. Preserve their separate source dates and missing-value meanings.

There are 30 active selections, six per team. Published history can include outgoing players as well as the active roster, so public datasets can contain more than 30 player records. Preserve approved transfer credit and frozen history rather than filtering everything down to the current selection.

See the [data and release contract](docs/data-and-releases.md) for validation, publication and rollback details. d3 is distributed under the ISC license, copyright Mike Bostock.
