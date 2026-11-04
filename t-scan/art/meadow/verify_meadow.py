"""Inspect saved art and round-trip the exported kit through Blender's glTF importer."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'steve_meadow_001.blend'))
scene=bpy.data.scenes['Meadow_OpenField']
ground=bpy.data.collections['GROUND / 100 flat modules']
flat=all(abs((o.matrix_world@v.co).z)<1e-6 for o in ground.objects for v in o.data.vertices)
seams={}
for o in ground.objects:
 for v in o.data.vertices:
  p=o.matrix_world@v.co
  if abs(abs(v.co.x)-1)<1e-6 or abs(abs(v.co.y)-1)<1e-6:
   key=(round(p.x,5),round(p.y,5));col=tuple(o.data.color_attributes['Color'].data[v.index].color)
   if key in seams:assert max(abs(a-b) for a,b in zip(seams[key],col))<1e-5
   seams[key]=col
assert flat and len(ground.objects)==100
manifest=json.loads((ROOT/'manifest.json').read_text())
results=[]
for entry in manifest['assets']:
 bpy.ops.wm.read_factory_settings(use_empty=True)
 bpy.ops.import_scene.gltf(filepath=str(ROOT/entry['file']))
 meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
 assert meshes,entry['id']
 points=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
 minimum=[min(p[i] for p in points) for i in range(3)];maximum=[max(p[i] for p in points) for i in range(3)]
 assert all(math.isfinite(x) for p in points for x in p)
 assert all(len(o.data.color_attributes)>0 for o in meshes),entry['id']
 if entry['role']=='ground':
  assert abs(minimum[2])<1e-5 and abs(maximum[2])<1e-5
  assert abs(maximum[0]-minimum[0]-2)<1e-5 and abs(maximum[1]-minimum[1]-2)<1e-5
 assert minimum[2]>-.015,entry['id']
 results.append(dict(asset=entry['id'],meshes=len(meshes),bounds_min=minimum,bounds_max=maximum,vertex_colors=True))
proof=dict(passed=True,flat_surface=flat,tile_count=100,matching_tile_border_colors=True,roundtrip_assets=len(results),roundtrip=results)
(ROOT/'export_validation.json').write_text(json.dumps(proof,indent=2))
print('MEADOW_VERIFIED',json.dumps({k:v for k,v in proof.items() if k!='roundtrip'}))
