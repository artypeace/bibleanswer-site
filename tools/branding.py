"""Shared visible local names; Bible Answer remains the primary site name."""
import html
import json
from pathlib import Path

COPY = json.loads((Path(__file__).parent / 'site-strings.json').read_text('utf-8'))


def local_name(lang):
    return COPY[lang].get('localName', '')


def alternate_names():
    return [row['localName'] for row in COPY.values() if row.get('localName')]


def footer_brand(lang, href):
    alias = local_name(lang)
    href = html.escape(href, quote=True)
    if not alias:
        return f'<a class="foot__brand" href="{href}">Bible Answer</a>'
    return (f'<a class="foot__brand foot__brand--localized" href="{href}">'
            '<span lang="en">Bible Answer</span>'
            '<span class="foot__separator" aria-hidden="true">|</span>'
            f'<span class="foot__local-name" lang="{COPY[lang]["htmlLang"]}">{html.escape(alias)}</span></a>')
