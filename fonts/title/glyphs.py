"""Glyph skeletons for the title font: squared geometric capitals.

Each definition draws centerline paths on a Pen (see tools/glyphpen.py) sized
by the build: H is the letter height (cap height for capitals and figures,
small-cap height for lowercase), W the box width and w the stroke weight.
Widths are given as a fraction of H, or as a function of (H, w).

Drawn from scratch for this project; see the repository's provenance rules.
"""

GLYPHS = {}  # char -> (width, maybe_band, mirror, draw)


def glyph(chars, width, maybe_band=None):
    """Register draw for each char; maybe_band (lo, hi) as fractions of H
    overrides the default 0..H clip. mirrored() reuses a drawing flipped."""
    def register(draw):
        for ch in chars:
            GLYPHS[ch] = (width, maybe_band, False, draw)
        return draw
    return register


def mirrored(ch, source):
    width, maybe_band, _, draw = GLYPHS[source]
    GLYPHS[ch] = (width, maybe_band, True, draw)


def stem_width(scale=1.0):
    return lambda H, w: w * scale


# --- Capitals (lowercase reuses them as small capitals) ---------------------

def _x_at(p0, p1, y):
    """x where the line through p0 and p1 crosses height y."""
    (x0, y0), (x1, y1) = p0, p1
    return x0 + (x1 - x0) * (y - y0) / (y1 - y0)


HOOK = 0.17        # length of the question mark's top hook, as a fraction of H
SHORT_HOOK = 0.10  # terminal hooks on C, S, 2, 3 and 7


@glyph('A', 0.92)
def _a(p):
    # Diagonal sides almost meeting at a small flat top, cut flat at the baseline.
    left = ((p.L - 0.1 * p.w, -p.w), (p.C - 0.06 * p.W, p.T))
    right = ((p.R + 0.1 * p.w, -p.w), (p.C + 0.06 * p.W, p.T))
    p.line(left[0], left[1], right[1], right[0], ends='butt')
    y = 0.36 * p.H
    p.line((_x_at(*left, y), y), (_x_at(*right, y), y), ends='butt')


@glyph('B', 0.90)
def _b(p):
    xt = p.R - 0.12 * p.W
    p.path((p.L, p.B), (p.L, p.T), (xt, p.T), (xt, p.M), (p.L, p.M), maybe_r=0, maybe_radii={2: p.bowl * 0.8, 3: p.bowl * 0.8})
    p.path((p.L, p.M), (p.R, p.M), (p.R, p.B), (p.L, p.B), maybe_r=0, maybe_radii={1: p.bowl * 0.8, 2: p.bowl})


@glyph('C', 0.88)
def _c(p):
    hook = SHORT_HOOK * p.H
    p.path((p.R, p.T - hook), (p.R, p.T), (p.L, p.T), (p.L, p.B), (p.R, p.B), (p.R, p.B + hook),
           maybe_radii={1: p.bowl * 0.6, 4: p.bowl * 0.6})


@glyph('D', 0.92)
def _d(p):
    p.path((p.L, p.B), (p.L, p.T), (p.R, p.T), (p.R, p.B), maybe_r=0, maybe_radii={2: p.bowl, 3: p.bowl}, closed=True)


@glyph('E', 0.82)
def _e(p):
    p.line((p.R, p.T), (p.L, p.T), (p.L, p.B), (p.R, p.B))
    p.line((p.L, p.M), (p.R - 0.10 * p.W, p.M))


@glyph('F', 0.80)
def _f(p):
    p.line((p.R, p.T), (p.L, p.T), (p.L, p.B))
    p.line((p.L, p.M), (p.R - 0.12 * p.W, p.M))


@glyph('G', 0.92)
def _g(p):
    p.path((p.R, p.T), (p.L, p.T), (p.L, p.B), (p.R, p.B), (p.R, p.M), (p.C + 0.05 * p.W, p.M), maybe_radii={4: 0})


@glyph('H', 0.92)
def _h(p):
    p.line((p.L, p.B), (p.L, p.T))
    p.line((p.R, p.B), (p.R, p.T))
    p.line((p.L, p.M), (p.R, p.M))


@glyph('I', stem_width())
def _i(p):
    p.line((p.C, p.B), (p.C, p.T))


@glyph('J', 0.80)
def _j(p):
    p.path((p.R, p.T), (p.R, p.B), (p.L, p.B), (p.L, p.B + 0.30 * p.H))


@glyph('K', 0.90)
def _k(p):
    p.line((p.L, p.B), (p.L, p.T))
    joint = p.L + 0.45 * p.w
    p.line((p.R + 0.35 * p.w, p.H + p.w), (joint, p.M), (p.R + 0.35 * p.w, -p.w), ends='butt')


@glyph('L', 0.78)
def _l(p):
    p.line((p.L, p.T), (p.L, p.B), (p.R, p.B))


@glyph('M', 1.08)
def _m(p):
    # The V stops short of the baseline.
    p.line((p.L, p.B), (p.L, p.T), (p.C, 0.30 * p.H), (p.R, p.T), (p.R, p.B))


@glyph('N', 0.95)
def _n(p):
    p.line((p.L, p.B), (p.L, p.T), (p.R, p.B), (p.R, p.T))


@glyph('O', 0.95)
def _o(p):
    p.path((p.L, p.B), (p.L, p.T), (p.R, p.T), (p.R, p.B), closed=True)


@glyph('P', 0.88)
def _p(p):
    p.path((p.L, p.B), (p.L, p.T), (p.R, p.T), (p.R, p.M), (p.L, p.M), maybe_r=0, maybe_radii={2: p.bowl, 3: p.bowl})


@glyph('Q', 0.95, maybe_band=(-0.14, 1.0))
def _q(p):
    p.path((p.L, p.B), (p.L, p.T), (p.R, p.T), (p.R, p.B), closed=True)
    # The tail runs from inside the bowl out through its bottom edge.
    p.line((p.C, 0.34 * p.H), (p.R - 0.04 * p.W, -0.30 * p.H), ends='butt')


@glyph('R', 0.90)
def _r(p):
    p.path((p.L, p.B), (p.L, p.T), (p.R, p.T), (p.R, p.M), (p.L, p.M), maybe_r=0, maybe_radii={2: p.bowl, 3: p.bowl})
    p.line((p.C - 0.05 * p.W, p.M), (p.R + 0.30 * p.w, -p.w), ends='butt')


@glyph('S', 0.88)
def _s(p):
    hook = SHORT_HOOK * p.H
    p.path((p.R, p.T - hook), (p.R, p.T), (p.L, p.T), (p.L, p.M), (p.R, p.M), (p.R, p.B), (p.L, p.B),
           (p.L, p.B + hook), maybe_radii={1: p.bowl * 0.6, 6: p.bowl * 0.6})


@glyph('T', 0.86)
def _t(p):
    p.line((p.L, p.T), (p.R, p.T))
    p.line((p.C, p.T), (p.C, p.B))


@glyph('U', 0.92)
def _u(p):
    p.path((p.L, p.T), (p.L, p.B), (p.R, p.B), (p.R, p.T))


@glyph('V', 0.94)
def _v(p):
    p.line((p.L - 0.30 * p.w, p.H + p.w), (p.C, 0.15 * p.w), (p.R + 0.30 * p.w, p.H + p.w), ends='butt')


@glyph('W', 1.20)
def _w(p):
    # Diagonal legs down to two points, rising to a centre apex at the top.
    low = 0.15 * p.w
    p.line((p.L - 0.3 * p.w, p.H + p.w), (0.27 * p.W, low), (p.C, p.T), (0.73 * p.W, low),
           (p.R + 0.3 * p.w, p.H + p.w), ends='butt')


@glyph('X', 0.92)
def _x(p):
    p.line((p.L - 0.35 * p.w, p.H + p.w), (p.R + 0.35 * p.w, -p.w), ends='butt')
    p.line((p.R + 0.35 * p.w, p.H + p.w), (p.L - 0.35 * p.w, -p.w), ends='butt')


@glyph('Y', 0.92)
def _y(p):
    p.line((p.L - 0.3 * p.w, p.H + p.w), (p.C, p.M), (p.R + 0.3 * p.w, p.H + p.w), ends='butt')
    p.line((p.C, p.M), (p.C, p.B))


@glyph('Z', 0.86)
def _z(p):
    p.line((p.L, p.T), (p.R, p.T), (p.L, p.B), (p.R, p.B))


# --- Figures: one shared width, so changing numbers do not shift -------------

FIGURE = 0.80


@glyph('0', FIGURE)
def _0(p):
    p.path((p.L, p.B), (p.L, p.T), (p.R, p.T), (p.R, p.B), closed=True)


@glyph('1', FIGURE)
def _1(p):
    x = p.C + 0.12 * p.W
    p.line((p.C - 0.22 * p.W, p.T), (x, p.T), (x, p.B))


@glyph('2', FIGURE)
def _2(p):
    hook = SHORT_HOOK * p.H
    p.path((p.L, p.T - hook), (p.L, p.T), (p.R, p.T), (p.R, p.M), (p.L, p.M), (p.L, p.B), (p.R, p.B),
           (p.R, p.B + hook), maybe_radii={1: p.bowl * 0.6, 6: p.bowl * 0.6})


@glyph('3', FIGURE)
def _3(p):
    hook = SHORT_HOOK * p.H
    p.path((p.L, p.T - hook), (p.L, p.T), (p.R, p.T), (p.R, p.B), (p.L, p.B), (p.L, p.B + hook),
           maybe_radii={1: p.bowl * 0.6, 4: p.bowl * 0.6})
    p.line((p.L + 0.22 * p.W, p.M), (p.R, p.M))


@glyph('4', FIGURE)
def _4(p):
    # A diagonal from the top of the stem down to the bar.
    y = 0.36 * p.H
    x = p.R - 0.16 * p.W
    p.line((x, p.B), (x, p.T), (p.L - 0.2 * p.w, y), (p.R, y))


@glyph('5', FIGURE)
def _5(p):
    y = 0.58 * p.H  # the bar sits above the middle
    p.path((p.R, p.T), (p.L, p.T), (p.L, y), (p.R, y), (p.R, p.B), (p.L, p.B), maybe_r=0,
           maybe_radii={3: p.bowl, 4: p.bowl})


@glyph('6', FIGURE)
def _6(p):
    p.path((p.R, p.T), (p.L, p.T), (p.L, p.B), (p.R, p.B), (p.R, p.M), (p.L, p.M), maybe_radii={4: 0})


@glyph('7', FIGURE)
def _7(p):
    p.line((p.L, p.T - SHORT_HOOK * p.H), (p.L, p.T), (p.R, p.T), (p.C - 0.12 * p.W, -p.w))


@glyph('8', FIGURE)
def _8(p):
    p.path((p.L, p.B), (p.L, p.T), (p.R, p.T), (p.R, p.B), closed=True)
    p.line((p.L, p.M), (p.R, p.M))


@glyph('9', FIGURE)
def _9(p):
    tail = p.L + 0.35 * (p.R - p.L)  # a short tail along the bottom
    p.path((p.R, p.M), (p.L, p.M), (p.L, p.T), (p.R, p.T), (p.R, p.B), (tail, p.B), maybe_radii={0: 0})


# --- Punctuation and symbols --------------------------------------------------

TALL = (-0.16, 1.16)  # brackets, braces and bars reach past the caps
LOW = (-0.22, 1.0)    # comma, semicolon and underscore dip below the baseline


@glyph('!', stem_width())
def _excl(p):
    p.line((p.C, p.T), (p.C, 0.32 * p.H))
    p.dot(p.C, p.w / 2)


@glyph('"', stem_width(3.0))
def _quote(p):
    p.line((p.L, p.T), (p.L, 0.70 * p.H))
    p.line((p.R, p.T), (p.R, 0.70 * p.H))


@glyph("'", stem_width())
def _apos(p):
    p.line((p.C, p.T), (p.C, 0.70 * p.H))


@glyph('#', 0.92)
def _hash(p):
    lean = 0.09 * p.W
    for x in (0.34 * p.W, 0.66 * p.W):
        p.line((x - lean, -p.w), (x + lean, p.H + p.w), ends='butt')
    for y in (0.34 * p.H, 0.66 * p.H):
        p.line((p.L, y), (p.R, y))


@glyph('$', 0.88, maybe_band=(-0.12, 1.12))
def _dollar(p):
    # The S sits closer to its middle bar than a letter S does.
    top, bottom = 0.86 * p.H - p.w / 2, 0.14 * p.H + p.w / 2
    p.path((p.R, top), (p.L, top), (p.L, p.M), (p.R, p.M), (p.R, bottom), (p.L, bottom))
    p.line((p.C, -0.12 * p.H), (p.C, 1.12 * p.H), ends='butt')


@glyph('%', 0.95)
def _percent(p):
    s = 0.30 * p.W
    r = p.bowl * 0.5
    p.path((p.L, p.T - s), (p.L, p.T), (p.L + s, p.T), (p.L + s, p.T - s), maybe_r=r, closed=True)
    p.path((p.R - s, p.B), (p.R - s, p.B + s), (p.R, p.B + s), (p.R, p.B), maybe_r=r, closed=True)
    p.line((p.R + 0.2 * p.w, p.H + p.w), (p.L - 0.2 * p.w, -p.w), ends='butt')


@glyph('&', 0.95)
def _amp(p):
    # A small loop over a larger bowl whose bottom curves up and out through
    # the glyph to the right, and a leg from the loop down to the right.
    xt = p.C + 0.10 * p.W
    p.path((p.L + 0.12 * p.W, p.M), (p.L + 0.12 * p.W, p.T), (xt, p.T), (xt, p.M), maybe_r=p.bowl * 0.6, closed=True)
    p.path((p.L + 0.12 * p.W, p.M), (p.L, p.M), (p.L, p.B), (p.C - 0.05 * p.W, p.B), (p.R + 0.3 * p.w, 0.66 * p.H),
           maybe_radii={1: p.bowl * 0.6, 2: p.bowl, 3: p.bowl * 1.6})
    p.line((xt - 0.3 * p.w, p.M + 0.3 * p.w), (p.R + 0.3 * p.w, -p.w), ends='butt')


@glyph('(', 0.42, maybe_band=TALL)
def _lparen(p):
    top, bottom = 1.16 * p.H - p.w / 2, -0.16 * p.H + p.w / 2
    p.path((p.R, top), (p.L, top), (p.L, bottom), (p.R, bottom), maybe_r=p.bowl * 1.3)


mirrored(')', '(')


@glyph('[', 0.42, maybe_band=TALL)
def _lbracket(p):
    top, bottom = 1.16 * p.H - p.w / 2, -0.16 * p.H + p.w / 2
    p.line((p.R, top), (p.L, top), (p.L, bottom), (p.R, bottom))


mirrored(']', '[')


@glyph('{', 0.52, maybe_band=TALL)
def _lbrace(p):
    top, bottom = 1.16 * p.H - p.w / 2, -0.16 * p.H + p.w / 2
    x = p.C + 0.08 * p.W
    p.path((p.R, top), (x, top), (x, p.M), (p.L, p.M), maybe_r=0, maybe_radii={1: p.bowl * 0.8})
    p.path((p.L, p.M), (x, p.M), (x, bottom), (p.R, bottom), maybe_r=0, maybe_radii={2: p.bowl * 0.8})


mirrored('}', '{')


@glyph('*', 0.62)
def _star(p):
    cy, arm = 0.74 * p.H, 0.22 * p.H
    p.line((p.C, cy + arm), (p.C, cy - arm), ends='butt')
    for dx, dy in ((0.866, 0.5), (0.866, -0.5)):
        p.line((p.C - dx * arm, cy - dy * arm), (p.C + dx * arm, cy + dy * arm), ends='butt')


@glyph('+', 0.76)
def _plus(p):
    p.line((p.L, p.M), (p.R, p.M))
    half = (p.R - p.L) / 2
    p.line((p.C, p.M - half), (p.C, p.M + half))


@glyph(',', stem_width(), maybe_band=LOW)
def _comma(p):
    p.line((p.C, p.w), (p.C, -0.16 * p.H))


@glyph('-', 0.60)
def _hyphen(p):
    p.line((p.L, p.M), (p.R, p.M))


@glyph('.', stem_width())
def _period(p):
    p.dot(p.C, p.w / 2)


@glyph('/', 0.62)
def _slash(p):
    p.line((p.L - 0.2 * p.w, -p.w), (p.R + 0.2 * p.w, p.H + p.w), ends='butt')


mirrored('\\', '/')


@glyph(':', stem_width())
def _colon(p):
    p.dot(p.C, p.w / 2)
    p.dot(p.C, 0.56 * p.H)


@glyph(';', stem_width(), maybe_band=LOW)
def _semicolon(p):
    p.line((p.C, p.w), (p.C, -0.16 * p.H))
    p.dot(p.C, 0.56 * p.H)


@glyph('<', 0.70)
def _less(p):
    p.line((p.R, p.M + 0.32 * p.H), (p.L + 0.10 * p.w, p.M), (p.R, p.M - 0.32 * p.H))


mirrored('>', '<')


@glyph('=', 0.70)
def _equals(p):
    for y in (p.M - 0.17 * p.H, p.M + 0.17 * p.H):
        p.line((p.L, y), (p.R, y))


@glyph('?', 0.82)
def _question(p):
    y = 0.56 * p.H
    p.path((p.L, p.T - HOOK * p.H), (p.L, p.T), (p.R, p.T), (p.R, y), (p.C, y), (p.C, 0.32 * p.H),
           maybe_radii={1: p.bowl * 0.6, 4: 0})
    p.dot(p.C, p.w / 2)


@glyph('@', 1.0)
def _at(p):
    # An inner box joined to a frame that closes along the bottom.
    y0, y1, x0 = 0.30 * p.H, 0.68 * p.H, p.C - 0.10 * p.W
    p.path((x0, y1), (p.R, y1), (p.R, y0), (x0, y0), maybe_r=p.bowl * 0.5, closed=True)
    p.path((p.R, y0), (p.R, p.T), (p.L, p.T), (p.L, p.B), (p.R, p.B), maybe_radii={1: p.bowl, 2: p.bowl, 3: p.bowl})


@glyph('^', 0.70)
def _caret(p):
    p.line((p.L, 0.50 * p.H), (p.C, p.T + 0.15 * p.w), (p.R, 0.50 * p.H))


@glyph('_', 0.70, maybe_band=LOW)
def _underscore(p):
    y = -0.22 * p.H + p.w / 2
    p.line((p.L, y), (p.R, y))


@glyph('`', 0.42)
def _grave(p):
    p.line((p.L - 0.2 * p.w, p.H + 0.2 * p.w), (p.R, 0.74 * p.H), ends='butt')


@glyph('|', stem_width(), maybe_band=TALL)
def _bar(p):
    p.line((p.C, -0.16 * p.H), (p.C, 1.16 * p.H), ends='butt')


@glyph('~', 0.82)
def _tilde(p):
    lo, hi = p.M - 0.09 * p.H, p.M + 0.09 * p.H
    third = (p.R - p.L) / 3
    p.line((p.L, lo), (p.L + third, hi), (p.L + 2 * third, lo), (p.R, hi))


PRINTABLE = [chr(c) for c in range(0x21, 0x7F)]
LOWERCASE = 'abcdefghijklmnopqrstuvwxyz'
