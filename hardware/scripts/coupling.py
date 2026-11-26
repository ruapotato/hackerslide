"""Which nets run side by side on the carrier, and for how long: a crosstalk screen for the auto-routed signals.

  python3 coupling.py [BOARD.kicad_pcb]      (system python: needs pcbnew, numpy)

For every pair of nearly parallel track segments of different nets on the same layer, closer than GAP edge to edge,
the overlapping length is added up per net pair.  The estimate is the saturated backward crosstalk of two lines
over a plane, Kb = 1 / (4 (1 + (s/h)^2)), s = centre spacing, h = height over the plane (0.1 mm: F over In1, B and
In2 over each other's copper), reached when the coupled length exceeds rise time x 75 mm/ns; shorter runs couple
proportionally less.  With the 2 ns edges of this board's ordinary signals that length is 150 mm, so the figure
printed is Kb x min(1, L / 150).

Pairs that belong together (the two lines of a differential pair) are left out.  The table lists every pair where
a net from QUIET (analogue audio, resets, enables, clocks that glitch a state machine) lies next to anything, and
the longest of the rest.
"""
import collections
import math
import sys

import numpy as np
import pcbnew

GAP = 0.30          # edge-to-edge distance below which a neighbour counts, mm
H = 0.1             # height over the reference copper, mm
SAT = 150.0         # coupled length at which backward crosstalk saturates for 2 ns edges, mm
QUIET = ('HP_', 'MIC', 'HPGND', 'JACK_', 'RUN_PG', 'RST', 'RESET', 'NRPIBOOT', 'PWR_', 'CHG_QON', 'FUSE_EN',
         'I2S_MCLK', 'I2S_SCLK', 'SD_CLK', 'I2C_', 'LED_K', 'CHG_TS', 'BATT_NTC', 'BATT_ILIM', 'BOOST_FB', 'REGN')
LOUD = ('BL_SW', 'BOOST_SW', 'CHG_SW', 'CHG_BTST', 'LED_A', 'SD_CLK', 'I2S_MCLK', 'I2S_SCLK', 'USB_D', 'DSI_')


def pair_of(a, b):
    strip = lambda n: n[:-2] if n.endswith(('_P', '_N')) else (n[:-1] if n.endswith(('DP', 'DM')) else n)
    return a != b and strip(a) == strip(b) and len(strip(a)) < len(a)


def main(path):
    b = pcbnew.LoadBoard(path)
    T = pcbnew.ToMM
    segs = collections.defaultdict(list)
    for t in b.GetTracks():
        if t.GetClass() != 'PCB_TRACK' or t.GetLength() < pcbnew.FromMM(0.3):
            continue
        s, e = t.GetStart(), t.GetEnd()
        segs[t.GetLayerName()].append((T(s.x), T(s.y), T(e.x), T(e.y), T(t.GetWidth()), t.GetNetname()))
    tot = collections.defaultdict(lambda: [0.0, 9.9, set()])
    for layer, L in segs.items():
        A = np.array([s[:5] for s in L])
        d = A[:, 2:4] - A[:, 0:2]
        ln = np.hypot(d[:, 0], d[:, 1])
        u = d / ln[:, None]
        mid = (A[:, 0:2] + A[:, 2:4]) / 2
        for i in range(len(L)):
            near = np.nonzero(np.hypot(mid[:, 0] - mid[i, 0], mid[:, 1] - mid[i, 1]) < (ln + ln[i]) / 2 + 1.0)[0]
            for j in near:
                if j <= i or L[i][5] == L[j][5] or pair_of(L[i][5], L[j][5]):
                    continue
                if abs(u[i] @ u[j]) < 0.97:
                    continue
                # project segment j on segment i
                r0, r1 = A[j, 0:2] - A[i, 0:2], A[j, 2:4] - A[i, 0:2]
                t0, t1 = sorted((r0 @ u[i], r1 @ u[i]))
                ov = min(t1, ln[i]) - max(t0, 0.0)
                if ov <= 0.2:
                    continue
                n = np.array([-u[i][1], u[i][0]])
                dist = (abs(r0 @ n) + abs(r1 @ n)) / 2
                gap = dist - (A[i, 4] + A[j, 4]) / 2
                if gap > GAP:
                    continue
                k = tuple(sorted((L[i][5], L[j][5])))
                tot[k][0] += ov
                tot[k][1] = min(tot[k][1], dist)
                tot[k][2].add(layer)
    rows = []
    for (a, c), (length, s, layers) in tot.items():
        kb = 1 / (4 * (1 + (s / H) ** 2)) * min(1.0, length / SAT)
        quiet = any(q in n for n in (a, c) for q in QUIET)
        loud = any(q in n for n in (a, c) for q in LOUD)
        rows.append((kb, length, s, a, c, ','.join(sorted(l[:-3] for l in layers)), quiet, loud))
    rows.sort(reverse=True)
    print('| Net | Neighbour | Layer | Side by side | Centre spacing | Estimated crosstalk |')
    print('|---|---|---|---|---|---|')
    shown = 0
    for kb, length, s, a, c, layers, quiet, loud in rows:
        if 'GND' in (a, c):
            continue
        if (quiet and loud and length > 1.0) or (shown < 12 and kb >= 0.002):
            print(f'| {a} | {c} | {layers} | {length:.1f} mm | {s:.2f} mm | {kb * 100:.1f} %{" **" if quiet and loud else ""} |')
            shown += 1
    print(f'\n{len(rows)} net pairs run side by side within {GAP} mm; worst estimate {rows[0][0] * 100:.1f} %.')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else '../carrier/carrier.kicad_pcb')
