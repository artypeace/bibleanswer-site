#!/usr/bin/env python3
"""Copies the three legal pages from a folder, byte for byte, then re-adds the site's <head> block:

    python3 tools/sync_legal.py /path/to/folder-with-privacy.html-terms.html-support.html-style.css

The text of privacy.html, terms.html and support.html is the legal text the App Store and the app link to;
it is never rewritten by the build, only its <head> gets canonical / Open Graph / App Store banner tags.
Once the app and the App Store point at bibleanswer.app, these files here are the ones to edit."""
import pathlib, shutil, subprocess, sys

src = pathlib.Path(sys.argv[1])
dst = pathlib.Path(__file__).resolve().parent.parent
for name in ('privacy.html', 'terms.html', 'support.html', 'style.css'):
    shutil.copyfile(src / name, dst / name)
    print('copied', name)
subprocess.check_call([sys.executable, str(dst / 'tools' / 'build.py')])
