import copy,json,tempfile,unittest
from pathlib import Path
from grid_world import GridWorld
from grid_context import ascii_world,inference_messages,FLAG_SYMBOLS,WORLD_POLICY
from context_records import envelope
from world_test_support import publish,poll

class AsciiWorldTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.world=GridWorld(Path(self.tmp.name)/'world.json');publish(self.world,'presenter')
 def tearDown(self):self.tmp.cleanup()
 def test_all_cells_round_trip_exact_avatar_and_flag_occupancy(self):
  for row in range(1,11):
   for col in range(1,11):
    self.world.state['avatar'].update(col=col,row=row)
    state=self.world.observe();before=copy.deepcopy(state);text=ascii_world(state)
    self.assertEqual(state,before);self.assertTrue(text.isascii())
    rows=[line for line in text.splitlines() if line[9:12]==' | ']
    self.assertEqual([int(line[7:9]) for line in rows],list(range(10,0,-1)))
    cells={(c,int(line[7:9])):cell for line in rows for c,cell in enumerate(line.split('|')[1].split(),1)}
    self.assertEqual(len(cells),100)
    self.assertEqual([key for key,cell in cells.items() if cell[0]=='@'],[(col,row)])
    expected={(t['col'],t['row']):FLAG_SYMBOLS[t['color']] for t in state['visible_targets']}
    self.assertEqual({key:cell[1] for key,cell in cells.items() if cell[1]!='.'},expected)
    standing=','.join(state['standing_on']) or 'none'
    self.assertIn('Standing ON: '+standing+'.',text)
 def test_near_flag_and_on_flag_are_distinct(self):
  self.world.state['avatar'].update(col=2,row=6)
  near=ascii_world(self.world.observe());self.assertIn('Standing ON: none.',near)
  self.world.state['avatar'].update(row=8)
  on=ascii_world(self.world.observe());self.assertIn('Standing ON: target_red.',on)
  self.assertIn('08 | .. @R',on);self.assertIn('06 | .. @.',near)
 def test_full_production_projection_one_map_no_nested_worlds_and_native_receipts(self):
  world=self.world.observe();record=envelope('decision_context',current_observation={'observation':{'world':world}},historical_memory={'self_model':['Steve']})
  receipt=dict(action_id='a',call_id='c',action='move_north',outcome='moved',position_before=[5,4],position_after=[5,5],presentation_status='settled',observation=world)
  messages=[dict(role='user',content=record),dict(role='assistant',content='I chose north.',tool_calls=[dict(id='c',type='function',function=dict(name='move_north',arguments='{}'))]),dict(role='tool',tool_call_id='c',content=json.dumps(receipt)),dict(role='user',content=record)]
  original=copy.deepcopy(messages);projected=inference_messages(messages)
  self.assertEqual(messages,original);self.assertEqual(projected[1],messages[1]);self.assertEqual(projected[2]['tool_call_id'],'c')
  self.assertEqual(sum('CURRENT WORLD / '+WORLD_POLICY in m.get('content','') for m in projected),1)
  compact=json.loads(projected[2]['content']);self.assertNotIn('observation',compact);self.assertEqual(compact['position_after'],dict(x=5,y=5));self.assertEqual(compact['presentation_status'],'settled')
  self.assertNotIn('visible_targets',json.dumps(projected));self.assertIn('historical_observation',projected[0]['content'])
  self.assertIn('historical_memory',projected[-1]['content']);self.assertIn('CURRENT WORLD /',projected[-1]['content'])
 def test_compass_labels_and_measured_facing_do_not_rotate_the_board(self):
  boards=[]
  for direction in ('north','south','east','west'):
   self.world.state['avatar']['facing']=direction;text=ascii_world(self.world.observe())
   for label in ('NORTH (N)','SOUTH (S)','WEST','EAST (E)'):self.assertIn(label,text)
   self.assertIn('facing '+direction+'.',text);self.assertIn('AVATAR STATE / measured now',text)
   boards.append([line for line in text.splitlines() if line[9:12]==' | '])
  self.assertTrue(all(board==boards[0] for board in boards))
 def test_only_latest_movement_receipt_is_recent_and_notepad_cannot_impersonate_it(self):
  messages=[]
  for number in (1,2):
   messages.extend([dict(role='assistant',content='',tool_calls=[dict(id=str(number),type='function',function=dict(name='move_north',arguments='{}'))]),dict(role='tool',tool_call_id=str(number),content=json.dumps(dict(action_id=str(number),outcome='blocked_boundary',position_before=[7,10],position_after=[7,10],presentation_status='settled')))])
  messages.append(dict(role='tool',tool_call_id='note',content=json.dumps(dict(record_type='notepad_receipt',notepad={'revision':1,'content':'"action_id"'}))))
  original=copy.deepcopy(messages);projected=inference_messages(messages)
  self.assertEqual(messages,original);self.assertIn('Historical outcome',projected[1]['content']);self.assertIn('Most recent action result',projected[3]['content'])
  self.assertEqual(projected[3]['tool_call_id'],'2');self.assertEqual(json.loads(projected[3]['content'])['position_after'],dict(x=7,y=10))
 def test_absolute_step_semantics_match_controller_for_every_initial_facing(self):
  from movement_tools import DIRECTIONS
  for facing in ('north','south','east','west'):
   for name,(dx,dy) in DIRECTIONS.items():
    self.world.reset();self.world.state['avatar'].update(col=5,row=5,facing=facing);poll(self.world,'presenter')
    r=self.world.nominate(name,{},facing+name,self.world.observe()['observation_id'],'call')
    self.assertEqual(r['position_after'],[5+dx,5+dy]);self.assertEqual(r['facing_after'],name[5:])
    self.world.acknowledge('presenter',r['action_id'],self.world.state['session_id'])

if __name__=='__main__':unittest.main()
