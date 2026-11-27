"""Blender stills of the UMPC concept: blender -b --factory-startup -P umpc_scene.py -- OUT.png [az el dist explode]"""
import json
import os
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import scene as S  # noqa: E402

MODEL = os.path.join(HERE, '..', 'umpc')
SCREEN = os.environ.get('UMPC_SCREEN', '/var/tmp/hackerslide-agent/render/umpc/screen.png')
ST = json.load(open(os.path.join(MODEL, 'stack.json')))


def load(name, m):
    before = set(bpy.data.objects)
    bpy.ops.wm.stl_import(filepath=os.path.join(MODEL, 'scene', f'closed_{name}.stl'))
    o = (set(bpy.data.objects) - before).pop()
    o.name = name
    o.data.materials.append(m)
    S.smooth(o)
    return o


def main():
    argv = sys.argv[sys.argv.index('--') + 1:]
    out = argv[0]
    az, el, dist, ex = (float(v) for v in (argv[1:5] if len(argv) >= 5 else (-25, 40, 520, 0)))
    bpy.ops.wm.read_factory_settings(use_empty=True)
    M = dict(shell=S.mat('u_shell', (0.62, 0.36, 0.12), 0.42, coat=0.25), front=S.mat('u_front', (0.05, 0.05, 0.055), 0.4, coat=0.3),
             keycaps=S.mat('u_cap', (0.10, 0.10, 0.11), 0.45), stick=S.mat('u_stick', (0.13, 0.13, 0.14), 0.3, coat=0.4),
             kbd_pcb=S.mat('u_kbd', (0.03, 0.22, 0.10), 0.35), cells=S.mat('u_cell', (0.55, 0.57, 0.62), 0.3, metal=0.6),
             carrier=S.mat('u_carrier', (0.03, 0.22, 0.10), 0.35), module=S.mat('u_mod', (0.08, 0.2, 0.45), 0.35),
             thermal=S.mat('u_pad', (0.85, 0.45, 0.2), 0.6), panel=S.mat('u_panel', (0.02, 0.02, 0.025), 0.15),
             shoulders=S.mat('u_sh', (0.08, 0.08, 0.09), 0.4))
    objs = {n: load(n, m) for n, m in M.items()}
    x, y, z, w, h = ST['screen']
    bpy.ops.mesh.primitive_plane_add(size=1, location=(x + w / 2, y + h / 2, z + 0.02))
    scr = bpy.context.active_object
    scr.scale = (w, h, 1)
    bpy.ops.object.transform_apply(scale=True)
    scr.data.materials.append(S.image_mat('u_screen', SCREEN, emit=1.6, rough=0.15))
    objs['screen'] = scr
    leg = S.mat('u_leg', (0.9, 0.9, 0.88), 0.6)
    legs = []
    for k in ST['keys']:
        if k['label']:
            legs.append(S.text('l' + k['side'] + str(k['r']) + str(k['c']), k['label'], k['x'], k['y'], ST['z_keytop'] + 0.02,
                               3.0 if len(k['label']) == 1 else 1.9, leg))
    E = dict(ST['explode'], screen=ST['explode']['panel'])
    for n, o in objs.items():
        o.location.z += E.get(n, 0) * ex
    for o in legs:
        o.location.z += E['keycaps'] * ex
    cam = S.stage('cycles', 128, (1920, 1080))
    fl = bpy.data.objects.get('floor')
    fl.location.z = -0.05 - 1.0 * ex
    S.aim(cam, (ST['w'] / 2, ST['h'] / 2, 6 + 25 * ex), az, el, dist, 70)
    bpy.context.scene.render.filepath = out
    bpy.ops.render.render(write_still=True)


if __name__ == '__main__':
    main()
