#!/usr/bin/env node
// Cross-page native foreground-mask comparison; browser compositing is outside this oracle.
'use strict';
const path=require('node:path'),fs=require('node:fs'),assert=require('node:assert/strict');
const flag=(name,fallback)=>process.argv.find(x=>x.startsWith('--'+name+'='))?.slice(name.length+3)||fallback;
const hostFile=fs.existsSync(path.join(__dirname,'app/sim/page.js'))?path.join(__dirname,'app/sim/page.js'):path.resolve(__dirname,'../../../sim/page.js');
const {host}=require(hostFile);
const native=require(flag('canvas-module',process.env.CANVAS_MODULE||'@napi-rs/canvas'));
const base=path.resolve(flag('baseline',path.join(__dirname,'baseline/murmuration.html')));
const current=path.resolve(flag('current',path.join(__dirname,'app/murmuration.html')));
const options={query:'seed=1&n=20&calm&painted',native,width:1440,height:900,dpr:2};
const pages=[host(base,options),host(current,options)];
const S=8,side=128,dim=side*S;
const canvases=pages.map(()=>native.createCanvas(dim,dim));
function makeState(M,c){
 if(c.species==='starling'){const g=M.gait(0,c.phase,.5);g.phase=c.phase;g.weight=c.weight;g.hold=c.hold;g.mode=c.weight>.5?'flap':c.hold;return g}
 const f=M.falconState();f.pose=c.pose;f.elapsed=c.elapsed||0;f.phase=c.phase||0;f.flap=c.flap||0;f.blend=1;return f;
}
function centerY(z){const f=Math.min(450/Math.tan(23*Math.PI/180),720/Math.tan(21*Math.PI/180)),p=Math.atan(270/f),ct=Math.cos(p),st=Math.sin(p),yr=34,zc=yr*st+z*ct;return 450-(yr*ct-z*st)*f/zc}
function render(idx,c){const page=pages[idx],M=page.state.Motion,ctx=canvases[idx].getContext('2d');
 ctx.setTransform(1,0,0,1,0,0);ctx.clearRect(0,0,dim,dim);
 const y0=Math.floor(centerY(c.z)-64),x0=656;
 ctx.setTransform(S,0,0,S,-S*x0,-S*y0);ctx.fillStyle='#000';
 const p=new page.window.Path2D();page.state.pushMotion(p,c.species,makeState(M,c),0,36,c.z,c.v[0],c.v[1],c.v[2],c.bank,1,c.species==='starling'?1.63:4.4);
 ctx.fill(p);return ctx.getImageData(0,0,dim,dim).data;
}
function compare(a,b){const n=dim*dim,A=new Uint8Array(n),B=new Uint8Array(n);let na=0,nb=0,diff=0;
 for(let i=0;i<n;i++){A[i]=a[4*i+3]>=128?1:0;B[i]=b[4*i+3]>=128?1:0;na+=A[i];nb+=B[i];diff+=A[i]!==B[i]}
 if(!na||!nb)throw new Error(`empty glyph ${na}/${nb}`);
 function directed(src,dst){let max=0,missing=0;for(let i=0;i<n;i++)if(src[i]&&!dst[i]){
  missing++;const x=i%dim,y=(i/dim)|0;let best=Infinity;
  for(let dy=-48;dy<=48;dy++)for(let dx=-48;dx<=48;dx++){
   const xx=x+dx,yy=y+dy;if(xx<0||xx>=dim||yy<0||yy>=dim)continue;
   if(dst[yy*dim+xx])best=Math.min(best,dx*dx+dy*dy);
  }
  max=Math.max(max,Math.sqrt(best)/S);
 }return {maxCssPx:max,missing}}
 const f=directed(A,B),r=directed(B,A);return {areaBase:na,areaCurrent:nb,differentPixels:diff,errorCssPx:Math.max(f.maxCssPx,r.maxCssPx),baseToCurrent:f,currentToBase:r};
}
const orientations=[{v:[0,0,1],bank:0},{v:[.6,.2,.775],bank:.8},{v:[1,0,0],bank:-.9},{v:[-.4,-.2,.894],bank:.4}],far=[],near=[];
for(const z of [75,90,160])for(const phase of [0,.25,.5,.75])for(const [weight,hold] of [[1,'glide'],[.35,'glide'],[0,'bound']])for(const o of orientations)far.push({species:'starling',z,phase,weight,hold,...o});
for(const z of [190,260])for(const [pose,elapsed,flap,phase] of [['glide',0,0,0],['glide',0,.8,.25],['tuck',.2,0,0],['tuck',.6,0,0],['stoop',0,0,0],['pullout',.3,0,0],['pullout',.8,0,0]])for(const o of orientations)far.push({species:'falcon',z,pose,elapsed,flap,phase,...o});
for(const o of orientations){near.push({species:'starling',z:45,phase:.25,weight:1,hold:'glide',...o});near.push({species:'falcon',z:45,pose:'pullout',elapsed:.3,flap:0,phase:0,...o})}
const evalCases=arr=>arr.map(c=>({case:c,...compare(render(0,c),render(1,c))}));
const farResults=evalCases(far),nearResults=evalCases(near);
for(const clip of Object.values(pages[1].state.Motion.data.species.starling.clips))for(const frame of clip.frames)for(let j=2;j<frame.length;j+=3)frame[j]=0;
const sentinel={species:'starling',z:75,phase:.25,weight:1,hold:'glide',v:[.6,.2,.775],bank:.8};
const negative=compare(render(0,sentinel),render(1,sentinel));
const failures=farResults.filter(r=>r.errorCssPx>.5);
const max=Math.max(...farResults.map(r=>r.errorCssPx));
assert.equal(failures.length,0,'far silhouette exceeds 0.5 CSS px');
assert.equal(nearResults.filter(r=>r.differentPixels>0).length,0,'near pixels differ');
assert(negative.errorCssPx>.5,'flattened-Z sentinel did not fail');
console.log(JSON.stringify({status:'passed',baselineFile:base,currentFile:current,baseline:pages[0].htmlSha256,current:pages[1].htmlSha256,scale:S,thresholdCssPx:.5,farCount:farResults.length,farMaxCssPx:Math.max(...farResults.map(r=>r.errorCssPx)),farFailureCount:failures.length,farFailures:failures.slice(0,12),nearCount:nearResults.length,nearMaxCssPx:Math.max(...nearResults.map(r=>r.errorCssPx)),nearNonIdentical:nearResults.filter(r=>r.differentPixels>0),negativeControl:negative}));
