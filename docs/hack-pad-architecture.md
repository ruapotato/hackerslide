# Hack pad: system plan (2026-11-27)

The parts and decisions so far, gathered into one list to draw the schematic from. Sources:
[decisions/0009](decisions/0009-hack-pad.md), [hack-pad-survey.md](hack-pad-survey.md),
[hack-pad-sensors.md](hack-pad-sensors.md). **This is a plan. No schematic exists yet, and pin assignments,
supply voltages and bus loading have not been checked against the datasheets.** Each "check" below is a job to do
before that block is drawn.

## Shape

One 6-layer board, about 125 x 69 mm, in the keyboard half: keys and D-pad on its top side, everything else
underneath. A thin display half slides over it and holds only the e-paper panel. A small moving cable joins
them. Target thickness about 13.3 mm (arithmetic, not a model).

## Blocks

| Block | Parts | Talks to the brain over | Notes and checks |
|---|---|---|---|
| Brain | NXP MIMXRT1172CVM8A (800 MHz + 400 MHz cores), 289-ball BGA | | Check from the datasheet that the 1172 has every interface used below |
| Memory | 2 x W9825G6KH (64 MB), as on NXP's evaluation board; positions for 128 MB | memory bus | Check the 128 MB wiring against the reference manual |
| Program storage | W25Q128JV flash | FlexSPI | Boot configuration pins as on the evaluation board |
| Card | microSD socket (as on the Linux carrier) | SD interface | |
| USB | USB-C: charging, and the brain's high-speed port | USB | Second high-speed port to an internal header |
| Display | Good Display GDEY0426T82-FT01C: e-paper, touch, front light | SPI (panel), I2C (touch FT6336U), one PWM (light) | Through the moving cable. Check the front light's supply in the specification |
| Keyboard | 40 keys + Esc, Tab + 5-switch D-pad, TCA8418 scanner | I2C | Carries over from the Linux design with the new layout |
| Audio | ES8316 codec, headphone jack (a low-profile one to be chosen) | I2S, I2C | Carries over |
| Microphones | 2 x TDK T5837 (sound, ultrasound to 50 kHz) | PDM | Two sound holes |
| Power | BQ25895 charger, MAX17048 gauge, TPS259531 battery fuse, 3.3 V and 1.8 V regulators for the brain | I2C | No 5 V boost any more. Battery: GlobTek 1950 mAh, 4.5 mm. Fuse setting to suit its 3.9 A rating |
| Wi-Fi, Bluetooth, Thread | ESP32-C6-MINI-1 module | SPI or SDIO, UART | Its own antenna on the module |
| Sub-GHz | TI CC1101 | SPI | 300-348, 387-464, 779-928 MHz |
| LoRa, 2.4 GHz | Semtech LR1121 | SPI | |
| NFC | ST ST25R3916B, loop antenna on the board | SPI | Antenna about 40 x 30 mm, clear of copper and the battery |
| 125 kHz tags | coil driver and comparator from ordinary parts | timer pins, ADC | |
| Infrared | receiver and LED | timer pins | Window |
| 2.4 GHz packets | Si24R1 | SPI | |
| Position | ATGM336H | UART | |
| Broadcast receiver | Skyworks Si4732 | I2C, I2S | Long, medium, short wave and FM |
| **SDR A** | Semtech SX1255, 32 MHz reference | I2S (samples), SPI | 400-510 MHz, 1 MHz wide, receive and send |
| **SDR C** | Si5351A, 74CBTLV3253, OPA1612, PCM1808 | I2S, I2C | 0.1-30 MHz receive |
| **SDR B** | LMX2572 synthesizer, LTC5567 and ADEX-10L mixers, amplifier, SKY13414 and BGS12 switches, filter bank | SPI, control pins | Shifts 10 MHz-4 GHz into SDR A's range. Fitted (David left this to stock: every part is stocked). Drawn so that it can be left off the board without affecting A |
| Sensors, core set | STCC4 + SHT40, SGP41, BMP581, AS7341, OPT4001, VL53L1X, MLX90632, LSM6DSV16X, MMC5983MA, TMAG5273, LMH2110, RV-3032 clock | I2C (two buses), ADC | One switched supply for the power-hungry ones |
| Sensors, added | BGT60LTR11AIP radar, AD8232 heart trace, BME690, MiCS-5524, VL53L5CX | SPI, I2C, ADC | All stocked at JLCPCB |
| Bench tools | INA237 power monitor, FUSB302B USB-C sniffer, 8-bit protected probe port (SN74AXC8T245), MCP4728 outputs, MAX31856 thermocouple, CAN and RS-485 drivers | I2C, SPI, pins | On an expansion header along one edge |
| Lamp | 365 nm UV LED | pin | |

## Antennas

Sub-GHz and the SDR want a connector for an external antenna; everything else uses chip or board antennas. One
small coaxial connector with a switch between CC1101, LR1121 and the SDR is the plan. Check: isolation between
transmitting radios and the SDR's input.

## Openings in the case

One gas vent, two sound holes, one window strip (light, colour, distance, infrared), one hole for the distance
thermometer, one for the lamp, one antenna connector, USB-C, headphone jack, card slot, and the expansion header.

## Known hard parts

1. The 289-ball brain with its memory bus: six layers, and the first block to lay out.
2. Radio layout: five transmitters and two sensitive receivers on one board.
3. The moving cable now carries the display's signals.
4. Sleep current with this many parts: every block needs a way to be switched off.
5. Firmware: every part above needs a driver in HackOS.
