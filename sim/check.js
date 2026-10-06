#!/usr/bin/env node
'use strict';
const assert=require('node:assert/strict'),cp=require('node:child_process'),path=require('node:path');
const {host}=require('./page');
const html=path.resolve(__dirname,'../murmuration.html');
const a=host(html,{query:'seed=7&n=40&painted'}),b=host(html,{query:'seed=7&n=40&painted'});
for(let i=0;i<120;i++) {
  a.frame();b.frame();
  assert.deepEqual(a.snapshot().arrays,b.snapshot().arrays,'same-input trajectory replay differs');
  assert.deepEqual(a.snapshot().hunts,b.snapshot().hunts,'same-input hunt replay differs');
}
assert.ok(a.canvasCalls['Path2D.lineTo']>0,'frame callback did not draw birds');
b.state.vx[0]+=.01;
assert.notDeepEqual(a.snapshot().arrays.vx,b.snapshot().arrays.vx,'velocity oracle missed perturbation');
// Exercise the long-run consumer boundary: the page's ring keeps only 400 events,
// while the host captures each event by identity before it is evicted.
for(let i=0;i<450;i++) {
  a.state.huntLog.push({type:'synthetic-ring-probe',id:i});
  if(a.state.huntLog.length>400)a.state.huntLog.shift();
  a.frame();
}
assert.equal(a.state.huntLog.length,400);
assert.equal(a.fullHunts.filter(e=>e.type==='synthetic-ring-probe').length,450);
const motion=cp.execFileSync(process.execPath,[path.resolve(__dirname,'../motion/check.js')],{encoding:'utf8'});
assert.equal(JSON.parse(motion).status,'passed');
for(const script of ['run.js','differential.js'])for(const timing of [['--seconds','banana'],['--seconds','0.001','--dt-ms','1000']]) {
  const bad=cp.spawnSync(process.execPath,[path.resolve(__dirname,script),...timing],{encoding:'utf8'});
  assert.notEqual(bad.status,0,`${script} accepted invalid timing ${timing.join(' ')}`);
  assert.match(bad.stderr,timing[1]==='banana'?/Error: invalid seconds/:/Error: duration must contain at least one frame/,`${script} failed through the wrong channel`);
  assert.doesNotMatch(bad.stdout,/"status":"equal"/,`${script} emitted a false equality result`);
}
console.log(JSON.stringify({status:'passed',replayFrames:120,velocityNegativeControl:true,ringEvents:450,
  canvasPathLines:a.canvasCalls['Path2D.lineTo'],motion:JSON.parse(motion).checked}));
