#!/usr/bin/env node
'use strict';
// Optional actual-page raster probes. This is native Canvas, not browser layout QA.
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const { host, hash } = require('./page');
const root = path.resolve(__dirname, '..');
const moduleArg = process.argv.find(x => x.startsWith('--canvas-module='));
const canvasModule = moduleArg?.slice('--canvas-module='.length) || process.env.CANVAS_MODULE || '@napi-rs/canvas';
const outputArg = process.argv.find(x => x.startsWith('--output='));
const output = path.resolve(outputArg?.slice('--output='.length) || path.join(root, 'sim-output'));
fs.mkdirSync(output, { recursive: true });
const options = { canvasModule, width: 1440, height: 900, query: 'painted' };
const calmQuery = 'seed=1&calm&n=400&warm=20&painted';
const artifacts = [];
function image(page, id, name) {
  const e = page.document.getElementById(id);
  const surface = e._nativeCanvas;
  assert(surface, 'native Canvas was not instantiated');
  const buffer = surface.toBuffer('image/png');
  fs.writeFileSync(path.join(output, name), buffer);
  const result = { name, sha256: hash(buffer), bytes: buffer.length, width: surface.width, height: surface.height };
  assert(result.bytes > 1000, 'empty or trivial raster');
  artifacts.push(result);
  return result.sha256;
}

// Known-good: real XYZ drawing is reached. Known-bad: flattening the atlas changes pixels.
const flock = host(path.join(root, 'murmuration.html'), { ...options, query: calmQuery });
let samples = 0;
const M = flock.state.Motion, sample = M.sampleGait;
M.sampleGait = (...args) => { samples++; return sample(...args); };
flock.frame();
assert(samples > 0, 'default renderer did not sample XYZ gait surfaces');
const calm = image(flock, 'c', 'flock.png');
assert.equal(artifacts.at(-1).width, options.width);
assert.equal(artifacts.at(-1).height, options.height);
// The page deliberately accumulates trails: compare equal draw histories in fresh hosts.
const repeat = host(path.join(root, 'murmuration.html'), { ...options, query: calmQuery });
repeat.frame();
assert.equal(image(repeat, 'c', 'flock-repeat.png'), calm, 'equal simulation and drawing histories must reproduce pixels');
const flattened = host(path.join(root, 'murmuration.html'), { ...options, query: calmQuery });
for (const clip of Object.values(flattened.state.Motion.data.species.starling.clips))
  for (const frame of clip.frames) for (let j = 2; j < frame.length; j += 3) frame[j] = 0;
flattened.frame();
assert.notEqual(image(flattened, 'c', 'flattened-z-sentinel.png'), calm, 'raster oracle cannot distinguish flattened XYZ geometry');

const attack = host(path.join(root, 'murmuration.html'), { ...options, query: 'seed=7&calm&n=400&warm=20&painted' });
attack.dispatch('pointerdown', { clientX: 650, clientY: 300 });
assert(attack.state.fal.on, 'actual pointer handler did not launch a hunt');
for (let k = 0; k < 120; k++) attack.frame();
image(attack, 'c', 'attack.png');

// Exercise actual viewer handlers; HTML/CSS layout is supplied by the host, not a browser.
const viewer = host(path.join(root, 'motion-lab.html'), { ...options, width: 1100, height: 650 });
const el = id => viewer.document.getElementById(id);
el('view').value = 'front';
el('phase').value = '0'; el('phase').oninput(); viewer.frame();
const phase0 = image(viewer, 'bird', 'starling-front-phase0.png');
el('phase').value = '.46'; el('phase').oninput(); viewer.frame();
assert.notEqual(image(viewer, 'bird', 'starling-front-phase46.png'), phase0);
assert.equal(el('play').textContent, 'Play');
const views = [];
for (const species of ['starling', 'falcon']) {
  el('species').value = species; el('species').onchange();
  for (const view of ['top', 'front', 'side', 'quarter']) {
    el('view').value = view; viewer.frame();
    views.push(image(viewer, 'bird', `${species}-${view}.png`));
    assert(el('readout').textContent.includes('Span in this pose'));
  }
}
assert.equal(new Set(views).size, 8, 'species/view selection did not change the raster');
el('clip').value = 'pullout'; el('phase').value = '.3'; el('phase').oninput(); viewer.frame();
image(viewer, 'bird', 'falcon-pullout.png');
el('play').onclick(); assert.equal(el('play').textContent, 'Pause');
console.log(JSON.stringify({ verdict: 'TARGET_PASS', scope: 'actual-page native Canvas drawing and viewer JavaScript; browser DOM/CSS unobserved',
  node: process.version, canvasModule, page: flock.htmlSha256, assets: flock.assets, samples, artifacts }, null, 2));
