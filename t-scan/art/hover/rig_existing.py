import bpy
bpy.ops.wm.open_mainfile(filepath=r'C:/Users/bradl/OneDrive/Desktop/steve/t-scan/art/hover/steve_hover_unicorn.blend')
scene=bpy.context.scene
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

bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print('HOVER_RIG_SAVED',len(rig.data.bones))
