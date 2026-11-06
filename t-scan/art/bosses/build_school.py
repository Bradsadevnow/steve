"""Cursed high school bosses. Exec after boss_helpers (and build_dungeon/build_swap for shared materials). Front is -Y."""

SUIT = mat('Suit grey', (.34, .36, .42, 1), 0, .8); SUIT_LT = mat('Suit light', (.5, .52, .58, 1), 0, .8); SHIRT_W = mat('Shirt white', (.92, .92, .9, 1), 0, .7)
TIE = mat('Tie maroon', (.5, .08, .14, 1), 0, .6); BEIGE = mat('Intercom beige', (.82, .78, .66, 1), 0, .45); GRILLE = mat('Grille dark', (.12, .12, .14, 1), .4, .5)
BRASS = mat('Brass', (.85, .65, .2, 1), .8, .3); PAPER = mat('Paper', (.96, .95, .9, 1), 0, .8); CLIP = mat('Clipboard wood', (.55, .38, .22, 1), 0, .7)
RULER = mat('Ruler wood', (.82, .62, .35, 1), 0, .6); SOUND = mat('Sound wave', (.3, .95, .85, 1), 0, .3, 2.5); CAUTION = mat('Caution yellow', (1, .85, .1, 1), 0, .4)


def build_principal_fogwhistle():
    b = Boss('boss_principal_fogwhistle', 'school', 'Principal Fogwhistle: a spindly principal whose mouth is a PA horn. Announces attacks over the intercom. Carries a yardstick lance and a detention-slip clipboard.')
    rnd = random.Random(61)
    # pencil legs and big polished shoes
    for sx in (-1, 1):
        x = sx * .55
        b.box('shoe', (x, -.45, .22), (.7, 1.5, .44), BLACK, bevel=.1); b.box('shoe shine', (x, -.9, .38), (.4, .4, .06), WHITE, bevel=0)
        b.cyl('leg', (x, 0, 1.9), .17, 3.2, SUIT, bevel=.02, verts=12)
        b.cyl('sock', (x, 0, .6), .2, .4, SHIRT_W, bevel=0, verts=12)
    b.box('hips', (0, 0, 3.6), (1.5, .7, .55), SUIT, bevel=.1); b.box('belt', (0, 0, 3.9), (1.55, .74, .12), BLACK, bevel=.02); b.box('buckle', (0, -.38, 3.9), (.25, .05, .14), BRASS, bevel=.02)
    # long vest torso with tie
    b.box('torso', (0, 0, 5.1), (1.35, .75, 2.4), SUIT_LT, bevel=.12); b.box('shirt', (0, -.38, 5.4), (.55, .06, 1.9), SHIRT_W, bevel=.02)
    b.box('tie', (0, -.43, 5.2), (.2, .05, 1.5), TIE, bevel=.02); b.box('tie knot', (0, -.43, 6.0), (.28, .08, .22), TIE, bevel=.03)
    for k in range(5): b.box('tie stripe', (0, -.46, 4.7 + k * .26), (.2, .02, .06), GOLD, bevel=0, rot=(0, 0, 0))
    for sx in (-1, 1):
        b.box('lapel', (sx * .45, -.4, 5.6), (.3, .06, 1.5), SUIT, bevel=.03, rot=(0, 0, sx * -10)); b.ball('button', (sx * .2, -.42, 4.5), .06, BRASS)
    # lanyard whistle (a fog whistle)
    b.sweep('lanyard', [(-.45, -.3, 6.2), (-.3, -.48, 5.3), (0, -.52, 4.6), (.3, -.48, 5.3), (.45, -.3, 6.2)], lambda t: (.05, .02), (1, 0, 0), RED, sides=4)
    b.cyl('whistle tube', (0, -.65, 4.45), .12, .6, BRASS, rot=(0, 90, 0), bevel=.02); b.ball('whistle chamber', (-.25, -.65, 4.45), .2, BRASS); b.cyl('whistle mouth', (.32, -.65, 4.45), .1, .2, BRASS, rot=(0, 90, 0), bevel=0)
    # long neck, and a head that is an intercom box with a loudspeaker mouth
    b.cyl('neck', (0, 0, 6.8), .2, 1.3, SHIRT_W, bevel=.02, verts=12); b.box('collar', (0, 0, 6.35), (.8, .5, .22), SHIRT_W, bevel=.04)
    b.box('head box', (0, 0, 8.0), (2.1, 1.5, 1.8), BEIGE, bevel=.16, seg=3)
    b.box('speaker grille', (0, -.77, 7.7), (1.5, .06, .8), GRILLE, bevel=.03)
    for k in range(8): b.box('grille slat', (0, -.82, 7.4 + k * .1), (1.4, .02, .04), STEEL, bevel=0)
    b.cyl('horn', (0, -1.55, 7.7), .45, 1.5, GRILLE, r2=1.0, rot=(90, 0, 0), bevel=.03, verts=32); b.torus('horn rim', (0, -2.3, 7.7), 1.0, .08, BRASS, rot=(90, 0, 0))
    b.cyl('horn inner', (0, -2.2, 7.7), .9, .05, BLACK, rot=(90, 0, 0), bevel=0, verts=32)
    for sx in (-1, 1):
        b.eye('eye', (sx * .55, -.8, 8.45), .27, look=(0, -1, 0), iris=IRIS_AMBER)
        b.torus('glasses', (sx * .55, -.9, 8.45), .33, .04, BLACK, rot=(90, 0, 0)); b.box('brow', (sx * .55, -.86, 8.85), (.55, .07, .1), BLACK, bevel=.02, rot=(0, 0, sx * -16))
    b.box('glasses bridge', (0, -.9, 8.5), (.3, .04, .05), BLACK, bevel=.01)
    b.cyl('antenna', (.6, .2, 9.4), .04, 1.0, STEEL, bevel=0, verts=8); b.ball('antenna tip', (.6, .2, 9.95), .12, GLOW_RED)
    b.sweep('comb over', [(-.8, -.2, 8.95), (-.1, -.45, 9.05), (.7, -.2, 8.95)], lambda t: (.12, .04), (0, 1, 0), HAIR_DK, sides=6)
    b.box('name plate', (0, -.5, 6.7), (.7, .05, .22), BRASS, bevel=.02)
    # sound rings: the announcement
    for k, (y, r) in enumerate([(-2.7, 1.1), (-3.4, 1.6), (-4.1, 2.1)]): b.torus('sound ring', (0, y, 7.7), r, .07, SOUND, rot=(90, 0, 0))
    for k in range(10): a = k * 0.628; b.box('sound note', (math.cos(a) * 1.4, -3.4 - (k % 3) * .5, 7.7 + math.sin(a) * 1.4), (.18, .04, .18), SOUND, bevel=0, rot=(0, math.degrees(a), 0))
    # arms: spindly, one with a yardstick lance, one with a detention clipboard shield
    b.ball('shoulder R', (.78, 0, 6.1), .26, SUIT); b.ball('shoulder L', (-.78, 0, 6.1), .26, SUIT)
    b.tube('arm R', [(.8, 0, 6.0), (1.9, -.2, 5.2), (2.8, -.9, 4.8)], .16, .13, SUIT); b.ball('hand R', (2.85, -.95, 4.8), (.22, .26, .22), SHIRT_W)
    b.tube('arm L', [(-.8, 0, 6.0), (-1.7, -.2, 5.2), (-2.0, -.9, 5.0)], .16, .13, SUIT); b.ball('hand L', (-2.05, -.95, 5.0), (.22, .26, .22), SHIRT_W)
    # yardstick lance
    b.box('yardstick', (2.95, -1.5, 6.9), (.4, .09, 6.6), RULER, bevel=.02, rot=(-18, 0, 4))
    for k in range(18): b.box('tick', (3.13 + (k % 2) * .06, -1.62 + (k * .35) * .32 * 0, 3.7 + k * .35), (.1 - (k % 2) * .04, .02, .03), BLACK, bevel=0, rot=(-18, 0, 4))
    b.cyl('yardstick tip', (3.25, -2.2, 10.2), .2, .5, STEEL, r2=.01, rot=(-18, 0, 4), bevel=0, verts=4)
    # clipboard shield with a DETENTION slip
    b.box('clipboard', (-2.7, -1.5, 5.4), (2.0, .14, 2.7), CLIP, bevel=.07); b.box('paper', (-2.7, -1.6, 5.35), (1.7, .02, 2.3), PAPER, bevel=0)
    b.box('clip', (-2.7, -1.6, 6.6), (.9, .1, .3), STEEL, bevel=.03)
    for k in range(5): b.box('slip text', (-3.25 + k * .27, -1.64, 5.9), (.2, .02, .35), RED, bevel=0)
    for k in range(5): b.box('slip line', (-2.7, -1.64, 5.3 - k * .22), (1.3 - (k % 2) * .3, .02, .05), BLACK, bevel=0)
    b.cyl('pencil', (-1.9, -1.7, 5.2), .05, 1.6, YELLOW, rot=(0, 20, -35), bevel=0, verts=6)
    # the floor: a wet-floor sign and a mop bucket
    for sx in (-1, 1): b.box('caution panel', (-3.2 + sx * .0, -3.0 + sx * .25, .55), (1.0, .06, 1.1), CAUTION, bevel=.03, rot=(sx * -14, 0, 0))
    b.box('caution figure', (-3.2, -3.28, .65), (.2, .02, .6), BLACK, bevel=0, rot=(-14, 0, 0)); b.ball('caution head', (-3.2, -3.32, 1.0), .12, BLACK)
    b.cyl('bucket', (3.2, -2.7, .4), .5, .8, SUIT_LT, r2=.6, bevel=.03); b.cyl('mop handle', (3.4, -2.6, 1.6), .05, 2.4, WOOD_DK, rot=(0, -10, 0), bevel=0, verts=8)
    for k in range(8): b.cyl('mop strand', (3.05 + k * .03, -2.6, .9), .04, .6, WHITE, rot=(0, 0, 0), bevel=0, verts=6)
    for k in range(12): b.box('hall pass', (rnd.uniform(-4, 4), rnd.uniform(-3.5, 1), rnd.uniform(2, 6.5)), (.28, .02, .2), PAPER, bevel=0, rot=(rnd.uniform(0, 90), rnd.uniform(0, 90), rnd.uniform(0, 90)))
    return b
