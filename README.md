# bibleanswer.app

The website of [Bible Answer](https://apps.apple.com/app/id6761124514) — iPhone, iPad, Apple Watch.

Static pages, published by GitHub Pages from `main` (root) under the custom domain `bibleanswer.app` (file `CNAME`).

| Address | What it is |
| --- | --- |
| `/` `/ru/` `/es/` `/pt/` `/fr/` `/fil/` | The home page in six languages: a complete page each, with its own title, description, canonical address and `hreflang` links. |
| `/privacy` `/terms` `/support` | The legal pages, with the language anchors `#en #ru #es #pt #fr #fil`. The text is a byte-for-byte copy of the pages the App Store and the app link to today (`artypeace.github.io/bible-answer/…`). |
| `/press/` | The press kit, in English: descriptions to copy, the facts, the app icon, news, contact. In the sitemap. |
| `/articles/`, `/ru/articles/` | Reading-guide indexes and four original guides in English / Russian. Static HTML, matching language alternatives, Article / BreadcrumbList data and local share cards. |
| `/feed.xml` | RSS 2.0 feed of English reading guides plus news in `tools/news.json` (the press page lists the news). |
| `/llms.txt` `/llms-full.txt` | A short and a full description for AI assistants (llmstxt.org format), built from the same strings as the site. |
| `/<key>.txt` | The IndexNow key file (see below). |
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
| `tools/articles.json`, `tools/build_articles.py` | Original guide content and the static page renderer. Dates belong to articles, not rebuilds. |
| `tools/article-verses/` | Exact JSON stdout from the social workspace’s `tools/verse.py`; source quotations are never edited or translated by hand. |
| `articles.css` | Styles loaded only by reading-guide pages; the landing page remains unchanged except for a footer link. |
| `tools/make_article_og.py` | Regenerates the eight 1200×630 JPEG share cards from existing local artwork and fonts. Optional Pillow / fontTools; ordinary builds do not need them. |
| `tools/news.json` | The news items (id, date, title, summary). Add one and rebuild: it appears in `feed.xml` and on `/press/`. English reading guides from `tools/articles.json` are included in the same feed. |
| `tools/indexnow.py` | Sends changed addresses to the IndexNow engines (Bing, Yandex, ...). Run by `.github/workflows/indexnow.yml` after each deploy; `--dry-run` shows what it would send. |
| `tools/make_sky.py` | Rebuilds `assets/sky-night.svg`: a deterministic vector star field with soft navy glows. Sharp at every display density; no raster upscaling. Standard library only. |
| `tools/make_og.py` | Draws the link-preview pictures `assets/og/og-<lang>.jpg` (1200×630). Needs Pillow, fontTools, brotli. |
| `tools/optimize_screens.py` | Makes light web copies of the App Store screenshots. |
| `tools/import_feature_previews.py` | Imports reviewed native screens for Advice, Reading plans and Verse of the Day, plus the app’s plate artwork. Pillow required. |
| `tools/make_device_previews.py` | Regenerates original vector device housings containing real native screens in all six languages. Pillow required. |
| `tools/import_screens.py` | Brings the app's real screens (from its own screenshot run) into the site, then rebuilds. |
| `tools/sync_legal.py` | Re-copies the three legal pages from another folder, byte for byte. |
| `site.css`, `app.js`, `fonts/` | Look and motion: the canvas sky, headings that rise word by word, the phone that follows the page (a pinned stage with five scenes), parallax. `app.js` is cosmetic; every page works without it, and with "reduce motion" or on a phone the story is a column of cards. |

### Things to fill in (all in `tools/config.json`, then `python3 tools/build.py`)

* `contactEmail` — `support@bibleanswer.app` (Cloudflare Email Routing forwards it to `bibleanswerapp@gmail.com`). The legal pages carry their own copy of the address in their text (`bibleanswerapp@gmail.com`); change it there if you want them to match.
* `social` — the accounts that exist (platform, language, handle, url). Only entries with a url are shown: in the footer and on `/links`, and listed in the structured data (`sameAs`). Add an entry when an account for another language is created.
* `googleVerify`, `bingVerify`, `yandexVerify`, `pinterestVerify` — the codes the webmaster tools and Pinterest give for the "HTML tag" method; each empty value means no tag. (Google can instead be verified with a DNS TXT record in Cloudflare.)
* `appLive` — `false` until the app is on the App Store. The press page, `llms.txt` and `llms-full.txt` then say "launching soon" instead of "on the App Store". Set `true` on release day and rebuild.
* `requirements` — the OS versions named on the press page and in `llms.txt` (from the app's deployment targets).
* `indexNowKey` — the IndexNow key; `build.py` publishes it as `/<key>.txt`. It is not a secret. To change it, edit the value, rebuild, and delete the old `<key>.txt`.
* `macAvailable` — `true`: the Mac is shown like the other devices. `false` would put the "soon" badge back.
* `showScreenshotSlots` — `false` hides the screenshots strip until real screenshots exist.

### Real screens from the app

The phone that follows the page, the Mac window and the "screens" strip show the app. Until real screens are added they are
drawn from the app's own words and engravings (the frame itself is the one of the app's App Store screenshots). To use the
real ones, run the app's screenshot tool (`tools/store-screenshots` in the app repository) and then

    python3 tools/import_screens.py <the folder the tool wrote to> --default en
    git add -A && git commit -m "Real app screens" && git push

`--default en` lets a language that has no screens of its own show the English ones. Details: `tools/import_screens.py`,
`assets/screens/README.md`, `assets/story/README.md`.

### Illustrated feature sections and daily screens

The four “Everything inside” sections combine complete native app screenshots,
artwork from the app, and text. “A verse for every day” shows the native verse sheet,
Morning prayer, and the Apple Watch app. All six languages have their own screens.
The device cards use original vector housings containing real app screenshots.
See `assets/inside/README.md`, `assets/today/verse/README.md` and
`assets/devices/README.md` for source details and regeneration.

### The phone on the home page

Five scenes (read, guide, counsel, quiet, hours) change as you scroll. They are drawn from the app's own words and engravings.
To use real screen recordings or screenshots instead, drop files into `assets/story/` (see `assets/story/README.md`) and run the build.

### Screenshots and Apple badges

* `assets/screens/README.md` — where the App Store screenshots go (per device and language). Until they are there, the page shows quiet placeholders.
* `assets/badges/` — Apple's official "Download on the App Store" badges, one per language (already in place; see its README).

### IndexNow, RSS and llms.txt

* **IndexNow** tells Bing, Yandex, Naver and Seznam at once which pages changed. Google does not take part: it learns from `sitemap.xml` and Search Console. The workflow `indexnow.yml` runs after GitHub Pages has deployed a push and sends only the addresses of the pages whose files changed. Run it by hand (Actions → indexnow → Run workflow) to send every page once. Only addresses leave the repository; the site itself still makes no third-party request.
* **feed.xml** is generated from `tools/news.json`; every page's `<head>` points to it.
* **llms.txt / llms-full.txt** state the facts an assistant should repeat (free, no account, verses unchanged, how answers are made, languages, devices). Keep them true: they are built from `tools/app-strings.json`, `tools/site-strings.json` and `tools/config.json`, so a change to the app's words reaches them with the next build.

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

### Adding a reading guide

The first set covers starting to read the Bible, forgiveness after an apology,
gratitude on a hard day, and wisdom before a decision. Every guide has an English
and Russian page. Other landing-page languages link to the English index, with
EN visible in the label; no untranslated article pages are generated.

Add one matching language pair to `tools/articles.json`, with a stable `key`, a
slug for each language, the actual publication date, title, description, lead,
local plate and sections. Supported blocks are paragraph, passage, steps and
practice. Passage blocks name a JSON file in `tools/article-verses/`. Obtain
new quotations through `tools/verse.py` in the social workspace, preserving its
stdout. This is the same text source the app uses.

Use original context and examples; compare every quotation with its source and
avoid turning a reflection into a claim the passage makes. The index explains
AI assistance and the translation used; author data names Bible Answer and
does not invent a human biography or credentials.

Generate matching share cards with `python3 tools/make_article_og.py` (Pillow
and fontTools), or supply an equivalent Cormorant variable TTF with `--font`.
Then run the normal build and check. The indexes, related guides, reciprocal
hreflang, sitemap and English RSS entries are generated from the content.
Keep publication dates stable; update a guide’s date when its content materially
changes. No arbitrary word-count target or tracking script is required.

### Real night sky

Every page's dark sky is the photograph the app's night uses: the sky over La Silla, credited visibly under the home page's hero as **ESO/P. Horálek**, under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). It turns about the zenith once in twenty minutes in CSS (`.sky__disc` in `site.css`) and stands still under reduced motion. Source, alterations and original checksum: `assets/sky/credits.json`; the image is made in the app repository (`tools/sky/`).

The video loads after the main page, only in dark mode, with motion allowed and data saving off. It pauses outside the hero or in a hidden tab. The sky button pauses/resumes it; pause preference lasts for the browser session. A real still photograph remains if playback is unavailable or motion is reduced. Mobile receives a separate narrow MP4. Articles keep their existing static sky.

### Appearance

The sun/moon button offers Light, Dark and Use device settings, localized in all six languages. `theme.js` restores the local preference before the stylesheet paints, shares it across pages/tabs and updates the browser theme color. `tools/theme.py` renders the shared control. Device settings are the default; there is no separate time-of-day rule. Without JavaScript, CSS still follows the device and the inactive control stays hidden. The sky video follows the selected theme and retains its independent pause and reduced-motion settings. No preference is transmitted.
