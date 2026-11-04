"""Four zero-argument movements, completion, and agent-authored task tools."""
import json
from types import SimpleNamespace
from grid_context import inference_messages
import agent_task_list
DIRECTIONS={'move_north':(0,1),'move_south':(0,-1),'move_east':(1,0),'move_west':(-1,0)}
COMPLETE='complete'
MAP_DIRECTIONS={'move_north':'y +1','move_south':'y -1','move_east':'x +1','move_west':'x -1'}
TOOLS=[dict(type='function',function=dict(name=n,description='Request one step '+n[5:]+' ('+MAP_DIRECTIONS[n]+'). x and y each range from 1 to 10. Independent of facing; the step also faces '+n[5:]+'. The environment reports the actual outcome.',parameters=dict(type='object',properties={},required=[],additionalProperties=False))) for n in DIRECTIONS]
TOOLS.append(dict(type='function',function=dict(name=COMPLETE,description='End this interaction and stop further decision ticks when finished or handing control back to the human. A later human message wakes the loop again. Does not move the avatar or certify that a navigation goal succeeded.',parameters=dict(type='object',properties={},required=[],additionalProperties=False))))
TOOLS+=agent_task_list.TOOLS
def validate(name,text):
 if name in agent_task_list.NAMES:return agent_task_list.validate(name,text)
 if name not in (*DIRECTIONS,COMPLETE) or json.loads(text)!={}:raise ValueError('Only registered zero-argument actions are supported')
 return dict(tool=name)
def registry(active_task=False):return SimpleNamespace(TOOLS=TOOLS,SCHEMAS=dict.fromkeys((*DIRECTIONS,COMPLETE,*agent_task_list.NAMES)),validate=validate,DIRECT_ARGUMENTS=True,SINGLE_ACTION=True,INFERENCE_MESSAGES=inference_messages)
