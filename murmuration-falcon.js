// Headless hunt measurements for murmuration.html, scored against falcon/refs/hunting_notes.md.
//   node murmuration-falcon.js [seconds=300] [query="seed=1&n=400"] [--json]
//   node murmuration-falcon.js --merge run1.json run2.json ...   pool several --json runs (e.g. seeds run in parallel)
// Runs the page under node (same stubs as murmuration-check.js) with spontaneous hunts and reports
// each observable next to its measured target. World units: 0.5 m.

const fs = require('fs'), vm = require('vm'), path = require('path');
const args = process.argv.slice(2), json = args.includes('--json');
const pos = args.filter(a => !a.startsWith('--'));
const merge = args.includes('--merge');
const secs = merge ? 0 : +(pos[0] || 300), query = merge ? '' : pos[1] || 'seed=1&n=400';
const raw = merge ? pool(pos.map(f => JSON.parse(fs.readFileSync(f, 'utf8')))) : simulate();
report(raw);

function pool(runs) {
  const out = { runs: runs.map(r => r.run), strikes: [], hunts: [], gaps: [], waveSpeeds: [], waveReach: [], control: [], pulses: 0 };
  for (const r of runs) for (const k of ['strikes', 'hunts', 'gaps', 'waveSpeeds', 'waveReach', 'control']) out[k].push(...r[k]);
  out.pulses = runs.reduce((a, r) => a + r.pulses, 0);
  return out;
}

function simulate() {

const htmlArg = args.find(a => a.startsWith('--html='));   // --html=FILE: measure another copy of the page
let src = fs.readFileSync(htmlArg ? htmlArg.slice(7) : path.join(__dirname, 'murmuration.html'), 'utf8');
src = src.slice(src.indexOf('<script>') + 8, src.lastIndexOf('</script>'));
const noop = () => {};
const canvasProxy = () => new Proxy({}, { get: (t, p) => (p in t ? t[p] : (p === 'data' ? [] : (...a) => canvasProxy())), set: (t, p, v) => (t[p] = v, true) });
const el = () => ({ textContent: '', classList: { add: noop, toggle: noop, remove: noop, contains: () => false }, getContext: () => canvasProxy(), width: 0, height: 0, style: {}, appendChild: noop });
const win = {
  document: { getElementById: el, createElement: el, body: { appendChild: noop }, addEventListener: noop },
  innerWidth: 1440, innerHeight: 900, devicePixelRatio: 1,
  location: { search: '?' + query + '&debug' }, URLSearchParams, performance, Math, console,
  requestAnimationFrame: noop, addEventListener: noop, setTimeout: noop, clearTimeout: noop,
  Float32Array, Float64Array, Int32Array, Int8Array, Uint32Array, Uint8Array, Array,
  Path2D: class { moveTo() {} lineTo() {} closePath() {} },
};
win.window = win;
vm.createContext(win);
vm.runInContext(src, win);
const m = win.murm, N = m.N;

function flockShape() {                          // radius of gyration, polarization, clusters (link 8 u = 4 m)
  let cx = 0, cy = 0, cz = 0, Px = 0, Py = 0, Pz = 0;
  for (let i = 0; i < N; i++) {
    cx += m.px[i]; cy += m.py[i]; cz += m.pz[i];
    const s = Math.hypot(m.vx[i], m.vy[i], m.vz[i]); Px += m.vx[i] / s; Py += m.vy[i] / s; Pz += m.vz[i] / s;
  }
  cx /= N; cy /= N; cz /= N;
  let r2 = 0;
  for (let i = 0; i < N; i++) r2 += (m.px[i] - cx) ** 2 + (m.py[i] - cy) ** 2 + (m.pz[i] - cz) ** 2;
  const par = Int32Array.from({ length: N }, (_, i) => i);
  const find = i => { while (par[i] !== i) i = par[i] = par[par[i]]; return i; };
  for (let i = 0; i < N; i++) for (let j = i + 1; j < N; j++)
    if ((m.px[i] - m.px[j]) ** 2 + (m.py[i] - m.py[j]) ** 2 + (m.pz[i] - m.pz[j]) ** 2 < 64) par[find(i)] = find(j);
  const size = new Map();
  for (let i = 0; i < N; i++) { const r = find(i); size.set(r, (size.get(r) || 0) + 1); }
  const big = [...size.values()].filter(v => v >= .05 * N).length;   // groups of at least 5 % of the flock
  return { rg: Math.sqrt(r2 / N), phi: Math.hypot(Px, Py, Pz) / N, groups: big };
}

const dt = 1 / 60;
let simT = 0, seen = 0;
const strikes = [], hunts = [], pulses = [], pending = [];
const shapeLog = [];                             // flock shape twice a second
const trig = [];                                 // wave triggers: [t, pulse index, distance from the seed]
const prevWT = new Float32Array(N).fill(1e3);
for (let s = 0; s < secs * 60; s++) {
  simT += dt; m.step(dt, simT);
  const log = m.huntLog;
  for (; seen < log.length + 0 && log[seen]; seen++) {
    const e = log[seen];
    if (e.type === 'strike') { strikes.push(e); pending.push(e); }
    else if (e.type === 'hunt') hunts.push(e);
    else if (e.type === 'pulse') pulses.push(e);
  }
  if (log.length >= 400) seen = log.length;      // the page keeps the last 400 events
  for (let i = 0; i < N; i++) {                  // a fresh roll: wT reset to 0 since the last frame
    if (m.wT[i] < prevWT[i]) {
      const k = pulses.findIndex(p => p.id === m.wP[i]), p = pulses[k];
      if (p) trig.push([simT - p.t, k, Math.hypot(m.px[i] - p.x, m.py[i] - p.y, m.pz[i] - p.z)]);
    }
    prevWT[i] = m.wT[i];
  }
  if (s % 30 === 0) shapeLog.push({ t: simT, falcon: m.fal.on, ...flockShape() });
}

// Flock response around each strike: baseline 1 s before the pass, then the next 3 s.
const at = t => shapeLog.reduce((b, x) => Math.abs(x.t - t) < Math.abs(b.t - t) ? x : b, shapeLog[0]);
for (const e of strikes) {
  const before = at(e.t - 1), after = shapeLog.filter(x => x.t > e.t && x.t <= e.t + 3);
  if (!after.length) continue;
  e.expand = Math.max(...after.map(x => x.rg)) / before.rg;
  e.phiMin = Math.min(...after.map(x => x.phi));
  e.split = after.some(x => x.groups > 1);
}

// Wave front speed per pulse: slope of distance against trigger time (least squares, through the seed).
const waveSpeeds = [], waveReach = [];
pulses.forEach((p, k) => {
  const pts = trig.filter(r => r[1] === k && r[0] > 0);
  if (pts.length < 15) return;
  let stt = 0, std = 0;
  for (const [tt, , d] of pts) { stt += tt * tt; std += tt * d; }
  waveSpeeds.push(std / stt); waveReach.push(pts.length / N);
});

// Control windows: the same expansion and split tests 3 s ahead of a moment with no falcon for 10 s around it.
const control = [];
for (const x of shapeLog) {
  const win = shapeLog.filter(y => y.t >= x.t - 10 && y.t <= x.t + 3);
  if (x.t < 20 || win.some(y => y.falcon) || win[win.length - 1].t < x.t + 2.9) continue;
  const after = win.filter(y => y.t > x.t), before = at(x.t - 1);
  control.push({ expand: Math.max(...after.map(y => y.rg)) / before.rg, split: after.some(y => y.groups > 1) });
}
const gaps = [];
for (let k = 1; k < strikes.length; k++) if (strikes[k].t - strikes[k - 1].t < 30) gaps.push(strikes[k].t - strikes[k - 1].t);
return { run: { secs, query }, strikes, hunts, gaps, waveSpeeds, waveReach, control, pulses: pulses.length };
}

function report({ strikes, hunts, gaps, waveSpeeds, waveReach, control, pulses, runs }) {
const mean = a => a.length ? a.reduce((x, y) => x + y, 0) / a.length : NaN;
const median = a => { if (!a.length) return NaN; const b = [...a].sort((x, y) => x - y); return b[b.length >> 1]; };
const frac = (a, f) => a.length ? a.filter(f).length / a.length : NaN;
const done = hunts.filter(h => !h.cut);
const res = {
  
  attackMix: [0, 1, 2].map(k => frac(strikes, e => e.kind === k)),
  peakSpeedFromAbove_ms: median(strikes.filter(e => e.kind === 0).map(e => e.peak * .5)),
  peakSpeedAll_ms: median(strikes.map(e => e.peak * .5)),
  meanN: mean(strikes.map(e => e.n).filter(Number.isFinite)),
  stoopDur_s: median(strikes.map(e => e.dur)),
  pnDur_s: median(strikes.map(e => e.pnDur)),
  pnPath_m: median(strikes.map(e => e.pnPath * .5)),
  controlExpanded20: frac(control, e => e.expand > 1.2),
  controlSplit: frac(control, e => e.split),
  miss_m: median(strikes.map(e => e.miss * .5)),
  strikeContact: frac(strikes, e => e.contact),
  huntContact: frac(done, h => h.contact),
  strikesPerHunt: mean(done.map(h => h.strikes)),
  gapsUnder5s: frac(gaps, g => g < 5),
  flashFlagged: frac(strikes, e => e.flash),
  expanded20: frac(strikes.filter(e => e.expand), e => e.expand > 1.2),
  split: frac(strikes.filter(e => e.expand), e => e.split),
  phiMin: median(strikes.filter(e => e.phiMin).map(e => e.phiMin)),
  huntsWithWaves: frac(done, h => h.waves),
  waveSpeed_ms: { mean: mean(waveSpeeds) * .5, min: Math.min(...waveSpeeds) * .5, max: Math.max(...waveSpeeds) * .5, n: waveSpeeds.length },
  waveReach: median(waveReach),
};
if (json) { console.log(JSON.stringify({ strikes, hunts, gaps, waveSpeeds, waveReach, control, pulses, run: { secs, query } })); return; }
const f = (v, d = 2) => Number.isFinite(v) ? v.toFixed(d) : '—';
const rows = [
  ['strikes per hunt', f(res.strikesPerHunt), '~3 (Procaccini 2011 Table 2, derived)'],
  ['strike gaps under 5 s', f(res.gapsUnder5s), '0.31 (Procaccini 2011)'],
  ['attack mix above/side/below', res.attackMix.map(v => f(v)).join('/'), '0.69/0.21/0.10 Storms 2019; 0.30/0.57/0.13 Procaccini 2011'],
  ['peak speed from above, m/s', f(res.peakSpeedFromAbove_ms, 1), '31–39 wild stoops (Alerstam 1987, abstract)'],
  ['peak speed, all strikes, m/s', f(res.peakSpeedAll_ms, 1), 'mean stoop ~25 m/s'],
  ['mean PN gain N', f(res.meanN), 'median 2.6, IQR 1.5–3.2 (Brighton 2017)'],
  ['stoop duration, s', f(res.stoopDur_s, 1), '—'],
  ['PN phase duration, s', f(res.pnDur_s, 1), 'median 4.9 (Brighton 2017)'],
  ['PN phase path, m', f(res.pnPath_m, 0), '47–114 (Brighton 2017)'],
  ['median miss distance, m', f(res.miss_m), '—'],
  ['strikes with a contact', f(res.strikeContact), '—'],
  ['hunts with a contact (page CONTACT)', f(res.huntContact), '0.23–0.24 success (Zoratto 2010, Procaccini 2011)'],
  ['strikes flagged flash expansion', f(res.flashFlagged), '0.25 (Storms 2019)'],
  ['strikes with >20 % expansion', f(res.expanded20), '0.25 flash expansion (Storms 2019)'],
  ['  flagged / not flagged', `${f(frac(strikes.filter(e => e.expand && e.flash), e => e.expand > 1.2))}/${f(frac(strikes.filter(e => e.expand && !e.flash), e => e.expand > 1.2))}`, ''],
  ['strikes followed by a split', f(res.split), '0.22 (78 % do not split; Storms 2019)'],
  ['  same tests with no falcon (expand/split)', `${f(res.controlExpanded20)}/${f(res.controlSplit)}`, 'baseline of the metric'],
  ['median lowest polarization after a strike', f(res.phiMin), '—'],
  ['hunts with waves', f(res.huntsWithWaves), '0.36–0.42 (Procaccini 2011)'],
  ['wave speed mean (min–max), m/s', `${f(res.waveSpeed_ms.mean, 1)} (${f(res.waveSpeed_ms.min, 1)}–${f(res.waveSpeed_ms.max, 1)}), ${res.waveSpeed_ms.n} pulses`, '13 (3.7–25) (Procaccini 2011)'],
  ['median share of flock reached by a pulse', f(res.waveReach), '—'],
];
console.log(`${runs ? runs.length + ' runs' : secs + ' s, ' + query}: ${strikes.length} strikes in ${hunts.length} hunts, ${pulses} wave pulses`);
for (const [k, v, t] of rows) console.log(`${k.padEnd(42)} ${String(v).padEnd(30)} ${t}`);
}
