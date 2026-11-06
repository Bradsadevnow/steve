"""Character ownership, authoritative preview, scaling receipts and legacy migration."""
import copy,json,tempfile,unittest,uuid
from pathlib import Path
from unittest.mock import patch
import character_rules as rules
from grid_world import GridWorld,GridDispatch
from world_test_support import publish,poll
from grid_context import compact_receipt

class StatsTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.path=Path(self.tmp.name)/'world.json';self.world=GridWorld(self.path);publish(self.world)
 def tearDown(self):self.tmp.cleanup()
 def request(self,equipment=None,body='unicore'):
  return dict(character_id='steve',expected_revision=self.world.state['character']['revision'],catalog_version=rules.CATALOG['version'],body_id=body,equipment=equipment if equipment is not None else [dict(socket_id='arm_R',module_id='warrior_blade'),dict(socket_id='arm_L',module_id='warrior_shield')])
 def equip(self,equipment=None,body='unicore'):
  return self.world.apply_character(dict(self.request(equipment,body),request_id=uuid.uuid4().hex))['character']
 def test_base_and_relevant_equipment_bonuses(self):
  bare=self.world.observe()['character'];self.assertEqual([a['effective'] for a in bare['sheet']['attributes']],[1]*5)
  equipped=self.equip();attrs={a['id']:a for a in equipped['sheet']['attributes']}
  self.assertEqual([attrs[k]['effective'] for k in ('STR','DEX','INT','WIS','CON')],[3,1,1,1,3])
  self.assertEqual(attrs['STR']['equipment_bonus'],2);self.assertEqual(attrs['CON']['equipment_bonus'],2)
  self.assertEqual(equipped['sheet']['hp'],dict(current=10,maximum=12));self.assertEqual(equipped['sheet']['mp'],dict(current=10,maximum=10))
  self.assertNotIn('stats',equipped);self.assertNotIn('stats',self.world.observe()['character'])
 def test_preview_and_apply_match_without_preview_writes(self):
  before=copy.deepcopy(self.world.state);disk=self.path.read_bytes();preview=self.world.preview_character(self.request())
  self.assertTrue(preview['preview']);self.assertEqual(self.world.state,before);self.assertEqual(self.path.read_bytes(),disk)
  self.assertEqual(preview['character'],self.equip());self.assertEqual(self.world.state['game_tick'],0)
 def test_preview_rejects_injected_stats_and_stale_revisions(self):
  request=self.request();request['stats']={'STR':999}
  with self.assertRaises(ValueError):self.world.preview_character(request)
  request=self.request();request['expected_revision']-=1
  with self.assertRaisesRegex(ValueError,'Stale'):self.world.preview_character(request)
 def test_agent_perception_excludes_private_stats_and_asset_prototypes(self):
  self.world.state['training_targets']=[dict(id='target',prototype='bosses_dummy_unarmed',col=6,row=6,hp=10,max_hp=10)]
  perceived=GridDispatch(self.world).snapshot()['observation']['world']
  self.assertNotIn('stats',perceived['character']);self.assertNotIn('prototype',perceived['training_targets'][0]);self.assertEqual(perceived['training_targets'][0]['id'],'target')
 def test_unequip_removes_bonus_and_preserves_resources_across_apply_reset_restart(self):
  self.equip();character=self.world.state['character'];character['stats']['resources']['hp']['current']=6
  self.world.state['character']=rules.project(character)
  bare=self.equip([]);self.assertEqual(bare['capabilities'],[]);self.assertEqual([a['effective'] for a in bare['sheet']['attributes']],[1]*5)
  self.assertEqual(bare['sheet']['hp']['current'],6);self.world.reset()
  restarted=GridWorld(self.path);self.assertEqual(restarted.observe()['character']['sheet']['hp']['current'],6)
 def test_bounded_formula_rounding_and_no_capability_from_stats(self):
  self.equip();character=copy.deepcopy(self.world.state['character'])
  for base,expected in ((1,1),(3,1),(4,2),(7,3)):
   character['stats']['base']['CON']=base
   self.assertEqual(rules.ability(character,'shield_bash')['damage'],expected)
  character['stats']['base']['STR']=7;self.assertEqual(rules.ability(character,'slash')['damage'],9)
  character['stats']['base']['STR']=100;character.update(equipment=[],capabilities=[])
  self.assertEqual(rules.project(character)['sheet']['abilities'],[])
 def test_multi_mount_modules_contribute_once_and_bonuses_stack_per_instance(self):
  equipment=[dict(socket_id=slot,module_id='warrior_shield') for slot in ('left_upper','right_upper','left_lower')]+[dict(socket_id='right_lower',module_id='warrior_blade')]
  value=self.equip(equipment,'bulwark');abilities={a['id']:a for a in value['sheet']['abilities']}
  self.assertEqual(abilities['shield_bash']['effective_stat'],7);self.assertEqual(abilities['shield_bash']['damage'],2)
  self.assertEqual(value['capabilities'],['shield_bash','slash'])
 def test_scaled_attack_receipt_and_overkill_are_committed(self):
  self.equip();avatar=self.world.state['avatar'];self.world.state['training_targets']=[dict(id='dummy',col=avatar['col'],row=avatar['row']+1,hp=2,max_hp=10)]
  poll(self.world);receipt=self.world.nominate('slash',{'target_id':'dummy'},'turn',self.world.observe()['observation_id'],'native-call')
  self.assertEqual((receipt['damage'],receipt['nominal_damage']),(2,3));self.assertEqual(receipt['scaling_stat'],'STR');self.assertEqual(receipt['effective_stat'],3)
  self.assertEqual(receipt['rules_version'],rules.RULES_VERSION);self.assertEqual(receipt['damage_curve'],dict(numerator=1,denominator=1,minimum=1))
  self.assertEqual(json.loads(self.path.read_text())['last_committed_action'],receipt);self.assertEqual(compact_receipt(receipt)['stats_revision'],receipt['stats_revision'])
 def test_legacy_migration_preserves_run_equipment_and_is_idempotent(self):
  self.equip();legacy=copy.deepcopy(self.world.state);old=legacy['character'];old.pop('stats');old.pop('sheet');old['catalog_version']='steve-equipment-v1'
  self.path.write_text(json.dumps(legacy));migrated=GridWorld(self.path);character=migrated.state['character']
  self.assertEqual(character['equipment'],old['equipment']);self.assertEqual(character['revision'],old['revision']+1)
  for key in ('session_id','avatar','game_tick'):self.assertEqual(migrated.state[key],legacy[key])
  self.assertEqual(len(migrated.state['character_migrations']),1);self.assertEqual(GridWorld(self.path).state['character'],character)
 def test_apply_save_failure_rolls_back_stats_and_equipment(self):
  before=copy.deepcopy(self.world.state)
  with patch.object(self.world,'save',side_effect=OSError('fixture full disk')):
   with self.assertRaises(OSError):self.equip()
  self.assertEqual(before,self.world.state)
 def test_con_hp_clamp_cannot_heal_by_swapping_or_restart(self):
  self.equip();character=self.world.state['character'];character['stats']['resources']['hp']['current']=12
  self.world.state['character']=rules.project(character)
  bare=self.equip([]);self.assertEqual(bare['sheet']['hp'],dict(current=10,maximum=10))
  self.assertEqual(self.world.state['character']['stats']['resources']['hp'],bare['sheet']['hp'])
  equipped=self.equip();self.assertEqual(equipped['sheet']['hp'],dict(current=10,maximum=12))
  self.world.reset();restarted=GridWorld(self.path)
  self.assertEqual(restarted.observe()['character']['sheet']['hp'],dict(current=10,maximum=12))
 def test_con_hp_scales_with_effective_stat_and_does_not_revive(self):
  self.equip();character=copy.deepcopy(self.world.state['character'])
  character['stats']['base']['CON']=4;character['stats']['level_gains']['CON']=2
  character['stats']['resources']['hp']['current']=0
  value=rules.project(character)
  self.assertEqual(value['sheet']['hp'],dict(current=0,maximum=17))
  self.assertEqual(rules.project(value),value)
 def test_saved_fixed_hp_rules_migrate_once_without_healing(self):
  self.equip();legacy=copy.deepcopy(self.world.state);old=legacy['character'];old['stats']['resources']['hp']=dict(current=6,maximum=10)
  self.path.write_text(json.dumps(legacy));migrated=GridWorld(self.path)
  value=migrated.state['character'];self.assertEqual(value['sheet']['hp'],dict(current=6,maximum=12))
  self.assertEqual(value['revision'],old['revision']+1)
  for key in ('session_id','avatar','game_tick'):self.assertEqual(migrated.state[key],legacy[key])
  self.assertEqual(GridWorld(self.path).state['character'],value)

if __name__=='__main__':unittest.main()
