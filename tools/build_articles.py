#!/usr/bin/env python3
"""Static reading guides. All Scripture comes from saved verse.py stdout."""
import datetime,html,json,math,pathlib,re
E=lambda text:html.escape(str(text),quote=True)
LANGS = ('en', 'ru', 'es', 'pt', 'fr', 'fil')
LANG_CODE = {'en':'en', 'ru':'ru', 'es':'es', 'pt':'pt-BR', 'fr':'fr', 'fil':'fil'}
UI = json.loads((pathlib.Path(__file__).parent / 'article-ui.json').read_text('utf-8'))
def load(root):return json.loads((root/'tools/articles.json').read_text('utf-8'))
def path(a):return f'{"" if a["lang"]=="en" else a["lang"]+"/"}articles/{a["slug"]}/'
def hub(lang):return f'{"" if lang=="en" else lang+"/"}articles/'
def home(lang):return '/' if lang=='en' else f'/{lang}/'
def verse(root,source):return json.loads((root/'tools/article-verses'/source).read_text('utf-8'))
def word_count(root,a):
 text=[a['lead']]
 for s in a['sections']:
  text.append(s['title'])
  for b in s['blocks']:
   text+=([b['text']] if b['type']=='paragraph' else [verse(root,b['source'])['text']] if b['type']=='passage' else b['items'])
 return len(' '.join(text).split())
def duration(root,a):return max(2,math.ceil(word_count(root,a)/(190 if a['lang']=='ru' else 220)))
def stamp(date,lang):
 d=datetime.date.fromisoformat(date)
 months={'ru':['января','февраля','марта','апреля','мая','июня','июля','августа','сентября','октября','ноября','декабря'], 'es':['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre'], 'pt':['janeiro','fevereiro','março','abril','maio','junho','julho','agosto','setembro','outubro','novembro','dezembro'], 'fr':['janvier','février','mars','avril','mai','juin','juillet','août','septembre','octobre','novembre','décembre'], 'fil':['Enero','Pebrero','Marso','Abril','Mayo','Hunyo','Hulyo','Agosto','Setyembre','Oktubre','Nobyembre','Disyembre']}
 if lang=='en':return d.strftime('%B %d, %Y').replace(' 0',' ')
 month=months[lang][d.month-1]
 return f'{month} {d.day}, {d.year}' if lang=='fil' else f'{d.day} de {month} de {d.year}' if lang in ('es','pt') else f'{d.day} {month} {d.year}'
def alternatives(cfg,pages,current):
 urls={a['lang']:cfg['siteUrl'].rstrip('/')+'/'+path(a) for a in pages}
 return ''.join(f'<link rel="alternate" hreflang="{LANG_CODE[lang]}" href="{E(url)}">\n' for lang,url in urls.items())+f'<link rel="alternate" hreflang="x-default" href="{E(urls["en"])}">\n'
def navigation(lang,pages):
 u=UI[lang]
 choices=''.join(f'<li><a href="/{path(a) if a.get("slug") else hub(a["lang"])}" lang="{LANG_CODE[a["lang"]]}" hreflang="{LANG_CODE[a["lang"]]}"'+(' aria-current="page"' if a['lang']==lang else '')+f'>{UI[a["lang"]]["label"]}</a></li>' for a in pages)
 return (f'<a class="article-skip" href="#main">{u["skip"]}</a><header class="article-nav"><div class="article-nav__in">'
 '<a class="mark" href="'+home(lang)+'">Bible Answer</a>'
 f'<nav aria-label="{u["hub"]}"><a href="{home(lang)}">{u["home"]}</a><a href="/{hub(lang)}">{u["hub"]}</a></nav>'
 f'<details class="article-language-menu"><summary aria-label="{u["language"]}">{u["label"]}</summary><ul>{choices}</ul></details></div></header>')
def footer(cfg,lang):
 u=UI[lang]
 license_note = f'<p class="article-license"><a href="https://creativecommons.org/licenses/by-sa/4.0/">{u["article_license"]}</a></p>' if lang=='fil' else ''
 return f'<footer class="foot article-footer"><p><a href="/privacy#{lang}">{u["privacy"]}</a><span class="dot">·</span><wbr><a href="/terms#{lang}">{u["terms"]}</a></p><p><a href="mailto:{E(cfg["contactEmail"])}">{E(cfg["contactEmail"])}</a></p>{license_note}</footer>'
def card(root,a):
 u=UI[a['lang']]
 return (f'<a class="guide-card" href="/{path(a)}"><div class="guide-card__image"><img src="/assets/plates/{a["plate"]}.webp" width="900" height="600" alt="" loading="lazy" decoding="async"></div><div class="guide-card__body">'
 f'<p class="article-kicker">{E(a["category"])} <span>· {duration(root,a)} {u["reading"]}</span></p><h2>{E(a["title"])}</h2><p>{E(a["lead"])}</p><span class="guide-card__arrow" aria-hidden="true">↗</span></div></a>')
def app_card(lang,cfg=None,key=None):
 u=UI[lang];copy=u['feature_copy'].get(key,u['apptext'])
 link=f'<a class="btn btn--ghost" href="{home(lang)}">{u["appcta"]}</a>'
 if cfg and cfg.get('appLive'):
  link=f'<a class="btn btn--gold" href="{E(cfg["appStoreUrl"])}">{u["store"]}</a>'+link
 return f'<aside class="article-app"><img src="/assets/icon.png" width="64" height="64" alt=""><div><h2>{u["app"]}</h2><p>{E(copy)}</p></div><div class="article-app__actions">{link}</div></aside>'
def shell(cfg,lang,title,description,url,image,extra,body,head_common,og_head,article=False):
 meta=og_head(title,description,url,image,UI[lang]['locale'])
 if article:meta=meta.replace('content="website"','content="article"')
 return f'<!doctype html>\n<html lang="{LANG_CODE[lang]}">\n<head>\n'+head_common(None,title,description,url,image,'index,follow,max-image-preview:large','/',extra)+meta+'<link rel="preload" href="/fonts/cormorant-garamond.woff2" as="font" type="font/woff2" crossorigin>\n<link rel="stylesheet" href="/site.css">\n<link rel="stylesheet" href="/articles.css">\n</head>\n<body class="article-site"><div class="sky" aria-hidden="true"><div class="sky__img"></div><div class="sky__veil"></div></div>'+body+'</body>\n</html>\n'
def index_page(root,cfg,lang,all_articles,head_common,og_head):
 u=UI[lang];site=cfg['siteUrl'].rstrip('/');mine=sorted([a for a in all_articles if a['lang']==lang],key=lambda a: ('start','anxiety','morning','money','psalm23','forgiveness','gratitude','wisdom').index(a['key']));url=site+'/'+hub(lang)
 pairs=[dict(lang=l) for l in LANGS]
 alt=''.join(f'<link rel="alternate" hreflang="{LANG_CODE[l]}" href="{site}/{hub(l)}">\n' for l in LANGS)+f'<link rel="alternate" hreflang="x-default" href="{site}/{hub("en")}">\n'
 data={'@context':'https://schema.org','@type':'CollectionPage','name':u['index_title'],'url':url,'inLanguage':LANG_CODE[lang],'description':u['description'],'hasPart':[{'@type':'Article','headline':a['title'],'url':site+'/'+path(a)} for a in mine]}
 extra=alt+'<script type="application/ld+json">'+json.dumps(data,ensure_ascii=False)+'</script>\n'
 body=navigation(lang,pairs)+f'<main id="main" class="guide-index"><section class="guide-index__hero"><p class="article-kicker">Bible Answer · {u["hub"]}</p><h1>{u["title"]}</h1><p>{u["lead"]}</p></section><div class="guide-grid">'+''.join(card(root,a) for a in mine)+f'</div>{app_card(lang,cfg)}</main>'+footer(cfg,lang)
 return shell(cfg,lang,u['index_title'],u['description'],url,site+f'/assets/og/og-{lang}.jpg',extra,body,head_common,og_head)
def edition(u):
 text=E(u['edition'])
 if 'CC BY-SA' in text:return f'<a href="https://creativecommons.org/licenses/by-sa/4.0/">{text}</a>'
 if 'CC BY' in text:return f'<a href="https://creativecommons.org/licenses/by/4.0/">{text}</a>'
 return text

def render_block(root,b,u):
 if b['type']=='paragraph':return '<p>'+E(b['text'])+'</p>'
 if b['type']=='steps':return '<ol class="article-steps">'+''.join('<li>'+E(i)+'</li>' for i in b['items'])+'</ol>'
 if b['type']=='practice':return f'<aside class="article-practice"><h3>{E(b["title"])}</h3><ul>'+''.join('<li>'+E(i)+'</li>' for i in b['items'])+'</ul></aside>'
 if b['type']=='passage':
  v=verse(root,b['source']);q=f'<figure class="article-verse"><blockquote>{E(v["text"])}</blockquote><figcaption>{E(v["reference"])}<span>{edition(u)}</span></figcaption></figure>'
  if b.get('expanded'):return f'<details class="article-passage"><summary>{u["passage"]}: {E(v["reference"])}</summary>{q}</details>'
  return q
 raise ValueError(b['type'])
def article_page(root,cfg,a,all_articles,head_common,og_head):
 lang=a['lang'];u=UI[lang];site=cfg['siteUrl'].rstrip('/');url=site+'/'+path(a);image=site+f'/assets/og/articles/{lang}-{a["key"]}.jpg'
 pair=[b for b in all_articles if b['key']==a['key']]
 breadcrumbs=[{'@type':'ListItem','position':1,'name':'Bible Answer','item':site+home(lang)},{'@type':'ListItem','position':2,'name':u['hub'],'item':site+'/'+hub(lang)},{'@type':'ListItem','position':3,'name':a['title'],'item':url}]
 organization={'@type':'Organization','name':'Bible Answer','url':site+'/','logo':{'@type':'ImageObject','url':site+'/assets/icon.png'}}
 data={'@context':'https://schema.org','@graph':[{'@type':'Article','headline':a['title'],'description':a['description'],'inLanguage':LANG_CODE[lang],'datePublished':a['date'],'dateModified':a['date'],'mainEntityOfPage':{'@type':'WebPage','@id':url},'image':[image],'author':{'@type':'Organization','name':'Bible Answer','url':site+'/'+hub(lang)},'publisher':organization,'wordCount':word_count(root,a)},{'@type':'BreadcrumbList','itemListElement':breadcrumbs}]}
 extra=alternatives(cfg,pair,lang)+'<script type="application/ld+json">'+json.dumps(data,ensure_ascii=False)+'</script>\n'+f'<meta property="article:published_time" content="{a["date"]}">\n<meta property="article:modified_time" content="{a["date"]}">\n'
 toc=''.join(f'<a href="#{s["id"]}">{E(s["title"])}</a>' for s in a['sections'])
 body=navigation(lang,pair)+f'<main id="main" class="reading-guide"><nav class="article-breadcrumbs" aria-label="{u["hub"]}"><a href="/{hub(lang)}">{u["hub"]}</a><span aria-hidden="true">/</span><span>{E(a["category"])}</span></nav><header class="article-hero"><div><p class="article-kicker">{E(a["category"])}</p><h1>{E(a["title"])}</h1><p class="article-lead">{E(a["lead"])}</p><p class="article-byline">{u["byline"]} <span>·</span> <time datetime="{a["date"]}">{stamp(a["date"],lang)}</time> <span>·</span> {duration(root,a)} {u["reading"]}</p></div><figure><img src="/assets/plates/{a["plate"]}.webp" width="900" height="600" alt="" fetchpriority="high" decoding="async"></figure></header><div class="article-layout"><aside class="article-toc"><h2>{u["contents"]}</h2><nav aria-label="{u["contents"]}">{toc}</nav></aside><article class="article-prose">'+''.join(f'<section id="{s["id"]}"><h2>{E(s["title"])}</h2>'+''.join(render_block(root,b,u) for b in s['blocks'])+'</section>' for s in a['sections'])+f'<p class="article-method-note">{edition(u)} · <a href="/terms#{lang}">{u["terms"]}</a></p></article></div>{app_card(lang,cfg,a["key"])}<section class="article-related"><h2>{u["next"]}</h2><div class="guide-grid">'+''.join(card(root,b) for b in sorted([b for b in all_articles if b['lang']==lang and b['key']!=a['key']],key=lambda b: ('anxiety','morning','money','psalm23','start','forgiveness','gratitude','wisdom').index(b['key']))[:3])+'</div></section></main>'+footer(cfg,lang)
 return shell(cfg,lang,a['seo_title']+' — Bible Answer' if len(a['seo_title'])+15<=70 else a['seo_title'],a['description'],url,image,extra,body,head_common,og_head,True)
def write(root,cfg,head_common,og_head):
 all_articles=load(root)
 for lang in LANGS:
  dest=root/hub(lang);dest.mkdir(parents=True,exist_ok=True);(dest/'index.html').write_text(index_page(root,cfg,lang,all_articles,head_common,og_head),'utf-8')
 for a in all_articles:
  dest=root/path(a);dest.mkdir(parents=True,exist_ok=True);(dest/'index.html').write_text(article_page(root,cfg,a,all_articles,head_common,og_head),'utf-8')
 print(f'wrote {len(all_articles)} reading guides and {len(LANGS)} indexes')
def sitemap_rows(root,cfg):
 site=cfg['siteUrl'].rstrip('/');all_articles=load(root);rows=[]
 groups=[[dict(lang=l,slug=None,date=max(a['date'] for a in all_articles)) for l in LANGS]]+[[a for a in all_articles if a['key']==key] for key in dict.fromkeys(a['key'] for a in all_articles)]
 for group in groups:
  urls={a['lang']:site+'/'+(path(a) if a['slug'] else hub(a['lang'])) for a in group}
  alts=''.join(f'\n    <xhtml:link rel="alternate" hreflang="{LANG_CODE[l]}" href="{url}"/>' for l,url in urls.items())+f'\n    <xhtml:link rel="alternate" hreflang="x-default" href="{urls["en"]}"/>'
  for a in group:rows.append(f'  <url>\n    <loc>{urls[a["lang"]]}</loc>{alts}\n    <lastmod>{a["date"]}</lastmod>\n  </url>')
 return rows
