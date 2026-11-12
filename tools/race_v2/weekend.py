#!/usr/bin/env python3
"""Prepare a private, unapproved weekly run from live-read evidence; no service writes."""
import argparse
import csv
import hashlib
import json
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

try:
    from . import race_run as r
except ImportError:
    import race_run as r


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def prepare(root, monday, context_file, metadata_file, hebdo_file, transfers_file,
            baseline_dir, baseline_commit, scoring_file):
    root = Path(root).resolve()
    if any((p / '.git').exists() for p in (root, *root.parents)):
        raise r.Refused('Private runs must be outside every Git checkout.')
    monday = date.fromisoformat(monday)
    if monday.weekday() != 0:
        raise r.Refused('Choose the target Monday, not the Sunday start date.')
    r.check_commit(baseline_commit)
    context = r.read(context_file)
    source_files = {k: Path(v).resolve() for k, v in {
        'context': context_file, 'metadata': metadata_file, 'native_hebdo': hebdo_file,
        'transfers': transfers_file, 'scoring': scoring_file,
        'roster': context['roster_file'], 'profile': context['profile_file'],
        **{'baseline_' + n: Path(baseline_dir) / (n + '.json') for n in r.DATASETS}}.items()}
    hashes = {k: sha(p) for k, p in source_files.items()}
    if root.exists():
        saved = r.read(root / 'preparation.json')
        if saved['target_monday'] != monday.isoformat() or saved['input_sha256'] != hashes or saved['baseline_commit'] != baseline_commit:
            raise r.Refused('Prepared inputs changed. Preserve this run and prepare a linked revision.')
        return r.checked_status(root, r.load(root))
    with source_files['roster'].open(newline='', encoding='utf-8-sig') as f:
        roster = [x for x in csv.DictReader(f) if x.get('active', '').upper() == 'TRUE']
    slugs = [x['tennis_abstract_slug'] for x in roster]
    if len(roster) != 30 or len(set(slugs)) != 30 or any(sum(x['team'] == t for x in roster) != 6 for t in ('PAT', 'DOC', 'CHAN', 'CHEF', 'JULES')):
        raise r.Refused('Resolve a complete 30-player, six-per-team registry.')
    sheets = {x['properties']['title']: x['properties'] for x in r.read(metadata_file)['sheets']}
    required = {'HEBDO', 'BILAN', 'TEAMS', 'JOUEURS', 'LIVE', 'TRANSFERTS'} | {x['sheet_name'] for x in roster}
    if not required <= sheets.keys():
        raise r.Refused('Native workbook targets are incomplete.')
    if any(sheets[x['sheet_name']].get('hidden', False) for x in roster):
        raise r.Refused('An active registry selection points to an archived native tab.')
    rows = [x for x in r.read(hebdo_file)['values'][2:] if len(x) >= 17 and type(x[1]) is int]
    previous = max(rows, key=lambda x: x[1])
    prior_date = date(1899, 12, 30) + timedelta(days=previous[0])
    if prior_date + timedelta(days=7) != monday:
        raise r.Refused('Resolve missing/skipped competition weeks explicitly; do not infer ISO weeks.')
    week = previous[1] + 1
    snapshot = monday.strftime('%Y%m%d') + 'w' + str(week)
    if snapshot in sheets:
        raise r.Refused('Target snapshot already exists; reconcile the existing update instead.')
    baseline = r.read(Path(baseline_dir) / 'hebdo.json')
    last = [x for x in baseline if x['week'] == previous[1]]
    teams = ('PAT', 'DOC', 'CHAN', 'CHEF', 'JULES')
    if len(last) != 5 or {x['team'] for x in last} != set(teams):
        raise r.Refused('Published prior week does not cover five teams.')
    for i, team in enumerate(teams):
        row = next(x for x in last if x['team'] == team)
        if row['date'] != prior_date.isoformat() or [row[k] for k in ('race', 'duels', 'total')] != previous[2 + i*3:5 + i*3]:
            raise r.Refused('Native prior-week totals differ from published data: ' + team)
    players = r.read(Path(baseline_dir) / 'players.json')
    for player in roster:
        # Public short labels may contain transfer annotations such as '(entré)'.
        # Join stable approved full identities; do not parse display suffixes.
        matches = [x for x in players if x['team'] == player['team'] and
                   (x.get('full') == player['canonical_name'] if player.get('canonical_name')
                    else x['short'] == player['sheet_name'])]
        if len(matches) != 1:
            raise r.Refused('Published/registry roster mapping differs: ' + player['sheet_name'])
    cutoff = datetime.combine(monday, datetime.min.time(), ZoneInfo('America/New_York'))
    config = {'run_id': f'{monday}-w{week}-r1', 'season': monday.year,
        'target_monday': monday.isoformat(), 'competition_week': week,
        'competition_week_evidence': 'HEBDO native prior week/date reconciled with published baseline; evidence/native_hebdo.json',
        'cutoff': cutoff.isoformat(), 'workflow_timezone': 'America/New_York',
        'profile_version': 'workflow-v2-2026-11-10', 'profile_file': 'profile.json',
        'roster_version': hashes['roster'], 'roster_file': 'roster.csv',
        'scoring_version': r.digest({'scoring': hashes['scoring'], 'transfers': hashes['transfers']}),
        'repository': 'peozenou/race', 'production_branch': 'main',
        'dashboard_url': f'https://peozenou.github.io/race/{monday.year}/'}
    profile = {'version': config['profile_version'],
        'approved_scope': source_files['profile'].read_text(),
        'destinations': context['destinations'],
        'native_targets': {n: sheets[n]['sheetId'] for n in sorted(required)},
        'source_epoch_recheck_required_at_start': True,
        'independent_elo': 'Complete weekly read-only check; append only under an explicitly bound Start scope.',
        'private_utr': 'User-supplied observations only; no carry-forward as a new week.'}
    # Validate everything before creating a usable run; no Start is recorded.
    root.mkdir(parents=True, mode=0o700)
    try:
        for key, src in source_files.items():
            dest = 'roster.csv' if key == 'roster' else 'evidence/' + key + ('.md' if key in {'profile', 'scoring'} else '.json')
            p = root / dest; p.parent.mkdir(exist_ok=True); p.write_bytes(src.read_bytes())
        r.atomic(root / 'profile.json', profile)
        r.atomic(root / 'input-config.json', config)
        r.atomic(root / 'preparation.json', {'target_monday': monday.isoformat(),
            'input_sha256': hashes, 'baseline_commit': baseline_commit,
            'prepared_at': r.now(), 'status': 'PREPARED_NOT_STARTED'})
        state = r.init(root, root / 'input-config.json')
        r.atomic(root / 'readiness-observation.template.json', {
            'season': monday.year, 'competition_week': week,
            'profile_hash': state['profile_sha256'], 'roster_hash': hashes['roster'],
            'expected_players': [x['tennis_abstract_slug'] for x in roster],
            'players': [{'player_id': x['tennis_abstract_slug'], 'serve_evidence_path': None,
                         'return_evidence_path': None} for x in roster],
            'event_scope_verified': False, 'watchlist_scope_verified': False,
            'watchlist_evidence': [], 'relevant_events': [], 'evidence': [],
            'cutoff_recheck_verified': False, 'dated_TE_release_verified': False})
        r.atomic(root / 'capture-worklist.json', {'status': 'AWAITING_PRIMARY_EVIDENCE',
            'players': [{'player_id': x['tennis_abstract_slug'], 'team': x['team'],
                         'sheet_id': sheets[x['sheet_name']]['sheetId'],
                         'views': ['Serve', 'Return'], 'state': 'pending'} for x in roster],
            'reuse_rule': 'Only reuse a capture when its entire dependency and event coverage are independently unchanged.'})
        checkpoints = [cutoff - timedelta(hours=6), cutoff - timedelta(hours=3),
                       cutoff + timedelta(minutes=30), cutoff + timedelta(hours=8, minutes=30)]
        r.atomic(root / 'weekend-plan.json', {'status': 'PREPARED_NOT_STARTED',
            'checkpoints': [x.isoformat() for x in checkpoints],
            'phone_delivery': 'PILOT_REQUIRED', 'unattended_source_access': 'PILOT_REQUIRED',
            'schedule_activation': 'OFF', 'required_decisions': ['Start exact week/profile', 'Approve exact candidate hash'],
            'optional_intake': 'UTR value and week, if supplied; never blocks Race',
            'claude_dispatch': 'Patrick passes the generated phase-3 brief explicitly'})
        return r.checked_status(root, state)
    except Exception:
        # Preserve partial evidence for diagnosis; never silently initialize over it.
        (root / 'PREPARATION_FAILED.txt').write_text('Incomplete preparation. Inspect and preserve; no Start was authorized.\n')
        raise


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('run-dir', 'target-monday', 'context', 'metadata', 'hebdo', 'transfers', 'baseline-dir', 'baseline-commit', 'scoring'):
        p.add_argument('--' + name, required=True)
    a = p.parse_args()
    try:
        out = prepare(a.run_dir, a.target_monday, a.context, a.metadata, a.hebdo, a.transfers,
                      a.baseline_dir, a.baseline_commit, a.scoring)
        print(json.dumps(out, indent=2))
    except (r.Refused, ValueError, KeyError, OSError) as e:
        p.exit(2, 'Preparation stopped: ' + str(e) + '\n')


if __name__ == '__main__':
    main()
