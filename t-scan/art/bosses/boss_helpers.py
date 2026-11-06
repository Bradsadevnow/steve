"""Boss kit helpers (Blender Python). Bosses are static actor pieces, 3 x 3 cells (6 m) unless noted, front toward -Y, floor at z=0.
Every boss is an EMPTY named PIECE_<id> with category 'enemy' and blocks_movement True, so export_kit.py classifies it as an actor.
Load with: exec(bpy.data.texts['boss_helpers'].as_string(), globals())"""
import bpy, bmesh, math, random
from mathutils import Vector, noise
D = bpy.data

def getcol(n, parent=None):
    c = D.collections.get(n)
    if not c:
        c = D.collections.new(n); (parent or bpy.context.scene.collection).children.link(c)
    return c

def mat(name, c, metal=0.0, rough=.55, emit=0):
    if name in D.materials: return D.materials[name]
    m = D.materials.new(name); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    b.inputs['Base Color'].default_value = c; b.inputs['Metallic'].default_value = metal; b.inputs['Roughness'].default_value = rough
    if emit: b.inputs['Emission Color'].default_value = c; b.inputs['Emission Strength'].default_value = emit
    m.diffuse_color = c; return m

# shared palette
WOOD = mat('Wood', (.46, .29, .17, 1)); WOOD_DK = mat('Wood / dark', (.30, .18, .10, 1)); WOOD_LT = mat('Wood / light', (.62, .42, .25, 1))
IRON = mat('Iron', (.22, .24, .29, 1), .5, .45); STEEL = mat('Steel', (.7, .73, .78, 1), .8, .3); GOLD = mat('Trim / gold', (.85, .56, .16, 1), .7, .3)
BONE = mat('Bone', (.86, .84, .76, 1)); RED = mat('Red', (.75, .18, .2, 1)); DARKRED = mat('Red / deep', (.32, .06, .09, 1))
PINK = mat('Tongue pink', (.9, .36, .5, 1), 0, .35); WHITE = mat('Eye white', (.96, .96, .94, 1), 0, .25); BLACK = mat('Pupil', (.03, .03, .05, 1), 0, .2)
GLOW_RED = mat('Glow / ruby', (1.0, .15, .2, 1), 0, .3, 3.0); GLOW_GREEN = mat('Glow / toxic', (.45, 1.0, .35, 1), 0, .3, 3.0)
GLOW_TEAL = mat('Glow / teal', (.14, .74, .63, 1), 0, .3, 2.5); GLOW_GOLD = mat('Glow / gold', (1.0, .78, .25, 1), 0, .3, 2.5)
GLOW_PINK = mat('Glow / pink', (1.0, .35, .7, 1), 0, .3, 2.5); GLOW_VIOLET = mat('Glow / violet', (.7, .4, 1.0, 1), 0, .3, 3.0)
IRIS_GREEN = mat('Iris green', (.35, .85, .25, 1), 0, .3); IRIS_AMBER = mat('Iris amber', (.95, .6, .1, 1), 0, .3)
GEM_BLUE = mat('Gem blue', (.15, .35, 1.0, 1), .2, .15, 1.2); GEM_GREEN = mat('Gem green', (.1, .85, .4, 1), .2, .15, 1.2)

class Boss:
    """A boss piece: an empty with meshes parented to it. All sizes in metres."""
    def __init__(self, name, env, note='', cells=3):
        self.col = getcol('BOSS ' + env, getcol('BOSSES'))
        self.root = D.objects.new('PIECE_' + name, None); self.root.empty_display_type = 'PLAIN_AXES'; self.root.empty_display_size = .5
        self.col.objects.link(self.root)
        self.root['category'] = 'enemy'; self.root['blocks_movement'] = True
        self.root['footprint'] = '%dx%d cells (%dm)' % (cells, cells, cells * 2); self.root['note'] = note; self.root['boss'] = True
        self.n = 0; self.holder = None
    def hold(self, name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None, scale=(1, 1, 1)):
        """Start a sub-assembly: later parts are placed in this holder's local space (use for hinged lids, arms)."""
        h = D.objects.new('%s / %s' % (self.root.name, name), None); h.empty_display_type = 'ARROWS'; h.empty_display_size = .3; self.col.objects.link(h)
        h.parent = parent or self.root; h.location = loc; h.rotation_euler = [math.radians(a) for a in rot]; h.scale = scale; self.holder = h; return h
    def release(self): self.holder = None
    def fin(self, ob, m, bevel=0, seg=2, smooth=True):
        for c in list(ob.users_collection): c.objects.unlink(ob)
        self.col.objects.link(ob); ob.parent = self.holder or self.root; ob.data.materials.append(m); self.n += 1
        if smooth:
            for p in ob.data.polygons: p.use_smooth = True
        if bevel:
            b = ob.modifiers.new('Bevel', 'BEVEL'); b.width = bevel; b.segments = seg; b.limit_method = 'ANGLE'; b.angle_limit = math.radians(35)
            w = ob.modifiers.new('WeightedNormal', 'WEIGHTED_NORMAL'); w.keep_sharp = True
        return ob
    def _name(self, ob, n): ob.name = '%s / %s' % (self.root.name, n)
    def box(self, n, loc, size, m, bevel=.04, rot=(0, 0, 0), seg=2):
        bpy.ops.mesh.primitive_cube_add(size=1, location=loc); ob = bpy.context.object; self._name(ob, n)
        ob.scale = size; bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        ob.rotation_euler = [math.radians(a) for a in rot]; return self.fin(ob, m, bevel, seg)
    def cyl(self, n, loc, r, h, m, rot=(0, 0, 0), bevel=.02, r2=None, verts=24, sc=(1, 1, 1)):
        if r2 is None: bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=h, location=loc)
        else: bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r, radius2=r2, depth=h, location=loc)
        ob = bpy.context.object; self._name(ob, n); ob.scale = sc; bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        ob.rotation_euler = [math.radians(a) for a in rot]; return self.fin(ob, m, bevel)
    def ball(self, n, loc, scale, m, rot=(0, 0, 0), segs=24):
        if isinstance(scale, (int, float)): scale = (scale, scale, scale)
        bpy.ops.mesh.primitive_uv_sphere_add(segments=segs, ring_count=max(8, segs // 2), location=loc); ob = bpy.context.object; self._name(ob, n)
        ob.scale = scale; bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        ob.rotation_euler = [math.radians(a) for a in rot]; return self.fin(ob, m, 0)
    def torus(self, n, loc, major, minor, m, rot=(0, 0, 0)):
        bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor, major_segments=36, minor_segments=10, location=loc)
        ob = bpy.context.object; self._name(ob, n); ob.rotation_euler = [math.radians(a) for a in rot]; return self.fin(ob, m, 0)
    def blob(self, n, loc, size, m, seed=1, amp=.18, freq=1.3, sub=3, rot=(0, 0, 0), floor=None):
        """A lumpy sculpted ellipsoid: an ico sphere pushed around by 3D noise."""
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=sub, radius=1, location=(0, 0, 0)); ob = bpy.context.object; self._name(ob, n)
        off = Vector((seed * 7.31, seed * 3.17, seed * 5.53))
        for v in ob.data.vertices:
            k = 1 + amp * noise.noise(v.co * freq + off)
            v.co = Vector((v.co.x * k * size[0], v.co.y * k * size[1], v.co.z * k * size[2]))
            if floor is not None and v.co.z < floor: v.co.z = floor
        ob.rotation_euler = [math.radians(a) for a in rot]; ob.location = loc
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=False); return self.fin(ob, m, 0)
    def sweep(self, n, pts, shape, wdir, m, sides=10, cap=True):
        """Tube along a Catmull-Rom path; shape(t)->(half_width, half_thickness)."""
        P = [Vector(p) for p in pts]; Q = [P[0]] + P + [P[-1]]; path = []
        for i in range(1, len(Q) - 2):
            p0, p1, p2, p3 = Q[i - 1], Q[i], Q[i + 1], Q[i + 2]
            for k in range(8):
                t = k / 8; t2 = t * t; t3 = t2 * t
                path.append(.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
        path.append(P[-1]); N = len(path); me = D.meshes.new(n); bm = bmesh.new(); layers = []
        for i, q in enumerate(path):
            t = (path[min(i + 1, N - 1)] - path[max(i - 1, 0)]).normalized(); w = (Vector(wdir) - t * Vector(wdir).dot(t))
            if w.length < 1e-4: w = Vector((1, 0, 0)) - t * t.x
            w.normalize(); h = t.cross(w).normalized(); wd, ht = shape(i / (N - 1))
            layers.append([bm.verts.new(q + w * math.cos(2 * math.pi * k / sides) * wd + h * math.sin(2 * math.pi * k / sides) * ht) for k in range(sides)])
        for i in range(N - 1):
            for k in range(sides): bm.faces.new((layers[i][k], layers[i][(k + 1) % sides], layers[i + 1][(k + 1) % sides], layers[i + 1][k]))
        if cap: bm.faces.new(layers[0][::-1]); bm.faces.new(layers[-1])
        bm.normal_update(); bm.to_mesh(me); bm.free()
        ob = D.objects.new('%s / %s' % (self.root.name, n), me); self.col.objects.link(ob); return self.fin(ob, m, 0)
    def tube(self, n, pts, r0, r1, m, sides=10):
        return self.sweep(n, pts, lambda t: (r0 + (r1 - r0) * t, r0 + (r1 - r0) * t), (1, 0, 0), m, sides)
    def eye(self, n, loc, r, look=(0, -1, 0), iris=None):
        """Googly eye: white ball with a pupil on the side facing `look`."""
        d = Vector(look).normalized(); self.ball(n + ' white', loc, r, WHITE)
        self.ball(n + ' pupil', Vector(loc) + d * r * .8, r * .55, BLACK)
        if iris: self.ball(n + ' iris', Vector(loc) + d * r * .72, r * .72, iris)
    def spikes(self, n, centre, count, radius, length, m, axis='z', thick=.07, tilt=0, phase=0):
        c = Vector(centre)
        for k in range(count):
            a = phase + k * 2 * math.pi / count; dx, dy = math.cos(a), math.sin(a)
            if axis == 'z': loc = c + Vector((dx * radius, dy * radius, length / 2)); rot = (math.degrees(dy * tilt), math.degrees(-dx * tilt), 0)
            else: loc = c; rot = (0, 0, 0)
            self.cyl('%s %d' % (n, k), loc, thick, length, m, rot=rot, r2=0.002, bevel=0, verts=8)

def mirror_x(f):
    for sx in (-1, 1): f(sx)

def layout_bosses(spacing=8.0):
    roots = sorted([o for o in D.objects if o.type == 'EMPTY' and o.name.startswith('PIECE_') and 'category' in o], key=lambda o: o.name)
    for i, r in enumerate(roots): r.location = ((i % 4) * spacing, -(i // 4) * spacing, 0)
    return roots

def only_show(root_name):
    """Show just one piece (for previews)."""
    keep = set(); r = D.objects[root_name]; stack = [r]
    while stack:
        o = stack.pop(); keep.add(o); stack.extend(o.children)
    for o in D.objects:
        if o.type in ('MESH', 'EMPTY'): o.hide_viewport = o not in keep; o.hide_render = o not in keep

def aim(target=(0, 0, 1.6), dist=15, az=35, el=22, lens=40):
    """Point the preview camera at a piece from azimuth/elevation (degrees)."""
    cam = D.objects['PV_cam']; a = math.radians(az); e = math.radians(el)
    cam.location = Vector(target) + Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e))) * dist
    cam.rotation_euler = (Vector(target) - cam.location).to_track_quat('-Z', 'Y').to_euler(); cam.data.lens = lens

def shot(path, target=(0, 0, 1.6), dist=15, az=35, el=22):
    aim(target, dist, az, el); bpy.context.scene.render.filepath = path; bpy.ops.render.render(write_still=True)

# Review layout: one row per environment, 12 m between slots, so previews never overlap.
PARK_ROW = {'dungeon': 0, 'swap': -14, 'school': -28}

def park(root_name, env, slot):
    D.objects[root_name].location = (slot * 12, PARK_ROW[env], 0)
