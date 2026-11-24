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
    # cross-checked with Hirose DF40 catalogue recommended layout (rows 3.78 outer / 1.5 inner).
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
    # Keystone 5135 "mini" key-pad dome, 7.0 mm across flats, legs on 8.0 mm mounting diameter, centre pad 3.0 mm
    # (Keystone catalogue p.97). Domes are NOT soldered: they sit on these pads under Keystone 5200 adhesive spacer.
    name = 'SW_Keystone_5135_Dome_7mm'
    body = f'\t(pad "2" smd circle (at 0 0) (size 3.0 3.0) (layers "F.Cu" "F.Mask") (uuid "{uid(name, "c")}"))\n'
    for i, (x, y) in enumerate(((2.83, 2.83), (-2.83, 2.83), (2.83, -2.83), (-2.83, -2.83))):
        body += f'\t(pad "1" smd circle (at {x} {y}) (size 1.0 1.0) (layers "F.Cu" "F.Mask") (uuid "{uid(name, i)}"))\n'
    body += f'\t(fp_circle (center 0 0) (end 4.0 0) (stroke (width 0.05) (type solid)) (fill none) (layer "F.Fab") (uuid "{uid(name, "fab")}"))\n'
    body += rect('F.CrtYd', -3.5, -3.5, 3.5, 3.5, tag=name)
    return name, fp_text(name, 'Keystone 5135 metal dome contact pattern (TODO(verify) against Keystone application drawing; '
                               'unsoldered, gold/ENIG finish required)', body, attr='smd allow_missing_courtyard', ref_y=-4.2, val_y=4.2)


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
    for f in (df40, sksw, dome5135, keycap_hole, m2_hole):
        name, text = f()
        open(os.path.join(FP, name + '.kicad_mod'), 'w').write(text)


if __name__ == '__main__':
    main()
