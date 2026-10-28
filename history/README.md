# THE RACE — historical datasets (2019–2026)

Every past edition converted from its Google Sheet into the same six-file JSON format as `2026/data/`,
plus a stacked history that runs from 2019 through the current 2026 release.

## Layout

| Path | Contents |
|---|---|
| `<season>/data/` (2019–2025) | `hebdo`, `joueurs`, `players`, `matches`, `calendar`, `team_colors` — same field names and meanings as `2026/data/` |
| `history/data/` | The same six datasets stacked across 2019–2026, each row tagged with `season` and `scoring_system`, plus `rosters.json` and `seasons.json` |
| `history/validation.json` | Every reconciliation check run by the converter (value, reference, pass/fail) |
| `history/tools/` | `build_history.py` + `common.py`, the converter that produced these files |

`2026/data/` is untouched; its rows are copied into `history/data/` unchanged.

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
| `hebdo` | `rank` (1 = leader that week), `share` |
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
| 2025 | 5 | weeks 0–34 | weeks 1–34 | Tennis Abstract tabs | Week 35 excluded (corrupted tab) |
| 2026 | 5 | current release | current release | current release | In progress |

Fields with no historical source are `null`, never zero: Elo/yElo, serve/return percentages,
and (for 2019–2021) ATP Race rank/points. 2019–2023 matches cover tour-level main draws only.

## Transfers

In-season transfers follow the 2026 convention: both players keep their records, labelled
`(sorti)` / `(entré)` and sharing one `transfer_date`. In `joueurs`, the outgoing player keeps his
frozen credit after leaving, and the incoming player is credited net of it, so team sums match HEBDO.
The ledger used (2023–2025) is in `seasons.json › transfers`.

## Known source issues (kept as recorded, not corrected)

- **2025** — tab `20251117w35` holds the 2024 Race table, so the workbook's week-35 totals are wrong; excluded. HEBDO week-12 JULES typed as 4,529 (block sums to 4,579). HEBDO duel totals stale in the last weeks.
- **2024** — HEBDO week-2 CHEF reads CHAN's cell (615 instead of 820); week-24 CHEF reads the week-25 tab. LIVE, BILAN and tab `20241118w39` re-evaluate live web imports (they now show 2026 values) and are not used.
- **2023** — LIVE/BILAN Race columns are live formulas and are not used.
- **2020** — CHEF final total differs between HEBDO and SCORES.

Details per check are in `history/validation.json`.

## Rebuilding

```sh
python3 -I history/tools/build_history.py SRC_DIR OUT_DIR 2026/data
```

`SRC_DIR` must contain the native `.xlsx` exports of each season's workbook and a `sackmann/` folder
with `atp_matches_YYYY.csv`, `atp_players.csv` and `atp_rankings_*.csv`. Those sources are private
inputs and are not stored in this repository.
