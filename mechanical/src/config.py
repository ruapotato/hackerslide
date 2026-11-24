"""HackerSlide 810 enclosure: every dimension in one place (mm).

Coordinate system: X = device width (128, left->right seen from the screen), Y = device height (72, top edge
y=0 -> user edge y=72), Z = thickness (z=0 is the bottom of the keyboard tray, screen faces +Z).

Sources are noted per value: [ds] = datasheet/vendor page linked in docs/, [dec] = design decision record,
[est] = estimate/assumption to be checked on the fit mule.
"""

# ---------------------------------------------------------------- body / tray footprint
BODY_W = 128.0            # [dec] N810 footprint 128 x 72
BODY_H = 72.0
CORNER_R = 6.0            # [est] plan-view corner radius
WALL = 1.4                # [dec] FDM walls 1.2-1.6
FLOOR = 1.2               # [est] FDM floor/roof
TRAY_FLOOR = 1.0          # [est]

# ---------------------------------------------------------------- off-the-shelf parts (envelopes)
MODULE = dict(w=55.0, h=40.0, t=4.7, stack=1.5, mated=5.078,    # [ds] Core3566 datasheet ch.3 (text copied from the CM4
              soc_xy=(31.99, 16.98), soc_size=(14.0, 14.0))     # datasheet; LuckFox's drawing scales to ~4.5: TODO(verify)
                                                                # on a real module).  [est] SoC position from the CM4 drawing
# Focus LCDs E40RB-I-MW430-CB, landscape, its bottom (FPC) edge toward the device RIGHT.  [ds] spec p.3
PANEL = dict(w=98.10, h=58.26, t=4.25, aa_w=86.40, aa_h=51.84, lens_w=97.70, lens_h=57.86,
             fpc_end='right',
             tail_bulge=1.7,          # [ds] 1.5 mm max components on the folded tails + FPC and shield film [est]
             tft_bulge_len=15.0,      # [est] component area of the display tail, measured from the FPC edge
             tft_tail=(47.75, 30.33), # [ds] folded display tail: contact end from the FPC edge, centre from the long edge
             ctp_tail=(56.5, 15.4))   # [est] touch tail: 57.7 flat minus the fold; centre scaled off the drawing
CARRIER = dict(w=71.6, h=66.0, t=1.0, r=3.0)                         # hardware/scripts/carrier_pcb.py
# Battery: PKCELL LP785060 (Adafruit 328), 2500 mAh, the only stocked cell with a datasheet found on 2026-11-24.
# [ds] MAX 8.1 x 50.5 x 62.5 incl. protection board.  Max charge 1.5 A, max continuous discharge 1.5 A.
BATTERY = dict(w=50.5, h=62.5, t=8.1, swell=0.3)
BATTERY_LAYOUT = 'cutout'  # the carrier does not cover the cell (David, 2026-11-24)
PANEL_GAP = 1.9            # carrier display side -> panel back: room for the folded panel tails and J4/J5 (1.0 mm)

# ---------------------------------------------------------------- keyboard stack ([dec] 102 x 29 + D-pad)
KBD_PCB = dict(w=125.0, h=31.0, t=0.8, under_gap=1.2)            # under_gap: SOD-323 diodes on the bottom (1.1 max)
SWITCH_H = 0.6                                                   # [ds] Alps SKSWCFE010
KEYCAP = dict(flange_t=0.5, top_t=1.2, nub_h=0.3)                # nub: audit K1 (was 0.1)
PLATE_T = 0.8                                                    # top-plate PCB
KEY_CLEARANCE = 3.5        # [dec] 3-4 mm between top key row and the screen-side body edge when open

# ---------------------------------------------------------------- slider
RAIL = dict(w=2.0, h=2.4, clear=0.25, lip=1.0)   # [est] rails on the left/right sides, running in Y
SLIDE_GAP = 0.4                                  # [est] air gap between body underside and tray top
# Detents (no spring).  Sizes are parameters to tune on the fit mule (audit E3: 3 x 1 mm was probably too weak).
MAGNET_BODY = dict(d=6.0, t=1.0, clear=0.1)      # [est] N52 discs pressed into the back-shell floor from outside
MAGNET_TRAY = dict(d=6.0, t=2.0, clear=0.1)      # [est] N52 discs in the tray posts
MAGNET_HALL = dict(d=5.0, t=2.0, clear=0.1)      # [est] slider-closed sense magnet (audit A2), under carrier U10
SCREWS = dict(insert_d=3.2, insert_l=3.0, screw_d=2.2, boss_d=5.6)   # [est] M2 heat-set inserts (CNC Kitchen style)

# ---------------------------------------------------------------- derived stack (closed)
PLATE_RIM = 0.3            # tray rim above the top plate = keycap tops flush with the rim
TRAY_T = (TRAY_FLOOR + KBD_PCB['under_gap'] + KBD_PCB['t'] + SWITCH_H + KEYCAP['nub_h'] + KEYCAP['flange_t'] + 0.1
          + PLATE_T + PLATE_RIM)
Z_TRAY_TOP = TRAY_T
Z_BODY_BOTTOM = Z_TRAY_TOP + SLIDE_GAP
Z_BACK_IN = Z_BODY_BOTTOM + FLOOR                 # inside face of the removable back (tub floor)
BACK_TUB_H = RAIL['h'] + 0.6                      # back-shell tub wall height; its left/right sides carry the rail grooves
RAIL_INSET = RAIL['w'] + RAIL['clear']            # body narrows by this per side over the tub height
if BATTERY_LAYOUT == 'cutout':
    # The cell bay runs from the back-shell floor to the panel back.  The carrier hangs in the same height:
    # cavity (module, jack, inductors) + board + PANEL_GAP.
    BAY_H = BATTERY['t'] + BATTERY['swell']
    CAVITY = BAY_H - CARRIER['t'] - PANEL_GAP
else:                                             # 'under': cell stacked under the module (spec 3.7), for comparison
    CAVITY = MODULE['mated'] + 0.3 + BATTERY['t'] + BATTERY['swell']
    BAY_H = CAVITY + CARRIER['t'] + PANEL_GAP
THERMAL_GAP = CAVITY - MODULE['mated'] if BATTERY_LAYOUT == 'cutout' else 0.3   # SoC side of the module -> back shell:
assert THERMAL_GAP >= 0.2, THERMAL_GAP            # filled by a pad or copper shim of this thickness (audit E4)
Z_CARRIER_F = Z_BACK_IN + CAVITY                  # carrier F side (faces down)
Z_CARRIER_B = Z_CARRIER_F + CARRIER['t']
Z_PANEL_BOTTOM = Z_CARRIER_B + PANEL_GAP
Z_PANEL_TOP = Z_PANEL_BOTTOM + PANEL['t']
BEZEL_LIP = 0.8                                   # [est] front-shell roof over the lens edge (holds the panel)
Z_BODY_TOP = Z_PANEL_TOP + BEZEL_LIP
BODY_T = Z_BODY_TOP - Z_BODY_BOTTOM
TOTAL_T = Z_BODY_TOP

# ---------------------------------------------------------------- slide travel (open)
TRAVEL = KBD_PCB['h'] + KEY_CLEARANCE + WALL      # expose the keyboard PCB + clearance + tray end wall
OPEN_H = BODY_H + TRAVEL

# plan positions (device top view, mm from body top-left)
PANEL_XY = ((BODY_W - PANEL['w']) / 2, (BODY_H - PANEL['h']) / 2)
# The carrier's port edge sits 0.3 mm from the inner wall on the device right, so the USB-C, jack and microSD
# mouths reach the wall (audit E1).  The carrier is mounted F-side down, so its KiCad view is mirrored in X:
#   device_x = CARRIER_XY[0] + CARRIER['w'] - kicad_x,  device_y = CARRIER_XY[1] + kicad_y
CARRIER_XY = (BODY_W - WALL - 0.3 - CARRIER['w'], (BODY_H - CARRIER['h']) / 2)
MODULE_KICAD = (7.5, 12.0)    # module outline top-left in carrier KiCad coords (carrier_pcb.MODULE)
MODULE_ROT180 = True          # module turned 180 deg in the carrier frame (carrier_pcb.module_xy)
BATT_XY = (RAIL_INSET + WALL + 0.25, (BODY_H - BATTERY['h']) / 2)      # cell bay, device left
KBD_XY = ((BODY_W - KBD_PCB['w']) / 2, BODY_H - WALL - KBD_PCB['h'])   # keyboard PCB in the tray
# carrier features, KiCad coords (keep in step with hardware/scripts/carrier_pcb.py)
SCREW_KICAD = ((3.8, 20.0), (3.8, 46.0))          # HS1 / HS2: the shell bosses clamp the carrier here
HALL_KICAD = (41.0, 2.1)                          # U10
USB_KICAD_Y, JACK_KICAD_Y, SD_KICAD_Y = 33.0, 5.0, 58.6
BUTTON_KICAD_X = (34.0, 49.0, 57.0)               # power, volume +, volume -
KBD_FPC_KICAD = (31.5, 61.6)                      # J9 signal row; the 8-way cable is 4.5 mm wide
J4_KICAD, J5_KICAD = (61.7, 31.8), (69.2, 46.7)   # panel / touch connectors on the display side


def carrier_to_device(kx, ky):
    return CARRIER_XY[0] + CARRIER['w'] - kx, CARRIER_XY[1] + ky


SCREW_XY = [carrier_to_device(*p) for p in SCREW_KICAD]
BOSS_D = SCREWS['boss_d']

# Detents: ONE tray magnet per side.  It sits over body magnet A when closed and over body magnet B (= A + TRAVEL)
# when open; nothing is in between, so there is no false stop mid-travel (audit E2).
MAGNET_X = (7.0, BODY_W - 7.0)
MAGNET_Y_CLOSED = 30.0
MAGNET_Y_OPEN = MAGNET_Y_CLOSED + TRAVEL
assert MAGNET_Y_OPEN + MAGNET_BODY['d'] / 2 < BODY_H - WALL, MAGNET_Y_OPEN
HALL_XY = carrier_to_device(*HALL_KICAD)          # sense magnet position in the tray when CLOSED
# Keyboard cable: leaves J9 toward the device bottom, turns down through this slot in the back-shell floor, runs
# back under the body, makes the rolling loop in the tray's empty upper half and enters keyboard J1 (audit E5).
KBD_FPC_X = carrier_to_device(*KBD_FPC_KICAD)[0]
FPC_SLOT = dict(w=6.5, l=1.6, y=BODY_H - WALL - 1.4)   # slot centre y; width along X
FPC_LOOP_Y_CLOSED = 21.0                               # [est] loop apex (device y) with the slider closed

MODULE_XY = carrier_to_device(MODULE_KICAD[0] + MODULE['w'], MODULE_KICAD[1])        # module outline, device top-left
SOC_XY = ((MODULE['w'] - MODULE['soc_xy'][0], MODULE['h'] - MODULE['soc_xy'][1]) if MODULE_ROT180
          else MODULE['soc_xy'])                                                  # [est] SoC centre in the module outline
SECTION_X = MODULE_XY[0] + SOC_XY[0]              # render cross-section plane: through the (estimated) SoC position
