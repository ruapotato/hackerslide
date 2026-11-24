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
}
CAP = {
    '15p': ('C1548', '0402CG150J500NT', C0402), '22n': ('C1532', '0402B223K500NT', C0402),
    '100n': ('C1525', 'CL05B104KO5NNNC', C0402), '1u': ('C52923', 'CL05A105KA5NQNC', C0402),
    '4.7u': ('C23733', 'CL05A475MP5NRNC', C0402), '10u': ('C19702', 'CL10A106KP8NNNC', C0603),
    '22u': ('C45783', 'CL21A226MAQNNNE', C0805),
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
    return sheet.add(ref, 'Device', 'C', value, fp, {'1': a, '2': b}, fields=fields(lcsc, mpn, 'Samsung/FH'), dnp=dnp)
