"""Body font punctuation and symbols, in capital weights.

Drawn from scratch for this project; see the repository's provenance rules.
"""
from tools.bodypen import HUGE, N, Registry

GLYPHS = Registry()
glyph = GLYPHS.glyph

AXIS = 0.40  # maths symbols centre on this fraction of the cap height
DOT_SB = (70, 70)


def comma(p, y=0):
    """A square dot at y with a tail slanting down to the left."""
    T = p.T
    p.dot(0, y)
    p.poly((0.30 * T, y + 30), (T, y + 30), (0.55 * T, y - 160), (0.05 * T, y - 160))


def brace(p):
    """The upper half of {, flipped to make the lower half."""
    top, mid = p.H + 110, (p.H + 110 - 150) / 2
    p.stroke(N(p.W, top - 0.45 * p.t, 180), N(0.55 * p.W, top - 110, 270), N(0.55 * p.W, mid + 90, 270),
             N(0, mid, 200), k=0.9)
    p.flip(mid, keep=True)


@glyph('!', lambda p: p.T, sb=DOT_SB)
def _exclam(p):
    p.stroke(N(p.T / 2, p.H, 270), N(p.T / 2, 0.30 * p.H, 270, k=0.8))
    p.dot(0, 0)


@glyph('"', 158, sb=(50, 50))
def _quotedbl(p):
    w = 0.48 * p.T
    p.rect(0, p.H - 250, w, p.H)
    p.rect(p.W - w, p.H - 250, p.W, p.H)


@glyph('#', 560, sb=(20, 20))
def _numbersign(p):
    for x in (0.36, 0.72):
        p.diag((x * p.W, p.H), ((x - 0.08) * p.W, 0), k=0.72, reach0=0, reach1=0)
    p.clip(0, 0, p.W, p.H)
    for y in (0.27, 0.60):
        p.rect(0, y * p.H, p.W, y * p.H + 0.8 * p.t)


@glyph('$', 545, sb=(36, 36))
def _dollar(p):
    p.s_curve(p.H)
    w = 0.55 * p.T
    p.rect((p.W - w) / 2, -90, (p.W + w) / 2, p.H + 90)


@glyph('%', 760, sb=(30, 30))
def _percent(p):
    p.ring(0, 0.45 * p.H, 0.36 * p.W, p.H + p.o, k=0.8)
    p.ring(0.64 * p.W, -p.o, p.W, 0.55 * p.H - p.o, k=0.8)
    p.diag((0.80 * p.W, p.H), (0.20 * p.W, 0), k=0.8)
    p.clip(0, -p.o, p.W, p.H + p.o)


@glyph('&', 560, sb=(36, 20))
def _ampersand(p):
    p.ring(0.12 * p.W, 0.52 * p.H, 0.62 * p.W, p.H + p.o, k=0.85)
    p.diag((0.24 * p.W, 0.62 * p.H), (p.W - 40, 0), k=0.95, reach0=0)
    p.clip(-HUGE, 0, p.W, HUGE)
    p.stroke(N(0.40 * p.W, 0.58 * p.H, 225), N(p.T / 2, 0.24 * p.H, 270), N(0.40 * p.W, p.t / 2 - p.o, 0),
             N(0.82 * p.W, 0.40 * p.H, 60), cut1=0)


@glyph("'", lambda p: 0.85 * p.T, sb=(50, 50))
def _quotesingle(p):
    p.rect(0, p.H - 250, p.W, p.H)


@glyph('(', 230, sb=(50, 10))
def _parenleft(p):
    p.stroke(N(p.W, p.H + 130, 236), N(0.45 * p.T, 330, 270), N(p.W, -170, 304), k=0.9, cut0=0, cut1=0)
    p.clip(0, -HUGE, p.W, HUGE)


@glyph(')', 230, sb=(10, 50))
def _parenright(p):
    _parenleft(p)
    p.mirror()


@glyph('*', 380, sb=(30, 30))
def _asterisk(p):
    cx, cy, r = p.W / 2, p.H - 170, 170
    for dx, dy in ((0, 1), (0.866, 0.5), (0.866, -0.5)):
        p.diag((cx - dx * r, cy - dy * r), (cx + dx * r, cy + dy * r), k=0.7, reach0=0, reach1=0)


@glyph('+', 520, sb=(40, 40))
def _plus(p):
    cy, h = AXIS * p.H, 0.42 * p.T
    p.rect(0, cy - h, p.W, cy + h)
    p.rect(p.W / 2 - h, cy - p.W / 2, p.W / 2 + h, cy + p.W / 2)


@glyph(',', lambda p: p.T, sb=DOT_SB)
def _comma(p):
    comma(p)


@glyph('-', 300, sb=(40, 40))
def _hyphen(p):
    cy, h = AXIS * p.H, 0.42 * p.T
    p.rect(0, cy - h, p.W, cy + h)


@glyph('.', lambda p: p.T, sb=DOT_SB)
def _period(p):
    p.dot(0, 0)


@glyph('/', 350, sb=(10, 10))
def _slash(p):
    p.diag((0.15 * p.W, -110), (0.85 * p.W, p.H + 50), k=0.85)
    p.clip(0, -110, p.W, p.H + 50)


@glyph(':', lambda p: p.T, sb=DOT_SB)
def _colon(p):
    p.dot(0, 0)
    p.dot(0, p.X - p.T)


@glyph(';', lambda p: p.T, sb=DOT_SB)
def _semicolon(p):
    comma(p)
    p.dot(0, p.X - p.T)


@glyph('<', 500, sb=(50, 50))
def _less(p):
    cy = AXIS * p.H
    p.stroke(N(p.W, cy + 210), N(0, cy), N(p.W, cy - 210), k=0.85)
    p.clip(0, -HUGE, p.W, HUGE)


@glyph('=', 520, sb=(40, 40))
def _equal(p):
    cy, h = AXIS * p.H, 0.36 * p.T
    p.rect(0, cy + 45, p.W, cy + 45 + 2 * h)
    p.rect(0, cy - 45 - 2 * h, p.W, cy - 45)


@glyph('>', 500, sb=(50, 50))
def _greater(p):
    _less(p)
    p.mirror()


@glyph('?', 355, sb=(36, 40))
def _question(p):
    p.stroke(N(p.T / 2 + 4, 0.69 * p.H, 80), N(0.5 * p.W, p.H + p.o - p.t / 2, 0), N(p.W - p.T / 2, 0.72 * p.H, 270),
             N(0.5 * p.W + 20, 0.42 * p.H, 235), N(0.5 * p.W, 0.28 * p.H, 270), cut0=0)
    p.dot(0.5 * p.W - p.T / 2, 0)


@glyph('@', 820, sb=(40, 40))
def _at(p):
    k = 0.72
    stem = 0.64 * p.W
    p.ring(0, -0.18 * p.H, p.W, 1.02 * p.H, k=k)
    p.cut(0.60 * p.W, -HUGE, HUGE, 0.36 * p.H)
    p.ring(0.28 * p.W, 0.12 * p.H, stem, 0.70 * p.H, k=0.8)
    p.rect(stem - 0.8 * p.T, 0.12 * p.H, stem, 0.70 * p.H)
    p.stroke(N(stem - 0.4 * p.T, 0.26 * p.H, 270), N(stem + 70, 0.12 * p.H + 0.4 * p.t, 0),
             N(p.W - k * p.T / 2, 0.36 * p.H, 90), k=0.8)


@glyph('[', 230, sb=(70, 10))
def _bracketleft(p):
    top = p.H + 110
    p.stem(0, -150, top, k=0.95)
    p.bar(0, p.W, top - p.t)
    p.bar(0, p.W, -150)


@glyph('\\', 350, sb=(10, 10))
def _backslash(p):
    _slash(p)
    p.mirror()


@glyph(']', 230, sb=(10, 70))
def _bracketright(p):
    _bracketleft(p)
    p.mirror()


@glyph('^', 480, sb=(30, 30))
def _asciicircum(p):
    hw = 0.8 * p.T / 2
    p.diag((hw, 0.38 * p.H), (p.W / 2, p.H), k=0.8, reach0=0, reach1=60)
    p.mirror(keep=True)
    p.clip(y1=p.H)


@glyph('_', 520, sb=(0, 0))
def _underscore(p):
    p.bar(0, p.W, -150)


@glyph('`', 165, sb=(40, 40))
def _grave(p):
    p.diag((0, p.H + 30), (p.W, 0.80 * p.H), k=0.75, reach0=0, reach1=0)


@glyph('{', 260, sb=(50, 20))
def _braceleft(p):
    brace(p)


@glyph('|', lambda p: 0.8 * p.T, sb=(70, 70))
def _bar(p):
    p.rect(0, -200, p.W, p.H + 110)


@glyph('}', 260, sb=(20, 50))
def _braceright(p):
    brace(p)
    p.mirror()


@glyph('~', 520, sb=(40, 40))
def _asciitilde(p):
    cy = AXIS * p.H
    p.stroke(N(0, cy - 30, 32), N(0.30 * p.W, cy + 55, 0), N(0.70 * p.W, cy - 55, 0), N(p.W, cy + 30, 32),
             k=0.8, cut0=90, cut1=90)
