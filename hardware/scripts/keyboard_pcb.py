"""Place (and optionally autoroute) the keyboard PCB.  Usage: keyboard_pcb.py alps|dome BOARD_DIR [--route]

Stack: switches on the top (F) side; diodes, the TCA8418 scanner and the FPC connector on the bottom (B) side,
so the top side stays flat for the top-plate PCB and keycaps (KeebDeck-style stack, see docs/keyboard.md).
Everything on the bottom is at most 1.1 mm high (tray clearance 1.2 mm, mechanical/src/config.py).
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
    B = Board(os.path.join(bdir, 'netlist.json'), layers=2, thickness=0.8)
    B.outline(0, 0, KL.BOARD_W, KL.BOARD_H, r=1.5)
    keepout = [(x - 1.8, y - 1.8, x + 1.8, y + 1.8) for (x, y) in TOP_PLATE_HOLES]
    for i, (x, y) in enumerate(TOP_PLATE_HOLES):
        B.place(f'H{i + 1}', x, y, 0, 'F')
    # switches (top) and their diodes (bottom, just below the switch)
    for i, (kname, r, c, x, y) in enumerate(KL.keys(variant)):
        B.place(f'SW{i + 1}', x, y, 0, 'F')
        B.text(kname, x, y - (2.6 if variant == 'alps' else 0), pcbnew.F_Fab, 0.8)
    # scanner on the bottom of the D-pad zone; FPC connector at the top edge, opening toward the body
    B.place('J1', 11.5, 4.3, 0, 'B')     # on the bottom side rot 0 puts the FPC opening toward y = 0
    B.place('U1', 6.3, 10.2, 0, 'B')
    B.place('U2', 16.8, 8.0, 90, 'B')
    B.pack(['C1', 'C2', 'R3', 'R4', 'R1', 'R2'], 11.5, 8.5, 'B', keepout=keepout)
    for i, (kname, r, c, x, y) in enumerate(KL.keys(variant)):
        if f'D{i + 1}' in B.fps:
            B.pack([f'D{i + 1}'], x, y + 2.3, 'B', rot=0, keepout=keepout)
    B.pack(['TP1', 'TP2', 'TP3', 'TP4'], 18.5, 14.0, 'B', keepout=keepout)
    left = B.unplaced()
    assert not left, left
    B.text('HackerSlide 810 keyboard ' + ('Alps SKSW' if variant == 'alps' else 'Keystone 5135 domes') + ' rev 0.1 DRAFT  CERN-OHL-S-2.0',
           KL.BOARD_W / 2 + 10, KL.BOARD_H - 1.5, pcbnew.B_SilkS, 0.8, mirror=True)
    # GND pour on both layers
    pts = [(0, 0), (KL.BOARD_W, 0), (KL.BOARD_W, KL.BOARD_H), (0, KL.BOARD_H)]
    B.zone('GND', pcbnew.B_Cu, pts, clearance=0.2)
    B.zone('GND', pcbnew.F_Cu, pts, clearance=0.2)
    path = B.save(os.path.join(bdir, name + '.kicad_pcb'))
    nl_sheets = None
    set_project_rules(path.replace('.kicad_pcb', '.kicad_pro'), RULES, CLASSES, PATTERNS)
    if do_route:
        print(route(path, passes=30, timeout=3000))
    return path


if __name__ == '__main__':
    print(build(sys.argv[1], sys.argv[2], '--route' in sys.argv))
