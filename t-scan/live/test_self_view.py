import copy,json,tempfile,unittest
from pathlib import Path
from runtime_store import RuntimeStore
from grid_world import GridWorld
from agent_task_list import execute
from self_view import build
from world_test_support import publish

class SelfViewTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.r=RuntimeStore(self.root/'memory.db');self.w=GridWorld(self.root/'world.json');publish(self.w)
 def tearDown(self):self.r.close();self.tmp.cleanup()
 def view(self,run='run-a'):return build(self.r,self.w,run,dict(status='ready'))
 def task(self):execute(self.r,'task_list_write',dict(task_id='blue',title='Visit blue',status='pending',expected_revision=0),'task')
 def plan(self):
  self.task();self.r.agent.execute('plan_handoff',dict(task_id='blue',task_list_revision=1,reason='Human requested the visit',criterion='visit_landmark',landmark_id='target_blue',instructions='Visit the selected landmark'),'handoff','decision','run-a',self.w.observe())
 def claim(self,owner='self',scope='global',status='held'):
  return self.r.agent.execute('assertion_write',dict(owner=owner,claim_id='claim',dimension='competence',statement='I need to record completed tasks before leaving.',status=status,scope=scope,source_refs='',reason='My assessment of past attempts',expected_revision=0),'claim','decision','run-a',self.w.observe())
 def test_curator_notes_stay_in_inspection_not_self_authored_state(self):
  self.r.import_seed(dict(records=[dict(key='seed',kind='self_model',status='curated_self_model',summary='A curator described Steve as warm.',source=dict(path='curation'))]))
  view=self.view();self.assertEqual(view['assessments'],[]);self.assertEqual(view['beliefs'],[])
  self.assertEqual(view['inspection']['records'][0]['statement'],'A curator described Steve as warm.')
 def test_unfinished_task_never_becomes_automatically_selected_focus(self):
  self.task();view=self.view();self.assertIsNone(view['focus']);self.assertEqual(view['unfinished'][0]['title'],'Visit blue');self.assertIsNone(self.r.agent.get('plan','current'))
 def test_explicit_focus_and_reason_disappear_when_task_completed_or_run_changes(self):
  self.plan();view=self.view();self.assertEqual(view['focus']['reason'],'Human requested the visit');self.assertIsNone(self.view('run-b')['focus'])
  execute(self.r,'task_mark_complete',dict(task_id='blue',expected_revision=1),'complete-task')
  view=self.view();self.assertIsNone(view['focus']);self.assertEqual(view['unfinished'],[])
  self.assertEqual(view['finished'],[dict(id='blue',title='Visit blue',status='completed')])
  self.assertFalse(self.w.receipts)  # A task status is Steve's claim, not proof of arrival.
 def test_self_assessments_and_beliefs_preserve_authored_text(self):
  self.claim();view=self.view();self.assertEqual(view['assessments'][0]['statement'],'I need to record completed tasks before leaving.');self.assertEqual(view['beliefs'],[])
 def test_old_run_claim_is_only_in_inspection(self):
  self.claim(scope='run');view=self.view('run-b');self.assertEqual(view['assessments'],[]);self.assertEqual(len(view['inspection']['records']),1)
 def test_projection_does_not_modify_state_or_promote_claims(self):
  self.plan();self.claim();world=copy.deepcopy(self.w.state);before=self.r.db.total_changes;records=self.r.agent.records()
  first=self.view();self.view();self.assertEqual(self.r.db.total_changes,before);self.assertEqual(self.r.agent.records(),records);self.assertEqual(self.w.state,world)
  self.assertFalse(self.w.receipts);self.assertEqual(first['activity'],'Idle')
 def test_measured_activity_comes_from_current_run_controller_evidence(self):
  r=self.w.nominate('move_east',{},'move',self.w.observe()['observation_id'],'action');self.w.acknowledge('test',r['action_id'],self.w.state['session_id']);receipt=self.w.wait(r['action_id']);self.r.agent.evidence('run-a',receipt)
  view=self.view();self.assertEqual(view['attempts']['moved'],1);self.assertIn('(5, 5) → (6, 5)',view['recent'][0]['summary']);self.assertEqual(self.view('run-b')['recent'],[])
 def test_retired_assessment_is_hidden_and_private_operator_notes_not_loaded(self):
  self.claim(status='retired');view=self.view();self.assertEqual(view['assessments'],[]);self.assertNotIn('operator_notes',view)

 def goal(self,key='visit_in_order',status='active',lifetime='run',revision=0):
  return self.r.agent.execute('intention_write',dict(intention_id=key,statement='Visit blue, then red, then yellow.',reason='Human request',status=status,lifetime=lifetime,expected_revision=revision),'goal-'+key+status,'decision','run-a',self.w.observe())
 def test_goal_and_tasks_are_shown_separately_and_in_list_order(self):
  self.goal();self.task();execute(self.r,'task_list_write',dict(task_id='red',title='Visit red',status='in_progress',expected_revision=1),'task2')
  view=self.view();self.assertEqual([g['id'] for g in view['goals']],['visit_in_order']);self.assertEqual(view['goals'][0]['status'],'active')
  self.assertEqual([(t['id'],t['status']) for t in view['tasks']],[('blue','pending'),('red','in_progress')]);self.assertIn('own assessments',view['status_note'])
  self.assertEqual(view['commitments'],[])
 def test_focus_and_goal_link_come_from_the_agents_plan(self):
  self.goal();self.task()
  self.r.agent.execute('plan_handoff',dict(task_id='blue',task_list_revision=1,reason='Human requested the visit',criterion='visit_landmark',landmark_id='target_blue',instructions='Visit the selected landmark',intention_id='visit_in_order'),'handoff','decision','run-a',self.w.observe())
  view=self.view();self.assertEqual(view['focus']['goal_id'],'visit_in_order');self.assertTrue(view['goals'][0]['linked_to_focus']);self.assertEqual([t['in_focus'] for t in view['tasks']],[True])
 def test_unlinked_goal_and_unselected_tasks_are_not_marked_as_focus(self):
  self.goal();self.task();view=self.view();self.assertFalse(view['goals'][0]['linked_to_focus']);self.assertEqual([t['in_focus'] for t in view['tasks']],[False])
 def test_fulfilled_goal_stays_visible_as_an_assessment_and_is_not_a_commitment(self):
  self.goal();self.goal(status='fulfilled',revision=1);view=self.view()
  self.assertEqual([(g['id'],g['status']) for g in view['goals']],[('visit_in_order','fulfilled')]);self.assertEqual(view['commitments'],[])
 def test_goal_from_another_run_is_not_listed(self):
  self.goal();self.assertEqual(self.view('run-b')['goals'],[])
 def test_persistent_commitment_is_a_commitment_not_a_run_goal(self):
  self.goal(key='keep_promises',lifetime='persistent');view=self.view();self.assertEqual(view['goals'],[]);self.assertEqual([c['id'] for c in view['commitments']],['keep_promises'])

if __name__=='__main__':unittest.main()
