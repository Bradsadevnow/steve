"""Swap meet boss: Dowser Dave, the Inflatable Prophet. Exec after boss_helpers (and build_swap for shared materials). Front is -Y."""

DAVE = mat('Dave magenta', (.95, .2, .55, 1), 0, .35); DAVE_Y = mat('Dave yellow', (1, .85, .15, 1), 0, .35); DAVE_C = mat('Dave cyan', (.1, .8, .9, 1), 0, .35)
BLOWER = mat('Blower grey', (.55, .58, .62, 1), .5, .45); HALO = mat('Halo gold', (1, .85, .3, 1), 0, .3, 2.2); BARK = mat('Dowsing bark', (.45, .3, .18, 1), 0, .8)


def _cr(pts, k=10):
    P = [Vector(p) for p in pts]; Q = [P[0]] + P + [P[-1]]; out = []
    for i in range(1, len(Q) - 2):
        p0, p1, p2, p3 = Q[i - 1], Q[i], Q[i + 1], Q[i + 2]
        for j in range(k):
            t = j / k; t2 = t * t; t3 = t2 * t
            out.append(.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    out.append(P[-1]); return out


def _euler_to(v):
    return tuple(math.degrees(x) for x in Vector((0, 0, 1)).rotation_difference(Vector(v).normalized()).to_euler())


def build_dowser_dave():
    b = Boss('boss_dowser_dave', 'swap', 'Dowser Dave, the Inflatable Prophet: a wacky waving tube man on a leaf blower. Flails a pennant whip and points a dowsing rod.')
    rnd = random.Random(51)
    # the blower he rises from
    b.box('blower', (0, 0, .85), (3.8, 3.4, 1.7), BLOWER, bevel=.14); b.box('blower top', (0, 0, 1.75), (3.9, 3.5, .1), IRON, bevel=.03)
    b.cyl('fan cage', (0, -1.75, .85), 1.3, .2, IRON, rot=(90, 0, 0), bevel=.02); b.torus('fan ring', (0, -1.85, .85), 1.25, .06, STEEL, rot=(90, 0, 0)); b.torus('fan ring2', (0, -1.85, .85), .7, .05, STEEL, rot=(90, 0, 0))
    for k in range(8): a = k * math.pi / 4; b.box('fan spoke', (math.cos(a) * .62, -1.87, .85 + math.sin(a) * .62), (.06, .04, 1.2), STEEL, bevel=0, rot=(0, math.degrees(-a) + 90, 0))
    b.box('power switch', (1.0, -1.34, 1.1), (.3, .06, .2), RED, bevel=.02); b.sweep('power cord', [(1.4, 0, .3), (2.4, -.8, .05), (3.2, -2.0, .05), (3.6, -3.2, .05)], lambda t: (.06, .06), (1, 0, 0), BLACK, sides=6)
    b.cyl('duct', (0, 0, 2.15), 1.3, .7, IRON, r2=.95, bevel=.03, verts=32)
    # the tube body: a wobbling sweep with coloured stripe rings
    path_pts = [(0, 0, 2.3), (.7, 0, 3.4), (-.8, .1, 5.0), (.9, 0, 6.6), (-.6, 0, 8.0), (.3, -.1, 9.3)]
    body = _cr(path_pts, 10); N = len(body)
    b.sweep('body', path_pts, lambda t: (.95 - .2 * t + .08 * math.sin(t * 45), .95 - .2 * t + .08 * math.sin(t * 45)), (1, 0, 0), DAVE, sides=20)
    for i in range(4, N - 2, 8):
        r = .95 - .2 * (i / (N - 1)) + .1; tang = body[min(i + 1, N - 1)] - body[i - 1]
        b.torus('stripe', body[i], r, .06, [DAVE_Y, DAVE_C][(i // 8) % 2], rot=_euler_to(tang))
    # head: a big round inflated face on top with a halo
    hc = Vector(body[-1]) + Vector((0, 0, .9))
    b.ball('head', hc, (1.05, .95, 1.05), DAVE); b.ball('face patch', hc + Vector((0, -.5, -.05)), (.8, .5, .85), DAVE_Y)
    for sx in (-1, 1):
        b.eye('eye', hc + Vector((sx * .4, -.78, .25)), .3, look=(sx * .1, -1, 0), iris=IRIS_GREEN)
        b.box('brow', hc + Vector((sx * .42, -.82, .6)), (.4, .08, .12), BLACK, bevel=.03, rot=(0, 0, sx * -15))
    b.torus('grin', hc + Vector((0, -.84, -.28)), .42, .08, DARKRED, rot=(80, 0, 0)); b.box('grin cover', hc + Vector((0, -.8, -.12)), (.9, .06, .3), YELLOW, bevel=0) if False else None
    for k in range(6): b.box('tooth', hc + Vector((-.3 + k * .12, -.9, -.3)), (.1, .04, .14), WHITE, bevel=.01)
    b.cyl('nose', hc + Vector((0, -.95, 0)), .12, .3, DAVE_Y, rot=(90, 0, 0), r2=.2, bevel=.02)
    b.torus('halo', hc + Vector((0, .05, 1.5)), .7, .07, HALO, rot=(80, 0, 0))
    for k in range(4): b.sweep('streamer', [(hc.x + (k - 1.5) * .35, hc.y - .2, hc.z - .8), (hc.x + (k - 1.5) * .5, hc.y - .5, hc.z - 1.6), (hc.x + (k - 1.5) * .45, hc.y - .3, hc.z - 2.4)], lambda t: (.12, .02), (1, 0, 0), [DAVE_Y, DAVE_C][k % 2], sides=4)
    # flailing arms: long inflatable tubes with mitts
    arm_r = _cr([(.6, 0, 6.8), (2.2, -.2, 8.0), (3.4, -.6, 6.8), (3.6, -1.2, 5.4)], 8); arm_l = _cr([(-.6, 0, 6.6), (-2.2, 0, 5.2), (-3.2, -.5, 6.6), (-3.6, -1.0, 8.2)], 8)
    b.sweep('arm R', [(.6, 0, 6.8), (2.2, -.2, 8.0), (3.4, -.6, 6.8), (3.6, -1.2, 5.4)], lambda t: (.45 - .08 * t + .04 * math.sin(t * 40), .45 - .08 * t + .04 * math.sin(t * 40)), (0, 1, 0), DAVE, sides=14)
    b.sweep('arm L', [(-.6, 0, 6.6), (-2.2, 0, 5.2), (-3.2, -.5, 6.6), (-3.6, -1.0, 8.2)], lambda t: (.45 - .08 * t + .04 * math.sin(t * 40), .45 - .08 * t + .04 * math.sin(t * 40)), (0, 1, 0), DAVE, sides=14)
    b.ball('mitt R', arm_r[-1], (.6, .5, .6), DAVE_Y); b.ball('mitt L', arm_l[-1], (.6, .5, .6), DAVE_Y)
    # right: grand opening pennant whip
    hand = Vector(arm_r[-1]); whip = _cr([tuple(hand), (hand.x + .9, hand.y - 1.2, hand.z - .6), (hand.x + 2.0, hand.y - 2.4, hand.z + .2), (hand.x + 1.2, hand.y - 3.6, hand.z + 1.4), (hand.x - .6, hand.y - 4.2, hand.z + 1.0)], 8)
    b.sweep('whip string', [tuple(hand), (hand.x + .9, hand.y - 1.2, hand.z - .6), (hand.x + 2.0, hand.y - 2.4, hand.z + .2), (hand.x + 1.2, hand.y - 3.6, hand.z + 1.4), (hand.x - .6, hand.y - 4.2, hand.z + 1.0)], lambda t: (.05, .05), (1, 0, 0), IRON, sides=6)
    for i in range(3, len(whip) - 2, 3):
        tang = whip[i + 1] - whip[i - 1]; b.cyl('pennant', whip[i] + Vector((0, 0, -.28)), .32, .03, [RED, DAVE_Y, DAVE_C, WHITE][(i // 3) % 4], verts=3, rot=(90, 0, 0), bevel=0)
    b.ball('whip weight', whip[-1], .22, GOLD)
    # left: a giant dowsing rod, pointing at buried treasure
    hand = Vector(arm_l[-1]); tip = Vector((hand.x - 1.2, hand.y - 3.2, hand.z - .2))
    b.cyl('rod shaft', hand + (tip - hand) * .5, .12, (tip - hand).length, BARK, rot=_euler_to(tip - hand), bevel=.01, verts=10)
    for sx in (-1, 1):
        end = tip + Vector((sx * 1.1, -.9, .5)); mid = (tip + end) / 2
        b.cyl('rod fork', mid, .1, (end - tip).length, BARK, rot=_euler_to(end - tip), bevel=.01, verts=10); b.ball('rod bud', end, .1, GLOW_TEAL)
    for k in range(5): b.ball('dowse drop', tip + Vector((rnd.uniform(-1, 1), rnd.uniform(-1.6, -.5), rnd.uniform(-1.2, .8))), (.07, .07, .13), GLOW_TEAL)
    # wind swirls and the opening-day sign
    for k in range(5):
        a = k * 1.25; pts = [(math.cos(a + j * .7) * (2.2 + j * .25), math.sin(a + j * .7) * (2.2 + j * .25), .6 + j * .8) for j in range(6)]
        b.sweep('wind', pts, lambda t: (.05, .05), (1, 0, 0), WHITE, sides=5)
    b.box('sign board', (3.2, -3.0, .9), (2.0, .12, 1.0), YELLOW, bevel=.04, rot=(0, 0, -8)); b.cyl('sign post', (3.2, -3.0, .35), .06, .7, WOOD_DK, bevel=0)
    for k in range(6): b.box('sign text', (2.6 + k * .24, -3.08, .95), (.14, .02, .4), RED, bevel=0, rot=(0, 0, -8))
    for k in range(12): b.box('grass', (rnd.uniform(-3.5, 3.5), rnd.uniform(-3.5, 2), .12), (.05, .05, .25), mat('Grass', (.3, .7, .3, 1)), bevel=0, rot=(rnd.uniform(-20, 20), 0, 0))
    return b
