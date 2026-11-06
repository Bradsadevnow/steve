"""Read-only combat cards. No routes, recommended actions or invented enemy stats."""
import json
import character_rules
import combat_rules
import world_perception

POLICY='combat-card-v1'

def quoted(value):
 return json.dumps(value,ensure_ascii=True).replace('<','\\u003c').replace('>','\\u003e')

def lines(world):
 character=world.get('character',{});sheet=character.get('sheet',{})
 if not character:return ['CURRENT CHARACTER / unavailable']
 attributes={a['id']:a['effective'] for a in sheet.get('attributes',[])}
 resource=lambda key:str(sheet.get(key,{}).get('current','?'))+'/'+str(sheet.get(key,{}).get('maximum','?'))
 result=['CURRENT CHARACTER / measured now; '+POLICY,'-'*40,
         'Level '+str(sheet.get('level','?'))+' | HP '+resource('hp')+' | MP '+resource('mp'),
         '    '.join(stat+' '+str(attributes.get(stat,'?')) for stat in character_rules.character_stats.ATTRIBUTES),
         'Loadout revision '+str(character.get('revision','?'))+' | Sheet revision '+str(sheet.get('revision','?')),
         '', 'EQUIPPED MODULES / grants come from these items']
 for item in character.get('equipment',[]):
  module=character_rules.MODULES.get(item['module_id'],{})
  modifiers=module.get('stat_modifiers',[])
  bonus='; '+', '.join(('+' if m['amount']>0 else '')+str(m['amount'])+' '+m['stat'] for m in modifiers) if modifiers else ''
  result.append(quoted(item['socket_id'])+': '+quoted(module.get('name',item['module_id']))+bonus)
 if not character.get('equipment'):result.append('None.')
 result+=['','EQUIPPED COMBAT ABILITIES / executor phase; current registry governs calls']
 targets=world.get('training_targets',[]);blocked={(o['col'],o['row']) for o in world.get('visible_obstacles',[])}
 for ability in sheet.get('abilities',[]):
  result.append(ability['id']+'(target_id): damage '+str(ability['damage'])+' | reach '+str(ability['reach'])+' cardinal cell(s)')
  result.append('  '+ability['targeting'])
  valid=[target['id'] for target in targets if combat_rules.resolve_attack(ability['id'],ability,world['self'],target,blocked)['decision']=='ACCEPT']
  result.append('  Physically valid target IDs now: '+quoted(valid))
 if not sheet.get('abilities'):result.append('None. No equipped combat actions.')
 result+=['','TRAINING TARGETS / measured now; passive, stationary, no retaliation','-'*40]
 for target in world_perception.entities(world,'training_targets'):
  result.append('id='+quoted(target['id'])+' | name='+quoted(target.get('name','Training target'))+' | x='+str(target['col'])+' y='+str(target['row'])+' | HP '+str(target['hp'])+'/'+str(target['max_hp'])+' | '+('alive' if target['hp']>0 else 'defeated')+' | blocks_cell='+str((target['col'],target['row']) in blocked).lower())
 if not targets:result.append('None observed.')
 result.append('Game tick: '+str(world.get('game_tick',0)))
 return result
