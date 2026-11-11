# Acquisition and source handoff contract

## Evidence and exact-run records

Retain run ID, season, target Monday, competition-week evidence, exclusive cutoff, timezone, source/parser/configuration/roster/scoring versions, prior-run link, actual access route and module states. Readiness and acquisition are not publication. A blocked source names its evidence, affected output, responsible module and resume checkpoint.

Each raw artifact records original URL/file, source/player identity, publication date, event date if applicable, capture/ingestion time, SHA-256, schema/parser version, coverage and immutable raw path. Keep available-at separate from observed-at; a newly captured old event does not prove past availability. Exact resume verifies all relevant digests and lock/cooldown state. A mismatch needs reconciliation, not silent reuse or modified evidence.

Canonical tables retain original text, typed values/units, null reasons and source-row references. Distinguish source player IDs/aliases, contest keys and player-perspective keys; ratings/rankings use player + source + actual publication date + type + revision. Version roster/rules by season/team/slot. Private UTR uses person + date/week meaning + type; corrected observations and MatchTrack re-exports create linked revisions rather than duplicate facts.

## Source gates

- TA: complete required active-roster coverage, paired target-season displayed Serve/Return keys, grounded URL/control/table identity and evidence for an empty season. Errors are not empty results. Visible blanks remain blank; no hidden raw table fills them. Retain round/surface/score/status and original dates/text. Independently reconcile actual completion/cutoff; tournament start is not finish time.
- Elo: both complete men's Elo and season yElo reports, distinct schemas and actual dates, including source Peak Month text and blanks. Never filter the import to the Race roster. Primary pages are https://tennisabstract.com/reports/atp_elo_ratings.html and https://tennisabstract.com/reports/atp_season_yelo_ratings.html .
- TE: actual Race/ATP pagination/table selectors and enough tail coverage for unique selected-player joins. Primary starting page: https://www.tennisexplorer.com/ranking/atp-men/ . Missing/error and a genuine published zero are different states. Prior exceptions are ledger-specific, not blanket policy.
- UTR: Patrick's supplied value and date/week semantics, with type/measurement time only when known. Do not scrape, invent a weekly observation or republish junior data. Resolve the real private Sheet and dashboard before a requested update.
- MatchTrack: genuine original bytes, file/logical duplicate checks, event/date/opponent/format/score identity, revision history, point progression/final score and declared coverage. Rates need count denominators; absent server/rally/error fields are not zero. Keep private sources separate from public pro data.

## Preview and writer boundary

Read actual native workbook metadata/headers/prestate before exact ranges. A source-only handoff can supply typed candidates and unresolved mappings; it is not an approved Sheet patch. Private configuration supplies actual destination IDs and permissions; public documentation contains no personal identifiers.

Race mapped inputs are B:X, with verified text/numeric/duration conventions and displayed blanks preserved. Protect result/duel formulas, unrelated formats and old history; legitimate inserted-row reference propagation must be checked. Scoring/transfer semantics come from the current approved registry/ledger, not a stale roster or inferred membership date. Elo creates complete dated pairs and preserves old tabs; TE creates one actual dated frozen snapshot and never invents historical Mondays from current rankings.

Handoff includes artifact access/hash, typed candidates, source dates, gaps/withholding, check counts and authorization state. The writer uses the approved profile or exact separate scope, verified backup/prestate, bounded writes and independent readback. Routine in-profile writes need no repeated submodule approval after Start; publication still needs Patrick's exact candidate approval. A post-seal volatile LIVE failure is health only, not grounds to revoke an unchanged approved snapshot.

## Completion limits

Offline parsing/testing does not establish live source access, Sheet readback, publication or phone notification delivery. Report observed capabilities and exact remaining checks. Do not claim a one-click launcher, active schedule or hosted source adapter from instructions alone. Routine figures/email are not part of the v2 weekly process; separately requested historical figure or mail work retains its own explicit scope.
