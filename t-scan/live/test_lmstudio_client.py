import copy,json,unittest
from unittest.mock import patch
from movement_tools import registry
from lmstudio_client import LMStudio,api_messages,chat_events

class Response:
 def __init__(self,events):self.lines=[b'data: '+json.dumps(e).encode()+b'\n' for e in events]+[b'data: [DONE]\n']
 def __enter__(self):return self
 def __exit__(self,*args):pass
 def __iter__(self):return iter(self.lines)
class Dispatch:
 def __init__(self):self.calls=[]
 def submit(self,target,key,tool):self.calls.append((tool,target));return key
 def wait(self,key):return dict(outcome='observed',world={'actual':'evidence'})
 def reject(self,tool,args,call_id,reason):return dict(outcome=reason)
class FakeClient:
 def __init__(self,responses):self.responses=iter(responses);self.seen=[]
 def stream(self,messages,*args):self.seen.append(copy.deepcopy(messages));yield from next(self.responses)
def response(calls=None,finish='stop'):
 return [dict(kind='response',text='hello',calls=calls or [],finish=finish)]
def call(arguments='{}',name='move_east'):
 return dict(id='provider-id',type='function',function=dict(name=name,arguments=arguments))

class LMStudioTests(unittest.TestCase):
 def run_loop(self,client):
  dispatch=Dispatch();saved=[]
  events=list(chat_events(client,[dict(role='user',content='task')],dispatch,'request',registry(),.2,lambda:'HARNESS RECORD / current state',lambda m:saved.append(copy.deepcopy(m)),lambda:False))
  return dispatch,saved,events
 def test_old_native_arguments_converted_without_mutating_history(self):
  messages=[dict(role='assistant',tool_calls=[dict(function=dict(arguments={'target':{'hex_id':'all'}}))])]
  converted=api_messages(messages)
  self.assertIsInstance(converted[0]['tool_calls'][0]['function']['arguments'],str)
  self.assertIsInstance(messages[0]['tool_calls'][0]['function']['arguments'],dict)
 def test_stream_assembles_fragmented_structured_calls_and_usage(self):
  c=LMStudio('http://test','model');events=[{'choices':[{'delta':{'tool_calls':[{'index':0,'id':'abc','function':{'name':'inspect','arguments':'{"target":'}}]}}]}, {'choices':[{'delta':{'tool_calls':[{'index':0,'function':{'arguments':'{"hex_id":"all"}}'}}]},'finish_reason':'tool_calls'}]}, {'choices':[],'usage':{'prompt_tokens':10,'completion_tokens':3}}]
  with patch.object(c,'request',return_value=Response(events)):
   values=list(c.stream([],[],.1))
  self.assertEqual(values[-1]['calls'][0]['function']['arguments'],'{"target":{"hex_id":"all"}}')
  self.assertEqual(values[0]['usage']['completion_tokens'],3)
 def test_one_decision_saves_native_call_and_receipt_before_returning(self):
  client=FakeClient([response([call()],'tool_calls'),response()]);dispatch,saved,_=self.run_loop(client)
  self.assertEqual(dispatch.calls,[('move_east',{})])
  self.assertEqual(len(client.seen),1)
  self.assertEqual([m['role'] for m in saved[-1]][-2:],['assistant','tool'])
  self.assertIn('evidence',saved[-1][-1]['content'])
  self.assertEqual(saved[-1][-2]['tool_calls'][0]['id'],saved[-1][-1]['tool_call_id'])
 def test_reasoning_fragments_stay_separate_and_raw_stream_is_preserved(self):
  c=LMStudio('http://test','model');raw=[];c.on_stream_event=raw.append
  events=[{'choices':[{'delta':{'reasoning_content':'Consider ','reasoning':'Consider '}}]}, {'choices':[{'delta':{'reasoning':'south.'}}]}, {'choices':[{'delta':{'content':'Answer.'},'finish_reason':'stop'}]}, {'choices':[],'usage':{'completion_tokens_details':{'reasoning_tokens':5}}}]
  with patch.object(c,'request',return_value=Response(events)):out=list(c.stream([],[],1))
  self.assertEqual(''.join(e['piece'] for e in out if e['kind']=='reasoning'),'Consider south.')
  self.assertEqual(out[-1]['text'],'Answer.');self.assertEqual(raw[-1],'[DONE]');self.assertEqual(json.loads(raw[0]),events[0])
  client=FakeClient([[dict(kind='reasoning',piece='PRIVATE FIXTURE'),*response()]])
  _,saved,forwarded=self.run_loop(client)
  self.assertIn('reasoning',[e['kind'] for e in forwarded]);self.assertNotIn('PRIVATE FIXTURE',json.dumps(saved))
 def test_received_raw_reasoning_survives_operator_interruption(self):
  c=LMStudio('http://test','model');raw=[];c.on_stream_event=raw.append
  with patch.object(c,'request',return_value=Response([{'choices':[{'delta':{'reasoning_content':'partial'}}]}])):
   with self.assertRaises(InterruptedError):list(c.stream([],[],1,lambda:True))
  self.assertEqual(json.loads(raw[0])['choices'][0]['delta']['reasoning_content'],'partial')
 def test_malformed_arguments_are_receipted_without_dispatch(self):
  dispatch,saved,_=self.run_loop(FakeClient([response([call('not json')],'tool_calls'),response()]))
  self.assertFalse(dispatch.calls);self.assertIn('rejected',saved[-1][-1]['content'])
 def test_unregistered_tool_and_extra_fields_are_rejected(self):
  for c in (call(name='pick_up'),call('{"target":{"hex_id":"all"},"extra":1}')):
   dispatch,_,_=self.run_loop(FakeClient([response([c],'tool_calls'),response()]))
   self.assertFalse(dispatch.calls)
 def test_length_limit_never_executes_partial_tools(self):
  dispatch,_,events=self.run_loop(FakeClient([response([call()],'length')]))
  self.assertFalse(dispatch.calls);self.assertEqual(events[-1]['reason'],'provider_output_limit')
 def test_missing_stream_completion_is_error(self):
  c=LMStudio('http://test','model')
  with patch.object(c,'request',return_value=Response([])):
   with self.assertRaisesRegex(RuntimeError,'completion marker'):list(c.stream([],[],.1))

if __name__=='__main__':unittest.main()
