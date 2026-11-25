"""Part catalogue: one place for symbol, footprint, value and sourcing fields.

LCSC codes are JLCPCB/LCSC part numbers.  bom/tools/check_bom.py re-queries every code against the JLCPCB parts
API and records price, stock, basic/extended status and the date checked in bom/bom.csv.
"""

R0402 = 'Resistor_SMD:R_0402_1005Metric'
C0402 = 'Capacitor_SMD:C_0402_1005Metric'
C0603 = 'Capacitor_SMD:C_0603_1608Metric'
C0805 = 'Capacitor_SMD:C_0805_2012Metric'

# value -> (LCSC, MPN) for JLC basic 0402 1% resistors (checked 2026-11-24 via JLC parts API)
RES = {
    '0': ('C17168', '0402WGF0000TCE'), '22': ('C25092', '0402WGF220JTCE'), '27': ('C25100', '0402WGF270JTCE'),
    '100': ('C25076', '0402WGF1000TCE'), '200': ('C25087', '0402WGF2000TCE'), '330': ('C25104', '0402WGF3300TCE'),
    '470': ('C25117', '0402WGF4700TCE'), '1k': ('C11702', '0402WGF1001TCE'), '2.2k': ('C25879', '0402WGF2201TCE'),
    '3.3k': ('C25890', '0402WGF3301TCE'), '4.7k': ('C25900', '0402WGF4701TCE'), '5.1k': ('C25905', '0402WGF5101TCE'),
    '10k': ('C25744', '0402WGF1002TCE'), '22k': ('C25768', '0402WGF2202TCE'), '100k': ('C25741', '0402WGF1003TCE'),
    '1M': ('C26083', '0402WGF1004TCE'),
    # added after the 2026-11-24 audit (JLC parts API, same date)
    '5.1': ('C25128', '0402WGF510KTCE'), '300': ('C25102', '0402WGF3000TCE'), '33': ('C25105', '0402WGF330JTCE'), '220': ('C25091', '0402WGF2200TCE'),
    '15k': ('C25756', '0402WGF1502TCE'), '20k': ('C25765', '0402WGF2002TCE'), '47k': ('C25792', '0402WGF4702TCE'), '51k': ('C25794', '0402WGF5102TCE'),
    '402k': ('C25785', '0402WGF4023TCE'), '560k': ('C132339', '0402WGF5603TCE'),
}
CAP = {
    '15p': ('C1548', '0402CG150J500NT', C0402), '22n': ('C1532', '0402B223K500NT', C0402),
    '100n': ('C1525', 'CL05B104KO5NNNC', C0402), '1u': ('C52923', 'CL05A105KA5NQNC', C0402),
    '4.7u': ('C23733', 'CL05A475MP5NRNC', C0402), '10u': ('C19702', 'CL10A106KP8NNNC', C0603),
    '22u': ('C45783', 'CL21A226MAQNNNE', C0805),
    '22p': ('C1555', '0402CG220J500NT', C0402), '100p': ('C1546', '0402CG101J500NT', C0402),
    '4.7u/0603': ('C19666', 'CL10A475KO8NNNC', C0603),      # where DC bias matters (REGN)
    '2.2u/50V': ('C307528', 'CL21A225KBFNNNE', C0805),      # backlight output
}


def fields(lcsc, mpn, mfr='', **extra):
    d = {'LCSC': lcsc, 'MPN': mpn}
    if mfr:
        d['Manufacturer'] = mfr
    d.update(extra)
    return d


def R(sheet, ref, value, a, b, dnp=False, note=''):
    lcsc, mpn = RES[value]
    f = fields(lcsc, mpn, 'UNI-ROYAL')
    if note:
        f['Description'] = note
    return sheet.add(ref, 'Device', 'R', value, R0402, {'1': a, '2': b}, fields=f, dnp=dnp)


def C(sheet, ref, value, a, b='GND', dnp=False):
    lcsc, mpn, fp = CAP[value]
    mfr = 'FH' if mpn.startswith('0402') else 'Samsung'
    return sheet.add(ref, 'Device', 'C', value.split('/')[0], fp, {'1': a, '2': b}, fields=fields(lcsc, mpn, mfr), dnp=dnp)


def TP(sheet, ref, net):
    return sheet.add(ref, 'Connector', 'TestPoint', net, 'TestPoint:TestPoint_Pad_D1.0mm', {'1': net})


def TVS(sheet, ref, net, note=''):
    """Bidirectional ESD diode to GND (Nexperia PESD5V0S1BL, SOD-882)."""
    return sheet.add(ref, 'Device', 'D_TVS', 'PESD5V0S1BL', 'Diode_SMD:D_SOD-882', {'1': net, '2': 'GND'},
                     fields=fields('C84374', 'PESD5V0S1BL,315', 'Nexperia', Description=note or 'ESD, bidirectional'))


def SCHOTTKY(sheet, ref, anode, cathode, note=''):
    return sheet.add(ref, 'Device', 'D_Schottky', '1N5819WS', 'Diode_SMD:D_SOD-323', {'1': cathode, '2': anode},
                     fields=fields('C191023', '1N5819WS', 'Hottech', Description=note))
