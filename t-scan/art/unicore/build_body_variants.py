"""Create isolated chassis concepts from the authored Uni-Core head; never overwrite the source."""
import bpy, math, json
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parent
OUT=BASE/'body_variants';OUT.mkdir(exist_ok=True)
source_head=list(bpy.data.collections['HEAD'].all_objects)
for c in list(bpy.context.scene.collection.children):bpy.context.scene.collection.children.unlink(c)
scene=bpy.context.scene
def mat(name,rgb,metal=.0,emission=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*rgb,1);m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*rgb,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=.36
 if emission:p.inputs['Emission Color'].default_value=(*rgb,1);p.inputs['Emission Strength'].default_value=emission
 return m
white=mat('Variant porcelain',(.76,.84,.80));teal=mat('Variant teal',(.035,.34,.36),.5);dark=mat('Variant joints',(.065,.10,.13),.55);gold=mat('Mount brass',(.72,.48,.15),.65);glow=mat('Mount mint',(.30,.94,.77),.15,2);lilac=mat('Variant lilac',(.43,.30,.58),.3)
def link(o,col,parent=None):
 for c in list(o.users_collection):c.objects.unlink(o)
 col.objects.link(o);o.parent=parent;return o
def cube(name,loc,size,material,col,parent):
 bpy.ops.mesh.primitive_cube_add(size=1,location=(0,0,0));o=link(bpy.context.object,col,parent);o.name=name;o.location=loc;o.scale=size
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 mod=o.modifiers.new('Soft corners','BEVEL');mod.width=.10;mod.segments=3;o.modifiers.new('Weighted normals','WEIGHTED_NORMAL');o.data.materials.append(material);return o
def ball(name,loc,size,material,col,parent):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=20);o=link(bpy.context.object,col,parent);o.name=name;o.location=loc;o.scale=size;o.data.materials.append(material)
 for p in o.data.polygons:p.use_smooth=True
 return o
def ring(name,loc,radius,material,col,parent,rot=(0,0,0)):
 bpy.ops.mesh.primitive_torus_add(major_radius=radius,minor_radius=.045,major_segments=36,minor_segments=10)
 o=link(bpy.context.object,col,parent);o.name=name;o.location=loc;o.rotation_euler=rot;o.data.materials.append(material);return o
def empty(name,col,parent,loc):
 o=bpy.data.objects.new(name,None);col.objects.link(o);o.parent=parent;o.location=loc;o.empty_display_type='ARROWS';o.empty_display_size=.22;return o
def head(col,root,loc,scale):
 hr=empty(col.name+' / HEAD_ROOT',col,root,loc);hr.scale=(scale,)*3
 inverse=bpy.data.objects['HEAD_ROOT'].matrix_world.inverted()
 for old in source_head:
  if old.type!='MESH':continue
  new=old.copy();col.objects.link(new);new.name=col.name+' / '+old.name;new.hide_render=False;new.hide_viewport=False
  new.parent=hr;new.matrix_parent_inverse.identity();new.matrix_basis=inverse @ old.matrix_world
def socket(col,root,specs,name,loc,kind,rot=(math.pi/2,0,0),size=.115):
 o=empty('SOCKET_'+name,col,root,loc);o['mount_type']=kind;o['socket_id']=name
 o.rotation_euler=rot
 ring('Visible mount / '+name,loc,size,gold,col,root,rot)
 specs.append(dict(id=name,type=kind,position=list(loc),rotation=list(rot)))
 return o
records=[];collections=[]
def chassis(id,title,x):
 col=bpy.data.collections.new(title);scene.collection.children.link(col);collections.append(col)
 root=empty('BODY_'+id,col,None,(x,0,0));root['body_id']=id;root['concept_only']=True;return col,root,[]
# Scout: a small forward tool, one dorsal utility mount, and a horn focus.
c,r,s=chassis('skimmer','01 - Skimmer',-3.65)
ball('Scout shell',(0,0,.69),(.63,.49,.40),white,c,r);ball('Scout keel',(0,.04,.48),(.57,.45,.17),teal,c,r)
head(c,r,(0,.03,1.28),.72)
for side in [-1,1]:
 cube('Scout wing',(side*.63,.10,.63),(.36,.51,.13),teal,c,r)
 ball('Scout engine',(side*.48,.38,.51),(.16,.20,.16),dark,c,r);ring('Engine glow',(side*.48,.52,.51),.105,glow,c,r,(math.pi/2,0,0))
cube('Scout front tool bracket',(0,-.43,.49),(.29,.24,.24),dark,c,r)
socket(c,r,s,'ventral_tool',(0,-.59,.49),'light_tool')
socket(c,r,s,'dorsal_utility',(0,.43,.86),'utility',(0,0,0))
socket(c,r,s,'horn',(0,-.02,2.06),'focus',(0,0,0),.075)
records.append(dict(id='skimmer',name='Skimmer',sockets=s,role='Compact hover scout; one light tool, one utility module, one horn focus.'))
# Carrier: four independently occupied standard tool mounts, plus two dorsal mounts and horn.
c,r,s=chassis('bulwark','02 - Bulwark',0)
cube('Carrier torso',(0,0,.99),(1.45,.82,.94),white,c,r);cube('Carrier reactor plate',(0,-.44,1.05),(.80,.10,.50),teal,c,r)
ball('Carrier reactor',(0,-.51,1.10),(.16,.075,.16),glow,c,r);ball('Carrier hover skirt',(0,0,.36),(1.13,.63,.23),teal,c,r)
head(c,r,(0,.03,1.75),.81)
for side in [-1,1]:
 for label,z in [('upper',1.21),('lower',.67)]:
  cube('Carrier outrigger',(side*.91,0,z),(.48,.48,.36),white if label=='upper' else lilac,c,r)
  cube('Carrier tool coupling',(side*.95,-.26,z),(.26,.15,.25),dark,c,r)
  socket(c,r,s,('left' if side<0 else 'right')+'_'+label,(side*.95,-.36,z),'tool')
 socket(c,r,s,('left' if side<0 else 'right')+'_back',(side*.40,.47,1.33),'utility',(0,0,0))
socket(c,r,s,'horn',(0,-.02,2.63),'focus',(0,0,0),.075)
records.append(dict(id='bulwark',name='Bulwark',sockets=s,role='Wide hover carrier; four tool couplings, two back utilities, one horn focus.'))
# Orb: three floating, radial arcane hardpoints, with no hand-tool mounts.
c,r,s=chassis('wisp','03 - Wisp',3.65)
ball('Wisp spherical shell',(0,0,.75),(.57,.52,.56),white,c,r)
ring('Wisp equator',(0,0,.74),.57,teal,c,r);ring('Wisp hover halo',(0,0,.22),.57,glow,c,r)
ball('Wisp reactor',(0,-.51,.74),(.19,.06,.19),lilac,c,r);head(c,r,(0,.03,1.37),.72)
for n,a in enumerate([-math.pi/2,math.pi/6,5*math.pi/6],1):
 x,y=.94*math.cos(a),.94*math.sin(a)
 ball('Floating coupling '+str(n),(x,y,.62),(.19,.19,.19),teal,c,r)
 socket(c,r,s,'orbit_'+str(n),(x,y,.82),'arcane',(0,0,0),.13)
socket(c,r,s,'horn',(0,-.02,2.15),'focus',(0,0,0),.075)
records.append(dict(id='wisp',name='Wisp',sockets=s,role='Floating orb; three arcane satellite mounts and one horn focus; no hand-tool sockets.'))
# A separate studio, with no effect on the source file or open Blender session.
studio=bpy.data.collections.new('Studio');scene.collection.children.link(studio)
floor=mat('Studio ground',(.07,.105,.12))
cube('Ground',(0,0,-.14),(200,200,.1),floor,studio,None)
def text(body,loc,size):
 curve=bpy.data.curves.new('Caption','FONT');curve.body=body;curve.align_x='CENTER';curve.size=size;curve.extrude=.001
 o=bpy.data.objects.new(body,curve);studio.objects.link(o);o.location=loc;o.rotation_euler=(math.pi/2,0,0);curve.materials.append(white)
for x,rec in zip([-3.65,0,3.65],records):
 text(rec['name'].upper(),(x,-.91,-.03),.24);text(str(len(rec['sockets']))+' MOUNTS',(x,-.92,-.26),.13)
world=bpy.data.worlds.new('Variant studio');scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.12,.18,.20,1);world.node_tree.nodes['Background'].inputs[1].default_value=.6
for name,pos,power,size in [('Key',(-4,-6,8),1800,7),('Fill',(5,-2,6),1400,6),('Rim',(1,5,7),2300,5)]:
 data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size;o=bpy.data.objects.new(name,data);studio.objects.link(o);o.location=pos;o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
cam_data=bpy.data.cameras.new('Variants camera');cam=bpy.data.objects.new('Variants camera',cam_data);studio.objects.link(cam);scene.camera=cam;cam_data.type='ORTHO'
def camera(pos,target,scale):cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam_data.ortho_scale=scale
camera((5,-15,7),(0,0,1.10),12.3)
scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True
scene.render.resolution_x=1800;scene.render.resolution_y=900;scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX';scene.render.image_settings.file_format='PNG'
scene.render.filepath=str(OUT/'chassis_lineup.png')
(OUT/'body_catalog.concept.json').write_text(json.dumps({'status':'design prototypes; not imported or gameplay balanced','bodies':records},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'unicore_body_variants.blend'))
bpy.ops.render.render(write_still=True)
for col,x,rec in zip(collections,[-3.65,0,3.65],records):
 for other in collections:other.hide_render=other!=col
 for o in studio.objects:
  if o.type=='FONT':o.hide_render=True
 scene.render.resolution_x=850;scene.render.resolution_y=950
 camera((x+3.5,-6,3.4),(x,0,1.15),3.7)
 scene.render.filepath=str(OUT/(rec['id']+'.png'));bpy.ops.render.render(write_still=True)
