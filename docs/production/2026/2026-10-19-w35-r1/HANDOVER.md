# Step 6 production handover — release 2026-10-19-w35-r1 (week 35)

Owner: **Claude**. Prepared 20 October 2026, America/New_York. This is the public copy of the step-6 completion note for ChatGPT/Codex. The private copy additionally carries the cleared workbook fingerprint and approval records, which stay in the private run storage (see [data and release contract](../../../data-and-releases.md#publicprivate-boundary)).

## Production result

| Field | Value |
|---|---|
| `owner` | Claude |
| `production_status` | `LIVE_DASHBOARD_VERIFIED` for release r1 (presentation revision 2) |
| `release_id` | `2026-10-19-w35-r1` |
| `data_commit_sha` | [`8246a06b84f1b8c6ab316f8a7a29f16fabf71c1d`](https://github.com/peozenou/race/commit/8246a06b84f1b8c6ab316f8a7a29f16fabf71c1d) |
| `dashboard_commit_sha` | [`5b776276f246fcdc1748b884d16704fcd1fb299f`](https://github.com/peozenou/race/commit/5b776276f246fcdc1748b884d16704fcd1fb299f) |
| Production history | `82b00d9` → `8246a06` (release data, fast-forward) → [`73942d5`](https://github.com/peozenou/race/commit/73942d5bebadd34ac476b8e8a4e61e61e4690263) (week-35 build) → `5b77627` (Sinner/Lehecka lineup line) |
| `dashboard_url` | https://peozenou.github.io/race/2026/ |
| `build_data_version` / `live_data_version` | `d926b326a7fb` / `d926b326a7fb` |
| `live_week` | 35, Monday 19 October 2026 (competition week, not ISO week) |
| `ui_checks_verified` | true |
| `live_verified_at` | 2026-10-20T14:56:57-04:00 (data fetch 14:56:42-04:00) |
| Deployment | GitHub Pages run [39479004023](https://github.com/peozenou/race/actions/runs/39479004023): build, deploy and report all success at 18:56:10Z; deployment 7208392543 success; served `index.html` byte-identical to the commit (SHA-256 `7aa3e29227baa6f34cee5fb4367e61ba12cf09f22b5c8e3bae5fd7e8fe6d9efa`) |

The first week-35 build (`73942d5`, run [39472725729](https://github.com/peozenou/race/actions/runs/39472725729)) was verified live at 2026-10-20T14:15:26-04:00, including an in-page SHA-256 check in a second desktop Chrome session. Commits after `5b77627` that touch only `docs/` do not change the dashboard: `git diff 5b77627..HEAD -- 2026` is empty for them.

### Live datasets

All six served files match the approved step-5 hashes, both at the plain URL and with the page's `?v=` token:

| File | Rows | SHA-256 |
|---|---:|---|
| `hebdo.json` | 180 | `4ac943b83332663419c566fa57528cf77ee41c02738627498289e502c3ea97d9` |
| `joueurs.json` | 1052 | `dc9e22e13d85fda2c93142db35eaf5289d29408e68e12890774a91cd87ab1792` |
| `players.json` | 31 | `d3a4e8e3fba59d18a3a0be0af1c61f47c50d6e395954d8098a80e9759e96b742` |
| `matches.json` | 1508 | `ce004bb80c89bf2151109b43bbf0f7c7802899fd1efacabd91802ec7fa35b78e` |
| `calendar.json` | 13 | `a5b40cae611cf05229e6b7b572c035e7f19ec081a881804c64b611cdc7c9ba1a` |
| `team_colors.json` | 5 | `3ee69192269cf441b532cbeb47432effae3f202e1d02707ede686718ab315ca7` |

### Verified on the live page

| Team | Race | Duels | Total | Weekly gain |
|---|---:|---:|---:|---:|
| CHEF | 18,069 | 185 | 18,254 | +710 |
| DOC | 15,988 | 125 | 16,113 | +538 |
| CHAN | 14,455 | 170 | 14,625 | +860 |
| PAT | 11,786 | 140 | 11,926 | +620 |
| JULES | 10,992 | 95 | 11,087 | +420 |

Source dates shown separately from the competition Monday: Tennis Explorer rankings 19 Oct 2026; Elo/yElo 28 Sep 2026; Sinner's retained rankings 5 Oct 2026. Kouame's approved +24 appears once (300 raw, 324 credited). The five active-player aggregate fields that are null in `players.json` (`tpw`, `rpw`, `ace_pct`, `first_won`, `second_won`) are not displayed anywhere, so no zero or invented rate is shown.

Browser checks (headless Chromium on the live URL): 0 console errors, 0 page errors, 0 failed requests; standings cards; season, rank and gains charts; duel matrix; tooltips; 30-line player table (six per team); team filters; sorting; search; player detail with history chart; Sinner/Lehecka detail with player switch; notes tab; tab navigation; 390 px mobile width without horizontal scroll; `tutoriel.mp4` served. Reports and screenshots are in [`evidence/`](evidence/).

### Presentation changes in step 6 (dashboard source only; datasets untouched)

- **One lineup line per post.** An outgoing and an incoming player with the same team and `transfer_date` (short labels ending `(sorti)` and `(entré)`) are shown as one line, **Sinner/Lehecka**, so each team lists six posts. The line adds both players' credited Race and duel points (currently 7,950 + 75) and shows the incoming player's record, rank and Elo; its detail switches between the two seasons and charts the post's credited Race. The tournaments chart keeps one bubble per player.
  - **Export contract:** keep both player records, the `(sorti)` / `(entré)` labels and the same `transfer_date` on both. No schema change.
- **Pending incoming contribution.** While Lehecka's credited JOUEURS value is 0, the line notes that his contribution is pending and his 2,225 raw Race points are not yet counted; gains show "—", not 0. The note disappears once JOUEURS credits him.
- Kouame's adjustment note; archived ranking date and Elo date labelled separately.

## Requested data change — revised release r2

**Requested change (pending audit and clearance):** count Lehecka's CHEF entry from the start of week 34, with the ranking in force at his entry as his baseline: **2,055 Race points (Tennis Explorer, 5 October 2026)**. His gains add to Sinner's retained 7,950 Race / 75 duels for the CHEF post. Apply before the week-35 email.

**Why 2,055 is an observed baseline:**

- Tennis Explorer published no ranking on 12 October (two-week Shanghai Masters). Its Race and ATP ranking selectors list 05.10.2026 then 19.10.2026. Evidence: run captures of https://www.tennisexplorer.com/ranking/atp-men/?t=race&page=1 (2026-10-20T02:07:47Z, SHA-256 `37a4366790ce05a86a56bd69844f8ebc312ada54693c0652574b84f42a8b3c43`) and https://www.tennisexplorer.com/ranking/atp-men/?page=1 (2026-10-20T02:08:52Z, SHA-256 `36bb154284d59152e63a02eff331313a965283c62392287d224e978881acb8ef`).
- Week 34 already used the 5 October ranking for every player: HEBDO week-34 Race equals week 33, and the week-34 `players.json` has `rankings_date` 2026-10-05 for all records, with Lehecka at 2,055. Sinner's 7,950 is frozen at the same ranking, so the post hands over at one observation.
- Lehecka's matches in the window: Shanghai R2 win over Borges (10 Oct, unrostered) and R3 loss to CHEF teammate Jodar (12 Oct, after the week-34 cutoff, already in r1). No duel change.

**Owning steps:** step 3 sets the transfer baseline and recomputes LIVE/snapshot blocks, JOUEURS, HEBDO, TEAMS and BILAN for week 35; step 4 re-audits and obtains renewed clearance; step 5 exports `2026-10-19-w35-r2` (expected to change `hebdo.json` and `joueurs.json` only); then Claude repeats step 6. Keep `transfer_date` 12 October unless it is deliberately relabelled; if it moves, re-check duel eligibility for both players' 5–12 October matches.

**Expected values for independent verification** (Claude's arithmetic from r1, not audited):

| Item | r1 (live now) | Expected r2 |
|---|---:|---:|
| JOUEURS Lehecka, week 34 | 0 | 0 |
| JOUEURS Lehecka, week 35 | 0 | 170 (2,225 − 2,055) |
| CHEF week 35 Race / Duels / Total | 18,069 / 185 / 18,254 | 18,239 / 185 / 18,424 |
| CHEF weekly gain | +710 | +880 |
| Sinner/Lehecka post, credited | 7,950 | 8,120 |
| Other teams | unchanged | unchanged |
| Grand total | 72,005 | 72,175 (71,460 Race + 715 duels); weekly gain 3,318 |
| Order | CHEF, DOC, CHAN, PAT, JULES | unchanged; CHEF leads DOC by 2,311 |

## Step 7

**Blocked.** Do not draft the week-35 email from r1; it should use the r2 totals. Step 7 resumes after r2 is cleared, published and verified live in a new step 6.

## Files

- [`completion.json`](completion.json): machine-readable completion note (public fields).
- [`evidence/live-data-73942d5.json`](evidence/live-data-73942d5.json), [`evidence/live-data-5b77627.json`](evidence/live-data-5b77627.json): served page version, headers and the six dataset hashes.
- [`evidence/live-ui-73942d5.json`](evidence/live-ui-73942d5.json), [`evidence/live-ui-5b77627.json`](evidence/live-ui-5b77627.json): browser-check outputs.
- `evidence/5b77627-*.png`: live screenshots (teams, players, Sinner/Lehecka detail for each player, notes, mobile).
