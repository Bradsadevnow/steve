"""Validate Unity-authored world data. No production landmark layout lives here."""
import hashlib,json,re

SCHEMA='meadow-world-v1'
def validate_manifest(value):
 if not isinstance(value,dict) or set(value)!={'schema','world_id','revision','columns','rows','landmarks'}:
  raise ValueError('Expected a complete Unity world manifest')
 if value['schema']!=SCHEMA or value['world_id']!='steve_grid_v1':raise ValueError('Unsupported world identity or schema')
 if type(value['revision']) is not int or value['revision']<1:raise ValueError('World revision must be a positive integer')
 if type(value['columns']) is not int or type(value['rows']) is not int or (value['columns'],value['rows'])!=(10,10):
  raise ValueError('This movement interface supports a 10 by 10 meadow')
 if not isinstance(value['landmarks'],list) or len(value['landmarks'])>100:raise ValueError('Invalid landmarks')
 ids=set();cells=set();landmarks=[]
 for item in value['landmarks']:
  if not isinstance(item,dict) or set(item)!={'id','name','kind','color','col','row','occupiable'}:raise ValueError('Invalid landmark fields')
  if not isinstance(item['id'],str) or not re.fullmatch(r'[a-zA-Z0-9_-]{1,64}',item['id']) or item['id'] in ids:raise ValueError('Landmark IDs must be unique stable identifiers')
  if not isinstance(item['name'],str) or not 1<=len(item['name'])<=100:raise ValueError('Invalid landmark name')
  if item['kind']!='flag' or item['color'] not in ('blue','red','yellow','purple','orange') or item['occupiable'] is not True:raise ValueError('Unsupported landmark interaction metadata')
  if any(type(item[k]) is not int or not 1<=item[k]<=10 for k in ('col','row')):raise ValueError('Landmark outside the meadow')
  cell=(item['col'],item['row'])
  if cell in cells:raise ValueError('Only one landmark may occupy each cell')
  ids.add(item['id']);cells.add(cell);landmarks.append(dict(item))
 result=dict(value,landmarks=sorted(landmarks,key=lambda item:item['id']))
 digest=hashlib.sha256(json.dumps(result,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()
 return result,digest
