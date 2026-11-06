"""Ownership and persistence regressions from the character/combat cleanup."""
import copy,tempfile,unittest,uuid
from pathlib import Path
from unittest.mock import patch
from grid_world import GridWorld
from movement_tools import registry
from test_built_world import built,piece,placement
import character_rules

class CombatCleanupTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.world=GridWorld(Path(self.tmp.name)/'world.json')
  self.manifest=built();self.manifest['catalog'].append(piece('bosses_dummy_unarmed','Training dummy','actor',True));self.manifest['obstacles'].append(placement('dummy','bosses_dummy_unarmed',10,10));self.world.register_world('test',self.manifest)
 def tearDown(self):self.tmp.cleanup()
 def test_unrelated_world_edits_preserve_damaged_and_defeated_targets(self):
  for hp in (4,0):
   self.world.state['training_targets'][0]['hp']=hp;self.manifest['revision']+=1;self.manifest['props'][1]['yaw']=(self.manifest['props'][1]['yaw']+90)%360
   self.world.register_world('test',self.manifest)
   self.assertEqual(self.world.observe()['training_targets'][0]['hp'],hp)
  restarted=GridWorld(self.world.path);restarted.register_world('test',self.manifest)
  self.assertEqual(restarted.observe()['training_targets'][0]['hp'],0)
 def test_replaced_target_initializes_and_removed_target_stays_removed(self):
  self.world.state['training_targets'][0]['hp']=0;self.manifest['revision']+=1;self.manifest['obstacles'][-1]['id']='replacement'
  self.world.register_world('test',self.manifest);self.assertEqual(self.world.observe()['training_targets'][0]['hp'],10)
  self.manifest['revision']+=1;self.manifest['obstacles'].pop();self.manifest['catalog']=[p for p in self.manifest['catalog'] if p['prototype']!='bosses_dummy_unarmed'];self.world.register_world('test',self.manifest)
  self.assertEqual(self.world.observe()['training_targets'],[])
 def test_failed_attack_save_rolls_back_all_effects_and_allows_retry(self):
  w=self.world;w.apply_character(dict(request_id=uuid.uuid4().hex,character_id='steve',expected_revision=w.state['character']['revision'],catalog_version=character_rules.CATALOG['version'],body_id='unicore',equipment=[dict(socket_id='arm_R',module_id='warrior_blade')]))
  w.state['avatar'].update(col=10,row=9);w.save();before=copy.deepcopy(w.state);disk=w.path.read_bytes();obs=w.observe()['observation_id']
  with patch.object(w,'save',side_effect=OSError('fixture full disk')):
   with self.assertRaises(OSError):w.nominate('slash',{'target_id':'dummy'},'retry-turn',obs,'call')
  self.assertEqual(w.state,before);self.assertEqual(w.path.read_bytes(),disk);self.assertIsNone(w.pending);self.assertIsNone(w.last_action);self.assertEqual(w.receipts,[]);self.assertNotIn('retry-turn',w.used_turns)
  receipt=w.nominate('slash',{'target_id':'dummy'},'retry-turn',obs,'call');self.assertEqual(receipt['target_hp_after'],7)
 def test_failed_world_save_preserves_position_targets_and_journal(self):
  w=self.world;before=copy.deepcopy(w.state);journal=w.path.with_suffix('.receipts.jsonl').read_bytes();self.manifest.update(revision=4,spawn=dict(col=4,row=4))
  with patch.object(w,'save',side_effect=OSError('fixture full disk')):
   with self.assertRaises(OSError):w.register_world('test',self.manifest)
  self.assertEqual(w.state,before);self.assertEqual(w.path.with_suffix('.receipts.jsonl').read_bytes(),journal)
 def test_registry_rejects_unequipped_and_wrong_phase_actions(self):
  for phase,caps in [('planner',['slash']),('executor',[]),(None,['slash'])]:
   reg=registry(phase=phase,capabilities=caps)
   with self.assertRaisesRegex(ValueError,'not registered'):reg.validate('slash','{"target_id":"dummy"}')
  reg=registry(phase='executor',capabilities=['slash','invented_spell'])
  self.assertNotIn('invented_spell',reg.SCHEMAS);self.assertEqual(reg.validate('slash','{"target_id":"dummy"}')['target_id'],'dummy')

if __name__=='__main__':unittest.main()
