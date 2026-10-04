# Measure a batch of candidate poses in one Blender run (exec'd after build/render/measure).
# Globals in: CANDIDATES (list of [label, pose dict]).  Prints one metrics line per candidate.
import json
ref = None
for label, pose in CANDIDATES:                                         # noqa: F821
    set_pose(OBJS['rig'], pose, OBJS['tail'])                          # noqa: F821
    m = measure(OBJS['rig'])                                           # noqa: F821
    print('TUNE', json.dumps({'label': label, **{k: round(v, 4) for k, v in m.items() if isinstance(v, float)}}))
