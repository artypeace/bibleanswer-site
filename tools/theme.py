"""Shared, localized appearance control. No remote assets or inline event handlers."""
from html import escape

LABELS = {
    'en': ('Appearance', 'Light', 'Dark', 'Use device settings'),
    'ru': ('Тема сайта', 'Светлая', 'Тёмная', 'Как на устройстве'),
    'es': ('Apariencia', 'Claro', 'Oscuro', 'Como el dispositivo'),
    'pt': ('Aparência', 'Claro', 'Escuro', 'Como no dispositivo'),
    'fr': ('Apparence', 'Clair', 'Sombre', 'Selon l’appareil'),
    'fil': ('Tema', 'Maliwanag', 'Madilim', 'Gaya ng device'),
}
PATHS = {
    'light': '<circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M2 12h2m16 0h2M4.9 4.9l1.4 1.4m11.4 11.4 1.4 1.4M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
    'dark': '<path d="M20.6 14.2A8.9 8.9 0 0 1 9.8 3.4 9 9 0 1 0 20.6 14.2Z"/><path d="M17 3v4m-2-2h4"/>',
    'auto': '<rect x="3" y="4" width="18" height="13" rx="3"/><path d="M8 21h8m-4-4v4M12 7v7"/>',
    'check': '<path d="m5 12 4 4L19 6"/>',
}

def icon(kind, cls=''):
    return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true">{PATHS[kind]}</svg>'

def control(lang):
    title, light, dark, auto = LABELS[lang]
    options = ''.join(
        f'<button type="button" data-theme-choice="{value}" aria-pressed="false">'
        + icon(value, 'theme-menu__option-icon')
        + f'<span class="theme-menu__label">{escape(label)}</span>'
        + icon('check', 'theme-menu__check') + '</button>'
        for value, label in [('light', light), ('dark', dark), ('auto', auto)])
    return (f'<details class="theme-menu" data-theme-menu hidden>'
            f'<summary aria-label="{escape(title)}" title="{escape(title)}">'
            '<span class="theme-menu__orb" aria-hidden="true">'
            + icon('light', 'theme-menu__sun') + icon('dark', 'theme-menu__moon')
            + '<i class="theme-menu__auto-dot"></i></span></summary>'
            f'<div class="theme-menu__panel"><p class="theme-menu__heading">{escape(title)}</p>'
            f'<div class="theme-menu__choices" role="group" aria-label="{escape(title)}">{options}</div></div></details>')
