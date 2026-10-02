#!/usr/bin/env python3
"""Import visually reviewed native screens and the app's existing artwork.

Requires Pillow. Screens are only downscaled and encoded: no crop, retouch,
composited text, or generated UI. Review each original before running this tool.

python3 tools/import_feature_previews.py --screens /path/to/reviewed/pngs \
    --plates /path/to/app/plates
"""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
LANGS = ('en', 'ru', 'es', 'pt', 'fr', 'fil')
SCREENS = {'advice-money': 'inside/advice-money', 'plans': 'inside/plans', 'verse': 'today/verse'}
PLATES = ('plate-gate', 'plate-script', 'plate-mite', 'plate-plan-mark',
          'plate-plan-john', 'plate-kind-poetry', 'plate-plan-psalms', 'plate-plan-nt')


def encode(source, destination, width, expected=None):
    with Image.open(source) as original:
        size = original.size
        if expected and size != expected:
            raise ValueError(f'{source.name}: expected {expected}, got {size}')
        image = original.convert('RGB')
        if image.width > width:
            image = image.resize((width, round(image.height * width / image.width)), Image.Resampling.LANCZOS)
        destination.parent.mkdir(parents=True, exist_ok=True)
        image.save(destination, 'WEBP', quality=90, method=6)
    return {'sourceFile': source.name, 'sourceSize': list(size),
            'sourceSha256': hashlib.sha256(source.read_bytes()).hexdigest(),
            'output': destination.relative_to(ROOT).as_posix(),
            'outputSha256': hashlib.sha256(destination.read_bytes()).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--screens', type=Path, required=True)
    parser.add_argument('--plates', type=Path, required=True)
    args = parser.parse_args()
    sources = []
    for lang in LANGS:
        for screen, folder in SCREENS.items():
            sources.append(encode(args.screens / f'{lang}-{screen}.png',
                                  ROOT / 'assets' / folder / f'{lang}.webp', 720, (1320, 2868)))
    for plate in PLATES:
        sources.append(encode(args.plates / f'{plate}.jpg', ROOT / 'assets/plates' / f'{plate}.webp', 1100))
    manifest = {'screens': 'Native iPhone simulator captures; visually reviewed before import.',
                'processing': 'Proportional downscaling and WebP encoding only.', 'files': sources}
    (ROOT / 'assets/inside/sources.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print(f'Imported {len(LANGS) * len(SCREENS)} complete screens and {len(PLATES)} artwork files.')


if __name__ == '__main__':
    main()
