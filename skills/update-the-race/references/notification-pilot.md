# Readiness and iPhone notification pilot

Status: **PENDING_PILOT — schedules must remain paused.** The checkpoint times and write profile were approved on 10 November 2026; that approval is not evidence that source access or phone delivery works.

## Acceptance before scheduling activation

1. Run the readiness adapter without writes against current primary sources. Prove correct roster/event scope, paired displayed TA evidence, late/unfinished results, source lag and UNKNOWN on access failure. Respect TA cooldowns and do not bypass source challenges.
2. Persist private per-week readiness and notification state. Re-run/restart the same case: one actionable Start notice, no duplicate push. Supersede a changed pending payload without sending another notice; reject its old approval hash.
3. Verify the actual supported notification route on Patrick's iPhone: account/device connection, permission, background/locked delivery and notification opening the correct run. Desktop/inbox success alone does not pass. If native app delivery cannot satisfy this, implement/test the Home Screen Web Push route before claiming phone readiness.
4. Opening the notice must not approve Start. Confirm an explicit authenticated owner decision binds week, profile and current readiness payload. Test stale/replayed commands and a changed candidate.
5. Confirm Sunday Start remains provisional until Monday cutoff/TE source checks. At unresolved final fallback, create one consolidated attention item with no repeat-completion pings. Prove that accepted Start or completion stops that week's readiness requests.
6. Save timestamped private pilot evidence and report which route passed. Only then change the approved paused schedule to active and independently read back its timezone/cadence/status.

Approved cadence: Sunday 18:00 and 21:00; Monday 00:30 and 08:30 America/New_York. Keep daylight-saving behavior explicit. Local runs require the supported computer/app and source session to be available; a static public site is not an unattended private executor.

No notification is sent, no schedule is activated and no authenticated approval service is created by this document. Use the Codex automation action for real schedule management; do not install hand-written cron files as a substitute. Notification preferences belong in platform configuration rather than prompt promises. Pilot failures stay visible and do not justify silently changing the requested channel.
