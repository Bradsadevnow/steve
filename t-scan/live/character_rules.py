"""Trusted equipment definitions and pure validation. No visual or Self claims grant capabilities."""
import copy, hashlib, json
from pathlib import Path
import character_stats,combat_rules

CATALOG=json.loads(Path(__file__).with_name('character_catalog.json').read_text(encoding='utf-8'))
CATALOG_HASH=hashlib.sha256(json.dumps(CATALOG,sort_keys=True,separators=(',',':')).encode()).hexdigest()
BODIES={b['id']:b for b in CATALOG['bodies']}
MODULES={m['id']:m for m in CATALOG['modules']}
MECHANICS=json.loads(Path(__file__).with_name('character_mechanics.json').read_text(encoding='utf-8'))
RULES_VERSION=MECHANICS['rules_version']
ACTIONS={a['id']:a for module in MODULES.values() for a in module.get('abilities',[])}
if CATALOG['version']!=MECHANICS['version'] or set(ACTIONS)!={'slash','shield_bash'}:raise ValueError('Equipment mechanics/catalog mismatch; regenerate the local catalog')
for module_id,definition in MECHANICS['modules'].items():
 if any(MODULES[module_id].get(k)!=v for k,v in definition.items()):raise ValueError('Stale module mechanics: '+module_id)
for definition in ACTIONS.values():
 if definition['stat'] not in character_stats.ATTRIBUTES or any(type(definition[k]) is not int or definition[k]<1 for k in ('numerator','denominator','minimum','reach')):raise ValueError('Invalid trusted ability curve')

def initial():
 return project(dict(character_id='steve',revision=0,catalog_version=CATALOG['version'],body_id='hover',equipment=[],capabilities=[],stats=character_stats.initial()))

def project(character):
 value=copy.deepcopy(character);value['sheet']=character_stats.sheet(value,MODULES)
 # Commit resource clamps into the owned copy: re-equipping must never restore hidden HP.
 resources={k:copy.deepcopy(value['sheet'][k]) for k in ('hp','mp')}
 if value['stats']['resources']!=resources:
  value['stats']['resources']=resources;value['stats']['revision']+=1
  value['sheet']=character_stats.sheet(value,MODULES)
 value['sheet']['rules_version']=RULES_VERSION
 value['sheet']['abilities']=[combat_rules.evaluate(ACTIONS[name],value['sheet'],RULES_VERSION) for name in value['capabilities']]
 return value

def migrate(character):
 value=copy.deepcopy(character);changed='stats' not in value or value.get('catalog_version')!=CATALOG['version']
 if value.get('catalog_version') not in ('steve-equipment-v1',CATALOG['version']):raise ValueError('Unsupported saved equipment catalog; refusing to discard character state')
 equipment,capabilities=validate(value['body_id'],value['equipment'])
 if 'stats' not in value:value['stats']=character_stats.initial()
 value.update(equipment=equipment,capabilities=capabilities,catalog_version=CATALOG['version'])
 projected=project(value)
 changed=changed or projected['stats']!=value['stats']
 if changed:projected['revision']+=1
 return project(projected),changed

def ability(character,name):
 # Rebuild from character-owned source state, never a client/model supplied damage value or stale projection.
 value=project(character)
 return next(a for a in value['sheet']['abilities'] if a['id']==name)

def public(character):
 value=copy.deepcopy(character);value.pop('stats',None)
 return value

def validate(body_id,equipment):
 if not isinstance(body_id,str) or body_id not in BODIES:raise ValueError('Unknown body: '+str(body_id))
 if not isinstance(equipment,list) or len(equipment)>16:raise ValueError('Equipment must be a list of at most 16 module assignments')
 body=BODIES[body_id];sockets={s['id']:s for s in body['sockets']};occupied=set();resolved=[];actions=set()
 for assignment in equipment:
  if not isinstance(assignment,dict) or set(assignment)!={'socket_id','module_id'}:raise ValueError('Each assignment requires exactly socket_id and module_id')
  slot=assignment['socket_id']
  if not isinstance(slot,str) or not isinstance(assignment['module_id'],str):raise ValueError('socket_id and module_id must be strings')
  module=MODULES.get(assignment['module_id'])
  if slot not in sockets:raise ValueError('Body '+body_id+' has no socket '+str(slot)+'. Remove or remap that module.')
  if module is None:raise ValueError('Unknown module: '+str(assignment['module_id']))
  if sockets[slot]['type'] not in module['mount_types']:raise ValueError(module['name']+' is incompatible with '+slot)
  sites=[slot]
  if module['slots']==2:
   partner=next((p['secondary'] for p in body['pairs'] if p['primary']==slot),None)
   if partner is None:raise ValueError(module['name']+' needs a supported two-mount pair; choose its primary socket')
   sites.append(partner)
  if occupied.intersection(sites):raise ValueError('Mount conflict at '+', '.join(sorted(occupied.intersection(sites)))+'. Unequip the conflicting module first.')
  occupied.update(sites);resolved.append(dict(socket_id=slot,module_id=module['id']));actions.update(module['actions'])
 return sorted(resolved,key=lambda a:a['socket_id']),sorted(actions)

def tools(capabilities):
 return [dict(type='function',function=dict(name=name,description=ACTIONS[name]['targeting']+' Read evaluated damage, reach and physically valid target IDs in CURRENT CHARACTER. Requires confirmed equipment; one admitted attack advances game time by one tick.',parameters=dict(type='object',properties=dict(target_id=dict(type='string',description='Measured target ID from TRAINING TARGETS')),required=['target_id'],additionalProperties=False))) for name in sorted(set(capabilities)&ACTIONS.keys())]

def validate_action(name,text):
 value=json.loads(text)
 if not isinstance(value,dict) or set(value)!={'target_id'} or not isinstance(value['target_id'],str) or not 1<=len(value['target_id'])<=64:raise ValueError(name+' requires exactly a nonempty target_id from current observations')
 return dict(tool=name,**value)
