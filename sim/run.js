#!/usr/bin/env node
'use strict';
const path=require('node:path');
const crypto=require('node:crypto');
const {host}=require('./page');
const args=process.argv.slice(2);
function flag(name,fallback) {const i=args.indexOf(`--${name}`);return i<0?fallback:args[i+1];}
const file=path.resolve(flag('html',path.join(__dirname,'../murmuration.html')));
const query=flag('query','seed=1&n=80&calm');
const seconds=Number(flag('seconds','10')),dtMs=Number(flag('dt-ms',String(1000/60)));
const format=flag('format','json');
if(!Number.isFinite(seconds)||seconds<=0||!Number.isFinite(dtMs)||dtMs<=0||!['json','csv'].includes(format))throw new Error('invalid seconds, dt-ms, or format');
const frames=Math.round(seconds*1000/dtMs);
if(!Number.isSafeInteger(frames)||frames<1)throw new Error('duration must contain at least one frame');
const h=host(file,{query,canvasModule:flag('canvas-module',undefined)});
const sha=crypto.createHash('sha256'),rows=[];
const inputFile=flag('inputs',null);
const inputSource=inputFile?require('node:fs').readFileSync(inputFile):null;
const inputs=inputSource?JSON.parse(inputSource):[];
if(!Array.isArray(inputs)||inputs.some(e=>!Number.isFinite(e.atMs)||e.atMs<0||typeof e.type!=='string'))throw new Error('invalid input replay file');
inputs.sort((a,b)=>a.atMs-b.atMs);let nextInput=0;
for(let i=0;i<frames;i++) {
  while(nextInput<inputs.length&&inputs[nextInput].atMs<=(i+1)*dtMs) {
    const {atMs,type,...detail}=inputs[nextInput++];h.dispatch(type,detail);
  }
  h.frame(dtMs);
  const s=h.snapshot();
  sha.update(JSON.stringify([s.arrays,s.fal,s.hunts]));
  if(i===0||i===frames-1||Math.floor((i+1)*dtMs/1000)!==Math.floor(i*dtMs/1000))
    rows.push({frame:i+1,timeMs:s.timeMs,simT:s.simT,polarization:s.stats.pol,nearest:s.stats.nn,out:s.stats.out,
      falconOn:s.fal.on,mode:s.fal.mode,hunts:s.hunts.filter(e=>e.type==='hunt').length,strikes:s.hunts.filter(e=>e.type==='strike').length});
}
const end=h.snapshot();
const result={kind:'actual-page-vm-simulation',metadata:{file,htmlSha256:h.htmlSha256,scriptAssets:h.assets,query:h.query,
  seed:h.state.seed,seconds,dtMs,frames,clock:'virtual',canvas:flag('canvas-module',undefined)?'native':'strict-stub',node:process.version,
  inputs:inputSource?{file:path.resolve(inputFile),sha256:crypto.createHash('sha256').update(inputSource).digest('hex'),count:inputs.length,
    policy:'dispatch before first frame whose end time reaches atMs',events:inputs}:null},
  summary:{traceSha256:sha.digest('hex'),simT:end.simT,drawCalls:end.canvasCalls,fullHunts:end.hunts},rows};
if(format==='json')console.log(JSON.stringify(result));
else {
  console.log(`# metadata=${JSON.stringify(result.metadata)}`);
  console.log(`# traceSha256=${result.summary.traceSha256}`);
  console.log(Object.keys(rows[0]).join(','));
  for(const row of rows)console.log(Object.values(row).map(v=>v==null?'':String(v)).join(','));
}
