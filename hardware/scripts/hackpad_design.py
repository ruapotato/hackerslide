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
from parts import C, CAP, R, RES, TP, fields

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
