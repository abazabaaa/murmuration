// Frame-exact capture of the page, pasted into the browser console (or run through Chrome automation) on
//   http://127.0.0.1:8766/murmuration.html?debug&halt&warm=T&seed=S[&calm][&variant...]
// It hides the stats panel, stops the page's own animation loop, then steps and draws one 1/60 s frame at a
// time (so ?trail ghosts are exactly what a 60 fps display shows) and posts each PNG to the local upload
// server (scratchpad upload.js on 127.0.0.1:8767), named TAG_0000.png ... Progress is in window.__cap.
window.captureClip = async (tag, frames, port = 8767) => {
  const m = window.murm, c = document.getElementById('c');
  window.__cap = { tag, done: 0, frames, t0: m.simT, error: null };
  dispatchEvent(new KeyboardEvent('keydown', { key: 'c' }));        // the panel is on by default with ?debug
  window.requestAnimationFrame = () => 0;                            // the page's loop stops after its next frame
  await new Promise(r => setTimeout(r, 200));
  let t = m.simT;
  try {
    for (let k = 0; k < frames; k++) {
      t += 1 / 60; m.step(1 / 60, t); m.draw(1 / 60);
      const blob = await new Promise(r => c.toBlob(r, 'image/png'));
      const res = await fetch(`http://127.0.0.1:${port}/save?name=${tag}_${String(k).padStart(4, '0')}.png`,
        { method: 'POST', headers: { 'Content-Type': 'image/png' }, body: blob });
      if (!res.ok) throw new Error('upload failed ' + res.status);
      window.__cap.done = k + 1;
    }
  } catch (e) { window.__cap.error = String(e); }
  window.__cap.t1 = t;
  return window.__cap;
};
