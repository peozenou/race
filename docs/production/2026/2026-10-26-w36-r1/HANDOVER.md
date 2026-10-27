# Step 6 production handover — release 2026-10-26-w36-r1 (week 36)

Owner: **Claude**. Prepared 27 October 2026, America/New_York. This is the public copy of the step-6 completion note for ChatGPT/Codex. The private copy additionally carries the cleared workbook fingerprint and approval records, which stay in private run storage (see [data and release contract](../../../data-and-releases.md#publicprivate-boundary)).

## Production result

| Field | Value |
|---|---|
| `owner` | Claude |
| `production_status` | `LIVE_DASHBOARD_VERIFIED` |
| `release_id` | `2026-10-26-w36-r1` (branch `data-release/2026-10-26-w36-r1`) |
| `data_commit_sha` | [`3220344fc042fa9f471aaaaff475f9b82cfc66ef`](https://github.com/peozenou/race/commit/3220344fc042fa9f471aaaaff475f9b82cfc66ef) |
| `dashboard_commit_sha` | [`8fe2905d6d357ec63d55d302b558374bac7b2389`](https://github.com/peozenou/race/commit/8fe2905d6d357ec63d55d302b558374bac7b2389) |
| Production history | `6bb71bd` (previous main) → `3220344` (release data, fast-forward) → `8fe2905` (week-36 build). No concurrent changes on `main` to merge. |
| `dashboard_url` | https://peozenou.github.io/race/2026/ |
| `build_data_version` / `live_data_version` | `ae164c5669a3` / `ae164c5669a3` |
| `live_week` | 36, Monday 26 October 2026 (competition week, not ISO week) |
| `ui_checks_verified` | true (40 checks, 0 failures, light and dark) |
| `live_verified_at` | 2026-10-27T07:06:46-04:00 (data fetch 07:05:54-04:00) |
| Deployment | GitHub Pages run [40493412269](https://github.com/peozenou/race/actions/runs/40493412269): build, report-build-status and deploy all success; deployment 7356744664 success at 11:05:16Z. Served `index.html` byte-identical to the commit (SHA-256 `1c10bd445e08bcd81ad9353ef5c40dee981d395d97a5188ea0eea36cc5aa5424`). |

Later commits that touch only `docs/` (such as the one adding this note) do not change the dashboard: `git diff 8fe2905..HEAD -- 2026` is empty for them.

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

Browser checks (headless Chromium on the live URL, light and dark): 0 console errors, 0 page errors, 0 failed requests; standings cards; season, rank and gains charts with tooltip; duel matrix; 30-line player table, six per team under each team filter; sorting; search; detail views for Sinner/Lehecka (both players), Kouame, Bernet and Rune; Notes tab; tab navigation; 390 px mobile width without horizontal scroll; `tutoriel.mp4` served byte-identical to the repository.

### Dashboard source change (datasets untouched)

`RACE_QUAL` in `2026/source/dashboard.html` now references this release and no longer lists Lehecka's hold, since his entry baseline (2,055) is confirmed and credited. The hold display would have switched itself off anyway; removing it records the resolved state. Kouame's adjustment entry stays. French interface, design, navigation and tutorial are unchanged.

## Accepted qualifications carried

- 69 historical zero cells lack matching saved source rows; this is not a general missing-equals-zero rule.
- Tennis Abstract omits the known Kouame loss at Jingshan.
- Elo/yElo remains dated 28 September 2026.

## Step 7

**Unblocked.** Production is verified live. The week-36 email may link https://peozenou.github.io/race/2026/, bound to dashboard commit `8fe2905`. Claude has not drafted or sent any email.

## Files

- [`completion.json`](completion.json): machine-readable completion note (public fields).
- [`evidence/live-data-8fe2905.json`](evidence/live-data-8fe2905.json): served page version, headers, the six dataset hashes in both URL variants, tutorial and landing page.
- [`evidence/live-ui-8fe2905.json`](evidence/live-ui-8fe2905.json): browser-check output, light and dark, with the 40 named checks.
- `evidence/8fe2905-*.png`: live screenshots (teams, CHEF composition with tooltip in light and dark, Sinner/Lehecka detail for each player, Notes tab, mobile).
