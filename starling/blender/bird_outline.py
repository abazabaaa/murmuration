# Export vertex-correspondent plan-view (top) outlines for every pose. exec'd after build/render/measure.
# Globals in: OUT_JSON (path), ONLY (pose names or None).
# Output units: the full-spread half-span (P['wing']['half_span']); a = along the body, forward +,
# origin on the shoulder line (model y = 0); w = across, right side only (+x).  Every pose has the
# same point count and the same material points, because they are fixed mesh vertex indices:
#   wing  top-surface vertex 2*(i*(NC+1)+j): leading edge j=0, i=0..NU (root -> tip), then
#         trailing edge j=NC, i=NU-1..0 (tip -> root; the tip vertex is not repeated)
#   body  bill tip (w = 0), then ring vertex i*24 (the +x point of loft ring i), i=0..48, nose -> rump
#   tail  top layer i*15+j: right edge j=14, i=0..10 (base -> tip), then tip row j=13..7 (to centre)
import bpy, json
NU, NC, NR_BODY, N_RING, TAIL_NR, TAIL_NA = 56, 16, 24, 48, 10, 14     # must match bird_build.py
o = OBJS                                                                 # noqa: F821
hs = P['wing']['half_span']                                              # noqa: F821


def eval_xy(ob):
    subs = [(m, m.show_viewport) for m in ob.modifiers if m.type == 'SUBSURF']
    for m, _ in subs: m.show_viewport = False                            # keep the base vertex indices
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    ev = ob.evaluated_get(dg); me = ev.to_mesh()
    assert len(me.vertices) == len(ob.data.vertices), (ob.name, len(me.vertices))
    pts = [ob.matrix_world @ v.co for v in me.vertices]
    ev.to_mesh_clear()
    for m, s in subs: m.show_viewport = s
    return pts


def flat(pts, idx):
    out = []
    for k in idx:
        p = pts[k]; out += [round(p.y / hs, 5), round(p.x / hs, 5)]
    return out


wing_idx = [2 * (i * (NC + 1)) for i in range(NU + 1)] + [2 * (i * (NC + 1) + NC) for i in range(NU - 1, -1, -1)]
body_idx = [i * NR_BODY for i in range(N_RING + 1)]
tail_idx = [i * (TAIL_NA + 1) + TAIL_NA for i in range(TAIL_NR + 1)] + [TAIL_NR * (TAIL_NA + 1) + j for j in range(TAIL_NA - 1, TAIL_NA // 2 - 1, -1)]
wingR = next(w for w in o['wings'] if w.name.endswith('.R'))
res = {'halfSpanM': round(hs, 5), 'L_m': P['L'], 'spanOverL_full': round(2 * hs / P['L'], 4),       # noqa: F821
       'origin': 'shoulder line (model y = 0); a forward, w to the right wing',
       'noseA': round(P['body']['y_bill'] / hs, 5),                                                # noqa: F821
       'tailTipA': round((P['tail']['y_base'] - P['tail']['length']) / hs, 5),                     # noqa: F821
       'counts': {'wing': len(wing_idx), 'body': len(body_idx), 'tail': len(tail_idx)},
       'tailFanOfPose': {}, 'wing': {}}
for n in POSES:                                                                                    # noqa: F821
    if n.startswith('_') or (ONLY and n not in ONLY): continue                                     # noqa: F821
    set_pose(o['rig'], POSES[n], o['tail'])                                                        # noqa: F821
    res['wing'][n] = flat(eval_xy(wingR), wing_idx)
    res['tailFanOfPose'][n] = POSES[n].get('tail_fan', 0)                                          # noqa: F821
set_pose(o['rig'], {}, o['tail'])                                                                  # noqa: F821
bill = eval_xy(o['bill']); tip = max(bill, key=lambda q: q.y)                                   # the bill cone pokes past ring 0
res['body'] = [round(tip.y / hs, 5), 0.0] + flat(eval_xy(o['body']), body_idx)
res['counts']['body'] += 1
kb = o['tail'].data.shape_keys.key_blocks['Fanned']
for key, v in (('tail', 0.0), ('tailFan', 1.0)):
    kb.value = v; res[key] = flat(eval_xy(o['tail']), tail_idx)
kb.value = 0.0
json.dump(res, open(OUT_JSON, 'w'), separators=(',', ':'))
print('outline', {k: res['counts'][k] for k in res['counts']}, 'poses', list(res['wing']))
