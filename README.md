# THE RACE

THE RACE is a five-team fantasy tennis league. This repository holds the public dashboards, approved professional-player datasets and the versioned weekly workflow.

[All seasons](https://peozenou.github.io/race/) · [2026 dashboard](https://peozenou.github.io/race/2026/)

## Weekly workflow v2

Patrick approved this design on **10 November 2026**. New weekly runs have four visible phases and two routine decisions. The former email task is removed. Historical seven-step runs and existing email drafts remain unchanged.

| Phase | Owner | Verified result | Weight |
|---|---|---|---:|
| 1. Collect | GPT | Complete source evidence and bounded, verified Sheet updates | 35% |
| 2. Validate and review | GPT; Patrick approves | Independent checks and approval of the exact frozen candidate | 30% |
| 3. Release and hand over | GPT | Six-file data commit, remote readback and Claude handoff | 10% |
| 4. Publish and verify | Claude | Successful deployment, matching served data/version and browser checks | 25% |

The two routine decisions are **Start under the approved write profile** and **Approve this exact release**. Routine in-profile TA, TE and summary writes do not each require another permission request. A new roster/rule/history change or other out-of-profile exception still needs a specific decision. Patrick currently invokes Claude explicitly with the prepared handoff; automatic cross-assistant dispatch is not implemented.

The progress bar counts verified work, not elapsed time. A source/approval/Claude wait stops the bar and names the next action. Only verified live production reaches 100%.

## Start here

- [Weekly operating workflow](docs/weekly-workflow.md): phases, approvals, weekly independent lanes, recovery and progress.
- [Approved write profile](docs/standard-write-profile.md): permitted routine operations and exceptions.
- [Data and release contract](docs/data-and-releases.md): source authority, six schemas, transfers and immutable release boundary.
- [Claude production runbook](docs/claude-dashboard-production.md): phase-4 build, publication and live checks.
- [Runner and receipt contracts](tools/race_v2/README.md): deterministic private-state runner; actual connector actions remain skills-owned.
- [Reference deck](docs/workflow-v2-review/process.html) · [PDF](docs/workflow-v2-review/process.pdf) · [Quarto source](docs/workflow-v2-review/process.qmd).
- [Progress preview](docs/workflow-v2-review/progress.html): synthetic examples, not a live monitor.
- [Installable skills](skills/README.md): portable package without private configuration or credentials.

## Sunday watch and independent weekly lanes

The approved readiness checkpoints are **Sunday 18:00 and 21:00; Monday 00:30 and 08:30, America/New_York**. The watch checks the relevant roster results on TA, requests Start once per competition week, and never treats notification delivery as approval. Sunday Start is provisional until Monday cutoff and actual TE publication are verified.

**Notification activation is pending the pilot.** Documentation and inactive schedule suggestions do not prove unattended TA access or iPhone delivery. The computer/app, source adapter, private state and real phone delivery/deduplication tests must pass before activation. See [readiness and notification pilot](docs/notification-pilot.md).

Two weekly lanes run independently of Race and each other:

- **Elo + yElo:** GPT checks both complete TA reports, preserves their actual dates, imports a new verified dated pair when advanced, and makes zero writes when unchanged. A Race release explicitly selects one frozen pair; a later Elo update cannot silently replace it.
- **Tiago UTR:** Patrick supplies the weekly value and date/week meaning. GPT updates the private Sheet and private dashboard, with backup/provenance/readback. Missing input remains pending; no UTR scraping or fabricated observation. MatchTrack remains a separate private submodule.

The Start request can include the pending UTR value/week input so no separate ping is needed. A configured independent Elo append runs under Start only if its own private binding/scope is included. Show these statuses beneath the Race progress bar, outside its percentage denominator. Missing UTR or unchanged/delayed independent Elo does not block Race. No junior data is published here.

## Authority and ownership

TA displayed Serve/Return tables own match statistics; complete TA Elo/yElo reports own ratings; Tennis Explorer owns Race/ATP rankings; approved rules and transfers own league scoring. Preserve blanks, actual publication dates and earned outgoing credit. Thirty active selections do not imply 30 public rows: resolve the current complete active/archived set from the registry and ledger.

After approval, the immutable source/release snapshot and six commit hashes are the authority. A later volatile LIVE import outage is a maintenance warning, not a reason to revoke an unchanged frozen release. A real correction creates a linked revision and renewed affected review.

GPT owns acquisition, data checks and release. Claude owns dashboard changes, build, production and live verification. Patrick owns Start, release clearance and nonroutine decisions. There is no automatic email task or authority to send existing drafts.

## Repository layout and build

| Path | Purpose |
|---|---|
| 2026/data/ | Existing six approved JSON datasets |
| 2026/source/dashboard.html | Claude-maintained French dashboard source |
| 2026/tools/build.py | Existing generated-page/version builder |
| 2026/assets/ | Runtime, theme and vendored d3 |
| history/ | Historical edition inputs; preserve unrelated work |
| docs/production/ | Public production notes/evidence, without private approvals |
| tools/race_v2/ | Deterministic four-phase private-state runner and tests |
| skills/ | Versioned installable skills and shared public contracts |

From the repository root, run **python3 2026/tools/build.py** after an approved data/source change. Claude verifies and publishes the matching data/generated page together. Documentation-only changes do not require rebuilding the dashboard. Preview images and tutorial regeneration are separate optional tasks.

This repository must not contain private workbook configuration, approvals, junior statistics, mail records, credentials or notification subscriptions. A future private owner app and a public read-only companion can share versioned run/release contracts; GitHub Pages alone is not an authenticated approval backend. Free app distribution does not imply free model/backend operation.

Repository documentation is English; existing worksheet names, JSON keys and French interface wording stay established. d3 is distributed under the ISC license, copyright Mike Bostock.
