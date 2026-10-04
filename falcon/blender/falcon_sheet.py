# Render every pose's silhouettes (top + front) to OUT_DIR. exec'd after build/render/measure.
import json, os
os.makedirs(OUT_DIR, exist_ok=True)                    # noqa: F821
silhouette_setup()                                     # noqa: F821
metrics = {}
for n in POSES:                                        # noqa: F821
    if n.startswith('_'): continue
    if ONLY and n not in ONLY: continue                # noqa: F821
    m = pose_and_measure(n)                            # noqa: F821
    metrics[n] = {k: (round(v, 3) if isinstance(v, float) else v) for k, v in m.items()}
    for view in VIEWS:                                 # noqa: F821
        render_to(f'{OUT_DIR}/{n}__{view}.png', CAMS[view], (RES, RES))   # noqa: F821
json.dump(metrics, open(f'{OUT_DIR}/metrics.json', 'w'), indent=1)
print(json.dumps(metrics))
