"""Original modular meadow art for Steve. Run with Blender --background --python.
No inference, movement rules, obstructions or governance are implemented by this art file.
"""
import bpy, math, random, json
from pathlib import Path
from mathutils import Vector, Quaternion

ROOT=Path(__file__).resolve().parent
ROOT.mkdir(parents=True,exist_ok=True)
(ROOT/'exports').mkdir(exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
R=random.Random(311026)
scene=bpy.context.scene
scene.name='Meadow_OpenField'
scene.unit_settings.system='METRIC'
scene['project_owner']='Steve / t-scan'
scene['purpose']='Flat open meadow art; 10 by 10 cells; no movement implementation.'
scene['cell_size_m']=2.0
scene['walkable_surface_z']=0.0

def collection(name,sc=scene):
 c=bpy.data.collections.new(name);sc.collection.children.link(c);return c
ground_col=collection('GROUND / 100 flat modules')
dress_col=collection('DECORATION / nonblocking grass and flowers')
base_col=collection('PRESENTATION / soil edge and studio')
kit=bpy.data.scenes.new('Meadow_Kit')
kit.unit_settings.system='METRIC'
assets_col=collection('ASSETS / individually reusable meshes',kit)
kit_stage=collection('PRESENTATION / asset display',kit)

def mix(a,b,t):return tuple(a[i]*(1-t)+b[i]*t for i in range(3))
GROUND=(.225,.365,.125)
GRASS_ROOT=(.15,.28,.075)
GRASS_TIP=(.43,.59,.16)
LEAF_DARK=(.095,.235,.105)
LEAF_LIGHT=(.34,.49,.135)
BARK=(.27,.135,.075)
CREAM=(.94,.88,.63)
GOLD=(.88,.47,.065)
PURPLE=(.47,.27,.67)

mat=bpy.data.materials.new('Meadow / portable painted vertex colors')
mat.use_nodes=True
nodes=mat.node_tree.nodes
bs=next(n for n in nodes if n.type=='BSDF_PRINCIPLED')
bs.inputs['Roughness'].default_value=.83
attr=nodes.new('ShaderNodeVertexColor');attr.layer_name='Color'
mat.node_tree.links.new(attr.outputs['Color'],bs.inputs['Base Color'])

class Mesh:
 def __init__(self):self.v=[];self.f=[];self.c=[];self.smooth=[]
 def vertex(self,p,c):self.v.append(tuple(p));self.c.append(tuple(c)+(1,));return len(self.v)-1
 def face(self,ids,smooth=True):self.f.append(tuple(ids));self.smooth.append(smooth)
 def ribbon(self,base,direction,length,width,color0,color1,bend=.22,segments=5):
  base=Vector(base);d=Vector(direction).normalized();side=d.cross(Vector((0,0,1)))
  if side.length<.01:side=Vector((1,0,0))
  side.normalize();forward=side.cross(d).normalized();pairs=[]
  for i in range(segments+1):
   t=i/segments;p=base+d*(length*t)+forward*(bend*t*t)
   w=width*(math.sin(math.pi*(t*.9+.06))**.7)*(1-t*.96)
   pairs.append([self.vertex(p-side*w,mix(color0,color1,t)),self.vertex(p+side*w,mix(color0,color1,t))])
  for i in range(segments):self.face((pairs[i][0],pairs[i][1],pairs[i+1][1],pairs[i+1][0]))
 def leaf(self,base,direction,length,width,color):
  # Folded lanceolate leaf; shaped silhouette and a raised central vein.
  base=Vector(base);d=Vector(direction).normalized()
  cross=d.cross(Vector((0,0,1)))
  if cross.length<.01:cross=Vector((1,0,0))
  cross.normalize();ids=[]
  for i in range(5):
   t=i/4;p=base+d*length*t+Vector((0,0,.11*length*math.sin(t*math.pi)))
   w=width*(math.sin(math.pi*t)**.8)
   ids.append([self.vertex(p-cross*w,color),self.vertex(p+Vector((0,0,w*.22)),mix(color,(.7,.72,.3),.13)),self.vertex(p+cross*w,color)])
  for i in range(4):
   self.face((ids[i][0],ids[i][1],ids[i+1][1],ids[i+1][0]));self.face((ids[i][1],ids[i][2],ids[i+1][2],ids[i+1][1]))
 def tube(self,points,radii,color,sides=8):
  rings=[]
  for i,(p,r) in enumerate(zip(points,radii)):
   p=Vector(p);direction=Vector(points[min(i+1,len(points)-1)])-Vector(points[max(0,i-1)])
   q=direction.to_track_quat('Z','Y')
   rings.append([self.vertex(p+q@Vector((math.cos(j*math.tau/sides)*r,math.sin(j*math.tau/sides)*r,0)),mix(color,(.56,.34,.14),.13*(j%3))) for j in range(sides)])
  self.face(tuple(reversed(rings[0])),False);self.face(rings[-1],False)
  for i in range(len(rings)-1):
   for j in range(sides):self.face((rings[i][j],rings[i][(j+1)%sides],rings[i+1][(j+1)%sides],rings[i+1][j]))
 def blob(self,center,scale,color,seed,segments=16,rings=10,rough=.08):
  center=Vector(center);ids=[]
  top=self.vertex(center+Vector((0,0,scale[2])),mix(color,(.63,.64,.22),.12))
  bottom=self.vertex(center-Vector((0,0,scale[2])),tuple(x*.73 for x in color))
  for i in range(1,rings):
   theta=math.pi*i/rings;row=[]
   for j in range(segments):
    phi=math.tau*j/segments
    k=1+rough*(math.sin(phi*3+seed+theta*2)*.6+math.cos(phi*5-theta*3+seed)*.4)
    p=Vector((math.sin(theta)*math.cos(phi)*scale[0]*k,math.sin(theta)*math.sin(phi)*scale[1]*k,math.cos(theta)*scale[2]*k))
    col=mix(tuple(x*.73 for x in color),mix(color,(.63,.64,.22),.16),(.5+.5*math.cos(theta))*.8+.1)
    row.append(self.vertex(center+p,col))
   ids.append(row)
  for j in range(segments):
   self.face((top,ids[0][j],ids[0][(j+1)%segments]))
   self.face((ids[-1][j],bottom,ids[-1][(j+1)%segments]))
  for i in range(len(ids)-1):
   for j in range(segments):self.face((ids[i][j],ids[i+1][j],ids[i+1][(j+1)%segments],ids[i][(j+1)%segments]))
 def object(self,name,col):
  mesh=bpy.data.meshes.new(name+' / mesh');mesh.from_pydata(self.v,[],self.f);mesh.update()
  ca=mesh.color_attributes.new(name='Color',type='FLOAT_COLOR',domain='POINT')
  for i,c in enumerate(self.c):ca.data[i].color=c
  for i,p in enumerate(mesh.polygons):p.use_smooth=self.smooth[i]
  ob=bpy.data.objects.new(name,mesh);col.objects.link(ob);mesh.materials.append(mat);return ob

ASSETS=[]
def asset(mesh,name,kind,footprint=None):
 bottom=min(v[2] for v in mesh.v)
 if kind!='ground':mesh.v=[(x,y,z-bottom) for x,y,z in mesh.v]
 ob=mesh.object(name,assets_col);ob.asset_mark();ob.asset_data.description=f'Original Steve meadow kit. {kind}. Grounded origin. Z-up, meters. Independent art asset.'
 ob['project_owner']='Steve';ob['asset_role']=kind;ob['collision']='none' if kind in ('ground','decoration') else 'candidate only; assign logical obstruction later'
 if footprint:ob['suggested_footprint_cells']=footprint
 ASSETS.append(ob);return ob

tiles=[]
for variant in range(4):
 m=Mesh();n=8
 for j in range(n+1):
  for i in range(n+1):
   x=-1+2*i/n;y=-1+2*j/n
   fade=(1-x*x)*(1-y*y)
   t=fade*(.5+.5*math.sin(x*2.6+y*1.4+variant*1.7))*.17
   m.vertex((x,y,0),mix(GROUND,(.4,.46,.16),t))
 for j in range(n):
  for i in range(n):
   a=j*(n+1)+i;m.face((a,a+1,a+n+2,a+n+1))
 tiles.append(asset(m,f'Ground_2m_Variant_{variant+1:02}','ground'))

grasses=[]
for variant in range(5):
 m=Mesh();rng=random.Random(600+variant)
 for i in range(8+variant*2):
  a=rng.uniform(0,math.tau);r=rng.uniform(0,.12);height=rng.uniform(.15,.38)*(1+variant*.07)
  m.ribbon((math.cos(a)*r,math.sin(a)*r,0),(math.cos(a)*.3,math.sin(a)*.3,1),height,rng.uniform(.012,.026),GRASS_ROOT,mix(GRASS_TIP,(.59,.6,.2),rng.random()*.3),rng.uniform(.05,.19))
 grasses.append(asset(m,f'Grass_Tuft_{variant+1:02}','decoration'))

flowers=[]
for variant,name in enumerate(['Daisy_Cream','Buttercup_Gold','Wildflower_Lilac','Clover_Pink']):
 m=Mesh();rng=random.Random(700+variant)
 for k in range(3):
  x=rng.uniform(-.12,.12);y=rng.uniform(-.12,.12);h=.25+rng.uniform(0,.15)
  m.tube([(x,y,0),(x+.025,y,h*.55),(x+.04,y+.01,h)],[.009,.007,.004],(.13,.26,.07),5)
  m.leaf((x,y,h*.35),(.7,.3,.3),.18,.045,(.22,.36,.1));m.leaf((x+.01,y,h*.5),(-.6,-.2,.35),.13,.04,(.26,.4,.11))
  center=(x+.04,y+.01,h);color=[CREAM,(.93,.66,.11),(.63,.43,.8),(.75,.37,.53)][variant]
  if variant==3:
   for j in range(11):
    a=j*2.4;rr=.035*math.sqrt(j/11);m.blob((center[0]+math.cos(a)*rr,center[1]+math.sin(a)*rr,center[2]+.04*(1-j/11)),(.025,.025,.033),color,j,8,5,.03)
  else:
   count=10 if variant==0 else 6
   for j in range(count):
    a=j*math.tau/count;m.leaf(center,(math.cos(a),math.sin(a),.15),.095 if variant==0 else .075,.025 if variant==0 else .037,color)
   m.blob((center[0],center[1],center[2]+.009),(.03,.03,.017),GOLD,0,10,5,.02)
 flowers.append(asset(m,name,'decoration'))

def shrub(name,width,height,seed,bloom=False):
 m=Mesh();rng=random.Random(seed)
 for i in range(7):
  a=i*2.4;r=width*rng.uniform(.05,.35);c=(math.cos(a)*r,math.sin(a)*r,height*(.35+rng.random()*.2))
  m.blob(c,(width*.31,width*.27,height*.38),mix(LEAF_DARK,LEAF_LIGHT,.3+rng.random()*.6),i+seed,14,9,.13)
  for j in range(12):
   t=j*2.4;pos=Vector(c)+Vector((math.cos(t)*width*.28,math.sin(t)*width*.25,height*.19))
   m.leaf(pos,(math.cos(t),math.sin(t),.55),rng.uniform(.14,.23),.047,mix(LEAF_LIGHT,(.53,.6,.19),rng.random()*.25))
  if bloom:
   for j in range(3):
    t=j*2.4;m.blob((c[0]+.18*math.cos(t),c[1]+.18*math.sin(t),c[2]+height*.32),(.04,.04,.035),(.8,.48,.63),j,8,5,.05)
 return asset(m,name,'obstruction_candidate',1 if width<2 else 2)
bushes=[shrub('Bush_Round',1.45,.95,41),shrub('Bush_Low_Spreading',1.9,.65,42),shrub('Bush_Flowering',1.35,1.1,43,True)]

trees=[]
for variant in range(3):
 m=Mesh();rng=random.Random(800+variant);height=[4.4,5.5,3.9][variant];wide=[1.55,1.38,1.7][variant]
 # An asymmetrical tapering trunk, visible fork, and spreading roots.
 trunk=[(0,0,0),(.07,-.02,height*.24),(-.07,.04,height*.49),(.18,.02,height*.7)]
 m.tube(trunk,[.29,.22,.15,.06],BARK,11)
 for k in range(5):
  a=k*math.tau/5+.2;m.tube([(math.cos(a)*.68,math.sin(a)*.68,.015),(math.cos(a)*.3,math.sin(a)*.3,.13),(0,0,.43)],[.035,.12,.19],BARK,7)
 for k in range(6):
  a=k*2.4+.3;end=(math.cos(a)*wide*.65,math.sin(a)*wide*.56,height*(.67+.11*(k%2)))
  m.tube([trunk[2],(end[0]*.5,end[1]*.5,height*.62),end],[.12,.08,.025],BARK,8)
 # Overlapping lobed canopy masses; small leaf sprays break the outer silhouette.
 for k in range(9):
  a=k*2.4;r=wide*(.65 if k<7 else .25);z=height*(.72 if k<7 else .91)+rng.uniform(-.12,.12)
  c=Vector((math.cos(a)*r,math.sin(a)*r*.84,z))
  col=mix(LEAF_DARK,LEAF_LIGHT,.45+rng.random()*.4)
  if variant==2:col=mix(col,(.58,.55,.17),.22)
  m.blob(c,(wide*.65,wide*.6,height*.19),col,k+variant,18,12,.1)
  for j in range(22):
   theta=rng.uniform(.15,2.25);phi=rng.uniform(0,math.tau)
   normal=Vector((math.sin(theta)*math.cos(phi),math.sin(theta)*math.sin(phi),math.cos(theta)))
   pos=c+Vector((normal.x*wide*.62,normal.y*wide*.58,normal.z*height*.185))
   m.leaf(pos,normal+Vector((0,0,.25)),rng.uniform(.15,.28),rng.uniform(.055,.085),mix(col,(.58,.64,.2),.16+rng.random()*.12))
 trees.append(asset(m,['Tree_Oak_Soft','Tree_Aspen_Tall','Tree_Maple_Goldgreen'][variant],'obstruction_candidate',2))

rocks=[]
for i in range(3):
 m=Mesh();m.blob((0,0,.22+i*.13),(.5+i*.22,.38+i*.18,.28+i*.16),(.31,.36,.36),i+4,10,6,.18)
 for idx,p in enumerate(m.v):
  if p[2]<.015:m.v[idx]=(p[0],p[1],.015)
 rocks.append(asset(m,f'Rock_Moss_{i+1:02}','obstruction_candidate',1))

# Keep original asset transforms at grounded local origin for export.
for ob in ASSETS:
 ob.location=(0,0,0)
 bpy.context.view_layer.objects.active=ob if ob.name in bpy.context.view_layer.objects else None
 bpy.ops.object.select_all(action='DESELECT')
 # Temporarily link to the active scene solely for selected-object export.
 scene.collection.objects.link(ob);ob.select_set(True);bpy.context.view_layer.objects.active=ob
 bpy.ops.export_scene.gltf(filepath=str(ROOT/'exports'/f'{ob.name}.glb'),export_format='GLB',use_selection=True,export_extras=True)
 scene.collection.objects.unlink(ob)

def instance(asset,name,col,location,scale=1,yaw=0):
 ob=bpy.data.objects.new(name,asset.data);col.objects.link(ob);ob.location=location;ob.scale=(scale,scale,scale);ob.rotation_euler.z=yaw
 ob['asset_id']=asset.name;ob['collision']='none';return ob

for y in range(10):
 for x in range(10):instance(tiles[R.randrange(4)],f'Ground_Cell_{x+1:02}_{y+1:02}',ground_col,(-9+x*2,-9+y*2,0),1,R.randrange(4)*math.pi/2)

# Art scatter is visual only; grass is low in the center and richer near the edges.
# Density fields create patches and clear breathing room rather than uniform confetti.
for j in range(95):
 for i in range(95):
  x=-9.9+i*.21+R.uniform(-.1,.1);y=-9.9+j*.21+R.uniform(-.1,.1)
  edge=max(abs(x),abs(y))/10
  wave=.5+.5*math.sin(x*.8+math.sin(y*.6))*math.cos(y*.67)
  probability=.28+.35*wave+.16*edge
  if R.random()<probability:
   instance(grasses[R.randrange(5)],f'Grass_{j:02}_{i:02}',dress_col,(x,y,.001),R.uniform(.65,1.25)*(1 if edge>.6 else .64),R.uniform(0,math.tau))
for i in range(210):
 a=R.uniform(0,math.tau);r=R.uniform(7.4,9.7);x=math.cos(a)*r;y=math.sin(a)*r
 if max(abs(x),abs(y))>9.8:continue
 # Flower species occur in local communities rather than a random rainbow.
 species=0 if x<0 and y<2 else 2 if y>2 else 1 if x>2 else 3
 instance(flowers[species],f'Flower_Patch_{i:03}',dress_col,(x,y,.002),R.uniform(.7,1.2),R.uniform(0,math.tau))

def solid_material(name,color,rough=1):
 mat=bpy.data.materials.new(name);mat.diffuse_color=(*color,1);mat.use_nodes=True
 bs=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=rough;return mat
soil=solid_material('Earth / warm cut bank',(.19,.105,.065))
stage_mat=solid_material('Studio / sage',(.135,.19,.16))
card_mat=solid_material('Kit / parchment',(.65,.67,.49))

def cube(name,location,scale,material,col,bevel=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=location);ob=bpy.context.object;ob.name=name
 ob.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);ob.data.materials.append(material)
 for c in list(ob.users_collection):c.objects.unlink(ob)
 col.objects.link(ob)
 if bevel:
  mod=ob.modifiers.new('Soft outside edge','BEVEL');mod.width=bevel;mod.segments=3
  ob.modifiers.new('Weighted face shading','WEIGHTED_NORMAL')
 return ob
cube('Meadow soil foundation',(0,0,-.38),(20,.0+20,.7),soil,base_col,.16)
cube('Studio floor',(0,0,-.85),(200,200,.2),stage_mat,base_col,.08)
# Sparse pebbles embedded into the cut edge add strata, without intruding on the field.
for i in range(70):
 a=R.randrange(4);u=R.uniform(-9.65,9.65);z=R.uniform(-.58,-.19)
 p=[(u,-10.005,z),(10.005,u,z),(u,10.005,z),(-10.005,u,z)][a]
 instance(rocks[i%3],f'Soil pebble_{i:02}',base_col,p,R.uniform(.06,.14),R.random()*math.tau)

def setup(sc,target,ortho,cam_location,res=(1400,1100)):
 try:sc.render.engine='CYCLES'
 except TypeError:pass
 sc.cycles.samples=48;sc.cycles.use_denoising=True
 sc.render.resolution_x=res[0];sc.render.resolution_y=res[1];sc.render.resolution_percentage=100
 sc.render.image_settings.file_format='PNG';sc.world=bpy.data.worlds.new(sc.name+' / world');sc.world.use_nodes=True
 bg=next(n for n in sc.world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs['Color'].default_value=(.52,.66,.72,1);bg.inputs['Strength'].default_value=.45
 try:sc.view_settings.view_transform='AgX'
 except TypeError:pass
 cam_data=bpy.data.cameras.new(sc.name+' / camera');cam=bpy.data.objects.new(sc.name+' / camera',cam_data);sc.collection.objects.link(cam)
 cam.location=cam_location;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam_data.type='ORTHO';cam_data.ortho_scale=ortho;sc.camera=cam;cam_data.lens=45
 for name,loc,power,size,color in [('Sunlight',(-8,-10,22),2300,12,(1,.87,.64)),('Sky fill',(10,4,15),1500,14,(.65,.8,1))]:
  ld=bpy.data.lights.new(sc.name+' / '+name,'AREA');ld.energy=power;ld.shape='DISK';ld.size=size;ld.color=color
  ob=bpy.data.objects.new(ld.name,ld);sc.collection.objects.link(ob);ob.location=loc;ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
 # Sun is the steady broad source; area lamps soften the presentation shadows.
 ld=bpy.data.lights.new(sc.name+' / afternoon','SUN');ld.energy=2.1;ld.angle=.22;ob=bpy.data.objects.new(ld.name,ld);sc.collection.objects.link(ob);ob.rotation_euler=(.45,-.5,-.4)

setup(scene,(0,0,-.1),28,(24,-31,27))

# The kit scene is an asset catalog, not part of the traversable meadow.
for idx,ob in enumerate(ASSETS):
 if ob in trees:loc=((-5,0,5)[trees.index(ob)],5,0)
 elif ob in bushes:loc=((-5,0,5)[bushes.index(ob)],.1,0)
 elif ob in rocks:loc=((-5,0,5)[rocks.index(ob)],-3.8,0)
 elif ob in tiles:loc=(-7+tiles.index(ob)*4.5,-8.4,0)
 elif ob in grasses:loc=(-6+grasses.index(ob)*3,-11.4,0)
 else:loc=(-5.5+flowers.index(ob)*3.7,-13.8,0)
 ob.location=loc
cube('Asset catalog floor',(0,-3,-.26),(23,25,.45),card_mat,kit_stage,.25)
setup(kit,(0,-3,1),27,(22,-32,26),(1500,1500))

def label(text,location,size=.22):
 curve=bpy.data.curves.new(text,'FONT');curve.body=text;curve.size=size;curve.align_x='CENTER';curve.extrude=.001
 ob=bpy.data.objects.new(text,curve);kit_stage.objects.link(ob);ob.location=location
 curve.materials.append(solid_material('Ink / '+text,(.08,.16,.13)))
for ob in ASSETS:label(ob.name.replace('_',' '),(ob.location.x,ob.location.y-(2 if ob in trees else 1.2 if ob in tiles else .65),.012),.18)

# Keep a usable material-preview camera view when opening the saved file.
bpy.context.window.scene=scene
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.shading.type='MATERIAL'

manifest=dict(project_owner='Steve',name='Meadow kit 001',cell_size_m=2,board_cells=[10,10],movement_plane_z=0,logical_obstructions=[],runtime_status='Art only; no engine or governance changes.',assets=[dict(id=o.name,file='exports/'+o.name+'.glb',role=o['asset_role'],vertices=len(o.data.vertices),triangles=sum(len(p.vertices)-2 for p in o.data.polygons)) for o in ASSETS])
(ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2))
validation=dict(flat_ground=all(abs(v.co.z)<1e-7 for o in ground_col.objects for v in o.data.vertices),tile_count=len(ground_col.objects),tile_dimensions_m=[2,2],trees_on_playfield=0,bushes_on_playfield=0,shared_decoration_meshes=len(set(o.data.name for o in dress_col.objects)),decoration_instances=len(dress_col.objects),exported_assets=len(ASSETS),external_images=0)
assert validation['flat_ground'] and validation['tile_count']==100
(ROOT/'validation.json').write_text(json.dumps(validation,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'steve_meadow_001.blend'))
scene.render.filepath=str(ROOT/'meadow_open_field.png');bpy.ops.render.render(write_still=True,scene=scene.name)
kit.render.filepath=str(ROOT/'meadow_asset_kit.png');bpy.ops.render.render(write_still=True,scene=kit.name)
print('MEADOW_COMPLETE',json.dumps(validation))
