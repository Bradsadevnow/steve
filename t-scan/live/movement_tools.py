"""Four zero-argument movements, completion, and agent-authored task tools."""
import json
from types import SimpleNamespace
from grid_context import inference_messages
import agent_task_list
import agent_state_tools
DIRECTIONS={'move_north':(0,1),'move_south':(0,-1),'move_east':(1,0),'move_west':(-1,0)}
COMPLETE='complete'
MAP_DIRECTIONS={'move_north':'y +1','move_south':'y -1','move_east':'x +1','move_west':'x -1'}
TOOLS=[dict(type='function',function=dict(name=n,description='Request one step '+n[5:]+' ('+MAP_DIRECTIONS[n]+'). x and y each range from 1 to 10. The environment reports the actual outcome.',parameters=dict(type='object',properties={},required=[],additionalProperties=False))) for n in DIRECTIONS]
TOOLS.append(dict(type='function',function=dict(name=COMPLETE,description='End this interaction and stop further decision ticks when finished or handing control back to the human. Takes no arguments. A later human message wakes the loop again. Does not move the avatar, mark a task done (the planner phase records task statuses with task_mark_complete) or certify that a navigation goal succeeded.',parameters=dict(type='object',properties={},required=[],additionalProperties=False))))
TOOLS+=agent_task_list.TOOLS+agent_state_tools.TOOLS
def done_hint(names=None):
 """Where a task is marked done, stated for the tools the caller actually has."""
 if names is None:return 'Task statuses are recorded in the planner phase with task_mark_complete.'
 if 'task_mark_complete' in names:return 'To record that a task is done, call task_mark_complete.'
 if 'request_replan' in names:return 'task_mark_complete is not available in this phase. To record that a task is done, call request_replan to return to planning, where it is available.'
 return 'Task statuses are recorded in the planner phase with task_mark_complete.'
def validate(name,text,names=None):
 if name in agent_state_tools.NAMES:return agent_state_tools.validate(name,text)
 if name in agent_task_list.NAMES:return agent_task_list.validate(name,text)
 if name not in (*DIRECTIONS,COMPLETE):raise ValueError('Unregistered tool name')
 value=json.loads(text)
 if value!={}:
  received=', '.join(sorted(value)) if isinstance(value,dict) else 'a '+type(value).__name__+' value'
  hint=' complete() ends the interaction; it does not mark a task done. '+done_hint(names) if name==COMPLETE else ''
  raise ValueError(name+'() takes no arguments, but received: '+received+'. Nothing was executed. Call '+name+'() with an empty argument object.'+hint)
 return dict(tool=name)
# Epoch clock registration. CLOCK_TOOLS are the calls that advance the world; the executor can count only
# these (COUNT_CLOCK) toward the epoch budget instead of every call (COUNT_ALL, the v8.4 behavior).
# A clock tool spends the budget only when the controller admitted it (an outcome in CLOCK_OUTCOMES);
# rejected, stale or offline attempts do not. Future world actions register by joining CLOCK_TOOLS
# and CLOCK_OUTCOMES. Non-clock calls (tasks, reads, notes) are free but bounded by MAX_TOTAL_CALLS.
CLOCK_TOOLS=frozenset(DIRECTIONS)
CLOCK_OUTCOMES=frozenset({'moved','blocked_boundary'})
COUNT_ALL='all_calls';COUNT_CLOCK='clock_actions';COUNT_ACCEPTED='accepted_calls'
MAX_TOTAL_CALLS=8
def registry(active_task=False,phase=None,max_calls=3,count_policy=COUNT_ALL,max_total_calls=MAX_TOTAL_CALLS):
 if count_policy not in (COUNT_ALL,COUNT_CLOCK,COUNT_ACCEPTED):raise ValueError('Unknown epoch count policy')
 names=({COMPLETE,*agent_task_list.NAMES,*agent_state_tools.PLANNER} if phase=='planner' else {COMPLETE,*DIRECTIONS,*agent_state_tools.EXECUTOR} if phase=='executor' else {t['function']['name'] for t in TOOLS})
 return SimpleNamespace(TOOLS=[t for t in TOOLS if t['function']['name'] in names],SCHEMAS=dict.fromkeys(names),validate=lambda name,text:validate(name,text,frozenset(names)),DIRECT_ARGUMENTS=True,SINGLE_ACTION=max_calls==1,MAX_CALLS=max_calls,INFERENCE_MESSAGES=inference_messages,CLOCK=frozenset(names&CLOCK_TOOLS),CLOCK_OUTCOMES=CLOCK_OUTCOMES,COUNT_POLICY=count_policy,MAX_TOTAL_CALLS=max_total_calls)
