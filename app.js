/* Bible Answer — the website. Cosmetic only: a living sky, words that rise, the phone that follows the page, parallax
   and the timing of the example. Every page is complete without it, and it makes no requests of any kind. */
(() => {
  'use strict';

  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const $ = id => document.getElementById(id);
  const clamp = (v, a, b) => Math.min(b, Math.max(a, v));

  /* ---------------------------------------------------------------- the sky: stars with depth, a shooting star */
  function sky() {
    const host = $('stars');
    if (!host) return;
    const cv = document.createElement('canvas');
    cv.className = 'stars__cv';
    cv.setAttribute('aria-hidden', 'true');
    host.appendChild(cv);
    const ctx = cv.getContext('2d');
    if (!ctx) return;

    const light = matchMedia('(prefers-color-scheme: light)');
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    let seed = 20260928;   // fixed seed: the same sky on every visit
    const rnd = () => { seed |= 0; seed = (seed + 0x6D2B79F5) | 0; let x = Math.imul(seed ^ (seed >>> 15), 1 | seed); x = (x + Math.imul(x ^ (x >>> 7), 61 | x)) ^ x; return ((x ^ (x >>> 14)) >>> 0) / 4294967296; };
    let W = 0, H = 0, stars = [], shot = null, nextShot = 0, px = 0, py = 0, tx = 0, ty = 0, running = false;

    function layout() {
      W = host.clientWidth; H = host.clientHeight;
      if (!W || !H) return;
      cv.width = Math.round(W * dpr); cv.height = Math.round(H * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      const n = Math.round(Math.min(230, (W * H) / 8200));
      stars = Array.from({ length: n }, () => {
        const q = rnd();
        return { x: rnd(), y: rnd() * 0.92, z: q < 0.6 ? 0.3 : q < 0.9 ? 0.65 : 1, r: 0.5 + rnd() * 1.1, a: 0.35 + rnd() * 0.5, ph: rnd() * 6.283, sp: 0.4 + rnd() * 1.4, gold: rnd() < 0.12 };
      });
    }

    function draw(t) {
      ctx.clearRect(0, 0, W, H);
      px += (tx - px) * 0.04; py += (ty - py) * 0.04;
      for (const s of stars) {
        const drift = reduced ? 0 : t * 0.004 * s.z;
        const x = ((s.x * W + drift + px * s.z * 20) % W + W) % W;
        const y = s.y * H + py * s.z * 12;
        ctx.globalAlpha = s.a * (reduced ? 1 : 0.55 + 0.45 * Math.sin(t * 0.001 * s.sp + s.ph));
        ctx.fillStyle = s.gold ? '#E8C47A' : '#FFF3D6';
        ctx.beginPath(); ctx.arc(x, y, s.r * (0.8 + s.z * 0.5), 0, 6.283); ctx.fill();
      }
      if (!reduced) {
        if (!shot && t > nextShot) {
          shot = { x: W * (0.25 + rnd() * 0.6), y: H * (0.04 + rnd() * 0.26), a: 0.35 + rnd() * 0.25, t0: t, len: 150 + rnd() * 90 };
          nextShot = t + 7000 + rnd() * 6000;
        }
        if (shot) {
          const k = (t - shot.t0) / 950;
          if (k >= 1) shot = null;
          else {
            const d = k * 420, hx = shot.x + Math.cos(shot.a) * d, hy = shot.y + Math.sin(shot.a) * d;
            const tl = Math.min(shot.len, d), tailx = hx - Math.cos(shot.a) * tl, taily = hy - Math.sin(shot.a) * tl;
            const g = ctx.createLinearGradient(tailx, taily, hx, hy);
            g.addColorStop(0, 'rgba(255,243,214,0)'); g.addColorStop(1, 'rgba(255,243,214,.95)');
            ctx.globalAlpha = Math.sin(Math.PI * k);
            ctx.strokeStyle = g; ctx.lineWidth = 1.4; ctx.lineCap = 'round';
            ctx.beginPath(); ctx.moveTo(tailx, taily); ctx.lineTo(hx, hy); ctx.stroke();
          }
        }
      }
      ctx.globalAlpha = 1;
    }

    const active = () => !document.hidden && !light.matches && window.scrollY < window.innerHeight * 1.15;
    function loop(t) {
      if (!active()) { running = false; return; }
      draw(t);
      requestAnimationFrame(loop);
    }
    function wake() { if (!reduced && !running && active()) { running = true; requestAnimationFrame(loop); } }

    layout();
    draw(0);
    if (reduced) return;
    wake();
    addEventListener('scroll', wake, { passive: true });
    document.addEventListener('visibilitychange', wake);
    if (light.addEventListener) light.addEventListener('change', wake);
    let rz;
    addEventListener('resize', () => { clearTimeout(rz); rz = setTimeout(() => { layout(); draw(performance.now()); wake(); }, 150); });
    if (matchMedia('(hover: hover) and (pointer: fine)').matches) {
      addEventListener('pointermove', e => { tx = (e.clientX / innerWidth - 0.5) * 2; ty = (e.clientY / innerHeight - 0.5) * 2; }, { passive: true });
    }
  }

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

  sky();
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
