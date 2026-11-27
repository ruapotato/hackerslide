"""HackLite: small pocketable HackOS device (CadQuery concept model).  python hacklite.py [--out DIR]

Portrait-ish: e-ink screen on top, a split thumb keyboard below whose width sets the device width, a 5-way nav switch
between the keyboard halves (the touch screen does the pointing).  Parts (research of 2026-11-27,
docs/research/plugin-mcu-and-eink-2026-11-27.md and lipo-cells-2026-11-27.md):
  brain   PJRC Teensy 4.1 (NXP i.MX RT1062, 600 MHz Cortex-M7, HackOS target exists), 61 x 17.8 mm, mounted under the
          main board with its pins cut short: about 4.5 mm stack (ESTIMATE)
  screen  Good Display GDEY031T10-T21, 3.1" 320 x 240 e-ink with capacitive touch: outline 73.8 x 53.2 mm, 1.53 mm thick
  cell    Adafruit #328 (PKCELL LP785060, 2500 mAh, 9.25 Wh): datasheet maximum 62.5 x 50.5 x 8.1 mm, under the screen
X width, Y height (top edge at Y = H), Z thickness (back at Z = 0), screen up.
"""
import argparse
import json
import os

import cadquery as cq

HERE = os.path.dirname(os.path.abspath(__file__))
PANEL = dict(w=73.8, h=53.2, t=1.53, aa_w=62.0, aa_h=46.5)   # active area: ESTIMATE until the drawing is read
CELL = dict(w=62.5, h=50.5, t=8.1)
TEENSY = dict(w=61.0, h=17.8, t=4.5)
KEY = dict(pitch_x=7.0, pitch_y=7.0, cap_w=6.3, cap_h=6.2, cols=5, rows=4)
SWITCH_H, NUB, FLANGE, CAP_TOP = 0.6, 0.3, 0.5, 1.2
KEYSTACK = SWITCH_H + NUB + FLANGE + CAP_TOP
BOARD_T = 0.8
BACK, WALL, FRONT, GAP = 1.2, 1.6, 0.4, 0.3
CENTRE_GAP = 12.0                                            # between the keyboard halves: the nav switch
R = 8.0
HALF = KEY['cols'] * KEY['pitch_x']
W = 2 * HALF + CENTRE_GAP + 2 * (WALL + 2.5)
KEYS_Y0 = WALL + 3.0                                         # bottom of the key field
SCREEN_Y0 = KEYS_Y0 + KEY['rows'] * KEY['pitch_y'] + 3.0
H = SCREEN_Y0 + PANEL['h'] + 3.0 + WALL
# one main board across the device: cell under the screen half, Teensy under the keyboard half
Z_BOARD = BACK + max(CELL['t'] + GAP, TEENSY['t'] + 0.2)
Z_PANEL = Z_BOARD + BOARD_T + GAP
T = max(Z_PANEL + PANEL['t'] + FRONT, Z_BOARD + BOARD_T + KEYSTACK)
Z_PANEL = T - FRONT - PANEL['t']
Z_FRONT = T - FRONT
CX = W / 2


def rbox(x0, y0, z0, x1, y1, z1, r=0.0):
    b = cq.Workplane('XY').box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))
    r = min(r, (x1 - x0) / 2 - 0.01, (y1 - y0) / 2 - 0.01)
    return b.edges('|Z').fillet(r) if r > 0.05 else b


LEGENDS = {'L': [['Esc', '1', '2', '3', '4'], ['Q', 'W', 'E', 'R', 'T'], ['A', 'S', 'D', 'F', 'G'], ['Shift', 'Z', 'X', 'C', 'V']],
           'R': [['5', '6', '7', '8', 'Del'], ['Y', 'U', 'I', 'O', 'P'], ['H', 'J', 'K', 'L', 'Ent'], ['B', 'N', 'M', 'Spc', 'Fn']]}


def keys():
    out = []
    for side, x0 in (('L', CX - CENTRE_GAP / 2 - HALF), ('R', CX + CENTRE_GAP / 2)):
        for r in range(KEY['rows']):
            for c in range(KEY['cols']):
                out.append((side, r, c, x0 + (c + 0.5) * KEY['pitch_x'], KEYS_Y0 + (KEY['rows'] - r - 0.5) * KEY['pitch_y']))
    return out


def parts():
    outline = lambda z0, z1, inset=0.0: rbox(inset, inset, z0, W - inset, H - inset, z1, R - inset)
    shell = outline(0, Z_FRONT).cut(outline(BACK, T + 1, WALL))
    front = outline(Z_FRONT, T)
    px0, py0 = CX - PANEL['w'] / 2, SCREEN_Y0
    ax0, ay0 = CX - PANEL['aa_w'] / 2, py0 + (PANEL['h'] - PANEL['aa_h']) / 2
    front = front.cut(rbox(ax0 - 0.5, ay0 - 0.5, Z_FRONT - 1, ax0 + PANEL['aa_w'] + 0.5, ay0 + PANEL['aa_h'] + 0.5, T + 1, 1.0))
    caps = None
    for side, r, c, x, y in keys():
        cap = rbox(x - KEY['cap_w'] / 2, y - KEY['cap_h'] / 2, Z_BOARD + BOARD_T + SWITCH_H + NUB, x + KEY['cap_w'] / 2, y + KEY['cap_h'] / 2, T, 1.2)
        caps = cap if caps is None else caps.union(cap)
        front = front.cut(rbox(x - KEY['cap_w'] / 2 - 0.3, y - KEY['cap_h'] / 2 - 0.3, Z_FRONT - 1, x + KEY['cap_w'] / 2 + 0.3, y + KEY['cap_h'] / 2 + 0.3, T + 1, 1.4))
    ny = KEYS_Y0 + KEY['rows'] * KEY['pitch_y'] / 2                        # 5-way nav switch between the halves
    nav = cq.Workplane('XY').circle(4.5).extrude(T + 0.6 - (Z_BOARD + BOARD_T)).translate((CX, ny, Z_BOARD + BOARD_T))
    front = front.cut(cq.Workplane('XY').circle(5.0).extrude(3).translate((CX, ny, Z_FRONT - 1)))
    board = rbox(WALL + 0.3, WALL + 0.3, Z_BOARD, W - WALL - 0.3, H - WALL - 0.3, Z_BOARD + BOARD_T, R - WALL - 0.3)
    cell = rbox(CX - CELL['w'] / 2, py0 + (PANEL['h'] - CELL['h']) / 2, BACK, CX + CELL['w'] / 2, py0 + (PANEL['h'] + CELL['h']) / 2, BACK + CELL['t'], 2.0)
    teensy = rbox(CX - TEENSY['w'] / 2, KEYS_Y0 + 2, Z_BOARD - TEENSY['t'], CX + TEENSY['w'] / 2, KEYS_Y0 + 2 + TEENSY['h'], Z_BOARD, 0.5)
    panel = rbox(px0, py0, Z_PANEL, px0 + PANEL['w'], py0 + PANEL['h'], Z_PANEL + PANEL['t'], 0.8)
    screen = (ax0, ay0, Z_PANEL + PANEL['t'], PANEL['aa_w'], PANEL['aa_h'])
    return dict(shell=shell, front=front, keycaps=caps, stick=nav, kbd_pcb=board, cells=cell, module=teensy, panel=panel), screen


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=os.path.join(HERE, '..', 'hacklite'))
    out = ap.parse_args().out
    os.makedirs(os.path.join(out, 'scene'), exist_ok=True)
    d, screen = parts()
    names, bad = list(d), []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if {a, b} in ({'stick', 'front'},):
                continue
            try:
                v = d[a].intersect(d[b]).val().Volume()
            except Exception:
                v = 0.0
            if v > 0.01:
                bad.append((a, b, round(v, 2)))
    print('collisions:', bad or 'none')
    for n, p in d.items():
        cq.exporters.export(p, os.path.join(out, 'scene', f'closed_{n}.stl'), tolerance=0.02, angularTolerance=0.1)
    ks = [dict(side=s, r=r, c=c, x=x, y=y, label=LEGENDS[s][r][c]) for s, r, c, x, y in keys()]
    json.dump(dict(w=W, h=H, t=T, z_keytop=T, screen=screen, keys=ks,
                   explode=dict(shell=0, cells=10, module=10, kbd_pcb=22, panel=32, keycaps=36, stick=36, front=46)),
              open(os.path.join(out, 'stack.json'), 'w'), indent=1)
    print(f'HackLite {W:.1f} x {H:.1f} x {T:.2f} mm')


if __name__ == '__main__':
    main()
