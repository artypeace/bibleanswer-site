/* Website analytics only. Basic consent: no Google request before opt-in. */
(() => {
  'use strict';
  const script = document.currentScript;
  const id = script?.dataset.gaId || '';
  if (!/^G-[A-Z0-9]{6,20}$/.test(id)) return;
  const key = 'bibleanswer-website-analytics-v1';
  const copy = {
    "en": [
      "Cookies on this site",
      "Cookies help us improve this site.",
      "Accept",
      "Reject",
      "Settings",
      "Google Analytics receives information about visits, your browser and device. Analytics starts only after you accept. Your choice is saved for up to 180 days; you can change or withdraw it in Cookie settings at the bottom of any page.",
      "How Google uses data",
      "Close",
      "Cookie settings",
      "Privacy policy"
    ],
    "ru": [
      "Файлы cookie",
      "Мы используем cookie, чтобы улучшать сайт.",
      "Принять",
      "Отклонить",
      "Настроить",
      "Google Analytics получает сведения о посещениях, браузере и устройстве. Аналитика включается только с вашего согласия. Выбор сохраняется до 180 дней; изменить или отозвать его можно в «Настройках cookie» внизу страницы.",
      "Как Google использует данные",
      "Закрыть",
      "Настройки cookie",
      "Политика конфиденциальности"
    ],
    "es": [
      "Cookies en este sitio",
      "Usamos cookies para mejorar el sitio.",
      "Aceptar",
      "Rechazar",
      "Configurar",
      "Google Analytics recibe información sobre las visitas, el navegador y el dispositivo. Las estadísticas solo se activan si aceptas. Tu elección se guarda hasta 180 días; puedes cambiarla o retirar tu consentimiento en «Ajustes de cookies», al pie de cada página.",
      "Cómo usa Google los datos",
      "Cerrar",
      "Ajustes de cookies",
      "Política de privacidad"
    ],
    "pt": [
      "Cookies neste site",
      "Usamos cookies para melhorar o site.",
      "Aceitar",
      "Recusar",
      "Configurar",
      "O Google Analytics recebe informações sobre visitas, navegador e dispositivo. A análise só começa depois que você aceita. Sua escolha é salva por até 180 dias; você pode alterá-la ou retirar seu consentimento em «Configurações de cookies», no fim de cada página.",
      "Como o Google usa os dados",
      "Fechar",
      "Configurações de cookies",
      "Política de privacidade"
    ],
    "fr": [
      "Cookies sur ce site",
      "Des cookies pour améliorer ce site.",
      "Accepter",
      "Refuser",
      "Configurer",
      "Google Analytics reçoit des informations sur les visites, le navigateur et l’appareil. La mesure d’audience ne commence qu’avec ton accord. Ton choix est conservé jusqu’à 180 jours ; tu peux le modifier ou retirer ton accord via « Réglages des cookies », en bas de chaque page.",
      "Utilisation des données par Google",
      "Fermer",
      "Réglages des cookies",
      "Politique de confidentialité"
    ],
    "fil": [
      "Cookies sa website",
      "Cookies para mapabuti ang website.",
      "Pumayag",
      "Tumanggi",
      "Mga setting",
      "Tumatanggap ang Google Analytics ng impormasyon tungkol sa mga pagbisita, browser, at device. Nagsisimula lang ang pagsusuri kapag pumayag ka. Iniimbak ang pasya mo nang hanggang 180 araw; maaari mo itong baguhin o bawiin sa «Mga setting ng cookies» sa ibaba ng bawat pahina.",
      "Paggamit ng Google sa datos",
      "Isara",
      "Mga setting ng cookies",
      "Patakaran sa privacy"
    ]
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
  const title = document.createElement('h2'); title.textContent = t[0]; title.tabIndex = -1;
  const message = document.createElement('p'); message.className = 'ba-analytics-message'; message.textContent = t[1];
  const details = document.createElement('div'); details.className = 'ba-analytics-details'; details.id = 'ba-analytics-details'; details.hidden = true;
  const explanation = document.createElement('p'); explanation.textContent = t[5];
  const policy = document.createElement('a'); policy.href = '/privacy#website-analytics-' + (copy[language] ? language : 'en'); policy.textContent = t[9];
  const googlePolicy = document.createElement('a'); googlePolicy.href = 'https://policies.google.com/technologies/partner-sites'; googlePolicy.rel = 'noopener noreferrer'; googlePolicy.textContent = t[6];
  const links = document.createElement('div'); links.className = 'ba-analytics-links'; links.append(policy, googlePolicy);
  details.append(explanation, links);
  const actions = document.createElement('div'); actions.className = 'ba-analytics-actions';
  const yes = document.createElement('button'); yes.type = 'button'; yes.textContent = t[2];
  const no = document.createElement('button'); no.type = 'button'; no.textContent = t[3];
  const configure = document.createElement('button'); configure.type = 'button'; configure.textContent = t[4]; configure.setAttribute('aria-controls', details.id);
  const close = document.createElement('button'); close.type = 'button'; close.textContent = t[7]; close.hidden = true;
  actions.append(yes, no, configure, close); panel.append(title, message, details, actions);
  const settings = document.createElement('button'); settings.type = 'button'; settings.className = 'ba-analytics-settings'; settings.textContent = t[8];
  function showDetails(expanded) {
    details.hidden = !expanded;
    configure.hidden = expanded;
    close.hidden = !expanded;
    panel.className = 'ba-analytics-panel' + (expanded ? ' ba-analytics-panel--expanded' : '');
    (expanded ? title : configure).focus({preventScroll:true});
  }
  function closeDetails() {
    if (choice) { panel.hidden = true; settings.focus({preventScroll:true}); }
    else { showDetails(false); }
  }
  configure.addEventListener('click', () => showDetails(true));
  settings.addEventListener('click', () => { panel.hidden = false; showDetails(true); });
  close.addEventListener('click', closeDetails);
  panel.addEventListener('keydown', event => {
    if (event.key === 'Escape' && !details.hidden) { event.preventDefault(); closeDetails(); }
  });
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
