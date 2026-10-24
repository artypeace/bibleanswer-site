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
PHOTOS=('back','front-daylight','neck-detail','folded')
def alt(c,name):return c['alts'][ORIGINAL_PHOTOS.index(name)]
# The file each photo is served from: the neck detail is turned 90° to the right in the file itself,
# and the back is the owner's night photograph on the bridge.
FILE={'neck-detail':'neck-detail-v','back':'back-bridge'}
def file(name):return FILE.get(name,name)
def candidates(name):
    real={'back':1672,'front-daylight':1672,'neck-detail':941,'folded':900}.get(name,1800)
    return ', '.join(f'{image(name,w)} {min(w,real)}w' for w in (640,1200,1800))
E=lambda s:html.escape(str(s),quote=True)
def path(lang):return ('' if lang=='en' else lang+'/')+'shop/'
def home(lang):return '/' if lang=='en' else '/'+lang+'/'
def version(root,name):return hashlib.sha256((root/name).read_bytes()).hexdigest()[:12]
def image(name,width=1200):return f'/assets/shop/love-above-all/{file(name)}-{width}.webp'
def full(name):return f'/assets/shop/love-above-all/{file(name)}.jpg'
def img(name,alt,*,lazy=True,cls=''):
    sizes='(max-width: 999px) 100vw, 58vw'
    dims={'back':(1672,941),'folded':(900,1600),'front-daylight':(1672,941),'neck-detail':(941,1672)}[name]
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
    n=len(PHOTOS)
    slides=''.join(f'<figure class="look" id="look-{i+1}"><a href="{full(p)}" data-zoom="{i}" aria-label="{E(c["zoom"])} — {E(c[p])}">{img(p,alt(c,p),lazy=i>0,cls="look-img look-"+p)}</a></figure>' for i,p in enumerate(PHOTOS))
    dots=''.join(f'<span class="look-dot"{" data-on" if i==0 else ""}></span>' for i in range(n))
    assets=json.dumps([{'full':full(p),'alt':alt(c,p)} for p in PHOTOS],ensure_ascii=False)
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
   <div class="looks-meta" aria-hidden="true"><span class="looks-count"><span data-look>1</span> / {n}</span><span class="looks-dots">{dots}</span></div>
  </div>
  <div class="buy"><div class="buy-in">
   <p class="buy-kicker"><span>First Drop</span> <i aria-hidden="true">·</i> <span>{E(c['editionShort'])}</span></p>
   <h1 id="product-title">Love Above All</h1>
   <p class="buy-line">The Essential Tee</p>
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
  <p class="credo-kicker">{E(c['craft'])}</p>
  <h2 id="credo-title">Faith in <em>every detail.</em></h2>
  <p class="credo-ref">The Ichthys <span aria-hidden="true">/</span> 1 Corinthians 13:4</p>
  <p class="credo-text">{E(c['storyText'])}</p>
 </section>
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
