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

import carrier_cells as cells
from pcbgen import Board, finish_routing, route, save_scripted, set_project_rules

W, H = 71.6, 66.0
MX, MY = 11.0, 15.5           # module frame origin = CM4 mounting hole "0,0" (RPi CM4IO footprint frame)
MODULE = (MX - 3.5, MY - 3.5, MX + 51.5, MY + 36.5)
SCREWS = ((3.8, 20.0), (3.8, 46.0))                       # body screws HS1/HS2 (config.SCREW_KICAD)
HALL = (41.0, 2.1)                                        # U10; the tray sense magnet sits on this axis (config.HALL_KICAD)
U5_XY = (46.5, 59.6)                                      # 5 V boost block (carrier_cells.boost)
U3_XY = (65.4, 20.2)                                      # charger block (carrier_cells.charger)
CHG_SIGNALS = ('I2C_B_SDA', 'I2C_B_SCL', 'CHG_STAT', 'CHG_DM', 'CHG_DP', 'CHG_INT_N', 'CHG_ILIM', 'CHG_TS', 'CHG_QON_N')
J10_POS = (69.5, 5.1)                                     # battery header, pin 1 (+); pins 2, 3 at +2.5, +5.0 in y
PLUG = (49.0, 2.7, 62.9, 12.6)                            # kept free on F: mated plug and the wire bend (config.BATT_PLUG)
J4_POS, J5_POS = (61.7, 31.8), (69.2, 46.7)               # signal-pad rows of the panel / touch connectors (B side)

RULES = {'min_clearance': 0.09, 'min_track_width': 0.09, 'min_via_diameter': 0.45, 'min_through_hole_diameter': 0.2,
         'min_copper_edge_clearance': 0.25, 'min_hole_clearance': 0.2, 'min_hole_to_hole': 0.25,
         'min_via_annular_width': 0.1}
# Pair geometry from impedance.py (2-D field solution) for 0.0994 mm 3313 prepreg, er 4.1, over the In1 plane:
# DSI 0.10 / 0.15 = 100 ohm, USB 0.12 / 0.12 = 89 ohm.  The board has to be ordered with that prepreg
# (JLCPCB JLC04101H-3313, see bom/fab-orders.md); with 7628 prepreg (0.21 mm) these pairs would be 107 / 97 ohm.
CLASSES = [{'name': 'Default', 'clearance': 0.09, 'track_width': 0.1, 'via_diameter': 0.45, 'via_drill': 0.2},
           {'name': 'Power', 'clearance': 0.09, 'track_width': 0.5, 'via_diameter': 0.6, 'via_drill': 0.3},
           {'name': 'HV', 'clearance': 0.09, 'track_width': 0.3, 'via_diameter': 0.6, 'via_drill': 0.3},   # backlight: up to 38 V
           {'name': 'DSI', 'clearance': 0.09, 'track_width': 0.1, 'via_diameter': 0.45, 'via_drill': 0.2,
            'diff_pair_width': 0.1, 'diff_pair_gap': 0.15},
           {'name': 'USB', 'clearance': 0.09, 'track_width': 0.12, 'via_diameter': 0.45, 'via_drill': 0.2,
            'diff_pair_width': 0.12, 'diff_pair_gap': 0.12}]
PATTERNS = [('VBUS', 'Power'), ('VSYS', 'Power'), ('VSYS_LIM', 'Power'), ('VBAT', 'Power'), ('+5V', 'Power'), ('PMID', 'Power'),
            ('CHG_SW', 'Power'), ('BOOST_SW', 'Power'), ('BL_SW', 'HV'), ('LED_A', 'HV'),
            ('DSI_*', 'DSI'), ('USB_D?', 'USB')]


def module_xy(xr, yr):
    """RPi CM4IO footprint frame (holes at 0,0 / 33,0 / 0,-48 / 33,-48) -> board.  Module long axis along X, turned
    so that J1A (pins 1-100: power, SD, I2S, UART, GPIO) is on the bottom strip and J1B (USB, DSI) on the top.
    This is the audited placement rotated by 180 degrees about the module centre (a pure rotation, no mirror)."""
    return MX + 48.0 + yr, MY + 33.0 - xr


def build(bdir, do_route=False):
    B = Board(os.path.join(bdir, 'netlist.json'), layers=4, thickness=1.0)
    B.margin = 0.3                 # lanes for 0.1 mm tracks between neighbouring passives
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
    # Fan-out: an escape stub and a via for every used pin of the fine-pitch parts (ground pins too: their vias
    # land on the In1 ground plane).  Done right after each part is placed, so the passives packed afterwards
    # stay clear.  The router then connects vias; it does not thread between pads.
    # J1B and the 5 V end of J1A: three rows of vias.  The rest of J1A (GPIO, I2C, UART, SD, buttons): four rows, so
    # that three tracks instead of one fit between two vias of a row; with three rows the pins there walled each
    # other in.
    B.fanout('J1B', lengths=(0.9, 1.5, 2.1), width=0.1, skip=())
    B.fanout('J1A', lengths=(0.9, 1.5, 2.1), width=0.1, skip=(), where=lambda x, y: x > 41.5)
    B.fanout('J1A', lengths=(0.9, 1.5, 2.1, 2.7), width=0.1, skip=(), where=lambda x, y: x <= 41.5)

    # Display side.  The panel's folded tails need 1.9 mm of the 3.3 mm gap, so 0402 parts (up to 0.55 mm) and
    # test pads may sit under them; nothing taller is placed there.
    keep_b = []

    moved = []

    def pk(refs, x, y, region):
        """Pack near (x, y) on the component side; a part that does not fit goes to the same spot on the display
        side (0402 parts are 0.5 mm high, the gap behind the panel is 3.3 mm)."""
        for ref in refs:
            dbg = os.environ.pop('PLACE_DEBUG', None)     # pack() must raise here, not force the part in
            try:
                B.pack([ref], x, y, 'F', region=region, keepout=keep)
            except RuntimeError:
                moved.append(ref)
                B.pack([ref], x, y, 'B', region=region, keepout=keep_b)
            finally:
                if dbg:
                    os.environ['PLACE_DEBUG'] = dbg

    def PF(ref, x, y, rot=0, side='F', lens=(1.1, 1.8)):
        P(ref, x, y, rot, side)
        B.fanout(ref, lengths=lens, width=0.15, skip=())

    # ---- edge connectors (E1: mouths reach the 1.4 mm enclosure wall, whose inner face is 0.3 mm off the edge) ----
    P('J2', 2.6, 33.0, -90)          # USB-C, shell front 1.1 mm past the board edge
    P('J6', 0.6, 5.0, 0)             # 3.5 mm jack, collar 1.4 mm past the board edge
    P('J7', 8.1, 58.6, 90)           # microSD, card end 1.65 mm past the board edge (flush with the body)
    P('SW1', 34.0, 1.7, 180)        # power: plunger toward the top edge (A3)
    P('SW2', 49.0, 1.7, 180)        # volume +
    P('SW3', 57.0, 1.7, 180)        # volume -
    PF('J9', 31.5, 61.6, 0)          # keyboard FPC, opening toward the bottom edge (toward the slider)
    P('J8', 23.0, 62.6, 0)           # debug UART, side entry toward the bottom edge
    P('J10', *J10_POS, -90)          # battery connector (Molex 5268, through-hole): the plug comes in from the module side and
    keep.append(PLUG)                # lies over the top strip, which stays free of parts there (David 2026-11-25: plug, not solder)
    PF('J4', *J4_POS, 90, 'B')       # panel FPC: opening toward device-right, pin 1 toward the top (see module docstring)
    P('J5', *J5_POS, 90, 'B')        # touch FPC: its escape is laid by hand in cells.touch
    cells.touch(B)
    P('U10', *HALL, 0)               # slider hall switch, top strip: above the tray's upper half

    PF('U11', 18.4, 54.0, 0, lens=(0.9, 1.5))
    PF('U12', 18.4, 57.6, 0, lens=(0.9, 1.5))
    cells.sd_links(B)
    cells.dsi(B)                     # needs the fan-out vias of J1B and J4
    # ---- power: boost (bottom strip; the 5 V pins of J1A are at x 43..45, y 50.5) ----
    cells.boost(B, *U5_XY)
    pk(['C33', 'C34'], 47.0, 55.2, region=(41.8, 52.3, 56.5, 58.0))
    # GPIO_VREF (module pin 78): R30 and its two capacitors in one column with the three GPIO_VREF pads in line,
    # so the router has a single connection to make, from the pin's escape via to this column
    v = cells.Cell(B, 39.6, 54.9)
    v.two('C37', 0.0, 0.0, 'L'); v.two('C30', 0.0, 1.0, 'L'); v.two('R30', 0.0, 2.0, 'R')
    v.T('GPIO_VREF', [('C37', '1'), ('C30', '1'), ('R30', '2')], 0.2)
    v.T('GND', [('C37', '2'), ('C30', '2')], 0.2)
    v.gnd('C37', '2', 0.85, -0.15, w=0.2, d=0.45, drill=0.2)    # between the SD lanes on the display side
    pk(['C35', 'C36'], 42.5, 57.5, region=(36.0, 52.3, 56.5, 65.6))
    # ---- power: charger + gauge (left strip, next to the battery bay) ----
    cells.charger(B, *U3_XY)
    # second VSYS_LIM path on the display side, parallel to the In2 area (3 A): keep parts and vias out of it
    for vx in (64.9, 66.1, 67.3):                 # 1.2 mm apart: the ground plane keeps its webs between them
        B.via('VSYS_LIM', vx, 58.9, 0.6, 0.3)
        B.via('VSYS_LIM', vx - 0.2, 53.2, 0.6, 0.3)   # and again above, so both ends of the lower strap are tied to In2
    for vy in (46.3, 47.5, 48.7):                 # lower end of the upper strap (beside J5's body)
        B.via('VSYS_LIM', 64.75, vy, 0.6, 0.3)
    keep.append((64.2, 45.8, 65.3, 49.3)); keep.append((64.1, 52.6, 67.8, 53.8))
    keep_b.append((64.0, U3_XY[1] + 13.8, 68.4, 65.7))
    keep_b.append((52.0, 62.2, 68.4, 65.7)); keep_b.append((52.0, 60.0, 54.9, 65.7))
    B.fanout('U3', lengths=(0.9, 1.5), width=0.15, only=CHG_SIGNALS[:5])
    cells.gauge(B, 65.0, 9.0)
    # ---- USB-C side (right strip) ----
    cells.usb(B)
    # ---- power button diodes near SW1; hall sensor support ----
    pk(['D3', 'D7', 'D8', 'D9', 'R26', 'R27', 'TP15'], 34.0, 5.5, region=(30.5, 3.8, 40.5, 11.8))
    pk(['C76', 'R75'], HALL[0], 5.0, region=(38.0, 0.3, 45.0, 11.8))
    # ---- audio (top strip next to the jack) ----
    PF('U7', 19.5, 6.3, 0, lens=(1.0, 1.6, 2.2))
    # codec decoupling: on the display side straight behind the codec, each capacitor at the escape via of its pin
    # (the vias ring the part on the module side, so there the nearest free spot is 5-10 mm away); then a ground
    # via at each capacitor
    for ref, ax, ay in (('C50', 20.1, 10.3), ('C58', 21.2, 10.3), ('C59', 19.2, 10.3), ('C52', 23.5, 5.6),
                        ('C55', 23.5, 6.4), ('C56', 23.5, 4.6), ('C57', 21.1, 2.3), ('C63', 20.2, 2.3),
                        ('C53', 15.5, 5.5), ('C51', 15.5, 6.3), ('C64', 20.1, 11.2), ('C54', 24.8, 5.2)):
        B.pack([ref], ax, ay, 'B', region=(13.5, 0.4, 30.0, 11.9), keepout=keep_b)
        if ref != 'C58' and not any(B.gnd_via(ref, '2', dist=d_) for d_ in (0.75, 1.1, 1.5)):
            print('no room for a ground via at', ref)
    pk(['R44'], 24.0, 3.0, region=(14.0, 0.3, 30.3, 11.8))
    # HPGND joins ground at the jack and nowhere else: R49 beside the sleeve strap R60
    B.pack(['R49'], 13.6, 10.4, 'B', region=(9.0, 6.0, 19.0, 11.9), keepout=keep_b)
    B.gnd_via('R49', '2')
    pk(['R46', 'R47', 'R69', 'R60', 'R61', 'R62', 'R63', 'D10', 'D11', 'D12', 'C60', 'C61', 'C62', 'R45', 'R65', 'R48', 'R64'], 13.0, 10.8, region=(0.4, 0.3, 33.0, 11.8))
    # ---- I2S straps under the J1A I2S pins (x 32..37) ----
    # I2S straps and their test pads: display side, under the module just north of J1A.  Both alternatives start at
    # module pins in x 32..37 and all five signals go on to the codec in the top strip, so nothing has to cross J1A
    # twice (on the bottom strip, where they were, they did).
    B.pack([f'R{n}' for n in range(50, 60)], 34.5, 42.5, 'B', region=(28.0, 37.5, 42.0, 44.0), keepout=keep_b)
    B.pack(['TP30', 'TP31', 'TP32', 'TP33'], 34.5, 39.0, 'B', region=(26.0, 33.0, 44.0, 41.0), keepout=keep_b)
    # ---- backlight (top strip) ----
    # ---- backlight: left strip below the charger, next to the panel connector's LED pins and on the VSYS_LIM area;
    # 6 mm from the DSI vias at J4 (it used to be in the top strip, where the battery plug now lies)
    # Everything of it stays above y 45: the touch connector J5 is on the display side at y 44-50, and the module
    # side is the only layer on which its signals can cross this strip (In2 and the display side are VSYS_LIM copper)
    cells.backlight(B, 66.5, 38.4)
    lx, ly = B.pad_xy('L3', '1'); rx, _ = B.pad_xy('L3', '2')
    z = B.zone(None, pcbnew.F_Cu, [(min(lx, rx) + 0.75, ly - 1.7), (max(lx, rx) - 0.75, ly - 1.7), (max(lx, rx) - 0.75, ly + 1.7),
                                  (min(lx, rx) + 0.75, ly + 1.7)], keepout=True)
    z.SetDoNotAllowTracks(True); z.SetZoneName('no_tracks_under_L3')     # nothing between the inductor's pads
    pk(['TP20'], 64.5, 47.5, region=(62.8, 36.3, 71.3, 58.0))
    pk(['R25', 'R67'], 67.0, 36.0, region=(62.8, 33.0, 71.3, 58.0))
    pk(['R86', 'R87'], 58.5, 5.0, region=(45.0, 3.8, 61.8, 11.8))
    # ---- bottom strip, right part: microSD and debug UART ----
    pk(['R33', 'R34', 'R35', 'R36'], 23.0, 57.5, region=(19.9, 52.3, 26.6, 59.0))
    pk(['C80', 'C81'], 14.0, 52.9, region=(9.0, 52.2, 27.0, 56.0))
    pk(['R80', 'R81', 'R82', 'R83', 'R84', 'R85'], 20.0, 60.0, region=(15.3, 52.3, 27.0, 65.6))
    pk(['R71', 'R72', 'R73', 'R74', 'C77'], 31.5, 58.0, region=(27.0, 52.3, 35.9, 60.6))
    # ---- bottom strip, left part: boot/reset, LED, test points ----
    P('SW4', 60.0, 55.0, 0)
    P('SW5', 60.0, 60.3, 0)
    # each switch has two pads per terminal, joined inside the part; KiCad wants them joined on the board as well.
    # The link goes round the locating hole.  R37 sits right at the reset switch.
    for sw, net in (('SW4', 'NRPIBOOT'), ('SW5', 'RST_SW_N')):
        (ax, ay), (bx, by) = sorted((pcbnew.ToMM(p.GetPosition().x), pcbnew.ToMM(p.GetPosition().y))
                                    for p in B.fps[sw].Pads() if p.GetNumber() == '1')
        B.track(net, [(ax, ay), (ax, ay - 0.9), (bx, by - 0.9), (bx, by)], 0.2, pcbnew.F_Cu)
    v = cells.Cell(B, 63.45, 60.9)
    v.two('R37', 0.0, 0.0, 'U')
    v.T('RST_SW_N', [(61.8 - 63.45, 59.58 - 60.9), (0.0, 59.58 - 60.9), ('R37', '1')], 0.2)
    B.pack(['TP4', 'TP11', 'TP12', 'TP5', 'TP13', 'TP16', 'TP21', 'TP36', 'TP37'], 44.0, 28.0, 'B', region=(30.0, 20.0, 56.0, 38.0), keepout=keep_b)   # test points, display side, clear of the panel tails
    B.pack(['TP34', 'TP35'], 23.0, 57.0, 'B', region=(14.0, 52.3, 30.0, 65.6), keepout=keep_b)   # UART pads behind J8
    # touch I2C pull-ups: display side, where the hand-laid escape of J5 ends (not inside the fenced left strip)
    B.pack(['R40', 'R41'], 62.5, 53.5, 'B', region=(56.0, 52.4, 63.7, 58.0), keepout=keep_b)
    pk(['R32', 'D2', 'D13', 'R92', 'R31', 'C40', 'C41'], 63.0, 63.5, region=(56.8, 52.3, 71.3, 65.6))
    rest = B.unplaced()
    pk(rest, 66.0, 58.0, region=(56.8, 46.0, 71.3, 65.6))
    left = B.unplaced()
    assert not left, left
    # ground vias right at the parts whose ground the pour and the router would otherwise bring from afar:
    # the jack's ESD diodes, the SD and panel supply capacitors, the hall sensor's capacitor, the USB ESD part
    for ref, pad in (('D10', '2'), ('D11', '2'), ('D12', '2'), ('C80', '2'), ('C81', '2'), ('C41', '2'), ('C40', '2'),
                     ('C76', '2'), ('C33', '2'), ('C34', '2'), ('C35', '2'), ('C36', '2')):
        if not any(B.gnd_via(ref, pad, dist=d_) for d_ in (0.75, 1.1, 1.5, 2.0)):
            print('no room for a ground via at', ref)
    print('on the display side for lack of room:', ' '.join(moved))
    # ---- documentation layers ----
    B.rect(*MODULE, pcbnew.F_Fab, 0.15)
    B.text('CM4-format module 55x40 (DF40 1.5 mm stack: keep clear)', (MODULE[0] + MODULE[2]) / 2, MY + 16.5, pcbnew.F_Fab, 1.0)
    B.text('HackerSlide 810 carrier rev 0.1', 35.0, 22.0, pcbnew.F_SilkS, 1.0)
    B.text('github.com/ruapotato/hackerslide  CERN-OHL-S-2.0', 35.0, 44.0, pcbnew.F_SilkS, 0.8)
    for txt, k in (('+', 0), ('T', 1), ('-', 2)):
        B.text(txt, 62.2, J10_POS[1] + 2.5 * k, pcbnew.F_SilkS, 0.8)
    # no copper between the DF40 pad rows (Hirose DF40 catalogue, land pattern note 3; audit M6)
    for xr in (-0.46, 33.46):
        cx, cy = module_xy(xr, -21.5)
        z = B.zone(None, pcbnew.F_Cu, [(cx - 10.2, cy - 1.1), (cx + 10.2, cy - 1.1), (cx + 10.2, cy + 1.1), (cx - 10.2, cy + 1.1)],
                   keepout=True)
        z.SetDoNotAllowTracks(True); z.SetDoNotAllowVias(True); z.SetDoNotAllowCopperPour(True)
        z.SetZoneName('df40_no_copper')
    # copper: GND plane on In1 and GND pours on F/B.  High-current paths get their own areas (priority above the
    # pours) so they are not left to thin autorouted tracks; the router or a human drops the vias into them.
    def area(net, layer, x0, y0, x1, y1, prio=2):
        return B.zone(net, layer, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], priority=prio, clearance=0.2)
    # VBUS on In2: USB-C -> under the module below the J1B fan-out vias -> up past the module corner -> top strip
    # -> down into the charger block.  (The row of J1B vias would cut a straight strip into slivers.)
    ox, oy = U3_XY
    # Widths are set by power_paths.py: wherever vias cross the area it must stay at least 1.5 mm wide.
    for box in ((4.5, 16.2, 12.5, 36.2), (1.3, 34.9, 12.5, 39.9), (4.5, 19.2, 52.5, 23.4), (48.2, 10.6, 52.5, 23.4), (48.2, 10.6, ox + 4.0, 13.4),
                (ox + 1.4, 10.6, ox + 4.0, oy - 2.6)):
        area('VBUS', pcbnew.In2_Cu, *box)
    # VBAT on the display side: battery connector pin 1 -> down the left of the charger -> its BAT vias and C17
    jx, jy = J10_POS
    area('VBAT', pcbnew.B_Cu, ox - 3.3, jy - 1.2, jx + 1.0, jy + 1.1)
    area('VBAT', pcbnew.B_Cu, ox - 3.3, jy - 1.2, ox - 1.7, oy + 4.9)
    area('VBAT', pcbnew.B_Cu, ox - 3.3, oy + 2.6, ox - 1.0, oy + 4.9)
    area('VSYS_LIM', pcbnew.In2_Cu, ox - 1.0, oy + 11.4, 71.3, 65.7)   # limiter -> down the left strip -> along the bottom strip -> boost
    area('VSYS_LIM', pcbnew.In2_Cu, 41.0, 58.0, 71.3, 65.7)
    area('VSYS_LIM', pcbnew.B_Cu, ox - 1.2, oy + 14.0, 71.2, oy + 16.0)       # display side: from the fuse's OUT vias ...
    # ... down the left strip (four vias into In2 on the way).  The strip is open for 1.8 mm just below the touch
    # connector J5: its signals leave on the display side through that gap (In2 carries the current alone there,
    # 6.9 mm wide; the module side above J5 belongs to the backlight parts)
    area('VSYS_LIM', pcbnew.B_Cu, ox - 1.2, oy + 14.0, ox + 2.8, 50.1)
    area('VSYS_LIM', pcbnew.B_Cu, ox - 1.2, 51.9, ox + 2.8, 65.65)
    area('VSYS_LIM', pcbnew.B_Cu, 52.2, 62.4, ox + 2.8, 65.65)                # ... along the bottom edge ...
    area('VSYS_LIM', pcbnew.B_Cu, 52.2, 60.2, 54.7, 65.65)                    # ... to the boost's three VSYS_LIM vias
    bx, by = U5_XY
    area('+5V', pcbnew.F_Cu, 42.2, 50.2, 45.6, 53.2)             # ties the stubs of module pins 77-87 together
    area('+5V', pcbnew.B_Cu, bx - 5.9, 50.6, bx - 1.6, by - 1.9)  # boost output vias -> fan-out vias of pins 77-87
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
    save_scripted(path)             # what is on the board now is scripted; the router may only take up its own work
    if do_route:
        # gridroute.py on F / In2 / B; In1 is the ground plane, so a via anywhere reaches ground.
        # DSI and USB are already in as scripted pairs (carrier_cells); the router does ordinary signals only.
        import subprocess
        gr = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gridroute.sh')
        # (gridroute's --fine option, a second attempt inside the same run, was tried here and did not do better)
        for extra in (['--width', '0.13', '--clearance', '0.15'], ['--width', '0.1', '--clearance', '0.13', '--stitch'],
                      ['--width', '0.1', '--clearance', '0.12', '--power-width', '0.25', '--stitch']):
            subprocess.run([gr, os.path.abspath(bdir), 'carrier', '--layers', 'F.Cu,In2.Cu,B.Cu', '--power-width', '0.4'] + extra, check=True)
        # (a later --power-width overrides the 0.4: the last passes let short power links neck down)
        set_project_rules(path.replace('.kicad_pcb', '.kicad_pro'), RULES, CLASSES, PATTERNS)
    return path


def repair(bdir):
    board = os.path.join(os.path.abspath(bdir), 'carrier.kicad_pcb')
    finish_routing(board, ['--layers', 'F.Cu,In2.Cu,B.Cu', '--width', '0.1', '--power-width', '0.25', '--stitch'], (0.15, 0.12))
    set_project_rules(board.replace('.kicad_pcb', '.kicad_pro'), RULES, CLASSES, PATTERNS)


if __name__ == '__main__':
    if '--repair' in sys.argv:
        repair(sys.argv[1])
    else:
        print(build(sys.argv[1], '--route' in sys.argv))
        if '--route' in sys.argv:
            repair(sys.argv[1])
