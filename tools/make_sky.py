#!/usr/bin/env python3
"""Build the website's resolution-independent night sky (standard library only).

Run from any directory: python3 tools/make_sky.py
The static stars are paths with round caps; they stay sharp at every pixel
density. Broad radial gradients provide atmosphere without a raster texture.
The fixed seed keeps the same sky across languages and rebuilds.
"""
import math
from pathlib import Path
import random

ROOT = Path(__file__).resolve().parent.parent
WIDTH, HEIGHT = 3840, 2400


def build():
    rng = random.Random(20261002)
    groups = {}
    # Uniform field plus an oblique, gently clustered band. Keep the middle
    # relatively quiet, where the headline and the app icon sit.
    for i in range(6400):
        x = rng.uniform(0, WIDTH)
        if i < 4700:
            y = rng.uniform(0, HEIGHT)
        else:
            y = 1640 - x * .27 + rng.gauss(0, 220)
        if not 0 < y < HEIGHT:
            continue
        centre = math.exp(-((x - 1920) / 820) ** 2 - ((y - 1050) / 740) ** 2)
        if rng.random() < centre * .48:
            continue
        tier = rng.choices(range(4), weights=[56, 30, 12, 2])[0]
        colour = rng.choices(['#DDE7F5', '#B5CBF1', '#F4E5CC'], weights=[72, 23, 5])[0]
        groups.setdefault((tier, colour), []).append(f'M{x:.1f} {y:.1f}h.01')

    out = ['''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 3840 2400" width="3840" height="2400">
  <defs>
    <linearGradient id="night" x2="0" y2="1">
      <stop stop-color="#091222"/>
      <stop offset=".5" stop-color="#0D172B"/>
      <stop offset="1" stop-color="#101829"/>
    </linearGradient>
    <radialGradient id="blue">
      <stop stop-color="#7296D8" stop-opacity=".19"/>
      <stop offset=".42" stop-color="#466AA9" stop-opacity=".09"/>
      <stop offset="1" stop-color="#263C68" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="dust">
      <stop stop-color="#7A83A9" stop-opacity=".15"/>
      <stop offset=".5" stop-color="#536086" stop-opacity=".06"/>
      <stop offset="1" stop-color="#253657" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="warm">
      <stop stop-color="#C4A875" stop-opacity=".06"/>
      <stop offset="1" stop-color="#9C8358" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="halo">
      <stop stop-color="#E1EDFF" stop-opacity=".46"/>
      <stop offset=".12" stop-color="#98B9F0" stop-opacity=".19"/>
      <stop offset=".38" stop-color="#7097D7" stop-opacity=".05"/>
      <stop offset="1" stop-color="#4C72AD" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <path fill="url(#night)" d="M0 0h3840v2400H0z"/>
  <ellipse cx="680" cy="700" rx="1400" ry="980" fill="url(#blue)"/>
  <ellipse cx="3270" cy="1620" rx="1350" ry="1180" fill="url(#blue)" opacity=".65"/>
  <ellipse cx="3300" cy="440" rx="1150" ry="740" fill="url(#warm)"/>
  <g transform="rotate(-16 1920 1200)">
    <ellipse cx="1950" cy="1160" rx="2500" ry="460" fill="url(#dust)"/>
    <ellipse cx="590" cy="1080" rx="920" ry="230" fill="url(#dust)"/>
    <ellipse cx="2970" cy="1290" rx="1060" ry="310" fill="url(#dust)"/>
  </g>''']
    for (tier, colour), points in sorted(groups.items()):
        diameter = [1.5, 2.1, 3, 4][tier]
        opacity = [.32, .48, .67, .88][tier]
        out.append(f'  <path d="{"".join(points)}" fill="none" stroke="{colour}" stroke-width="{diameter}" stroke-opacity="{opacity}" stroke-linecap="round"/>')

    # A handful of luminous stars, with a pinpoint core and a soft falloff.
    # This is decorative artwork, not an astronomical map.
    for x, y, radius in [(420, 520, 3.2), (970, 900, 2.6), (1490, 410, 3.1),
                         (2430, 620, 2.7), (3090, 340, 3.4), (3480, 1060, 2.8),
                         (630, 1660, 2.5), (2770, 1760, 2.8), (1890, 1590, 2.3)]:
        out.append(f'  <circle cx="{x}" cy="{y}" r="{radius * 15:.1f}" fill="url(#halo)"/>')
        out.append(f'  <circle cx="{x}" cy="{y}" r="{radius}" fill="#DFEAFE" opacity=".94"/>')
        out.append(f'  <circle cx="{x}" cy="{y}" r="{radius * .4:.1f}" fill="#FFFFFF"/>')
    out.append('</svg>\n')
    target = ROOT / 'assets/sky-night.svg'
    target.write_text('\n'.join(out), encoding='utf-8')
    print(f'{target.name}: {sum(map(len, groups.values()))} stars, {target.stat().st_size:,} bytes')


if __name__ == '__main__':
    build()
