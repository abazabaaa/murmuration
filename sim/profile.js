#!/usr/bin/env node
'use strict';
// Isolate actual-page function costs. This is a local CPU benchmark, not browser FPS.
const path=require('node:path');
const {performance}=require('node:perf_hooks');
const {host}=require('./page');
const args=process.argv.slice(2), flag=(name,d)=>args.find(x=>x.startsWith('--'+name+'='))?.split('=').slice(1).join('=')||d;
const file=path.resolve(flag('html',path.join(__dirname,'../murmuration.html')));
const canvasModule=flag('canvas-module',process.env.CANVAS_MODULE);
const native=!!canvasModule;
const mode=flag('mode','xyz');
const frames=+flag('frames','120');
if(!Number.isSafeInteger(frames)||frames<30||!['xyz','legacy'].includes(mode))throw new Error('use >=30 frames and xyz or legacy mode');
for(const [name,fallback] of [['n','400'],['width','1440'],['height','900'],['dpr','1']])
 if(!Number.isFinite(+flag(name,fallback))||+flag(name,fallback)<=0)throw new Error('invalid '+name);
const h=host(file,{query:`seed=1&calm&warm=20&painted&n=${flag('n','400')}${mode==='legacy'?'&motion=legacy':''}`,
 width:+flag('width','1440'),height:+flag('height','900'),dpr:+flag('dpr','1'),
 canvasModule});
const m=h.state, samples={step:[],draw:[],analyse:[]}, quantile=(a,p)=>[...a].sort((a,b)=>a-b)[Math.floor((a.length-1)*p)];
const before={...h.canvasCalls};
for(let i=0;i<frames+20;i++) {
 const t=20+(i+1)/60;
 let start=performance.now();m.step(1/60,t);let end=performance.now();if(i>=20)samples.step.push(end-start);
 if(i%30===0){start=performance.now();m.analyse(t);end=performance.now();if(i>=20)samples.analyse.push(end-start);}
 start=performance.now();m.draw();end=performance.now();if(i>=20)samples.draw.push(end-start);
}
const timings=Object.fromEntries(Object.entries(samples).map(([k,a])=>[k,{medianMs:quantile(a,.5),p95Ms:quantile(a,.95),meanMs:a.reduce((a,b)=>a+b,0)/a.length}]));
const counters=Object.fromEntries(Object.entries(h.canvasCalls).map(([k,v])=>[k,v-(before[k]||0)]));
console.log(JSON.stringify({file,node:process.version,canvasModule:canvasModule||null,measurement:'isolated page functions; 20 unmeasured warm-up frames; counters include warm-up; not browser FPS',pageSha256:h.htmlSha256,assets:h.assets,n:m.N,mode,native,frames,width:h.window.innerWidth,height:h.window.innerHeight,dpr:h.window.devicePixelRatio,timings,counters}));
