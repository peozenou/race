# Phase 4 production handover — release 2026-11-16-w39-r1 (week 39)

Owner: **Claude**. Prepared 22 November 2026, America/New_York. This is the public copy of the phase-4 completion note. Private approvals and run fingerprints stay in private run storage (see [data and release contract](../../../data-and-releases.md#publicprivate-boundary)).

## Production result

| Field | Value |
|---|---|
| `owner` | Claude |
| `production_status` | `LIVE_DASHBOARD_VERIFIED` |
| `release_id` | `2026-11-16-w39-r1` (branch `codex/data/2026-11-16-w39-r1`) |
| `data_commit_sha` | [`10ef84eac40fe82d66c16ab4505b22f479f53eb0`](https://github.com/peozenou/race/commit/10ef84eac40fe82d66c16ab4505b22f479f53eb0) |
| `dashboard_commit_sha` | [`7c31bddbbdcad4455008148668edf411bd22558d`](https://github.com/peozenou/race/commit/7c31bddbbdcad4455008148668edf411bd22558d) |
| Production history | `67626ef` (previous main; still remote HEAD at start and just before the push) → `10ef84e` (release data, fast-forward) → `7c31bdd` (week-39 build). No concurrent work had to be merged. |
| `dashboard_url` | https://peozenou.github.io/race/2026/ |
| `build_data_version` / `live_data_version` | `03791704d6b6` / `03791704d6b6` (previous `a6518298bcdb`) |
| `live_week` | 39, Monday 16 November 2026 (competition week, not ISO week) |
| `ui_checks_verified` | true (0 console errors, desktop and mobile) |
| `live_verified_at` | 2026-11-22T10:44:22-05:00 |
| Deployment | GitHub Pages run [45039801511](https://github.com/peozenou/race/actions/runs/45039801511): build, report-build-status and deploy all success; deployment 7981033570, deploy job finished 2026-11-22T15:43:09Z. Served `index.html` is byte-identical to the commit (SHA-256 `944f29d2dc6c684dd749ee9deef695f00a461c1b1cb7c77af038c9bcb7d081dc`). |

### Live datasets

The handoff's six SHA-256 values were checked against release commit `10ef84e` before use. All six served files match them at the plain URL, with the page's `?v=03791704d6b6` token, and through an in-page SHA-256 fetch in the browser. No mix of old and new cached files was served.

| File | Rows | SHA-256 |
|---|---:|---|
| `hebdo.json` | 200 | `fbf69817fd76b85df67874a9af820e1530455c3dcb9881946402728bc07e3168` |
| `joueurs.json` | 1200 | `44b39816a2a1706fb3ba57ee709d2ba8a5fb6b30096ee9e1d8801c934ccafe1b` |
| `players.json` | 32 | `698af91176a32a600602af45eb3500eaf9d3652e9cfbae5be80065db70af7b24` |
| `matches.json` | 1751 | `527d0dbdafc12dd84aff01ce9ec32070765cdc5ee57db8fcf9d2e88c7a996fdc` |
| `calendar.json` | 13 | `a5b40cae611cf05229e6b7b572c035e7f19ec081a881804c64b611cdc7c9ba1a` |
| `team_colors.json` | 5 | `3ee69192269cf441b532cbeb47432effae3f202e1d02707ede686718ab315ca7` |

Checked before use: the release commit touches only the four weekly files. In `hebdo`, weeks 0–38 are unchanged and week 39 adds 5 rows. Every previous `joueurs` row is kept and week 39 adds 32, each equal to its week-38 value. The 1,726 previous match perspectives keep their order, IDs and results. 156 of them change only `level`, from Qualifications to their main-draw category (91 ATP 500/250, 42 Masters 1000, 23 Grand Chelem). 25 new perspectives are added (`M1727`–`M1751`), including four « Finales ATP » perspectives dated 15 November. Main-tour W/L changes for 26 players: the 25 with relabelled matches, plus Rune, whose change comes only from his three new week-39 ATP 500/250 matches.

### Verified on the live page

| Team | Race | Duels | Total | Change vs week 38 |
|---|---:|---:|---:|---:|
| CHEF | 18,939 | 195 | 19,134 | 0 |
| DOC | 16,971 | 170 | 17,141 | +15 |
| CHAN | 16,875 | 205 | 17,080 | 0 |
| PAT | 14,053 | 165 | 14,218 | +5 |
| JULES | 11,592 | 115 | 11,707 | 0 |

All 200 team-weeks satisfy Race + Duels = Total. Each team's week-39 JOUEURS sum equals its HEBDO Race.

- **Header.** « THE RACE 2026 — Bilan 39e semaine ». Takeaway: « Après la semaine 39 (16 nov. 2026), CHEF est devant avec 19 134 points, suivi de DOC. Meilleure progression de la semaine : DOC (+15). » The « notamment grâce à » clause is omitted by the generator because no lineup line has a positive JOUEURS gain this week. This follows from the approved unchanged-Race qualification, and DOC's gain is duels only.
- **Finales ATP.** In Arthur Fils's detail, the category table reads Grand Chelem 1–2, Finales ATP 0–1, Masters 1000 22–7, ATP 500/250 16–7, Qualifications 2–0. The latest match is 15 Nov, Finales ATP (Turin), Poule, lost to Ben Shelton 6-2 3-6 6-3.
- **Transfers.** 30 lineup lines from 32 player records. Sinner/Lehecka (CHEF, 8,435) and Engel/Blockx (PAT) remain single lines. The player switch reads « Lehecka (depuis le 12 oct.) » / « Sinner (jusqu’au 12 oct.) ».
- **Filters.** Team filter « Toutes les équipes, PAT, DOC, CHAN, CHEF, JULES »; PAT shows 6 lines.
- **Source dates**, shown separately from the competition Monday: Tennis Explorer rankings 16 Nov 2026 (retained: Engel 26 Oct, Sinner 5 Oct); Elo/yElo 16 Nov 2026; matches through 16 Nov 2026; HEBDO semaine 39, 16 Nov 2026.
- **Nulls.** No "NaN", "null" or "undefined" text on the Équipes or Historique tabs.
- **Historique.** Palmarès and all history figures draw, with no horizontal scroll at 390 px.
- **Tooltips.** The season-chart tooltip appears on hover.
- `tutoriel.mp4`, the landing page, `source/dashboard.html` and all three assets are served byte-identical to the commit.

The checks ran in headless Google Chrome (Playwright) in Claude's cloud workspace against the canonical URL at 1400 px and 390 px. The same checks passed on the locally built page before the push.

### Dashboard source changes (datasets untouched)

These are the release-driven changes for `atp-finals-category-2026`, both in `2026/source/dashboard.html`:

- « Finales ATP » is added to the existing `LEVELS` display order, after Grand Chelem. The placement follows the ranking-points tier, since no earlier ordering existed.
- It is also added to the `player_levels` accessible description.

There are no new JSON keys and no design change. `RACE_QUAL` is unchanged (Kouame `adjust` only), because the handoff named no new hold or adjustment. The preview image, tutorial and `history/` were not touched.

## Accepted qualifications carried

- QF category relabel (156 labels, 25 players' main-tour W/L); IDs, results, Race/Duels and earlier weekly figures unchanged.
- Finales ATP added as a level/event value with no new keys.
- 69 historical zeros lack saved primary rows (Rune 32, Bernet 29, Draper 4, Fonseca 3, Fils 1). This is not a general rule that missing means zero.
- Tennis Abstract still omits Kouame's Jingshan loss; his approved +24 Race adjustment is applied once.
- Some old PAT/DOC notes predate approved scoring corrections, without numerical effect.
- Five aggregate percentage fields remain null for the 30 active players: unavailable, not observed zero.
- DR is a descriptive unweighted mean of available match ratios. French Open statistics are source backfills, not new results.
- The Historique tab's « rang actuel » reads `history/data/ranks.json`, which this release did not refresh.
- Outgoing identities keep their older source dates (Engel 26 Oct, Sinner 5 Oct).
- All 30 Race values dated 16 November equal their 9 November values; Race gains are not inferred from tournament outcomes.

## Completion

Phase 4 is done and the week-39 v2 run is complete. There is no email phase, and Claude has not drafted or sent any email.

## Files

- [`completion.json`](completion.json): machine-readable completion note (public fields).
- [`evidence/live-data-7c31bdd.json`](evidence/live-data-7c31bdd.json): served page, the six dataset hashes in two URL variants, row counts, assets, tutorial and landing page.
- [`evidence/live-ui-7c31bdd.json`](evidence/live-ui-7c31bdd.json): browser-check results, including the in-page hashes.
- `evidence/7c31bdd-01-teams-1400.jpg`: header and standings.
- `evidence/7c31bdd-02-joueurs-fils-finales-1400.jpg`: players table with the Fils row selected.
- `evidence/7c31bdd-03-historique-390.jpg`: Historique tab at 390 px.
