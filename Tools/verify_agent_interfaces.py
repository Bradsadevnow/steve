"""Bounded real-provider interface check in a new, isolated SQLite store.

Uses normal context, registry and tool boundaries. Never touches live Steve state
or dispatches physical movement. This is an interface check, not a navigation trial.
"""
import argparse,json,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'t-scan/live'))
from runtime_store import RuntimeStore
from grid_world import GridWorld,GridDispatch
from grid_conversation import GridConversation
from agent_notepad import AgentDispatch
from movement_tools import registry
from lmstudio_client import LMStudio,chat_events
from run_archive import RunArchive
from atomic_json import write_json

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--lm-url',default='http://192.168.1.128:1234');p.add_argument('--model',default='google/gemma-4-e4b');args=p.parse_args()
 args.output.mkdir(parents=True,exist_ok=False)
 runtime=RuntimeStore(args.output/'memory.db');world=GridWorld(args.output/'world.json')
 # No presenter and no movement capability are supplied to this planner check.
 conversation=GridConversation(args.output/'conversation.json',runtime)
 archive=RunArchive(args.output,conversation,runtime,world,dict(model=args.model,lm_url=args.lm_url,temperature=1,condition='isolated_self_doctrine_interface_check'))
 client=LMStudio(args.lm_url,args.model);client.connect()
 client.on_request=lambda path,payload:archive.request(path,payload,current[0])
 client.on_stream_event=lambda data:archive.stream_event(current[0],data)
 dispatch=AgentDispatch(GridDispatch(world),runtime);dispatch.run_id=archive.current['id'];conversation.run_id=dispatch.run_id
 prompt='Interface verification using synthetic test data only. Create a global Self competence assertion with claim_id interface_check stating that this is a synthetic interface test, not evidence of real competence. Read it back with agent_read, cite its current revision with assertion_cite, then repair that assertion using assertion_write with its current revision and an explicit repair reason; change its statement to say the interface test was revised. Finally call complete. Use empty source_refs for this synthetic assessment. Do not create navigation tasks or request movement.'
 runtime.accept_user(prompt,'verification-human');conversation.user(prompt)
 deadline=time.monotonic()+180;receipts=[];current=[''];error=None
 try:
  for step in range(12):
   if time.monotonic()>=deadline:raise TimeoutError('Interface verification deadline')
   current[0]='interface-'+str(step);dispatch.bind(current[0])
   if step:conversation.tick('verification-human')
   for event in chat_events(client,conversation.messages,dispatch,current[0],registry(phase='planner'),1,lambda:conversation.context(dispatch),conversation.checkpoint,lambda:time.monotonic()>=deadline):
    if event['kind']!='token':archive.event(current[0],event)
    if event['kind']=='receipt':receipts.append(dict(tool=event['call']['function']['name'],result=event['result']))
   if receipts and receipts[-1]['tool']=='complete':break
 except Exception as exc:error=str(exc)
 history=runtime.agent.history('self','interface_check')
 tools={r['tool'] for r in receipts if not r['result']['outcome'].startswith('rejected')}
 passed=len(history)>=2 and {'agent_read','assertion_cite','assertion_write','complete'}<=tools and not world.receipts[:-1]
 report=dict(passed=passed,error=error,tools=[dict(tool=r['tool'],outcome=r['result']['outcome']) for r in receipts],history=history,archive=str(archive.folder.resolve()),kind='isolated_real_provider_interface_verification')
 write_json(args.output/'verification.json',report);print(json.dumps(dict(passed=passed,error=error,tools=report['tools'],archive=report['archive'])),flush=True);runtime.close()
 raise SystemExit(0 if passed else 1)

if __name__=='__main__':main()
