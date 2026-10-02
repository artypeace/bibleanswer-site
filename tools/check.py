#!/usr/bin/env python3
"""Checks the built site without a browser. Exit status 1 if anything is wrong.

    python3 tools/check.py

It checks, for every page: the App Store banner tag, a canonical address, a title and a description,
Open Graph / Twitter tags and that the picture they name exists, hreflang links that point both ways,
that every local link and asset resolves to a file, that no page loads anything from another host,
and that the structured data parses. It also checks sitemap.xml and the three legal pages."""
import json, pathlib, re, sys
from html.parser import HTMLParser
from urllib.parse import urldefrag, urlparse

ROOT = pathlib.Path(__file__).resolve().parent.parent
CFG = json.loads((ROOT / 'tools/config.json').read_text('utf-8'))
SITE = CFG['siteUrl'].rstrip('/')
LANGS = ['en', 'pt', 'es', 'ru', 'fr', 'fil']
PATH = {'en': '', 'pt': 'pt', 'es': 'es', 'ru': 'ru', 'fr': 'fr', 'fil': 'fil'}
PAGES = ['index.html'] + [f'{p}/index.html' for p in PATH.values() if p] + ['links/index.html', '404.html',
                                                                              'privacy.html', 'terms.html', 'support.html', 'press/index.html']
import build_articles
ARTICLES = build_articles.load(ROOT)
PAGES += [build_articles.hub(l) + 'index.html' for l in ('en', 'ru')]
PAGES += [build_articles.path(a) + 'index.html' for a in ARTICLES]
problems = []


def bad(page, msg):
    problems.append(f'{page}: {msg}')


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.meta, self.links, self.refs, self.jsonld, self.ids = [], [], [], [], set()
        self.title, self._in_title, self._in_ld, self._ld = '', False, False, ''

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get('id'):
            self.ids.add(a['id'])
        if tag == 'meta':
            self.meta.append(a)
        elif tag == 'link':
            self.links.append(a)
            if a.get('href'):
                self.refs.append(a['href'])
        elif tag == 'title':
            self._in_title = True
        elif tag == 'script':
            if a.get('type') == 'application/ld+json':
                self._in_ld, self._ld = True, ''
            if a.get('src'):
                self.refs.append(a['src'])
        elif tag in ('a', 'img', 'source') and (a.get('href') or a.get('src')):
            self.refs.append(a.get('href') or a.get('src'))
        elif tag == 'video' and a.get('poster'):
            self.refs.append(a['poster'])
        elif tag == 'use' and a.get('href'):
            self.refs.append(a['href'])

    def handle_endtag(self, tag):
        if tag == 'title':
            self._in_title = False
        elif tag == 'script' and self._in_ld:
            self._in_ld = False
            self.jsonld.append(self._ld)

    def handle_data(self, d):
        if self._in_title:
            self.title += d
        if self._in_ld:
            self._ld += d


def meta(p, **kw):
    for m in p.meta:
        if all(m.get(k) == v for k, v in kw.items()):
            return m.get('content')
    return None


def local_file(page, ref):
    """The file a local reference points at, or None for an external one."""
    ref, _ = urldefrag(ref)
    u = urlparse(ref)
    if u.scheme in ('mailto', 'tel', 'data', 'javascript'):
        return None
    if u.scheme or u.netloc:
        if f'{u.scheme}://{u.netloc}' == SITE:
            ref = u.path
        else:
            return None
    ref = u.path
    if not ref:
        return pathlib.Path(page)
    base = pathlib.PurePosixPath(page).parent
    path = pathlib.PurePosixPath(ref.lstrip('/')) if ref.startswith('/') else (base / ref)
    parts = []
    for part in path.parts:
        if part == '..':
            parts and parts.pop()
        elif part != '.':
            parts.append(part)
    return pathlib.Path(*parts) if parts else pathlib.Path('.')


def resolves(rel):
    p = ROOT / rel
    return p.is_file() or (p.is_dir() and (p / 'index.html').is_file()) or (ROOT / f'{rel}.html').is_file()


pages = {}
for name in PAGES:
    path = ROOT / name
    if not path.exists():
        bad(name, 'missing')
        continue
    p = Page()
    p.feed(path.read_text('utf-8'))
    pages[name] = p
    private = name in ('links/index.html', '404.html')

    if meta(p, name='apple-itunes-app') != f'app-id={CFG["appStoreId"]}':
        bad(name, 'apple-itunes-app tag missing or wrong')
    if not private:
        canon = [l['href'] for l in p.links if l.get('rel') == 'canonical']
        if len(canon) != 1:
            bad(name, 'needs exactly one canonical link')
        elif not canon[0].startswith(SITE):
            bad(name, f'canonical is not on {SITE}: {canon[0]}')
        if not p.title.strip():
            bad(name, 'no <title>')
        if len(p.title.strip()) > 70:
            bad(name, f'title is {len(p.title.strip())} characters')
        if name in ('index.html',) or name.endswith('/index.html') and name != 'links/index.html':
            d = meta(p, name='description') or ''
            if not 70 <= len(d) <= 170:
                bad(name, f'description is {len(d)} characters')
        img = meta(p, property='og:image')
        if not img:
            bad(name, 'no og:image')
        elif not (ROOT / urlparse(img).path.lstrip('/')).exists():
            bad(name, f'og:image file is missing: {img}')
        if meta(p, name='twitter:card') != 'summary_large_image':
            bad(name, 'twitter:card is not summary_large_image')
        if meta(p, property='og:url') not in [l['href'] for l in p.links if l.get('rel') == 'canonical']:
            bad(name, 'og:url differs from canonical')
    if meta(p, name='robots') is None and not private:
        bad(name, 'no robots meta')

    for ref in p.refs:
        f = local_file(name, ref)
        if f is None:
            if re.match(r'(https?:)?//', ref) and not ref.startswith(SITE):
                tag_is_link = ref.startswith('http')
                # outgoing <a href> links are allowed; anything the page loads is not
                if any(x.get('href') == ref and x.get('rel') in ('stylesheet', 'icon', 'preload') for x in p.links):
                    bad(name, f'loads from another host: {ref}')
            continue
        if not resolves(f.as_posix()):
            bad(name, f'link or asset does not resolve: {ref}')

    for ld in p.jsonld:
        try:
            data = json.loads(ld)
        except ValueError as err:
            bad(name, f'JSON-LD does not parse: {err}')
            continue
        if data.get('@type') == 'SoftwareApplication':
            for k in ('name', 'operatingSystem', 'applicationCategory', 'offers', 'inLanguage'):
                if k not in data:
                    bad(name, f'JSON-LD SoftwareApplication has no {k}')

# the six home pages: hreflang both ways, language set on <html>, a CSP and no inline handlers
for lang in LANGS:
    name = f'{PATH[lang]}/index.html'.lstrip('/')
    p = pages.get(name)
    if not p:
        continue
    alts = {l.get('hreflang'): l['href'] for l in p.links if l.get('rel') == 'alternate' and l.get('hreflang')}
    if len(alts) != 7 or 'x-default' not in alts:
        bad(name, f'expected 6 languages and x-default in hreflang, found {sorted(alts)}')
    else:
        want = {f'{SITE}/{PATH[l]}'.rstrip('/') + ('/' if PATH[l] == '' else '') for l in LANGS}
        got = {v for k, v in alts.items() if k != 'x-default'}
        if {g.rstrip('/') for g in got} != {w.rstrip('/') for w in want}:
            bad(name, 'hreflang addresses do not match the six pages')
    text = (ROOT / name).read_text('utf-8')
    if 'Content-Security-Policy' not in text:
        bad(name, 'no Content-Security-Policy')
    if re.search(r'\son\w+="', text):
        bad(name, 'inline event handler (the CSP forbids it)')

# sitemap
sm = (ROOT / 'sitemap.xml').read_text('utf-8')
locs = re.findall(r'<loc>([^<]+)</loc>', sm)
for need in [f'{SITE}/' + (PATH[l] + '/' if PATH[l] else '') for l in LANGS] + [f'{SITE}/privacy', f'{SITE}/terms', f'{SITE}/support', f'{SITE}/press/']:
    if need not in locs:
        bad('sitemap.xml', f'{need} is not listed')
for lang in ('en', 'ru'):
    if SITE + '/' + build_articles.hub(lang) not in locs:
        bad('sitemap.xml', f'{lang} reading guide index is not listed')
for a in ARTICLES:
    name = build_articles.path(a) + 'index.html'
    p = pages[name]
    url = SITE + '/' + build_articles.path(a)
    if url not in locs:
        bad('sitemap.xml', f'{url} is not listed')
    canon = [l['href'] for l in p.links if l.get('rel') == 'canonical']
    if canon != [url]:
        bad(name, 'article canonical differs from its public address')
    pair = [b for b in ARTICLES if b['key'] == a['key']]
    want = {b['lang']: SITE + '/' + build_articles.path(b) for b in pair}
    want['x-default'] = want['en']
    got = {l['hreflang']: l['href'] for l in p.links if l.get('rel') == 'alternate' and l.get('hreflang')}
    if got != want:
        bad(name, 'article language alternates do not match its actual translations')
    text = (ROOT / name).read_text('utf-8')
    if len(re.findall(r'<h1(?:\s[^>]*)?>', text)) != 1:
        bad(name, 'article needs one H1')
    for section in a['sections']:
        for b in section['blocks']:
            if b['type'] == 'passage':
                v = build_articles.verse(ROOT, b['source'])
                if v['lang'] != a['lang'] or build_articles.E(v['text']) not in text or build_articles.E(v['reference']) not in text:
                    bad(name, 'quotation differs from its verse.py source')
                if v['text'][-1] in ':,;—' or '…' in v['text']:
                    bad(name, 'quotation has an incomplete ending')
    graph = json.loads(p.jsonld[0]).get('@graph', [])
    schema = next((g for g in graph if g.get('@type') == 'Article'), {})
    if schema.get('headline') != a['title'] or schema.get('datePublished') != a['date'] or schema.get('inLanguage') != a['lang']:
        bad(name, 'Article data does not match the visible article')
if 'links' in ' '.join(locs):
    bad('sitemap.xml', '/links must stay out of the sitemap')
if f'Sitemap: {SITE}/sitemap.xml' not in (ROOT / 'robots.txt').read_text('utf-8'):
    bad('robots.txt', 'does not name the sitemap')

# feed, llms.txt, IndexNow key
import xml.etree.ElementTree as ET
try:
    rss = ET.parse(ROOT / 'feed.xml').getroot()
    items = rss.findall('./channel/item')
    if rss.tag != 'rss' or not items:
        bad('feed.xml', 'is not an RSS feed with items')
    for it in items:
        for tag in ('title', 'link', 'guid', 'pubDate', 'description'):
            if it.find(tag) is None or not (it.find(tag).text or '').strip():
                bad('feed.xml', f'an item has no {tag}')
except (ET.ParseError, OSError) as err:
    bad('feed.xml', f'does not parse: {err}')
for name in ('llms.txt', 'llms-full.txt'):
    path = ROOT / name
    if not path.exists():
        bad(name, 'missing')
        continue
    text = path.read_text('utf-8')
    if not text.startswith('# '):
        bad(name, 'must start with a "# " title')
    for url in re.findall(r'\]\((https?://[^)\s]+)\)', text) + re.findall(r'(?<![(\w])(https://bibleanswer\.app[^\s)]*)', text):
        if url.startswith(SITE):
            rel_path = urldefrag(url)[0][len(SITE):].lstrip('/')
            if rel_path and not resolves(rel_path):
                bad(name, f'link does not resolve: {url}')
key = CFG.get('indexNowKey')
if key and ((ROOT / f'{key}.txt').read_text('utf-8') if (ROOT / f'{key}.txt').exists() else None) != key:
    bad(f'{key}.txt', 'the IndexNow key file is missing or does not hold the key')

# GitHub Pages
if (ROOT / 'CNAME').read_text().strip() != SITE.split('://', 1)[1]:
    bad('CNAME', 'does not match siteUrl')
if not (ROOT / '.nojekyll').exists():
    bad('.nojekyll', 'missing')

# legal pages: language anchors used by the App Store and the app
for name in ('privacy.html', 'terms.html', 'support.html'):
    p = pages.get(name)
    if p:
        for a in LANGS:
            if a not in p.ids:
                bad(name, f'anchor #{a} is missing')

if problems:
    print('\n'.join(problems))
    print(f'\n{len(problems)} problem(s)')
    sys.exit(1)
print(f'ok: {len(pages)} pages checked')
