"""First Drop: one real product, six languages, orders via existing Instagram profiles.

No checkout, stock counter, payment collection or messages are generated here.
"""
import hashlib, html, json
from pathlib import Path
import theme, branding

LANGS=('en','ru','es','pt','fr','fil')
CODES={'en':'en','ru':'ru','es':'es','pt':'pt-BR','fr':'fr','fil':'fil'}
HANDLES={'en':'bibleanswerapp','ru':'bibleanswerapp_ru','es':'bibleanswerapp_es','pt':'bibleanswerapp_br','fr':'bibleanswerapp_fr','fil':'bibleanswerapp_ph'}
COPY=json.loads((Path(__file__).parent/'shop-copy.json').read_text('utf-8'))
ORIGINAL_PHOTOS=('folded','front','back','worn','front-daylight','neck-detail')
PHOTOS=('front-daylight','back','folded','neck-detail','petronas')
EDITORIAL_PHOTOS=('hanger','embroidery-macro','window','friends','street-back')
def alt(c,name):
    if name == 'petronas':
        return c['cityAlt']
    return c['photoAlts'][name] if name in c.get('photoAlts',{}) else c['alts'][ORIGINAL_PHOTOS.index(name)]
FILE={'neck-detail':'neck-detail-v','back':'back-bridge'}
DIMENSIONS={'front-daylight': (1672, 941), 'back': (1672, 941), 'folded': (900, 1488), 'neck-detail': (941, 1672), 'petronas': (1800, 3200), 'hanger': (1664, 2080), 'embroidery-macro': (2048, 2048), 'window': (1152, 2048), 'friends': (1664, 2080), 'street-back': (1664, 2080)}
def file(name):return FILE.get(name,name)
def candidates(name):
    real=DIMENSIONS[name][0]
    widths={}
    for target in (640,1200,1800):
        widths.setdefault(min(target,real),target)
    return ', '.join(f'{image(name,target)} {width}w' for width,target in widths.items())
E=lambda s:html.escape(str(s),quote=True)
def path(lang):return ('' if lang=='en' else lang+'/')+'shop/'
def home(lang):return '/' if lang=='en' else '/'+lang+'/'
def version(root,name):return hashlib.sha256((root/name).read_bytes()).hexdigest()[:12]
def image(name,width=1200):return f'/assets/shop/love-above-all/{file(name)}-{width}.webp'
def full(name):return f'/assets/shop/love-above-all/{file(name)}.jpg'
def img(name,alt,*,lazy=True,cls=''):
    sizes='(max-width: 590px) calc(100vw - 32px), (max-width: 999px) 560px, (max-width: 1680px) 50vw, 830px'
    dims=DIMENSIONS[name]
    return f'<img class="{cls}" src="{image(name)}" srcset="{candidates(name)}" sizes="{sizes}" alt="{E(alt)}" width="{dims[0]}" height="{dims[1]}" decoding="async" '+('loading="lazy"' if lazy else 'fetchpriority="high"')+'>'
def page(root,cfg,lang,head_common,og_head):
    c=COPY[lang];site=cfg['siteUrl'].rstrip('/');url=site+'/'+path(lang);title=f'Love Above All — First Drop | Bible Answer';photo=site+full(PHOTOS[0])
    alts=''.join(f'<link rel="alternate" hreflang="{CODES[l]}" href="{site}/{path(l)}">\n' for l in LANGS)+f'<link rel="alternate" hreflang="x-default" href="{site}/{path("en")}">\n'
    data={'@context':'https://schema.org','@graph':[{'@type':'Product','@id':site+'/shop/#love-above-all','name':'Bible Answer Love Above All T-Shirt — First Drop','description':c['description'],'brand':{'@type':'Brand','name':'Bible Answer'},'image':[site+full(p) for p in PHOTOS],'sku':'BA-LAA-FIRST-DROP','material':'Cotton, 280 g/m²','color':c['colour'],'size':['M','L','XL'],'url':url,'offers':{'@type':'Offer','price':'33.00','priceCurrency':'USD','url':url}}, {'@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':'Bible Answer','item':site+home(lang)},{'@type':'ListItem','position':2,'name':c['shop'],'item':url}]}]}
    ld=json.dumps(data,ensure_ascii=False).replace('</','<\\/')
    extra=alts+f'<script type="application/ld+json">{ld}</script>\n'
    head=head_common(None,title,c['description'],url,photo,'index,follow,max-image-preview:large','/',extra)+og_head(title,c['description'],url,photo,{'en':'en_US','ru':'ru_RU','es':'es_ES','pt':'pt_BR','fr':'fr_FR','fil':'fil_PH'}[lang])
    languages=''.join(f'<li><a href="/{path(l)}" hreflang="{CODES[l]}" lang="{CODES[l]}"'+(' aria-current="page"' if l==lang else '')+f'>{COPY[l]["lang"]}</a></li>' for l in LANGS)
    instagram=f'https://www.instagram.com/{HANDLES[lang]}/'
    def slide(i,p):
        label=c['front'] if p=='front-daylight' else c[p]
        return f'<figure class="look" id="look-{i+1}"><a href="{full(p)}" data-zoom="{i}" aria-label="{E(c["zoom"])} — {E(label)}">{img(p,alt(c,p),lazy=i>0,cls="look-img")}</a></figure>'
    slides=''.join(slide(i,p) for i,p in enumerate(PHOTOS))
    editorial=''.join(slide(i,p) for i,p in enumerate(EDITORIAL_PHOTOS,len(PHOTOS)))
    thumbs=''.join(f'<button type="button" aria-pressed="{str(i==0).lower()}" aria-controls="look-{i+1}"><img src="/assets/shop/love-above-all/{file(p)}-thumb.webp" width="240" height="160" alt=""><span>{E(c["front"] if p=="front-daylight" else c[p])}</span></button>' for i,p in enumerate(PHOTOS))
    assets=json.dumps([{'full':full(p),'alt':alt(c,p)} for p in PHOTOS+EDITORIAL_PHOTOS],ensure_ascii=False)
    specs=''.join(f'<li>{E(x)}</li>' for x in (c['material'],c['silhouette'],c['craft'],c['colour']))
    faq=''.join(f'<details class="fold"><summary>{E(q)}<span class="fold-mark" aria-hidden="true"></span></summary><p>{E(a)}</p></details>' for q,a in c['questions'])
    sizes=''.join(f'<label><input type="radio" name="size" value="{sz}"><span>{sz}</span></label>' for sz in ('M','L','XL'))
    return f'''<!doctype html>
<html lang="{CODES[lang]}"><head>{head}
<link rel="stylesheet" href="/site.css">
<link rel="stylesheet" href="/shop.css?v={version(root,'shop.css')}">
<script defer src="/shop.js?v={version(root,'shop.js')}"></script>
</head><body class="shop-site">
<a class="skip" href="#main">{E(c['skip'])}</a>
<p class="shop-topline">{E(c['shipping'])}</p>
<header class="shop-header">
 <nav class="shop-nav" aria-label="Bible Answer"><a href="{home(lang)}">{E(c['app'])}</a><a href="/{path(lang)}" aria-current="page">{E(c['shop'])}</a></nav>
 <a class="shop-wordmark" href="{home(lang)}">Bible Answer</a>
 <div class="shop-tools"><details class="langmenu"><summary>{E(c['lang'])}</summary><ul>{languages}</ul></details>{theme.control(lang)}</div>
</header>
<main id="main" class="shop-main">
 <section class="product" aria-labelledby="product-title">
  <div class="looks" aria-label="{E(c['gallery'])}" data-photos="{E(assets)}">
   <div class="looks-track">{slides}</div>
   <div class="looks-thumbs">{thumbs}</div>
  </div>
  <div class="buy"><div class="buy-in">
   <p class="buy-kicker"><span>First Drop</span> <i aria-hidden="true">·</i> <span>{E(c['editionShort'])}</span></p>
   <h1 id="product-title">Love Above All</h1>
   <p class="buy-line">{E(c['type'])}</p>
   <p class="buy-price">$33 <span>USD</span></p>
   <p class="buy-ship">{E(c['shipping'])}</p>
   <div class="buy-size">
    <div class="buy-size-head"><span>{E(c['sizeLabel'])}</span><a href="{instagram}" target="_blank" rel="noopener noreferrer">{E(c['sizeHelp'])}</a></div>
    <fieldset id="size-options"><legend class="sr">{E(c['size'])}</legend><div class="sizes">{sizes}</div></fieldset>
   </div>
   <a class="buy-cta" href="{instagram}" target="_blank" rel="noopener noreferrer" data-template="{E(c['chosen'])}"><span data-cta>{E(c['cta'])}</span><span aria-hidden="true">↗</span></a>
   <p class="buy-note">{E(c['order'])}</p>
   <div class="folds">
    <details class="fold" open><summary>{E(c['detailsTitle'])}<span class="fold-mark" aria-hidden="true"></span></summary><ul class="specs">{specs}</ul></details>
    {faq}
   </div>
  </div></div>
 </section>
 <section class="credo" aria-labelledby="credo-title">
  <div class="credo-copy">
  <h2 id="credo-title">{E(c['cityName'])}</h2>
  <p class="credo-text">{E(c['storyText'])}</p>
  </div>
  <figure class="shop-city">
   <video controls playsinline preload="none" width="720" height="1280" aria-label="{E(c['cityAlt'])}" poster="/assets/shop/love-above-all/petronas-poster.webp">
    <source src="/assets/shop/love-above-all/petronas.mp4" type="video/mp4">
    <img src="/assets/shop/love-above-all/petronas-poster.webp" alt="{E(c['cityAlt'])}" width="563" height="1000" loading="lazy">
   </video>
   <figcaption>{E(c['cityCaption'])}</figcaption>
  </figure>
 </section>
 <details class="shop-lookbook fold">
  <summary>{E(c['lookbook'])}<span class="fold-mark" aria-hidden="true"></span></summary>
  <div class="lookbook-grid">{editorial}</div>
 </details>
</main>
<footer class="shop-footer">{branding.footer_brand(lang,home(lang))}<nav><a href="{home(lang)}">{E(c['backTo'])}</a><a href="/privacy#{lang}">{E(c['privacy'])}</a><a href="{instagram}" target="_blank" rel="noopener noreferrer">Instagram</a></nav><p class="shop-footer-note">{E(c['footerNote'])}</p></footer>
<aside class="mobile-buy" hidden aria-label="{E(c['shop'])}"><span class="mobile-buy-price">$33</span><a href="#size-options" data-mobile-cta data-order="{instagram}" data-order-label="{E(c['cta'])}">{E(c['size'])}</a></aside>
<dialog class="photo-dialog" aria-label="{E(c['gallery'])}"><button type="button" class="photo-close" aria-label="{E(c['close'])}"></button><img src="{full(PHOTOS[0])}" alt=""></dialog>
</body></html>'''
def write(root,cfg,head_common,og_head):
    for lang in LANGS:
        target=root/path(lang)/'index.html';target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(page(root,cfg,lang,head_common,og_head),encoding='utf-8')
    print('wrote six localized First Drop pages')
def sitemap_rows(cfg):
    site=cfg['siteUrl'].rstrip('/')
    alts=''.join(f'\n    <xhtml:link rel="alternate" hreflang="{CODES[l]}" href="{site}/{path(l)}"/>' for l in LANGS)+f'\n    <xhtml:link rel="alternate" hreflang="x-default" href="{site}/{path("en")}"/>'
    return [f'  <url>\n    <loc>{site}/{path(l)}</loc>{alts}\n  </url>' for l in LANGS]
