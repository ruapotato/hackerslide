"""Hack pad: which brain pad does what.  One table, checked against NXP's pin-function table.

  python3 hackpad_pins.py            # check, print a summary
  python3 hackpad_pins.py --md       # write docs/hack-pad-pins.md

PLAN, NOT FINAL.  Each row: pad, the pad function used (as spelled in hardware/hackpad/data/pinmux.csv, or GPIO, or an
analogue channel), the net name, and what it is for.  The check proves only that the function exists on that pad and
that no pad is used twice; it does not prove that two functions of one peripheral may be split over pad groups, nor
any timing.  The SNVS pads are 1.8 V and weak (data/power.md), so they only take open-drain signals pulled up to
the SNVS supply.  Slow control lines (resets, enables, most interrupts) are not here: they go to I2C port expanders.

Things this plan assumes that are NOT yet verified from a datasheet:
  * the camera port's 8-bit mode takes its data on CSI_DATA02..09 (as on earlier i.MX RT parts);
  * the SDR chips accept 1.8 V logic on the LPSPI4 pads of the 1.8 V bank (else a level shifter);
  * ST25R3916B run in its I2C mode; ESP32-C6 as an SPI slave.
"""
import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROWS = {r['pad']: r for r in csv.DictReader(open(os.path.join(HERE, '..', 'hackpad', 'data', 'pinmux.csv')))}

P = []   # (pad, function, net, use)


def a(pad, fn, net, use):
    P.append(('GPIO_' + pad, fn, net, use))


# SDR samples: FPGA -> camera port
a('AD_12', 'VIDEO_MUX_CSI_PIXCLK', 'SDR_CLK', 'SDR sample bus clock from the FPGA')
a('AD_14', 'VIDEO_MUX_CSI_VSYNC', 'SDR_FRAME', 'SDR sample bus frame')
a('AD_15', 'VIDEO_MUX_CSI_HSYNC', 'SDR_VALID', 'SDR sample bus valid')
for i in range(8):
    a(f'AD_{16 + i}', f'VIDEO_MUX_CSI_DATA{9 - i:02d}', f'SDR_D{7 - i}', 'SDR sample bus data')
# SDR control, 1.8 V bank (shares the flash bank's supply)
a('SD_B2_00', 'LPSPI4_SCK', 'SDR_SCK', 'SDR control SPI')
a('SD_B2_02', 'LPSPI4_SDO', 'SDR_MOSI', 'SDR control SPI')
a('SD_B2_03', 'LPSPI4_SDI', 'SDR_MISO', 'SDR control SPI')
a('SD_B2_01', 'LPSPI4_PCS0', 'SDR_CS_RADIO_N', 'AT86RF215 select')
a('SD_B2_04', 'LPSPI4_PCS1', 'SDR_CS_FPGA_N', 'FPGA select (also loads it)')
a('SD_B2_05', 'LPSPI4_PCS2', 'SDR_CS_SYNTH_N', 'converter synthesizer select')
# shortwave receiver's converter (it is the clock master; its master clock comes from the Si5351)
a('LPSR_06', 'SAI4_RX_DATA', 'HF_I2S_DATA', 'shortwave ADC data')
a('LPSR_07', 'SAI4_RX_BCLK', 'HF_I2S_BCLK', 'shortwave ADC bit clock')
a('LPSR_08', 'SAI4_RX_SYNC', 'HF_I2S_LRCK', 'shortwave ADC word clock')
# packet radios: one SPI bus
a('LPSR_10', 'LPSPI6_SCK', 'RF_SCK', 'radio SPI')
a('LPSR_11', 'LPSPI6_SDO', 'RF_MOSI', 'radio SPI')
a('LPSR_12', 'LPSPI6_SDI', 'RF_MISO', 'radio SPI')
a('LPSR_09', 'LPSPI6_PCS0', 'RF_CS_CC1101_N', 'CC1101 select')
a('DISP_B2_12', 'GPIO', 'RF_CS_LR1121_N', 'LR1121 select')
a('DISP_B2_13', 'GPIO', 'RF_CS_NRF_N', 'Si24R1 select')
a('EMC_B2_20', 'GPIO', 'RF_CS_TC_N', 'MAX31856 thermocouple select (same bus)')
a('AD_13', 'GPIO', 'RF_CS_WIFI_N', 'ESP32-C6 select')
a('EMC_B2_19', 'QTIMER3_TIMER2', 'CC1101_GDO0', 'raw sub-GHz data, timed by a counter')
a('EMC_B2_18', 'QTIMER3_TIMER1', 'GPS_PPS', 'GPS second pulse, timed by a counter')
a('DISP_B2_10', 'LPUART2_TX', 'GPS_RXD', 'to the GPS module')
a('DISP_B2_11', 'LPUART2_RX', 'GPS_TXD', 'from the GPS module')
a('DISP_B1_00', 'QTIMER1_TIMER0', 'IR_TX', 'infrared send')
a('DISP_B1_01', 'QTIMER1_TIMER1', 'IR_RX', 'infrared receive')
a('DISP_B1_04', 'QTIMER2_TIMER1', 'LF_CARRIER', '125 kHz carrier')
a('DISP_B1_05', 'QTIMER2_TIMER2', 'LF_DATA', '125 kHz demodulated data')
# I2C buses
a('AD_32', 'LPI2C1_SCL', 'I2C_S_SCL', 'sensor bus')
a('AD_33', 'LPI2C1_SDA', 'I2C_S_SDA', 'sensor bus')
a('DISP_B1_02', 'LPI2C3_SCL', 'I2C_U_SCL', 'touch, keyboard, codec, NFC')
a('DISP_B1_03', 'LPI2C3_SDA', 'I2C_U_SDA', 'touch, keyboard, codec, NFC')
a('LPSR_05', 'LPI2C5_SCL', 'I2C_P_SCL', 'charger, gauge, USB-C, clock, port expanders (works in low-power modes)')
a('LPSR_04', 'LPI2C5_SDA', 'I2C_P_SDA', 'charger, gauge, USB-C, clock, port expanders')
# audio
a('DISP_B2_06', 'SAI1_RX_DATA00', 'AUD_ADC', 'codec to brain')
a('DISP_B2_07', 'SAI1_TX_DATA00', 'AUD_DAC', 'brain to codec')
a('DISP_B2_08', 'SAI1_TX_BCLK', 'AUD_BCLK', 'audio bit clock')
a('DISP_B2_09', 'SAI1_TX_SYNC', 'AUD_LRCK', 'audio word clock')
a('DISP_B2_03', 'SAI1_MCLK', 'BT_CFG9', 'audio master clock; ALSO boot strap 9 (pulled low; the codec input does not drive it)')
a('LPSR_00', 'MIC_CLK', 'PDM_CLK', 'two wide-band microphones')
a('LPSR_01', 'MIC_BITSTREAM00', 'PDM_DATA', 'two wide-band microphones')
# display, card
a('AD_28', 'LPSPI1_SCK', 'EPD_SCK', 'e-paper')
a('AD_30', 'LPSPI1_SDO', 'EPD_MOSI', 'e-paper')
a('AD_29', 'LPSPI1_PCS0', 'EPD_CS_N', 'e-paper')
a('AD_31', 'GPIO', 'EPD_DC', 'e-paper data/command')
a('AD_34', 'GPIO', 'EPD_RST_N', 'e-paper reset')
a('AD_35', 'GPIO', 'EPD_BUSY', 'e-paper busy')
for i, n in enumerate(('CMD', 'CLK', 'DATA0', 'DATA1', 'DATA2', 'DATA3')):
    a(f'SD_B1_{i:02d}', 'USDHC1_' + n, 'SD_' + n.replace('DATA', 'D'), 'microSD')
# bench header through the level shifter; the same pads give CAN, UARTs, PWM and capture
for i, pad in enumerate(('AD_00', 'AD_01', 'AD_02', 'AD_03', 'AD_04', 'AD_05', 'AD_26', 'AD_27')):
    a(pad, 'FLEXIO2_FLEXIO%02d' % (i if i < 6 else 20 + i), f'BENCH{i}', 'bench header line (logic analyser, pattern, UART, PWM)')
a('DISP_B2_14', 'CAN1_TX', 'CAN_TX', 'CAN transceiver')
a('DISP_B2_15', 'CAN1_RX', 'CAN_RX', 'CAN transceiver')
for pad, ch, net, use in (('AD_06', 'ADC1_CH0A', 'AIN_RFPWR', 'RF power detector'), ('AD_07', 'ADC1_CH0B', 'AIN_ECG', 'heart signal'),
                          ('AD_08', 'ADC1_CH1A', 'AIN_GAS', 'gas sensor'), ('AD_09', 'ADC1_CH1B', 'AIN_BENCH1', 'bench analogue in 1'),
                          ('AD_10', 'ADC1_CH2A', 'AIN_BENCH2', 'bench analogue in 2'), ('AD_11', 'ADC1_CH2B', 'AIN_SPARE', 'spare')):
    a(pad, ch, net, use)
# interrupts that must wake the device: SNVS pads, open drain, pulled up to the SNVS supply
for i, (net, use) in enumerate((('IOX_INT_N', 'port expanders'), ('KB_INT_N', 'keyboard'), ('TOUCH_INT_N', 'touch'),
                                ('CHG_INT_N', 'charger'), ('GAUGE_ALRT_N', 'fuel gauge'), ('USBC_INT_N', 'USB-C controller'),
                                ('RTC_INT_N', 'clock chip'), ('IMU_INT_N', 'motion sensor'), ('SD_CD_N', 'card detect'),
                                ('LID_N', 'slider open/closed'))):
    a(f'SNVS_{i:02d}', 'GPIO', net, 'wake: ' + use)
RESERVED = {'GPIO_EMC_B1_40': 'second memory bank select (SEMC_RDY)', 'GPIO_EMC_B1_41': 'second memory bank select (SEMC_CSX0)',
            'GPIO_EMC_B1_39': 'must float (SEMC_DQS)'}
SHARED = {'GPIO_DISP_B2_03'}         # also a boot strap in hackpad_design.py


def check():
    seen = {}
    for pad, fn, net, use in P:
        r = ROWS[pad]
        assert pad not in seen and pad not in RESERVED, pad
        seen[pad] = net
        have = {f for i in range(12) for f in (r[f'ALT{i}'] or '').split(' | ')} | set((r['analog_functions'] or '').replace(' ', '').split('|'))
        assert fn == 'GPIO' or fn in have, (pad, fn, sorted(have))
    return seen


if __name__ == '__main__':
    seen = check()
    import hackpad_design as h
    h.build()
    clash = [p for p in seen if ROWS[p]['ball'] in h.U and p not in SHARED]
    assert not clash, clash
    free = [p for p, r in ROWS.items() if r['ball'] not in h.U and p not in seen and p not in RESERVED]
    print(len(P), 'pads planned;', len(free), 'free:', ' '.join(free))
    if '--md' in sys.argv:
        out = ['# Hack pad: brain pin plan', '', 'Generated by `hardware/scripts/hackpad_pins.py`. A plan, not final; the',
               'unverified assumptions are listed at the top of that script. Slow control lines go to I2C port expanders.', '',
               '| Pad | Ball | Function | Net | Use |', '|---|---|---|---|---|']
        out += [f"| {p[5:]} | {ROWS[p]['ball']} | {fn} | {net} | {use} |" for p, fn, net, use in P]
        out += [f"| {p[5:]} | {ROWS[p]['ball']} | reserved | | {u} |" for p, u in RESERVED.items()]
        out += ['', 'Free: ' + (', '.join(p[5:] for p in free) or 'none') + '.', '']
        open(os.path.join(HERE, '..', '..', 'docs', 'hack-pad-pins.md'), 'w').write('\n'.join(out))
