"""Public setup guides for the Bible Answer reading connector."""
import html
import json
from pathlib import Path

from build_articles import LANGS, LANG_CODE, UI, app_card, footer, hub, navigation, shell


ENDPOINT = 'https://mcp.bibleanswer.app/mcp'
COPY = json.loads(Path(__file__).with_name('connector-copy.json').read_text('utf-8'))
E = lambda text: html.escape(text, quote=True)


def path(lang):
    return ('' if lang == 'en' else lang + '/') + 'connectors/'


def page(cfg, lang, head_common, og_head):
    c = COPY[lang]
    site = cfg['siteUrl'].rstrip('/')
    urls = {LANG_CODE[l]: site + '/' + path(l) for l in LANGS}
    urls['x-default'] = urls['en']
    extra = ''.join(f'<link rel="alternate" hreflang="{code}" href="{E(url)}">\n' for code, url in urls.items())
    extra += '<link rel="stylesheet" href="/connectors.css">\n'
    url = urls[LANG_CODE[lang]]
    title = c['title'] + ' | Bible Answer'
    data = {'@context': 'https://schema.org', '@type': 'WebPage', 'name': title, 'url': url,
            'description': c['lead'], 'inLanguage': LANG_CODE[lang]}
    extra += '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False).replace('</', '<\\/') + '</script>\n'
    links = ''.join(f'<a href="#{key}">{label}</a>' for key, label in
                    (('address', E(c['address'])), ('claude', 'Claude'), ('grok', 'Grok'), ('codex', 'Codex')))
    body = navigation(lang, [{'lang': l} for l in LANGS], lambda a: path(a['lang'])) + f'''
<main id="main" class="guide-index">
  <header class="guide-index__hero"><p class="article-kicker">Bible Answer</p><h1>{E(c['title'])}</h1><p>{E(c['lead'])}</p></header>
  <div class="article-layout">
    <aside class="article-toc"><h2>{UI[lang]['contents']}</h2><nav aria-label="{E(UI[lang]['contents'])}">{links}</nav></aside>
    <article class="article-prose">
      <section id="address" aria-labelledby="connector-address"><h2 id="connector-address">{E(c['address'])}</h2>
        <p class="connector-code"><code>{ENDPOINT}</code></p><p>{E(c['about'])}</p></section>
      <section id="claude"><h2>Claude</h2><p>{E(c['claude'])}</p><p><a href="https://claude.ai/">{E(c['openClaude'])}</a></p></section>
      <section id="grok"><h2>Grok</h2><p>{E(c['grok'])}</p><p><a href="https://grok.com/connectors">{E(c['openGrok'])}</a></p></section>
      <section id="codex"><h2>Codex</h2><p>{E(c['codex'])}</p>
        <p class="connector-code"><code>codex mcp add bible-answer --url {ENDPOINT}</code></p></section>
      <section id="try"><h2>{E(c['try'])}</h2><blockquote class="connector-prompt">{E(c['prompt'])}</blockquote>
        <p><a href="/{hub(lang)}">{E(c['read'])}</a></p></section>
      <p class="article-method-note">{E(c['privacy'])} <a href="https://mcp.bibleanswer.app/privacy">{E(c['privacyLink'])}</a></p>
    </article>
  </div>
  {app_card(lang, cfg)}
</main>
''' + footer(cfg, lang)
    return shell(cfg, lang, title, c['lead'], url, site + f'/assets/og/og-{lang}.jpg', extra, body, head_common, og_head)


def write(root, cfg, head_common, og_head):
    for lang in LANGS:
        target = root / path(lang) / 'index.html'
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(page(cfg, lang, head_common, og_head), encoding='utf-8')
    print('wrote six localized connector guides')


def sitemap_rows(cfg):
    site = cfg['siteUrl'].rstrip('/')
    urls = {LANG_CODE[l]: site + '/' + path(l) for l in LANGS}
    urls['x-default'] = urls['en']
    alts = ''.join(f'\n    <xhtml:link rel="alternate" hreflang="{code}" href="{E(url)}"/>' for code, url in urls.items())
    return [f'  <url>\n    <loc>{E(urls[LANG_CODE[l]])}</loc>{alts}\n  </url>' for l in LANGS]
