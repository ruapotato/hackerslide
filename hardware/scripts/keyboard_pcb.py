"""Place (and optionally autoroute) the keyboard PCB.  Usage: keyboard_pcb.py alps|dome BOARD_DIR [--route]

Stack: switches on the top (F) side; diodes, RP2040, flash, crystal and the FPC on the bottom (B) side, so
the top side stays flat for the top-plate PCB and keycaps (KeebDeck-style stack, see docs/keyboard.md).
"""
import os
import sys

import pcbnew

import kbd_layout as KL
from pcbgen import Board, route, set_project_rules

TOP_PLATE_HOLES = [(3.0, 3.0), (20.0, 3.0), (3.0, 28.0), (20.0, 28.0),
                   (KL.FIELD_X0 + KL.PITCH_X * 4, KL.FIELD_Y0 + KL.PITCH_Y * 1),
                   (KL.FIELD_X0 + KL.PITCH_X * 4, KL.FIELD_Y0 + KL.PITCH_Y * 3),
                   (KL.FIELD_X0 + KL.PITCH_X * 8, KL.FIELD_Y0 + KL.PITCH_Y * 1),
                   (KL.FIELD_X0 + KL.PITCH_X * 8, KL.FIELD_Y0 + KL.PITCH_Y * 3),
                   (KL.FIELD_X0 + KL.PITCH_X * 11, KL.FIELD_Y0 + KL.PITCH_Y * 1),
                   (KL.FIELD_X0 + KL.PITCH_X * 11, KL.FIELD_Y0 + KL.PITCH_Y * 3)]

RULES = {'min_clearance': 0.127, 'min_track_width': 0.127, 'min_via_diameter': 0.45, 'min_through_hole_diameter': 0.2,
         'min_copper_edge_clearance': 0.3, 'min_hole_clearance': 0.2, 'min_hole_to_hole': 0.25,
         'min_via_annular_width': 0.1}
CLASSES = [{'name': 'Default', 'clearance': 0.15, 'track_width': 0.15, 'via_diameter': 0.45, 'via_drill': 0.2},
           {'name': 'Power', 'clearance': 0.15, 'track_width': 0.3, 'via_diameter': 0.5, 'via_drill': 0.25},
           {'name': 'USB', 'clearance': 0.15, 'track_width': 0.2, 'via_diameter': 0.45, 'via_drill': 0.2,
            'diff_pair_width': 0.2, 'diff_pair_gap': 0.15}]
PATTERNS = [('+3V3', 'Power'), ('+1V1', 'Power'), ('GND', 'Power'), ('USB_D*', 'USB')]


def build(variant, bdir, do_route=False):
    name = 'keyboard' if variant == 'alps' else 'keyboard-5135'
    B = Board(os.path.join(bdir, 'netlist.json'), layers=2, thickness=0.8)
    B.outline(0, 0, KL.BOARD_W, KL.BOARD_H, r=1.5)
    keepout = [(x - 1.1, y - 1.1, x + 1.1, y + 1.1) for (x, y) in TOP_PLATE_HOLES]
    for i, (x, y) in enumerate(TOP_PLATE_HOLES):
        fp = pcbnew.FootprintLoad(os.path.join(os.path.dirname(__file__), '..', 'lib', 'hackerslide.pretty'),
                                  'MountingHole_M1.6_NPTH')
        fp.SetReference(f'H{i + 1}')
        fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
        fp.SetBoardOnly(True)
        B.b.Add(fp)
    # switches (top) and their diodes (bottom, just below the switch)
    for i, (kname, r, c, x, y) in enumerate(KL.keys(variant)):
        B.place(f'SW{i + 1}', x, y, 0, 'F')
        B.text(kname, x, y - (2.6 if variant == 'alps' else 0), pcbnew.F_Fab, 0.8)
    # scanner cluster on the bottom of the D-pad zone; FPC at the top edge (toward the hinge/body)
    B.place('J1', 11.5, 3.2, 180, 'B')
    B.pack(['U1'], 11.5, 15.0, 'B', keepout=keepout)
    B.pack(['U2'], 11.5, 25.0, 'B', keepout=keepout)
    for i, (kname, r, c, x, y) in enumerate(KL.keys(variant)):
        B.pack([f'D{i + 1}'], x, y + 2.3, 'B', rot=0, keepout=keepout)
    B.pack(['Y1', 'R1', 'C1', 'C2'], 5.0, 14.0, 'B', keepout=keepout)
    B.pack(['C21'], 11.5, 25.0, 'B', keepout=keepout)
    B.pack(['C10', 'C11', 'C12', 'C13', 'C14', 'C15', 'C16', 'C17', 'C18', 'C19', 'C20'], 11.5, 14.0, 'B', keepout=keepout)
    B.pack(['R2', 'R3', 'R4', 'R5', 'R6'], 17.0, 9.0, 'B', keepout=keepout)
    B.pack(['TP1', 'TP2', 'TP3', 'TP4'], 26.0, 15.5, 'B', keepout=keepout)
    left = B.unplaced()
    assert not left, left
    B.text('HackerSlide 810 keyboard ' + ('Alps SKSW' if variant == 'alps' else 'Keystone 5135 domes') + ' rev 0.1 DRAFT',
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
