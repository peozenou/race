# Phase 4 — Claude dashboard production

**Owner: Claude.** Update, build, publish and verify the Race dashboard from the exact approved data release handed off in phase 3. This is the final phase of workflow v2; there is no weekly email task.

The sequence is: **GPT collects → GPT validates and Patrick approves the exact candidate → GPT releases and prepares the handoff → Claude publishes and verifies live**. Patrick explicitly invokes Claude with that handoff.

## Required handoff

Before starting, obtain the phase-3 handoff through Patrick or the agreed repository release context:

- Release ID and dedicated data-release branch/commit.
- SHA-256 hashes for all six approved JSON files: hebdo, joueurs, players, matches, calendar and team_colors.
- Target season, competition week/date, match cutoff and actual ranking/rating source dates.
- Five approved team totals, retained transfer credit/holds, missingness and source qualifications.
- Previous production commit/version, actual public season URL and the requested dashboard checks.
- Confirmation that Patrick cleared this same data state; detailed approval evidence and private run fingerprints stay in private run storage.

Read the latest [weekly workflow](run-contract.md), [data contract](dashboard-contract.md), repository instructions and current remote HEAD. Verify the release's file hashes and preserve concurrent dashboard/source/tutorial changes. A stale local checkout is not a safe production baseline.

The current public season URL is [THE RACE 2026](https://peozenou.github.io/race/2026/). Resolve the correct URL and compatible build/data contract before publishing another season.

## Update and build

Incorporate the exact six-file approved release. Update the dashboard as needed to reflect that release, including current week/date, source labels, transfer state, tables and charts. Preserve the established French interface, existing design and unrelated work unless Patrick requests a broader change. A routine weekly production task does not authorize an unrelated redesign.

Transfers are presented as described in [replacement lines on the dashboard](dashboard-contract.md#replacement-lines-on-the-dashboard). The dashboard shows one `outgoing/incoming` line per post. The outgoing player's part uses the team colour and the incoming player's part a darker shade of it. When the handoff names a new held contribution or approved Race adjustment, add it to `RACE_QUAL` in the dashboard source.

### Approved dashboard wording (Patrick, 27 October 2026)

Keep this wording and these presentation choices in every weekly build. They are generated from the data, so a routine release needs no text edit:

| Element | Approved form |
|---|---|
| Header title and page `<title>` | `THE RACE 2026 — Bilan <n>e semaine` (week from HEBDO; the page title is set in `build.py`) |
| Header summary | « Après la semaine <n> (<date>), <1st> est devant avec <total> points, suivi de <2nd>. Meilleure progression de la semaine : <team> (+<gain>), notamment grâce à <player> (+<gain>). » The player is the best-progressing team's lineup line with the largest credited JOUEURS gain that week; ties are all named. |
| Header source line | « Sources : Tennis Abstract et Tennis Explorer », linking to https://www.tennisabstract.com/ and https://www.tennisexplorer.com/ |
| Joueurs tab summary | « <player> (<team>) compte le plus de points Race (<pts>) ; <player> (<team>) a le meilleur rendement, avec <n> points par tournoi. » |
| Team composition card | Title « Contributions par équipe »; note « Points Race de chaque joueur à la dernière mise à jour, total cumulé par équipe ; le détail par joueur s’obtient en passant dessus. » |
| Players table | First column « Rang »: place among the 30 lineup lines by credited Race points, with ▲/▼ and places moved since the previous week, or = when unchanged |

Do not silently modify cleared league data or scoring rules to make the presentation agree. If a data/identity/transfer issue is discovered, return it to the owning data/audit step and wait for the affected state to be verified and cleared again.

### Historique tab

The **Historique** tab reads the league history from `history/data/` (seasons, hebdo, rosters, players, ranks, calendar), loaded only when the tab opens, and takes the current edition from the six weekly files. A routine weekly release needs no history change: the current edition's standings, rosters and transfers update with `2026/data/`. Two inputs are refreshed by hand when useful: `history/data/ranks.json` (`python3 -I history/tools/player_ranks.py SRC_DIR`, current ATP rank from the latest dated tab) and `history/race_history.sqlite` (`python3 -I history/tools/consolidate.py`). The edition notes shown in the tab (`HIST_NOTES` in the source) are French summaries of `history/README.md`. At season end, the finished edition is added to `history/` before the next season's folder is created.

From the repository root, run the existing builder:

```sh
python3 2026/tools/build.py
```

The builder reads the six JSON files, the history files used by the Historique tab and `2026/source/dashboard.html`, then writes `2026/index.html` with the data-version token and current metadata. Verify the built page references the intended release/version. Do not regenerate the optional preview image or tutorial, or change assets/source unrelated to the release, without a separate need or request.

## Publish

Check current production HEAD immediately before publishing. Incorporate the approved data and required generated page/source changes together into the production commit, preserving concurrent changes. Keep the release commit traceable in the production note. Use the repository's actual configured GitHub Pages publication route; do not invent a deployment workflow or assume a fixed completion delay.

A successful commit, push or build is an intermediate result. If deployment is still running, failed or serving cached older files, record the exact status and resume point. Do not claim production complete until the actual served result is checked. No background monitor is configured merely by this runbook.

## Verify the live dashboard

Verify the canonical public dashboard URL in a browser and compare it with the release and production commits:

1. All six served JSON datasets match the approved phase-3 hashes. Confirm that a mixture of old/new cached files is not being served.
2. The served page's data-version token matches the verified build, and the page loads without release-related errors.
3. The intended competition week/date and all five team totals match the approved release. Preserve true source dates separately from the competition Monday.
4. Player/team filters, ranking/statistics tables, player history and team-history charts work with the actual active/archived transfer representation. Each team shows six lineup lines. A replacement line adds both players' credited points, shows its two shades in the composition bar and post chart, and switches between the two players in its detail view.
5. Approved source qualifications, retained outgoing credit, incoming holds and null meanings are represented accurately. Missing data is not silently presented as an observed zero.
6. Existing navigation, tooltip and tutorial behavior remains intact within the affected scope.

Save actual verification time and evidence. A cache-busting request can help diagnose stale publication, but the verified completion note must identify the canonical public dashboard link. A stale or wrong release is a failed/pending production check, not an acceptable freshness qualification.

## Completion handoff to ChatGPT/Codex

Return a concrete completion note to Patrick/the coordinator. Include:

| Field | Meaning |
|---|---|
| `owner` | `Claude` |
| `production_status` | `LIVE_DASHBOARD_VERIFIED` only after the checks above |
| `release_id`, `data_commit_sha` | The exact approved phase-3 data release |
| `dashboard_commit_sha` | The actual production build/publication commit |
| `dashboard_url` | The verified canonical public season URL for the completed release |
| `live_data_sha256` | All six served dataset hashes matching the approved release |
| `build_data_version`, `live_data_version` | Matching built and served versions |
| `live_week` | The verified competition week |
| `ui_checks_verified` | Actual browser-check result, not a build-only assertion |
| `live_verified_at` | Timezone-aware timestamp of the real live observation |
| Evidence references | Claude completion, production/deployment details and served data/browser checks |

Claude also saves a public copy of the completion note, without the workbook fingerprint or approval records, with its live evidence under `docs/production/<season>/<release_id>/` (for example [2026-10-19-w35-r1](https://github.com/peozenou/race/blob/main/docs/production/2026/2026-10-19-w35-r1/HANDOVER.md)).

The private coordinator receipt also binds the same approved release snapshot digest, saves Claude's actual completion evidence and records the immutable receipt hash. Do not upload private approvals, junior data or personal account details merely to supply that evidence. A receipt's assertion is not a substitute for inspecting the real result.

After verification, phase 4 becomes done (or a specifically accepted bounded qualification with the correct live release) and the v2 weekly run is complete. Do not create or send email, or touch existing drafts.

If production changes after verification, reverify the affected production state while preserving the immutable approved data release. A volatile LIVE import outage alone does not revoke it. A real correction to frozen data or rules creates a linked candidate revision and renewed affected approval. Preserve prior commits and completion notes; legacy drafts remain untouched.

## Ownership and invocation

Patrick explicitly invokes Claude for this production task. Preparing a handoff does not automatically message, start or impersonate Claude. ChatGPT/Codex's `$race-publish-dashboard` skill prepares the handoff, tracks `awaiting_claude`, checks the returned evidence and updates the shared progress record. It does not substitute a Codex-run build for the Claude-owned production stage.

Example request to Claude:

> Run phase 4 using the approved phase-3 release identified in this handoff. Follow `docs/claude-dashboard-production.md`: update, build, publish and verify the Race dashboard, preserve concurrent work, and return the production commit, verified dashboard URL, data/version evidence and completion note to finish the weekly run.

## Implementation and notification state

Workflow v2 was approved on 10 November 2026. The private v2 runner records phase 4 only from evidence consistent with phase 3 and the sealed release. It does not impersonate Claude or independently certify source truth. Read its [receipt contract](runner-contract.md) before returning the completion payload. Historical production notes may retain their original step-6/step-7 terminology; they are immutable evidence, not current instructions.

The readiness notification pilot and scheduler activation are separate from dashboard publication. A production completion note does not assert that an iPhone notification was delivered.
