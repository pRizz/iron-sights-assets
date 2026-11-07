"""Glyphs for the body font: a bold neo-grotesque sans for running text.

The drawings live in four parts (capitals, lowercase, figures, punctuation),
each a Registry of draw functions on a tools.bodypen.Pen. This module loads
them and builds one glyph's outline for tools/build.py.

Drawn from scratch for this project; see the repository's provenance rules.
"""
import importlib.util
from pathlib import Path

from tools import geometry
from tools.bodypen import Pen

PARTS = ('capitals', 'lowercase', 'figures', 'punctuation')
# How far (font units) an outline may stray from the drawn curve when points
# are dropped. Small, so curves keep facets of about 15 units rather than the
# 30 to 60 a coarser clean-up leaves, which show as corners in large text.
CURVE_TOLERANCE = 0.15
PRINTABLE = [chr(c) for c in range(0x21, 0x7F)]


def _load(part):
    path = Path(__file__).with_name(f'{part}.py')
    spec = importlib.util.spec_from_file_location(f'fonts_body_{part}', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.GLYPHS


GLYPHS = {}
for _part in PARTS:
    GLYPHS.update(_load(_part))


def draw_glyph(params, ch):
    """(contours, advance) for one character, in font units."""
    spec = GLYPHS[ch]
    pen = Pen(params, spec.case)
    pen.W = spec.width(pen) if callable(spec.width) else spec.width
    spec.draw(pen)
    pen.condense()
    ink = pen.W * params['condense']
    if spec.maybe_advance is None:
        left, advance = spec.sb[0], spec.sb[0] + ink + spec.sb[1]
    else:
        advance = spec.maybe_advance
        left = (advance - ink) / 2 if spec.sb[0] is None else spec.sb[0]
    smooth = geometry.simplify(pen.outline(), CURVE_TOLERANCE)
    contours = [[(x + round(left), y) for x, y in c] for c in geometry.finish(smooth, clean=0.01)]
    return contours, round(advance)
