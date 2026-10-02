# Official "Download on the App Store" badges

Apple's own artwork, black badge, unmodified, one file per language: `app-store-<lang>.svg`
(en, ru, es, pt = Brazilian Portuguese, fr, fil = Apple's Philippines/Tagalog badge).

Source: Apple's Marketing Tools (https://toolbox.marketingtools.apple.com/en-us/app-store), e.g.
`https://toolbox.marketingtools.apple.com/api/v2/badges/download-on-the-app-store/black/ru-ru`
(locales used: en-us, ru-ru, es-es, pt-br, fr-fr, tl-ph).

Do not redraw, recolour, re-typeset or stretch the badge (Apple's marketing guidelines). If a language has no file,
the page falls back to the English badge; with no file at all it shows a plain gold button in the page's language.

`python3 tools/build.py` picks the files up by itself.
