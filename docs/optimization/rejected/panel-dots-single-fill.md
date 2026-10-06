# Rejected: one fill for the 32 correlation-panel dots

Hypothesis: `series()` in `drawPanel` fills 32 separate 1.8 px arcs per series (64 `beginPath/arc/fill`
per frame while the panel is shown, ~13 % of the N1000 frame in the Chrome self-profile). The dots are
disjoint (10.4 px apart, 3.6 px across), so one path with 32 `moveTo`+`arc` subpaths and one `fill`
should cover the same pixels.

Oracle: same-origin iframes of the before/after pages with identical synthetic `corr` values, panel
drawn over a flat fill, 384x266 CSS px region read back at DPR 2 (408 576 px). Negative control: dot
radius 1.9 instead of 1.8.

Result (Chrome 154, macOS, 1728x820 CSS, DPR 2):

| pair | different pixels | max channel delta | mean delta when different |
| --- | --- | --- | --- |
| before vs single fill | 1194 | 77 | 15.5 |
| before vs r=1.9 control | 1241 | 87 | 25.3 |
| single fill vs control | 846 | 111 | 47.0 |

Chrome anti-aliases a multi-contour path differently from 32 single-disc fills, so the output is not
pixel-identical. Rejected on the fidelity rule, not on speed (speed was not measured).
