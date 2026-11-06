"""Two isolated native-provider probes using actual conversation/context construction; never main Steve."""
import json,sys,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'t-scan/live'))
import character_rules as rules
from grid_world import GridWorld,GridDispatch
from world_test_support import publish,poll
from grid_conversation import GridConversation,VERSION
from runtime_store import RuntimeStore
from context_records import decode_envelope
from lmstudio_client import LMStudio
from movement_tools import registry

output=ROOT/'t-scan/runtime_data/verification'/('stats-provider-'+uuid.uuid4().hex[:8]);output.mkdir(parents=True)
client=LMStudio('http://192.168.1.128:1234','google/gemma-4-e4b');client.connect();results=[]
for action,con_base,distance,expected in [('slash',1,1,3),('shield_bash',4,3,2)]:
 folder=output/action;folder.mkdir();world=GridWorld(folder/'world.json');publish(world)
 world.apply_character(dict(request_id=uuid.uuid4().hex,character_id='steve',expected_revision=0,catalog_version=rules.CATALOG['version'],body_id='unicore',equipment=[dict(socket_id='arm_R',module_id='warrior_blade'),dict(socket_id='arm_L',module_id='warrior_shield')]))
 world.state['character']['stats']['base']['CON']=con_base;world.state['character']['stats']['revision']+=1;world.state['character']=rules.project(world.state['character'])
 a=world.state['avatar'];world.state['training_targets']=[dict(id='fixture_dummy',prototype='bosses_dummy_unarmed',col=a['col'],row=a['row']+distance,hp=10,max_hp=10)];world.save()
 runtime=RuntimeStore(folder/'isolated.sqlite3');runtime.import_seed({'records':[dict(key='fixture-identity',kind='self_model',status='curated_self_model',summary='Steve is a hovering unicorn. This source belongs only to the isolated verification fixture.',source={'path':'isolated verification fixture'})]})
 runtime.agent.transition('executor','Isolated registered-capability test',world.state['session_id'])
 conversation=GridConversation(folder/'conversation.json',runtime)
 prompt='Isolated combat check: use '+action+' on fixture_dummy exactly once now. The target is '+str(distance)+' squares north in a clear cardinal lane. Use a native action tool; inspect the measured sheet for current damage.'
 conversation.user(prompt);dispatch=GridDispatch(world);dispatch.bind('fixture-decision');reg=registry(phase='executor',capabilities=world.state['character']['capabilities'])
 context=conversation.context(dispatch);record=decode_envelope(context)[1]
 assert 'simulated_affect' not in record and 'self_model' in record and 'historical_memory' in record
 messages=reg.INFERENCE_MESSAGES(conversation.messages+[dict(role='user',content=context)])
 assert sum('CURRENT WORLD /' in m.get('content','') for m in messages)==1
 assert '"effective": 3' in messages[-1]['content'] and '"stats"' not in messages[-1]['content']
 assert 'bosses_dummy_unarmed' not in json.dumps(messages)
 (folder/'context.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
 client.on_request=lambda path,payload,f=folder:(f/'provider-request.json').write_text(json.dumps(dict(path=path,payload=payload),indent=2),encoding='utf-8')
 reasoning=[];response=None
 for event in client.stream(messages,reg.TOOLS,1.):
  if event['kind']=='reasoning':reasoning.append(event['piece'])
  if event['kind']=='response':response=event
 (folder/'provider-reasoning.txt').write_text(''.join(reasoning),encoding='utf-8');(folder/'provider-response.json').write_text(json.dumps(response,indent=2),encoding='utf-8')
 result=dict(action=action,expected_damage=expected,success=False)
 if response and len(response['calls'])==1:
  call=response['calls'][0]
  if call['function']['name']==action:
   args=json.loads(call['function']['arguments']);reg.validate(action,call['function']['arguments']);poll(world)
   receipt=world.nominate(action,args,'fixture-decision',world.observe()['observation_id'],call['id'])
   if receipt['presentation_status']=='pending':world.acknowledge('test',receipt['action_id'],world.state['session_id'])
   result.update(receipt=receipt,success=receipt['outcome']=='target_hit' and receipt.get('damage')==expected)
   settled=world.wait(receipt['action_id'])
   followup=reg.INFERENCE_MESSAGES(conversation.messages+[dict(role='user',content=context),dict(role='assistant',content=response['text'],tool_calls=response['calls']),dict(role='tool',tool_call_id=call['id'],content=json.dumps(settled)),dict(role='user',content=conversation.context(dispatch))])
   assert followup[-2]['role']=='tool' and followup[-2]['tool_call_id']==call['id'] and 'scaling_stat' in followup[-2]['content']
   (folder/'assembled-followup.json').write_text(json.dumps(client.payload(followup,1.,reg.TOOLS),indent=2),encoding='utf-8')
 runtime.close();results.append(result)
report=dict(condition=VERSION,scope='isolated native executor probes with synthetic presentation acknowledgments, not autonomous Unity combat',passed=sum(r['success'] for r in results),total=len(results),results=results)
(output/'result.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(dict(output=str(output),**report),indent=2))
raise SystemExit(0 if report['passed']==report['total'] else 1)
