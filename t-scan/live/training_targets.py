"""Passive target instances owned by the world. No enemy progression is implied."""
import copy

PROTOTYPES=frozenset({'bosses_dummy_unarmed','bosses_dummy_melee','bosses_dummy_ranged'})

def from_manifest(definition,previous=()):
 """Preserve damage on unchanged instances; initialize new/replaced placements."""
 existing={(t['id'],t['prototype'],t['col'],t['row']):t for t in previous}
 targets=[]
 for placement in (definition or {}).get('obstacles',[]):
  if placement.get('prototype') not in PROTOTYPES:continue
  key=tuple(placement[k] for k in ('id','prototype','col','row'))
  target=existing.get(key)
  targets.append(copy.deepcopy(target) if target is not None else dict(zip(('id','prototype','col','row'),key),hp=10,max_hp=10))
 return targets
