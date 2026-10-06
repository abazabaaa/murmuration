# Independent optimization handoff review

Reviewed 2026-10-05 from a package extracted outside the Git checkout at
`~/prj/murmuration-optimization-handoff-20261005-review`.
This was a read-only product review. No timed benchmark, browser run,
dependency installation, or product-source edit was made.

## Source and proposal review

The frozen HTML SHA-256 was
`d24849dffb2feb6882cece1fa00f56852a5d22f3ddd840559ecd4e05aacf8646`,
matching the proposal scope. I checked `PHYSICS_PROPOSALS.md`,
`ARCHITECTURE_PROPOSALS.md`, and `BENCHMARK_RUNBOOK.md` against the page and
probe sources. The top-seven global search, separate position-update pass,
two unordered-pair analysis passes, panel cadence, differential comparison
fields, and profiler limitations are represented accurately. The documents
label speedups as hypotheses and keep native Canvas, virtual-host, and browser
evidence distinct. I found no source-level proposal blocker.

## Portable package checks

Commands below ran from the extracted package root or its `app/` subdirectory.
The package was outside a Git repository (`git rev-parse --is-inside-work-tree`
exited 128); no `/tmp` scratch data was supplied.

| Check | Command and observed result |
| --- | --- |
| Integrity | `python3 verify-package.py .` returned `status: matched`, 118 manifest files, and the expected baseline HTML hash. In a disposable copy, appending a sentinel to `app/CREDITS.md` made the verifier exit 1 with `changed: app/CREDITS.md`. |
| Built-in behavior and controls | From `app/`, `node sim/check.js` returned `status: passed`, including 120 replay frames, the velocity negative control, 450 retained ring events, and the motion suite. |
| Explicit-baseline comparison | From `app/`, `node sim/differential.js --baseline ~/prj/murmuration-optimization-handoff-20261005-review/baseline/murmuration.html --current murmuration.html --seconds 8 --cases 'seed=7&n=40&falcon&painted' --inputs sim/example-inputs.json` returned `status: equal`, 480 paired frames and one hunt event. This is a bounded portability check, not the runbook's 40-second/N400 acceptance gate. |
| Timing negative controls | From `app/`, `node sim/differential.js --seconds banana` exited 1 with `invalid seconds or dt-ms`; `node sim/differential.js --seconds 0.001 --dt-ms 1000` exited 1 with `duration must contain at least one frame`. These failures occurred without Git extraction. |
| Native glyph comparison | From the root, `node glyph-compare.js --baseline=~/prj/murmuration-optimization-handoff-20261005-review/baseline/murmuration.html --current=~/prj/murmuration-optimization-handoff-20261005-review/app/murmuration.html --canvas-module=~/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@napi-rs/canvas` passed 200 far and eight near cases. Baseline and current HTML are identical, so both matrix errors were zero; flattening Z produced 2.25347 CSS px maximum error and was rejected by the 0.5 CSS px gate. This used an already installed external native provider. |

The native glyph check proves the portable tool can execute and detect its
negative control. It does not independently re-establish the earlier
pre-contour-versus-current 0.17678 CSS px measurement, and no browser frame
rate or target-device presentation was observed.

## Package completeness finding

The review package omitted three evidence files that
`app/docs/FIRST_MILESTONE.md` links relative to itself:
`docs/verification/simulator-example.csv`, `docs/verification/flock-40s.txt`,
and `docs/verification/blender-inventory.txt`. All three exist in the source
checkout. Include them in the final package and rerun its manifest verifier;
this review's 118-file count belongs to the preliminary package.

Final-package readback: `~/prj/murmuration-optimization-handoff-20261005`
included all three files. `python3 verify-package.py .` returned `status:
matched` for 122 files and the same baseline HTML hash. A scan of every
relative Markdown link in `app/**/*.md` found zero missing targets. The three
restored files had nonzero sizes (2,086, 925, and 3,020 bytes, respectively).
The native glyph and behavior probes above ran on the preliminary package;
the final rebuild added documentation/evidence files and did not change the
tested HTML or probe sources.
