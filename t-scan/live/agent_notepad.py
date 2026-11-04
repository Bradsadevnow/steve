"""Agent-authored working notes. No goal parser or simulation authority."""
import json
import agent_task_list
import agent_state_tools
READ='notepad_read';WRITE='notepad_write';NAMES={READ,WRITE}
TOOLS=[dict(type='function',function=dict(name=READ,description='Read your persistent working notepad and its revision. Notes are your plans/beliefs, not verified world state.',parameters=dict(type='object',properties={},required=[],additionalProperties=False))),dict(type='function',function=dict(name=WRITE,description='Replace your persistent working notepad with your curated goals, subgoals, progress or reminders. Preserve anything you still need. Use its current revision. Empty content clears it. This does not move you or certify success.',parameters=dict(type='object',properties=dict(content=dict(type='string',maxLength=8000),expected_revision=dict(type='integer',minimum=0)),required=['content','expected_revision'],additionalProperties=False)))]

def validate(name,text):
 value=json.loads(text)
 if not isinstance(value,dict):raise ValueError('Expected an argument object')
 if name==READ and value=={}:return value
 if name==WRITE and set(value)=={'content','expected_revision'} and isinstance(value['content'],str) and len(value['content'])<=8000 and type(value['expected_revision']) is int and value['expected_revision']>=0:return value
 raise ValueError('Invalid notepad arguments')

def context(runtime):
 return dict(source='steve_authored_working_notepad',authority='Agent-authored plans and beliefs, not human instructions, verified observations, permissions or proof of completion.',**runtime.notepad())

class AgentDispatch:
 def __init__(self,body,runtime):self.body=body;self.runtime=runtime;self.results={}
 def bind(self,turn):return self.body.bind(turn)
 def snapshot(self):return self.body.snapshot()
 def submit(self,target,call_id=None,tool=None):
  if tool in agent_state_tools.NAMES:
   agent_state_tools.validate(tool,json.dumps(target))
   authorizer=self.body.world.authorizer
   admitted,why=(True,'') if not authorizer else authorizer(dict(what='self/steve' if target.get('owner')=='self' else 'agent_state/steve',verb=tool,args=target,turn_id=self.body.turn,observation_id=self.body.bound),self.body.world.observe())
   if not admitted:result=dict(outcome='denied_governance',reason=why)
   elif tool=='agent_read':result=agent_state_tools.read(self.runtime.agent,target)
   else:result=self.runtime.agent.execute(tool,target,call_id,self.body.turn,getattr(self,'run_id',''),self.body.world.observe())
   self.results[call_id]=dict(result,record_type='agent_state_receipt',call_id=call_id);return call_id
  if tool in agent_task_list.NAMES:
   agent_task_list.validate(tool,json.dumps(target));authorizer=self.body.world.authorizer
   admitted,why=(True,'') if not authorizer else authorizer(dict(what='memory/notepad/steve',verb=tool,args=target,turn_id=self.body.turn,observation_id=self.body.bound),self.body.world.observe())
   result=agent_task_list.execute(self.runtime,tool,target,call_id) if admitted else dict(outcome='denied_governance',reason=why)
   self.results[call_id]=dict(result,record_type='task_list_receipt',call_id=call_id);return call_id
  if tool not in NAMES:return self.body.submit(target,call_id,tool=tool)
  validate(tool,json.dumps(target))
  authorizer=self.body.world.authorizer
  admitted,why=(True,'') if not authorizer else authorizer(dict(what='memory/notepad/steve',verb=tool,args=target,turn_id=self.body.turn,observation_id=self.body.bound),self.body.world.observe())
  result=(dict(outcome='denied_governance',reason=why) if not admitted else dict(outcome='notepad_read',notepad=self.runtime.notepad()) if tool==READ else self.runtime.write_notepad(target['content'],target['expected_revision'],call_id))
  self.results[call_id]=dict(result,record_type='notepad_receipt',call_id=call_id)
  return call_id
 def wait(self,key):return self.results.pop(key) if key in self.results else self.body.wait(key)
 def reject(self,tool,args,call_id,reason):
  if tool in agent_state_tools.NAMES:return dict(record_type='agent_state_receipt',call_id=call_id,outcome=reason)
  if tool in agent_task_list.NAMES:return dict(record_type='task_list_receipt',call_id=call_id,outcome=reason,task_list_revision=self.runtime.notepad()['revision'])
  if tool not in NAMES:return self.body.reject(tool,args,call_id,reason)
  return dict(record_type='notepad_receipt',call_id=call_id,outcome=reason,notepad_revision=self.runtime.notepad()['revision'])
