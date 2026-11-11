---
name: tennis-update-elo
description: "Independently check and update both complete TA Elo/yElo reports weekly or on demand, preserving dated snapshots, source truth and history."
---

# Independent weekly Elo + yElo

Read the [Elo contract](../update-the-race/references/elo-contract.md), [helper inventory](../update-the-race/references/adapters.md) and exact private lane record. This task neither starts nor blocks Race or Tiago. Prefer checking it alongside Sunday readiness; it may also be requested alone.

Acquire BOTH complete men's reports, save raw HTML/CSV/hash and actual report dates, independently compare all fields/rows including blanks/Peak Month text and verify existinglatestpair. Verified unchanged reports mean NO_SOURCE_ADVANCE and zero writes. Advanced reports receive an exact bounded new extraction-date pair preview, backup/prestate and full typed readback under current authorization. No silent overwrite, duplicate pair or fabricated aligned date; mixed-date/schema/history exceptions require a concrete decision.

Preserve all oldtabs and record source dates/counts/protection/readback privately. Direct routine update authorization is reusable for that scope; do not ask again solely because this is an independent lane. A later pair must not replace the snapshot selected by a sealed Race candidate without affected release review. Show separate weekly lane status beneath the Race progress bar, outside its denominator.
