import unittest,tempfile,json,copy
from pathlib import Path
from grid_conversation import GridConversation,SYSTEM,VERSION
from runtime_store import RuntimeStore
from lmstudio_client import chat_events
from movement_tools import registry
class GridContractTests(unittest.TestCase):
 def test_migration_preserves_history_and_task_is_paused(self):
  with tempfile.TemporaryDirectory() as t:
   path=Path(t)/'conversation.json';old=[dict(role='system',content='old interface'),dict(role='user',content='Keep this conversation.'),dict(role='assistant',content='Preserved.')]
   path.write_text(json.dumps(dict(version='shared-chat-v4-targets',messages=old,task=dict(status='active',id='old'))))
   store=RuntimeStore(Path(t)/'memory.db')
   try:
    c=GridConversation(path,store)
    self.assertEqual(c.messages[0]['content'],SYSTEM);self.assertEqual(c.messages[1:-1],old[1:]);self.assertNotEqual(c.task['status'],'active');self.assertEqual(json.loads(path.read_text())['version'],VERSION)
   finally:store.db.close()
 def exercise(self,calls):
  class Client:
   count=0
   def stream(self,*args):
    self.count+=1;yield dict(kind='response',text='',calls=copy.deepcopy(calls),finish='tool_calls')
  class Dispatch:
   executed=0;rejected=0
   def submit(self,*args,**kwargs):self.executed+=1;return 'key'
   def wait(self,key):return dict(outcome='moved',presentation_status='settled')
   def reject(self,*args):self.rejected+=1;return dict(outcome='rejected_conflict')
  c=Client();d=Dispatch();events=list(chat_events(c,[],d,'turn',registry(),.1,lambda:'CURRENT STATE',lambda m:None,lambda:False));return c,d,events
 def test_scheduled_turn_bounds_three_separate_zero_argument_decisions(self):
  c,d,e=self.exercise([dict(id='a',type='function',function=dict(name='move_east',arguments='{}'))]);self.assertEqual(c.count,3);self.assertEqual(d.executed,3);self.assertEqual(e[-1]['reason'],'tool_call_limit')
 def test_conflicting_batch_executes_nothing(self):
  calls=[dict(id=n,type='function',function=dict(name=n,arguments='{}')) for n in ('move_east','move_north')];c,d,e=self.exercise(calls);self.assertEqual(d.executed,0);self.assertEqual(d.rejected,2)
 def test_coordinate_arguments_are_rejected(self):
  c,d,e=self.exercise([dict(id='a',type='function',function=dict(name='move_east',arguments='{"col":8}'))]);self.assertEqual(d.executed,0);self.assertEqual(d.rejected,3)
 def test_clock_tick_does_not_assign_a_goal(self):
  with tempfile.TemporaryDirectory() as t:
   store=RuntimeStore(Path(t)/'memory.db')
   try:
    c=GridConversation(Path(t)/'conversation.json',store);c.tick();self.assertIsNone(c.task)
    self.assertIn('conversation_continuation',c.messages[-1]['content']);self.assertNotIn('target_blue',c.messages[-1]['content']);self.assertNotIn('Navigate',c.messages[-1]['content'])
   finally:store.db.close()
