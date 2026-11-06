"""Bake a Blender kit file into Unity's compact binary mesh format plus a role catalog.

Run with Blender's Python, never the harness environment:
  blender -b <kit>.blend --python export_kit.py -- <out_dir> <pack_id> "<Pack title>"

Reads every EMPTY named PIECE_<name> that carries a 'category' property. Each piece becomes one vertex-coloured
mesh in piece-local coordinates (floor top at z=0, cell centre at the origin). Axes follow the existing
hover/course exporters: Unity = (blender x, blender z, blender y) with reversed winding.
Colour comes from each material's base colour. Emissive materials keep their colour and lower vertex alpha:
alpha = 1 - emit, so alpha 1 means no glow.

The role is derived here, once, from the piece's category and blocks_movement flag. Nothing downstream may
re-label a piece. See ROLE_RULES. The backend independently rejects any manifest whose roles and blocking disagree.
"""
import bpy, sys, json, struct, math, os
from mathutils import Vector

args = sys.argv[sys.argv.index('--') + 1:]
OUT, PACK, TITLE = args[0], args[1], args[2]
os.makedirs(OUT, exist_ok=True)

# category + blocks_movement -> role. Roles: floor, wall, obstacle, structure, hazard, decor, actor.
def role_of(category, blocks, name):
    if category == 'floor': return 'floor'
    if category == 'hazard': return 'hazard'
    if category == 'enemy': return 'actor'
    if category == 'wall': return 'wall'
    if category == 'fence': return 'wall' if blocks else 'structure'
    if category == 'structure': return 'structure'
    if category in ('prop', 'stall'): return 'obstacle' if blocks else 'decor'
    raise ValueError('Unclassified piece category %r for %s' % (category, name))

NAMES = {
 'floor_flag_a':'Flagstone floor','floor_flag_b':'Big flagstone floor','floor_flag_c':'Cracked flagstone floor','floor_mossy':'Mossy flagstone floor','floor_rune':'Glowing rune floor',
 'floor_plate':'Pressure plate','hazard_spikes':'Spike trap','wall_plain':'Stone wall','wall_torch':'Torch wall','wall_banner':'Banner wall','wall_cracked':'Cracked wall',
 'door_closed':'Wooden door','arch_gate':'Stone archway','pillar_round':'Stone pillar','pillar_broken':'Broken pillar','stairs_down':'Stairs down',
 'prop_barrel':'Barrel','prop_bones':'Skull and bones','prop_bookshelf':'Bookshelf','prop_brazier':'Brazier','prop_chest':'Treasure chest','prop_crate':'Crate','prop_crate_stack':'Crates and barrel','prop_rubble':'Rubble','prop_statue_knight':'Knight statue',
 'floor_asphalt_a':'Asphalt (gum and cracks)','floor_asphalt_b':'Asphalt (parking line)','floor_asphalt_c':'Plain asphalt','floor_gravel':'Gravel','floor_dirt':'Dirt (one weed)','floor_tarp':'Blue tarp','floor_rug':'Ornate rug',
 'fence_chainlink':'Chain-link fence','gate_entrance':'Entrance gate','prop_balloons':'Balloon bunch','prop_box_fan':'Box fan','prop_box_stack':'Box stack','prop_funnel_cart':'Funnel cake cart','prop_gnomes':'Gnome trio',
 'prop_jacket_rack':'Jacket rack','prop_mannequins':'Mannequin heap','prop_portapotty':'Porta-potty','prop_shopping_cart':'Shopping cart','prop_tube_man':'Inflatable tube man','prop_tv_bin':'As-seen-on-TV bin','prop_vhs_tower':'VHS tower',
 'stall_canopy':'Canopy tent','stall_dolls':'Doll table','stall_table':'Folding table',
 'floor_hall_a':'Checker linoleum','floor_hall_b':'Speckled linoleum','floor_gym':'Gym floor (court lines)','floor_gym_b':'Gym floor','floor_cafe':'Cafeteria tile (spill)','floor_cafe_b':'Cafeteria tile','floor_carpet':'Classroom carpet (stain)','floor_carpet_b':'Classroom carpet',
 'prop_bleachers':'Bleachers','prop_cafe_table':'Lunch table','prop_desks':'Student desks','prop_fountain':'Water fountain','prop_hoop':'Basketball hoop','prop_lostfound':'Lost and found','prop_mascot_statue':'Wombat statue','prop_teacher_desk':"Teacher's desk",
 'prop_trashcan':'Trash can','prop_vending':'Vending machine','prop_wetfloor':'Wet floor sign and mop bucket','prop_whiteboard':'Whiteboard','stairs_up':'Stairs up',
 'wall_bulletin':'Bulletin board wall','wall_clock':'Clock wall','wall_hall':'Hallway wall','wall_lockers_a':'Locker wall (teal)','wall_lockers_b':'Locker wall (navy)','wall_trophy':'Trophy case wall','wall_window':'Window wall','door_classroom':'Classroom door',
 'enemy_cart':'Cart monster','enemy_gnome':'Gnome walker','enemy_haggler':'Haggler','enemy_mannequin':'Possessed mannequin','enemy_mascot':'Bootleg mascot','enemy_goblin':'Goblin bomber','enemy_golem':'Stone golem','enemy_mimic':'Mimic','enemy_skeleton':'Skeleton knight','enemy_slime':'Slime',
 'enemy_hall_monitor':'Hall monitor','enemy_locker':'Rogue locker','enemy_meat':'Mystery meat blob','enemy_pep_wombat':'Pep rally wombat','enemy_sub_teacher':'Substitute teacher',
 'boss_mimic_queen':'Mimic Queen','enemy_mimic_queen_mini':'Tiny mimic queen','boss_glitterfang':'Count Glitterfang','boss_archivist_mold':'Grand Archivist Mold',
 'boss_haggler':'The Haggler','boss_raccoon_stack':'Big Raccoon Energy','boss_dowser_dave':'Dowser Dave','boss_principal_fogwhistle':'Principal Fogwhistle',
 'boss_lunch_lady':'The Lunch Lady Colossus','boss_pep_rally':'Pep Rally, Incarnate',
 'dummy_unarmed':'Crash-test dummy','dummy_melee':'Crash-test dummy with sword','dummy_ranged':'Crash-test dummy with crossbow'}
ROLE_OVERRIDE = {'door_classroom': 'structure'}   # doors are structures everywhere
# triangle budget per piece (floors are instanced 225 times in a full world)
BUDGET = {'floor': 1800, 'default': 9000, 'boss': 16000}   # bosses are one-off sculpts: a larger budget
PREFIX_ROLE_WORD = {'floor', 'wall'}   # these read better as a trailing word: "Plain wall"
def display_name(name):
    if name in NAMES: return NAMES[name]
    print('WARNING unnamed piece:', name)
    parts = name.split('_')
    lead = parts[0]
    if lead in ('prop', 'stall', 'enemy', 'hazard', 'fence', 'gate', 'pillar', 'arch', 'door', 'stairs') and len(parts) > 1:
        words = parts[1:] if lead in ('prop', 'stall', 'enemy') else parts[1:] + [lead] if lead in ('fence', 'gate') else parts
    elif lead in PREFIX_ROLE_WORD:
        words = parts[1:] + [lead]
    else:
        words = parts
    variant = ''
    if len(words) > 1 and len(words[-1]) == 1 and words[-1].isalpha() and words[-1] not in ('a',) or (len(words) > 1 and words[-1] in ('a', 'b', 'c') and len(words[-2]) > 1):
        variant = ' (%s)' % words[-1].upper(); words = words[:-1]
    text = ' '.join(words)
    return text[:1].upper() + text[1:] + variant

def footprint_of(root):
    """Cells covered per side, from the piece's footprint note ('3x3 cells (6m)' -> 3). Only actors may be larger than 1."""
    try: return int(str(root.get('footprint', '1x1')).split('x')[0])
    except ValueError: return 1

def material_color(mat):
    if mat is None: return (0.5, 0.5, 0.5, 1.0)
    r, g, b, _ = mat.diffuse_color
    alpha = 1.0
    if mat.node_tree:
        bsdf = next((n for n in mat.node_tree.nodes if n.type == 'PRINCIPLED_BSDF' or n.type == 'BSDF_PRINCIPLED'), None)
        if bsdf is not None and 'Emission Strength' in bsdf.inputs:
            strength = bsdf.inputs['Emission Strength'].default_value
            if strength > 0:
                alpha = 1.0 - min(1.0, strength / 3.0) * 0.95
    return (r, g, b, alpha)

def descendants(root):
    out = []
    stack = list(root.children)
    while stack:
        ob = stack.pop()
        out.append(ob)
        stack.extend(ob.children)
    return out

def plan_ratios(root, budget):
    """Small, busy objects (pebbles, confetti, speckles, tiny balls) are simplified hardest; then the piece is scaled to budget."""
    ratios = {}
    for ob in descendants(root):
        if ob.type != 'MESH' or ob.hide_render: continue
        tris = sum(len(p.vertices) - 2 for p in ob.data.polygons)
        size = max(ob.dimensions) if ob.dimensions else 1
        r = 1.0
        if tris > 120 and size < 0.4: r = max(0.04, 90.0 / tris)
        ratios[ob.name] = [r, tris]
    total = sum(max(8, t * r) for r, t in ratios.values())
    if total > budget:
        scale = budget / total
        for name, rt in ratios.items():
            if rt[1] * rt[0] > 150: rt[0] = max(0.05, rt[0] * scale)
    return {k: v[0] for k, v in ratios.items()}

def bake(root, depsgraph):
    positions, normals, colors, indices = [], [], [], []
    ratios = plan_ratios(root, BUDGET['floor'] if str(root.get('category')) == 'floor' else BUDGET['boss'] if root.get('boss') else BUDGET['default'])
    lookup = {}
    inverse = root.matrix_world.inverted()
    for ob in descendants(root):
        if ob.type != 'MESH' or ob.hide_render: continue
        r = ratios.get(ob.name, 1.0); mod = None
        if r < 0.999:
            mod = ob.modifiers.new('EXPORT_DECIMATE', 'DECIMATE'); mod.ratio = r; mod.decimate_type = 'COLLAPSE'
            bpy.context.view_layer.update()
        depsgraph = bpy.context.evaluated_depsgraph_get()
        evaluated = ob.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        mesh.calc_loop_triangles()
        matrix = inverse @ ob.matrix_world
        normal_matrix = matrix.to_3x3().inverted().transposed()
        slot_colors = [material_color(m) for m in mesh.materials] or [material_color(None)]
        corner_normals = mesh.corner_normals
        for tri in mesh.loop_triangles:
            color = slot_colors[min(tri.material_index, len(slot_colors) - 1)]
            c8 = tuple(max(0, min(255, int(round(v * 255)))) for v in color)
            order = (tri.loops[0], tri.loops[2], tri.loops[1])
            for loop in order:
                vi = mesh.loops[loop].vertex_index
                p = matrix @ mesh.vertices[vi].co
                n = (normal_matrix @ Vector(corner_normals[loop].vector)).normalized()
                pu = (round(p.x, 4), round(p.z, 4), round(p.y, 4))
                nu = tuple(max(-127, min(127, int(round(v * 127)))) for v in (n.x, n.z, n.y))
                key = (pu, nu, c8)
                idx = lookup.get(key)
                if idx is None:
                    idx = len(positions); lookup[key] = idx
                    positions.append(pu); normals.append(nu); colors.append(c8)
                indices.append(idx)
        evaluated.to_mesh_clear()
        if mod is not None: ob.modifiers.remove(mod)
    return positions, normals, colors, indices

depsgraph = bpy.context.evaluated_depsgraph_get()
roots = sorted((o for o in bpy.data.objects if o.type == 'EMPTY' and o.name.startswith('PIECE_') and 'category' in o), key=lambda o: o.name)
catalog, blob = [], bytearray()
blob += b'SKIT' + struct.pack('<II', 1, 0)
count = 0
for root in roots:
    raw = root.name[len('PIECE_'):]
    pid = PACK + '_' + raw
    category = str(root['category']); blocks = bool(root['blocks_movement'])
    positions, normals, colors, indices = bake(root, depsgraph)
    if not indices:
        print('SKIPPED (no geometry):', raw); continue
    key = pid.encode('utf-8')
    blob += struct.pack('<H', len(key)) + key + struct.pack('<II', len(positions), len(indices))
    for p in positions: blob += struct.pack('<3f', *p)
    for n in normals: blob += struct.pack('<3bb', n[0], n[1], n[2], 0)
    for c in colors: blob += struct.pack('<4B', *c)
    for i in indices: blob += struct.pack('<I', i)
    ys = [p[1] for p in positions]
    catalog.append(dict(id=pid, name=display_name(raw), role=ROLE_OVERRIDE.get(raw) or role_of(category, blocks, raw), blocks=blocks,
                        category=category, pack=PACK, footprint=footprint_of(root), tier=('boss' if raw.startswith('boss_') else 'enemy'), note=str(root.get('note', '')), height=round(max(ys), 3), vertices=len(positions), triangles=len(indices) // 3))
    count += 1
blob[8:12] = struct.pack('<I', count)
with open(os.path.join(OUT, 'kit_%s.bytes' % PACK), 'wb') as f: f.write(blob)
with open(os.path.join(OUT, 'catalog_%s.json' % PACK), 'w', encoding='utf-8') as f:
    json.dump(dict(pack=PACK, title=TITLE, pieces=catalog), f, indent=1)
print('EXPORTED', PACK, count, 'pieces,', len(blob), 'bytes')
for entry in catalog: print(' ', entry['id'], '|', entry['name'], '|', entry['role'], '| blocks' if entry['blocks'] else '| open', '|', entry['triangles'], 'tris')
