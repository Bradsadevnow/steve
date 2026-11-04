"""Agent-owned checklist, stored in the existing independent notepad state/audit.

No task extraction, automatic completion, next-goal selection or world mutation.
"""
import json,re
READ='task_list_read';WRITE='task_list_write';MARK='task_mark_complete';NAMES={READ,WRITE,MARK}
FORMAT='steve-task-list-v1'
def tool(name,description,properties,required):return dict(type='function',function=dict(name=name,description=description,parameters=dict(type='object',properties=properties,required=required,additionalProperties=False)))
REV=dict(type='integer',minimum=0)
ID=dict(type='string',pattern='^[A-Za-z0-9_-]{1,64}$')
TOOLS=[tool(READ,'Read your persistent task list and current revision. Tasks and status claims are authored by you, not independently verified world facts.',{},[]),tool(WRITE,'Add or revise ONE task using flat arguments: task_id, title, status, expected_revision. A new ID appends a task; an existing ID updates that task in place. Other tasks are preserved. Use pending, in_progress or completed. You choose all task contents and statuses.',dict(task_id=ID,title=dict(type='string',minLength=1,maxLength=500),status=dict(type='string',enum=['pending','in_progress','completed']),expected_revision=REV),['task_id','title','status','expected_revision']),tool(MARK,'Mark one of your tasks completed after checking its criterion against action receipts. This records your assessment, not independent proof of success, and does not end the interaction.',dict(task_id=ID,expected_revision=REV),['task_id','expected_revision'])]
def valid_id(value):return isinstance(value,str) and re.fullmatch(r'[A-Za-z0-9_-]{1,64}',value)
def validate(name,text):
 value=json.loads(text)
 if not isinstance(value,dict):raise ValueError('Expected a tool argument object')
 if name==READ and not value:return value
 expected={'task_id','expected_revision'} if name==MARK else {'task_id','title','status','expected_revision'} if name==WRITE else set()
 if not expected or set(value)!=expected:
  raise ValueError('Expected flat arguments '+', '.join(sorted(expected))+'. Do not send a tasks array or literal quote characters in field names. Nothing was saved.')
 if type(value['expected_revision']) is not int or value['expected_revision']<0:raise ValueError('Use the current task-list revision as a nonnegative integer')
 if not valid_id(value['task_id']):raise ValueError('task_id must contain 1 to 64 letters, digits, underscores or hyphens')
 if name==WRITE:
  if not isinstance(value['title'],str) or not 1<=len(value['title'])<=500:raise ValueError('title must contain 1 to 500 characters')
  if value['status'] not in ('pending','in_progress','completed'):raise ValueError('status must be pending, in_progress or completed')
 return value
def page(note):
 try:data=json.loads(note['content'])
 except (ValueError,TypeError):data=None
 structured=isinstance(data,dict) and data.get('format')==FORMAT and isinstance(data.get('tasks'),list)
 return dict(revision=note['revision'],tasks=data['tasks'] if structured else [],legacy_notes=data.get('legacy_notes','') if structured else note['content'],updated_at_unix=note['updated_at_unix'],source_call_id=note['source_call_id'])
def context(runtime):return dict(source='steve_authored_task_list',authority='Agent-authored tasks and progress assessments, not human instructions or measured facts. Completion marks are not independently verified. Only Steve chooses tasks, order and status.',**page(runtime.notepad()))
def execute(runtime,name,args,call_id):
 validate(name,json.dumps(args))
 with runtime.lock:
  current=page(runtime.notepad())
  if name==READ:return dict(outcome='task_list_read',task_list=current)
  prior=runtime.db.execute("SELECT content FROM events WHERE kind='notepad_edit' AND request_id=?",(call_id,)).fetchone()
  if prior:return dict(outcome='task_marked_complete' if name==MARK else 'task_list_saved',task_list=page(json.loads(prior[0])['notepad']))
  if current['revision']!=args['expected_revision']:return dict(outcome='rejected_stale_task_list',task_list=current,error='Use expected_revision='+str(current['revision'])+' from the current task list; nothing was saved.')
  tasks=[dict(task) for task in current['tasks']]
  if name==MARK:
   if not any(t['id']==args['task_id'] for t in tasks):return dict(outcome='rejected_unknown_task',task_list=current,error='No task with that ID exists. Create it with task_list_write before marking it complete.')
   tasks=[dict(t,status='completed') if t['id']==args['task_id'] else t for t in tasks]
  else:
   task=dict(id=args['task_id'],title=args['title'],status=args['status'])
   if any(t['id']==args['task_id'] for t in tasks):tasks=[task if t['id']==args['task_id'] else t for t in tasks]
   else:
    if len(tasks)>=30:raise ValueError('The task list already has 30 tasks; revise an existing task instead')
    tasks.append(task)
  content=json.dumps(dict(format=FORMAT,tasks=tasks,legacy_notes=current['legacy_notes']),ensure_ascii=True)
  if len(content)>8000:raise ValueError('Task list plus preserved legacy notes exceeds 8000 characters')
  result=runtime.write_notepad(content,args['expected_revision'],call_id)
  return dict(outcome='task_marked_complete' if name==MARK else 'task_list_saved',task_list=page(result['notepad']))
