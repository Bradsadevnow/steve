"""Cursed swap meet bosses. Exec after boss_helpers and build_dungeon (for shared materials). Front is -Y."""

TAN = mat('Skin tan', (.85, .6, .42, 1), 0, .6); SHIRT = mat('Shirt turquoise', (.1, .72, .74, 1), 0, .7)
CLOTH_RED = mat('Tablecloth red', (.8, .15, .18, 1), 0, .8); CLOTH_WHITE = mat('Tablecloth white', (.95, .93, .9, 1), 0, .8)
LAMINATE = mat('Laminate', (.62, .55, .45, 1), 0, .5); CASH = mat('Cash green', (.4, .75, .42, 1), 0, .6)
PLASTIC_BEIGE = mat('Plastic beige', (.82, .78, .66, 1), 0, .4); PLASTIC_RED = mat('Plastic red', (.85, .12, .12, 1), 0, .3)
SIGN_RED = mat('Sale red', (.9, .1, .1, 1), 0, .5); YELLOW = mat('Yellow', (1, .85, .15, 1), 0, .4); TEAL_CAP = mat('Cap teal', (.05, .55, .6, 1), 0, .6)
HAIR_DK = mat('Hair dark', (.22, .12, .06, 1), 0, .4); LINING = mat('Cape lining', (.7, .06, .34, 1), 0, .4)
RUG = [mat('Rug maroon', (.55, .1, .15, 1)), mat('Rug cream', (.9, .85, .7, 1)), mat('Rug blue', (.12, .2, .5, 1)), mat('Rug orange', (.9, .5, .1, 1))]


def build_haggler():
    b = Boss('boss_haggler', 'swap', 'The Haggler: a six-armed folding-table merchant with a megaphone beard. Every arm holds a bargain. NO REFUNDS.')
    rnd = random.Random(31)
    # folding table with crossed legs and a hanging cloth
    b.box('table top', (0, 0, 2.15), (5.0, 2.6, .22), LAMINATE, bevel=.06); b.box('table lip', (0, 0, 2.05), (5.1, 2.7, .1), IRON, bevel=.03)
    for sx in (-1, 1):
        x = sx * 2.0
        for s2 in (-1, 1): b.cyl('table leg', (x, 0, 1.05), .06, 2.3, STEEL, rot=(s2 * 22, 0, 0), bevel=0, verts=10)
        b.box('foot bar', (x, 0, .06), (.14, 1.5, .1), IRON, bevel=.02)
    for i in range(14):
        b.box('cloth', (-2.3 + i * .355, -1.36, 1.5), (.35, .05, 1.2 - .05 * (i % 3)), CLOTH_RED if i % 2 else CLOTH_WHITE, bevel=.01)
    b.box('sign', (0, -1.42, 1.5), (2.6, .06, .7), YELLOW, bevel=.02)
    for k in range(9): b.box('sign text', (-1.1 + k * .27, -1.47, 1.5), (.16, .02, .4 if k != 4 else .2), BLACK, bevel=0)   # NO REFUNDS
    # junk on the table
    b.cyl('lamp base', (-1.8, -.7, 2.4), .22, .3, GOLD, bevel=.02); b.cyl('lamp shade', (-1.8, -.7, 2.9), .38, .6, LINING, r2=.22, bevel=.02)
    for k in range(5): b.cyl('record', (1.7, -.6, 2.3 + k * .03), .45, .02, BLACK, bevel=0)
    b.ball('rubber chicken', (1.0, -.9, 2.45), (.2, .3, .18), YELLOW); b.cyl('chicken neck', (1.0, -1.15, 2.6), .05, .3, YELLOW, rot=(70, 0, 0), bevel=0)
    for k in range(4): b.box('vhs', (-.6 + k * .02, -.9, 2.34 + k * .1), (.7, .5, .09), BLACK if k % 2 else IRON, bevel=.01)
    b.ball('cursed doll head', (.2, -.95, 2.5), .22, WHITE); b.eye('doll eye', (.2, -1.1, 2.55), .06, look=(0, -1, 0), iris=GLOW_RED)
    # torso: round merchant in a loud shirt, sitting behind the table
    b.blob('belly', (0, .5, 3.2), (1.35, 1.0, 1.25), SHIRT, seed=2, amp=.05)
    for k in range(40):
        a = rnd.uniform(3.4, 6.0); e = rnd.uniform(-.3, .7)
        d = Vector((math.cos(a) * math.cos(e), math.sin(a) * math.cos(e), math.sin(e)))
        b.ball('flower', Vector((0, .5, 3.2)) + Vector((d.x * 1.36, d.y * 1.0, d.z * 1.25)), .13, [GLOW_PINK, YELLOW, WHITE][k % 3])
    for k in range(5): b.torus('gold chain', (0, -.2, 3.75 - k * .03), .6 - k * .02, .04, GOLD, rot=(70, 0, 0))
    b.cyl('medallion', (0, -.55, 3.05), .3, .06, GOLD, rot=(90, 0, 0), bevel=.01); b.box('dollar', (0, -.6, 3.05), (.08, .02, .32), BLACK, bevel=0)
    # head, cap, shades, megaphone beard
    b.blob('head', (0, .4, 5.05), (.85, .78, .82), TAN, seed=5, amp=.03)
    b.cyl('cap dome', (0, .4, 5.4), .68, .5, TEAL_CAP, bevel=.04); b.box('cap brim', (0, -.2, 5.2), (1.3, .7, .08), TEAL_CAP, bevel=.03)
    for k in range(5): b.box('cap text', (-.3 + k * .15, -.3, 5.5), (.1, .03, .2), WHITE, bevel=0)
    for sx in (-1, 1):
        b.box('shade lens', (sx * .3, -.2, 5.0), (.4, .06, .26), BLACK, bevel=.05); b.box('lens glint', (sx * .38, -.26, 5.06), (.1, .01, .05), WHITE, bevel=0)
    b.box('shade bridge', (0, -.2, 5.06), (.2, .05, .05), BLACK, bevel=.01)
    b.blob('mustache', (0, -.18, 4.72), (.45, .12, .12), HAIR_DK, seed=3, amp=.1, sub=2)
    b.cyl('megaphone', (0, -.85, 4.1), .24, 1.9, PLASTIC_RED, r2=.6, rot=(90, 0, 0), bevel=.02, verts=32)
    b.torus('mega rim', (0, -1.8, 4.1), .6, .06, WHITE, rot=(90, 0, 0)); b.cyl('mega mouth', (0, -1.78, 4.1), .56, .02, BLACK, rot=(90, 0, 0), bevel=0, verts=32)
    b.torus('mega stripe', (0, -1.2, 4.1), .42, .035, WHITE, rot=(90, 0, 0))
    b.box('mega trigger', (0, -.7, 3.95), (.12, .3, .3), IRON, bevel=.02)
    for k in range(14):
        a = k * 6.283 / 14; b.blob('beard tuft', (math.cos(a) * .3, -.28 + math.sin(a) * .1, 4.4 + math.sin(a * 2) * .1), (.12, .12, .25), HAIR_DK, seed=k, amp=.2, sub=1)

    # six arms
    def arm(pts, hand, r0=.26, r1=.2):
        b.tube('arm', pts, r0, r1, TAN); b.ball('hand', hand, (.3, .3, .3), TAN); b.cyl('sleeve', pts[0], r0 + .08, .35, SHIRT, bevel=.02)
    arm([(1.2, .5, 3.9), (2.0, .3, 4.3), (2.8, -.3, 4.6)], (2.9, -.4, 4.6))        # R1 calculator
    arm([(1.3, .4, 3.4), (2.1, -.2, 3.3), (2.5, -1.0, 3.2)], (2.55, -1.1, 3.2))    # R2 price gun
    arm([(1.2, .5, 2.9), (2.0, .2, 2.7), (2.6, -.5, 2.5)], (2.65, -.6, 2.5))       # R3 rug club
    arm([(-1.2, .5, 3.9), (-2.0, .3, 4.5), (-2.7, -.5, 5.0)], (-2.75, -.55, 5.0))  # L1 sale sign
    arm([(-1.3, .4, 3.4), (-2.1, -.1, 3.4), (-2.6, -.9, 3.3)], (-2.65, -1.0, 3.3)) # L2 phone flail
    arm([(-1.2, .5, 2.9), (-1.9, .2, 2.7), (-2.3, -.6, 2.6)], (-2.35, -.7, 2.6))   # L3 cash fan
    # R1: calculator sledge
    b.cyl('calc handle', (2.9, -.4, 5.5), .09, 2.0, IRON, bevel=.01)
    b.box('calc body', (2.9, -.45, 6.9), (1.2, .5, 1.6), PLASTIC_BEIGE, bevel=.08); b.box('calc display', (2.9, -.72, 7.4), (.95, .04, .35), GLOW_GREEN, bevel=0)
    for r in range(4):
        for c in range(4): b.box('key', (2.58 + c * .21, -.72, 7.0 - r * .24), (.15, .04, .16), [PLASTIC_RED, WHITE, WHITE, IRON][c], bevel=0)
    # R2: oversized price-tag gun
    b.box('gun body', (2.55, -1.4, 3.5), (.45, 1.3, .55), YELLOW, bevel=.07); b.cyl('gun barrel', (2.55, -2.2, 3.6), .15, .9, IRON, rot=(90, 0, 0), bevel=.02)
    b.box('gun handle', (2.55, -1.1, 3.0), (.35, .3, .8), YELLOW, bevel=.05, rot=(15, 0, 0)); b.box('gun trigger', (2.55, -1.45, 3.1), (.08, .08, .3), IRON, bevel=0)
    b.sweep('price tags', [(2.55, -2.6, 3.6), (2.7, -3.0, 3.9), (2.6, -3.3, 3.5)], lambda t: (.18, .01), (0, 0, 1), WHITE, sides=4)
    for k in range(3): b.box('tag', (2.6 + k * .05, -2.9 - k * .2, 3.8 - k * .1), (.28, .02, .2), RED, bevel=0)
    # R3: rolled-up rug club
    for k in range(13): b.cyl('rug ring', (2.9 + k * .03, -.6 - k * .12, 1.2 + k * .2), .38, .22, RUG[k % 4], bevel=.01, rot=(-24, 0, 4))
    b.cyl('rug end', (3.3, -2.2, 3.8), .36, .06, RUG[1], rot=(-24, 0, 4), bevel=0)
    # L1: SALE shield
    b.cyl('sign pole', (-2.75, -.55, 4.2), .06, 1.8, WOOD_DK, bevel=0)
    b.box('sale board', (-2.75, -1.0, 6.0), (2.2, .14, 1.7), SIGN_RED, bevel=.08, rot=(0, 0, 4)); b.box('sale border', (-2.75, -1.09, 6.0), (2.0, .02, 1.5), WHITE, bevel=0, rot=(0, 0, 4))
    for k in range(4): b.box('sale text', (-3.3 + k * .42, -1.12, 6.15), (.3, .02, .5), SIGN_RED, bevel=0, rot=(0, 0, 4))
    for k in range(3): b.box('percent', (-3.1 + k * .55, -1.12, 5.65), (.3, .02, .35), YELLOW, bevel=0, rot=(0, 0, 4))
    # L2: rotary phone flail on a cord
    b.sweep('phone cord', [(-2.65, -1.0, 3.3), (-3.1, -1.4, 2.4), (-3.0, -1.9, 1.5), (-3.2, -2.1, .95)], lambda t: (.04, .04), (1, 0, 0), IRON, sides=6)
    b.box('phone body', (-3.2, -2.1, .75), (1.1, .9, .5), PLASTIC_RED, bevel=.12); b.cyl('phone dial', (-3.2, -2.1, 1.02), .3, .04, WHITE, bevel=0)
    b.cyl('phone handset', (-3.2, -2.1, 1.2), .1, 1.1, PLASTIC_RED, rot=(0, 90, 0), bevel=.04)
    for e in (-1, 1): b.ball('handset end', (-3.2 + e * .55, -2.1, 1.2), (.2, .18, .2), PLASTIC_RED)
    for k in range(5):
        a = k * 1.256; d = Vector((math.cos(a) * .9, math.sin(a) * .9, .35)).normalized()
        b.cyl('phone spike', Vector((-3.2, -2.1, .75)) + d * .8, .05, .4, STEEL, r2=.01, rot=tuple(math.degrees(x) for x in Vector((0, 0, 1)).rotation_difference(d).to_euler()), bevel=0, verts=8)
    # L3: fan of cash
    for k in range(9):
        a = -70 + k * 17.5; b.box('bill', (-2.35 + math.sin(math.radians(a)) * .5, -.8, 3.4 + math.cos(math.radians(a)) * .5), (.4, .02, 1.0), CASH, bevel=0, rot=(0, -a, 0))
    b.cyl('bill pin', (-2.35, -.8, 2.9), .06, .1, GOLD, rot=(90, 0, 0), bevel=0)
    # floating coupons
    for k in range(16): b.box('coupon', (rnd.uniform(-3.6, 3.6), rnd.uniform(-2.5, 1.5), rnd.uniform(3, 7)), (.3, .02, .2), YELLOW if k % 2 else WHITE, bevel=0, rot=(rnd.uniform(0, 90), rnd.uniform(0, 90), rnd.uniform(0, 90)))
    return b
