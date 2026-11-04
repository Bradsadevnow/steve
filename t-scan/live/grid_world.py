"""One authoritative grid writer, separate mechanical admission and cosmetic presentation."""
import copy,json,sys,threading,time,uuid
from pathlib import Path
from movement_tools import DIRECTIONS,COMPLETE
from atomic_json import write_json
from world_manifest import validate_manifest
SCHEMA='steve-grid-v1'
class GridWorld:
 def __init__(self,path,clock=time.monotonic,authorizer=None):
  self.path=Path(path);self.clock=clock;self.authorizer=authorizer;self.lock=threading.Condition(threading.RLock());self.receipts=[];self.used_turns=set();self.pending=None;self.enabled=True;self.running=False;self.last_poll=-1e9;self.presenter='';self.last_action=None
  self.loop_origin=None;self.pause_reason='startup';self.definition_confirmed=False
  self._digest=None
  if self.path.exists():self._load()
  else:self._initial()
  self.save()
 def _load(self):
  """Resume saved state; a truncated or malformed file is set aside, loudly, instead of blocking startup."""
  try:
   state=json.loads(self.path.read_text(encoding='utf-8'));a=state['avatar']
   if not (isinstance(state,dict) and state.get('world_id')=='steve_grid_v1' and isinstance(state.get('session_id'),str) and type(state.get('observation_seq')) is int and type(state.get('world_revision')) is int and type(a['col']) is int and type(a['row']) is int and 1<=a['col']<=10 and 1<=a['row']<=10 and a.get('facing') in ('north','south','east','west')):raise ValueError('unexpected grid state shape')
   self.state=state
  except (OSError,ValueError,KeyError,TypeError) as error:
   aside=self.path.with_name(self.path.name+'.corrupt-'+time.strftime('%Y%m%d-%H%M%S'))
   try:self.path.replace(aside)
   except OSError:aside=None
   print('WARNING: grid state unreadable ('+str(error)+'); '+('kept as '+str(aside) if aside else 'could not be moved')+'; starting a fresh grid session',file=sys.stderr,flush=True)
   self._initial()
 def _initial(self):
  definition=copy.deepcopy(getattr(self,'state',{}).get('world_definition'))
  self.state=dict(world_id='steve_grid_v1',session_id=uuid.uuid4().hex,observation_seq=0,world_revision=0,avatar=dict(id='steve',col=5,row=5,facing='north'))
  if definition:self.state['world_definition']=definition
 @property
 def world_ready(self):return self.definition_confirmed and self.clock()-self.last_poll<=3
 def register_world(self,client,manifest):
  definition,digest=validate_manifest(manifest)
  if not isinstance(client,str) or not client or len(client)>128:raise ValueError('Invalid environment client')
  with self.lock:
   old=self.state.get('world_definition');changed=old!=definition
   if self.presenter and client!=self.presenter and self.clock()-self.last_poll<=3:raise ValueError('Another environment client is presenting this world')
   if changed:
    if self.pending or self.running:raise ValueError('Stop the decision loop and finish presentation before changing the world')
    if old and definition['revision']<=old['revision']:raise ValueError('Changed world definitions require a higher revision')
   confirmed_now=not self.definition_confirmed
   if changed or confirmed_now:
    self.state['world_definition']=definition
    self.state.pop('targets',None);self.state.pop('landmarks_version',None)
    self.state['observation_seq']+=1
    if changed:self.state['world_revision']+=1
    self.save()
    self._log(dict(kind='world_definition_registered',source='unity_environment',manifest_hash=digest,definition=definition,session_id=self.state['session_id'],world_revision=self.state['world_revision']))
   self.definition_confirmed=True;self.presenter=client;self.last_poll=self.clock()
   return self.observe()
 def save(self):
  write_json(self.path,self.state)
 def observe(self):
  with self.lock:
   a=self.state['avatar'];definition=self.state.get('world_definition');targets=definition['landmarks'] if definition and self.definition_confirmed else [];locations={(t['col'],t['row']):t['id'] for t in targets}
   adjacent={n[5:]:dict(terrain='open_floor' if 1<=a['col']+d[0]<=10 and 1<=a['row']+d[1]<=10 else 'board_edge',target=locations.get((a['col']+d[0],a['row']+d[1]))) for n,d in DIRECTIONS.items()}
   standing=[t['id'] for t in targets if (a['col'],a['row'])==(t['col'],t['row'])]
   state={k:copy.deepcopy(v) for k,v in self.state.items() if k not in ('targets','landmarks_version','world_definition')}
   if not definition:digest=''
   elif self._digest and self._digest[0] is definition:digest=self._digest[1]
   else:digest=validate_manifest(definition)[1];self._digest=(definition,digest)
   provenance=dict(source='unity_environment',world_id=self.state['world_id'],revision=definition['revision'] if definition else None,manifest_hash=digest,status='confirmed' if self.world_ready else 'disconnected' if self.definition_confirmed else 'awaiting_unity_manifest')
   return dict(schema=SCHEMA,**state,world_ready=self.world_ready,world_manifest_hash=digest,world_definition=provenance,observation_id=f"{self.state['session_id']}:obs-{self.state['observation_seq']:04}",self=copy.deepcopy(a),board=dict(columns=10,rows=10,north='row+1',east='col+1'),visible_targets=copy.deepcopy(targets),surroundings=adjacent,standing_on=standing,last_action=copy.deepcopy(self.last_action),available_tools=[*DIRECTIONS,COMPLETE],enabled=self.enabled,running=self.running,decision_loop=dict(active=self.running,origin_request_id=self.loop_origin,pause_reason=self.pause_reason),presentation=copy.deepcopy(self.pending))
 def wake(self,request_id):
  with self.lock:
   self.running=True;self.loop_origin=request_id;self.pause_reason=None
   self._log(dict(kind='decision_loop_wake',source='human_message',request_id=request_id,session_id=self.state['session_id']))
 def idle(self):
  with self.lock:
   if self.running and not self.pending:
    self.running=False;self.pause_reason='no_action'
    self._log(dict(kind='decision_loop_idle',source='controller',reason='no_tool_requested',origin_request_id=self.loop_origin,session_id=self.state['session_id']))
 def stall(self,epochs):
  """The loop made no progress for several epochs in a row: hand control back, say why, choose nothing."""
  with self.lock:
   if self.running:
    self.running=False;self.pause_reason='stalled'
    self._log(dict(kind='decision_loop_stalled',source='controller',reason='repeated_rejection',epochs=epochs,origin_request_id=self.loop_origin,session_id=self.state['session_id']))
 def reset(self):
  with self.lock:
   if self.pending:raise ValueError('Stop presentation before resetting')
   self._initial();self.used_turns.clear();self.receipts=[];self.last_action=None;self.enabled=True;self.running=False;self.loop_origin=None;self.pause_reason='reset';self.save();return self.observe()
 def control(self,action):
  with self.lock:
   if action=='stop':
    self.running=False;self.pause_reason='operator'
   elif action in ('start','run'):self.enabled=True;self.running=action=='run' or self.running
   elif action=='reset':return self.reset()
   else:raise ValueError('Unknown grid control')
   return self.observe()
 def poll(self,client,manifest_hash=None):
  with self.lock:
   if not self.definition_confirmed or client!=self.presenter or manifest_hash!=self.observe()['world_manifest_hash']:raise ValueError('Register the matching Unity world manifest before polling')
   self.last_poll=self.clock()
   return self.observe()
 def nominate(self,name,args,turn,observation,call_id,force_reject=None):
  with self.lock:
   before=copy.deepcopy(self.state['avatar']);actual=self.observe();outcome=force_reject;decision='DENY';why='';after=copy.deepcopy(before)
   if not outcome:
    if name not in (*DIRECTIONS,COMPLETE) or args!={}:outcome='rejected_schema'
    elif turn in self.used_turns:outcome='rejected_duplicate'
    elif observation!=actual['observation_id']:outcome='rejected_stale'
    elif self.pending:outcome='rejected_busy'
    elif name in DIRECTIONS and not self.world_ready:outcome='offline'
    else:
     # Extension point for Warden. A denial cannot modify state. No intent claim is made here.
     admitted=True
     if self.authorizer:
      try:admitted,why=self.authorizer(dict(what='decision_loop/steve' if name==COMPLETE else 'avatars/steve',verb=name,args={},turn_id=turn,observation_id=observation),copy.deepcopy(self.state))
      except Exception as e:admitted=False;why='Governance error: '+str(e)
     if not admitted:outcome='denied_governance'
     else:
      decision='ACCEPT'
      if name==COMPLETE:self.running=False;self.pause_reason='complete';outcome='interaction_complete'
      else:
       dx,dy=DIRECTIONS[name];col=before['col']+dx;row=before['row']+dy;after['facing']=name[5:]
       if 1<=col<=10 and 1<=row<=10:after.update(col=col,row=row);outcome='moved'
       else:outcome='blocked_boundary'
   self.used_turns.add(turn);self.state['observation_seq']+=1
   if after!=before:self.state['avatar']=after;self.state['world_revision']+=1
   receipt=dict(action_id='act-'+uuid.uuid4().hex,call_id=call_id,turn_id=turn,session_id=self.state['session_id'],observation_id=observation,action=str(name)[:64],decision=decision,decision_basis=why or outcome,outcome=outcome,position_before=[before['col'],before['row']],position_after=[after['col'],after['row']],facing_before=before['facing'],facing_after=after['facing'],world_revision=self.state['world_revision'],observation_seq=self.state['observation_seq'],presentation_status='not_required')
   if outcome in ('moved','blocked_boundary'):
    receipt['presentation_status']='pending';self.pending=copy.deepcopy(receipt)
   self.last_action=receipt;self.receipts.append(receipt);self.save();self._log(receipt);return copy.deepcopy(receipt)
 def _log(self,value):
  with self.path.with_suffix('.receipts.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(value)+'\n')
 def _presented(self,action_id,status):
  if not self.pending or self.pending['action_id']!=action_id:return False
  next(r for r in reversed(self.receipts) if r['action_id']==action_id)['presentation_status']=status;self.pending=None;self._log(dict(kind='presentation_result',action_id=action_id,status=status));self.lock.notify_all();return True
 def acknowledge(self,client,action_id,session_id):
  with self.lock:
   if client!=self.presenter or session_id!=self.state['session_id']:return False
   return self._presented(action_id,'settled')
 def wait(self,action_id,timeout=15):
  with self.lock:
   deadline=self.clock()+timeout
   while self.pending and self.pending['action_id']==action_id:
    if self.clock()>=deadline:self.running=False;self.pause_reason='presentation_timeout';self._presented(action_id,'timeout');break
    self.lock.wait(.1)
   receipt=next(r for r in reversed(self.receipts) if r['action_id']==action_id)
   return dict(receipt,observation=self.observe())

class GridDispatch:
 def __init__(self,world):self.world=world;self.bound='';self.turn='';self.local={}
 def bind(self,turn):self.turn=turn;self.bound=self.world.observe()['observation_id']
 def snapshot(self):
  state=self.world.observe();fields=('schema','session_id','observation_id','observation_seq','world_revision','world_ready','world_definition','self','board','visible_targets','surroundings','standing_on','last_action','available_tools','enabled','decision_loop')
  return dict(observation=dict(world={k:state[k] for k in fields}),state_source='deterministic_grid')
 def submit(self,target,call_id=None,tool=None):
  r=self.world.nominate(tool,target,self.turn,self.bound,call_id);self.local[call_id]=r['action_id'];return call_id
 def reject(self,tool,args,call_id,reason):
  r=self.world.nominate(tool,args,self.turn,self.bound,call_id,reason);return self.world.wait(r['action_id'])
 def wait(self,key):return self.world.wait(self.local.pop(key))
