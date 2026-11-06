"""Blender geometry export only; placement belongs to the Unity world asset."""
import bpy,json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(root/'environments/meadow_course_001/meadow_course_001.blend'))
def part(key,objects):
 v=[];n=[];c=[];t=[]
 for o in objects:
  mesh=o.data;mesh.calc_loop_triangles()
  for tri in mesh.loop_triangles:
   start=len(v)//3
   for index in tri.vertices:
    p=mesh.vertices[index].co;normal=tri.normal
    if key=='ground':p=o.matrix_world@p
    color=o.data.materials[tri.material_index].diffuse_color
    v.extend((p.x,p.z,p.y));n.extend((normal.x,normal.z,normal.y));c.extend(color)
   t.extend((start,start+2,start+1))
 return dict(name=key,key=key,vertices=v,normals=n,colors=c,triangles=t)
parts=[part(o.name,[o]) for o in bpy.data.collections['ASSETS - reusable originals'].objects]
scene=bpy.data.scenes['Course Preview - 15x15 - visual study']
ground=[o for o in scene.objects if o.type=='MESH' and o.name.startswith(('Grid x','Grid y','15 by 15','Flat meadow','Start tile'))]
parts.append(part('ground',ground))
out=root/'TScanViewer/Assets/Resources/Meadow/course.json'
out.write_text(json.dumps(dict(prototypes=parts),separators=(',',':')))
print('Exported',len(parts),'prototypes to',out)
