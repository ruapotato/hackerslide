"""Place (and optionally autoroute) the keyboard PCB.  Usage: keyboard_pcb.py alps|dome BOARD_DIR [--route]

The board is the floor of the keyboard tray and the bottom skin of the device (David, 2026-11-24), so EVERYTHING is
on the top (F) side and the bottom stays bare.  It covers the whole tray: the key area is y = 0..31, and the board
continues to y = -38 under the part of the tray that stays below the body (FPC connector, room for the cable loop).
The top plate sits 1.5 mm above the board on four SMT spacers; parts under it are at most 1.0 mm high, and the
diodes (0.5 mm) sit under the keycap flanges, which ride 0.9 mm above the board.
"""
import os
import sys

import pcbnew

import kbd_layout as KL
from pcbgen import Board, route, set_project_rules

TOP_PLATE_HOLES = KL.PLATE_HOLES

RULES = {'min_clearance': 0.127, 'min_track_width': 0.127, 'min_via_diameter': 0.45, 'min_through_hole_diameter': 0.2,
         'min_copper_edge_clearance': 0.3, 'min_hole_clearance': 0.2, 'min_hole_to_hole': 0.25,
         'min_via_annular_width': 0.1}
CLASSES = [{'name': 'Default', 'clearance': 0.15, 'track_width': 0.15, 'via_diameter': 0.45, 'via_drill': 0.2},
           {'name': 'Power', 'clearance': 0.15, 'track_width': 0.3, 'via_diameter': 0.5, 'via_drill': 0.25}]
PATTERNS = [('+3V3', 'Power'), ('GND', 'Power')]


def build(variant, bdir, do_route=False):
    name = 'keyboard' if variant == 'alps' else 'keyboard-5135'
    top = -KL.BOARD_TOP_EXT
    B = Board(os.path.join(bdir, 'netlist.json'), layers=2, thickness=KL.PCB_T)
    B.outline(0, top, KL.BOARD_W, KL.BOARD_H, r=1.5)
    B.region = (0.4, top + 0.4, KL.BOARD_W - 0.4, KL.BOARD_H - 0.4)
    keepout = [(x - 2.6, y - 2.6, x + 2.6, y + 2.6) for (x, y) in TOP_PLATE_HOLES]
    for i, (x, y) in enumerate(TOP_PLATE_HOLES):
        B.place(f'H{i + 1}', x, y, 0, 'F')
    # keycap flanges ride 0.9 mm above the board: only the 0.5 mm diodes may sit under them
    c = KL.CAP
    flanges = []
    for i, (kname, r, col, x, y) in enumerate(KL.keys(variant)):
        B.place(f'SW{i + 1}', x, y, 0, 'F')
        B.text(kname, x, y - (2.6 if variant == 'alps' else 0), pcbnew.F_Fab, 0.8)
        hw, hh = (2.8, 2.8) if r == 4 else (c['flange_w'] / 2, c['flange_h'] / 2)
        flanges.append((x - hw - 0.2, y - hh - 0.2, x + hw + 0.2, y + hh + 0.2))
    # one diode per matrix position, next to its switch and under the same keycap
    for i, (kname, r, col, x, y) in enumerate(KL.keys(variant)):
        if f'D{i + 1}' in B.fps:
            B.pack([f'D{i + 1}'], x, y + (2.1 if variant == 'alps' else 0), 'F', rot=0, keepout=keepout,
                   region=(x - 3.6, y - 3.2, x + 3.6, y + 3.2))
    # FPC connector above the key area, opening toward the top of the tray, straight below carrier J9; ESD clamp at it
    jx, jy = KL.J1_XY
    B.place('J1', jx, jy, 180, 'F')
    B.place('U2', jx, jy + 2.5, 0, 'F')
    # spring-pin landing pads: device x 105..120, under the carrier bottom strip when open (tray y 19..33)
    for i in range(6):
        B.place(f'LP{i + 1}', 104.0 + 3.0 * i, -13.5, 0, 'F')
    # scanner and its passives: D-pad zone corners, clear of the D-pad keycaps and of the spacers
    ko = keepout + flanges
    B.place('U1', 6.0, 9.6, 0, 'F')
    B.pack(['C1', 'C2', 'R3', 'R4', 'R1', 'R2'], 17.0, 9.0, 'F', keepout=ko, region=(0.6, 0.6, 22.4, 30.4))
    B.pack(['TP1', 'TP2', 'TP3', 'TP4'], 18.0, 22.5, 'F', keepout=ko, region=(0.6, 0.6, 22.4, 30.4))
    left = B.unplaced()
    assert not left, left
    B.text('HackerSlide 810 keyboard ' + ('Alps SKSW' if variant == 'alps' else 'Keystone 5135 domes') + ' rev 0.1 DRAFT  CERN-OHL-S-2.0',
           KL.BOARD_W / 2, -20.0, pcbnew.F_SilkS, 1.0)
    # GND pour on both layers
    pts = [(0, top), (KL.BOARD_W, top), (KL.BOARD_W, KL.BOARD_H), (0, KL.BOARD_H)]
    B.zone('GND', pcbnew.B_Cu, pts, clearance=0.2)
    B.zone('GND', pcbnew.F_Cu, pts, clearance=0.2)
    path = B.save(os.path.join(bdir, name + '.kicad_pcb'))
    nl_sheets = None
    set_project_rules(path.replace('.kicad_pcb', '.kicad_pro'), RULES, CLASSES, PATTERNS)
    # The Wuerth WA-SMSI footprint is a solder ring around its own non-plated hole: not a clearance fault.
    open(path.replace('.kicad_pcb', '.kicad_dru'), 'w').write(
        '(version 1)\n(rule "wuerth_spacer_ring"\n  (condition "A.memberOfFootprint(\'H?\') && B.memberOfFootprint(\'H?\')")\n'
        '  (constraint hole_clearance (min 0mm)))\n')
    if do_route:
        print(route(path, passes=30, timeout=3000))
    return path


if __name__ == '__main__':
    print(build(sys.argv[1], sys.argv[2], '--route' in sys.argv))
