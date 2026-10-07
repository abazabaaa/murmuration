// Headless check for murmuration.html: runs the page script under node with DOM stubs, then
// measures the Cavagna et al. (2010) observables with an independent implementation and
// cross-checks the in-page analysis against it.
//   node murmuration-check.js murmuration.html [seconds=40] [query="seed=1&n=400"]   (the page itself defaults to 5,000 birds)
//   SERIES=1 ...              per-second time series (Φ, L, nn, |u|, clusters, out-of-frame)
//   DETAIL=30,40 ...          per-cluster breakdown at those simulated seconds
// Query is the page URL query, e.g. "seed=2&n=1000&calm&noise=1.5".

const fs = require('fs'), vm = require('vm');
const file = process.argv[2], secs = +(process.argv[3] || 40), query = process.argv[4] || 'seed=1&n=400';

let src = fs.readFileSync(file, 'utf8');
src = src.slice(src.indexOf('<script>') + 8, src.lastIndexOf('</script>'));
if (!/window\.murm\s*=/.test(src)) {          // legacy file: expose internals by patching
  src = src.replace(/\}\)\(\);\s*$/, 'window.murm = { step, stats, px, py, pz, vx, vy, vz, N, get simT() { return simT; } };\n})();');
}

const noop = () => {};
const canvasProxy = () => new Proxy({}, { get: (t, p) => (p in t ? t[p] : (p === 'data' ? [] : (...a) => canvasProxy())), set: (t, p, v) => (t[p] = v, true) });
const el = () => ({ textContent: '', classList: { add: noop, toggle: noop, remove: noop, contains: () => false }, getContext: () => canvasProxy(), width: 0, height: 0, style: {}, appendChild: noop });
const doc = { getElementById: el, createElement: el, body: { appendChild: noop }, addEventListener: noop };
const win = {
  document: doc, innerWidth: 1440, innerHeight: 900, devicePixelRatio: 1,
  location: { search: '?' + query + '&debug' }, URLSearchParams, performance, Math, console,
  requestAnimationFrame: noop, addEventListener: noop, setTimeout: noop, clearTimeout: noop,
  Float32Array, Float64Array, Int32Array, Uint32Array, Uint8Array, Array, Path2D: class { moveTo() {} lineTo() {} closePath() {} },
};
win.window = win;
vm.createContext(win);
vm.runInContext(src, win, { filename: file });
const m = win.murm;
if (!m) throw new Error('window.murm not exposed');

// -------- reference implementation of the paper's observables (all in world units)
function analyse() {
  const N = m.N, px = m.px, py = m.py, pz = m.pz, vx = m.vx, vy = m.vy, vz = m.vz;
  let Vx = 0, Vy = 0, Vz = 0, S = 0, Px = 0, Py = 0, Pz = 0;
  for (let i = 0; i < N; i++) {
    Vx += vx[i]; Vy += vy[i]; Vz += vz[i];
    const s = Math.hypot(vx[i], vy[i], vz[i]); S += s; Px += vx[i] / s; Py += vy[i] / s; Pz += vz[i] / s;
  }
  Vx /= N; Vy /= N; Vz /= N; S /= N;
  const phi = Math.hypot(Px, Py, Pz) / N;             // Eq 1
  const ux = new Float64Array(N), uy = new Float64Array(N), uz = new Float64Array(N), sp = new Float64Array(N);
  let c0 = 0, c0s = 0, sumU = [0, 0, 0], sumS = 0;
  for (let i = 0; i < N; i++) {
    ux[i] = vx[i] - Vx; uy[i] = vy[i] - Vy; uz[i] = vz[i] - Vz;   // Eq 2
    sp[i] = Math.hypot(vx[i], vy[i], vz[i]) - S;                   // Eq 16
    c0 += ux[i] * ux[i] + uy[i] * uy[i] + uz[i] * uz[i]; c0s += sp[i] * sp[i];
    sumU[0] += ux[i]; sumU[1] += uy[i]; sumU[2] += uz[i]; sumS += sp[i];
  }
  c0 /= N; c0s /= N;                                             // C(0) = 1 normalisation
  // pairwise
  let L = 0;
  const r = [];
  for (let i = 0; i < N; i++) for (let j = i + 1; j < N; j++) {
    const d = Math.hypot(px[i] - px[j], py[i] - py[j], pz[i] - pz[j]);
    if (d > L) L = d;
  }
  const NB = 40, dr = L / NB, num = new Float64Array(NB), nums = new Float64Array(NB), cnt = new Float64Array(NB);
  for (let i = 0; i < N; i++) for (let j = i + 1; j < N; j++) {
    const d = Math.hypot(px[i] - px[j], py[i] - py[j], pz[i] - pz[j]);
    let b = Math.min(NB - 1, (d / dr) | 0);
    num[b] += ux[i] * ux[j] + uy[i] * uy[j] + uz[i] * uz[j]; nums[b] += sp[i] * sp[j]; cnt[b]++;
  }
  const C = [], Cs = [];
  for (let b = 0; b < NB; b++) { C.push(cnt[b] ? num[b] / cnt[b] / c0 : NaN); Cs.push(cnt[b] ? nums[b] / cnt[b] / c0s : NaN); }
  const xi = zero(C, dr), xis = zero(Cs, dr);
  const sumNum = num.reduce((a, b) => a + b, 0), sumNums = nums.reduce((a, b) => a + b, 0);
  return { N, phi, S, sigS: Math.sqrt(c0s), rmsU: Math.sqrt(c0), L, xi, xis, C, Cs, dr,
    sumU: Math.hypot(...sumU), sumS, eq14: sumNum / (-N * c0 / 2), eq14s: sumNums / (-N * c0s / 2) };
}
function zero(C, dr) {                        // first sign change of the binned C(r)  (Eq 5)
  for (let b = 1; b < C.length; b++) {
    if (Number.isNaN(C[b]) || Number.isNaN(C[b - 1])) continue;
    if (C[b - 1] > 0 && C[b] <= 0) { const f = C[b - 1] / (C[b - 1] - C[b]); return (b - 1 + f + .5) * dr; }
  }
  return NaN;
}

// connected components with link distance `link` (world units): counts sub-flocks
function clusters(link) {
  const N = m.N, px = m.px, py = m.py, pz = m.pz, lab = new Int32Array(N).fill(-1);
  let nc = 0, l2 = link * link, biggest = 0;
  for (let s = 0; s < N; s++) {
    if (lab[s] >= 0) continue;
    const stack = [s]; lab[s] = nc; let size = 0;
    while (stack.length) {
      const i = stack.pop(); size++;
      for (let j = 0; j < N; j++) if (lab[j] < 0 && (px[i] - px[j]) ** 2 + (py[i] - py[j]) ** 2 + (pz[i] - pz[j]) ** 2 < l2) { lab[j] = nc; stack.push(j); }
    }
    biggest = Math.max(biggest, size); nc++;
  }
  return { nc, biggest };
}

// gyration tensor semi-axes (sqrt of eigenvalues), largest first: flock shape
function shape() {
  const N = m.N, px = m.px, py = m.py, pz = m.pz;
  let cx = 0, cy = 0, cz = 0;
  for (let i = 0; i < N; i++) { cx += px[i]; cy += py[i]; cz += pz[i]; }
  cx /= N; cy /= N; cz /= N;
  const T = [[0, 0, 0], [0, 0, 0], [0, 0, 0]];
  for (let i = 0; i < N; i++) {
    const d = [px[i] - cx, py[i] - cy, pz[i] - cz];
    for (let a = 0; a < 3; a++) for (let b = 0; b < 3; b++) T[a][b] += d[a] * d[b] / N;
  }
  // Jacobi eigenvalues for a 3x3 symmetric matrix
  const A = T.map(r => r.slice());
  for (let sweep = 0; sweep < 50; sweep++) {
    let off = 0; for (let p = 0; p < 3; p++) for (let q = p + 1; q < 3; q++) off += A[p][q] ** 2;
    if (off < 1e-12) break;
    for (let p = 0; p < 3; p++) for (let q = p + 1; q < 3; q++) {
      if (Math.abs(A[p][q]) < 1e-15) continue;
      const th = .5 * Math.atan2(2 * A[p][q], A[q][q] - A[p][p]), c = Math.cos(th), s = Math.sin(th);
      for (let k = 0; k < 3; k++) { const akp = A[k][p], akq = A[k][q]; A[k][p] = c * akp - s * akq; A[k][q] = s * akp + c * akq; }
      for (let k = 0; k < 3; k++) { const apk = A[p][k], aqk = A[q][k]; A[p][k] = c * apk - s * aqk; A[q][k] = s * apk + c * aqk; }
    }
  }
  return [A[0][0], A[1][1], A[2][2]].map(v => Math.sqrt(Math.max(0, v))).sort((a, b) => b - a);
}

// per-cluster detail: size, offset of the cluster centroid from the flock centroid, heading angle
// relative to the flock's mean velocity, mean speed
function clusterDetail(link) {
  const N = m.N, px = m.px, py = m.py, pz = m.pz, vx = m.vx, vy = m.vy, vz = m.vz, lab = new Int32Array(N).fill(-1);
  let nc = 0, l2 = link * link;
  for (let s = 0; s < N; s++) {
    if (lab[s] >= 0) continue;
    const stack = [s]; lab[s] = nc;
    while (stack.length) {
      const i = stack.pop();
      for (let j = 0; j < N; j++) if (lab[j] < 0 && (px[i] - px[j]) ** 2 + (py[i] - py[j]) ** 2 + (pz[i] - pz[j]) ** 2 < l2) { lab[j] = nc; stack.push(j); }
    }
    nc++;
  }
  let gx = 0, gy = 0, gz = 0, Vx = 0, Vy = 0, Vz = 0;
  for (let i = 0; i < N; i++) { gx += px[i]; gy += py[i]; gz += pz[i]; Vx += vx[i]; Vy += vy[i]; Vz += vz[i]; }
  gx /= N; gy /= N; gz /= N; const Vn = Math.hypot(Vx, Vy, Vz); Vx /= Vn; Vy /= Vn; Vz /= Vn;
  const out = [];
  for (let c = 0; c < nc; c++) {
    let n = 0, cx = 0, cy = 0, cz = 0, ux = 0, uy = 0, uz = 0, sp = 0;
    for (let i = 0; i < N; i++) if (lab[i] === c) { n++; cx += px[i]; cy += py[i]; cz += pz[i]; ux += vx[i]; uy += vy[i]; uz += vz[i]; sp += Math.hypot(vx[i], vy[i], vz[i]); }
    cx = cx / n - gx; cy = cy / n - gy; cz = cz / n - gz;
    const un = Math.hypot(ux, uy, uz), cos = (ux * Vx + uy * Vy + uz * Vz) / un;
    const along = cx * Vx + cy * Vy + cz * Vz, perp = Math.sqrt(Math.max(0, cx * cx + cy * cy + cz * cz - along * along));
    out.push({ n, along: +along.toFixed(0), perp: +perp.toFixed(0), headingDeg: +(Math.acos(Math.max(-1, Math.min(1, cos))) * 180 / Math.PI).toFixed(0), speed: +(sp / n).toFixed(1), pol: +(un / n / (sp / n)).toFixed(2) });
  }
  return out.sort((a, b) => b.n - a.n);
}

// -------- run
const dt = 1 / 60;
const shapes = [];
const detailAt = (process.env.DETAIL || '').split(',').filter(Boolean).map(Number);
const series = process.env.SERIES;
let t0 = Date.now(), samples = [], maxDiff = 0, maxXiDiff = 0, simT = 0;
for (let s = 0; s < secs * 60; s++) {
  simT += dt; m.step(dt, simT);
  if (detailAt.length && s % 60 === 0 && detailAt.includes(Math.round(simT))) {
    console.log(`t=${Math.round(simT)} falcon=${m.fal.on} clusters: ` + clusterDetail(12).map(c => `[n${c.n} along${c.along} perp${c.perp} hdg${c.headingDeg}° v${c.speed} pol${c.pol}]`).join(' '));
  }
  if (s % 30 === 0 && s >= 10 * 60) {
    const a = analyse(); samples.push(a);
    const sh = shape(); shapes.push(sh);
    if (series) {
      const c = clusters(12);
      process.stdout.write(`axes ${sh.map(v => v.toFixed(0)).join('/')} `);
      let ou = 0, ov = 0, oz = 0;
      if (m.cam) {
        const K = m.cam;
        for (let i = 0; i < m.N; i++) {
          const yr = m.py[i] - K.CAM_H, zc = yr * K.st + m.pz[i] * K.ct, yc = yr * K.ct - m.pz[i] * K.st, u = m.px[i] / zc, v = yc / zc;
          if (u > K.UM || u < -K.UM) ou++; if (v > K.VT || v < K.VB) ov++; if (zc > K.ZMAX || zc < K.ZMIN) oz++;
        }
      }
      console.log(`t=${simT.toFixed(0).padStart(3)} phi=${a.phi.toFixed(3)} L=${a.L.toFixed(0).padStart(4)} nn=${m.stats.nn.toFixed(1)} |u|=${a.rmsU.toFixed(1)} clusters=${c.nc} biggest=${c.biggest} out=${m.stats.out} (u ${ou} v ${ov} z ${oz})${m.fal && m.fal.on ? ' FALCON' : ''}`);
    }
    if (m.analyse) {                          // cross-check the in-page implementation against this one
      m.analyse(simT);
      if (m.draw) m.draw();                    // exercise the drawing + panel code against the canvas stub
      const c = m.corr;
      // same bins only if NBIN matches; compare scalar observables instead
      maxDiff = Math.max(maxDiff, Math.abs(c.phi - a.phi), Math.abs(c.L - a.L) / a.L, Math.abs(c.speed - a.S) / a.S, Math.abs(c.rmsU - a.rmsU) / a.rmsU, Math.abs(c.sigSpeed - a.sigS) / a.sigS);
      if (Number.isFinite(c.xi) && Number.isFinite(a.xi)) maxXiDiff = Math.max(maxXiDiff, Math.abs(c.xi - a.xi) / a.L);
      // Eq 14 on the in-page bins: Σ_b cnt_b C_b c0 = -N c0 / 2  =>  Σ_b cnt_b C_b = -N/2
      // (bins below the page's MIN_PAIRS threshold are NaN there; recompute those from the raw sums is not
      // possible from outside, so only check when every bin is populated)
      let s14 = 0, ok = true; for (let b = 0; b < c.C.length; b++) { if (Number.isNaN(c.C[b])) { ok = false; break; } s14 += c.cnt[b] * c.C[b]; }
      a.eq14page = ok ? s14 / (-m.N / 2) : NaN;
    }
  }
}
const wall = (Date.now() - t0) / secs;
const mean = k => samples.reduce((a, s) => a + (Number.isFinite(s[k]) ? s[k] : 0), 0) / samples.filter(s => Number.isFinite(s[k])).length;
const last = samples[samples.length - 1];
console.log(`file=${file}  N=${m.N}  sim ${secs}s  wall ${wall.toFixed(0)} ms/sim-s  samples=${samples.length}`);
console.log(`mean:  phi=${mean('phi').toFixed(3)}  speed=${mean('S').toFixed(2)} ±${mean('sigS').toFixed(2)}  |u|rms=${mean('rmsU').toFixed(2)}  L=${mean('L').toFixed(1)}  xi=${mean('xi').toFixed(1)}  xi_sp=${mean('xis').toFixed(1)}  xi/L=${(samples.map(s => s.xi / s.L).filter(Number.isFinite).reduce((a, b) => a + b, 0) / samples.filter(s => Number.isFinite(s.xi)).length).toFixed(3)}  xi_sp/L=${(samples.map(s => s.xis / s.L).filter(Number.isFinite).reduce((a, b) => a + b, 0) / samples.filter(s => Number.isFinite(s.xis)).length).toFixed(3)}  nn=${m.stats.nn.toFixed(2)}`);
console.log(`shape: mean gyration semi-axes ${[0, 1, 2].map(k => (shapes.reduce((s, v) => s + v[k], 0) / shapes.length).toFixed(1)).join(' / ')} u`);
console.log(`checks: |sum u| = ${last.sumU.toExponential(2)}  sum phi = ${last.sumS.toExponential(2)}  Eq14 ratio (should be 1) = ${last.eq14.toFixed(4)} / ${last.eq14s.toFixed(4)}`);
console.log('last C(r):   ' + last.C.map(v => v.toFixed(2)).join(' '));
console.log('last Csp(r): ' + last.Cs.map(v => v.toFixed(2)).join(' '));
if (m.analyse) console.log(`in-page vs reference: max rel diff of scalars ${maxDiff.toExponential(2)}, max |Δξ|/L ${maxXiDiff.toFixed(4)} (bin widths differ: 32 vs 40 bins), Eq14 on page bins = ${last.eq14page.toFixed(4)}`);
