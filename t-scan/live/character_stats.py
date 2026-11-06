"""Character-owned attributes/resources and read-only projections. No world or agent dependencies."""
import copy

SCHEMA='steve-character-stats-v1'
RESOURCE_RULES_VERSION='steve-resources-v2-con-hp'
ATTRIBUTES=('STR','DEX','INT','WIS','CON')

def initial():
 return dict(schema=SCHEMA,revision=1,level=1,base={k:1 for k in ATTRIBUTES},level_gains={k:0 for k in ATTRIBUTES},resources={k:dict(current=10,maximum=10) for k in ('hp','mp')})

def validate(stats):
 if not isinstance(stats,dict) or stats.get('schema')!=SCHEMA:raise ValueError('Unsupported character stats schema')
 for key in ('revision','level'):
  if type(stats.get(key)) is not int or not 1<=stats[key]<=1000000:raise ValueError('Invalid character '+key)
 for key,minimum in (('base',1),('level_gains',0)):
  values=stats.get(key)
  if not isinstance(values,dict) or set(values)!=set(ATTRIBUTES) or any(type(n) is not int or not minimum<=n<=1000000 for n in values.values()):raise ValueError('Invalid character '+key)
 for key in ('hp','mp'):
  value=stats.get('resources',{}).get(key)
  if not isinstance(value,dict) or set(value)!={'current','maximum'} or any(type(n) is not int for n in value.values()) or not 0<=value['current']<=value['maximum']<=1000000000 or value['maximum']<1:raise ValueError('Invalid character '+key+' resource')

def sheet(character,modules):
 stats=character['stats'];validate(stats);bonuses={k:0 for k in ATTRIBUTES}
 for assignment in character['equipment']:
  for modifier in modules[assignment['module_id']].get('stat_modifiers',[]):bonuses[modifier['stat']]+=modifier['amount']
 attributes=[dict(id=k,base_value=stats['base'][k],level_bonus=stats['level_gains'][k],equipment_bonus=bonuses[k],temporary_bonus=0,effective=max(1,stats['base'][k]+stats['level_gains'][k]+bonuses[k])) for k in ATTRIBUTES]
 resources=copy.deepcopy(stats['resources'])
 con=next(a['effective'] for a in attributes if a['id']=='CON')
 resources['hp']['maximum']=10+con-1
 resources['hp']['current']=min(resources['hp']['current'],resources['hp']['maximum'])
 return dict(revision=stats['revision']+character['revision'],schema=SCHEMA,resource_rules_version=RESOURCE_RULES_VERSION,level=stats['level'],attributes=attributes,**resources)
