# Phase 4 production handover — release 2026-11-23-w40-r2 (week 40)

Owner: **Claude**. Prepared 23 November 2026, America/New_York. This is the public copy of the phase-4 completion note; machine-readable fields are in [completion.json](completion.json). Private approvals and run fingerprints stay in private run storage.

## Production result

| Field | Value |
|---|---|
| `owner` | Claude |
| `production_status` | `LIVE_DASHBOARD_VERIFIED` |
| `release_id` | `2026-11-23-w40-r2` (branch `claude/data/2026-11-23-w40-r2`), a linked revision of `2026-11-23-w40-r1` |
| `data_commit_sha` | [`db44c9fc74d006be39b2e80a105304ec63ca38fb`](https://github.com/peozenou/race/commit/db44c9fc74d006be39b2e80a105304ec63ca38fb) (r1: [`997221e`](https://github.com/peozenou/race/commit/997221e31b05565ea2c05c2bb26a7d964c9ae802), hashes verified, never published alone) |
| `dashboard_commit_sha` | [`e02e1cb6eefb931268d387d3ca0f0b8b070d935a`](https://github.com/peozenou/race/commit/e02e1cb6eefb931268d387d3ca0f0b8b070d935a) |
| Production history | `0c3febb` (previous main, remote HEAD at start and just before the push) → `997221e` (r1 data) → `db44c9f` (r2 data) → `e02e1cb` (week-40 build). No concurrent work had to be merged. |
| `dashboard_url` | https://peozenou.github.io/race/2026/ |
| `build_data_version` / `live_data_version` | `bb024041c6c2` / `bb024041c6c2` (previous `03791704d6b6`) |
| `live_week` | 40, Monday 23 November 2026 (competition week, not ISO week) |
| `ui_checks_verified` | true (0 console errors, desktop 1400 px and mobile 390 px) |
| `live_verified_at` | 2026-11-23T22:31:31-05:00 |
| Deployment | GitHub Pages run 45319869617: build, report-build-status and deploy all success, deploy finished 2026-11-24T03:29:56Z. Served `index.html` is byte-identical to the commit. |

## Why r2

The r1 handoff hashes all matched the release commit. During the phase-4 review Patrick asked to verify the totals against the week's matches. Duels reconciled exactly, but Race was held at week-39 values although r1 adds the complete ATP Finals (Turin) results and the matching Tennis Explorer ATP-point increases. Patrick's instruction (23 Nov): hold, update the totals from the Turin matches, then update the week-40 dashboard.

Turin Race points were taken from the release's own « Finales ATP » match records (round-robin win 200, semi-final win 400, final win 500). Each equals that player's change in the release's TE 23 Nov ATP points:

| Player | Team | Turin record | Race added | Race 16 → 23 Nov |
|---|---|---|---:|---|
| Alcaraz | CHAN | 3–0, SF W, F W (title) | 1,500 | 6,100 → 7,600 |
| Zverev | DOC | 3–0, SF W, F L | 1,000 | 9,350 → 10,350 |
| Shelton | PAT | 2–1, SF L | 400 | 5,170 → 5,570 |
| Medvedev | CHAN | 2–1, SF L | 400 | 3,820 → 4,220 |
| Fils | CHEF | 1–2 | 200 | 3,625 → 3,825 |
| Tiafoe | JULES | 1–2 | 200 | 3,390 → 3,590 |
| Cobolli | DOC | 0–3 | 0 | 3,670 |
| Jodar | CHEF | 0–3 | 0 | 3,234 |

r2 changes only week-40 HEBDO race/total, six week-40 JOUEURS rows and `players.json` race points (plus race rank Fils 7 → 6, Cobolli 6 → 7). Weeks 0–39, duels, matches, calendar and colours are unchanged. All Turin points are credited in week 40, including the four 15 Nov round-robin perspectives already present in week 39. The week's Challenger results (Blanch at Drummondville, Budkov Kjaer at Helsinki) are not credited. The TE Race table itself was not independently read in this phase.

## Verified on the live page

| Team | Race | Duels | Total | Change vs week 39 |
|---|---:|---:|---:|---:|
| CHEF | 19,139 | 195 | 19,334 | +200 |
| CHAN | 18,775 | 235 | 19,010 | +1,930 |
| DOC | 17,971 | 185 | 18,156 | +1,015 |
| PAT | 14,453 | 170 | 14,623 | +405 |
| JULES | 11,792 | 120 | 11,912 | +205 |

Duels match the week's Turin matches between rostered players: CHAN +30 (Alcaraz 4 wins, Medvedev 2), DOC +15 (Zverev 3), PAT +5 (Shelton d. Jodar), JULES +5 (Tiafoe d. Cobolli), CHEF 0 (Fils–Jodar is a same-team match). All team-weeks satisfy Race + Duels = Total, and each team's week-40 JOUEURS sum equals its HEBDO Race.

- **Header.** « THE RACE 2026 — Bilan 40e semaine ». « Après la semaine 40 (23 nov. 2026), CHEF est devant avec 19 334 points, suivi de CHAN. Meilleure progression de la semaine : CHAN (+1 930), notamment grâce à Alcaraz (+1 500). » CHAN shows ▲ était 3e, DOC ▼ était 2e.
- **Datasets.** All six served files match the r2 hashes in [completion.json](completion.json), both plain and with `?v=bb024041c6c2`, and through an in-page fetch at both widths. No mix of old and new files was served.
- **Transfers.** 30 lineup lines from 32 player records; Sinner/Lehecka and Engel/Blockx stay single lines; the switch reads « Lehecka (depuis le 12 oct.) » / « Sinner (jusqu’au 12 oct.) ». PAT filter shows 6 lines.
- **Source dates**, separate from the competition Monday: TE rankings 23 Nov 2026 (retained: Engel 26 Oct, Sinner 5 Oct); Elo/yElo 16 Nov 2026; matches through 23 Nov 2026.
- **Nulls and layout.** No "NaN", "null" or "undefined" text; Historique draws with no horizontal scroll at 390 px.

Evidence: [teams 1400 px](evidence/e02e1cb-01-teams-1400.jpg), [joueurs 1400 px](evidence/e02e1cb-02-joueurs-1400.jpg), [historique 390 px](evidence/e02e1cb-03-historique-390.jpg), [UI checks](evidence/live-ui-e02e1cb.json). Checks ran in headless Google Chrome (Playwright) in Claude's cloud workspace against the canonical URL.

## Accepted qualifications carried

- The r1 note that retained outgoing snapshots repeat the previous week's active TE date is a text erratum; the explicit dates above apply.
- Qualifications carried from week 39 are unchanged (Kouame +24 adjustment applied once; historical zeros without saved rows are not a general missing-equals-zero rule; five aggregate percentage fields null for active players; outgoing identities keep older source dates).
- r2 is a Claude-derived revision on Patrick's instruction; the GPT data step should re-audit it against the TE Race table and bind it in private release storage.

## Addendum — season close (23 Nov 2026, 22:37 America/New_York)

At Patrick's request, [`def6e09`](https://github.com/peozenou/race/commit/def6e09) adds a season-close line under the header summary: « Dernière mise à jour de la saison : ce bilan de la 40e semaine est le classement final de THE RACE 2026. CHEF remporte l'édition avec 19 334 points. » It is driven by `SEASON_FINAL_WEEK = 40` in `2026/source/dashboard.html` and the leader in the standings. Title, summary wording and the six datasets are unchanged (same r2 hashes). Re-verified live: Pages run 45320664505 success, served `index.html` byte-identical to the commit, data version `fed23d76429e`, line shown at 1400 px and 390 px, 0 console errors, no horizontal scroll.
