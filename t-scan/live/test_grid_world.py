import copy,tempfile,unittest,threading,time,json,uuid
from pathlib import Path
from grid_world import GridWorld
from movement_tools import TOOLS,DIRECTIONS
from world_test_support import publish,poll
class GridTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.w=GridWorld(Path(self.temp.name)/'world.json');publish(self.w);self.w.control('start')
 def tearDown(self):self.temp.cleanup()
 def step(self,name,turn=None,obs=None,args=None):
  poll(self.w);return self.w.nominate(name,args or {},turn or uuid.uuid4().hex,obs or self.w.observe()['observation_id'],'call')
 def settle(self,r):self.assertTrue(self.w.acknowledge('test',r['action_id'],self.w.state['session_id']))
 def test_spawn_and_exact_tools(self):
  self.assertEqual(self.w.observe()['self'],dict(id='steve',col=5,row=5,facing='north'));self.assertEqual({t['function']['name'] for t in TOOLS},set(DIRECTIONS)|{'complete','task_list_read','task_list_write','task_mark_complete','task_remove','agent_read','assertion_write','assertion_cite','assertion_link','intention_write','plan_handoff','request_replan'})
  for t in TOOLS:
   if t['function']['name'] in set(DIRECTIONS)|{'complete','task_list_read'}:self.assertEqual(t['function']['parameters']['properties'],{})
 def test_five_flags_are_distinct_visible_and_occupiable(self):
  flags=self.w.observe()['visible_targets'];self.assertEqual({f['color'] for f in flags},{'blue','red','yellow','purple','orange'});self.assertEqual(len({(f['col'],f['row']) for f in flags}),5)
  for f in flags:
   self.assertTrue(1<=f['col']<=10 and 1<=f['row']<=10);self.assertTrue(f['occupiable']);self.assertEqual(f['kind'],'flag')
   # Enter each flag's cell with a normal cardinal action; flags add no collision rule.
   self.w.state['avatar'].update(col=f['col'],row=f['row']-1);r=self.step('move_north');self.assertEqual(r['outcome'],'moved');self.assertIn(f['id'],self.w.observe()['standing_on']);self.settle(r)
 def test_surroundings_identify_every_flag(self):
  for f in self.w.observe()['visible_targets']:
   self.w.state['avatar'].update(col=f['col'],row=f['row']-1);self.assertEqual(self.w.observe()['surroundings']['north']['target'],f['id'])
 def test_existing_session_gets_flags_without_resetting_avatar(self):
  legacy=copy.deepcopy(self.w.state);legacy.pop('world_definition');legacy['targets']=[dict(id='target_blue',col=8,row=7)];legacy['avatar'].update(col=4,row=6);self.w.path.write_text(json.dumps(legacy));new=GridWorld(self.w.path)
  self.assertEqual(new.observe()['visible_targets'],[]);self.assertFalse(new.world_ready);publish(new)
  self.assertEqual(new.state['session_id'],legacy['session_id']);self.assertEqual(new.state['avatar'],legacy['avatar']);self.assertEqual(len(new.observe()['visible_targets']),5);self.assertEqual(new.state['world_revision'],legacy['world_revision']+1)
 def test_each_direction_changes_one_square(self):
  for tool,(dx,dy) in DIRECTIONS.items():
   before=self.w.observe()['self'];r=self.step(tool);self.assertEqual(r['position_after'],[before['col']+dx,before['row']+dy]);self.settle(r)
 def test_boundary_changes_facing_not_position(self):
  self.w.state['avatar'].update(col=1,row=10)
  for name in ('move_north','move_west'):
   r=self.step(name);self.assertEqual(r['outcome'],'blocked_boundary');self.assertEqual(r['position_after'],[1,10]);self.assertEqual(self.w.observe()['self']['facing'],name[5:]);self.settle(r)
 def test_duplicate_stale_unsupported_and_args_never_move(self):
  obs=self.w.observe()['observation_id'];r=self.step('move_east','once',obs);self.settle(r)
  for tool,turn,o,args,expected in [('move_east','once',obs,{},'rejected_duplicate'),('move_north','new',obs,{},'rejected_stale'),('teleport','bad',None,{},'rejected_schema'),('move_east','arg',None,{'distance':2},'rejected_schema')]:
   before=copy.deepcopy(self.w.state['avatar']);r=self.step(tool,turn,o,args);self.assertEqual(r['outcome'],expected);self.assertEqual(self.w.state['avatar'],before)
  self.assertEqual(self.w.state['observation_seq'],6);self.assertEqual(len(self.w.receipts),5)
 def test_wait_blocks_until_correct_presenter_ack(self):
  r=self.step('move_north');result=[];t=threading.Thread(target=lambda:result.append(self.w.wait(r['action_id'])));t.start();time.sleep(.03)
  self.assertFalse(result);self.assertFalse(self.w.acknowledge('other',r['action_id'],self.w.state['session_id']));self.settle(r);t.join(1);self.assertEqual(result[0]['presentation_status'],'settled')
 def test_busy_attempt_cannot_replace_pending_commit(self):
  r=self.step('move_east');other=self.step('move_north');self.assertEqual(other['outcome'],'rejected_busy');self.settle(r);self.assertEqual(self.w.wait(r['action_id'])['presentation_status'],'settled')
 def test_reset_new_identity_and_initial_state(self):
  old=self.w.state['session_id'];r=self.step('move_east');self.settle(r);self.w.control('stop');s=self.w.reset();self.assertNotEqual(old,s['session_id']);self.assertEqual(s['self']['col'],5);self.assertEqual(s['world_revision'],0)
 def test_governance_denial_and_error_do_not_mutate(self):
  self.w.authorizer=lambda n,s:(False,'policy denied');r=self.step('move_east');self.assertEqual(r['decision'],'DENY');self.assertEqual(r['position_after'],[5,5])
 def test_session_persistence(self):
  r=self.step('move_east');self.settle(r);other=GridWorld(self.w.path);self.assertEqual(other.observe()['self']['col'],6);self.assertTrue(other.enabled);self.assertFalse(other.running)
 def test_stop_pauses_clock_but_manual_movement_needs_no_arming(self):
  self.w.control('run');self.w.control('stop');self.assertFalse(self.w.running);self.assertTrue(self.w.observe()['enabled'])
  r=self.step('move_north');self.assertEqual(r['outcome'],'moved');self.settle(r)
 def test_revision_changes_only_for_state_changes(self):
  initial=self.w.state['world_revision'];self.w.state['avatar'].update(row=10,facing='north');r=self.step('move_north');self.assertEqual(r['world_revision'],initial);self.settle(r);r=self.step('move_west');self.assertEqual(r['world_revision'],initial+1);self.settle(r)
 def test_every_cell_all_directions(self):
  for col in range(1,11):
   for row in range(1,11):
    for tool,(dx,dy) in DIRECTIONS.items():
     self.w.state['avatar'].update(col=col,row=row);r=self.step(tool);valid=1<=col+dx<=10 and 1<=row+dy<=10
     self.assertEqual(r['position_after'],[col+dx,row+dy] if valid else [col,row]);self.settle(r)
if __name__=='__main__':unittest.main()
