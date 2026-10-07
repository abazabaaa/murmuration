// Headless large-flock measurements for murmuration.html, against field data on wild starling flocks
// (Rome/COBBS data: Ballerini 2008 PNAS and Anim Behav; Cavagna 2010, 2013, 2022; Attanasi 2015; Young 2013).
//   node murmuration-flock.js [seconds=80] [query="seed=1&calm&n=5000"] [--warm=20] [--json]
//   node murmuration-flock.js --null=uniform|gauss [--n=5000] [--diam=25,34,42] [--draws=30]
// Notes and page references for every target: ~/prj/murmuration-refs/flock/notes_*.md.
// Undisturbed flight only (?calm). Lengths in metres (0.5 m per world unit), times in seconds.
// The edge/centre and anisotropy statistics are biased even for featureless clouds (a surface bird has neighbours on
// one side only; finite samples scatter γ), so every run also measures them on uniform ellipsoids with the flock's own
// N and diameters, and prints that null beside the value.

const fs = require('fs'), vm = require('vm'), path = require('path');
const args = process.argv.slice(2), json = args.includes('--json');
const opt = (k, d) => { const a = args.find(x => x.startsWith(`--${k}=`)); return a ? a.slice(k.length + 3) : d; };
const pos = args.filter(a => !a.startsWith('--'));
const KQ = 10;                                 // neighbours kept: γ(1..10) and the overlap Q_10 (Cavagna 2013)

// ---- small numerics
const q = (a, p) => { const b = Float64Array.from(a).sort(); return b[Math.min(b.length - 1, Math.floor(p * b.length))]; };
const mean = a => a.reduce((s, v) => s + v, 0) / a.length;
const sd = a => Math.sqrt(mean(a.map(x => (x - mean(a)) ** 2)));
function eigSym(A) {                           // Jacobi; returns [values ascending, vectors (each an array)]
  const n = A.length, a = A.map(r => r.slice()), v = A.map((_, i) => A.map((_, j) => +(i === j)));
  for (let sweep = 0; sweep < 60; sweep++) {
    let off = 0;
    for (let p = 0; p < n; p++) for (let r = p + 1; r < n; r++) off += a[p][r] * a[p][r];
    if (off < 1e-22) break;
    for (let p = 0; p < n; p++) for (let r = p + 1; r < n; r++) {
      if (Math.abs(a[p][r]) < 1e-30) continue;
      const th = (a[r][r] - a[p][p]) / (2 * a[p][r]), t = Math.sign(th || 1) / (Math.abs(th) + Math.sqrt(th * th + 1));
      const cs = 1 / Math.sqrt(t * t + 1), sn = t * cs;
      for (let k = 0; k < n; k++) { const x = a[k][p], y = a[k][r]; a[k][p] = cs * x - sn * y; a[k][r] = sn * x + cs * y; }
      for (let k = 0; k < n; k++) { const x = a[p][k], y = a[r][k]; a[p][k] = cs * x - sn * y; a[r][k] = sn * x + cs * y; }
      for (let k = 0; k < n; k++) { const x = v[k][p], y = v[k][r]; v[k][p] = cs * x - sn * y; v[k][r] = sn * x + cs * y; }
    }
  }
  const idx = [...Array(n).keys()].sort((i, j) => a[i][i] - a[j][j]);
  return [idx.map(i => a[i][i]), idx.map(i => v.map(row => row[i]))];
}
function rotationOnto(P, Q) {                  // Horn 1987: rotation R minimising sum |R q_i - p_i|^2 (both centred)
  const [PX, PY, PZ] = P, [QX, QY, QZ] = Q, S = [[0, 0, 0], [0, 0, 0], [0, 0, 0]], A = [QX, QY, QZ], B = [PX, PY, PZ];
  for (let a = 0; a < 3; a++) for (let b = 0; b < 3; b++) { let s = 0; for (let i = 0; i < A[a].length; i++) s += A[a][i] * B[b][i]; S[a][b] = s; }
  const [[xx, xy, xz], [yx, yy, yz], [zx, zy, zz]] = S;
  const M = [[xx + yy + zz, yz - zy, zx - xz, xy - yx], [yz - zy, xx - yy - zz, xy + yx, zx + xz],
             [zx - xz, xy + yx, -xx + yy - zz, yz + zy], [xy - yx, zx + xz, yz + zy, -xx - yy + zz]];
  const [, ev] = eigSym(M), [w, x, y, z] = ev[3];
  return [[w * w + x * x - y * y - z * z, 2 * (x * y - w * z), 2 * (x * z + w * y)],
          [2 * (x * y + w * z), w * w - x * x + y * y - z * z, 2 * (y * z - w * x)],
          [2 * (x * z - w * y), 2 * (y * z + w * x), w * w - x * x - y * y + z * z]];
}
let seed = 12345;                              // the nulls' own generator (the page's streams stay untouched)
const urand = () => { seed = (seed * 1664525 + 1013904223) >>> 0; return seed / 4294967296; };
const grand = () => Math.sqrt(-2 * Math.log(urand() + 1e-12)) * Math.cos(2 * Math.PI * urand());

// ---- measurements on one configuration (centred positions in metres)
function knn(X, Y, Z, k) {                     // exact k nearest by brute force, and the largest pair distance
  const N = X.length, nb = new Int32Array(N * k).fill(-1), nd = new Float64Array(N * k).fill(Infinity);
  let L2 = 0;
  const ins = (i, j, d) => {
    const o = i * k;
    if (d >= nd[o + k - 1]) return;
    let s = k - 1;
    while (s > 0 && nd[o + s - 1] > d) { nd[o + s] = nd[o + s - 1]; nb[o + s] = nb[o + s - 1]; s--; }
    nd[o + s] = d; nb[o + s] = j;
  };
  for (let i = 0; i < N; i++) for (let j = i + 1; j < N; j++) {
    const dx = X[i] - X[j], dy = Y[i] - Y[j], dz = Z[i] - Z[j], d = dx * dx + dy * dy + dz * dz;
    if (d > L2) L2 = d;
    ins(i, j, d); ins(j, i, d);
  }
  return { nb, nd, L: Math.sqrt(L2) };
}
function moments(X, Y, Z) {
  const N = X.length, P = [X, Y, Z], C = [[0, 0, 0], [0, 0, 0], [0, 0, 0]];
  for (let a = 0; a < 3; a++) for (let b = a; b < 3; b++) { let s = 0; for (let i = 0; i < N; i++) s += P[a][i] * P[b][i]; C[a][b] = C[b][a] = s / N; }
  const [lam, vec] = eigSym(C);
  const ext = vec.map(e => { let lo = Infinity, hi = -Infinity; for (let i = 0; i < N; i++) { const p = X[i] * e[0] + Y[i] * e[1] + Z[i] * e[2]; if (p < lo) lo = p; if (p > hi) hi = p; } return hi - lo; });
  return { lam, vec, ext, diam: lam.map(l => 2 * Math.sqrt(5 * l)) };   // diam: the uniform ellipsoid with these moments (Ballerini's I1-I3)
}
function structure(X, Y, Z, mo, nbr, vh) {     // edge/centre spacing and neighbour anisotropy γ(n)
  const N = X.length, rho = new Float64Array(N);
  for (let i = 0; i < N; i++) {                // depth: radius in the inertia ellipsoid (1 at the surface of a uniform one)
    let r2 = 0;
    for (let k = 0; k < 3; k++) { const p = X[i] * mo.vec[k][0] + Y[i] * mo.vec[k][1] + Z[i] * mo.vec[k][2]; r2 += p * p / (5 * mo.lam[k]); }
    rho[i] = Math.sqrt(r2);
  }
  const rOut = q(rho, .9), rIn = q(rho, .5), outer = [], inner = [];
  for (let i = 0; i < N; i++) { const r1 = Math.sqrt(nbr.nd[i * KQ]); if (rho[i] >= rOut) outer.push(r1); else if (rho[i] <= rIn) inner.push(r1); }
  // Ballerini 2008 PNAS: over interior birds, the mean projector onto the direction to the n-th neighbour; W is its
  // eigenvector with the smallest eigenvalue (the direction with fewest neighbours); γ = (W·V)², 1/3 if isotropic.
  const gam = [];
  for (let n = 0; n < KQ; n++) {
    const Mt = [[0, 0, 0], [0, 0, 0], [0, 0, 0]];
    let c = 0;
    for (let i = 0; i < N; i++) {
      if (rho[i] > rIn) continue;
      const j = nbr.nb[i * KQ + n], ux = X[j] - X[i], uy = Y[j] - Y[i], uz = Z[j] - Z[i], d = Math.hypot(ux, uy, uz), u = [ux / d, uy / d, uz / d];
      for (let a = 0; a < 3; a++) for (let b = 0; b < 3; b++) Mt[a][b] += u[a] * u[b];
      c++;
    }
    const w = eigSym(Mt.map(r => r.map(x => x / c)))[1][0];
    gam.push((w[0] * vh[0] + w[1] * vh[1] + w[2] * vh[2]) ** 2);
  }
  return { edge: q(outer, .5) / q(inner, .5), gamma: gam };
}
function largestCluster(X, Y, Z, nbr) {       // share of birds in the largest group linked through the KQ-neighbour graph
  const N = X.length, lab = new Int32Array(N).fill(-1), r = 3 * q(Array.from({ length: N }, (_, i) => Math.sqrt(nbr.nd[i * KQ])), .5);
  let best = 0;
  for (let s0 = 0; s0 < N; s0++) {
    if (lab[s0] >= 0) continue;
    const st = [s0]; lab[s0] = s0; let n = 0;
    while (st.length) {
      const i = st.pop(); n++;
      for (let k = 0; k < KQ; k++) { const j = nbr.nb[i * KQ + k]; if (j >= 0 && lab[j] < 0 && nbr.nd[i * KQ + k] < r * r) { lab[j] = s0; st.push(j); } }
    }
    best = Math.max(best, n);
  }
  return best / N;
}
function cloud(N, diam, kind) {                // N points, uniform in (or Gaussian with the moments of) an ellipsoid
  const a = diam.map(d => d / 2), X = new Float64Array(N), Y = new Float64Array(N), Z = new Float64Array(N);
  for (let i = 0; i < N; i++) {
    let x, y, z;
    if (kind === 'gauss') { x = grand() / Math.sqrt(5); y = grand() / Math.sqrt(5); z = grand() / Math.sqrt(5); }
    else do { x = 2 * urand() - 1; y = 2 * urand() - 1; z = 2 * urand() - 1; } while (x * x + y * y + z * z > 1);
    X[i] = x * a[2]; Y[i] = y * a[0]; Z[i] = z * a[1];   // thin axis vertical (Y), as in flocks
  }
  return [X, Y, Z];
}
function nullStats(N, diam, kind, draws) {     // the edge ratio and γ(n) of featureless clouds, mean and SD over draws
  const E = [], G = [];
  for (let d = 0; d < draws; d++) {
    const [X, Y, Z] = cloud(N, diam, kind), mo = moments(X, Y, Z), nbr = knn(X, Y, Z, KQ);
    const ph = 2 * Math.PI * urand();          // level flight in a random horizontal direction
    const s = structure(X, Y, Z, mo, nbr, [Math.cos(ph), 0, Math.sin(ph)]);
    E.push(s.edge); G.push(s.gamma);
  }
  return { edge: [mean(E), sd(E)], gamma: [...Array(KQ).keys()].map(n => [mean(G.map(g => g[n])), sd(G.map(g => g[n]))]), draws };
}

if (opt('null')) {                             // calibration only: no page
  const N = +opt('n', 5000), diam = opt('diam', '25.4,34.3,42.2').split(',').map(Number), draws = +opt('draws', 30);
  const r = nullStats(N, diam, opt('null'), draws);
  if (json) { console.log(JSON.stringify(r)); process.exit(0); }
  console.log(`${opt('null')} cloud, N ${N}, diameters ${diam.join(' / ')} m, ${draws} draws`);
  console.log(`edge / centre nearest-neighbour distance  ${r.edge[0].toFixed(3)} ± ${r.edge[1].toFixed(3)} (SD of one draw)`);
  console.log(`γ(n), n = 1…10, mean ± SD of one draw     ${r.gamma.map(([m, s]) => `${m.toFixed(2)}±${s.toFixed(2)}`).join(' ')}`);
  process.exit(0);
}

// ---- the page, headless
const secs = +(pos[0] || 80), query = pos[1] || 'seed=1&calm&n=5000', WARM = +opt('warm', 20);
let src = fs.readFileSync(path.join(__dirname, 'murmuration.html'), 'utf8');
src = src.slice(src.indexOf('<script>') + 8, src.lastIndexOf('</script>'));
const noop = () => {};
const canvasProxy = () => new Proxy({}, { get: (t, p) => (p in t ? t[p] : (p === 'data' ? [] : (...a) => canvasProxy())), set: (t, p, v) => (t[p] = v, true) });
const el = () => ({ textContent: '', classList: { add: noop, toggle: noop, remove: noop, contains: () => false }, getContext: () => canvasProxy(), width: 0, height: 0, style: {}, appendChild: noop });
const win = {
  document: { getElementById: el, createElement: el, body: { appendChild: noop }, addEventListener: noop }, innerWidth: 1440, innerHeight: 900,
  devicePixelRatio: 1, location: { search: '?' + query + '&debug' }, URLSearchParams, performance, Math, console,
  requestAnimationFrame: noop, addEventListener: noop, setTimeout: noop, clearTimeout: noop,
  Float32Array, Float64Array, Int32Array, Int8Array, Uint32Array, Uint8Array, Array, Path2D: class { moveTo() {} lineTo() {} closePath() {} },
};
win.window = win;
vm.createContext(win);
vm.runInContext(src, win);
const m = win.murm, N = m.N, U = 0.5;          // metres per world unit
const DT = 1 / 60, REC = 6, LAGS = 35;         // positions every 0.1 s, as the field data; lags up to 3.5 s
const QP = new URLSearchParams(query), GEOMQ = +QP.get('geom') || 0;   // the rejoin radius the page uses (murmuration.html)
const RJQ = (QP.has('rj') ? +QP.get('rj') : QP.has('local') ? 100 : GEOMQ >= 2 ? 2 : 1) * 20 * Math.cbrt(N / 400) * U;

const snaps = [], origins = [];
const msd = new Float64Array(LAGS + 1), msdRot = new Float64Array(LAGS + 1), msdNN = new Float64Array(LAGS + 1), msdN = new Float64Array(LAGS + 1);
const q10 = { 10: [], 35: [] };
let step = 0, kFrame = -1;
const t0 = performance.now();
for (let t = DT; t <= secs + 1e-9; t += DT) {
  m.step(DT, t); step++;
  if (t < WARM - 1e-9 || step % REC) continue;
  kFrame++;
  const X = Float64Array.from(m.px), Y = Float64Array.from(m.py), Z = Float64Array.from(m.pz);
  let cx = 0, cy = 0, cz = 0;
  for (let i = 0; i < N; i++) { cx += X[i]; cy += Y[i]; cz += Z[i]; }
  cx /= N; cy /= N; cz /= N;
  for (let i = 0; i < N; i++) { X[i] = (X[i] - cx) * U; Y[i] = (Y[i] - cy) * U; Z[i] = (Z[i] - cz) * U; }
  for (const o of origins) {                   // displacement since each origin
    const lag = kFrame - o.k;
    if (lag < 1 || lag > LAGS) continue;
    // Cavagna 2013 Eq 2.3: displacement in the centre-of-mass frame (translation removed, not rotation). Also kept,
    // as a diagnostic, the same with the flock's rigid rotation since the origin removed (Horn).
    const R = rotationOnto([o.X, o.Y, o.Z], [X, Y, Z]);
    let s = 0, sr = 0, sn = 0;
    for (let i = 0; i < N; i++) {
      s += (X[i] - o.X[i]) ** 2 + (Y[i] - o.Y[i]) ** 2 + (Z[i] - o.Z[i]) ** 2;
      const rx = R[0][0] * X[i] + R[0][1] * Y[i] + R[0][2] * Z[i], ry = R[1][0] * X[i] + R[1][1] * Y[i] + R[1][2] * Z[i], rz = R[2][0] * X[i] + R[2][1] * Y[i] + R[2][2] * Z[i];
      sr += (rx - o.X[i]) ** 2 + (ry - o.Y[i]) ** 2 + (rz - o.Z[i]) ** 2;
      const j = o.nn1[i];                      // Eq 2.5: change in the distance to the nearest neighbour at the origin
      sn += (Math.hypot(X[i] - X[j], Y[i] - Y[j], Z[i] - Z[j]) - Math.hypot(o.X[i] - o.X[j], o.Y[i] - o.Y[j], o.Z[i] - o.Z[j])) ** 2;
    }
    msd[lag] += s / N; msdRot[lag] += sr / N; msdNN[lag] += sn / N; msdN[lag]++;
    if (lag === 10 || lag === 35) {
      const now = knn(X, Y, Z, KQ).nb;
      let keep = 0;
      for (let i = 0; i < N; i++) {
        const a = new Set(Array.from(o.nb.subarray(i * KQ, i * KQ + KQ)));
        for (let s2 = 0; s2 < KQ; s2++) if (a.has(now[i * KQ + s2])) keep++;
      }
      q10[lag].push(keep / (N * KQ));
    }
  }
  while (origins.length && kFrame - origins[0].k > LAGS) origins.shift();
  if (kFrame % 10) continue;                   // once a second: everything else; a new displacement origin every 5 s
  let Vx = 0, Vy = 0, Vz = 0, Px = 0, Py = 0, Pz = 0;
  const sp = new Float64Array(N);
  for (let i = 0; i < N; i++) {
    Vx += m.vx[i]; Vy += m.vy[i]; Vz += m.vz[i];
    sp[i] = Math.hypot(m.vx[i], m.vy[i], m.vz[i]); Px += m.vx[i] / sp[i]; Py += m.vy[i] / sp[i]; Pz += m.vz[i] / sp[i];
  }
  const S = mean(Array.from(sp)), V = Math.hypot(Vx, Vy, Vz) / N, vh = [Vx / N / V, Vy / N / V, Vz / N / V];
  const mo = moments(X, Y, Z), nbr = knn(X, Y, Z, KQ), st = structure(X, Y, Z, mo, nbr, vh);
  const nn = Array.from({ length: N }, (_, i) => Math.sqrt(nbr.nd[i * KQ]));
  const { lam, vec } = mo;
  snaps.push({
    t: +(WARM + kFrame / 10).toFixed(1), phi: Math.hypot(Px, Py, Pz) / N, V: V * U, S: S * U,
    spread: [q(sp, .05) / S, q(sp, .5) / S, q(sp, .95) / S], cvS: Math.sqrt(mean(Array.from(sp, s => (s - S) ** 2))) / S,
    L: nbr.L, ext: mo.ext, diam: mo.diam, thick: Math.sqrt(lam[0] / lam[2]),
    thinUp: Math.abs(vec[0][1]), longAlongV: Math.abs(vec[2][0] * vh[0] + vec[2][1] * vh[1] + vec[2][2] * vh[2]), climb: vh[1],
    nn: q(nn, .5), nnP: [q(nn, .1), q(nn, .9)], edge: st.edge, gamma: st.gamma, big: largestCluster(X, Y, Z, nbr),
    held: m.stats.out / N,
    beyond: (() => { let c = 0; for (let i = 0; i < N; i++) if (X[i] * X[i] + Y[i] * Y[i] + Z[i] * Z[i] > RJQ * RJQ) c++; return c / N; })(),
  });
  if (kFrame % 50 === 0) {
    const nn1 = new Int32Array(N); for (let i = 0; i < N; i++) nn1[i] = nbr.nb[i * KQ];
    origins.push({ k: kFrame, X, Y, Z, nn1, nb: nbr.nb });
  }
}
const wall = (performance.now() - t0) / 1000;

// ---- report
const fit = arr => {                           // log-log slope of an MSD over 0.4-1.5 s (Cavagna 2013)
  const xs = [], ys = [];
  for (let l = 4; l <= 15; l++) if (msdN[l]) { xs.push(Math.log(l / 10)); ys.push(Math.log(arr[l] / msdN[l])); }
  const mx = mean(xs), my = mean(ys);
  return xs.reduce((s, x, i) => s + (x - mx) * (ys[i] - my), 0) / xs.reduce((s, x) => s + (x - mx) ** 2, 0);
};
const col = k => snaps.map(s => s[k]), avg3 = k => [0, 1, 2].map(j => mean(snaps.map(s => s[k][j])));
const res = {
  run: { query, N, secs, warm: WARM, samples: snaps.length, wall_s: +wall.toFixed(0) },
  phi: mean(col('phi')), V: mean(col('V')), cvS: mean(col('cvS')), spread: avg3('spread'),
  L: mean(col('L')), ext: avg3('ext'), diam: avg3('diam'), thick: [q(col('thick'), .1), q(col('thick'), .5), q(col('thick'), .9)],
  ar2: q(snaps.map(s => s.diam[1] / s.diam[0]), .5), ar3: q(snaps.map(s => s.diam[2] / s.diam[0]), .5),
  thickNN: q(snaps.map(s => s.diam[0] / s.nn), .5), vg: q(snaps.map(s => Math.abs(s.climb)), .5),
  thinUp: q(col('thinUp'), .5), longAlongV: q(col('longAlongV'), .5),
  nn: mean(col('nn')), nnP: [mean(snaps.map(s => s.nnP[0])), mean(snaps.map(s => s.nnP[1]))],
  edge: [mean(col('edge')), sd(col('edge'))],
  gamma: [...Array(KQ).keys()].map(n => [mean(snaps.map(s => s.gamma[n])), sd(snaps.map(s => s.gamma[n])) / Math.sqrt(snaps.length)]),
  msd1: msdN[10] ? msd[10] / msdN[10] : null, msdRot1: msdN[10] ? msdRot[10] / msdN[10] : null, msdNN1: msdN[10] ? msdNN[10] / msdN[10] : null,
  alpha: fit(msd), alphaNN: fit(msdNN), q10_1: q10[10].length ? mean(q10[10]) : null, q10_35: q10[35].length ? mean(q10[35]) : null,
};
res.big = q(col('big'), .1);                  // the worst decile of the largest group's share
res.fragmented = res.phi < .8 || res.big < .9;
res.null = nullStats(N, res.diam, 'uniform', 10);   // the same statistics on uniform ellipsoids of this N and shape
if (json) { console.log(JSON.stringify({ ...res, snaps })); process.exit(0); }
const f = (x, d = 2) => x == null || Number.isNaN(x) ? '—' : (+x).toFixed(d);
const g = res.gamma.slice(0, 6), gn = res.null.gamma.slice(0, 6);
const rows = [
  ['polarization Φ', f(res.phi, 3), '0.96 ± 0.03 (0.84–0.995); 0.975 ± 0.023, 45 flocks (Cavagna 2010 p11866; 2022 SI)'],
  ['group speed, m/s', f(res.V, 1), '10.6 (6.9–15.2) (Ballerini 2008 AB T1); 11.6 ± 2.5 (Cavagna 2010 SI)'],
  ['bird speed / mean, P5–P50–P95', res.spread.map(x => f(x)).join('–'), 'mostly 0.6–1.4 (Cavagna 2022 Fig 4, read from figure)'],
  ['bird speed spread, SD / mean', f(res.cvS), '≈0.13–0.2 if Gaussian (derived from Cavagna 2022 Fig 4)'],
  ['extent L (largest distance), m', f(res.L, 1), '9–86 m for N 122–4268 (Cavagna 2010 SI); depends on density, which varies 20x'],
  ['ellipsoid diameters I1 / I2 / I3, m', res.diam.map(x => f(x, 1)).join(' / '), 'thickness 5.3–19 m (N 448–2631); ≈10–25 by 50–120 m projected to 5,000 (Ballerini 2008 AB T1)'],
  ['aspect ratios I2/I1, I3/I1', `${f(res.ar2, 1)}, ${f(res.ar3, 1)}`, '2.8 ± 0.4, 5.6 ± 1.0, flat in N (AB p9)'],
  ['thickness / longest (second moments)', `${f(res.thick[1])} (10–90 %: ${f(res.thick[0])}–${f(res.thick[2])})`, '0.18 from 1:2.8:5.6; 0.13–0.44, mostly 0.13–0.27 (Young 2013 p4)'],
  ['thickness in neighbour spacings I1/r1', f(res.thickNN, 1), '5.7–13 (N 448–2631), ∝ N^⅓; ≈14–17 projected to 5,000 (AB T1)'],
  ['thin axis along gravity |I1·G|', f(res.thinUp), '0.93 ± 0.04 (AB T1)'],
  ['flight vs gravity |V·G|', f(res.vg), '0.13 ± 0.05 (AB T1)'],
  ['long axis along heading |I3·V|', f(res.longAlongV), 'uncorrelated (AB p9-10); 0.32 before turns, 0.90 after (Attanasi 2015 SI)'],
  ['nearest-neighbour distance r1, m', `${f(res.nn)} (10–90 %: ${f(res.nnP[0])}–${f(res.nnP[1])})`, '0.68–1.51, mean 1.05, independent of N (AB T1)'],
  ['edge / centre r1 (this flock | uniform null)', `${f(res.edge[0])} ± ${f(res.edge[1])} | ${f(res.null.edge[0])}`, '0.65–0.82: the edge is denser (AB Fig 6a); outer 10 % vs inner 50 % by ellipsoid depth'],
  ['anisotropy γ(n), n = 1…6 (± SE)', g.map(([v, e]) => `${f(v)}±${f(e)}`).join(' '), 'γ(1) ≈ 0.85, falling to 1/3 by n ≈ 4–7 (Ballerini 2008 PNAS Fig 3a)'],
  ['  same, uniform null (± SD of one draw)', gn.map(([v, e]) => `${f(v)}±${f(e)}`).join(' '), '1/3 if isotropic'],
  ['MSD at 1 s, centre-of-mass frame, m²', f(res.msd1), '≈1.9 (Cavagna 2013 Eq 2.3-2.4, Table 1, derived); N 239-1,246, no N trend'],
  ['  same, flock rotation also removed', f(res.msdRot1), 'diagnostic only (not a field measure)'],
  ['MSD exponent 0.4–1.5 s, CM frame', f(res.alpha), '1.73 ± 0.07 (Cavagna 2013 Table 1)'],
  ['mutual MSD at 1 s (neighbour distance), m²', f(res.msdNN1), '≈0.42 (Cavagna 2013 Eq 2.5, 2.7, derived)'],
  ['mutual MSD exponent', f(res.alphaNN), '1.58 ± 0.2 (Cavagna 2013 Eq 2.7)'],
  ['neighbours kept, Q10 after 1 s', f(res.q10_1), '≈0.77 (Cavagna 2013 Fig 3, read from figure)'],
  ['neighbours kept, Q10 after 3.5 s', f(res.q10_35), '≈0.5 (Cavagna 2013 Fig 3, read from figure)'],
];
console.log(`${query}: N ${N}, ${secs} s (measured after ${WARM} s, ${snaps.length} samples), ${res.run.wall_s} s wall`);
console.log(`${'birds outside the backstop box'.padEnd(44)} ${(f(100 * mean(col('held')), 1) + ' %').padEnd(44)} a box 1.25x the view; pushed back unless backstop=0`);
console.log(`${'birds beyond the rejoin radius'.padEnd(44)} ${(f(100 * mean(col('beyond')), 1) + ` % (radius ${f(RJQ, 0)} m)`).padEnd(44)} rejoin is for stragglers; a steady share is an artefact`);
console.log(`${'largest group (worst 10 % of samples)'.padEnd(44)} ${(f(100 * res.big, 0) + ' % of birds').padEnd(44)} ${res.fragmented ? 'FRAGMENTED: shape, edge and anisotropy rows are not reported' : 'one flock'}`);
const SHAPE = /diameters|aspect|thickness|thin axis|long axis|edge|anisotropy|uniform null|extent/;
for (const [a, b, c] of rows) if (!res.fragmented || !SHAPE.test(a)) console.log(`${a.padEnd(44)} ${String(b).padEnd(44)} ${c}`);
