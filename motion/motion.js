/* Compact, reference-informed motion. Flight forces remain in murmuration.html. */
(() => {
  'use strict';
  const data = globalThis.MURMURATION_MOTION_DATA;
  if (!data || data.format !== 1) throw new Error('Bird motion data missing or incompatible');
  const clamp = (x, a, b) => Math.max(a, Math.min(b, x));
  const smooth = t => (t = clamp(t, 0, 1), t * t * (3 - 2 * t));
  for (const model of Object.values(data.species)) {
    for (const clip of Object.values(model.clips)) clip.frames = clip.frames.map(f => new Float32Array(f));
    model.indices = {};
    for (const lod of ['near', 'far']) model.indices[lod] = [...new Set(model.faces[lod].flat())].sort((a, b) => a - b);
  }

  function bracket(clip, time) {
    if (clip.frames.length === 1) return [clip.frames[0], clip.frames[0], 0];
    time = clip.loop ? ((time % 1) + 1) % 1 : clamp(time, 0, 1);
    const ts = clip.times;
    let lo = 0, hi = ts.length - 1;
    while (hi - lo > 1) { const mid = (hi + lo) >> 1; if (ts[mid] <= time) lo = mid; else hi = mid; }
    return [clip.frames[lo], clip.frames[hi], (time - ts[lo]) / (ts[hi] - ts[lo])];
  }

  function sample(species, clip, time, out, indices) {
    const model = data.species[species], [a, b, u] = bracket(model.clips[clip], time);
    out ||= new Float32Array(a.length);
    indices ||= model.indices.near;
    for (const vi of indices) {
      const v = vi * 3;
      for (let j = v; j < v + 3; j++) out[j] = a[j] + (b[j] - a[j]) * u;
    }
    return out;
  }

  const gaitTable = data.species.starling.reference.intermittentFlight.rows;
  function gaitTargets(speed) {
    let i = 0;
    while (i < gaitTable.length-2 && speed > gaitTable[i+1].speedMps) i++;
    const a = gaitTable[i], b = gaitTable[i+1], u = clamp((speed-a.speedMps)/(b.speedMps-a.speedMps), 0, 1);
    const mix = key => a[key] + (b[key]-a[key])*u;
    return { flap: mix('flapSeconds'), glide: mix('glideSeconds'), hz: mix('meanHz') };
  }
  function variation(state) {
    state.random = (Math.imul(state.random, 1664525) + 1013904223) >>> 0;
    return state.random / 4294967296;
  }
  function gait(id, phase, individual) {
    // Separate deterministic stream, never consume the flock's behavioral RNG.
    const random = Math.imul(id+1, 2654435761) >>> 0, seed = random / 4294967296;
    return { phase, variation: individual, seed, random, elapsed: seed*1.15,
      mode: 'flap', hold: 'glide', weight: 1, hz: 12, boutScale: .85+.3*seed, duration: null };
  }
  function updateGait(state, dt, speedMps, alarm) {
    const target = gaitTargets(speedMps);
    state.hz = target.hz * (.94 + .12 * state.variation) * (1 + .08 * alarm);
    if (state.duration === null) state.duration = target.flap * state.boutScale;
    state.phase = (state.phase + dt * state.hz * state.weight) % 1;
    state.elapsed += dt;
    // Alarm and low-speed continuous flapping are conservative modeling rules.
    if ((alarm > .35 || speedMps < 7.5) && state.mode !== 'flap') { state.mode = 'flap'; state.elapsed = 0; state.duration = target.flap * state.boutScale; }
    if (state.mode === 'flap' && state.elapsed > state.duration && alarm < .25 && speedMps >= 7.5) {
      // Tobalske observed increasing bounds with speed; this probability is estimated.
      const bound = variation(state) < clamp((speedMps-12.5)/18, 0, .3);
      state.mode = state.hold = bound ? 'bound' : 'glide'; state.elapsed = 0;
      state.boutScale = .85 + .3*variation(state);
      state.duration = (bound ? .23 : target.glide) * state.boutScale;
    } else if (state.mode !== 'flap' && state.elapsed > state.duration) {
      state.mode = 'flap'; state.elapsed = 0; state.boutScale = .85+.3*variation(state);
      state.duration = target.flap * state.boutScale;
    }
    state.weight += ((state.mode === 'flap' ? 1 : 0)-state.weight) * (1-Math.exp(-dt*18));
  }

  function sampleGait(state, out, indices) {
    const model = data.species.starling;
    const [a, b, u] = bracket(model.clips.flap, state.phase), hold = model.clips[state.hold].frames[0];
    indices ||= model.indices.near;
    for (const vi of indices) for (let j = vi * 3; j < vi * 3 + 3; j++) {
      const flap = a[j] + (b[j] - a[j]) * u;
      out[j] = hold[j] + (flap - hold[j]) * state.weight;
    }
    return out;
  }

  function falconState() {
    const len = data.species.falcon.clips.glide.frames[0].length;
    return { mode: 'position', pose: 'glide', elapsed: 0, phase: 0, blend: 1, flap: 0,
             from: new Float32Array(len), scratch: new Float32Array(len), cooldown: 0 };
  }

  function sampleFalcon(state, out, indices) {
    const model = data.species.falcon;
    indices ||= model.indices.near;
    if (state.pose === 'tuck') sample('falcon', 'tuck', state.elapsed / .65, out, indices);
    else if (state.pose === 'stoop') sample('falcon', 'stoop_tuck', 0, out, indices);
    else if (state.pose === 'pullout') sample('falcon', 'pullout', state.elapsed / 1.1, out, indices);
    else {
      sample('falcon', 'glide', 0, out, indices);
      const [a, b, u] = bracket(model.clips.flap, state.phase), weight = state.flap;
      for (const vi of indices) for (let j = vi * 3; j < vi * 3 + 3; j++) out[j] += (a[j] + (b[j] - a[j]) * u - out[j]) * weight;
    }
    if (state.blend < 1) {
      const u = smooth(state.blend);
      for (const vi of indices) for (let j = vi * 3; j < vi * 3 + 3; j++) out[j] = state.from[j] + (out[j] - state.from[j]) * u;
    }
    return out;
  }

  function enterFalcon(state, pose) {
    // Save the current deformed surface so interrupted dives also transition continuously.
    sampleFalcon(state, state.scratch);
    state.from.set(state.scratch);
    state.pose = pose; state.elapsed = 0; state.blend = 0;
  }

  function updateFalcon(state, dt, mode, speedMps, load) {
    if (mode !== state.mode) {
      state.mode = mode;
      enterFalcon(state, mode === 'stoop' ? 'tuck' : mode === 'climb' ? 'pullout' : 'glide');
    }
    state.elapsed += dt; state.blend = Math.min(1, state.blend + dt / .16);
    state.phase = (state.phase + dt * (mode === 'climb' ? 5.1 : 4.5)) % 1;
    const effort = mode === 'climb' ? .9 : mode === 'position' || mode === 'leave' ? clamp(.8 - (speedMps - 12) * .04 + load * .3, .15, .9) : 0;
    state.flap += (effort - state.flap) * (1 - Math.exp(-dt * 8));
    if (mode === 'stoop') {
      if (load > .8 && state.pose !== 'pullout') enterFalcon(state, 'pullout');
      else if (state.pose === 'tuck' && (state.elapsed >= .65 || speedMps > 27)) enterFalcon(state, 'stoop');
    } else if (mode === 'climb' && state.pose === 'pullout' && state.elapsed >= 1.1) enterFalcon(state, 'glide');
  }

  globalThis.MurmurationMotion = { data, sample, gaitTargets, gait, updateGait, sampleGait, falconState, updateFalcon, sampleFalcon };
})();
