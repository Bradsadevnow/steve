"""Isolated mechanical Unity presentation smoke; never invokes a model or live store."""
import json,sys,threading,time
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'t-scan/live'))
from grid_world import GridWorld
folder=root/'TScanViewer/Temp/course-verification'
folder.mkdir(parents=True,exist_ok=True)
world=GridWorld(folder/'isolated-world.json')
class Handler(BaseHTTPRequestHandler):
 def log_message(self,*a):pass
 def send(self,value,status=200):
  data=json.dumps(value).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
 def do_GET(self):self.send({} if self.path=='/runtime' else world.observe())
 def do_POST(self):
  try:
   a=json.loads(self.rfile.read(int(self.headers['Content-Length'])))
   if self.path=='/grid/world':v=world.register_world(a['client_id'],a['manifest'])
   elif self.path=='/grid/poll':v=world.poll(a['client_id'],a['manifest_hash'])
   elif self.path=='/grid/ack':v=dict(accepted=world.acknowledge(a['client_id'],a['action_id'],a['session_id']))
   else:raise ValueError('Unsupported verification route')
   self.send(v)
  except (ValueError,KeyError) as e:self.send(dict(error=str(e)),400)
server=ThreadingHTTPServer(('127.0.0.1',8876),Handler);threading.Thread(target=server.serve_forever,daemon=True).start()
deadline=time.monotonic()+90
while not world.world_ready and time.monotonic()<deadline:time.sleep(.1)
assert world.world_ready,'Unity did not connect to isolated fixture'
world.reset();receipts=[]
for i,(name,outcome) in enumerate([('move_north','moved'),('move_north','moved'),('move_north','blocked_obstacle'),('move_south','moved'),('move_south','moved'),('move_east','moved'),('move_east','moved'),('move_east','blocked_obstacle')]):
 r=world.nominate(name,{},'course-smoke-'+str(i),world.observe()['observation_id'],'test-'+str(i));r=world.wait(r['action_id'],10)
 assert (r['outcome'],r['presentation_status'])==(outcome,'settled'),r
 receipts.append(r)
result=dict(passed=True,kind='mechanical fixture, no model navigation',receipts=receipts)
(folder/'result.json').write_text(json.dumps(result,indent=2));print('PASS: eight real Unity acknowledgements, including hedge and boulder collision',flush=True)
while not (folder/'stop').exists() and time.monotonic()<deadline:time.sleep(.1)
server.shutdown()
