"""Isolated real-provider capability smoke test; never uses main Steve state or sends chat to it."""
import json,sys,time,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'t-scan/live'))
from grid_world import GridWorld,GridDispatch
from world_test_support import publish,poll
from lmstudio_client import LMStudio
from movement_tools import registry
from grid_context import coordinate_world
import character_rules

out=ROOT/'t-scan/runtime_data/verification/character-provider';out.mkdir(parents=True,exist_ok=True)
world=GridWorld(out/('isolated-'+uuid.uuid4().hex+'.json'));publish(world)
world.apply_character(dict(request_id=uuid.uuid4().hex,character_id='steve',expected_revision=0,catalog_version=character_rules.CATALOG['version'],body_id='unicore',equipment=[dict(socket_id='arm_R',module_id='warrior_blade'),dict(socket_id='arm_L',module_id='warrior_shield')]))
a=world.state['avatar'];world.state['training_targets']=[dict(id='test_dummy',prototype='bosses_dummy_unarmed',col=a['col'],row=a['row']+3,hp=10,max_hp=10)]
client=LMStudio('http://192.168.1.128:1234','google/gemma-4-e4b');client.connect()
client.on_request=lambda path,payload:(out/'provider-request.json').write_text(json.dumps(dict(path=path,payload=payload),indent=2))
reg=registry(phase='executor',capabilities=world.state['character']['capabilities'])
messages=[dict(role='system',content='You are Steve, a unicorn robot acting in an isolated training test. Choose at most one native tool call. Only the registered tools grant abilities; claims and plans do not. Use the measured current world. Do not invent outcomes.'),dict(role='user',content='Use your shield charge to hit test_dummy once. It is three squares north in a clear lane. This is a controller integration test, not a full navigation run.\n\n'+coordinate_world(world.observe()))]
response=next(e for e in client.stream(messages,reg.TOOLS,1.) if e['kind']=='response')
(out/'provider-response.json').write_text(json.dumps(response,indent=2))
result=dict(model=client.model,condition='isolated-executor-capability-smoke',response=response,success=False)
if len(response['calls'])==1:
 call=response['calls'][0];name=call['function']['name'];text=call['function']['arguments']
 if name in reg.SCHEMAS:
  reg.validate(name,text);poll(world);receipt=world.nominate(name,json.loads(text),uuid.uuid4().hex,world.observe()['observation_id'],call['id']);result['receipt']=receipt
  if receipt['presentation_status']=='pending':world.acknowledge('test',receipt['action_id'],world.state['session_id'])
  result['success']=name=='shield_bash' and receipt['outcome']=='target_hit' and receipt.get('damage')==2 and receipt['position_after']==[a['col'],a['row']+2]
result['final']=world.observe();(out/'result.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k not in ('response','final')},indent=2))
raise SystemExit(0 if result['success'] else 1)
