"""Localized beginner walkthrough and editorial notes for Bible Answer."""
import json

from build_articles import E, GUIDANCE, LANG_CODE, LANGS, app_card, footer, guidance_path, hub, load, navigation, path, shell


SCREENS = ('story/read', 'story/guide', 'inside/plans')


def localized_urls(cfg, key):
    base = cfg['siteUrl'].rstrip('/')
    urls = {LANG_CODE[lang]: f'{base}/{guidance_path(lang, key)}' for lang in LANGS}
    urls['x-default'] = urls['en']
    return urls


def starter(root, lang, copy):
    guide = next(a for a in load(root) if a['lang'] == lang and a['key'] == 'first-gospel')
    steps = []
    for image, title, text in zip(SCREENS, copy[2:8:2], copy[3:8:2]):
        steps.append(f'''<section class="guidance-step">
  <div><h2>{E(title)}</h2><p>{E(text)}</p></div>
  <img src="/assets/{image}/{lang}.webp" width="720" height="1564" alt="{E(title)}" loading="lazy" decoding="async">
</section>''')
    return ''.join(steps) + f'<p><a href="/{path(guide)}">{E(copy[8])}</a></p>'


def editorial(cfg, copy):
    sections = [f'<section><h2>{E(title)}</h2><p>{E(text)}</p></section>'
                for title, text in zip(copy[2::2], copy[3::2])]
    email = E(cfg['contactEmail'])
    return ''.join(sections) + f'<p><a href="mailto:{email}">{email}</a></p>'


def page(root, cfg, lang, key, head_common, og_head):
    copy = GUIDANCE[lang][key]
    title, lead = copy[:2]
    urls = localized_urls(cfg, key)
    url = urls[LANG_CODE[lang]]
    extra = ''.join(f'<link rel="alternate" hreflang="{code}" href="{E(link)}">\n' for code, link in urls.items())
    extra += '<link rel="stylesheet" href="/guidance.css">\n'
    data = {'@context': 'https://schema.org', '@type': 'WebPage', 'name': title,
            'description': lead, 'url': url, 'inLanguage': LANG_CODE[lang]}
    extra += '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False).replace('</', '<\\/') + '</script>\n'
    content = starter(root, lang, copy) if key == 'start' else editorial(cfg, copy)
    body = navigation(lang, [{'lang': l} for l in LANGS], lambda a: guidance_path(a['lang'], key)) + f'''
<main id="main" class="guide-index guidance-page">
  <header class="guide-index__hero"><p class="article-kicker">Bible Answer</p><h1>{E(title)}</h1><p>{E(lead)}</p></header>
  <div class="article-prose">{content}</div>
{app_card(lang, cfg) if key == 'start' else ''}
</main>
''' + footer(cfg, lang)
    return shell(cfg, lang, title, lead, url, cfg['siteUrl'].rstrip('/') + f'/assets/og/og-{lang}.jpg',
                 extra, body, head_common, og_head)


def write(root, cfg, head_common, og_head):
    for lang in LANGS:
        for key in GUIDANCE[lang]:
            target = root / guidance_path(lang, key) / 'index.html'
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(page(root, cfg, lang, key, head_common, og_head), encoding='utf-8')


def sitemap_rows(cfg):
    rows = []
    for key in GUIDANCE['en']:
        urls = localized_urls(cfg, key)
        alts = ''.join(f'\n    <xhtml:link rel="alternate" hreflang="{code}" href="{E(url)}"/>' for code, url in urls.items())
        rows.extend(f'  <url>\n    <loc>{E(urls[LANG_CODE[lang]])}</loc>{alts}\n  </url>' for lang in LANGS)
    return rows
