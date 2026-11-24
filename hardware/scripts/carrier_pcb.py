"""Place (and optionally autoroute) the carrier PCB.  Usage: carrier_pcb.py BOARD_DIR [--route]

Coordinates are KiCad board coordinates seen from the component (F) side.  In the device the carrier is
mounted F-side DOWN (components face the back shell, the bare B side faces the display), so this view is the
device seen from the back: the device's right edge is x = 0 here.  See docs/carrier-board.md, "Orientation".

Layout zones (mm):
  module   CM4-format module, landscape, x 16..71, y 13..53 (DF40 1.5 mm stack: nothing under the module)
  battery  x 71..121, y 4..64 (cell sits between carrier and back shell): no parts
  left edge (device right side): microSD, USB-C, 3.5 mm jack     top edge: buttons
  top strip: charger, boost, backlight, display/touch FPC (FPC passes through slot S1)
  bottom strip: codec, USB mux/hub, keyboard FPC (toward the slider), debug UART
"""
import math
import os
import sys

import pcbnew

from pcbgen import Board, route, set_project_rules

W, H = 122.0, 66.0
MX, MY = 19.5, 16.5           # module frame origin = CM4 mounting hole "0,0" (RPi CM4IO footprint frame)
BATT = (71.0, 4.3, 121.0, 64.3)
MODULE = (MX - 3.5, MY - 3.5, MX + 51.5, MY + 36.5)
SLOT = (52.0, 9.2, 72.0, 10.8)  # FPC pass-through slot for panel + touch flex

RULES = {'min_clearance': 0.09, 'min_track_width': 0.09, 'min_via_diameter': 0.45, 'min_through_hole_diameter': 0.2,
         'min_copper_edge_clearance': 0.25, 'min_hole_clearance': 0.2, 'min_hole_to_hole': 0.25,
         'min_via_annular_width': 0.1}
# Impedance numbers are ESTIMATES for a JLC 4-layer 1.0 mm stackup; TODO(verify) with the JLC impedance calculator.
CLASSES = [{'name': 'Default', 'clearance': 0.1, 'track_width': 0.1, 'via_diameter': 0.45, 'via_drill': 0.2},
           {'name': 'Power', 'clearance': 0.15, 'track_width': 0.5, 'via_diameter': 0.6, 'via_drill': 0.3},
           {'name': 'DSI', 'clearance': 0.15, 'track_width': 0.1, 'via_diameter': 0.45, 'via_drill': 0.2,
            'diff_pair_width': 0.1, 'diff_pair_gap': 0.12},
           {'name': 'USB', 'clearance': 0.15, 'track_width': 0.12, 'via_diameter': 0.45, 'via_drill': 0.2,
            'diff_pair_width': 0.12, 'diff_pair_gap': 0.12}]
PATTERNS = [('VBUS', 'Power'), ('VSYS', 'Power'), ('VBAT', 'Power'), ('BATT_P', 'Power'), ('+5V', 'Power'),
            ('PMID', 'Power'), ('CHG_SW', 'Power'), ('BOOST_SW', 'Power'), ('DSI_*', 'DSI'), ('USB*_D?', 'USB'),
            ('HUB_UP_D?', 'USB'), ('KB_USB_D?', 'USB')]


def module_xy(xr, yr):
    """RPi CM4IO footprint frame (holes at 0,0 / 33,0 / 0,-48 / 33,-48) -> board, module long axis along X."""
    return MX - yr, MY + xr


def build(bdir, do_route=False):
    B = Board(os.path.join(bdir, 'netlist.json'), layers=4, thickness=1.0)
    B.outline(0, 0, W, H, r=2.0, cutouts=[SLOT])
    # ---- module sockets + standoffs (exact CM4 geometry) ------------------------------------------
    for ref, xr in (('J1A', -0.46), ('J1B', 33.46)):
        x, y = module_xy(xr, -21.5)
        B.place(ref, x, y, -90, 'F')
    for i, (xr, yr) in enumerate(((0, 0), (33, 0), (0, -48), (33, -48))):
        x, y = module_xy(xr, yr)
        B.place(f'H{i + 1}', x, y, 0, 'F')
    keep = [MODULE, BATT, (SLOT[0] - 0.5, SLOT[1] - 0.5, SLOT[2] + 0.5, SLOT[3] + 0.5)]
    # ---- edge parts -------------------------------------------------------------------------------
    B.place('J7', 6.7, 9.5, 90, 'F')        # microSD, card inserts from the device's right side
    B.place('J2', 4.0, 27.0, -90, 'F')      # USB-C
    B.place('J6', 8.8, 44.0, 0, 'F')        # 3.5 mm jack
    B.place('SW1', 16.5, 1.8, 0, 'F')        # power (device top-right)
    B.place('SW2', 98.0, 1.8, 0, 'F')       # volume + (device top-left)
    B.place('SW3', 106.0, 1.8, 0, 'F')      # volume -
    B.place('J4', 61.0, 5.6, 180, 'F')      # panel FPC (flex comes through the slot)
    B.place('J5', 45.0, 5.6, 180, 'F')      # touch FPC
    B.place('J9', 40.0, 61.6, 0, 'F')       # keyboard FPC toward the slider (device bottom edge)
    B.place('J3', 64.0, 64.2, 0, 'F')       # battery leads (hand soldered)
    B.place('U10', 68.5, 59.5, 0, 'F')     # hall switch for the slider detent magnet
    # ---- clusters ---------------------------------------------------------------------------------
    B.pack(['U3'], 26.0, 6.0, keepout=keep)          # charger near USB-C
    B.pack(['L1', 'C11', 'C12', 'C13', 'C14', 'C10', 'C15', 'C16', 'C17', 'R12', 'R13', 'R14', 'TH1', 'R15', 'D1',
            'U2', 'R10', 'R11'], 26.0, 6.0, keepout=keep)
    B.pack(['U5'], 36.5, 6.0, keepout=keep)          # boost right above module 5 V pins (77-87)
    B.pack(['L2', 'C21', 'C22', 'C23', 'C24', 'C20', 'R17', 'R18', 'R19', 'R20'], 36.5, 6.0, keepout=keep)
    B.pack(['U4', 'RS1', 'C18', 'C19', 'R16', 'D3'], 60.0, 58.0, keepout=keep)   # gauge near battery leads
    B.pack(['U6', 'L3', 'D4', 'C42', 'C43', 'R42', 'R43', 'C40', 'C41', 'R40', 'R41'], 52.0, 3.5, keepout=keep)
    B.pack(['C30', 'R30', 'C31', 'C32', 'C33', 'C34', 'C35', 'C36'], 34.0, 11.5, keepout=keep)
    B.pack(['U7'], 22.0, 60.0, keepout=keep)         # codec next to the jack
    B.pack(['C50', 'C51', 'C52', 'C53', 'C54', 'C55', 'C56', 'C57', 'C58', 'C59', 'C60', 'C61', 'R44', 'R45', 'R46',
            'R47', 'R48'], 22.0, 60.0, keepout=keep)
    B.pack([f'R{n}' for n in range(50, 60)], 30.0, 57.0, keepout=keep)
    B.pack(['U8', 'C70'], 52.0, 58.0, keepout=keep)  # mux close to module USB pins
    B.pack(['U9', 'Y2', 'C71', 'C72', 'C73', 'C74', 'C75', 'R70'], 58.0, 61.0, keepout=keep)
    B.pack(['R71', 'R72', 'R73', 'C76', 'R31', 'JP1'], 48.0, 56.0, keepout=keep)
    B.pack(['J8', 'R33', 'R34', 'R35', 'R36'], 12.0, 60.0, keepout=keep)
    B.pack(['SW4', 'SW5', 'R32', 'D2'], 14.0, 54.0, keepout=keep)
    B.pack(['R80', 'R81', 'R82', 'R83', 'R84', 'R85', 'C80', 'C81'], 15.0, 9.0, keepout=keep)
    B.pack(['R86', 'R87'], 92.0, 2.0, keepout=keep)
    tps = [r for r in B.unplaced() if r.startswith('TP')]
    B.pack(tps, 30.0, 50.0, keepout=keep)
    left = B.unplaced()
    assert not left, left
    # ---- documentation layers ---------------------------------------------------------------------
    B.rect(*MODULE, pcbnew.F_Fab, 0.15)
    B.text('CM4-format module 55x40 (DF40 1.5 mm stack: keep clear)', (MODULE[0] + MODULE[2]) / 2, MY + 18, pcbnew.F_Fab, 1.0)
    B.rect(*BATT, pcbnew.F_Fab, 0.15)
    B.text('1S LiPo cell envelope 50x60 (no parts)', (BATT[0] + BATT[2]) / 2, (BATT[1] + BATT[3]) / 2, pcbnew.F_Fab, 1.0)
    B.text('HackerSlide 810 carrier rev 0.1 DRAFT - NEEDS HUMAN REVIEW', 96.0, 30.0, pcbnew.F_SilkS, 1.0)
    B.text('github.com/ruapotato/hackerslide  AGPL-3.0', 96.0, 33.0, pcbnew.F_SilkS, 0.8)
    # battery zone: no footprints (rule area)
    z = B.zone(None, pcbnew.F_Cu, [(BATT[0], BATT[1]), (BATT[2], BATT[1]), (BATT[2], BATT[3]), (BATT[0], BATT[3])], keepout=True)
    z.SetDoNotAllowFootprints(True)
    ls = pcbnew.LSET(); ls.AddLayer(pcbnew.F_Cu); z.SetLayerSet(ls)
    z.SetZoneName('battery_no_parts')
    # copper: GND plane on In1, GND pours on F/B, +5V/VSYS pours left to the router (none here)
    full = [(0, 0), (W, 0), (W, H), (0, H)]
    B.zone('GND', pcbnew.In1_Cu, full, clearance=0.15)
    B.zone('GND', pcbnew.B_Cu, full, clearance=0.15)
    B.zone('GND', pcbnew.F_Cu, full, clearance=0.15)
    path = B.save(os.path.join(bdir, 'carrier.kicad_pcb'))
    set_project_rules(path.replace('.kicad_pcb', '.kicad_pro'), RULES, CLASSES, PATTERNS)
    if do_route:
        print(route(path, passes=40, timeout=5400))
    return path


if __name__ == '__main__':
    print(build(sys.argv[1], '--route' in sys.argv))
