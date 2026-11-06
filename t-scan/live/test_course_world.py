"""Synthetic v2 fixtures: collision, persistence and actual provider message projection."""
import copy,json,tempfile,unittest
from pathlib import Path
from grid_world import GridWorld,GridDispatch
from world_test_support import manifest
from world_manifest import validate_manifest
from grid_context import inference_messages
from context_records import envelope

def course():
 m=manifest();m.update(schema='meadow-world-v2',revision=2,columns=15,rows=15,spawn=dict(col=8,row=8),obstacles=[dict(id='test_wall',prototype='stone_wall',col=9,row=8)])
 m['landmarks'][0].update(col=15,row=15)
 return m

class CourseWorldTests(unittest.TestCase):
 def test_apply_changed_start_moves_avatar_without_resetting_run(self):
  with tempfile.TemporaryDirectory() as d:
   w=GridWorld(Path(d)/'world.json');value=course();w.register_world('test',value);w.reset()
   w.state['game_tick']=7;before=copy.deepcopy(w.state)
   value.update(revision=3,spawn=dict(col=13,row=4))
   after=w.register_world('test',value)
   self.assertEqual((after['self']['col'],after['self']['row']),(13,4))
   for field in ('session_id','character','game_tick'):self.assertEqual(w.state[field],before[field])
   self.assertEqual(w.register_world('test',value),after)
   restarted=GridWorld(w.path);restarted.register_world('test',value)
   self.assertEqual((restarted.observe()['self']['col'],restarted.observe()['self']['row']),(13,4))
   self.assertEqual(restarted.reset()['self']['col'],13)
 def test_apply_layout_with_unchanged_start_keeps_avatar_position(self):
  with tempfile.TemporaryDirectory() as d:
   w=GridWorld(Path(d)/'world.json');value=course();w.register_world('test',value);w.reset()
   w.state['avatar'].update(col=6,row=6)
   value['revision']=3;value['obstacles'][0].update(col=10,row=8)
   after=w.register_world('test',value)
   self.assertEqual((after['self']['col'],after['self']['row']),(6,6))
 def test_changed_start_cannot_move_avatar_while_running(self):
  with tempfile.TemporaryDirectory() as d:
   w=GridWorld(Path(d)/'world.json');value=course();w.register_world('test',value);w.wake('human')
   before=copy.deepcopy(w.state);value.update(revision=3,spawn=dict(col=13,row=4))
   with self.assertRaisesRegex(ValueError,'Stop the decision loop'):w.register_world('test',value)
   self.assertEqual(w.state,before)
 def test_invalid_overlap_and_out_of_bounds_are_rejected(self):
  for cell in [(8,8),(15,15),(16,1)]:
   m=course();m['obstacles'][0].update(col=cell[0],row=cell[1])
   with self.assertRaises(ValueError):validate_manifest(m)
  m=course();m['obstacles'].append(copy.deepcopy(m['obstacles'][0]))
  with self.assertRaises(ValueError):validate_manifest(m)
 def test_obstacles_block_without_moving_and_settle_before_next_step(self):
  with tempfile.TemporaryDirectory() as d:
   w=GridWorld(Path(d)/'world.json');w.register_world('test',course());w.reset()
   s=w.observe();self.assertEqual((s['self']['col'],s['self']['row']),(8,8));self.assertEqual(s['surroundings']['east']['terrain'],'obstacle')
   r=w.nominate('move_east',{},'one',s['observation_id'],'c1');self.assertEqual(r['outcome'],'blocked_obstacle');self.assertEqual(r['position_after'],[8,8]);self.assertEqual(r['presentation_status'],'pending')
   self.assertTrue(w.acknowledge('test',r['action_id'],s['session_id']));self.assertEqual(w.wait(r['action_id'])['presentation_status'],'settled')
   for i in range(7):
    r=w.nominate('move_north',{},'north'+str(i),w.observe()['observation_id'],'n'+str(i));w.acknowledge('test',r['action_id'],s['session_id'])
   self.assertEqual(w.observe()['self']['row'],15)
   r=w.nominate('move_north',{},'edge',w.observe()['observation_id'],'edge');self.assertEqual(r['outcome'],'blocked_boundary')
   restarted=GridWorld(w.path);self.assertEqual(restarted.observe()['self']['row'],15)
 def test_actual_provider_projection_has_current_obstacles_and_historical_bounds(self):
  with tempfile.TemporaryDirectory() as d:
   w=GridWorld(Path(d)/'w.json');w.register_world('test',course());w.reset()
   record=envelope('decision_context',current_observation=GridDispatch(w).snapshot(),agent_task_list={},historical_memory={})
   messages=[dict(role='system',content='Trusted'),dict(role='user',content='Visit blue'),dict(role='user',content=record)]
   actual=inference_messages(messages)
   text=actual[-1]['content'];self.assertIn('"x":[1,15]',text)
   row=next(line for line in text.splitlines() if line.startswith('08  ')).split()[1:]
   self.assertEqual(row[7:9],['@','X'])
   self.assertNotIn('test_wall',text);self.assertNotIn('stone_wall',text);self.assertNotIn('SURROUNDINGS /',text)
   self.assertIn(w.observe()['world_manifest_hash'],actual[-1]['content']);self.assertEqual(actual[0],messages[0])

if __name__=='__main__':unittest.main()
