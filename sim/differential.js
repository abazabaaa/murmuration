#!/usr/bin/env node
// Compare the old page and integrated page through their actual frame callbacks.
'use strict';
const fs=require('node:fs'),os=require('node:os'),path=require('node:path'),cp=require('node:child_process');
const {host}=require('./page');
// Newer baselines include motion objects/typed arrays. Compare their values,
// including NaN, rather than the identities of objects from independent hosts.
function sameState(a,b) {
  if(Object.is(a,b))return true;
  if(!a||!b||typeof a!=='object'||typeof b!=='object')return false;
  const keys=Object.keys(a);
  return keys.length===Object.keys(b).length&&keys.every(key=>Object.hasOwn(b,key)&&sameState(a[key],b[key]));
}
const args=process.argv.slice(2);
function flag(name,fallback) {const i=args.indexOf(`--${name}`);return i<0?fallback:args[i+1];}
const current=path.resolve(flag('current',path.join(__dirname,'../murmuration.html')));
const ref=flag('baseline-ref','0d3078f');
let base=flag('baseline',null),temp;

const cases=flag('cases',null)?.split(',')||['seed=1&n=80&calm','seed=7&n=80&calm','seed=1&n=80&falcon','seed=7&n=80&falcon'];
const seconds=Number(flag('seconds','15')),dtMs=Number(flag('dt-ms',String(1000/60)));
if(!Number.isFinite(seconds)||seconds<=0||!Number.isFinite(dtMs)||dtMs<=0)throw new Error('invalid seconds or dt-ms');
const frames=Math.round(seconds*1000/dtMs);
if(!Number.isSafeInteger(frames)||frames<1)throw new Error('duration must contain at least one frame');
const inputFile=flag('inputs',null),inputSource=inputFile?fs.readFileSync(inputFile):null;
const inputs=inputSource?JSON.parse(inputSource):[];
if(!Array.isArray(inputs)||inputs.some(e=>!Number.isFinite(e.atMs)||e.atMs<0||typeof e.type!=='string'))throw new Error('invalid input replay file');
inputs.sort((a,b)=>a.atMs-b.atMs);
if(!base) {temp=fs.mkdtempSync(path.join(os.tmpdir(),'murmuration-baseline-'));base=path.join(temp,'murmuration.html');
  fs.writeFileSync(base,cp.execFileSync('git',['show',`${ref}:murmuration.html`],{cwd:path.dirname(current)}));}
const results=[];
try {
for(const query of cases) {
  const a=host(base,{query}),b=host(current,{query});
  let samples=0,nextInput=0;
  for(let frame=1;frame<=frames;frame++) {
    while(nextInput<inputs.length&&inputs[nextInput].atMs<=frame*dtMs) {
      const {atMs,type,...detail}=inputs[nextInput++];a.dispatch(type,detail);b.dispatch(type,detail);
    }
    a.frame(dtMs);b.frame(dtMs);
    const x=a.snapshot(),y=b.snapshot();
    for(const key of ['px','py','pz','vx','vy','vz']) {
      const u=x.arrays[key],v=y.arrays[key];if(u.length!==v.length)throw new Error(`${query} frame ${frame} ${key} length ${u.length} != ${v.length}`);
      for(let i=0;i<u.length;i++)if(!Object.is(u[i],v[i]))throw new Error(`${query} frame ${frame} ${key}[${i}] ${u[i]} != ${v[i]}`);
    }
    for(const key of Object.keys(x.fal)) if(!sameState(x.fal[key],y.fal[key]))
      throw new Error(`${query} frame ${frame} fal.${key} ${x.fal[key]} != ${y.fal[key]}`);
    if(JSON.stringify(x.hunts)!==JSON.stringify(y.hunts))throw new Error(`${query} frame ${frame} hunt history differs`);
    samples++;
  }
  results.push({query,frames:samples,baselineScripts:a.assets,currentScripts:b.assets,
    drawCalls:{baseline:a.canvasCalls,current:b.canvasCalls},hunts:b.snapshot().hunts.length});
}
console.log(JSON.stringify({status:'equal',baseline:base,current,baselineRef:temp?ref:null,dtMs,seconds,
  inputs:inputSource?{file:path.resolve(inputFile),sha256:require('node:crypto').createHash('sha256').update(inputSource).digest('hex'),count:inputs.length,
    policy:'dispatch before first frame whose end time reaches atMs',events:inputs}:null,results}));
} finally {if(temp)fs.rmSync(temp,{recursive:true,force:true});}
