# Hack pad: sensor survey (2026-11-26/27)

For the "tricorder" scope in [decisions/0009](decisions/0009-hack-pad.md). Candidates are in production with a
listed price and visible stock; stock was read live from JLCPCB's parts library unless a line says otherwise.
Heights and ranges are from datasheets except where marked *unconfirmed*. The board cavity is about 4.8 mm high.
**Nothing is chosen or drawn yet.**

## What shapes the design

- **CO2 fits.** Sensirion's STCC4 is about 1.2 mm high and in stock. The better-known SCD40/41 are 6.5 mm.
- **Sound above hearing needs its own path.** The audio chip already in the design stops at 96 kHz sampling.
  A TDK T5837 microphone covers ordinary sound and ultrasound to about 50 kHz when clocked faster; 80 kHz needs a
  different microphone (only 217 in stock) and a faster converter.
- **Sound below hearing comes from the pressure sensor.** Bosch's BMP581 resolves 0.08-0.78 Pa depending on rate:
  enough for doors, wind, ventilation and storms, not faint signals.
- **No stocked chip for:** UV index, pulse oximetry, lightning detection, a thin thermal camera, a camera in
  JLCPCB's library, a Geiger-type radiation sensor.

## Core set: on the board by default

| Measures | Part | Height | Price | Stock | Needs in the case |
|---|---|---|---|---|---|
| CO2 | Sensirion STCC4 | 1.2 mm *unconfirmed* | $11.32 | 2,573 | vent |
| Temperature, humidity | Sensirion SHT40 | 0.5 mm *unconfirmed* | $1.31 | 11,975 | same vent |
| Volatile gases and NOx index | Sensirion SGP41 | 0.85 mm | $9.02 | 2,144 | same vent |
| Pressure, altitude, infrasound | Bosch BMP581 | 0.8 mm | $2.21 | 16,658 | same vent |
| Sound and ultrasound to 50 kHz, stereo | 2 x TDK T5837 | 0.98 mm | $4.20 | 7,158 | two small sound holes |
| Colour spectrum (8 bands + near infrared), light flicker | ams AS7341 | 1.0 mm | $7.52 | 5,012 | clear window |
| Brightness | TI OPT4001 | not read | $2.04 | 2,665 | same window |
| Laser distance to 4 m | ST VL53L1X | 1.56 mm | $4.95 | 12,307 | infrared-clear window |
| Temperature at a distance | Melexis MLX90632 | 1.0 mm | $7.24 | 2,345 | open hole or far-infrared window |
| Motion, tilt, electrostatic field | ST LSM6DSV16X | 0.83 mm | $2.86 | 17,744 | none |
| Compass, magnetic field | MEMSIC MMC5983MA | 1.0 mm | $1.98 | 2,472 | none |
| Strong magnets | TI TMAG5273 | SOT-23 | $1.38 | 411 | none |
| Radio field strength, 50 MHz-8 GHz | TI LMH2110 | under 1 mm *unconfirmed* | $1.50 | 2,974 | none |
| Voltage, current, power on a probe | TI INA237 | about 1.1 mm *unconfirmed* | $1.81 | 8,090 | probe contacts |
| USB-C power negotiation sniffer | onsemi FUSB302B | about 0.8 mm *unconfirmed* | $0.81 | 41,965 | none |
| Logic probe port with protection | SN74AXC8T245 + TPD4E05U06 | 1.2 mm | $1.44 | 6,877 | header |
| Analogue outputs, 4 channels | Microchip MCP4728 | 1.1 mm | $2.63 | 13,555 | header |
| Thermocouple probe | Maxim MAX31856 | 1.2 mm | $3.89 | 11,350 | probe contacts |
| CAN bus | TI TCAN3413 | about 1 mm | $1.57 | 10,464 | header |
| RS-485 | TI THVD1420 | 0.6 mm | $0.94 | 36,219 | header |
| Ultraviolet lamp, 365 nm | Silverlight 3535 LED | not read | $1.13 | 1,153 | hole |
| Clock | Micro Crystal RV-3032-C7 | 0.8 mm *unconfirmed* | $3.65 | 2,926 | none |

About $75 of parts and roughly 7-9 cm2 of board (estimate). Six openings in the case: one gas vent, two sound
holes, one window strip, one hole for the thermometer, one for the lamp. Asleep, all of it together draws a few
tens of microamps if the gas sensor and rangefinder are switched off.

## Extended set: optional positions or an expansion connector

| Measures | Part | Why not core | Price, stock |
|---|---|---|---|
| CO2, more accurate | Sensirion SCD41 | 6.5 mm: outside the case only | $19.44, 373 |
| Fine dust | Bosch BMV080 | 3.0 mm; $42.54 at DigiKey, stock not shown | |
| Ultrasound to 80 kHz | ST IMP23ABSU + TI TLV320ADC5140 | thin stock on the microphone | $10.44, 217 / 2,115 |
| Ground vibration, seismometer grade | ADI ADXL355 | price | $56.13, 858 |
| Motion through plastic (60 GHz radar) | Infineon BGT60LTR11AIP | firmware effort | $8.69, 4,325 |
| Breathing and heartbeat at a distance (radar) | Infineon BGT60TR13C | thin stock, firmware effort | $18.98, 188 |
| Thermal camera, 32 x 24 | Melexis MLX90640 | an 11 mm can: outside only | $22.89, 225 |
| Gamma radiation | onsemi MICROFC-60035 with a scintillator crystal | crystal source not found; needs a 28 V supply | $23.73, 1,378 |
| Heart trace (ECG) | ADI AD8232 | needs contact pads | $6.71, 1,689 |
| Reducing gases (CO, alcohol, hydrogen), not selective | SGX MiCS-5524 | 76 mW heater | $6.45, 1,780 |
| Distance in 8 x 8 zones | ST VL53L8CX | | $10.24, 467 |
| Weight, capacitance, impedance | NAU7802, FDC1004, AD5934 | need external probes | $1.88-13.44 |

## Not realistic here, one reason each

Thermal imaging inside the case (too tall); Geiger tube (size and 300 V); pulse oximeter (5 pieces in stock);
UV index (out of stock until January 2027); lightning detector (not in JLCPCB's library); mini spectrometer
($300 and tall); laser-scatter dust sensors (12 mm thick); gas-by-gas sensing (9 pieces of the only small part).
