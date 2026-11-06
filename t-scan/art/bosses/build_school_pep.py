"""High school boss: Pep Rally, Incarnate. Exec after boss_helpers, build_dungeon, build_swap and build_school (shared materials). Front is -Y."""

MAROON = mat('School maroon', (.5, .08, .16, 1), 0, .7); GOLD_UNI = mat('School gold', (1, .75, .15, 1), 0, .5); WOMBAT = mat('Wombat fur', (.5, .36, .24, 1), 0, .9)
WOMBAT_LT = mat('Wombat light', (.82, .68, .5, 1), 0, .9); SKIN_A = mat('Skin A', (.95, .75, .62, 1), 0, .6); SKIN_B = mat('Skin B', (.6, .38, .26, 1), 0, .6); SKIN_C = mat('Skin C', (.85, .6, .45, 1), 0, .6)
HAIR_Y = mat('Hair blonde', (.95, .8, .35, 1), 0, .5); HAIR_BK = mat('Hair black', (.08, .06, .08, 1), 0, .5); HAIR_R = mat('Hair red', (.8, .25, .1, 1), 0, .5)
FOAM = mat('Foam yellow', (1, .9, .2, 1), 0, .9); POM_W = mat('Pom white', (.98, .98, 1, 1), 0, .6)


def _pom(b, c, s, m1, m2, seed=1):
    rnd = random.Random(seed); x, y, z = c
    b.ball('pom core', c, s * .55, m1)
    for k in range(26):
        a = rnd.uniform(0, 6.28); e = math.asin(rnd.uniform(-1, 1)); d = Vector((math.cos(a) * math.cos(e), math.sin(a) * math.cos(e), math.sin(e)))
        b.cyl('pom strand', Vector(c) + d * s * .8, s * .12, s * .8, m1 if k % 2 else m2, r2=.004, rot=tuple(math.degrees(v) for v in Vector((0, 0, 1)).rotation_difference(d).to_euler()), bevel=0, verts=6)


def _cheerleader(b, base, tilt, skin, hair, mouth_open=True, seed=1):
    x, y, z = base
    b.blob('cheer torso', (x, y, z), (.75, .55, 1.0), MAROON, seed=seed, amp=.05, rot=(0, tilt, 0))
    b.box('cheer stripe', (x + math.sin(math.radians(tilt)) * -.1, y - .5, z), (.5, .04, .9), GOLD_UNI, bevel=.02, rot=(0, tilt, 0))
    hx = x + math.sin(math.radians(tilt)) * 1.05; hz = z + math.cos(math.radians(tilt)) * 1.05 + .4
    b.ball('cheer head', (hx, y - .1, hz), (.7, .64, .74), skin)
    for sx in (-1, 1):
        b.box('happy eye', (hx + sx * .22, y - .76, hz + .1), (.26, .04, .06), BLACK, bevel=.01, rot=(0, 0, sx * 18)); b.ball('blush', (hx + sx * .34, y - .66, hz - .14), (.1, .03, .08), PINK)
    b.ball('grin', (hx, y - .75, hz - .26), (.26, .06, .15), DARKRED); b.box('grin teeth', (hx, y - .8, hz - .18), (.28, .02, .06), WHITE, bevel=0)
    b.ball('hair top', (hx, y + .06, hz + .22), (.58, .52, .4), hair); b.sweep('ponytail', [(hx + .3, y + .35, hz + .35), (hx + .9, y + .6, hz + .4), (hx + 1.0, y + .7, hz - .5)], lambda t: (.2 * (1 - .5 * t), .12), (0, 0, 1), hair, sides=8)
    b.ball('bow', (hx + .32, y + .3, hz + .42), (.2, .08, .12), GOLD_UNI)
    # arms up with pom-poms
    for sx in (-1, 1):
        sh = Vector((x + sx * .75, y, z + .5)); hand = Vector((x + sx * 1.6, y - .5, z + 1.9 + (.3 if sx > 0 else 0)))
        b.tube('cheer arm', [tuple(sh), tuple((sh + hand) / 2 + Vector((sx * .2, -.2, 0))), tuple(hand)], .17, .13, skin)
        _pom(b, tuple(hand + Vector((sx * .1, -.1, .55))), .7, GOLD_UNI if sx > 0 else MAROON, POM_W, seed + sx)


def build_pep_rally():
    b = Boss('boss_pep_rally', 'school', 'Pep Rally, Incarnate: a mascot wombat fused with an entire cheer squad. Swings a giant foam finger and a megaphone cannon.')
    rnd = random.Random(81)
    # the wombat mascot: stout body, stubby legs, big head
    b.blob('belly', (0, 0, 3.0), (2.3, 1.9, 2.5), WOMBAT, seed=3, amp=.04)
    b.blob('tummy', (0, -1.55, 2.8), (1.5, .5, 1.7), WOMBAT_LT, seed=4, amp=.03)
    b.box('letter patch', (0, -2.0, 3.3), (1.0, .06, 1.1), GOLD_UNI, bevel=.04)
    b.box('P stem', (-.18, -2.05, 3.3), (.18, .03, .8), MAROON, bevel=0); b.box('P top', (.05, -2.05, 3.55), (.4, .03, .16), MAROON, bevel=0); b.box('P mid', (.05, -2.05, 3.2), (.4, .03, .16), MAROON, bevel=0); b.box('P side', (.28, -2.05, 3.38), (.16, .03, .4), MAROON, bevel=0)
    b.torus('collar sash', (0, 0, 4.4), 1.5, .12, GOLD_UNI, rot=(10, 0, 0))
    for sx in (-1, 1):
        x = sx * 1.1
        b.cyl('leg', (x, -.3, .85), .75, 1.7, WOMBAT, bevel=.05, r2=.65); b.ball('foot', (x, -.9, .3), (.85, 1.0, .35), WOMBAT_LT)
        for c in (-1, 0, 1): b.cyl('claw', (x + c * .32, -1.85, .22), .09, .4, BONE, r2=.01, rot=(95, 0, 0), bevel=0, verts=8)
    # head: big, round, cheerful, with buck teeth
    b.blob('head', (0, -.4, 6.0), (1.75, 1.55, 1.45), WOMBAT, seed=5, amp=.03)
    b.blob('muzzle', (0, -1.55, 5.6), (.85, .65, .65), WOMBAT_LT, seed=6, amp=.04)
    b.ball('nose', (0, -2.1, 5.85), (.45, .3, .32), BLACK); b.ball('nose shine', (-.1, -2.3, 5.95), .09, WHITE)
    for sx in (-1, 1):
        b.eye('eye', (sx * .72, -1.5, 6.5), .38, look=(0, -1, 0), iris=IRIS_AMBER)
        b.box('brow', (sx * .72, -1.65, 6.95), (.6, .09, .12), WOMBAT, bevel=.03, rot=(0, 0, sx * -14))
        b.ball('ear', (sx * 1.45, -.2, 7.2), (.55, .3, .6), WOMBAT); b.ball('ear in', (sx * 1.45, -.4, 7.2), (.34, .2, .4), PINK)
        b.ball('cheek', (sx * 1.15, -1.5, 5.4), (.3, .08, .22), PINK)
    b.box('buck tooth', (-.14, -2.0, 5.2), (.24, .08, .4), WHITE, bevel=.03); b.box('buck tooth', (.14, -2.0, 5.2), (.24, .08, .4), WHITE, bevel=.03)
    b.torus('headband', (0, -.4, 6.85), 1.55, .1, GOLD_UNI, rot=(0, 0, 0)) if False else b.torus('headband', (0, -.4, 7.0), 1.4, .1, GOLD_UNI, rot=(15, 0, 0))
    b.cyl('cheer visor', (0, -1.5, 7.2), 1.0, .08, MAROON, bevel=.02) if False else None
    # fused cheerleaders erupting from the wombat
    _cheerleader(b, (-3.1, .3, 5.0), 28, SKIN_A, HAIR_Y, seed=1)
    _cheerleader(b, (3.1, .3, 5.0), -28, SKIN_B, HAIR_BK, seed=2)
    _cheerleader(b, (-2.3, -1.9, 1.9), 38, SKIN_C, HAIR_R, seed=3)
    _cheerleader(b, (2.3, -1.9, 1.9), -38, SKIN_A, HAIR_BK, seed=4)
    # wombat's big weapons: a giant foam finger club and a megaphone cannon
    b.tube('wombat arm R', [(1.9, -.4, 4.0), (2.8, -1.1, 3.6), (3.3, -1.9, 3.3)], .5, .45, WOMBAT); b.ball('paw R', (3.35, -2.0, 3.3), (.55, .5, .5), WOMBAT_LT)
    b.tube('wombat arm L', [(-1.9, -.4, 4.0), (-2.8, -1.1, 3.6), (-3.3, -1.9, 3.3)], .5, .45, WOMBAT); b.ball('paw L', (-3.35, -2.0, 3.3), (.55, .5, .5), WOMBAT_LT)
    b.cyl('foam palm', (3.5, -2.0, 4.6), .8, 1.7, FOAM, r2=.85, bevel=.1); b.cyl('foam finger', (3.5, -2.0, 6.1), .4, 2.3, FOAM, r2=.36, bevel=.1)
    b.cyl('foam thumb', (4.2, -2.0, 4.8), .28, 1.0, FOAM, rot=(0, -50, 0), bevel=.08); b.box('foam 1', (3.5, -2.8, 4.6), (.12, .04, .8), MAROON, bevel=0); b.box('foam #', (3.5, -2.82, 4.55), (.6, .03, .12), MAROON, bevel=0)
    b.cyl('megaphone', (-3.5, -2.8, 4.6), .4, 2.4, GOLD_UNI, r2=1.15, rot=(80, 0, -10), bevel=.03, verts=32); b.torus('mega rim', (-3.9, -4.0, 4.3), 1.12, .07, WHITE, rot=(80, 0, -10)); b.cyl('mega mouth', (-3.9, -3.95, 4.32), 1.05, .03, BLACK, rot=(80, 0, -10), bevel=0, verts=32)
    for k, (y, r) in enumerate([(-4.8, 1.3), (-5.5, 1.8)]): b.torus('shout ring', (-4.1, y, 4.1), r, .07, SOUND, rot=(80, 0, -10)) if 'SOUND' in globals() else None
    # banner pennants and confetti
    b.sweep('banner string', [(-4.4, 2.0, 7.0), (-2.0, 2.2, 6.4), (1.0, 2.2, 6.4), (4.2, 2.0, 7.2)], lambda t: (.05, .05), (1, 0, 0), IRON, sides=5)
    for k in range(9): b.cyl('pennant', (-4.0 + k * .95, 2.15, 6.6 + .4 * math.sin(k * .7) - .3), .4, .04, [MAROON, GOLD_UNI][k % 2], verts=3, rot=(90, 0, 0), bevel=0)
    for k in range(40): b.box('confetti', (rnd.uniform(-5, 5), rnd.uniform(-4, 2.5), rnd.uniform(.5, 9)), (.14, .02, .08), [GOLD_UNI, MAROON, WHITE, GLOW_PINK, GLOW_TEAL][k % 5], bevel=0, rot=(rnd.uniform(0, 90), rnd.uniform(0, 90), rnd.uniform(0, 90)))
    return b
