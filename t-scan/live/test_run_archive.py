import copy,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from runtime_store import RuntimeStore
from grid_world import GridWorld,GridDispatch
from grid_conversation import GridConversation,SYSTEM
from run_archive import RunArchive
from lmstudio_client import LMStudio
from world_test_support import publish

class RunArchiveTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.runtime=RuntimeStore(self.root/'memory.db');self.world=GridWorld(self.root/'world.json');self.conversation=GridConversation(self.root/'conversation.json',self.runtime)
  self.runtime.accept_user('Please visit blue','human');self.conversation.user('Please visit blue');self.conversation.messages.append(dict(role='user',content=self.conversation.context(GridDispatch(self.world))))
  publish(self.world);receipt=self.world.nominate('move_east',{},'human',self.world.observe()['observation_id'],'call');self.world.acknowledge('test',receipt['action_id'],self.world.state['session_id']);receipt=self.world.wait(receipt['action_id'])
  self.conversation.messages.extend([dict(role='assistant',content='Heading east',tool_calls=[dict(id='call',type='function',function=dict(name='move_east',arguments='{}'))]),dict(role='tool',tool_call_id='call',content=json.dumps(receipt))]);self.conversation.save();self.runtime.write_notepad('Goal: blue',0,'note')
  self.archive=RunArchive(self.root,self.conversation,self.runtime,self.world,dict(model='fixture',temperature=1))
 def tearDown(self):self.runtime.close();self.tmp.cleanup()
 def test_archive_contains_chat_world_receipts_notes_and_exact_payload(self):
  original=copy.deepcopy(self.conversation.messages);before=copy.deepcopy(self.world.state);note=self.runtime.notepad();payload=dict(messages=[dict(role='user',content='actual request')],tool_choice='auto')
  self.archive.request('/v1/chat/completions',payload,'human');result=self.archive.new_chat(self.conversation,self.runtime,self.world,'rotate')
  folder=Path(result['archive_path']);self.assertEqual(json.loads((folder/'conversation.json').read_text())['messages'],original)
  self.assertEqual(json.loads((folder/'final-state.json').read_text())['self'],before['avatar']);self.assertEqual(json.loads((folder/'final-notepad.json').read_text()),note)
  self.assertEqual(json.loads((folder/'inference-requests.jsonl').read_text())['payload'],payload)
  self.assertEqual(len((folder/'state-snapshots.jsonl').read_text().splitlines()),2);self.assertIn('Heading east',(folder/'chat.md').read_text());self.assertIn('move_east',(folder/'tool-receipts.jsonl').read_text());self.assertTrue((folder/'controller-events.jsonl').exists())
  self.assertEqual(self.world.state['avatar'],dict(id='steve',col=5,row=5,facing='north'));self.assertNotEqual(self.world.state['session_id'],before['session_id']);self.assertEqual(self.runtime.notepad()['content'],'');self.assertEqual(self.conversation.messages,[dict(role='system',content=SYSTEM)]);self.assertEqual(self.runtime.history(),[]);self.assertFalse(self.world.running)
  self.assertEqual(json.loads((self.archive.folder/'start-notepad.json').read_text())['content'],'');self.assertEqual(json.loads((self.archive.folder/'start-state.json').read_text())['self'],self.world.state['avatar'])
 def test_archive_failure_leaves_chat_and_working_history_untouched(self):
  original=copy.deepcopy(self.conversation.messages);history=self.runtime.history()
  with patch.object(self.archive,'finish',side_effect=OSError('disk unavailable')):
   with self.assertRaises(OSError):self.archive.new_chat(self.conversation,self.runtime,self.world,'rotate')
  self.assertEqual(self.conversation.messages,original);self.assertEqual(self.runtime.history(),history)
 def test_repeated_http_request_key_cannot_clear_a_later_message(self):
  first=self.archive.new_chat(self.conversation,self.runtime,self.world,'rotate');self.conversation.user('Next run begins')
  second=self.archive.new_chat(self.conversation,self.runtime,self.world,'rotate')
  self.assertEqual(first,second);self.assertEqual(self.conversation.messages[-1]['content'],'Next run begins')
 def test_restart_resumes_capture_folder_and_next_runs_are_distinct(self):
  first=self.archive.current['id'];again=RunArchive(self.root,self.conversation,self.runtime,self.world,{})
  self.assertEqual(again.current['id'],first)
  self.archive.new_chat(self.conversation,self.runtime,self.world,'one');second=self.archive.current['id'];self.assertNotEqual(first,second)
  self.archive.new_chat(self.conversation,self.runtime,self.world,'two');self.assertNotEqual(second,self.archive.current['id'])
  self.assertEqual(len(list((self.root/'runs').glob('*/manifest.json'))),2)
 def test_changed_inference_conditions_are_recorded_without_rewriting_start_config(self):
  original=json.loads((self.archive.folder/'config.json').read_text())
  again=RunArchive(self.root,self.conversation,self.runtime,self.world,dict(model='fixture',temperature=.5))
  change=json.loads((again.folder/'condition-changes.jsonl').read_text())
  self.assertEqual(change['previous'],original);self.assertEqual(change['current']['config']['temperature'],.5)
  self.assertEqual(json.loads((again.folder/'config.json').read_text()),original)
 def test_provider_hook_records_actual_request_without_mutating_it(self):
  client=LMStudio('http://fixture','fixture');client.on_request=lambda path,payload:self.archive.request(path,payload,'human')
  payload=client.payload([dict(role='user',content='test')],1.)
  with patch('urllib.request.urlopen') as opened:client.request('/v1/chat/completions',payload)
  recorded=json.loads((self.archive.folder/'inference-requests.jsonl').read_text())
  self.assertEqual(recorded['payload'],json.loads(opened.call_args.args[0].data))
 def test_operator_notes_persist_restart_and_archive_next_to_chat(self):
  page=self.archive.save_operator_notes(self.archive.current['id'],0,'My observation\nHe moved north instead of south.')
  again=RunArchive(self.root,self.conversation,self.runtime,self.world,{})
  self.assertEqual(again.operator_notes(),page)
  result=self.archive.new_chat(self.conversation,self.runtime,self.world,'with-notes');folder=Path(result['archive_path'])
  self.assertEqual((folder/'operator-notes.md').read_text(),page['content']);self.assertEqual(json.loads((folder/'operator-notes.json').read_text()),page)
  self.assertEqual(self.archive.operator_notes()['content'],'');self.assertNotEqual(self.archive.operator_notes()['run_id'],page['run_id'])
 def test_late_or_stale_notes_cannot_overwrite_new_run_or_other_edits(self):
  from run_archive import OperatorNotesConflict
  old=self.archive.operator_notes();self.archive.save_operator_notes(old['run_id'],0,'First')
  with self.assertRaises(OperatorNotesConflict):self.archive.save_operator_notes(old['run_id'],0,'Stale')
  self.archive.new_chat(self.conversation,self.runtime,self.world,'rotate-notes')
  with self.assertRaises(OperatorNotesConflict):self.archive.save_operator_notes(old['run_id'],1,'Late response')
  self.assertEqual(self.archive.operator_notes()['content'],'')
 def test_operator_notes_never_enter_model_context_or_agent_notepad(self):
  from grid_worker import appraisal_messages
  from grid_context import inference_messages
  secret='HUMAN_ONLY_NOTE_X';self.archive.save_operator_notes(self.archive.current['id'],0,secret)
  context=self.conversation.context(GridDispatch(self.world));messages=inference_messages(self.conversation.messages+[dict(role='user',content=context)])
  self.assertNotIn(secret,json.dumps(messages));self.assertNotIn(secret,json.dumps(appraisal_messages(self.runtime,dict(prompt='Go ahead'))));self.assertNotIn(secret,self.runtime.notepad()['content'])
 def test_invalid_notes_and_failed_archive_preserve_saved_notes(self):
  for revision,text in ((True,'x'),(-1,'x'),(0,'x'*65537),(0,None)):
   with self.assertRaises(ValueError):self.archive.save_operator_notes(self.archive.current['id'],revision,text)
  page=self.archive.save_operator_notes(self.archive.current['id'],0,'Keep my notes')
  with patch.object(self.archive,'finish',side_effect=OSError('disk failure')):
   with self.assertRaises(OSError):self.archive.new_chat(self.conversation,self.runtime,self.world,'fail-notes')
  self.assertEqual(self.archive.operator_notes(),page)

if __name__=='__main__':unittest.main()
