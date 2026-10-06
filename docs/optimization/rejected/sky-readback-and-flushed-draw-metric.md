# Not an optimization: the "fixed ~7 ms flush cost" and the getImageData timing method

Measured in Chrome 154 (macOS, 1728x820/876 CSS, DPR 2, canvas 3456x1640/1752), N=20, medians of 12-40
repetitions of `fn(); ctx.getImageData(0,0,1,1)`:

| operation | ms |
| --- | --- |
| `drawImage(sky, 0, 0, W, H)` at alpha .5 | 6.9-7.8 |
| same into a quarter of the screen | 7.2-8.8 |
| same into a sixteenth | 5.0 |
| `drawImage` of a same-size pixel copy of sky | 2.6 |
| full-screen `fillRect` at alpha .5 | 0.4 |
| full 24 MB `getImageData` of the main canvas | 4.8 |
| `drawImage(sky)` after one `sctx.getImageData(0,0,1,1)` on the sky canvas | 2.4-2.6 |

The same numbers were obtained with the tab hidden and visible. The cost does not scale with the
destination size and a single readback of the *source* canvas removes it, which is the signature of a
canvas being demoted to software by the readbacks used to time it: the per-frame `getImageData` on the
main canvas puts it on the CPU, after which every `drawImage` of the GPU-backed sky pays a 24 MB
GPU->CPU copy. The real page never reads the main canvas back.

What the real pipeline does (visible tab, 120 Hz display, page's own rAF loop): with up to 8 ms of
extra busy-wait per frame added to the N=20 page and to the N=400 candidate the rAF interval stayed
8.3 ms, i.e. raster and compositing run off the main thread in parallel with the next frame's JS. The
frame rate is set by main-thread JS (step + draw JS); raster only matters once it exceeds a refresh
period. Forcing the sky readback in the app is therefore not an optimization (it would make the sky
CPU-backed for the GPU path) and was not committed. Timing numbers of the form "draw + getImageData"
measure a software path the user never sees; use step/draw JS medians and rAF intervals instead.

Real rAF intervals measured (visible, same scene seed=1 calm painted warm=20):

| page | N400 | N1000 | N2000 |
| --- | --- | --- | --- |
| frozen baseline d24849df | 16.4 ms | 42.5 ms | renderer unresponsive for >45 s |
| candidate 63f1b81 (start of this session) | 8.3 ms (cap) | 8.3 ms (cap) | 16.6 ms |
| candidate ca63e8f (end of this session) | 8.3 ms (cap) | 8.3 ms (cap) | 8.4 ms median, 16.8 ms p95 |
