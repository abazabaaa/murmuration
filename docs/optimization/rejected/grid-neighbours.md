# Rejected: exact grid neighbour search (2026-10-06)

`grid-neighbours.patch` replaced the O(N²) top-7 scan with a uniform grid searched shell by shell.
It ran the original float32 insertion scan, in index order, over the candidate cells, and
stopped only once every unsearched cell lay beyond the Kth distance (margin 1e-6 relative).

It was exact. `sim/neighbours-check.js` (in the patch) matched the full scan's ids, order and
float32 distances for 13,168 birds: 30 live frames at N 8–1000, plus lattice ties, duplicates,
split clouds, a straggler, a sheet, a line, one point and float32 near-tie layouts.
Mutations failed it: stopping after 27 cells, and skipping the index sort.
`sim/differential.js` was equal over 40 s for these cases:
`seed=1&n=400&calm`, `seed=7&n=100&falcon`, `seed=2&n=1000`, `seed=5&n=300&falcon`.

It was not faster:

| | baseline step (median) | grid step (median) |
|---|---|---|
| node vm, N400 | 1.32 ms | 4.0 ms |
| node vm, N1000 | 4.6 ms | 10.5 ms |
| node vm, N2000 | 12.5 ms | 22.0 ms |
| Chrome 154, N1000 | 3.0 ms | 3.0 ms |

About 57 candidate distances per bird were evaluated, against 400–1000. The shell walk and
per-bird bookkeeping cost more than Chrome's brute-force scan, which takes about 2 ns per pair.
The step is 0.8 ms at N400 in Chrome, so neighbour search is not this app's bottleneck.
Reconsider only for N well above 2000.
