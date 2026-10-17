/* Local behavior test: runs the consent code in a VM; never contacts Google. */
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const code = fs.readFileSync('analytics.js', 'utf8');
function boot({saved=null, lang='en', id='G-P0ZK25PW9Q', brokenStorage=false}={}) {
  class Element {
    constructor(tag) { this.tagName=tag; this.children=[]; this.handlers={}; this.hidden=false; this.dataset={}; }
    append(...els) { this.children.push(...els); }
    appendChild(el) { this.append(el); }
    setAttribute(k,v) { this[k]=v; }
    addEventListener(k,f) { this.handlers[k]=f; }
    focus(options) { state.focus=this; state.focusOptions=options; }
    click() { this.handlers.click?.(); }
    keydown(key) { const event={key,preventDefault(){state.keyPrevented=true;}}; this.handlers.keydown?.(event); }
  }
  const state={storage:saved ? JSON.stringify(saved):null, cookies:[],focus:null,focusOptions:null,keyPrevented:false};
  const head=new Element('head'), body=new Element('body'), footer=new Element('footer');
  const doc={currentScript:{dataset:{gaId:id}},documentElement:{lang}, referrer:'https://example.org/article?secret=value#fragment',head,body,querySelector:()=>footer,createElement:t=>new Element(t)};
  Object.defineProperty(doc,'cookie',{get:()=> '_ga=a; _ga_TEST=b; unrelated=yes',set:v=>state.cookies.push(v)});
  const window={};
  const storage={getItem(){if(brokenStorage)throw Error('blocked');return state.storage;},setItem(k,v){if(brokenStorage)throw Error('blocked');state.storage=v;}};
  vm.runInNewContext(code,{document:doc,window,localStorage:storage,location:{origin:'https://bibleanswer.app',pathname:'/ru/',hostname:'bibleanswer.app'},URL,Date,encodeURIComponent});
  return {...state,state,head,body,footer,window,panel:body.children[0], settings:footer.children[0]};
}
function visibleText(element) {
  if (element.hidden) return '';
  return [element.textContent || '', ...element.children.map(visibleText)].join(' ');
}
function controls(b) {
  const [title,message,details,actions]=b.panel.children;
  const [yes,no,configure,close]=actions.children;
  return {title,message,details,yes,no,configure,close};
}
const titles=new Set();
for (const lang of ['en','ru','es','pt-BR','fr','fil']) {
  const b=boot({lang});
  const {title,message,details,yes,no,configure,close}=controls(b);
  titles.add(title.textContent);
  assert.equal(b.head.children.length,0,`${lang}: no Google before consent`);
  assert.equal(b.window.dataLayer,undefined,`${lang}: no analytics events before consent`);
  assert.equal(b.panel.hidden,false);
  assert.ok(message.textContent.length<=50,`${lang}: compact first-layer copy`);
  assert.equal(b.panel.className,'ba-analytics-panel');
  assert.equal(details.hidden,true);
  assert.equal(close.hidden,true);
  assert.equal(configure.hidden,false);
  assert.ok(!visibleText(b.panel).includes('Google'),`${lang}: no provider jargon in first layer`);
  assert.equal(configure['aria-controls'],details.id);
  configure.click();
  assert.equal(details.hidden,false);
  assert.ok(b.panel.className.includes('ba-analytics-panel--expanded'));
  assert.equal(b.state.focus,title,`${lang}: focus the visible settings heading`);
  assert.ok(visibleText(details).includes('Google Analytics'),`${lang}: provider disclosed in settings`);
  const [privacy,googlePolicy]=details.children[1].children;
  assert.equal(privacy.href,'/privacy#website-analytics-'+lang.split('-')[0]);
  assert.equal(googlePolicy.href,'https://policies.google.com/technologies/partner-sites');
  assert.equal(b.head.children.length,0,`${lang}: configuring is not consent`);
  assert.equal(b.state.storage,null);
  assert.equal(b.state.focusOptions.preventScroll,true);
  close.click();
  assert.equal(b.panel.hidden,false,`${lang}: closing details does not silently decide`);
  assert.equal(details.hidden,true);
  assert.equal(b.panel.className,'ba-analytics-panel');
  assert.equal(b.state.focus,configure,`${lang}: never focus the visually hidden collapsed heading`);
  assert.equal(b.state.storage,null);
  configure.click(); b.panel.keydown('Escape');
  assert.equal(details.hidden,true);
  assert.equal(b.state.keyPrevented,true);
  assert.equal(b.head.children.length,0);
  no.click(); assert.equal(b.head.children.length,0); assert.equal(b.panel.hidden,true);
  assert.equal(JSON.parse(b.state.storage).value,'denied');
  b.settings.click(); assert.equal(b.panel.hidden,false);
  assert.equal(details.hidden,false,`${lang}: footer opens full settings for withdrawal`);
  close.click(); assert.equal(b.panel.hidden,true);
  assert.equal(JSON.parse(b.state.storage).value,'denied');
  b.settings.click();
  yes.click(); assert.equal(b.head.children.length,1); assert.ok(b.head.children[0].src.endsWith('G-P0ZK25PW9Q'));
  assert.equal(JSON.parse(b.state.storage).value,'granted');
  const consentDefault=b.window.dataLayer.find(x=>x[0]==='consent' && x[1]==='default')[2];
  assert.ok(Object.values(consentDefault).every(value=>value==='denied'));
  const consentUpdate=b.window.dataLayer.find(x=>x[0]==='consent' && x[1]==='update')[2];
  assert.equal(consentUpdate.analytics_storage,'granted');
  for (const key of ['ad_storage','ad_user_data','ad_personalization']) assert.equal(consentUpdate[key],'denied');
  const config=b.window.dataLayer.find(x=>x[0]==='config')[2];
  assert.equal(config.page_location,'https://bibleanswer.app/ru/');
  assert.equal(config.page_referrer,'https://example.org/article');
  assert.equal(config.allow_google_signals,false);
  assert.equal(config.allow_ad_personalization_signals,false);
  b.settings.click(); no.click(); assert.equal(b.window['ga-disable-G-P0ZK25PW9Q'],true);
  assert.equal(JSON.parse(b.state.storage).value,'denied');
  const revoked=b.window.dataLayer.filter(x=>x[0]==='consent').at(-1)[2];
  assert.ok(Object.values(revoked).every(value=>value==='denied'));
  assert.ok(b.state.cookies.some(c=>c.startsWith('_ga=;')));
  assert.ok(b.state.cookies.every(c=>!c.startsWith('unrelated=')));
  b.settings.click(); yes.click(); assert.equal(b.head.children.length,1,'do not load duplicate tag');
  assert.equal(b.window['ga-disable-G-P0ZK25PW9Q'],false);
}
assert.equal(titles.size,6,'each supported language has its own first layer');
for (const value of ['denied','granted']) {
  const b=boot({saved:{value,time:Date.now()}}); assert.equal(b.panel.hidden,true); assert.equal(b.head.children.length,value==='granted'?1:0);
  const {details}=controls(b);
  b.settings.click(); assert.equal(details.hidden,false);
  b.panel.keydown('Escape'); assert.equal(b.panel.hidden,true);
  assert.equal(JSON.parse(b.state.storage).value,value,'closing settings preserves a saved choice');
}
const expired=boot({saved:{value:'granted',time:Date.now()-181*86400000}});
assert.equal(expired.head.children.length,0); assert.equal(expired.panel.hidden,false);
const invalid=boot({saved:{value:'unknown',time:Date.now()}});
assert.equal(invalid.head.children.length,0); assert.equal(invalid.panel.hidden,false);
assert.equal(controls(boot({lang:'unknown'})).title.textContent,controls(boot()).title.textContent);
assert.equal(boot({id:''}).body.children.length,0);
const blocked=boot({brokenStorage:true});
assert.equal(blocked.head.children.length,0);
controls(blocked).configure.click(); assert.equal(blocked.head.children.length,0);
controls(blocked).yes.click(); assert.equal(blocked.head.children.length,1);
blocked.settings.click(); controls(blocked).no.click(); assert.equal(blocked.window['ga-disable-G-P0ZK25PW9Q'],true);
console.log('ok: 6 localized compact notices; configure/close/Escape never consent; saved choice and expiry; footer withdrawal; blocked storage; no Google before consent; advertising denied; no duplicate Google tag');
