# Step 6 production handover — release 2026-11-02-w37-r1 (week 37)

Owner: **Claude**. Prepared 2 November 2026, America/New_York. This is the public copy of the step-6 completion note for ChatGPT/Codex. The private copy additionally carries the cleared workbook fingerprint and approval records, which stay in private run storage (see [data and release contract](../../../data-and-releases.md#publicprivate-boundary)).

## Production result

| Field | Value |
|---|---|
| `owner` | Claude |
| `production_status` | `LIVE_DASHBOARD_VERIFIED` |
| `release_id` | `2026-11-02-w37-r1` (branch `data/2026-11-02-w37-r1`) |
| `data_commit_sha` | [`005231791f39eb6397c331726b4eeb8c9fc04e21`](https://github.com/peozenou/race/commit/005231791f39eb6397c331726b4eeb8c9fc04e21) |
| `dashboard_commit_sha` | [`7eadc7b130149fe2eecb86a4af1d3088f3faf44d`](https://github.com/peozenou/race/commit/7eadc7b130149fe2eecb86a4af1d3088f3faf44d) |
| Production history | `b04ca98` (previous main, Historique rework) → `0052317` (release data, fast-forward) → `7eadc7b` (week-37 build). The release branch sat directly on `b04ca98`, so all concurrent dashboard and history work on `main` is kept. |
| `dashboard_url` | https://peozenou.github.io/race/2026/ |
| `build_data_version` / `live_data_version` | `6eef7f8c31de` / `6eef7f8c31de` |
| `live_week` | 37, Monday 2 November 2026 (competition week, not ISO week) |
| `ui_checks_verified` | true (23 checks, 0 failures, dark and light, desktop and 375 px) |
| `live_verified_at` | 2026-11-02T18:02:34-05:00 (data fetch 17:59:26-05:00) |
| Deployment | GitHub Pages run [41541660989](https://github.com/peozenou/race/actions/runs/41541660989): build, report-build-status and deploy all success; deployment 7505559597, deploy job finished 2026-11-02T22:59:08Z. Served `index.html` byte-identical to the commit (SHA-256 `6ff07a462493ce0636f30a24b6c0975ebbec186df9582e1bf3ddf6383cdd428f`). |

### Live datasets

The step-6 request named the release ID, branch and commit but did not list SHA-256 values, so the approved hashes are those of the six files at release commit `0052317`, read from git before use. All six served files match them at the plain URL, with the page's `?v=` token, and through an in-page SHA-256 fetch in the browser:

| File | Rows | SHA-256 |
|---|---:|---|
| `hebdo.json` | 190 | `bd28076246549a7b6934150fc199e58ad05f4136d1edc9526d6bfc856b1baa6a` |
| `joueurs.json` | 1136 | `75f79e050b00a4060f7b2efefb0d14c3bb0b21e633eedfe77a6c8f65abb839d4` |
| `players.json` | 32 | `f37f92ec9d987604e3f7b12334c042800c4e0d955529abbe432eaca87965c31b` |
| `matches.json` | 1676 | `721922e5ebd1a1caa6be2a979b94b29d91882349481788599c0de36996b39250` |
| `calendar.json` | 13 | `a5b40cae611cf05229e6b7b572c035e7f19ec081a881804c64b611cdc7c9ba1a` |
| `team_colors.json` | 5 | `3ee69192269cf441b532cbeb47432effae3f202e1d02707ede686718ab315ca7` |

Checked before use: the release commit touches only the four weekly files. Weeks 0–36 of `hebdo` and `joueurs` are unchanged; week 37 adds 5 and 32 rows. The 1,607 previous match perspectives are kept in order, plus 69 new ones (`M1608`–`M1676`). One earlier perspective changed as cleared (`M1549` opponent rank 65 → 60); it was published as is.

### Verified on the live page

| Team | Race | Duels | Total | Change vs week 36 |
|---|---:|---:|---:|---:|
| CHEF | 18,809 | 195 | 19,004 | +450 |
| DOC | 16,800 | 150 | 16,950 | +542 |
| CHAN | 15,755 | 185 | 15,940 | +940 |
| PAT | 12,993 | 150 | 13,143 | +489 |
| JULES | 11,572 | 110 | 11,682 | +240 |

Grand total 76,719, up 2,661. Order CHEF, DOC, CHAN, PAT, JULES; CHEF leads DOC by 2,054. All 190 team-weeks satisfy Race + Duels = Total, and each team's week-37 JOUEURS sum equals its HEBDO Race.

- **Header.** « THE RACE 2026 — Bilan 37e semaine ». Takeaway: « Après la semaine 37 (2 nov. 2026), CHEF est devant avec 19 004 points, suivi de DOC. Meilleure progression de la semaine : CHAN (+940), notamment grâce à Alcaraz (+510). »
- **Sinner/Lehecka.** One CHEF line credited 8,435 (Sinner 7,950 in `#93c47d` + Lehecka 485 in `#678958`) and 75 duel points. The composition bar, post chart and player switch show both parts. Sinner's detail keeps his rankings at 5 Oct 2026.
- **Engel/Blockx.** One PAT line credited 757 (Engel 62 in `#8e7cc3` + Blockx 695 in `#635789`) and 5 duel points. The composition tooltip reads Engel (sorti) 62, Blockx (entré) 695, post total 757, 6 % of the team. Engel's detail keeps his rankings at 26 Oct 2026, as exported.
- **Kouame.** Credited 449 with the note: 425 raw Tennis Explorer Race + approved +24, applied once.
- **Nulls.** Rune's Elo, yElo and age show "—". The null aggregate rates (`tpw`, `rpw`, `ace_pct`, `first_won`, `second_won`) are not displayed, and no "NaN", "null" or "undefined" text appears.
- **Source dates**, shown separately from the competition Monday: Tennis Explorer rankings 2 Nov 2026 (retained: Engel 26 Oct, Sinner 5 Oct); Elo/yElo 28 Sep 2026; matches through 2 Nov 2026.
- **Historique.** The 2026 edition shows "en cours · sem. 37" with CHEF at 19,004, and the palmarès current column reads "sem. 37". The current edition is read from `2026/data`.

Browser checks (Claude desktop built-in browser, Chromium, on the live URL): 0 console errors; versioned data and history requests; standings cards and gains; season chart tooltip; duel matrix; 30-line player table, six per team under each team filter; search; sorting; composition two shades for both posts with tooltip; detail and player switch for Sinner/Lehecka and Engel/Blockx; Kouame and Rune details; Barème et sources tab; Historique tab; navigation between the four tabs; 375 px mobile width without horizontal scroll on every tab; `tutoriel.mp4` and the landing page served byte-identical to the repository.

### Dashboard source changes (datasets untouched)

The only change is the `RACE_QUAL` comment in `2026/source/dashboard.html`, which now references this release. Its entries are unchanged (Kouame's `adjust` only), since the handoff named no new hold or adjustment. The French interface, design, navigation, Historique tab, `history/` data and tutorial are unchanged. The preview image and tutorial were not regenerated.

## Accepted qualifications carried

- 69 historical zero cells lack matching saved source rows. This is not a general rule that missing means zero.
- Tennis Abstract omits the known Kouame loss at Jingshan.
- Elo/yElo remains dated 28 September 2026.
- The Historique tab's "rang actuel" (each former player's current ATP rank) reads `history/data/ranks.json`, which is still dated 26 October 2026 and labelled that way on the page. This release did not refresh the history export, and step 6 left it unchanged.

## Step 7

**Unblocked.** Use https://peozenou.github.io/race/2026/, bound to dashboard commit `7eadc7b` (data version `6eef7f8c31de`), verified live at 2026-11-02T18:02:34-05:00. Claude has not drafted or sent any email.

## Files

- [`completion.json`](completion.json): machine-readable completion note (public fields).
- [`evidence/live-data-7eadc7b.json`](evidence/live-data-7eadc7b.json): served page version, headers, the six dataset hashes in both URL variants, assets, tutorial and landing page.
- [`evidence/live-ui-7eadc7b.json`](evidence/live-ui-7eadc7b.json): browser-check results (23 named checks).
- `evidence/7eadc7b-01-composition-tooltip-light.jpg`: composition bar with both two-shade posts and the Engel/Blockx tooltip.
- `evidence/7eadc7b-02-notes-sources-light.jpg`: Barème et sources tab with transfers and source dates.
- `evidence/7eadc7b-03-players-pat-filter-dark.jpg`: Joueurs tab filtered to PAT (dark).
