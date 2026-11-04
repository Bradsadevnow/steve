"""Steve-owned original hover body, reusing an explicit copy of his established head."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
UNITY=ROOT.parents[2]/'TScanViewer/Assets/Resources/Meadow'
# art/hover -> t-scan -> workspace
UNITY=ROOT.parents[2]/'TScanViewer/Assets/Resources/Meadow'
UNITY.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
def mat(name,color,metal=0,emission=0):
 m=bpy.data.materials.new(name);m.diffuse_color=tuple(color);m.use_nodes=True;p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Base Color'].default_value=color;p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=.32
 if emission:p.inputs['Emission Color'].default_value=color;p.inputs['Emission Strength'].default_value=emission
 return m
cream=mat('Hover / warm cream',(.86,.83,.65,1));teal=mat('Hover / enamel teal',(.045,.31,.32,1),.25);gold=mat('Hover / brushed gold',(.62,.38,.1,1),.65);glow=mat('Hover / gentle levitation',(.14,.74,.63,1),.15,1.5)
head=json.loads((ROOT/'head_source.json').read_text())
for part in head['parts']:
 v=part['vertices'];vertices=[(v[i]*.85,v[i+2]*.85,v[i+1]*.85+1.15) for i in range(0,len(v),3)];tri=part['triangles'];faces=[(tri[i],tri[i+2],tri[i+1]) for i in range(0,len(tri),3)]
 mesh=bpy.data.meshes.new(part['name']);mesh.from_pydata(vertices,[],faces);mesh.update();ob=bpy.data.objects.new(part['name'],mesh);bpy.context.collection.objects.link(ob)
 color=part['color'];ob.data.materials.append(mat(part['name'],(color['r'],color['g'],color['b'],color['a'])))
 for p in mesh.polygons:p.use_smooth=True
def ellipsoid(name,location,scale,material):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=24,location=location);ob=bpy.context.object;ob.name=name;ob.scale=scale;ob.data.materials.append(material)
 for p in ob.data.polygons:p.use_smooth=True
 return ob
ellipsoid('POD / cream hull',(0,0,.56),(.67,.55,.32),cream)
ellipsoid('POD / teal skirt',(0,0,.37),(.69,.57,.14),teal)
ellipsoid('POD / soft underside light',(0,0,.29),(.53,.43,.065),glow)
ellipsoid('POD / neck collar',(0,0,.83),(.39,.35,.075),gold)
for i in range(3):ellipsoid('POD / gold front indicator '+str(i),((i-1)*.13,-.52,.55),(.032,.018,.032),gold if i!=1 else glow)
for side in (-1,1):ellipsoid('POD / side enamel '+str(side),(side*.6,0,.59),(.1,.32,.15),teal)
scene=bpy.context.scene;scene.name='STEVE / Hover Unicorn v0.1';scene.unit_settings.system='METRIC'
scene['project_owner']='Steve / t-scan';scene['head_source']='Explicit geometry copy from SteveUnicornTower prefab. No game/short assets.'
def export(objects,path):
 dg=bpy.context.evaluated_depsgraph_get();parts=[]
 for ob in objects:
  if ob.type!='MESH':continue
  ev=ob.evaluated_get(dg);mesh=ev.to_mesh();mesh.calc_loop_triangles();v=[];n=[];colors=[];tri=[]
  ca=mesh.color_attributes.get('Color');normal_matrix=ob.matrix_world.to_3x3().inverted().transposed()
  for face in mesh.loop_triangles:
   m=mesh.materials[face.material_index] if mesh.materials else None;color=m.diffuse_color if m else (.3,.5,.2,1)
   for li in (face.loops[0],face.loops[2],face.loops[1]):
    vi=mesh.loops[li].vertex_index;p=ob.matrix_world@mesh.vertices[vi].co;normal=(normal_matrix@mesh.corner_normals[li].vector).normalized()
    v.extend((p.x,p.z,p.y));n.extend((normal.x,normal.z,normal.y));colors.extend(tuple(ca.data[vi].color) if ca and ca.domain=='POINT' else tuple(color));tri.append(len(tri))
  parts.append(dict(name=ob.name,vertices=v,normals=n,colors=colors,triangles=tri));ev.to_mesh_clear()
 path.write_text(json.dumps(dict(parts=parts),separators=(',',':')))
export(list(scene.objects),UNITY/'hover.json')
# Authoring rig: rigid head and independent eye pivots; presentation remains engine-owned.
bpy.ops.object.armature_add();rig=bpy.context.object;rig.name='STEVE_HOVER_RIG';bpy.ops.object.mode_set(mode='EDIT')
root=rig.data.edit_bones[0];root.name='root';root.head=(0,0,.3);root.tail=(0,0,.8)
hb=rig.data.edit_bones.new('head');hb.head=(0,0,1.15);hb.tail=(0,0,1.7);hb.parent=root
for side,x in [('L',-.2),('R',.2)]:
 bone=rig.data.edit_bones.new('eye.'+side);bone.head=(x,-.3,1.2);bone.tail=(x,-.5,1.2);bone.parent=hb
bpy.ops.object.mode_set(mode='OBJECT');rig.show_in_front=True
for ob in list(scene.objects):
 if ob.type!='MESH':continue
 world_matrix=ob.matrix_world.copy();name=ob.name
 eye=any(word in name for word in ('iris','pupil','catchlight'))
 bone='eye.L' if eye and name.endswith('L') else 'eye.R' if eye and name.endswith('R') else 'root' if name.startswith('POD /') else 'head'
 ob.parent=rig;ob.parent_type='BONE';ob.parent_bone=bone;ob.matrix_world=world_matrix
# Add a simple Blender camera/light rig for the editable source and preview.
world=bpy.data.worlds.new('Hover / studio');world.use_nodes=True;world.node_tree.nodes.get('Background').inputs[0].default_value=(.12,.18,.19,1);world.node_tree.nodes.get('Background').inputs[1].default_value=.6;scene.world=world
for loc,power,size in [((-3,-4,5),550,4),((3,-2,3),350,3)]:
 bpy.ops.object.light_add(type='AREA',location=loc);ob=bpy.context.object;ob.data.energy=power;ob.data.shape='DISK';ob.data.size=size;ob.rotation_euler=(Vector((0,0,1))-ob.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(3,-5,2.6));camera=bpy.context.object;camera.rotation_euler=(Vector((0,0,1))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=3.2;scene.camera=camera
scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True;scene.render.resolution_x=1000;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'steve_hover_unicorn.blend'))
scene.render.filepath=str(ROOT/'hover_preview.png');bpy.ops.render.render(write_still=True)
# Explicit copy of the meadow's geometry to this project's Unity resource payload.
bpy.ops.wm.open_mainfile(filepath=str(ROOT.parent/'meadow/steve_meadow_001.blend'))
scene=bpy.data.scenes['Meadow_OpenField'];bpy.context.window.scene=scene
cols=['GROUND / 100 flat modules','DECORATION / nonblocking grass and flowers','PRESENTATION / soil edge and studio']
objects=[o for name in cols for o in bpy.data.collections[name].objects if o.type=='MESH' and o.name!='Studio floor']
prototypes={};instances=[]
for ob in objects:
 key=ob.data.name
 if key not in prototypes:
  # Prototype extraction in local coordinates keeps the payload compact.
  copy=ob.copy();copy.data=ob.data;bpy.context.collection.objects.link(copy);copy.matrix_world.identity();export([copy],UNITY/'prototype.tmp.json');prototypes[key]=json.loads((UNITY/'prototype.tmp.json').read_text())['parts'][0];bpy.data.objects.remove(copy,do_unlink=True)
 instances.append(dict(prototype=key,position=dict(x=ob.location.x,y=ob.location.z,z=ob.location.y),scale=dict(x=ob.scale.x,y=ob.scale.z,z=ob.scale.y),yaw=-math.degrees(ob.rotation_euler.z)))
(UNITY/'field.json').write_text(json.dumps(dict(prototypes=[dict(p,key=k) for k,p in prototypes.items()],instances=instances),separators=(',',':')))
(UNITY/'prototype.tmp.json').unlink()
print('HOVER_AND_MEADOW_EXPORTED',len(head['parts']),len(prototypes),len(instances))
