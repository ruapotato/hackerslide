"""HackerSlide 810 enclosure: every dimension in one place (mm).

Coordinate system: X = device width (128, left->right seen from the screen), Y = device height (72, top edge
y=0 -> user edge y=72), Z = thickness (z=0 is the bottom of the keyboard tray, screen faces +Z).

Sources are noted per value: [ds] = datasheet/vendor page linked in docs/, [dec] = design decision record,
[est] = estimate/assumption to be checked on the fit mule.
"""

# ---------------------------------------------------------------- body / tray footprint
BODY_W = 131.5            # [dec] David 2026-11-27: 3.5 mm wider than the N810's 128, on the battery side, for the 54 mm Jauch pack
SHIFT_X = BODY_W - 128.0  # the panel, carrier and keyboard keep their places relative to the right edge
BODY_H = 74.0            # [dec] David 2026-11-25: 2 mm longer than the N810's 72, for the battery leads (see BATT_XY)
CORNER_R = 6.0            # [est] plan-view corner radius
WALL = 1.4                # [dec] FDM walls 1.2-1.6
FLOOR = 1.2               # [est] FDM floor/roof
TRAY_FLOOR = 0.0          # the keyboard PCB is the tray floor (David, 2026-11-24); the printed tray is a frame

N810 = dict(w=128.0, h=72.0, t=14.0)   # Nokia N810 envelope, reference only (spec 2026-11-20, target dimensions table)
LIBREM5 = dict(w=152.0, h=74.0, t=15.0)  # Purism Librem 5, reference only (docs.puri.sm hardware specs, read 2026-11-24)

# ---------------------------------------------------------------- off-the-shelf parts (envelopes)
# Heights and the SoC position are measured on LuckFox's own STEP model (core3566_v1_2.stp, files.luckfox.com), not
# the datasheet text (which repeats the CM4's 4.7 / 5.078 mm): PCB 1.2, tallest top part (an inductor) 1.8, SoC 0.9.
# TODO(verify) with calipers on a real module; the datasheet gives the SoC as 0.7 +-0.11.
MODULE = dict(w=55.0, h=40.0, t=4.09, stack=1.5, mated=4.50,    # mated = carrier surface -> tallest part
              soc_top=3.60,                                     # carrier surface -> SoC lid (1.5 + 1.2 + 0.9)
              soc_kicad=(34.28, 35.04),                         # SoC centre in carrier KiCad coordinates
              soc_size=(14.0, 14.0))                            # pad size; the package is 15 x 15, turned 45 degrees
# Focus LCDs E40RB-I-MW430-CB, landscape, its bottom (FPC) edge toward the device RIGHT.  [ds] spec p.3
PANEL = dict(w=98.10, h=58.26, t=4.25, aa_w=86.40, aa_h=51.84, lens_w=97.70, lens_h=57.86,
             fpc_end='right',
             tail_bulge=1.7,          # [ds] 1.5 mm max components on the folded tails + FPC and shield film [est]
             tft_bulge_len=15.0,      # [est] component area of the display tail, measured from the FPC edge
             tft_tail=(47.75, 30.33), # [ds] folded display tail: contact end from the FPC edge, centre from the long edge
             ctp_tail=(56.5, 15.4))   # [est] touch tail: 57.7 flat minus the fold; centre scaled off the drawing
CARRIER = dict(w=71.6, h=66.0, t=1.0, r=3.0)                         # hardware/scripts/carrier_pcb.py
# Battery: Jauch LP675365JU (DigiKey, Jauch no. 246522), chosen by David 2026-11-27 after the BAK pack went end-of-life:
# 1S1P with protection, 2800 mAh min / 3000 typ, 2 A max discharge and charge (limited by its 26 AWG leads), no
# thermistor.  [ds] rev 1.3 (12/2024): max 54.0 x 68.0 mm, 6.9 mm thick as delivered and 7.4 mm after cycling; two
# 70 mm leads leave the middle of one 54 mm edge.
BATTERY = dict(w=54.0, h=68.0, t=7.4, swell=0.3)
BATTERY_LAYOUT = 'cutout'  # the carrier does not cover the cell (David, 2026-11-24)
# Carrier display side -> panel back.  The folded display tail carries parts (PANEL['tail_bulge']) in a strip
# 15 mm deep along the panel's FPC edge; in carrier KiCad coordinates that strip is TAIL_ZONE_KICAD.  The tallest
# carrier part under it is C80 (0603, 0.9 mm), so the gap is 0.9 + 1.7.  Clearing that strip of parts on a later
# board would allow 1.9 mm (flat tail over J4/J5, 1.0 mm) and a device 0.7 mm thinner.
TAIL_ZONE_KICAD = (12.25, 6.9, 29.25, 59.1)
B_SIDE_UNDER_TAIL = 0.9    # [ds] C80; checked against the board by hardware/scripts/fit_check.py
PANEL_GAP_MIN = max(1.9, B_SIDE_UNDER_TAIL + PANEL['tail_bulge'])
CAVITY_MIN = 5.5           # carrier component side -> back shell: module 5.08 + thermal interface; jack 4.5; L3 3.0

# ---------------------------------------------------------------- keyboard stack ([dec] 102 x 29 + D-pad)
KBD_PCB = dict(w=125.0, h=31.0, t=1.0, under_gap=0.0,            # h = key area; the board continues top_ext further up
               top_ext=38.0)                                     # the tray (hardware/scripts/kbd_layout.py BOARD_TOP_EXT)
SWITCH_H = 0.6                                                   # [ds] Alps SKSWCFE010
KEYCAP = dict(flange_t=0.5, top_t=1.2, nub_h=0.3)                # nub: audit K1 (was 0.1)
PLATE_T = 0.8                                                    # top-plate PCB
KEY_CLEARANCE = 3.5        # [dec] 3-4 mm between top key row and the screen-side body edge when open

# ---------------------------------------------------------------- slider
RAIL = dict(w=1.2, h=2.4, clear=0.25, lip=0.8)   # [est] rails on the left/right sides, running in Y
TUB_SIDE = 2.2            # back-shell side wall: thick enough to keep 1.15 mm of plastic behind the rail groove
SLIDE_GAP = 0.4                                  # [est] air gap between body underside and tray top
# Detents (no spring).  Sizes are parameters to tune on the fit mule (audit E3: 3 x 1 mm was probably too weak).
MAGNET_BODY = dict(d=6.0, t=1.0, clear=0.1)      # [est] N52 discs pressed into the back-shell floor from outside
MAGNET_TRAY = dict(d=6.0, t=2.0, clear=0.1)      # [est] N52 discs in the tray posts
MAGNET_HALL = dict(d=5.0, t=2.0, clear=0.1)      # [est] slider-closed sense magnet (audit A2), under carrier U10
SCREWS = dict(insert_d=3.2, insert_l=3.0, screw_d=2.2, boss_d=5.6)   # [est] M2 heat-set inserts (CNC Kitchen style)

# ---------------------------------------------------------------- derived stack (closed)
PLATE_RIM = 0.3            # tray rim above the top plate = keycap tops flush with the rim
PLATE_STANDOFF = SWITCH_H + KEYCAP['nub_h'] + KEYCAP['flange_t'] + 0.1   # top plate above the keyboard PCB
assert abs(PLATE_STANDOFF - 1.5) < 1e-6, PLATE_STANDOFF                # = Wuerth 9774015633 spacer height
TRAY_T = TRAY_FLOOR + KBD_PCB['under_gap'] + KBD_PCB['t'] + PLATE_STANDOFF + PLATE_T + PLATE_RIM
Z_TRAY_TOP = TRAY_T
Z_BODY_BOTTOM = Z_TRAY_TOP + SLIDE_GAP
Z_BACK_IN = Z_BODY_BOTTOM + FLOOR                 # inside face of the removable back (tub floor)
BACK_TUB_H = RAIL['h'] + 0.6                      # back-shell tub wall height; its left/right sides carry the rail grooves
RAIL_INSET = RAIL['w'] + RAIL['clear']            # body narrows by this per side over the tub height
if BATTERY_LAYOUT == 'cutout':
    # The cell bay runs from the back-shell floor to the panel back.  The carrier hangs in the same height:
    # cavity (module, jack, inductors) + board + PANEL_GAP.
    BAY_H = max(BATTERY['t'] + BATTERY['swell'], CAVITY_MIN + CARRIER['t'] + PANEL_GAP_MIN)
    CAVITY = CAVITY_MIN                            # keep the module close to the back shell (short thermal path);
    PANEL_GAP = BAY_H - CARRIER['t'] - CAVITY      # any spare height goes behind the panel
else:                                             # 'under': cell stacked under the module (spec 3.7), for comparison
    CAVITY = MODULE['mated'] + 0.3 + BATTERY['t'] + BATTERY['swell']
    PANEL_GAP = PANEL_GAP_MIN
    BAY_H = CAVITY + CARRIER['t'] + PANEL_GAP
THERMAL_GAP = CAVITY - MODULE['soc_top'] if BATTERY_LAYOUT == 'cutout' else 0.3   # SoC side of the module -> back shell:
assert THERMAL_GAP >= 0.2, THERMAL_GAP            # filled by a pad or copper shim of this thickness (audit E4)
Z_CARRIER_F = Z_BACK_IN + CAVITY                  # carrier F side (faces down)
Z_CARRIER_B = Z_CARRIER_F + CARRIER['t']
B_SIDE_MAX = 1.1           # [ds] tallest display-side part anywhere (D9, only fitted for the hard power-cycle option)
TAIL_FLAT = 0.3            # [est] a flat stretch of panel tail lying over a part outside the component strip
assert B_SIDE_MAX + TAIL_FLAT <= PANEL_GAP + 1e-9 and B_SIDE_UNDER_TAIL + PANEL['tail_bulge'] <= PANEL_GAP + 1e-9, PANEL_GAP
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
PANEL_XY = ((128.0 - PANEL['w']) / 2 + SHIFT_X, 6.87)     # y from the top edge: where it was in the 72 mm body, so the folded
#                                                  tails still land on J4/J5; the extra 2 mm is below the panel
# The carrier's port edge sits 0.3 mm from the inner wall on the device right, so the USB-C, jack and microSD
# mouths reach the wall (audit E1).  The carrier is mounted F-side down, so its KiCad view is mirrored in X:
#   device_x = CARRIER_XY[0] + CARRIER['w'] - kicad_x,  device_y = CARRIER_XY[1] + kicad_y
CARRIER_XY = (BODY_W - WALL - 0.3 - CARRIER['w'], 3.0)      # against the top wall: the buttons on its top edge reach it
MODULE_KICAD = (7.5, 12.0)    # module outline top-left in carrier KiCad coords (carrier_pcb.MODULE)
MODULE_ROT180 = True          # module turned 180 deg in the carrier frame (carrier_pcb.module_xy)
# The pack's three leads (22 AWG, 60 mm) leave a corner of its short edge.  The pack sits at the bottom of the bay,
# which leaves 2.6 mm above it for the leads to turn toward the carrier; they run in the cavity under the carrier's
# top strip to the plug.
BATT_LEAD_GAP = 2.6
BATT_XY = (RAIL_INSET + TUB_SIDE + 0.25, WALL + BATT_LEAD_GAP)             # cell bay, device left
assert BATT_XY[0] + BATTERY['w'] + 0.25 <= CARRIER_XY[0], (BATT_XY, CARRIER_XY)
assert BATT_XY[1] + BATTERY['h'] <= BODY_H - WALL - 0.5, BATT_XY
# Battery header J10 (Molex 5268-03A right-angle, 4.9 mm high) and the mated 5264 plug with the bend of its leads,
# in carrier KiCad coordinates (carrier_pcb.J10_POS, PLUG): x0, y0, x1, y1
BATT_HEADER_KICAD = (62.85, 2.65, 70.85, 12.55)
BATT_PLUG_KICAD = (53.0, 3.6, 62.85, 11.6)       # [est] housing about 4.5 mm proud of the shroud + 5 mm for the bend
BATT_CONN_H = 4.9                                # [ds] Molex 5268-NA catalogue drawing
assert BATT_CONN_H <= CAVITY - 0.3, (BATT_CONN_H, CAVITY)
KBD_XY = ((128.0 - KBD_PCB['w']) / 2 + SHIFT_X, BODY_H - WALL - KBD_PCB['h'])   # keyboard PCB in the tray: under carrier J9
TRAY_LEFT = KBD_XY[0] - 0.1   # the tray's left wall is thicker, up to the keyboard PCB's edge
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
# The cable is our own 0.07 mm flex circuit (hardware/keyboard-flex).  A channel in the back-shell floor above the
# cable lane gives the rolling loop its height: channel roof down to the keyboard PCB.
FPC = dict(t=0.07, w=4.5, length=79.0, channel=0.8)
FPC_LOOP_R = (Z_BODY_BOTTOM + FPC['channel'] - (TRAY_FLOOR + KBD_PCB['t'])) / 2       # 1.9 mm
assert FPC_LOOP_R >= 15 * FPC['t'], FPC_LOOP_R         # JLCPCB guidance for repeated bending: >= 10-15 x thickness
J1_TRAY_Y = KBD_XY[1] - 9.0 - 3.4                      # keyboard J1 opening in tray coords (kbd_layout.J1_XY, FH34 depth)
_j9_mouth_y = CARRIER_XY[1] + KBD_FPC_KICAD[1] + 3.4
FPC_LEN = (3.0 + (FPC_SLOT['y'] - _j9_mouth_y)                      # in J9, then out to the slot
           + (Z_CARRIER_F - 0.5) - (Z_BODY_BOTTOM + FPC['channel'])   # down through the slot
           + (FPC_SLOT['y'] - FPC_LOOP_Y_CLOSED)                      # back under the body
           + 3.14159 * FPC_LOOP_R                                     # the loop
           + (J1_TRAY_Y - FPC_LOOP_Y_CLOSED) + 3.0)                   # forward into J1
assert abs(FPC_LEN - FPC['length']) < 1.0, FPC_LEN     # keep hardware/scripts/flex_design.py LENGTH in step
FPC_LOOP_Y_OPEN_TRAY = FPC_LOOP_Y_CLOSED - TRAVEL / 2  # loop apex in TRAY coordinates when open
assert FPC_LOOP_Y_OPEN_TRAY > WALL + 0.5, FPC_LOOP_Y_OPEN_TRAY

MODULE_XY = carrier_to_device(MODULE_KICAD[0] + MODULE['w'], MODULE_KICAD[1])        # module outline, device top-left
_soc = carrier_to_device(*MODULE['soc_kicad'])
SOC_XY = (_soc[0] - MODULE_XY[0], _soc[1] - MODULE_XY[1])                         # SoC centre in the module outline (device view)
SECTION_X = MODULE_XY[0] + SOC_XY[0]              # render cross-section plane: through the (estimated) SoC position

# ---------------------------------------------------------------- what holds it together (2026-11-27)
# Travel stop: a tab on a spring arm along the tray's top wall runs in a blind channel under the back-shell floor.
# The channel's two ends are the closed and the open stop; a ramp on the body's user edge lets the tab snap in when
# the tray is slid on.  To take the tray off, pull the arm down from below (it lies in the gap above the PCB edge).
STOP = dict(x=40.0, tab_w=4.4, chan_w=5.0, chan_d=0.7, rise=0.55, y0=1.7, y1=3.4, arm_len=18.0, arm_t=1.2)
# Back shell to front shell on the battery side: three rigid hooks on the back shell catch ledges inside the front
# shell's left wall (hook it in, swing it shut, two screws on the carrier side).
HOOKS = dict(ys=(14.0, 37.0, 60.0), length=8.0, reach=1.0, ledge_h=1.0, hook_h=2.2, play=0.2)
PLATE_LIP = 0.8            # tray rim over the top plate's edge (left, right and user side); the rim is PLATE_RIM thick
BUTTON_CAP = dict(w=4.0, h=1.5, proud=0.4, flange=0.8, flange_t=0.95)   # printed caps for power / volume
EDGE_R = 0.6               # rounding of the outer top and bottom edges
