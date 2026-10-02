# Screenshots

The home page of every language has a "screens" strip. Until a file exists, a quiet placeholder with the app
icon is shown in its place; as soon as a file is there, the page picks it up on the next
`python3 tools/build.py` (nothing else to edit).

```
assets/screens/<device>/<lang>/<n>.png      (or .webp / .jpg)

device  iphone   n = 1..4    1320 x 2868  (the App Store size for iPhone 6.9")
        ipad     n = 1..2    2064 x 2752  (the App Store size for iPad 13")
lang    en  ru  es  pt  fr  fil
```

Mac is not shown yet ("coming soon" on the page). When it is released, the slots for 2880 x 1800 shots are
added in `tools/build.py` (`SHOTS`, `SHOT_SIZE`).

Smaller copies for the web
--------------------------
The App Store originals are large. If you put them here, the page would load a few megabytes per picture.
Put lighter copies in `assets/screens/web/<device>/<lang>/<n>.webp` (same names) — the build prefers
`web/` when it exists — or run

    python3 tools/optimize_screens.py

which writes them for you (about 60–120 KB each at the same pixel size).

The pictures must be real screens of the app — nothing drawn, nothing from a mock-up that the app does
not show — and in the page's own language (the app in that language, with that language's verse).
