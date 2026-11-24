"""Keyboard geometry shared by the keyboard PCB, the top plate and the mechanical model.

All numbers are mm, KiCad board coordinates (origin top-left of the keyboard PCB, +Y toward the user).
Key field 102 x 29 mm and the ~24 mm D-pad zone come from the design decision (docs/decisions/0003).
"""
BOARD_W = 125.0          # 23 mm D-pad zone + 102 mm key field; tray walls 1.5 mm -> 128 mm tray
BOARD_H = 31.0           # 29 mm key field + 1 mm margin top/bottom
DPAD_ZONE_W = 23.0
FIELD_X0, FIELD_Y0 = DPAD_ZONE_W, 1.0
COLS, ROWS = 12, 4
PITCH_X = 102.0 / COLS   # 8.5 mm
PITCH_Y = 29.0 / ROWS    # 7.25 mm
DPAD_C = (DPAD_ZONE_W / 2, BOARD_H / 2)
DPAD_STEP = {'alps': 6.0, 'dome': 7.0}   # centre-to-direction spacing per switch variant
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


def keys(variant='alps'):
    """[(name, row, col, x, y)] matrix position for every switch; D-pad is matrix row 4."""
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
