# Step 6 production handover — release 2026-11-09-w38-r1 (week 38)

Owner: **Claude**. Prepared 9 November 2026, America/New_York. This is the public copy of the step-6 completion note for ChatGPT/Codex. The private copy additionally carries the cleared workbook fingerprint and approval records, which stay in private run storage (see [data and release contract](../../../data-and-releases.md#publicprivate-boundary)).

## Production result

| Field | Value |
|---|---|
| `owner` | Claude |
| `production_status` | `LIVE_DASHBOARD_VERIFIED` |
| `release_id` | `2026-11-09-w38-r1` (branch `codex/data/2026-11-09-w38-r1`) |
| `data_commit_sha` | [`80dd9c93e80f058cfd2cc7dca31dd2f17b9341ef`](https://github.com/peozenou/race/commit/80dd9c93e80f058cfd2cc7dca31dd2f17b9341ef) |
| `dashboard_commit_sha` | [`28ed160e1c87beeaaf567e42fca96e824821bc86`](https://github.com/peozenou/race/commit/28ed160e1c87beeaaf567e42fca96e824821bc86) |
| Production history | `3ac21c9` (previous main; still remote HEAD when work started and just before the push) → `80dd9c9` (release data, fast-forward) → `28ed160` (week-38 build). No concurrent work had to be merged. |
| `dashboard_url` | https://peozenou.github.io/race/2026/ |
| `build_data_version` / `live_data_version` | `a6518298bcdb` / `a6518298bcdb` (previous `f130955966ac`) |
| `live_week` | 38, Monday 9 November 2026 (competition week, not ISO week) |
| `ui_checks_verified` | true (25 checks, 0 failed, 0 console errors) |
| `live_verified_at` | 2026-11-09T18:57:46-05:00 |
| Deployment | GitHub Pages run [42724243586](https://github.com/peozenou/race/actions/runs/42724243586): build, report-build-status and deploy all success; deployment 7669403633, deploy job finished 2026-11-09T23:55:24Z. Served `index.html` byte-identical to the commit (SHA-256 `100f1d11aa61aac58e180b87b8d7852fb80d2d5849261507f939ea6401fdb7ca`). |

### Live datasets

The handoff's six SHA-256 values were checked against release commit `80dd9c9` before use. All six served files match them at the plain URL, with the page's `?v=a6518298bcdb` token and through an in-page SHA-256 fetch in two browser sessions. No mix of old and new cached files was served.

| File | Rows | SHA-256 |
|---|---:|---|
| `hebdo.json` | 195 | `0ab8245921f138b8f6f30160d1565780a0db615dbdc43eedf971092746515da2` |
| `joueurs.json` | 1168 | `054a9835699f79150d2b826a829fa7628929b47210d50a9805c0e0e0e01917f4` |
| `players.json` | 32 | `f0982f1a5f0f9ab9da22877eaed9df9001174c2c09eff197655472ffa243e7f4` |
| `matches.json` | 1726 | `3375a378f65d05f46957d6f49e746e67e09eeeff3a33bb369972bb0efaee0349` |
| `calendar.json` | 13 | `a5b40cae611cf05229e6b7b572c035e7f19ec081a881804c64b611cdc7c9ba1a` |
| `team_colors.json` | 5 | `3ee69192269cf441b532cbeb47432effae3f202e1d02707ede686718ab315ca7` |

Checked before use: the release commit touches only the four weekly files. Weeks 0–37 of `hebdo` are unchanged and week 38 adds 5 rows. Every previous `joueurs` row is kept and week 38 adds 32. The 1,676 previous match perspectives are kept in order, plus 50 new ones (`M1677`–`M1726`). The two approved score-spelling corrections keep their IDs: `M1407` and `M1425`, « 7-5 5-3 Def. » → « 7-5 5-3 DEF ».

### Verified on the live page

| Team | Race | Duels | Total | Change vs week 37 |
|---|---:|---:|---:|---:|
| CHEF | 18,939 | 195 | 19,134 | +130 |
| DOC | 16,971 | 155 | 17,126 | +176 |
| CHAN | 16,875 | 205 | 17,080 | +1,140 |
| PAT | 14,053 | 160 | 14,213 | +1,070 |
| JULES | 11,592 | 115 | 11,707 | +25 |

The grand total is 79,260, up 2,541. The order is CHEF, DOC, CHAN, PAT, JULES, and CHEF leads DOC by 2,008. All 195 team-weeks satisfy Race + Duels = Total, and each team's week-38 JOUEURS sum equals its HEBDO Race.

- **Header.** « THE RACE 2026 — Bilan 38e semaine ». Takeaway: « Après la semaine 38 (9 nov. 2026), CHEF est devant avec 19 134 points, suivi de DOC. Meilleure progression de la semaine : CHAN (+1 140), notamment grâce à Alcaraz (+990). »
- **Sinner/Lehecka.** One CHEF line is credited 8,435 (Sinner 7,950 in `#93c47d` + Lehecka 485 in `#678958`) with 75 duel points. The composition bar, its tooltip, the post chart and the player switch all show both parts. Sinner's detail keeps his rankings at 5 Oct 2026.
- **Engel/Blockx.** One PAT line is credited 747 (Engel 62 in `#8e7cc3` + Blockx 685 in `#635789`) with 5 duel points. The tooltip reads Engel (sorti) 62, Blockx (entré) 685, post total 747, 5 % of the team. Engel's detail keeps his rankings at 26 Oct 2026.
- **Kouame.** Credited 449* with the note: 425 raw Tennis Explorer Race + approved +24, applied once.
- **Holds.** None. No pending incoming contribution is displayed.
- **Nulls.** Rune's Elo shows "—". The five null aggregate rates (`tpw`, `rpw`, `ace_pct`, `first_won`, `second_won`) are not displayed, and no "NaN", "null" or "undefined" text appears on any tab.
- **Source dates**, shown separately from the competition Monday:
  - Tennis Explorer rankings 9 Nov 2026 (retained: Engel 26 Oct, Sinner 5 Oct).
  - Elo/yElo 28 Sep 2026.
  - Matches through 9 Nov 2026.
  - Duel matrix as of 9 Nov 2026.
- **Joueurs tab.** 30 lineup lines from 32 player records, six per team under every team filter. The « Rang » column shows ▲/▼/=, and search works.
- **Historique.** The palmarès current column reads "sem. 38". All five history figures draw.

The checks ran in headless Google Chrome (Playwright) in Claude's cloud workspace against the live canonical URL, in light mode at 1280 px and dark mode at 375 px:
- 0 console errors, and versioned data and history requests.
- Standings cards and gains, the season-chart tooltip and the duel matrix.
- The player table, team filters, search, the composition bar's two shades with tooltips, and the detail views and player switches for both replacement lines.
- The Kouame and Rune qualifications, the Barème et sources tab and the Historique tab.
- The page is exactly 1280 px and 375 px wide on all four tabs, with no horizontal scroll.
- `tutoriel.mp4`, the landing page and both assets are served byte-identical to the repository.

### Dashboard source changes (datasets untouched)

The only source change is the `RACE_QUAL` comment in `2026/source/dashboard.html`, which now references this release. Its entries are unchanged (Kouame's `adjust` only) because the handoff named no new hold or adjustment. The preview image, tutorial and `history/` were not touched.

### Observation (no action taken)

The Engel/Blockx line moved from 757 to 747 (−10). Blockx's raw Tennis Explorer Race went from 1,650 (2 Nov) to 1,640 (9 Nov), and his credited value is 1,640 − 955 entry baseline = 685, consistent with the approved rule. Race can legitimately decrease in a published ranking, so this cleared value is shown unchanged.

## Accepted qualifications carried

- 69 historical zeros lack saved primary rows (Rune 32, Bernet 29, Draper 4, Fonseca 3, Fils 1). This is not a general rule that missing means zero.
- Tennis Abstract still omits Kouame's known Jingshan loss.
- Retained Elo/yElo is dated 28 September 2026; Rune's six ratings and age remain null.
- Some old PAT/DOC notes predate approved scoring corrections, without numerical effect.
- For the 30 active players the five aggregate percentage fields are null because opportunity counts are absent. They are not presented as observed zero.
- DR remains a descriptive mean of available match ratios, not a pooled season rate.
- The Historique tab's "rang actuel" reads `history/data/ranks.json`, which this release did not refresh.

## Step 7

**Unblocked.** Use https://peozenou.github.io/race/2026/, bound to dashboard commit `28ed160` (data version `a6518298bcdb`), verified live at 2026-11-09T18:57:46-05:00. Claude has not drafted or sent any email.

## Files

- [`completion.json`](completion.json): machine-readable completion note (public fields).
- [`evidence/live-data-28ed160.json`](evidence/live-data-28ed160.json): served page, the six dataset hashes in all three variants, assets, tutorial and landing page.
- [`evidence/live-ui-28ed160.json`](evidence/live-ui-28ed160.json): browser-check results (25 named checks).
- `evidence/28ed160-01-teams-light-1280.jpg`: header and standings.
- `evidence/28ed160-02-composition-light-1280.jpg`: composition bar with both two-shade posts and the Sinner/Lehecka tooltip.
- `evidence/28ed160-03-detail-sinner-lehecka-dark-375.jpg`: Joueurs tab at 375 px with the qualification note and the Sinner/Lehecka player switch.
- `evidence/28ed160-04-historique-dark-375.jpg`: Historique tab at 375 px.
