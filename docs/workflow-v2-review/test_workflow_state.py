"""Offline contract tests; synthetic input, no live side effects."""
import unittest
from workflow_state import PHASE_WEIGHTS, assess_readiness, queue_start_request, accept_start_approval, calculate_progress, revise_workset
CONTEXT = {'season':2026,'competition_week':39,'profile_hash':'a'*64,'roster_hash':'b'*64}
def ready_observation():
    players=[f'synthetic-player-{i:02d}' for i in range(1,31)]
    return {**CONTEXT,'expected_players':players,'source_errors':[], 'event_scope_verified':True,'watchlist_scope_verified':True,
        'players':[{'player_id':p,'serve_verified':True,'return_verified':True,'serve_result_ids':['synthetic-final'],'return_result_ids':['synthetic-final']} for p in players],
        'relevant_events':[{'event_id':'synthetic-event','closure':'COMPLETE','watched_results':[{'result_id':'synthetic-final','status':'COMPLETED','selected_players':players[:2]}]}],
        'cutoff_recheck_verified':False,'dated_TE_release_verified':False}
def blank_run():
    return {'production_verified':False,'phases':{n:{'total':4,'verified':0,'status':'pending','workset_revision':1} for n in PHASE_WEIGHTS}}
class ReadinessTests(unittest.TestCase):
    def test_sunday_start_is_not_monday_release(self):
        o=ready_observation();r=assess_readiness(o,CONTEXT)
        self.assertTrue(r['ready_to_start']);self.assertFalse(r['release_sources_ready']);self.assertEqual(r['release_waits'],['cutoff_recheck','dated_TE_release'])
        o.update(cutoff_recheck_verified=True,dated_TE_release_verified=True);self.assertTrue(assess_readiness(o,CONTEXT)['release_sources_ready'])
    def test_missing_and_duplicate_coverage_fail_closed(self):
        for duplicate in (False,True):
            o=ready_observation();o['players'].pop()
            if duplicate:o['players'].append(o['players'][0])
            self.assertEqual(assess_readiness(o,CONTEXT)['status'],'UNKNOWN')
    def test_fetch_error_is_unknown(self):
        o=ready_observation();o['source_errors']=['timeout'];self.assertEqual(assess_readiness(o,CONTEXT)['status'],'UNKNOWN')
    def test_empty_events_need_explicit_scope_proof(self):
        o=ready_observation();o['relevant_events']=[];self.assertEqual(assess_readiness(o,CONTEXT)['status'],'UNKNOWN')
        o['no_relevant_events_confirmed']=True;self.assertTrue(assess_readiness(o,CONTEXT)['ready_to_start'])
    def test_unfinished_is_not_ready(self):
        o=ready_observation();o['relevant_events'][0]['closure']='ONGOING';o['relevant_events'][0]['watched_results'][0]['status']='UNFINISHED'
        self.assertEqual(assess_readiness(o,CONTEXT)['status'],'NOT_READY')
    def test_both_TA_views_must_reflect_completed_results(self):
        o=ready_observation();o['players'][0]['return_result_ids']=[];r=assess_readiness(o,CONTEXT)
        self.assertEqual(r['status'],'NOT_READY');self.assertTrue(any('TA_lag' in x for x in r['pending']))
    def test_profile_mismatch_is_unknown(self):
        o=ready_observation();o['profile_hash']='c'*64;self.assertEqual(assess_readiness(o,CONTEXT)['status'],'UNKNOWN')
    def test_week_dedupe_and_stale_candidate_rejection(self):
        o=ready_observation();r=assess_readiness(o,CONTEXT);request,outbox=queue_start_request(r,[])
        self.assertIsNone(queue_start_request(r,outbox)[0]);self.assertEqual(len(outbox),1)
        o['players'][2]['serve_result_ids'].append('changed-source');new=assess_readiness(o,CONTEXT);self.assertIsNone(queue_start_request(new,outbox)[0])
        command={'owner_authenticated':True,'approved':True,'request_id':request['request_id'],'readiness_hash':r['readiness_hash']}
        with self.assertRaisesRegex(ValueError,'stale candidate'):accept_start_approval(command,request,new)
        self.assertTrue(accept_start_approval(command,request,r)['approved'])
    def test_pending_request_refreshes_without_another_notification(self):
        observation=ready_observation();old=assess_readiness(observation,CONTEXT)
        old_request,outbox=queue_start_request(old,[])
        outbox[0]['delivery_status']='DELIVERED_SYNTHETIC'
        observation['players'][2]['serve_result_ids'].append('later-source-evidence')
        current=assess_readiness(observation,CONTEXT)
        notification,updated=queue_start_request(current,outbox)
        self.assertIsNone(notification);self.assertEqual(len(updated),1)
        self.assertEqual(updated[0]['delivery_status'],'DELIVERED_SYNTHETIC')
        self.assertEqual(updated[0]['superseded_request_ids'],[old_request['request_id']])
        self.assertNotEqual(updated[0]['request_id'],old_request['request_id'])
        command={'owner_authenticated':True,'approved':True,'request_id':updated[0]['request_id'],'readiness_hash':current['readiness_hash']}
        self.assertTrue(accept_start_approval(command,updated[0],current)['approved'])
        self.assertEqual(outbox[0]['readiness_hash'],old['readiness_hash'])
    def test_accepted_request_cannot_be_replayed(self):
        readiness=assess_readiness(ready_observation(),CONTEXT)
        request,_=queue_start_request(readiness,[])
        command={'owner_authenticated':True,'approved':True,'request_id':request['request_id'],'readiness_hash':readiness['readiness_hash']}
        request['approval_status']='APPROVED'
        with self.assertRaisesRegex(ValueError,'not pending'):
            accept_start_approval(command,request,readiness)
    def test_notification_never_approves(self):
        r=assess_readiness(ready_observation(),CONTEXT);request,_=queue_start_request(r,[])
        with self.assertRaisesRegex(ValueError,'explicit'):accept_start_approval({'request_id':request['request_id'],'readiness_hash':r['readiness_hash']},request,r)
        self.assertEqual(request['approval_status'],'PENDING')
class ProgressTests(unittest.TestCase):
    def test_weighted_units_while_waiting(self):
        r=blank_run();r['phases']['acquire'].update(verified=4,status='completed');r['phases']['validate'].update(verified=2,status='waiting')
        p=calculate_progress(r);self.assertEqual(p['percent'],50);self.assertFalse(p['complete'])
    def test_unknown_active_total_is_indeterminate(self):
        r=blank_run();r['phases']['acquire'].update(total=None,verified=2,status='running');p=calculate_progress(r)
        self.assertIsNone(p['percent']);self.assertTrue(p['indeterminate']);self.assertEqual(p['verified_floor_percent'],0)
    def test_order_barrier(self):
        r=blank_run();r['phases']['release'].update(verified=1,status='running')
        with self.assertRaisesRegex(ValueError,'barrier'):calculate_progress(r)
    def test_no_false_100(self):
        r=blank_run()
        for p in r['phases'].values():p.update(verified=4,status='completed')
        with self.assertRaisesRegex(ValueError,'production proof'):calculate_progress(r)
        r['production_verified']=True;self.assertTrue(calculate_progress(r)['complete']);self.assertEqual(calculate_progress(r)['percent'],100)
    def test_explicit_workset_revision_preserves_verified_work(self):
        r=blank_run();r['phases']['acquire'].update(verified=2,status='running');n=revise_workset(r,'acquire',8,'Additional evidenced pages discovered')
        self.assertEqual(n['phases']['acquire']['verified'],2);self.assertEqual(n['phases']['acquire']['workset_revision'],2)
        self.assertEqual(n['progress']['percent'],8.75);self.assertEqual(len(n['workset_events']),1);self.assertEqual(r['phases']['acquire']['total'],4)
        with self.assertRaises(ValueError):revise_workset(r,'acquire',1,'Discard work')
    def test_unverified_units_cannot_be_completed(self):
        r=blank_run();r['phases']['acquire'].update(verified=3,status='completed')
        with self.assertRaisesRegex(ValueError,'all verified'):calculate_progress(r)
if __name__=='__main__':unittest.main()
