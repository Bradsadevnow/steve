"""Bake local character meshes and a versioned catalog for Unity and Python."""
import bpy, json, struct, ast
from pathlib import Path
from mathutils import Vector, Matrix, Euler
BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[2]
OUT=ROOT/'TScanViewer/Assets/Resources/Meadow/character';OUT.mkdir(parents=True,exist_ok=True)
# Reuse the project's vertex-colour bake, without executing its command-line entry point.
tree=ast.parse((BASE.parent/'export_kit.py').read_text(encoding='utf-8-sig'))
for node in tree.body:
 if isinstance(node,ast.FunctionDef) and node.name in {'material_color','descendants','plan_ratios','bake'}:
  exec(compile(ast.Module(body=[node],type_ignores=[]),'export_kit.py','exec'))
BUDGET={'floor':1800,'default':42000,'boss':42000}
environment_ratios=plan_ratios
def plan_ratios(root,budget):
 ratios=environment_ratios(root,budget)
 for ob in descendants(root):
  if any(tag in ob.name for tag in ('EYES /','UNICORN /','FACE /','MANE /')):ratios[ob.name]=1.0
 return ratios
meshes=[];bodies=[];modules=[]
def bake_asset(root,id):
 for o in descendants(root):o.hide_render=False
 bpy.context.view_layer.update()
 p,n,c,i=bake(root,bpy.context.evaluated_depsgraph_get(),position_precision=6);meshes.append((id,p,n,c,i))
def socket(id,kind,position,rotation=None):
 x,y,z=position
 basis=Matrix(((1,0,0),(0,0,1),(0,1,0)))
 q=(basis @ (rotation if rotation is not None else Matrix.Identity(3)) @ basis).to_quaternion()
 return dict(id=id,type=kind,x=x,y=z,z=y,qx=q.x,qy=q.y,qz=q.z,qw=q.w)
def body(id,name,root,sockets,pairs):
 bake_asset(root,'body_'+id);bodies.append(dict(id=id,name=name,mesh='body_'+id,sockets=sockets,pairs=pairs))
source=BASE/'unicore_chassis.blend'
bpy.ops.wm.open_mainfile(filepath=str(source))
def activate_source():
 for col in bpy.data.collections:col.hide_viewport=False;col.hide_render=False
 def visit(layer):
  layer.exclude=False;layer.hide_viewport=False
  for child in layer.children:visit(child)
 visit(bpy.context.view_layer.layer_collection)
 for ob in bpy.context.scene.objects:ob.hide_viewport=False;ob.hide_set(False)
 bpy.context.view_layer.update()
activate_source()
# Keep the existing hover body selectable by declining to replace its renderer.
bodies.append(dict(id='hover',name='Original Hover',mesh='',sockets=[],pairs=[]))
hover=json.loads((ROOT/'TScanViewer/Assets/Resources/Meadow/hover.json').read_text())
hp=[];hn=[];hc=[];hi=[]
for part in hover['parts']:
 offset=len(hp);v=part['vertices'];n=part['normals'];c=part['colors']
 hp.extend(tuple(v[i:i+3]) for i in range(0,len(v),3));hn.extend(tuple(max(-127,min(127,round(a*127))) for a in n[i:i+3]) for i in range(0,len(n),3));hc.extend(tuple(max(0,min(255,round(a*255))) for a in c[i:i+4]) for i in range(0,len(c),4));hi.extend(offset+i for i in part['triangles'])
meshes.append(('body_hover',hp,hn,hc,hi));bodies[0]['mesh']='body_hover'
root=bpy.data.objects['UNICORE_ROOT']
for o in list(root.children):
 if o.name.startswith('SOCKET_'):
  for child in list(o.children):
   if child.name.startswith('MOD_'):child.parent=None
slots=[]
for o in bpy.data.objects:
 if o.name.startswith('SOCKET_'):
  id=o.name[7:];slots.append(socket(id,'tool' if id.startswith('arm_') else 'focus' if id=='horn' else 'utility',o.matrix_world.translation,o.matrix_world.to_quaternion().to_matrix()))
body('unicore','Uni-Core',root,slots,[dict(primary='arm_R',secondary='arm_L')])
for o in sorted(list(bpy.data.objects),key=lambda o:o.name):
 if not o.name.startswith('MOD_') or 'socket' not in o:continue
 id=o.name[4:];anchor=bpy.data.objects[str(o['socket'])]
 # Module meshes are baked relative to their authored attachment socket.
 wrapper=bpy.data.objects.new('EXPORT_'+id,None);bpy.context.scene.collection.objects.link(wrapper);wrapper.matrix_world=anchor.matrix_world.copy()
 o.parent=wrapper;o.matrix_parent_inverse=Matrix.Identity(4);o.matrix_basis=Matrix.Identity(4)
 bake_asset(wrapper,'module_'+id)
 action=['slash'] if id=='warrior_blade' else ['shield_bash'] if id=='warrior_shield' else []
 kind=['tool','light_tool'] if id in ('warrior_blade','rogue_dagger') else ['tool','arcane'] if id not in ('warrior_shield','mage2h_greatstaff') else ['tool']
 if id in ('cleric_orb','mage2h_lens'):kind=['tool','arcane','focus','utility']
 if id in ('ranger_coil','mage_tome','rogue_hook'):kind+=['utility']
 modules.append(dict(id=id,name=id.replace('_',' ').title(),mesh='module_'+id,mount_types=kind,slots=2 if id=='mage2h_greatstaff' else 1,actions=action,description='Slash: 3 damage, adjacent target.' if action==['slash'] else 'Shield Bash: clear cardinal lane, target within 3 squares, stop adjacent, 1 damage.' if action else 'Visual prototype. No combat action is implemented for this module yet.'))
bpy.ops.wm.open_mainfile(filepath=str(BASE/'body_variants/unicore_body_variants.blend'))
activate_source()
concept=json.loads((BASE/'body_variants/body_catalog.concept.json').read_text())
for rec in concept['bodies']:
 root=bpy.data.objects['BODY_'+rec['id']]
 body(rec['id'],rec['name'],root,[socket(s['id'],s['type'],s['position'],Euler(s['rotation']).to_matrix()) for s in rec['sockets']], [dict(primary='right_upper',secondary='left_upper'),dict(primary='right_lower',secondary='left_lower')] if rec['id']=='bulwark' else [])
mechanics=json.loads((ROOT/'t-scan/live/character_mechanics.json').read_text())
for module in modules:
 module.update(stat_modifiers=[],abilities=[])
 module.update(mechanics['modules'].get(module['id'],{}))
starter=BASE/'starter_chassis/starter_chassis.blend'
if starter.exists():
 bpy.ops.wm.open_mainfile(filepath=str(starter));activate_source()
 for rec in json.loads((starter.parent/'body_catalog.json').read_text())['bodies']:
  body(rec['id'],rec['name'],bpy.data.objects['BODY_'+rec['id']],[socket(s['id'],s['type'],s['position'],Euler(s['rotation']).to_matrix()) for s in rec['sockets']],rec['pairs'])
catalog=dict(version=mechanics['version'],bodies=bodies,modules=modules)
encoded=json.dumps(catalog,indent=1)
(ROOT/'t-scan/live/character_catalog.json').write_text(encoded,encoding='utf-8');(OUT/'catalog.json').write_text(encoded,encoding='utf-8')
blob=bytearray(b'SKIT'+struct.pack('<II',1,len(meshes)))
for id,p,n,c,i in meshes:
 key=id.encode();blob+=struct.pack('<H',len(key))+key+struct.pack('<II',len(p),len(i))
 for xyz in p:blob+=struct.pack('<3f',*xyz)
 for xyz in n:blob+=struct.pack('<3bb',*xyz,0)
 for rgba in c:blob+=struct.pack('<4B',*rgba)
 for index in i:blob+=struct.pack('<I',index)
(OUT/'meshes.bytes').write_bytes(blob)
print('CHARACTER EXPORT',len(bodies),'bodies',len(modules),'modules',len(blob),'bytes')
