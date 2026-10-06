// Headless hunt measurements for murmuration.html, scored against falcon/refs/hunting_notes.md.
//   node murmuration-falcon.js [seconds=300] [query="seed=1&n=400"] [--json]
//   node murmuration-falcon.js --merge run1.json run2.json ...   pool several --json runs (e.g. seeds run in parallel)
//   --flythrough   list every time the falcon overlaps the flock on screen, with what really happened and a URL to replay it
//   --view=WxH     browser window size (default 1440x900); a replay URL only reproduces the run in a window of this size
//   --export=T0:T1 [--out=FILE]   write falcon and bird trajectories for replay/replay_build.py (Blender)
// Runs the page under node (same stubs as murmuration-check.js) with spontaneous hunts and reports
// each observable next to its measured target. World units: 0.5 m.

const fs = require('fs'), vm = require('vm'), path = require('path');
const args = process.argv.slice(2), json = args.includes('--json');
const pos = args.filter(a => !a.startsWith('--'));
const merge = args.includes('--merge');
const secs = merge ? 0 : +(pos[0] || 300), query = merge ? '' : pos[1] || 'seed=1&n=400';
const LISTS = ['strikes', 'stoops', 'hunts', 'gaps', 'waveSpeeds', 'waveReach', 'control', 'flythrough', 'posNear', 'density', 'camDepth'];
const raw = merge ? pool(pos.map(f => JSON.parse(fs.readFileSync(f, 'utf8')))) : simulate();
report(raw);

function pool(runs) {
  const out = { runs: runs.map(r => r.run), pulses: 0 };
  for (const k of LISTS) out[k] = [];
  for (const r of runs) for (const k of LISTS) out[k].push(...(r[k] || []));
  out.pulses = runs.reduce((a, r) => a + r.pulses, 0);
  return out;
}

function simulate() {

const htmlArg = args.find(a => a.startsWith('--html='));
const viewArg = args.find(a => a.startsWith('--view='));   // --view=WxH: the browser window (the camera framing, and so the run, depends on it)
const VIEW = viewArg ? viewArg.slice(7).split('x').map(Number) : [1440, 900];   // --html=FILE: measure another copy of the page
let src = fs.readFileSync(htmlArg ? htmlArg.slice(7) : path.join(__dirname, 'murmuration.html'), 'utf8');
src = src.slice(src.indexOf('<script>') + 8, src.lastIndexOf('</script>'));
const noop = () => {};
const canvasProxy = () => new Proxy({}, { get: (t, p) => (p in t ? t[p] : (p === 'data' ? [] : (...a) => canvasProxy())), set: (t, p, v) => (t[p] = v, true) });
const el = () => ({ textContent: '', classList: { add: noop, toggle: noop, remove: noop, contains: () => false }, getContext: () => canvasProxy(), width: 0, height: 0, style: {}, appendChild: noop });
const win = {
  document: { getElementById: el, createElement: el, body: { appendChild: noop }, addEventListener: noop },
  innerWidth: VIEW[0], innerHeight: VIEW[1], devicePixelRatio: 1,
  location: { search: '?' + query + '&debug' }, URLSearchParams, performance, Math, console,
  requestAnimationFrame: noop, addEventListener: noop, setTimeout: noop, clearTimeout: noop,
  Float32Array, Float64Array, Int32Array, Int8Array, Uint32Array, Uint8Array, Array,
  Path2D: class { moveTo() {} lineTo() {} closePath() {} },
};
win.window = win;
vm.createContext(win);
vm.runInContext(src, win);
const m = win.murm, N = m.N, C = m.cam, K = m.consts;

// ---- screen-space overlap of the falcon with the flock ("fly-throughs")
// A frame counts when at least 3 drawn birds overlap the drawn falcon on screen. Each such frame records how
// far the falcon really is from the flock: the nearest bird in 3D (u) and the depth gap along the camera axis.
const NEAR = 12;                                 // u (6 m): beyond this the falcon is clear of every bird
const CLOSE = 6;                                 // u (3 m): birds this close should get out of the way
const fly = [];
const proj = (x, y, z) => { const yr = y - C.CAM_H, zc = yr * C.st + z * C.ct; return [x / zc, (yr * C.ct - z * C.st) / zc, zc]; };
function flyFrame(t) {
  const fal = m.fal;
  const [uf, vf, zf] = proj(fal.x, fal.y, fal.z);
  if (zf < 10) return;
  const rf = K.FALCON_SPAN * C.sizeK / 2 / zf;
  let hits = 0, d3 = 1e9, nDodge = 0, nAlarm = 0, nRoll = 0;
  const zs = [], near = [], dod = [];
  for (let i = 0; i < N; i++) {
    const [ub, vb, zb] = proj(m.px[i], m.py[i], m.pz[i]);
    if (Math.hypot(ub - uf, vb - vf) < rf + K.SPAN * C.sizeK * m.size[i] / 2 / zb) { hits++; zs.push(zb); }
    const d = Math.hypot(m.px[i] - fal.x, m.py[i] - fal.y, m.pz[i] - fal.z);
    if (d < d3) d3 = d;
    if (d < CLOSE) near.push(i);
    if (m.dodge[i]) { nDodge++; dod.push(i); }
    if (m.alarm[i] > .3) nAlarm++;
    if (m.wT[i] < .55) nRoll++;
  }
  if (hits < 3) return;
  zs.sort((a, b) => a - b);
  fly.push({ t, mode: fal.mode, mt: fal.mt, d3, dz: zf - zs[zs.length >> 1], hits, nDodge, nAlarm, nRoll, flee: fal.fleeK, near, dod });
}

// ---- optical density: projected wing area of the birds per unit area of the flock's outline on screen
// (a stand-in for the observer's "blackening"; Storms 2019 note it is easily confused with waves).
function hullArea(pts) {                         // monotone chain
  pts.sort((a, b) => a[0] - b[0] || a[1] - b[1]);
  const cr = (o, a, b) => (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]);
  const lo = [], hi = [];
  for (const p of pts) { while (lo.length > 1 && cr(lo[lo.length - 2], lo[lo.length - 1], p) <= 0) lo.pop(); lo.push(p); }
  for (let k = pts.length - 1; k >= 0; k--) { const p = pts[k]; while (hi.length > 1 && cr(hi[hi.length - 2], hi[hi.length - 1], p) <= 0) hi.pop(); hi.push(p); }
  const h = lo.slice(0, -1).concat(hi.slice(0, -1));
  let a = 0;
  for (let k = 0; k < h.length; k++) { const p = h[k], q = h[(k + 1) % h.length]; a += p[0] * q[1] - q[0] * p[1]; }
  return Math.abs(a) / 2;
}
function opticalDensity() {
  const pts = [];
  let wing = 0;
  for (let i = 0; i < N; i++) {
    const x = m.px[i], y = m.py[i], z = m.pz[i], [u, v, zc] = proj(x, y, z);
    pts.push([u, v]);
    const s = Math.hypot(m.vx[i], m.vy[i], m.vz[i]) + 1e-6, fx = m.vx[i] / s, fy = m.vy[i] / s, fz = m.vz[i] / s;
    const rl = Math.hypot(fx, fz) + 1e-6, rx = fz / rl, rz = -fx / rl;
    const nx = fy * rz, ny = fz * rx - fx * rz, nz = -fy * rx;                     // wing normal before the roll (as birdFrame)
    const e = m.wT[i] < .25 ? m.wT[i] / .25 : m.wT[i] < .55 ? 1 - (m.wT[i] - .25) / .3 : 0;
    const bk = m.bank[i] + m.attSD * m.att[i] + (e > 0 ? m.wS[i] * K.WAVE_ROLL * m.wL[i] * e * e * (3 - 2 * e) : 0);
    const cb = Math.cos(bk), sb = Math.sin(bk);
    const Nx = nx * cb + rx * sb, Ny = ny * cb, Nz = nz * cb + rz * sb;
    const vl = Math.hypot(x, y - C.CAM_H, z);
    const r = K.SPAN * C.sizeK * m.size[i] / zc;
    wing += r * r * Math.abs((Nx * x + Ny * (y - C.CAM_H) + Nz * z) / vl);
  }
  return wing / hullArea(pts);
}

// ---- --export=T0:T1 [--out=FILE]: falcon and bird trajectories at 30 Hz for replay/replay_build.py
const expArg = args.find(a => a.startsWith('--export='));
const exp = expArg ? expArg.slice(9).split(':').map(Number) : null;
const outArg = args.find(a => a.startsWith('--out='));
const rec = exp ? { falcon: { pos: [], vel: [], mode: [] }, birds: { pos: [], state: [] }, t: [], check: [] } : null;
function recordFrame(t, s) {
  const fal = m.fal, r2 = v => Math.round(v * 100) / 100;
  rec.t.push(r2(t));
  rec.falcon.pos.push(fal.on ? [r2(fal.x), r2(fal.y), r2(fal.z)] : null);
  rec.falcon.vel.push(fal.on ? [r2(fal.vx), r2(fal.vy), r2(fal.vz)] : null);
  rec.falcon.mode.push(fal.on ? fal.mode : 'off');
  const pos = new Array(3 * N), st = new Array(N);
  for (let i = 0; i < N; i++) {
    pos[3 * i] = r2(m.px[i]); pos[3 * i + 1] = r2(m.py[i]); pos[3 * i + 2] = r2(m.pz[i]);
    const flee = fal.on && fal.fleeK > .5 && Math.hypot(m.px[i] - fal.x, m.py[i] - fal.y, m.pz[i] - fal.z) < K.R_FLEE;
    st[i] = (m.dodge[i] ? 1 : 0) | (m.alarm[i] > .3 ? 2 : 0) | (m.wT[i] < .55 ? 4 : 0) | (flee ? 8 : 0);
  }
  rec.birds.pos.push(pos); rec.birds.state.push(st);
  if (s % 60 === 0) for (const i of [0, N >> 1, N - 1]) {   // the page's own projection of three birds, once a second, to check the replay camera
    const [u, v] = proj(m.px[i], m.py[i], m.pz[i]);
    rec.check.push({ t: r2(t), i, sx: C.cx + u * C.f, sy: C.cy - v * C.f });
  }
}

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
const strikes = [], stoops = [], hunts = [], pulses = [], pending = [];
const camDepth = [];                             // falcon depth along the camera axis (u) and mode, twice a second
const posNear = [];                              // falcon to nearest bird while it waits in position, twice a second (u)
const dens = [];                                 // optical density twice a second
const shapeLog = [];                             // flock shape twice a second
const trig = [];                                 // wave triggers: [t, pulse index, distance from the seed]
const prevWT = new Float32Array(N).fill(1e3);
for (let s = 0; s < secs * 60; s++) {
  simT += dt; m.step(dt, simT);
  const log = m.huntLog;
  for (; seen < log.length + 0 && log[seen]; seen++) {
    const e = log[seen];
    if (e.type === 'strike') { strikes.push(e); pending.push(e); }
    else if (e.type === 'stoop') stoops.push(e);
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
  if (m.fal.on) flyFrame(simT);
  if (s % 30 === 0) {
    dens.push([simT, m.fal.on, opticalDensity()]);
    if (m.fal.on) camDepth.push([proj(m.fal.x, m.fal.y, m.fal.z)[2], m.fal.mode, simT]);
    if (m.fal.on && m.fal.mode === 'position') {
      let d = 1e9;
      for (let i = 0; i < N; i++) d = Math.min(d, Math.hypot(m.px[i] - m.fal.x, m.py[i] - m.fal.y, m.pz[i] - m.fal.z));
      posNear.push(d);
    }
  }
  if (rec && simT >= exp[0] && simT <= exp[1] && s % 2 === 0) recordFrame(simT, s);
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

// Wave pulses in the 5 s before each attack begins (Storms 2019 time attacks from the falcon's switch
// to a trajectory aimed at a bird, which here is the start of the stoop).
for (const e of stoops) e.pulseBefore = pulses.some(p => p.t >= e.t - 5 && p.t < e.t);

// Fly-through episodes: overlap frames less than 0.2 s apart in one falcon mode, kept if at least 0.1 s long.
const flythrough = [];
for (let k = 0; k < fly.length;) {
  let j = k;
  while (j + 1 < fly.length && fly[j + 1].t - fly[j].t < .2 && fly[j + 1].mode === fly[k].mode) j++;
  const fr = fly.slice(k, j + 1); k = j + 1;
  if (fr[fr.length - 1].t - fr[0].t < .1) continue;
  const best = fr.reduce((a, b) => b.d3 < a.d3 ? b : a);
  const nearSet = new Set(fr.flatMap(x => x.near)), dodSet = new Set(fr.flatMap(x => x.dod));
  const modes = [...new Set(fr.map(x => x.mode))];
  const strike = modes.includes('stoop') ? strikes.find(e => e.t >= fr[0].t - .1 && e.t <= fr[fr.length - 1].t + 1) : null;
  const ep = {
    t0: fr[0].t, t1: fr[fr.length - 1].t, modes, mode: best.mode, mt: best.mt, d3: best.d3, dz: best.dz,
    near: nearSet.size, dodgers: dodSet.size, flee: Math.max(...fr.map(x => x.flee)), alarmed: Math.max(...fr.map(x => x.nAlarm)),
    strike: strike ? { miss: strike.miss, caAlong: strike.caAlong, flash: strike.flash } : null,
  };
  const reacted = ep.dodgers > 0 || ep.flee > .5;
  ep.bucket = ep.d3 > NEAR ? (ep.strike && ep.strike.caAlong > .8 ? 'over-lead' : 'illusion: depth')
    : ep.mode !== 'stoop' ? (reacted ? 'non-stoop, reacted' : ep.mode === 'climb' && ep.mt < 1.5 ? 'non-stoop gap: carry-through' : 'non-stoop gap: ' + ep.mode)
    : ep.flee > .5 ? 'stoop, flash expansion' : ep.near - ep.dodgers > ep.dodgers ? 'stoop, dodge too narrow' : 'stoop, dodged';
  ep.url = `murmuration.html?${query}&warm=${Math.max(0, ep.t0 - 2).toFixed(1)}&inset (window ${VIEW.join('×')})`;
  flythrough.push(ep);
}

// Optical density before and after each attack begins, against moments with no falcon for 10 s around them.
const density = [];
const dMean = (a, b) => { const v = dens.filter(x => x[0] >= a && x[0] < b).map(x => x[2]); return v.length ? v.reduce((p, q) => p + q, 0) / v.length : NaN; };
for (const e of stoops) density.push({ kind: 'attack', pre: dMean(e.t - 5, e.t), post: dMean(e.t, e.t + 2), base: dMean(e.t - 15, e.t - 10) });
for (const x of dens) {
  if (x[0] < 20 || x[1] || dens.some(y => Math.abs(y[0] - x[0]) <= 10 && y[1])) continue;
  density.push({ kind: 'control', pre: dMean(x[0] - 5, x[0]), post: dMean(x[0], x[0] + 2), base: dMean(x[0] - 15, x[0] - 10) });
}

if (rec) {
  const file = outArg ? outArg.slice(6) : path.join(__dirname, 'replay', 'out', `replay_${query.replace(/[^a-z0-9=]+/gi, '_')}_${exp[0]}-${exp[1]}.json`);
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, JSON.stringify({
    meta: { query, t0: exp[0], t1: exp[1], hz: 30, unit_m: m.M, N,
      cam: { W: C.W, H: C.H, f: C.f, cx: C.cx, cy: C.cy, CAM_H: C.CAM_H, pitch: Math.atan2(C.st, C.ct), HORIZON: C.HORIZON, sizeK: C.sizeK },
      consts: K, state_bits: { dodge: 1, alarm: 2, rolling: 4, flee: 8 } },
    t: rec.t, falcon: rec.falcon, birds: rec.birds, check: rec.check,
    events: [...stoops, ...strikes, ...pulses].filter(e => e.t >= exp[0] - 1 && e.t <= exp[1] + 1).sort((a, b) => a.t - b.t),
    episodes: flythrough.filter(e => e.t1 >= exp[0] && e.t0 <= exp[1]),
  }));
  console.error(`wrote ${file} (${rec.t.length} frames)`);
}
return { run: { secs, query }, strikes, stoops, hunts, gaps, waveSpeeds, waveReach, control, flythrough, posNear, density, camDepth, pulses: pulses.length };
}

function report({ strikes, stoops = [], hunts, gaps, waveSpeeds, waveReach, control, flythrough = [], posNear = [], density = [], camDepth = [], pulses, runs }) {
const mean = a => a.length ? a.reduce((x, y) => x + y, 0) / a.length : NaN;
const median = a => { if (!a.length) return NaN; const b = [...a].sort((x, y) => x - y); return b[b.length >> 1]; };
const frac = (a, f) => a.length ? a.filter(f).length / a.length : NaN;
const quant = (a, q) => { if (!a.length) return NaN; const b = [...a].sort((x, y) => x - y); return b[Math.min(b.length - 1, Math.floor(q * b.length))]; };
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
if (json) { console.log(JSON.stringify({ strikes, stoops, hunts, gaps, waveSpeeds, waveReach, control, flythrough, posNear, density, camDepth, pulses, run: { secs, query } })); return; }
const byKind = k => frac(strikes.filter(e => e.kind === k), e => e.flash);
const bySpd = k => frac(strikes.filter(e => (e.spd ?? 1) === k), e => e.flash);
const att = density.filter(d => d.kind === 'attack' && Number.isFinite(d.pre) && Number.isFinite(d.base));
const ctl = density.filter(d => d.kind === 'control' && Number.isFinite(d.pre) && Number.isFinite(d.base));
const ratio = (a, k) => median(a.map(d => d[k] / d.base));
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
  ['strikes flagged flash expansion', f(res.flashFlagged), '0.34 within 5 s (Storms 2019 Fig 6); 0.25 as the next event (Fig 3)'],
  ['  by attack above/side/below', [0, 1, 2].map(k => f(byKind(k))).join('/'), '0.42/0.11/0.22 (Fig 6)'],
  ['  by speed slow/medium/fast', [0, 1, 2].map(k => f(bySpd(k))).join('/'), '0.00/0.36/0.47 (Fig 6)'],
  ['  speed mix slow/medium/fast', [0, 1, 2].map(k => f(frac(strikes, e => (e.spd ?? 1) === k))).join('/'), '0.09/0.82/0.09 (Storms 2019)'],
  ['strikes with >20 % expansion', f(res.expanded20), '0.25 flash expansion (Storms 2019)'],
  ['  flagged / not flagged', `${f(frac(strikes.filter(e => e.expand && e.flash), e => e.expand > 1.2))}/${f(frac(strikes.filter(e => e.expand && !e.flash), e => e.expand > 1.2))}`, ''],
  ['strikes followed by a split', f(res.split), '—'],
  ['  flash expansions followed by a split', f(frac(strikes.filter(e => e.expand && e.flash), e => e.split)), '0.22 (Storms 2019 Fig 3)'],
  ['  same tests with no falcon (expand/split)', `${f(res.controlExpanded20)}/${f(res.controlSplit)}`, 'baseline of the metric'],
  ['median lowest polarization after a strike', f(res.phiMin), '—'],
  ['hunts with waves', f(res.huntsWithWaves), '0.36–0.42 (Procaccini 2011)'],
  ['wave speed mean (min–max), m/s', `${f(res.waveSpeed_ms.mean, 1)} (${f(res.waveSpeed_ms.min, 1)}–${f(res.waveSpeed_ms.max, 1)}), ${res.waveSpeed_ms.n} pulses`, '13 (3.7–25) (Procaccini 2011)'],
  ['median share of flock reached by a pulse', f(res.waveReach), '—'],
  ['attacks with a wave pulse in the 5 s before', f(frac(stoops, e => e.pulseBefore)), '0.28 (Storms 2019 Fig 3)'],
  ['optical density vs 10–15 s earlier, 5 s before attack', `${f(ratio(att, 'pre'))} (control ${f(ratio(ctl, 'pre'))})`, 'blackening clusters −4…+2 s (Storms 2019); timing only'],
  ['  same, 2 s after the attack begins', `${f(ratio(att, 'post'))} (control ${f(ratio(ctl, 'post'))})`, ''],
  ['falcon beside or behind the camera (all / positioned)', `${f(frac(camDepth, x => x[0] < 10))} / ${f(frac(camDepth.filter(x => x[1] === 'position'), x => x[0] < 10))}`, 'share of time; not drawn then'],
  ['falcon within 37 m of the camera (all / positioned)', `${f(frac(camDepth, x => x[0] < 75))} / ${f(frac(camDepth.filter(x => x[1] === 'position'), x => x[0] < 75))}`, '—'],
  ['falcon to nearest bird while positioned, m', `${f(median(posNear) * .5, 0)} (10–90 %: ${f(quant(posNear, .1) * .5, 0)}–${f(quant(posNear, .9) * .5, 0)})`, '—'],
];
console.log(`${runs ? runs.length + ' runs' : secs + ' s, ' + query}: ${strikes.length} strikes in ${hunts.length} hunts, ${pulses} wave pulses`);
for (const [k, v, t] of rows) console.log(`${k.padEnd(42)} ${String(v).padEnd(30)} ${t}`);

// Fly-throughs: times the drawn falcon overlaps at least 3 drawn birds, sorted by what really happened.
console.log(`\nfly-throughs on screen: ${flythrough.length} episodes (nearest bird ≤ 6 m counts as through the flock)`);
const buckets = {};
for (const e of flythrough) (buckets[e.bucket] = buckets[e.bucket] || []).push(e);
for (const [b, es] of Object.entries(buckets).sort((a, c) => c[1].length - a[1].length))
  console.log(`  ${b.padEnd(34)} ${String(es.length).padStart(4)}   nearest bird median ${f(median(es.map(e => e.d3)) * .5, 1)} m, depth gap median ${f(median(es.map(e => e.dz)) * .5, 1)} m`);
console.log(`  within 2 m, by mode: ${['stoop', 'climb', 'position', 'leave'].map(md => `${md} ${flythrough.filter(e => e.mode === md && e.d3 < 4).length}`).join(', ')}`);
if (args.includes('--flythrough')) for (const e of flythrough)
  console.log(`  t ${f(e.t0, 1)}–${f(e.t1, 1)} ${e.bucket.padEnd(30)} ${e.mode.padEnd(8)} nearest ${f(e.d3 * .5, 2)} m, depth gap ${f(e.dz * .5, 1)} m, ${e.near} near / ${e.dodgers} dodged${e.strike ? `, ahead ${f(e.strike.caAlong, 2)} Rg` : ''}   ${e.url}`);
}
