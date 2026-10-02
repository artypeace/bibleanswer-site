# bibleanswer.app

The website of [Bible Answer](https://apps.apple.com/app/id6761124514) — iPhone, iPad, Apple Watch.

Static pages, published by GitHub Pages from `main` (root) under the custom domain `bibleanswer.app` (file `CNAME`).

| Address | What it is |
| --- | --- |
| `/` `/ru/` `/es/` `/pt/` `/fr/` `/fil/` | The home page in six languages: a complete page each, with its own title, description, canonical address and `hreflang` links. |
| `/privacy` `/terms` `/support` | The legal pages, with the language anchors `#en #ru #es #pt #fr #fil`. The text is a byte-for-byte copy of the pages the App Store and the app link to today (`artypeace.github.io/bible-answer/…`). |
| `/links` | The page behind "link in bio": language choice, the App Store, the social accounts. Not in the sitemap, `noindex`. |
| `404.html` | Any other address. |

The site shows what the app does; it does **not** ask the server anything. The example answer is fixed text. The pages load nothing from any other host, set no cookie and count nothing (the Content-Security-Policy says so: `connect-src 'none'`).

## Rebuilding

```
python3 tools/build.py      # Python 3, standard library only; commit the result
python3 tools/check.py      # tags, links, images, sitemap, anchors — the same check runs on every push
```

| File | What it is |
| --- | --- |
| `tools/config.json` | The address, the App Store link and id, the contact e-mail, the social accounts (kept in this one place), the Pinterest verification code, the switch for the screenshot slots. |
| `tools/app-strings.json` | Words shared with the app (tagline, feelings, section names). Produced by `tools/extract_from_app.py` from the app's and the server's own sources; never edited by hand. |
| `tools/site-strings.json` | The website's own copy, titles, descriptions and the example answer, in all six languages. |
| `tools/build.py` | Turns the files above into pages, `sitemap.xml`, `robots.txt`. |
| `tools/make_og.py` | Draws the link-preview pictures `assets/og/og-<lang>.jpg` (1200×630). Needs Pillow, fontTools, brotli. |
| `tools/optimize_screens.py` | Makes light web copies of the App Store screenshots. |
| `tools/sync_legal.py` | Re-copies the three legal pages from another folder, byte for byte. |
| `site.css`, `app.js`, `fonts/` | Look and motion: the canvas sky, headings that rise word by word, the phone that follows the page (a pinned stage with five scenes), parallax. `app.js` is cosmetic; every page works without it, and with "reduce motion" or on a phone the story is a column of cards. |

### Things to fill in (all in `tools/config.json`, then `python3 tools/build.py`)

* `contactEmail` — `support@bibleanswer.app` (Cloudflare Email Routing forwards it to `bibleanswerapp@gmail.com`). The legal pages carry their own copy of the address in their text (`bibleanswerapp@gmail.com`); change it there if you want them to match.
* `social` — the accounts that exist (platform, language, handle, url). Only entries with a url are shown: in the footer and on `/links`, and listed in the structured data (`sameAs`). Add an entry when an account for another language is created.
* `googleVerify`, `bingVerify`, `yandexVerify`, `pinterestVerify` — the codes the webmaster tools and Pinterest give for the "HTML tag" method; each empty value means no tag. (Google can instead be verified with a DNS TXT record in Cloudflare.)
* `showScreenshotSlots` — `false` hides the screenshots strip until real screenshots exist.

### The phone on the home page

Five scenes (read, guide, counsel, quiet, hours) change as you scroll. They are drawn from the app's own words and engravings.
To use real screen recordings or screenshots instead, drop files into `assets/story/` (see `assets/story/README.md`) and run the build.

### Screenshots and Apple badges

* `assets/screens/README.md` — where the App Store screenshots go (per device and language). Until they are there, the page shows quiet placeholders.
* `assets/badges/` — Apple's official "Download on the App Store" badges, one per language (already in place; see its README).

## Publishing, step by step

Domain: `bibleanswer.app` (bought at Cloudflare). `.app` is on the HTTPS-only list of browsers, so the address works only once GitHub has issued its certificate: set up in this order.

1. **Verify the domain** (so nobody else can claim it on GitHub) — GitHub account `artypeace` → Settings → Pages → *Add a domain* → `bibleanswer.app`. GitHub shows a TXT record `_github-pages-challenge-artypeace.bibleanswer.app` and a value.
2. **Cloudflare → bibleanswer.app → DNS → Records.** Every record is **DNS only** (grey cloud), not Proxied — otherwise GitHub cannot issue the certificate.

   | Type | Name | Content |
   | --- | --- | --- |
   | A | `@` | `185.199.108.153` |
   | A | `@` | `185.199.109.153` |
   | A | `@` | `185.199.110.153` |
   | A | `@` | `185.199.111.153` |
   | AAAA | `@` | `2606:50c0:8000::153` |
   | AAAA | `@` | `2606:50c0:8001::153` |
   | AAAA | `@` | `2606:50c0:8002::153` |
   | AAAA | `@` | `2606:50c0:8003::153` |
   | CNAME | `www` | `artypeace.github.io` |
   | TXT | `_github-pages-challenge-artypeace` | the value from step 1 |

   If a CAA record exists, it must allow `letsencrypt.org`. Delete Cloudflare's default parking records for `@` and `www` if there are any.
3. GitHub account → Settings → Pages → press *Verify* next to `bibleanswer.app` (after the TXT has propagated; minutes, rarely longer).
4. This repository → Settings → Pages → *Build and deployment*: Source *Deploy from a branch*, branch `main`, folder `/ (root)`. The custom domain is read from `CNAME`; wait for the green "DNS check successful".
5. Tick **Enforce HTTPS** (it appears once the certificate is issued — up to an hour).
6. `www.bibleanswer.app` redirects to `bibleanswer.app` by itself.

Check: `https://bibleanswer.app/`, `/ru/`, `/privacy#ru`, `/links`, a wrong address (should show the 404 page), and `curl -I http://bibleanswer.app` (should redirect to https).

Search engines: add the site in Google Search Console and Bing Webmaster Tools as a *domain* property (a TXT record in Cloudflare), submit `https://bibleanswer.app/sitemap.xml`.

## Not part of this repository

`artypeace.github.io` (the user site) stays as it is: it serves `app-ads.txt` for another app and the privacy, terms and support addresses the App Store and the app link to today. No custom domain is attached to it.
