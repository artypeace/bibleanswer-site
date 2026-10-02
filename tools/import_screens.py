#!/usr/bin/env python3
"""Brings the app's real screens into the website. Two ways.

A. From a folder of screenshots by hand (an iPhone screenshot of each screen, saved as is):

    python3 tools/import_screens.py --lang ru --read read.png --guide guide.png --counsel advice.png --quiet player.png --hours prayer.png
    (Mac window: --mac-answer a.png --mac-bible b.png --mac-advice c.png --mac-listen d.png;  --default makes it the picture for every language without its own)

B. From the app's own App Store screenshot run
(tools/store-screenshots in the app repository: shoot.sh makes the raw screens, storeframes makes the frames):

    python3 tools/import_screens.py ~/store-screenshots          # the folder shoot.sh writes to ($STORE_WORK)
    python3 tools/import_screens.py ~/store-screenshots --lang ru en
    python3 tools/import_screens.py ~/store-screenshots --default en

It reads   <work>/raw/<tag>-<name>.png          the real screens, untouched, 1320 x 2868  (tag: en ru es ptBR fr fil)
           <work>/out/<tag>-<NN>-<name>.png     the composed frames (headline + iPhone), 1320 x 2868
           <work>/out-ipad/<tag>-<NN>-<name>.png   the iPad frames, 2064 x 2752 (optional)
           <work>/raw-mac/<tag>-<name>.png      the Mac app's own window, title bar and sidebar included (optional)
           <work>/out-mac/<tag>-<NN>-<name>.png the Mac frames, 2880 x 1800 (optional)
and writes light WebP copies:
  assets/story/<scene>/<lang>.webp      the screens inside the phone that follows the page   (see STORY)
  assets/mac/<scene>/<lang>.webp        the Mac window on the home page                       (see MAC_STORY)
  assets/screens/iphone/<lang>/<n>.webp the "A look inside" strip                              (see GALLERY)
  assets/screens/ipad/<lang>/<n>.webp
  assets/screens/mac/<lang>/<n>.webp
then rebuilds the site. Standard library plus Pillow. Nothing is drawn or changed: the pictures are the app's own."""
import argparse, pathlib, subprocess, sys
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
LANGS = {'en': 'en', 'ru': 'ru', 'es': 'es', 'pt': 'ptBR', 'fr': 'fr', 'fil': 'fil'}   # site language -> the tag in file names
ALIASES = {'pt': ('ptBR', 'ptbr', 'pt-BR', 'pt-br', 'pt')}

# scene of the phone on the home page -> the raw screen that shows it
STORY = {'read': 'bible', 'guide': 'guide', 'counsel': 'advice', 'quiet': 'soundplayer3', 'hours': 'prayer'}
# the "A look inside" strip: the composed frames, in order (4 for iPhone, 2 for iPad)
GALLERY = {'iphone': ('02-answer', '03-bible', '06-guide', '07-sounds'), 'ipad': ('02-answer', '03-bible'), 'mac': ('02-answer', '03-bible', '05-advice')}
# the sections of the Mac window on the home page -> the raw window screenshot that shows it (the first one found)
MAC_STORY = {'answer': ('answer', 'home'), 'bible': ('bible',), 'advice': ('advice',), 'listen': ('moments', 'listen', 'sounds')}
WIDTH = {'story': 720, 'iphone': 640, 'ipad': 900, 'mac': 900, 'macwin': 1600}


def find(folder, tags, stem):
    for t in tags:
        p = folder / f'{t}-{stem}.png'
        if p.exists():
            return p
    return None


def save(src, dst, width, ratio=None):
    im = Image.open(src).convert('RGB')
    if ratio and abs(im.width / im.height - ratio) > 0.01:
        print(f'  warning: {src.name} is {im.width}x{im.height}, not the expected shape')
    h = round(im.height * width / im.width)
    dst.parent.mkdir(parents=True, exist_ok=True)
    im.resize((width, h), Image.LANCZOS).save(dst, 'WEBP', quality=84, method=6)
    return dst.stat().st_size // 1024


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('work', nargs='?', help='the folder shoot.sh writes to (STORE_WORK): raw/, out/, out-ipad/ ...')
    for scene in STORY:
        ap.add_argument(f'--{scene}', metavar='PNG', help=f'one screenshot for the "{scene}" scene of the phone (with --lang)')
    for scene in MAC_STORY:
        ap.add_argument(f'--mac-{scene}', metavar='PNG', help=f'one window screenshot for the "{scene}" section of the Mac window (with --lang)')
    ap.add_argument('--lang', nargs='*', choices=list(LANGS), help='only these site languages (default: all that are there)')
    ap.add_argument('--default', choices=list(LANGS), help='also use this language\'s screens for every language without its own')
    ap.add_argument('--no-build', action='store_true')
    a = ap.parse_args()
    hand = {sc: getattr(a, sc) for sc in STORY if getattr(a, sc)}
    hand_mac = {sc: getattr(a, f'mac_{sc}') for sc in MAC_STORY if getattr(a, f'mac_{sc}')}
    if hand or hand_mac:
        if not a.lang or len(a.lang) != 1:
            sys.exit('with single screenshots give exactly one language: --lang ru')
        lang = a.lang[0]
        for scene, path in hand.items():
            kb = save(pathlib.Path(path).expanduser(), ROOT / f'assets/story/{scene}/{lang}.webp', WIDTH['story'], 1320 / 2868)
            print(f'{lang:3} phone {scene} {kb}KB')
            if a.default == lang:
                save(pathlib.Path(path).expanduser(), ROOT / f'assets/story/{scene}/default.webp', WIDTH['story'], 1320 / 2868)
        for scene, path in hand_mac.items():
            kb = save(pathlib.Path(path).expanduser(), ROOT / f'assets/mac/{scene}/{lang}.webp', WIDTH['macwin'], 2640 / 1698)
            print(f'{lang:3} mac {scene} {kb}KB')
            if a.default == lang:
                save(pathlib.Path(path).expanduser(), ROOT / f'assets/mac/{scene}/default.webp', WIDTH['macwin'], 2640 / 1698)
        if not a.no_build:
            subprocess.check_call([sys.executable, str(ROOT / 'tools' / 'build.py')])
        return
    if not a.work:
        sys.exit('give the folder of the screenshot run, or single screenshots (--read ... --lang ru); see --help')
    work = pathlib.Path(a.work).expanduser()
    raw, out, out_ipad = work / 'raw', work / 'out', work / 'out-ipad'
    raw_mac, out_mac = work / 'raw-mac', work / 'out-mac'
    if not any(d.is_dir() for d in (raw, out, raw_mac, out_mac)):
        sys.exit(f'{work}: no raw/, out/, raw-mac/ or out-mac/ folder here')

    done = 0
    for lang in (a.lang or list(LANGS)):
        tags = ALIASES.get(lang, (LANGS[lang],))
        wrote = []
        for scene, stem in STORY.items():
            src = find(raw, tags, stem)
            if src:
                kb = save(src, ROOT / f'assets/story/{scene}/{lang}.webp', WIDTH['story'], 1320 / 2868)
                wrote.append(f'{scene} {kb}KB')
                if a.default == lang:
                    save(src, ROOT / f'assets/story/{scene}/default.webp', WIDTH['story'], 1320 / 2868)
        for scene, stems in MAC_STORY.items():
            src = next((f for f in (find(raw_mac, tags, st) for st in stems) if f), None)
            if src:
                kb = save(src, ROOT / f'assets/mac/{scene}/{lang}.webp', WIDTH['macwin'], 2640 / 1698)
                wrote.append(f'mac {scene} {kb}KB')
                if a.default == lang:
                    save(src, ROOT / f'assets/mac/{scene}/default.webp', WIDTH['macwin'], 2640 / 1698)
        for device, folder in (('iphone', out), ('ipad', out_ipad), ('mac', out_mac)):
            for n, stem in enumerate(GALLERY[device], 1):
                src = find(folder, tags, stem)
                if src:
                    kb = save(src, ROOT / f'assets/screens/{device}/{lang}/{n}.webp', WIDTH[device])
                    wrote.append(f'{device}/{n} {kb}KB')
        print(f'{lang:3}', ', '.join(wrote) if wrote else '- nothing found (tag ' + '/'.join(tags) + ')')
        done += bool(wrote)
    if not done:
        sys.exit('no screens found: check the folder and the file names (<tag>-<name>.png)')
    if not a.no_build:
        subprocess.check_call([sys.executable, str(ROOT / 'tools' / 'build.py')])


if __name__ == '__main__':
    main()
