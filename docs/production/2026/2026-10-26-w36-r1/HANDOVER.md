# Step 6 production handover — release 2026-10-26-w36-r1 (week 36)

Owner: **Claude**. Prepared 27 October 2026, America/New_York. This is the public copy of the step-6 completion note for ChatGPT/Codex. The private copy additionally carries the cleared workbook fingerprint and approval records, which stay in private run storage (see [data and release contract](../../../data-and-releases.md#publicprivate-boundary)).

## Production result

| Field | Value |
|---|---|
| `owner` | Claude |
| `production_status` | `LIVE_DASHBOARD_VERIFIED` for release r1 (presentation revision 4) |
| `release_id` | `2026-10-26-w36-r1` (branch `data-release/2026-10-26-w36-r1`) |
| `data_commit_sha` | [`3220344fc042fa9f471aaaaff475f9b82cfc66ef`](https://github.com/peozenou/race/commit/3220344fc042fa9f471aaaaff475f9b82cfc66ef) |
| `dashboard_commit_sha` | [`dbb14d51dbc5cac3b2574d5de4f6fe67e6fff5b1`](https://github.com/peozenou/race/commit/dbb14d51dbc5cac3b2574d5de4f6fe67e6fff5b1) |
| Production history | `6bb71bd` (previous main) → `3220344` (release data, fast-forward) → [`8fe2905`](https://github.com/peozenou/race/commit/8fe2905d6d357ec63d55d302b558374bac7b2389) (week-36 build) → `01aadc4` (docs only) → [`4e4b2b0`](https://github.com/peozenou/race/commit/4e4b2b0afd277077f7196e9d9713cfcecd9779fe) (players-table rank column) → `8548472` (docs only) → [`f98d2ad`](https://github.com/peozenou/race/commit/f98d2ad6a6f4f710de101b3fd1b12d85b7897901) (header title, takeaway, sources line) → `5a8dbb8` (docs only) → `dbb14d5` (composition card title and note). No concurrent changes on `main` to merge. |
| `dashboard_url` | https://peozenou.github.io/race/2026/ |
| `build_data_version` / `live_data_version` | `b65d0faa0c3a` / `b65d0faa0c3a` |
| `live_week` | 36, Monday 26 October 2026 (competition week, not ISO week) |
| `ui_checks_verified` | true (47 checks, 0 failures, light and dark) |
| `live_verified_at` | 2026-10-27T22:05:41-04:00 (data fetch 22:04:56-04:00) |
| Deployment | GitHub Pages run [40618760406](https://github.com/peozenou/race/actions/runs/40618760406): build, report-build-status and deploy all success; deployment 7375212458 success at 2026-10-28T02:04:54Z. Served `index.html` byte-identical to the commit (SHA-256 `c30cddaf7593e9e1733e3837c8cb48fb683b61487324bfad104e67e13e24a830`). |

Earlier production states, each verified live and superseded the same day at Patrick's request: `8fe2905` (data version `ae164c5669a3`, run [40493412269](https://github.com/peozenou/race/actions/runs/40493412269)) at 2026-10-27T07:06:46-04:00, and `4e4b2b0` (data version `7f446c6ee322`, run [40598150235](https://github.com/peozenou/race/actions/runs/40598150235)) at 18:54:34-04:00, and `f98d2ad` (data version `0a47e72f8a89`, run [40617701722](https://github.com/peozenou/race/actions/runs/40617701722)) at 21:55:09-04:00. All kept the six approved datasets unchanged. Later commits that touch only `docs/` do not change the dashboard: `git diff dbb14d5..HEAD -- 2026` is empty for them.

### Live datasets

All six served files match the approved step-5 hashes at the plain URL, with the page's `?v=` token, and through an in-page SHA-256 fetch in the browser:

| File | Rows | SHA-256 |
|---|---:|---|
| `hebdo.json` | 185 | `0c4e282a9a9b84379fdac6297edbf8564267a59dc0fe547943953c2fc0da0906` |
| `joueurs.json` | 1083 | `c0c6b7b4560a5dee605ebf6cf52f26e89bc74d1b774a5df10005a3f79ab06e06` |
| `players.json` | 31 | `5f43f14c1e2ee7c6fd107ff7ce4469b5b1e7349408dcf3f49b7afdb0475580e8` |
| `matches.json` | 1549 | `8ecad7b2aeccc02cb926a9bb0eb24b7617ad91c91c4b1d459398d9226cd030d6` |
| `calendar.json` | 13 | `a5b40cae611cf05229e6b7b572c035e7f19ec081a881804c64b611cdc7c9ba1a` |
| `team_colors.json` | 5 | `3ee69192269cf441b532cbeb47432effae3f202e1d02707ede686718ab315ca7` |

Before use: the release commit's diff from `main` touches only the four changed data files; the 1,508 previous match perspectives are unchanged and in order, plus 41 new ones (`M1509`–`M1549`).

### Verified on the live page

| Team | Race | Duels | Total | Change vs corrected week 35 |
|---|---:|---:|---:|---:|
| CHEF | 18,364 | 190 | 18,554 | +130 |
| DOC | 16,268 | 130 | 16,398 | +285 |
| CHAN | 14,825 | 175 | 15,000 | +375 |
| PAT | 11,824 | 140 | 11,964 | +38 |
| JULES | 11,332 | 110 | 11,442 | +355 |

Grand total 73,358, up 1,183. Order CHEF, DOC, CHAN, PAT, JULES; CHEF leads DOC by 2,156.

- **Corrected history.** All 185 team-weeks computed in the page satisfy Race + Duels = Total. Weeks 1 and 2 show the repaired totals (week 1: PAT 1,700, DOC 1,573, CHAN 3,390, CHEF 1,159, JULES 2,655). CHEF's week 35 is 18,424.
- **Sinner/Lehecka.** One CHEF line credited 8,145 (Sinner 7,950 in `#93c47d` + Lehecka 195 in `#678958`) and 75 duel points. Gains +25 last week, +195 over four weeks. Composition bar, its tooltip, the post chart bands and the player switch all show both parts. No "pending" wording remains anywhere on the page.
- **Kouame.** Credited 349 with the note: 325 raw Tennis Explorer Race + approved +24, applied once.
- **Bernet** is the current DOC selection; Machac does not appear.
- **Nulls.** Rune's Elo, yElo and age show "—". The null aggregate rates are not displayed.
- **Source dates** shown separately from the competition Monday: Tennis Explorer rankings 26 Oct 2026; Elo/yElo 28 Sep 2026; Sinner's retained rankings 5 Oct 2026; matches through 26 Oct 2026.

- **Rank column (revision 2).** Each line's place among the 30, with movement since week 35: Medvedev, Fils, Fritz, Musetti and Blanch ▲1; Cobolli, Tiafoe, Paul, Michelsen and Draper ▼1; the rest unchanged (=).

Browser checks (headless Chromium on the live URL, light and dark): 0 console errors, 0 page errors, 0 failed requests; standings cards; season, rank and gains charts with tooltip; duel matrix; 30-line player table, six per team under each team filter; sorting; search; detail views for Sinner/Lehecka (both players), Kouame, Bernet and Rune; Notes tab; tab navigation; 390 px mobile width without horizontal scroll; `tutoriel.mp4` served byte-identical to the repository.

### Dashboard source changes (datasets untouched)

`RACE_QUAL` in `2026/source/dashboard.html` now references this release and no longer lists Lehecka's hold, since his entry baseline (2,055) is confirmed and credited. The hold display would have switched itself off anyway; removing it records the resolved state. Kouame's adjustment entry stays. French interface, design, navigation and tutorial are unchanged.

**Revision 2 (`4e4b2b0`, requested by Patrick on 27 October).** The players table gains a sortable **Rang** column: each lineup line's place among the 30 lines by credited JOUEURS Race points, with ▲/▼ and the number of places moved since the previous week, or = when unchanged (hover gives the previous place). Ties share a place; a replacement line is ranked on the post total; the place stays the overall one under a team filter. It reuses the standings cards' ▲/▼ colours.

**Revision 3 (`f98d2ad`, requested by Patrick on 27 October).** Header title **THE RACE 2026 — Bilan 36e semaine** (also the page `<title>`, set in `build.py`; the week number follows HEBDO). Takeaway: « Après la semaine 36 (26 oct. 2026), CHEF est devant avec 18 554 points, suivi de DOC. Meilleure progression de la semaine : CHAN (+375), notamment grâce à Medvedev (+240). » The named player is the best-progressing team's line with the largest credited JOUEURS gain that week; ties are all named. The head note is replaced by « Sources : Tennis Abstract et Tennis Explorer », linking to tennisabstract.com and tennisexplorer.com.

**Revision 4 (`dbb14d5`, requested by Patrick on 27 October).** The composition card on the Joueurs tab is titled **Contributions par équipe**, with the note « Points Race de chaque joueur à la dernière mise à jour, total cumulé par équipe ; le détail par joueur s’obtient en passant dessus. » The tab's summary sentence already read « Zverev (DOC) compte le plus de points Race (9 150) … », so it was left as is.

## Accepted qualifications carried

- 69 historical zero cells lack matching saved source rows; this is not a general missing-equals-zero rule.
- Tennis Abstract omits the known Kouame loss at Jingshan.
- Elo/yElo remains dated 28 September 2026.

## Step 7

**Re-bind required.** Production changed after the first verification, so any step-7 receipt or draft bound to an earlier commit must be re-bound to dashboard commit `dbb14d5` (data version `b65d0faa0c3a`), verified live at 2026-10-27T22:05:41-04:00. The URL, week, datasets and totals are unchanged. Claude has not drafted or sent any email.

## Files

- [`completion.json`](completion.json): machine-readable completion note (public fields).
- [`evidence/live-data-dbb14d5.json`](evidence/live-data-dbb14d5.json) and [`evidence/live-ui-dbb14d5.json`](evidence/live-ui-dbb14d5.json) (current, 47 checks).
- [`evidence/live-data-f98d2ad.json`](evidence/live-data-f98d2ad.json) and [`evidence/live-ui-f98d2ad.json`](evidence/live-ui-f98d2ad.json) (revision 3, 45 checks); `evidence/f98d2ad-08-header-light.png`: live header.
- [`evidence/live-data-4e4b2b0.json`](evidence/live-data-4e4b2b0.json) and [`evidence/live-ui-4e4b2b0.json`](evidence/live-ui-4e4b2b0.json) (revision 2, 43 checks); `evidence/4e4b2b0-*.png`: live players table with the rank column.
- [`evidence/live-data-8fe2905.json`](evidence/live-data-8fe2905.json) (first state): served page version, headers, the six dataset hashes in both URL variants, tutorial and landing page.
- [`evidence/live-ui-8fe2905.json`](evidence/live-ui-8fe2905.json): browser-check output, light and dark, with the 40 named checks.
- `evidence/8fe2905-*.png`: live screenshots (teams, CHEF composition with tooltip in light and dark, Sinner/Lehecka detail for each player, Notes tab, mobile).
