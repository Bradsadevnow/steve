"""One authoritative grid writer, separate mechanical admission and cosmetic presentation."""
import copy,json,sys,threading,time,uuid
from pathlib import Path
from movement_tools import DIRECTIONS,COMPLETE
from atomic_json import write_json
from world_manifest import validate_manifest,expand_obstacles
import character_rules
import combat_rules
import training_targets
import world_perception
SCHEMA='steve-grid-v1'
class GridWorld:
 def __init__(self,path,clock=time.monotonic,authorizer=None):
  self.path=Path(path);self.clock=clock;self.authorizer=authorizer;self.lock=threading.Condition(threading.RLock());self.receipts=[];self.used_turns=set();self.pending=None;self.enabled=True;self.running=False;self.last_poll=-1e9;self.presenter='';self.last_action=None
  self.loop_origin=None;self.pause_reason='startup';self.definition_confirmed=False
  self._digest=None
  if self.path.exists():self._load()
  else:self._initial()
  self.state.setdefault('character',character_rules.initial());self.state.setdefault('game_tick',0);self.state.setdefault('training_targets',[]);self.state.setdefault('loadout_receipts',[])
  old_character=copy.deepcopy(self.state['character']);self.state['character'],migrated=character_rules.migrate(old_character)
  if migrated:
   migration=dict(kind='character_stats_migration',schema='steve-character-stats-v1',resource_rules_version=character_rules.character_stats.RESOURCE_RULES_VERSION,previous_catalog=old_character['catalog_version'],catalog_version=character_rules.CATALOG['version'],previous_revision=old_character['revision'],revision=self.state['character']['revision'],reason='Reconcile trusted character/equipment/resource rules; preserve current HP subject to max clamp, body, equipment, session and position')
   self.state['character_migrations']=(self.state.get('character_migrations',[])+[migration])[-32:];self.state['observation_seq']+=1
  self.save()
  if migrated:self._log(migration)
 def _load(self):
  """Resume saved state; a truncated or malformed file is set aside, loudly, instead of blocking startup."""
  try:
   state=json.loads(self.path.read_text(encoding='utf-8'));a=state['avatar']
   if not (isinstance(state,dict) and state.get('world_id')=='steve_grid_v1' and isinstance(state.get('session_id'),str) and type(state.get('observation_seq')) is int and type(state.get('world_revision')) is int and type(a['col']) is int and type(a['row']) is int and 1<=a['col']<=state.get('world_definition',{}).get('columns',10) and 1<=a['row']<=state.get('world_definition',{}).get('rows',10) and a.get('facing') in ('north','south','east','west')):raise ValueError('unexpected grid state shape')
   self.state=state
  except (OSError,ValueError,KeyError,TypeError) as error:
   aside=self.path.with_name(self.path.name+'.corrupt-'+time.strftime('%Y%m%d-%H%M%S'))
   try:self.path.replace(aside)
   except OSError:aside=None
   print('WARNING: grid state unreadable ('+str(error)+'); '+('kept as '+str(aside) if aside else 'could not be moved')+'; starting a fresh grid session',file=sys.stderr,flush=True)
   self._initial()
 def _initial(self):
  definition=copy.deepcopy(getattr(self,'state',{}).get('world_definition'))
  character=copy.deepcopy(getattr(self,'state',{}).get('character',character_rules.initial()))
  self.state=dict(world_id='steve_grid_v1',session_id=uuid.uuid4().hex,observation_seq=0,world_revision=0,avatar=dict(id='steve',col=(definition or {}).get('spawn',{}).get('col',5),row=(definition or {}).get('spawn',{}).get('row',5),facing='north'))
  if definition:self.state['world_definition']=definition
  self.state.update(character=character,game_tick=0,training_targets=training_targets.from_manifest(definition),loadout_receipts=[])
 def apply_character(self,data):
  with self.lock:
   if not isinstance(data,dict) or set(data)!={'request_id','character_id','expected_revision','catalog_version','body_id','equipment'}:raise ValueError('Loadout requires request_id, character_id, expected_revision, catalog_version, body_id and equipment')
   request_id=data['request_id']
   if not isinstance(request_id,str) or not 1<=len(request_id)<=128:raise ValueError('A nonempty request_id is required')
   for prior in self.state['loadout_receipts']:
    if prior['request_id']==request_id:
     if prior['request']!=data:raise ValueError('request_id was already used for a different loadout')
     return copy.deepcopy(prior)
   if self.running or self.pending:raise ValueError('Stop Steve and wait for the current presentation before applying equipment')
   value=self.preview_character({k:v for k,v in data.items() if k!='request_id'})['character']
   receipt=dict(outcome='loadout_applied',request_id=request_id,request=copy.deepcopy(data),character=copy.deepcopy(value),catalog_hash=character_rules.CATALOG_HASH)
   value['stats']=copy.deepcopy(self.state['character']['stats'])
   value=character_rules.project(value)
   receipt['character']=character_rules.public(value)
   # Character and idempotency receipt commit together in the authoritative snapshot.
   previous=copy.deepcopy(self.state)
   self.state['character']=value;self.state['loadout_receipts']=(self.state['loadout_receipts']+[receipt])[-128:];self.state['observation_seq']+=1
   try:self.save()
   except OSError:self.state=previous;raise
   self._log(dict(kind='loadout_applied',**receipt));return copy.deepcopy(receipt)
 def preview_character(self,data):
  with self.lock:
   if not isinstance(data,dict) or set(data)!={'character_id','expected_revision','catalog_version','body_id','equipment'}:raise ValueError('Preview requires character_id, expected_revision, catalog_version, body_id and equipment')
   old=self.state['character']
   if data['character_id']!='steve':raise ValueError('Unknown character_id')
   if type(data['expected_revision']) is not int or data['expected_revision']!=old['revision']:raise ValueError('Stale loadout revision; current revision is '+str(old['revision'])+'. Refresh and review before applying.')
   if data['catalog_version']!=character_rules.CATALOG['version']:raise ValueError('Equipment catalog mismatch; reload the current catalog')
   equipment,capabilities=character_rules.validate(data['body_id'],data['equipment'])
   value=dict(copy.deepcopy(old),revision=old['revision']+1,catalog_version=character_rules.CATALOG['version'],body_id=data['body_id'],equipment=equipment,capabilities=capabilities)
   return dict(preview=True,expected_revision=old['revision'],character=character_rules.public(character_rules.project(value)),catalog_hash=character_rules.CATALOG_HASH)
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
    previous_state=copy.deepcopy(self.state);relocation=None
    self.state['world_definition']=definition
    if changed or not self.state.get('training_targets'):self.state['training_targets']=training_targets.from_manifest(definition,self.state.get('training_targets',[]))
    a=self.state['avatar'];blocked={(o['col'],o['row']) for o in expand_obstacles(definition)}
    spawn_changed=bool(old and old.get('spawn')!=definition.get('spawn'))
    if spawn_changed or (a['col'],a['row']) in blocked or not (1<=a['col']<=definition['columns'] and 1<=a['row']<=definition['rows']):
     previous=copy.deepcopy(a);a.update(definition.get('spawn',dict(col=5,row=5)));self.state['world_revision']+=1
     relocation=dict(kind='world_change_relocation',position_before=previous,position_after=copy.deepcopy(a),reason="Operator changed Steve's authored start" if spawn_changed else 'Previous cell is not occupiable in the new Unity world')
    self.state.pop('targets',None);self.state.pop('landmarks_version',None)
    self.state['observation_seq']+=1
    if changed:self.state['world_revision']+=1
    try:self.save()
    except OSError:self.state=previous_state;raise
    if relocation:self._log(relocation)
    self._log(dict(kind='world_definition_registered',source='unity_environment',manifest_hash=digest,definition=definition,session_id=self.state['session_id'],world_revision=self.state['world_revision']))
   self.definition_confirmed=True;self.presenter=client;self.last_poll=self.clock()
   return self.observe()
 def save(self):
  write_json(self.path,self.state)
 def observe(self):
  with self.lock:
   a=self.state['avatar'];definition=self.state.get('world_definition');targets=definition['landmarks'] if definition and self.definition_confirmed else [];locations={(t['col'],t['row']):t['id'] for t in targets}
   columns=definition['columns'] if definition else 10;rows=definition['rows'] if definition else 10
   catalog={c['prototype']:c for c in definition.get('catalog',[])} if definition else {}
   named=lambda items:[dict(i,name=catalog[i['prototype']]['name'],role=catalog[i['prototype']]['role']) if i.get('prototype') in catalog else dict(i) for i in items]
   live=bool(definition and self.definition_confirmed)
   obstacles=named(expand_obstacles(definition)) if live else [];blocked={(o['col'],o['row']):o['id'] for o in obstacles}
   hazards=[i for i in named(definition.get('props',[])) if i.get('role')=='hazard'] if live else [];hazardous={(h['col'],h['row']):h['id'] for h in hazards}
   labels={o['id']:o.get('name') for o in obstacles+hazards}
   def neighbour(d):
    c=(a['col']+d[0],a['row']+d[1])
    if not (1<=c[0]<=columns and 1<=c[1]<=rows):return dict(terrain='board_edge',target=None)
    if c in blocked:return dict(terrain='obstacle',target=locations.get(c),**({'feature':labels[blocked[c]]} if labels.get(blocked[c]) else {}))
    if c in hazardous:return dict(terrain='hazard',target=locations.get(c),**({'feature':labels[hazardous[c]]} if labels.get(hazardous[c]) else {}))
    return dict(terrain='open_floor',target=locations.get(c))
   adjacent={n[5:]:neighbour(d) for n,d in DIRECTIONS.items()}
   standing=[t['id'] for t in targets if (a['col'],a['row'])==(t['col'],t['row'])]
   state={k:copy.deepcopy(v) for k,v in self.state.items() if k not in ('targets','landmarks_version','world_definition','loadout_receipts','last_committed_action','character_migrations')}
   state['character']=character_rules.public(state['character'])
   if not definition:digest=''
   elif self._digest and self._digest[0] is definition:digest=self._digest[1]
   else:digest=validate_manifest(definition)[1];self._digest=(definition,digest)
   provenance=dict(source='unity_environment',world_id=self.state['world_id'],revision=definition['revision'] if definition else None,manifest_hash=digest,status='confirmed' if self.world_ready else 'disconnected' if self.definition_confirmed else 'awaiting_unity_manifest')
   return dict(schema=SCHEMA,**state,world_ready=self.world_ready,world_manifest_hash=digest,world_definition=provenance,observation_id=f"{self.state['session_id']}:obs-{self.state['observation_seq']:04}",self=copy.deepcopy(a),board=dict(columns=columns,rows=rows,north='row+1',east='col+1'),visible_targets=copy.deepcopy(targets),visible_obstacles=copy.deepcopy(obstacles),visible_hazards=copy.deepcopy(hazards),hazard_here=hazardous.get((a['col'],a['row'])),surroundings=adjacent,standing_on=standing,last_action=copy.deepcopy(self.last_action),available_tools=[*DIRECTIONS,COMPLETE,*self.state['character']['capabilities']],enabled=self.enabled,running=self.running,decision_loop=dict(active=self.running,origin_request_id=self.loop_origin,pause_reason=self.pause_reason),presentation=copy.deepcopy(self.pending))
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
   previous_state=copy.deepcopy(self.state);previous_pending=copy.deepcopy(self.pending);previous_last=self.last_action;turn_was_used=turn in self.used_turns
   before=copy.deepcopy(self.state['avatar']);actual=self.observe();outcome=force_reject;decision='DENY';why='';after=copy.deepcopy(before)
   combat={}
   if not outcome:
    if name not in (*DIRECTIONS,COMPLETE,*character_rules.ACTIONS) or (name in (*DIRECTIONS,COMPLETE) and args!={}):outcome='rejected_schema'
    elif turn in self.used_turns:outcome='rejected_duplicate'
    elif observation!=actual['observation_id']:outcome='rejected_stale'
    elif self.pending:outcome='rejected_busy'
    elif name!=COMPLETE and not self.world_ready:outcome='offline'
    elif name in character_rules.ACTIONS and name not in self.state['character']['capabilities']:outcome='rejected_unequipped';why='This action is not granted by the confirmed loadout'
    else:
     # Extension point for Warden. A denial cannot modify state. No intent claim is made here.
     admitted=True
     if self.authorizer:
      try:admitted,why=self.authorizer(dict(what='decision_loop/steve' if name==COMPLETE else 'avatars/steve',verb=name,args=args,turn_id=turn,observation_id=observation),copy.deepcopy(self.state))
      except Exception as e:admitted=False;why='Governance error: '+str(e)
     if not admitted:outcome='denied_governance'
     else:
      decision='ACCEPT'
      if name==COMPLETE:self.running=False;self.pause_reason='complete';outcome='interaction_complete'
      elif name in character_rules.ACTIONS:
       try:character_rules.validate_action(name,json.dumps(args))
       except (ValueError,TypeError):outcome='rejected_schema';decision='DENY'
       else:
        target=next((e for e in self.state['training_targets'] if e['id']==args['target_id']),None)
        effect=combat_rules.resolve_attack(name,character_rules.ability(self.state['character'],name),before,target,{(o['col'],o['row']) for o in actual['visible_obstacles']})
        outcome=effect['outcome'];decision=effect['decision'];why=effect['reason'];after=effect['position_after'];combat=effect['combat']
        if combat:target['hp']=combat['target_hp_after']
      else:
       dx,dy=DIRECTIONS[name];col=before['col']+dx;row=before['row']+dy;after['facing']=name[5:]
       if not (1<=col<=actual['board']['columns'] and 1<=row<=actual['board']['rows']):outcome='blocked_boundary'
       elif any((o['col'],o['row'])==(col,row) for o in actual['visible_obstacles']):outcome='blocked_obstacle'
       else:after.update(col=col,row=row);outcome='moved'
   self.used_turns.add(turn);self.state['observation_seq']+=1
   if after!=before or combat:self.state['avatar']=after;self.state['world_revision']+=1
   if outcome in ('moved','blocked_boundary','blocked_obstacle','target_hit'):self.state['game_tick']+=1
   receipt=dict(action_id='act-'+uuid.uuid4().hex,call_id=call_id,turn_id=turn,session_id=self.state['session_id'],observation_id=observation,action=str(name)[:64],decision=decision,decision_basis=why or outcome,outcome=outcome,position_before=[before['col'],before['row']],position_after=[after['col'],after['row']],facing_before=before['facing'],facing_after=after['facing'],world_revision=self.state['world_revision'],observation_seq=self.state['observation_seq'],presentation_status='not_required')
   receipt.update(combat,game_tick=self.state['game_tick'],loadout_revision=self.state['character']['revision'])
   if outcome in ('moved','blocked_boundary','blocked_obstacle','target_hit'):
    receipt['presentation_status']='pending';self.pending=copy.deepcopy(receipt)
   self.state['last_committed_action']=copy.deepcopy(receipt);self.last_action=receipt;self.receipts.append(receipt)
   try:self.save()
   except OSError:
    self.state=previous_state;self.pending=previous_pending;self.last_action=previous_last;self.receipts.pop()
    if not turn_was_used:self.used_turns.discard(turn)
    raise
   self._log(receipt);return copy.deepcopy(receipt)
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
  state=self.world.observe();fields=('schema','session_id','observation_id','observation_seq','world_revision','world_ready','world_definition','self','board','visible_targets','visible_obstacles','visible_hazards','hazard_here','surroundings','standing_on','last_action','available_tools','enabled','decision_loop','character','game_tick','training_targets')
  perceived={k:state[k] for k in fields}
  for key in ('visible_obstacles','visible_hazards','training_targets'):perceived[key]=world_perception.entities(state,key)
  return dict(observation=dict(world=perceived),state_source='deterministic_grid')
 def submit(self,target,call_id=None,tool=None):
  r=self.world.nominate(tool,target,self.turn,self.bound,call_id);self.local[call_id]=r['action_id'];return call_id
 def reject(self,tool,args,call_id,reason):
  r=self.world.nominate(tool,args,self.turn,self.bound,call_id,reason);return self.world.wait(r['action_id'])
 def wait(self,key):return self.world.wait(self.local.pop(key))
