"""Generate the HackerSlide project library: hardware/lib/hackerslide.kicad_sym + hackerslide.pretty/.

Every symbol/footprint here is drawn by this script from the cited datasheet dimensions (no vendor files are
copied).  Sources are recorded in hardware/lib/SOURCES.md.
"""
import json
import os

from kigen import uid
from sexpr import quote

HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.join(HERE, '..', 'lib')
FP = os.path.join(LIB, 'hackerslide.pretty')

# CM4 pin names (Raspberry Pi CM4 datasheet, section "Pinout"); used as names on the module symbols.
CM4 = {int(k): v for k, v in json.load(open(os.path.join(HERE, 'cm4_pin_names.json'))).items()}


# ----------------------------------------------------------------------------------------------------------
# symbols
def box_symbol(name, left, right, ref='U', descr='', footprint='', datasheet='~', width=None, top=(), bottom=()):
    """left/right: lists of (number, name, etype) or None for a gap. Pins 2.54 apart, length 2.54."""
    n = max(len(left), len(right))
    h = (n + 1) * 2.54
    maxname = max([len(p[1]) for p in left + right if p] + [4])
    w = width or max(10.16, round((maxname * 1.27 * 2 + 5.08) / 2.54) * 2.54)
    if len(top) or len(bottom):
        w = max(w, (max(len(top), len(bottom)) + 1) * 2.54)
    x0, y0 = -w / 2, h / 2
    pins = []

    def pin(num, pname, etype, x, y, ang):
        hide = ' (hide yes)' if etype == 'passive_hidden' else ''
        et = 'passive' if etype == 'passive_hidden' else etype
        pins.append(f'\t\t\t(pin {et} line (at {x:.2f} {y:.2f} {ang}) (length 2.54){hide} '
                    f'(name {quote(pname)} (effects (font (size 1.016 1.016)))) (number {quote(num)} (effects (font (size 1.016 1.016)))))')

    for i, p in enumerate(left):
        if p:
            pin(p[0], p[1], p[2], x0 - 2.54, y0 - 2.54 * (i + 1), 0)
    for i, p in enumerate(right):
        if p:
            pin(p[0], p[1], p[2], -x0 + 2.54, y0 - 2.54 * (i + 1), 180)
    for i, p in enumerate(top):
        if p:
            pin(p[0], p[1], p[2], x0 + 2.54 * (i + 1), y0 + 2.54, 270)
    for i, p in enumerate(bottom):
        if p:
            pin(p[0], p[1], p[2], x0 + 2.54 * (i + 1), -y0 - 2.54, 90)
    return (f'\t(symbol {quote(name)} (pin_names (offset 1.016)) (exclude_from_sim no) (in_bom yes) (on_board yes)\n'
            f'\t\t(property "Reference" {quote(ref)} (at {x0:.2f} {y0 + 1.27:.2f} 0) (effects (font (size 1.27 1.27)) (justify left bottom)))\n'
            f'\t\t(property "Value" {quote(name)} (at {x0:.2f} {-y0 - 1.27:.2f} 0) (effects (font (size 1.27 1.27)) (justify left top)))\n'
            f'\t\t(property "Footprint" {quote(footprint)} (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))\n'
            f'\t\t(property "Datasheet" {quote(datasheet)} (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))\n'
            f'\t\t(property "Description" {quote(descr)} (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))\n'
            f'\t\t(symbol {quote(name + "_0_1")}\n\t\t\t(rectangle (start {x0:.2f} {y0:.2f}) (end {-x0:.2f} {-y0:.2f}) '
            f'(stroke (width 0.254) (type default)) (fill (type background)))\n\t\t)\n'
            f'\t\t(symbol {quote(name + "_1_1")}\n' + '\n'.join(pins) + '\n\t\t)\n\t)\n')


def cm4_type(n, name):
    if name == 'GND':
        return 'power_in'
    if name.startswith('+5V'):
        return 'power_in'
    if n in (84, 88):            # one power_out per rail (86/90 are the same rails)
        return 'power_out'
    if n in (86, 90):
        return 'passive'
    return 'bidirectional'


def cm4_symbol(sym, first):
    left, right = [], []
    for k in range(first, first + 100):
        nm = CM4[k]
        p = (str(k - first + 1), f'{k} {nm}', cm4_type(k, nm))
        (left if k % 2 else right).append(p)
    return box_symbol(sym, left, right, ref='J',
                      descr=f'CM4-format module, board-to-board connector pins {first}-{first + 99} '
                            '(pin names per Raspberry Pi CM4 datasheet; symbol pin number = DF40 pad number)',
                      footprint='hackerslide:Hirose_DF40C-100DS-0.4V_2x50_P0.4mm')


def symbols():
    out = [cm4_symbol('CM4_Conn_A_1-100', 1), cm4_symbol('CM4_Conn_B_101-200', 101)]
    P, B, I, O, PI, PO, NC = 'passive', 'bidirectional', 'input', 'output', 'power_in', 'power_out', 'no_connect'
    # ES8316 (Everest datasheet rev 6.0, pin table section 2)
    out.append(box_symbol('ES8316', [
        ('1', 'CCLK', I), ('32', 'CDATA', B), ('31', 'CE', I), None, ('2', 'MCLK', I), ('6', 'SCLK', B),
        ('8', 'DLRCK', B), ('7', 'DSDIN', I), ('9', 'ASDOUT', O), None, ('10', 'GPIO1', B), ('11', 'GPIO2', B),
        ('12', 'GPIO3', B), None, ('3', 'DVDD', PI), ('4', 'PVDD', PI), ('22', 'AVDD', PI), ('14', 'CPVDD', PI)],
        [('20', 'LOUT', O), ('19', 'ROUT', O), None, ('30', 'LIN1', I), ('29', 'RIN1', I), ('28', 'LIN2', I),
         ('27', 'RIN2', I), ('26', 'MICBIAS', PO), None, ('21', 'DACVREF', P), ('24', 'ADCVREF', P), ('25', 'VMID', P),
         ('15', 'CPTOP', P), ('16', 'CPBOT', P), ('13', 'CPVSSP', P), ('18', 'CPGNDREF', P), None,
         ('5', 'DGND', PI), ('23', 'AGND', PI), ('17', 'CPGND', PI), ('33', 'EP', P)],
        descr='Everest ES8316 low-power audio codec with headphone driver (mainline Linux: snd-soc-es8316)',
        footprint='Package_DFN_QFN:QFN-32-1EP_4x4mm_P0.4mm_EP2.9x2.9mm',
        datasheet='https://www.lcsc.com/datasheet/lcsc_datasheet_1811151643_Everest-semi-Everest-Semiconductor-ES8316_C365735.pdf'))
    # TPS61169 (TI SNVSA40B, Table 4-1)
    out.append(box_symbol('TPS61169', [('5', 'VIN', PI), ('4', 'CTRL', I)], [('1', 'SW', P), ('3', 'FB', I), ('2', 'GND', PI)],
                          descr='TI TPS61169 white-LED boost driver, 38 V switch, FB 204 mV',
                          footprint='Package_TO_SOT_SMD:SOT-353_SC-70-5',
                          datasheet='https://www.ti.com/lit/ds/symlink/tps61169.pdf'))
    # TCA8418 (TI SCPS215G, RTW pin table): pins 1-8 = ROW7..ROW0, 9-18 = COL0..COL9
    out.append(box_symbol('TCA8418RTW',
        [('22', 'SDA', B), ('23', 'SCL', I), ('24', '~{INT}', 'open_collector'), ('20', '~{RESET}', I), None,
         ('21', 'VCC', PI), ('19', 'GND', PI), ('25', 'EP', P)] + [None] * 2,
        [(str(8 - r), f'ROW{r}', B) for r in range(8)] + [None] + [(str(9 + c), f'COL{c}', B) for c in range(10)],
        descr='TI TCA8418 I2C keypad scanner, 8x10 matrix, address 0x34 (mainline Linux: tca8418_keypad)',
        footprint='Package_DFN_QFN:WQFN-24-1EP_4x4mm_P0.5mm_EP2.45x2.45mm',
        datasheet='https://www.ti.com/lit/ds/symlink/tca8418.pdf'))
    # MAX17048 (Maxim 19-6171 Rev 7, TDFN pin table)
    out.append(box_symbol('MAX17048',
        [('2', 'CELL', P), ('3', 'VDD', PI), ('1', 'CTG', P), ('4', 'GND', PI), ('9', 'EP', P)],
        [('8', 'SDA', B), ('7', 'SCL', I), ('5', '~{ALRT}', 'open_collector'), ('6', 'QSTRT', I)],
        descr='Maxim MAX17048 1-cell ModelGauge fuel gauge, address 0x36 (mainline Linux: max17040_battery)',
        footprint='Package_DFN_QFN:TDFN-8-1EP_2x2mm_P0.5mm_EP0.8x1.2mm',
        datasheet='https://www.analog.com/media/en/technical-documentation/data-sheets/MAX17048-MAX17049.pdf'))
    # TPS2553 (TI SLVS841, DBV pin table: 1 IN, 2 GND, 3 EN (active high), 4 FAULT, 5 ILIM, 6 OUT)
    out.append(box_symbol('TPS2553DBV', [('1', 'IN', PI), ('3', 'EN', I), ('5', 'ILIM', P), ('2', 'GND', PI)],
                          [('6', 'OUT', PO), ('4', '~{FAULT}', 'open_collector')],
                          descr='TI TPS2553 adjustable current-limited power switch, 75 mA - 1.7 A, 85 mOhm, auto-retry',
                          footprint='Package_TO_SOT_SMD:SOT-23-6', datasheet='https://www.ti.com/lit/ds/symlink/tps2553.pdf'))
    # SHOU HAN PJ-342 3.5 mm 4-pole jack with two switches (terminal numbers from the SHOU HAN drawing).
    # Pole assignment is INFERRED from contact depth in the drawing: TODO(verify) with a sample.
    out.append(box_symbol('PJ-342',
        [('3', 'TIP', P), ('4', 'TIP_SW', P), ('6', 'RING1', P), ('7', 'RING1_SW', P)],
        [('2', 'P2_RING2?', P), ('5', 'P5_SLEEVE?', P)], ref='J',
        descr='SHOU HAN PJ-342 3.5 mm TRRS jack, SMD, tip and ring1 normally-closed switches, 4.5 mm high',
        footprint='hackerslide:Jack_3.5mm_SHOUHAN_PJ-342'))
    # Alps SKSWCFE010 / Keystone 5135 key switch: 2 terminals
    out.append(box_symbol('KeySwitch', [('1', 'A', P)], [('2', 'B', P)], ref='SW', width=5.08,
                          descr='Keyboard key contact (Alps SKSWCFE010 tact switch or Keystone 5135 dome footprint)'))
    return ('(kicad_symbol_lib\n\t(version 20241209)\n\t(generator "hackerslide_mklib")\n\t(generator_version "9.0")\n'
            + ''.join(out) + ')\n')


# ----------------------------------------------------------------------------------------------------------
# footprints
def fp_text(name, descr, body, attr='smd', ref_y=-3, val_y=3):
    return (f'(footprint {quote(name)}\n\t(version 20240108)\n\t(generator "hackerslide_mklib")\n\t(layer "F.Cu")\n'
            f'\t(descr {quote(descr)})\n'
            f'\t(property "Reference" "REF**" (at 0 {ref_y} 0) (layer "F.SilkS") (uuid "{uid(name, "ref")}") (effects (font (size 0.8 0.8) (thickness 0.12))))\n'
            f'\t(property "Value" {quote(name)} (at 0 {val_y} 0) (layer "F.Fab") (uuid "{uid(name, "val")}") (effects (font (size 0.8 0.8) (thickness 0.12))))\n'
            f'\t(attr {attr})\n' + body + ')\n')


def rect(layer, x0, y0, x1, y1, w=0.05, tag=''):
    return ''.join(f'\t(fp_line (start {a:.3f} {b:.3f}) (end {c:.3f} {d:.3f}) (stroke (width {w}) (type solid)) (layer "{layer}") '
                   f'(uuid "{uid(tag, layer, a, b, c, d)}"))\n'
                   for (a, b, c, d) in ((x0, y0, x1, y0), (x1, y0, x1, y1), (x1, y1, x0, y1), (x0, y1, x0, y0)))


def df40():
    # Pad geometry: Raspberry Pi CM4 IO board footprint (0.2 x 0.7 mm pads, rows 3.08 mm apart, 0.4 mm pitch),
    # cross-checked with Hirose DF40 catalogue p.3 recommended layout (3.78 outer span / 2.38 inner gap).
    # Hirose note 3: no conductive pattern between the two pad rows (see the keepout in carrier_pcb.py).
    name = 'Hirose_DF40C-100DS-0.4V_2x50_P0.4mm'
    body = ''
    for n in range(1, 101):
        i = (n - 1) // 2
        y = -9.8 + i * 0.4
        x = -1.54 if n % 2 else 1.54
        body += (f'\t(pad "{n}" smd rect (at {x:.2f} {y:.2f}) (size 0.7 0.2) (layers "F.Cu" "F.Paste" "F.Mask") '
                 f'(uuid "{uid(name, n)}"))\n')
    body += rect('F.CrtYd', -2.2, -11.6, 2.2, 11.6, tag=name)
    body += rect('F.Fab', -1.69, -11.3, 1.69, 11.3, w=0.1, tag=name)
    body += f'\t(fp_circle (center -2.3 -9.8) (end -2.2 -9.8) (stroke (width 0.2) (type solid)) (fill none) (layer "F.SilkS") (uuid "{uid(name, "p1")}"))\n'
    return name, fp_text(name, 'Hirose DF40C-100DS-0.4V(51) receptacle, 1.5 mm stack, CM4 module socket. '
                               'Pad 1 at the pin-1 dot. Source: Hirose DF40 catalogue + RPi CM4IO KiCad (geometry only).',
                         body, ref_y=-12.5, val_y=12.5)


def sksw():
    # Alps SKSW series drawing (LCSC C255576 datasheet p.2): lands 0.6 x 1.5 mm, 2.6 mm inner / 3.8 mm outer.
    name = 'SW_Alps_SKSWCFE010_3x2mm'
    body = ''
    for n, x in ((1, -1.6), (2, 1.6)):
        body += f'\t(pad "{n}" smd rect (at {x} 0) (size 0.6 1.5) (layers "F.Cu" "F.Paste" "F.Mask") (uuid "{uid(name, n)}"))\n'
    body += rect('F.Fab', -1.5, -1.0, 1.5, 1.0, w=0.1, tag=name)
    body += rect('F.CrtYd', -2.1, -1.0 - 0.25, 2.1, 1.25, tag=name)
    return name, fp_text(name, 'Alps Alpine SKSWCFE010 3x2 mm 0.6 mm-tall tact switch', body, ref_y=-2, val_y=2)


def dome5135():
    # Keystone 5135 "Mini" four-leg dome (catalogue p.97): 8.4 mm tip to tip, 7.0 mm across the 45 degree flats,
    # feet on an 8.0 mm circle.  Domes are NOT soldered; they sit on the pads under an adhesive retainer.
    # NON-STANDARD LANDS: Keystone draws five 3.0 mm pads, which do not fit the 8.5 x 7.25 mm key pitch (audit
    # K6/K7).  Here the four foot pads are 1.8 mm on the 8.0 mm foot circle, feet on the diagonals.  Foot pads of
    # vertically adjacent keys merge, so pad "1" must be a net shared by the keys above and below (the column).
    # TODO(verify): get the Mini-series land drawing from Keystone before ordering this variant.
    name = 'SW_Keystone_5135_Dome_7mm'
    body = f'\t(pad "2" smd circle (at 0 0) (size 3.0 3.0) (layers "F.Cu" "F.Mask") (uuid "{uid(name, "c")}"))\n'
    for i, (x, y) in enumerate(((2.83, 2.83), (-2.83, 2.83), (2.83, -2.83), (-2.83, -2.83))):
        body += f'\t(pad "1" smd circle (at {x} {y}) (size 1.8 1.8) (layers "F.Cu" "F.Mask") (uuid "{uid(name, i)}"))\n'
    pts = ' '.join(f'(xy {x} {y})' for x, y in ((0.7, 4.2), (4.2, 0.7), (4.2, -0.7), (0.7, -4.2), (-0.7, -4.2), (-4.2, -0.7), (-4.2, 0.7), (-0.7, 4.2)))
    body += f'\t(fp_poly (pts {pts}) (stroke (width 0.05) (type solid)) (fill none) (layer "F.Fab") (uuid "{uid(name, "fab")}"))\n'
    return name, fp_text(name, 'Keystone 5135 four-leg metal dome, NON-STANDARD reduced lands (TODO(verify) against Keystone Mini land '
                               'drawing); unsoldered, hard gold or ENIG finish', body, attr='smd allow_missing_courtyard', ref_y=-4.6, val_y=4.6)


def fh34(n):
    # Hirose FH34SRJ-nS-0.5SH(50): 1.0 mm high, back-flip, top AND bottom contact.  Land pattern from the Hirose
    # FH34 catalogue p.5 ("Recommended PCB mounting pattern", FH34SRJ): signal lands 0.3 x 0.8 on 0.5 pitch,
    # two hold-down lands 0.4 x 0.8 centred 3.3 mm in front of the signal row, E/F from the table.
    # Drawn as in the catalogue view: signal row at the top, FPC opening toward +Y, contact No.1 at +X.
    B = 0.5 * (n - 1)
    E, F = B + 1.6, B + 2.4
    name = f'Hirose_FH34SRJ-{n}S-0.5SH_1x{n:02d}-1MP_P0.50mm_Horizontal'
    body = ''
    for k in range(1, n + 1):
        x = B / 2 - 0.5 * (k - 1)
        body += f'\t(pad "{k}" smd rect (at {x:.3f} 0) (size 0.3 0.8) (layers "F.Cu" "F.Paste" "F.Mask") (uuid "{uid(name, k)}"))\n'
    for i, x in enumerate((-(E + F) / 4, (E + F) / 4)):
        body += f'\t(pad "MP" smd rect (at {x:.3f} 3.3) (size 0.4 0.8) (layers "F.Cu" "F.Paste" "F.Mask") (uuid "{uid(name, "mp", i)}"))\n'
    A = B + 2.5                                   # product length (catalogue Fig.1)
    body += rect('F.Fab', -A / 2, -0.15, A / 2, 3.25, w=0.1, tag=name)
    body += rect('F.CrtYd', -F / 2 - 0.3, -0.75, F / 2 + 0.3, 4.05, tag=name)
    body += rect('F.SilkS', -A / 2 - 0.1, 0.75, A / 2 + 0.1, 2.6, w=0.12, tag=name + 's')
    body += f'\t(fp_circle (center {B / 2 + 0.9:.3f} -0.5) (end {B / 2 + 1.0:.3f} -0.5) (stroke (width 0.2) (type solid)) (fill none) (layer "F.SilkS") (uuid "{uid(name, "p1")}"))\n'
    body += f'\t(fp_text user "FPC" (at 0 3.6 0) (layer "F.Fab") (uuid "{uid(name, "t")}") (effects (font (size 0.5 0.5) (thickness 0.08))))\n'
    return name, fp_text(name, f'Hirose FH34SRJ-{n}S-0.5SH(50) FPC connector, 0.5 mm pitch, 1.0 mm high, back-flip, top+bottom '
                               'contact. FPC opening toward +Y, contact 1 at +X (dot). Source: Hirose FH34 catalogue p.5.',
                         body, ref_y=-1.6, val_y=5.0)


def pj342():
    # SHOU HAN PJ-342 drawing (LCSC C668606), "PCB terminal dimension, TOP VIEW": jack opening at -X.
    # x measured from the body front face (the 2 mm collar sticks out to x = -2); body 12 x 6.4 x 4.5 mm.
    # Row A (y = -3.6): terminals 2, 3, 4 with left edges at 2.2 / 9.5 / 11.5.  Row B (y = +3.6): terminals
    # 5, 6, 7 with left edges at 2.2 / 5.5 / 11.0.  Lands 1.5 wide, rows 5.2 inner / 9.2 outer.
    # Two 1.5 mm locating pegs on the centre line at x = 2.4 and 9.4.
    name = 'Jack_3.5mm_SHOUHAN_PJ-342'
    body = ''
    for num, x0, y in (('2', 2.2, -3.6), ('3', 9.5, -3.6), ('4', 11.5, -3.6), ('5', 2.2, 3.6), ('6', 5.5, 3.6), ('7', 11.0, 3.6)):
        body += (f'\t(pad "{num}" smd rect (at {x0 + 0.75:.2f} {y:.2f}) (size 1.5 2.0) (layers "F.Cu" "F.Paste" "F.Mask") '
                 f'(uuid "{uid(name, num)}"))\n')
    for i, x in enumerate((2.4, 9.4)):
        body += f'\t(pad "" np_thru_hole circle (at {x} 0) (size 1.5 1.5) (drill 1.5) (layers "*.Cu" "*.Mask") (uuid "{uid(name, "h", i)}"))\n'
    body += rect('F.Fab', 0, -3.2, 12.0, 3.2, w=0.1, tag=name)
    body += rect('F.Fab', -2.0, -2.5, 0, 2.5, w=0.1, tag=name + 'c')
    body += rect('F.CrtYd', -2.2, -4.9, 13.4, 4.9, tag=name)
    body += rect('F.SilkS', 4.2, -3.3, 9.0, -3.3, w=0.12, tag=name + 's1')
    body += rect('F.SilkS', 7.6, 3.3, 10.5, 3.3, w=0.12, tag=name + 's2')
    return name, fp_text(name, 'SHOU HAN PJ-342 3.5 mm 4-pole SMD jack with switches, 4.5 mm high. Opening at -X; place x = 0 '
                               'on the board edge. Source: SHOU HAN PJ-342 drawing. TODO(verify) pole assignment with a sample.',
                         body, ref_y=-5.8, val_y=5.8)


def fpc_fingers(n=8):
    # Contact end of our own flex cable for Hirose FH34SRJ-nS-0.5SH: dimensions from the Hirose FH34 catalogue p.5
    # ("Recommended FPC/FFC Dimensions"): width G = 0.5 (n - 1) + 1.0, contacts 0.3 wide on 0.5 pitch, uncovered
    # length 1.5 +/- 0.3, total thickness 0.3 +/- 0.03 with a stiffener at least 2.5 long on the back.
    # JLCPCB flex rule: finger copper stays 0.2 mm off the board edge.  Origin = centre of the tip edge, cable body
    # toward +Y.  Pad 1 at -X.
    name = f'FPC_Fingers_1x{n:02d}_P0.5mm_FH34'
    body = ''
    for k in range(1, n + 1):
        x = (k - (n + 1) / 2) * 0.5
        body += (f'\t(pad "{k}" smd rect (at {x:.3f} 1.0) (size 0.3 1.6) (layers "F.Cu" "F.Mask") (uuid "{uid(name, k)}"))\n')
    G = 0.5 * (n - 1) + 1.0
    body += rect('F.Fab', -G / 2, 0, G / 2, 4.0, w=0.1, tag=name)
    body += rect('Cmts.User', -G / 2, 0, G / 2, 4.0, w=0.1, tag=name + 'st')
    body += f'\t(fp_text user "PI stiffener 0.225 on the back, 0..4 mm" (at 0 5.0 0) (layer "Cmts.User") (uuid "{uid(name, "t")}") (effects (font (size 0.4 0.4) (thickness 0.06))))\n'
    return name, fp_text(name, f'Flex cable contact end for Hirose FH34SRJ-{n}S-0.5SH: {n} fingers, 0.5 mm pitch, 1.5 mm uncovered, '
                               '0.225 mm PI stiffener on the back (0.07 mm flex -> 0.3 mm). Source: Hirose FH34 catalogue p.5.',
                         body, attr='smd exclude_from_pos_files exclude_from_bom allow_missing_courtyard', ref_y=-1.2, val_y=6.2)


def contact_pad():
    name = 'ContactPad_2x4mm'
    body = f'\t(pad "1" smd roundrect (at 0 0) (size 2.0 4.0) (layers "F.Cu" "F.Mask") (roundrect_rratio 0.25) (uuid "{uid(name)}"))\n'
    body += rect('F.CrtYd', -1.25, -2.25, 1.25, 2.25, tag=name)
    return name, fp_text(name, 'Bare gold landing pad for a spring pin (keyboard link experiment), no paste',
                         body, attr='smd exclude_from_pos_files exclude_from_bom', ref_y=-3.0, val_y=3.0)


def hole_m16_pad():
    name = 'MountingHole_M1.6_Pad'
    body = (f'\t(pad "1" thru_hole circle (at 0 0) (size 3.0 3.0) (drill 1.7) (layers "*.Cu" "*.Mask") (uuid "{uid(name)}"))\n'
            f'\t(fp_circle (center 0 0) (end 1.75 0) (stroke (width 0.05) (type solid)) (fill none) (layer "F.CrtYd") (uuid "{uid(name, "c")}"))\n')
    return name, fp_text(name, 'M1.6 plated hole with 3.0 mm pad (ties the top plate to keyboard GND through the screw)',
                         body, attr='through_hole exclude_from_pos_files', ref_y=-2.5, val_y=2.5)


def hole_m2_npth():
    name = 'MountingHole_M2_NPTH_BodyScrew'
    body = f'\t(pad "" np_thru_hole circle (at 0 0) (size 2.4 2.4) (drill 2.4) (layers "*.Cu" "*.Mask") (uuid "{uid(name)}"))\n'
    body += f'\t(fp_circle (center 0 0) (end 2.9 0) (stroke (width 0.05) (type solid)) (fill none) (layer "F.CrtYd") (uuid "{uid(name, "c")}"))\n'
    body += f'\t(fp_circle (center 0 0) (end 2.9 0) (stroke (width 0.05) (type solid)) (fill none) (layer "B.CrtYd") (uuid "{uid(name, "cb")}"))\n'
    return name, fp_text(name, 'M2 body screw passage, non plated; 5.8 mm keep-clear both sides for the shell bosses that clamp the board',
                         body, attr='exclude_from_pos_files exclude_from_bom', ref_y=-3.6, val_y=3.6)


def keycap_hole():
    name = 'MountingHole_M1.6_NPTH'
    body = f'\t(pad "" np_thru_hole circle (at 0 0) (size 1.7 1.7) (drill 1.7) (layers "*.Cu" "*.Mask") (uuid "{uid(name)}"))\n'
    body += f'\t(fp_circle (center 0 0) (end 1.6 0) (stroke (width 0.05) (type solid)) (fill none) (layer "F.CrtYd") (uuid "{uid(name, "c")}"))\n'
    return name, fp_text(name, 'M1.6 clearance hole, non plated', body, attr='exclude_from_pos_files exclude_from_bom', ref_y=-2.5, val_y=2.5)


def m2_hole():
    name = 'MountingHole_M2.5_CM4_Standoff'
    body = (f'\t(pad "1" thru_hole circle (at 0 0) (size 5.0 5.0) (drill 2.7) (layers "*.Cu" "*.Mask") (uuid "{uid(name)}"))\n'
            f'\t(fp_circle (center 0 0) (end 3.0 0) (stroke (width 0.05) (type solid)) (fill none) (layer "F.CrtYd") (uuid "{uid(name, "c")}"))\n')
    return name, fp_text(name, 'M2.5 plated hole for CM4 module standoff (2.7 mm drill like the RPi CM4IO), tied to GND',
                         body, attr='through_hole', ref_y=-3.5, val_y=3.5)


def main():
    os.makedirs(FP, exist_ok=True)
    open(os.path.join(LIB, 'hackerslide.kicad_sym'), 'w').write(symbols())
    for f in (df40, sksw, dome5135, keycap_hole, m2_hole, pj342, hole_m16_pad, hole_m2_npth, lambda: fh34(20), lambda: fh34(8), fpc_fingers, contact_pad):
        name, text = f()
        open(os.path.join(FP, name + '.kicad_mod'), 'w').write(text)


if __name__ == '__main__':
    main()
