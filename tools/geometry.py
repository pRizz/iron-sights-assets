"""Exact integer outline geometry for parametric glyphs.

Glyphs are drawn as centerline paths, stroked to a weight, unioned and
softened, all in Clipper's integer arithmetic so every build gives the same
points. Coordinates are font units with y up; Clipper works at SCALE times
that resolution and results are rounded back to whole font units.
"""
import math

import pyclipper

SCALE = 16
ARC_STEPS = 8  # segments per quarter circle on rounded path corners


def _to_clipper(points):
    return [(round(x * SCALE), round(y * SCALE)) for x, y in points]


def _from_clipper(path):
    return [(round(x / SCALE), round(y / SCALE)) for x, y in path]


def rounded_path(points, radius=0.0, radii=None, closed=False):
    """A polyline with each corner replaced by a circular arc.

    radius applies to every corner; radii maps a corner's index in points to
    its own radius. An arc never takes more than half of either neighbouring
    segment.
    """
    count = len(points)
    out = []
    for i, (x, y) in enumerate(points):
        is_end = not closed and (i == 0 or i == count - 1)
        r = 0.0 if is_end else (radii or {}).get(i, radius)
        if r <= 0:
            out.append((x, y))
            continue
        px, py = points[i - 1]
        nx, ny = points[(i + 1) % count]
        din = (x - px, y - py)
        dout = (nx - x, ny - y)
        lin = math.sqrt(din[0] * din[0] + din[1] * din[1])
        lout = math.sqrt(dout[0] * dout[0] + dout[1] * dout[1])
        if lin == 0 or lout == 0:
            out.append((x, y))
            continue
        uin = (din[0] / lin, din[1] / lin)
        uout = (dout[0] / lout, dout[1] / lout)
        turn = math.atan2(uin[0] * uout[1] - uin[1] * uout[0], uin[0] * uout[0] + uin[1] * uout[1])
        if abs(turn) < 1e-9:
            out.append((x, y))
            continue
        cut = r * math.tan(abs(turn) / 2)
        limit = min(lin, lout) / 2
        if cut > limit:
            r *= limit / cut
            cut = limit
        start = (x - uin[0] * cut, y - uin[1] * cut)
        side = 1.0 if turn > 0 else -1.0
        normal = (-uin[1] * side, uin[0] * side)
        center = (start[0] + normal[0] * r, start[1] + normal[1] * r)
        a0 = math.atan2(start[1] - center[1], start[0] - center[0])
        steps = max(1, round(ARC_STEPS * abs(turn) / (math.pi / 2)))
        for k in range(steps + 1):
            a = a0 + turn * k / steps
            out.append((center[0] + r * math.cos(a), center[1] + r * math.sin(a)))
    return out


def stroke(path, weight, closed=False, ends='square'):
    """Polygons covering a path stroked at weight, with mitered joins.

    ends is 'square' (extend half the weight past each end) or 'butt'.
    """
    offset = pyclipper.PyclipperOffset(miter_limit=8.0, arc_tolerance=0.25 * SCALE)
    if closed:
        end_type = pyclipper.ET_CLOSEDLINE
    elif ends == 'butt':
        end_type = pyclipper.ET_OPENBUTT
    else:
        end_type = pyclipper.ET_OPENSQUARE
    offset.AddPath(_to_clipper(path), pyclipper.JT_MITER, end_type)
    return offset.Execute(weight / 2 * SCALE)


def box(x0, y0, x1, y1):
    """A rectangle as a Clipper polygon."""
    return _to_clipper([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])


def union(polygons):
    if not polygons:
        return []
    clip = pyclipper.Pyclipper()
    clip.AddPaths(polygons, pyclipper.PT_SUBJECT, True)
    return clip.Execute(pyclipper.CT_UNION, pyclipper.PFT_NONZERO, pyclipper.PFT_NONZERO)


def intersect(polygons, clip_polygons):
    if not polygons:
        return []
    clip = pyclipper.Pyclipper()
    clip.AddPaths(polygons, pyclipper.PT_SUBJECT, True)
    clip.AddPaths(clip_polygons, pyclipper.PT_CLIP, True)
    return clip.Execute(pyclipper.CT_INTERSECTION, pyclipper.PFT_NONZERO, pyclipper.PFT_NONZERO)


def subtract(polygons, cut_polygons):
    if not polygons:
        return []
    clip = pyclipper.Pyclipper()
    clip.AddPaths(polygons, pyclipper.PT_SUBJECT, True)
    clip.AddPaths(cut_polygons, pyclipper.PT_CLIP, True)
    return clip.Execute(pyclipper.CT_DIFFERENCE, pyclipper.PFT_NONZERO, pyclipper.PFT_NONZERO)


def _offset_polygons(polygons, delta):
    offset = pyclipper.PyclipperOffset(miter_limit=8.0, arc_tolerance=0.25 * SCALE)
    offset.AddPaths(polygons, pyclipper.JT_ROUND, pyclipper.ET_CLOSEDPOLYGON)
    return offset.Execute(delta * SCALE)


def soften(polygons, convex=0.0, concave=0.0):
    """Round convex corners by convex and concave corners by concave (font units)."""
    if convex > 0:
        polygons = _offset_polygons(_offset_polygons(polygons, -convex), convex)
    if concave > 0:
        polygons = _offset_polygons(_offset_polygons(polygons, concave), -concave)
    return polygons


def finish(polygons):
    """Clipper polygons to clean font-unit contours: outers counter-clockwise,
    holes clockwise (y up), duplicate and collinear points removed, in a
    stable order."""
    contours = []
    for poly in polygons:
        pts = _from_clipper(poly)
        pts = pyclipper.CleanPolygon(pts, 0.5)
        deduped = []
        for p in pts:
            if not deduped or deduped[-1] != tuple(p):
                deduped.append(tuple(p))
        if len(deduped) > 1 and deduped[0] == deduped[-1]:
            deduped.pop()
        if len(deduped) < 3 or pyclipper.Area(deduped) == 0:
            continue
        contours.append(deduped)
    # Clipper keeps hole orientation opposite to outers; normalise by winding
    # relative to the union (outer area positive).
    result = []
    for c in contours:
        result.append(_canonical_start(c))
    result.sort(key=lambda c: (min(p[1] for p in c), min(p[0] for p in c), len(c)))
    return result


def _canonical_start(contour):
    """Rotate a contour to start at its lowest-then-leftmost point, so the
    point order is independent of Clipper's internal start choice."""
    i = min(range(len(contour)), key=lambda k: (contour[k][1], contour[k][0]))
    return contour[i:] + contour[:i]


def area(contour):
    return pyclipper.Area(contour)
