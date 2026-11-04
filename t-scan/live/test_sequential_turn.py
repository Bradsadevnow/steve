"""Three separate model choices with real task/world state and native receipts."""
import copy,json,tempfile,unittest
from pathlib import Path
from grid_world import GridWorld,GridDispatch
from runtime_store import RuntimeStore
from agent_notepad import AgentDispatch
from grid_conversation import GridConversation
from movement_tools import registry
from decision_executor import chat_events
from agent_task_list import context
from world_test_support import publish,poll

def response(name=None,args=None,finish='tool_calls'):
 return dict(kind='response',text='' if name else 'Done speaking.',calls=[] if name is None else [dict(id='provider',type='function',function=dict(name=name,arguments=json.dumps(args or {})))],finish=finish)

class SequentialTurnTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.runtime=RuntimeStore(self.root/'memory.db');self.world=GridWorld(self.root/'world.json');publish(self.world);self.world.wake('human')
  world=self.world
  class PresentedDispatch(GridDispatch):
   def wait(self,key):
    if world.pending:world.acknowledge('test',world.pending['action_id'],world.state['session_id'])
    return super().wait(key)
  self.dispatch=AgentDispatch(PresentedDispatch(world),self.runtime);self.dispatch.run_id='run'
  self.conversation=GridConversation(self.root/'chat.json',self.runtime);self.conversation.run_id='run';self.seen=[];self.stopped=False
 def tearDown(self):self.runtime.close();self.tmp.cleanup()
 def run_turn(self,choose,phase=None):
  if phase:self.runtime.agent.transition(phase,'test fixture','run')
  owner=self
  class Client:
   def stream(self,messages,tools,*args):
    owner.seen.append(copy.deepcopy(messages));yield choose(len(owner.seen),messages,tools)
  return list(chat_events(Client(),self.conversation.messages,self.dispatch,'turn',registry(phase=phase),1,lambda:self.conversation.context(self.dispatch),self.conversation.checkpoint,lambda:self.stopped))
 def test_three_movements_each_observe_settled_feedback_and_new_binding(self):
  def choose(n,messages,tools):
   state=self.world.observe();self.assertIsNone(state['presentation']);self.assertEqual(state['self']['col'],4+n)
   self.assertEqual(self.dispatch.body.bound,state['observation_id'])
   if n>1:
    result=json.loads(next(m['content'] for m in reversed(messages) if m['role']=='tool'));self.assertEqual(result['presentation_status'],'settled')
    self.assertEqual(result['position_after'],dict(x=4+n,y=5))
   return response('move_east')
  events=self.run_turn(choose,'executor');self.assertEqual(len(self.seen),3);self.assertEqual(self.world.state['avatar']['col'],8);self.assertTrue(self.world.running)
  self.assertEqual(events[-1]['reason'],'tool_call_limit');calls=[e['call']['id'] for e in events if e['kind']=='call'];self.assertEqual(len(set(calls)),3)
  for m in self.conversation.messages:
   if m['role']=='tool':self.assertIn(m['tool_call_id'],calls)
 def test_task_edits_use_feedback_revisions_without_automatic_repair(self):
  def choose(n,messages,tools):
   if n>1:self.assertEqual(json.loads(next(m['content'] for m in reversed(messages) if m['role']=='tool'))['task_list_revision'],n-1)
   return response('task_list_write',dict(task_id='task'+str(n),title='Goal '+str(n),status='pending',expected_revision=n-1))
  self.run_turn(choose,'planner');self.assertEqual(context(self.runtime)['revision'],3);self.assertEqual(len(context(self.runtime)['tasks']),3);self.assertFalse(self.world.receipts)
 def test_repeated_stale_calls_exhaust_budget_without_repair(self):
  events=self.run_turn(lambda *a:response('task_list_write',dict(task_id='x',title='x',status='pending',expected_revision=99)),'planner')
  self.assertEqual([e['result']['outcome'] for e in events if e['kind']=='receipt'],['rejected_stale_task_list']*3);self.assertEqual(context(self.runtime)['revision'],0)
 def test_handoff_ends_before_executor_call_and_refreshes_registry(self):
  def choose(n,*a):
   if n==1:return response('task_list_write',dict(task_id='x',title='Visit blue',status='pending',expected_revision=0))
   return response('plan_handoff',dict(task_id='x',task_list_revision=1,reason='Requested visit',criterion='visit_landmark',landmark_id='target_blue',instructions='Visit blue'))
  events=self.run_turn(choose,'planner');self.assertEqual(len(self.seen),2);self.assertEqual(events[-1]['reason'],'phase_boundary');self.assertFalse(self.world.receipts)
  phase=self.runtime.agent.phase()['phase'];self.assertEqual(phase,'executor');self.assertIn('move_east',registry(phase=phase).SCHEMAS);self.assertNotIn('task_list_write',registry(phase=phase).SCHEMAS)
 def test_replan_and_complete_end_early(self):
  for name in ('request_replan','complete'):
   with self.subTest(name=name):
    self.seen=[];events=self.run_turn(lambda *a:response(name,dict(reason='Review progress') if name=='request_replan' else {}),'executor');self.assertEqual(len(self.seen),1);self.assertEqual(events[-1]['reason'],'phase_boundary')
 def test_text_only_reply_after_tool_returns_no_action_reason(self):
  events=self.run_turn(lambda n,*a:response('task_list_read') if n==1 else response(),'planner');self.assertEqual(len(self.seen),2);self.assertEqual(events[-1]['reason'],'model_finished')
 def test_operator_interrupt_after_receipt_prevents_next_inference(self):
  original=self.dispatch.wait
  def wait(key):result=original(key);self.stopped=True;return result
  self.dispatch.wait=wait
  with self.assertRaises(InterruptedError):self.run_turn(lambda *a:response('move_east'),'executor')
  self.assertEqual(len(self.seen),1);self.assertEqual(self.world.state['avatar']['col'],6);self.assertEqual(self.conversation.messages[-1]['role'],'tool')
 def test_presentation_timeout_ends_turn(self):
  self.dispatch.wait=lambda key:dict(outcome='moved',presentation_status='timeout')
  events=self.run_turn(lambda *a:response('move_east'),'executor');self.assertEqual(len(self.seen),1);self.assertEqual(events[-1]['reason'],'interrupted')
 def test_multiple_calls_in_single_response_are_all_rejected(self):
  def choose(*a):
   value=response('move_east');value['calls']+=response('move_north')['calls'];return value
  events=self.run_turn(choose,'executor');self.assertEqual(len(self.seen),1);self.assertEqual(self.world.state['avatar']['col'],5);self.assertEqual(events[-1]['reason'],'rejected_conflict')
 def test_provider_output_limit_does_not_execute_tool(self):
  self.run_turn(lambda *a:response('move_east',finish='length'),'executor');self.assertFalse(self.world.receipts)

if __name__=='__main__':unittest.main()
