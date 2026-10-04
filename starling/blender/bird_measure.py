# Species-neutral copy of falcon/blender/falcon_measure.py.
# Pose the bird and measure it from the evaluated (deformed) meshes. exec'd after build/render.
import bpy, json, math
from mathutils import Vector

POSES = json.load(open(POSES_PATH))            # noqa: F821  (injected)


def evaluated_points():
    dg = bpy.context.evaluated_depsgraph_get()
    pts = []
    for ob in bpy.data.collections[PREFIX].objects:                  # noqa: F821
        if ob.type != 'MESH': continue
        ev = ob.evaluated_get(dg)
        me = ev.to_mesh()
        mw = ob.matrix_world
        pts += [mw @ v.co for v in me.vertices]
        ev.to_mesh_clear()
    return pts


def measure(rig):
    P['L']                                       # noqa: F821
    L = P['L']; ybill = P['body']['y_bill']      # noqa: F821
    pts = evaluated_points()
    xs = [p.x for p in pts]; ys = [p.y for p in pts]; zs = [p.z for p in pts]
    span = max(xs) - min(xs)
    wing = [p for p in pts if abs(p.x) > .136 * P['wing']['half_span']]   # noqa: F821  (falcon: 0.07 m)
    tipR = max(pts, key=lambda p: p.x)
    wr = rig.matrix_world @ rig.pose.bones['hand.R'].head
    sh = rig.matrix_world @ rig.pose.bones['humerus.R'].head
    hand_vec = (rig.matrix_world @ rig.pose.bones['hand.R'].tail) - wr
    hand_sweep = math.degrees(math.atan2(-hand_vec.y, hand_vec.x))          # aft of lateral, plan view
    hand_droop = math.degrees(math.atan2(-hand_vec.z, math.hypot(hand_vec.x, hand_vec.y)))
    return dict(span_over_L=span / L, width_m=span,
                tip_aft_of_bill_L=(ybill - tipR.y) / L,
                wingtip_aft_of_bill_L_min=(ybill - min(p.y for p in wing)) / L if wing else None,
                wrist_off_midline_L=abs(wr.x) / L, wrist_ahead_of_shoulder_L=(wr.y - sh.y) / L,
                hand_sweep_deg=hand_sweep, hand_droop_deg=hand_droop,
                height_m=max(zs) - min(zs),
                # the wingtip (hand bone tail) against the shoulder joint: the published flap targets
                tip_above_shoulder_m=(rig.matrix_world @ rig.pose.bones['hand.R'].tail).z - sh.z,
                tip_aft_of_shoulder_m=sh.y - (rig.matrix_world @ rig.pose.bones['hand.R'].tail).y)


def pose_and_measure(name):
    o = OBJS                                      # noqa: F821
    set_pose(o['rig'], POSES[name], o['tail'])    # noqa: F821
    return measure(o['rig'])
