"""High school boss: The Lunch Lady Colossus. Exec after boss_helpers, build_dungeon, build_swap and build_school (shared materials). Front is -Y."""

STAINLESS = mat('Stainless', (.72, .75, .78, 1), .85, .25); UNIFORM = mat('Uniform pink', (.95, .6, .7, 1), 0, .7); APRON = mat('Apron white', (.95, .94, .9, 1), 0, .8)
GLOVE = mat('Glove yellow', (1, .85, .15, 1), 0, .35); SKIN_P = mat('Skin peach', (.95, .72, .6, 1), 0, .6); HAIR_GREY = mat('Hair grey', (.7, .7, .74, 1), 0, .8)
NET = mat('Hairnet', (.85, .85, .9, 1), 0, .6); LIPS = mat('Lipstick', (.8, .1, .25, 1), 0, .3); GRAVY = mat('Gravy glow', (.45, .9, .25, 1), 0, .3, 1.6)
MEAT = mat('Mystery meat', (.55, .3, .22, 1), 0, .4); MEAT_PINK = mat('Meat pink', (.85, .45, .45, 1), 0, .4); MASH = mat('Mashed potato', (.96, .92, .75, 1), 0, .7)
PEAS = mat('Peas', (.3, .75, .25, 1), 0, .4); JELLO = mat('Jello red', (.9, .1, .2, 1), 0, .15, .3); TRAY = mat('Tray teal', (.15, .55, .6, 1), 0, .4)


def _meat_monster(b, loc, s, seed):
    x, y, z = loc
    b.blob('meat', (x, y, z + .02), (.6 * s, .55 * s, .6 * s), MEAT if seed % 2 else MEAT_PINK, seed=seed, amp=.14, floor=0)
    for sx in (-1, 1): b.eye('meat eye', (x + sx * .22 * s, y - .5 * s, z + .75 * s), .14 * s, look=(0, -1, 0), iris=IRIS_AMBER)
    b.torus('meat mouth', (x, y - .5 * s, z + .38 * s), .2 * s, .05 * s, DARKRED, rot=(90, 0, 0))
    for k in range(5): b.cyl('meat tooth', (x - .15 * s + k * .075 * s, y - .56 * s, z + .43 * s), .03 * s, .1 * s, WHITE, r2=.003, rot=(180, 0, 0), bevel=0, verts=6)
    for sx in (-1, 1): b.cyl('meat leg', (x + sx * .3 * s, y - .1 * s, z + .12 * s), .07 * s, .3 * s, MEAT, bevel=0, verts=8)


def build_lunch_lady():
    b = Boss('boss_lunch_lady', 'school', 'The Lunch Lady Colossus: a huge cafeteria lunch lady rising from a steam table. Swings a giant ladle of glowing gravy and serves mystery meat that fights back.')
    rnd = random.Random(71)
    # steam table counter
    b.box('counter', (0, 0, .95), (5.6, 2.6, 1.9), STAINLESS, bevel=.1); b.box('counter top', (0, 0, 1.95), (5.8, 2.8, .12), STEEL, bevel=.04)
    for k in range(5): b.box('panel seam', (-2.2 + k * 1.1, -1.32, .95), (.04, .03, 1.7), IRON, bevel=0)
    b.box('tray rail', (0, -1.7, 1.3), (5.6, .14, .1), STEEL, bevel=.03); b.cyl('rail post', (-2.6, -1.7, 1.0), .05, .6, STEEL, bevel=0, verts=8); b.cyl('rail post', (2.6, -1.7, 1.0), .05, .6, STEEL, bevel=0, verts=8)
    for sx in (-1, 1): b.cyl('wheel', (sx * 2.5, -1.0, .2), .2, .15, BLACK, rot=(0, 90, 0), bevel=.01)
    # sneeze guard (frame only)
    for sx in (-1, 1): b.cyl('guard post', (sx * 2.6, -1.0, 2.7), .05, 1.3, STEEL, bevel=0, verts=8)
    b.box('guard bar', (0, -1.1, 3.35), (5.3, .06, .08), STEEL, bevel=.01, rot=(-12, 0, 0))
    # food wells: potatoes, peas, jello, and a vat of mystery meat
    for i, (x, m) in enumerate([(-2.0, MASH), (-.7, PEAS), (.6, JELLO), (1.9, MEAT)]):
        b.box('well', (x, -.5, 2.05), (1.1, 1.3, .12), IRON, bevel=.03)
        if m is PEAS:
            for k in range(30): b.ball('pea', (x + rnd.uniform(-.45, .45), -.5 + rnd.uniform(-.5, .5), 2.15 + rnd.uniform(0, .12)), .07, PEAS)
        else:
            b.blob('food', (x, -.5, 2.07), (.5, .6, .3), m, seed=i + 1, amp=.12, floor=0)
    for k in range(7): a = rnd.uniform(0, 6.28); b.ball('steam', (rnd.uniform(-2.4, 2.4), rnd.uniform(-.8, .2), rnd.uniform(2.6, 3.6)), rnd.uniform(.12, .28), WHITE)
    # the lunch lady: pink uniform, white apron, enormous (scaled up about the counter top)
    b.hold('lady', loc=(0, 0, -.585), scale=(1.3, 1.3, 1.3))
    b.blob('torso', (0, .9, 3.9), (1.75, 1.3, 1.5), UNIFORM, seed=2, amp=.04)
    b.box('apron', (0, .1, 3.7), (2.1, .12, 2.3), APRON, bevel=.1); b.box('apron pocket', (0, 0, 3.0), (1.3, .08, .55), APRON, bevel=.03)
    for k in range(3): b.cyl('spork', (-.35 + k * .35, -.02, 3.35), .04, .6, STEEL, bevel=0, verts=8); b.ball('spork bowl', (-.35 + k * .35, -.02, 3.7), (.1, .03, .14), STEEL)
    for k in range(5): b.blob('stain', (-.7 + rnd.uniform(0, 1.4), -.08, 3.7 + rnd.uniform(-.5, .7)), (.14, .02, .14), [MEAT, GRAVY, MASH, JELLO][k % 4], seed=k, amp=.1, sub=1)
    for sx in (-1, 1): b.cyl('apron strap', (sx * .75, .15, 5.0), .06, 1.1, APRON, rot=(0, sx * 12, 0), bevel=0, verts=8)
    b.cyl('neck', (0, .9, 5.1), .45, .35, SKIN_P, bevel=0)
    b.blob('head', (0, .9, 5.9), (1.0, .95, 1.0), SKIN_P, seed=4, amp=.025)
    b.blob('hair bun', (0, 1.35, 6.55), (.7, .6, .45), HAIR_GREY, seed=2, amp=.1)
    # hairnet: rings around the hair
    for k in range(5): b.torus('net lat', (0, .95, 6.1 + k * .13 - .1), 1.0 - k * .13, .018, NET, rot=(0, 0, 0))
    for k in range(6): b.torus('net meridian', (0, .95, 6.2), 1.02, .016, NET, rot=(90, 0, k * 30))
    for sx in (-1, 1):
        b.eye('eye', (sx * .38, .15, 6.0), .2, look=(0, -1, 0), iris=IRIS_GREEN)
        b.box('lid', (sx * .38, .08, 6.17), (.5, .06, .12), SKIN_P, bevel=.03); b.box('brow', (sx * .38, .08, 6.42), (.5, .07, .09), HAIR_GREY, bevel=.02, rot=(0, 0, sx * -20))
        b.ball('cheek', (sx * .62, .12, 5.6), (.18, .05, .14), PINK)
    b.cyl('nose', (0, .1, 5.82), .1, .3, SKIN_P, r2=.07, rot=(100, 0, 0), bevel=0, verts=10); b.ball('mole', (.35, .05, 5.65), .04, BLACK)
    b.torus('lips', (0, .05, 5.45), .25, .07, LIPS, rot=(90, 0, 0)); b.box('lip glare', (.1, -.02, 5.5), (.1, .02, .02), WHITE, bevel=0)
    b.torus('glasses', (-.38, .02, 6.0), .3, .03, STEEL, rot=(90, 0, 0)) if False else None
    # arms and big yellow rubber gloves
    for sx in (-1, 1):
        b.ball('shoulder', (sx * 1.6, .9, 4.6), (.55, .5, .5), UNIFORM)
    b.tube('arm R', [(1.6, .8, 4.5), (2.4, .2, 4.4), (2.6, -.6, 4.4)], .45, .38, UNIFORM); b.ball('glove R', (2.65, -.7, 4.4), (.5, .45, .45), GLOVE)
    b.tube('arm L', [(-1.6, .8, 4.5), (-2.4, .2, 4.4), (-2.6, -.6, 4.5)], .45, .38, UNIFORM); b.ball('glove L', (-2.65, -.7, 4.5), (.5, .45, .45), GLOVE)
    for sx in (-1, 1):
        for k in range(4): b.cyl('glove finger', (sx * 2.65 + (k - 1.5) * .17, -1.05, 4.5), .08, .35, GLOVE, rot=(90, 0, 0), r2=.07, bevel=0, verts=8)
    # right: the giant ladle, raised for a smash
    b.cyl('ladle handle', (3.1, -1.1, 6.6), .16, 4.6, STEEL, rot=(0, 8, 0), bevel=.02, verts=14)
    b.sweep('ladle neck', [(3.4, -1.1, 8.8), (3.6, -1.2, 9.5), (3.3, -1.5, 10.0)], lambda t: (.16, .16), (1, 0, 0), STEEL, sides=10)
    b.ball('ladle bowl', (2.9, -1.9, 10.2), (1.2, 1.2, .75), STEEL); b.ball('ladle gravy', (2.9, -1.9, 10.35), (1.0, 1.0, .5), GRAVY)
    for k in range(7): a = k * .9; b.ball('gravy bubble', (2.9 + math.cos(a) * .5, -1.9 + math.sin(a) * .5, 10.75 + (k % 3) * .12), .1, GRAVY)
    for k in range(3): b.ball('gravy drip', (3.6, -1.9 + k * .15, 9.5 - k * .5), (.09, .09, .16), GRAVY)
    # left: a cafeteria tray as a shield, with a spork rim
    b.box('tray', (-2.9, -1.6, 4.9), (2.8, .16, 2.0), TRAY, bevel=.1, rot=(0, 0, -6))
    for k in range(4): b.box('tray well', (-3.6 + k * .5, -1.72, 4.9), (.4, .04, 1.6), mat('Tray inner', (.1, .4, .45, 1)), bevel=.01, rot=(0, 0, -6))
    for k in range(8): b.cyl('spork spike', (-4.2 + k * .38, -1.75, 5.95 + (k % 2) * .05), .05, .5, STEEL, r2=.01, rot=(0, 0, 0), bevel=0, verts=6)
    for k in range(9): b.cyl('tater tot', (-3.9 + (k % 3) * .4, -1.8, 4.5 + (k // 3) * .4), .13, .26, CRUST, rot=(90, 0, 0), bevel=.03, verts=10)
    b.release()
    # mystery meat monsters scrambling off the counter
    for i, (x, y, z, s) in enumerate([(-1.6, -2.7, 0, 1.0), (.4, -3.1, 0, 1.2), (2.1, -2.8, 0, .9), (-3.1, -2.3, 0, .7), (3.5, -2.4, 0, .75)]): _meat_monster(b, (x, y, z), s, i + 3)
    # a lunch menu on the back wall of the pass
    b.box('menu board', (0, 2.6, 5.0), (3.2, .12, 1.8), BLACK, bevel=.05)
    for k in range(4): b.box('menu line', (-.9 + (k % 2) * .4, 2.52, 5.5 - k * .35), (1.4 - (k % 2) * .5, .02, .09), WHITE, bevel=0)
    for k in range(3): b.cyl('menu question', (1.1, 2.52, 5.4 - k * .3), .04, .2, GLOW_RED, rot=(90, 0, 0), bevel=0, verts=6)
    return b
