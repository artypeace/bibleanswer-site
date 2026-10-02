# Screenshots

The home page of every language has a "screens" strip (iPhone, iPad, Mac). Only existing real screenshots are displayed; missing slots are omitted. As soon as a file is there, the page picks it up on the next
`python3 tools/build.py` (nothing else to edit).

**The easy way:** the app repository already makes the App Store screenshots (`tools/store-screenshots/`, with its own
README). Run it on the Mac, then in this repository:

    python3 tools/import_screens.py ~/path/to/store-screenshots --default en

It converts the app's own pictures to light WebP and puts them here, and also in `assets/story/` (the phone that follows
the page) and `assets/mac/` (the Mac window). See `tools/import_screens.py` for which frame goes where.

**By hand:**

```
assets/screens/<device>/<lang>/<n>.webp      (or .png / .jpg)

device  iphone   n = 1..4    1320 x 2868  (the App Store size for iPhone 6.9")
        ipad     n = 1..2    2064 x 2752  (13")
        mac      n = 1..3    2880 x 1800
lang    en  ru  es  pt  fr  fil
```

The pictures must be real screens of the app, in the page's own language (the interface, that language's verse).
If you put the full-size App Store originals here, the page would load a few megabytes per picture: put light copies in
`assets/screens/web/<device>/<lang>/<n>.webp` (same names; the build prefers `web/`) or run
`python3 tools/optimize_screens.py`.
