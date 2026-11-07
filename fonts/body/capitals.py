"""Body font capitals. Font units: cap height H, ink from x 0 to W.

Drawn from scratch for this project; see the repository's provenance rules.
"""
from tools.bodypen import HUGE, N, Registry

GLYPHS = Registry()
glyph = GLYPHS.glyph

STEM_SB = (72, 72)
ROUND_SB = (42, 42)


def half_width(p, k=1.0):
    """Half the horizontal width of a steep diagonal, for placing its foot."""
    return (p.t + 0.94 ** 2 * (p.T - p.t)) * k / 2 / 0.94


def arm_point(arm0, arm1, x, lift=15):
    """Where K's leg starts: on the arm's centreline at x, lifted a little
    so the leg's square end stays inside the arm."""
    t = (x - arm0[0]) / (arm1[0] - arm0[0])
    return (x, arm0[1] + t * (arm1[1] - arm0[1]) + lift)


@glyph('A', 650, sb=(12, 12))
def _a(p):
    hw = half_width(p)
    p.diag((hw, 0), (p.W / 2, p.H))
    p.diag((p.W - hw, 0), (p.W / 2, p.H))
    p.clip(0, 0, p.W, p.H)
    p.bar(hw + 40, p.W - hw - 40, 0.25 * p.H)


@glyph('B', 545, sb=(72, 40))
def _b(p):
    mid = 0.535 * p.H
    p.lobe(p.W - 28, mid - p.t / 2, p.H)
    p.lobe(p.W, 0, mid + p.t / 2)
    p.stem(0, 0, p.H)


@glyph('C', 590, sb=ROUND_SB)
def _c(p):
    p.ring(0, -p.o, p.W, p.H + p.o)
    p.cut(0.5 * p.W, 0.31 * p.H, HUGE, 0.69 * p.H)


@glyph('D', 585, sb=(72, 42))
def _d(p):
    p.lobe(p.W, 0, p.H, roundness=1.0)
    p.stem(0, 0, p.H)


@glyph('E', 480, sb=(72, 34))
def _e(p):
    p.stem(0, 0, p.H)
    p.bar(0, p.W - 12, p.H - p.t)
    p.bar(0, p.W - 40, (p.H - p.t) / 2)
    p.bar(0, p.W, 0)


@glyph('F', 460, sb=(72, 28))
def _f(p):
    p.stem(0, 0, p.H)
    p.bar(0, p.W, p.H - p.t)
    p.bar(0, p.W - 30, (p.H - p.t) / 2 - 10)


@glyph('G', 610, sb=(42, 58))
def _g(p):
    bar_top = 0.48 * p.H
    p.ring(0, -p.o, p.W, p.H + p.o)
    p.cut(0.5 * p.W, bar_top, HUGE, 0.69 * p.H)
    p.rect(0.52 * p.W, bar_top - p.t, p.W - p.T / 2, bar_top)  # ends inside the bowl's side


@glyph('H', 565, sb=STEM_SB)
def _h(p):
    p.stem(0, 0, p.H)
    p.stem(p.W - p.T, 0, p.H)
    p.bar(p.T / 2, p.W - p.T / 2, (p.H - p.t) / 2 + 6)


@glyph('I', lambda p: p.T, sb=STEM_SB)
def _i(p):
    p.stem(0, 0, p.H)


@glyph('J', 430, sb=(26, 72))
def _j(p):
    top = 500
    mid = (top - p.o) / 2
    p.ring(0, -p.o, p.W, top)
    p.cut(-HUGE, mid, HUGE, HUGE)
    p.cut(-HUGE, 0.27 * p.H, p.W / 2, HUGE)
    p.stem(p.W - p.T, mid, p.H)


@glyph('K', 555, sb=(72, 12))
def _k(p):
    arm0, arm1 = (0.6 * p.T, 0.30 * p.H), (p.W - 70, p.H)
    p.diag(arm0, arm1)
    p.diag(arm_point(arm0, arm1, 270), (p.W - 70, 0), reach0=0)
    p.clip(0.4 * p.T, 0, p.W, p.H)
    p.stem(0, 0, p.H)


@glyph('L', 455, sb=(72, 20))
def _l(p):
    p.stem(0, 0, p.H)
    p.bar(0, p.W, 0)


@glyph('M', 710, sb=STEM_SB)
def _m(p):
    p.diag((0.62 * p.T, p.H), (p.W / 2, -10), k=0.86)
    p.diag((p.W - 0.62 * p.T, p.H), (p.W / 2, -10), k=0.86)
    p.clip(0, 0, p.W, p.H)
    p.stem(0, 0, p.H)
    p.stem(p.W - p.T, 0, p.H)


@glyph('N', 555, sb=STEM_SB)
def _n(p):
    p.diag((0.6 * p.T, p.H), (p.W - 0.6 * p.T, 0), k=0.97)
    p.clip(0, 0, p.W, p.H)
    p.stem(0, 0, p.H, k=0.94)
    p.stem(p.W - 0.94 * p.T, 0, p.H, k=0.94)


@glyph('O', 640, sb=ROUND_SB)
def _o(p):
    p.ring(0, -p.o, p.W, p.H + p.o)


@glyph('P', 525, sb=(72, 30))
def _p(p):
    p.lobe(p.W, 0.37 * p.H, p.H)
    p.stem(0, 0, p.H)


@glyph('Q', 650, sb=(42, 30))
def _q(p):
    p.ring(0, -p.o, p.W - 10, p.H + p.o)
    p.stroke(N(0.58 * p.W, 0.23 * p.H), N(p.W, -0.06 * p.H), k=0.92)
    p.clip(x1=p.W)


@glyph('R', 555, sb=(72, 24))
def _r(p):
    bottom = 0.37 * p.H
    # The leg starts inside the bowl's lower bar and is cut at its top, so
    # its square start never shows in the counter.
    p.diag((0.36 * p.W, bottom + p.t / 2), (p.W - 60, 0))
    p.clip(-HUGE, 0, p.W, bottom + p.t)
    p.lobe(p.W - 30, bottom, p.H)
    p.stem(0, 0, p.H)


@glyph('S', 545, sb=(36, 36))
def _s(p):
    p.s_curve(p.H)


@glyph('T', 570, sb=(16, 16))
def _t(p):
    p.bar(0, p.W, p.H - p.t)
    p.stem((p.W - p.T) / 2, 0, p.H)


@glyph('U', 565, sb=(70, 70))
def _u(p):
    top = 560
    mid = (top - p.o) / 2
    p.ring(0, -p.o, p.W, top)
    p.cut(-HUGE, mid, HUGE, HUGE)
    p.stem(0, mid, p.H)
    p.stem(p.W - p.T, mid, p.H)


@glyph('V', 630, sb=(10, 10))
def _v(p):
    hw = half_width(p)
    p.diag((hw, p.H), (p.W / 2, 0))
    p.diag((p.W - hw, p.H), (p.W / 2, 0))
    p.clip(0, 0, p.W, p.H)


@glyph('W', 900, sb=(8, 8))
def _w(p):
    hw = half_width(p, 0.9)
    for top, foot in ((hw, 0.27), (0.5 * p.W, 0.27), (0.5 * p.W, 0.73), (p.W - hw, 0.73)):
        p.diag((top, p.H), (foot * p.W, 0), k=0.9)
    p.clip(0, 0, p.W, p.H)


@glyph('X', 620, sb=(12, 12))
def _x(p):
    hw = half_width(p)
    p.diag((hw, p.H), (p.W - hw, 0))
    p.diag((p.W - hw, p.H), (hw, 0))
    p.clip(0, 0, p.W, p.H)


@glyph('Y', 625, sb=(8, 8))
def _y(p):
    hw = half_width(p)
    fork = (p.W / 2, 0.42 * p.H)
    p.diag((hw, p.H), fork, reach1=40)
    p.diag((p.W - hw, p.H), fork, reach1=40)
    p.clip(0, 0, p.W, p.H)
    p.stem((p.W - p.T) / 2, 0, 0.45 * p.H)


@glyph('Z', 545, sb=(30, 30))
def _z(p):
    p.corner_diag((p.W - 10, p.H - p.t), (0, p.t))
    p.clip(0, 0, p.W - 10, p.H)
    p.bar(0, p.W - 10, p.H - p.t)
    p.bar(0, p.W, 0)
