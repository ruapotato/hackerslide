"""Place (and optionally autoroute) the carrier PCB.  Usage: carrier_pcb.py BOARD_DIR [--route]

Revised after the 2026-11-24 audit: the carrier no longer covers the battery (David, 2026-11-24: "carrier cut out
around the battery"), edge connectors reach the enclosure wall (E1), power parts are placed by hand next to their
ICs (audit "Placement"), and the display connectors sit on the display side where the folded panel tails land (E6).

Coordinates are KiCad board coordinates seen from the component (F) side.  In the device the carrier is mounted
F-side DOWN (components face the back shell, the B side faces the display), so this view is the device seen from
the back: board x = 0 is the device's RIGHT edge, board y = 0 is toward the device's top edge.
  device_x = 126.3 - board_x      device_y = 3.0 + board_y      (mechanical/src/config.py CARRIER_XY)

Zones (mm):
  module      x 7.5..62.5, y 12..52   CM4-format module on 1.5 mm DF40 stack: no parts under it on F
  right strip x 0..7.5                USB-C, body screws HS1/HS2 (the shell bosses clamp the board there)
  top strip   y 0..12                 3.5 mm jack + codec | backlight | battery connector; buttons and hall switch on the edge
  left strip  x 62.5..71.6            charger, fuel gauge (next to the battery bay, which starts at x = 71.9)
  bottom strip y 52..66               microSD, debug UART, keyboard FPC (toward the slider), I2S straps, 5 V boost, test points
  B side      J4 (panel) and J5 (touch) only: the panel tails fold behind the panel and plug in from device-right
"""
import os
import sys

import pcbnew

from pcbgen import Board, route, set_project_rules

W, H = 71.6, 66.0
MX, MY = 11.0, 15.5           # module frame origin = CM4 mounting hole "0,0" (RPi CM4IO footprint frame)
MODULE = (MX - 3.5, MY - 3.5, MX + 51.5, MY + 36.5)
SCREWS = ((3.8, 20.0), (3.8, 46.0))                       # body screws HS1/HS2 (config.SCREW_KICAD)
HALL = (41.0, 2.1)                                        # U10; the tray sense magnet sits on this axis (config.HALL_KICAD)
J4_POS, J5_POS = (61.7, 31.8), (69.2, 46.7)               # signal-pad rows of the panel / touch connectors (B side)

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
PATTERNS = [('VBUS', 'Power'), ('VSYS', 'Power'), ('VBAT', 'Power'), ('+5V', 'Power'), ('PMID', 'Power'),
            ('CHG_SW', 'Power'), ('BOOST_SW', 'Power'), ('BL_SW', 'Power'), ('LED_A', 'Power'),
            ('DSI_*', 'DSI'), ('USB_D?', 'USB')]


def module_xy(xr, yr):
    """RPi CM4IO footprint frame (holes at 0,0 / 33,0 / 0,-48 / 33,-48) -> board.  Module long axis along X, turned
    so that J1A (pins 1-100: power, SD, I2S, UART, GPIO) is on the bottom strip and J1B (USB, DSI) on the top.
    This is the audited placement rotated by 180 degrees about the module centre (a pure rotation, no mirror)."""
    return MX + 48.0 + yr, MY + 33.0 - xr


def build(bdir, do_route=False):
    B = Board(os.path.join(bdir, 'netlist.json'), layers=4, thickness=1.0)
    B.outline(0, 0, W, H, r=3.0)    # 3 mm corners clear the enclosure's inner corner radius (config.CARRIER['r'])
    P = B.place
    # ---- module sockets + spacers (exact CM4 geometry, verified in the audit against the CM4IO footprint) ----
    for ref, xr in (('J1A', -0.46), ('J1B', 33.46)):
        P(ref, *module_xy(xr, -21.5), 90, 'F')
    for i, (xr, yr) in enumerate(((0, 0), (33, 0), (0, -48), (33, -48))):
        P(f'H{i + 1}', *module_xy(xr, yr), 0, 'F')
    for i, (x, y) in enumerate(SCREWS):
        P(f'HS{i + 1}', x, y, 0, 'F')
    keep = [MODULE] + [(x - 3.0, y - 3.0, x + 3.0, y + 3.0) for (x, y) in SCREWS]

    # ---- edge connectors (E1: mouths reach the 1.4 mm enclosure wall, whose inner face is 0.3 mm off the edge) ----
    P('J2', 2.6, 33.0, -90)          # USB-C, shell front 1.1 mm past the board edge
    P('J6', 0.6, 5.0, 0)             # 3.5 mm jack, collar 1.4 mm past the board edge
    P('J7', 8.1, 58.6, 90)           # microSD, card end 1.65 mm past the board edge (flush with the body)
    P('SW1', 34.0, 1.7, 180)        # power: plunger toward the top edge (A3)
    P('SW2', 49.0, 1.7, 180)        # volume +
    P('SW3', 57.0, 1.7, 180)        # volume -
    P('J9', 31.5, 61.6, 0)           # keyboard FPC, opening toward the bottom edge (toward the slider)
    P('J8', 23.0, 62.6, 0)           # debug UART, side entry toward the bottom edge
    P('J10', 65.8, 5.4, 90)          # battery connector, opening toward the battery bay
    P('J3', 64.6, 54.2, 0)           # alternative battery solder pads
    P('J4', *J4_POS, 90, 'B')        # panel FPC: opening toward device-right, pin 1 toward the top (see module docstring)
    P('J5', *J5_POS, 90, 'B')        # touch FPC
    P('U10', *HALL, 0)               # slider hall switch, top strip: above the tray's upper half

    # ---- power: boost (bottom strip; the 5 V pins of J1A are at x 43..45, y 50.5) ----
    P('U5', 46.5, 59.0, 0)
    P('L2', 52.2, 59.0, 90)
    B.pack(['C22', 'C23', 'C24'], 44.0, 53.2, region=(42.6, 52.3, 56.5, 56.8), keepout=keep)
    B.pack(['C21'], 52.0, 63.5, region=(41.8, 52.3, 56.5, 65.6), keepout=keep)
    B.pack(['C33', 'C34'], 47.0, 55.2, region=(41.8, 52.3, 56.5, 58.0), keepout=keep)
    B.pack(['R18', 'R19', 'C26', 'C20', 'R17', 'R23', 'R24', 'R20'], 44.5, 63.5,
           region=(41.8, 56.8, 56.5, 65.6), keepout=keep)
    B.pack(['C35', 'C36', 'C30', 'C37', 'R30'], 42.5, 57.5, region=(36.0, 52.3, 56.5, 65.6), keepout=keep)
    # ---- power: charger + gauge (left strip, next to the battery bay) ----
    P('U3', 67.0, 15.0, 0)
    P('L1', 67.0, 21.3, 0)
    B.pack(['C11', 'C12', 'C13', 'C14', 'C10', 'C15', 'C16', 'C17'], 67.0, 18.0, region=(62.8, 9.8, 71.3, 31.0), keepout=keep)
    B.pack(['R12', 'R13', 'R14', 'R25', 'R28', 'R29', 'R21', 'R22', 'R15', 'D1'], 67.0, 29.0, region=(62.8, 9.8, 71.3, 40.0), keepout=keep)
    P('U4', 67.0, 41.5, 0)
    B.pack(['C19', 'R16', 'TH1', 'TP3', 'TP7', 'TP8', 'TP2'], 67.0, 44.0, region=(62.8, 36.0, 71.3, 65.6), keepout=keep)
    # ---- USB-C side (right strip) ----
    P('U2', 3.8, 25.4, 90)
    B.pack(['D5', 'R10', 'R11', 'C25', 'TP1'], 3.8, 40.5, region=(0.4, 12.2, 7.3, 43.0), keepout=keep)
    # ---- power button diodes near SW1; hall sensor support ----
    B.pack(['D3', 'D7', 'D8', 'R26', 'R27', 'TP15'], 34.0, 5.5, region=(30.5, 3.8, 40.5, 11.8), keepout=keep)
    B.pack(['C76', 'R75'], HALL[0], 5.0, region=(38.0, 0.3, 45.0, 11.8), keepout=keep)
    # ---- audio (top strip next to the jack) ----
    P('U7', 19.5, 6.3, 0)
    B.pack(['C58', 'C59', 'C64', 'C53', 'C50', 'C51', 'C52', 'C54', 'C55', 'C56', 'C57', 'C63', 'R44'], 19.5, 6.3,
           region=(14.0, 0.3, 30.3, 11.8), keepout=keep)
    B.pack(['R46', 'R47', 'R49', 'R60', 'R61', 'R62', 'R63', 'D10', 'D11', 'D12', 'C60', 'C61', 'C62', 'R45', 'R65', 'R48', 'R64'],
           13.0, 10.8, region=(0.4, 0.3, 30.3, 11.8), keepout=keep)
    # ---- I2S straps under the J1A I2S pins (x 32..37) ----
    B.pack(['TP30', 'TP31', 'TP32', 'TP33'], 31.5, 54.0, region=(26.8, 52.3, 36.0, 58.6), keepout=keep)
    B.pack([f'R{n}' for n in range(50, 60)], 38.5, 53.0, region=(36.0, 52.3, 42.4, 65.6), keepout=keep)
    # ---- backlight (top strip) ----
    P('U6', 49.0, 9.8, 0)
    P('L3', 54.2, 7.8, 0)
    B.pack(['D4', 'C42', 'C43', 'R42', 'R43', 'TP20'], 49.0, 6.0, region=(45.0, 3.8, 61.8, 11.8), keepout=keep)
    B.pack(['R86', 'R87'], 58.5, 5.0, region=(45.0, 3.8, 61.8, 11.8), keepout=keep)
    # ---- bottom strip, right part: microSD and debug UART ----
    P('U11', 16.2, 54.0, 0)
    P('U12', 16.2, 57.2, 0)
    B.pack(['R33', 'R34', 'R35', 'R36'], 23.0, 57.5, region=(19.9, 52.3, 26.6, 59.0), keepout=keep)
    B.pack(['R80', 'R81', 'R82', 'R83', 'R84', 'R85', 'C80', 'C81'], 17.5, 60.5, region=(15.3, 52.3, 26.6, 65.6), keepout=keep)
    B.pack(['R71', 'R72', 'R73', 'R74', 'C77'], 31.5, 59.3, region=(27.0, 56.5, 35.8, 60.6), keepout=keep)
    # ---- bottom strip, left part: boot/reset, LED, test points ----
    P('SW4', 60.0, 55.0, 0)
    P('SW5', 60.0, 60.3, 0)
    B.pack(['TP4', 'TP6', 'TP9'], 48.0, 61.0, 'B', region=(41.0, 54.0, 56.5, 65.6))     # boost test points, display side
    B.pack(['R37', 'TP13', 'R32', 'D2', 'R31', 'TP16', 'R40', 'R41', 'C40', 'C41', 'TP21'], 63.0, 63.5, region=(56.8, 52.3, 71.3, 65.6), keepout=keep)
    rest = B.unplaced()
    B.pack(rest, 66.0, 58.0, region=(56.8, 46.0, 71.3, 65.6), keepout=keep)
    left = B.unplaced()
    assert not left, left
    # ---- documentation layers ----
    B.rect(*MODULE, pcbnew.F_Fab, 0.15)
    B.text('CM4-format module 55x40 (DF40 1.5 mm stack: keep clear)', (MODULE[0] + MODULE[2]) / 2, MY + 16.5, pcbnew.F_Fab, 1.0)
    B.text('HackerSlide 810 carrier rev 0.1 DRAFT', 35.0, 22.0, pcbnew.F_SilkS, 1.0)
    B.text('NEEDS HUMAN REVIEW', 35.0, 24.0, pcbnew.F_SilkS, 1.0)
    B.text('github.com/ruapotato/hackerslide  CERN-OHL-S-2.0', 35.0, 44.0, pcbnew.F_SilkS, 0.8)
    B.text('BATT +', 68.3, 8.3, pcbnew.F_SilkS, 0.7)
    # no copper between the DF40 pad rows (Hirose DF40 catalogue, land pattern note 3; audit M6)
    for xr in (-0.46, 33.46):
        cx, cy = module_xy(xr, -21.5)
        z = B.zone(None, pcbnew.F_Cu, [(cx - 10.2, cy - 1.1), (cx + 10.2, cy - 1.1), (cx + 10.2, cy + 1.1), (cx - 10.2, cy + 1.1)],
                   keepout=True)
        z.SetDoNotAllowTracks(True); z.SetDoNotAllowVias(True); z.SetDoNotAllowCopperPour(True)
        z.SetZoneName('df40_no_copper')
    # copper: GND plane on In1, GND pours on F/B; power nets are routed (In2 is the power/signal layer)
    full = [(0, 0), (W, 0), (W, H), (0, H)]
    B.zone('GND', pcbnew.In1_Cu, full, clearance=0.15)
    B.zone('GND', pcbnew.B_Cu, full, clearance=0.15)
    B.zone('GND', pcbnew.F_Cu, full, clearance=0.15)
    path = B.save(os.path.join(bdir, 'carrier.kicad_pcb'))
    set_project_rules(path.replace('.kicad_pcb', '.kicad_pro'), RULES, CLASSES, PATTERNS)
    # The Wuerth WA-SMSI footprint is a solder ring around its own non-plated hole: not a clearance fault.
    open(path.replace('.kicad_pcb', '.kicad_dru'), 'w').write(
        '(version 1)\n(rule "wuerth_spacer_ring"\n  (condition "A.memberOfFootprint(\'H?\') && B.memberOfFootprint(\'H?\')")\n'
        '  (constraint hole_clearance (min 0mm)))\n')
    if do_route:
        print(route(path, passes=40, timeout=5400))
    return path


if __name__ == '__main__':
    print(build(sys.argv[1], '--route' in sys.argv))
