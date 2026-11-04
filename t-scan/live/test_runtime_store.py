import json,tempfile,unittest
from pathlib import Path
from runtime_store import RuntimeStore,BASE
class RuntimeTests(unittest.TestCase):
 def test_clear_working_memory_hides_old_chat_but_preserves_notes_and_audit(self):
  with tempfile.TemporaryDirectory() as d:
   s=RuntimeStore(Path(d)/'s.db');s.accept_user('Remember: teal is my favorite.', 'old');s.event('assistant','Old reply','old');notes=s.notes();s.clear_working_memory()
   self.assertEqual(s.history(),[]);self.assertEqual(s.snapshot()['recent'],[]);self.assertEqual(s.notes(),notes);self.assertEqual(s.db.execute("SELECT COUNT(*) FROM events WHERE kind='user'").fetchone()[0],1)
   s.accept_user('Fresh chat','fresh');self.assertEqual([m['content'] for m in s.history()],['Fresh chat']);s.close()
 def test_restart_provenance_decay_and_idempotency(self):
  with tempfile.TemporaryDirectory() as d:
   now=[1000.];p=Path(d)/'s.db';s=RuntimeStore(p,lambda:now[0]);eid=s.accept_user('Remember: I prefer teal.', 'a');s.event('assistant','Noted.','a',eid)
   payload=json.dumps(dict(signals=[dict(name='joy',delta=2)]));s.apply_appraisal(payload,eid,'a');first=s.snapshot()['affect']['joy'];s.apply_appraisal(payload,eid,'a');self.assertEqual(s.snapshot()['affect']['joy'],first);s.close()
   s=RuntimeStore(p,lambda:now[0]);self.assertEqual(len(s.history()),2);self.assertEqual(s.notes()[0]['source_event_id'],eid);self.assertEqual(s.snapshot()['affect']['joy'],first)
   now[0]+=3600;self.assertLess(s.snapshot()['affect']['joy'],first);s.close()
 def test_invalid_and_recall_dont_change_state(self):
  with tempfile.TemporaryDirectory() as d:
   s=RuntimeStore(Path(d)/'s.db',lambda:0);eid=s.accept_user('hello','a');before=s.snapshot()['affect']
   for value in ({'signals':[{'name':'joy','delta':99}]},{'signals':[{'name':'permissions','delta':1}]}):
    with self.assertRaises(ValueError):s.apply_appraisal(json.dumps(value),eid,'x')
   self.assertEqual(s.snapshot()['affect'],before);s.history();s.notes();self.assertEqual(s.snapshot()['affect'],before);s.close()
class SeedTests(unittest.TestCase):
 def test_import_is_idempotent_and_separate_from_conversation_and_affect(self):
  with tempfile.TemporaryDirectory() as d:
   s=RuntimeStore(Path(d)/'s.db',lambda:0);before=s.snapshot()['affect'];pack={'records':[{'key':'a','kind':'interaction_preference','status':'historical_user_statement','summary':'Brad enjoys debate and independent responses.','source':{'path':'archive','start_line':12,'excerpt':'I love debate'}}]}
   s.import_seed(pack);s.import_seed(pack)
   self.assertEqual(len(s.seed_memories()),1);self.assertEqual(s.history(),[]);self.assertEqual(s.snapshot()['affect'],before)
   record=s.seed_memories('debate')[0];self.assertTrue(record['source_event_id']);self.assertEqual(record['status'],'historical_user_statement');s.close()
 def test_invalid_batch_does_not_partially_import(self):
  with tempfile.TemporaryDirectory() as d:
   s=RuntimeStore(Path(d)/'s.db');good={'key':'a','kind':'preference','status':'historical_user_statement','summary':'A preference','source':{'path':'archive'}}
   with self.assertRaises(ValueError):s.import_seed({'records':[good,dict(good,key='b',status='verified_superpower')]})
   self.assertEqual(s.seed_memories(),[]);s.close()
class SeparationTests(unittest.TestCase):
 def test_plans_are_excluded_from_conversation_and_graphs_are_disjoint(self):
  with tempfile.TemporaryDirectory() as d:
   path=Path(d)/'s.db';s=RuntimeStore(path)
   records=[dict(key='pref',kind='interest',status='historical_user_statement',summary='Brad enjoys music',source={'path':'archive'}),dict(key='plan',kind='historical_design',status='historical_user_statement',summary='Proposed a VR hand',source={'path':'archive'}),dict(key='report',kind='historical_project',status='historical_user_statement',summary='Reported a finished engine',source={'path':'archive'})]
   s.import_seed(dict(records=records));self.assertEqual(len(s.seed_memories(collection='conversation')),1)
   self.assertNotIn('Proposed a VR hand',s.context('hello'));self.assertIn('Proposed a VR hand',s.development_context('build a VR hand'))
   self.assertEqual(s.development_context('hello'), '')
   g=s.graphs();a={n['id'] for n in g['conversation']['nodes']};b={n['id'] for n in g['development']['nodes']};self.assertFalse(a&b)
   for graph in g.values():
    ids={n['id'] for n in graph['nodes']}
    for e in graph['edges']:self.assertIn(e['source'],ids);self.assertIn(e['target'],ids)
   self.assertEqual(s.seed_memories('engine',collection='development')[0]['stage'],'unverified_implementation_report')
   s.close();s=RuntimeStore(path);self.assertEqual(len(s.seed_memories(collection='development')),2);s.close()
if __name__=='__main__':unittest.main()
