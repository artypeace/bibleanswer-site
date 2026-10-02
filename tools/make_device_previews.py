#!/usr/bin/env python3
"""Regenerate original vector housings with real native app screenshots.

Requires Pillow. Review all sources first. No Apple Design Resources are used.
python3 tools/make_device_previews.py --screens /path/to/app/screens \
    --watch '/path/to/Apple Watch'

--screens contains raw/<tag>-home.png, raw-ipad/<tag>-home.png,
and raw-mac/<tag>-home.png. Portuguese source tag is ptBR.
--watch contains <language>/01-word.png (Portuguese folder: pt-BR).
"""
from pathlib import Path
from PIL import Image
import argparse
import base64
import hashlib
import io
import json

ROOT = Path(__file__).resolve().parent.parent
LANGS = {'en': 'en', 'ru': 'ru', 'es': 'es', 'pt': 'ptBR', 'fr': 'fr', 'fil': 'fil'}


def screenshot(path, width):
    with Image.open(path) as source:
        size = source.size
        image = source.convert('RGB')
        if image.width > width:
            image = image.resize((width, round(image.height * width / image.width)), Image.Resampling.LANCZOS)
        output = io.BytesIO()
        image.save(output, 'WEBP', quality=90, method=6)
    return 'data:image/webp;base64,' + base64.b64encode(output.getvalue()).decode(), size


def wrap(width, height, definitions, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}"><defs>{definitions}</defs>{body}</svg>')


def phone(screen):
    return wrap(1450, 3000, '''
      <linearGradient id="metal" x1="0" y1="0" x2="1" y2=".2">
        <stop stop-color="#444d52"/><stop offset=".025" stop-color="#b5babe"/>
        <stop offset=".065" stop-color="#525b60"/><stop offset=".5" stop-color="#788185"/>
        <stop offset=".935" stop-color="#3d464c"/><stop offset=".98" stop-color="#bac1c5"/>
        <stop offset="1" stop-color="#374146"/>
      </linearGradient>
      <linearGradient id="edge" x1="0" y1="0" x2=".2" y2="1">
        <stop stop-color="#d9dde0"/><stop offset=".12" stop-color="#667075"/>
        <stop offset=".8" stop-color="#303a3f"/><stop offset="1" stop-color="#929b9f"/>
      </linearGradient>
      <clipPath id="display"><rect x="65" y="66" width="1320" height="2868" rx="166"/></clipPath>
    ''', f'''
      <g fill="url(#edge)" stroke="#232c31" stroke-width="3">
        <rect x="16" y="390" width="23" height="114" rx="9"/>
        <rect x="16" y="572" width="23" height="224" rx="9"/>
        <rect x="16" y="843" width="23" height="224" rx="9"/>
        <rect x="1411" y="726" width="23" height="362" rx="9"/>
      </g>
      <rect x="27" y="17" width="1396" height="2966" rx="211" fill="url(#metal)" stroke="url(#edge)" stroke-width="7"/>
      <rect x="41" y="32" width="1368" height="2936" rx="197" fill="#030609" stroke="#a8b0b4" stroke-opacity=".42" stroke-width="3"/>
      <image href="{screen}" x="65" y="66" width="1320" height="2868" clip-path="url(#display)"/>
      <rect x="516" y="114" width="418" height="114" rx="57" fill="#010204"/>
      <circle cx="877" cy="171" r="17" fill="#070d17"/><circle cx="877" cy="171" r="9" fill="#0b1829"/>
      <path d="M210 23h1030M210 2977h1030" stroke="#e5eaec" stroke-opacity=".3" stroke-width="2"/>
      <path d="M29 321h14M1408 321h14M29 2681h14M1408 2681h14" stroke="#192329" stroke-width="9"/>
    ''')


def tablet(screen):
    return wrap(2196, 2884, '''
      <linearGradient id="metal" x1="0" y1="0" x2="1" y2=".4">
        <stop stop-color="#6c757a"/><stop offset=".03" stop-color="#c4c9cd"/>
        <stop offset=".07" stop-color="#687177"/><stop offset=".92" stop-color="#596268"/>
        <stop offset=".985" stop-color="#c2c8cc"/><stop offset="1" stop-color="#5c666c"/>
      </linearGradient>
      <clipPath id="display"><rect x="66" y="66" width="2064" height="2752" rx="92"/></clipPath>
    ''', f'''
      <rect x="211" y="0" width="136" height="8" rx="3" fill="#899298"/>
      <rect x="2" y="5" width="2192" height="2874" rx="126" fill="url(#metal)" stroke="#d3d8db" stroke-opacity=".55" stroke-width="4"/>
      <rect x="16" y="19" width="2164" height="2846" rx="114" fill="#050708"/>
      <image href="{screen}" x="66" y="66" width="2064" height="2752" clip-path="url(#display)"/>
      <circle cx="2155" cy="1442" r="10" fill="#111923"/><circle cx="2155" cy="1442" r="5" fill="#203147"/>
      <path d="M160 10h1876M160 2874h1876" stroke="#dde1e3" stroke-opacity=".2" stroke-width="3"/>
    ''')


def watch(screen):
    return wrap(720, 1450, '''
      <linearGradient id="band" x1="0" y1="0" x2="1" y2="0">
        <stop stop-color="#14191b"/><stop offset=".12" stop-color="#353b3e"/>
        <stop offset=".5" stop-color="#252b2e"/><stop offset=".87" stop-color="#2c3235"/>
        <stop offset="1" stop-color="#121719"/>
      </linearGradient>
      <linearGradient id="metal" x1="0" y1="0" x2="1" y2=".3">
        <stop stop-color="#192026"/><stop offset=".07" stop-color="#a0a9af"/>
        <stop offset=".13" stop-color="#465158"/><stop offset=".85" stop-color="#3b454e"/>
        <stop offset=".94" stop-color="#9faab1"/><stop offset="1" stop-color="#1a232a"/>
      </linearGradient>
      <linearGradient id="glass" x1="0" y1="0" x2=".1" y2="1">
        <stop stop-color="#4b5960"/><stop offset=".1" stop-color="#0e151a"/>
        <stop offset=".9" stop-color="#070e13"/><stop offset="1" stop-color="#26333c"/>
      </linearGradient>
      <clipPath id="display"><rect x="143" y="467" width="416" height="496" rx="94"/></clipPath>
    ''', f'''
      <path d="M202 430V112Q202 28 270 28H432Q500 28 500 112V430Z" fill="url(#band)" stroke="#586064" stroke-opacity=".5" stroke-width="3"/>
      <path d="M199 997H503L486 1332Q483 1418 414 1418H288Q219 1418 216 1332Z" fill="url(#band)" stroke="#586064" stroke-opacity=".5" stroke-width="3"/>
      <path d="M217 124V383M485 124V383M215 1070L230 1322M487 1070L472 1322" fill="none" stroke="#798184" stroke-opacity=".15" stroke-width="3"/>
      <rect x="268" y="80" width="166" height="38" rx="19" fill="#101619" stroke="#454e52" stroke-width="2"/>
      <rect x="310" y="162" width="82" height="40" rx="20" fill="#4a5357" stroke="#71797c" stroke-width="2"/>
      <g fill="#11181c" stroke="#485157" stroke-width="2">
        <ellipse cx="351" cy="1123" rx="11" ry="18"/><ellipse cx="351" cy="1192" rx="11" ry="18"/><ellipse cx="351" cy="1261" rx="11" ry="18"/><ellipse cx="351" cy="1330" rx="11" ry="18"/>
      </g>
      <rect x="611" y="529" width="64" height="105" rx="22" fill="url(#metal)" stroke="#94a0a9" stroke-width="3"/>
      <path d="M653 543v76M660 543v76M666 549v64" stroke="#1c262f" stroke-width="3"/>
      <rect x="613" y="713" width="17" height="106" rx="8" fill="#596770"/>
      <rect x="75" y="385" width="552" height="660" rx="181" fill="url(#metal)" stroke="#929da5" stroke-width="3"/>
      <rect x="91" y="399" width="520" height="631" rx="166" fill="url(#glass)" stroke="#141d23" stroke-width="6"/>
      <image href="{screen}" x="143" y="467" width="416" height="496" clip-path="url(#display)"/>
      <path d="M167 428c48-27 118-31 185-31 67 0 137 4 185 31" fill="none" stroke="#b4c0c5" stroke-opacity=".26" stroke-width="4"/>
    ''')


def laptop(screen):
    return wrap(3000, 1950, '''
      <linearGradient id="metal" x1="0" y1="0" x2=".05" y2="1">
        <stop stop-color="#b2bbc0"/><stop offset=".06" stop-color="#5b666e"/>
        <stop offset=".89" stop-color="#424c54"/><stop offset="1" stop-color="#89949c"/>
      </linearGradient>
      <linearGradient id="base" x1="0" y1="0" x2="0" y2="1">
        <stop stop-color="#c4ccd1"/><stop offset=".14" stop-color="#a1adb5"/>
        <stop offset=".45" stop-color="#586772"/><stop offset=".8" stop-color="#293741"/>
        <stop offset="1" stop-color="#72818b"/>
      </linearGradient>
      <clipPath id="display"><rect x="220" y="80" width="2560" height="1645" rx="25"/></clipPath>
    ''', f'''
      <rect x="180" y="39" width="2640" height="1752" rx="59" fill="url(#metal)" stroke="#c4cdd2" stroke-width="4"/>
      <rect x="192" y="52" width="2616" height="1730" rx="47" fill="#06090d"/>
      <image href="{screen}" x="220" y="80" width="2560" height="1645" clip-path="url(#display)" preserveAspectRatio="xMidYMid meet"/>
      <path d="M1335 79h330v61a25 25 0 0 1-25 25h-280a25 25 0 0 1-25-25Z" fill="#05080c"/>
      <circle cx="1500" cy="114" r="7" fill="#142132"/>
      <path d="M20 1791h2960v34c-3 38-46 74-111 86H131c-65-12-108-48-111-86Z" fill="url(#base)" stroke="#626f78" stroke-width="3"/>
      <path d="M1220 1792h560v13c-1 18-12 26-35 26h-490c-23 0-34-8-35-26Z" fill="#52616d" stroke="#d0d8dc" stroke-opacity=".55" stroke-width="2"/>
      <path d="M123 1909h2754" stroke="#1d2a35" stroke-width="8"/>
      <path d="M160 1917h240v11H160ZM2600 1917h240v11h-240Z" fill="#15212b"/>
    ''')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--screens', type=Path, required=True)
    parser.add_argument('--watch', type=Path, required=True)
    args = parser.parse_args()
    output = ROOT / 'assets/devices'
    manifest = []
    for lang, tag in LANGS.items():
        sources = {
            'iphone': args.screens / f'raw/{tag}-home.png',
            'ipad': args.screens / f'raw-ipad/{tag}-home.png',
            'watch': args.watch / ('pt-BR' if lang == 'pt' else lang) / '01-word.png',
            'mac': args.screens / f'raw-mac/{tag}-home.png',
        }
        for name, maker in [('iphone', phone), ('ipad', tablet), ('watch', watch), ('mac', laptop)]:
            screen, size = screenshot(sources[name], {'iphone': 720, 'ipad': 640, 'watch': 416, 'mac': 800}[name])
            destination = output / name / f'{lang}.svg'
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(maker(screen), encoding='utf-8')
            manifest.append({'language': lang, 'device': name, 'sourceFile': sources[name].name,
                             'sourceSize': list(size), 'sourceSHA256': hashlib.sha256(sources[name].read_bytes()).hexdigest(),
                             'output': destination.relative_to(ROOT).as_posix(), 'housing': 'original vector illustration'})
    (output / 'sources.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print('Wrote 24 original device illustrations with native app screens.')


if __name__ == '__main__':
    main()
