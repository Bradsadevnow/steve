"""Render a transparent thumbnail for every kit piece, from one consistent view, for the builder palette.

Run with Blender's Python, never the harness environment:
  blender -b <kit>.blend --python export_thumbs.py -- <out_dir> <pack_id> [size]

Same selection rule and ids as export_kit.py: every EMPTY named PIECE_<name> with a 'category' property becomes
<out_dir>/<pack_id>_<name>.png. The view is the game's three-quarter angle, lit by a warm key and a cool fill.
"""
import bpy, sys, math, os
from mathutils import Vector

args = sys.argv[sys.argv.index('--') + 1:]
OUT, PACK = args[0], args[1]
SIZE = int(args[2]) if len(args) > 2 else 256
os.makedirs(OUT, exist_ok=True)

scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = scene.render.resolution_y = SIZE
scene.render.film_transparent = True
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
try: scene.eevee.taa_render_samples = 24
except Exception: pass
try: scene.view_settings.view_transform = 'Standard'
except Exception: pass

# own lights and camera, so the kit file's own rig never matters
for ob in list(bpy.data.objects):
    if ob.name.startswith('THUMB_'): bpy.data.objects.remove(ob, do_unlink=True)
col = bpy.data.collections.get('THUMB_RIG') or bpy.data.collections.new('THUMB_RIG')
if col.name not in scene.collection.children: scene.collection.children.link(col)
def rig(name, data):
    ob = bpy.data.objects.new('THUMB_' + name, data); col.objects.link(ob); return ob
cam = rig('cam', bpy.data.cameras.new('THUMB_cam')); cam.data.type = 'ORTHO'; scene.camera = cam
key = rig('key', bpy.data.lights.new('THUMB_key', 'SUN')); key.data.energy = 4.2; key.data.color = (1.0, 0.93, 0.8); key.rotation_euler = (math.radians(52), 0, math.radians(-38))
fill = rig('fill', bpy.data.lights.new('THUMB_fill', 'SUN')); fill.data.energy = 1.3; fill.data.color = (0.75, 0.86, 1.0); fill.rotation_euler = (math.radians(62), 0, math.radians(150))
world = bpy.data.worlds.new('THUMB_world'); world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (0.7, 0.76, 0.82, 1); world.node_tree.nodes['Background'].inputs[1].default_value = 0.55
scene.world = world

roots = sorted((o for o in bpy.data.objects if o.type == 'EMPTY' and o.name.startswith('PIECE_') and 'category' in o), key=lambda o: o.name)

def descendants(root):
    out = [root]; stack = list(root.children)
    while stack:
        ob = stack.pop(); out.append(ob); stack.extend(ob.children)
    return out

# A kit file may have been saved with collections hidden from render (e.g. after a demo-scene render). Undo that here.
for c in bpy.data.collections: c.hide_render = False; c.hide_viewport = False
def reveal(layer):
    layer.exclude = False; layer.hide_viewport = False
    for child in layer.children: reveal(child)
reveal(bpy.context.view_layer.layer_collection)
everything = [o for o in bpy.data.objects if not o.name.startswith('THUMB_')]
count = 0
for root in roots:
    shown = set(descendants(root))
    for ob in everything: ob.hide_render = ob not in shown
    # bounds of the piece in world space
    pts = []
    for ob in shown:
        if ob.type == 'MESH' and not ob.hide_render:
            pts += [ob.matrix_world @ Vector(c) for c in ob.bound_box]
    if not pts: continue
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    centre = (lo + hi) / 2
    span = (hi - lo)
    radius = max(Vector((span.x, span.y, 0)).length, span.z * 1.15, 2.2)
    cam.data.ortho_scale = radius * 1.32
    direction = Vector((0.62, -0.78, 0.62)).normalized()
    cam.location = centre + direction * 40
    cam.rotation_euler = (centre - cam.location).to_track_quat('-Z', 'Y').to_euler()
    cam.data.clip_end = 120
    scene.render.filepath = os.path.join(OUT, '%s_%s.png' % (PACK, root.name[len('PIECE_'):]))
    bpy.ops.render.render(write_still=True)
    count += 1
print('THUMBS', PACK, count)
