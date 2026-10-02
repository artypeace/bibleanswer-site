#!/usr/bin/env python3
"""Local share cards from the site's own artwork, typefaces and guide titles.

Pillow / fontTools are only needed to regenerate these committed JPEG assets;
the ordinary site build remains standard-library only.
"""
import argparse,io,json,pathlib
from PIL import Image,ImageDraw,ImageFont,ImageFilter
ROOT=pathlib.Path(__file__).resolve().parent.parent
FONT_PATH=None
def font(size,weight=500):
 if FONT_PATH:result=ImageFont.truetype(str(FONT_PATH),size)
 else:
  from fontTools.ttLib import TTFont
  f=TTFont(ROOT/'fonts/cormorant-garamond.woff2');f.flavor=None;buf=io.BytesIO();f.save(buf);buf.seek(0)
  result=ImageFont.truetype(buf,size)
 result.set_variation_by_axes([weight]);return result
def lines(draw,text,f,width):
 rows=[];line=''
 for word in text.split():
  candidate=(line+' '+word).strip()
  if line and draw.textlength(candidate,font=f)>width:rows.append(line);line=word
  else:line=candidate
 rows.append(line);return rows
def make(a):
 im=Image.new('RGB',(1200,630),'#0F1628')
 sky=Image.open(ROOT/'assets/sky-dark.jpg').convert('RGB').resize((1200,630),Image.Resampling.LANCZOS)
 im=Image.blend(im,sky,.24)
 plate=Image.open(ROOT/f'assets/plates/{a["plate"]}.webp').convert('RGB')
 plate.thumbnail((380,420),Image.Resampling.LANCZOS)
 layer=Image.new('RGBA',im.size);layer.alpha_composite(plate.convert('RGBA'),(790+(380-plate.width)//2,145+(350-plate.height)//2))
 im=Image.alpha_composite(im.convert('RGBA'),layer)
 d=ImageDraw.Draw(im);cream='#F2EADB';gold='#D4A857'
 icon=Image.open(ROOT/'assets/icon.png').convert('RGBA').resize((64,64),Image.Resampling.LANCZOS)
 mask=Image.new('L',(64,64),0);ImageDraw.Draw(mask).rounded_rectangle((0,0,63,63),radius=15,fill=255);icon.putalpha(mask)
 im.alpha_composite(icon,(58,44));d=ImageDraw.Draw(im)
 d.text((143,60),'BIBLE ANSWER',font=font(27,600),fill=gold)
 size=78
 while True:
  f=font(size);rows=lines(d,a['title'],f,700)
  if len(rows)*size*1.08<=330:break
  size-=2
 y=190
 for row in rows:d.text((60,y),row,font=f,fill=cream);y+=int(size*1.08)
 d.line([(62,542),(710,542)],fill=gold,width=1)
 d.text((60,562),{'en':'READING GUIDES','ru':'Статьи о чтении Библии','es':'LECTURA DE LA BIBLIA','pt':'LEITURA DA BÍBLIA','fr':'LIRE LA BIBLE','fil':'PAGBABASA NG BIBLIYA'}[a['lang']],font=font(28),fill=gold)
 path=ROOT/f'assets/og/articles/{a["lang"]}-{a["key"]}.jpg';path.parent.mkdir(parents=True,exist_ok=True)
 im.convert('RGB').save(path,quality=88,optimize=True)
 return path
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--missing',action='store_true');parser.add_argument('--font',type=pathlib.Path,help='optional equivalent Cormorant Garamond variable TTF');args=parser.parse_args();FONT_PATH=args.font
 for a in json.loads((ROOT/'tools/articles.json').read_text()):
  if args.missing and (ROOT/f'assets/og/articles/{a["lang"]}-{a["key"]}.jpg').exists():continue
  print(make(a).relative_to(ROOT))
