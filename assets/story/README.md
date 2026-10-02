# Real screens for the phone on the home page

The pinned phone on the home page shows five scenes, one for each step of the story. Until a file is added here,
a drawn scene made of the app's own words and engravings is shown. Add a real screen recording or screenshot and the
page uses it instead (run `python3 tools/build.py`; nothing else to edit).

```
assets/story/<scene>/<lang>.webm   and/or  <lang>.mp4      a screen recording (muted loop, 5-15 s)
assets/story/<scene>/<lang>-poster.webp                    optional first-frame picture shown before it plays
assets/story/<scene>/<lang>.webp   (or .png / .jpg)        a screenshot instead of a video

scene   read   guide   counsel   quiet   hours
lang    en  ru  es  pt  fr  fil      or  default  (used for every language without its own file)
```

* Picture ratio: the phone's screen is 1320 x 2868 (iPhone 6.9"). Record a full-screen iPhone capture (QuickTime:
  File > New Movie Recording > iPhone, or Control Centre > Screen Recording) and crop to that ratio.
* Keep video light: about 1-2 MB each. Example with ffmpeg:
  `ffmpeg -i in.mov -an -vf "scale=660:-2,fps=30" -c:v libvpx-vp9 -b:v 0 -crf 34 out.webm` and, for Safari,
  `ffmpeg -i in.mov -an -vf "scale=660:-2,fps=30" -c:v libx264 -crf 26 -pix_fmt yuv420p -movflags +faststart out.mp4`.
  Provide both a `.webm` and an `.mp4` of the same name.
* A video plays only while its scene is on screen and pauses when you scroll away. With "reduce motion" set it does not
  autoplay. Nothing is loaded from another host.
* Record the app in the language of the page (the verse, the interface). The screens must be the real app.
