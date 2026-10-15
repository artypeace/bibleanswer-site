"""Optional GA4 for the website; the Google tag loads only after opt-in."""
import hashlib, html, re, json

def measurement_id(cfg):
    value=cfg.get('analyticsMeasurementId','').strip()
    if value and not re.fullmatch(r'G-[A-Z0-9]{6,20}',value):
        raise ValueError('analyticsMeasurementId must be an actual GA4 G- identifier')
    return value

def policy(csp,cfg):
    if not measurement_id(cfg):return csp
    return csp.replace("script-src 'self'", "script-src 'self' https://www.googletagmanager.com").replace("img-src 'self' data:","img-src 'self' data: https://www.googletagmanager.com https://*.google-analytics.com").replace("connect-src 'none'", "connect-src https://www.googletagmanager.com https://*.google-analytics.com https://*.google.com")

def head(root,cfg,base):
    ident=measurement_id(cfg)
    if not ident:return ''
    js=hashlib.sha256((root/'analytics.js').read_bytes()).hexdigest()[:12]
    css=hashlib.sha256((root/'analytics.css').read_bytes()).hexdigest()[:12]
    return (f'<link rel="stylesheet" href="{base}analytics.css?v={css}">\n'
            f'<script defer src="{base}analytics.js?v={js}" data-ga-id="{html.escape(ident)}"></script>\n')

NOTICE = re.compile(r'<!-- website:analytics -->.*?<!-- /website:analytics -->\n?', re.S)
def privacy_notice(text, root, cfg):
    text = NOTICE.sub('', text)
    if not measurement_id(cfg): return text
    copy = json.loads((root/'tools/website-analytics-notice.json').read_text('utf-8'))
    rows = ['<!-- website:analytics -->', '<aside aria-label="Website analytics">']
    for lang, parts in copy.items():
        rows.append('<section lang="'+lang+'" id="website-analytics-'+lang+'"><h2>'+html.escape(parts[0])+'</h2>')
        rows.extend('<p>'+html.escape(p)+'</p>' for p in parts[1:])
        rows.append('<p><a href="https://policies.google.com/technologies/partner-sites" rel="noopener noreferrer">Google</a></p></section>')
    rows.extend(['</aside>', '<!-- /website:analytics -->'])
    return re.sub(r'<main>\s*', lambda _: '<main>\n'+'\n'.join(rows)+'\n', text, count=1)
