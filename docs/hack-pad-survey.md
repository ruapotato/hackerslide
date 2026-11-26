# Hack pad: parts survey (2026-11-26) and a proposed starting point

For [decisions/0009](decisions/0009-hack-pad.md). Only parts in production with a listed price and visible stock
count as candidates. Stock was read on 2026-11-26 from the JLCPCB and LCSC parts interfaces and DigiKey pages;
Mouser could not be read. Figures marked *from memory* were not re-checked against a datasheet in this pass.
**Nothing here is designed yet, and David has not chosen among the options.**

## Brain

| Part | Core | RAM | Package | Stock, price | MicroPython | Note |
|---|---|---|---|---|---|---|
| **NXP i.MX RT1176** | Cortex-M7 at 1 GHz + Cortex-M4 at 400 MHz | 2 MB on chip; add 32 MB SDRAM ($5.35, 7,705 in stock) | 289-ball BGA, 0.8 mm | 516 at DigiKey, $26.83 | Official board (RT1170 EVK) | Fastest microcontroller found in stock. Two high-speed USB ports, MIPI-DSI, parallel capture. Needs external flash. 289 balls on a 4-layer board is tight: likely 6 layers |
| ST STM32N657 | Cortex-M55 at 800 MHz + neural unit | 4.2 MB on chip | 264-ball BGA, 0.8 mm | 2,441 at DigiKey, $24.07 | Official boards, OpenMV | No DSI. Needs external flash |
| ST STM32H7S7 / H7R7 | Cortex-M7 at 600 MHz | 620 KB | 144-ball BGA or 176-pin QFP | 1,240-1,662 at DigiKey, about $11 | none | Available in a leaded package |
| NXP i.MX RT1062 | Cortex-M7 at 600 MHz | 1 MB | 196-ball BGA | 1,269 at JLCPCB, $10.64 | Official (Teensy 4) | The Teensy 4 chip: large audio and radio code base |
| Espressif ESP32-P4 | two RISC-V cores at 400 MHz | 32 MB in the package | **chip: 0 in stock everywhere until about May 2027** | Only on Waveshare's module, $10.99, no stock count shown | Official since v1.27 | Most RAM for Python and the richest hobby-radio code, but one source and a preliminary datasheet |
| Espressif ESP32-S3 | two cores at 240 MHz | 8 MB with the module | module | 34,492 at JLCPCB, $5.30 | Mature | Wi-Fi and Bluetooth built in; the base of most open "hacking" firmware |
| Raspberry Pi RP2350B | two Cortex-M33 at 150 MHz | 520 KB | 80-pin QFN | 7,776 at JLCPCB, $1.28 | Mature | The cheap baseline |

## Radios in stock

| Job | Part | Covers | Stock, price |
|---|---|---|---|
| Sub-GHz remote-control bands | TI CC1101 | 300-348, 387-464, 779-928 MHz | 16,943, $1.96 |
| LoRa and long range, plus 2.4 GHz | Semtech LR1121 | 150-960 MHz, 1.9-2.1 GHz, 2.4 GHz | 3,439, $4.36 |
| NFC, 13.56 MHz | ST ST25R3916B (the Flipper's reader family) | read, write, emulate | 1,417, $5.94 |
| 125 kHz tags | discrete coil driver and comparator | | ordinary parts |
| Wi-Fi 6, Bluetooth LE, Zigbee/Thread | Espressif ESP32-C6 module | 2.4 GHz | 6,033, $3.99 |
| 2.4 GHz packet sniffing | Si24R1 (nRF24-compatible) | 2.4 GHz | 7,987, $0.87 |
| Infrared | receiver and LED | | cents |
| Shortwave, AM, FM broadcast | Skyworks Si4732 | 150 kHz-30 MHz, 64-108 MHz, receive | 226, $2.73 |
| Position | ATGM336H | GPS, BeiDou | 3,576, $2.54 |
| **Software-defined radio** | Microchip AT86RF215IQ with a small FPGA (Gowin GW1NZ-LV1, 637 in stock, $6.65) | 389-510, 779-1020, 2400-2483 MHz; 2.5 MHz wide; receive and transmit | 392-538 at DigiKey, $6.67 |

**What is not available:** the HackRF's chain (its MAX2837 has no stock anywhere); the PlutoSDR's AD9363 (61
pieces at $96, discontinued at DigiKey); every receive-only TV-tuner chip. So "1 MHz to 6 GHz" is out, and so is
anything 20 MHz wide. What a microcontroller can do with the AT86RF215: spectrum and waterfall, FM, AM and
single-sideband, pagers and similar narrow signals, capture and replay of a few hundred kilohertz.

## Displays in stock

| Panel | Size | Thickness | Behaviour | Price |
|---|---|---|---|---|
| Good Display GDEQ0426T82 e-paper | 4.26", 800 x 480 | 0.93 mm | Partial update 0.42 s, full 3.5 s; holds an image with no power | $22.99 (Waveshare) |
| The 4.0" panel already in the design | 480 x 800 | 4.25 mm | Fast, backlit; the RT1176 can drive it | $77 |
| Sharp memory LCD LS032B7DD02 | 3.16", 336 x 536 | not read | Fast, reflective, microwatts | $39.14, 218 at DigiKey |

The 4.4" Sharp panel is 75 mm tall and does not fit a 74 mm body.

**Chosen since (2026-11-27):** the same panel with touch and a front light, GDEY0426T82-FT01C, 1.98 mm, $33.68,
94 in stock at Good Display's store. See [decisions/0009](decisions/0009-hack-pad.md).

## A starting point to react to

- **Brain:** i.MX RT1176 with 32 MB SDRAM, and an ESP32-C6 module beside it for Wi-Fi, Bluetooth and Thread.
- **Radios:** every row of the table above.
- **Display:** the e-paper panel. It is what makes the device thin; it is poor for a moving waterfall.
- **Battery:** GlobTek BL1950P4071611S1PCPT, 1950 mAh, 4.5 mm, 3.9 A, 317 at DigiKey.
- **Arrangement:** everything in the keyboard half, a thin display half sliding over it.
- **Thickness, by arithmetic only:** keys 2.3 + board 1.0 + battery 4.8 + back cover 1.0, sliding gap 0.4, display
  half about 2.8: **about 12.3 mm**, if the headphone jack is replaced by a low-profile one (today's is 5.0 mm).
- **Parts for the brain, radios and display:** about $120-140 (estimate), against $161 for the Linux module and
  panel alone.
- **Firmware:** nothing to fork whole. MicroPython has an official RT1170 port; RadioLib covers the Semtech and TI
  radios; ST's NFC library and the Flipper's protocol tables are references. This is the largest piece of work.

## Transmitting, in the USA (facts, not legal advice; from memory)

A hobbyist may build up to five uncertified units for personal use (47 CFR 15.23) and must still stay inside the
emission limits. Unlicensed transmitting is allowed in specific bands only: 260-470 MHz for short control signals,
902-928 MHz, 2.4 GHz, 13.56 MHz, with limits on power. Wider transmitting needs an amateur licence, in amateur
bands only. The Flipper Zero is certified and limits its transmit frequencies by region; the firmware here should
do the same.

## Software-defined radio from JLCPCB's own stock (searched 2026-11-26)

David prefers every part to come from the assembler's shelf. The AT86RF215 chosen above has no stock there in any
version, and neither does any other wideband radio chip, TV-tuner chip or wideband demodulator. What can be built:

| Block | Parts (JLCPCB stock) | Covers | Width | Send | Cost |
|---|---|---|---|---|---|
| A. Semtech SX1255 | SX1255 (178), a 32 MHz reference | 400-510 MHz | up to 1 MHz | yes, about 3 mW | about $8 |
| C. Shortwave detector | Si5351A clock (7,031), bus switch 74CBTLV3253 (11,354), OPA1612 (18,292), PCM1808 converter (45,283) | 0.1-30 MHz, weaker to about 50 MHz | 96-160 kHz | not planned | $5-10 |
| B. Converter in front of the SX1255 (optional) | LMX2572 synthesizer (1,393), LTC5567 mixer (2,393), amplifier, switches, filters | about 300 MHz-4 GHz | up to 1 MHz | bench only | $60-70 |

The shortwave detector is the classic design used in several open ham radios; the T41 project runs one on the
same chip family as this board's brain. Block B is a frequency shifter: it moves a chosen slice of spectrum into
the SX1255's range.

Not possible from that shelf: more than 1 MHz at once; clean sending outside 400-510 MHz; anything above 4 GHz;
gap-free cover between about 50 and 300 MHz; image-free reception above about 1.9 GHz without more filters.
The whole plan rests on one listing of 178 SX1255s.
