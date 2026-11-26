"""HackerSlide hack pad, lid board: the small board in the display half.

  python3 hackpad_lid_design.py ../hackpad-lid

DRAFT, NOT BUILT, NOT REVIEWED.  It holds only what must sit next to the e-paper panel: the panel's drive circuit,
copied from the maker's reference circuit (Good Display GDEY0426T82-FT01C specification, section 8.2, page 11), and
the three flat-cable sockets of the panel (display 24-pin, touch 6-pin, front light 6-pin).  Pin tables: the same
specification section 5 (display) and its outline drawing (touch and front light).  One 20-way flat cable (J1) goes
through the slider to the main board; pin k here is pin k there.  Tallest part: 1.5 mm (L1).
"""
import sys

from kigen import Design
from parts import C, R, TP, fields

LINK = {1: 'GND', 2: '+3V3', 3: 'GND', 4: 'EPD_SCK', 5: 'GND', 6: 'EPD_MOSI', 7: 'EPD_CS_N', 8: 'EPD_DC', 9: 'EPD_RST_N',
        10: 'EPD_BUSY', 11: 'GND', 12: 'I2C_U_SCL', 13: 'I2C_U_SDA', 14: 'TOUCH_INT', 15: 'TOUCH_RST_N', 16: 'GND',
        17: 'FL_C_A', 18: 'FL_C_K', 19: 'FL_W_K', 20: 'FL_W_A'}


def link_connector(sheet, ref, descr):
    nets = {str(k): v for k, v in LINK.items()}
    nets['MP'] = 'GND'
    return sheet.add(ref, 'Connector_Generic_MountingPin', 'Conn_01x20_MountingPin', 'FH34SRJ-20S-0.5SH',
                     'hackerslide:Hirose_FH34SRJ-20S-0.5SH_1x20-1MP_P0.50mm_Horizontal', nets,
                     fields=fields('C2802370', 'FH34SRJ-20S-0.5SH(50)', 'Hirose', Description=descr))


def build():
    d = Design('hackpad-lid', 'HackerSlide hack pad lid board', comments=[
        'Rev 0.1 DRAFT. Not built, not reviewed. E-paper drive circuit after Good Display GDEY0426T82-FT01C spec section 8.2.'])
    s = d.sheet('panel', 'E-paper drive circuit and panel sockets', paper='A3', notes=[
        'Reference circuit of the panel maker, same values: L1 47 uH, Q1 Si1308EDL, D1-D3 MBR0530, R1 1M, R2 2.2 ohm,',
        '    4.7 uF / 25 V on the drive rails, 1 uF on VCI, VDD and VCOM.',
        'D1/D2 polarity follows the usual charge pump of this controller family (VGL negative): the reference drawing is',
        '    too coarse to read the diode direction. CHECK against a known-good board before ordering.',
        'BS1 low = 4-wire SPI. Temperature-sensor pins 6, 7 and VPP are left open as in the reference circuit.',
        'Touch (FT6336U): 3.3 V supply; its interrupt goes to the main board, which shifts it to the 1.8 V wake pad.',
        'Front light: two LED strings (cool, warm), driven from the main board; this board only passes them through.',
        'All three panel sockets take contacts on either side of the cable (Hirose FH34SRJ, 1.0 mm high).'])
    link_connector(s, 'J1', 'to the main board through the slider')
    epd = {'2': 'GDR', '3': 'RESE', '5': 'VSH2', '8': 'GND', '9': 'EPD_BUSY', '10': 'EPD_RST_N', '11': 'EPD_DC', '12': 'EPD_CS_N',
           '13': 'EPD_SCK', '14': 'EPD_MOSI', '15': '+3V3', '16': '+3V3', '17': 'GND', '18': 'EPD_VDD', '20': 'VSH1', '21': 'PREVGH',
           '22': 'VSL', '23': 'PREVGL', '24': 'VCOM', 'MP': 'GND'}
    s.add('J2', 'Connector_Generic_MountingPin', 'Conn_01x24_MountingPin', 'FH34SRJ-24S-0.5SH',
          'hackerslide:Hirose_FH34SRJ-24S-0.5SH_1x24-1MP_P0.50mm_Horizontal', epd,
          fields=fields('C324726', 'FH34SRJ-24S-0.5SH(50)', 'Hirose', Description='e-paper panel, 24 contacts'))
    s.add('J3', 'Connector_Generic_MountingPin', 'Conn_01x06_MountingPin', 'FH34SRJ-6S-0.5SH',
          'hackerslide:Hirose_FH34SRJ-6S-0.5SH_1x06-1MP_P0.50mm_Horizontal',
          {'1': 'GND', '2': '+3V3', '3': 'TOUCH_RST_N', '4': 'TOUCH_INT', '5': 'I2C_U_SDA', '6': 'I2C_U_SCL', 'MP': 'GND'},
          fields=fields('C224194', 'FH34SRJ-6S-0.5SH(50)', 'Hirose', Description='touch panel (FT6336U)'))
    s.add('J4', 'Connector_Generic_MountingPin', 'Conn_01x06_MountingPin', 'FH34SRJ-6S-0.5SH',
          'hackerslide:Hirose_FH34SRJ-6S-0.5SH_1x06-1MP_P0.50mm_Horizontal',
          {'1': 'FL_C_A', '2': 'FL_C_K', '5': 'FL_W_A', '6': 'FL_W_K', 'MP': 'GND'},
          fields=fields('C224194', 'FH34SRJ-6S-0.5SH(50)', 'Hirose', Description='front light: 1 cool +, 2 cool -, 5 warm +, 6 warm -'))
    s.add('L1', 'Device', 'L', '47uH', 'Inductor_SMD:L_Taiyo-Yuden_NR-30xx', {'1': '+3V3', '2': 'EPD_SW'},
          fields=fields('C83435', 'SWPA3015S470MT', 'Sunlord', Description='47 uH, 350 mA, 3 x 3 x 1.5 mm (the reference names NR3015)'))
    s.add('Q1', 'Transistor_FET', '2N7002', 'SI1308EDL', 'Package_TO_SOT_SMD:SOT-323_SC-70', {'1': 'GDR', '2': 'RESE', '3': 'EPD_SW'},
          fields=fields('C469327', 'SI1308EDL-T1-GE3', 'Vishay', Description='the reference circuit\'s transistor. CHECK pin order 1 G, 2 S, 3 D'))
    R(s, 'R1', '1M', 'GDR', 'GND')
    s.add('R2', 'Device', 'R', '2.2', 'Resistor_SMD:R_0603_1608Metric', {'1': 'RESE', '2': 'GND'},
          fields=fields('C22939', '0603WAF220KT5E', 'UNI-ROYAL', Description='current sense, 1 %'))
    for ref, an, ca in (('D1', 'PREVGL', 'EPD_CP'), ('D2', 'EPD_CP', 'GND'), ('D3', 'EPD_SW', 'PREVGH')):
        s.add(ref, 'Device', 'D_Schottky', 'MBR0530', 'Diode_SMD:D_SOD-123', {'1': ca, '2': an},
              fields=fields('C82046', 'MBR0530T1G', 'onsemi'))
    for ref, v, a, b in (('C2', '4.7u/25V', 'VSH2', 'GND'), ('C3', '4.7u/25V', 'EPD_SW', 'EPD_CP'), ('C4', '4.7u/25V', '+3V3', 'GND'),
                         ('C5', '4.7u/25V', 'PREVGH', 'GND'), ('C6', '1u', '+3V3', 'GND'), ('C7', '1u', 'EPD_VDD', 'GND'),
                         ('C9', '4.7u/25V', 'VSH1', 'GND'), ('C10', '4.7u/25V', 'VSL', 'GND'), ('C11', '4.7u/25V', 'PREVGL', 'GND'),
                         ('C12', '1u', 'VCOM', 'GND'), ('C13', '100n', '+3V3', 'GND')):
        C(s, ref, v, a, b)
    for i, net in enumerate(('PREVGH', 'PREVGL', 'VCOM', 'VSH1', 'VSL', '+3V3', 'GND')):
        TP(s, f'TP{i + 1}', net)
    return d


if __name__ == '__main__':
    d = build()
    for prob in d.check():
        print('CHECK:', prob)
    print('PWR_FLAG on', sorted(d.write(sys.argv[1])))
