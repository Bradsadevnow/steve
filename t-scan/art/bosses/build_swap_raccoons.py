"""Swap meet boss: Big Raccoon Energy. Exec after boss_helpers, build_dungeon and build_swap (shared materials). Front is -Y."""

RACCOON = mat('Raccoon fur', (.46, .46, .52, 1), 0, .9); RACCOON_DK = mat('Raccoon dark', (.1, .1, .13, 1), 0, .9); RACCOON_LT = mat('Raccoon light', (.92, .9, .88, 1), 0, .9)
COAT_TAN = mat('Trench tan', (.74, .6, .36, 1), 0, .8); COAT_SHADE = mat('Trench shade', (.55, .43, .24, 1), 0, .8); FEDORA = mat('Fedora brown', (.3, .2, .12, 1), 0, .7)
FISH = mat('Fish silver', (.6, .72, .85, 1), .6, .25); CHICKEN = mat('Chicken gold', (.8, .5, .15, 1), 0, .5); CRUST = mat('Pizza cheese', (.98, .78, .22, 1), 0, .5)
TRASH = mat('Trash lid', (.45, .5, .52, 1), .6, .45)


def _raccoon_head(b, c, s=1.0, hat=False, shades=False, seed=1):
    x, y, z = c
    b.blob('head', (x, y, z), (.9 * s, .8 * s, .78 * s), RACCOON, seed=seed, amp=.05)
    b.blob('muzzle', (x, y - .6 * s, z - .2 * s), (.45 * s, .4 * s, .32 * s), RACCOON_LT, seed=2, amp=.04)
    b.ball('nose', (x, y - .98 * s, z - .1 * s), (.17 * s, .13 * s, .13 * s), BLACK)
    for sx in (-1, 1):
        b.blob('mask', (x + sx * .38 * s, y - .62 * s, z + .12 * s), (.32 * s, .14 * s, .22 * s), RACCOON_DK, seed=3, amp=.05, rot=(0, 0, sx * -18))
        b.eye('eye', (x + sx * .36 * s, y - .76 * s, z + .16 * s), .17 * s, look=(0, -1, 0), iris=IRIS_AMBER)
        b.ball('ear', (x + sx * .62 * s, y + .05 * s, z + .66 * s), (.27 * s, .18 * s, .3 * s), RACCOON); b.ball('ear in', (x + sx * .62 * s, y - .08 * s, z + .66 * s), (.17 * s, .1 * s, .2 * s), PINK)
        b.cyl('cheek tuft', (x + sx * .85 * s, y - .25 * s, z - .25 * s), .14 * s, .35 * s, RACCOON_LT, r2=.01, rot=(0, sx * 70, 0), bevel=0, verts=8)
    if shades:
        for sx in (-1, 1): b.box('shade', (x + sx * .36 * s, y - .92 * s, z + .18 * s), (.42 * s, .05, .3 * s), BLACK, bevel=.05)
        b.box('shade bridge', (x, y - .92 * s, z + .22 * s), (.2 * s, .04, .05), BLACK, bevel=.01)
    if hat:
        b.cyl('hat brim', (x, y, z + .65 * s), 1.15 * s, .08 * s, FEDORA, bevel=.02); b.cyl('hat crown', (x, y, z + .95 * s), .72 * s, .6 * s, FEDORA, r2=.6 * s, bevel=.03)
        b.cyl('hat band', (x, y, z + .75 * s), .74 * s, .14 * s, RED, bevel=.01)


def build_raccoon_stack():
    b = Boss('boss_raccoon_stack', 'swap', 'Big Raccoon Energy: three raccoons in one trench coat, stacked three stories high. The one on top is in charge.')
    rnd = random.Random(41)
    # the coat: three flared tiers with belts and pleats
    for name, z, h, r, r2 in (('lower', 1.85, 2.5, 1.95, 1.55), ('middle', 4.35, 2.3, 1.55, 1.25), ('upper', 6.55, 2.0, 1.25, 1.0)):
        b.cyl('coat ' + name, (0, 0, z), r, h, COAT_TAN, r2=r2, bevel=.04, verts=40)
        for k in range(10):
            a = k * 6.283 / 10; rr = (r + r2) / 2; b.box('pleat', (math.cos(a) * rr, math.sin(a) * rr, z), (.06, .06, h * .95), COAT_SHADE, bevel=0, rot=(0, 0, math.degrees(a)))
        b.torus('belt ' + name, (0, 0, z + h / 2 - .1), r2 * 1.02, .12, FEDORA)
        b.torus('hem ' + name, (0, 0, z - h / 2 + .06), r * 1.0, .1, COAT_SHADE)
        b.box('buckle ' + name, (0, -r2 - .02, z + h / 2 - .1), (.3, .08, .26), GOLD, bevel=.03)
    b.cyl('collar', (0, 0, 7.7), 1.15, .4, COAT_SHADE, r2=1.3, bevel=.03, verts=32)
    for sx in (-1, 1): b.box('lapel', (sx * .6, -.95, 7.25), (.5, .1, 1.1), COAT_SHADE, bevel=.04, rot=(0, 0, sx * -22))
    # three raccoons: bottom and middle poke out of the coat front, the boss on top wears the hat
    _raccoon_head(b, (0, -1.35, 2.75), 1.0, seed=1)
    _raccoon_head(b, (0, -1.15, 5.0), .95, seed=2)
    _raccoon_head(b, (0, -.35, 8.25), 1.15, hat=True, shades=True, seed=3)
    b.blob('fake mustache', (0, -1.7, 7.7), (.6, .14, .14), HAIR_DK, seed=1, amp=.1, sub=2)
    # feet under the hem, paws out of the sleeves
    for sx in (-1, 1):
        b.ball('foot', (sx * .85, -1.65, .22), (.5, .7, .22), RACCOON_DK)
        for c in (-1, 0, 1): b.cyl('claw', (sx * .85 + c * .16, -2.28, .14), .05, .22, BONE, r2=.008, rot=(95, 0, 0), bevel=0, verts=8)

    def sleeve(pts, hand):
        b.tube('sleeve', pts, .42, .34, COAT_TAN); b.ball('paw', hand, (.42, .42, .4), RACCOON_DK)
        for c in (-1, 0, 1): b.cyl('finger', (hand[0] + c * .14, hand[1] - .3, hand[2] - .05), .05, .22, RACCOON_DK, r2=.04, rot=(90, 0, 0), bevel=0, verts=8)
    sleeve([(1.15, 0, 6.9), (2.0, -.4, 6.7), (2.5, -1.0, 6.3)], (2.55, -1.05, 6.3))
    sleeve([(-1.15, 0, 6.9), (-2.0, -.4, 6.7), (-2.5, -1.0, 6.4)], (-2.55, -1.05, 6.4))
    sleeve([(1.5, 0, 4.6), (2.3, -.4, 4.3), (2.8, -1.0, 4.0)], (2.85, -1.05, 4.0))
    sleeve([(-1.5, 0, 4.6), (-2.3, -.4, 4.3), (-2.8, -1.0, 4.0)], (-2.85, -1.05, 4.0))
    # top right: a giant fish used as a sword
    b.blob('fish', (3.4, -1.25, 8.3), (.42, .22, 1.7), FISH, seed=4, amp=.04, rot=(0, 18, 0))
    b.blob('fish belly', (3.3, -1.45, 8.1), (.3, .14, 1.4), WHITE, seed=5, amp=.03, rot=(0, 18, 0))
    b.cyl('fish tail', (2.85, -1.25, 6.75), 1.0, .14, FISH, r2=.12, bevel=0, rot=(90, 0, 18), verts=4)
    for k in range(9): b.ball('fish scale', (3.2 + (k % 3) * .12 - .1, -1.55, 7.2 + k * .22), (.09, .03, .09), WHITE)
    b.torus('fish mouth', (3.82, -1.35, 9.75), .16, .05, DARKRED, rot=(60, 0, 18))
    b.cyl('fish fin', (3.7, -1.25, 9.4), .35, .6, FISH, r2=.02, bevel=0, rot=(0, 18, 0), verts=4)
    b.eye('fish eye', (3.62, -1.5, 9.5), .18, look=(0, -1, 0), iris=IRIS_GREEN)
    b.cyl('fish gill', (3.45, -1.45, 9.0), .09, .5, RED, bevel=0, rot=(0, 18, 0), verts=8)
    # top left: dented trash-can lid shield
    b.cyl('trash lid', (-2.75, -1.35, 6.5), 1.25, .14, TRASH, rot=(90, 0, 0), bevel=.03, verts=36); b.torus('trash rim', (-2.75, -1.4, 6.5), 1.22, .07, TRASH, rot=(90, 0, 0))
    b.torus('lid handle', (-2.75, -1.55, 6.5), .3, .05, IRON, rot=(90, 0, 0))
    for k in range(5): a = k * 1.26; b.ball('dent', (-2.75 + math.cos(a) * .7, -1.4, 6.5 + math.sin(a) * .7), (.12, .03, .12), COAT_SHADE)
    for k in range(4): b.box('stain', (-3.1 + k * .35, -1.45, 6.8 - k * .2), (.25, .02, .08), RACCOON_DK, bevel=0)
    # middle right: pepperoni pizza slice shield
    b.cyl('pizza', (3.05, -1.5, 4.2), 1.35, .14, CRUST, rot=(90, 0, 180), verts=3, bevel=.02); b.cyl('pizza crust', (3.05, -1.5, 5.18), .12, 1.5, COAT_SHADE, rot=(0, 90, 0), bevel=0, verts=10)
    for dx, dz in [(0, 3.9), (.35, 4.35), (-.35, 4.35), (0, 4.8)]: b.cyl('pepperoni', (3.05 + dx, -1.62, dz), .2, .05, RED, rot=(90, 0, 0), bevel=0)
    # middle left: rotisserie chicken mace
    b.cyl('drumstick bone', (-3.2, -1.2, 3.6), .09, 1.6, BONE, rot=(0, -10, 0), bevel=.02, verts=10); b.ball('bone knob', (-3.5, -1.2, 2.85), .16, BONE)
    b.blob('chicken', (-3.55, -1.3, 5.0), (.95, .75, .85), CHICKEN, seed=6, amp=.08, rot=(0, -10, 0))
    for sx in (-1, 1): b.blob('chicken leg', (-3.55 + sx * .7, -1.6, 4.7), (.28, .28, .6), CHICKEN, seed=7, amp=.1, sub=2, rot=(40, 0, sx * 20))
    for k in range(6): b.box('grill mark', (-3.8 + k * .22, -1.95, 5.0 + (k % 2) * .12), (.1, .02, .3), COAT_SHADE, bevel=0, rot=(0, 0, 30))
    # ringed tail curling behind the stack
    path = [(0, 1.5, 1.0), (.6, 2.6, 2.4), (1.6, 3.0, 4.2), (1.4, 2.7, 6.2), (.2, 2.2, 7.8)]
    pts = []
    for i in range(len(path) - 1):
        for k in range(5):
            t = k / 5; pts.append(tuple(path[i][j] + (path[i + 1][j] - path[i][j]) * t for j in range(3)))
    for i, p in enumerate(pts): b.ball('tail ring', p, (.55 - .01 * i, .55 - .01 * i, .42), RACCOON_DK if i % 2 else RACCOON)
    b.ball('tail tip', pts[-1], .45, RACCOON_DK)
    # pockets with snacks
    for sx in (-1, 1): b.box('pocket', (sx * 1.0, -1.72, 1.5), (.7, .12, .5), COAT_SHADE, bevel=.03, rot=(-8, 0, sx * 10))
    b.cyl('baguette', (1.0, -1.7, 2.2), .12, 1.4, CRUST, rot=(-12, 0, 18), bevel=.02, verts=12)
    b.cyl('bone snack', (-1.0, -1.75, 1.85), .06, .7, BONE, rot=(-8, 0, -22), bevel=.01, verts=8)
    # clutter and flies
    for k in range(10): b.cyl('can', (rnd.uniform(-3.6, 3.6), rnd.uniform(-3.2, -2.3), .15), .16, .3, STEEL, bevel=.01, rot=(rnd.uniform(0, 90), 0, rnd.uniform(0, 180)))
    for k in range(8): b.ball('fly', (rnd.uniform(-3, 3), rnd.uniform(-2.5, .5), rnd.uniform(1, 9.5)), .07, BLACK)
    return b
