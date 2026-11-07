"""Variable-width strokes along smooth centerlines, for the drawn body font.

A stroke runs through nodes. Two neighbouring nodes that both give a
direction are joined by a cubic Bezier whose handles point along those
directions and reach `tension` of the way to where the two tangent lines
meet (0.55 draws a circle's quarter; more draws squarer curves). Nodes on one
line with the same direction give a straight run, and a node without a
direction makes a sharp, mitered corner.

The width follows the direction of travel, as a broad pen held for vertical
stress would: `thick` across vertical travel, `thin` across horizontal travel
and `thin + (thick - thin) * sin(angle)**2` between, times each node's scale
`k` (blended along a segment). The square keeps the width from growing faster
than a curve falls away from its extreme, so bowls do not bulge past their
heights. So stems come out heavier than bars and bowls
thin towards their tops and bottoms without drawing each contour by hand.

Ends are square to the stroke unless a cut angle is given: the stroke then
runs on past its end and is trimmed by a straight line through the end point
at that angle (0 for a horizontal cut), as grotesque terminals are.

Everything is returned as Clipper polygons (see tools/geometry.py), one quad
per sampled step plus corner wedges, ready to be unioned.
"""
import math
from typing import NamedTuple

from tools import geometry

SAMPLE_STEP = 8.0   # font units of control polygon per sample on curves
STRAIGHT_STEP = 40.0  # samples on straight runs whose width scale changes
MITER_LIMIT = 4.0   # corner wedges longer than this many widths are bevelled
CUT_REACH = 1.6     # the trimmed end region, in widths along the stroke
FAR = 5000.0        # half-plane size for cuts


class Node(NamedTuple):
    x: float
    y: float
    d: float | None = None  # direction of travel in degrees, or None for a corner
    k: float = 1.0          # width scale at this node
    t: float | None = None  # tension for the segments touching this node


def _unit(degrees):
    r = math.radians(degrees)
    return math.cos(r), math.sin(r)


def _length(x, y):
    return math.sqrt(x * x + y * y)


def _controls(n0, n1, tension):
    """The cubic's four control points from n0 to n1."""
    p0, p3 = (n0.x, n0.y), (n1.x, n1.y)
    dx, dy = p3[0] - p0[0], p3[1] - p0[1]
    chord = _length(dx, dy)
    u0 = _unit(n0.d) if n0.d is not None else None
    u1 = _unit(n1.d) if n1.d is not None else None
    l0 = l1 = chord / 3
    if u0 and u1:
        det = u0[0] * u1[1] - u1[0] * u0[1]
        if abs(det) > 1e-9:
            # p0 + s u0 meets p3 - r u1
            s = (dx * u1[1] - u1[0] * dy) / det
            r = (u0[0] * dy - dx * u0[1]) / det
            if s > 0 and r > 0:
                l0, l1 = tension * s, tension * r
    u0 = u0 or (dx / chord, dy / chord)
    u1 = u1 or (dx / chord, dy / chord)
    p1 = (p0[0] + u0[0] * l0, p0[1] + u0[1] * l0)
    p2 = (p3[0] - u1[0] * l1, p3[1] - u1[1] * l1)
    return p0, p1, p2, p3


def _is_line(n0, n1):
    if n0.d is None and n1.d is None:
        return True
    if n0.d is None or n1.d is None or n0.d != n1.d:
        return False
    ux, uy = _unit(n0.d)
    return abs((n1.x - n0.x) * uy - (n1.y - n0.y) * ux) < 1e-6


def _segment_samples(n0, n1, tension):
    """[(x, y, tx, ty, k)] along one segment, both ends included."""
    p0, p1, p2, p3 = _controls(n0, n1, tension)
    if _is_line(n0, n1):
        span = _length(p3[0] - p0[0], p3[1] - p0[1])
        steps = 1 if n0.k == n1.k else max(1, math.ceil(span / STRAIGHT_STEP))
    else:
        poly = (_length(p1[0] - p0[0], p1[1] - p0[1]) + _length(p2[0] - p1[0], p2[1] - p1[1])
                + _length(p3[0] - p2[0], p3[1] - p2[1]))
        steps = max(4, math.ceil(poly / SAMPLE_STEP))
    out = []
    for i in range(steps + 1):
        t = i / steps
        a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
        x = a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0]
        y = a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]
        tx = 3 * ((1 - t) ** 2 * (p1[0] - p0[0]) + 2 * (1 - t) * t * (p2[0] - p1[0]) + t * t * (p3[0] - p2[0]))
        ty = 3 * ((1 - t) ** 2 * (p1[1] - p0[1]) + 2 * (1 - t) * t * (p2[1] - p1[1]) + t * t * (p3[1] - p2[1]))
        if _length(tx, ty) < 1e-9:
            tx, ty = p3[0] - p0[0], p3[1] - p0[1]
        out.append((x, y, tx, ty, n0.k + (n1.k - n0.k) * t))
    return out


def _width(tx, ty, k, thick, thin):
    return (thin + (thick - thin) * ty * ty / (tx * tx + ty * ty)) * k


def _sides(sample, thick, thin):
    """The stroke's left and right edge points at a sample, and its width."""
    x, y, tx, ty, k = sample
    n = _length(tx, ty)
    w = _width(tx, ty, k, thick, thin)
    nx, ny = -ty / n * w / 2, tx / n * w / 2
    return (x + nx, y + ny), (x - nx, y - ny), w


def _quad(a, b, thick, thin):
    al, ar, _ = _sides(a, thick, thin)
    bl, br, _ = _sides(b, thick, thin)
    return [ar, br, bl, al]


def _area(points):
    return sum(points[i - 1][0] * points[i][1] - points[i][0] * points[i - 1][1] for i in range(len(points))) / 2


def _cells(points):
    """Split a quad (or pass a triangle) into counter-clockwise triangles.
    On the inside of a curve tighter than the stroke, a step's quad folds
    over itself; its two halves would otherwise wind in opposite directions
    and cancel coverage where they overlap their neighbours."""
    tris = [points] if len(points) == 3 else [points[:3], [points[0], points[2], points[3]]]
    return [t if _area(t) >= 0 else t[::-1] for t in tris]


def _line_cross(p, u, q, v):
    """Where p + s u meets q + r v, or None for parallel lines."""
    det = u[0] * v[1] - v[0] * u[1]
    if abs(det) < 1e-9:
        return None
    s = ((q[0] - p[0]) * v[1] - v[0] * (q[1] - p[1])) / det
    return (p[0] + u[0] * s, p[1] + u[1] * s)


def _wedges(before, after, thick, thin):
    """Mitered fill for a sharp corner between two samples at the same point."""
    out = []
    bl, br, wb = _sides(before, thick, thin)
    al, ar, _ = _sides(after, thick, thin)
    centre = (before[0], before[1])
    for p, q in ((bl, al), (br, ar)):
        tip = _line_cross(p, (before[2], before[3]), q, (after[2], after[3]))
        if tip is None or _length(tip[0] - centre[0], tip[1] - centre[1]) > MITER_LIMIT * wb:
            out.append([centre, p, q])
        else:
            out.append([centre, p, tip, q])
    return out


def _keep_side(point, tangent, angle):
    """A half-plane through point, bounded by a line at angle, on the side the
    tangent points into."""
    ax, ay = _unit(angle)
    nx, ny = -ay, ax
    if nx * tangent[0] + ny * tangent[1] < 0:
        nx, ny = -nx, -ny
    x, y = point
    return [(x + ax * FAR, y + ay * FAR), (x - ax * FAR, y - ay * FAR),
            (x - ax * FAR + nx * FAR, y - ay * FAR + ny * FAR), (x + ax * FAR + nx * FAR, y + ay * FAR + ny * FAR)]


def stroke(nodes, thick, thin, tension, closed=False, cut0=None, cut1=None):
    """Clipper polygons covering the stroke through nodes (see the module docs)."""
    nodes = list(nodes)
    pairs = list(zip(nodes, nodes[1:])) + ([(nodes[-1], nodes[0])] if closed else [])
    runs = []  # (samples, corner_after)
    for n0, n1 in pairs:
        tension_here = n0.t if n0.t is not None else (n1.t if n1.t is not None else tension)
        runs.append(_segment_samples(n0, n1, tension_here))
    quads, wedges = [], []
    distance = [0.0]
    samples = []
    for i, run in enumerate(runs):
        if samples:
            prev = samples[-1]
            corner = (prev[2] * run[0][3] - prev[3] * run[0][2]) ** 2 > 1e-6 * (
                _length(prev[2], prev[3]) * _length(run[0][2], run[0][3])) ** 2
            if corner:
                wedges += _wedges(prev, run[0], thick, thin)
        for j, s in enumerate(run):
            if samples and j == 0:
                quads.append((len(samples) - 1, len(samples), True))
            elif samples:
                quads.append((len(samples) - 1, len(samples), False))
            if samples:
                p = samples[-1]
                distance.append(distance[-1] + _length(s[0] - p[0], s[1] - p[1]))
            samples.append(s)
    if closed:
        first, last = samples[0], samples[-1]
        corner = (last[2] * first[3] - last[3] * first[2]) ** 2 > 1e-6 * (
            _length(last[2], last[3]) * _length(first[2], first[3])) ** 2
        if corner:
            wedges += _wedges(last, first, thick, thin)

    total = distance[-1]
    polys = {0: [], 1: [], 2: [], 3: []}  # bit 1: near a cut start, bit 2: near a cut end
    reach0 = CUT_REACH * _sides(samples[0], thick, thin)[2] if cut0 is not None else -1
    reach1 = CUT_REACH * _sides(samples[-1], thick, thin)[2] if cut1 is not None else -1
    for a, b, joint in quads:
        if joint and samples[a][:2] == samples[b][:2]:
            continue  # the shared point between two segments
        group = (1 if distance[b] <= reach0 else 0) | (2 if total - distance[a] <= reach1 else 0)
        polys[group] += _cells(_quad(samples[a], samples[b], thick, thin))
    polys[0] += [cell for wedge in wedges for cell in _cells(wedge)]
    for which, cut in ((0, cut0), (1, cut1)):
        if cut is None:
            continue
        s = samples[0] if which == 0 else samples[-1]
        n = _length(s[2], s[3])
        u = (s[2] / n, s[3] / n)
        sign = -1 if which == 0 else 1
        reach = 2 * _sides(s, thick, thin)[2]
        beyond = (s[0] + sign * u[0] * reach, s[1] + sign * u[1] * reach, s[2], s[3], s[4])
        piece = _quad(beyond, s, thick, thin) if which == 0 else _quad(s, beyond, thick, thin)
        polys[1 << which] += _cells(piece)

    out = [geometry._to_clipper(q) for q in polys[0]]
    for group in (1, 2, 3):
        if not polys[group]:
            continue
        merged = geometry.union([geometry._to_clipper(q) for q in polys[group]])
        for which, cut in ((0, cut0), (1, cut1)):
            if group & (1 << which):
                s = samples[0] if which == 0 else samples[-1]
                inward = (s[2], s[3]) if which == 0 else (-s[2], -s[3])
                merged = geometry.intersect(merged, [geometry._to_clipper(_keep_side((s[0], s[1]), inward, cut))])
        out += merged
    return out
