import copy,json,tempfile,unittest,uuid
from pathlib import Path
import character_rules as rules
from grid_world import GridWorld,GridDispatch
from movement_tools import registry
from world_test_support import publish,poll
from grid_context import coordinate_world

class CharacterTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.w=GridWorld(Path(self.tmp.name)/'world.json');publish(self.w)
 def tearDown(self):self.tmp.cleanup()
 def request(self,body='unicore',equipment=None):
  return dict(request_id=uuid.uuid4().hex,character_id='steve',expected_revision=self.w.state['character']['revision'],catalog_version=rules.CATALOG['version'],body_id=body,equipment=equipment if equipment is not None else [dict(socket_id='arm_R',module_id='warrior_blade'),dict(socket_id='arm_L',module_id='warrior_shield')])
 def attack(self,name='shield_bash',args=None):
  poll(self.w);return self.w.nominate(name,args or {'target_id':'dummy'},uuid.uuid4().hex,self.w.observe()['observation_id'],'call')
 def equip(self):return self.w.apply_character(self.request())
 def test_body_mounts_and_conflicts(self):
  self.assertEqual([len(rules.BODIES[b]['sockets']) for b in ['skimmer','bulwark','wisp']],[3,7,4])
  with self.assertRaisesRegex(ValueError,'no socket'):rules.validate('wisp',self.request()['equipment'])
  with self.assertRaisesRegex(ValueError,'conflict'):rules.validate('unicore',[dict(socket_id='arm_R',module_id='mage2h_greatstaff'),dict(socket_id='arm_L',module_id='warrior_shield')])
  with self.assertRaisesRegex(ValueError,'incompatible'):rules.validate('skimmer',[dict(socket_id='ventral_tool',module_id='mage2h_greatstaff')])
  with self.assertRaisesRegex(ValueError,'two-mount'):rules.validate('unicore',[dict(socket_id='arm_L',module_id='mage2h_greatstaff')])
 def test_three_mount_duelist_and_mantle_configurations(self):
  self.assertEqual({s['id'] for s in rules.BODIES['duelist']['sockets']},{'hand_L','hand_R','horn'})
  self.assertEqual({s['id'] for s in rules.BODIES['mantle']['sockets']},{'shoulder_L','shoulder_R','horn'})
  equipment,caps=rules.validate('duelist',[dict(socket_id='hand_R',module_id='warrior_blade'),dict(socket_id='hand_L',module_id='warrior_shield')])
  self.assertEqual(caps,['shield_bash','slash']);rules.validate('duelist',[dict(socket_id='hand_R',module_id='mage2h_greatstaff')])
  rules.validate('mantle',[dict(socket_id='shoulder_L',module_id='cleric_orb'),dict(socket_id='shoulder_R',module_id='mage_tome'),dict(socket_id='horn',module_id='mage2h_lens')])
  with self.assertRaisesRegex(ValueError,'incompatible'):rules.validate('mantle',[dict(socket_id='shoulder_L',module_id='warrior_blade')])
  with self.assertRaisesRegex(ValueError,'no socket'):rules.validate('mantle',equipment)
  request=self.request(body='duelist',equipment=equipment);request.pop('request_id');preview=self.w.preview_character(request)
  self.assertEqual([a['effective'] for a in preview['character']['sheet']['attributes']],[3,1,1,1,3]);self.assertEqual(self.w.state['character']['body_id'],'hover')
 def test_apply_atomic_snapshot_idempotency_and_revision(self):
  req=self.request();first=self.w.apply_character(req);self.assertEqual(first,self.w.apply_character(req));self.assertEqual(self.w.state['game_tick'],0)
  new=GridWorld(self.w.path);self.assertEqual(new.state['character']['capabilities'],['shield_bash','slash']);self.assertEqual(first,new.apply_character(req))
  changed=copy.deepcopy(req);changed['body_id']='wisp'
  with self.assertRaisesRegex(ValueError,'different'):new.apply_character(changed)
  changed['request_id']=uuid.uuid4().hex
  with self.assertRaisesRegex(ValueError,'Stale'):new.apply_character(changed)
 def test_no_untrusted_fields_or_busy_mutation(self):
  req=self.request();req['damage']=9000
  with self.assertRaises(ValueError):self.w.apply_character(req)
  self.w.running=True
  with self.assertRaisesRegex(ValueError,'Stop'):self.equip()
  self.assertEqual(self.w.state['character']['revision'],0)
 def test_bash_commits_damage_position_tick_and_receipt_together(self):
  self.equip();a=self.w.state['avatar'];self.w.state['training_targets']=[dict(id='dummy',col=a['col'],row=a['row']+3,hp=10,max_hp=10)]
  old=a.copy();r=self.attack();self.assertEqual(r['outcome'],'target_hit');self.assertEqual(r['damage'],1);self.assertEqual(r['target_hp_after'],9);self.assertEqual(r['position_after'],[old['col'],old['row']+2]);self.assertEqual(self.w.state['game_tick'],1)
  disk=json.loads(self.w.path.read_text());self.assertEqual(disk['training_targets'][0]['hp'],9);self.assertEqual(disk['avatar']['row'],old['row']+2);self.assertEqual(disk['last_committed_action']['action_id'],r['action_id'])
  self.w.acknowledge('test',r['action_id'],self.w.state['session_id']);r=self.attack('slash');self.assertEqual(r['target_hp_after'],6);self.assertEqual(r['damage'],3)
 def test_clear_lane_range_and_unequipped_rejections_are_free(self):
  self.equip();a=self.w.state['avatar'];self.w.state['training_targets']=[dict(id='dummy',col=a['col']+1,row=a['row']+1,hp=10,max_hp=10)]
  self.assertEqual(self.attack()['outcome'],'rejected_range');self.assertEqual(self.w.state['game_tick'],0)
  self.w.state['training_targets'][0].update(col=a['col'],row=a['row']+3)
  self.w.state['world_definition']['schema']='meadow-world-v2';self.w.state['world_definition']['obstacles']=[dict(id='block',prototype='wall',col=a['col'],row=a['row']+1,yaw=0)];self.w.state['world_definition']['catalog']=[dict(prototype='wall',name='Wall',role='wall',blocks=True)]
  # Use a separate authoritative snapshot in the test to isolate lane collision from manifest admission.
  original=self.w.observe
  self.w.observe=lambda:dict(original(),visible_obstacles=[dict(id='block',col=a['col'],row=a['row']+1)])
  self.w._digest=(self.w.state['world_definition'],'synthetic-test-hash')
  self.assertEqual(self.attack()['outcome'],'rejected_lane');self.assertEqual(self.w.state['game_tick'],0)
 def test_tools_context_removal_and_new_chat_preserve_equipment(self):
  self.equip();caps=self.w.state['character']['capabilities'];names=lambda r:{t['function']['name'] for t in r.TOOLS}
  self.assertIn('slash',names(registry(phase='executor',capabilities=caps)));self.assertNotIn('slash',names(registry(phase='planner',capabilities=caps)))
  self.assertIn('CURRENT CHARACTER',coordinate_world(self.w.observe()))
  self.assertIn('character',GridDispatch(self.w).snapshot()['observation']['world'])
  self.w.reset();self.assertEqual(self.w.state['character']['capabilities'],caps)
  self.w.apply_character(self.request(equipment=[]));self.assertEqual(self.attack()['outcome'],'rejected_unequipped');self.assertNotIn('slash',names(registry(phase='executor',capabilities=[])))

if __name__=='__main__':unittest.main()
