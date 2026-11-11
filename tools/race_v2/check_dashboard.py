#!/usr/bin/env python3
"""Offline six-JSON bundle checks against an independently prepared source contract.

No API, GitHub mutation or automatic conversion of nulls. Does not prove source truth.
"""
import argparse
import hashlib
import json
import math
from collections import Counter
from datetime import date
from pathlib import Path

FILES=('hebdo','joueurs','players','matches','calendar','team_colors')

def check(data_dir, expected):
    problems=[]; notes=[]; tables={}; hashes={}
    def require(condition,message):
        if not condition: problems.append(message)
    for name in FILES:
        path=Path(data_dir)/(name+'.json')
        raw=path.read_bytes(); hashes[name]=hashlib.sha256(raw).hexdigest()
        rows=json.loads(raw)
        require(isinstance(rows,list),name+': expected a list of row objects')
        if not isinstance(rows,list): rows=[]
        tables[name]=rows
        require(len(rows)==expected['expected_rows'][name],name+': row count differs from source contract')
        cols=set(expected['expected_columns'][name])
        for n,row in enumerate(rows,1):
            if not isinstance(row,dict): problems.append(f'{name} row {n}: not an object');continue
            require(set(row)==cols,f'{name} row {n}: schema keys differ')
            def inspect(v):
                if isinstance(v,float):require(math.isfinite(v),f'{name} row {n}: non-finite number')
                elif isinstance(v,dict):
                    for k,x in v.items(): inspect(k);inspect(x)
                elif isinstance(v,list):
                    for x in v:inspect(x)
                elif isinstance(v,str):
                    lower=v.casefold()
                    require(not any(p in lower for p in ('tiago','matchtrack','tiago_private','@gmail.com','@orange.fr','@yahoo.fr')),
                            f'{name} row {n}: private content detected')
            inspect(row)
            for k in row:
                require(k.casefold() not in {'utr','email','recipients','draft_id','observation_date','reporter','raw_file'},
                        f'{name} row {n}: private/unexpected field {k}')
    teams=set(expected['teams']); active=set(expected['active_players']); week=expected['target_week']
    archived=set(expected['archived_players']); published=set(expected['published_players'])
    current=set(expected['current_week_players'])
    require(len(teams)==5 and len(active)==30,'Expected source contract requires 5 teams / 30 active players')
    require(not (active & archived) and published==active|archived,'Published set must resolve active and retained outgoing identities')
    date.fromisoformat(expected['target_date'])
    def unique(rows,keys,label):
        observed=Counter(tuple(r[k] for k in keys) for r in rows)
        require(all(n==1 for n in observed.values()),label+': duplicate logical keys')
    unique(tables['hebdo'],('team','week'),'HEBDO')
    unique(tables['joueurs'],('team','player','week'),'JOUEURS')
    unique(tables['players'],('player',),'players')
    unique(tables['matches'],('mid',),'matches export IDs')
    # Source crosswalk must separately certify stable perspective IDs; do not merge two sides of one contest.
    unique(tables['matches'],('player','event_date','event','round','opponent','score'),'match perspectives')
    require({r['player'] for r in tables['players']}==published,'players: published membership differs from source contract')
    selected=[r for r in tables['players'] if r['player'] in active]
    require(Counter(r['team'] for r in selected)==Counter({t:6 for t in teams}),'players: active selection requires 6 per team')
    require({r['team'] for r in tables['team_colors']}==teams,'team colors differ from source teams')
    for name in ('hebdo','joueurs'):
        require(all(type(r['week']) is int and 0<=r['week']<=week for r in tables[name]),name+': invalid/future week')
    h=[r for r in tables['hebdo'] if r['week']==week]
    require(len(h)==5 and {r['team'] for r in h}==teams,'HEBDO: target week requires five teams')
    require(max((r['week'] for r in tables['hebdo']),default=-1)==week,'HEBDO latest week differs')
    for r in h:
        require(r['date']==expected['target_date'],'HEBDO target date differs')
        source=expected['team_totals'][r['team']]
        for key in ('race','duels','total'):
            require(type(r[key]) in (int,float) and r[key]==source[key],f"HEBDO {r['team']}: {key} differs from source")
        adjustment=source.get('adjustment',0)
        require(r['total']==r['race']+r['duels']+adjustment,f"HEBDO {r['team']}: sum/adjustment differs")
    j=[r for r in tables['joueurs'] if r['week']==week]
    require({r['player'] for r in j}==current,'JOUEURS target week differs from expected transfer/contribution set')
    for r in tables['joueurs']:
        require(r['race'] is None or (type(r['race']) in (int,float) and r['race']>=0),'JOUEURS Race must be numeric or null')
        if r['race'] is None:notes.append(f"Null retained: {r['player']} week {r['week']}")
    for r in tables['players']:
        for key in ('rankings_date','elo_date'):
            source_dates=expected.get('source_dates_by_player',{}).get(r['player'],expected['source_dates'])
            require(r.get(key)==source_dates.get(key),f"{r['player']}: {key} differs from selected source")
        for key in ('tpw','rpw','ace_pct','first_won','second_won'):
            value=r.get(key)
            require(value is None or (type(value) in (int,float) and 0<=value<=1),f"{r['player']}: {key} not fraction/null")
    require(expected.get('field_reconciliation_passed') is True,'Full source-to-export field reconciliation is not certified')
    if any(r.get('race') is None for r in j):notes.append('Target-week nulls need explicit dashboard compatibility/release qualification.')
    return {'result':'FAIL' if problems else ('QUALIFIED' if notes else 'PASS'),
            'scope':'Offline structural/internal checks; independent source comparison is separately required',
            'row_counts':{n:len(tables[n]) for n in FILES}, 'sha256':hashes,
            'problems':problems, 'qualifications':notes}

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data-dir',type=Path,required=True);p.add_argument('--expected-file',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args(argv)
    try:r=check(a.data_dir,json.loads(a.expected_file.read_text()))
    except (KeyError,ValueError,OSError,TypeError) as e:r={'result':'FAIL','problems':['Invalid bundle/source contract: '+str(e)]}
    a.output.write_text(json.dumps(r,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'result':r['result'],'problems':r.get('problems',[])},ensure_ascii=False))
    return 2 if r['result']=='FAIL' else 0

if __name__=='__main__':raise SystemExit(main())
