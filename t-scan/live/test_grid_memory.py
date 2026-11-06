import copy,json,tempfile,unittest
from pathlib import Path
from runtime_store import RuntimeStore
from grid_context import memory_context,inference_messages
from grid_conversation import GridConversation
from context_records import envelope
from lmstudio_client import chat_events,LMStudio
from movement_tools import registry

def unpack(text):return json.loads(text.split('\n',2)[2].rsplit('\n',1)[0])

class GridMemoryTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.store=RuntimeStore(Path(self.tmp.name)/'memory.db')
  records=[dict(key='identity',kind='self_model',status='curated_self_model',summary='Steve is a companion.',source={'path':'curation'}),dict(key='plan',kind='current_direction',status='current_user_direction',summary='Build VR fingers and limbs.',source={'path':'old-plan'}),dict(key='music',kind='interest',status='historical_user_statement',summary='Brad enjoys Thrice music.',source={'path':'chat'}),dict(key='substring',kind='interest',status='historical_user_statement',summary='Brad preferred another movie.',source={'path':'chat'})]
  self.store.import_seed(dict(records=records))
 def tearDown(self):self.store.close();self.tmp.cleanup()
 def test_no_filler_but_identity_and_notes_preserved(self):
  self.store.accept_user('Remember: I prefer teal.','note')
  value=memory_context(self.store,[dict(role='user',content='Move to the red flag please')])
  self.assertEqual([r['key'] for r in value['self_model']],['identity']);self.assertEqual(value['recalled_conversation'],[])
  self.assertEqual(value['notes'][0]['content'],'I prefer teal.')
  self.assertNotIn('VR fingers',json.dumps(value));self.assertEqual(len(self.store.seed_memories(collection='development')),1)
 def test_relevant_conversational_recall_uses_human_not_harness_text(self):
  messages=[dict(role='user',content='Tell me about Thrice'),dict(role='user',content=envelope('decision_tick',irrelevant='movie'))]
  self.assertEqual([r['key'] for r in memory_context(self.store,messages)['recalled_conversation']],['music'])
  self.assertEqual(self.store.seed_memories('',collection='conversation',relevant_only=True),[])
 def test_projection_keeps_native_boundaries_world_and_durable_memory(self):
  old=envelope('decision_context',current_observation={'measured':'old'},historical_memory={'development':['VR fingers']})
  latest=envelope('decision_context',current_observation={'measured':'now'},historical_memory={'self_model':['Steve']})
  messages=[dict(role='system',content='rules'),dict(role='user',content=old),dict(role='assistant',content='Thinking',tool_calls=[dict(id='a',type='function',function=dict(name='move_north',arguments='{}'))]),dict(role='tool',tool_call_id='a',content='actual receipt'),dict(role='user',content=latest)]
  original=copy.deepcopy(messages);projected=inference_messages(messages)
  self.assertEqual(messages,original);self.assertEqual(projected[2:],messages[2:]);self.assertEqual(unpack(projected[1]['content'])['kind'],'historical_observation')
  self.assertNotIn('VR fingers',json.dumps(projected));self.assertIn('VR fingers',json.dumps(messages))
 def test_production_chat_path_projects_only_outgoing_copy(self):
  historical=envelope('decision_context',historical_memory={'development':['VR fingers']})
  saved=[];payloads=[]
  class Client:
   def stream(self,messages,tools,temperature,should_stop):
    payloads.append(LMStudio('http://unused','fixture').payload(messages,temperature,tools))
    yield dict(kind='response',text='Thinking aloud.',calls=[],finish='stop')
  list(chat_events(Client(),[dict(role='user',content=historical)],None,'test',registry(),.1,lambda:envelope('decision_context',historical_memory={'self_model':['Steve']}),lambda m:saved.append(copy.deepcopy(m)),lambda:False))
  self.assertNotIn('VR fingers',json.dumps(payloads));self.assertIn('VR fingers',json.dumps(saved))
  self.assertEqual(payloads[0]['tool_choice'],'auto')
 def test_meadow_context_uses_snapshot_without_retired_bench_projection(self):
  conversation=GridConversation(Path(self.tmp.name)/'conversation.json',self.store)
  conversation.user('Go to the flag')
  class Observation:
   def snapshot(self):return dict(state_source='deterministic_grid',observation={'world':{'self':{'col':2,'row':5}}})
  value=unpack(conversation.context(Observation()))
  self.assertEqual(value['current_observation'],Observation().snapshot());self.assertIsNone(value['active_task'])
  self.assertNotIn('VR fingers',json.dumps(value));self.assertNotIn('simulated_affect',value)

if __name__=='__main__':unittest.main()
