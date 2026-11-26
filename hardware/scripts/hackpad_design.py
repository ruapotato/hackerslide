"""HackerSlide hack pad main board: schematic source (first sheets: brain, its supplies, clocks, boot, debug, memory).

  python3 hackpad_design.py ../hackpad

DRAFT, NOT BUILT, NOT REVIEWED.  The brain is an NXP i.MX RT1176 in "B" silicon (decisions/0009).  Every connection
to it is taken from the cross-checked data in hardware/hackpad/data/ (ball map, NXP's evaluation board MIMXRT1170-EVKB,
hardware guide), and each block says which file and which EVKB part it follows.  Where this board departs from the
EVKB the line says DEPARTS and why.  Pads not assigned yet are left unconnected: later sheets (display, radios,
sensors, audio, power input) will claim them from pinmux.csv.

Rails on these sheets: +3V3 (main; its regulator is on the power sheet, not drawn yet), +1V8 (LDO from +3V3),
VDD_SOC (the chip's own converter, about 1.1 V), and filtered branches of the first two.
"""
import csv
import os
import re
import sys

from kigen import Design
from parts import C, CAP, R, RES, TP, fields

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'hackpad', 'data')
BALLS = list(csv.DictReader(open(os.path.join(DATA, 'ballmap.csv'))))
BY_NAME = {}
for _r in BALLS:
    BY_NAME.setdefault(_r['name'], []).append(_r['ball'])

# parts these sheets need that the catalogue did not have (JLCPCB codes; stock is re-read by bom/tools/make_bom.py)
RES.update({'30k': ('C25776', '0402WGF3002TCE'), '10k': RES['10k']})
CAP.update({'220n': ('C16772', 'CL05B224KO5NNNC', CAP['100n'][2]), '4.7p': ('C1569', '0402CG4R7C500NT', CAP['100n'][2]),
            '22u/0603': ('C59461', 'CL10A226MQ8NRNC', 'Capacitor_SMD:C_0603_1608Metric')})

U = {}          # ball -> net, filled by the helpers below; one dict so that a ball can only be claimed once


def pad(name, net):
    """Connect every ball called `name` (a pad such as GPIO_AD_24 or a supply such as VDD_SOC_IN) to `net`."""
    for b in BY_NAME[name]:
        assert b not in U, (name, b, U[b], net)
        U[b] = net


def bead(sheet, ref, a, b):
    sheet.add(ref, 'Device', 'FerriteBead', '120R@100MHz', 'Inductor_SMD:L_0402_1005Metric', {'1': a, '2': b},
              fields=fields('C88970', 'BLM15PX121SN1D', 'Murata', Description='120 ohm at 100 MHz, as the beads on the EVKB'))


def build():
    d = Design('hackpad', 'HackerSlide hack pad main board', comments=[
        'Rev 0.1 DRAFT: brain, supplies, clocks, boot, debug and memory only. Not built, not reviewed.',
        'Source of every brain connection: hardware/hackpad/data (NXP data sheet IMXRT1170BIEC rev 1, MIMXRT1170-EVKB schematic).'])

    # ------------------------------------------------------------------------------------------ supplies
    p = d.sheet('mcu_power', 'Brain: supplies and decoupling', paper='A2', notes=[
        'Follows hardware/hackpad/data/power.md. Decoupling per rail is the hardware guide table (HDUG rev 2, table 1) plus',
        '    the EVKB additions on the converter outputs. Place the 0402 parts under the balls named in that table.',
        'VDD_SOC is made by the chip itself (DCDC_DIG, about 1.1 V at 800 MHz) through L1.',
        'The chip also makes 1.8 V (DCDC_ANA) but only for on-chip loads up to 150 mA. As on the EVKB it gets its',
        '    capacitors and is otherwise unused: the 1.8 V inputs take +1V8 from the LDO U2.',
        'Power-up order (data sheet 4.2.1): SNVS, LPSR and DCDC_IN may be one 3.3 V net, as here. DCDC_PSWITCH must rise',
        '    5-40 ms after DCDC_IN: R1 30k x C1 220n = 6.6 ms, the EVKB values.',
        'DEPARTS from the EVKB: NVCC_DISP1 is on +3V3 (EVKB: 1.8 V) because nothing here needs that bank at 1.8 V.',
        'MIPI is unused (the e-paper panel is SPI): VDD_MIPI_1P8 and VDD_MIPI_1P0 go to GND through 10k (data sheet table 6).',
        'TODO before layout: an always-on supply for VDD_SNVS_IN so that the clock keeps time with +3V3 off (now strapped by R3).'])
    for n in ('DCDC_IN', 'DCDC_IN_Q', 'VDD_LPSR_IN', 'NVCC_EMC1', 'NVCC_EMC2', 'NVCC_GPIO', 'NVCC_LPSR', 'NVCC_DISP1',
              'NVCC_DISP2', 'NVCC_SD1'):
        pad(n, '+3V3')
    pad('NVCC_SD2', '+1V8')                       # the boot flash is a 1.8 V part, as on the EVKB
    for n in ('DCDC_DIG', 'DCDC_DIG_SENSE', 'VDD_SOC_IN'):
        pad(n, 'VDD_SOC')
    for n in ('DCDC_ANA', 'DCDC_ANA_SENSE'):
        pad(n, 'DCDC_1V8')
    pad('DCDC_LP', 'DCDC_LP'); pad('DCDC_LN', 'DCDC_LN')
    pad('DCDC_PSWITCH', 'DCDC_PSWITCH'); pad('DCDC_MODE', 'DCDC_MODE')
    pad('VDD_LPSR_ANA', 'VDD_LPSR_ANA'); pad('VDD_LPSR_DIG', 'VDD_LPSR_DIG')
    pad('VDD_SNVS_IN', 'VDD_SNVS_IN'); pad('VDD_SNVS_ANA', 'VDD_SNVS_ANA'); pad('NVCC_SNVS', 'VDD_SNVS_ANA')
    pad('VDD_SNVS_DIG', 'VDD_SNVS_DIG')
    pad('VDDA_1P8_IN', '+1V8A'); pad('VDDA_ADC_1P8', '+1V8A'); pad('ADC_VREFH', '+1V8A')
    pad('VDDA_1P0', 'VDDA_1P0')
    pad('VDDA_ADC_3P3', '+3V3A')
    pad('VDD_USB_1P8', '+1V8_USB'); pad('VDD_USB_3P3', '+3V3_USB')
    pad('VDD_MIPI_1P8', 'MIPI_1P8_OFF'); pad('VDD_MIPI_1P0', 'MIPI_1P0_OFF')
    for r in BALLS:
        if r['kind'] == 'ground':
            U[r['ball']] = 'GND'

    p.add('L1', 'Device', 'L', '4.7uH', 'Inductor_SMD:L_Taiyo-Yuden_MD-2020', {'1': 'DCDC_LP', '2': 'DCDC_LN'},
          fields=fields('', 'TBD', '', Description='4.7 uH, saturation > 1.5 A (HDUG; EVKB L15 is 1.9 A, 91 mohm). PART TO BE CHOSEN: '
                                                   'the data sheet says 1 A typ, the guide > 1.5 A'))
    R(p, 'R1', '30k', '+3V3', 'DCDC_PSWITCH', note='EVKB R396')
    C(p, 'C1', '220n', 'DCDC_PSWITCH')
    R(p, 'R2', '4.7k', 'DCDC_MODE', 'GND', note='EVKB R398: converter enabled')
    C(p, 'C2', '100n', 'DCDC_MODE')
    R(p, 'R3', '0', '+3V3', 'VDD_SNVS_IN', note='strap; see the TODO on this sheet')
    R(p, 'R4', '10k', 'MIPI_1P8_OFF', 'GND')
    R(p, 'R5', '10k', 'MIPI_1P0_OFF', 'GND')
    bead(p, 'FB1', '+1V8', '+1V8A')
    bead(p, 'FB2', '+3V3', '+3V3A')
    bead(p, 'FB3', '+1V8', '+1V8_USB')
    bead(p, 'FB4', '+3V3', '+3V3_USB')
    p.add('U2', 'Regulator_Linear', 'AMS1117-1.8', 'AMS1117-1.8', 'Package_TO_SOT_SMD:SOT-223-3_TabPin2',
          {'3': '+3V3', '2': '+1V8', '1': 'GND'},
          fields=fields('C347220', 'AMS1117-1.8', 'UMW', Description='1.8 V for the analogue, USB and flash supplies: the EVKB\'s part (U1). '
                                                                     'A lower-dropout, lower-idle-current LDO should replace it before layout'))
    C(p, 'C3', '10u', '+3V3'); C(p, 'C4', '22u', '+1V8')
    # decoupling: (net, [values]) from the hardware guide table, in the order of power.md section 6
    DEC = [('+3V3', ['100n', '4.7u', '22u']),                                   # DCDC_IN
           ('DCDC_1V8', ['2.2u', '100n', '10u', '22u']),                        # DCDC_ANA + sense; EVKB adds 10 + 22 uF
           ('VDD_SOC', ['2.2u', '22u', '100n', '10u']),                         # DCDC_DIG + sense; EVKB adds 10 uF
           ('VDD_SOC', ['100n', '1u', '1u', '4.7u', '4.7u', '22u']),            # VDD_SOC_IN
           ('+1V8A', ['100n', '1u']),                                           # VDDA_1P8_IN (a later guide revision: 1 uF)
           ('+3V3', ['4.7u']), ('VDD_LPSR_ANA', ['4.7u']), ('VDD_LPSR_DIG', ['2.2u']),
           ('VDD_SNVS_IN', ['1u']), ('VDD_SNVS_ANA', ['2.2u', '100n']), ('VDD_SNVS_DIG', ['220n']),
           ('+1V8_USB', ['1u']), ('+3V3_USB', ['1u']), ('+1V8A', ['1u', '2.2u']),   # ADC_1P8, VREFH
           ('+3V3A', ['1u', '100n']), ('VDDA_1P0', ['2.2u']),
           ('+3V3', ['2.2u']),                                                  # NVCC_SD1
           ('+1V8', ['2.2u']),                                                  # NVCC_SD2
           ('+3V3', ['2.2u', '4.7u']), ('+3V3', ['2.2u', '4.7u']), ('+3V3', ['2.2u', '4.7u']),   # NVCC_EMC1, EMC2, GPIO
           ('+3V3', ['2.2u']), ('+3V3', ['2.2u']), ('+3V3', ['2.2u'])]          # NVCC_DISP1, DISP2, LPSR
    n = 10
    for net, vals in DEC:
        for v in vals:
            C(p, f'C{n}', v, net)
            n += 1

    # ------------------------------------------------------------------------------------------ clocks, reset, boot, debug
    k = d.sheet('mcu_core', 'Brain: clocks, reset, boot and debug', paper='A2', notes=[
        'Follows hardware/hackpad/data/power.md sections 5 and 7 and boot.md.',
        '24 MHz crystal as EVKB Y4 (8 pF load, 4.7 pF capacitors); 32.768 kHz crystal as EVKB Y5, its capacitors unfitted.',
        '    CRYSTAL PART NUMBERS TO BE CHOSEN from stock with those figures.',
        'Boot: BOOT_MODE = 10 (run from the flash) by R20/R21. Holding SW1 while resetting gives 01, the serial loader on',
        '    USB1 and LPUART1: SW1 lifts BOOT_MODE0 and Q1 pulls BOOT_MODE1 down.',
        'The twelve BT_CFG pads must not float on a part with blank fuses: all zero selects QSPI flash on FlexSPI1.',
        '    10k to GND each. Anything put on those pads later must not pull them up while the chip leaves reset.',
        'POR_B: 100n as on the EVKB and a reset button. NXP recommends a supervisor with its threshold above 2.6 V: TODO.',
        'ONOFF is the power key (short press: on / interrupt; about 5 s: forced off). PMIC_ON_REQ will enable the 3.3 V',
        '    regulator on the power sheet. SWD on test pads; console on LPUART1, the port the serial loader also uses.'])
    pad('XTALI', 'XTAL24_I'); pad('XTALO', 'XTAL24_O'); pad('RTC_XTALI', 'XTAL32_I'); pad('RTC_XTALO', 'XTAL32_O')
    k.add('Y1', 'Device', 'Crystal_GND24', '24MHz', 'Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm',
          {'1': 'XTAL24_I', '3': 'XTAL24_O', '2': 'GND', '4': 'GND'},
          fields=fields('', 'TBD', '', Description='24 MHz, CL 8 pF, ESR <= 60 ohm, +-20 ppm (EVKB Y4). PART TO BE CHOSEN'))
    C(k, 'C80', '4.7p', 'XTAL24_I'); C(k, 'C81', '4.7p', 'XTAL24_O')
    k.add('Y2', 'Device', 'Crystal', '32.768kHz', 'Crystal:Crystal_SMD_3215-2Pin_3.2x1.5mm', {'1': 'XTAL32_I', '2': 'XTAL32_O'},
          fields=fields('', 'TBD', '', Description='32.768 kHz, ESR < 100 kohm (EVKB Y5). PART TO BE CHOSEN'))
    C(k, 'C82', '15p', 'XTAL32_I', dnp=True); C(k, 'C83', '15p', 'XTAL32_O', dnp=True)
    pad('POR_B', 'POR_B'); pad('ONOFF', 'ONOFF'); pad('PMIC_ON_REQ', 'PMIC_ON_REQ'); pad('WAKEUP', 'WAKEUP')
    pad('TEST_MODE', 'GND')
    C(k, 'C84', '100n', 'POR_B')
    k.add('SW2', 'Switch', 'SW_Push', 'RESET', 'hackerslide:SW_Alps_SKSWCFE010_3x2mm', {'1': 'POR_B', '2': 'GND'},
          fields=fields('C255576', 'SKSWCFE010', 'Alps Alpine'))
    C(k, 'C85', '100n', 'ONOFF')
    pad('GPIO_LPSR_02', 'BOOT_MODE0'); pad('GPIO_LPSR_03', 'BOOT_MODE1')
    R(k, 'R20', '100k', 'BOOT_MODE0', 'GND')
    R(k, 'R21', '4.7k', 'BOOT_MODE1', '+3V3', note='logic 1 through 4.7k to NVCC_LPSR (HDUG table 9)')
    k.add('SW1', 'Switch', 'SW_Push', 'BOOT', 'hackerslide:SW_Alps_SKSWCFE010_3x2mm', {'1': 'BOOT_SEL', '2': '+3V3'},
          fields=fields('C255576', 'SKSWCFE010', 'Alps Alpine'))
    R(k, 'R22', '1k', 'BOOT_SEL', 'BOOT_MODE0')
    R(k, 'R23', '100k', 'BOOT_SEL', 'GND')
    k.add('Q1', 'Transistor_FET', '2N7002', '2N7002', 'Package_TO_SOT_SMD:SOT-23', {'1': 'BOOT_SEL', '2': 'GND', '3': 'BOOT_MODE1'},
          fields=fields('C8545', '2N7002', 'Jiangsu Changjing', Description='pulls BOOT_MODE1 low while SW1 is held'))
    for i, name in enumerate(['GPIO_DISP_B1_06', 'GPIO_DISP_B1_07', 'GPIO_DISP_B1_08', 'GPIO_DISP_B1_09', 'GPIO_DISP_B1_10',
                              'GPIO_DISP_B1_11', 'GPIO_DISP_B2_00', 'GPIO_DISP_B2_01', 'GPIO_DISP_B2_02', 'GPIO_DISP_B2_03',
                              'GPIO_DISP_B2_04', 'GPIO_DISP_B2_05']):
        pad(name, f'BT_CFG{i}')
        R(k, f'R{30 + i}', '10k', f'BT_CFG{i}', 'GND')
    pad('GPIO_LPSR_14', 'SWD_CLK'); pad('GPIO_LPSR_15', 'SWD_DIO'); pad('GPIO_LPSR_13', 'JTAG_MOD')
    R(k, 'R24', '4.7k', 'JTAG_MOD', 'GND', note='HDUG: pull down')
    pad('GPIO_AD_24', 'UART_DBG_TX'); pad('GPIO_AD_25', 'UART_DBG_RX')
    k.add('J1', 'Connector', 'Conn_01x03_Pin', 'DEBUG_UART', 'Connector_JST:JST_SH_SM03B-SRSS-TB_1x03-1MP_P1.00mm_Horizontal',
          {'1': 'UART_DBG_RX', '2': 'GND', '3': 'UART_DBG_TX'},
          fields=fields('C160403', 'SM03B-SRSS-TB(LF)(SN)', 'JST', Description='Raspberry Pi debug-probe pin order: 1 = into the board'))
    for i, net in enumerate(('SWD_CLK', 'SWD_DIO', 'POR_B', '+3V3', 'GND', 'VDD_SOC', '+1V8', 'BOOT_MODE0', 'BOOT_MODE1',
                             'PMIC_ON_REQ', 'WAKEUP', 'ONOFF')):
        TP(k, f'TP{i + 1}', net)

    # ------------------------------------------------------------------------------------------ memory
    m = d.sheet('memory', 'SDRAM 64 MB and boot flash', paper='A2', notes=[
        'SDRAM exactly as on the EVKB (hardware/hackpad/data/sdram.csv): two W9825G6KH, 16 bits each, forming one 32-bit bank',
        '    on SEMC_CS0. Pad for pad and pin for pin the same; the EVKB has no series resistors on this bus.',
        'SEMC_DQS (ball J2) must stay unconnected: the chip loops its own clock back through that pad.',
        '128 MB later: on B silicon a second bank may only use SEMC_CSX0 (ball L1) or SEMC_RDY (ball K1) as its chip select',
        '    (erratum ERR052401). Not drawn yet.',
        'Flash: FlexSPI1 port A on GPIO_SD_B2_06..11 (boot.md). W25Q128JW, 1.8 V, the part of the first EVKB revision.',
        '    FLEXSPI1_A_DQS (ball E14) must stay unconnected for 133 MHz.',
        'TODO before layout: check the W9825G6KH and W25Q128JW pin numbers against Winbond\'s data sheets (taken here from',
        '    KiCad\'s library symbols and the EVKB schematic).'])
    rows = list(csv.DictReader(open(os.path.join(DATA, 'sdram.csv'))))
    chips = {'U13': {}, 'U25': {}}
    for r in rows:
        mm = re.search(r'\(pin (\d+)\)', r['sdram_connection'])
        if not mm:
            continue                                  # SEMC_DQS, RDY, CSX0, CLKX: not part of the SDRAM bank
        pad(r['mcu_pad'], r['evkb_net'])
        for u in chips:
            if u + '.' in r['sdram_connection']:
                chips[u][mm.group(1)] = r['evkb_net']
    assert all(len(c) == 39 for c in chips.values()), {u: len(c) for u, c in chips.items()}
    for ref, u in (('U3', 'U13'), ('U4', 'U25')):
        nets = dict(chips[u])
        for pin in ('1', '14', '27', '3', '9', '43', '49'):
            nets[pin] = '+3V3'
        for pin in ('28', '41', '54', '6', '12', '46', '52'):
            nets[pin] = 'GND'
        m.add(ref, 'hackerslide', 'W9825G6KH', 'W9825G6KH-6', 'Package_SO:TSOP-II-54_22.2x10.16mm_P0.8mm', nets,
              fields=fields('C62246', 'W9825G6KH-6', 'Winbond', Description=f'256 Mbit SDRAM (EVKB {u}; the EVKB fits the -5I grade)'))
        for i in range(7):
            C(m, f'C{100 + (0 if ref == "U3" else 10) + i}', '100n', '+3V3')
    FL = {'GPIO_SD_B2_06': ('FSPI_CS', '1'), 'GPIO_SD_B2_07': ('FSPI_CLK', '6'), 'GPIO_SD_B2_08': ('FSPI_D0', '5'),
          'GPIO_SD_B2_09': ('FSPI_D1', '2'), 'GPIO_SD_B2_10': ('FSPI_D2', '3'), 'GPIO_SD_B2_11': ('FSPI_D3', '7')}
    nets = {'4': 'GND', '8': '+1V8'}
    for name, (net, pin) in FL.items():
        pad(name, net)
        nets[pin] = net
    m.add('U5', 'Memory_Flash', 'W25Q128JVS', 'W25Q128JWSIQ', 'Package_SO:SOIC-8_5.3x5.3mm_P1.27mm', nets,
          fields=fields('C7150045', 'W25Q128JWSIQ', 'Winbond', Description='128 Mbit QSPI NOR, 1.8 V (the JW type), boot device'))
    R(m, 'R50', '10k', 'FSPI_CS', '+1V8', note='EVKB R165')
    C(m, 'C120', '100n', '+1V8')

    # the brain itself goes on the first sheet, with every ball claimed above
    p.add('U1', 'hackerslide', 'MIMXRT117x_BGA289', 'MIMXRT1176', 'Package_BGA:MAPBGA-289_14x14mm_Layout17x17_P0.8mm', dict(U),
          fields=fields('', 'MIMXRT1176xVMxB', 'NXP', Description='i.MX RT1176, B silicon. Exact part number (grade, 800 MHz or 1 GHz) '
                                                                 'to be chosen from stock; the ball map is the same for all'))
    return d


if __name__ == '__main__':
    d = build()
    for prob in d.check():
        print('CHECK:', prob)
    print(len(U), 'of 289 balls connected; PWR_FLAG on', sorted(d.write(sys.argv[1])))
