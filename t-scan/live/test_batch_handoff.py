"""Batch cleanup may stop its own turn, never a replacement human turn."""
import json,tempfile,threading,unittest,urllib.request,urllib.error
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from http.server import ThreadingHTTPServer
import bridge,transit_batch

class BatchHandoffTests(unittest.TestCase):
 def setUp(self):
  self.calls=[];self.world=SimpleNamespace(loop_origin='batch',pending=None,control=lambda action:self.calls.append(action) or dict(stopped=True))
  self.patch=patch.multiple(bridge,grid_world=self.world,lock=threading.Lock(),pending=None,active_kind=None,state={},runtime=SimpleNamespace(event=lambda *a:None),run_archive=None,conversation=SimpleNamespace(pause=lambda *a:None),request=threading.Event(),turn_interrupt=threading.Event())
  self.patch.start();self.server=ThreadingHTTPServer(('127.0.0.1',0),bridge.Handler);self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
 def tearDown(self):self.server.shutdown();self.server.server_close();self.thread.join();self.patch.stop()
 def stop(self):
  request=urllib.request.Request('http://127.0.0.1:'+str(self.server.server_port)+'/grid/control',data=json.dumps(dict(action='stop',expected_origin_request_id='batch')).encode(),headers={'Content-Type':'application/json'})
  try:
   with urllib.request.urlopen(request) as response:return response.status,json.load(response)
  except urllib.error.HTTPError as error:return error.code,json.load(error)
 def test_queued_correction_survives_cleanup_before_worker_claims_it(self):
  bridge.pending=dict(requestId='human');status,result=self.stop();self.assertEqual(status,409);self.assertEqual(self.calls,[]);self.assertEqual(bridge.pending['requestId'],'human');self.assertFalse(bridge.turn_interrupt.is_set())
 def test_claimed_correction_survives_cleanup(self):
  self.world.loop_origin='human';self.assertEqual(self.stop()[0],409);self.assertEqual(self.calls,[])
 def test_owned_turn_can_still_be_stopped(self):
  self.assertEqual(self.stop()[0],200);self.assertEqual(self.calls,['stop']);self.assertTrue(bridge.turn_interrupt.is_set())
 def test_runner_releases_human_takeover_without_stop_or_reset(self):
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder);data=root/'data';data.mkdir();(data/'current-run.json').write_text('{"id":"run"}');(data/'grid-world.receipts.jsonl').touch();calls=[];polls=0
   initial=dict(world_ready=True,running=False,presentation=None,self=dict(id='steve',col=5,row=5,facing='north'))
   class Response:
    def __init__(self,value):self.value=value
    def __enter__(self):return self
    def __exit__(self,*a):pass
    def read(self):return json.dumps(self.value).encode()
   def api(request,**kw):
    nonlocal polls
    route=urllib.parse.urlsplit(request.full_url).path;calls.append(route)
    if route=='/grid/state':
     polls+=1
     return Response(initial if polls<=2 else dict(initial,running=True,decision_loop=dict(origin_request_id='batch' if polls==3 else 'human')))
    return Response(dict(status='ready') if route=='/health' else dict(requestId='batch') if route=='/generate' else {})
   with patch('sys.argv',['batch','--output',str(root/'out'),'--data-dir',str(data)]),patch.object(transit_batch.urllib.request,'urlopen',api),patch.object(transit_batch.time,'sleep',lambda _:None):transit_batch.main()
   report=json.loads((root/'out'/'status.json').read_text());self.assertEqual(report['status'],'cancelled');self.assertNotIn('/grid/control',calls);self.assertEqual(calls.count('/chat/new'),1);self.assertEqual(report['results'],[])

if __name__=='__main__':unittest.main()
