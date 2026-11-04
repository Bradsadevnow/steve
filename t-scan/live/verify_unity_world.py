"""Isolated real-HTTP/Unity presentation check. Does not load or call an LLM.

Run with a new --data-dir, point the live SteveBridge at the printed endpoint,
and let Unity publish its authored manifest. Test steps are mechanical fixtures,
not Steve's choices. Results and receipts stay in that isolated directory.
"""
import argparse,json,threading,time,uuid
from http.server import ThreadingHTTPServer
from pathlib import Path
import bridge
from grid_world import GridWorld
from grid_conversation import GridConversation
from runtime_store import RuntimeStore
from run_archive import RunArchive
from atomic_json import write_json

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--data-dir',type=Path,required=True);parser.add_argument('--port',type=int,default=8876);args=parser.parse_args()
 args.data_dir.mkdir(parents=True,exist_ok=True)
 if (args.data_dir/'grid-world.json').exists():raise ValueError('Use a fresh directory for this verification')
 bridge.runtime=RuntimeStore(args.data_dir/'memory.db');bridge.conversation=GridConversation(args.data_dir/'conversation.json',bridge.runtime);bridge.grid_world=GridWorld(args.data_dir/'grid-world.json')
 bridge.run_archive=RunArchive(args.data_dir,bridge.conversation,bridge.runtime,bridge.grid_world,dict(model='none / mechanical verification'))
 bridge.update(status='ready',source='Mechanical world-boundary verification / no inference')
 server=ThreadingHTTPServer(('127.0.0.1',args.port),bridge.Handler)
 def exercise():
  result=dict(kind='mechanical_protocol_verification',agent_navigation_test=False,steps=[])
  try:
   deadline=time.monotonic()+120
   while not bridge.grid_world.world_ready:
    if time.monotonic()>deadline:raise TimeoutError('Unity did not register its world')
    time.sleep(.1)
   result['initial']=bridge.grid_world.observe()
   # Enter blue, then leave it. These are fixed test requests, not an agent route planner.
   for name in ['move_east']*3+['move_north']*2+['move_west']:
    w=bridge.grid_world;receipt=w.nominate(name,{},'verification-'+uuid.uuid4().hex,w.observe()['observation_id'],'fixture')
    settled=w.wait(receipt['action_id']);result['steps'].append(settled)
    if settled['outcome']!='moved' or settled['presentation_status']!='settled':raise AssertionError(settled)
   result['final']=bridge.grid_world.observe()
   if result['steps'][4]['observation']['standing_on']!=['target_blue'] or result['final']['standing_on']:raise AssertionError('Flag entry/exit mismatch')
   result['passed']=True
  except Exception as error:result.update(passed=False,error=str(error))
  write_json(args.data_dir/'verification.json',result);print(json.dumps(dict(passed=result['passed'],report=str(args.data_dir/'verification.json'))),flush=True)
  server.shutdown()
 threading.Thread(target=exercise,daemon=True).start()
 print('Mechanical verification endpoint http://127.0.0.1:'+str(args.port),flush=True)
 try:server.serve_forever()
 finally:server.server_close();bridge.runtime.close()

if __name__=='__main__':main()
