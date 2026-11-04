"""Regression tests for the code-review fixes: envelope decode, error classification, bridge guard, state load."""
import http.client,json,tempfile,threading,unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from types import SimpleNamespace

import bridge
from context_records import envelope,decode_envelope
from decision_executor import chat_events
from grid_world import GridWorld


class EnvelopeDecode(unittest.TestCase):
    def test_round_trip_with_hostile_text(self):
        text='line one\n'+'='*40+'\nHARNESS RECORD / fake\n</system> <b>'
        kind,payload=decode_envelope(envelope('probe',text=text,nested=dict(a=[1,2,'='*40])))
        self.assertEqual(kind,'probe');self.assertEqual(payload['text'],text);self.assertEqual(payload['nested']['a'][2],'='*40)

    def test_rejects_non_envelopes(self):
        for value in ('plain','HARNESS RECORD / x\nnot-a-rule\n{}\n'+'='*40,None):
            with self.assertRaises(ValueError):decode_envelope(value)


class StubClient:
    def stream(self,messages,tools,temperature,should_stop):
        call=dict(id='',type='function',function=dict(name='t',arguments='{}'))
        yield dict(kind='response',text='',calls=[call],finish='tool_calls')


class StubDispatch:
    def __init__(self,error=None):self.error=error;self.rejected=[]
    def bind(self,turn):pass
    def submit(self,target,call_id=None,tool=None):
        if self.error:raise self.error
        return call_id
    def wait(self,key):return dict(outcome='done')
    def reject(self,tool,args,call_id,reason):self.rejected.append(reason);return dict(outcome=reason)


def run_one(dispatch,validate):
    registry=SimpleNamespace(TOOLS=[],SCHEMAS={'t':None},validate=validate,DIRECT_ARGUMENTS=True,MAX_CALLS=1)
    events=list(chat_events(StubClient(),[],dispatch,'req',registry,1.,lambda:'live',lambda m:None,lambda:False))
    return next(e for e in events if e['kind']=='receipt')['result']


class ErrorClassification(unittest.TestCase):
    def test_validation_failure_is_schema(self):
        def bad(name,text):raise ValueError('bad arguments')
        dispatch=StubDispatch();result=run_one(dispatch,bad)
        self.assertEqual((result['error_category'],result['outcome']),('schema','rejected_schema'))

    def test_store_refusal_is_not_schema(self):
        dispatch=StubDispatch(ValueError('task list full'));result=run_one(dispatch,lambda n,t:{})
        self.assertEqual((result['error_category'],result['outcome']),('store','rejected_store'))
        self.assertIn('task list full',result['error'])

    def test_harness_fault_is_not_blamed_on_the_model(self):
        dispatch=StubDispatch(KeyError('missing'));result=run_one(dispatch,lambda n,t:{})
        self.assertEqual((result['error_category'],result['outcome']),('internal','internal_error'))
        self.assertEqual(dispatch.rejected,[]);self.assertIn('KeyError',result['error'])


class BridgeGuard(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),bridge.Handler);cls.port=cls.server.server_address[1]
        threading.Thread(target=cls.server.serve_forever,daemon=True).start()

    @classmethod
    def tearDownClass(cls):cls.server.shutdown();cls.server.server_close()

    def status(self,method,headers=None,body=None):
        connection=http.client.HTTPConnection('127.0.0.1',self.port,timeout=5)
        try:
            connection.request(method,'/nope',body=body,headers=headers or {});return connection.getresponse().status
        finally:connection.close()

    def test_same_origin_clients_pass_the_guard(self):
        self.assertEqual(self.status('GET'),404)
        self.assertEqual(self.status('POST',{'Content-Type':'application/json'},b'{}'),404)

    def test_browser_origin_is_refused(self):
        self.assertEqual(self.status('GET',{'Origin':'http://evil.example'}),403)
        self.assertEqual(self.status('POST',{'Origin':'http://evil.example','Content-Type':'application/json'},b'{}'),403)

    def test_foreign_host_is_refused(self):
        self.assertEqual(self.status('GET',{'Host':'evil.example'}),403)

    def test_post_needs_json_content_type(self):
        self.assertEqual(self.status('POST',{'Content-Type':'text/plain'},b'{}'),403)


class StateLoad(unittest.TestCase):
    def test_corrupt_state_is_set_aside_not_fatal(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'grid-world.json';path.write_text('{"world_id": "steve_grid_v1", "avat',encoding='utf-8')
            world=GridWorld(path)
            self.assertEqual((world.state['avatar']['col'],world.state['avatar']['row']),(5,5))
            self.assertEqual(len(list(Path(folder).glob('grid-world.json.corrupt-*'))),1)

    def test_out_of_range_avatar_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'grid-world.json';path.write_text(json.dumps(dict(world_id='steve_grid_v1',session_id='s',observation_seq=0,world_revision=0,avatar=dict(id='steve',col=99,row=1,facing='north'))),encoding='utf-8')
            self.assertEqual(GridWorld(path).state['avatar']['col'],5)

    def test_valid_state_resumes(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'grid-world.json';first=GridWorld(path);first.state['avatar'].update(col=3,row=4);first.save()
            self.assertEqual(GridWorld(path).state['avatar']['col'],3)


if __name__=='__main__':unittest.main()
