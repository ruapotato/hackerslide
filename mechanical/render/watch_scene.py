"""Blender still of the watch concept: blender -b --factory-startup -P watch_scene.py -- OUT.png [az el dist]"""
import json
import math
import os
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import scene as S  # noqa: E402

MODEL = os.path.join(HERE, '..', 'watch')
FACE = os.environ.get('WATCH_FACE', '/var/tmp/hackerslide-agent/render/watch/face.png')
ST = json.load(open(os.path.join(MODEL, 'stack.json')))


def load(name, m):
    before = set(bpy.data.objects)
    bpy.ops.wm.stl_import(filepath=os.path.join(MODEL, 'scene', f'closed_{name}.stl'))
    o = (set(bpy.data.objects) - before).pop()
    o.data.materials.append(m)
    S.smooth(o)
    return o


def main():
    argv = sys.argv[sys.argv.index('--') + 1:]
    out = argv[0]
    az, el, dist = (float(v) for v in (argv[1:4] if len(argv) >= 4 else (-30, 38, 260)))
    bpy.ops.wm.read_factory_settings(use_empty=True)
    load('case', S.mat('w_case', (0.62, 0.36, 0.12), 0.4, coat=0.3))
    load('bezel', S.mat('w_bezel', (0.04, 0.04, 0.045), 0.35, coat=0.4))
    load('strap', S.mat('w_strap', (0.05, 0.05, 0.055), 0.7))
    load('glass', S.mat('w_glass', (0.9, 0.9, 0.9), 0.02, alpha=0.08))
    x, y, z, w, h = ST['screen']
    bpy.ops.mesh.primitive_plane_add(size=1, location=(x + w / 2, y + h / 2, z + 0.02))
    o = bpy.context.active_object
    o.scale = (w, h, 1)
    bpy.ops.object.transform_apply(scale=True)
    o.data.materials.append(S.image_mat('face', FACE, emit=0.25, rough=0.85))
    cam = S.stage('cycles', 128, (1600, 1200))
    fl = bpy.data.objects.get('floor')
    fl.location.z = 1.9
    S.aim(cam, (ST['w'] / 2, ST['h'] / 2, ST['t'] / 2), az, el, dist, 70)
    bpy.context.scene.render.filepath = out
    bpy.ops.render.render(write_still=True)


if __name__ == '__main__':
    main()
