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
    focus() { state.focus=this; }
    click() { this.handlers.click?.(); }
  }
  const state={storage:saved ? JSON.stringify(saved):null, cookies:[],focus:null};
  const head=new Element('head'), body=new Element('body'), footer=new Element('footer');
  const doc={currentScript:{dataset:{gaId:id}},documentElement:{lang}, referrer:'https://example.org/article?secret=value#fragment',head,body,querySelector:()=>footer,createElement:t=>new Element(t)};
  Object.defineProperty(doc,'cookie',{get:()=> '_ga=a; _ga_TEST=b; unrelated=yes',set:v=>state.cookies.push(v)});
  const window={};
  const storage={getItem(){if(brokenStorage)throw Error('blocked');return state.storage;},setItem(k,v){if(brokenStorage)throw Error('blocked');state.storage=v;}};
  vm.runInNewContext(code,{document:doc,window,localStorage:storage,location:{origin:'https://bibleanswer.app',pathname:'/ru/',hostname:'bibleanswer.app'},URL,Date,encodeURIComponent});
  return {...state,state,head,body,footer,window,panel:body.children[0], settings:footer.children[0]};
}
for (const lang of ['en','ru','es','pt-BR','fr','fil']) {
  const b=boot({lang});
  assert.equal(b.head.children.length,0,`${lang}: no Google before consent`);
  assert.equal(b.panel.hidden,false);
  const [yes,no]=b.panel.children[3].children;
  no.click(); assert.equal(b.head.children.length,0); assert.equal(b.panel.hidden,true);
  assert.equal(JSON.parse(b.state.storage).value,'denied');
  b.settings.click(); assert.equal(b.panel.hidden,false);
  yes.click(); assert.equal(b.head.children.length,1); assert.ok(b.head.children[0].src.endsWith('G-P0ZK25PW9Q'));
  const config=b.window.dataLayer.find(x=>x[0]==='config')[2];
  assert.equal(config.page_location,'https://bibleanswer.app/ru/');
  assert.equal(config.page_referrer,'https://example.org/article');
  assert.equal(config.allow_google_signals,false);
  assert.equal(config.allow_ad_personalization_signals,false);
  b.settings.click(); no.click(); assert.equal(b.window['ga-disable-G-P0ZK25PW9Q'],true);
  assert.ok(b.state.cookies.some(c=>c.startsWith('_ga=;')));
  assert.ok(b.state.cookies.every(c=>!c.startsWith('unrelated=')));
  b.settings.click(); yes.click(); assert.equal(b.head.children.length,1,'do not load duplicate tag');
  assert.equal(b.window['ga-disable-G-P0ZK25PW9Q'],false);
}
for (const value of ['denied','granted']) {
  const b=boot({saved:{value,time:Date.now()}}); assert.equal(b.panel.hidden,true); assert.equal(b.head.children.length,value==='granted'?1:0);
}
assert.equal(boot({saved:{value:'granted',time:Date.now()-181*86400000}}).head.children.length,0);
assert.equal(boot({id:''}).body.children.length,0);
assert.equal(boot({brokenStorage:true}).head.children.length,0);
console.log('ok: consent across 6 languages, persistence, expiry, revoke/regrant, no requests before consent, no duplicate Google tag');
