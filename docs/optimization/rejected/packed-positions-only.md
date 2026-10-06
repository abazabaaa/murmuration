# Superseded: packed positions alone in the neighbour scan

Copying px/py/pz into one interleaved Float32Array for the O(N^2) scan (exact: same float32 values, same
expression) gave Chrome N1000 step 2.7 -> 2.6 ms (A-B-B-A: A 2.7, B 2.6, B 2.6, A 2.7), within noise
on its own. Holding the stored Kth distance in a local (`kth`, Infinity until K are held) on top of it
is what paid: Chrome N2000 step 9.0/8.8 -> 7.4/7.3 ms. The combined form is committed (05a056a); the
packed-only form is recorded here so it is not retried as a separate change.
