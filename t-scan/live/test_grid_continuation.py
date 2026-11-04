"""Regression fixtures exercise the real scheduler; fake model outputs exist only in tests."""
import copy,json,tempfile,threading,time,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from grid_world import GridWorld
from grid_worker import claim_job,run
from grid_conversation import GridConversation
from runtime_store import RuntimeStore
from world_test_support import publish,poll

class ContinuationTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.world=GridWorld(self.root/'world.json');publish(self.world,'presenter')
  self.b=SimpleNamespace(lock=threading.RLock(),grid_world=self.world,pending=None,active_kind=None,turn_interrupt=threading.Event())
 def tearDown(self):self.tmp.cleanup()
 def message(self,key='human-1'):
  self.b.pending=dict(source='user',prompt='A user message',requestId=key)
 def test_human_wakes_and_action_feedback_keeps_loop_active(self):
  self.assertIsNone(claim_job(self.b,0,1));self.message();self.assertEqual(claim_job(self.b,0,1)['source'],'user');self.assertTrue(self.world.running)
  r=self.world.nominate('move_east',{},'turn',self.world.observe()['observation_id'],'call');self.world.acknowledge('presenter',r['action_id'],self.world.state['session_id'])
  self.b.active_kind=None
  self.assertIsNone(claim_job(self.b,2,1));self.assertEqual(claim_job(self.b,2,2)['source'],'tick')
 def test_no_action_idle_pause_is_not_forged_as_agent_tool_use(self):
  self.world.wake('human');before=copy.deepcopy(self.world.state);self.world.idle()
  self.assertFalse(self.world.running);self.assertEqual(self.world.pause_reason,'no_action');self.assertEqual(self.world.receipts,[]);self.assertEqual(self.world.state,before)
  self.message('next-human');claim_job(self.b,0,1);self.assertTrue(self.world.running)
 def test_agent_pause_is_receipted_without_moving_then_human_wakes(self):
  self.world.wake('human-1');before=copy.deepcopy(self.world.state);obs=self.world.observe()['observation_id']
  r=self.world.nominate('complete',{},'turn',obs,'call');self.assertEqual(r['outcome'],'interaction_complete');self.assertEqual(r['presentation_status'],'not_required');self.assertFalse(self.world.running)
  self.assertEqual(self.world.state['avatar'],before['avatar']);self.assertEqual(self.world.state['world_revision'],before['world_revision']);self.assertEqual(self.world.observe()['decision_loop']['pause_reason'],'complete')
  self.assertIsNone(claim_job(self.b,0,1));self.message('human-2');claim_job(self.b,0,1);self.assertTrue(self.world.running);self.assertEqual(self.world.loop_origin,'human-2')
 def test_pending_presentation_blocks_next_decision_and_keeps_human_message(self):
  self.world.wake('human-1');r=self.world.nominate('move_east',{},'turn',self.world.observe()['observation_id'],'call');self.message()
  self.assertIsNone(claim_job(self.b,0,1));self.assertIsNotNone(self.b.pending)
  self.world.acknowledge('presenter',r['action_id'],self.world.state['session_id']);self.assertEqual(claim_job(self.b,0,1)['source'],'user')
 def test_human_input_wins_over_due_continuation(self):
  self.world.wake('old');self.message('new');job=claim_job(self.b,0,1);self.assertEqual(job['requestId'],'new');self.assertEqual(self.world.loop_origin,'new')
 def test_stale_or_denied_pause_does_not_stop_loop(self):
  self.world.wake('human');r=self.world.nominate('complete',{},'turn','stale','call');self.assertEqual(r['outcome'],'rejected_stale');self.assertTrue(self.world.running)
  self.world.authorizer=lambda nomination,state:(False,'not admitted');r=self.world.nominate('complete',{},'turn-2',self.world.observe()['observation_id'],'call-2');self.assertEqual(r['decision'],'DENY');self.assertTrue(self.world.running)
 def test_pause_is_available_even_if_presentation_client_is_offline(self):
  self.world.wake('human');self.world.last_poll=-1e9;r=self.world.nominate('complete',{},'turn',self.world.observe()['observation_id'],'call');self.assertEqual(r['outcome'],'interaction_complete')
 def test_actual_worker_continues_two_steps_pauses_and_wakes_again(self):
  bridge=self.b;bridge.request=threading.Event();bridge.shutdown=threading.Event();bridge.state={};bridge.turn_start=None
  bridge.runtime=RuntimeStore(self.root/'memory.db');bridge.conversation=GridConversation(self.root/'conversation.json',bridge.runtime)
  bridge.update=lambda **kw:bridge.state.update(kw)
  seen=[]
  class FakeModel:
   context=131072
   def __init__(self,*args):pass
   def connect(self):return {}
   def appraisal(self,messages):return '{"signals":[]}'
   def stream(self,messages,tools,temperature,should_stop):
    seen.append(copy.deepcopy(messages));n=len(seen)
    previous=[json.loads(m['content']) for m in messages if m['role']=='tool']
    if n==2:assert previous[-1]['presentation_status']=='settled'
    name='move_east' if n<=2 else 'complete'
    yield dict(kind='response',text='',calls=[dict(id='fixture',type='function',function=dict(name=name,arguments='{}'))],finish='tool_calls')
  args=SimpleNamespace(lm_url='http://unused',model='test-fixture',ctx=131072,temperature=.1)
  self.message();bridge.pending['source_id']=bridge.runtime.accept_user('A user message','human-1')
  def await_pause(count):
   deadline=time.monotonic()+4
   while time.monotonic()<deadline:
    poll(self.world,'presenter')
    if self.world.pending:self.world.acknowledge('presenter',self.world.pending['action_id'],self.world.state['session_id'])
    if len(seen)>=count and not self.world.running and bridge.active_kind is None:return
    time.sleep(.01)
   self.fail('Worker did not reach explicit pause')
  with patch('grid_worker.LMStudio',FakeModel):
   thread=threading.Thread(target=run,args=(bridge,args),daemon=True);thread.start()
   try:
    await_pause(3);self.assertEqual(self.world.state['avatar']['col'],7)
    self.assertEqual([r['action'] for r in self.world.receipts],['move_east','move_east','complete'])
    self.message('human-2');bridge.pending['source_id']=bridge.runtime.accept_user('Another message','human-2');bridge.request.set();await_pause(4)
    self.assertEqual(self.world.loop_origin,'human-2');self.assertEqual(self.world.state['avatar']['col'],7)
   finally:bridge.shutdown.set();bridge.request.set();thread.join(2);bridge.runtime.close()
 def test_text_only_reply_waits_instead_of_ticking_repeatedly(self):
  bridge=self.b;bridge.request=threading.Event();bridge.shutdown=threading.Event();bridge.state={};bridge.turn_start=None
  bridge.runtime=RuntimeStore(self.root/'memory.db');bridge.conversation=GridConversation(self.root/'conversation.json',bridge.runtime);bridge.update=lambda **kw:bridge.state.update(kw)
  calls=[]
  class TextOnlyModel:
   context=131072
   def __init__(self,*args):pass
   def connect(self):return {}
   def appraisal(self,messages):return '{"signals":[]}'
   def stream(self,*args):
    calls.append(1);yield dict(kind='response',text='I am still waiting.',calls=[],finish='stop')
  self.message();bridge.pending['source_id']=bridge.runtime.accept_user('Hello','human-1');args=SimpleNamespace(lm_url='http://unused',model='test-fixture',ctx=131072,temperature=.1)
  with patch('grid_worker.LMStudio',TextOnlyModel):
   thread=threading.Thread(target=run,args=(bridge,args),daemon=True);thread.start()
   try:
    deadline=time.monotonic()+3
    while time.monotonic()<deadline and (not calls or self.world.running or bridge.active_kind is not None):time.sleep(.01)
    time.sleep(.5)
    self.assertEqual(len(calls),1);self.assertFalse(self.world.running);self.assertEqual(self.world.pause_reason,'no_action');self.assertEqual(self.world.receipts,[])
   finally:bridge.shutdown.set();bridge.request.set();thread.join(2);bridge.runtime.close()
