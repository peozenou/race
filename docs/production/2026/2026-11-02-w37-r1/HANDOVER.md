# Step 6 production handover — release 2026-11-02-w37-r1 (week 37)

Owner: **Claude**. Prepared 2 November 2026, America/New_York. This is the public copy of the step-6 completion note for ChatGPT/Codex. The private copy additionally carries the cleared workbook fingerprint and approval records, which stay in private run storage (see [data and release contract](../../../data-and-releases.md#publicprivate-boundary)).

## Production result

| Field | Value |
|---|---|
| `owner` | Claude |
| `production_status` | `LIVE_DASHBOARD_VERIFIED` for release r1 (presentation revision 3) |
| `release_id` | `2026-11-02-w37-r1` (branch `data/2026-11-02-w37-r1`) |
| `data_commit_sha` | [`005231791f39eb6397c331726b4eeb8c9fc04e21`](https://github.com/peozenou/race/commit/005231791f39eb6397c331726b4eeb8c9fc04e21) |
| `dashboard_commit_sha` | [`aab1ce9798db008f166e182e5f6ad74ac83873dd`](https://github.com/peozenou/race/commit/aab1ce9798db008f166e182e5f6ad74ac83873dd) |
| Production history | `b04ca98` (previous main, Historique rework) → `0052317` (release data, fast-forward) → [`7eadc7b`](https://github.com/peozenou/race/commit/7eadc7b130149fe2eecb86a4af1d3088f3faf44d) (week-37 build) → `a9d6317` (docs only) → [`f330aa8`](https://github.com/peozenou/race/commit/f330aa81a93e759ab180bc22e1a4a4073286b3e7) (Historique heatmap, lollipop and waffle) → `e31df13` (docs only) → `aab1ce9` (wrap long transfer names). The release branch sat directly on `b04ca98`, so all concurrent dashboard and history work on `main` is kept. |
| `dashboard_url` | https://peozenou.github.io/race/2026/ |
| `build_data_version` / `live_data_version` | `f130955966ac` / `f130955966ac` |
| `live_week` | 37, Monday 2 November 2026 (competition week, not ISO week) |
| `ui_checks_verified` | true (no remaining failures; every tab and edition fits a 375 px screen) |
| `live_verified_at` | 2026-11-02T22:05:29-05:00 (data fetch 22:04:48-05:00) |
| Deployment | GitHub Pages run [41569939158](https://github.com/peozenou/race/actions/runs/41569939158): build, report-build-status and deploy all success; deployment 7509276187, deploy job finished 2026-11-03T03:04:34Z. Served `index.html` byte-identical to the commit (SHA-256 `51f149d2030597f5c54ba035b5562c614dfae267856e7f34c21c9785d2d4b6f0`). |

Earlier week-37 states, each verified live and superseded the same evening at Patrick's request: `7eadc7b` (data version `6eef7f8c31de`, run [41541660989](https://github.com/peozenou/race/actions/runs/41541660989)) at 2026-11-02T18:02:34-05:00, and `f330aa8` (data version `3565c4654c57`, run [41568762676](https://github.com/peozenou/race/actions/runs/41568762676)) at 21:55:26-05:00. All kept the six approved datasets unchanged.

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

Browser checks (Claude desktop built-in browser, Chromium, on the live URL): 0 console errors; versioned data and history requests; standings cards and gains; season chart tooltip; duel matrix; 30-line player table, six per team under each team filter; search; sorting; composition two shades for both posts with tooltip; detail and player switch for Sinner/Lehecka and Engel/Blockx; Kouame and Rune details; Barème et sources tab; Historique tab; navigation between the four tabs; 375 px mobile width (see the correction below for the Historique tab); `tutoriel.mp4` and the landing page served byte-identical to the repository.

### Dashboard source changes (datasets untouched)

**Revision 1 (`7eadc7b`).** The only change is the `RACE_QUAL` comment in `2026/source/dashboard.html`, which now references this release. Its entries are unchanged (Kouame's `adjust` only), since the handoff named no new hold or adjustment. The preview image and tutorial were not regenerated.

**Revision 2 (`f330aa8`, requested by Patrick on 2 November).** Three Historique figures, chosen from different families in the [Python Graph Gallery](https://python-graph-gallery.com/), drawn in d3 from history data the page already loads (the 2026 edition from `2026/data`):

- **Part des points, édition par édition** (heatmap): each team's share of all points per edition, in one neutral ramp; ★ marks the champion and the 2026 column is outlined. Tooltip: rank, share and total.
- **Avance du vainqueur** (lollipop): the winner's margin over the runner-up as a percentage of the runner-up's total, from CHAN +0.7 % (2022) to DOC +46 % (2021); 2026 CHEF +12 % as a hollow dot.
- **En tête, semaine après semaine** (waffle): one square per recorded update in the colour of the team then leading, one row per edition (2022 has only its final standings). Legend: CHAN 93, DOC 63, CHEF 60, PAT 26 of 242 updates, no ties. Tooltip: lead over the second team.

On narrow screens the heatmap's years shorten to 19…26 and waffle rows wrap so squares stay at least 8 px. All shares, margins and lead counts shown live were recomputed independently from `history/data/seasons.json`, `history/data/hebdo.json` and `2026/data/hebdo.json` and match. Datasets, `history/` files, the other tabs, navigation and tutorial are unchanged.

**Revision-2 browser checks** (built-in browser, live URL, light 1024 px and dark 375 px): 0 console errors; six in-page hashes match; header and five totals; Joueurs tab unchanged with both two-shade posts; Historique bump chart and edition cards; the three new figures' values and tooltips; history files served byte-identical. The browser pane was not on screen, which pauses animation-frame redraws, so the data-driven redraws were re-triggered by switching tabs; with that, every chart drew.

**Correction.** The revision-1 check reported no horizontal scroll on any tab at 375 px. That measurement was taken before the Historique data had loaded. With the data loaded, the Historique tab is 379 px wide at 375 px on both `7eadc7b` and `f330aa8`, caused by the existing 2025 transfer label « Giovanni Mpetshi Perricard→Justin Engel » in the edition detail. The new figures stay within the card (right edge 359 px).

**Revision 3 (`aab1ce9`, requested by Patrick on 2 November).** The transfer list's name column can now shrink (`minmax(0,1fr)`) and a long name wraps inside its pill (radius 9 px, so one-line pills look as before). « Giovanni Mpetshi Perricard » now takes two lines. Live at 375 px in dark mode, the page is exactly 375 px wide on Équipes, Joueurs, Barème et sources and Historique, including the 2023–2026 edition details; locally, before publishing, all editions 2019–2026 were checked the same way. 0 console errors; the Historique charts draw; datasets and history files unchanged.

## Accepted qualifications carried

- 69 historical zero cells lack matching saved source rows. This is not a general rule that missing means zero.
- Tennis Abstract omits the known Kouame loss at Jingshan.
- Elo/yElo remains dated 28 September 2026.
- The Historique tab's "rang actuel" (each former player's current ATP rank) reads `history/data/ranks.json`, which is still dated 26 October 2026 and labelled that way on the page. This release did not refresh the history export, and step 6 left it unchanged.

## Step 7

**Unblocked; re-bind if needed.** Use https://peozenou.github.io/race/2026/, bound to dashboard commit `aab1ce9` (data version `f130955966ac`), verified live at 2026-11-02T22:05:29-05:00. Any step-7 receipt or draft bound to `7eadc7b` or `f330aa8` must be re-bound; the URL, week, datasets and totals are unchanged. Claude has not drafted or sent any email.

## Files

- [`completion.json`](completion.json): machine-readable completion note (public fields).
- [`evidence/live-data-aab1ce9.json`](evidence/live-data-aab1ce9.json) and [`evidence/live-ui-aab1ce9.json`](evidence/live-ui-aab1ce9.json) (current, revision 3): served page, datasets, history files; 375 px width checks.
- [`evidence/live-data-f330aa8.json`](evidence/live-data-f330aa8.json) and [`evidence/live-ui-f330aa8.json`](evidence/live-ui-f330aa8.json) (revision 2): served page, six datasets in both URL variants, history files, assets, tutorial and landing page; browser checks of the new figures.
- [`evidence/live-data-7eadc7b.json`](evidence/live-data-7eadc7b.json) (revision 1): served page version, headers, the six dataset hashes in both URL variants, assets, tutorial and landing page.
- [`evidence/live-ui-7eadc7b.json`](evidence/live-ui-7eadc7b.json): browser-check results (23 named checks).
- `evidence/7eadc7b-01-composition-tooltip-light.jpg`: composition bar with both two-shade posts and the Engel/Blockx tooltip.
- `evidence/7eadc7b-02-notes-sources-light.jpg`: Barème et sources tab with transfers and source dates.
- `evidence/7eadc7b-03-players-pat-filter-dark.jpg`: Joueurs tab filtered to PAT (dark).
