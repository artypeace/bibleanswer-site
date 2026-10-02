#!/usr/bin/env python3
"""Tells the search engines that use IndexNow (Bing, Yandex, Naver, Seznam; Google does not) that pages changed.

    python3 tools/indexnow.py --all                 # every page in sitemap.xml
    python3 tools/indexnow.py --changed HEAD~1 HEAD # the pages whose files differ between two commits
    python3 tools/indexnow.py --dry-run --all       # print what would be sent

The key is in tools/config.json ("indexNowKey"); build.py publishes it as /<key>.txt, which is how the engines know the
site is yours. The key is not a secret. Only addresses are sent. Standard library only. The workflow
.github/workflows/indexnow.yml runs this after every deploy of the site."""
import argparse, json, pathlib, re, subprocess, sys, urllib.error, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
CFG = json.loads((ROOT / 'tools/config.json').read_text('utf-8'))
SITE = CFG['siteUrl'].rstrip('/')
ENDPOINT = 'https://api.indexnow.org/IndexNow'
FLAT = {'privacy.html': '/privacy', 'terms.html': '/terms', 'support.html': '/support'}   # these are served without .html
SKIP = {'links/index.html', '404.html'}                                                   # not in the index on purpose


def all_urls():
    return re.findall(r'<loc>([^<]+)</loc>', (ROOT / 'sitemap.xml').read_text('utf-8'))


def url_for(path):
    if path in SKIP:
        return None
    if path in FLAT:
        return SITE + FLAT[path]
    if path == 'index.html':
        return SITE + '/'
    if path.endswith('/index.html'):
        return SITE + '/' + path[:-len('index.html')]
    return None


def changed_urls(a, b):
    names = subprocess.check_output(['git', 'diff', '--name-only', a, b], cwd=ROOT, text=True).split()
    found = [url_for(n) for n in names]
    return sorted({u for u in found if u})


def submit(urls, dry):
    key = CFG.get('indexNowKey')
    if not key:
        sys.exit('no "indexNowKey" in tools/config.json')
    host = SITE.split('://', 1)[1]
    payload = {'host': host, 'key': key, 'keyLocation': f'{SITE}/{key}.txt', 'urlList': urls}
    print(f'{len(urls)} address(es) for {host}:')
    for u in urls:
        print('  ' + u)
    if dry or not urls:
        print('dry run, nothing sent' if dry else 'nothing to send')
        return
    req = urllib.request.Request(ENDPOINT, data=json.dumps(payload).encode(), method='POST',
                                 headers={'Content-Type': 'application/json; charset=utf-8', 'User-Agent': 'bibleanswer-site-indexnow'})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            print(f'IndexNow answered {r.status} (200 = received, 202 = received, the key is checked later)')
    except urllib.error.HTTPError as err:
        hint = {400: 'bad request', 403: 'the key was not found at keyLocation (is the site deployed?)', 422: 'an address does not belong to the host', 429: 'too many requests'}
        sys.exit(f'IndexNow answered {err.code}: {hint.get(err.code, err.reason)}')


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument('--all', action='store_true', help='every address in sitemap.xml')
    g.add_argument('--changed', nargs=2, metavar=('FROM', 'TO'), help='the pages whose files differ between two commits')
    p.add_argument('--dry-run', action='store_true')
    a = p.parse_args()
    submit(all_urls() if a.all else changed_urls(*a.changed), a.dry_run)


if __name__ == '__main__':
    main()
