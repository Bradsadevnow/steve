"""Explicit operator-owned chat runs and lossless local research exports."""
import copy,json,threading,time,uuid
from pathlib import Path
from atomic_json import write_json
from grid_conversation import SYSTEM,VERSION

class OperatorNotesConflict(ValueError):
 def __init__(self,current):self.current=current;super().__init__('Run or notes revision changed; reload the saved notes before editing again')

class RunArchive:
 def __init__(self,root,conversation,runtime,world,config):
  self.root=Path(root);self.pointer=self.root/'current-run.json';self.config=config;self.lock=threading.RLock()
  if self.pointer.exists():
   self.current=json.loads(self.pointer.read_text(encoding='utf-8'));self.record_configuration(conversation)
  else:self.start(conversation,runtime,world,'capture_started_with_existing_history')
 @property
 def folder(self):return self.root/'runs'/self.current['id']
 def configuration(self,conversation):
  from movement_tools import TOOLS
  return dict(config=self.config,conversation=conversation.metadata(),system=SYSTEM,tools=TOOLS,capture=dict(version='provider-reasoning-v1',raw_stream='inference-stream.jsonl',reasoning='separate archive events and UI; excluded from conversation/memory'))
 def record_configuration(self,conversation):
  active=self.folder/'active-config.json';previous_path=active if active.exists() else self.folder/'config.json'
  previous=json.loads(previous_path.read_text(encoding='utf-8'));current=self.configuration(conversation)
  if previous!=current:self.append('condition-changes.jsonl',dict(time=time.time(),kind='inference_configuration_changed',previous=previous,current=current))
  write_json(active,current)
 def start(self,conversation,runtime,world,reason):
  stamp=time.strftime('%Y%m%d-%H%M%S',time.gmtime())
  self.current=dict(id=stamp+'-'+uuid.uuid4().hex[:8],started_at_unix=time.time(),reason=reason,event_start_id=runtime.db.execute('SELECT COALESCE(MAX(id),0) FROM events').fetchone()[0])
  log=world.path.with_suffix('.receipts.jsonl')
  self.current['controller_log_start']=log.stat().st_size if log.exists() and reason=='operator_new_chat' else 0
  if reason=='capture_started_with_existing_history':
   cutoff=runtime.db.execute("SELECT value FROM state WHERE key='working_memory_cutoff'").fetchone()
   self.current['event_start_id']=int(cutoff[0]) if cutoff else 0
  self.folder.mkdir(parents=True,exist_ok=False)
  write_json(self.folder/'start-state.json',world.observe());write_json(self.folder/'start-notepad.json',runtime.notepad())
  from agent_task_list import context as task_list_context
  write_json(self.folder/'start-task-list.json',task_list_context(runtime))
  configuration=self.configuration(conversation)
  write_json(self.folder/'config.json',configuration);write_json(self.folder/'active-config.json',configuration)
  from grid_context import ascii_world
  (self.folder/'start-world.txt').write_text(ascii_world(world.observe()),encoding='utf-8')
  write_json(self.pointer,self.current)
 def append(self,name,value):
  with self.lock:
   with (self.folder/name).open('a',encoding='utf-8') as output:output.write(json.dumps(value,ensure_ascii=True)+'\n')
 def request(self,path,payload,request_id):self.append('inference-requests.jsonl',dict(time=time.time(),request_id=request_id,path=path,payload=payload))
 def event(self,request_id,event):self.append('inference-events.jsonl',dict(time=time.time(),request_id=request_id,event=event))
 def stream_event(self,request_id,data):self.append('inference-stream.jsonl',dict(time=time.time(),request_id=request_id,data=data))
 def operator_notes(self):
  with self.lock:
   path=self.folder/'operator-notes.json'
   return json.loads(path.read_text(encoding='utf-8')) if path.exists() else dict(run_id=self.current['id'],revision=0,content='',updated_at_unix=None,source='human_operator',included_in_model_context=False)
 def save_operator_notes(self,run_id,expected_revision,content):
  if not isinstance(content,str) or len(content)>65536 or type(expected_revision) is not int or expected_revision<0:raise ValueError('Notes require up to 65536 characters and a nonnegative integer revision')
  with self.lock:
   current=self.operator_notes()
   if run_id!=self.current['id'] or expected_revision!=current['revision']:raise OperatorNotesConflict(current)
   if current['content']==content:return current
   value=dict(current,revision=current['revision']+1,content=content,updated_at_unix=time.time())
   write_json(self.folder/'operator-notes.json',value)
   return value
 def finish(self,conversation,runtime,world):
  with self.lock:
   messages=copy.deepcopy(conversation.messages);folder=self.folder
   write_json(folder/'conversation.json',dict(version=VERSION,messages=messages,task=conversation.task))
   chat=[];snapshots=[];receipts=[]
   for index,message in enumerate(messages):
    text=message.get('content') or ''
    if message['role']=='user' and text.startswith('HARNESS RECORD / decision_context\n'):
     record=json.loads(text.split('\n',2)[2].rsplit('\n',1)[0]);snapshots.append(dict(message_index=index,source='decision_context',record=record))
    elif message['role']=='tool':
     result=json.loads(text);receipts.append(dict(message_index=index,tool_call_id=message['tool_call_id'],result=result))
     if result.get('observation'):snapshots.append(dict(message_index=index,source='tool_receipt',record=result['observation']))
    elif message['role'] in ('user','assistant') and text and not text.startswith('HARNESS RECORD / '):chat.append('## '+message['role'].upper()+'\n\n'+text+'\n')
   (folder/'chat.md').write_text('\n'.join(chat),encoding='utf-8')
   for name,values in [('state-snapshots.jsonl',snapshots),('tool-receipts.jsonl',receipts)]:
    (folder/name).write_text(''.join(json.dumps(v,ensure_ascii=True)+'\n' for v in values),encoding='utf-8')
   write_json(folder/'final-state.json',world.observe());write_json(folder/'final-notepad.json',runtime.notepad());write_json(folder/'final-affect.json',runtime.snapshot()['affect'])
   from agent_task_list import context as task_list_context
   write_json(folder/'final-task-list.json',task_list_context(runtime))
   notes=self.operator_notes();write_json(folder/'operator-notes.json',notes)
   (folder/'operator-notes.md').write_text(notes['content'],encoding='utf-8')
   from grid_context import ascii_world
   (folder/'final-world.txt').write_text(ascii_world(world.observe()),encoding='utf-8')
   log=world.path.with_suffix('.receipts.jsonl')
   if log.exists():
    with log.open('rb') as source:source.seek(self.current.get('controller_log_start',0));(folder/'controller-events.jsonl').write_bytes(source.read())
   with runtime.lock:
    events=[dict(r) for r in runtime.db.execute('SELECT * FROM events WHERE id>? ORDER BY id',(self.current['event_start_id'],))]
   (folder/'runtime-events.jsonl').write_text(''.join(json.dumps(v,ensure_ascii=True)+'\n' for v in events),encoding='utf-8')
   manifest=dict(**self.current,status='archived',ended_at_unix=time.time(),message_count=len(messages),observation_count=len(snapshots),tool_receipt_count=len(receipts),inference_capture='Exact outgoing requests recorded since instrumentation/start; earlier world contexts and receipts recovered from retained transcript.',new_chat_policy='Fresh conversation, reset position and empty working notepad. Long-term memory and affect retained. Loop paused.')
   write_json(folder/'manifest.json',manifest)
   return dict(archived_run_id=self.current['id'],archive_path=str(folder.resolve()))
 def new_chat(self,conversation,runtime,world,request_id):
  with self.lock,conversation.lock,runtime.lock:
   prior=runtime.db.execute("SELECT content FROM events WHERE kind='chat_run_rotated' AND request_id=?",(request_id,)).fetchone()
   if prior:return json.loads(prior[0])
   # Archive must finish successfully before any chat state is cleared.
   archived=self.finish(conversation,runtime,world)
   conversation.messages=[dict(role='system',content=SYSTEM)];conversation.task=None;conversation.save()
   runtime.clear_working_memory()
   note=runtime.notepad();runtime.write_notepad('',note['revision'],'operator-new-chat:'+request_id)
   world.reset()
   self.start(conversation,runtime,world,'operator_new_chat')
   result=dict(**archived,new_run_id=self.current['id'],position_reset=True,notepad_cleared=True)
   runtime.event('chat_run_rotated',json.dumps(result),request_id)
   return result
