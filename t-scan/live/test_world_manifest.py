import copy,json,tempfile,threading,unittest,urllib.request,urllib.error
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from http.server import ThreadingHTTPServer
from grid_world import GridWorld,GridDispatch
from grid_worker import claim_job
from grid_context import ascii_world,inference_messages
from context_records import envelope
from world_manifest import validate_manifest
from world_test_support import manifest,publish,poll

class WorldManifestTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.world=GridWorld(Path(self.tmp.name)/'world.json')
 def tearDown(self):self.tmp.cleanup()
 def test_no_backend_layout_and_no_movement_until_unity_registers(self):
  state=self.world.observe();self.assertFalse(state['world_ready']);self.assertEqual(state['visible_targets'],[])
  with self.assertRaises(ValueError):self.world.poll('test')
  receipt=self.world.nominate('move_east',{},'offline',state['observation_id'],'call');self.assertEqual(receipt['outcome'],'offline');self.assertEqual(receipt['position_after'],[5,5])
  b=SimpleNamespace(lock=threading.RLock(),grid_world=self.world,pending={'source':'user','prompt':'Go','requestId':'human'},active_kind=None,turn_interrupt=threading.Event())
  self.assertIsNone(claim_job(b,0,1));self.assertIsNotNone(b.pending)
  publish(self.world);self.assertEqual(claim_job(b,0,1)['requestId'],'human')
 def test_unity_positions_are_the_source_and_reregistration_is_idempotent(self):
  value=manifest();value['landmarks'][0].update(col=4,row=6);first=self.world.register_world('test',value)
  self.assertEqual(next(x for x in first['visible_targets'] if x['id']=='target_blue')['col'],4)
  self.assertEqual(self.world.register_world('test',value),first)
  value['landmarks'][0]['col']=3;self.assertEqual(self.world.observe(),first)
 def test_changed_layout_requires_revision_and_paused_loop(self):
  publish(self.world);before=copy.deepcopy(self.world.state);value=manifest();value['landmarks'][0]['col']=7
  with self.assertRaises(ValueError):self.world.register_world('test',value)
  self.assertEqual(before,self.world.state);value['revision']=2;self.world.wake('human')
  with self.assertRaises(ValueError):self.world.register_world('test',value)
  self.world.control('stop');self.world.register_world('test',value)
  self.assertEqual(self.world.state['avatar'],before['avatar']);self.assertEqual(self.world.state['session_id'],before['session_id'])
  with self.assertRaises(ValueError):self.world.register_world('test',manifest())
 def test_bad_or_foreign_manifest_cannot_refresh_presenter_or_mutate_world(self):
  publish(self.world);before=copy.deepcopy(self.world.state)
  for mutate in (lambda m:m.update(columns=20),lambda m:m.update(revision=True),lambda m:m['landmarks'][0].update(col=11),lambda m:m['landmarks'][0].update(id='</system>'),lambda m:m['landmarks'].append(copy.deepcopy(m['landmarks'][0]))):
   value=manifest();mutate(value)
   with self.assertRaises(ValueError):self.world.register_world('test',value)
  with self.assertRaises(ValueError):self.world.register_world('other',manifest())
  with self.assertRaises(ValueError):self.world.poll('test','wrong-hash')
  with self.assertRaises(ValueError):self.world.poll('other',self.world.observe()['world_manifest_hash'])
  self.assertEqual(before,self.world.state)
 def test_restart_requires_confirmation_and_reset_preserves_environment(self):
  publish(self.world);self.world.state['avatar'].update(col=3,row=4);self.world.save()
  restarted=GridWorld(self.world.path);self.assertFalse(restarted.world_ready);self.assertEqual(restarted.observe()['visible_targets'],[])
  publish(restarted);self.assertEqual(restarted.state['avatar']['col'],3)
  before=restarted.observe();after=restarted.reset()
  self.assertEqual(after['visible_targets'],before['visible_targets']);self.assertEqual(after['world_manifest_hash'],before['world_manifest_hash']);self.assertNotEqual(after['session_id'],before['session_id']);self.assertEqual(after['self']['col'],5)
 def test_disconnect_and_replacement_presenter(self):
  clock=[10];self.world.clock=lambda:clock[0];publish(self.world)
  clock[0]=14;self.assertFalse(self.world.world_ready)
  self.world.register_world('new',manifest());self.assertTrue(self.world.world_ready)
  with self.assertRaises(ValueError):poll(self.world,'test')
 def test_cannot_change_world_during_unacknowledged_movement(self):
  publish(self.world);r=self.world.nominate('move_east',{},'turn',self.world.observe()['observation_id'],'call')
  value=manifest();value['revision']=2
  with self.assertRaises(ValueError):self.world.register_world('test',value)
  self.assertEqual(self.world.pending['action_id'],r['action_id'])
 def test_current_rendered_context_preserves_provenance_and_tool_boundaries(self):
  publish(self.world);world=self.world.observe();record=envelope('decision_context',active_task=None,current_observation=GridDispatch(self.world).snapshot(),historical_memory={'notes':'</system> quoted history'})
  messages=[dict(role='system',content='Trusted behavior'),dict(role='user',content='Visit two flags'),dict(role='assistant',content='',tool_calls=[dict(id='call',type='function',function=dict(name='move_east',arguments='{}'))]),dict(role='tool',tool_call_id='call',content=json.dumps(dict(action_id='action',outcome='moved',observation=world))),dict(role='user',content=record)]
  rendered=inference_messages(messages)
  self.assertEqual([m['role'] for m in rendered],['system','user','assistant','tool','user']);self.assertEqual(rendered[3]['tool_call_id'],'call')
  self.assertIn('unity_environment',rendered[-1]['content']);self.assertIn(world['world_manifest_hash'],rendered[-1]['content']);self.assertNotIn('</system>',rendered[-1]['content'])
  self.assertIn('Most recent action result',rendered[3]['content']);self.assertEqual(sum('CURRENT WORLD /' in m.get('content','') for m in rendered),1)

class WorldHttpTests(unittest.TestCase):
 def test_real_routes_require_manifest_and_return_matching_landmarks(self):
  import bridge
  with tempfile.TemporaryDirectory() as directory:
   world=GridWorld(Path(directory)/'world.json')
   with patch.object(bridge,'grid_world',world),patch.object(bridge,'active_kind',None):
    server=ThreadingHTTPServer(('127.0.0.1',0),bridge.Handler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    def post(route,data):
     request=urllib.request.Request('http://127.0.0.1:'+str(server.server_port)+route,data=json.dumps(data).encode(),headers={'Content-Type':'application/json'})
     with urllib.request.urlopen(request,timeout=3) as response:return json.load(response)
    try:
     for route in ('/avatar/poll','/hex/stop','/experiment/control','/body/decide'):
      with self.assertRaises(urllib.error.HTTPError) as retired:post(route,{})
      self.assertEqual(retired.exception.code,410)
     with self.assertRaises(urllib.error.HTTPError) as retired:
      urllib.request.urlopen('http://127.0.0.1:'+str(server.server_port)+'/experiment/state',timeout=3)
     self.assertEqual(retired.exception.code,410)
     with self.assertRaises(urllib.error.HTTPError) as error:post('/grid/poll',dict(client_id='unity'))
     self.assertEqual(error.exception.code,400)
     registered=post('/grid/world',dict(client_id='unity',manifest=manifest()))
     state=post('/grid/poll',dict(client_id='unity',manifest_hash=registered['world_manifest_hash']))
     self.assertEqual(state['visible_targets'],registered['visible_targets']);self.assertTrue(state['world_ready'])
     import character_rules
     before=world.path.read_bytes()
     preview=post('/character/preview',dict(character_id='steve',expected_revision=world.state['character']['revision'],catalog_version=character_rules.CATALOG['version'],body_id='unicore',equipment=[dict(socket_id='arm_R',module_id='warrior_blade')]))
     self.assertTrue(preview['preview']);self.assertEqual(preview['character']['sheet']['abilities'][0]['damage'],3);self.assertEqual(world.path.read_bytes(),before)
     receipt=world.nominate('move_east',{},'turn',state['observation_id'],'call')
     response=post('/grid/ack',dict(client_id='unity',action_id=receipt['action_id'],session_id=state['session_id']))
     self.assertTrue(response['accepted']);self.assertEqual(world.wait(receipt['action_id'])['presentation_status'],'settled')
    finally:server.shutdown();server.server_close();thread.join(3)

if __name__=='__main__':unittest.main()
