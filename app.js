/* Bible Answer — the website. Cosmetic only: words that rise, the phone that follows the page, parallax and the
   timing of the example. Every page is complete without it. The sky turns in CSS (site.css); there are no third-party requests. */
(() => {
  'use strict';

  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const $ = id => document.getElementById(id);
  const clamp = (v, a, b) => Math.min(b, Math.max(a, v));

  /** Adds a class to elements as they come into view, once. */
  function onView(selector, cls, options) {
    const items = document.querySelectorAll(selector);
    if (!('IntersectionObserver' in window) || reduced) { items.forEach(n => n.classList.add(cls)); return; }
    const io = new IntersectionObserver(entries => {
      entries.forEach(en => { if (en.isIntersecting) { en.target.classList.add(cls); io.unobserve(en.target); } });
    }, options);
    items.forEach(n => io.observe(n));
  }

  /* ---------------------------------------------------------------- the story: which step is on, which scene shows */
  function story() {
    const root = document.querySelector('.story');
    if (!root) return;
    const steps = [...root.querySelectorAll('.step')];
    const scenes = [...root.querySelectorAll('.scene')];
    const dots = [...root.querySelectorAll('.story__dots li')];
    let cur = -1;
    const show = i => {
      if (i === cur || i < 0) return;
      cur = i;
      steps.forEach((s, k) => s.classList.toggle('is-on', k === i));
      scenes.forEach((s, k) => {
        s.classList.toggle('on', k === i);
        const v = s.querySelector('video');
        if (v) { if (k === i && !reduced) v.play().catch(() => {}); else v.pause(); }
      });
      dots.forEach((d, k) => d.classList.toggle('on', k === i));
    };
    show(0);
    if ('IntersectionObserver' in window) {
      const io = new IntersectionObserver(entries => {
        entries.forEach(en => { if (en.isIntersecting) show(steps.indexOf(en.target)); });
      }, { rootMargin: '-46% 0px -46% 0px' });
      steps.forEach(s => io.observe(s));
    }
    if (reduced) return;
    // the phone leans a little as you pass: progress through the section, 0..1
    let queued = false;
    const frame = () => {
      queued = false;
      const r = root.getBoundingClientRect();
      root.style.setProperty('--sp', clamp((innerHeight * 0.5 - r.top) / Math.max(1, r.height), 0, 1).toFixed(3));
    };
    const onScroll = () => { if (!queued) { queued = true; requestAnimationFrame(frame); } };
    addEventListener('scroll', onScroll, { passive: true });
    addEventListener('resize', onScroll);
    frame();
  }

  /* ---------------------------------------------------------------- scroll: the hero leaves, the art drifts */
  function scrollEffects() {
    if (reduced) return;
    const root = document.documentElement;
    const hero = document.querySelector('.hero');
    const floaters = Array.from(document.querySelectorAll('[data-parallax]'));
    let queued = false;
    const frame = () => {
      queued = false;
      const y = window.scrollY;
      root.style.setProperty('--scroll', y.toFixed(1));
      if (hero) root.style.setProperty('--hp', clamp(y / (hero.offsetHeight * 0.7), 0, 1).toFixed(3));
      const vh = window.innerHeight;
      floaters.forEach(f => {
        const r = f.getBoundingClientRect();
        if (r.bottom < -240 || r.top > vh + 240) return;
        f.style.setProperty('--py', ((r.top + r.height / 2 - vh / 2) * -0.06).toFixed(1));
      });
    };
    const onScroll = () => { if (!queued) { queued = true; requestAnimationFrame(frame); } };
    addEventListener('scroll', onScroll, { passive: true });
    addEventListener('resize', onScroll);
    frame();
  }

  /* ---------------------------------------------------------------- the buttons lean toward the pointer */
  function magnet() {
    if (reduced || !matchMedia('(hover: hover) and (pointer: fine)').matches) return;
    document.querySelectorAll('.hero__cta .badge, .hero__cta .btn, .cta .badge, .cta .btn').forEach(el => {
      el.addEventListener('pointermove', e => {
        const r = el.getBoundingClientRect();
        el.style.transform = `translate(${(((e.clientX - r.left) / r.width - 0.5) * 12).toFixed(1)}px,${(((e.clientY - r.top) / r.height - 0.5) * 9).toFixed(1)}px)`;
      });
      el.addEventListener('pointerleave', () => { el.style.transform = ''; });
    });
  }

  /* ---------------------------------------------------------------- the Mac window: one section after another */
  function mac() {
    const w = document.querySelector('[data-mac]');
    if (!w) return;
    const scenes = [...w.querySelectorAll('.mscene, .macwin__shot')];
    const items = [...w.querySelectorAll('.macwin__side li')];
    if (scenes.length < 2) return;
    let i = 0, timer = null;
    const show = k => { i = k; scenes.forEach((s, j) => s.classList.toggle('on', j === k)); items.forEach((l, j) => l.classList.toggle('on', j === k)); };
    const start = () => { if (!timer && !reduced) timer = setInterval(() => show((i + 1) % scenes.length), 4300); };
    const stop = () => { clearInterval(timer); timer = null; };
    if ('IntersectionObserver' in window) new IntersectionObserver(es => es.forEach(e => (e.isIntersecting ? start() : stop())), { threshold: 0.35 }).observe(w);
    show(0);
  }

  /* ---------------------------------------------------------------- the counts run up once, when they come into view */
  function counters() {
    const items = [...document.querySelectorAll('[data-count]')];
    if (!items.length || reduced || !('IntersectionObserver' in window)) return;
    const io = new IntersectionObserver(entries => entries.forEach(en => {
      if (!en.isIntersecting) return;
      io.unobserve(en.target);
      const el = en.target, n = +el.dataset.count, t0 = performance.now();
      const tick = t => { const k = clamp((t - t0) / 1300, 0, 1); el.textContent = Math.round(n * (1 - Math.pow(1 - k, 3))); if (k < 1) requestAnimationFrame(tick); };
      requestAnimationFrame(tick);
    }), { threshold: 0.6 });
    items.forEach(n => io.observe(n));
  }

  /* ---------------------------------------------------------------- "Copy" buttons (the press page): the text is on the page without them */
  function copiers() {
    document.querySelectorAll('[data-copy]').forEach(btn => {
      const src = document.getElementById(btn.dataset.copy);
      if (!src) return;
      btn.hidden = false;
      const label = btn.textContent;
      btn.addEventListener('click', async () => {
        let ok = false;
        try { await navigator.clipboard.writeText(src.textContent.trim()); ok = true; } catch (err) {
          const r = document.createRange(); r.selectNodeContents(src);
          const sel = getSelection(); sel.removeAllRanges(); sel.addRange(r);
          try { ok = document.execCommand('copy'); } catch (err2) { /* the text stays selected */ }
        }
        btn.textContent = ok ? btn.dataset.done : label;
        setTimeout(() => { btn.textContent = label; }, 1800);
      });
    });
  }

  copiers();
  onView('.reveal', 'in', { threshold: 0.12, rootMargin: '0px 0px -6% 0px' });
  onView('.split:not(.split--hero)', 'in', { threshold: 0.5, rootMargin: '0px 0px -8% 0px' });
  onView('[data-demo]', 'is-playing', { threshold: 0.3 });
  story();
  mac();
  counters();
  scrollEffects();
  magnet();
})();
