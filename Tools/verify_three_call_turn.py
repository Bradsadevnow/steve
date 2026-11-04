"""Isolated real-LM task-tool smoke; never opens Steve's private state or wakes him."""
import json,sys,tempfile,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'t-scan/live'))
from runtime_store import RuntimeStore
from grid_world import GridWorld,GridDispatch
from world_test_support import publish
from grid_conversation import GridConversation,VERSION
from agent_notepad import AgentDispatch
from movement_tools import registry
from lmstudio_client import LMStudio,chat_events
from agent_task_list import context

def main():
 output=ROOT/'t-scan/runtime_data/verification'/('three-call-smoke-'+time.strftime('%Y%m%d-%H%M%S',time.gmtime()))
 output.mkdir(parents=True,exist_ok=False)
 with tempfile.TemporaryDirectory() as folder:
  root=Path(folder);runtime=RuntimeStore(root/'memory.db');world=GridWorld(root/'world.json');publish(world)
  conversation=GridConversation(root/'chat.json',runtime);conversation.run_id='isolated-smoke'
  conversation.user('Please create three separate pending tasks: visit blue, visit red, and visit yellow. Do not start navigation yet; just record these three goals.')
  dispatch=AgentDispatch(GridDispatch(world),runtime);dispatch.run_id='isolated-smoke';client=LMStudio('http://192.168.1.128:1234','google/gemma-4-e4b');client.connect();requests=[];events=[]
  client.on_request=lambda path,payload:requests.append(dict(path=path,payload=payload))
  started=time.time()
  try:
   for event in chat_events(client,conversation.messages,dispatch,'smoke',registry(phase='planner'),1,lambda:conversation.context(dispatch),conversation.checkpoint,lambda:False):events.append(event)
   receipts=[e for e in events if e['kind']=='receipt'];report=dict(condition=VERSION,isolated=True,synthetic_test_world=True,elapsed_seconds=time.time()-started,provider_requests=len(requests),calls=[dict(tool=e['call']['function']['name'],outcome=e['result']['outcome'],call_id=e['call']['id']) for e in receipts],ending=events[-1].get('reason'),task_list=context(runtime),world_receipts=len(world.receipts))
   report['passed']=len(receipts)==3 and len(requests)==3 and report['ending']=='tool_call_limit' and all(e['result']['outcome']=='task_list_saved' for e in receipts) and len(report['task_list']['tasks'])==3 and not world.receipts
  finally:
   (output/'requests.json').write_text(json.dumps(requests,indent=2),encoding='utf-8');(output/'events.json').write_text(json.dumps(events,indent=2),encoding='utf-8');runtime.close()
  (output/'result.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(dict(result=str(output/'result.json'),**report),indent=2))
  if not report['passed']:raise SystemExit(1)

if __name__=='__main__':main()
