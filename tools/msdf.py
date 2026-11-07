"""Multi-channel signed distance fields for polygon outlines.

Follows the method of Viktor Chlumsky's msdfgen (MIT): contour edges are
coloured so that the two edges meeting at a sharp corner never share all
three channels, each channel stores the signed pseudo-distance to its nearest
edge, and the median of the three channels reconstructs sharp corners. The
alpha channel holds the true signed distance (an MTSDF), useful for outlines
and as a fallback.

Outlines are lists of contours of (x, y) points with straight edges, outers
counter-clockwise and holes clockwise (y up), so the inside is always to the
left of an edge. Distances are positive inside.
"""
import math

import numpy as np

RED, GREEN, BLUE = 1, 2, 4
CYAN, MAGENTA, YELLOW, WHITE = GREEN | BLUE, RED | BLUE, RED | GREEN, RED | GREEN | BLUE
CYCLE = (CYAN, MAGENTA, YELLOW)
# A turn sharper than this (radians) is a corner; arc facets are smaller.
CORNER_TURN = math.radians(25)
# Texels further than this (pixels) from the outline take the true distance in
# every channel (see generate()).
CORRECT_BEYOND = 1.5


def _edges(contour):
    pts = list(contour)
    return [(pts[i], pts[(i + 1) % len(pts)]) for i in range(len(pts))]


def _turn(e0, e1):
    (ax, ay), (bx, by) = e0
    (cx, cy), (dx, dy) = e1
    ux, uy = bx - ax, by - ay
    vx, vy = dx - cx, dy - cy
    return abs(math.atan2(ux * vy - uy * vx, ux * vx + uy * vy))


def colour_edges(contours):
    """Return [(p0, p1, colour)] for every edge of every contour."""
    out = []
    for contour in contours:
        edges = _edges(contour)
        n = len(edges)
        corners = [i for i in range(n) if _turn(edges[i - 1], edges[i]) > CORNER_TURN]
        if not corners:
            out += [(a, b, WHITE) for a, b in edges]
            continue
        if len(corners) == 1:
            # A single corner: split the loop into three runs from it.
            start = corners[0]
            for k in range(n):
                i = (start + k) % n
                out.append((*edges[i], CYCLE[min(2, k * 3 // n)]))
            continue
        runs = len(corners)
        colours = [CYCLE[k % 3] for k in range(runs)]
        if runs % 3 == 1:
            colours[-1] = CYCLE[1]  # differs from the run before it and the first
        for k, start in enumerate(corners):
            end = corners[(k + 1) % runs]
            i = start
            while True:
                out.append((*edges[i], colours[k]))
                i = (i + 1) % n
                if i == end:
                    break
    return out


def _winding(px, py, contours):
    """Nonzero winding number of each point."""
    wind = np.zeros(px.shape, dtype=np.int32)
    for contour in contours:
        for (ax, ay), (bx, by) in _edges(contour):
            up = (ay <= py) & (by > py)
            down = (ay > py) & (by <= py)
            side = (bx - ax) * (py - ay) - (px - ax) * (by - ay)
            wind += np.where(up & (side > 0), 1, 0)
            wind -= np.where(down & (side < 0), 1, 0)
    return wind


def generate(contours, width, height, origin, scale, px_range):
    """An MTSDF image (height, width, 4) of uint8 for the outline.

    origin is the font-unit point at the image's lower-left corner, scale the
    pixels per font unit and px_range the distance (in pixels) spanning the
    full 0..255 range. Row 0 is the image's top.
    """
    ys, xs = np.mgrid[0:height, 0:width]
    px = origin[0] + (xs + 0.5) / scale
    py = origin[1] + (height - ys - 0.5) / scale

    coloured = colour_edges(contours)
    best = {c: (np.full(px.shape, np.inf), np.full(px.shape, np.inf), np.zeros(px.shape)) for c in (RED, GREEN, BLUE)}
    true_d = np.full(px.shape, np.inf)
    for (ax, ay), (bx, by), colour in coloured:
        ex, ey = bx - ax, by - ay
        length = math.sqrt(ex * ex + ey * ey)
        if length == 0:
            continue
        dx, dy = ex / length, ey / length
        qx, qy = px - ax, py - ay
        t = (qx * dx + qy * dy) / length
        tc = np.clip(t, 0.0, 1.0)
        cx, cy = qx - tc * ex, qy - tc * ey
        dist = np.sqrt(cx * cx + cy * cy)
        side = np.where(dx * qy - dy * qx >= 0, 1.0, -1.0)
        # Ties at a shared endpoint go to the edge that points more across
        # the query direction (msdfgen's orthogonality rule).
        at_end = (t <= 0) | (t >= 1)
        safe = np.where(dist > 0, dist, 1.0)
        ortho = np.where(at_end, np.abs((cx * dx + cy * dy) / safe), 0.0)
        key = dist + 1e-7 * ortho
        # Pseudo-distance: past an end, the distance to the edge's extended
        # line when that is nearer.
        perp = dx * qy - dy * qx
        perp_end = dx * (py - by) - dy * (px - bx)
        signed = side * dist
        before = (t < 0) & (np.abs(perp) <= dist)
        after = (t > 1) & (np.abs(perp_end) <= dist)
        signed = np.where(before, perp, np.where(after, perp_end, signed))
        true_d = np.minimum(true_d, dist)
        for c in (RED, GREEN, BLUE):
            if colour & c:
                bkey, bdist, bsigned = best[c]
                take = key < bkey
                best[c] = (np.where(take, key, bkey), np.where(take, dist, bdist), np.where(take, signed, bsigned))

    inside = _winding(px, py, contours) != 0
    signed_true = np.where(inside, true_d, -true_d) * scale
    out = np.zeros((height, width, 4), dtype=np.uint8)
    for i, c in enumerate((RED, GREEN, BLUE)):
        # Error correction: only texels near an edge place it and keep its
        # corners sharp. Further away, extended edge lines in two channels
        # can agree on a false near-edge median (a pocket such as the foot of
        # an n's counter), which small text, drawn over a narrow coverage
        # range, shows as a faint dot; there the true distance is used.
        far = np.abs(signed_true) > CORRECT_BEYOND
        out[..., i] = _encode(np.where(far, signed_true, best[c][2] * scale), px_range)
    out[..., 3] = _encode(signed_true, px_range)
    return out


def _encode(distance_px, px_range):
    v = np.clip(distance_px / px_range + 0.5, 0.0, 1.0)
    return np.floor(v * 255.0 + 0.5).astype(np.uint8)


def median(image):
    """The reconstructed signed field (0..1, 0.5 at the edge) of an MSDF."""
    r, g, b = (image[..., i].astype(np.int32) for i in range(3))
    return (np.maximum(np.minimum(r, g), np.minimum(np.maximum(r, g), b)) / 255.0)
