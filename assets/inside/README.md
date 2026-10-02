# Feature previews

The Guide and Three readings use the existing native captures in `assets/story/`.
Advice shows the native Money article. Reading plans shows the native plan picker.
The new screens were captured on 2026-10-02 in the iPhone 17 Pro Max simulator
(iOS 26.3), from Bible Answer’s own Debug app. All six languages were individually
viewed and checked before import. No Springboard prompts, debug overlays, crashes
or personal conversations are present.

Capture routes: `-debugGuide plan`, `-debugAdvice money`; daily verse uses the
app’s `-debugOpenURL bibleanswer://verse` and `-debugVerseOfDay "LAM 3 22 23"`.
Use the app route rather than `simctl openurl`, which can show a system prompt.

`tools/import_feature_previews.py` proportionally downscales complete 1320×2868
native PNGs to 720px wide and encodes WebP. There is no creative crop, upscaling,
retouching, composited text or generated UI. Sources and hashes: `sources.json`.
Raw PNGs stay outside the public repository.

The decorative photographs, engravings and manuscript come from Bible Answer’s
existing plate library (public domain or CC0, as documented by the app). Plan
thumbnails use the same artwork as the native app. Background plates can be
cropped and faded; the native screenshots are displayed with `object-fit: contain`.
