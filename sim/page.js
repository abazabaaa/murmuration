// Deterministic, deliberately small DOM/canvas host for the actual HTML scripts.
// This checks JavaScript execution and geometry arguments; it does not rasterize pixels.
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const crypto = require('node:crypto');

const hash = source => crypto.createHash('sha256').update(source).digest('hex');
const finite = (name, args) => {
  for (const arg of args) if (typeof arg === 'number' && !Number.isFinite(arg))
    throw new Error(`${name}: non-finite coordinate ${arg}`);
};

function host(htmlFile, options = {}) {
  const root = path.dirname(path.resolve(htmlFile));
  const html = fs.readFileSync(htmlFile, 'utf8');
  const assets = [];
  const events = new Map(), elements = new Map(), raf = new Map(), timers = new Map();
  const canvasCalls = {};
  const native = options.native || (options.canvasModule ? require(options.canvasModule) : null);
  const fullHunts = [], seenHunts = new WeakSet();
  let now = 0, serial = 0;
  const count = name => { canvasCalls[name] = (canvasCalls[name] || 0) + 1; };
  const method = name => (...args) => { finite(name, args); count(name); };
  const methods = ['beginPath','closePath','moveTo','lineTo','quadraticCurveTo','bezierCurveTo','arc','ellipse',
    'rect','roundRect','fillRect','clearRect','strokeRect','fill','stroke','drawImage','fillText','strokeText',
    'save','restore','translate','scale','rotate','transform','setTransform','resetTransform','setLineDash',
    'clip','putImageData'];
  const gradient = () => ({ addColorStop: method('addColorStop') });
  const ctx = () => {
    const result = { canvas: null, createLinearGradient: (...a) => (finite('createLinearGradient', a), count('createLinearGradient'), gradient()),
      createRadialGradient: (...a) => (finite('createRadialGradient', a), count('createRadialGradient'), gradient()),
      createPattern: () => (count('createPattern'), {}),
      createImageData: (w,h) => { finite('createImageData',[w,h]); count('createImageData'); return {data:new Uint8ClampedArray(w*h*4),width:w,height:h}; },
      measureText: text => ({width:String(text).length*7}) };
    for (const name of methods) result[name] = method(name);
    return new Proxy(result, {get(target,key) { if (key in target || typeof key === 'symbol') return target[key];
      throw new Error(`unsupported canvas API ${String(key)}`); },
      set(target,key,value) {if(typeof value==='number'&&!Number.isFinite(value))throw new Error(`canvas.${String(key)}: non-finite value`);
        target[key]=value;return true;}});
  };
  class Path2D {
    constructor() { this.calls = 0; }
  }
  for (const name of ['moveTo','lineTo','quadraticCurveTo','bezierCurveTo','arc','ellipse','rect','roundRect','closePath','addPath'])
    Path2D.prototype[name] = function (...a) { finite(`Path2D.${name}`,a); this.calls++; count(`Path2D.${name}`); };
  let CanvasPath=Path2D;
  if(native?.Path2D) {
    CanvasPath=class extends native.Path2D {};
    for(const name of ['moveTo','lineTo','quadraticCurveTo','bezierCurveTo','arc','ellipse','rect','roundRect','closePath','addPath'])
      if(typeof native.Path2D.prototype[name]==='function') CanvasPath.prototype[name]=function(...a) {
        finite(`nativePath2D.${name}`,a);count(`nativePath2D.${name}`);return native.Path2D.prototype[name].apply(this,a);
      };
  }
  function element(tag = 'div', id = '') {
    const classes = new Set();
    const e = {tagName:tag.toUpperCase(),id,style:{},children:[],value:'',textContent:'',
      classList:{add:x=>classes.add(x),remove:x=>classes.delete(x),contains:x=>classes.has(x),toggle:x=>classes.has(x)?(classes.delete(x),false):(classes.add(x),true)},
      appendChild(x){this.children.push(x); if(this.tagName==='SELECT'&&this.children.length===1)this.value=x.value;
        if (x.id) elements.set(x.id,x);},append(x){this.appendChild(x);},
      addEventListener(type,fn){this[`on${type}`]=fn;},
      getBoundingClientRect(){return {x:0,y:0,width:options.width||1440,height:options.height||900};},
      getContext(type){if(type!=='2d') throw new Error(`unsupported canvas context ${type}`);
        if(!this._ctx) {
          if(native && tag==='canvas') {
            this._nativeCanvas=native.createCanvas(this.width||options.width||1440,this.height||options.height||900);
            const raw=this._nativeCanvas.getContext('2d');
            this._ctx=new Proxy(raw,{get(target,key){const value=target[key];
              if(typeof value==='function')return(...args)=>{finite(`nativeCanvas.${String(key)}`,args);count(`nativeCanvas.${String(key)}`);
                if((key==='drawImage'||key==='createPattern')&&args[0]?._nativeCanvas)args[0]=args[0]._nativeCanvas;
                return value.apply(target,args);};
              return value;},set(target,key,value){if(typeof value==='number'&&!Number.isFinite(value))throw new Error(`nativeCanvas.${String(key)}: non-finite value`);
                target[key]=value;return true;}});
          } else this._ctx=ctx();
        }
        return this._ctx;}};
    let innerHTML='';Object.defineProperty(e,'innerHTML',{get(){return innerHTML;},set(v){innerHTML=v;if(v==='')this.children=[];}});
    for(const dim of ['width','height']) {let value=0;Object.defineProperty(e,dim,{get(){return value;},set(v){value=v;if(this._nativeCanvas)this._nativeCanvas[dim]=v;}});}
    if(tag==='img') {
      e.naturalWidth=2048; e.naturalHeight=1024;
      Object.defineProperty(e,'src',{get(){return this._src;},set(v){this._src=v;
        const found = fs.existsSync(path.join(root,v));
        timers.set(++serial,{at:now,fn:()=>{if(found && options.imageLoad!==false) this.onload?.(); else this.onerror?.(new Error(`image unavailable: ${v}`));}});
      }});
    }
    return e;
  }
  for(const match of html.matchAll(/<([a-z]+)\b[^>]*\bid="([^"]+)"[^>]*>/gi)) elements.set(match[2],element(match[1],match[2]));
  for(const match of html.matchAll(/<select\b[^>]*\bid="([^"]+)"[^>]*>([\s\S]*?)<\/select>/gi)) {
    const e=elements.get(match[1]);if(!e)continue;
    for(const opt of match[2].matchAll(/<option\b[^>]*\bvalue="([^"]+)"[^>]*>/gi)) e.append({value:opt[1]});
    e.value=e.children[0]?.value||'';
  }
  for(const match of html.matchAll(/<input\b[^>]*\bid="([^"]+)"[^>]*\bvalue="([^"]+)"[^>]*>/gi)) elements.get(match[1]).value=match[2];
  const document = {body:element('body'),getElementById:id=>{if(!elements.has(id)) throw new Error(`missing DOM id ${id}`);return elements.get(id);},
    createElement:tag=>element(tag), addEventListener(type,fn){events.set(`document:${type}`,[...(events.get(`document:${type}`)||[]),fn]);}};
  const query = new URLSearchParams(options.query || 'seed=1');
  if(!query.has('seed'))query.set('seed','1');
  if(native&&!query.has('painted'))throw new Error('native canvas requires ?painted until image decoding is supported');
  query.set('debug','');
  const win = {document,innerWidth:options.width||1440,innerHeight:options.height||900,devicePixelRatio:options.dpr||1,
    location:{search:`?${query}`},URLSearchParams,Math,console,Float32Array,Float64Array,Int32Array,Int8Array,Uint32Array,Uint8Array,Uint8ClampedArray,Array,Path2D:CanvasPath,
    performance:{now:()=>now},
    requestAnimationFrame:fn=>{const id=++serial;raf.set(id,fn);return id;},cancelAnimationFrame:id=>raf.delete(id),
    setTimeout:(fn,delay=0)=>{const id=++serial;timers.set(id,{at:now+Math.max(0,Number(delay)),fn});return id;},clearTimeout:id=>timers.delete(id),
    addEventListener(type,fn){events.set(type,[...(events.get(type)||[]),fn]);},removeEventListener(type,fn){events.set(type,(events.get(type)||[]).filter(x=>x!==fn));}};
  win.window=win; win.globalThis=win;
  vm.createContext(win);
  const scriptRE=/<script\b([^>]*)>([\s\S]*?)<\/script>/gi;
  let match, index=0;
  while((match=scriptRE.exec(html))) {
    const attr=match[1], src=attr.match(/\bsrc\s*=\s*["']([^"']+)["']/i);
    const file=src ? path.resolve(root,src[1]) : path.resolve(root,`<inline-${++index}>`);
    if(src && !file.startsWith(root+path.sep)) throw new Error(`script escapes page root: ${src[1]}`);
    const code=src ? fs.readFileSync(file,'utf8') : match[2];
    assets.push({file:src?path.relative(root,file):`<inline-${index}>`,sha256:hash(code)});
    vm.runInContext(code,win,{filename:file,timeout:options.scriptTimeoutMs||30000});
  }
  if(!assets.length) throw new Error('page has no scripts');
  function dueTimers() {
    for(let passes=0;passes<1000;passes++) {
      const next=[...timers].filter(([,t])=>t.at<=now).sort((a,b)=>a[1].at-b[1].at||a[0]-b[0])[0];
      if(!next)return;
      timers.delete(next[0]);next[1].fn();
    }
    throw new Error('timer loop exceeded 1000 callbacks');
  }
  function frame(dtMs=1000/60) {
    if(!Number.isFinite(dtMs)||dtMs<=0) throw new Error(`invalid frame dt ${dtMs}`);
    now+=dtMs;dueTimers();
    const batch=[...raf.values()];raf.clear();
    if(!batch.length) throw new Error('no scheduled animation frame');
    for(const fn of batch)fn(now);
    captureHunts();
  }
  function captureHunts() {for(const e of win.murm?.huntLog||[]) if(e && typeof e==='object' && !seenHunts.has(e)) {seenHunts.add(e);fullHunts.push(e);}}
  function dispatch(type,detail={}) {for(const fn of events.get(type)||[])fn({type,...detail});}
  function snapshot() {
    const m=win.murm;if(!m)throw new Error('page did not expose window.murm under ?debug');
    const arrays={};for(const key of ['px','py','pz','vx','vy','vz']) {
      if(!m[key]||m[key].length!==m.N)throw new Error(`missing or mis-sized ${key}`);
      arrays[key]=Array.from(m[key]); finite(key,arrays[key]);
    }
    const fal={};for(const key of Object.keys(m.fal||{})) fal[key]=m.fal[key];
    captureHunts();
    const hunts=Array.from(fullHunts,e=>({...e}));
    return {timeMs:now,simT:m.simT,arrays,fal,hunts,stats:{...m.stats},canvasCalls:{...canvasCalls}};
  }
  return {window:win,document,assets,htmlSha256:hash(html),query:query.toString(),canvasCalls,frame,dispatch,snapshot,
    get fullHunts(){captureHunts();return fullHunts;},
    get now(){return now;},get state(){return win.murm;}};
}
module.exports={host,hash};
