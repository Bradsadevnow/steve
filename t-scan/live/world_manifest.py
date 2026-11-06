"""Validate Unity-authored world data. No production landmark or obstacle layout lives here."""
import hashlib,json,re
from collections import deque

SCHEMA='meadow-world-v1'
V2='meadow-world-v2'
V3='meadow-world-v3'
IDENT=re.compile(r'[a-zA-Z0-9_-]{1,64}')
YAWS=(0,90,180,270)
# What a role MEANS is decided here, never by the manifest. blocks: the blocking the role requires (None = either).
# layer: which manifest list may hold a piece of this role. A piece's role is assigned once, in the catalog, and the
# placement lists below must agree with it: a floor cannot be placed as a wall, a wall cannot be decor.
ROLES={
 'floor':dict(layer='floor',blocks=False),
 'wall':dict(layer='object',blocks=True),
 'obstacle':dict(layer='object',blocks=True),
 'structure':dict(layer='either',blocks=None),   # doors block; archways and stairs do not
 'hazard':dict(layer='prop',blocks=False),       # walkable, flagged for later mechanics
 'decor':dict(layer='prop',blocks=False),       # cosmetic only
 'actor':dict(layer='object',blocks=True)}       # enemies and bosses: static, blocking, may cover 1 or 3 cells square (catalog footprint)
FOOTPRINTS=(1,3)

def _cell(item,size,what):
 if any(type(item[k]) is not int or not 1<=item[k]<=size for k in ('col','row')):raise ValueError(what+' outside the meadow')
 return (item['col'],item['row'])

def _reachable(start,blocked,size):
 seen={start};queue=deque([start])
 while queue:
  c,r=queue.popleft()
  for dc,dr in ((1,0),(-1,0),(0,1),(0,-1)):
   nxt=(c+dc,r+dr)
   if 1<=nxt[0]<=size and 1<=nxt[1]<=size and nxt not in blocked and nxt not in seen:seen.add(nxt);queue.append(nxt)
 return seen

def _catalog(value):
 if not isinstance(value,list) or not 1<=len(value)<=400:raise ValueError('Invalid asset catalog')
 table={}
 for item in value:
  if not isinstance(item,dict) or set(item) not in ({'prototype','name','role','blocks'},{'prototype','name','role','blocks','footprint'}):raise ValueError('Invalid catalog entry fields')
  if not isinstance(item['prototype'],str) or not IDENT.fullmatch(item['prototype']) or item['prototype'] in table:raise ValueError('Catalog prototypes must be unique stable identifiers')
  if not isinstance(item['name'],str) or not 1<=len(item['name'])<=100:raise ValueError('Invalid catalog name')
  rule=ROLES.get(item['role'])
  if rule is None:raise ValueError('Catalog role '+json.dumps(item['role'])+' is not a placeable role; expected one of '+', '.join(ROLES))
  if type(item['blocks']) is not bool or (rule['blocks'] is not None and item['blocks']!=rule['blocks']):
   raise ValueError('Catalog piece '+item['prototype']+' is a '+item['role']+' so it '+('must' if rule['blocks'] else 'cannot')+' block movement')
  if 'footprint' in item and (type(item['footprint']) is not int or item['footprint'] not in FOOTPRINTS or (item['footprint']>1 and item['role']!='actor')):
   raise ValueError('Catalog piece '+item['prototype']+' has an unsupported footprint; only actors may cover 3 x 3 cells')
  table[item['prototype']]=dict(item)
 return table

def _placements(items,table,size,what,allowed,ids,spawn,landmark_cells):
 placed={};result=[]
 if not isinstance(items,list) or len(items)>size*size:raise ValueError('Invalid '+what)
 for item in items:
  if not isinstance(item,dict) or set(item)!={'id','prototype','col','row','yaw'}:raise ValueError('Invalid '+what+' fields')
  if not isinstance(item['id'],str) or not IDENT.fullmatch(item['id']) or item['id'] in ids:raise ValueError('Placement IDs must be unique stable identifiers')
  if item['yaw'] not in YAWS or type(item['yaw']) is not int:raise ValueError('Placement yaw must be 0, 90, 180 or 270')
  piece=table.get(item['prototype'])
  if piece is None:raise ValueError(what+' '+item['id']+' uses a prototype that is not in the catalog')
  if not allowed(piece):raise ValueError(what+' '+item['id']+': '+piece['name']+' is a '+piece['role']+' and cannot be placed there')
  cell=_cell(item,size,what[:1].upper()+what[1:])
  if cell in placed:raise ValueError('Only one piece of this kind may occupy a cell: '+item['id']+' overlaps '+placed[cell])
  ids.add(item['id']);placed[cell]=item['id'];result.append(dict(item))
 return placed,sorted(result,key=lambda item:item['id'])

def _validate_v3(value):
 size=15
 fields={'schema','world_id','revision','columns','rows','landmarks','spawn','obstacles','floors','props','catalog'}
 if set(value)!=fields:raise ValueError('Expected a complete Unity world manifest')
 if value['world_id']!='steve_grid_v1':raise ValueError('Unsupported world identity or schema')
 if type(value['revision']) is not int or value['revision']<1:raise ValueError('World revision must be a positive integer')
 if type(value['columns']) is not int or type(value['rows']) is not int or (value['columns'],value['rows'])!=(size,size):raise ValueError('World dimensions do not match the meadow schema')
 table=_catalog(value['catalog'])
 ids=set();landmark_cells={};landmarks=[]
 if not isinstance(value['landmarks'],list) or len(value['landmarks'])>100:raise ValueError('Invalid landmarks')
 for item in value['landmarks']:
  if not isinstance(item,dict) or set(item)!={'id','name','kind','color','col','row','occupiable'}:raise ValueError('Invalid landmark fields')
  if not isinstance(item['id'],str) or not IDENT.fullmatch(item['id']) or item['id'] in ids:raise ValueError('Landmark IDs must be unique stable identifiers')
  if not isinstance(item['name'],str) or not 1<=len(item['name'])<=100:raise ValueError('Invalid landmark name')
  if item['kind']!='flag' or item['color'] not in ('blue','red','yellow','purple','orange') or item['occupiable'] is not True:raise ValueError('Unsupported landmark interaction metadata')
  cell=_cell(item,size,'Landmark')
  if cell in landmark_cells:raise ValueError('Only one landmark may occupy each cell')
  ids.add(item['id']);landmark_cells[cell]=item['id'];landmarks.append(dict(item))
 spawn=value['spawn']
 if not isinstance(spawn,dict) or set(spawn)!={'col','row'}:raise ValueError('Invalid world spawn')
 spawn_cell=_cell(spawn,size,'Spawn')
 floors=value['floors']
 if not isinstance(floors,list) or len(floors)!=size*size:raise ValueError('floors must list one floor piece for each of the %d cells, row by row from (1,1)'%(size*size))
 for number,proto in enumerate(floors):
  piece=table.get(proto) if isinstance(proto,str) else None
  if piece is None or piece['role']!='floor':raise ValueError('Cell (%d,%d) has %s as its floor, which is not a floor piece'%(number%size+1,number//size+1,json.dumps(proto)[:60]))
 blocking,obstacles=_placements(value['obstacles'],table,size,'obstacle',lambda p:p['blocks'] and p['role'] in ('wall','obstacle','structure','actor'),ids,spawn_cell,landmark_cells)
 occupied={}
 for o in obstacles:
  half=table[o['prototype']].get('footprint',1)//2
  for dc in range(-half,half+1):
   for dr in range(-half,half+1):
    covered=(o['col']+dc,o['row']+dr)
    if not (1<=covered[0]<=size and 1<=covered[1]<=size):raise ValueError('Obstacle '+o['id']+' ('+table[o['prototype']]['name']+') extends past the edge of the meadow')
    if covered in occupied:raise ValueError('Obstacle '+o['id']+' overlaps '+occupied[covered])
    occupied[covered]=o['id']
 blocking=occupied
 props_placed,props=_placements(value['props'],table,size,'prop',lambda p:(not p['blocks']) and p['role'] in ('hazard','decor','structure'),ids,spawn_cell,landmark_cells)
 for cell,name in blocking.items():
  if cell==spawn_cell or cell in landmark_cells:raise ValueError('Obstacle '+name+' must not overlap the spawn or a landmark')
  if cell in props_placed:raise ValueError('Prop '+props_placed[cell]+' sits inside blocking obstacle '+name)
 by_id={p['id']:p for p in props}
 for cell,name in props_placed.items():
  if table[by_id[name]['prototype']]['role']=='hazard' and (cell==spawn_cell or cell in landmark_cells):raise ValueError('Hazard '+name+' must not sit on the spawn or a landmark')
 used={*floors,*(o['prototype'] for o in obstacles),*(p['prototype'] for p in props)}
 if used!=set(table):raise ValueError('The catalog must list exactly the pieces in use; unused: '+', '.join(sorted(set(table)-used))+' missing: '+', '.join(sorted(used-set(table))))
 reachable=_reachable(spawn_cell,set(blocking),size)
 for cell,name in landmark_cells.items():
  if cell not in reachable:raise ValueError('Landmark '+name+' cannot be reached from the spawn without crossing an obstacle')
 result=dict(value,landmarks=sorted(landmarks,key=lambda item:item['id']),obstacles=obstacles,props=props,catalog=sorted((dict(c) for c in table.values()),key=lambda item:item['prototype']))
 return result

def expand_obstacles(definition):
 """One entry per blocked cell. Pieces with a larger footprint cover every cell around their anchor; all share the anchor's id."""
 catalog={c['prototype']:c for c in definition.get('catalog',[])}
 out=[]
 for o in definition.get('obstacles',[]):
  half=catalog.get(o.get('prototype'),{}).get('footprint',1)//2
  for dc in range(-half,half+1):
   for dr in range(-half,half+1):out.append(o if not half else dict(o,col=o['col']+dc,row=o['row']+dr))
 return out

def validate_manifest(value):
 if not isinstance(value,dict):raise ValueError('Expected a complete Unity world manifest')
 if value.get('schema')==V3:
  result=_validate_v3(value)
  return result,hashlib.sha256(json.dumps(result,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()
 course=value.get('schema')==V2
 fields={'schema','world_id','revision','columns','rows','landmarks'} | ({'spawn','obstacles'} if course else set())
 if set(value)!=fields:
  raise ValueError('Expected a complete Unity world manifest')
 if value['schema'] not in (SCHEMA,V2) or value['world_id']!='steve_grid_v1':raise ValueError('Unsupported world identity or schema')
 if type(value['revision']) is not int or value['revision']<1:raise ValueError('World revision must be a positive integer')
 size=15 if course else 10
 if type(value['columns']) is not int or type(value['rows']) is not int or (value['columns'],value['rows'])!=(size,size):
  raise ValueError('World dimensions do not match the meadow schema')
 if not isinstance(value['landmarks'],list) or len(value['landmarks'])>100:raise ValueError('Invalid landmarks')
 ids=set();cells=set();landmarks=[]
 for item in value['landmarks']:
  if not isinstance(item,dict) or set(item)!={'id','name','kind','color','col','row','occupiable'}:raise ValueError('Invalid landmark fields')
  if not isinstance(item['id'],str) or not re.fullmatch(r'[a-zA-Z0-9_-]{1,64}',item['id']) or item['id'] in ids:raise ValueError('Landmark IDs must be unique stable identifiers')
  if not isinstance(item['name'],str) or not 1<=len(item['name'])<=100:raise ValueError('Invalid landmark name')
  if item['kind']!='flag' or item['color'] not in ('blue','red','yellow','purple','orange') or item['occupiable'] is not True:raise ValueError('Unsupported landmark interaction metadata')
  if any(type(item[k]) is not int or not 1<=item[k]<=size for k in ('col','row')):raise ValueError('Landmark outside the meadow')
  cell=(item['col'],item['row'])
  if cell in cells:raise ValueError('Only one landmark may occupy each cell')
  ids.add(item['id']);cells.add(cell);landmarks.append(dict(item))
 result=dict(value,landmarks=sorted(landmarks,key=lambda item:item['id']))
 if course:
  spawn=value['spawn']
  if not isinstance(spawn,dict) or set(spawn)!={'col','row'} or any(type(spawn[k]) is not int or not 1<=spawn[k]<=size for k in ('col','row')):raise ValueError('Invalid world spawn')
  if not isinstance(value['obstacles'],list) or len(value['obstacles'])>225:raise ValueError('Invalid obstacles')
  blocked=set();obstacles=[]
  for item in value['obstacles']:
   if not isinstance(item,dict) or set(item)!={'id','prototype','col','row'}:raise ValueError('Invalid obstacle fields')
   if not isinstance(item['id'],str) or not re.fullmatch(r'[a-zA-Z0-9_-]{1,64}',item['id']) or item['id'] in ids:raise ValueError('Obstacle IDs must be unique')
   if item['prototype'] not in ('stone_wall','wood_hurdle','boulder_cluster','hedge'):raise ValueError('Unknown obstacle prototype')
   if any(type(item[k]) is not int or not 1<=item[k]<=size for k in ('col','row')):raise ValueError('Obstacle outside the meadow')
   cell=(item['col'],item['row'])
   if cell in blocked or cell in cells or cell==(spawn['col'],spawn['row']):raise ValueError('Obstacles must not overlap landmarks, spawn or each other')
   blocked.add(cell);ids.add(item['id']);obstacles.append(dict(item))
  result['obstacles']=sorted(obstacles,key=lambda item:item['id'])
 digest=hashlib.sha256(json.dumps(result,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()
 return result,digest
