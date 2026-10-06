#!/usr/bin/env node
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs'),os=require('node:os'),path=require('node:path');
const {host}=require('./page-harness');
const root=path.resolve(__dirname,'..');
const page=host(path.join(root,'murmuration.html'),{query:'seed=1&n=40&painted'});
const M=page.state.Motion;
const checked={clips:0,faces:0,lodProbes:0,viewerFrames:0,transitions:0,negativeControls:0};
const finite=a=>{for(const x of a)assert.ok(Number.isFinite(x),'nonfinite geometry');};
const distance=(a,b)=>Math.max(...a.map((v,i)=>Math.abs(v-b[i])));

for(const [species,model] of Object.entries(M.data.species)) {
  const size=model.clips.glide.frames[0].length/3;
  assert.equal(size,model.report.vertices);
  assert.ok(model.report.denseWithheldFlapMaxVertexErrorM<.003,`${species} withheld interpolation exceeds 3 mm`);
  assert.deepEqual(Array.from(M.sample(species,'flap',0)),Array.from(M.sample(species,'flap',1)),`${species} flap loop does not close`);
  for(const lod of ['near','far'])for(const face of model.faces[lod]) {
    assert.equal(face.length,3);for(const vi of face)assert.ok(Number.isInteger(vi)&&vi>=0&&vi<size);
    checked.faces++;
  }
  for(const clip of Object.values(model.clips))for(const frame of clip.frames) {
    assert.equal(frame.length,size*3);finite(frame);
  }
  for(const name of Object.keys(model.clips))for(const time of [0,.1,.25,.46,.5,.73,.9,1]) {
    const vertices=M.sample(species,name,time);finite(vertices);assert.equal(vertices.length,size*3);checked.clips++;
  }
}
// The reported starling stroke must be expressed in vertical XYZ, not only width.
const top=M.sample('starling','flap',0),bottom=M.sample('starling','flap',.46),halfSpan=M.data.species.starling.halfSpanM;
const topZ=Array.from(top).filter((_,i)=>i%3===2),bottomZ=Array.from(bottom).filter((_,i)=>i%3===2);
assert.ok((Math.max(...topZ)-Math.min(...bottomZ))*halfSpan>.26,'vertical stroke below reported 0.28 m scale');

// Both geometry levels must pass through the page's actual perspective path.
const sampleGait=M.sampleGait,sampleFalcon=M.sampleFalcon,observed=[];
M.sampleGait=function(state,out,indices){observed.push({species:'starling',indices:indices?.length});return sampleGait.apply(this,arguments);};
M.sampleFalcon=function(state,out,indices){observed.push({species:'falcon',indices:indices?.length});return sampleFalcon.apply(this,arguments);};
try {
  for(const species of ['starling','falcon'])for(const [lod,z] of [['near',45],['far',190]]) {
    const pathObj=new page.window.Path2D(),model=M.data.species[species];
    const state=species==='starling'?M.gait(2,.25,.5):M.falconState();
    const span=species==='starling'?1.63:4.4;
    page.state.pushMotion(pathObj,species,state,0,36,z,0,0,1,0,1,span);
    assert.equal(observed.at(-1).species,species);
    assert.equal(observed.at(-1).indices,model.indices[lod].length,`${species} z=${z} selected wrong LOD`);
    assert.equal(model.indices[lod].length,lod==='near'?316:47);
    assert.equal(model.faces[lod].length,lod==='near'?440:48);
    assert.ok(pathObj.calls>0&&pathObj.calls<model.faces[lod].length*4,`${species} ${lod} contours missing or not reducing path work`);
    checked.lodProbes++;
  }
} finally {M.sampleGait=sampleGait;M.sampleFalcon=sampleFalcon;}

// Near birds draw the outline of their triangles' union. Under the non-zero rule it must cover
// exactly the points the triangles cover, in every pose and view, including folded ones.
{
  const recorder=()=>{const loops=[];return {loops,moveTo(x,y){loops.push([[x,y]]);},lineTo(x,y){loops.at(-1).push([x,y]);},closePath(){}};};
  const winding=(loops,x,y)=>{let w=0;for(const l of loops)for(let i=0;i<l.length;i++){const [ax,ay]=l[i],[bx,by]=l[(i+1)%l.length];
    if(ay<=y){if(by>y&&(bx-ax)*(y-ay)-(x-ax)*(by-ay)>0)w++;}else if(by<=y&&(bx-ax)*(y-ay)-(x-ax)*(by-ay)<0)w--;}return w;};
  let seed=12345;const rnd=()=>(seed=Math.imul(seed^seed>>>15,2246822507)+1013904223>>>0)/4294967296;
  const X=page.state.motionX,Y=page.state.motionY,stats={cases:0,points:0,covered:0,multi:0,folded:0};
  const sampleGait=M.sampleGait,sampleFalcon=M.sampleFalcon;let lodSize=0;
  M.sampleGait=function(state,out,indices){lodSize=indices.length;return sampleGait.apply(this,arguments);};
  M.sampleFalcon=function(state,out,indices){lodSize=indices.length;return sampleFalcon.apply(this,arguments);};
  try {
  for(let c=0;c<160;c++) {
    const species=c%4===3?'falcon':'starling',model=M.data.species[species];
    let state;
    if(species==='starling'){state=M.gait(c,rnd(),.5);if(c%8===2)for(let i=0;i<400&&state.mode==='flap';i++)M.updateGait(state,1/60,14,0);}
    else {state=M.falconState();const mode=['stoop','climb','position','stoop'][c%16>>2];for(let i=0;i<(c*7)%200;i++)M.updateFalcon(state,1/60,mode,mode==='stoop'?60:20,.3);}
    let fx=rnd()-.5,fy=rnd()-.5,fz=rnd()-.5;const r=Math.hypot(fx,fy,fz);fx/=r;fy/=r;fz/=r;
    const path=recorder();
    page.state.pushMotion(path,species,state,(rnd()-.5)*6,36+(rnd()-.5)*4,20+rnd()*20,fx,fy,fz,(rnd()-.5)*2,1,species==='starling'?1.63:4.4);
    assert.equal(lodSize,model.indices.near.length,`oracle must exercise the near LOD (case ${c} ${species})`);
    const tris=model.faces.near.map(f=>f.map(v=>[X[v],Y[v]]));
    const signs=new Set(tris.map(([a,b,c])=>Math.sign((b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]))));
    if(signs.has(1)&&signs.has(-1))stats.folded++;
    let x0=Infinity,x1=-Infinity,y0=Infinity,y1=-Infinity;for(const t of tris)for(const [x,y] of t){x0=Math.min(x0,x);x1=Math.max(x1,x);y0=Math.min(y0,y);y1=Math.max(y1,y);}
    for(let k=0;k<1500;k++) {
      const x=x0+(x1-x0)*rnd(),y=y0+(y1-y0)*rnd();let n=0;
      for(const [a,b,c] of tris){const d1=(b[0]-a[0])*(y-a[1])-(b[1]-a[1])*(x-a[0]),d2=(c[0]-b[0])*(y-b[1])-(c[1]-b[1])*(x-b[0]),d3=(a[0]-c[0])*(y-c[1])-(a[1]-c[1])*(x-c[0]);
        if(d1>0&&d2>0&&d3>0||d1<0&&d2<0&&d3<0)n++;}
      const w=winding(path.loops,x,y);
      assert.equal(w!==0,n>0,`${species} case ${c}: outline covers (${x},${y}) ${w} times, triangles ${n}`);
      assert.equal(Math.abs(w),n,`${species} case ${c}: winding ${w} differs from triangle count ${n}`);
      stats.points++;if(n)stats.covered++;if(n>1)stats.multi++;
    }
    assert.ok(path.loops.length<model.faces.near.length/4,'near outline is not reducing path work');
    stats.cases++;
  }
  } finally {M.sampleGait=sampleGait;M.sampleFalcon=sampleFalcon;}
  assert.ok(stats.folded>stats.cases/2&&stats.multi>1000,'near oracle never saw folded or overlapping projections');
  checked.nearUnion=stats;
}

// Interrupted pullout: the first sample after each switch equals the outgoing shape.
const fal=M.falconState(),out=new Float32Array(948),before=new Float32Array(948);
for(const mode of ['stoop','climb','stoop','climb','position']) {
  M.sampleFalcon(fal,before);M.updateFalcon(fal,0,mode,22,.1);M.sampleFalcon(fal,out);
  finite(out);assert.ok(distance(before,out)<1e-6,`discontinuous falcon switch to ${mode}`);
  M.updateFalcon(fal,.08,mode,22,.1);M.sampleFalcon(fal,out);finite(out);checked.transitions++;
}

// Interrupted glide/bound: alarm returns the bird to flapping with finite blended geometry.
const gait=M.gait(7,.37,.5),gout=new Float32Array(948);
for(let i=0;i<500&&gait.mode==='flap';i++)M.updateGait(gait,1/60,12,0);
assert.notEqual(gait.mode,'flap','intermittent flight never reached glide/bound');
M.sampleGait(gait,gout);finite(gout);
M.updateGait(gait,1/60,12,1);assert.equal(gait.mode,'flap');M.sampleGait(gait,gout);finite(gout);checked.transitions++;
// Independent schedules must yield mixed gaits and distinct phases over a 10 s run.
const birds=Array.from({length:100},(_,i)=>M.gait(i,i/100,.5));let mixedFrames=0;
for(let k=0;k<600;k++) {
  for(const bird of birds)M.updateGait(bird,1/60,11.5,0);
  if(new Set(birds.map(b=>b.mode)).size>1)mixedFrames++;
}
assert.ok(mixedFrames>300,`only ${mixedFrames}/600 mixed-gait frames`);
assert.ok(new Set(birds.map(b=>b.phase.toFixed(3))).size>90,'phases synchronized');
for(const bird of birds) {for(let k=0;k<50;k++)M.updateGait(bird,1/60,11.5,1);assert.equal(bird.mode,'flap');}
checked.mixedGaitFrames=mixedFrames;

// The standalone viewer loads external scripts in page order and exercises controls.
const viewer=host(path.join(root,'motion-lab.html'),{}),doc=viewer.document;
for(const species of ['starling','falcon'])for(const view of ['quarter','top','front','side']) {
  doc.getElementById('species').value=species;doc.getElementById('species').onchange();
  doc.getElementById('view').value=view;viewer.frame();
  assert.match(doc.getElementById('readout').textContent,/Span in this pose:/);checked.viewerFrames++;
}

// A known bad velocity perturbation must be caught by the exact trajectory oracle.
const twin=host(path.join(root,'murmuration.html'),{query:'seed=1&n=40&painted'});
page.frame();twin.frame();twin.state.vx[0]+=.01;
assert.notDeepEqual(page.snapshot().arrays.vx,twin.snapshot().arrays.vx);checked.negativeControls++;

// Missing external asset, nonfinite canvas coordinate and unknown canvas method fail closed.
const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'murmuration-sim-check-'));
try {
  const bad=path.join(tmp,'bad.html');fs.writeFileSync(bad,'<script src="missing.js"></script>');
  assert.throws(()=>host(bad),/ENOENT/);checked.negativeControls++;
  fs.writeFileSync(bad,'<canvas id="c"></canvas><script>requestAnimationFrame(()=>document.getElementById("c").getContext("2d").moveTo(NaN,0))</script>');
  assert.throws(()=>host(bad).frame(),/non-finite/);checked.negativeControls++;
  fs.writeFileSync(bad,'<canvas id="c"></canvas><script>requestAnimationFrame(()=>document.getElementById("c").getContext("2d").imaginary())</script>');
  assert.throws(()=>host(bad).frame(),/unsupported canvas API/);checked.negativeControls++;
} finally {fs.rmSync(tmp,{recursive:true,force:true});}
console.log(JSON.stringify({status:'passed',checked,assets:page.assets,viewerAssets:viewer.assets}));
