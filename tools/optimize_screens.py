#!/usr/bin/env python3
"""Makes light web copies of the App Store screenshots:

    python3 tools/optimize_screens.py

Reads assets/screens/<device>/<lang>/<n>.png|jpg and writes assets/screens/web/<device>/<lang>/<n>.webp
at the same pixel size (the page sets width/height from the originals). Needs Pillow."""
import pathlib
from PIL import Image

root = pathlib.Path(__file__).resolve().parent.parent / 'assets' / 'screens'
done = 0
for src in sorted(root.glob('*/*/*')):
    if src.suffix.lower() not in ('.png', '.jpg', '.jpeg') or src.parts[len(root.parts)] == 'web':
        continue
    device, lang = src.parts[-3], src.parts[-2]
    dst = root / 'web' / device / lang / f'{src.stem}.webp'
    dst.parent.mkdir(parents=True, exist_ok=True)
    Image.open(src).convert('RGB').save(dst, 'WEBP', quality=82, method=6)
    print(f'{src.relative_to(root)} ({src.stat().st_size // 1024} KB) -> {dst.relative_to(root)} ({dst.stat().st_size // 1024} KB)')
    done += 1
print(done, 'pictures')
