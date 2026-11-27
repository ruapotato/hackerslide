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

import hackpad_lid_design as LID
import hackpad_pins as PINS
import hp_layout as HP
from kigen import Design
from parts import C, CAP, R, RES, SCHOTTKY, TP, TVS, fields

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'hackpad', 'data')
BALLS = list(csv.DictReader(open(os.path.join(DATA, 'ballmap.csv'))))
BY_NAME = {}
for _r in BALLS:
    BY_NAME.setdefault(_r['name'], []).append(_r['ball'])

# parts these sheets need that the catalogue did not have (JLCPCB codes; stock is re-read by bom/tools/make_bom.py)
RES.update({'30k': ('C25776', '0402WGF3002TCE'), '200k': ('C25764', '0402WGF2003TCE')})
CAP.update({'10p': ('C1545', '0402CG100J500NT', CAP['100n'][2]),
            '1u/50V': ('C15849', 'CL10A105KB8NNNC', 'Capacitor_SMD:C_0603_1608Metric'),
            '220n': ('C16772', 'CL05B224KO5NNNC', CAP['100n'][2]), '4.7p': ('C1569', '0402CG4R7C500NT', CAP['100n'][2]),
            '22u/0603': ('C59461', 'CL10A226MQ8NRNC', 'Capacitor_SMD:C_0603_1608Metric')})

U = {}          # ball -> net, filled by the helpers below; one dict so that a ball can only be claimed once


def pad(name, net):
    """Connect every ball called `name` (a pad such as GPIO_AD_24 or a supply such as VDD_SOC_IN) to `net`."""
    for b in BY_NAME[name]:
        assert b not in U, (name, b, U[b], net)
        U[b] = net


def use(net):
    """Claim the pad that hackpad_pins.py plans for `net`."""
    (padname,) = [p for p, fn, n, u in PINS.P if n == net]
    pad(padname, net)


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
        'Rails made here: +1V8 (U2, step-down, digital), +1V8_LDO (U11, analogue and USB), VDD_SNVS_IN (U12, 3.0 V always on from VSYS).',
        'VSYS is the battery/charger system rail (power sheet, not drawn yet).'])
    pad('NVCC_EMC1', '+1V8'); pad('NVCC_EMC2', '+1V8')      # the memory is a 1.8 V type
    for n in ('DCDC_IN', 'DCDC_IN_Q', 'VDD_LPSR_IN', 'NVCC_GPIO', 'NVCC_LPSR', 'NVCC_DISP1',
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

    p.add('L1', 'Device', 'L', '4.7uH', 'Inductor_SMD:L_Taiyo-Yuden_NR-40xx', {'1': 'DCDC_LP', '2': 'DCDC_LN'},
          fields=fields('C92961', 'NRS4018T4R7MDGJ', 'Taiyo Yuden', Description='4.7 uH, saturation 2.0 A, 70 mohm, 4 x 4 x 1.8 mm (NXP asks > 1.5 A)'))
    R(p, 'R1', '30k', '+3V3', 'DCDC_PSWITCH', note='EVKB R396')
    C(p, 'C1', '220n', 'DCDC_PSWITCH')
    R(p, 'R2', '4.7k', 'DCDC_MODE', 'GND', note='EVKB R398: converter enabled')
    C(p, 'C2', '100n', 'DCDC_MODE')
    # VDD_SNVS_IN comes from U12 below
    R(p, 'R4', '10k', 'MIPI_1P8_OFF', 'GND')
    R(p, 'R5', '10k', 'MIPI_1P0_OFF', 'GND')
    bead(p, 'FB1', '+1V8_LDO', '+1V8A')
    bead(p, 'FB2', '+3V3', '+3V3A')
    bead(p, 'FB3', '+1V8_LDO', '+1V8_USB')
    bead(p, 'FB4', '+3V3', '+3V3_USB')
    p.add('U2', 'Regulator_Switching', 'TLV62568DBV', 'TLV62568DBVR', 'Package_TO_SOT_SMD:SOT-23-5',
          {'1': '+3V3', '2': 'GND', '3': 'SW_1V8', '4': '+3V3', '5': 'FB_1V8'},
          fields=fields('C163219', 'TLV62568DBVR', 'Texas Instruments', Description='1.8 V, 1 A step-down for the memory, its pad banks and the flash'))
    p.add('L3', 'Device', 'L', '2.2uH', 'Inductor_SMD:L_Murata_DFE201610P', {'1': 'SW_1V8', '2': '+1V8'},
          fields=fields('C337893', 'DFE201612E-2R2M=P2', 'Murata', Description='2.2 uH, 1.8 A, 2.0 x 1.6 x 1.2 mm. CHECK the footprint against the Murata land pattern'))
    R(p, 'R6', '200k', '+1V8', 'FB_1V8', note='0.6 V x (1 + 200k/100k) = 1.8 V'); R(p, 'R7', '100k', 'FB_1V8', 'GND')
    C(p, 'C3', '4.7u', '+3V3'); C(p, 'C4', '10u', '+1V8')
    p.add('U11', 'Regulator_Linear', 'AP2112K-1.8', 'TPS7A2018', 'Package_TO_SOT_SMD:SOT-23-5',
          {'1': '+3V3', '2': 'GND', '3': '+3V3', '5': '+1V8_LDO'},
          fields=fields('C963430', 'TPS7A2018PDBVR', 'Texas Instruments', Description='quiet 1.8 V, 300 mA, for the analogue and USB supplies (6.5 uA idle)'))
    C(p, 'C5', '1u', '+3V3'); C(p, 'C6', '1u', '+1V8_LDO')
    p.add('U12', 'Regulator_Linear', 'AP2112K-1.8', 'TPS7A0230', 'Package_TO_SOT_SMD:SOT-23-5',
          {'1': 'VSYS', '2': 'GND', '3': 'VSYS', '5': 'VDD_SNVS_IN'},
          fields=fields('C3747031', 'TPS7A0230PDBVR', 'Texas Instruments', Description='3.0 V always on from the battery rail (25 nA idle): keeps the clock running'))
    C(p, 'C7', '1u', 'VSYS')
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
           ('+1V8', ['2.2u', '4.7u']), ('+1V8', ['2.2u', '4.7u']), ('+3V3', ['2.2u', '4.7u']),   # NVCC_EMC1, EMC2, GPIO
           ('+3V3', ['2.2u']), ('+3V3', ['2.2u']), ('+3V3', ['2.2u'])]          # NVCC_DISP1, DISP2, LPSR
    n = 10
    for net, vals in DEC:
        for v in vals:
            C(p, f'C{n}', v, net)
            n += 1

    # ------------------------------------------------------------------------------------------ clocks, reset, boot, debug
    k = d.sheet('mcu_core', 'Brain: clocks, reset, boot and debug', paper='A2', notes=[
        'Follows hardware/hackpad/data/power.md sections 5 and 7 and boot.md.',
        '24 MHz crystal: 8 pF load with NXP\'s 4.7 pF capacitors; computed to run a little fast: MEASURE on the first board.',
        '32.768 kHz crystal: 7 pF load, 10 pF capacitors fitted (NXP\'s board leaves them off; the chip adds no load of its own).',
        'Boot: BOOT_MODE = 10 (run from the flash) by R20/R21. Holding SW1 while resetting gives 01, the serial loader on',
        '    USB1 and LPUART1: SW1 lifts BOOT_MODE0 and Q1 pulls BOOT_MODE1 down.',
        'The twelve BT_CFG pads must not float on a part with blank fuses: all zero selects QSPI flash on FlexSPI1.',
        '    10k to GND each. Anything put on those pads later must not pull them up while the chip leaves reset.',
        'POR_B: supervisor U10 (3.0 V threshold, about 62 ms delay from C86) drives it open drain; the reset button is on its',
        '    manual-reset input. DEPARTS from the EVKB, whose supervisor power-cycles the 3.3 V supply instead.',
        'ONOFF is the power key (short press: on / interrupt; about 5 s: forced off). PMIC_ON_REQ will enable the 3.3 V',
        '    regulator on the power sheet. SWD on test pads; console on LPUART1, the port the serial loader also uses.'])
    pad('XTALI', 'XTAL24_I'); pad('XTALO', 'XTAL24_O'); pad('RTC_XTALI', 'XTAL32_I'); pad('RTC_XTALO', 'XTAL32_O')
    k.add('Y1', 'Device', 'Crystal_GND24', '24MHz', 'Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm',
          {'1': 'XTAL24_I', '3': 'XTAL24_O', '2': 'GND', '4': 'GND'},
          fields=fields('C156248', 'NX3225GA-24MHZ-STD-CRG-2', 'NDK', Description='24 MHz, CL 8 pF, ESR 50 ohm max, +-20 ppm'))
    C(k, 'C80', '4.7p', 'XTAL24_I'); C(k, 'C81', '4.7p', 'XTAL24_O')
    k.add('Y2', 'Device', 'Crystal', '32.768kHz', 'Crystal:Crystal_SMD_3215-2Pin_3.2x1.5mm', {'1': 'XTAL32_I', '2': 'XTAL32_O'},
          fields=fields('C48615', 'Q13FC13500002', 'Epson', Description='FC-135, 32.768 kHz, CL 7 pF, ESR 70 kohm max'))
    C(k, 'C82', '10p', 'XTAL32_I'); C(k, 'C83', '10p', 'XTAL32_O')
    pad('POR_B', 'POR_B'); pad('ONOFF', 'ONOFF'); pad('PMIC_ON_REQ', 'PMIC_ON_REQ'); pad('WAKEUP', 'WAKEUP')
    pad('TEST_MODE', 'GND')
    C(k, 'C84', '100n', 'POR_B')
    k.add('U10', 'hackerslide', 'TPS3840DL', 'TPS3840DL30', 'Package_TO_SOT_SMD:SOT-23-5',
          {'1': 'POR_B', '2': '+3V3', '3': 'GND', '4': 'RESET_BTN_N', '5': 'POR_CT'},
          fields=fields('C2862542', 'TPS3840DL30DBVR', 'Texas Instruments', Description='holds POR_B low below 3.0 V on +3V3, open drain, 300 nA'))
    C(k, 'C86', '100n', 'POR_CT')
    C(k, 'C87', '100n', '+3V3')
    k.add('SW2', 'Switch', 'SW_Push', 'RESET', 'hackerslide:SW_Alps_SKSWCFE010_3x2mm', {'1': 'RESET_BTN_N', '2': 'GND'},
          fields=fields('C255576', 'SKSWCFE010', 'Alps Alpine', Description='on the supervisor\'s manual-reset input (internal pull-up)'))
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
    m = d.sheet('memory', 'SDRAM 128 MB (positions for 256 MB) and boot flash', paper='A2', notes=[
        'Two Winbond W989D6DB (512 Mbit, 16 bits wide, 1.8 V low-power type) form one 32-bit bank of 128 MB on SEMC_CS0:',
        '    U3 carries D0-D15, U4 carries D16-D31. The brain pads are the ones NXP\'s board uses (data/sdram.csv); the chips are',
        '    not: NXP fits 3.3 V W9825G6KH. Both memory pad banks (NVCC_EMC1, NVCC_EMC2) therefore run at 1.8 V.',
        'U8/U9 are the same again on SEMC_CSX0 (ball L1) for 256 MB: NOT FITTED on the first build. On B silicon only CSX0 or',
        '    RDY may be a second SDRAM select (erratum ERR052401). No NXP board has two banks: this wiring is inferred.',
        'NOT PROVEN: this chip type asks for an extended mode register write at start-up (BA1 high); NXP\'s driver does not send',
        '    one and no report of this chip family on this controller was found. The data sheet gives full drive, all banks',
        '    refreshed as the reset state on one page and "undefined" on another. To be tried on the evaluation board first.',
        'Timing: 166 MHz at CAS latency 3 at most (NXP\'s own settings run their faster chips at 198 MHz).',
        'SEMC_DQS (ball J2) must stay unconnected: the chip loops its own clock back through that pad.',
        'Flash: FlexSPI1 port A on GPIO_SD_B2_06..11 (boot.md). FLEXSPI1_A_DQS (ball E14) must stay unconnected for 133 MHz.',
        'Pin numbers of both memories were compared with Winbond\'s data sheets (W989D6DB A01-002 p.5, W25Q128JW rev G p.6).'])
    rows = {r['semc_signal']: r for r in csv.DictReader(open(os.path.join(DATA, 'sdram.csv')))}
    DQ = ['A8', 'B9', 'B8', 'C9', 'C8', 'D9', 'D8', 'E9', 'E1', 'D2', 'D1', 'C2', 'C1', 'B2', 'B1', 'A2']
    AD = ['H7', 'H8', 'J8', 'J7', 'J3', 'J2', 'H3', 'H2', 'H1', 'G3', 'H9', 'G2', 'G1']
    CTL = {'BA0': 'G7', 'BA1': 'G8', 'semc_clk': 'F2', 'semc_cke': 'F3', 'semc_ras': 'F8', 'semc_cas': 'F7', 'semc_we': 'F9'}

    def sig(name):
        r = rows[name]
        if r['mcu_ball'] not in U:
            pad(r['mcu_pad'], r['evkb_net'])
        return r['evkb_net']
    cn = 100
    for ref, half, cs, fitted in (('U3', 0, 'CS0', True), ('U4', 1, 'CS0', True), ('U8', 0, 'CSX0', False), ('U9', 1, 'CSX0', False)):
        nets = {b: sig(f'ADDR{i:02d}') for i, b in enumerate(AD)}
        nets.update({b: sig(f'DATA{16 * half + i:02d}') for i, b in enumerate(DQ)})
        nets.update({b: sig(n) for n, b in CTL.items()})
        nets['E8'], nets['F1'], nets['G9'] = sig(f'DM{2 * half}'), sig(f'DM{2 * half + 1}'), sig(cs)
        for b in ('A9', 'E7', 'J9', 'A7', 'B3', 'C7', 'D3'):
            nets[b] = '+1V8'
        for b in ('A1', 'E3', 'J1', 'A3', 'B7', 'C3', 'D7'):
            nets[b] = 'GND'
        m.add(ref, 'hackerslide', 'W989D6DB', 'W989D6DBGX6I', 'Package_BGA:Alliance_TFBGA-54_8x8mm_Layout9x9_P0.8mm', nets, dnp=not fitted,
              fields=fields('C2641243', 'W989D6DBGX6I', 'Winbond', Description='512 Mbit low-power SDRAM, 1.8 V, 8 x 9 x 1.0 mm. The footprint '
                            'is the 8 x 8 mm one with the same ball pattern: widen its outline before layout'))
        for i in range(7):
            C(m, f'C{cn}', '100n', '+1V8', dnp=not fitted); cn += 1
    R(m, 'R51', '10k', sig('CS0'), '+1V8'); R(m, 'R52', '10k', sig('CSX0'), '+1V8', note='second bank deselected when not fitted or not set up')
    cn = 150
    FL = {'GPIO_SD_B2_06': ('FSPI_CS', '1'), 'GPIO_SD_B2_07': ('FSPI_CLK', '6'), 'GPIO_SD_B2_08': ('FSPI_D0', '5'),
          'GPIO_SD_B2_09': ('FSPI_D1', '2'), 'GPIO_SD_B2_10': ('FSPI_D2', '3'), 'GPIO_SD_B2_11': ('FSPI_D3', '7')}
    nets = {'4': 'GND', '8': '+1V8'}
    for name, (net, pin) in FL.items():
        pad(name, net)
        nets[pin] = net
    m.add('U5', 'Memory_Flash', 'W25Q128JVS', 'W25Q128JWPIQ', 'Package_SON:WSON-8-1EP_6x5mm_P1.27mm_EP3.4x4.3mm', nets,
          fields=fields('C2689660', 'W25Q128JWPIQ', 'Winbond', Description='128 Mbit QSPI NOR, 1.8 V, 0.8 mm high. IQ type: quad mode is '
                                                                           'fixed on. The centre pad is left unconnected'))
    R(m, 'R50', '10k', 'FSPI_CS', '+1V8', note='EVKB R165')
    C(m, 'C160', '100n', '+1V8'); C(m, 'C161', '1u', '+1V8')

    # ------------------------------------------------------------------------------------------ keyboard
    kb = d.sheet('keyboard', 'Keyboard: 47 keys on a TCA8418 scanner', paper='A2', notes=[
        'Layout and matrix positions come from hp_layout.py (N810-style rows, Esc, Tab, four arrows and OK).',
        'Each key: switch in series with a diode, anode toward the row; the scanner drives columns low and reads rows.',
        '    Both Space switches share one matrix position and one diode.',
        'Scanner at 3.3 V on the I2C_U bus, address 0x34. Its interrupt is open drain and goes to a 1.8 V wake pad of the',
        '    brain, pulled up to the SNVS supply. Reset comes from a port expander (later sheet); pulled up here.',
        'Unused scanner rows and columns are tied to +3V3 through 100k as the TI data sheet asks.'])
    mat = HP.matrix()
    nrow = max(r for r, c in mat.values()) + 1
    ncol = max(c for r, c in mat.values()) + 1
    assert nrow <= 8 and ncol <= 10
    n = 0
    for key in HP.keys():
        r, c = mat[key['name']]
        node = f'K{r}_{c}'
        for j, _xy in enumerate(key['switches']):
            n += 1
            kb.add(f'SW{10 + n}', 'hackerslide', 'KeySwitch', key['name'], 'hackerslide:SW_Alps_SKSWCFE010_3x2mm',
                   {'1': f'KCOL{c}', '2': node},
                   fields=fields('C255576', 'SKSWCFE010', 'Alps Alpine', Description=f'key "{key["name"]}" row {r} column {c}'))
        kb.add(f'D{10 + n}', 'Diode', '1N4148WS', '1N4148W4', 'Diode_SMD:D_SOD-882', {'2': f'KROW{r}', '1': node},
               fields=fields('C42432416', '1N4148W4', 'BORN', Description='DFN1006-2, 0.55 mm high: fits under the keycap flange'))
    use('I2C_U_SCL'); use('I2C_U_SDA'); use('KB_INT_N')
    nets = {'22': 'I2C_U_SDA', '23': 'I2C_U_SCL', '24': 'KB_INT_N', '20': 'KB_RST_N', '21': '+3V3', '19': 'GND', '25': 'GND'}
    rr = 60
    for r in range(8):
        nets[str(8 - r)] = f'KROW{r}'
        if r >= nrow:
            R(kb, f'R{rr}', '100k', f'KROW{r}', '+3V3'); rr += 1
    for c in range(10):
        nets[str(9 + c)] = f'KCOL{c}'
        if c >= ncol:
            R(kb, f'R{rr}', '100k', f'KCOL{c}', '+3V3'); rr += 1
    kb.add('U6', 'hackerslide', 'TCA8418RTW', 'TCA8418RTWR', 'Package_DFN_QFN:WQFN-24-1EP_4x4mm_P0.5mm_EP2.45x2.45mm', nets,
           fields=fields('C138713', 'TCA8418RTWR', 'Texas Instruments'))
    R(kb, 'R70', '100k', 'KB_INT_N', 'VDD_SNVS_ANA', note='open drain to a 1.8 V wake pad; the SNVS supply gives 1 mA at most')
    R(kb, 'R71', '10k', 'KB_RST_N', '+3V3')
    R(kb, 'R72', '2.2k', 'I2C_U_SCL', '+3V3'); R(kb, 'R73', '2.2k', 'I2C_U_SDA', '+3V3')
    C(kb, 'C130', '100n', '+3V3'); C(kb, 'C131', '1u', '+3V3')

    # ------------------------------------------------------------------------------------------ display link
    dp = d.sheet('display', 'Display link: e-paper, touch, front light', paper='A3', notes=[
        'The e-paper drive circuit is on the lid board (hackpad_lid_design.py). J2 is the 20-way cable to it through the',
        '    slider; pin k here is pin k on the lid board.',
        'E-paper on LPSPI1 (write only).',
        'Touch interrupt: the FT6336U drives 3.3 V levels, the wake pad is 1.8 V. Q2 passes only the low level (gate at the',
        '    1.8 V SNVS supply); R82 pulls the pad side up to that supply.',
        'Front light: LM3630A, two strings set independently over I2C (cool on ILED1, warm on ILED2), so no timer pad is',
        '    needed. Address 0x36 on the I2C_U bus. The panel specification gives no string current or voltage: its adapter',
        '    board feeds the strings from 15 V through resistors. START LOW (a few mA) AND MEASURE; set the 16 V limit in the',
        '    chip before turning the strings on (its power-on limit is 24 V; C141 is rated 50 V for that reason).',
        'FL_EN and TOUCH_RST_N will come from a port expander (later sheet).'])
    for net in ('EPD_SCK', 'EPD_MOSI', 'EPD_CS_N', 'EPD_DC', 'EPD_RST_N', 'EPD_BUSY', 'TOUCH_INT_N'):
        use(net)
    LID.link_connector(dp, 'J2', 'to the lid board through the slider')
    R(dp, 'R80', '100k', 'EPD_BUSY', 'GND', note='defined level with the lid unplugged')
    R(dp, 'R81', '10k', 'TOUCH_INT', '+3V3')
    R(dp, 'R82', '100k', 'TOUCH_INT_N', 'VDD_SNVS_ANA', note='the SNVS supply gives 1 mA at most: weak pull-ups only')
    dp.add('Q2', 'Transistor_FET', '2N7002', 'DMG1012T', 'Package_TO_SOT_SMD:SOT-523', {'1': 'VDD_SNVS_ANA', '2': 'TOUCH_INT_N', '3': 'TOUCH_INT'},
           fields=fields('C20512', 'DMG1012T-7', 'Diodes Incorporated', Description='threshold 1 V max. CHECK pin order 1 G, 2 S, 3 D'))
    R(dp, 'R83', '10k', 'TOUCH_RST_N', '+3V3')
    dp.add('U7', 'hackerslide', 'LM3630A', 'LM3630ATME', 'hackerslide:Texas_DSBGA-12_YFQ_1.42x1.94mm_Layout3x4_P0.4mm',
           {'C3': '+3V3', 'B1': 'FL_EN', 'C1': 'GND', 'C2': 'GND', 'A1': 'I2C_U_SDA', 'A2': 'I2C_U_SCL', 'B2': 'FL_INT_N', 'B3': 'GND',
            'A3': 'FL_SW', 'D1': 'FL_VOUT', 'D3': 'FL_C_K', 'D2': 'FL_W_K'},
           fields=fields('C1880284', 'LM3630ATME', 'Texas Instruments', Description='only about 100 in stock at JLCPCB on 2026-11-26: confirm before ordering'))
    dp.add('L2', 'Device', 'L', '10uH', 'Inductor_SMD:L_Taiyo-Yuden_NR-30xx', {'1': '+3V3', '2': 'FL_SW'},
           fields=fields('C45403', 'SWPA3015S100MT', 'Sunlord', Description='10 uH, 770 mA, 3 x 3 x 1.5 mm'))
    dp.add('D2', 'Device', 'D_Schottky', 'MBR0530', 'Diode_SMD:D_SOD-123', {'1': 'FL_VOUT', '2': 'FL_SW'},
           fields=fields('C82046', 'MBR0530T1G', 'onsemi'))
    R(dp, 'R84', '0', 'FL_VOUT', 'FL_C_A'); R(dp, 'R85', '0', 'FL_VOUT', 'FL_W_A')
    R(dp, 'R86', '100k', 'FL_EN', 'GND', note='front light off until the firmware enables it')
    R(dp, 'R87', '100k', 'FL_INT_N', '+3V3')
    C(dp, 'C140', '2.2u', '+3V3'); C(dp, 'C141', '1u/50V', 'FL_VOUT')
    for i, net in enumerate(('FL_VOUT', 'FL_EN', 'TOUCH_RST_N', 'FL_INT_N')):
        TP(dp, f'TP{20 + i}', net)

    # ------------------------------------------------------------------------------------------ power input
    pw = d.sheet('power', 'USB-C, charger, battery, fuel gauge, 3.3 V', paper='A2', notes=[
        'Carried over from the Linux design (same chips, same values) unless a line says otherwise.',
        'USB-C: device only, 5.1k on CC1/CC2. The charger never sees D+/D- (R203/R204 not fitted), so the input stays at 5 V',
        '    and the ILIM resistor caps it at about 0.755 A. A USB-C controller for power-delivery tricks is a later sheet.',
        'USB data goes to the brain\'s USB1 port, the one its built-in loader uses. USB1_VBUS must never exceed 5.6 V.',
        'Cell: GlobTek BL1950P4071611S1PCPT, 1950 mAh. Its plug is Molex Micro-Latch 2.00 mm (51065-0400): pins 1-2 red +,',
        '    3-4 black -. Header J4 mates with it; MEASURE the plug before first use. Header height not verified.',
        '    The charger resets to 2.05 A charge current; the input cap keeps the cell under about 1.25 A whatever the',
        '    register says. CHECK the pack\'s maximum charge current and set the register lower in firmware.',
        'U15 (eFuse, 1.86 A typical) limits everything fed from VSYS_LIM, as before: under the pack\'s 3.9 A rating and the',
        '    header\'s 2 A per contact.',
        '3.3 V: TPS63802 buck-boost from VSYS_LIM, TI reference values (0.47 uH, 511k / 91k = 3.31 V). The brain\'s PMIC_ON_REQ',
        '    (1.8 V logic, high = on) enables it; the always-on 3.0 V supply U12 keeps that pin alive. PG is a test pad.',
        'Power key SW3: to the brain\'s ONOFF pin and to the charger\'s /QON (ship-mode exit), each through a Schottky.',
        'Charger and gauge interrupts are open drain, pulled up to the 1.8 V SNVS supply, on wake pads.',
        'The USB-C socket is still the 3.26 mm one of the Linux design; the lower HRO TYPE-C-31-M-14 replaces it once its',
        '    drawing is turned into a footprint.'])
    pad('USB1_DP', 'USB_DP'); pad('USB1_DN', 'USB_DM'); pad('USB1_VBUS', 'VBUS')
    for net in ('I2C_P_SCL', 'I2C_P_SDA', 'CHG_INT_N', 'GAUGE_ALRT_N'):
        use(net)
    pw.add('J3', 'Connector', 'USB_C_Receptacle_USB2.0_16P', 'TYPE-C-31-M-12', 'Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12',
           {'A4': 'VBUS', 'A9': 'VBUS', 'B4': 'VBUS', 'B9': 'VBUS', 'A1': 'GND', 'A12': 'GND', 'B1': 'GND', 'B12': 'GND',
            'S1': 'GND', 'A5': 'CC1', 'B5': 'CC2', 'A6': 'USB_DP', 'B6': 'USB_DP', 'A7': 'USB_DM', 'B7': 'USB_DM'},
           fields=fields('C165948', 'TYPE-C-31-M-12', 'Korean Hroparts'))
    R(pw, 'R200', '5.1k', 'CC1', 'GND'); R(pw, 'R201', '5.1k', 'CC2', 'GND')
    pw.add('U17', 'Power_Protection', 'USBLC6-2SC6', 'USBLC6-2SC6', 'Package_TO_SOT_SMD:SOT-23-6',
           {'1': 'USB_DP', '6': 'USB_DP', '3': 'USB_DM', '4': 'USB_DM', '5': 'ESD_BIAS', '2': 'GND'},
           fields=fields('C7519', 'USBLC6-2SC6', 'STMicroelectronics'))
    C(pw, 'C200', '100n', 'ESD_BIAS'); C(pw, 'C201', '1u', 'VBUS')
    pw.add('D200', 'Device', 'D_Zener', 'SMF6.0A', 'Diode_SMD:D_SOD-123F', {'1': 'VBUS', '2': 'GND'},
           fields=fields('C123790', 'SMF6.0A', 'MDD', Description='VBUS TVS, 6 V stand-off'))
    R(pw, 'R203', '0', 'USB_DP', 'CHG_DP', dnp=True); R(pw, 'R204', '0', 'USB_DM', 'CHG_DM', dnp=True)
    R(pw, 'R205', '15k', 'CHG_DP', 'GND'); R(pw, 'R206', '15k', 'CHG_DM', 'GND')
    pw.add('U13', 'Battery_Management', 'BQ25895RTW', 'BQ25895RTWR',
           'Package_DFN_QFN:Texas_RTW_WQFN-24-1EP_4x4mm_P0.5mm_EP2.7x2.7mm_ThermalVias',
           {'1': 'VBUS', '2': 'CHG_DP', '3': 'CHG_DM', '10': 'CHG_ILIM', '4': 'CHG_STAT', '6': 'I2C_P_SDA', '5': 'I2C_P_SCL',
            '7': 'CHG_INT_N', '8': 'GND', '9': 'GND', '12': 'CHG_QON_N', '17': 'GND', '18': 'GND', '25': 'GND', '23': 'PMID',
            '19': 'CHG_SW', '20': 'CHG_SW', '21': 'CHG_BTST', '15': 'VSYS', '16': 'VSYS', '13': 'VBAT', '14': 'VBAT', '22': 'REGN',
            '11': 'CHG_TS'}, fields=fields('C80200', 'BQ25895RTWR', 'Texas Instruments'))
    C(pw, 'C202', '22u', 'PMID'); C(pw, 'C203', '22u', 'PMID')
    pw.add('C204', 'Device', 'C', '47n', 'Capacitor_SMD:C_0402_1005Metric', {'1': 'CHG_BTST', '2': 'CHG_SW'},
           fields=fields('C307434', 'CL05B473KO5NNNC', 'Samsung'))
    C(pw, 'C205', '4.7u/0603', 'REGN')
    pw.add('L4', 'Device', 'L', '2.2uH', 'Inductor_SMD:L_Sunlord_MWSA0402S', {'1': 'CHG_SW', '2': 'VSYS'},
           fields=fields('C408335', 'MWSA0402S-2R2MT', 'Sunlord', Description='saturation 4.0 A, 58 mohm, 2.0 mm high'))
    C(pw, 'C206', '22u', 'VSYS'); C(pw, 'C207', '22u', 'VSYS'); C(pw, 'C208', '10u', 'VBAT')
    R(pw, 'R207', '470', 'CHG_ILIM', 'GND', note='input limit 355/470 = 0.755 A typical')
    R(pw, 'R208', '100k', 'CHG_INT_N', 'VDD_SNVS_ANA')
    pw.add('R209', 'Device', 'R', '5.23k', 'Resistor_SMD:R_0402_1005Metric', {'1': 'REGN', '2': 'CHG_TS'},
           fields=fields('C25907', '0402WGF5231TCE', 'UNI-ROYAL'))
    pw.add('R210', 'Device', 'R', '30.1k', 'Resistor_SMD:R_0402_1005Metric', {'1': 'CHG_TS', '2': 'GND'},
           fields=fields('C29402', '0402WGF3012TCE', 'UNI-ROYAL'))
    pw.add('TH1', 'Device', 'Thermistor_NTC', '10k B3380', 'Resistor_SMD:R_0402_1005Metric', {'1': 'CHG_TS', '2': 'GND'},
           fields=fields('C77131', 'NCP15XH103F03RC', 'Murata', Description='on the board next to the battery'))
    R(pw, 'R211', '2.2k', 'VSYS', 'CHG_LED_A')
    pw.add('D201', 'Device', 'LED', 'red', 'LED_SMD:LED_0603_1608Metric', {'2': 'CHG_LED_A', '1': 'CHG_STAT'},
           fields=fields('C2286', 'KT-0603R', 'Hubei KENTO', Description='charging'))
    pw.add('J4', 'Connector', 'Conn_01x04_Pin', 'BATT', 'Connector_Molex:Molex_Micro-Latch_53254-0470_1x04_P2.00mm_Horizontal',
           {'1': 'VBAT', '2': 'VBAT', '3': 'GND', '4': 'GND'},
           fields=fields('C293629', '532540470', 'Molex', Description='mates with the pack\'s Molex 51065-0400 plug: 1-2 +, 3-4 -'))
    pw.add('U14', 'hackerslide', 'MAX17048', 'MAX17048G+T10', 'Package_DFN_QFN:TDFN-8-1EP_2x2mm_P0.5mm_EP0.8x1.2mm',
           {'1': 'GND', '2': 'VBAT', '3': 'VBAT', '4': 'GND', '5': 'GAUGE_ALRT_N', '6': 'GND', '7': 'I2C_P_SCL', '8': 'I2C_P_SDA', '9': 'GND'},
           fields=fields('C2682616', 'MAX17048G+T10', 'Analog Devices / Maxim', Description='fuel gauge, address 0x36'))
    C(pw, 'C209', '100n', 'VBAT'); R(pw, 'R212', '100k', 'GAUGE_ALRT_N', 'VDD_SNVS_ANA')
    R(pw, 'R213', '2.2k', 'I2C_P_SCL', '+3V3'); R(pw, 'R214', '2.2k', 'I2C_P_SDA', '+3V3')
    pw.add('U15', 'hackerslide', 'TPS2595DSG', 'TPS259531DSGR', 'Package_SON:WSON-8-1EP_2x2mm_P0.5mm_EP0.9x1.6mm',
           {'3': 'VSYS', '4': 'VSYS', '2': 'FUSE_EN', '7': 'BATT_ILIM', '5': 'VSYS_LIM', '6': 'BATT_OC_N', '8': 'GND', '9': 'GND'},
           fields=fields('C2155674', 'TPS259531DSGR', 'Texas Instruments', Description='eFuse, auto-retry'))
    R(pw, 'R215', '1.1k', 'BATT_ILIM', 'GND', note='limit 1.86 A typical (about 1.73-1.99 A)')
    R(pw, 'R216', '10k', 'BATT_OC_N', '+3V3'); R(pw, 'R217', '10M', 'VSYS', 'FUSE_EN'); C(pw, 'C210', '100n', 'VSYS')
    pw.add('U16', 'hackerslide', 'TPS63802', 'TPS63802DLAR', 'hackerslide:Texas_DLA0010A_VSON-HR-10_3x2mm',
           {'10': 'VSYS_LIM', '1': 'PMIC_ON_REQ', '2': 'GND', '3': 'GND', '8': 'GND', '9': 'BB_L1', '7': 'BB_L2', '6': '+3V3',
            '4': 'BB_FB', '5': 'BB_PG'}, fields=fields('C2845237', 'TPS63802DLAR', 'Texas Instruments', Description='3.3 V, 2 A, 11 uA idle'))
    pw.add('L5', 'Device', 'L', '0.47uH', 'Inductor_SMD:L_Murata_DFE201610P', {'1': 'BB_L1', '2': 'BB_L2'},
           fields=fields('C668312', 'DFE201612E-R47M=P2', 'Murata', Description='0.47 uH, 26 mohm, 2.0 x 1.6 x 1.2 mm (TI table 10-2). CHECK the footprint'))
    pw.add('R218', 'Device', 'R', '511k', 'Resistor_SMD:R_0402_1005Metric', {'1': '+3V3', '2': 'BB_FB'},
           fields=fields('C64042', '0402WGF5113TCE', 'UNI-ROYAL'))
    pw.add('R219', 'Device', 'R', '91k', 'Resistor_SMD:R_0402_1005Metric', {'1': 'BB_FB', '2': 'GND'},
           fields=fields('C4147', '0402WGF9102TCE', 'UNI-ROYAL'))
    R(pw, 'R220', '100k', 'BB_PG', '+3V3'); R(pw, 'R221', '100k', 'PMIC_ON_REQ', 'GND', note='the enable must not float')
    C(pw, 'C211', '10u', 'VSYS_LIM'); C(pw, 'C212', '22u/0603', '+3V3'); C(pw, 'C213', '22u/0603', '+3V3')
    pw.add('SW3', 'Switch', 'SW_Push', 'PWR', 'Button_Switch_SMD:SW_SPST_EVQP7C', {'1': 'PWR_SW_N', '2': 'GND'},
           fields=fields('C388883', 'EVQP7C01P', 'Panasonic', Description='side-actuated power key'))
    SCHOTTKY(pw, 'D202', 'CHG_QON_N', 'PWR_SW_N', note='/QON'); SCHOTTKY(pw, 'D203', 'ONOFF', 'PWR_SW_N', note='brain ONOFF (internal pull-up)')
    for i, net in enumerate(('VBUS', 'VSYS', 'VBAT', 'VSYS_LIM', 'BB_PG', 'REGN', 'CHG_TS', 'CHG_QON_N', 'BATT_OC_N')):
        TP(pw, f'TP{30 + i}', net)

    # ------------------------------------------------------------------------------------------ audio
    au = d.sheet('audio', 'Audio out: ES8316 codec and 3-pole headphone jack', paper='A3', notes=[
        'Audio OUT only (David 2026-11-26): 3-pole jack sunk into a notch in the board edge, about 2.15 mm above the board.',
        'Codec circuit carried over from the Linux design (Everest application circuit): AVDD/PVDD 3.3 V, DVDD/CPVDD 1.8 V,',
        '    I2C address 0x10 on the I2C_U bus, master clock required. Its two recording inputs are grounded through',
        '    capacitors: the built-in microphones go straight to the brain.',
        'The master clock pad is also boot strap 9 (pulled low by 10k on the brain sheet); the codec pin is an input.',
        'Jack terminals from the XKB drawing: 1 sleeve, 2 and 3 signal, 4-5 an isolated switch. Which of 2 and 3 is the tip',
        '    is not stated: a wrong guess swaps left and right, which the firmware can swap back. Whether the switch is',
        '    closed with or without a plug is not stated either: the firmware learns the polarity.',
        'HPGND joins GND only through R236, placed at the jack.'])
    for net in ('AUD_DAC', 'AUD_ADC', 'AUD_BCLK', 'AUD_LRCK'):
        use(net)
    au.add('U18', 'hackerslide', 'ES8316', 'ES8316', 'Package_DFN_QFN:VQFN-32-1EP_4x4mm_P0.4mm_EP2.8x2.8mm',
           {'1': 'I2C_U_SCL', '32': 'I2C_U_SDA', '31': 'GND', '2': 'BT_CFG9', '6': 'AUD_BCLK', '8': 'AUD_LRCK', '7': 'AUD_DAC',
            '9': 'AUD_ADC', '10': 'HP_DET', '11': 'CODEC_GPIO2', '12': 'CODEC_IRQ', '3': '+1V8', '4': '+3V3', '22': 'AVDD_CODEC',
            '14': '+1V8', '20': 'HP_L', '19': 'HP_R', '30': 'MIC_P', '29': 'MIC_N', '26': 'MICBIAS', '21': 'DACVREF', '24': 'ADCVREF',
            '25': 'VMID', '15': 'CPTOP', '16': 'CPBOT', '13': 'CPVSSP', '18': 'HPGND', '5': 'GND', '23': 'GND', '17': 'GND', '33': 'GND'},
           fields=fields('C365735', 'ES8316', 'Everest Semiconductor'))
    R(au, 'R230', '0', '+3V3', 'AVDD_CODEC', note='place a ferrite here if noise shows up')
    for i, net in enumerate(('+1V8', '+3V3', 'AVDD_CODEC', '+1V8')):
        C(au, f'C{230 + i}', '100n', net)
    C(au, 'C234', '10u', 'AVDD_CODEC'); C(au, 'C235', '1u', 'DACVREF'); C(au, 'C236', '1u', 'ADCVREF'); C(au, 'C237', '1u', 'VMID')
    C(au, 'C238', '1u', 'CPTOP', 'CPBOT'); C(au, 'C239', '4.7u', 'CPVSSP'); C(au, 'C240', '1u', 'MICBIAS'); C(au, 'C241', '1u', '+1V8')
    C(au, 'C242', '1u', 'MIC_P', 'HPGND'); C(au, 'C243', '1u', 'MIC_N', 'HPGND')
    R(au, 'R231', '33', 'HP_L', 'JACK_A'); R(au, 'R232', '33', 'HP_R', 'JACK_B')
    R(au, 'R233', '100k', 'HP_DET', '+3V3', note='jack switch to ground on the other side')
    R(au, 'R234', '100k', 'CODEC_GPIO2', 'GND'); R(au, 'R235', '100k', 'CODEC_IRQ', 'GND')
    R(au, 'R236', '0', 'HPGND', 'GND', note='single ground join, at the jack')
    au.add('J5', 'hackerslide', 'PJ-3528S', 'PJ-3528S', 'hackerslide:Jack_3.5mm_XKB_PJ-3528S_EdgeNotch',
           {'3': 'JACK_A', '2': 'JACK_B', '1': 'HPGND', '5': 'HP_DET', '4': 'GND'},
           fields=fields('C2764617', 'PJ-3528S', 'XKB Connection', Description='3-pole, 4.1 mm tall, sunk into the board edge'))
    TVS(au, 'D210', 'JACK_A'); TVS(au, 'D211', 'JACK_B')
    for i, net in enumerate(('AUD_LRCK', 'AUD_BCLK', 'AUD_DAC', 'HP_DET')):
        TP(au, f'TP{40 + i}', net)

    # ------------------------------------------------------------------------------------------ card and port expanders
    io = d.sheet('card_io', 'microSD card and port expanders', paper='A3', notes=[
        'microSD on USDHC1 (3.3 V signalling only; the pad bank NVCC_SD1 is fixed at 3.3 V). Card detect is a switch to ground',
        '    on a 1.8 V wake pad, pulled up to the SNVS supply. Socket and protection as in the Linux design.',
        'Port expanders: two TCA6416A on the I2C_P bus (0x20 and 0x21) carry the slow control lines the brain has no pads',
        '    for. Their interrupt outputs are open drain and share one wake pad. Ports are inputs after reset, so every line',
        '    that must have a level before the firmware runs has its own pull resistor on its own sheet.',
        'IOX_A bits so far: 0 keyboard reset, 1 touch reset, 2 front-light enable, 3 front-light fault, 4 battery limiter',
        '    fault, 5 3.3 V good, 6 codec interrupt. The rest, and all of IOX_B, wait for the radio and sensor sheets.'])
    for net in ('SD_CMD', 'SD_CLK', 'SD_D0', 'SD_D1', 'SD_D2', 'SD_D3', 'SD_CD_N', 'IOX_INT_N'):
        use(net)
    io.add('J6', 'Connector', 'Micro_SD_Card_Det2', 'microSD', 'Connector_Card:microSD_HC_Molex_104031-0811',
           {'1': 'SD_D2', '2': 'SD_D3', '3': 'SD_CMD', '4': '+3V3', '5': 'SD_CLK', '6': 'GND', '7': 'SD_D0', '8': 'SD_D1',
            '9': 'SD_CD_N', '10': 'GND', '11': 'GND'}, fields=fields('C585350', '1040310811', 'Molex'))
    for i, net in enumerate(('SD_CMD', 'SD_D0', 'SD_D1', 'SD_D2', 'SD_D3')):
        R(io, f'R{250 + i}', '47k', net, '+3V3')
    R(io, 'R255', '100k', 'SD_CD_N', 'VDD_SNVS_ANA')
    C(io, 'C250', '10u', '+3V3'); C(io, 'C251', '100n', '+3V3')
    for ref, nets in (('U21', ('SD_CLK', 'SD_CMD', 'SD_D0', 'SD_D1')), ('U22', ('SD_D2', 'SD_D3', 'SD_CD_N', None))):
        pins = {'3': 'GND', '8': 'GND'}
        for pin, net in zip(('1', '2', '4', '5'), nets):
            if net:
                pins[pin] = net
        io.add(ref, 'Power_Protection', 'TPD4E05U06DQA', 'TPD4E05U06DQAR', 'Package_SON:USON-10_2.5x1.0mm_P0.5mm', pins,
               fields=fields('C138714', 'TPD4E05U06DQAR', 'Texas Instruments', Description='card ESD protection'))
    IOX_A = ['KB_RST_N', 'TOUCH_RST_N', 'FL_EN', 'FL_INT_N', 'BATT_OC_N', 'BB_PG', 'CODEC_IRQ']
    for ref, addr, bits in (('U19', 'GND', IOX_A), ('U20', '+3V3', [])):
        nets = {'23': '+3V3', '21': '+3V3', '19': 'I2C_P_SCL', '20': 'I2C_P_SDA', '22': 'IOX_INT_N', '24': 'IOX_RST_N', '18': addr,
                '9': 'GND', '25': 'GND'}
        for i, net in enumerate(bits):
            nets[str(1 + i) if i < 8 else str(2 + i)] = net
        io.add(ref, 'hackerslide', 'TCA6416ARTW', 'TCA6416ARTWR', 'Package_DFN_QFN:WQFN-24-1EP_4x4mm_P0.5mm_EP2.45x2.45mm', nets,
               fields=fields('C182336', 'TCA6416ARTWR', 'Texas Instruments', Description='port expander, address ' + ('0x20' if addr == 'GND' else '0x21')))
    R(io, 'R256', '100k', 'IOX_INT_N', 'VDD_SNVS_ANA'); R(io, 'R257', '10k', 'IOX_RST_N', '+3V3')
    C(io, 'C252', '100n', '+3V3'); C(io, 'C253', '100n', '+3V3')
    TP(io, 'TP50', 'IOX_INT_N'); TP(io, 'TP51', 'IOX_RST_N')

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
