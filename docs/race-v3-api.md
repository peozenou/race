# THE RACE weekly update — API (pipeline v3)

One workflow, **race-week.yml**, runs the whole week. Patrick, ChatGPT and Claude all drive it the same way, through GitHub. There is no server to host.

| You want to | Patrick (phone) | ChatGPT (GPT Action) | Claude |
|---|---|---|---|
| Start the week | [Live page](https://peozenou.github.io/race/run/) → **Lancer la semaine** → *Run workflow* | `startWeeklyUpdate` | `gh workflow run race-week.yml -R peozenou/race -f dry_run=false` |
| Follow progress | Live page (refreshes every 15 s) or the GitHub app | `listRuns` → `listProgressPoints` → `listProgressDetails` | `gh run watch <id> -R peozenou/race` |
| Approve publication | **Valider la publication** → *Review deployments* → *Approve* | `getPendingApproval` → `approvePublication` (only after Patrick says so) | `gh api -X POST repos/peozenou/race/actions/runs/<id>/pending_deployments -f state=approved …` (only after Patrick says so) |
| Stop | *Cancel workflow* | `cancelRun` | `gh run cancel <id> -R peozenou/race` |

The ChatGPT Action is defined in [tools/race_v3/openapi.yaml](../tools/race_v3/openapi.yaml). Claude uses the same REST calls through `gh` or the GitHub connector.

## The six progress points

Each point is one workflow job. The pipeline writes its key facts as annotations, which anyone can read through the public API. The live page shows them.

| # | Job name | What is checked | Shown live |
|---|---|---|---|
| 1 | `1 · Collecte` | Source pages fetched; player and match records parsed | records collected, source dates |
| 2 | `2 · Calcul et contrôles` | New week's JOUEURS/HEBDO computed; history append-only, roster 5 × 6, totals = Race + duels, JOUEURS sum = HEBDO Race, duels = players' duel points, no match after the cutoff | five totals, weekly change, warnings |
| 3 | `3 · Validation` | GitHub pauses until Patrick approves (environment `race-release`) | "En attente de votre validation" |
| 4 | `4 · Publication` | The approved six files (hash-checked) are installed, the page is built, and one commit is pushed to main | commit |
| 5 | `5 · Vérification en ligne` | The live site serves all six approved hashes and the new week title | pass or the mismatched file |
| 6 | `6 · Export Sheet` | Reference copy written to the Sheet's EXPORT tab (output only) | rows written, or skipped |

A dry run (`dry_run=true`, the default) stops after point 2. Nothing is written.

## Rules for assistants

- Start a run whenever Patrick asks. A dry run is always safe.
- Approve publication only after Patrick has seen the five totals and said yes in the conversation. Starting a run is not approval.
- A failed point stops the run. Report the point's annotation; do not rerun with changed inputs to make a check pass.
- A roster change (transfer) or rule change stops at point 2 with "Roster change needs a decision". It needs Patrick's decision and a code or data change, not a retry.
- Never put private data (Tiago, UTR, MatchTrack, emails) in inputs, commits or annotations.

## One-time setup

1. **Approval gate.** Settings → Environments → New environment `race-release` → Required reviewers: peozenou.
2. **ChatGPT.** Create a fine-grained token limited to peozenou/race: Actions read/write, Deployments read/write, Contents read. In the GPT editor, add an Action from `openapi.yaml` with Bearer authentication.
3. **Sheet copy (optional).** Add the secret `GOOGLE_SERVICE_ACCOUNT_JSON`, then the variable `RACE_SPREADSHEET_ID`. Share the Sheet with the service account's email as editor.
4. **Sources.** Run "THE RACE — pilote des sources" once to see whether Tennis Abstract and Tennis Explorer answer GitHub's servers.
