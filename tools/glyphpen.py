"""A drawing context for parametric stroked glyphs.

A glyph function receives a Pen sized for one glyph and adds centerline paths
to it. Named positions keep the definitions readable:

    L, R   left and right stem centerlines (half a weight inside the box)
    B, T   bottom and top bar centerlines
    C, M   horizontal and vertical middles of the box
    H, W   box height and width; w is the stroke weight
"""
from tools import geometry


class Pen:
    def __init__(self, height, width, weight, bowl, band=None, mirror=False):
        self.mirror = mirror  # draw x as W - x: one definition makes ( and )
        self.H = height
        self.W = width
        self.w = weight
        self.bowl = bowl  # centerline radius of rounded corners
        self.L = weight / 2
        self.R = width - weight / 2
        self.B = weight / 2
        self.T = height - weight / 2
        self.C = width / 2
        self.M = height / 2
        self.band = band if band is not None else (0, height)
        self.polygons = []

    def path(self, *points, r=None, radii=None, closed=False, ends='square'):
        """A stroked path; corners round by r (default: the bowl radius) or by
        radii {corner index: radius}. r=0 keeps every corner square."""
        radius = self.bowl if r is None else r
        line = geometry.rounded_path([self._x(p) for p in points], radius, radii, closed)
        self.polygons += geometry.stroke(line, self.w, closed, ends)

    def line(self, *points, ends='square'):
        """A stroked path with square (mitered) corners."""
        self.path(*points, r=0, ends=ends)

    def dot(self, x, y, size=None):
        """A square dot centered on (x, y), one weight across by default."""
        s = (size or self.w) / 2
        x = self._x((x, y))[0]
        self.polygons.append(geometry.box(x - s, y - s, x + s, y + s))

    def _x(self, point):
        x, y = point
        return (self.W - x, y) if self.mirror else (x, y)

    def outline(self, convex=0.0, concave=0.0):
        """The finished outline as Clipper polygons: unioned, clipped to the
        glyph box (its width by the vertical band), then softened."""
        merged = geometry.union(self.polygons)
        lo, hi = self.band
        clipped = geometry.intersect(merged, [geometry.box(0, lo, self.W, hi)])
        return geometry.soften(clipped, convex, concave)
