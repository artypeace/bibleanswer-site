(() => {
  const input = document.getElementById('guide-search');
  if (!input) return;
  const controls = input.closest('.guide-search');
  const empty = controls.querySelector('[role="status"]');
  const normalize = value => value.toLowerCase().normalize('NFKD').replace(/\p{M}/gu, '');
  const guides = [...document.querySelectorAll('[data-guide-search]')]
    .map(card => [card, normalize(card.dataset.guideSearch)]);

  function filter() {
    const words = normalize(input.value).match(/[\p{L}\p{N}:]+/gu) ?? [];
    let visible = 0;
    for (const [card, index] of guides) {
      card.hidden = !words.every(word => index.includes(word));
      if (!card.hidden) visible++;
    }
    empty.hidden = visible > 0;
  }

  input.addEventListener('input', filter);
  controls.hidden = false;
  filter();
})();
