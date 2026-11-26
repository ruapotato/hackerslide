"""Hack pad keyboard geometry and switch matrix, shared by the board, the top plate and the enclosure model.

Layout decided by David on 2026-11-27 (docs/keyboard.md, "Next layout"): three letter rows of eleven keys and a
bottom row as on the Nokia N810, digits on Fn + the top row, Esc and Tab above a five-switch D-pad on the left.
All numbers are mm in board coordinates: origin at the top-left of the key area, +y toward the user.

  python3 hp_layout.py        prints the key list and checks the matrix
"""
AREA_W, AREA_H = 125.0, 31.0          # key area on the board (the board itself is larger: it is the main board)
LEFT_W = 23.0                          # Esc, Tab and the D-pad
FIELD_X0, FIELD_Y0 = LEFT_W, 1.0
FIELD_W, FIELD_H = 102.0, 29.0
COLS, ROWS = 11, 4
PITCH_X = FIELD_W / COLS               # 9.27 mm
PITCH_Y = FIELD_H / ROWS               # 7.25 mm
CAP_GAP = 0.6

# (legend, Fn legend) per key; None continues the key above (the tall Enter)
LETTERS = [
    [('Q', '1'), ('W', '2'), ('E', '3'), ('R', '4'), ('T', '5'), ('Y', '6'), ('U', '7'), ('I', '8'), ('O', '9'), ('P', '0'), ('Bksp', 'Del')],
    [('A', '!'), ('S', '"'), ('D', '@'), ('F', '#'), ('G', '\\'), ('H', '/'), ('J', '('), ('K', ')'), ('L', '*'), (',', '?'), ('Enter', '')],
    [('Z', "'"), ('X', '^'), ('C', '~'), ('V', '%'), ('B', '&'), ('N', '$'), ('M', '`'), (';', '|'), ('-', '_'), ('+', '='), None],
]
# bottom row: (legend, Fn legend, width in key units)
BOTTOM = [('Fn', '', 1.5), ('ShiftL', '', 1.0), ('Chr', 'Alt', 1.0), ('Space', '', 3.0), (',<', '[', 1.0), ('.>', ']', 1.0),
          ('Ctrl', '', 1.0), ('ShiftR', '', 1.5)]
assert abs(sum(w for _, _, w in BOTTOM) - COLS) < 1e-9
DPAD_C = (LEFT_W / 2, 18.6)
DPAD_STEP = 6.4
LEFT = [('Esc', 6.25, 4.0, 9.5, 5.6), ('Tab', 16.75, 4.0, 9.5, 5.6),
        ('Up', DPAD_C[0], DPAD_C[1] - DPAD_STEP, 6.4, 6.4), ('Down', DPAD_C[0], DPAD_C[1] + DPAD_STEP, 6.4, 6.4),
        ('Left', DPAD_C[0] - DPAD_STEP, DPAD_C[1], 6.4, 6.4), ('Right', DPAD_C[0] + DPAD_STEP, DPAD_C[1], 6.4, 6.4),
        ('OK', DPAD_C[0], DPAD_C[1], 6.4, 6.4)]


def keys():
    """[dict(name, fn, x, y, w, h, switches)]: cap centre and size; switches = [(x, y)] under the cap (the 3-wide
    space bar and nothing else has two, wired in parallel)."""
    out = []
    for r, row in enumerate(LETTERS):
        for c, k in enumerate(row):
            if k is None:
                continue
            x, y = FIELD_X0 + PITCH_X * (c + 0.5), FIELD_Y0 + PITCH_Y * (r + 0.5)
            h = PITCH_Y
            if k[0] == 'Enter':                      # two rows tall, one switch in the middle
                y += PITCH_Y / 2
                h = 2 * PITCH_Y
            out.append(dict(name=k[0], fn=k[1], x=x, y=y, w=PITCH_X, h=h, switches=[(x, y)]))
    x = FIELD_X0
    y = FIELD_Y0 + PITCH_Y * 3.5
    for name, fn, u in BOTTOM:
        w = u * PITCH_X
        cx = x + w / 2
        sw = [(cx - 0.9 * PITCH_X, y), (cx + 0.9 * PITCH_X, y)] if name == 'Space' else [(cx, y)]
        out.append(dict(name=name, fn=fn, x=cx, y=y, w=w, h=PITCH_Y, switches=sw))
        x += w
    for name, cx, cy, w, h in LEFT:
        out.append(dict(name=name, fn='', x=cx, y=cy, w=w, h=h, switches=[(cx, cy)]))
    return out


def matrix():
    """{key name: (ROW, COL)} for the TCA8418 (8 rows x 10 columns).  Letter-row keys in columns 0-9 sit at their
    own row and column; the eleventh column, the bottom row and the left cluster fill rows 3-5."""
    m = {}
    for r, row in enumerate(LETTERS):
        for c, k in enumerate(row):
            if k is not None and c < 10:
                m[k[0]] = (r, c)
    m['Bksp'], m['Enter'] = (3, 8), (3, 9)
    for c, (name, _fn, _u) in enumerate(BOTTOM):
        m[name] = (3, c)
    for c, (name, *_r) in enumerate(LEFT):
        m[name] = (4, c)
    return m


if __name__ == '__main__':
    ks, m = keys(), matrix()
    assert len(ks) == len(m) == len(set(m.values())), (len(ks), len(m), len(set(m.values())))
    assert all(r < 8 and c < 10 for r, c in m.values())
    for a in ks:                                       # caps must not overlap and must stay on the key area
        assert CAP_GAP / 2 - 1e-6 <= a['x'] - a['w'] / 2 and a['x'] + a['w'] / 2 <= AREA_W + 1e-6, a['name']
        for b in ks:
            if a is not b:
                assert (abs(a['x'] - b['x']) >= (a['w'] + b['w']) / 2 - 1e-6
                        or abs(a['y'] - b['y']) >= (a['h'] + b['h']) / 2 - 1e-6), (a['name'], b['name'])
    n_sw = sum(len(k['switches']) for k in ks)
    print(f'{len(ks)} keys, {n_sw} switches, matrix rows used {sorted({r for r, _ in m.values()})}')
    for k in ks:
        print(f"{k['name']:7s} fn {k['fn'] or '-':3s} at ({k['x']:6.2f}, {k['y']:5.2f}) {k['w']:5.2f} x {k['h']:5.2f}  ROW{m[k['name']][0]} COL{m[k['name']][1]}")
