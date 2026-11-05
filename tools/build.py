"""Build a parametric font: outlines, TTF, MTSDF atlas, metrics and specimen.

    python -m tools.build            build every font into dist/
    python -m tools.build --out DIR  build into DIR instead (used by the checks)

Builds are deterministic: the same sources and pinned tools give the same
outlines, font file, metrics and atlas pixels.
"""
import argparse
import importlib.util
import json
import math
from pathlib import Path

import numpy as np
from fontTools.agl import UV2AGL
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from PIL import Image

from tools import geometry, msdf
from tools.glyphpen import Pen

ROOT = Path(__file__).resolve().parent.parent
FONTS = ['title']
COPYRIGHT = 'Copyright (c) 2026 Peter Ryszkiewicz and Iron Sights assets contributors'
LICENSE_URL = 'https://github.com/pRizz/iron-sights-assets/blob/main/LICENSE'
# Fixed head timestamps (seconds since 1904-01-01) keep the TTF reproducible.
TIMESTAMP = 3_844_000_000
SPECIMEN = [
    'ABCDEFGHIJKLM',
    'NOPQRSTUVWXYZ',
    'abcdefghijklm',
    'nopqrstuvwxyz',
    '0123456789 +-=*/%#&@',
    '!"\'()[]{}<>?.,:;_^`~|\\$',
    'OBJECTIVE A: COMPLETE',
    'Time 00:42.17  Ammo 07/21',
]


def load_definitions(name):
    path = ROOT / 'fonts' / name / 'glyphs.py'
    spec = importlib.util.spec_from_file_location(f'fonts_{name}_glyphs', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    params = json.loads((ROOT / 'fonts' / name / 'params.json').read_text(encoding='utf-8'))
    return module, params


def draw_glyph(defs, params, ch):
    """(contours, advance) for one character, in font units."""
    small = ch in defs.LOWERCASE
    width_spec, band, mirror, draw = defs.GLYPHS[ch.upper() if small else ch]
    height = params['smallcapHeight'] if small else params['capHeight']
    weight = params['smallcapWeight'] if small else params['weight']
    width = width_spec(height, weight) if callable(width_spec) else width_spec * height
    lo, hi = (band[0] * height, band[1] * height) if band else (0, height)
    pen = Pen(height, width, weight, params['bowl'] * weight, (lo, hi), mirror)
    draw(pen)
    polygons = pen.outline(convex=params['softenConvex'])
    sb = params['sidebearing']
    contours = [[(x + sb, y) for x, y in c] for c in geometry.finish(polygons)]
    return contours, round(width + 2 * sb)


def build_outlines(defs, params):
    glyphs = {}
    for ch in defs.PRINTABLE:
        glyphs[ch] = draw_glyph(defs, params, ch)
    return glyphs


def glyph_name(ch):
    return UV2AGL.get(ord(ch), f'uni{ord(ch):04X}')


def bounds(contours):
    xs = [x for c in contours for x, _ in c]
    ys = [y for c in contours for _, y in c]
    return (min(xs), min(ys), max(xs), max(ys))


def write_ttf(params, glyphs, path):
    upm = params['unitsPerEm']
    order = ['.notdef', 'space'] + [glyph_name(ch) for ch in glyphs]
    fb = FontBuilder(upm, isTTF=True)
    fb.setupGlyphOrder(order)
    cmap = {0x20: 'space'}
    cmap.update({ord(ch): glyph_name(ch) for ch in glyphs})
    fb.setupCharacterMap(cmap)

    def tt_glyph(contours):
        pen = TTGlyphPen(None)
        for contour in contours:
            pts = list(reversed(contour))  # TrueType outers run clockwise
            pen.moveTo(pts[0])
            for p in pts[1:]:
                pen.lineTo(p)
            pen.closePath()
        return pen.glyph()

    cap = params['capHeight']
    notdef = [[(50, 0), (50, cap), (450, cap), (450, 0)][::-1], [(100, 50), (400, 50), (400, cap - 50), (100, cap - 50)][::-1]]
    tables = {'.notdef': tt_glyph([notdef[0][::-1], notdef[1][::-1]]), 'space': tt_glyph([])}
    metrics = {'.notdef': (500, 50), 'space': (params['space'], 0)}
    for ch, (contours, advance) in glyphs.items():
        name = glyph_name(ch)
        tables[name] = tt_glyph(contours)
        metrics[name] = (advance, bounds(contours)[0] if contours else 0)
    fb.setupGlyf(tables)
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=params['ascender'], descent=params['descender'])
    fb.setupNameTable({
        'familyName': params['family'],
        'styleName': 'Regular',
        'uniqueFontIdentifier': f"{params['postscriptName']};{params['version']}",
        'fullName': f"{params['family']} Regular",
        'psName': params['postscriptName'],
        'version': f"Version {params['version']}",
        'copyright': COPYRIGHT,
        'licenseDescription': 'MIT License',
        'licenseInfoURL': LICENSE_URL,
    })
    fb.setupOS2(sTypoAscender=params['ascender'], sTypoDescender=params['descender'], sTypoLineGap=0,
                usWinAscent=params['ascender'], usWinDescent=-params['descender'],
                sCapHeight=cap, sxHeight=params['smallcapHeight'], fsType=0, achVendID='NONE')
    fb.setupPost()
    fb.font['head'].created = TIMESTAMP
    fb.font['head'].modified = TIMESTAMP
    fb.font.recalcTimestamp = False
    fb.font.save(str(path))


def build_atlas(params, glyphs):
    """The MTSDF atlas image and each glyph's cell, as metrics entries."""
    atlas = params['atlas']
    scale = atlas['pxPerEm'] / params['unitsPerEm']
    pad = math.ceil(atlas['pxRange'] / 2) + 1
    boxes = {ch: bounds(c) for ch, (c, _) in glyphs.items() if c}
    cell_w = max(math.ceil((b[2] - b[0]) * scale) for b in boxes.values()) + 2 * pad + 1
    cell_h = max(math.ceil((b[3] - b[1]) * scale) for b in boxes.values()) + 2 * pad + 1
    columns = atlas['columns']
    rows = math.ceil(len(glyphs) / columns)
    image = np.zeros((rows * cell_h, columns * cell_w, 4), dtype=np.uint8)
    entries = {}
    for i, (ch, (contours, advance)) in enumerate(glyphs.items()):
        b = bounds(contours)
        # Snap the cell's lower-left to whole atlas pixels below the ink.
        ox = (math.floor(b[0] * scale) - pad) / scale
        oy = (math.floor(b[1] * scale) - pad) / scale
        cell = msdf.generate(contours, cell_w, cell_h, (ox, oy), scale, atlas['pxRange'])
        col, row = i % columns, i // columns
        image[row * cell_h:(row + 1) * cell_h, col * cell_w:(col + 1) * cell_w] = cell
        entries[ch] = {
            'codepoint': ord(ch),
            'advance': advance,
            'bounds': list(b),
            'atlas': [col * cell_w, row * cell_h, cell_w, cell_h],
            'plane': [round(ox, 4), round(oy, 4), round(ox + cell_w / scale, 4), round(oy + cell_h / scale, 4)],
        }
    return image, entries


def write_metrics(params, entries, image, path):
    atlas = params['atlas']
    doc = {
        'family': params['family'],
        'version': params['version'],
        'license': 'MIT',
        'unitsPerEm': params['unitsPerEm'],
        'capHeight': params['capHeight'],
        'smallcapHeight': params['smallcapHeight'],
        'ascender': params['ascender'],
        'descender': params['descender'],
        'space': params['space'],
        'atlas': {
            'type': 'mtsdf',
            'file': 'atlas.png',
            'width': int(image.shape[1]),
            'height': int(image.shape[0]),
            'pxPerEm': atlas['pxPerEm'],
            'pxRange': atlas['pxRange'],
            'yOrigin': 'top',
        },
        'glyphs': {ch: e for ch, e in entries.items()},
    }
    path.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + '\n', encoding='utf-8', newline='\n')


def render_text(image, entries, params, lines, cap_px, margin=24):
    """Text drawn from the MTSDF atlas, as a shader would: bilinear samples,
    median of three, coverage over one screen pixel."""
    atlas = params['atlas']
    units_px = cap_px / params['capHeight']
    line_h = math.ceil((params['ascender'] - params['descender']) * units_px)
    widths = []
    for text in lines:
        widths.append(sum((entries[ch]['advance'] if ch in entries else params['space']) for ch in text) * units_px)
    out_w = int(math.ceil(max(widths))) + 2 * margin
    out_h = line_h * len(lines) + 2 * margin
    canvas = np.ones((out_h, out_w), dtype=np.float64)
    field = image.astype(np.float64) / 255.0
    atlas_scale = atlas['pxPerEm'] / params['unitsPerEm']
    for li, text in enumerate(lines):
        pen_x = float(margin)
        base_y = margin + li * line_h + params['ascender'] * units_px
        for ch in text:
            if ch not in entries:
                pen_x += params['space'] * units_px
                continue
            e = entries[ch]
            ax, ay, aw, ah = e['atlas']
            pl, pb, pr, pt = e['plane']
            x0, x1 = pen_x + pl * units_px, pen_x + pr * units_px
            y0, y1 = base_y - pt * units_px, base_y - pb * units_px
            ix0, ix1 = max(0, int(math.floor(x0))), min(out_w, int(math.ceil(x1)))
            iy0, iy1 = max(0, int(math.floor(y0))), min(out_h, int(math.ceil(y1)))
            gy, gx = np.mgrid[iy0:iy1, ix0:ix1]
            u = (gx + 0.5 - x0) / (x1 - x0) * aw - 0.5 + ax
            v = (gy + 0.5 - y0) / (y1 - y0) * ah - 0.5 + ay
            u = np.clip(u, ax, ax + aw - 1)
            v = np.clip(v, ay, ay + ah - 1)
            u0, v0 = np.floor(u).astype(int), np.floor(v).astype(int)
            u1, v1 = np.minimum(u0 + 1, ax + aw - 1), np.minimum(v0 + 1, ay + ah - 1)
            fu, fv = (u - u0)[..., None], (v - v0)[..., None]
            sample = (field[v0, u0] * (1 - fu) * (1 - fv) + field[v0, u1] * fu * (1 - fv)
                      + field[v1, u0] * (1 - fu) * fv + field[v1, u1] * fu * fv)
            r, g, b = sample[..., 0], sample[..., 1], sample[..., 2]
            med = np.maximum(np.minimum(r, g), np.minimum(np.maximum(r, g), b))
            screen_range = atlas['pxRange'] * units_px / atlas_scale
            cover = np.clip((med - 0.5) * screen_range + 0.5, 0.0, 1.0)
            region = canvas[iy0:iy1, ix0:ix1]
            canvas[iy0:iy1, ix0:ix1] = np.minimum(region, 1.0 - cover)
            pen_x += e['advance'] * units_px
    gray = np.floor(canvas * 255.0 + 0.5).astype(np.uint8)
    return gray


def build_font(name, out_dir):
    defs, params = load_definitions(name)
    glyphs = build_outlines(defs, params)
    out_dir.mkdir(parents=True, exist_ok=True)
    write_ttf(params, glyphs, out_dir / f"{params['postscriptName']}.ttf")
    image, entries = build_atlas(params, glyphs)
    Image.fromarray(image, 'RGBA').save(out_dir / 'atlas.png', optimize=False, compress_level=9)
    write_metrics(params, entries, image, out_dir / 'metrics.json')
    Image.fromarray(render_text(image, entries, params, SPECIMEN, 56), 'L').save(
        out_dir / 'specimen.png', optimize=False, compress_level=9)
    return glyphs, image, entries


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--out', type=Path, default=ROOT / 'dist')
    args = parser.parse_args()
    for name in FONTS:
        build_font(name, args.out / name)
        print(f'built {name} -> {args.out / name}')


if __name__ == '__main__':
    main()
