"""ROM-free checks for the title font.

    python -m unittest discover -s tests -t .
"""
import tempfile
import unittest
from pathlib import Path

import numpy as np
from fontTools.ttLib import TTFont

from tools import build, check_dist, geometry, msdf


class TitleFont(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.defs, cls.params = build.load_definitions('title')
        cls.tmp = tempfile.TemporaryDirectory()
        cls.out = Path(cls.tmp.name) / 'title'
        cls.glyphs, cls.image, cls.entries = build.build_font('title', cls.out)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_covers_printable_ascii(self):
        self.assertEqual(sorted(self.glyphs), [chr(c) for c in range(0x21, 0x7F)])
        for ch, (contours, advance) in self.glyphs.items():
            self.assertTrue(contours, f'{ch!r} has no outline')
            self.assertGreater(advance, 0, ch)

    def test_letters_sit_on_their_heights(self):
        p = self.params
        for ch in 'ABCDEFGHIJKLMNOPRSTUVWXYZ0123456789':
            _, bottom, _, top = build.bounds(self.glyphs[ch][0])
            self.assertEqual((bottom, top), (0, p['capHeight']), ch)
        for ch in 'abcdefghijklmnoprstuvwxyz':
            _, bottom, _, top = build.bounds(self.glyphs[ch][0])
            self.assertEqual((bottom, top), (0, p['smallcapHeight']), ch)

    def test_ink_stays_inside_the_advance(self):
        sb = self.params['sidebearing']
        for ch, (contours, advance) in self.glyphs.items():
            left, _, right, _ = build.bounds(contours)
            self.assertGreaterEqual(left, sb, ch)
            self.assertLessEqual(right, advance - sb, ch)

    def test_contours_are_clean(self):
        for ch, (contours, _) in self.glyphs.items():
            outer = sum(1 for c in contours if geometry.area(c) > 0)
            self.assertGreaterEqual(outer, 1, ch)
            for c in contours:
                self.assertGreaterEqual(len(c), 3, ch)
                self.assertEqual(len(set(c)), len(c), f'{ch!r} repeats a point')

    def test_font_file(self):
        font = TTFont(str(self.out / f"{self.params['postscriptName']}.ttf"))
        cmap = font.getBestCmap()
        self.assertEqual(sorted(cmap), list(range(0x20, 0x7F)))
        self.assertEqual(font['head'].created, build.TIMESTAMP)
        self.assertEqual(font['head'].modified, build.TIMESTAMP)
        self.assertEqual(font['OS/2'].fsType, 0)
        names = {r.nameID: r.toUnicode() for r in font['name'].names}
        self.assertEqual(names[13], 'MIT License')
        self.assertIn('Iron Sights assets contributors', names[0])

    def test_field_matches_the_outline(self):
        """Away from edges, the median of the three channels agrees with the
        true inside/outside (alpha), so no channel artefacts flip pixels."""
        rng = self.params['atlas']['pxRange']
        med = msdf.median(self.image)
        alpha = self.image[..., 3] / 255.0
        clear = np.abs(alpha - 0.5) * rng > 0.75  # more than 0.75 px from an edge
        bad = clear & ((med > 0.5) != (alpha > 0.5))
        self.assertEqual(int(bad.sum()), 0)

    def test_field_reaches_inside_and_outside(self):
        alpha = self.image[..., 3]
        self.assertGreater(int(alpha.max()), 200)
        self.assertEqual(int(alpha.min()), 0)

    def test_corner_colours_differ(self):
        edges = msdf.colour_edges([[(0, 0), (100, 0), (100, 100), (0, 100)]])
        colours = [c for _, _, c in edges]
        for i in range(4):
            shared = colours[i] & colours[i - 1]
            self.assertNotEqual(shared, msdf.WHITE)
            self.assertNotEqual(colours[i], colours[i - 1])

    def test_builds_are_deterministic(self):
        with tempfile.TemporaryDirectory() as tmp:
            again = Path(tmp) / 'title'
            build.build_font('title', again)
            self.assertEqual(check_dist.differences(self.out, again), [])


if __name__ == '__main__':
    unittest.main()
