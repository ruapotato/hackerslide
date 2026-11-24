"""Keyboard geometry shared by the keyboard PCB, the top plate and the mechanical model.

All numbers are mm, KiCad board coordinates (origin top-left of the keyboard PCB, +Y toward the user).
Key field 102 x 29 mm and the ~24 mm D-pad zone come from the design decision (docs/decisions/0003).
"""
BOARD_W = 125.0          # 23 mm D-pad zone + 102 mm key field; tray walls 1.5 mm -> 128 mm tray
BOARD_H = 31.0           # key area: 29 mm key field + 1 mm margin top/bottom (y = 0..31)
BOARD_TOP_EXT = 38.0     # the PCB is the tray floor (David, 2026-11-24): it continues above the key area to y = -38
PCB_T = 1.0              # structural: it is the bottom skin of the device
PLATE_STANDOFF = 1.5     # top-plate underside above the PCB = height of the Wuerth 9774015633 SMT spacers
J1_XY = (93.3, -2.5)     # keyboard FPC connector (signal row), under carrier J9: mechanical/src/config.py KBD_FPC_X
DPAD_ZONE_W = 23.0
FIELD_X0, FIELD_Y0 = DPAD_ZONE_W, 1.0
COLS, ROWS = 12, 4
PITCH_X = 102.0 / COLS   # 8.5 mm
PITCH_Y = 29.0 / ROWS    # 7.25 mm
DPAD_C = (DPAD_ZONE_W / 2, BOARD_H / 2)
DPAD_STEP = {'alps': 6.0, 'dome': 7.3}   # centre-to-direction spacing; domes are 7.0 across flats (audit K8)
CAP_GAP = 0.6            # gap between neighbouring keycaps

# Proposed legends (N810-like, number row added). Fn layer and exact legends are an open question.
LEGENDS = [
    ['Esc', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'Bksp'],
    ['Tab', 'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '-'],
    ['Ctrl', 'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', ';', 'Enter'],
    ['Shift', 'Fn', 'Z', 'X', 'C', 'V', 'Space', 'Space', 'B', 'N', 'M', '.'],
]
DPAD_KEYS = [('Up', 0, -1), ('Down', 0, 1), ('Left', -1, 0), ('Right', 1, 0), ('OK', 0, 0)]


def key_center(r, c):
    return FIELD_X0 + PITCH_X * (c + 0.5), FIELD_Y0 + PITCH_Y * (r + 0.5)


def dpad_center(i, variant='alps'):
    _, dx, dy = DPAD_KEYS[i]
    s = DPAD_STEP[variant]
    return DPAD_C[0] + dx * s, DPAD_C[1] + dy * s


def matrix_pos(r, c):
    """Physical (row, col) -> TCA8418 (ROW, COL).  The chip has 8 rows x 10 columns, so the two right-hand
    physical columns fold into ROW4 and the D-pad (physical row 4) becomes ROW5.  Both Space keys share a position."""
    if r == 4:
        return 5, c
    if c >= 10:
        return 4, (c - 10) * 4 + r
    if LEGENDS[r][c] == 'Space':
        return 3, 6
    return r, c


def keys(variant='alps'):
    """[(name, row, col, x, y)] PHYSICAL position of every switch; the D-pad is physical row 4.  Use matrix_pos()
    for the electrical row/column."""
    out = []
    for r in range(ROWS):
        for c in range(COLS):
            x, y = key_center(r, c)
            out.append((LEGENDS[r][c], r, c, x, y))
    for i, (name, _dx, _dy) in enumerate(DPAD_KEYS):
        x, y = dpad_center(i, variant)
        out.append((name, 4, i, x, y))
    return out

# Secondary (Fn-layer) legends printed on the top plate above each key. Proposal only.
FN_LEGENDS = [
    ['`', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'Del'],
    ['', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '='],
    ['', '[', ']', '{', '}', '\\', '|', '<', '>', "'", '"', ''],
    ['Caps', '', '~', '+', '_', '?', '', '', '/', ',', 'Alt', 'Super'],
]
CAP = {'top_w': 7.0, 'top_h': 5.8, 'flange_w': PITCH_X - CAP_GAP, 'flange_h': PITCH_Y - CAP_GAP,
       'top_t': 1.2, 'flange_t': 0.5}   # keycap geometry used by the top plate and the printable keycaps
PLATE_HOLE_CLEAR = 0.15                  # per side, plate hole vs keycap top

# Top-plate fixing: four M1.6 SMT spacers (Wuerth 9774015633, 1.5 mm) soldered to the PCB in the D-pad zone; the
# plate is screwed onto them, which also grounds it.  Inside the key field the webs between keycap openings are
# 1.2 mm wide, too narrow for a screw; the tray frame's lips hold the other three plate edges.
PLATE_HOLES = [(3.0, 3.0), (20.0, 3.0), (3.0, 28.0), (20.0, 28.0)]
