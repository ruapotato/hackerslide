"""Key names on the keyboard board's silkscreen, in brackets beside each switch's reference: "SW14 (Q)".

  python3 key_labels.py BOARD.kicad_pcb      adds them to an existing (routed) board; copper is not touched
keyboard_pcb.py calls add() when it builds the board.  For bring-up: with the bare board on the bench, a probe or a
pair of tweezers on a switch tells you which key the scanner should report.
"""
import sys

import pcbnew

import kbd_layout as KL

MM = pcbnew.FromMM
MARK = 'key_label'      # labels are found again by this prefix in their own text: "(" ... ")" plus position check


def labels(variant='alps'):
    """[(text, x, y, size, justify)]: beside the switch reference, which sits 2.0 mm above the switch centre."""
    out = []
    for (name, r, col, x, y) in KL.keys(variant):
        s = f'({name})'
        if r == 4:                               # D-pad: the Left key has the OK key to its right
            out.append((s, x - 1.95, y - 2.0, 0.6, 'right') if name == 'Left' else (s, x + 1.95, y - 2.0, 0.6, 'left'))
        elif col == KL.COLS - 1:                 # last column: no room to the right; use the diode's line
            out.append((s, x - 1.3, y + 3.45, 0.65, 'right'))
        else:
            out.append((s, x + 1.95, y - 2.0, 0.65, 'left'))
    return out


def _clash(board, box, others):
    edge = board.GetBoardEdgesBoundingBox()
    edge.Inflate(-MM(0.3))
    return (not edge.Contains(box) or any(box.Intersects(o) for o in others))


def add(board, variant='alps', sizes=(0.8, 0.7, 0.65, 0.6)):
    """Adds the labels, each at the largest of `sizes` that touches no pad, no other silkscreen text and not the
    edge.  Returns (labels, the ones that fit at no size)."""
    want = {s for (s, *_r) in labels(variant)}
    fixed = [f.Reference().GetBoundingBox() for f in board.GetFootprints() if f.Reference().IsVisible()]
    fixed += [p.GetBoundingBox() for f in board.GetFootprints() for p in f.Pads()]
    old = [d for d in board.GetDrawings() if d.GetClass() == 'PCB_TEXT' and d.GetLayer() == pcbnew.F_SilkS
           and d.GetText() in want]
    for d in old:                                # idempotent: drop labels from an earlier run
        board.Remove(d)
    made, bad = [], []
    for (s, x, y, _size, just) in labels(variant):
        t = pcbnew.PCB_TEXT(board)
        t.SetText(s)
        t.SetLayer(pcbnew.F_SilkS)
        t.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_LEFT if just == 'left' else pcbnew.GR_TEXT_H_ALIGN_RIGHT)
        t.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
        for size in sizes:
            t.SetTextSize(pcbnew.VECTOR2I(MM(size), MM(size)))
            t.SetTextThickness(MM(size * 0.15))
            if not _clash(board, t.GetBoundingBox(), fixed):
                break
        else:
            bad.append(s)
        board.Add(t)
        fixed.append(t.GetBoundingBox())
        made.append(t)
    return made, bad


if __name__ == '__main__':
    b = pcbnew.LoadBoard(sys.argv[1])
    made, bad = add(b)
    small = sorted({t.GetText() for t in made if pcbnew.ToMM(t.GetTextSize().x) < 0.79})
    print(len(made), 'key labels; below 0.8 mm:', small or 'none', '; clashing:', bad or 'none')
    if not bad:
        pcbnew.SaveBoard(sys.argv[1], b)
