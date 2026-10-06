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
    if(lod==='near') assert.equal(pathObj.calls,model.faces[lod].length*4,`${species} z=${z} drew wrong face count`);
    else assert.ok(pathObj.calls>0&&pathObj.calls<model.faces.far.length*4,`${species} far contours missing or not reducing path work`);
    checked.lodProbes++;
  }
} finally {M.sampleGait=sampleGait;M.sampleFalcon=sampleFalcon;}

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
