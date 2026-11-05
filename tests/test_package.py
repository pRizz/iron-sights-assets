"""ROM-free checks for release packaging.

    python -m unittest discover -s tests -t .
"""
import hashlib
import tarfile
import tempfile
import unittest
from pathlib import Path

from tools import package_release


class Packaging(unittest.TestCase):
    def _pack(self, font_dir, out):
        package_release.pack_font(font_dir, b'license text\n', out)
        return out.read_bytes()

    def test_archives_are_reproducible_and_sorted_case_sensitively(self):
        # Arrange: names whose case-insensitive and case-sensitive orders differ.
        with tempfile.TemporaryDirectory() as tmp:
            font = Path(tmp) / 'demo'
            font.mkdir()
            for name in ('atlas.png', 'Zeta.ttf', 'metrics.json'):
                (font / name).write_bytes(name.encode())

            # Act
            first = self._pack(font, Path(tmp) / 'a.tar.gz')
            second = self._pack(font, Path(tmp) / 'b.tar.gz')
            with tarfile.open(Path(tmp) / 'a.tar.gz') as tar:
                names = tar.getnames()
                mtimes = {m.mtime for m in tar.getmembers()}

        # Assert
        self.assertEqual(hashlib.sha256(first).digest(), hashlib.sha256(second).digest())
        self.assertEqual(names, ['demo/Zeta.ttf', 'demo/atlas.png', 'demo/metrics.json', 'demo/LICENSE'])
        self.assertEqual(mtimes, {package_release.MTIME})


if __name__ == '__main__':
    unittest.main()
