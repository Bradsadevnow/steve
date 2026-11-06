"""Pure engine evaluator for trusted module ability definitions. Never mutates actors or targets."""
def evaluate(definition,sheet,rules_version):
 stat=next(a['effective'] for a in sheet['attributes'] if a['id']==definition['stat'])
 damage=max(definition['minimum'],stat*definition['numerator']//definition['denominator'])
 return dict(definition,effective_stat=stat,damage=damage,rules_version=rules_version,stats_revision=sheet['revision'])

def resolve_attack(name,evaluated,actor,target,blocked_cells):
 """Return a proposed effect; the grid writer alone commits it or ticks time."""
 def reject(outcome,reason):return dict(outcome=outcome,decision='DENY',reason=reason,position_after=dict(actor),combat={})
 if target is None or target['hp']<=0:return reject('rejected_target','Choose a current living training target ID')
 dx=target['col']-actor['col'];dy=target['row']-actor['row'];distance=abs(dx)+abs(dy);reach=evaluated['reach']
 if (dx!=0 and dy!=0) or not 1<=distance<=reach:return reject('rejected_range','Target must be in a straight cardinal lane within '+str(reach)+' squares')
 sx=(dx>0)-(dx<0);sy=(dy>0)-(dy<0)
 if any((actor['col']+sx*i,actor['row']+sy*i) in blocked_cells for i in range(1,distance)):return reject('rejected_lane','The charge lane is blocked')
 after=dict(actor)
 if name=='shield_bash':after.update(col=target['col']-sx,row=target['row']-sy)
 after['facing']='east' if sx>0 else 'west' if sx<0 else 'north' if sy>0 else 'south'
 damage=min(target['hp'],evaluated['damage']);hp=target['hp']-damage
 combat=dict(target_id=target['id'],damage=damage,nominal_damage=evaluated['damage'],scaling_stat=evaluated['stat'],effective_stat=evaluated['effective_stat'],stats_revision=evaluated['stats_revision'],rules_version=evaluated['rules_version'],damage_curve={k:evaluated[k] for k in ('numerator','denominator','minimum')},target_hp_before=target['hp'],target_hp_after=hp,target_defeated=hp==0)
 return dict(outcome='target_hit',decision='ACCEPT',reason='',position_after=after,combat=combat)
