"""Private preparation tests: real transitions, no connected service calls."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from datetime import date

import weekend as w
import race_run as r
from test_race_run import Fixture


class WeekendTests(unittest.TestCase):
    def setUp(self):
        self.f = Fixture()
        self.f.bundle()
        self.base = self.f.root / 'candidate'
        players = r.read(self.base / 'players.json')
        for i, p in enumerate(players): p['short'] = f'Player{i:02}'
        self.f.put('candidate/players.json', players)
        hebdo = r.read(self.base / 'hebdo.json')
        for row in hebdo: row.update(week=38, date='2026-11-09')
        self.f.put('candidate/hebdo.json', hebdo)
        serial = (date(2026, 11, 9) - date(1899, 12, 30)).days
        self.f.put('native.json', {'values': [[], [], [serial, 38] + [6, 0, 6]*5]})
        names = ['HEBDO','BILAN','TEAMS','JOUEURS','LIVE','TRANSFERTS'] + [f'Player{i:02}' for i in range(30)]
        self.f.put('metadata.json', {'sheets': [{'properties': {'title': n, 'sheetId': i}} for i,n in enumerate(names)]})
        self.f.put('transfers.json', {'values': [['Synthetic transfer ledger']]})
        self.f.put('scoring.md', 'Synthetic +5 duel rule')
        self.f.put('context.json', {'roster_file': str(self.f.root/'roster.csv'),
            'profile_file': str(self.f.root/'profile.json'), 'destinations': {'race': {'spreadsheet_id': 'synthetic-private'}}})
        self.root = self.f.root / 'prepared'

    def tearDown(self):
        self.f.clock.stop(); self.f.tmp.cleanup()

    def prepare(self):
        f=self.f.root
        return w.prepare(self.root, '2026-11-16', f/'context.json', f/'metadata.json',
            f/'native.json', f/'transfers.json', self.base, '1'*40, f/'scoring.md')

    def test_week_is_derived_from_league_and_no_start_is_granted(self):
        report=self.prepare();state=r.load(self.root)
        self.assertEqual(state['config']['competition_week'],39)
        self.assertIsNone(state['start_approval'])
        self.assertEqual(report['percent'],0)
        self.assertEqual(report['state'],'waiting_readiness')
        self.assertIn('not approval',report['next_action'])
        self.assertEqual(list(r.checked_status(self.root,r.load(self.root))['phases']),list(r.PHASES))
        self.assertTrue((self.root/'PROGRESS.html').exists())
        plan=r.read(self.root/'weekend-plan.json')
        self.assertEqual(plan['checkpoints'],['2026-11-15T18:00:00-05:00','2026-11-15T21:00:00-05:00','2026-11-16T00:30:00-05:00','2026-11-16T08:30:00-05:00'])
        self.assertEqual(r.read(self.root/'evidence/native_hebdo.json'),r.read(self.f.root/'native.json'))
        self.assertEqual(r.read(self.root/'evidence/baseline_hebdo.json'),r.read(self.base/'hebdo.json'))

    def test_repeat_is_idempotent_and_changed_input_is_refused(self):
        self.prepare();before=(self.root/'run-state.json').read_bytes()
        self.prepare();self.assertEqual(before,(self.root/'run-state.json').read_bytes())
        self.f.put('scoring.md','Changed rule')
        with self.assertRaises(r.Refused): self.prepare()

    def test_transfer_display_label_is_not_an_identity(self):
        import csv
        p=self.f.root/'roster.csv'
        with p.open(newline='') as f: rows=list(csv.DictReader(f))
        for x in rows:x['canonical_name']=x['sheet_name']+' Full'
        with p.open('w',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
        players=r.read(self.base/'players.json')
        for i,x in enumerate(players):
            x['full']=f'Player{i:02} Full';x['short']+=' (entré)'
        self.f.put('candidate/players.json',players)
        self.assertIsNone(self.prepare()['readiness'])

    def test_mismatched_published_total_is_not_a_new_week(self):
        x=r.read(self.base/'hebdo.json');x[0]['total']=99;self.f.put('candidate/hebdo.json',x)
        with self.assertRaises(r.Refused): self.prepare()
        self.assertFalse(self.root.exists())

    def test_archived_roster_and_existing_week_are_refused(self):
        x=r.read(self.f.root/'metadata.json');x['sheets'][-1]['properties']['hidden']=True;self.f.put('metadata.json',x)
        with self.assertRaises(r.Refused):self.prepare()
        x['sheets'][-1]['properties']['hidden']=False
        x['sheets'].append({'properties':{'title':'20261116w39','sheetId':999}})
        self.f.put('metadata.json',x)
        with self.assertRaises(r.Refused):self.prepare()

    def test_skipped_date_and_public_checkout_are_refused(self):
        x=r.read(self.f.root/'native.json');x['values'][2][0]-=7;self.f.put('native.json',x)
        with self.assertRaises(r.Refused):self.prepare()
        self.root=self.f.root/'public'/'private-run';(self.f.root/'public/.git').mkdir(parents=True)
        with self.assertRaises(r.Refused):self.prepare()

if __name__=='__main__': unittest.main()
