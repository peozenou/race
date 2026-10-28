# THE RACE — historical datasets (2019–2026)

Every past edition converted from its Google Sheet into the same six-file JSON format as `2026/data/`,
plus a stacked history that runs from 2019 through the current 2026 release.

## Layout

| Path | Contents |
|---|---|
| `<season>/data/` (2019–2025) | `hebdo`, `joueurs`, `players`, `matches`, `calendar`, `team_colors` — same field names and meanings as `2026/data/` |
| `history/data/` | The same six datasets stacked across 2019–2026, each row tagged with `season` and `scoring_system`, plus `rosters.json` and `seasons.json` |
| `history/validation.json` | Every reconciliation check run by the converter (value, reference, pass/fail) |
| `history/data/corrections.json` | Every change made to a recorded workbook value (recorded → corrected, reason, evidence), plus corrections awaiting a league decision |
| `history/race_history.sqlite`, `history/csv/` | The consolidated database (see below) |
| `history/tools/` | `build_history.py` + `common.py` (the converter) and `audit_bareme.py` (2019–2021 tournament audit) |

`2026/data/` is untouched; its rows are copied into `history/data/` unchanged.

## Consolidated database

`history/race_history.sqlite` holds everything in one file, rebuilt from `history/data/` by
`python3 -I history/tools/consolidate.py`. `history/csv/` has the same tables as CSV (for Stata, R or Excel).

| Table | Grain |
|---|---|
| `seasons` | One row per edition: scoring system, status, final week/date, champion, notes |
| `teams`, `season_teams` | Team palette; which teams played each season |
| `final_standings` | Season × team: rank, race, duels, total |
| `people` | One row per player ever rostered (`person_key` = `atp:<Sackmann id>`, or `name:<player>` when unknown) |
| `rosters`, `transfers` | Season stints with start/end dates and frozen credits; in-season swaps |
| `hebdo` | Season × week × team, with `rank`, `share` and the workbook's original values |
| `joueurs` | Season × week × team × player credited points |
| `players` | Season × team × player summary (2026 schema + `league_points`, `slot`) |
| `matches` | One row per player perspective on a match |
| `calendar` | Major events per season |
| `corrections` | Every applied correction, plus the 2020 Vienna case pending a decision |

Views: `v_team_seasons` (team results by season), `v_team_honours` (titles, average rank and share),
`v_player_careers` (each player across editions), `v_duels` (every scored duel).

```sql
SELECT * FROM v_team_honours ORDER BY titles DESC, avg_rank;
```

## Two scoring eras

| Seasons | `scoring_system` | What `race` means |
|---|---|---|
| 2019–2021 | `bareme` | League barème points by round reached (BAREME tab: e.g. ATP 250 SF 5 / F 10 / W 15; Slam QF 20 … W 60 in 2019, 70 from 2020), plus 5 per duel |
| 2022–2026 | `race` | ATP Race points (Tennis Explorer) credited to the team, plus 5 per duel |

Points are not comparable across eras. Compare eras with `hebdo.rank` and `hebdo.share`
(team total ÷ sum of all teams that week), which are added in `history/data/hebdo.json`.

## Extra fields in `history/data/`

| File | Added fields |
|---|---|
| all | `season`, `scoring_system` (matches carry `season` and a season-prefixed `mid`, e.g. `2023-M0412`) |
| `hebdo` | `rank` (1 = leader that week), `share`, `corrected`, `race_recorded` / `duels_recorded` / `total_recorded` (the workbook's original values) |
| `joueurs`, `players` | `atp_id` (Jeff Sackmann `tennis_atp` player id, stable across seasons) |
| `players` | `league_points` (player's credited points at the last recorded week), `slot` (2019–2020 roster tags: Top 10, Moins 21, Frenchie) |
| `rosters` | One row per stint: `season`, `team`, `source_team` (e.g. `REM`), `player`, `atp_id`, `start`, `end`, `frozen_race`, `frozen_duels`, `entry_offset` |
| `seasons` | Teams, final week/date, final standings, champion, transfer ledger, coverage notes, data issues |

Team `REM` (2019–2022 sheets) is the same franchise as `DOC` and is coded `DOC`; the original label is kept in `rosters.source_team`.

## Coverage by season

| Season | Teams | hebdo | joueurs | matches | Notes |
|---|---|---|---|---|---|
| 2019 | 3 | weekly, 30 weeks (totals only) | final week | Sackmann tour-level | Race/duels split only in the final week |
| 2020 | 4 | weekly, 19 weeks | final week | Sackmann tour-level | COVID gap Feb–Aug; CHEF final 410 (HEBDO) vs 430 (SCORES) |
| 2021 | 4 | weekly, 37 weeks | final week | Sackmann tour-level | |
| 2022 | 4 | final only (`week`/`date` null) | final only | Sackmann tour-level | Only BILAN ATP survives; player duel points not recorded |
| 2023 | 4 | weekly, 46 weeks | weeks 1–37 (rebuilt from dated TE tabs) | Sackmann tour-level | HEBDO updated irregularly |
| 2024 | 4 | weeks 0–38 | weeks 1–38 | Tennis Abstract tabs | Ends 11 Nov 2024 (pre-Finals) as recorded |
| 2025 | 5 | weeks 0–35 | weeks 1–35 | Tennis Abstract tabs | Week 35 rebuilt (week 34 + ATP Finals) |
| 2026 | 5 | current release | current release | current release | In progress |

Fields with no historical source are `null`, never zero: Elo/yElo, serve/return percentages,
and (for 2019–2021) ATP Race rank/points. 2019–2023 matches cover tour-level main draws only.

## Transfers

In-season transfers follow the 2026 convention: both players keep their records, labelled
`(sorti)` / `(entré)` and sharing one `transfer_date`. In `joueurs`, the outgoing player keeps his
frozen credit after leaving, and the incoming player is credited net of it, so team sums match HEBDO.
The ledger used (2023–2025) is in `seasons.json › transfers`.

## Corrections

The per-season files carry corrected values; `history/data/hebdo.json` keeps the workbook's
original figures next to them (`*_recorded`, `corrected`). Only errors provable from the workbook
itself or from match results were corrected:

| Season | Correction | Effect |
|---|---|---|
| 2025 | Week-35 tab held the 2024 Race table; rebuilt as week 34 + ATP Finals points (Sinner 1,500, Alcaraz 1,000, Zverev/Fritz/De Minaur/Musetti 200) | Final: CHAN 23,335 · CHEF 22,497 · DOC 13,964 · JULES 13,546 · PAT 13,095 |
| 2025 | Weekly duel points rebuilt from the per-match rule (+5 per win over another team's rostered player); the HEBDO column had drifted (CHEF stuck at 150–155) | Final duels CHAN 250 · CHEF 245 · PAT 160 · DOC 140 · JULES 135 |
| 2025 | Week-12 JULES typed 4,529 vs 4,579 in the team block | +50 that week |
| 2024 | Week-2 CHEF read CHAN's cell; week-24 CHEF read the week-25 tab | Two weeks fixed |
| 2024 | Opponent ranks filled from the weekly ATP tables | Best-win fields populated |
| 2023 | CHAN missed in the week-28 update and carried for 5 weeks | CHAN 14,269 → 17,479, weeks 28–32 |
| 2021 | CHEF Slam points moved to the right weeks (formula skipped quarter-finalists; compensated at Roland-Garros) | Season total unchanged |
| 2020 | Hamburg CHEF formula bug (Rublev's final, +20) | HEBDO = SCORES = 430 |

**Awaiting a league decision (not applied):** in 2020 the "Vienne" row holds the Nur-Sultan results,
so Vienna was never scored. Rublev won it (+60 for CHEF), which would move CHEF from 4th to 3rd.

**Still open:** 2022 has only final standings; 2023 player rows stop at week 37 and 11 small HEBDO
timing gaps remain; Kouame's 2025 tab is empty; 2024 final CHEF duels 240 (HEBDO) vs 230 (matches);
2019 Auger-Aliassime's early results are excluded consistently (likely a roster change).
LIVE/BILAN tabs and the 2024 week-39 tab are live web imports and are never used.

## Rebuilding

```sh
python3 -I history/tools/build_history.py SRC_DIR OUT_DIR 2026/data
```

`SRC_DIR` must contain the native `.xlsx` exports of each season's workbook and a `sackmann/` folder
with `atp_matches_YYYY.csv`, `atp_players.csv` and `atp_rankings_*.csv`. Those sources are private
inputs and are not stored in this repository.
