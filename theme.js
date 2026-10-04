/* Appearance is a local preference, shared by this site's pages. Set it before CSS paints. */
(() => {
  'use strict';
  const root = document.documentElement;
  const key = 'bible-answer-theme';
  const system = matchMedia('(prefers-color-scheme: dark)');
  const motion = matchMedia('(prefers-reduced-motion: reduce)');
  const valid = value => ['light', 'dark', 'auto'].includes(value);
  let preference = 'auto', timer;
  try { const saved = localStorage.getItem(key); if (valid(saved)) preference = saved; } catch (_) {}

  function apply(animate = false) {
    const theme = preference === 'auto' ? (system.matches ? 'dark' : 'light') : preference;
    const changed = root.dataset.theme !== theme;
    if (animate && changed && !motion.matches) {
      clearTimeout(timer);
      root.classList.add('theme-changing');
      timer = setTimeout(() => root.classList.remove('theme-changing'), 350);
    }
    root.dataset.theme = theme;
    root.dataset.themePreference = preference;
    root.style.colorScheme = theme;
    const meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.content = theme === 'dark' ? '#0F1628' : '#DCEDF6';
    document.querySelectorAll('[data-theme-menu]').forEach(menu => {
      menu.hidden = false;
      menu.querySelectorAll('[data-theme-choice]').forEach(button => {
        button.setAttribute('aria-pressed', String(button.dataset.themeChoice === preference));
      });
      const selected = menu.querySelector(`[data-theme-choice="${preference}"] .theme-menu__label`);
      const summary = menu.querySelector('summary');
      if (selected && summary) summary.title = `${summary.getAttribute('aria-label')} · ${selected.textContent}`;
    });
    if (changed) document.dispatchEvent(new Event('bible-theme-change'));
  }
  apply();

  const onSystemChange = () => { if (preference === 'auto') apply(true); };
  if (system.addEventListener) system.addEventListener('change', onSystemChange);
  else if (system.addListener) system.addListener(onSystemChange);
  addEventListener('storage', event => {
    if (event.key !== key && event.key !== null) return;
    preference = valid(event.newValue) ? event.newValue : 'auto';
    apply(true);
  });

  function bind() {
    const menus = [...document.querySelectorAll('[data-theme-menu]')];
    const close = (menu, focus = false) => {
      menu.open = false;
      if (focus) menu.querySelector('summary').focus();
    };
    menus.forEach(menu => {
      menu.querySelectorAll('[data-theme-choice]').forEach(button => {
        button.addEventListener('click', () => {
          preference = button.dataset.themeChoice;
          try { localStorage.setItem(key, preference); } catch (_) {}
          apply(true);
          close(menu, true);
        });
      });
      menu.addEventListener('keydown', event => {
        if (event.key === 'Escape' && menu.open) { event.preventDefault(); close(menu, true); }
      });
      menu.addEventListener('toggle', () => {
        if (menu.open) document.querySelectorAll('.langmenu[open], .article-language-menu[open]').forEach(other => { other.open = false; });
      });
      menu.addEventListener('focusout', event => {
        if (event.relatedTarget && !menu.contains(event.relatedTarget)) close(menu);
      });
    });
    document.addEventListener('pointerdown', event => {
      menus.forEach(menu => { if (menu.open && !menu.contains(event.target)) close(menu); });
    });
    apply();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', bind, { once: true });
  else bind();
})();
