/* Website analytics only. Basic consent: no Google request before opt-in. */
(() => {
  'use strict';
  const script = document.currentScript;
  const id = script?.dataset.gaId || '';
  if (!/^G-[A-Z0-9]{6,20}$/.test(id)) return;
  const key = 'bibleanswer-website-analytics-v1';
  const copy = {
    en: ['Website analytics', 'May we use Google Analytics to understand visits and improve this website?', 'Allow analytics', 'No, thanks', 'Analytics settings', 'Google receives visit, browser and device information and uses cookies to distinguish visits. This choice applies to the website. You can change it here at any time.', 'How Google uses data', 'Close'],
    ru: ['Статистика сайта', 'Разрешить Google Analytics, чтобы понимать посещаемость и улучшать сайт?', 'Разрешить статистику', 'Нет, спасибо', 'Настройки статистики', 'Google получает сведения о посещениях, браузере и устройстве и использует cookies, чтобы различать посещения. Этот выбор относится к сайту. Его можно изменить здесь в любой момент.', 'Как Google использует данные', 'Закрыть'],
    es: ['Estadísticas del sitio', '¿Nos permites usar Google Analytics para conocer las visitas y mejorar este sitio?', 'Permitir estadísticas', 'No, gracias', 'Configurar estadísticas', 'Google recibe información sobre las visitas, el navegador y el dispositivo, y usa cookies para distinguir las visitas. Esta elección se aplica al sitio web. Puedes cambiarla aquí cuando quieras.', 'Cómo usa Google los datos', 'Cerrar'],
    pt: ['Estatísticas do site', 'Você permite o uso do Google Analytics para entender as visitas e melhorar este site?', 'Permitir estatísticas', 'Não, obrigado', 'Configurar estatísticas', 'O Google recebe informações sobre visitas, navegador e dispositivo e usa cookies para distinguir as visitas. Essa escolha vale para o site. Você pode alterá-la aqui a qualquer momento.', 'Como o Google usa os dados', 'Fechar'],
    fr: ['Statistiques du site', 'Acceptes-tu Google Analytics pour nous aider à comprendre les visites et à améliorer ce site ?', 'Accepter les statistiques', 'Non merci', 'Réglages des statistiques', 'Google reçoit des informations sur les visites, le navigateur et l’appareil, et utilise des cookies pour distinguer les visites. Ce choix concerne le site. Tu peux le modifier ici à tout moment.', 'Utilisation des données par Google', 'Fermer'],
    fil: ['Estadistika ng website', 'Papayagan mo ba ang Google Analytics upang maunawaan ang mga pagbisita at mapabuti ang website?', 'Payagan ang estadistika', 'Hindi, salamat', 'Mga setting ng estadistika', 'Tumatanggap ang Google ng impormasyon tungkol sa mga pagbisita, browser, at device. Gumagamit ito ng cookies upang matukoy ang magkakaibang pagbisita. Para sa website ang pasyang ito at maaari mo itong baguhin dito anumang oras.', 'Paggamit ng Google sa datos', 'Isara']
  };
  const language = (document.documentElement.lang || 'en').toLowerCase().split('-')[0];
  const t = copy[language] || copy.en;
  const denied = { analytics_storage: 'denied', ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied' };
  let choice = null;
  try { const saved = JSON.parse(localStorage.getItem(key)); if (saved && Date.now() - saved.time < 180 * 86400000 && ['granted','denied'].includes(saved.value)) choice = saved.value; } catch (_) {}
  let loaded = false;
  function tag() { window.dataLayer = window.dataLayer || []; window.dataLayer.push(arguments); }
  const cleanLocation = () => location.origin + location.pathname;
  const cleanReferrer = () => { try { const u = new URL(document.referrer); return u.origin + u.pathname; } catch (_) { return ''; } };
  function start() {
    if (loaded) return;
    loaded = true;
    window['ga-disable-' + id] = false;
    window.gtag = window.gtag || tag;
    tag('consent', 'default', denied);
    tag('consent', 'update', { ...denied, analytics_storage: 'granted' });
    tag('js', new Date());
    tag('config', id, { allow_google_signals: false, allow_ad_personalization_signals: false, page_location: cleanLocation(), page_referrer: cleanReferrer(), cookie_expires: 15552000, cookie_update: false });
    const google = document.createElement('script');
    google.async = true;
    google.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(id);
    document.head.appendChild(google);
  }
  function removeAnalyticsCookies() {
    const names = document.cookie.split(';').map(c => c.trim().split('=')[0]).filter(n => n === '_ga' || n.startsWith('_ga_'));
    const host = location.hostname.split('.');
    const domains = ['', ...host.map((_,i) => '.' + host.slice(i).join('.'))];
    names.forEach(name => domains.forEach(domain => { document.cookie = name + '=; Max-Age=0; Path=/; SameSite=Lax' + (domain ? '; Domain=' + domain : ''); }));
  }
  const panel = document.createElement('section');
  panel.className = 'ba-analytics-panel';
  panel.setAttribute('role', 'region');
  panel.setAttribute('aria-label', t[0]);
  const title = document.createElement('h2'); title.textContent = t[0];
  const message = document.createElement('p'); message.textContent = t[1];
  const details = document.createElement('details');
  const summary = document.createElement('summary'); summary.textContent = t[4];
  const explanation = document.createElement('p'); explanation.textContent = t[5];
  const policy = document.createElement('a'); policy.href = '/privacy#website-analytics-' + (copy[language] ? language : 'en'); policy.textContent = t[0];
  details.append(summary, explanation, policy);
  const actions = document.createElement('div'); actions.className = 'ba-analytics-actions';
  const yes = document.createElement('button'); yes.type = 'button'; yes.textContent = t[2];
  const no = document.createElement('button'); no.type = 'button'; no.textContent = t[3];
  const close = document.createElement('button'); close.type = 'button'; close.textContent = t[7]; close.hidden = !choice;
  actions.append(yes, no, close); panel.append(title, message, details, actions);
  const settings = document.createElement('button'); settings.type = 'button'; settings.className = 'ba-analytics-settings'; settings.textContent = t[4];
  settings.addEventListener('click', () => { panel.hidden = false; close.hidden = !choice; yes.focus({preventScroll:true}); });
  close.addEventListener('click', () => { panel.hidden = true; settings.focus({preventScroll:true}); });
  function setChoice(value) {
    choice = value;
    try { localStorage.setItem(key, JSON.stringify({value, time:Date.now()})); } catch (_) {}
    if (value === 'granted') {
      if (!loaded) start();
      else { window['ga-disable-' + id] = false; tag('consent', 'update', {...denied, analytics_storage: 'granted'}); }
    } else {
      window['ga-disable-' + id] = true;
      if (loaded) tag('consent', 'update', denied);
      removeAnalyticsCookies();
    }
    panel.hidden = true; settings.focus({preventScroll:true});
  }
  yes.addEventListener('click', () => setChoice('granted'));
  no.addEventListener('click', () => setChoice('denied'));
  panel.hidden = Boolean(choice);
  document.body.append(panel);
  const footer = document.querySelector('footer');
  (footer || document.body).append(settings);
  if (choice === 'granted') start();
})();
