#!/usr/bin/env python3
"""Frame existing full native WebP screenshots without re-encoding their pixels."""
from pathlib import Path
import base64,hashlib,json
from make_device_previews import phone,LANGS
ROOT=Path(__file__).resolve().parent.parent
rows=[]
for group in ['story/guide','story/read','story/hours','inside/advice-money','inside/plans','today/verse']:
 for lang in LANGS:
  source=ROOT/f'assets/{group}/{lang}.webp';output=ROOT/f'assets/previews/{group}/{lang}.svg'
  output.parent.mkdir(parents=True,exist_ok=True)
  output.write_text(phone('data:image/webp;base64,'+base64.b64encode(source.read_bytes()).decode()))
  rows.append(dict(language=lang,device='iphone',source=source.relative_to(ROOT).as_posix(),output=output.relative_to(ROOT).as_posix(),sourceSHA256=hashlib.sha256(source.read_bytes()).hexdigest(),screenPixels='unchanged'))
(ROOT/'assets/previews/sources.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
print('Framed 36 unchanged native screenshots.')
