"""ROM-free checks for the body font.

    python -m unittest discover -s tests -t .
"""
import tempfile
import unittest
from pathlib import Path

import numpy as np
from fontTools.ttLib import TTFont

from tools import brush, build, check_dist, geometry, msdf
from tools.brush import Node as N


class BodyFont(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.defs, cls.params = build.load_definitions('body')
        cls.tmp = tempfile.TemporaryDirectory()
        cls.out = Path(cls.tmp.name) / 'body'
        cls.glyphs, cls.image, cls.entries = build.build_font('body', cls.out)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def _heights(self, ch):
        _, bottom, _, top = build.bounds(self.glyphs[ch][0])
        return bottom, top

    def test_covers_printable_ascii(self):
        self.assertEqual(sorted(self.glyphs), [chr(c) for c in range(0x21, 0x7F)])
        for ch, (contours, advance) in self.glyphs.items():
            self.assertTrue(contours, f'{ch!r} has no outline')
            self.assertGreater(advance, 0, ch)

    def test_letters_sit_on_their_heights(self):
        p = self.params
        o = p['overshoot']
        for ch in 'ABDEFHIKLMNPRTVWXYZ147':
            self.assertEqual(self._heights(ch), (0, p['capHeight']), ch)
        for ch in 'CGOS0235689':
            bottom, top = self._heights(ch)
            self.assertTrue(-o <= bottom <= 0 and p['capHeight'] <= top <= p['capHeight'] + o, ch)
        for ch in 'iklmnrvwxz':
            self.assertEqual(self._heights(ch)[0], 0, ch)
        for ch in 'mnruvwxz':
            top = self._heights(ch)[1]
            self.assertTrue(p['xHeight'] <= top <= p['xHeight'] + o, ch)
        for ch in 'bdhkl':
            self.assertEqual(self._heights(ch)[1], p['glyphAscender'], ch)
        for ch in 'gjpqy':
            bottom = self._heights(ch)[0]
            self.assertTrue(p['glyphDescender'] - o <= bottom <= p['glyphDescender'], ch)

    def test_ink_stays_inside_the_advance(self):
        for ch, (contours, advance) in self.glyphs.items():
            left, _, right, _ = build.bounds(contours)
            self.assertGreaterEqual(left, 0, ch)
            self.assertLessEqual(right, advance, ch)

    def test_figures_share_one_advance(self):
        advances = {self.glyphs[ch][1] for ch in '0123456789'}
        self.assertEqual(len(advances), 1)

    def test_contours_are_clean(self):
        for ch, (contours, _) in self.glyphs.items():
            outer = sum(1 for c in contours if geometry.area(c) > 0)
            self.assertGreaterEqual(outer, 1, ch)
            for c in contours:
                self.assertGreaterEqual(len(c), 3, ch)
                self.assertEqual(len(set(c)), len(c), f'{ch!r} repeats a point')

    def test_one_piece_letters_stay_in_one_piece(self):
        """Strokes join up: no letter outside i, j and the marks breaks apart."""
        for ch in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghklmnopqrstuvwxyz0123456789':
            outers = [c for c in self.glyphs[ch][0] if geometry.area(c) > 0]
            self.assertEqual(len(outers), 1, ch)

    def test_stems_are_heavier_than_bars(self):
        """The brush makes vertical travel thick and horizontal travel thin."""
        polygons = brush.stroke([N(0, 0, 90), N(0, 100, 90)], 130, 100, 0.6)
        polygons += brush.stroke([N(200, 0, 0), N(300, 0, 0)], 130, 100, 0.6)
        stem, bar = sorted(geometry.finish(geometry.union(polygons)), key=lambda c: min(x for x, _ in c))
        self.assertEqual(max(x for x, _ in stem) - min(x for x, _ in stem), 130)
        self.assertEqual(max(y for _, y in bar) - min(y for _, y in bar), 100)

    def test_cut_terminals_are_flat(self):
        """A horizontal cut trims a slanted end to a level line."""
        polygons = brush.stroke([N(0, 0, 60), N(100, 173, 60)], 120, 120, 0.6, cut1=0)
        contour = geometry.finish(geometry.union(polygons))[0]
        top = max(y for _, y in contour)
        self.assertEqual(top, 173)
        self.assertGreaterEqual(sum(1 for _, y in contour if y == top), 2)

    def test_font_file(self):
        font = TTFont(str(self.out / f"{self.params['postscriptName']}.ttf"))
        cmap = font.getBestCmap()
        self.assertEqual(sorted(cmap), list(range(0x20, 0x7F)))
        self.assertEqual(font['head'].created, build.TIMESTAMP)
        self.assertEqual(font['OS/2'].fsType, 0)
        self.assertEqual(font['OS/2'].sxHeight, self.params['xHeight'])
        names = {r.nameID: r.toUnicode() for r in font['name'].names}
        self.assertEqual(names[2], 'Bold')
        self.assertEqual(names[13], 'MIT License')

    def test_field_matches_the_outline(self):
        rng = self.params['atlas']['pxRange']
        med = msdf.median(self.image)
        alpha = self.image[..., 3] / 255.0
        clear = np.abs(alpha - 0.5) * rng > 0.75
        bad = clear & ((med > 0.5) != (alpha > 0.5))
        self.assertEqual(int(bad.sum()), 0)

    def test_far_texels_hold_the_true_distance(self):
        """Away from edges every channel holds the true distance, so no false
        near-edge median can show as a dot in small text."""
        rng = self.params['atlas']['pxRange']
        alpha = self.image[..., 3].astype(int)
        far = np.abs(alpha / 255.0 - 0.5) * rng > msdf.CORRECT_BEYOND + 0.1
        for channel in range(3):
            self.assertEqual(int(np.abs(self.image[..., channel].astype(int) - alpha)[far].max()), 0)

    def test_metrics_name_the_x_height(self):
        doc = (self.out / 'metrics.json').read_text(encoding='utf-8')
        self.assertIn('"xHeight": 516', doc)
        self.assertNotIn('smallcapHeight', doc)

    def test_builds_are_deterministic(self):
        with tempfile.TemporaryDirectory() as tmp:
            again = Path(tmp) / 'body'
            build.build_font('body', again)
            self.assertEqual(check_dist.differences(self.out, again), [])


if __name__ == '__main__':
    unittest.main()
