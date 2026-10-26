// Run: node tests_search_escape.mjs
// Real discovery/mobile modules, narrow DOM/event doubles; not a browser test.
import assert from 'node:assert/strict';
import {createDiscoveryUI} from '../site/discovery-ui.js';
import {createMobileUI} from '../site/mobile-ui.js';

class UiEvent {
  constructor(type,options={}){this.type=type;this.defaultPrevented=false;this.propagationStopped=false;Object.assign(this,options);}
  preventDefault(){this.defaultPrevented=true;}
  stopPropagation(){this.propagationStopped=true;}
}
class Element {
  constructor(env){this.env=env;this.listeners={};this.attrs={};this.dataset={};this.open=false;this.hidden=true;this.value='';this.selectionStart=0;this.selectionEnd=0;this.selectionDirection='none';this.classes=new Set();this.classList={add:k=>this.classes.add(k),remove:k=>this.classes.delete(k),contains:k=>this.classes.has(k),toggle:(k,v)=>v?this.classes.add(k):this.classes.delete(k)};}
  addEventListener(type,fn){(this.listeners[type]??=[]).push(fn);}
  dispatchEvent(event){event.target??=this;for(const fn of this.listeners[event.type]||[])fn(event);return !event.defaultPrevented;}
  setAttribute(key,value){this.attrs[key]=String(value);}
  getAttribute(key){return this.attrs[key]??null;}
  removeAttribute(key){delete this.attrs[key];}
  before(anchor){anchor.parentElement=this.parentElement;anchor.nextSibling=this;this.anchor=anchor;}
  after(node){node.parentElement=this.parentElement;this.nextSibling=node;node.anchor=this;}
  append(node){if(node.anchor){node.anchor.nextSibling=null;node.anchor=null;}node.parentElement=this;}
  contains(node){for(let n=node;n;n=n.parentElement)if(n===this)return true;return false;}
  focus(){if(this.env.document.activeElement===this)return;this.env.document.activeElement=this;this.dispatchEvent(new UiEvent('focus'));}
  blur(){if(this.env.document.activeElement===this)this.env.document.activeElement=null;}
  showModal(){this.returnFocus=this.env.document.activeElement;this.open=true;}
  close(){if(!this.open)return;this.open=false;this.returnFocus?.focus();this.env.queue.push(()=>this.dispatchEvent(new UiEvent('close')));}
  setSelectionRange(start,end,direction){this.selectionStart=start;this.selectionEnd=end;this.selectionDirection=direction;}
  scrollIntoView(){}
  insertAdjacentHTML(){}
  getBoundingClientRect(){return {left:0,right:100,top:0,bottom:100};}
}
const originalGlobals=Object.fromEntries(['document','window','matchMedia','Event','setTimeout','clearTimeout'].map(k=>[k,{present:k in globalThis,value:globalThis[k]}]));
function fixture(isMobile){
  const env={nodes:new Map(),queue:[],timers:new Map(),nextTimer:0,applied:0,filterCancelled:0,dismissed:0};
  env.get=selector=>{if(!env.nodes.has(selector))env.nodes.set(selector,new Element(env));return env.nodes.get(selector);};
  const doc=new Element(env);env.document=doc;doc.body=new Element(env);doc.documentElement={lang:'fr'};doc.activeElement=null;doc.querySelector=env.get;doc.querySelectorAll=()=>[];doc.createComment=()=>new Element(env);
  env.media={matches:isMobile,addEventListener(){}};
  env.flush=()=>{while(env.queue.length)env.queue.shift()();};
  globalThis.document=doc;globalThis.Event=UiEvent;globalThis.matchMedia=()=>env.media;
  globalThis.setTimeout=fn=>{const id=++env.nextTimer;env.timers.set(id,fn);return id;};globalThis.clearTimeout=id=>env.timers.delete(id);
  env.suggestionResult={suggestions:[]};globalThis.window={getCatalogJson:()=>env.pending||Promise.resolve(env.suggestionResult)};
  env.host=new Element(env);env.get('.search-shell').parentElement=env.host;env.get('#filters').parentElement=env.host;env.get('#search').parentElement=env.get('.search-shell');env.get('.mobile-search-body').parentElement=env.get('#search-dialog');
  env.state={q:'alternateur',language:'fr',make:'Renault',model:'Clio',engine:'1.5 DCI',category:'mechanics',platform:'youtube',page:1};
  env.url=new URL('https://example.invalid/?q=alternateur&language=fr&make=Renault&model=Clio&engine=1.5+DCI');
  env.beforeState=JSON.stringify(env.state);env.beforeUrl=env.url.href;doc.body.classList.add('results-mode');
  const ctx={escape:String,t:(fr)=>fr,getUi:()=> 'fr',getState:()=>env.state,storage:{get:(_,fallback)=>fallback,set(){}},langName:l=>l,applySearch:state=>{env.applied++;env.state=state;env.url.searchParams.set('q',state.q||'');},openVideo(){},openGuide(){},clearFilter(){throw Error('Escape must not clear a filter');},clearVehicle(){throw Error('Escape must not clear a vehicle');}};
  env.discovery=createDiscoveryUI(ctx);
  env.mobile=createMobileUI({t:ctx.t,getState:ctx.getState,getTotal:()=>20,isLoading:()=>false,onExplore:()=>{env.get('#search').value=env.state.q;},filterStudio:{beginDraft(){},cancelDraft(){env.filterCancelled++;},update(){},hasPendingChanges:()=>false}});
  doc.addEventListener('rl:search-dismiss',()=>env.dismissed++);
  env.input=env.get('#search');env.input.value='alternateur';env.input.setSelectionRange(2,6,'forward');env.mobile.openSearch();
  env.escape=()=>{
    const event=new UiEvent('keydown',{key:'Escape'});env.input.dispatchEvent(event);
    // Model the reported type=search default action. The production listener
    // must cancel it rather than relying on a browser to emit an input event.
    if(!event.defaultPrevented)env.input.value='';
    env.flush();return event;
  };
  env.assertUnchanged=()=>{assert.equal(JSON.stringify(env.state),env.beforeState);assert.equal(env.url.href,env.beforeUrl);assert.equal(env.applied,0);assert.equal(env.input.value,'alternateur');assert.deepEqual([env.input.selectionStart,env.input.selectionEnd,env.input.selectionDirection],[2,6,'forward']);};
  return env;
}
const results=[];
async function test(name,run){try{await run();results.push({name,status:'passed'});}catch(error){results.push({name,status:'failed',error:error.message});}}
async function showSuggestions(env){env.suggestionResult={suggestions:[{type:'topic',id:'battery',label:'Alternateur et batterie',count:20}]};env.discovery.refreshSuggestions();await Promise.resolve();assert.equal(env.get('#search-suggestions').hidden,false);}

try{
  await test('desktop Escape with closed suggestions preserves input, selection, committed search and focus',()=>{
    const e=fixture(false),event=e.escape();assert.equal(event.defaultPrevented,true);assert.equal(event.propagationStopped,false);assert.equal(e.dismissed,1);e.assertUnchanged();assert.equal(e.document.activeElement,e.input);assert.equal(e.get('#search-dialog').open,false);assert.equal(e.input.getAttribute('aria-expanded'),'false');
  });
  await test('mobile Escape with closed suggestions dismisses the sheet and restores edit-search focus',()=>{
    const e=fixture(true);assert.equal(e.get('#search-dialog').open,true);assert.equal(e.escape().defaultPrevented,true);e.assertUnchanged();assert.equal(e.dismissed,1);assert.equal(e.get('#search-dialog').open,false);assert.equal(e.document.activeElement,e.get('#edit-search'));assert.equal(e.get('.search-shell').parentElement,e.host);assert.equal(e.document.body.classList.contains('sheet-open'),false);
  });
  for(const mobile of [false,true])await test(`first Escape closes open suggestions only (${mobile?'mobile':'desktop'})`,async()=>{
    const e=fixture(mobile);await showSuggestions(e);e.input.dispatchEvent(new UiEvent('keydown',{key:'ArrowDown'}));assert.equal(e.input.getAttribute('aria-activedescendant'),'suggestion-0');const event=e.escape();assert.equal(event.defaultPrevented,true);assert.equal(event.propagationStopped,true);assert.equal(e.dismissed,0);assert.equal(e.get('#search-suggestions').hidden,true);assert.equal(e.get('#search-helper').hidden,true);assert.equal(e.input.getAttribute('aria-expanded'),'false');assert.equal(e.input.getAttribute('aria-activedescendant'),null);assert.equal(e.get('#suggestion-status').textContent,'');assert.equal(e.get('#search-dialog').open,mobile);assert.equal(e.document.activeElement,e.input);e.assertUnchanged();
  });
  await test('second mobile Escape dismisses after closing suggestions; reopening retains the exact draft',async()=>{
    const e=fixture(true);await showSuggestions(e);e.escape();e.escape();assert.equal(e.dismissed,1);assert.equal(e.get('#search-dialog').open,false);e.mobile.openSearch();assert.equal(e.get('#search-dialog').open,true);assert.equal(e.document.activeElement,e.input);e.assertUnchanged();
  });
  await test('Escape cancels pending suggestions so a late response cannot reopen the popup',async()=>{
    const e=fixture(true);let complete;e.pending=new Promise(resolve=>{complete=resolve;});e.discovery.refreshSuggestions();e.escape();complete({suggestions:[{type:'topic',id:'battery',label:'Alternateur',count:20}]});await Promise.resolve();assert.equal(e.get('#search-dialog').open,false);assert.equal(e.get('#search-suggestions').hidden,true);assert.equal(e.get('#search-helper').hidden,true);e.assertUnchanged();
  });
  await test('native search-dialog cancel remains available outside the input',()=>{
    const e=fixture(true),dialog=e.get('#search-dialog'),event=new UiEvent('cancel');dialog.dispatchEvent(event);assert.equal(event.defaultPrevented,false);dialog.close();e.flush();assert.equal(e.dismissed,0);assert.equal(dialog.open,false);assert.equal(e.document.activeElement,e.get('#edit-search'));assert.equal(e.document.body.classList.contains('sheet-open'),false);e.assertUnchanged();
  });
  await test('native filter-dialog cancel still cancels its draft and returns focus',()=>{
    const e=fixture(true);e.mobile.closeSearch();e.flush();e.mobile.openFilters();const dialog=e.get('#filters-dialog'),event=new UiEvent('cancel');dialog.dispatchEvent(event);assert.equal(event.defaultPrevented,false);dialog.close();e.flush();assert.equal(e.filterCancelled,1);assert.equal(e.document.activeElement,e.get('#mobile-filters'));assert.equal(e.get('#filters').parentElement,e.host);e.assertUnchanged();
  });
  await test('non-Escape keys retain their default action when suggestions are closed',()=>{
    const e=fixture(false);for(const key of ['Enter','Tab','ArrowLeft','Backspace']){const event=new UiEvent('keydown',{key});e.input.dispatchEvent(event);assert.equal(event.defaultPrevented,false);assert.equal(event.propagationStopped,false);}assert.equal(e.dismissed,0);e.assertUnchanged();
  });
}finally{
  for(const [key,original]of Object.entries(originalGlobals)){if(original.present)globalThis[key]=original.value;else delete globalThis[key];}
}
const report={status:results.every(r=>r.status==='passed')?'passed':'failed',passed:results.filter(r=>r.status==='passed').length,failed:results.filter(r=>r.status==='failed').length,scope:'Production discovery/mobile modules with narrow DOM, dialog-focus, timer and native-search-clear test doubles. Browser rendering and native conformance not tested.',results};
console.log(JSON.stringify(report,null,2));
if(report.failed)process.exitCode=1;
