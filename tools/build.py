#!/usr/bin/env python3
"""Builds the Bible Answer website (bibleanswer.app) from the files in tools/.

    python3 tools/build.py                       # uses tools/config.json
    python3 tools/build.py --site-url https://example.test    # for a trial copy elsewhere

It writes: index.html and <lang>/index.html for the six languages, links/index.html, 404.html,
sitemap.xml, robots.txt, and the <head> block of privacy.html, terms.html and support.html
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
import argparse, base64, datetime, hashlib, html, json, pathlib, re

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
CFG = json.loads((HERE / 'config.json').read_text('utf-8'))
APP = json.loads((HERE / 'app-strings.json').read_text('utf-8'))
SITE = json.loads((HERE / 'site-strings.json').read_text('utf-8'))
LANGS = ['en', 'pt', 'es', 'ru', 'fr', 'fil']

FEATURED = [0, 13, 5, 1, 6, 3]     # the six feelings the app shows first
POSITIVE = [14, 15, 16, 17, 18]    # "with a thankful heart"
ICONS = ['anxious', 'overwhelmed', 'selfworth', 'lost', 'courage', 'future', 'exhausted', 'forgiveness',
         'morning', 'anger', 'guilt', 'trust', 'money', 'lonely', 'gratitude', 'joy', 'praise', 'goodnews', 'peace']
GUIDE_ICONS = ['book', 'path', 'era', 'person', 'word', 'map', 'thread']    # order of site-strings guideChips
DEMO_FEELING = 0                   # "I'm anxious and I can't settle." -> Philippians 4:6-7
SHOTS = {'iphone': 4, 'ipad': 2}   # screenshot slots per language (see assets/screens/README.md)
SHOT_SIZE = {'iphone': (1320, 2868), 'ipad': (2064, 2752)}

BOOT = "document.documentElement.classList.add('js')"   # tells the stylesheet scripts run, so reveal-on-scroll may hide things
BOOT_HASH = 'sha256-' + base64.b64encode(hashlib.sha256(BOOT.encode()).digest()).decode()
CSP = (f"default-src 'none'; script-src 'self' '{BOOT_HASH}'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; "
       "font-src 'self'; connect-src 'none'; base-uri 'none'; form-action 'none'")

e = lambda s: html.escape(str(s), quote=True)


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


ART = {
    'iphone': '<svg viewBox="0 0 120 90" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><rect x="40" y="8" width="40" height="74" rx="10"/><path d="M52 15h16" opacity=".5"/><path d="M48 32h24M48 40h24M48 48h16" opacity=".5"/></svg>',
    'ipad': '<svg viewBox="0 0 120 90" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><rect x="20" y="10" width="80" height="70" rx="9"/><path d="M33 28h30M33 36h50M33 44h42M33 52h26" opacity=".5"/><path d="M60 72h.01" stroke-width="2.4"/></svg>',
    'watch': '<svg viewBox="0 0 120 90" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><rect x="38" y="12" width="44" height="66" rx="13"/><path d="M46 12l3-9h22l3 9M46 78l3 9h22l3-9" opacity=".6"/><circle cx="60" cy="45" r="14" opacity=".55"/><path d="M60 31a14 14 0 0 1 14 14" stroke-width="2.4"/><path d="M56 45h8M60 41v8" opacity=".9"/></svg>',
    'mac': '<svg viewBox="0 0 120 90" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><rect x="22" y="14" width="76" height="46" rx="5"/><path d="M12 68h96l-6 8H18z"/><path d="M34 30h30M34 38h44" opacity=".5"/></svg>',
}


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
    return f'<meta name="p:domain_verify" content="{e(CFG["pinterestVerify"])}">\n' if CFG.get('pinterestVerify') else ''


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


def screens_section(lang, base):
    s = SITE[lang]
    found = {d: [shot_file(d, lang, n) for n in range(1, k + 1)] for d, k in SHOTS.items()}
    if not CFG.get('showScreenshotSlots', True) and not any(any(v) for v in found.values()):
        return ''
    names = {'iphone': 'iPhone', 'ipad': 'iPad'}
    rows = []
    for device, files in found.items():
        w, h = SHOT_SIZE[device]
        figs = []
        for n, path in enumerate(files, 1):
            if path:
                alt = s['shotAlt'].format(device=names[device], n=n)
                figs.append(f'<figure class="shot shot--{device} reveal" style="--d:{(n - 1) * 0.08:.2f}s"><img src="{base}{path}" width="{w}" height="{h}" loading="lazy" decoding="async" alt="{e(alt)}"></figure>')
            else:
                figs.append(f'<figure class="shot shot--{device} reveal" style="--d:{(n - 1) * 0.08:.2f}s" aria-hidden="true"><div class="shot__ph"><img src="{base}assets/icon.png" width="64" height="64" alt=""></div></figure>')
        rows.append(f'<div class="shots shots--{device}">{"".join(figs)}</div>')
    return (f'<section class="section screens" id="screens" aria-labelledby="h-screens"><div class="wrap">'
            f'<h2 id="h-screens" class="reveal">{e(s["screensH"])}</h2>{"".join(rows)}</div></section>')


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
            '<meta name="color-scheme" content="dark light">\n<meta name="theme-color" content="#0F1628">\n'
            f'<meta name="apple-itunes-app" content="app-id={e(CFG["appStoreId"])}">\n{social_meta()}{extra}{icons_head(base)}')


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
        '@type': 'SoftwareApplication', '@id': site + '/#app', 'name': 'Bible Answer', 'description': s['metaDescription'],
        'applicationCategory': 'ReferenceApplication', 'operatingSystem': 'iOS', 'url': canonical, 'image': og,
        'inLanguage': [SITE[l]['hreflang'] for l in LANGS], 'downloadUrl': CFG['appStoreUrl'],
        'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'USD'},
    }
    if any(shots):
        ld_app['screenshot'] = [f'{site}/{p}' for p in shots if p]
    ld = {'@context': 'https://schema.org', '@graph': [
        {'@type': 'WebSite', '@id': site + '/#site', 'name': 'Bible Answer', 'url': site + '/', 'inLanguage': s['hreflang']}, ld_app]}
    ld_json = json.dumps(ld, ensure_ascii=False, indent=1).replace('</', '<\\/')

    current = ' aria-current="true"'
    lang_items = ''.join(
        f'<li><a href="{rel(lang, l)}" lang="{e(SITE[l]["htmlLang"])}" hreflang="{e(SITE[l]["hreflang"])}"{current if l == lang else ""}>{e(APP[l]["name"])}</a></li>' for l in LANGS)
    lang_pills = ''.join(
        f'<a class="pill pill--lang" href="{rel(lang, l)}" lang="{e(SITE[l]["htmlLang"])}" hreflang="{e(SITE[l]["hreflang"])}"{current if l == lang else ""}>{e(APP[l]["name"])}</a>' for l in LANGS)
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
            <p class="fine part" style="--i:10">{e(s["fine"])} <a href="{base}terms#{e(lang)}">{e(s["terms"])}</a></p>
          </div>
        </div>
      </article>'''

    lens = ''.join(f'<span{" class=on" if i == 0 else ""}>{e(t)}</span>' for i, t in enumerate(ap['lens']))
    guide_chips = ''.join(f'<div class="chip-sm">{gicon(GUIDE_ICONS[i], base)}<span>{e(t)}</span></div>' for i, t in enumerate(s['guideChips']))
    topics = ''.join(f'<div class="topic"><b></b><span>{e(t)}</span></div>' for t in ap['topics'])
    hours = ''.join(f'<span class="pill">{e(t)}</span>' for t in ap['hours'])
    devices = ''.join(
        f'<article class="device{" device--soon" if k == "mac" else ""} reveal" style="--d:{d}s"><div class="device__art" aria-hidden="true">{ART[k]}</div>'
        f'<h3>{t}{(" <span class=soon>" + e(s["soon"]) + "</span>") if k == "mac" else ""}</h3><p>{e(s[k + "P"])}</p></article>'
        for d, (k, t) in zip((0, .1, .2, .3), (('iphone', 'iPhone'), ('ipad', 'iPad'), ('watch', 'Apple Watch'), ('mac', 'Mac'))))

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
<div class="sky" aria-hidden="true"><div class="sky__img"></div><div class="stars" id="stars"></div><div class="sky__veil"></div></div>

<header class="nav">
  <div class="nav__in">
    <a class="mark" href="{rel(lang, lang)}">Bible Answer</a>
    <nav class="nav__links" aria-label="Bible Answer">
      <a href="#ask">{e(s["navAsk"])}</a>
      <a href="#read">{e(s["navRead"])}</a>
      <a href="#guide">{e(s["navGuide"])}</a>
      <a href="#devices">{e(s["navDevices"])}</a>
      <a href="#private">{e(s["navPrivacy"])}</a>
    </nav>
    <div class="nav__tools">
      <details class="langmenu"><summary aria-label="{e(ap["name"])}">{e(ap["name"])}</summary><ul>{lang_items}</ul></details>
      {store_nav}
    </div>
  </div>
</header>

<main id="main">
  <section class="hero" aria-labelledby="h-hero">
    <div class="hero__in" id="heroIn">
      <img class="hero__icon rise" style="--i:0" src="{base}assets/icon.png" width="96" height="96" alt="Bible Answer">
      <h1 id="h-hero" class="rise" style="--i:1">{e(ap["tagline"])}</h1>
      <p class="hero__sub rise" style="--i:2">{e(ap["subtitle"])}</p>
      <div class="hero__cta rise" style="--i:3">
        {store}
        <a class="link" href="#ask">{e(s["seeHow"])}</a>
      </div>
    </div>
    <svg class="hero__hint ico" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 9l6 6 6-6"/></svg>
  </section>

  <section class="section ask" id="ask" aria-labelledby="h-ask">
    <div class="wrap">
      <h2 id="h-ask" class="reveal">{e(ap["prompt"])}</h2>
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

  <section class="section" id="read" aria-labelledby="h-read">
    <div class="wrap">
      <div class="feature">
        <div class="feature__text reveal">
          <div class="eyebrow">{e(s["navRead"])}</div>
          <h2 id="h-read">{e(s["readH"])}</h2>
          <p>{e(s["readP"])}</p>
        </div>
        <div class="reveal" style="--d:.15s">
          <div class="card reader" data-parallax aria-hidden="true">
            <span class="skl skl--head"></span>
            <span class="skl"><b></b></span><span class="skl" style="width:96%"></span><span class="skl" style="width:88%"></span>
            <span class="skl" style="margin-top:22px"><b></b></span><span class="skl" style="width:92%"></span><span class="skl" style="width:64%"></span>
            <div class="sheet"><div class="lens">{lens}</div><span class="skl" style="margin-top:16px"></span><span class="skl" style="width:82%;margin-top:9px"></span></div>
          </div>
        </div>
      </div>

      <div class="feature feature--flip" id="guide">
        <div class="feature__text reveal">
          <div class="eyebrow">{e(s["navGuide"])}</div>
          <h2>{e(s["guideH"])}</h2>
          <p>{e(s["guideP"])}</p>
        </div>
        <div class="reveal" style="--d:.15s">
          <div class="card guidecard" data-parallax aria-hidden="true">
            <img class="guidecard__img" src="{base}assets/plates/plate-timeline.webp" width="900" height="494" alt="" loading="lazy" decoding="async">
            <div class="chipgrid">{guide_chips}</div>
          </div>
        </div>
      </div>

      <div class="feature" id="counsel">
        <div class="feature__text reveal">
          <h2>{e(s["counselH"])}</h2>
          <p>{e(s["counselP"])}</p>
        </div>
        <div class="reveal" style="--d:.15s">
          <div class="card topicscard" data-parallax aria-hidden="true"><div class="topics">{topics}</div></div>
        </div>
      </div>

      <div class="feature feature--flip" id="quiet">
        <div class="feature__text reveal">
          <h2>{e(s["quietH"])}</h2>
          <p>{e(s["quietP"])}</p>
        </div>
        <div class="reveal" style="--d:.15s">
          <div class="card player" data-parallax aria-hidden="true">
            <div class="player__img" style="background-image:url({base}assets/plates/plate-galilee.webp)"></div><div class="player__veil"></div>
            <div class="play"><svg viewBox="0 0 24 24"><path d="M8 5.5v13l11-6.5z"/></svg></div>
            <div class="eq"><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i></div>
            <div class="bar"><i></i></div>
          </div>
        </div>
      </div>

      <div class="feature" id="hours">
        <div class="feature__text reveal">
          <h2>{e(s["hoursH"])}</h2>
          <p>{e(s["hoursP"])}</p>
          <div class="hourlist">{hours}</div>
        </div>
        <div class="reveal" style="--d:.15s">
          <div class="card platecard" data-parallax aria-hidden="true">
            <img src="{base}assets/plates/plate-hours.webp" width="520" height="834" alt="" loading="lazy" decoding="async">
          </div>
        </div>
      </div>
    </div>
  </section>

  <section class="section today" id="today" aria-labelledby="h-today">
    <div class="wrap">
      <h2 id="h-today" class="reveal">{e(s["todayH"])}</h2>
      <p class="lede reveal" style="--d:.1s">{e(s["todayP"])}</p>
      <div class="mini-grid" aria-hidden="true">
        <div class="mini mini--widget reveal"><span class="label">{e(ap["tagline"])}</span><span class="skl"></span><span class="skl" style="width:84%"></span><span class="skl" style="width:62%"></span></div>
        <div class="mini mini--lock reveal" style="--d:.1s"><span class="clock">9:41</span><span class="skl" style="width:70%"></span><span class="skl" style="width:50%"></span></div>
        <div class="mini mini--watch reveal" style="--d:.2s"><span class="ring"></span>{icon("peace", base)}</div>
      </div>
    </div>
  </section>

  <section class="section platforms" id="devices" aria-labelledby="h-devices">
    <div class="wrap">
      <h2 id="h-devices" class="reveal">{e(s["devicesH"])}</h2>
      <div class="device-grid">{devices}</div>
    </div>
  </section>

  {screens_section(lang, base)}

  <section class="section languages" id="languages" aria-labelledby="h-langs">
    <div class="wrap">
      <h2 id="h-langs" class="reveal">{e(s["langsH"])}</h2>
      <p class="lede reveal" style="--d:.1s">{e(s["langsP"])}</p>
      <div class="lang-grid reveal" style="--d:.15s">{lang_pills}</div>
    </div>
  </section>

  <section class="section privacy" id="private" aria-labelledby="h-priv">
    <div class="wrap">
      <h2 id="h-priv" class="reveal">{e(s["privH"])}</h2>
      <div class="trio">
        <div class="reveal"><h3>{e(s["priv1T"])}</h3><p>{e(s["priv1P"])}</p></div>
        <div class="reveal" style="--d:.12s"><h3>{e(s["priv2T"])}</h3><p>{e(s["priv2P"])}</p></div>
        <div class="reveal" style="--d:.24s"><h3>{e(s["priv3T"])}</h3><p>{e(s["priv3P"])}</p></div>
      </div>
    </div>
  </section>

  <section class="section cta" aria-label="{e(s["storeText"])}">
    <div class="wrap">
      <h2 class="reveal">{e(ap["tagline"])}</h2>
      <p class="reveal" style="--d:.1s">{store}</p>
    </div>
  </section>
</main>

<footer class="foot">
  <p><a href="{base}support">{e(s["footSupport"])}</a><span class="dot">·</span><wbr><a href="{base}privacy#{e(lang)}">{e(s["privacy"])}</a><span class="dot">·</span><wbr><a href="{base}terms#{e(lang)}">{e(s["terms"])}</a><span class="dot">·</span><wbr><a href="mailto:{e(CFG["contactEmail"])}">{e(CFG["contactEmail"])}</a></p>
  <p>{foot_langs}</p>
  <p class="foot__fine">{e(s["creditArt"])} <a href="{base}terms#{e(lang)}">{e(s["terms"])}</a></p>
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
    handles = {h['lang']: h for h in CFG['social']}

    def row(l):
        h = handles.get(l, {})
        handle = e(h.get('handle', ''))
        social = (f'<a class="links__handle" href="{e(h["url"])}" rel="me noopener">{handle}</a>' if h.get('url') else f'<span class="links__handle">{handle}</span>') if handle else ''
        return (f'<li><a class="links__lang" href="../{SITE[l]["path"]}" lang="{e(SITE[l]["htmlLang"])}" hreflang="{e(SITE[l]["hreflang"])}">{e(APP[l]["name"])}</a>{social}</li>')

    return f'''<!doctype html>
<html lang="en">
<head>
{head_common(None, title, desc, canonical, og, "noindex,follow", "../")}{og_head(title, desc, canonical, og)}<link rel="preload" href="../fonts/cormorant-garamond.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="../site.css">
<script>{BOOT}</script>
</head>
<body class="solo">
<div class="sky" aria-hidden="true"><div class="sky__img"></div><div class="sky__veil"></div></div>
<main class="links" id="main">
  <img class="hero__icon" src="../assets/icon.png" width="96" height="96" alt="Bible Answer">
  <h1 class="links__title">Bible Answer</h1>
  <p class="links__tag">{e(APP["en"]["tagline"])}</p>
  <p class="links__store">{store_link("en", "../")}</p>
  <ul class="links__list">{"".join(row(l) for l in LANGS)}</ul>
  <p class="links__foot"><a href="../support">Support</a><span class="dot">·</span><wbr><a href="../privacy#en">Privacy Policy</a><span class="dot">·</span><wbr><a href="../terms#en">Terms of Use</a></p>
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
<div class="sky" aria-hidden="true"><div class="sky__img"></div><div class="sky__veil"></div></div>
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
            f'<meta name="apple-itunes-app" content="app-id={e(CFG["appStoreId"])}">\n{social_meta()}'
            f'{og_head(title, desc, url, og)}{icons_head("/")}<!-- /site:head -->\n')


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
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
            + '\n'.join(rows) + '\n</urlset>\n')


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
    (ROOT / 'sitemap.xml').write_text(sitemap(a.lastmod), encoding='utf-8')
    (ROOT / 'robots.txt').write_text(f'User-agent: *\nAllow: /\n\nSitemap: {CFG["siteUrl"].rstrip("/")}/sitemap.xml\n', encoding='utf-8')
    print('wrote sitemap.xml, robots.txt')

    empty = [f'{d}/{l}/{n}' for l in LANGS for d, k in SHOTS.items() for n in range(1, k + 1) if not shot_file(d, l, n)]
    if empty:
        print(f'note: {len(empty)} screenshot slots are empty (assets/screens/README.md says where they go)')
    if not any(have(f'assets/badges/app-store-{l}.svg') for l in LANGS):
        print('note: no Apple badge files in assets/badges/ - the pages show a plain "Download on the App Store" button')


if __name__ == '__main__':
    main()
