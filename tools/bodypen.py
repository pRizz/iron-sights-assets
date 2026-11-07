"""A drawing context for the body font's glyphs (see tools/brush.py).

A glyph function receives a Pen for one glyph and draws in font units, with
x from 0 at the ink's left edge to W at its right and y up from the baseline.
Named heights and weights keep the definitions readable:

    H, X       cap height and x-height
    A, D       ascender top and descender bottom of lowercase letters
    o          overshoot of round shapes past those heights
    T, t       the case's thick (stem) and thin (bar) weights
    W          the glyph's ink width

Operations act on what has been drawn so far, in order: draw a ring, cut its
aperture, then add a bar. Polygons are Clipper's (tools/geometry.py).
"""
from typing import NamedTuple

from tools import brush, geometry
from tools.brush import Node

N = Node
HUGE = 10_000


class Spec(NamedTuple):
    width: object  # font units before condensing, or a function of the Pen
    sb: tuple      # left and right sidebearings; left None centres the ink
    case: str      # 'upper' or 'lower': which weights it uses
    draw: object
    maybe_advance: float | None = None  # a fixed advance (the figures)


class Registry(dict):
    """char -> Spec, filled by the @glyph decorator."""

    def glyph(self, chars, width, sb=(60, 60), case='upper', maybe_advance=None):
        def register(draw):
            for ch in chars:
                self[ch] = Spec(width, sb, case, draw, maybe_advance)
            return draw
        return register


class Pen:
    def __init__(self, params, case, maybe_width=None):
        weights = params[case]
        # Glyphs are drawn wide and condensed afterwards (see condense()), so
        # vertical weights are drawn heavier by the same factor.
        self.condensing = params['condense']
        self.H = params['capHeight']
        self.X = params['xHeight']
        self.A = params['glyphAscender']
        self.D = params['glyphDescender']
        self.o = params['overshoot']
        self.T = weights['thick'] / self.condensing
        self.t = weights['thin']
        self.tension = params['tension']
        self.W = maybe_width or 0
        self.polygons = []

    # --- Drawing -----------------------------------------------------------

    def stroke(self, *nodes, closed=False, cut0=None, cut1=None, k=1.0):
        """A brush stroke through nodes; k scales both weights."""
        self.polygons += brush.stroke(nodes, self.T * k, self.t * k, self.tension, closed, cut0, cut1)

    def rect(self, x0, y0, x1, y1):
        self.polygons.append(geometry.box(x0, y0, x1, y1))

    def poly(self, *points):
        """A polygon, in either winding."""
        points = list(points) if brush._area(points) >= 0 else list(points)[::-1]
        self.polygons.append(geometry._to_clipper(points))

    def stem(self, x0, y0, y1, k=1.0):
        """A vertical stem of the thick weight with its left edge at x0."""
        self.rect(x0, y0, x0 + self.T * k, y1)

    def bar(self, x0, x1, y0, k=1.0):
        """A horizontal bar of the thin weight with its bottom at y0."""
        self.rect(x0, y0, x1, y0 + self.t * k)

    def ring(self, x0, y0, x1, y1, k=1.0, maybe_tension=None):
        """A closed bowl whose outer edge touches the box's four sides."""
        tk, sk = self.T * k / 2, self.t * k / 2
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        ten = maybe_tension or self.tension
        self.polygons += brush.stroke([
            N(cx, y0 + sk, 0), N(x1 - tk, cy, 90), N(cx, y1 - sk, 180), N(x0 + tk, cy, 270),
        ], self.T * k, self.t * k, ten, closed=True)

    def diag(self, p0, p1, k=1.0, reach0=400, reach1=400):
        """A straight stroke through two points, run on past them by reach0
        and reach1 so a later clip can cut its ends."""
        (x0, y0), (x1, y1) = p0, p1
        length = brush._length(x1 - x0, y1 - y0)
        ux, uy = (x1 - x0) / length, (y1 - y0) / length
        a = (x0 - ux * reach0, y0 - uy * reach0)
        b = (x1 + ux * reach1, y1 + uy * reach1)
        self.polygons += brush.stroke([N(*a), N(*b)], self.T * k, self.t * k, self.tension)

    def slant_half(self, p0, p1, k=1.0):
        """Half the horizontal width of a straight stroke from p0 to p1, so its
        edge can be placed on a corner."""
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]
        sin2 = dy * dy / (dx * dx + dy * dy)
        return (self.t + (self.T - self.t) * sin2) * k / 2 / sin2 ** 0.5

    def corner_diag(self, top_right, bottom_left, k=1.0):
        """A diagonal whose right edge passes through top_right and whose left
        edge passes through bottom_left (Z, z and 7 meeting their bars)."""
        (x1, y1), (x0, y0) = top_right, bottom_left
        hw = self.slant_half((x0, y0), (x1, y1), k)
        for _ in range(3):  # the half width depends on the slope it sets
            hw = self.slant_half((x0 + hw, y0), (x1 - hw, y1), k)
        self.diag((x1 - hw, y1), (x0 + hw, y0), k)

    def lobe(self, x_right, y0, y1, roundness=0.9, k=1.0):
        """A D-shaped bowl from a stem at x 0..T out to x_right, between the
        outer heights y0 and y1 (B, D, P and R)."""
        top, bottom = y1 - self.t * k / 2, y0 + self.t * k / 2
        right = x_right - self.T * k / 2
        r = (top - bottom) / 2
        xa = max(self.T, right - r * roundness)
        self.stroke(N(self.T / 2, top, 0), N(xa, top, 0), N(right, (top + bottom) / 2, 270),
                    N(xa, bottom, 180), N(self.T / 2, bottom, 180), k=k)

    def s_curve(self, height, spine=1.1):
        """The S stroke from its upper terminal to its lower one, filling the
        ink width between the baseline and height."""
        W, T, t, o = self.W, self.T, self.t, self.o
        self.stroke(N(W - T / 2 - 6, 0.70 * height, 100), N(0.50 * W, height + o - t / 2, 180),
                    N(T / 2, 0.745 * height, 270), N(0.50 * W, 0.505 * height, 335, k=spine),
                    N(W - T / 2, 0.245 * height, 270), N(0.48 * W, t / 2 - o, 180),
                    N(T / 2 + 4, 0.27 * height, 100), cut0=0, cut1=0)

    def dot(self, x0, y0, maybe_size=None):
        """A square dot with its lower-left corner at (x0, y0)."""
        s = maybe_size or self.T
        self.rect(x0, y0, x0 + s, y0 + s)

    # --- Editing what is drawn --------------------------------------------

    def _merged(self):
        return geometry.union(self.polygons)

    def cut(self, x0, y0, x1, y1):
        """Remove a box from everything drawn so far."""
        self.polygons = geometry.subtract(self._merged(), [geometry.box(x0, y0, x1, y1)])

    def cut_poly(self, *points):
        self.polygons = geometry.subtract(self._merged(), [geometry._to_clipper(points)])

    def clip(self, x0=-HUGE, y0=-HUGE, x1=HUGE, y1=HUGE):
        """Keep only what lies inside a box."""
        self.polygons = geometry.intersect(self._merged(), [geometry.box(x0, y0, x1, y1)])

    def _map(self, f, reflects, keep=False):
        """Move every point by f; a reflection also reverses each polygon so
        its winding (and so what later unions treat as inside) is kept."""
        merged = self._merged()
        moved = [[f(x, y) for x, y in poly] for poly in merged]
        self.polygons = ([poly[::-1] for poly in moved] if reflects else moved) + (merged if keep else [])

    def mirror(self, keep=False):
        """Flip everything drawn so far left to right within the ink width;
        keep=True also keeps the original (a symmetric pair)."""
        w = round(self.W * geometry.SCALE)
        self._map(lambda x, y: (w - x, y), reflects=True, keep=keep)

    def flip(self, y_mid, keep=False):
        """Flip everything drawn so far top to bottom about y_mid."""
        m = round(2 * y_mid * geometry.SCALE)
        self._map(lambda x, y: (x, m - y), reflects=True, keep=keep)

    def rotate(self, y_mid):
        """Turn everything drawn so far half a turn about the ink box's
        centre at height y_mid (n into u)."""
        w = round(self.W * geometry.SCALE)
        m = round(2 * y_mid * geometry.SCALE)
        self._map(lambda x, y: (w - x, m - y), reflects=False)

    def condense(self):
        """Narrow everything drawn by the font's condense factor; stems come
        back to their thick weight, horizontal bars keep theirs."""
        f = self.condensing
        self._map(lambda x, y: (round(x * f), y), reflects=False)

    def outline(self):
        return self._merged()
