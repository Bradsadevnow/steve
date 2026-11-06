"""Dungeon bosses. Exec after boss_helpers. Front is -Y."""

def _coins(b, rnd, n, cx, cy, spread, base_z=.04, mats=None):
    mats = mats or [GOLD, GLOW_GOLD]
    for i in range(n):
        a = rnd.uniform(0, 6.283); r = rnd.uniform(0, spread) ** .8 * 1.0
        x, y = cx + math.cos(a) * r * 1.4, cy + math.sin(a) * r
        z = base_z + .06 * rnd.random() + max(0, (1 - r / spread)) * .25
        b.cyl('coin', (x, y, z), .2, .05, mats[0] if rnd.random() < .85 else mats[1], rot=(rnd.uniform(-35, 35), rnd.uniform(-35, 35), rnd.uniform(0, 180)), bevel=.008, verts=14)


def build_mimic_queen():
    b = Boss('boss_mimic_queen', 'dungeon', 'A treasure chest wearing a crown, with too many teeth and a tongue she uses as a flail. Wields a scepter and a sack of coins.')
    rnd = random.Random(7)
    # --- body: lion-footed chest
    b.box('base', (0, 0, .95), (4.2, 3.0, 1.6), WOOD, bevel=.12)
    for x in (-1.6, 0, 1.6): b.box('board', (x, -1.52, .95), (1.3, .06, 1.5), WOOD_DK if x == 0 else WOOD_LT, bevel=.03)
    for x in (-1.35, 1.35): b.box('band', (x, 0, .95), (.22, 3.12, 1.66), IRON, bevel=.04)
    for sx in (-1, 1):
        for sy in (-1, 1): b.box('corner', (sx * 2.08, sy * 1.46, .95), (.26, .26, 1.7), GOLD, bevel=.05)
    b.box('lock plate', (0, -1.57, 1.15), (.9, .1, 1.0), GOLD, bevel=.04); b.ball('keyhole', (0, -1.64, 1.2), (.14, .06, .2), BLACK)
    b.box('rim', (0, 0, 1.74), (4.3, 3.1, .14), GOLD, bevel=.04)
    b.box('mouth', (0, 0, 1.78), (3.9, 2.7, .08), DARKRED, bevel=0)
    # lower teeth: front row big, side rows smaller
    for i in range(13):
        x = -1.8 + i * .3; b.cyl('tooth', (x, -1.34, 1.95), .08, .38 + .1 * (i % 2), BONE, r2=0.01, bevel=0, verts=8)
    for sx in (-1, 1):
        for i in range(8): b.cyl('tooth', (sx * 1.92, -1.1 + i * .3, 1.92), .07, .3, BONE, r2=0.01, bevel=0, verts=8)
    # legs: lion paws with claws
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = sx * 1.65, sy * 1.05
            b.tube('thigh', [(x, y, .3), (x * 1.08, y + sy * .15, .65), (x * 1.04, y, 0.2)], .27, .2, WOOD_DK)
            b.ball('paw', (x * 1.06, y - .1, .2), (.42, .5, .22), WOOD_DK)
            for c in (-1, 0, 1): b.cyl('claw', (x * 1.06 + c * .17, y - .55, .12), .06, .3, BONE, r2=0.008, rot=(100, 0, 0), bevel=0, verts=8)
    # --- tongue: big flail tongue lolling out of the mouth
    b.sweep('tongue', [(0, -.2, 1.85), (0, -1.2, 2.25), (.4, -2.2, 1.2), (.3, -2.9, .35), (-.5, -2.6, .1), (-.9, -2.0, .12)],
            lambda t: (.5 * (1 - .35 * t), .13), (1, 0, 0), PINK, sides=12)
    b.ball('tongue tip', (-.9, -2.0, .18), (.34, .34, .2), PINK)
    # --- lid: hinged at the back, thrown open
    b.hold('lid', loc=(0, 1.5, 1.72), rot=(-62, 0, 0))
    b.box('lid slab', (0, -1.5, .32), (4.2, 3.0, .64), WOOD_LT, bevel=.28, seg=4)
    for x in (-1.35, 1.35): b.box('lid band', (x, -1.5, .34), (.22, 3.1, .72), IRON, bevel=.04)
    b.box('lid rim', (0, -3.0, .3), (4.3, .16, .7), GOLD, bevel=.05)
    for i in range(13): b.cyl('tooth up', (-1.8 + i * .3, -2.86, -.2), .08, .4 + .1 * (i % 2), BONE, r2=0.01, rot=(180, 0, 0), bevel=0, verts=8)
    for sx in (-1, 1):
        for i in range(8): b.cyl('tooth up', (sx * 1.96, -.5 - i * .3, -.18), .07, .32, BONE, r2=0.01, rot=(180, 0, 0), bevel=0, verts=8)
    # eyes on the lid underside
    for k, (x, y, r) in enumerate([(-1.2, -1.2, .34), (-.4, -1.8, .46), (.55, -1.3, .38), (1.3, -2.0, .3), (0.05, -.6, .24), (-1.55, -2.2, .24)]):
        b.eye('eye%d' % k, (x, y, -.05), r, look=(0, 0, -1), iris=IRIS_GREEN)
    b.release()
    # crown: perched on the lid tip, kept upright in world space
    b.hold('crown', loc=(0, 1.5 + 3.0 * math.cos(math.radians(62)) * -1 + 0, 1.72 + 3.0 * math.sin(math.radians(62))), rot=(0, 0, 0))
    b.cyl('crown ring', (0, 0, .25), .95, .5, GOLD, bevel=.03); b.cyl('crown band', (0, 0, .06), 1.0, .14, GOLD, bevel=.02)
    for k in range(7):
        a = k * 2 * math.pi / 7; b.cyl('crown spike', (math.cos(a) * .85, math.sin(a) * .85, .78), .16, .72, GOLD, r2=.02, bevel=0, verts=8)
        b.ball('crown gem', (math.cos(a) * .85, math.sin(a) * .85, 1.2), .1, GLOW_RED if k % 2 else GEM_BLUE)
    b.ball('crown jewel', (0, -.98, .3), (.2, .1, .2), GLOW_RED)
    b.release()
    # --- weapons: a scepter on the left, a coin-sack flail on the right, each held by a tongue-tentacle
    # scepter (stupidly oversized, topped with a ruby and a salad fork)
    b.cyl('scepter shaft', (-2.9, -1.3, 2.2), .1, 4.4, GOLD, bevel=.01)
    b.ball('scepter orb', (-2.9, -1.3, 4.6), .42, GLOW_RED)
    for k in range(5):
        a = k * 2 * math.pi / 5; b.cyl('scepter prong', (-2.9 + math.cos(a) * .3, -1.3 + math.sin(a) * .3, 4.95), .06, .6, GOLD, r2=.01, bevel=0, verts=8)
    b.torus('scepter ring', (-2.9, -1.3, 4.3), .5, .05, GOLD, rot=(75, 0, 20))
    b.sweep('tentacle L', [(-1.9, -.4, 1.9), (-2.8, -.5, 2.6), (-3.1, -1.0, 2.4), (-2.9, -1.3, 2.0)], lambda t: (.2 - .07 * t, .2 - .07 * t), (0, 0, 1), PINK, sides=10)
    b.torus('grip L', (-2.9, -1.3, 2.0), .17, .09, PINK, rot=(0, 0, 0)); b.torus('grip L2', (-2.9, -1.3, 2.3), .17, .08, PINK, rot=(0, 0, 0))
    # flail: chain of links to a spiked sack of coins
    b.sweep('tentacle R', [(1.9, -.4, 1.9), (2.8, -.7, 2.7), (3.0, -1.3, 3.0), (2.9, -1.9, 2.8)], lambda t: (.2 - .07 * t, .2 - .07 * t), (0, 0, 1), PINK, sides=10)
    for i in range(5): b.torus('link', (2.9, -1.95, 2.65 - i * .2), .12, .035, IRON, rot=(90 * (i % 2), 90 * ((i + 1) % 2), 0))
    b.blob('coin sack', (2.9, -1.95, .95), (.85, .85, .85), WOOD_LT, seed=3, amp=.2)
    b.cyl('sack tie', (2.9, -1.95, 1.7), .3, .16, RED, bevel=.02)
    for k in range(12):
        a = k * 2.399963; e = math.asin(rnd.uniform(-.8, .9)); ca, sa, ce, se = math.cos(a), math.sin(a), math.cos(e), math.sin(e)
        d = Vector((ca * ce, sa * ce, se)); b.cyl('sack spike', Vector((2.9, -1.95, .95)) + d * 1.1, .09, .55, STEEL, r2=.01, rot=tuple(math.degrees(x) for x in Vector((0, 0, 1)).rotation_difference(d).to_euler()), bevel=0, verts=8)
    _coins(b, rnd, 14, 2.9, -1.95, .7, base_z=.02)
    # hoard spilling around her
    _coins(b, rnd, 48, -.9, -2.3, 1.4); _coins(b, rnd, 20, 1.7, -2.2, 1.0)
    for k in range(9):
        b.ball('gem', (rnd.uniform(-1.9, 1.9), rnd.uniform(-2.7, -1.9), .22), (.16, .16, .22), [GEM_BLUE, GEM_GREEN, GLOW_RED][k % 3])
    return b


def build_mimic_queen_mini():
    """A tiny mimic queen: a minion, 1 cell, same silhouette."""
    b = Boss('enemy_mimic_queen_mini', 'dungeon', 'A tiny mimic queen: a chest the size of a footstool in a crown, snapping at ankles.', cells=1)
    b.box('base', (0, 0, .32), (1.05, .76, .42), WOOD, bevel=.04)
    for x in (-.4, .4): b.box('band', (x, 0, .32), (.07, .8, .45), IRON, bevel=.015)
    b.box('rim', (0, 0, .55), (1.1, .8, .05), GOLD, bevel=.015); b.box('mouth', (0, 0, .57), (.95, .66, .03), DARKRED, bevel=0)
    b.box('lock', (0, -.4, .36), (.22, .04, .26), GOLD, bevel=.015)
    for i in range(7): b.cyl('tooth', (-.45 + i * .15, -.34, .66), .03, .16 + .04 * (i % 2), BONE, r2=.004, bevel=0, verts=6)
    for sx in (-1, 1):
        for sy in (-1, 1): b.ball('paw', (sx * .42, sy * .26, .06), (.12, .14, .07), WOOD_DK)
    b.sweep('tongue', [(0, -.05, .6), (0, -.3, .75), (.1, -.55, .3), (.05, -.7, .06)], lambda t: (.13 * (1 - .3 * t), .035), (1, 0, 0), PINK, sides=8)
    b.hold('lid', loc=(0, .38, .58), rot=(-58, 0, 0))
    b.box('lid', (0, -.38, .09), (1.05, .76, .16), WOOD_LT, bevel=.06, seg=3)
    for i in range(7): b.cyl('tooth up', (-.45 + i * .15, -.7, -.05), .03, .14, BONE, r2=.004, rot=(180, 0, 0), bevel=0, verts=6)
    b.eye('eye0', (-.2, -.3, -.02), .1, look=(0, 0, -1), iris=IRIS_GREEN); b.eye('eye1', (.2, -.4, -.02), .13, look=(0, 0, -1), iris=IRIS_GREEN)
    b.release()
    b.hold('crown', loc=(0, .38 - .76 * math.cos(math.radians(58)), .58 + .76 * math.sin(math.radians(58))))
    b.cyl('ring', (0, 0, .08), .26, .14, GOLD, bevel=.01)
    for k in range(5): a = k * 6.283 / 5; b.cyl('spike', (math.cos(a) * .22, math.sin(a) * .22, .2), .05, .2, GOLD, r2=.01, bevel=0, verts=6)
    b.ball('gem', (0, -.27, .1), .05, GLOW_RED)
    b.release()
    # a toothpick-sized scepter
    b.cyl('scepter', (-.62, -.28, .5), .02, 1.0, GOLD, bevel=0, verts=8); b.ball('orb', (-.62, -.28, 1.04), .07, GLOW_RED)
    b.sweep('arm', [(-.4, -.1, .5), (-.55, -.2, .5), (-.62, -.28, .45)], lambda t: (.04, .04), (0, 0, 1), PINK, sides=6)
    return b


COAT = mat('Coat black', (.05, .05, .09, 1), 0, .6); COAT_LT = mat('Coat / sheen', (.12, .1, .2, 1), .3, .35)
SKIN = mat('Skin sparkle', (.8, .76, .94, 1), 0, .3, .08); HAIR_DK = mat('Hair dark', (.22, .12, .06, 1), 0, .4); HAIR = mat('Hair bronze', (.5, .3, .14, 1), .2, .35)
CAPE = mat('Cape violet', (.2, .05, .32, 1), 0, .5); LINING = mat('Cape lining', (.7, .06, .34, 1), 0, .4)
SPARKS = [GLOW_PINK, GLOW_TEAL, GLOW_GOLD, GLOW_VIOLET]


def _diamond(b, n, loc, s, m, rot=(0, 0, 0)):
    """A little four-sided sparkle: two cones base to base."""
    x, y, z = loc
    b.cyl(n, (x, y, z + s * .5), s * .5, s, m, r2=.0, bevel=0, verts=4, rot=rot); b.cyl(n, (x, y, z - s * .5), s * .5, s, m, r2=.0, bevel=0, verts=4, rot=(180 + rot[0], rot[1], rot[2]))


def build_count_glitterfang():
    b = Boss('boss_glitterfang', 'dungeon', 'Count Glitterfang the Brooding: a very pale, very sparkly vampire. Wields a rhinestone baseball bat and a cape of bats.')
    rnd = random.Random(13)
    # boots and legs
    for sx in (-1, 1):
        x = sx * .5
        b.box('boot', (x, -.35, .25), (.62, 1.3, .5), COAT, bevel=.1); b.box('boot cuff', (x, 0, .6), (.6, .66, .2), COAT_LT, bevel=.04)
        b.cyl('leg', (x, 0, 1.5), .26, 1.9, COAT, r2=.32, bevel=.02)
    b.box('hips', (0, 0, 2.55), (1.5, .8, .6), COAT, bevel=.1); b.box('belt', (0, -.01, 2.78), (1.55, .84, .14), COAT_LT, bevel=.03); b.box('buckle', (0, -.45, 2.78), (.3, .06, .18), GOLD, bevel=.02)
    # torso: long dark coat, open at the chest to show glittering pale skin
    b.blob('coat', (0, 0, 3.4), (.95, .55, 1.0), COAT, seed=2, amp=.06)
    b.blob('chest', (0, -.38, 3.55), (.42, .22, .68), SKIN, seed=3, amp=.04)
    for sx in (-1, 1): b.box('lapel', (sx * .5, -.42, 3.5), (.32, .08, 1.15), COAT_LT, bevel=.03, rot=(0, 0, sx * -14))
    for k in range(14): _diamond(b, 'chest glint', (rnd.uniform(-.3, .3), -.58, 3.2 + rnd.uniform(0, .8)), .09, SPARKS[k % 4], rot=(90, 0, 0))
    # arms: right arm raised holding the bat, left hand clasping the collar
    b.ball('shoulder R', (1.05, 0, 4.05), (.36, .34, .34), COAT); b.ball('shoulder L', (-1.05, 0, 4.05), (.36, .34, .34), COAT)
    b.tube('arm R', [(1.1, 0, 4.0), (1.7, -.3, 3.5), (1.9, -.9, 3.0)], .24, .2, COAT)
    b.ball('hand R', (1.95, -1.0, 2.95), (.24, .28, .24), SKIN)
    b.tube('arm L', [(-1.1, 0, 4.0), (-1.3, -.4, 3.4), (-.55, -.7, 4.05)], .24, .2, COAT)
    b.ball('hand L', (-.4, -.72, 4.15), (.26, .2, .22), SKIN)
    for k in range(4): b.tube('finger', [(-.5 + k * .08, -.82, 4.2), (-.4 + k * .08, -.9, 4.4)], .04, .035, SKIN, sides=6)
    # head
    b.cyl('neck', (0, 0, 4.3), .26, .4, SKIN, bevel=0)
    b.blob('head', (0, 0, 4.85), (.55, .5, .66), SKIN, seed=4, amp=.025)
    b.cyl('nose', (0, -.45, 4.8), .06, .18, SKIN, r2=.02, rot=(100, 0, 0), bevel=0, verts=10)
    for sx in (-1, 1):
        b.eye('eye', (sx * .22, -.42, 4.95), .21, look=(0, -1, 0), iris=IRIS_AMBER)
        b.box('brow', (sx * .24, -.46, 5.22), (.36, .08, .09), HAIR_DK, bevel=.02, rot=(0, 0, sx * -20))
        b.cyl('fang', (sx * .09, -.4, 4.48), .045, .2, WHITE, r2=.005, rot=(180, 0, 0), bevel=0, verts=8)
        b.cyl('ear', (sx * .5, 0, 4.9), .1, .32, SKIN, r2=.01, rot=(0, sx * -30, 0), bevel=0, verts=8)
    b.box('smirk', (0, -.44, 4.55), (.28, .04, .05), DARKRED, bevel=.01, rot=(0, 0, 6))
    for k in range(16): a = rnd.uniform(0, 6.28); _diamond(b, 'cheek glint', (math.cos(a) * .47 * rnd.uniform(.6, 1), -.4 - abs(math.sin(a)) * .08, 4.85 + rnd.uniform(-.3, .3)), .05, SPARKS[k % 4], rot=(90, 0, 0))
    # sweeping hair with a pompadour and a lock over one eye
    b.blob('hair', (0, .1, 5.25), (.56, .52, .36), HAIR, seed=6, amp=.1)
    b.sweep('pompadour', [(0, -.1, 5.4), (0, -.5, 5.75), (0, -.9, 5.6)], lambda t: (.3 * (1 - .3 * t), .2), (1, 0, 0), HAIR, sides=8)
    b.sweep('lock', [(.15, -.35, 5.3), (.3, -.55, 5.0), (.22, -.5, 4.78)], lambda t: (.1, .06), (1, 0, 0), HAIR, sides=6)
    # cape: huge collar and a wide spread behind
    for sx in (-1, 1):
        b.box('collar', (sx * .6, .25, 4.7), (.1, .7, 1.3), CAPE, bevel=.03, rot=(-8, 0, sx * -16))
        b.box('collar lining', (sx * .56, .12, 4.7), (.05, .66, 1.2), LINING, bevel=.01, rot=(-8, 0, sx * -16))
        b.sweep('cape', [(sx * .9, .35, 4.0), (sx * 1.7, 1.0, 2.8), (sx * 2.6, 1.7, 1.2), (sx * 2.8, 1.6, .15)], lambda t: (.9 + 1.0 * t, .05), (0, 1, 0), CAPE, sides=6)
        b.sweep('cape lining', [(sx * .9, .3, 4.0), (sx * 1.7, .94, 2.8), (sx * 2.6, 1.64, 1.2), (sx * 2.8, 1.54, .15)], lambda t: (.85 + 1.0 * t, .04), (0, 1, 0), LINING, sides=6)
    b.box('cape back', (0, .9, 2.6), (2.4, .06, 3.4), CAPE, bevel=.02, rot=(8, 0, 0))
    # weapon: an enormous rhinestone baseball bat
    d = Vector((math.sin(math.radians(18)), 0, math.cos(math.radians(18)))); base = Vector((2.45, -1.1, 4.1)) - d * 1.7
    b.cyl('bat', (2.45, -1.1, 4.1), .13, 3.4, WOOD_LT, r2=.4, rot=(0, 18, -4), bevel=.02, verts=24)
    b.cyl('bat knob', base - d * .05, .2, .16, WOOD_DK, rot=(0, 18, -4), bevel=.03)
    for k in range(60):
        t = rnd.uniform(.35, 1.0); a = rnd.uniform(0, 6.28); r = .13 + .27 * t
        p = base + d * (3.4 * t) + Vector((math.cos(a) * r * 1.05, math.sin(a) * r * 1.05, 0)); b.ball('rhinestone', p, .07, SPARKS[k % 4])
    b.cyl('bat banding', base + d * 1.0, .2, .12, GOLD, r2=.22, bevel=.02, rot=(0, 18, -4))
    # glitter cloud, and a few little bats on strings
    for k in range(64):
        a = rnd.uniform(0, 6.28); r = rnd.uniform(1.7, 3.3); _diamond(b, 'glitter', (math.cos(a) * r, abs(math.sin(a)) * r * .8 + .2 if math.sin(a) < 0 and r < 2.2 else math.sin(a) * r * .8, rnd.uniform(.4, 6.2)), rnd.uniform(.14, .3), SPARKS[k % 4], rot=(rnd.uniform(0, 40), 0, rnd.uniform(0, 90)))
    for k, (x, y, z) in enumerate([(-2.4, -1.4, 4.9), (2.9, 1.2, 5.2), (-1.0, 1.6, 5.8), (1.4, -1.7, 5.7)]):
        b.ball('bat body', (x, y, z), (.18, .14, .2), COAT)
        for sx in (-1, 1): b.box('bat wing', (x + sx * .32, y, z + .04), (.5, .03, .22), COAT, bevel=.01, rot=(0, sx * 22, sx * -10))
        b.eye('bat eye', (x, y - .12, z + .06), .05, look=(0, -1, 0), iris=GLOW_RED)
    return b


MOLD = mat('Mold mint', (.55, .86, .52, 1), 0, .9); MOLD_DK = mat('Mold deep', (.25, .55, .34, 1), 0, .9)
HAT = mat('Wizard hat', (.28, .12, .5, 1), 0, .6); INK = mat('Ink', (.03, .03, .09, 1), .3, .12); CREAM = mat('Feather cream', (.96, .93, .82, 1), 0, .5)
FEATHER_BLUE = mat('Feather blue', (.25, .5, .95, 1), 0, .5); GHOST = mat('Ghost cloth', (.85, .88, .92, 1), 0, .7)
SPINES = [mat('Book red', (.7, .12, .16, 1)), mat('Book teal', (.1, .5, .52, 1)), mat('Book purple', (.4, .22, .62, 1)), mat('Book mustard', (.85, .62, .15, 1)), mat('Book green', (.18, .45, .24, 1)), mat('Book navy', (.12, .18, .45, 1))]


def build_archivist_mold():
    b = Boss('boss_archivist_mold', 'dungeon', 'Grand Archivist Mold: a floating bookshelf wizard with a spore-cloud head. Fights with an OVERDUE rubber stamp and a dripping quill.')
    rnd = random.Random(21)
    z0 = .9   # floats above the floor
    # shelf carcass
    b.box('back', (0, .4, z0 + 2.0), (2.7, .24, 4.1), WOOD_DK, bevel=.05)
    for sx in (-1, 1): b.box('side', (sx * 1.38, 0, z0 + 2.0), (.2, 1.0, 4.1), WOOD, bevel=.05)
    for i in range(6): b.box('shelf', (0, 0, z0 + .06 + i * .78), (2.7, 1.0, .14), WOOD_LT, bevel=.04)
    b.box('cornice', (0, -.05, z0 + 4.26), (3.1, 1.2, .26), GOLD, bevel=.06); b.box('plinth', (0, -.05, z0 - .1), (3.0, 1.15, .22), WOOD_DK, bevel=.05)
    # books
    for row in range(5):
        x = -1.2
        while x < 1.15:
            w = rnd.uniform(.16, .28); h = rnd.uniform(.5, .72); gap = rnd.random()
            if gap < .08: x += .3; continue
            lean = rnd.uniform(-14, 14) if rnd.random() < .18 else 0
            b.box('book', (x + w / 2, -.05, z0 + .13 + row * .78 + h / 2 + .02), (w, .66, h), SPINES[rnd.randrange(6)], bevel=.02, rot=(0, lean, 0)); x += w + .015
    # a glowing crack in the shelf and mold creeping over everything
    b.box('crack glow', (-.2, -.52, z0 + 2.2), (.07, .02, 1.5), GLOW_GREEN, bevel=0, rot=(0, 12, 0))
    for i, (x, z, s) in enumerate([(-1.2, z0 + 3.5, .5), (1.2, z0 + 1.2, .45), (.6, z0 + 4.4, .5), (-.9, z0 + .4, .4), (1.4, z0 + 3.0, .35)]):
        b.blob('mold patch', (x, -.45, z), (s, s * .5, s * .8), MOLD, seed=i + 1, amp=.22)
    for i in range(10):
        x = rnd.uniform(-1.3, 1.3); z = z0 + rnd.choice([4.38, 1.5, 2.3, .15]) 
        b.cyl('stem', (x, -.3, z + .15), .05, .3, CREAM, bevel=0, verts=8); b.ball('cap', (x, -.3, z + .35), (.17, .17, .1), [RED, GLOW_PINK, GLOW_TEAL][i % 3])
    # floating base: dangling bookmarks and an ink pool with toadstools
    for k in range(7):
        x = -1.1 + k * .37; b.sweep('bookmark', [(x, -.1, z0 - .2), (x + rnd.uniform(-.2, .2), -.2, z0 - .8), (x + rnd.uniform(-.3, .3), -.1, z0 - 1.1)], lambda t: (.06, .015), (1, 0, 0), [RED, GOLD, GLOW_TEAL][k % 3], sides=4)
    b.blob('ink pool', (0, -.3, 0), (2.3, 1.7, .22), INK, seed=2, amp=.1, floor=0)
    for k in range(9):
        a = rnd.uniform(0, 6.28); r = rnd.uniform(1.4, 2.4); x, y = math.cos(a) * r, math.sin(a) * r * .8; hh = rnd.uniform(.25, .6)
        b.cyl('toadstool stem', (x, y, hh / 2), .07, hh, CREAM, bevel=0, verts=8); b.ball('toadstool cap', (x, y, hh), (.24, .24, .14), [RED, GLOW_PINK, MOLD][k % 3])
    # head: a boiling cloud of mould and spores with half-moon glasses and a wizard hat
    hz = z0 + 5.05
    for i, (x, y, z, s) in enumerate([(0, 0, 0, 1.0), (-.65, -.1, -.15, .65), (.65, -.1, -.15, .65), (-.4, -.25, .45, .6), (.45, -.2, .4, .6), (0, -.4, -.35, .55), (-.3, .3, .1, .6), (.3, .3, .1, .6)]):
        b.blob('cloud', (x, y, hz + z), (s, s, s * .9), MOLD, seed=i + 9, amp=.14, sub=2)
    for k in range(18):
        a = rnd.uniform(0, 6.28); e = rnd.uniform(-.4, 1.0); d = Vector((math.cos(a) * math.cos(e), math.sin(a) * math.cos(e), math.sin(e)))
        b.ball('puff', Vector((0, 0, hz)) + d * rnd.uniform(1.0, 1.35), rnd.uniform(.08, .16), MOLD_DK if k % 2 else GLOW_GREEN)
    for sx in (-1, 1):
        b.eye('eye', (sx * .34, -.88, hz + .05), .24, look=(0, -1, 0), iris=IRIS_AMBER)
        b.torus('lens', (sx * .34, -.95, hz + .05), .3, .04, GOLD, rot=(90, 0, 0))
    b.box('glasses bridge', (0, -.95, hz + .12), (.2, .04, .05), GOLD, bevel=.01)
    b.torus('shush mouth', (0, -.92, hz - .42), .17, .06, DARKRED, rot=(90, 0, 0))
    for k in range(7):
        x = -.45 + k * .15; b.sweep('beard', [(x, -.8, hz - .6), (x * 1.1, -.95, hz - 1.1), (x * 1.2, -.9, hz - 1.7 + abs(k - 3) * .15)], lambda t: (.09 * (1 - .6 * t), .09 * (1 - .6 * t)), (1, 0, 0), MOLD, sides=6)
    b.cyl('hat brim', (0, 0, hz + 1.05), 1.35, .1, HAT, bevel=.03); b.cyl('hat', (0, 0, hz + 1.9), .95, 1.6, HAT, r2=.1, bevel=.03)
    b.sweep('hat tip', [(0, 0, hz + 2.6), (0, .3, hz + 3.1), (0, .9, hz + 3.1)], lambda t: (.12 * (1 - .8 * t), .12 * (1 - .8 * t)), (1, 0, 0), HAT, sides=8)
    b.cyl('hat band', (0, 0, hz + 1.25), 1.08, .16, GOLD, r2=1.05, bevel=.01)
    for k in range(6): a = k * 1.05; b.ball('hat star', (math.cos(a) * .72, math.sin(a) * .72 - .4, hz + 1.6 + (k % 3) * .3), .06, GLOW_GOLD)
    # ghostly arms
    for sx in (-1, 1):
        b.ball('sleeve shoulder', (sx * 1.5, 0, z0 + 3.5), (.3, .3, .3), GHOST)
        b.tube('arm', [(sx * 1.5, 0, z0 + 3.4), (sx * 2.1, -.5, z0 + 2.8), (sx * 2.3, -1.1, z0 + 2.3)], .22, .16, GHOST)
        b.ball('glove', (sx * 2.3, -1.15, z0 + 2.25), (.26, .26, .26), CREAM)
    # right: OVERDUE rubber stamp mace
    b.cyl('stamp handle', (2.3, -1.15, z0 + 2.9), .1, 1.9, WOOD_DK, bevel=.02)
    b.box('stamp block', (2.3, -1.15, z0 + 4.1), (1.5, 1.0, .75), WOOD_LT, bevel=.1); b.box('stamp pad', (2.3, -1.67, z0 + 4.1), (1.35, .06, .6), RED, bevel=.01)
    for k in range(7): b.box('letter', (2.3 - .52 + k * .17, -1.72, z0 + 4.1), (.09, .03, .3), WHITE, bevel=0)
    b.cyl('stamp collar', (2.3, -1.15, z0 + 3.55), .2, .15, GOLD, bevel=.02)
    # left: a giant quill, dripping ink
    b.cyl('quill shaft', (-2.5, -1.2, z0 + 3.1), .06, 4.2, CREAM, r2=.04, rot=(0, -4, 0), bevel=0, verts=10)
    for sx in (-1, 1):
        b.blob('vane', (-2.5 + sx * .5, -1.2, z0 + 4.2), (.55, .07, 1.9), FEATHER_BLUE if sx < 0 else CREAM, seed=3 + sx, amp=.05, sub=3, rot=(0, 0, sx * -9))
        for k in range(7): b.cyl('barb', (-2.5 + sx * (.35 + .18 * (k % 2)), -1.2, z0 + 2.6 + k * .4), .02, .5, CREAM if sx < 0 else FEATHER_BLUE, r2=.004, rot=(0, sx * 70, 0), bevel=0, verts=6)
    b.cyl('nib', (-2.6, -1.2, z0 + .8), .09, .5, INK, r2=.01, rot=(180, 0, 0), bevel=0, verts=8)
    for k, (dz, s) in enumerate([(.25, .07), (-.25, .09), (-.8, .06)]): b.ball('ink drip', (-2.6, -1.2, z0 + dz), (s, s, s * 1.4), INK)
    b.blob('ink spill', (-2.6, -1.25, 0), (.7, .6, .1), INK, seed=4, amp=.1, floor=0)
    # floating spores
    for k in range(30):
        a = rnd.uniform(0, 6.28); r = rnd.uniform(1.6, 3.2); b.ball('spore', (math.cos(a) * r, math.sin(a) * r * .8, rnd.uniform(1, 7)), rnd.uniform(.05, .13), GLOW_GREEN if k % 2 else MOLD)
    return b
