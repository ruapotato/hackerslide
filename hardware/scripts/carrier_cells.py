"""Hand-laid power blocks of the carrier: every part and every track of the charger and of the 5 V boost is placed
here by coordinate, following the layout guidance in the TI datasheets, instead of being left to the grid router.

A block is written in its own frame: (0, 0) is the centre of its IC, x to the right and y down as seen from the
component side.  Tracks may name pads, so a moved part takes its tracks along.
"""
import pcbnew

F, In2, Bk = pcbnew.F_Cu, pcbnew.In2_Cu, pcbnew.B_Cu


class Cell:
    def __init__(self, B, ox, oy):
        self.B, self.ox, self.oy = B, ox, oy

    def xy(self, p):
        return self.B.pad_xy(*p) if isinstance(p[0], str) else (self.ox + p[0], self.oy + p[1])

    def P(self, ref, x, y, rot=0, side='F'):
        self.B.place(ref, self.ox + x, self.oy + y, rot, side)

    def T(self, net, pts, w, layer=F):
        self.B.track(net, [self.xy(p) for p in pts], w, layer)

    def V(self, net, x, y, d=0.6, drill=0.3):
        self.B.via(net, self.ox + x, self.oy + y, d, drill)

    def rel(self, ref, num):
        x, y = self.B.pad_xy(ref, num)
        return x - self.ox, y - self.oy

    def gnd(self, ref, num, dx, dy, w=0.4, d=0.6, drill=0.3):
        """a ground via next to a pad, joined by a short track (the In1 plane is 0.1 mm below)"""
        x, y = self.rel(ref, num)
        self.T('GND', [(x, y), (x + dx, y + dy)], w, Bk if self.B.fps[ref].IsFlipped() else F)
        self.V('GND', x + dx, y + dy, d, drill)

    def two(self, ref, x, y, d, side='F'):
        """place a two-pad part with pad 1 toward d ('L', 'R', 'U' or 'D' as seen in board coordinates)"""
        want = {'L': (-1, 0), 'R': (1, 0), 'U': (0, -1), 'D': (0, 1)}[d]
        fp = self.B.fps[ref]
        if side == 'B' and not fp.IsFlipped():
            fp.Flip(fp.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
        sgn = lambda v: (round(v, 1) > 0) - (round(v, 1) < 0)
        for rot in (0, 90, 180, 270):
            fp.SetOrientationDegrees(rot)
            fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(self.ox + x), pcbnew.FromMM(self.oy + y)))
            px, py = self.rel(ref, '1')
            if (sgn(px - x), sgn(py - y)) == want:
                return self.P(ref, x, y, rot, side)
        raise RuntimeError(ref)


def charger(B, ox, oy):
    """BQ25895 (U3) turned so that its two power sides face right and down the strip.

    Seen from the component side:   top    SDA SCL STAT D- D+ VBUS        right (top to bottom)  DSEL PMID REGN BTST SW SW
                                    left   INT OTG CE ILIM TS /QON        bottom (right to left) PGND PGND SYS SYS BAT BAT
    TI SLUSC88C section 11: (1) PMID capacitor right at PMID with a short ground return, (2) small SW node,
    (3) SYS and BAT capacitors next to their pins, ground returns into the exposed pad and the plane under it.
    """
    c = Cell(B, ox, oy)
    c.P('U3', 0, 0, -90)
    # ground pins into the exposed pad: PGND 17/18 (bottom right), OTG and /CE (left: OTG low = no boost mode, /CE low = charge enabled)
    for pin in ('17', '18', '8', '9'):
        x, y = c.rel('U3', pin)
        k = 0.6 / max(abs(x), abs(y))
        c.T('GND', [(x, y), (x * k, y * k)], 0.25)
    # PMID: C11 directly at pin 23, C12 beside it on the same copper; ground ends two vias away from the plane
    c.P('C11', 4.4, -1.75, 0)
    c.P('C12', 4.4, -3.75, 0)
    c.T('PMID', [('U3', '23'), (2.7, -0.75), (3.45, -1.35)], 0.25)
    c.T('PMID', [('C11', '1'), ('C12', '1')], 0.9)
    c.T('GND', [('C11', '2'), ('C12', '2')], 0.9)
    c.gnd('C12', '2', -0.5, -1.25)
    c.gnd('C12', '2', 0.15, -1.25)
    c.V('GND', c.rel('C11', '2')[0], -2.75)               # and one on the bar between the two, 1 mm from C11
    # SW: pins 19/20 -> L1 pad 1, bootstrap capacitor C13 from BTST straight onto the SW copper
    c.P('L1', 1.15, 5.5, 180)
    c.P('C13', 3.45, 0.7, -90)
    c.T('CHG_SW', [('U3', '19'), (2.9, 1.25)], 0.25)
    c.T('CHG_SW', [('U3', '20'), (2.9, 0.75), ('C13', '2')], 0.25)
    c.T('CHG_SW', [(2.3, 1.0), (3.0, 1.0), (3.0, 4.8)], 0.7)
    c.T('CHG_BTST', [('U3', '21'), ('C13', '1')], 0.2)
    # REGN capacitor
    c.P('C14', 5.0, 0.85, -90)
    c.T('REGN', [('U3', '22'), (4.3, -0.25), ('C14', '1')], 0.15)
    c.gnd('C14', '2', 0.0, 1.1)
    # SYS: pins 15/16 straight down into L1 pad 2; C15/C16 below the inductor; vias into the In2 VSYS area
    c.T('VSYS', [(0.0, 1.96), (0.0, 2.9), (-0.5, 3.5), (-0.5, 4.8)], 0.6)
    c.P('C15', -0.3, 9.6, -90)
    c.P('C16', 1.7, 9.6, -90)
    c.T('VSYS', [(-0.7, 6.5), (-0.7, 8.6)], 1.2)
    c.T('VSYS', [('C15', '1'), ('C16', '1'), (4.9, 8.65)], 0.9)
    c.T('VSYS', [(4.5, 8.65), (4.5, 7.9)], 0.9)
    for x, y in ((4.1, 8.65), (4.9, 8.65), (4.5, 7.9)):
        c.V('VSYS', x, y)
    c.T('GND', [('C15', '2'), ('C16', '2')], 0.9)
    c.gnd('C15', '2', 0.0, 1.15)
    c.gnd('C15', '2', 1.0, 1.15)
    # BAT: pins 13/14 -> three vias -> C17 and the VBAT copper on the display side (carrier_pcb draws that area)
    c.T('VBAT', [(-1.0, 1.96), (-1.0, 3.1), (-2.45, 3.1), (-2.45, 3.85)], 0.5)
    for x, y in ((-1.7, 3.1), (-2.45, 3.1), (-2.45, 3.85)):
        c.V('VBAT', x, y)
    c.two('C17', -0.9, 4.4, 'L', 'B')
    c.T('VBAT', [(-2.45, 3.85), ('C17', '1')], 0.5, Bk)
    c.gnd('C17', '2', 1.0, 0.0)
    # VBUS: pin 1 -> C10 -> vias into the In2 VBUS area
    c.P('C10', 1.5, -3.6, 90)
    c.T('VBUS', [('U3', '1'), (1.25, -2.75), ('C10', '1')], 0.3)
    c.T('VBUS', [('C10', '1'), (2.4, -3.1), (2.4, -4.3)], 0.3)
    for y in (-3.1, -3.7, -4.3):
        c.V('VBUS', 2.4, y, 0.45, 0.2)
    c.gnd('C10', '2', 0.0, -0.9, w=0.3, d=0.45, drill=0.2)

    # ---- signal pins ------------------------------------------------------------------------------------
    # left side: stubs under the module edge to vias; their parts are on the display side below the spacer H2
    for pin, net, vx in (('7', 'CHG_INT_N', -4.2), ('10', 'CHG_ILIM', -4.2), ('11', 'CHG_TS', -4.8), ('12', 'CHG_QON_N', -4.2)):
        x, y = c.rel('U3', pin)
        c.T(net, [(x, y), (vx, y)], 0.15)
        c.V(net, vx, y, 0.45, 0.2)
    c.two('R12', -5.5, -0.45, 'R', 'B')                   # ILIM -> GND
    c.T('CHG_ILIM', [(-4.2, 0.25), (-4.6, -0.15), ('R12', '1')], 0.15, Bk)
    c.gnd('R12', '2', 0.0, -0.8, w=0.25, d=0.45, drill=0.2)
    # TS divider: bus down x = -7.0; R68 brings in the pack thermistor, R13 goes to REGN, R14 (and TH1, DNP) to ground
    c.P('TP8', -8.4, 0.4, 0, 'B')
    c.T('CHG_TS', [(-4.8, 0.75), (-7.9, 0.75), ('TP8', '1')], 0.15, Bk)
    c.T('CHG_TS', [(-7.0, 0.75), (-7.0, 4.65)], 0.15, Bk)
    c.two('R68', -6.49, 1.8, 'R', 'B')
    c.two('R14', -6.49, 2.75, 'L', 'B')
    c.two('R13', -6.49, 3.7, 'R', 'B')
    c.two('TH1', -6.49, 4.65, 'L', 'B')
    for ref in ('R14', 'TH1'):
        c.gnd(ref, '2', 0.98, 0.0, w=0.25, d=0.45, drill=0.2)
    # REGN to R13: under the IC on In2
    c.V('REGN', 4.2, -0.25, 0.45, 0.2)
    c.V('REGN', -5.0, 3.7, 0.45, 0.2)
    c.T('REGN', [(4.2, -0.25), (4.2, 2.0), (-4.3, 2.0), (-4.3, 3.7), (-5.0, 3.7)], 0.15, In2)
    c.T('REGN', [(-5.0, 3.7), ('R13', '1')], 0.15, Bk)
    c.P('TP7', 4.2, -1.35, 0, 'B')
    c.T('REGN', [(4.2, -0.25), ('TP7', '1')], 0.15, Bk)
    # pack thermistor: battery connector pin 2 -> past the spacer hole -> R68
    # (around the top of the VBAT copper at J10 pin 1, then down between the spacer hole and the VBAT channel)
    jx, jy = c.rel('J10', '2')
    c.T('BATT_NTC', [(jx, jy), (jx + 1.55, jy), (jx + 1.55, 3.3 - oy), (-3.6, 3.3 - oy), (-3.6, 1.8), ('R68', '1')], 0.15, Bk)
    # top side: the generic fan-out gives SDA, SCL, STAT, D-, D+ their vias (carrier_pcb); the D+/D- pull-downs on the display side
    # (the DNP links R21/R22 to the USB pair are at the USB connector, so that they leave no stub on the pair)
    c.two('R29', -0.6, -5.4, 'R', 'B')                    # D- pull-down
    c.T('CHG_DM', [(0.25, -3.46), (0.25, -5.4), ('R29', '1')], 0.15, Bk)
    c.two('R28', 1.25, -6.3, 'D', 'B')                    # D+ pull-down
    c.T('CHG_DP', [(0.75, -2.86), (0.75, -4.9), (1.25, -5.4), ('R28', '1')], 0.15, Bk)
    c.gnd('R28', '2', 0.7, -0.4, w=0.25, d=0.45, drill=0.2)
    c.gnd('R29', '2', 0.0, -0.8, w=0.25, d=0.45, drill=0.2)
    c.P('TP3', -2.5, -7.5, 0, 'B')                        # VBAT, inside the VBAT copper

    # ---- battery fuse U13 (TPS259531, 2 x 2 mm) on the display side, straight under the VSYS vias --------------
    # turned so that IN (pins 3, 4) faces the vias and OUT (pin 5) faces the In2 VSYS_LIM area:
    #   top row    dVdt  EN  IN  IN        bottom row    GND  ILM  FLT  OUT
    c.P('U13', 3.8, 10.3, 270, 'B')
    c.T('VSYS', [(4.1, 8.65), (4.9, 8.65)], 0.6, Bk)
    c.T('VSYS', [(4.5, 7.9), (4.5, 8.65), (4.3, 8.9), (4.3, 9.35)], 0.6, Bk)
    c.two('C27', 5.55, 9.6, 'U', 'B')                      # input capacitor at IN
    c.T('VSYS', [(4.9, 8.65), ('C27', '1')], 0.4, Bk)
    c.gnd('C27', '2', 0.0, 0.8, w=0.3, d=0.45, drill=0.2)
    c.P('TP2', 4.8, 6.1, 0, 'B')
    c.T('VSYS', [(4.5, 7.9), ('TP2', '1')], 0.4, Bk)
    for dx in (-0.5, 0.0, 0.5):                           # in the exposed pad (1.6 x 0.9 mm as turned, about 0.3 W at 3 A)
        c.V('GND', 3.8 + dx, 10.3, 0.45, 0.2)
    c.T('GND', [('U13', '8'), (3.3, 10.6)], 0.25, Bk)
    # current limit: R66 right at ILM
    c.two('R66', 3.3, 13.1, 'U', 'B')
    c.T('BATT_ILIM', [('U13', '7'), ('R66', '1')], 0.15, Bk)
    c.T('GND', [('R66', '2'), (2.5, 13.3)], 0.25, Bk)
    c.V('GND', 2.5, 13.3, 0.45, 0.2)
    # FLT: a stub for the router (pull-up R67 and module pin 58)
    c.T('BATT_OC_N', [('U13', '6'), (4.05, 12.4)], 0.15, Bk)
    # OUT: four vias into the In2 VSYS_LIM area
    c.T('VSYS_LIM', [('U13', '5'), (4.6, 11.6), (5.3, 11.9), (5.3, 13.5)], 0.5, Bk)
    c.T('VSYS_LIM', [(5.3, 12.7), (4.5, 13.1)], 0.5, Bk)
    for x, y in ((5.3, 11.9), (5.3, 12.7), (5.3, 13.5), (4.5, 13.1)):
        c.V('VSYS_LIM', x, y)
    c.P('TP17', 4.4, 15.0, 0, 'B')                        # inside the display-side VSYS_LIM area
    c.T('VSYS_LIM', [(5.3, 13.5), (5.3, 15.0)], 0.6, Bk)
    # enable: R90 from VSYS; C90, R91 (both DNP) are the hard power-cycle option, see carrier_design.py
    c.two('R90', 3.6, 7.6, 'R', 'B')
    c.T('VSYS', [(4.5, 7.9), ('R90', '1')], 0.2, Bk)
    c.T('FUSE_EN', [('U13', '2'), (3.55, 8.1), ('R90', '2')], 0.15, Bk)
    c.two('C90', 1.6, 7.6, 'R', 'B')
    c.T('FUSE_EN', [('R90', '2'), ('C90', '1')], 0.15, Bk)
    c.gnd('C90', '2', -0.8, 0.0, w=0.25, d=0.45, drill=0.2)
    c.two('R91', 2.7, 6.0, 'D', 'B')
    c.T('FUSE_EN', [('R91', '1'), (2.7, 7.6)], 0.15, Bk)
    # charge LED on the component side beside the inductor, fed from the SYS copper
    c.two('R15', 5.2, 6.9, 'D')
    c.T('VSYS', [(4.5, 7.9), ('R15', '1')], 0.3)
    c.two('D1', 5.2, 4.45, 'U')                            # pad 1 = cathode (CHG_STAT), pad 2 = anode
    c.T('CHG_LED_A', [('R15', '2'), ('D1', '2')], 0.2)
    return c


def gauge(B, x, y):
    """MAX17048 fuel gauge (U4) on the display side beside the battery connector, so that CELL/VDD see the pack
    voltage at the connector and not after the charge-current path.  Turned so that CELL/VDD face the VBAT copper
    above it:  top row 1 2 3 4 (GND VDD CELL GND), bottom row 8 7 6 5 (SDA, SCL, QSTRT = GND, ALRT)."""
    c = Cell(B, x, y)
    c.P('U4', 0, 0, 270, 'B')
    c.T('VBAT', [('U4', '2'), (-0.25, -1.7), (0.25, -1.7), ('U4', '3')], 0.25, Bk)
    c.T('VBAT', [(0.0, -1.7), (0.0, -3.4)], 0.25, Bk)      # ends inside the VBAT copper at J10 pin 1
    c.two('C19', 0.75, -2.1, 'L', 'B')
    c.gnd('C19', '2', 0.8, 0.0, w=0.25, d=0.45, drill=0.2)
    for pin in ('1', '4', '6'):
        px, py = c.rel('U4', pin)
        c.T('GND', [(px, py), (px, py * 0.6), (px * 0.5, py * 0.3)], 0.2, Bk)
    c.V('GND', 0.0, 0.0, 0.45, 0.2)                       # in the exposed pad
    for pin, net, vy in (('5', 'GAUGE_INT', 1.9), ('7', 'I2C_B_SCL', 1.9), ('8', 'I2C_B_SDA', 2.5)):
        px, py = c.rel('U4', pin)
        c.T(net, [(px, py), (px, vy)], 0.15, Bk)
        c.V(net, px, vy, 0.45, 0.2)
    px, _ = c.rel('U4', '5')
    c.two('R16', px + 1.5, 1.9, 'L', 'B')                # ALRT pull-up; the router brings +3V3
    c.T('GAUGE_INT', [(px, 1.9), ('R16', '1')], 0.15, Bk)
    return c


def boost(B, ox, oy):
    """TPS61230 (U5) turned so that VOUT and SW face the module and the control pins face the board edge.

    Seen from the component side:   top    PG VOUT VOUT SW SW        bottom   SS FB HYS EN VIN
    TI SLVSAQ2C section 11: the output capacitors sit right at VOUT with their ground ends on vias into the plane
    that the exposed pad (PGND) is stitched to; SW is one short piece of copper; the feedback divider is on the
    quiet side and senses +5V at the far end of the output copper.
    """
    c = Cell(B, ox, oy)
    c.P('U5', 0, 0, -90)
    # output: pins 3/4 -> C22, C23, C24 in a row, +5V ends toward the IC
    for i, ref in enumerate(('C22', 'C23', 'C24')):
        c.two(ref, -0.25 - 2.0 * i, -4.25, 'D')
    c.T('+5V', [(-0.25, -1.48), (-0.25, -3.3)], 0.5)
    c.T('+5V', [('C22', '1'), ('C24', '1'), (-5.4, -3.3)], 1.0)
    c.T('GND', [('C22', '2'), ('C24', '2')], 0.9)
    for x in (-0.25, -2.25, -4.25):                        # one via each: more would cut the +5V copper behind them
        c.T('GND', [(x, -5.2), (x, -6.2)], 0.4)
        c.V('GND', x, -6.2)
    # +5V to the module: three vias into the +5V copper on the display side, which runs to the fan-out vias of
    # module pins 77-87 (carrier_pcb draws that area)
    c.T('+5V', [(-5.4, -3.3), (-5.4, -2.4), (-4.65, -2.4)], 0.5)
    for x, y in ((-5.4, -3.3), (-5.4, -2.4), (-4.65, -2.4)):
        c.V('+5V', x, y)
    # SW: pins 1/2 -> L2
    c.P('L2', 4.5, 0.0, 90)
    c.T('BOOST_SW', [('U5', '1'), (1.0, -2.0)], 0.25)
    c.T('BOOST_SW', [('U5', '2'), (0.5, -2.0)], 0.25)
    c.T('BOOST_SW', [(0.5, -2.0), (3.6, -2.0)], 0.5)
    # VIN: pin 10 -> L2 pad 1, C21, three vias into the In2 VSYS_LIM area
    c.T('VSYS_LIM', [(1.0, 1.7), (1.4, 2.1), (3.6, 2.1)], 0.4)
    c.two('C21', 3.9, 4.85, 'L')
    c.T('VSYS_LIM', [(2.91, 2.1), (2.91, 4.5)], 0.4)
    c.gnd('C21', '2', 1.05, 0.0)
    c.T('VSYS_LIM', [(5.2, 1.85), (7.3, 1.85)], 1.2)       # six vias for up to 3 A, on copper as wide as the pad allows
    for x in (6.4, 7.3):
        c.T('VSYS_LIM', [(x, 1.0), (x, 2.7)], 0.6)
        for y in (1.0, 1.85, 2.7):
            c.V('VSYS_LIM', x, y)
    # under-voltage divider: R17 from VIN to EN, R23 from EN to HYS, R24 from HYS to ground
    c.two('R23', 0.5, 2.75, 'R')
    c.T('BOOST_HYS', [('U5', '8'), ('R23', '2')], 0.15)
    c.T('BOOST_EN', [('U5', '9'), (0.5, 2.3), ('R23', '1')], 0.15)
    c.two('R17', 2.4, 3.35, 'R')                          # pad 1 (VIN side) sits on the VIN track to C21
    c.T('BOOST_EN', [('R23', '1'), ('R17', '2')], 0.15)
    c.two('R24', -0.01, 4.2, 'U')
    c.T('BOOST_HYS', [('R23', '2'), ('R24', '1')], 0.15)
    c.gnd('R24', '2', 0.0, 0.75, w=0.25, d=0.45, drill=0.2)
    # soft start
    c.two('C20', -3.3, 2.6, 'R')
    c.T('BOOST_SS', [('U5', '6'), (-1.0, 2.6), ('C20', '1')], 0.15)
    c.gnd('C20', '2', -0.75, 0.0, w=0.25, d=0.45, drill=0.2)
    # feedback divider R18 (C26 across it, DNP) / R19, sensed at the far end of the output copper
    c.two('R19', -1.45, 3.2, 'R')
    c.two('R18', -1.45, 4.15, 'L')
    c.two('C26', -1.45, 5.1, 'L')
    c.T('BOOST_FB', [('U5', '7'), (-0.5, 2.9), ('R19', '1'), ('R18', '2'), ('C26', '2')], 0.15)
    c.T('GND', [('R19', '2'), (-2.9, 3.55)], 0.25)
    c.V('GND', -2.9, 3.55, 0.45, 0.2)
    c.T('+5V', [('R18', '1'), ('C26', '1')], 0.15)
    c.T('+5V', [(-5.4, -2.4), (-5.4, 4.6), (-1.96, 4.6)], 0.15)
    # power good: pull-up R20 and a test pad on the display side
    c.two('R20', -3.1, -2.05, 'R')
    c.T('BOOST_PG', [('U5', '5'), (-1.0, -2.05), ('R20', '1')], 0.15)
    c.T('+5V', [('R20', '2'), (-3.61, -2.9)], 0.2)
    c.T('BOOST_PG', [('R20', '1'), (-2.59, -1.2)], 0.15)
    c.V('BOOST_PG', -2.59, -1.2, 0.45, 0.2)
    c.P('TP6', -3.5, -0.2, 0, 'B')
    c.T('BOOST_PG', [(-2.59, -1.2), ('TP6', '1')], 0.15, Bk)
    return c


def offset(pts, d):
    """the polyline shifted by d to the left of its direction of travel (board coordinates, y down), mitred"""
    import math
    lines = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        L = math.hypot(x1 - x0, y1 - y0)
        nx, ny = (y1 - y0) / L * d, -(x1 - x0) / L * d
        lines.append(((x0 + nx, y0 + ny), (x1 + nx, y1 + ny)))
    out = [lines[0][0]]
    for (a, b), (c, e) in zip(lines, lines[1:]):
        x1, y1, x2, y2, x3, y3, x4, y4 = *a, *b, *c, *e
        den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
        out.append((x1 + t * (x2 - x1), y1 + t * (y2 - y1)))
    out.append(lines[-1][1])
    return out


def dsi(B, W=0.1, GAP=0.15):
    """The three MIPI DSI pairs (clock, lane 0, lane 1) from the module connector J1B to the panel connector J4, as
    edge-coupled pairs on the component side straight over the In1 ground plane.

    J1B has the pairs in the order D0, D1, CLK; J4 wants D1, CLK, D0.  D0 stays on the outside of both bends; the
    clock pair changes places with D1 by dropping to the display side for 2 mm right at J1B.  P is always the left
    track in the direction of travel, so what it gains on the first bend it loses on the second.
    Width and gap: 100 ohm by impedance.py for 3313 prepreg (see carrier_pcb.CLASSES).
    """
    d = (W + GAP) / 2
    c = 0.5                                               # chamfer
    def bumps(pts, n, sign, x0, h=0.3, flat=0.3, gap=0.3):
        """n small detours in the first (eastward) stretch of a line, away from its partner: each adds 0.83 h"""
        y = pts[0][1]
        out = [pts[0]]
        for i in range(n):
            x = x0 + i * (2 * h + flat + gap)
            out += [(x, y), (x + h, y + sign * h), (x + h + flat, y + sign * h), (x + 2 * h + flat, y)]
        return out + pts[1:]

    def run(net, y_lane, x_vert, y_j4, x_start, lead_p, lead_n, tail_p, tail_n, comp=(0, 0), x_comp=47.0):
        """comp = (bumps on P, bumps on N): length compensation, see docs/carrier-board.md for the measured lengths"""
        cl = [(x_start, y_lane), (x_vert - c, y_lane), (x_vert, y_lane + c), (x_vert, y_j4 - c), (x_vert + c, y_j4), (62.15, y_j4)]
        B.track(net + '_P', lead_p + bumps(offset(cl, d), comp[0], -1, x_comp) + tail_p, W)
        B.track(net + '_N', lead_n + bumps(offset(cl, -d), comp[1], 1, x_comp) + tail_n, W)
    v = lambda net, near: B.via_xy(net, near)
    # lane 1: top lane, right-hand vertical
    (px, py), (nx, ny) = v('DSI_D1_P', (44, 18)), v('DSI_D1_N', (44, 18))
    jp, jn = v('DSI_D1_P', (63, 32)), v('DSI_D1_N', (63, 32))
    run('DSI_D1', 19.36, 58.79, 32.3, 44.6, [(px, py), (px, 19.0), (px + 0.25, 19.25)], [(nx, ny), (nx, 19.22), (nx + 0.25, 19.47)],
        [(62.3, jp[1]), jp], [(62.3, jn[1]), jn], comp=(0, 3), x_comp=45.2)
    # clock: on the display side from its J1B vias to two new vias below lane 1, then the middle lane
    (px, py), (nx, ny) = v('DSI_CLK_P', (45, 18)), v('DSI_CLK_N', (45, 18))
    jp, jn = v('DSI_CLK_P', (63, 34)), v('DSI_CLK_N', (63, 34))
    B.track('DSI_CLK_P', [(px, py), (px, 20.2)], W, Bk)
    B.track('DSI_CLK_N', [(nx, ny), (nx, 20.4), (nx - 0.15, 20.71)], W, Bk)
    B.via('DSI_CLK_P', px, 20.2); B.via('DSI_CLK_N', nx - 0.15, 20.71)
    run('DSI_CLK', 20.6, 58.19, 33.8, 45.9, [(px, 20.2), (px + 0.29, 20.49)], [(nx - 0.15, 20.71)],
        [(62.3, jp[1]), jp], [(62.3, jn[1]), jn], comp=(9, 0), x_comp=46.4)
    # lane 0: bottom lane, left-hand vertical
    (px, py), (nx, ny) = v('DSI_D0_P', (43, 18)), v('DSI_D0_N', (43, 18))
    jp, jn = v('DSI_D0_P', (63, 35)), v('DSI_D0_N', (63, 35))
    run('DSI_D0', 21.31, 57.59, 35.3, 43.4, [(px, py), (px, 20.9), (px + 0.3, 21.2)], [(nx, ny), (nx, 21.12), (nx + 0.3, 21.42)],
        [(62.3, jp[1]), jp], [(62.3, jn[1]), jn], comp=(0, 3), x_comp=44.0)


def usb(B, W=0.12, GAP=0.12):
    """USB-C receptacle J2, ESD array U2 and the USB 2.0 pair to the module, all on the component side over the In1
    ground plane (the pair), with the small parts on the display side under the connector.

    J2 has D+ on A6/B6 and D- on A7/B7, interleaved.  D+ is joined by a loop in front of the pads; D- by two vias and
    1 mm of track on the display side.  The pair runs through U2 (in at pins 6/4, out at pins 1/3: no stub), then
    under the module to the J1B fan-out vias.  The DNP adapter-detection links R21/R22 sit directly on the pair's
    vias at J2.  Width and gap come from carrier_pcb.CLASSES (calculated with impedance.py for the 3313 stack-up).
    """
    c = Cell(B, 0, 0)
    d = (W + GAP) / 2
    pad = lambda n: B.pad_xy('J2', n)
    c.P('U2', 3.8, 25.4, -90)                             # bottom row 4 5 6 (D-, bias, D+), top row 3 2 1 (D-, GND, D+)
    # --- at the connector
    c.T('USB_DP', [pad('A6'), (8.5, 32.75), (8.5, 33.75), pad('B6')], W)
    c.V('USB_DP', 8.5, 33.75, 0.45, 0.2)                  # only for R21
    for n in ('B7', 'A7'):
        c.T('USB_DM', [pad(n), (7.9, pad(n)[1])], W)
        c.V('USB_DM', 7.9, pad(n)[1], 0.45, 0.2)
    c.T('USB_DM', [(7.9, 32.25), (7.9, 33.25)], W, Bk)
    c.two('R22', 8.5, 32.75, 'L', 'B')                    # DNP: USB_DM -> CHG_DM
    c.two('R21', 9.1, 34.0, 'L', 'B')                     # DNP: USB_DP -> CHG_DP
    c.T('USB_DP', [(8.5, 33.75), ('R21', '1')], W, Bk)
    # --- J2 -> U2: east, north, west into the bottom row of U2 (D+ is the upper lane and stops first)
    cl = [(8.8, 32.37), (9.62 - 0.4, 32.37), (9.62, 32.37 - 0.4), (9.62, 27.62 + 0.4), (9.62 - 0.4, 27.62), (5.2, 27.62)]
    c.T('USB_DM', [(7.9, 32.25)] + offset(cl, d) + [(3.1, 27.62 + d), (2.85, 27.45), ('U2', '4')], W)
    c.T('USB_DP', [(8.5, 32.75)] + offset(cl, -d) + [(4.95, 27.62 - d), (4.75, 27.3), ('U2', '6')], W)
    # --- through U2
    c.T('USB_DP', [('U2', '6'), ('U2', '1')], W)
    c.T('USB_DM', [('U2', '4'), ('U2', '3')], W)
    c.V('ESD_BIAS', 3.8, 25.75, 0.45, 0.2)
    c.T('ESD_BIAS', [('U2', '5'), (3.8, 25.75)], 0.2)
    c.two('C25', 4.75, 25.75, 'L', 'B')
    c.T('ESD_BIAS', [(3.8, 25.75), ('C25', '1')], 0.2, Bk)
    c.gnd('C25', '2', 0.75, 0.0, w=0.25, d=0.45, drill=0.2)
    c.V('GND', 3.8, 25.05, 0.45, 0.2)
    c.T('GND', [('U2', '2'), (3.8, 25.05)], 0.2)
    # --- U2 -> module: north out of the top row, east under the module, north into the J1B fan-out vias
    vm, vp = B.via_xy('USB_DM', (28, 18)), B.via_xy('USB_DP', (28, 18))
    cl = [(5.4, 23.52), (28.3 - 0.4, 23.52), (28.3, 23.52 - 0.4), (28.3, 19.7)]
    c.T('USB_DM', [('U2', '3'), (2.85, 23.65), (3.1, 23.4)] + offset(cl, d) + [(vm[0], 19.45), vm], W)
    c.T('USB_DP', [('U2', '1'), (5.05, 23.64)] + offset(cl, -d) + [(vp[0], 19.45), vp], W)
    # --- VBUS, ground, CC
    for n, gy in (('A4', -1.05), ('A9', 0.95)):
        x, y = pad(n)
        c.T('VBUS', [(x, y), (8.75, y)], 0.5)
        c.V('VBUS', 8.0, y); c.V('VBUS', 8.75, y)
        gx, g0 = pad('A1' if gy < 0 else 'A12')
        c.T('GND', [(gx, g0), (8.0, y + gy)], 0.4)
        c.V('GND', 8.0, y + gy)
    for n, ref, vy in (('A5', 'R10', 31.6), ('B5', 'R11', 34.75)):
        c.T(B.fps['J2'].FindPadByNumber(n).GetNetname(), [pad(n), (7.5, pad(n)[1]), (8.0, vy)], 0.15)
        c.V(B.fps['J2'].FindPadByNumber(n).GetNetname(), 8.0, vy, 0.45, 0.2)
        c.two(ref, 6.8, vy, 'R', 'B')                     # Rd 5.1k to ground (the display-side pour)
        c.T(B.fps['J2'].FindPadByNumber(n).GetNetname(), [(8.0, vy), (ref, '1')], 0.15, Bk)
    c.P('TP1', 10.0, 30.55, 0, 'B')
    c.T('VBUS', [(8.75, 30.55), ('TP1', '1')], 0.3, Bk)
    c.P('D5', 3.8, 40.5, 0)
    c.T('VBUS', [('D5', '1'), (2.4, 39.2)], 0.5)
    c.V('VBUS', 2.4, 39.2)
    c.gnd('D5', '2', 1.1, 0.0)


def sd_links(B, W=0.1):
    """SD_D0 and SD_D2 from their J1A fan-out vias to the fan-out vias of the ESD arrays U11/U12, on the display
    side.  These two pins sit at the crowded end of the J1A via field and the router could not get them out once
    their neighbours were in; laid first, the router works around them.  The other SD lines are routed by it."""
    for net, ref, pin, lane in (('SD_D0', 'U11', '4', 54.1), ('SD_D2', 'U12', '1', 55.4)):
        vx, vy = B.via_xy(net, (40.5, 52.0))
        tx, ty = B.via_xy(net, B.pad_xy(ref, pin))
        k = abs(lane - ty)
        B.track(net, [(vx, vy), (vx, lane - 0.3), (vx - 0.3, lane), (22.0 + k, lane), (22.0, ty), (tx, ty)], W, pcbnew.B_Cu)


def touch(B):
    """Touch connector J5 (display side, left strip).  It is fenced in: In2 and the display side around it are
    VSYS_LIM copper and the module side above it carries the backlight.  Its five signals therefore leave by hand:
    from each pad toward the board edge, down past the connector's ground pad, and back under the connector
    through the 1.8 mm gap kept in the VSYS_LIM strap (carrier_pcb, y 50.1-51.9), ending just west of the strap
    where the router takes over on open board.  Innermost column and top row belong to the lowest pad."""
    lanes = (('7', 70.0, 50.45, 0.1), ('6', 70.25, 50.7, 0.1), ('5', 70.5, 50.95, 0.1), ('4', 70.75, 51.2, 0.1),
             ('3', 71.05, 51.5, 0.15))
    for k, (pad, x, y, w) in enumerate(lanes):
        px, py = B.pad_xy('J5', pad)
        net = B.fps['J5'].FindPadByNumber(pad).GetNetname()
        ye = 49.65 + 0.65 * k                      # west of the strap the five fan out to 0.65 mm pitch, so that the
        xb = 63.9 - 0.3 * (2 - abs(k - 2))        # the outer ones turn first
        B.track(net, [(px, py), (x, py), (x, y), (xb, y), (xb - abs(ye - y), ye), (62.3, ye)], w, Bk)   # router can reach each end
    # ground: pad 8 and the two hold-down pads are cut off from the pour by these tracks and by the strap
    px, py = B.pad_xy('J5', '8')
    B.track('GND', [(px, py), (px - 0.2, py + 0.9)], 0.2, Bk)
    B.via('GND', px - 0.2, py + 0.9, 0.45, 0.2)
    for mp in B.fps['J5'].Pads():
        if mp.GetNumber() == 'MP':
            mx, my = pcbnew.ToMM(mp.GetPosition().x), pcbnew.ToMM(mp.GetPosition().y)
            if my < 46:        # upper one: L3's pads are on the other side of the board here; the via goes between them
                B.via('GND', mx + 0.3, my, 0.45, 0.2)
            else:
                B.track('GND', [(mx, my), (mx - 1.0, my)], 0.2, Bk)
                B.via('GND', mx - 1.0, my, 0.45, 0.2)


def backlight(B, ox, oy):
    """TPS61169 LED driver (U6), laid out like the other switchers.  U6 is turned so that SW, GND and FB face the
    inductor below it and VIN and CTRL face up:

        C43 (input)   R43 (CTRL pull-down)
        VIN   CTRL
        [  U6   ]
        SW  GND  FB -- R42 (current sense) -- GND
        |
        L3 (SW pad on the left)        D4 stands left of that pad, C42 (output) below D4

    VIN and the inductor's other pad take VSYS_LIM from the In2 area through their own vias; every ground return
    is a via into the In1 plane next to the part.  LED_A and LED_K go on to the panel connector by the router."""
    c = Cell(B, ox, oy)
    for rot in (0, 90, 180, 270):
        c.P('U6', 0, 0, rot)
        x, y = c.rel('U6', '1')
        if x < -0.3 and y > 0.3:
            break
    else:
        raise RuntimeError('U6')
    c.P('L3', 0.5, 4.2, 0)
    if c.rel('L3', '2')[0] > 0:
        c.P('L3', 0.5, 4.2, 180)
    lx, ly = c.rel('L3', '2')
    c.T('BL_SW', [('U6', '1'), (lx + 0.35, ly - 1.5)], 0.3)
    c.two('D4', lx - 2.1, ly - 0.6, 'D')                       # anode (pad 2) up, level with the top of L3's SW pad
    dx, dy = c.rel('D4', '2')
    c.T('BL_SW', [(lx, dy), (dx, dy)], 0.4)
    c.two('C42', lx - 2.1, ly + 3.0, 'U')                      # output capacitor right under the diode
    c.T('LED_A', [('D4', '1'), ('C42', '1')], 0.4)
    c.gnd('C42', '2', 0.0, 0.9, w=0.4)
    vx, vy = c.rel('L3', '1')
    for d in (-0.9, 0.3):                                      # inductor supply: two vias into the In2 area
        c.T('VSYS_LIM', [(vx, vy + d), (vx + 1.15, vy + d)], 0.4)
        c.V('VSYS_LIM', vx + 1.15, vy + d)
    gx, gy = c.rel('U6', '2')
    c.T('GND', [(gx, gy), (gx, gy + 0.8)], 0.25)
    c.V('GND', gx, gy + 0.8, 0.45, 0.2)
    c.V('GND', gx, gy - 0.95, 0.45, 0.2)                   # and one under the part, between the pin rows
    c.T('GND', [(gx, gy), (gx, gy - 0.95)], 0.25)
    fx, fy = c.rel('U6', '3')
    c.two('R42', fx + 1.8, fy, 'L')
    c.T('LED_K', [('U6', '3'), ('R42', '1')], 0.2)
    c.gnd('R42', '2', 0.7, 0.0, w=0.2, d=0.45, drill=0.2)
    px, py = c.rel('U6', '5')
    c.two('C43', px + 0.48, py - 1.25, 'L')
    c.T('VSYS_LIM', [('U6', '5'), ('C43', '1')], 0.25)
    c.T('VSYS_LIM', [('C43', '1'), (px - 0.85, py - 1.25)], 0.25)
    c.V('VSYS_LIM', px - 0.85, py - 1.25, 0.45, 0.2)
    c.gnd('C43', '2', 0.75, 0.0, w=0.2, d=0.45, drill=0.2)
    qx, qy = c.rel('U6', '4')
    c.two('R43', qx + 1.8, qy, 'L')
    c.T('BL_PWM', [('U6', '4'), ('R43', '1')], 0.15)
    c.gnd('R43', '2', 0.7, 0.0, w=0.2, d=0.45, drill=0.2)
    return c
