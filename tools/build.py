#!/usr/bin/env python3
"""Builds the Bible Answer website (bibleanswer.app) from the files in tools/.

    python3 tools/build.py                       # uses tools/config.json
    python3 tools/build.py --site-url https://example.test    # for a trial copy elsewhere

It writes: index.html and <lang>/index.html for the six languages, links/index.html, 404.html,
sitemap.xml, robots.txt, press/index.html, feed.xml, llms.txt, llms-full.txt, the IndexNow key file, and the <head> block of privacy.html, terms.html and support.html
(their text is never touched). Standard library only.

Sources
  tools/config.json         address, App Store link and id, contact address, social handles, switches
  tools/app-strings.json    words shared with the app (tools/extract_from_app.py; never edit by hand)
  tools/site-strings.json   the website's own copy, titles, descriptions and the example answer

Why static pages: every language is a page of its own, readable by a search engine without running
a script, with its own title, description, canonical address and hreflang links. The one script the
pages run (app.js) is cosmetic: reveal on scroll, parallax, the timing of the example.
There is no analytics, no cookie, no third-party request; the Content-Security-Policy says so.
"""
import argparse, base64, datetime, email.utils, hashlib, html, json, pathlib, re
import build_articles
import theme
import branding


def local_name_line(lang):
    """The name in the page's language under the hero's "Bible Answer", as the app calls itself there."""
    name = branding.local_name(lang)
    return f'<p class="hero__localname rise" style="--i:1" lang="{branding.COPY[lang]["htmlLang"]}">{e(name)}</p>' if name else ''


def mark_local(lang):
    """The same beside the header's mark, on screens wide enough for both."""
    name = branding.local_name(lang)
    return f'<span class="mark__local" lang="{branding.COPY[lang]["htmlLang"]}">{e(name)}</span>' if name else ''

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
CFG = json.loads((HERE / 'config.json').read_text('utf-8'))
APP = json.loads((HERE / 'app-strings.json').read_text('utf-8'))
SITE = json.loads((HERE / 'site-strings.json').read_text('utf-8'))
MOMENTS = json.loads((HERE / 'moments.json').read_text('utf-8'))
LANGS = ['en', 'pt', 'es', 'ru', 'fr', 'fil']

FEATURED = [0, 13, 5, 1, 6, 3]     # the six feelings the app shows first
POSITIVE = [14, 15, 16, 17, 18]    # "with a thankful heart"
ICONS = ['anxious', 'overwhelmed', 'selfworth', 'lost', 'courage', 'future', 'exhausted', 'forgiveness',
         'morning', 'anger', 'guilt', 'trust', 'money', 'lonely', 'gratitude', 'joy', 'praise', 'goodnews', 'peace']
GUIDE_ICONS = ['book', 'path', 'era', 'person', 'word', 'map', 'thread']    # order of site-strings guideChips
DEMO_FEELING = 0                   # "I'm anxious and I can't settle." -> Philippians 4:6-7
SHOTS = {'iphone': 4, 'ipad': 2, 'mac': 3}   # screenshot slots per language (see assets/screens/README.md)
SHOT_SIZE = {'iphone': (1320, 2868), 'ipad': (2064, 2752), 'mac': (2880, 1800)}

BOOT = "document.documentElement.classList.add('js')"   # tells the stylesheet scripts run, so reveal-on-scroll may hide things
BOOT_HASH = 'sha256-' + base64.b64encode(hashlib.sha256(BOOT.encode()).digest()).decode()
CSP = (f"default-src 'none'; script-src 'self' '{BOOT_HASH}'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; "
       "font-src 'self'; media-src 'self'; connect-src 'none'; base-uri 'none'; form-action 'none'")

e = lambda s: html.escape(str(s), quote=True)


def days_label(n, lang):
    """`16 days`, with the right word for the number (Russian has three forms)."""
    if lang == 'ru':
        w = 'день' if n % 10 == 1 and n % 100 != 11 else 'дня' if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14 else 'дней'
    else:
        w = {'en': 'days', 'es': 'días', 'pt': 'dias', 'fr': 'jours', 'fil': 'araw'}[lang]
    return f'{n} {w}'


def split_words(text):
    """Every word in a mask of its own, so a heading can rise word by word; the text read aloud is unchanged."""
    return ' '.join(f'<span class="w"><span style="--i:{i}">{e(w)}</span></span>' for i, w in enumerate(text.split(' ')))


def h2(text, cls='', ident=''):
    attrs = (f' id="{ident}"' if ident else '') + f' class="split{" " + cls if cls else ""}"'
    return f'<h2{attrs}>{split_words(text)}</h2>'


def have(path):
    return (ROOT / path).exists()


def rel(src, dst):
    """Relative link from the page of language `src` to the page of language `dst`."""
    up = '../' if SITE[src]['path'] else ''
    return (up + SITE[dst]['path']) or './'


def icon(name, base, sprite='feelings', prefix='feel'):
    return f'<svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><use href="{base}assets/{sprite}.svg#{prefix}-{name}"></use></svg>'


def gicon(name, base):
    return icon(name, base, 'guide', 'guide')


def inside_nav_link(section, title):
    """Readable section links with a consistent set of decorative outline icons."""
    paths = {
        'guide': '<circle cx="12" cy="12" r="9"/><path d="m15.8 8.2-2.2 5.4-5.4 2.2 2.2-5.4z"/>',
        'readings': '<path d="M12 6.5C9.5 4.9 6.2 4.4 3 5.1v14c3.2-.7 6.5-.2 9 1.4 2.5-1.6 5.8-2.1 9-1.4v-14c-3.2-.7-6.5-.2-9 1.4ZM12 6.5v14M6 9h3m-3 3h3m-3 3h3m6-6h3m-3 3h3m-3 3h3"/>',
        'advice': '<path d="M20 4H4a2 2 0 0 0-2 2v11a2 2 0 0 0 2 2h3l4 3v-3h9a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2Z"/><path d="M12 8.8c-1.4-2.1-4.1-.5-3.1 1.3.6 1.2 3.1 2.9 3.1 2.9s2.5-1.7 3.1-2.9c1-1.8-1.7-3.4-3.1-1.3Z"/>',
        'plans': '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M8 3v4m8-4v4M3 10h18m-13 5 2.5 2.5L16 12"/>',
    }
    return (f'<a href="#inside-{section}"><span class="inside-nav__icon" aria-hidden="true">'
            f'<svg viewBox="0 0 24 24" focusable="false">{paths[section]}</svg></span>'
            f'<span class="inside-nav__label">{e(title)}</span></a>')


def device_product(name, lang, base, alt='', priority=False):
    """An original vector housing containing an unaltered real app screenshot."""
    dimensions = {'iphone': (1450, 3000), 'ipad': (2196, 2884), 'watch': (720, 1450), 'mac': (3000, 1950)}
    width, height = dimensions[name]
    path = f'assets/devices/{name}/{lang}.svg'
    if not have(path):
        raise FileNotFoundError(path)
    loading = 'loading="eager" fetchpriority="high"' if priority else 'loading="lazy"'
    return (f'<img class="device-product" src="{base}{path}" '
            f'width="{width}" height="{height}" alt="{e(alt)}" {loading} decoding="async">')


def real_screen_frame(path, base, alt):
    """A complete native screenshot, with a simple physical phone frame."""
    if not have(path):
        raise FileNotFoundError(path)
    framed = path.replace('assets/', 'assets/previews/', 1).replace('.webp', '.svg')
    if not have(framed):
        raise FileNotFoundError(framed)
    return (f'<img class="device-product content-iphone" src="{base}{framed}" width="1450" height="3000" '
            f'alt="{e(alt)}" loading="lazy" decoding="async">')


def inside_visual(section, lang, base, title):
    paths = {'guide': 'assets/story/guide', 'readings': 'assets/story/read',
             'advice': 'assets/inside/advice-money', 'plans': 'assets/inside/plans'}
    plates = {'guide': 'plate-gate', 'readings': 'plate-script', 'advice': 'plate-mite', 'plans': 'plate-plan-john'}
    alt = SITE[lang]['previewAlt'].format(section=title)
    return (f'<figure class="inblock__visual inblock__visual--{section}">'
            f'<img class="inblock__plate" src="{base}assets/plates/{plates[section]}.webp" alt="" loading="lazy" decoding="async">'
            f'{real_screen_frame(paths[section] + "/" + lang + ".webp", base, alt)}</figure>')


def moments_preview_section(lang, base):
    s, moments = SITE[lang], MOMENTS[lang]
    choices, descriptions, screens = [], [], []
    for index, moment in enumerate(moments):
        ident, title = moment['asset'], moment['title']
        checked = ' checked' if index == 0 else ''
        radio = f'<input class="moment-preview__radio sr" type="radio" name="moment-preview" id="moment-choice-{ident}" value="{ident}" aria-controls="moment-description-{ident} moment-screen-{ident}"{checked}>'
        choices.append(f'<label class="moment-preview__choice" for="moment-choice-{ident}">{radio}{e(title)}</label>')
        descriptions.append(f'<p class="moment-preview__summary moment-preview__summary--{ident}" id="moment-description-{ident}">{e(moment["description"])}</p>')
        image = real_screen_frame(f'assets/moments/{ident}/{lang}.webp', base,
                                  s['previewAlt'].format(section=title))
        screens.append(f'<figure class="moment-preview__screen moment-preview__screen--{ident}" id="moment-screen-{ident}">{image}</figure>')
    return f'''<section class="section moment-preview" id="moments" aria-labelledby="h-moments">
      <div class="wrap">
        <fieldset class="moment-preview__layout">
          <legend class="sr">{e(s['momentsChooseLabel'])}</legend>
          <div class="moment-preview__text">
            <p class="eyebrow reveal">{e(s['momentsLabel'])}</p>
            {h2(s['momentPreviewH'], '', 'h-moments')}
            <p class="moment-preview__description reveal">{e(s['momentPreviewP'])}</p>
            <div class="moment-preview__picker reveal">{''.join(choices)}</div>
            <div class="moment-preview__summaries">{''.join(descriptions)}</div>
            <p class="moment-preview__credit reveal">
              <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 10v4M8 6v12M12 3v18M16 6v12M20 10v4"/></svg>
              <span>{e(s['momentsMusicLabel'])}<br><strong>Marble Space</strong> {e(s['momentsMusicJoin'])} <strong>Arty</strong></span>
            </p>
          </div>
          <div class="moment-preview__visual reveal">{''.join(screens)}</div>
        </fieldset>
      </div>
    </section>'''


def daily_previews(lang, base):
    s, ap = SITE[lang], APP[lang]
    verse = real_screen_frame(f'assets/today/verse/{lang}.webp', base, s['previewAlt'].format(section=s['todayVerseLabel']))
    prayer = real_screen_frame(f'assets/story/hours/{lang}.webp', base, s['previewAlt'].format(section=ap['hours'][0]))
    watch = device_product('watch', lang, base).replace('alt=""', f'alt="{e(s["previewAlt"].format(section="Apple Watch"))}"')
    return '<div class="daily-previews">' + ''.join(
        f'<figure class="daily-preview daily-preview--{name}"><div class="daily-preview__art">{media}</div>'
        f'<figcaption>{e(caption)}</figcaption></figure>'
        for name, media, caption in [('verse', verse, s['todayVerseLabel']), ('prayer', prayer, ap['hours'][0]), ('watch', watch, 'Apple Watch')]) + '</div>'


# ------------------------------------------------------------------ shared pieces

def store_link(lang, base, cls=''):
    """The Download-on-the-App-Store control: Apple's own badge when its file is here, else a plain button."""
    s = SITE[lang]
    url = CFG['appStoreUrl']
    for name in (f'assets/badges/app-store-{lang}.svg', 'assets/badges/app-store-en.svg'):
        if have(name):
            return (f'<a class="badge {cls}" href="{e(url)}" aria-label="{e(s["storeText"])}">'
                    f'<img src="{base}{name}" alt="{e(s["storeText"])}" height="54"></a>')
    return f'<a class="btn btn--gold {cls}" href="{e(url)}">{e(s["storeText"])}</a>'


def social_meta():
    """Site-ownership tags the search engines and Pinterest ask for; each appears only once its code is in config.json."""
    tags = [('google-site-verification', 'googleVerify'), ('msvalidate.01', 'bingVerify'),
            ('yandex-verification', 'yandexVerify'), ('p:domain_verify', 'pinterestVerify')]
    return ''.join(f'<meta name="{n}" content="{e(CFG[k])}">\n' for n, k in tags if CFG.get(k))


def social_accounts():
    return [a for a in CFG.get('social', []) if a.get('url')]


def social_links(cls=''):
    """The accounts that exist, as links; a language other than English is marked (RU, ES, ...)."""
    out = []
    for a in social_accounts():
        mark = '' if a['lang'] == 'en' else f' <span class="soc__lang">{e(a["lang"].upper())}</span>'
        out.append(f'<a{cls} href="{e(a["url"])}" rel="me noopener" target="_blank">{e(a["platform"])}{mark}</a>')
    return out


def icons_head(base):
    return (f'<link rel="icon" href="{base}favicon.ico" sizes="any">\n'
            f'<link rel="icon" type="image/png" sizes="32x32" href="{base}assets/favicon-32.png">\n'
            f'<link rel="apple-touch-icon" href="{base}assets/apple-touch-icon.png">\n')


def og_head(title, desc, url, image, locale='', others=(), alt='Bible Answer'):
    out = ('<meta property="og:type" content="website">\n<meta property="og:site_name" content="Bible Answer">\n'
           f'<meta property="og:title" content="{e(title)}">\n<meta property="og:description" content="{e(desc)}">\n'
           f'<meta property="og:url" content="{e(url)}">\n<meta property="og:image" content="{e(image)}">\n'
           '<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="630">\n'
           f'<meta property="og:image:alt" content="{e(alt)}">\n')
    if locale:
        out += f'<meta property="og:locale" content="{e(locale)}">\n'
    out += ''.join(f'<meta property="og:locale:alternate" content="{e(o)}">\n' for o in others)
    out += (f'<meta name="twitter:card" content="summary_large_image">\n<meta name="twitter:title" content="{e(title)}">\n'
            f'<meta name="twitter:description" content="{e(desc)}">\n<meta name="twitter:image" content="{e(image)}">\n')
    return out


def shot_file(device, lang, n):
    for sub in ('web/', ''):
        for ext in ('webp', 'png', 'jpg'):
            p = f'assets/screens/{sub}{device}/{lang}/{n}.{ext}'
            if have(p):
                return p
    return None


STORY = ['read', 'guide', 'counsel', 'quiet', 'hours']   # the scenes of the pinned phone, in order


def story_media(scene, lang, base, inline=False):
    """A real screen recording or screenshot for one scene of the phone: assets/story/<scene>/<lang>.* or default.*
    (mp4/webm = video, webp/png/jpg = picture). Returns '' when none was added; the drawn scene is shown then."""
    for name in (lang, 'default'):
        vids = [f'assets/story/{scene}/{name}.{x}' for x in ('webm', 'mp4') if have(f'assets/story/{scene}/{name}.{x}')]
        if vids:
            poster = next((f'assets/story/{scene}/{name}-poster.{x}' for x in ('webp', 'jpg', 'png') if have(f'assets/story/{scene}/{name}-poster.{x}')), None)
            if inline:   # the stacked layout does not play video: its picture, if there is one
                return (f'<img class="sc-media" src="{base}{poster}" width="1320" height="2868" alt="" loading="lazy" decoding="async">' if poster else '')
            kinds = {'webm': 'video/webm', 'mp4': 'video/mp4'}
            srcs = ''.join(f'<source src="{base}{v}" type="{kinds[v.rsplit(".", 1)[1]]}">' for v in vids)
            pos = f' poster="{base}{poster}"' if poster else ''
            return f'<video class="sc-media" muted loop playsinline preload="none" disablepictureinpicture{pos}>{srcs}</video>'
        for x in ('webp', 'png', 'jpg'):
            if have(f'assets/story/{scene}/{name}.{x}'):
                return f'<img class="sc-media" src="{base}assets/story/{scene}/{name}.{x}" width="1320" height="2868" alt="" loading="lazy" decoding="async">'
    return ''


MAC_SCENES = ['answer', 'bible', 'advice', 'listen']   # the sidebar's first four sections, in order


def mac_shots(lang, base):
    """The app's own Mac window, one picture per section: assets/mac/<scene>/<lang>.* or default.*"""
    found = []
    for sc in MAC_SCENES:
        for name in (lang, 'default'):
            p = next((f'assets/mac/{sc}/{name}.{x}' for x in ('webp', 'png', 'jpg') if have(f'assets/mac/{sc}/{name}.{x}')), None)
            if p:
                found.append(p)
                break
    return found


def screens_section(lang, base):
    s = SITE[lang]
    found = {d: [shot_file(d, lang, n) for n in range(1, k + 1)] for d, k in SHOTS.items()}
    if not CFG.get('showScreenshotSlots', True) and not any(any(v) for v in found.values()):
        return ''
    names = {'iphone': 'iPhone', 'ipad': 'iPad', 'mac': 'Mac'}
    rows = []
    for device, files in found.items():
        w, h = SHOT_SIZE[device]
        figs = []
        for n, path in enumerate(files, 1):
            if path:
                alt = s['shotAlt'].format(device=names[device], n=n)
                figs.append(f'<figure class="shot shot--{device} reveal" style="--d:{(n - 1) * 0.08:.2f}s"><img src="{base}{path}" width="{w}" height="{h}" loading="lazy" decoding="async" alt="{e(alt)}"></figure>')

        rows.append(f'<div class="shots shots--{device}">{"".join(figs)}</div>')
    return (f'<section class="section screens" id="screens" aria-labelledby="h-screens"><div class="wrap">'
            f'<h2 id="h-screens" class="reveal">{e(s["screensH"])}</h2>{"".join(rows)}</div></section>')



def reading_guides_section(lang, base):
    s = SITE[lang]
    article_lang = lang
    mine = {a['key']: a for a in build_articles.load(ROOT) if a['lang'] == article_lang}
    guides = [mine[k] for k in ('start', 'anxiety', 'morning')]
    mark = ''
    cards = ''.join(f'<a class="home-guide reveal" href="/{build_articles.path(a)}"><div class="home-guide__image"><img src="{base}assets/plates/{a["plate"]}.webp" alt="" width="900" height="600" loading="lazy" decoding="async"></div><div class="home-guide__body"><p class="home-guide__meta">{e(a["category"])} · {build_articles.duration(ROOT,a)} {build_articles.UI[article_lang]["reading"]} {mark}</p><h3>{e(a["title"])}</h3><p>{e(a["lead"])}</p><span class="home-guide__arrow" aria-hidden="true">↗</span></div></a>' for a in guides)
    return f'<section class="section reading-guides" id="reading-guides" aria-labelledby="h-reading-guides"><div class="wrap">{h2(s["readingGuidesH"], "", "h-reading-guides")}<p class="lede reveal">{e(s["readingGuidesP"])}</p><div class="home-guides">{cards}</div><p class="reading-guides__all"><a class="btn btn--ghost" href="/{build_articles.hub(article_lang)}">{e(s["readingGuidesAll"])}</a></p></div></section>'

def theme_script(base):
    version = hashlib.sha256((ROOT / 'theme.js').read_bytes()).hexdigest()[:12]
    return f'<script src="{base}theme.js?v={version}"></script>\n'


def head_common(lang, title, desc, canonical, og_image, robots, base, extra=''):
    alternates = ''
    if lang:
        site = CFG['siteUrl'].rstrip('/')
        alternates = ''.join(f'<link rel="alternate" hreflang="{e(SITE[l]["hreflang"])}" href="{e(site + "/" + SITE[l]["path"])}">\n' for l in LANGS)
        alternates += f'<link rel="alternate" hreflang="x-default" href="{e(site + "/")}">\n'
    return (f'<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
            f'<meta http-equiv="Content-Security-Policy" content="{CSP}">\n<title>{e(title)}</title>\n'
            f'<meta name="description" content="{e(desc)}">\n<meta name="robots" content="{robots}">\n'
            f'<link rel="canonical" href="{e(canonical)}">\n{alternates}'
            f'<link rel="alternate" type="application/rss+xml" title="Bible Answer" href="{e(CFG["siteUrl"].rstrip("/") + "/feed.xml")}">\n'
            '<meta name="color-scheme" content="dark light">\n<meta name="theme-color" content="#0F1628">\n'
            f'<meta name="apple-itunes-app" content="app-id={e(CFG["appStoreId"])}">\n{social_meta()}{extra}{icons_head(base)}{theme_script(base)}')


# ------------------------------------------------------------------ the home page of one language

def home(lang):
    s, ap = SITE[lang], APP[lang]
    base = '../' if s['path'] else ''
    site = CFG['siteUrl'].rstrip('/')
    canonical = site + '/' + s['path']
    og = f'{site}/assets/og/og-{lang}.jpg'
    sample, feelings = s['sample'], ap['feelings']
    query = s['demoQuery']
    store = store_link(lang, base)
    store_nav = (f'<a class="btn btn--gold btn--small" href="{e(CFG["appStoreUrl"])}">{e(s["storeText"])}</a>')

    shots = [shot_file(d, lang, n) for d, k in SHOTS.items() for n in range(1, k + 1)]
    ld_app = {
        '@type': 'SoftwareApplication', '@id': site + '/#app', 'name': 'Bible Answer', **({'sameAs': [a['url'] for a in social_accounts()]} if social_accounts() else {}), 'description': s['metaDescription'],
        'applicationCategory': 'ReferenceApplication', 'operatingSystem': 'iOS, iPadOS, watchOS' + (', macOS' if CFG.get('macAvailable') else ''), 'url': canonical, 'image': og,
        'inLanguage': [SITE[l]['hreflang'] for l in LANGS], 'downloadUrl': CFG['appStoreUrl'],
        'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'USD'},
    }
    if any(shots):
        ld_app['screenshot'] = [f'{site}/{p}' for p in shots if p]
    ld = {'@context': 'https://schema.org', '@graph': [
        {'@type': 'WebSite', '@id': site + '/#site', 'name': 'Bible Answer', 'alternateName': branding.alternate_names(), 'url': site + '/', 'inLanguage': s['hreflang']}, ld_app]}
    ld_json = json.dumps(ld, ensure_ascii=False, indent=1).replace('</', '<\\/')

    current = ' aria-current="true"'
    lang_items = ''.join(
        f'<li><a href="{rel(lang, l)}" lang="{e(SITE[l]["htmlLang"])}" hreflang="{e(SITE[l]["hreflang"])}"{current if l == lang else ""}>{e(APP[l]["name"])}</a></li>' for l in LANGS)
    lang_pills = ''.join(
        f'<a class="pill pill--lang" href="{rel(lang, l)}" lang="{e(SITE[l]["htmlLang"])}" hreflang="{e(SITE[l]["hreflang"])}"{current if l == lang else ""}>{e(APP[l]["name"])}</a>' for l in LANGS)
    soc = social_links()
    foot_social = (f'<p class="foot__social">' + '<span class="dot">·</span><wbr>'.join(soc) + '</p>\n  ') if soc else ''
    foot_langs = '<span class="dot">·</span><wbr>'.join(
        f'<a href="{rel(lang, l)}" lang="{e(SITE[l]["htmlLang"])}" hreflang="{e(SITE[l]["hreflang"])}">{e(APP[l]["name"])}</a>' for l in LANGS)

    featured = ''.join(
        f'<div class="chip-lg{" first" if i == DEMO_FEELING else ""}"><span class="disc">{icon(ICONS[i], base)}</span><span>{e(feelings[i]["label"])}</span></div>' for i in FEATURED)
    warm = ''.join(f'<span class="pill pill--warm">{icon(ICONS[i], base)}<span>{e(feelings[i]["label"])}</span></span>' for i in POSITIVE)

    def block(label, text, quiet, i):
        return (f'<div class="block part" style="--i:{i}"><div class="head"><h3 class="label">{e(label)}</h3><i></i></div>'
                f'<p class="body{" body--quiet" if quiet else ""}">{e(text)}</p></div>')

    answer = f'''<article class="answer demo__answer" aria-label="{e(s["demoTag"])}: {e(sample["reference"])}">
        <p class="tag">{e(s["demoTag"])}</p>
        <div class="spread">
          <div class="verse-page">
            <div class="q part" style="--i:0">{e(query)}</div>
            <p class="ref part" style="--i:1">{e(sample["reference"])}</p>
            <hr class="hair part" style="--i:2">
            <blockquote class="verse part" style="--i:3">{e(sample["verse"])}</blockquote>
            <hr class="hair part" style="--i:4">
            <div class="credit part" style="--i:5">{e(sample["translation"])}</div>
          </div>
          <div class="gutter"></div>
          <div class="reading">
            {block(ap["forYou"], sample["forYou"], False, 6)}
            <div class="prayer part" style="--i:7"><div class="head"><i></i><h3 class="label">{e(ap["prayer"])}</h3><i></i></div><p>{e(sample["prayer"])}</p></div>
            {block(ap["context"], sample["context"], True, 8)}
            <div class="diamond part" style="--i:9"><i></i><b></b><i></i></div>
            <p class="fine part" style="--i:10"><a href="{base}terms#{e(lang)}">{e(s["terms"])}</a></p>
          </div>
        </div>
      </article>'''

    lens = ''.join(f'<span{" class=on" if i == 0 else ""}>{e(t)}</span>' for i, t in enumerate(ap['lens']))
    guide_chips = ''.join(f'<div class="chip-sm">{gicon(GUIDE_ICONS[i], base)}<span>{e(t)}</span></div>' for i, t in enumerate(s['guideChips']))
    topics = ''.join(f'<div class="topic"><b></b><span>{e(t)}</span></div>' for t in ap['topics'])
    hours = ''.join(f'<span class="pill">{e(t)}</span>' for t in ap['hours'])
    mac_ok = bool(CFG.get('macAvailable'))
    devices = ''.join(
        f'<article class="device{" device--soon" if k == "mac" and not mac_ok else ""}"><div class="device__art" aria-hidden="true">{device_product(k, lang, base)}</div>'
        f'<h3>{t}{(" <span class=soon>" + e(s["soon"]) + "</span>") if k == "mac" and not mac_ok else ""}</h3><p>{e(s["macSecP"] if k == "mac" and mac_ok else s[k + "P"])}</p></article>'
        for k, t in (('iphone', 'iPhone'), ('ipad', 'iPad'), ('watch', 'Apple Watch'), ('mac', 'Mac')))


    topics_scene = ''.join(f'<div class="topic topic--s"><span class="topic__t"><b></b>{e(t)}</span><i class="skl"></i><i class="skl" style="width:68%"></i></div>' for t in ap['topics'])
    topics_scene += ''.join('<div class="topic topic--s topic--ghost"><i class="skl" style="width:38%;margin-top:0"></i><i class="skl"></i><i class="skl" style="width:68%"></i></div>' for _ in range(3))
    widths = (92, 78, 96, 84, 90, 66, 94, 80, 88, 58)
    skl_lines = lambda n: ''.join(f'<span class="skl" style="width:{widths[k % len(widths)]}%"></span>' for k in range(n))
    era_rows = ''.join(f'<div class="sc-era"><b></b><i class="skl" style="width:{w}%"></i></div>' for w in (86, 72, 90, 64))
    eq = ''.join(f'<i style="--k:{k}"></i>' for k in range(9))
    plate = lambda n, w, h, cls='': f'<img{(" class=" + chr(34) + cls + chr(34)) if cls else ""} src="{base}assets/plates/{n}.webp" width="{w}" height="{h}" alt="" loading="lazy" decoding="async">'
    cards = {
        'read': f'''<div class="card reader" data-parallax aria-hidden="true">
            <span class="skl skl--head"></span>
            <span class="skl"><b></b></span><span class="skl" style="width:96%"></span><span class="skl" style="width:88%"></span>
            <span class="skl" style="margin-top:22px"><b></b></span><span class="skl" style="width:92%"></span><span class="skl" style="width:64%"></span>
            <div class="sheet"><div class="lens">{lens}</div><span class="skl" style="margin-top:16px"></span><span class="skl" style="width:82%;margin-top:9px"></span></div>
          </div>''',
        'guide': f'''<div class="card guidecard" data-parallax aria-hidden="true">
            {plate("plate-timeline", 900, 494, "guidecard__img")}
            <div class="chipgrid">{guide_chips}</div>
          </div>''',
        'counsel': f'<div class="card topicscard" data-parallax aria-hidden="true"><div class="topics">{topics}</div></div>',
        'quiet': f'''<div class="card player" data-parallax aria-hidden="true">
            <div class="player__img" style="background-image:url({base}assets/plates/plate-galilee.webp)"></div><div class="player__veil"></div>
            <div class="play"><svg viewBox="0 0 24 24"><path d="M8 5.5v13l11-6.5z"/></svg></div>
            <div class="eq">{eq}</div>
            <div class="bar"><i></i></div>
          </div>''',
        'hours': f'<div class="card platecard" data-parallax aria-hidden="true">{plate("plate-hours", 520, 834)}</div>',
    }
    scene_inner = {
        'read': f'''<div class="sc-body"><p class="sc-ref">{e(sample["reference"])}</p>{skl_lines(5)}<p class="sc-verse">{e(sample["verse"])}</p>{skl_lines(7)}</div>
              <div class="sc-sheet"><i class="sc-grab"></i><div class="lens">{lens}</div><span class="skl"></span><span class="skl" style="width:86%"></span><span class="skl" style="width:62%"></span></div>''',
        'guide': f'{plate("plate-timeline", 900, 494, "sc-plate")}<div class="chipgrid">{guide_chips}</div><div class="sc-eras">{era_rows}</div>',
        'counsel': f'<div class="sc-body"><div class="topics">{topics_scene}</div></div>',
        'quiet': f'''<div class="sc-bg" style="background-image:url({base}assets/plates/plate-galilee.webp)"></div><div class="sc-veil"></div>
              <div class="play"><svg viewBox="0 0 24 24"><path d="M8 5.5v13l11-6.5z"/></svg></div><div class="eq">{eq}</div><div class="bar"><i></i></div>''',
        'hours': f'{plate("plate-hours", 520, 834, "sc-plate sc-plate--fill")}<div class="sc-veil"></div><div class="sc-hours">{hours}</div>',
    }
    buttons_html = ''.join(f'<i class="phone__btn phone__btn--{side}" style="--t:{t};--l:{l}"></i>' for side, t, l in
                           (('l', 206, 34), ('l', 270, 64), ('l', 350, 64), ('r', 300, 100), ('r', 560, 58)))   # action, volume, side, camera control
    def card_for(key):
        m = story_media(key, lang, base, inline=True)
        if not m:
            return cards[key]
        return f'<div class="phone phone--inline" aria-hidden="true">{buttons_html}<div class="phone__body"><div class="phone__bezel"><div class="phone__screen"><i class="phone__island"></i>{m}</div></div></div></div>'
    mac_icons = ('<path d="M4 5h16v11H9l-5 4z"/>', '<path d="M4 5h7a2 2 0 0 1 1 .4 2 2 0 0 1 1-.4h7v13h-7a2 2 0 0 0-1 .4 2 2 0 0 0-1-.4H4zM12 5.4v13"/>',
                 '<path d="M12 3v18M5 6h11l3 3-3 3H5z"/>', '<path d="M5 10v4M9 7v10M13 4v16M17 8v8M21 11v2"/>', '<path d="M7 4h10v16l-5-4-5 4z"/>')
    mac_files = mac_shots(lang, base)
    if mac_files:
        mac_inner = ''.join(f'<img class="macwin__shot{" on" if i == 0 else ""}" src="{base}{f}" width="2640" height="1698" alt="" loading="lazy" decoding="async">' for i, f in enumerate(mac_files))
        mac_cls = ' macwin--real'
    else:
        side = ''.join(f'<li{" class=on" if i == 0 else ""}><svg viewBox="0 0 24 24" aria-hidden="true">{ic}</svg>{e(t)}</li>' for i, (ic, t) in enumerate(zip(mac_icons, ap['macSidebar'])))
        mac_inner = (
            f'<div class="macwin__bar"><i></i><i></i><i></i></div><ul class="macwin__side">{side}</ul><div class="macwin__main">'
            f'<div class="mscene on"><div class="mq">{e(query)}</div><p class="sc-ref">{e(sample["reference"])}</p><p class="sc-verse">{e(sample["verse"])}</p>{skl_lines(3)}</div>'
            f'<div class="mscene"><p class="sc-ref">{e(sample["reference"])}</p>{skl_lines(4)}<p class="sc-verse">{e(sample["verse"])}</p>{skl_lines(4)}<div class="lens">{lens}</div></div>'
            f'<div class="mscene"><div class="topics">{topics_scene}</div></div>'
            f'<div class="mscene mscene--listen"><div class="sc-bg" style="background-image:url({base}assets/plates/plate-galilee.webp)"></div><div class="sc-veil"></div>'
            f'<div class="play"><svg viewBox="0 0 24 24"><path d="M8 5.5v13l11-6.5z"/></svg></div><div class="eq">{eq}</div><div class="bar"><i></i></div></div></div>')
        mac_cls = ''
    soon_line = '' if mac_ok else f'<p class="soonline"><span class="soon">{e(s["soon"])}</span></p>'
    mac_html = (f'<section class="section macsec" id="mac" aria-labelledby="h-mac"><div class="wrap">{h2(s["macSecH"], "", "h-mac")}'
                f'<p class="lede reveal" style="--d:.1s">{e(s["macSecP"])}</p>{soon_line}'
                f'<div class="macwin{mac_cls} reveal" style="--d:.15s" data-mac aria-hidden="true">{mac_inner}</div></div></section>')
    ins = ap['inside']; cn = ins['counts']
    tile = lambda n, k: f'<div class="tile"><b data-count="{n}">{n}</b><span>{e(s[k])}</span></div>'
    guide_icons = {'intro': 'book', 'story': 'path', 'howto': 'book', 'timeline': 'era', 'people': 'person', 'words': 'word', 'map': 'map', 'genealogy': 'thread'}
    guide_rows = ''.join(f'<li>{gicon(guide_icons[i["key"]], base)}<div><b>{e(i["title"])}</b><span>{e(i["summary"])}</span></div></li>' for i in ins['guide']['items'])
    lens_boxes = ''.join(f'<div class="lensbox"><i class="lensbox__number" aria-hidden="true">{n:02d}</i><div><b>{e(x["name"])}</b><span>{e(x["caption"])}</span></div></div>' for n, x in enumerate(ins['lenses'], 1))
    advice_chips = ''.join(f'<span class="pill">{e(t)}</span>' for t in ins['advice']['topics'])
    plan_plates = {'mark': 'plate-plan-mark', 'john': 'plate-plan-john', 'proverbs': 'plate-kind-poetry', 'psalms': 'plate-plan-psalms', 'newTestament': 'plate-plan-nt'}
    plan_rows = ''.join(f'<li><img class="plan__plate" src="{base}assets/plates/{plan_plates[x["id"]]}.webp" alt="" loading="lazy" decoding="async"><div class="plan__words"><b>{e(x["title"])}</b><span class="plansum">{e(x["summary"])}</span></div><span class="days">{e(days_label(x["days"], lang))}</span></li>' for x in ins['plans']['items'])
    also = ''.join(f'<span class="pill">{e(t)}</span>' for t in (s['alsoSearch'], ap['macSidebar'][4], s['alsoShare']))
    inside_html = f'''<section class="section inside" id="inside" aria-labelledby="h-inside"><div class="wrap">
      {h2(s["insideH"], "", "h-inside")}
      <p class="lede reveal" style="--d:.1s">{e(s["insideP"])}</p>
      <nav class="inside-nav" aria-label="{e(s['insideNavLabel'])}">
        {inside_nav_link('guide', ins['guide']['title'])}
        {inside_nav_link('readings', s['readingsH'])}
        {inside_nav_link('advice', ins['advice']['title'])}
        {inside_nav_link('plans', s['plansH'])}
      </nav>
      <div class="inblocks">
        <article class="inblock inblock--guide reveal" id="inside-guide"><div class="inblock__head"><span class="inblock__index" aria-hidden="true">01</span><h3>{e(ins["guide"]["title"])}</h3><p>{e(ins["guide"]["lead"])}</p></div>
          {inside_visual('guide', lang, base, ins['guide']['title'])}
          <div class="inblock__body"><ul class="inlist">{guide_rows}</ul><div class="tiles">{tile(cn["eras"], "tileEras")}{tile(cn["people"], "tilePeople")}{tile(cn["terms"], "tileTerms")}{tile(cn["places"], "tilePlaces")}</div></div></article>
        <article class="inblock inblock--flip reveal" id="inside-readings"><div class="inblock__head"><span class="inblock__index" aria-hidden="true">02</span><h3>{e(s["readingsH"])}</h3><p>{e(s["readP"])}</p></div>
          {inside_visual('readings', lang, base, s['readingsH'])}
          <div class="inblock__body"><div class="lensboxes">{lens_boxes}</div></div></article>
        <article class="inblock inblock--advice reveal" id="inside-advice"><div class="inblock__head"><span class="inblock__index" aria-hidden="true">03</span><h3>{e(ins["advice"]["title"])}</h3><p>{e(ins["advice"]["lead"])}</p></div>
          {inside_visual('advice', lang, base, ins['advice']['title'])}
          <div class="inblock__body"><div class="tiles tiles--one">{tile(cn["topics"], "tileTopics")}</div><div class="chips">{advice_chips}</div></div></article>
        <article class="inblock inblock--flip reveal" id="inside-plans"><div class="inblock__head"><span class="inblock__index" aria-hidden="true">04</span><h3>{e(s["plansH"])}</h3><p>{e(ins["plans"]["lead"])}</p></div>
          {inside_visual('plans', lang, base, s['plansH'])}
          <div class="inblock__body"><ul class="plans">{plan_rows}</ul></div></article>
      </div>
      <p class="also reveal"><span class="also__h">{e(s["alsoH"])}</span>{also}</p>
    </div></section>'''
    story_text = [('readH', 'readP', ''), ('guideH', 'guideP', ''), ('counselH', 'counselP', ''), ('quietH', 'quietP', ''),
                  ('hoursH', 'hoursP', f'<div class="hourlist">{hours}</div>')]
    steps_html = '\n'.join(
        f'        <div class="step feature{" feature--flip" if i % 2 else ""}" id="{key}" data-step="{i}">'
        f'<div class="feature__text"><div class="eyebrow">{i + 1:02d}</div>{h2(s[hk])}<p class="reveal">{e(s[pk])}</p>{extra}</div>'
        f'<div class="reveal step__card" style="--d:.15s">{card_for(key)}</div></div>'
        for i, (key, (hk, pk, extra)) in enumerate(zip(STORY, story_text)))
    scenes_html = '\n'.join(
        f'              <div class="scene{" on" if i == 0 else ""}" data-scene="{key}">{story_media(key, lang, base) or scene_inner[key]}</div>' for i, key in enumerate(STORY))
    dots_html = ''.join(f'<li{" class=on" if i == 0 else ""}></li>' for i in range(len(STORY)))

    return f'''<!doctype html>
<html lang="{e(s["htmlLang"])}">
<head>
{head_common(lang, s["metaTitle"], s["metaDescription"], canonical, og, "index,follow,max-image-preview:large", base)}{og_head(s["metaTitle"], s["metaDescription"], canonical, og, s["ogLocale"], [SITE[l]["ogLocale"] for l in LANGS if l != lang])}<link rel="preload" href="{base}fonts/cormorant-garamond.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{base}site.css">
<script>{BOOT}</script>
<script type="application/ld+json">
{ld_json}
</script>
</head>
<body>
<a class="skip" href="#main">{e(s["skip"])}</a>
<div class="sky" aria-hidden="true"><div class="sky__disc"></div><div class="sky__veil"></div></div>

<header class="nav">
  <div class="nav__in">
    <a class="mark" href="{rel(lang, lang)}">Bible Answer{mark_local(lang)}</a>
    <nav class="nav__links" aria-label="Bible Answer">
      <a href="#ask">{e(s["navAsk"])}</a>
      <a href="#read">{e(s["navRead"])}</a>
      <a href="#guide">{e(s["navGuide"])}</a>
      <a href="#devices">{e(s["navDevices"])}</a>
      <a href="#reading-guides">{e(s["readingGuidesLabel"])}</a>
    </nav>
    <div class="nav__tools">
      <details class="langmenu"><summary aria-label="{e(ap["name"])}">{e(ap["name"])}</summary><ul>{lang_items}</ul></details>
      {theme.control(lang)}
      <a class="nav__reading" href="#reading-guides">{e(s["readingGuidesLabel"])}</a>
      {store_nav}
    </div>
  </div>
</header>

<main id="main">
  <section class="hero" aria-labelledby="h-hero">
    <div class="hero__fx" aria-hidden="true"><div class="hero__glow"></div></div>
    <div class="hero__in" id="heroIn">
      <div class="hero__copy">
      <div class="hero__identity"><img class="hero__icon" src="{base}assets/icon.png" width="64" height="64" alt=""></div>
      <h1 id="h-hero" class="split split--hero grad">{split_words('Bible Answer')}</h1>
      {local_name_line(lang)}
      <p class="hero__tagline">{e(ap["tagline"])}</p>
      <p class="hero__sub rise" style="--i:2">{e(ap["subtitle"])}</p>
      <div class="hero__cta rise" style="--i:3">
        {store}
        <a class="link" href="#ask">{e(s["seeHow"])}</a>
      </div>
      <p class="hero__devices">iPhone <span>·</span> iPad <span>·</span> Mac <span>·</span> Apple Watch</p>
      </div>
      <figure class="hero__preview">{device_product('iphone', lang, base, s['previewAlt'].format(section=ap['prompt']), priority=True)}</figure>
    </div>
    <div class="sky-caption">
      <small class="sky-credit"><a href="https://commons.wikimedia.org/wiki/File:Night_sky_at_La_Silla_(150121-22-lasilla-360-cc-fd).jpg">ESO/P. Horálek</a> · <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a> · {e(s["skyEdited"])}</small>
    </div>
    <svg class="hero__hint ico" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 9l6 6 6-6"/></svg>
  </section>

  <section class="section ask" id="ask" aria-labelledby="h-ask">
    <div class="wrap">
      {h2(ap["prompt"], "grad", "h-ask")}
      <p class="lede reveal" style="--d:.1s">{e(s["askLede"])}</p>
      <div class="demo reveal" style="--d:.15s" data-demo>
        <div class="demo__ask" aria-hidden="true">
          <div class="feelings">{featured}</div>
          <div class="good">{e(ap["goodDays"])}</div>
          <div class="pills">{warm}</div>
          <div class="composer demo__composer"><span class="demo__input"><span class="typed" style="--n:{len(query)}">{e(query)}</span><span class="caret"></span></span><span class="send"><svg class="ico" viewBox="0 0 24 24"><path d="M12 19V5"/><path d="M5 12l7-7 7 7"/></svg></span></div>
        </div>
        {answer}
      </div>
      <p class="demo__note reveal">{e(s["demoNote"])}</p>
    </div>
  </section>

  <section class="story" aria-label="Bible Answer">
    <div class="story__in">
      <div class="story__steps">
{steps_html}
      </div>
      <div class="stage" aria-hidden="true">
        <div class="phone">
          <div class="phone__glow"></div>
          {buttons_html}<div class="phone__body"><div class="phone__bezel">
            <div class="phone__screen"><i class="phone__island"></i>
{scenes_html}
            </div>
          </div></div>
        </div>
        <ol class="story__dots">{dots_html}</ol>
      </div>
    </div>
  </section>

  {moments_preview_section(lang, base)}

  {inside_html}

  {reading_guides_section(lang, base)}

  <section class="section today" id="today" aria-labelledby="h-today">
    <div class="wrap">
      {h2(s["todayH"], "", "h-today")}
      <p class="lede reveal" style="--d:.1s">{e(s["todayP"])}</p>
      {daily_previews(lang, base)}
    </div>
  </section>

  <section class="section platforms" id="devices" aria-labelledby="h-devices">
    <div class="wrap">
      {h2(s["devicesH"], "", "h-devices")}
      <div class="device-grid">{devices}</div>
    </div>
  </section>

  {mac_html}

  {screens_section(lang, base)}

  <section class="section languages" id="languages" aria-labelledby="h-langs">
    <div class="wrap">
      {h2(s["langsH"], "", "h-langs")}
      <p class="lede reveal" style="--d:.1s">{e(s["langsP"])}</p>
      <div class="lang-grid reveal" style="--d:.15s">{lang_pills}</div>
    </div>
  </section>

  <section class="section privacy" id="private" aria-labelledby="h-priv">
    <div class="wrap">
      {h2(s["privH"], "", "h-priv")}
      <div class="trio">
        <div class="reveal"><h3>{e(s["priv1T"])}</h3><p>{e(s["priv1P"])}</p></div>
        <div class="reveal" style="--d:.12s"><h3>{e(s["priv2T"])}</h3><p>{e(s["priv2P"])}</p></div>
        <div class="reveal" style="--d:.24s"><h3>{e(s["priv3T"])}</h3><p>{e(s["priv3P"])}</p></div>
      </div>
    </div>
  </section>

  <section class="section cta" aria-label="{e(s["storeText"])}">
    <div class="wrap cta__card">
      <img class="cta__icon" src="{base}assets/icon.png" width="64" height="64" alt="" loading="lazy">
      {h2(ap["tagline"], "grad")}
      <p class="reveal" style="--d:.1s">{store}</p>
    </div>
  </section>
</main>

<footer class="foot">
  {branding.footer_brand(lang, rel(lang, lang))}
  <p><a href="{'/' + build_articles.hub(lang)}" lang="{SITE[lang]['htmlLang']}">{e(s["readingGuides"])}</a><span class="dot">·</span><wbr><a href="{base}support">{e(s["footSupport"])}</a><span class="dot">·</span><wbr><a href="{base}privacy#{e(lang)}">{e(s["privacy"])}</a><span class="dot">·</span><wbr><a href="{base}terms#{e(lang)}">{e(s["terms"])}</a><span class="dot">·</span><wbr><a href="{base}press/" lang="en">Press</a><span class="dot">·</span><wbr><a href="mailto:{e(CFG["contactEmail"])}">{e(CFG["contactEmail"])}</a></p>
  <p>{foot_langs}</p>
  {foot_social}<p class="foot__fine">{e(s["creditArt"])} <a href="{base}terms#{e(lang)}">{e(s["terms"])}</a></p>
</footer>
<script src="{base}app.js" defer></script>
</body>
</html>
'''


# ------------------------------------------------------------------ /links, the page behind "link in bio"

def links_page():
    site = CFG['siteUrl'].rstrip('/')
    title, desc = 'Bible Answer — Links', 'Bible Answer: the app, and the page in your language.'
    canonical, og = site + '/links/', f'{site}/assets/og/og-en.jpg'

    def row(l):
        return (f'<li><a class="links__lang" href="../{SITE[l]["path"]}" lang="{e(SITE[l]["htmlLang"])}" hreflang="{e(SITE[l]["hreflang"])}">{e(APP[l]["name"])}</a></li>')

    follow = social_links(' class="pill"')
    follow_html = f'<p class="links__follow">{"".join(follow)}</p>' if follow else ''

    return f'''<!doctype html>
<html lang="en">
<head>
{head_common(None, title, desc, canonical, og, "noindex,follow", "../")}{og_head(title, desc, canonical, og)}<link rel="preload" href="../fonts/cormorant-garamond.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="../site.css">
<script>{BOOT}</script>
</head>
<body class="solo">
{theme.control("en")}
<div class="sky" aria-hidden="true"><div class="sky__disc"></div><div class="sky__veil"></div></div>
<main class="links" id="main">
  <img class="hero__icon" src="../assets/icon.png" width="96" height="96" alt="Bible Answer">
  <h1 class="links__title">Bible Answer</h1>
  <p class="links__tag">{e(APP["en"]["tagline"])}</p>
  <p class="links__store">{store_link("en", "../")}</p>
  <ul class="links__list">{"".join(row(l) for l in LANGS)}</ul>
  {follow_html}
  <p class="links__foot"><a href="../support">Support</a><span class="dot">·</span><wbr><a href="../privacy#en">Privacy Policy</a><span class="dot">·</span><wbr><a href="../terms#en">Terms of Use</a><span class="dot">·</span><wbr><a href="../press/">Press</a></p>
</main>
</body>
</html>
'''


# ------------------------------------------------------------------ 404 (served at any path, so every address is absolute)

def not_found():
    site = CFG['siteUrl'].rstrip('/')
    title, desc = 'Bible Answer — page not found', 'This page does not exist.'
    og = f'{site}/assets/og/og-en.jpg'
    items = ''.join(f'<li><a href="/{SITE[l]["path"]}" lang="{e(SITE[l]["htmlLang"])}">{e(APP[l]["name"])}</a></li>' for l in LANGS)
    return f'''<!doctype html>
<html lang="en">
<head>
{head_common(None, title, desc, site + "/", og, "noindex", "/")}<link rel="stylesheet" href="/site.css">
<script>{BOOT}</script>
</head>
<body class="solo">
{theme.control("en")}
<div class="sky" aria-hidden="true"><div class="sky__disc"></div><div class="sky__veil"></div></div>
<main class="links" id="main">
  <img class="hero__icon" src="/assets/icon.png" width="96" height="96" alt="Bible Answer">
  <h1 class="links__title">404</h1>
  <p class="links__tag">This page does not exist.</p>
  <ul class="links__list links__list--plain">{items}</ul>
</main>
</body>
</html>
'''


# ------------------------------------------------------------------ legal pages: the text stays, the <head> gets the site's tags

LEGAL = {'privacy': 'Bible Answer — Privacy Policy', 'terms': 'Bible Answer — Terms of Use', 'support': 'Bible Answer — Support'}
BLOCK = re.compile(r'<!-- site:head -->.*?<!-- /site:head -->\n?', re.S)


def legal_head(name, title):
    site = CFG['siteUrl'].rstrip('/')
    url = f'{site}/{name}'
    og = f'{site}/assets/og/og-en.jpg'
    desc = title
    return ('<!-- site:head -->\n'
            f'<link rel="canonical" href="{e(url)}">\n<meta name="robots" content="index,follow">\n'
            f'<link rel="alternate" type="application/rss+xml" title="Bible Answer" href="{e(site + "/feed.xml")}">\n'
            f'<meta name="apple-itunes-app" content="app-id={e(CFG["appStoreId"])}">\n{social_meta()}'
            f'{og_head(title, desc, url, og)}{icons_head("/")}{theme_script("/")}<!-- /site:head -->\n')


def write_legal():
    for name, title in LEGAL.items():
        path = ROOT / f'{name}.html'
        text = BLOCK.sub('', path.read_text('utf-8'))
        assert text.count('</head>') == 1, name
        path.write_text(text.replace('</head>', legal_head(name, title) + '</head>'), encoding='utf-8')
        print('wrote', path.name, '(head only)')


# ------------------------------------------------------------------ sitemap and robots

def sitemap(lastmod):
    site = CFG['siteUrl'].rstrip('/')
    rows = []
    stamp = f'\n    <lastmod>{lastmod}</lastmod>' if lastmod else ''
    for l in LANGS:
        alts = ''.join(f'\n    <xhtml:link rel="alternate" hreflang="{SITE[o]["hreflang"]}" href="{site}/{SITE[o]["path"]}"/>' for o in LANGS)
        alts += f'\n    <xhtml:link rel="alternate" hreflang="x-default" href="{site}/"/>'
        rows.append(f'  <url>\n    <loc>{site}/{SITE[l]["path"]}</loc>{alts}{stamp}\n  </url>')
    for name in LEGAL:
        rows.append(f'  <url>\n    <loc>{site}/{name}</loc>{stamp}\n  </url>')
    rows.append(f'  <url>\n    <loc>{site}/press/</loc>{stamp}\n  </url>')
    rows.extend(build_articles.sitemap_rows(ROOT, CFG))
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
            + '\n'.join(rows) + '\n</urlset>\n')


# ------------------------------------------------------------------ what the press page, llms.txt and the feed say (one source)

LANG_EN = {'en': 'English', 'pt': 'Portuguese (Brazil)', 'es': 'Spanish', 'ru': 'Russian', 'fr': 'French', 'fil': 'Filipino'}
BIBLE_EN = {'en': 'Berean Standard Bible', 'pt': 'Bíblia Livre (CC BY 4.0)', 'es': 'Reina-Valera 1909', 'ru': 'Synodal Translation (Синодальный перевод)',
            'fr': 'Louis Segond 1910', 'fil': 'ULB, unfoldingWord (CC BY-SA 4.0)'}
xml = lambda s: html.escape(str(s), quote=False)


def live():
    return bool(CFG.get('appLive'))


def counts():
    ins = APP['en']['inside']
    return dict(ins['counts'], plans=len(ins['plans']['items']), guide=len(ins['guide']['items']))


def one_line():
    return ('Bible Answer is a free app for iPhone, iPad, Mac and Apple Watch. Say what is on your heart and get a verse word for word, '
            'what it means and a short prayer.')


def short_text():
    return ('Bible Answer is a free Bible app for iPhone, iPad, Mac and Apple Watch, in six languages. Say what is on your heart and it answers '
            'with a verse quoted word for word, what it means and a short prayer. Around that sit the whole Bible with three readings of every verse, '
            'a guide to the story, counsel by topic, reading plans, a verse for every day and a place to be quiet. '
            'No account, no ads, no tracking.')


def long_text():
    c = counts()
    return (f'Bible Answer is a free Bible app for iPhone, iPad, Apple Watch and Mac, in English, Portuguese (Brazil), Spanish, Russian, French and Filipino. '
            'You say or type what you are going through, such as anxious, lost or grateful, and the app returns a passage quoted word for word from a '
            'public-domain or openly licensed translation, a plain explanation of what it means and a short prayer. The reflection is written with an '
            'AI model and may be incomplete or mistaken, and the app says so; the verse itself is never generated. '
            f'The app also holds the whole Bible with three readings of every verse (biblical, symbolic and application), a guide to the whole story, '
            f'advice gathered under {c["topics"]} topics, {c["plans"]} reading plans, a verse for every day on the Home Screen, Lock Screen and Apple Watch, '
            'and music and nature sounds for quiet moments. There is no account, no advertising and no analytics. '
            'Bible Answer is free; anyone who wishes to support it can leave a tip once, and nothing is locked or unlocked by it. '
            'It is made by one independent developer.')


def availability():
    return 'On the App Store' if live() else 'App Store, launching soon'


# ------------------------------------------------------------------ news: the feed and the press page read the same file

def news_items():
    path = HERE / 'news.json'
    items = json.loads(path.read_text('utf-8')) if path.exists() else []
    return sorted(items, key=lambda n: n['date'], reverse=True)


def rfc822(date):
    d = datetime.datetime.strptime(date, '%Y-%m-%d').replace(hour=9, tzinfo=datetime.timezone.utc)
    return email.utils.format_datetime(d)


def feed_xml():
    site = CFG['siteUrl'].rstrip('/')
    items = news_items()
    built = rfc822(items[0]['date'] if items else (CFG.get('lastmod') or '2026-01-01'))
    rows = ''.join(
        f'    <item>\n      <title>{xml(n["title"])}</title>\n      <link>{site}/press/#{xml(n["id"])}</link>\n'
        f'      <guid isPermaLink="false">bibleanswer.app:{xml(n["id"])}</guid>\n      <pubDate>{rfc822(n["date"])}</pubDate>\n'
        f'      <description>{xml(n["summary"])}</description>\n    </item>\n' for n in items)
    guides = [a for a in build_articles.load(ROOT) if a['lang'] == 'en']
    rows = ''.join(f'    <item>\n      <title>{xml(a["title"])}</title>\n      <link>{site}/{build_articles.path(a)}</link>\n'
                   f'      <guid isPermaLink="true">{site}/{build_articles.path(a)}</guid>\n      <pubDate>{rfc822(a["date"])}</pubDate>\n'
                   f'      <description>{xml(a["description"])}</description>\n    </item>\n' for a in guides) + rows
    built = rfc822(max([a['date'] for a in guides] + [n['date'] for n in items]))
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n  <channel>\n'
            '    <title>Bible Answer</title>\n'
            f'    <link>{site}/</link>\n    <description>Reading guides and news from Bible Answer.</description>\n'
            f'    <language>en</language>\n    <lastBuildDate>{built}</lastBuildDate>\n'
            f'    <atom:link href="{site}/feed.xml" rel="self" type="application/rss+xml"/>\n{rows}  </channel>\n</rss>\n')


# ------------------------------------------------------------------ /press

def press_page():
    site = CFG['siteUrl'].rstrip('/')
    title = 'Bible Answer — Press kit'
    desc = 'Facts, descriptions and pictures for writing about Bible Answer, the free Bible app for iPhone, iPad, Mac and Apple Watch.'
    canonical, og = site + '/press/', f'{site}/assets/og/og-en.jpg'
    c = counts()

    def copybox(ident, label, text):
        return (f'<div class="copybox"><div class="copybox__head"><h3>{e(label)}</h3>'
                f'<button type="button" class="copybtn" data-copy="{ident}" data-done="Copied" hidden>Copy</button></div>'
                f'<p id="{ident}">{e(text)}</p></div>')

    texts = ''.join(f'<li><span>{e(LANG_EN[l])}</span><b>{e(BIBLE_EN[l])}</b></li>' for l in LANGS)
    facts = [
        ('Name', 'Bible Answer (two words)'),
        ('What it is', 'A free Bible app: say what is on your heart, get a verse word for word, what it means and a short prayer'),
        ('Platforms', f'iPhone, iPad, Apple Watch and Mac. Requires {CFG.get("requirements", "")}'),
        ('Languages', ', '.join(LANG_EN[l] for l in LANGS)),
        ('Price', 'Free. An optional one-time tip supports the app; nothing is locked or unlocked by it'),
        ('Privacy', 'No account, no advertising, no analytics, no tracking across apps or websites'),
        ('How answers are made', 'The verse is quoted from the translation unchanged. The reflection and the prayer are written with an AI model through the '
                                 "app's own server, and the app says they may be incomplete or mistaken"),
        ('Inside', f'The whole Bible with three readings of every verse; a guide of {c["guide"]} parts; {c["eras"]} eras, {c["people"]} people, {c["terms"]} words and {c["places"]} places explained; '
                   f'advice under {c["topics"]} topics; {c["plans"]} reading plans; a verse for every day; prayers for the hour; music and sounds of nature'),
        ('Version', '1.0'),
        ('Availability', availability()),
        ('Made by', 'One independent developer'),
    ]
    facts_html = ''.join(f'<div><dt>{e(k)}</dt><dd>{e(v)}</dd></div>' for k, v in facts)

    pics = [f'<figure class="pic"><img src="../assets/press/bible-answer-icon-1024.png" width="160" height="160" alt="The Bible Answer app icon" loading="lazy">'
            '<figcaption><b>App icon</b><span>1024 × 1024 PNG</span><a href="../assets/press/bible-answer-icon-1024.png" download>Download</a></figcaption></figure>',
            f'<figure class="pic pic--wide"><img src="../assets/og/og-en.jpg" width="320" height="168" alt="Bible Answer: God’s Word for every moment" loading="lazy">'
            '<figcaption><b>Link preview</b><span>1200 × 630 JPG</span><a href="../assets/og/og-en.jpg" download>Download</a></figcaption></figure>']
    shots = [f'assets/screens/iphone/en/{n}.webp' for n in range(1, SHOTS['iphone'] + 1) if have(f'assets/screens/iphone/en/{n}.webp')]
    shots_html = ''.join(f'<figure class="pic pic--shot"><img src="../{p}" width="160" height="347" alt="" loading="lazy">'
                         f'<figcaption><b>iPhone screenshot {i}</b><a href="../{p}" download>Download</a></figcaption></figure>' for i, p in enumerate(shots, 1))
    shots_note = ('' if shots else '<p class="doc__note">Screenshots: the official set will be on the App Store page. Real screenshots in every language will be added here, '
                                    'and anything else you need, such as a screenshot in your language, you can ask for below.</p>')

    news = ''.join(f'<li id="{e(n["id"])}"><time datetime="{e(n["date"])}">{e(n["date"])}</time><b>{e(n["title"])}</b><span>{e(n["summary"])}</span></li>' for n in news_items())
    soc = social_links()
    soc_html = f'<p class="doc__social">{" ".join(soc)}</p>' if soc else ''
    cta = (f'<a class="btn btn--gold btn--small" href="{e(CFG["appStoreUrl"])}">Download on the App Store</a>' if live()
           else f'<a class="btn btn--gold btn--small" href="mailto:{e(CFG["contactEmail"])}">Contact</a>')

    return f'''<!doctype html>
<html lang="en">
<head>
{head_common(None, title, desc, canonical, og, "index,follow,max-image-preview:large", "../")}{og_head(title, desc, canonical, og)}<link rel="preload" href="../fonts/cormorant-garamond.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="../site.css">
<script>{BOOT}</script>
</head>
<body>
<a class="skip" href="#main">Skip to the content</a>
<div class="sky" aria-hidden="true"><div class="sky__disc"></div><div class="sky__veil"></div></div>

<header class="nav">
  <div class="nav__in">
    <a class="mark" href="../">Bible Answer</a>
    <nav class="nav__links" aria-label="Press kit">
      <a href="#about">About</a>
      <a href="#facts">Facts</a>
      <a href="#pictures">Pictures</a>
      <a href="#news">News</a>
      <a href="#contact">Contact</a>
    </nav>
    <div class="nav__tools">{theme.control("en")}{cta}</div>
  </div>
</header>

<main class="doc" id="main">
  <div class="doc__in">
    <p class="doc__eyebrow">Press kit</p>
    <h1>Writing about Bible Answer</h1>
    <p class="doc__lede">Descriptions you can copy, the facts, and the app icon. Everything here is for editorial use. This page is in English; the app and the site are in six languages.</p>

    <section id="about" aria-labelledby="h-about">
      <h2 id="h-about">In a few words</h2>
      {copybox("bp-line", "One line", one_line())}
      {copybox("bp-short", "Short", short_text())}
      {copybox("bp-long", "Long", long_text())}
    </section>

    <section id="facts" aria-labelledby="h-facts">
      <h2 id="h-facts">Facts</h2>
      <dl class="facts">{facts_html}</dl>
      <h3 class="doc__sub">Bible texts, one for each language</h3>
      <ul class="texts">{texts}</ul>
      <p class="doc__note">Verses are quoted word for word from these translations. Please keep them unaltered and name the translation when you quote one.</p>
    </section>

    <section id="pictures" aria-labelledby="h-pics">
      <h2 id="h-pics">Pictures</h2>
      <div class="pics">{"".join(pics)}{shots_html}</div>
      {shots_note}
      <h3 class="doc__sub">Using the name and the icon</h3>
      <p>Write the name as two words, Bible Answer. Use the icon as it is: no recolouring, cropping or effects. For the App Store badge, use Apple’s own artwork and follow
      <a href="https://developer.apple.com/app-store/marketing/guidelines/" rel="noopener" target="_blank">Apple’s marketing guidelines</a>.</p>
    </section>

    <section id="news" aria-labelledby="h-news">
      <h2 id="h-news">News</h2>
      <ul class="news">{news}</ul>
      <p><a href="{site}/feed.xml" type="application/rss+xml">RSS feed</a></p>
    </section>

    <section id="contact" aria-labelledby="h-contact">
      <h2 id="h-contact">Contact</h2>
      <p>For an interview, a number, a quote or a screenshot in your language, write to <a href="mailto:{e(CFG["contactEmail"])}">{e(CFG["contactEmail"])}</a>.</p>
      {soc_html}
    </section>
  </div>
</main>

<footer class="foot">
  <p><a href="../support">Support</a><span class="dot">·</span><wbr><a href="../privacy#en">Privacy Policy</a><span class="dot">·</span><wbr><a href="../terms#en">Terms of Use</a><span class="dot">·</span><wbr><a href="../">Bible Answer</a></p>
</footer>
<script src="../app.js" defer></script>
</body>
</html>
'''


# ------------------------------------------------------------------ llms.txt (short) and llms-full.txt (everything), for AI assistants

def llms_facts():
    return [
        'Free. An optional one-time tip supports the app; nothing is locked or unlocked by it.',
        'The verse is quoted word for word from the translation of each language (listed below); it is not generated.',
        'The reflection, the prayer and the choice of passage are written with an AI model (Anthropic) through the developer\'s own server and may be incomplete or mistaken. The app says so.',
        'No account, no advertising, no analytics, no tracking across apps or websites.',
        f'Platforms: iPhone, iPad, Apple Watch and Mac. Requires {CFG.get("requirements", "")}.',
        'Languages: ' + ', '.join(LANG_EN[l] for l in LANGS) + '.',
        'Availability: ' + ('on the App Store.' if live() else 'launching soon on the App Store (the App Store page opens at release).'),
    ]


def llms_txt():
    site = CFG['siteUrl'].rstrip('/')
    out = ['# Bible Answer', '', f'> {one_line()} Available in ' + ', '.join(LANG_EN[l] for l in LANGS[:-1]) + f' and {LANG_EN[LANGS[-1]]}. No account, no ads, no analytics.', '',
           'Facts to get right when you describe it:', ''] + [f'- {x}' for x in llms_facts()] + ['', '## The app', '']
    out.append(f'- [Bible Answer on the App Store]({CFG["appStoreUrl"]}): ' + ('the download page.' if live() else 'the download page; it opens when the app is released.'))
    out += ['', '## The website, one page per language', '']
    out += [f'- [{LANG_EN[l] if l == "en" else LANG_EN[l] + " – " + APP[l]["name"]}]({site}/{SITE[l]["path"]}): {SITE[l]["metaDescription"]}' for l in LANGS]
    out += ['', '## About and policies', '',
            f'- [Press kit]({site}/press/): descriptions to copy, facts, the app icon, contact.',
            f'- [Privacy Policy]({site}/privacy#en): what leaves the device and what does not.',
            f'- [Terms of Use]({site}/terms#en)',
            f'- [Support]({site}/support)',
            '', '## Optional', '',
            f'- [Full description for language models]({site}/llms-full.txt): what is inside, how answers are made, privacy, questions and answers.',
            f'- [News feed]({site}/feed.xml)', '']
    return '\n'.join(out)


def llms_full():
    site = CFG['siteUrl'].rstrip('/')
    en = APP['en']; ins = en['inside']; c = counts()
    S = SITE['en']
    out = ['# Bible Answer: full description', '', f'> {one_line()}', '',
           'This file is written for language models and for anyone who wants every fact in one place. The same facts are on https://bibleanswer.app/ and https://bibleanswer.app/press/.', '',
           '## What it is', '',
           short_text(), '',
           '## How it works', '',
           '1. Say or type what is on your heart, or tap a feeling (anxious, lost, grateful and others).',
           '2. You get a passage quoted word for word, a plain explanation of what it means for you, a short prayer, and the context of the passage.',
           '3. Read on: the whole Bible, three readings of every verse, a guide, advice by topic, reading plans.', '',
           '## What is inside', '', f'### {ins["guide"]["title"]}', '', ins['guide']['lead'], '']
    out += [f'- {i["title"]}: {i["summary"]}' for i in ins['guide']['items']]
    out += ['', '### Three readings of every verse', '']
    out += [f'- {x["name"]}: {x["caption"]}' for x in ins['lenses']]
    out += ['', f'### Advice by topic ({c["topics"]} topics)', '', ins['advice']['lead'], '', ', '.join(ins['advice']['topics']) + '.', '', '### Reading plans', '']
    out += [f'- {x["title"]} ({x["days"]} days): {x["summary"]}' for x in ins['plans']['items']]
    out += ['', '### Also', '',
            f'- Explained in the guide: {c["eras"]} eras, {c["people"]} people, {c["terms"]} words and {c["places"]} places.',
            f'- {S["todayH"]} {S["todayP"]}',
            f'- {S["quietH"]} {S["quietP"]}',
            f'- {S["hoursH"]} {", ".join(en["hours"])}.',
            f'- {S["alsoSearch"]}; verse cards to share.', '',
            '## Platforms', '',
            f'- iPhone: {S["iphoneP"]}', f'- iPad: {S["ipadP"]}', f'- Apple Watch: {S["watchP"]}', f'- Mac: {S["macSecP"]}',
            f'- Requires {CFG.get("requirements", "")}.', '',
            '## Languages and Bible texts', '', 'The app and the website are in six languages. Each uses one Bible translation, quoted unchanged:', '']
    out += [f'- {LANG_EN[l]}: {BIBLE_EN[l]}' for l in LANGS]
    out += ['', '## Privacy and data', '',
            '- No account. There is nothing to sign up for.',
            '- No advertising, no analytics, no tracking across apps or websites.',
            '- When you ask a question, the text is sent to the developer\'s server, which passes it to an AI model provider (Anthropic) to write the reflection. It is not linked to a name, an email, a device identifier or an account. The server does not store the questions.',
            '- Chapters of the Bible are fetched from a public Scripture service (bible.helloao.org) and kept on the device.',
            '- A tip is validated by RevenueCat with an anonymous identifier made by the app.',
            f'- Full text: {site}/privacy#en', '',
            '## Questions and answers', '',
            '**Is Bible Answer free?** Yes. If you wish to support it, you can leave a tip, once. Nothing is locked or unlocked by it.', '',
            '**Does it need an account?** No.', '',
            '**Are the verses written by AI?** No. Each verse is quoted word for word from the translation. The reflection, the prayer and the choice of passage are written with an AI model and may be incomplete or mistaken; the app says so.', '',
            '**Which devices?** iPhone, iPad, Apple Watch and Mac.', '',
            '**Which languages?** ' + ', '.join(LANG_EN[l] for l in LANGS) + '.', '',
            '**Who makes it?** One independent developer.', '',
            f'**Where can I get it?** {"On the App Store: " + CFG["appStoreUrl"] if live() else "It is launching soon on the App Store; the page " + CFG["appStoreUrl"] + " opens at release."}', '',
            '## Links', '',
            f'- Website: {site}/', f'- Press kit: {site}/press/', f'- Support: {site}/support', f'- Contact: {CFG["contactEmail"]}', '']
    return '\n'.join(out)


def write_extras():
    (ROOT / 'press').mkdir(exist_ok=True)
    (ROOT / 'press' / 'index.html').write_text(press_page(), encoding='utf-8')
    (ROOT / 'feed.xml').write_text(feed_xml(), encoding='utf-8')
    (ROOT / 'llms.txt').write_text(llms_txt(), encoding='utf-8')
    (ROOT / 'llms-full.txt').write_text(llms_full(), encoding='utf-8')
    key = CFG.get('indexNowKey')
    if key:
        (ROOT / f'{key}.txt').write_text(key, encoding='utf-8')
    print('wrote press/index.html, feed.xml, llms.txt, llms-full.txt' + (f', {key}.txt' if key else ''))


def version_stylesheets():
    """Refresh cached CSS when its content changes."""
    versions = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()[:12]
                for name in ('site.css', 'articles.css', 'style.css')}
    runtime_version = hashlib.sha256((ROOT / 'app.js').read_bytes()).hexdigest()[:12]
    runtime_pattern = re.compile(r'src="([^"?]*?)app\.js(?:\?[^" ]*)?"')
    pattern = re.compile(r'href="([^"?]*?)(site\.css|articles\.css|style\.css)(?:\?[^" ]*)?"')
    for page in ROOT.rglob('*.html'):
        source = page.read_text('utf-8')
        updated = pattern.sub(lambda m: f'href="{m[1]}{m[2]}?v={versions[m[2]]}"', source)
        updated = runtime_pattern.sub(lambda m: f'src="{m[1]}app.js?v={runtime_version}"', updated)
        if updated != source:
            page.write_text(updated, encoding='utf-8')


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--site-url', help='override siteUrl from tools/config.json (for a trial copy)')
    p.add_argument('--lastmod', default=CFG.get('lastmod', ''), help='date for sitemap.xml (default: "lastmod" in config.json; none if empty)')
    a = p.parse_args()
    if a.site_url:
        CFG['siteUrl'] = a.site_url

    for lang in LANGS:
        out = ROOT / SITE[lang]['path'] / 'index.html'
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(home(lang), encoding='utf-8')
        print('wrote', out.relative_to(ROOT))
    (ROOT / 'links').mkdir(exist_ok=True)
    (ROOT / 'links' / 'index.html').write_text(links_page(), encoding='utf-8')
    (ROOT / '404.html').write_text(not_found(), encoding='utf-8')
    print('wrote links/index.html, 404.html')
    write_legal()
    write_extras()
    build_articles.write(ROOT, CFG, head_common, og_head)
    version_stylesheets()
    (ROOT / 'sitemap.xml').write_text(sitemap(a.lastmod), encoding='utf-8')
    (ROOT / 'robots.txt').write_text(f'User-agent: *\nAllow: /\n\nSitemap: {CFG["siteUrl"].rstrip("/")}/sitemap.xml\n', encoding='utf-8')
    print('wrote sitemap.xml, robots.txt')

    empty = [f'{d}/{l}/{n}' for l in LANGS for d, k in SHOTS.items() for n in range(1, k + 1) if not shot_file(d, l, n)]
    if empty:
        print(f'note: {len(empty)} missing screenshot slots are omitted (assets/screens/README.md says where they go)')
    if not any(have(f'assets/badges/app-store-{l}.svg') for l in LANGS):
        print('note: no Apple badge files in assets/badges/ - the pages show a plain "Download on the App Store" button')


if __name__ == '__main__':
    main()
