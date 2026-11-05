"""Package dist/ for a release: one archive per font, the license and checksums.

    python -m tools.package_release v0.1.0 [--out release]

Each archive holds the font's folder and the LICENSE, with sorted names,
fixed times and no owner names, so the same dist/ always packs identically.
"""
import argparse
import gzip
import hashlib
import io
import shutil
import sys
import tarfile
from pathlib import Path

from tools import build

ROOT = build.ROOT
MTIME = 1767225600  # 2026-01-01T00:00:00Z


def _add(tar, name, data):
    info = tarfile.TarInfo(name)
    info.size = len(data)
    info.mtime = MTIME
    info.mode = 0o644
    info.uid = info.gid = 0
    info.uname = info.gname = ''
    tar.addfile(info, io.BytesIO(data))


def pack_font(font_dir, license_bytes, archive):
    """Write font_dir and LICENSE into a reproducible .tar.gz at archive."""
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode='w', format=tarfile.PAX_FORMAT) as tar:
        for path in sorted(font_dir.iterdir()):
            _add(tar, f'{font_dir.name}/{path.name}', path.read_bytes())
        _add(tar, f'{font_dir.name}/LICENSE', license_bytes)
    with archive.open('wb') as out, gzip.GzipFile(fileobj=out, mode='wb', mtime=0, filename='') as gz:
        gz.write(raw.getvalue())


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('tag')
    parser.add_argument('--out', type=Path, default=ROOT / 'release')
    args = parser.parse_args()
    if args.out.exists():
        shutil.rmtree(args.out)
    args.out.mkdir(parents=True)
    license_bytes = (ROOT / 'LICENSE').read_bytes()
    for name in build.FONTS:
        pack_font(ROOT / 'dist' / name, license_bytes, args.out / f'{name}-{args.tag}.tar.gz')
    (args.out / 'LICENSE').write_bytes(license_bytes)
    sums = []
    for path in sorted(args.out.iterdir()):
        sums.append(f'{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}\n')
    (args.out / 'SHA256SUMS').write_text(''.join(sums), encoding='utf-8', newline='\n')
    print(f'packed {len(build.FONTS)} font(s) into {args.out}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
