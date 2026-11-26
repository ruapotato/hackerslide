"""Differential impedance of an edge-coupled microstrip pair, by a 2-D finite-difference field solution.

  VENV/bin/python impedance.py                 (prints the table used in docs/carrier-board.md)

Quasi-static odd mode: Laplace's equation on a 2.5 um grid in half the cross-section (the symmetry plane between the
two tracks is at 0 V), once with the dielectrics and once with air; Zodd = 1 / (c * sqrt(C * C_air)), Zdiff = 2 Zodd.
Model: ground plane, prepreg of height h and permittivity er, tracks of trapezoid-free rectangular section w x t,
solder mask (er 3.8) 30 um on the laminate and 15 um over the copper (JLCPCB "Impedance Control Design Information":
1.2 mil on FR-4, 0.6 mil on copper, outer copper 1.6 mil finished).  Needs numpy and scipy.  It ignores etch-back
(the fab compensates) and dispersion, which is fine below a few GHz on a 30-50 mm run.  Expect +-5 %; the fab's own
tolerance is +-10 %.
"""
import numpy as np
from scipy.sparse import lil_matrix, csr_matrix
from scipy.sparse.linalg import spsolve

C0 = 299792458.0
E0 = 8.8541878128e-12


def zdiff(w, s, h, er, t=0.0406, mask=True, g=0.0025):
    W = s / 2 + w + max(8 * h, 1.2)          # half width of the box (mm)
    H = h + t + max(8 * h, 1.2)
    nx, ny = int(round(W / g)) + 1, int(round(H / g)) + 1
    x = np.arange(nx) * g
    y = np.arange(ny) * g
    X, Y = np.meshgrid(x, y)
    cond = (X >= s / 2 - 1e-9) & (X <= s / 2 + w + 1e-9) & (Y >= h - 1e-9) & (Y <= h + t + 1e-9)

    def cap(with_diel):
        eps = np.ones((ny, nx))
        if with_diel:
            eps[Y < h] = er
            if mask:
                eps[(Y >= h) & (Y < h + 0.030)] = 3.8
                eps[(X >= s / 2 - 0.015) & (X <= s / 2 + w + 0.015) & (Y >= h) & (Y < h + t + 0.015)] = 3.8
        idx = -np.ones((ny, nx), int)
        free = ~cond
        free[0, :] = False; free[-1, :] = False; free[:, 0] = False; free[:, -1] = False
        idx[free] = np.arange(free.sum())
        n = int(free.sum())
        rows, cols, vals = [], [], []
        b = np.zeros(n)
        ee = {}
        # permittivity on the links between nodes: mean of the two cells
        for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            e = 0.5 * (eps + np.roll(np.roll(eps, -dy, 0), -dx, 1))
            ee[(dy, dx)] = e
        ys, xs = np.nonzero(free)
        k = idx[ys, xs]
        diag = np.zeros(n)
        for (dy, dx), e in ee.items():
            yy, xx = ys + dy, xs + dx
            ev = e[ys, xs]
            diag += ev
            nb = idx[yy, xx]
            inside = nb >= 0
            rows.append(k[inside]); cols.append(nb[inside]); vals.append(-ev[inside])
            on = cond[yy, xx]
            b[k[on]] += ev[on] * 1.0
        rows.append(k); cols.append(k); vals.append(diag)
        A = csr_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))), shape=(n, n))
        v = np.zeros((ny, nx))
        v[cond] = 1.0
        v[free] = spsolve(A, b)
        # energy: C = sum eps * |grad V|^2 * e0 (per metre), V = 1
        en = 0.0
        for (dy, dx), e in ee.items():
            if (dy, dx) in ((0, 1), (1, 0)):
                dv = np.roll(np.roll(v, -dy, 0), -dx, 1) - v
                if dx:
                    dv[:, -1] = 0
                else:
                    dv[-1, :] = 0
                en += (e * dv * dv).sum()
        return en * E0

    c, ca = cap(True), cap(False)
    return 2.0 / (C0 * np.sqrt(c * ca))


if __name__ == '__main__':
    print('prepreg 3313, 0.0994 mm, er 4.1 (JLCPCB 4-layer builds with 3313 between the outer layer and the plane)')
    for w, s in ((0.10, 0.12), (0.11, 0.12), (0.12, 0.12), (0.13, 0.12), (0.14, 0.12), (0.15, 0.12), (0.10, 0.15), (0.11, 0.15)):
        print(f'  w {w:.2f}  gap {s:.2f}  Zdiff {zdiff(w, s, 0.0994, 4.1):6.1f} ohm')
    print('prepreg 7628, 0.2104 mm, er 4.4')
    for w, s in ((0.10, 0.12), (0.15, 0.12), (0.20, 0.15), (0.25, 0.15)):
        print(f'  w {w:.2f}  gap {s:.2f}  Zdiff {zdiff(w, s, 0.2104, 4.4):6.1f} ohm')
