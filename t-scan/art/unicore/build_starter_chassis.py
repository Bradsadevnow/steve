"""Two three-mount bodies, isolated from original/source and existing variant Blender files."""
import bpy,ast,json,math
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parent;OUT=BASE/'starter_chassis';OUT.mkdir(exist_ok=True)
for collection in bpy.data.collections:collection.hide_viewport=False;collection.hide_render=False
def activate(layer):
 layer.exclude=False;layer.hide_viewport=False
 for child in layer.children:activate(child)
activate(bpy.context.view_layer.layer_collection)
for ob in bpy.context.scene.objects:ob.hide_viewport=False;ob.hide_set(False)
bpy.context.view_layer.update()
source_head=list(bpy.data.collections['HEAD'].all_objects)
head_inverse=bpy.data.objects['HEAD_ROOT'].matrix_world.inverted()
horn_offset=head_inverse @ bpy.data.objects['SOCKET_horn'].matrix_world.translation
for collection in list(bpy.context.scene.collection.children):bpy.context.scene.collection.children.unlink(collection)
scene=bpy.context.scene;collections=[];records=[]
tree=ast.parse((BASE/'build_body_variants.py').read_text())
for node in tree.body:
 if isinstance(node,ast.FunctionDef) and node.name in {'mat','link','cube','ball','ring','empty','head','socket','chassis'}:
  code=ast.unparse(node).replace("m.node_tree.nodes.get('Principled BSDF')","next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')")
  exec(compile(code,'variant_helpers','exec'))
white=mat('Starter porcelain',(.76,.84,.80));teal=mat('Starter deep teal',(.025,.30,.34),.5);dark=mat('Starter joints',(.055,.09,.12),.55)
gold=mat('Starter brass mounts',(.72,.48,.15),.65);glow=mat('Starter mint reactor',(.25,.95,.80),.1,2);lilac=mat('Starter lilac',(.46,.30,.61),.3)
def mounted_head(c,r,s,loc,scale):
 head(c,r,loc,scale)
 socket(c,r,s,'horn',Vector(loc)+horn_offset*scale,'focus',(0,0,0),.075)

c,r,s=chassis('duelist','04 - Duelist',-2.05);r['concept_only']=False
cube('Duelist compact torso',(0,0,1.01),(.88,.64,.67),white,c,r)
cube('Duelist chest plate',(0,-.35,1.02),(.56,.10,.37),teal,c,r)
ball('Duelist reactor',(0,-.42,1.06),(.13,.055,.13),glow,c,r)
ball('Duelist hover hull',(0,.02,.36),(.73,.48,.19),teal,c,r)
ring('Duelist hover ring',(0,.02,.30),.52,glow,c,r)
for sign,label in ((-1,'L'),(1,'R')):
 ball('Duelist arm pivot '+label,(sign*.58,.02,1.10),(.16,.18,.16),dark,c,r)
 cube('Duelist forearm '+label,(sign*.66,-.03,.86),(.23,.30,.42),white,c,r)
 cube('Duelist wrist '+label,(sign*.66,-.15,.63),(.28,.30,.24),teal,c,r)
 cube('Duelist hand coupling '+label,(sign*.66,-.32,.65),(.24,.08,.22),dark,c,r)
 socket(c,r,s,'hand_'+label,(sign*.66,-.39,.65),'tool')
mounted_head(c,r,s,(0,.02,1.57),.79)
records.append(dict(id='duelist',name='Duelist',sockets=s,pairs=[dict(primary='hand_R',secondary='hand_L')],role='Lean hover duelist: left/right hand tools and horn focus only.'))

c,r,s=chassis('mantle','05 - Mantle',2.05);r['concept_only']=False
ball('Mantle core shell',(0,.02,.98),(.53,.44,.61),white,c,r)
cube('Mantle chest window',(0,-.41,1.01),(.43,.09,.39),lilac,c,r)
ball('Mantle reactor',(0,-.48,1.05),(.12,.05,.12),glow,c,r)
ball('Mantle hover keel',(0,.03,.33),(.67,.48,.18),teal,c,r)
ring('Mantle hover halo',(0,.03,.23),.53,glow,c,r)
for sign,label in ((-1,'L'),(1,'R')):
 cube('Mantle shoulder bridge '+label,(sign*.60,.05,1.26),(.55,.36,.18),dark,c,r)
 cube('Mantle shoulder platform '+label,(sign*.88,.05,1.27),(.41,.48,.20),teal,c,r)
 cube('Mantle shoulder armor '+label,(sign*.88,.05,1.16),(.39,.46,.13),lilac,c,r)
 socket(c,r,s,'shoulder_'+label,(sign*.88,.05,1.40),'utility',(0,0,0),.14)
mounted_head(c,r,s,(0,.02,1.64),.79)
records.append(dict(id='mantle',name='Mantle',sockets=s,pairs=[],role='Armless hover support core: left/right shoulder utilities and horn focus only.'))

studio=bpy.data.collections.new('Starter chassis studio');scene.collection.children.link(studio)
floor=mat('Starter studio floor',(.055,.08,.10));cube('Starter studio ground',(0,0,-.13),(200,200,.10),floor,studio,None)
for x,rec in zip((-2.05,2.05),records):
 curve=bpy.data.curves.new('Starter caption','FONT');curve.body=rec['name'].upper()+' / 3 MOUNTS';curve.align_x='CENTER';curve.size=.22;curve.materials.append(white)
 ob=bpy.data.objects.new('Caption '+rec['id'],curve);studio.objects.link(ob);ob.location=(x,-.95,-.04);ob.rotation_euler=(math.pi/2,0,0)
world=bpy.data.worlds.new('Starter studio world');scene.world=world;world.use_nodes=True
background=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND');background.inputs[0].default_value=(.12,.18,.20,1);background.inputs[1].default_value=.65
for name,pos,power,size in [('Key',(-4,-6,8),1800,7),('Fill',(5,-2,6),1400,6),('Rim',(1,5,7),2300,5)]:
 data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size;ob=bpy.data.objects.new(name,data);studio.objects.link(ob);ob.location=pos;ob.rotation_euler=(Vector((0,0,1))-ob.location).to_track_quat('-Z','Y').to_euler()
data=bpy.data.cameras.new('Starter chassis camera');camera=bpy.data.objects.new('Starter chassis camera',data);studio.objects.link(camera);scene.camera=camera;data.type='ORTHO'
def view(position,target,scale):camera.location=position;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler();data.ortho_scale=scale
view((4,-14,6),(0,0,1.15),8.7)
scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True;scene.render.resolution_percentage=100;scene.render.resolution_x=1500;scene.render.resolution_y=900
scene.view_settings.view_transform='AgX';scene.render.image_settings.file_format='PNG';scene.render.filepath=str(OUT/'starter_lineup.png')
bpy.context.view_layer.update()
for root in (bpy.data.objects['BODY_duelist'],bpy.data.objects['BODY_mantle']):
 assert len([o for o in root.children if o.get('socket_id')])==3
(OUT/'body_catalog.json').write_text(json.dumps(dict(status='authored three-mount chassis; no inherent stat bonuses',bodies=records),indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'starter_chassis.blend'));bpy.ops.render.render(write_still=True)
for col,x,rec in zip(collections,(-2.05,2.05),records):
 for other in collections:other.hide_render=other!=col
 for ob in studio.objects:
  if ob.type=='FONT':ob.hide_render=True
 view((x+3.2,-6,3.3),(x,0,1.2),3.7);scene.render.resolution_x=800;scene.render.resolution_y=900;scene.render.filepath=str(OUT/(rec['id']+'.png'));bpy.ops.render.render(write_still=True)
print('STARTER CHASSIS BUILT',json.dumps(records))
