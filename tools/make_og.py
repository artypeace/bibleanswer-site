#!/usr/bin/env python3
"""Draws the link-preview pictures (1200x630) the site shares on social networks and in
messengers: assets/og/og-<lang>.jpg, one per language. Needs Pillow and fontTools+brotli:

    python3 tools/make_og.py

The tagline comes from tools/app-strings.json (the app's own words), the sky, the icon and
the fonts are the ones the site already ships. Re-run it after the tagline changes."""
import io, json, pathlib
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

root = pathlib.Path(__file__).resolve().parent.parent
LANGS = ['en', 'ru', 'es', 'pt', 'fr', 'fil']
W, H = 1200, 630
GOLD, CREAM, SKY = (212, 168, 87), (242, 234, 219), (15, 22, 40)


def font(name, size, weight):
    f = TTFont(root / 'fonts' / f'{name}.woff2')
    f.flavor = None
    buf = io.BytesIO()
    f.save(buf)
    buf.seek(0)
    ft = ImageFont.truetype(buf, size)
    ft.set_variation_by_axes([weight])
    return ft


def fit(draw, text, name, weight, size, max_w):
    """The largest size (down from `size`) at which the text fits max_w."""
    while size > 24:
        ft = font(name, size, weight)
        if draw.textlength(text, font=ft) <= max_w:
            return ft
        size -= 2
    return font(name, 24, weight)


def background():
    sky = Image.open(root / 'assets/sky-dark.jpg').convert('RGB')
    sky = sky.crop((0, 260, W, 260 + H))
    shade = Image.new('RGB', (W, H), SKY)
    # a quiet veil: the sky shows at the top and fades into the page colour
    mask = Image.linear_gradient('L').resize((W, H))
    mask = mask.point(lambda v: int(60 + v * 0.62))
    return Image.composite(shade, sky, mask)


def make(lang, tagline):
    img = background()
    d = ImageDraw.Draw(img)
    icon = Image.open(root / 'assets/icon.png').convert('RGBA').resize((132, 132), Image.LANCZOS)
    mask = Image.new('L', (132, 132), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, 131, 131), radius=30, fill=255)
    img.paste(icon, (96, 150), mask)

    d.text((96, 318), 'Bible Answer', font=font('cormorant-garamond', 128, 500), fill=CREAM)
    ft = fit(d, tagline, 'cormorant-garamond-italic', 500, 56, W - 96 * 2)
    d.text((100, 468), tagline, font=ft, fill=GOLD)
    d.line((100, 570, 196, 570), fill=GOLD, width=2)
    d.text((212, 552), 'bibleanswer.app', font=font('cormorant-garamond', 30, 500), fill=(168, 155, 130))
    return img


def main():
    strings = json.loads((root / 'tools/app-strings.json').read_text(encoding='utf-8'))
    out = root / 'assets/og'
    out.mkdir(parents=True, exist_ok=True)
    for lang in LANGS:
        make(lang, strings[lang]['tagline']).save(out / f'og-{lang}.jpg', quality=88, optimize=True, progressive=True)
        print('wrote', out / f'og-{lang}.jpg')


if __name__ == '__main__':
    main()
