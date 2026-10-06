"""Read saved scenes in background Blender without changing or saving either file.

Blender --background --factory-startup --python sim/blender-inventory.py -- FILE FILE
"""
import bpy
import hashlib
import json
import sys
from pathlib import Path

files = sys.argv[sys.argv.index('--') + 1:]
results = []
for filename in files:
    source = Path(filename).resolve()
    bpy.ops.wm.open_mainfile(filepath=str(source))
    geometry = []
    for ob in sorted(bpy.data.objects, key=lambda ob: ob.name):
        if not ob.name.startswith(('MotionStarling', 'MotionFalcon')):
            continue
        record = {'name': ob.name, 'type': ob.type}
        if ob.type == 'MESH':
            record['vertices'] = [[float(v) for v in vertex.co] for vertex in ob.data.vertices]
            record['faces'] = [list(face.vertices) for face in ob.data.polygons]
        if ob.type == 'ARMATURE':
            record['bones'] = [{'name': b.name, 'head': list(b.head_local), 'tail': list(b.tail_local)} for b in ob.data.bones]
        geometry.append(record)
    actions = []
    used = {ob.animation_data.action.name for ob in bpy.data.objects
            if ob.name.startswith(('MotionStarling', 'MotionFalcon'))
            and ob.animation_data and ob.animation_data.action}
    for action in sorted(bpy.data.actions, key=lambda a: a.name):
        curves = []
        for layer in action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    for curve in bag.fcurves:
                        curves.append({'path': curve.data_path, 'index': curve.array_index,
                                       'keys': [{'co': list(k.co), 'left': list(k.handle_left), 'right': list(k.handle_right),
                                                 'interpolation': k.interpolation} for k in curve.keyframe_points]})
        actions.append({'name': action.name, 'curves': curves})
    digest = lambda data: hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
    results.append({'file': str(source), 'sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                    'scenes': [{'name': s.name, 'objects': sorted(o.name for o in s.objects),
                                'fps': s.render.fps, 'frames': [s.frame_start, s.frame_end]} for s in bpy.data.scenes],
                    'motionObjects': len(geometry), 'geometrySha256': digest(geometry),
                    'actions': [{'name': a['name'], 'curves': len(a['curves'])} for a in actions],
                    'activeScene': bpy.context.scene.name,
                    'usedActionsSha256': digest([a for a in actions if a['name'] in used]),
                    'actionsSha256': digest(actions)})
print('INVENTORY_JSON=' + json.dumps({'blender': bpy.app.version_string, 'files': results,
                                     'scope': 'saved base meshes/bones and action keyframes; no files saved'}))
