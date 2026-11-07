"""Body font figures: cap height H, capital weights, one shared advance so
changing numbers do not shift.

Drawn from scratch for this project; see the repository's provenance rules.
"""
import math

from tools.bodypen import HUGE, N, Registry

GLYPHS = Registry()
ADVANCE = 580


def glyph(ch, width, left=None):
    """A figure of drawn width `width`, centred in the shared advance unless
    `left` sets its left sidebearing."""
    return GLYPHS.glyph(ch, width, sb=(left, None), maybe_advance=ADVANCE)


def upper_terminal(p, height):
    """The rising curve over the top of 2, 3 and ?: from a left terminal over
    to the right side, as nodes to continue."""
    return [N(p.T / 2 + 4, 0.69 * height, 80), N(0.5 * p.W, height + p.o - p.t / 2, 0)]


@glyph('0', 500)
def _0(p):
    p.ring(0, -p.o, p.W, p.H + p.o)


@glyph('1', 300, left=110)
def _1(p):
    p.diag((p.W - p.T / 2, p.H - p.t / 2), (40, p.H - 200), k=0.9, reach0=0, reach1=0)
    p.clip(y1=p.H)
    p.stem(p.W - p.T, 0, p.H)


@glyph('2', 500)
def _2(p):
    # From the bowl the stroke sweeps into one straight diagonal that lands
    # in the bar's left corner.
    slope, mid_y = 228, 0.36 * p.H
    dx, dy = math.cos(math.radians(slope)), math.sin(math.radians(slope))
    # The stroke's left edge meets the bar's top at its left end.
    hw = p.slant_half((0, 0), (dx, dy))
    foot = (hw - (p.t / 2) * dx / dy, p.t / 2)
    mid = (foot[0] + dx * (mid_y - foot[1]) / dy, mid_y)
    p.stroke(*upper_terminal(p, p.H), N(p.W - p.T / 2, 0.71 * p.H, 270), N(*mid, slope), N(*foot, slope), cut0=0)
    p.clip(x0=0)
    p.bar(0, p.W, 0)


@glyph('3', 500)
def _3(p):
    mid = 0.545 * p.H
    p.stroke(*upper_terminal(p, p.H), N(p.W - p.T / 2 - 20, 0.77 * p.H, 270), N(0.55 * p.W, mid, 180),
             N(0.30 * p.W, mid, 180), cut0=0)
    p.stroke(N(0.30 * p.W, mid, 0), N(0.55 * p.W, mid, 0), N(p.W - p.T / 2, 0.27 * p.H, 270),
             N(0.48 * p.W, p.t / 2 - p.o, 180), N(p.T / 2 + 4, 0.26 * p.H, 100), cut1=0)


@glyph('4', 520)
def _4(p):
    stem = p.W - p.T - 40
    bar = 0.22 * p.H
    p.corner_diag((stem + 10, p.H), (0, bar + p.t), k=0.95)
    p.clip(0, bar, p.W, p.H)
    p.stem(stem, 0, p.H)
    p.bar(0, p.W, bar)


@glyph('5', 500)
def _5(p):
    left = 0.06 * p.W
    p.bar(left, p.W - 10, p.H - p.t)
    p.stroke(N(left + p.T / 2, 0.52 * p.H, 60, k=0.7), N(0.55 * p.W, 0.63 * p.H, 0), N(p.W - p.T / 2, 0.33 * p.H, 270),
             N(0.48 * p.W, p.t / 2 - p.o, 180), N(p.T / 2 + 4, 0.25 * p.H, 105), cut1=0)
    p.cut(-HUGE, 0.45 * p.H, left, HUGE)  # the bowl starts inside the upright, never beside it
    p.stem(left, 0.48 * p.H, p.H, k=0.95)


def six(p):
    p.ring(0, -p.o, p.W, 0.64 * p.H)
    p.stroke(N(p.T / 2, 0.32 * p.H, 90), N(p.T / 2, 0.50 * p.H, 90), N(0.52 * p.W, p.H + p.o - p.t / 2, 0),
             N(p.W - p.T / 2 - 10, 0.79 * p.H, 290), cut1=0)


@glyph('6', 505)
def _6(p):
    six(p)


@glyph('7', 500)
def _7(p):
    # The diagonal's right edge meets the bar's lower right corner, so
    # nothing shows past the bar.
    top = p.H - p.t
    foot = (0.30 * p.W, 0)
    hw = p.slant_half(foot, (p.W, top))
    for _ in range(3):
        hw = p.slant_half(foot, (p.W - hw, top))
    p.diag((p.W - hw, top), foot)
    p.clip(0, 0, p.W, top + 1)
    p.bar(0, p.W, top)


@glyph('8', 510)
def _8(p):
    mid = 0.555 * p.H
    p.ring(0.06 * p.W, mid - p.t / 2, 0.94 * p.W, p.H + p.o)
    p.ring(0, -p.o, p.W, mid + p.t / 2)


@glyph('9', 505)
def _9(p):
    six(p)
    p.rotate(p.H / 2)
