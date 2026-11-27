"""Blender scene of the hack pad concept model, for stills and clips.

  blender -b --factory-startup -P hackpad_scene.py -- SHOT OUT_DIR [--frames A B] [--size W H] [--samples N]

Loads the STLs and stack.json that mechanical/src/hackpad.py writes (default mechanical/hackpad/, or $HP_MODEL), the
screen picture (default /var/tmp/hackerslide-agent/render/hackpad/screen.png, or $HP_SCREEN) and, for the comparison
shot, the Linux design's scene STLs (/var/tmp/hackerslide-agent/render/assets/scene, or $HS_ASSETS/scene).

What is schematic: everything under the main board is a block of the right height in a plausible place (there is no
board layout yet), the shells are plain, and the screen picture is a mock-up.  The heights and therefore the
thickness are the model's real numbers.
"""
import json
import math
import os
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import scene as S  # noqa: E402  (materials, lights, camera helpers of the Linux-design scene)

MODEL = os.environ.get('HP_MODEL', os.path.join(HERE, '..', 'hackpad'))
SCREEN = os.environ.get('HP_SCREEN', '/var/tmp/hackerslide-agent/render/hackpad/screen.png')
LINUX = os.path.join(os.environ.get('HS_ASSETS', '/var/tmp/hackerslide-agent/render/assets'), 'scene')
ST = json.load(open(os.path.join(MODEL, 'stack.json')))
BW, BH = ST['body']
LID = ('lid_shell', 'panel', 'lid_board', 'lid_board_parts', 'screen_img')
# explode: how far each part rises (mm) when fully pulled apart, bottom to top
EXPLODE = {'base_shell': 0, 'nfc_coil': 7, 'battery': 16, 'board_parts': 30, 'board': 30, 'legends': 48,
           'key_plate': 40, 'keycaps': 48, 'lid_shell': 64, 'lid_board': 70, 'lid_board_parts': 70, 'panel': 78, 'screen_img': 78}


def load(name, material, tag='closed', parent=None, folder=MODEL):
    path = os.path.join(folder, 'scene', f'{tag}_{name}.stl') if folder == MODEL else os.path.join(folder, f'{tag}_{name}.stl')
    if not os.path.exists(path):
        return None
    before = set(bpy.data.objects)
    bpy.ops.wm.stl_import(filepath=path)
    o = (set(bpy.data.objects) - before).pop()
    o.name = f'{tag}_{name}'
    o.data.materials.append(material)
    S.smooth(o)
    if parent:
        o.parent = parent
    return o


def screen_plane(parent):
    x, y, z, w, h = ST['screen']
    bpy.ops.mesh.primitive_plane_add(size=1, location=(x + w / 2, y + h / 2, z + 0.02))
    o = bpy.context.active_object
    o.name = 'screen_img'
    o.scale = (w, h, 1)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(S.image_mat('epaper', SCREEN, emit=0.25, rough=0.85))
    o.parent = parent
    return o


def legends(parent, material):
    z = ST['z_key_top'] + 0.02
    objs = []
    for k in ST['keys']:
        label = {'ShiftL': 'Shift', 'ShiftR': 'Shift', 'Space': '', 'Enter': 'Ent', 'Back': 'Del'}.get(k['name'], k['name'])
        label = {'Up': '▲', 'Down': '▼', 'Left': '◀', 'Right': '▶'}.get(label, label)
        if not label:
            continue
        size = 3.2 if len(label) == 1 else 2.2
        objs.append(S.text('leg_' + k['name'], label, k['x'], k['y'] + (0.8 if k.get('fn') else 0), z, size, material, parent))
        if k.get('fn'):
            objs.append(S.text('fn_' + k['name'], k['fn'], k['x'], k['y'] - 2.2, z, 1.6, material, parent))
    return objs


class HackPad:
    def __init__(self, tag='closed', x0=0.0):
        M = dict(shell=S.mat('hp_shell', (0.62, 0.36, 0.12), 0.45, coat=0.2), lid=S.mat('hp_lid', (0.05, 0.055, 0.06), 0.35, coat=0.3),
                 board=S.mat('hp_board', (0.03, 0.22, 0.10), 0.35), parts=S.mat('hp_parts', (0.08, 0.08, 0.09), 0.4),
                 battery=S.mat('hp_batt', (0.55, 0.57, 0.62), 0.3, metal=0.6), coil=S.mat('hp_coil', (0.72, 0.38, 0.18), 0.3, metal=0.8),
                 plate=S.mat('hp_plate', (0.04, 0.04, 0.045), 0.6), cap=S.mat('hp_cap', (0.10, 0.10, 0.11), 0.45),
                 legend=S.mat('hp_legend', (0.85, 0.85, 0.82), 0.6), panel=S.mat('hp_panel', (0.18, 0.18, 0.19), 0.5),
                 lidb=S.mat('hp_lidb', (0.03, 0.22, 0.10), 0.35))
        self.root = S.empty('hackpad')
        self.root.location.x = x0
        self.lid = S.empty('lid', self.root)
        self.o = {}
        for n, m in (('base_shell', 'shell'), ('nfc_coil', 'coil'), ('battery', 'battery'), ('board_parts', 'parts'), ('board', 'board'),
                     ('key_plate', 'plate'), ('keycaps', 'cap')):
            self.o[n] = load(n, M[m], tag, self.root)
        for n, m in (('lid_shell', 'lid'), ('panel', 'panel'), ('lid_board', 'lidb'), ('lid_board_parts', 'parts')):
            self.o[n] = load(n, M[m], tag, self.lid)
        self.o['screen_img'] = screen_plane(self.lid) if tag != 'section' else None
        self.leg = S.empty('legends', self.root)
        if tag != 'section':
            legends(self.leg, M['legend'])
        self.o['legends'] = self.leg
        self.base = {n: o.location.copy() for n, o in self.o.items() if o}

    def set(self, slide, explode):
        self.lid.location.y = ST['travel'] * slide
        for n, o in self.o.items():
            if o:
                o.location = self.base[n] + Vector((0, 0, EXPLODE.get(n, 0) * explode))


def ease(t):
    return S.ease(t)


def lerp(a, b, t):
    return a + (b - a) * t


CX, CY = BW / 2, BH / 2


def s_hero(u):
    return dict(slide=0, explode=0, target=(CX, CY, 8), az=lerp(-35, 35, ease(u)), el=lerp(34, 26, ease(u)), dist=430)


def s_open(u):
    s = ease((u - 0.15) / 0.5)
    return dict(slide=s, explode=0, target=(CX, lerp(CY, CY + 14, s), 8), az=lerp(-22, -6, ease(u)), el=lerp(30, 44, ease(u)), dist=lerp(430, 480, ease(u)))


def s_explode(u):
    e = ease((u - 0.1) / 0.55)
    return dict(slide=1, explode=e, target=(CX, CY + 14, lerp(8, 40, e)), az=lerp(-6, 38, ease(u)), el=lerp(44, 16, e), dist=lerp(480, 720, e))


def s_keys(u):
    return dict(slide=1, explode=0, target=(lerp(30, 100, ease(u)), 18, 11), az=lerp(-15, 12, ease(u)), el=42, dist=220, lens=85)


def s_section(u):
    """The cut-away: looking at the cut face, the layers stacked up; the camera drifts along the cut."""
    return dict(slide=0, explode=0, section=True, target=(BW * 0.5, BH / 2, 7.5), az=lerp(62, 90, ease(u)), el=lerp(18, 3, ease(u)),
                dist=lerp(380, 330, ease(u)), lens=100, floor_z=-0.2)


def s_compare(u):
    """Hack pad (centre), the Linux handheld design (left) and an N810-sized block (right), turning to edge-on."""
    return dict(slide=0, explode=0, compare=True, target=(CX, CY, 10), az=lerp(-24, 0, ease(u)), el=lerp(28, 3, ease(u)),
                dist=lerp(1150, 1050, ease(u)), lens=70)


SHOTS = {'hp_hero': (s_hero, 180), 'hp_open': (s_open, 150), 'hp_explode': (s_explode, 240), 'hp_keys': (s_keys, 120),
         'hp_section': (s_section, 150), 'hp_compare': (s_compare, 180)}


def build_compare():
    """Linux design to the left (its own STLs, closed), N810 block to the right, with name and thickness labels."""
    grey = S.mat('lx_shell', (0.20, 0.22, 0.25), 0.45, coat=0.2)
    tray = S.mat('lx_tray', (0.25, 0.27, 0.30), 0.45)
    cap = S.mat('lx_cap', (0.9, 0.9, 0.88), 0.5)
    lx = S.empty('linux')
    for n, m in (('front_shell', grey), ('back_shell', grey), ('tray', tray), ('keycap_tops', cap), ('panel', S.mat('lx_panel', (0.02, 0.03, 0.05), 0.2))):
        load(n, m, 'closed', lx, folder=LINUX)
    lx.location.x = -160
    n810 = S.cube('n810', 0, 0, 0, 128, 72, 14, S.mat('n810', (0.55, 0.56, 0.58), 0.5, metal=0.3), bevel=2.0)
    n810.location.x += 160
    white = S.mat('label', (0.9, 0.9, 0.9), 0.5, emit=((0.9, 0.9, 0.9), 0.6))
    for name, x, t in (('Linux handheld  19.4 mm', -160 + 65.75, 19.35), ('Hack pad  %.1f mm' % ST['total'], CX, ST['total']),
                       ('Nokia N810  14 mm', 160 + 64, 14.0)):
        o = S.text('lab_' + name, name, x, -8, t + 9, 10, white)
        o.rotation_euler = (math.radians(90), 0, 0)


def main():
    argv = sys.argv[sys.argv.index('--') + 1:]
    shot, out = argv[0], argv[1]

    def arg(name, n, default):
        if name in argv:
            i = argv.index(name)
            return [type(default[0])(v) for v in argv[i + 1:i + 1 + n]]
        return default
    fn, total = SHOTS[shot]
    a, b = arg('--frames', 2, [0, total - 1])
    size = arg('--size', 2, [1920, 1080])
    samples = arg('--samples', 1, [128])[0]
    bpy.ops.wm.read_factory_settings(use_empty=True)
    first = fn(0.0)
    dev = HackPad('section' if first.get('section') else 'closed')
    if first.get('compare'):
        build_compare()
    cam = S.stage('cycles', samples, size)
    os.makedirs(out, exist_ok=True)
    floor = bpy.data.objects.get('floor')
    for f in range(a, b + 1):
        path = os.path.join(out, f'{shot}-{f:04d}.png')
        if os.path.exists(path) and '--force' not in argv:
            continue
        st = fn(f / max(1, total - 1))
        dev.set(st['slide'], st['explode'])
        if floor:
            floor.location.z = st.get('floor_z', -40 * st['explode'] - 0.05)
        S.aim(cam, st['target'], st['az'], st['el'], st['dist'], st.get('lens', 70))
        bpy.context.scene.render.filepath = path
        bpy.ops.render.render(write_still=True)
        print('FRAME', shot, f, flush=True)


if __name__ == '__main__':
    main()
