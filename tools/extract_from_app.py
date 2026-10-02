#!/usr/bin/env python3
"""Reads the words the website shares with the app out of the app's and the server's own
sources and writes tools/app-strings.json. Run it when the app's wording changes:

    python3 tools/extract_from_app.py /path/to/bible-answer /path/to/bible-answer-server

Nothing in app-strings.json is written by hand. The website's own copy lives in
site-strings.json. Standard library only; the two repositories are only read."""
import json, pathlib, re, sys

app = pathlib.Path(sys.argv[1])
server = pathlib.Path(sys.argv[2])
out_path = pathlib.Path(__file__).with_name('app-strings.json')

LANGS = ['en', 'pt', 'es', 'ru', 'fr', 'fil']
SWIFT = {'en': 'english', 'pt': 'portuguese', 'es': 'spanish', 'ru': 'russian', 'fr': 'french', 'fil': 'filipino'}
NAMES = {'en': 'English', 'pt': 'Português', 'es': 'Español', 'ru': 'Русский', 'fr': 'Français', 'fil': 'Filipino'}
ENUM = {'russian': 'ru', 'spanish': 'es', 'french': 'fr', 'portuguese': 'pt', 'filipino': 'fil'}   # default -> en
KEYS = {
    'tagline': 'appTagline', 'subtitle': 'welcome_subtitle', 'prompt': 'welcome_prompt',
    'placeholder': 'inputPlaceholder', 'goodDays': 'feelingsGoodDays',
    'forYou': 'answerSectionForYou', 'context': 'answerSectionContext', 'prayer': 'answerSectionPrayer',
}


def unescape(s):
    return s.replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')


def typo(s):
    """A straight apostrophe between letters becomes a typographic one."""
    return re.sub(r"(?<=\w)'(?=\w)", '’', s)


# ---------- Localizable.swift: the tagline, the feelings and a few section names ----------
src = (app / 'BibleAnswer/Models/Localizable.swift').read_text(encoding='utf-8')
starts = [(m.group(1), m.start()) for m in re.finditer(r'static let (english|portuguese|spanish|russian|french|filipino) = ', src)]
starts.append(('end', len(src)))
english_strings = src[src.index('private static let englishStrings'):starts[0][1]]
blocks = {n: src[p:starts[i + 1][1]] for i, (n, p) in enumerate(starts[:-1])}


def grab(block, key):
    m = re.search(r'"%s":\s*"((?:[^"\\]|\\.)*)"' % key, block)
    return typo(unescape(m.group(1))) if m else None


def feelings(lang):
    b = blocks[SWIFT[lang]]
    i = b.index('feelings: feelings([')
    body = b[i:b.index('])', i)]
    pairs = re.findall(r'\("((?:[^"\\]|\\.)*)",\s*"((?:[^"\\]|\\.)*)"\)', body)
    assert len(pairs) == 19, (lang, len(pairs))
    return [{'label': typo(unescape(a)), 'query': typo(unescape(q))} for a, q in pairs]


# ---------- a Swift `switch language { case .russian: return "…" … default: return "…" }` ----------
def switch_values(block):
    out = {}
    for name, text in re.findall(r'case \.(\w+):\s*return "((?:[^"\\]|\\.)*)"', block):
        if name in ENUM:
            out[ENUM[name]] = typo(unescape(text))
    m = re.search(r'default:\s*return "((?:[^"\\]|\\.)*)"', block)
    if m:
        out['en'] = typo(unescape(m.group(1)))
    return out


# ---------- the three readings of a verse: VerseInterpretation.swift ----------
vi = (app / 'BibleAnswer/Models/VerseInterpretation.swift').read_text(encoding='utf-8')
title_fn = vi[vi.index('func title(for language'):vi.index('func caption(for language')]
CASES = ('theological', 'symbolic', 'application')
lens = []
for case in CASES:
    i = title_fn.index(f'case .{case}:')
    later = [title_fn.find(f'case .{c}:', i + 1) for c in CASES if c != case]
    later = [n for n in later if n > i]
    lens.append(switch_values(title_fn[i:min(later) if later else len(title_fn)]))

# ---------- the prayer of the hour: Shared/HourOfPrayer.swift ----------
hp = (app / 'Shared/HourOfPrayer.swift').read_text(encoding='utf-8')
heading_fn = hp[hp.index('func heading(_ language'):hp.index('// MARK: Scripture')]
hours = {l: {} for l in LANGS}
for lang, hour, text in re.findall(r'case \("(\w+)", \.(\w+)\):\s*return "((?:[^"\\]|\\.)*)"', heading_fn):
    hours[lang][hour] = typo(unescape(text))
for hour, text in re.findall(r'case \(_, \.(\w+)\):\s*return "((?:[^"\\]|\\.)*)"', heading_fn):
    hours['en'][hour] = typo(unescape(text))

# ---------- the pages of counsel: the server's own content ----------
TOPICS = ['family', 'work', 'money', 'words']
topics = {l: [json.loads((server / f'content/advice.{t}.{l}.json').read_text(encoding='utf-8'))['title'] for t in TOPICS] for l in LANGS}

out = {}
for lang in LANGS:
    d = {}
    for k, swift_key in KEYS.items():
        v = grab(blocks[SWIFT[lang]], swift_key) if lang != 'en' else None
        d[k] = v if v is not None else grab(english_strings, swift_key)
    d['name'] = NAMES[lang]
    d['feelings'] = feelings(lang)
    d['lens'] = [l[lang] for l in lens]
    d['hours'] = [hours[lang][h] for h in ('morning', 'midday', 'evening', 'night')]
    d['topics'] = topics[lang]
    out[lang] = d
out_path.write_text(json.dumps(out, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
print('wrote', out_path)
for lang in LANGS:
    d = out[lang]
    print(f'  {lang:3}', '|', ', '.join(d['lens']), '|', ', '.join(d['hours']), '|', ', '.join(d['topics']))
