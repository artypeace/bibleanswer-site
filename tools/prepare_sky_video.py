#!/usr/bin/env python3
"""Prepare the licensed ESO night-sky clip. Requires FFmpeg; never touches app screenshots.
Usage: FFMPEG=/path/to/ffmpeg python3 tools/prepare_sky_video.py /path/to/Geminidstimelapse1.mp4
Source and attribution are in assets/sky/credits.json. The original stays outside the repository.
"""
import os, pathlib, shutil, subprocess, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
FFMPEG = os.environ.get('FFMPEG') or shutil.which('ffmpeg')
if not FFMPEG or len(sys.argv) != 2:
    sys.exit(__doc__)
source = pathlib.Path(sys.argv[1]).resolve()
out = ROOT / 'assets' / 'sky'
out.mkdir(parents=True, exist_ok=True)
# The last 8.5 seconds avoid the observatory's laser. Keep only the sky above the telescopes.
common = [FFMPEG, '-hide_banner', '-loglevel', 'error', '-y', '-ss', '21.5', '-t', '8.5', '-i', str(source), '-an', '-map_metadata', '-1']
for name, crop, scale, crf in [('geminids-desktop.mp4', '3840:1200:0:0', '2560:800', '25'),
                               ('geminids-mobile.mp4', '800:1200:1520:0', '720:1080', '25')]:
    subprocess.run(common + ['-vf', f'crop={crop},scale={scale}:flags=lanczos,setpts=1.2*PTS,fps=25',
                             '-c:v', 'libx264', '-preset', 'medium', '-threads', '2', '-crf', crf, '-pix_fmt', 'yuv420p',
                             '-maxrate', '3500k' if 'desktop' in name else '1200k', '-bufsize', '7000k' if 'desktop' in name else '2400k', '-profile:v', 'main', '-movflags', '+faststart', str(out / name)], check=True)
subprocess.run([FFMPEG, '-hide_banner', '-loglevel', 'error', '-y', '-ss', '21.5', '-i', str(source),
                '-frames:v', '1', '-vf', 'crop=3840:1200:0:0,scale=2560:800:flags=lanczos',
                '-c:v', 'libwebp', '-quality', '88', str(out / 'geminids-poster.webp')], check=True)
for p in sorted(out.glob('geminids-*')):
    print(p.name, p.stat().st_size)
