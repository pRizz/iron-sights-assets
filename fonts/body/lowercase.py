"""Body font lowercase. Font units: x-height X, ascender A, descender D, ink
from x 0 to W.

Drawn from scratch for this project; see the repository's provenance rules.
"""
from tools.bodypen import HUGE, N, Registry

GLYPHS = Registry()


def glyph(chars, width, sb=(62, 62)):
    return GLYPHS.glyph(chars, width, sb, case='lower')


ROUND_SB = (36, 36)
BOWL_REACH = 70  # how far a bowl's ring runs past its stem's left edge


def half_width(p, k=1.0):
    """Half the horizontal width of a steep diagonal, for placing its foot."""
    return (p.t + 0.9 ** 2 * (p.T - p.t)) * k / 2 / 0.9


def arch(p, x_stem, x_leg):
    """The shoulder of n, h and m: up the leg at x_leg, over, and down into
    the stem at x_stem, thinning where it joins."""
    leg = x_leg + p.T / 2
    apex = (x_stem + p.T + x_leg) / 2 + 0.06 * (x_leg - x_stem - p.T)
    top = p.X + p.o - p.t / 2
    p.stroke(N(leg, 0, 90), N(leg, top - 1.05 * (leg - apex), 90), N(apex, top, 180),
             N(x_stem + 0.55 * p.T, 0.60 * p.X, 255, k=0.55))


def bowl_with_stem(p, y0, y1):
    """A round bowl on a stem at x 0..T running from y0 to y1 (b and p)."""
    p.ring(-BOWL_REACH, -p.o, p.W, p.X + p.o)
    p.clip(0.5 * p.T, -HUGE, HUGE, HUGE)
    p.stem(0, y0, y1)


def k_shape(p):
    arm0, arm1 = (0.6 * p.T, 0.24 * p.X), (p.W - 50, p.X)
    p.diag(arm0, arm1)
    x = 0.5 * p.W
    t = (x - arm0[0]) / (arm1[0] - arm0[0])
    p.diag((x, arm0[1] + t * (arm1[1] - arm0[1]) + 12), (p.W - 50, 0), reach0=0)
    p.clip(0.4 * p.T, 0, p.W, p.X)


@glyph('a', 425, sb=(36, 62))
def _a(p):
    right = p.W - p.T / 2
    p.stroke(N(right, 0, 90), N(right, 0.58 * p.X, 90), N(0.48 * p.W, p.X + p.o - p.t / 2, 180),
             N(0.55 * p.T, 0.72 * p.X, 250), cut1=0)
    p.stroke(N(p.W - 0.6 * p.T, 0.49 * p.X, 180), N(0.45 * p.W, 0.49 * p.X, 180), N(p.T / 2, 0.25 * p.X, 270),
             N(0.42 * p.W, p.t / 2 - p.o, 0), N(p.W - 0.7 * p.T, 0.20 * p.X, 45, k=0.6))


@glyph('b', 495, sb=(62, 36))
def _b(p):
    bowl_with_stem(p, 0, p.A)


@glyph('c', 470, sb=(36, 30))
def _c(p):
    p.ring(0, -p.o, p.W, p.X + p.o)
    p.cut(0.5 * p.W, 0.31 * p.X, HUGE, 0.69 * p.X)


@glyph('d', 495, sb=(36, 62))
def _d(p):
    bowl_with_stem(p, 0, p.A)
    p.mirror()


@glyph('e', 485, sb=(36, 34))
def _e(p):
    bar = 0.42 * p.X
    p.ring(0, -p.o, p.W, p.X + p.o)
    p.cut(0.5 * p.W, 0.28 * p.X, HUGE, bar)
    p.bar(0.5 * p.T, p.W - 0.4 * p.T, bar)


@glyph('f', 300, sb=(24, 4))
def _f(p):
    x = 44 + p.T / 2
    top = p.A + 8 - p.t / 2
    p.stroke(N(x, 0, 90), N(x, p.A - 175, 90), N(x + 120, top, 0), N(p.W, top - 14, 352), cut1=90)
    p.bar(0, p.W - 40, p.X - p.t)


@glyph('g', 495, sb=(36, 62))
def _g(p):
    bowl_with_stem(p, 0, p.X)
    p.mirror()
    right = p.W - p.T / 2
    p.stroke(N(right, 10, 270), N(right, p.D + 150, 270), N(0.48 * p.W, p.D - p.o + p.t / 2, 180),
             N(0.6 * p.T, p.D + 125, 115), cut1=0)


@glyph('h', 425)
def _h(p):
    p.stem(0, 0, p.A)
    arch(p, 0, p.W - p.T)


@glyph('i', lambda p: p.T)
def _i(p):
    p.stem(0, 0, p.X)
    p.dot(0, p.X + 88)


@glyph('j', 222, sb=(8, 62))
def _j(p):
    right = p.W - p.T / 2
    bottom = p.D - p.o + p.t / 2
    p.stroke(N(right, p.X, 270), N(right, p.D + 140, 270), N(right - 110, bottom, 180), N(0, bottom + 6, 184), cut1=90)
    p.dot(p.W - p.T, p.X + 88)


@glyph('k', 425, sb=(62, 10))
def _k(p):
    k_shape(p)
    p.stem(0, 0, p.A)


@glyph('l', lambda p: p.T)
def _l(p):
    p.stem(0, 0, p.A)


@glyph('m', 745)
def _m(p):
    mid = (p.W - p.T) / 2
    p.stem(0, 0, p.X)
    arch(p, 0, mid)
    arch(p, mid, p.W - p.T)


@glyph('n', 425)
def _n(p):
    p.stem(0, 0, p.X)
    arch(p, 0, p.W - p.T)


@glyph('o', 490, sb=ROUND_SB)
def _o(p):
    p.ring(0, -p.o, p.W, p.X + p.o)


@glyph('p', 495, sb=(62, 36))
def _p(p):
    bowl_with_stem(p, p.D, p.X)


@glyph('q', 495, sb=(36, 62))
def _q(p):
    bowl_with_stem(p, p.D, p.X)
    p.mirror()


@glyph('r', 290, sb=(62, 8))
def _r(p):
    top = p.X + p.o - p.t / 2
    p.stem(0, 0, p.X)
    p.stroke(N(0.55 * p.T, 0.55 * p.X, 70, k=0.55), N(p.T + 110, top, 0), N(p.W, top - 22, 345), cut1=90)


@glyph('s', 430, sb=(32, 32))
def _s(p):
    p.s_curve(p.X, spine=1.08)


@glyph('t', 300, sb=(20, 10))
def _t(p):
    x = 44 + p.T / 2
    p.stroke(N(x, 0.89 * p.A, 270), N(x, 150, 270), N(x + 110, p.t / 2 - p.o, 0), N(p.W, p.t / 2 - p.o + 32, 24), cut1=90)
    p.bar(0, p.W - 30, p.X - p.t)


@glyph('u', 425)
def _u(p):
    p.stem(0, 0, p.X)
    arch(p, 0, p.W - p.T)
    p.rotate(p.X / 2)


@glyph('v', 500, sb=(8, 8))
def _v(p):
    hw = half_width(p)
    p.diag((hw, p.X), (p.W / 2, 0))
    p.diag((p.W - hw, p.X), (p.W / 2, 0))
    p.clip(0, 0, p.W, p.X)


@glyph('w', 750, sb=(6, 6))
def _w(p):
    hw = half_width(p, 0.88)
    for top, foot in ((hw, 0.27), (0.5 * p.W, 0.27), (0.5 * p.W, 0.73), (p.W - hw, 0.73)):
        p.diag((top, p.X), (foot * p.W, 0), k=0.88)
    p.clip(0, 0, p.W, p.X)


@glyph('x', 485, sb=(10, 10))
def _x(p):
    hw = half_width(p)
    p.diag((hw, p.X), (p.W - hw, 0))
    p.diag((p.W - hw, p.X), (hw, 0))
    p.clip(0, 0, p.W, p.X)


@glyph('y', 500, sb=(8, 8))
def _y(p):
    hw = half_width(p)
    p.diag((hw, p.X), (p.W / 2, 0), reach1=0)
    p.diag((p.W - hw, p.X), (p.W / 2, 0))
    p.clip(0, p.D, p.W, p.X)


@glyph('z', 430, sb=(28, 28))
def _z(p):
    p.corner_diag((p.W - 10, p.X - p.t), (0, p.t))
    p.clip(0, 0, p.W - 10, p.X)
    p.bar(0, p.W - 10, p.X - p.t)
    p.bar(0, p.W, 0)
