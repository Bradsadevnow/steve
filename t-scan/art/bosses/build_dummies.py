"""Crash-test dummies: one unarmed, one with a melee weapon, one with a ranged weapon. 1 cell (2 m), about 1.9 m tall, front toward -Y.
Exec after boss_helpers. They share one body builder so only the arms and the weapon differ."""

DUMMY = mat('Dummy yellow', (.98, .82, .1, 1), 0, .45); DUMMY_JOINT = mat('Dummy joint', (.07, .07, .09, 1), 0, .6)
DUMMY_RED = mat('Dummy target red', (.9, .12, .12, 1), 0, .4); DUMMY_WHITE = mat('Dummy target white', (.96, .96, .94, 1), 0, .5)


def _arm(b, sx, hand, elbow=None):
    sh = Vector((sx * .33, 0, 1.52)); hand = Vector(hand); elbow = Vector(elbow) if elbow is not None else (sh + hand) / 2 + Vector((sx * .08, .02, -.03))
    b.ball('shoulder', tuple(sh), .085, DUMMY_JOINT)
    b.tube('upper arm', [tuple(sh), tuple(elbow)], .06, .055, DUMMY); b.ball('elbow', tuple(elbow), .065, DUMMY_JOINT)
    b.tube('forearm', [tuple(elbow), tuple(hand)], .055, .05, DUMMY); b.ball('hand', tuple(hand), (.075, .075, .08), DUMMY_JOINT)


def _sword(b, hand):
    x, y, z = hand; t = math.radians(25); d = Vector((0, -math.sin(t), math.cos(t)))
    rot = (25, 0, 0); base = Vector(hand)
    b.cyl('grip', base + d * .0, .03, .2, WOOD_DK, rot=rot, bevel=.005, verts=10)
    b.ball('pommel', base - d * .12, .045, GOLD); b.box('guard', base + d * .12, (.38, .06, .07), GOLD, bevel=.015, rot=rot)
    b.box('blade', base + d * (.12 + .4), (.13, .03, .78), STEEL, bevel=.01, rot=rot)
    b.cyl('blade tip', base + d * (.12 + .84), .09, .14, STEEL, r2=.004, rot=rot, bevel=0, verts=4)
    b.box('fuller', base + d * (.12 + .4), (.03, .034, .6), IRON, bevel=0, rot=rot)


def _crossbow(b):
    y0 = -.42; z0 = 1.38
    b.box('stock', (0, y0, z0), (.12, .62, .14), WOOD_DK, bevel=.03); b.box('stock butt', (0, y0 + .33, z0 - .02), (.1, .12, .14), WOOD_DK, bevel=.02)
    b.box('trigger guard', (0, y0 + .05, z0 - .09), (.05, .12, .03), IRON, bevel=0); b.box('rail', (0, y0 - .05, z0 + .06), (.04, .55, .03), STEEL, bevel=0)
    for sx in (-1, 1):
        b.box('limb', (sx * .2, y0 - .3, z0 + .02), (.36, .07, .08), WOOD_LT, bevel=.02, rot=(0, 0, sx * -18))
        b.box('limb tip', (sx * .4, y0 - .26, z0 + .02), (.16, .07, .08), WOOD_LT, bevel=.02, rot=(0, 0, sx * -48))
    b.box('string L', (-.2, y0 - .22, z0 + .03), (.4, .01, .01), WHITE, bevel=0, rot=(0, 0, 38)); b.box('string R', (.2, y0 - .22, z0 + .03), (.4, .01, .01), WHITE, bevel=0, rot=(0, 0, -38))
    b.cyl('bolt', (0, y0 - .02, z0 + .1), .02, .5, WOOD_LT, rot=(90, 0, 0), bevel=0, verts=6); b.cyl('bolt head', (0, y0 - .3, z0 + .1), .035, .09, STEEL, r2=.002, rot=(90, 0, 0), bevel=0, verts=6)


def build_dummy(variant):
    names = {'unarmed': ('dummy_unarmed', 'A crash-test dummy with empty hands.'), 'melee': ('dummy_melee', 'A crash-test dummy with a sword.'), 'ranged': ('dummy_ranged', 'A crash-test dummy with a crossbow.')}
    n, note = names[variant]
    b = Boss(n, 'dummies', note, cells=1)
    # legs: black ankles and knees, yellow limbs
    for sx in (-1, 1):
        x = sx * .17
        b.box('foot', (x, -.08, .07), (.24, .46, .14), DUMMY_JOINT, bevel=.04); b.ball('ankle', (x, 0, .17), .07, DUMMY_JOINT)
        b.tube('shin', [(x, 0, .2), (x, 0, .5)], .068, .062, DUMMY); b.ball('knee', (x, 0, .52), .08, DUMMY_JOINT)
        b.tube('thigh', [(x, 0, .55), (x, 0, .88)], .09, .075, DUMMY)
    b.box('pelvis', (0, 0, .96), (.44, .24, .2), DUMMY, bevel=.05); b.cyl('waist', (0, 0, 1.08), .1, .08, DUMMY_JOINT, bevel=0)
    # torso with a bullseye target on the chest
    b.box('torso', (0, 0, 1.36), (.52, .27, .56), DUMMY, bevel=.07, seg=3)
    b.cyl('chest target red', (0, -.145, 1.4), .15, .01, DUMMY_RED, rot=(90, 0, 0), bevel=0, verts=32); b.cyl('chest target white', (0, -.15, 1.4), .1, .01, DUMMY_WHITE, rot=(90, 0, 0), bevel=0, verts=32)
    b.cyl('chest target bullseye', (0, -.155, 1.4), .045, .01, DUMMY_RED, rot=(90, 0, 0), bevel=0, verts=24)
    for k in (-1, 1): b.box('chest stripe', (k * .17, -.14, 1.18), (.1, .01, .05), DUMMY_JOINT, bevel=0)
    # neck and a round head with black quadrant marks and googly eyes
    b.cyl('neck', (0, 0, 1.68), .06, .1, DUMMY_JOINT, bevel=0, verts=12); b.ball('head', (0, 0, 1.84), (.18, .17, .18), DUMMY)
    b.cyl('head mark L', (-.17, -.02, 1.84), .09, .01, DUMMY_JOINT, rot=(0, 90, 0), bevel=0, verts=16); b.cyl('head mark R', (.17, -.02, 1.84), .09, .01, DUMMY_JOINT, rot=(0, 90, 0), bevel=0, verts=16)
    for sx in (-1, 1): b.eye('eye', (sx * .07, -.16, 1.88), .05, look=(0, -1, 0)); b.box('brow', (sx * .07, -.17, 1.95), (.08, .015, .02), DUMMY_JOINT, bevel=0, rot=(0, 0, sx * -10))
    b.box('mouth', (0, -.17, 1.77), (.08, .012, .015), DUMMY_JOINT, bevel=0)
    # arms and gear
    if variant == 'unarmed':
        _arm(b, -1, (-.44, -.08, .98), (-.4, 0, 1.24)); _arm(b, 1, (.44, -.08, .98), (.4, 0, 1.24))
    elif variant == 'melee':
        _arm(b, 1, (.42, -.38, 1.36), (.45, -.2, 1.34)); _arm(b, -1, (-.44, -.1, 1.0), (-.4, 0, 1.24)); _sword(b, (.42, -.38, 1.36))
    else:
        _arm(b, 1, (.07, -.3, 1.34), (.32, -.12, 1.4)); _arm(b, -1, (-.04, -.62, 1.36), (-.28, -.3, 1.4)); _crossbow(b)
    # a little floor plate so each stands like a display piece
    b.cyl('base', (0, -.05, .0), .5, .04, mat('Dummy base grey', (.4, .42, .48, 1), .3, .5), bevel=.01, verts=32)
    return b
