"""Measured agent-facing entity views. Asset prototype identifiers stay with world/presentation owners."""
def entities(world,key):
 names={e['id']:e['name'] for e in world.get('visible_obstacles',[]) if e.get('name')}
 result=[]
 for entity in world.get(key,[]):
  value={k:v for k,v in entity.items() if k!='prototype'}
  if key=='training_targets' and entity['id'] in names:value['name']=names[entity['id']]
  result.append(value)
 return result
