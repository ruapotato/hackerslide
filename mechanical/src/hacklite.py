"""HackLite: small HackOS handheld, keys LEFT and RIGHT of a small e-ink screen (CadQuery concept model).

  python hacklite.py [--layout bar29|side31] [--out DIR]

Two layouts (David, 2026-11-27: keys beside the screen like the HackBrain, not below it):
  bar29   Good Display GDEY029T71H, 2.9" 384 x 168 e-ink (no touch; outline 79.98 x 35.57 mm): a slim bar
  side31  Good Display GDEY031T10-T21, 3.1" 320 x 240 e-ink with touch (outline 73.8 x 53.2 x 1.53 mm)
Brain: SparkFun MicroMod Teensy Processor (NXP i.MX RT1062, the HackOS Teensy target; 22 x 22 mm card in an M.2
socket, about 6 mm above the board), under the left keys.  Cell under the screen (see CELLS).  Research:
docs/research/plugin-mcu-and-eink-2026-11-27.md and lipo-cells-2026-11-27.md.  Active areas: ESTIMATES.
X width, Y height, Z thickness (back at Z = 0), screen up.
"""
import argparse
import json
import os

import cadquery as cq

HERE = os.path.dirname(os.path.abspath(__file__))
PANELS = {'bar29': dict(w=79.98, h=35.57, t=1.2, aa_w=67.0, aa_h=29.2),
          'side31': dict(w=73.8, h=53.2, t=1.53, aa_w=62.0, aa_h=46.5)}
CELLS = {'bar29': dict(name='Jauch LP503759JU, 1350 mAh, 5.0 Wh', w=62.0, h=38.0, t=5.8),
         'side31': dict(name='Adafruit #328, 2500 mAh, 9.25 Wh', w=62.5, h=50.5, t=8.1)}
MODULE = dict(w=22.0, h=22.0, t=6.0)
KEY = dict(pitch_x=7.6, cols=5, rows=5, gap=0.7)                # keys fill the height beside the screen (David: less bezel);
                                                             # pitch_y follows from the height, caps are pitch minus gap
KEYSTACK = 0.6 + 0.3 + 0.5 + 1.2
BOARD_T, BACK, WALL, FRONT, GAP = 0.8, 1.2, 1.6, 0.4, 0.3
LEGENDS = {'L': [['Esc', '1', '2', '3', '4'], ['Q', 'W', 'E', 'R', 'T'], ['A', 'S', 'D', 'F', 'G'], ['Z', 'X', 'C', 'V', 'B'],
                 ['Shift', 'Ctrl', 'Alt', 'Tab', 'Spc']],
           'R': [['5', '6', '7', '8', 'Del'], ['Y', 'U', 'I', 'O', 'P'], ['H', 'J', 'K', 'L', 'Ent'], ['N', 'M', ',', '.', '/'],
                 ['Spc', 'Sym', '-', 'Fn', 'Shift']]}


def rbox(x0, y0, z0, x1, y1, z1, r=0.0):
    b = cq.Workplane('XY').box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))
    r = min(r, (x1 - x0) / 2 - 0.01, (y1 - y0) / 2 - 0.01)
    return b.edges('|Z').fillet(r) if r > 0.05 else b


def build(layout):
    P, C = PANELS[layout], CELLS[layout]
    half = KEY['cols'] * KEY['pitch_x']
    EDGE, SCREEN_GAP = 1.2, 2.0                              # key field to the wall, and to the screen
    W = 2 * (WALL + EDGE + half + SCREEN_GAP) + P['w']
    H = max(P['h'], C['h']) + 2 * WALL + 3.0
    pitch_y = (H - 2 * WALL - 2 * EDGE) / KEY['rows']
    R = min(6.0, H / 2 - 1)
    CX, CY = W / 2, H / 2
    z_board = BACK + max(C['t'] + GAP, MODULE['t'] + 0.2)
    T = max(z_board + BOARD_T + GAP + P['t'] + FRONT, z_board + BOARD_T + KEYSTACK)
    z_front = T - FRONT
    z_panel = z_front - P['t']
    outline = lambda z0, z1, i=0.0: rbox(i, i, z0, W - i, H - i, z1, R - i)
    shell = outline(0, z_front).cut(outline(BACK, T + 1, WALL))
    front = outline(z_front, T)
    ax0, ay0 = CX - P['aa_w'] / 2, CY - P['aa_h'] / 2
    front = front.cut(rbox(ax0 - 0.5, ay0 - 0.5, z_front - 1, ax0 + P['aa_w'] + 0.5, ay0 + P['aa_h'] + 0.5, T + 1, 1.0))
    keys, caps = [], None
    cw, ch = KEY['pitch_x'] - KEY['gap'], pitch_y - KEY['gap']
    for side, x0 in (('L', WALL + EDGE), ('R', W - WALL - EDGE - half)):
        for r in range(KEY['rows']):
            for c in range(KEY['cols']):
                x, y = x0 + (c + 0.5) * KEY['pitch_x'], CY + (KEY['rows'] / 2 - r - 0.5) * pitch_y
                keys.append(dict(side=side, r=r, c=c, x=x, y=y, label=LEGENDS[side][r][c]))
                cap = rbox(x - cw / 2, y - ch / 2, z_board + BOARD_T + 0.9, x + cw / 2, y + ch / 2, T, 1.2)
                caps = cap if caps is None else caps.union(cap)
    for side, x0 in (('L', WALL + EDGE), ('R', W - WALL - EDGE - half)):       # one opening per key field: no web between keys
        front = front.cut(rbox(x0 - 0.3, CY - KEY['rows'] * pitch_y / 2 - 0.3, z_front - 1, x0 + half + 0.3, CY + KEY['rows'] * pitch_y / 2 + 0.3, T + 1, 2.0))
    board = rbox(WALL + 0.3, WALL + 0.3, z_board, W - WALL - 0.3, H - WALL - 0.3, z_board + BOARD_T, R - WALL - 0.3)
    cell = rbox(CX - C['w'] / 2, CY - C['h'] / 2, BACK, CX + C['w'] / 2, CY + C['h'] / 2, BACK + C['t'], 2.0)
    mx = WALL + EDGE + half / 2
    module = rbox(mx - MODULE['w'] / 2, CY - MODULE['h'] / 2, z_board - MODULE['t'], mx + MODULE['w'] / 2, CY + MODULE['h'] / 2, z_board, 0.5)
    panel = rbox(CX - P['w'] / 2, CY - P['h'] / 2, z_panel, CX + P['w'] / 2, CY + P['h'] / 2, z_panel + P['t'], 0.8)
    d = dict(shell=shell, front=front, keycaps=caps, kbd_pcb=board, cells=cell, module=module, panel=panel)
    return d, dict(w=W, h=H, t=T, z_keytop=T, screen=(ax0, ay0, z_panel + P['t'], P['aa_w'], P['aa_h']), keys=keys,
                   cell=C['name'], explode=dict(shell=0, cells=8, module=8, kbd_pcb=18, panel=26, keycaps=30, front=38))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--layout', default='bar29', choices=sorted(PANELS))
    ap.add_argument('--out', default=None)
    ap.add_argument('--pitch', type=float, default=KEY['pitch_x'], help='key pitch across, mm (7.6 default; 6.0 = phone-keyboard size)')
    a = ap.parse_args()
    KEY['pitch_x'] = a.pitch
    out = a.out or os.path.join(HERE, '..', 'hacklite', a.layout + ('' if a.pitch == 7.6 else f'_p{a.pitch:g}'))
    os.makedirs(os.path.join(out, 'scene'), exist_ok=True)
    d, info = build(a.layout)
    names, bad = list(d), []
    for i, x in enumerate(names):
        for y in names[i + 1:]:
            try:
                v = d[x].intersect(d[y]).val().Volume()
            except Exception:
                v = 0.0
            if v > 0.01:
                bad.append((x, y, round(v, 2)))
    print(a.layout, 'collisions:', bad or 'none')
    for n, p in d.items():
        cq.exporters.export(p, os.path.join(out, 'scene', f'closed_{n}.stl'), tolerance=0.02, angularTolerance=0.1)
    json.dump(info, open(os.path.join(out, 'stack.json'), 'w'), indent=1)
    print(f"HackLite {a.layout}: {info['w']:.1f} x {info['h']:.1f} x {info['t']:.2f} mm; cell {info['cell']}")


if __name__ == '__main__':
    main()
