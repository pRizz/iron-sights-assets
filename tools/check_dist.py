"""Fail if dist/ differs from a fresh build of the sources.

    python -m tools.check_dist

Fonts and metrics must match byte for byte. PNG files are compared by their
pixels, since zlib versions may compress the same image differently.
"""
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

from tools import build

ROOT = build.ROOT


def differences(expected_dir, actual_dir):
    problems = []
    names = sorted({p.name for p in expected_dir.iterdir()} | {p.name for p in actual_dir.iterdir()})
    for name in names:
        exp, act = expected_dir / name, actual_dir / name
        if not exp.exists() or not act.exists():
            problems.append(f'{name}: present in only one of {expected_dir} and {actual_dir}')
        elif name.endswith('.png'):
            a = np.asarray(Image.open(exp))
            b = np.asarray(Image.open(act))
            if a.shape != b.shape or not np.array_equal(a, b):
                problems.append(f'{name}: pixels differ')
        elif exp.read_bytes() != act.read_bytes():
            problems.append(f'{name}: bytes differ')
    return problems


def main():
    problems = []
    with tempfile.TemporaryDirectory() as tmp:
        for name in build.FONTS:
            fresh = Path(tmp) / name
            build.build_font(name, fresh)
            committed = ROOT / 'dist' / name
            if not committed.exists():
                problems.append(f'dist/{name} is missing; run python -m tools.build')
                continue
            problems += [f'dist/{name}/{p}' for p in differences(committed, fresh)]
    for p in problems:
        print(p)
    if problems:
        print('dist/ is out of date with the sources; run python -m tools.build and commit the result')
        return 1
    print('dist/ matches a fresh build')
    return 0


if __name__ == '__main__':
    sys.exit(main())
