# Official "Download on the App Store" badges

Apple's own artwork, one file per language, named `app-store-<lang>.svg`:

    app-store-en.svg  app-store-ru.svg  app-store-es.svg
    app-store-pt.svg  app-store-fr.svg  app-store-fil.svg   (fil: Apple has no Filipino badge — the English one is used)

Where to get them: https://tools.applemarketingtools.com/ -> App Store -> "Download on the App Store" ->
pick the language, "SVG", and save the file here under the name above. Do not redraw, recolour or
re-typeset the badge (Apple's marketing guidelines); do not stretch it. Until the files are here, the
pages show a plain gold "Download on the App Store" button in the page's language.

`python3 tools/build.py` picks the files up by itself.
