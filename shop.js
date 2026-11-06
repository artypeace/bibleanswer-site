/* First Drop: the photographs, the size and the way to order. No cart, requests, stock or analytics:
   choosing a size only marks it, and the order is written by the person in Instagram. */
(() => {
  'use strict';
  const looks = document.querySelector('.looks');
  if (!looks) return;
  const photos = JSON.parse(looks.dataset.photos);
  const track = looks.querySelector('.looks-track');
  const thumbs = [...looks.querySelectorAll('.looks-thumbs button')];
  const motion = matchMedia('(prefers-reduced-motion: reduce)');
  let frame = 0;
  track.addEventListener('scroll', () => {
    if (frame) return;
    frame = requestAnimationFrame(() => {
      frame = 0;
      const active = Math.round(track.scrollLeft / Math.max(track.clientWidth, 1));
      thumbs.forEach((button, i) => button.setAttribute('aria-pressed', String(i === active)));
    });
  }, { passive: true });
  thumbs.forEach(button => button.addEventListener('click', () => {
    const slide = document.getElementById(button.getAttribute('aria-controls'));
    track.scrollTo({ left: slide.offsetLeft, behavior: motion.matches ? 'instant' : 'smooth' });
  }));

  // The size goes into the order button's words, so the message is clear before it is written.
  const cta = document.querySelector('.buy-cta');
  const ctaText = cta && cta.querySelector('[data-cta]');
  const base = ctaText ? ctaText.textContent : '';
  const mobileCta = document.querySelector('[data-mobile-cta]');
  document.querySelectorAll('input[name="size"]').forEach(input => {
    input.addEventListener('change', () => {
      if (ctaText) ctaText.textContent = base + ' · ' + input.value;
      if (mobileCta) {
        mobileCta.textContent = mobileCta.dataset.orderLabel + ' · ' + input.value;
        mobileCta.href = mobileCta.dataset.order;
        mobileCta.target = '_blank';
        mobileCta.rel = 'noopener noreferrer';
      }
    });
  });

  // One purchase action at a time on a phone: the bar hides while the real button, the questions
  // or a full photograph are on screen.
  const bar = document.querySelector('.mobile-buy');
  const dialog = document.querySelector('.photo-dialog');
  const narrow = matchMedia('(max-width: 999px)');
  if (bar && 'IntersectionObserver' in window) {
    let ctaSeen = false, foldsSeen = false;
    const update = () => { bar.hidden = !narrow.matches || ctaSeen || foldsSeen || Boolean(dialog && dialog.open); };
    const io = new IntersectionObserver(entries => {
      entries.forEach(e => {
        if (e.target.matches('.buy-cta')) ctaSeen = e.isIntersecting;
        if (e.target.matches('.folds')) foldsSeen = e.isIntersecting;
      });
      update();
    });
    io.observe(cta);
    io.observe(document.querySelector('.folds'));
    narrow.addEventListener('change', update);
    if (dialog) dialog.addEventListener('close', update);
  }

  // A photograph, whole.
  if (!dialog || typeof dialog.showModal !== 'function') return;
  const img = dialog.querySelector('img');
  document.querySelectorAll('[data-zoom]').forEach(link => {
    link.addEventListener('click', event => {
      event.preventDefault();
      const p = photos[Number(link.dataset.zoom)];
      img.src = p.full;
      img.alt = p.alt;
      if (bar) bar.hidden = true;
      dialog.showModal();
    });
  });
  dialog.querySelector('.photo-close').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => { if (event.target === dialog || event.target === img) dialog.close(); });
})();
