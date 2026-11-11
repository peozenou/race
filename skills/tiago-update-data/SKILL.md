---
name: tiago-update-data
description: "Independently update private Tiago UTR from Patrick's weekly observations and MatchTrack from genuine exports; either submodule may run while the other is pending."
---

# Independent private Tiago updates

Read the [private data contract](../update-the-race/references/tiago-contract.md) and exact private lane record. Keep Tiago UTR and MatchTrack statuses separate. Neither blocks Race/Elo; no junior data enters the public repository.

For weekly UTR, ask Patrick only if the value is requested and not supplied. Resolve date/week meaning and ratingtype where known; do not invent exact measurement time, scrape UTR or fill a missing week. Verify destination/headers/history/duplicates, save exact upsert preview and source provenance, backup/checkprestate, apply authorizedboundedwrite andreadbackprotected history. A same observation is no-op; corrections are linked revisions. If dashboard update is requested, use its actual private build/deployment path and verify source, commit, deployment andauthenticated live separately. Do not change access controls.

For MatchTrack, discover actual authorized files before asking for copies. Preserve genuine rawCSV/nativebytes and hashes, review header-driven schemas, stable match/revisionkeys, pointprogression/final scores/coverage/context andcountdenominators. Keep failedrecords quarantined andqualifications explicit; never silentlyrepair/promote historical records. Server/format/rally/tag fields remain unknown when absent. Use the existing reviewed parser helpers; data correctness is not implied by parser success. Preview/destination/backup/readback rules apply to requested writes. A UTR-only update does not require MatchTrack intake or coaching advice.

Show UTR and MatchTrack separately beneath the general progress view, outside the Race denominator. Keep every private observation, backup, source andapproval in private storage.
