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
    s = re.sub(r'\\u\{([0-9A-Fa-f]+)\}', lambda m: chr(int(m.group(1), 16)), s)
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

# ---------- the Mac sidebar: MacNavigation.swift lists the sections; their titles come from MacWords, AdviceWords and the app's own words
def func_body(text, name):
    """The source of `func name(...)` up to the next function."""
    m = re.search(r'(?:static |private |fileprivate )*func %s\(' % re.escape(name), text)
    i = m.start()
    n = re.search(r'\n\s*(?:static |private |fileprivate )*func \w+\(', text[m.end():])
    return text[i:m.end() + n.start() if n else len(text)]


mac_words = (app / 'BibleAnswerMac/MacWords.swift').read_text(encoding='utf-8')
mac_answer = switch_values(func_body(mac_words, 'answer'))
mac_listen = switch_values(func_body(mac_words, 'listen'))
advice_src = (app / 'BibleAnswer/Views/AdviceView.swift').read_text(encoding='utf-8')
mac_advice = switch_values(func_body(advice_src[advice_src.index('enum AdviceWords'):], 'menuTitle'))

# ---------- what is inside: the Guide, the three readings, the advice, the reading plans - the app's own words and the server's own counts
ORDER = ['ru', 'en', 'es', 'pt', 'fr', 'fil']          # BiblePlaces.index(language): the order of the arrays in GuideDestinationNames.swift


def cases(text, names):
    """text split at `case .a:` / `case "a":` markers -> {name: block}"""
    marks = []
    for n in names:
        m = re.search(r'case (?:\.%s|"%s"):' % (n, n), text)
        marks.append((n, m.start() if m else -1))
    marks = sorted((m for m in marks if m[1] >= 0), key=lambda x: x[1])
    return {n: text[i:(marks[k + 1][1] if k + 1 < len(marks) else len(text))] for k, (n, i) in enumerate(marks)}


def array_values(block):
    m = re.search(r'\[((?:"(?:[^"\\]|\\.)*",?\s*){6})\]\[BiblePlaces\.index', block)
    items = re.findall(r'"((?:[^"\\]|\\.)*)"', m.group(1))
    return {l: typo(unescape(t)) for l, t in zip(ORDER, items)}


def values(block):
    return array_values(block) if 'BiblePlaces.index' in block else switch_values(block)


gdn = (app / 'BibleAnswer/Views/Components/GuideDestinationNames.swift').read_text(encoding='utf-8')
gsvc = (app / 'BibleAnswer/Services/GuideService.swift').read_text(encoding='utf-8')
gview = (app / 'BibleAnswer/Views/GuideView.swift').read_text(encoding='utf-8')
guide_items = {}   # key -> {title: {lang: ..}, summary: {lang: ..}}
topic_title = cases(func_body(gsvc, 'title'), ['intro', 'story', 'howto'])
topic_summary = cases(func_body(gsvc, 'summary'), ['intro', 'story', 'howto'])
for k in ('intro', 'story', 'howto'):
    guide_items[k] = {'title': switch_values(topic_title[k]), 'summary': switch_values(topic_summary[k])}
for k, name in (('people', 'People'), ('timeline', 'Timeline'), ('map', 'Map'), ('words', 'Words')):
    guide_items[k] = {'title': switch_values(func_body(gdn, f'switch{name}Title')), 'summary': switch_values(func_body(gdn, f'switch{name}Summary'))}
dest_title = cases(func_body(gdn, 'title'), ['genealogy'])['genealogy']
dest_summary = cases(func_body(gdn, 'summary'), ['genealogy'])['genealogy']
guide_items['genealogy'] = {'title': array_values(dest_title), 'summary': array_values(dest_summary)}
GUIDE_ORDER = ['intro', 'story', 'howto', 'timeline', 'people', 'words', 'map', 'genealogy']   # the app's own order in the menu, plus the plates
guide_menu_title = switch_values(re.search(r'private var menuTitle: String \{.*?\n    \}', gview, re.S).group(0))
guide_menu_lead = switch_values(re.search(r'private var menuLead: String \{.*?\n    \}', gview, re.S).group(0))

advice_lead = switch_values(func_body(advice_src[advice_src.index('enum AdviceWords'):], 'menuLead'))
lens_captions = {}
vi_cap = vi[vi.index('func caption(for language'):]
for case in CASES:
    i = vi_cap.index(f'case .{case}:')
    later = [vi_cap.find(f'case .{c}:', i + 1) for c in CASES if c != case]
    later = [n for n in later if n > i]
    lens_captions[case] = switch_values(vi_cap[i:min(later) if later else len(vi_cap)])

plan_src = (app / 'BibleAnswer/Models/ReadingPlan.swift').read_text(encoding='utf-8')
PLANS = ['mark', 'john', 'proverbs', 'psalms', 'newTestament']
def plan_cases(body):
    """mark, john, proverbs, psalms are `case "id":` of the outer switch; the New Testament is its `default:` (the last one)."""
    cut = body.rindex('default:\n')
    got = cases(body[:cut], PLANS[:4])
    got['newTestament'] = body[cut:]
    return got
plan_title = plan_cases(func_body(plan_src, 'title'))
plan_summary = plan_cases(func_body(plan_src, 'summary'))
def days_of(pid):
    m = re.search(r'id: "%s",\s*days: \((\d+)\.\.\.(\d+)\)' % pid, plan_src)
    if m:
        return int(m.group(2))
    if pid == 'psalms':
        return len(re.findall(r'\d+', re.search(r'id: "psalms",\s*days: \[(.*?)\]', plan_src, re.S).group(1)))
    # the New Testament: about three chapters a day, never across two books (ReadingPlan.newTestament); the canon's 27 books
    nt = [28, 16, 24, 21, 28, 16, 16, 13, 6, 6, 4, 4, 5, 3, 6, 4, 3, 1, 13, 5, 5, 3, 5, 1, 1, 1, 22]
    target = -(-sum(nt) // 90)
    return sum(-(-c // target) for c in nt)
plan_days = {pid: days_of(pid) for pid in PLANS}
rp_view = (app / 'BibleAnswer/Views/ReadingPlanView.swift').read_text(encoding='utf-8')
plans_screen_title = switch_values(re.search(r'private var screenTitle: String \{.*?\n    \}', rp_view, re.S).group(0))
plans_lead = switch_values(re.search(r'private var lead: String \{.*?\n    \}', rp_view, re.S).group(0))

content = server / 'content'
def count(name, key):
    return len(json.loads((content / f'{name}.en.json').read_text(encoding='utf-8'))[key])
counts = {'eras': count('timeline', 'eras'), 'people': count('people', 'people'), 'terms': count('glossary', 'terms'),
          'places': count('places', 'places'), 'topics': len(list(content.glob('advice.*.en.json')))}
adv_topics = sorted(p.name.split('.')[1] for p in content.glob('advice.*.en.json'))
adv_titles = {l: [json.loads((content / f'advice.{t}.{l}.json').read_text(encoding='utf-8'))['title'] for t in adv_topics] for l in LANGS}

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
    bible = (grab(blocks[SWIFT[lang]], 'tabBible') if lang != 'en' else None) or grab(english_strings, 'tabBible')
    saved = (grab(blocks[SWIFT[lang]], 'savedVersesNav') if lang != 'en' else None) or grab(english_strings, 'savedVersesNav')
    d['inside'] = {
        'guide': {'title': guide_menu_title[lang], 'lead': guide_menu_lead[lang],
                  'items': [{'key': k, 'title': guide_items[k]['title'][lang], 'summary': guide_items[k]['summary'][lang]} for k in GUIDE_ORDER]},
        'lenses': [{'name': lens[i][lang], 'caption': lens_captions[c][lang]} for i, c in enumerate(CASES)],
        'advice': {'title': mac_advice[lang], 'lead': advice_lead[lang], 'topics': adv_titles[lang]},
        'plans': {'title': plans_screen_title[lang], 'lead': plans_lead[lang],
                  'items': [{'id': pid, 'title': switch_values(plan_title[pid])[lang], 'summary': switch_values(plan_summary[pid])[lang], 'days': plan_days[pid]} for pid in PLANS]},
        'counts': counts,
    }
    d['macSidebar'] = [mac_answer[lang], bible, mac_advice[lang], mac_listen[lang], saved]   # Answer, Bible, Advice, Listen, Saved
    out[lang] = d
out_path.write_text(json.dumps(out, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
print('wrote', out_path)
for lang in LANGS:
    d = out[lang]
    print(f'  {lang:3}', '|', ', '.join(d['lens']), '|', ', '.join(d['hours']), '|', ', '.join(d['topics']), '|', ', '.join(d['macSidebar']))
