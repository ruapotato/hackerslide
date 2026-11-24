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
MODULE = dict(w=55.0, h=40.0, t=4.7, stack=1.5, mated=5.078,    # [ds] CM4/Core3566 datasheet ch.3
              soc_xy=(31.99, 16.98), soc_size=(14.0, 14.0))     # [est] SoC position copied from CM4 drawing
PANEL = dict(w=105.4, h=62.4, t=3.93, aa_w=93.6, aa_h=56.16,    # [ds] Focus E43GB-I-MW405-C outline (landscape)
             fpc_end='left')                                     # FPC tail exits the device-left short side
CARRIER = dict(w=122.0, h=66.0, t=1.0, f_side_max=2.1)          # hardware/scripts/carrier_pcb.py; tallest F part FH12 2.0
# Battery: 3000 mAh class 7.5 x 50 x 60 pouch (generic 755060 size). Sourced cell still TODO(verify), see bom.
BATTERY = dict(w=50.0, h=60.0, t=7.5, swell=0.3)
BATTERY_LAYOUT = 'beside'  # 'beside' the module (proposal, keeps <= ~21 mm) or 'under' (section 3.7 stack)

# ---------------------------------------------------------------- keyboard stack ([dec] 102 x 29 + D-pad)
KBD_PCB = dict(w=125.0, h=31.0, t=0.8, under_gap=1.2)            # under_gap: SOD-323 diodes on the bottom (1.1 max)
SWITCH_H = 0.6                                                   # [ds] Alps SKSWCFE010
KEYCAP = dict(flange_t=0.5, top_t=1.2)
PLATE_T = 0.8                                                    # top-plate PCB
KEY_CLEARANCE = 3.5        # [dec] 3-4 mm between top key row and the screen-side body edge when open

# ---------------------------------------------------------------- slider
RAIL = dict(w=2.0, h=2.4, clear=0.25, lip=1.0)   # [est] rails on the left/right sides, running in Y
SLIDE_GAP = 0.4                                  # [est] air gap between body underside and tray top
MAGNET = dict(d=3.0, t=1.0, clear=0.1)           # [est] N52 disc 3 x 1 mm (detents, no spring)
SCREWS = dict(insert_d=3.2, insert_l=3.0, screw_d=2.2, boss_d=5.0)   # [est] M2 heat-set inserts (CNC Kitchen style)

# ---------------------------------------------------------------- derived stack (closed)
TRAY_T = TRAY_FLOOR + KBD_PCB['under_gap'] + KBD_PCB['t'] + SWITCH_H + KEYCAP['flange_t'] + 0.1 + PLATE_T + 0.4
Z_TRAY_TOP = TRAY_T
Z_BODY_BOTTOM = Z_TRAY_TOP + SLIDE_GAP
Z_BACK_IN = Z_BODY_BOTTOM + FLOOR                 # inside face of the removable back (tub floor)
BACK_TUB_H = RAIL['h'] + 0.6                      # back-shell tub wall height; its left/right sides carry the rail grooves
RAIL_INSET = RAIL['w'] + RAIL['clear']            # body narrows by this per side over the tub height
THERMAL_PAD = 0.5                                 # [est] SoC -> back shell pad / copper shim
CAVITY = max(MODULE['mated'] + THERMAL_PAD, BATTERY['t'] + BATTERY['swell'] if BATTERY_LAYOUT == 'beside' else 0,
             CARRIER['f_side_max'])
if BATTERY_LAYOUT == 'under':
    CAVITY = MODULE['mated'] + 0.3 + BATTERY['t'] + BATTERY['swell']
Z_CARRIER_F = Z_BACK_IN + CAVITY                  # carrier F side (faces down)
Z_CARRIER_B = Z_CARRIER_F + CARRIER['t']
Z_PANEL_BOTTOM = Z_CARRIER_B + 0.5                # 0.5 mm for the folded panel FPC
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
CARRIER_XY = ((BODY_W - CARRIER['w']) / 2, (BODY_H - CARRIER['h']) / 2)
# The carrier is mounted F-side down, so the KiCad view is mirrored in X (see hardware/scripts/carrier_pcb.py).
MODULE_KICAD = (16.0, 13.0)   # module outline top-left in carrier KiCad coords (carrier_pcb.MODULE)
BATT_KICAD = (71.0, 4.3)
KBD_XY = ((BODY_W - KBD_PCB['w']) / 2, BODY_H - WALL - KBD_PCB['h'])   # keyboard PCB in the tray

# Detents (no spring): the back-shell tub carries two magnets per side, A at body y = MAGNET_Y_CLOSED and B at
# body y = MAGNET_Y_OPEN.  The tray carries matching magnets at tray y = MAGNET_Y_CLOSED (meets A when closed)
# and MAGNET_Y_OPEN - TRAVEL (meets B when open).  Both tray spots are in the tray's upper half, which stays
# under the body in both positions, clear of the keyboard.
MAGNET_Y_CLOSED = 36.0
MAGNET_Y_OPEN = 55.0
MAGNET_X = (7.0, BODY_W - 7.0)
# Body fasteners: only two M2 screws, at the device-right corners (module side) through notches in the carrier.
# The battery fills the left side corner to corner, so the left edge is held by snap hooks (TODO, see enclosure.md).
SCREW_XY = [(BODY_W - 4.4, 4.4), (BODY_W - 4.4, BODY_H - 4.4)]
CARRIER_NOTCH = 4.6        # square notch at the two carrier corners under the screws (carrier KiCad x = 0 side)
BOSS_D = 5.6

SECTION_X = 86.0          # render cross-section plane: through the (estimated) SoC position
