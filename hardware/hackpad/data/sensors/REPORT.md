# Hack pad sensor set: datasheet extraction report (2026-11-26)

Per-part details are in the JSON files beside this report. Stock and price were read from JLCPCB's parts API on 2026-11-26.
Page numbers refer to the maker's data sheet (or the named application note) as downloaded to `../src/`.
Anything marked [mem] comes from memory, not from a document read in these sessions. Nothing here has been reviewed by a person.

## Status of each part

The first worker wrote 23 files. Each one has every required field. This session added the last 5 (AD8232, BGT60LTR11AIP,
BME690, MiCS-5524, VL53L5CX) and this report.

| Part | Order code | LCSC | Stock | Unit $ | Height mm | File |
|---|---|---|---|---|---|---|
| Sensirion STCC4 (hosts the SHT40) | STCC4-D-R3 | C49191471 | 2,573 | 11.32 | 1.17 | stcc4.json |
| Sensirion SHT40 (on the STCC4's own controller pins, 0x44 only) | SHT40-AD1B-R2 | C2909890 | 11,973 | 1.31 | 0.54 | sht40.json |
| Sensirion SGP41 | SGP41-D-R4 | C3659325 | 2,144 | 9.02 | 0.85 | sgp41.json |
| Bosch BMP581 | BMP581 | C5362283 | 16,653 | 2.21 | 0.75 | bmp581.json |
| TDK T5837 x2 | MMICT5837-00-012 | C6909259 | 7,158 | 2.10 | 0.98 | t5837.json |
| ams AS7341 | AS7341-DLGM | C2649486 | 5,012 | 7.52 | 1.0 | as7341.json |
| TI OPT4001 | OPT4001DNPRQ1 | C20199903 | 2,660 | 2.04 | 0.65 | opt4001.json |
| ST VL53L1X | VL53L1CXV0FY/1 | C190004 | 12,307 | 4.95 | 1.56 | vl53l1x.json |
| Melexis MLX90632 | MLX90632SLD-DCB-000-RE | C7541116 | 2,345 | 7.24 | 0.95 | mlx90632.json |
| ST LSM6DSV16X | LSM6DSV16XTR | C5267406 | 17,679 | 2.86 | 0.83 | lsm6dsv16x.json |
| MEMSIC MMC5983MA | MMC5983MA | C404329 | 2,462 | 1.98 | 1.0 | mmc5983ma.json |
| TI TMAG5273 | TMAG5273B2QDBVR | C41935525 | **411** | 1.38 | 1.45 | tmag5273.json |
| TI LMH2110 | LMH2110TMX/NOPB | C129356 | 2,974 | 1.50 | 0.6 | lmh2110.json |
| TI INA237 | INA237AIDGSR | C2864837 | 8,086 | 1.81 | 1.1 | ina237.json |
| onsemi FUSB302B | FUSB302BMPX | C132291 | 41,965 | 0.81 | 0.8 | fusb302b.json |
| TI SN74AXC8T245 | SN74AXC8T245PWR | C882718 | 6,877 | 1.27 | 1.2 | sn74axc8t245.json |
| TI TPD4E05U06 | TPD4E05U06DQAR | C138714 | 29,032 | 0.08 | 0.55 | tpd4e05u06.json |
| Microchip MCP4728 | MCP4728T-E/UN | C478093 | 13,555 | 2.63 | 1.1 | mcp4728.json |
| ADI MAX31856 | MAX31856MUD+T | C2653162 | 11,350 | 3.89 | 1.1 | max31856.json |
| TI TCAN3413 | TCAN3413DRBR | C22445415 | 10,464 | 1.57 | 1.0 | tcan3413.json |
| TI THVD1420 | THVD1420DRLR | C3235555 | 36,219 | 0.94 | 0.6 | thvd1420.json |
| 365 nm UV LED | Silverlight M3535N1UVS8U06-365nm | C2833503 | 1,153 | 1.13 | 2.85 | uv_led_365nm.json |
| Micro Crystal RV-3032-C7 | RV-3032-C7-32.768KHZ-2.5PPM-TA-QA | C5366550 | 2,926 | 3.65 | 0.8 | rv-3032-c7.json |
| Infineon BGT60LTR11AIP | BGT60LTR11AIPE6327XUMA2 | C3606906 | 4,325 | 8.69 | 0.56 | bgt60ltr11aip.json |
| ADI AD8232 | AD8232ACPZ-R7 | C43216 | 1,689 | 6.71 | 0.75 | ad8232.json |
| Bosch BME690 (chosen over BME688) | BME690 | C42431867 | 1,531 | 9.92 | 0.93 | bme690.json |
| SGX MiCS-5524 | MICS-5524 | C3659348 | 1,780 | 6.45 | 1.55 | mics5524.json |
| ST VL53L5CX | VL53L5CXV0GC/1 | C3178303 | 2,523 | 7.20 | 1.5 | vl53l5cx.json |

Nothing is below 300 in stock. The TMAG5273 B2 is the thinnest margin at 411. If it falls below 300, the next choices are the
TMAG5273A1 (0x35, x1 range, 3,159 in stock) or the C1 (0x78, 1,000 in stock). Either one also removes the cross-bus duplicate of 0x22.

### Spot check of two of the first worker's files

- **INA237** (checked against TI ZHCSNF5A). Pins 1-10 (A1, A0, ALERT, SDA, SCL, VS, GND, VBUS, IN-, IN+) match table 5-1 on p3 and
  the KiCad symbol `Sensor_Energy:INA237`, which extends INA226 with the same numbers. The address is 0x40 with A1 = A0 = GND (p17 table 7-2).
  The ranges are +-40.96 mV with 1.25 uV/LSB at ADCRANGE = 1 (p5, p22). Current is 640 uA typ / 750 uA max, and 2.8 / 5 uA in shutdown (p6).
  Common mode is -0.3 to 85 V and differential +-40 V (p3). **Result: correct.**
- **MCP4728** (checked against Microchip DS22187). Pins 1-10 match the p2 pinout and the KiCad symbol `Analog_DAC:MCP4728`.
  The address is 1100 A2 A1 A0 with factory bits 000, so 0x60 (p24, p30). Current is 800 / 1400 uA, 40 nA in power-down with the
  VDD reference and 45 uA with the internal reference (p3). **Result: correct.** One detail: those current rows are specified at VDD = 5.5 V,
  so at 3.3 V they slightly overstate the current.

## Shared I2C level shifter (one, in stock)

**TI PCA9306DCUR**: LCSC C33196, 6,314 in stock, $0.53, VSSOP-8 2.3 x 2 mm. KiCad symbol `Interface:PCA9306DC` with footprint
`Package_SO:VSSOP-8_2.3x2mm_P0.5mm`. Its pins (1 GND, 2 VREF1, 3 SCL1, 4 SDA1, 5 SDA2, 6 SCL2, 7 VREF2, 8 EN) were checked against
TI SCPS113L p3.

Wiring:
- VREF1 = +1V8. This rail must stay on in sleep, because the IMU wakes the brain.
- VREF2 and EN are joined and pulled to +3V3 through 200 k, with 100 pF to GND (p11).
- Side 2 (SCL2/SDA2) goes to I2C_S on the brain's side, using the existing I2C_S pull-ups.
- Side 1 gets one pair of pull-ups to +1V8 (2.2-4.7 k).

**Behind it (the 1.8 V segment of I2C_S):**
- **AS7341** (1.8 V only).
- **LSM6DSV16X**, so that its push-pull INT1 can go straight to the 1.8 V wake pad IMU_INT_N.
- **BME690**, which is optimised for 1.8 V.

These three still share I2C_S's address space, because the PCA9306 is a pass switch, not a mux. No other I2C part in the set needs 1.8 V.
The MLX90632 -000 variant, the VL53L1X in 2V8 mode and the VL53L5CX (1.8 V I2C thresholds) all sit on 3.3 V directly.

Other level translation that is not I2C:
- **T5837 PDM**: SN74AVC2T245RSWR (C128418, 159,343 in stock), already in t5837.json. Needed because NVCC_LPSR is 3.3 V.
- **BGT60 TDet/PDet**: SN74AXC2T45DCUR (C1858360, 11,950 in stock), from 1.5 V up to 3.3 V.

## (a) I2C address map

| Addr | I2C_S (sensors, LPI2C1, 3.3 V) | I2C_S 1.8 V segment | I2C_U (LPI2C3) | I2C_P (LPI2C5) |
|---|---|---|---|---|
| 0x10 | | | ES8316 | |
| 0x20 | **proposed 3rd TCA6416A (IOX_C)** | | | TCA6416A IOX_A |
| 0x21 | | | | TCA6416A IOX_B |
| 0x22 | TMAG5273 B2 | | | FUSB302B |
| 0x29 | VL53L1X **and** VL53L5CX (power-up default) | | | |
| 0x2B | VL53L5CX after moving it | | | |
| 0x30 | MMC5983MA | | | |
| 0x34 | | | TCA8418 | |
| 0x36 | | | LM3630A | MAX17048 |
| 0x38 | | | FT6336U | |
| 0x39 | | AS7341 | | |
| 0x3A | MLX90632 | | | |
| 0x40 | | | INA237 | |
| 0x45 | OPT4001 (ADDR = VDD) | | | |
| 0x46 | BMP581 (SDO = GND) | | | |
| 0x50 | | | ST25R3916B | |
| 0x51 | | | | RV-3032-C7 |
| 0x59 | SGP41 | | | |
| 0x60 | | | MCP4728 | |
| 0x64 | STCC4 (ADDR = GND) | | | |
| 0x6A | | LSM6DSV16X (SA0 = GND) | | BQ25895 |
| 0x76 | | BME690 (SDO = GND) | | |
| (0x44) | SHT40 sits on the STCC4's private controller bus, not on a brain bus | | | |

Conflicts:
1. **VL53L1X and VL53L5CX are both 0x29 on I2C_S. This is a real clash.** Neither has an address pin. To resolve it:
   - after TOF_PWR_EN goes high, hold TOF1_XSHUT low;
   - boot the VL53L5CX and set its address to 0x2B (the setting is volatile and is lost at every power cycle);
   - then release XSHUT.
   The alternative is to move the VL53L5CX to I2C_U at 0x29. Either way its roughly 84 KB firmware upload [mem] then crosses a 400 kHz bus.
2. Same address on different buses (no clash as planned, but they become clashes if anyone moves a part to another bus):
   - 0x22: TMAG5273 B2 on I2C_S and FUSB302B on I2C_P.
   - 0x36: LM3630A on I2C_U and MAX17048 on I2C_P.
   - 0x6A: LSM6DSV16X on I2C_S and BQ25895 on I2C_P.
3. Addresses chosen so as not to clash: OPT4001 at 0x45 and not 0x44, which keeps 0x44 free for a TMAG5273 D variant. The MCP4728 must not be
   reprogrammed to 0x64, the STCC4's address, if the two ever share a bus.
4. General call: the MCP4728 uses general-call commands, and the Sensirion parts answer general-call reset. Keep the DAC on I2C_U, away from them.
5. A third TCA6416A cannot go on I2C_P, because that part only offers 0x20/0x21 and both are taken. On I2C_S, 0x20 is free.

Proposed bus assignment:
- **I2C_S**: all the environmental, optical, motion and magnetic sensors in the table above, plus the 1.8 V segment, plus the optional IOX_C.
  Speed is limited to 400 kHz by the MMC5983MA.
- **I2C_U**: user-interface parts, plus INA237 and MCP4728 (bench instruments; their general calls stay off the sensor bus).
- **I2C_P**: power parts, FUSB302B, RV-3032 and the expanders. This bus works in low-power modes.

## (b) Interrupt, enable, reset and select lines

**Must reach the brain.** All of these are already in the pin plan:
- USBC_INT_N (SNVS_05) from FUSB302B. Open drain, pulled up to SNVS 1.8 V.
- RTC_INT_N (SNVS_06) from RV-3032. Open drain.
- IMU_INT_N (SNVS_07) from LSM6DSV16X INT1. 1.8 V only. Firmware sets it open-drain, active low.
- PDM_CLK and PDM_DATA (LPSR_00/01), through the SN74AVC2T245.
- AIN_RFPWR (LMH2110, through a 0.75 divider), AIN_ECG (AD8232, through a 0.5 divider), AIN_GAS (MiCS-5524 ratiometric from 1.8 V).
- BENCH0-7 through the SN74AXC8T245. The THVD1420 uses BENCH2 (D), BENCH3 (R) and BENCH4 (DE).
- CAN_TX and CAN_RX.
- RF_SCK, RF_MOSI and RF_MISO (LPSPI6), shared by the MAX31856.
- Optional: BGT60 IFQ to AIN_SPARE for raw Doppler.

**May sit on a port expander:**

| Kind | Lines | Count |
|---|---|---|
| Outputs, needed | RFDET_EN, TC_CS_N, GAS_HTR_EN, BENCH_DIR1, BENCH_DIR2, BENCH_OE_N, BENCH_VREF_EN, BENCH_VSEL0, BENCH_VSEL1, CAN_STB, CAN_TERM_EN, RS485_RE_N, UV_EN, TOF1_XSHUT, TOF_PWR_EN, TOF2_LPN, ECG_SDN, RADAR_EN, MIC_PWR_EN (new), BENCH_PWR_EN (new) | 20 |
| Inputs, needed | ECG_LOD_LA, ECG_LOD_RA, RADAR_TD_N (motion wake through IOX_INT_N), RADAR_PD | 4 |
| Optional | BARO_INT, INA_ALERT_N, TC_DRDY_N, TC_FAULT_N, DAC_LDAC_N, MAG_INT, ALS_INT, HALL_INT, TOF1_INT, TOF2_INT, ECG_ACDC | 11 |
| **Total** | **24 needed, 35 with all optional lines** | |

The existing expanders have **25 free bits**: IOX_A uses 7 of 16, IOX_B 0 of 16. The radio sheet has not claimed any of them yet.
**Conflict:** the sensors alone take 24 of the 25.

Proposal: add a third TCA6416ARTWR (C182336, 28,158 in stock) on I2C_S at 0x20, with its open-drain INT wired-OR onto IOX_INT_N.
That gives 41 free bits for sensors and radios together. The second-cheapest fix is to drop the optional lines and strap AC/DC.

**Strap or leave unconnected:**

| Part | Straps |
|---|---|
| STCC4 | ADDR to GND, VDDIO to +3V3 |
| SGP41 | pin 4 to GND |
| BMP581 | CSB to VDDIO, SDO to GND |
| T5837 | SELECT to GND / +1V8_MIC |
| AS7341 | LDR, GPIO and INT open (poll it) |
| OPT4001 | ADDR to VDD |
| VL53L1X | pin 8 open |
| VL53L5CX | I2C_RST 47k to GND, RSVD6 47k to IOVDD, RSVD to GND or open |
| MLX90632 | ADDR to GND |
| LSM6DSV16X | SA0 to GND, CS to VDDIO, INT2 open |
| MMC5983MA | CS to VDDIO |
| TMAG5273 | TEST to GND |
| INA237 | A0 and A1 to GND |
| MCP4728 | LDAC to GND, RDY open |
| MAX31856 | DNC open |
| RV-3032 | EVI 10k to GND |
| BME690 | CSB to VDDIO, SDO to GND |
| AD8232 | FR to +VS |
| BGT60 | QS1 open, QS2 22k/12k, QS3 22k/3.9k, QS4 open, PLL_Trig/SPICS/SPIRSTN 10k up, SPICLK/SPIDI 10k down, Vtune open |

## (c) Current: whole sensor set, typical values

**Asleep: about 100 uA with nothing switched.** The parts that matter:

| Part | Asleep (uA) |
|---|---|
| SGP41 idle | 34 (105 max) |
| T5837 pair, clock stopped | 18 |
| SN74AXC8T245 with VREF off | 12 |
| TCAN3413 standby | 10 |
| PCA9306 reference current | about 7 |
| MAX31856 | 5 |
| LMH2110 shutdown | 3.7 |
| INA237 shutdown | 2.8 |
| LSM6DSV16X power-down | 2.6 (more while armed for wake-on-motion) |

Everything else is below 2 uA each.

With +1V8_MIC and +3V3_BENCH switched off it falls to **about 63 uA**. If the SGP41 can be switched as well (see the next point),
it falls to **about 30 uA**. The VL53L5CX's LP idle alone would be 45-300 uA, so the time-of-flight rail must be switched.

**Everything on: about 175 mA from 3.3 V, plus up to 33 mA for the UV LED from VSYS.** The large loads:

| Part | Current |
|---|---|
| VL53L5CX ranging | 95 mA (peaks about 115) |
| MiCS-5524 heater | 32 mA |
| VL53L1X ranging | 16 mA (peak 40) |
| TCAN3413 recessive | 7 mA (42 dominant) |
| LMH2110 | 3.7 mA |
| BGT60 at 500 us PRT | 3.7 mA avg (128 mA pulses at 1.5 V) |
| BME690 gas scan | 3.1 mA (12-17 mA heater on) |
| SGP41 | 3 mA |

**Switched rails.** The proposed load switch is TPS22919DCKR (C2149796, 55,549 in stock, $0.13; 1.6-5.5 V, 1.5 A, 90 mohm,
8 uA on, 2 nA off; TI p3-5). One per rail:

| Rail | Feeds | Enable |
|---|---|---|
| +3V3_TOF | VL53L1X + VL53L5CX | TOF_PWR_EN |
| +3V3_HTR | MiCS-5524 heater | GAS_HTR_EN |
| +1V8_MIC | both T5837 | MIC_PWR_EN |
| +3V3_BENCH | SN74AXC8T245 VCCA, TCAN3413, THVD1420 | BENCH_PWR_EN |

- The radar needs no extra switch: the enable pin of its TLV75801PDBVR 1.5 V LDO (C2877852, 51,957 in stock) is the switch.
- The UV LED already has its own MOSFET.
- **Caution with switched rails on a live I2C bus.** An unpowered I2C part can clamp SDA/SCL through its protection diodes. No data sheet
  read here promises otherwise for the VL53L1X, VL53L5CX or SGP41.
  - Option 1: put the time-of-flight pair (and the SGP41, if it is switched) behind an enable-able buffer on its own segment,
    such as a TCA9517ADGKR (C201698, 16,648 in stock) [mem: that its pins are high-impedance when powered off; data sheet not read].
  - Option 2: leave those parts powered and use their own low-power states. That costs about 45-300 uA for the VL53L5CX and 34 uA for the SGP41.
  - The SGP41 file's suggestion to share a GAS_PWR_EN rail is withdrawn here: the SGP41 stays on +3V3_SENS unless option 1 is built.
- The MAX31856 must stay powered whenever LPSPI6 is active.

## Conflicts with the pin plan (summary)

1. **IMU_INT_N** is a 1.8 V open-drain wake pad, but LSM6DSV16X INT1 is push-pull at VDDIO. Fix: run the IMU at 1.8 V behind the
   PCA9306 and set it to open drain. This needs +1V8 to stay on in sleep.
2. **PDM_CLK/PDM_DATA** are on the LPSR bank at 3.3 V, but the T5837 is 1.8 V only. Fix: SN74AVC2T245 (separate DIR per bit).
3. **Expander bits**: 24 needed and 35 with options, against 25 free. Fix: a third TCA6416A on I2C_S at 0x20.
4. **No wake pad is left** for radar motion, CAN wake or the ECG. Radar wake has to go through the expander INT on IOX_INT_N.
   Wake-on-CAN (RXD low in standby) is not possible without a SNVS line.
5. **Two time-of-flight sensors at 0x29** on I2C_S. They must be started in order (XSHUT, then a soft address change).
6. **ECG electrodes cannot use the bench header.** Its eight lines go through a digital direction-controlled shifter. Use two (or three)
   case pads, or add three analogue header pins wired to the AD8232's protection resistors.
7. **MAX31856**: the pin plan names no SPI bus. It is proposed on LPSPI6 (3.3 V radio SPI), with the chip select on an expander.
8. **Analogue ranges against the 1.8 V reference.** LMH2110 reaches about 2.0-2.4 V (0.75 divider). AD8232 swings 0.1 V to VS-0.1 V
   (0.5 divider). MiCS-5524 is fed from the 1.8 V reference rail so it cannot exceed it. AIN_SPARE is free: proposed for the radar IF output.
9. **USB-C**: remove any external 5.1 k CC pull-downs on the existing receptacle. The FUSB302B supplies dead-battery Rd itself, and both together give 2.55 k.
10. **RV-3032 CLKOUT** is a 3.3 V push-pull output. It cannot drive the brain's 32 kHz input (VDD_LPSR_ANA level) without a divider; the planned crystal stays.
11. **THVD1420 sharing BENCH2/3/4**: RE needs its own expander line, otherwise the receiver fights the shifter on BENCH3.
    UART TX/RX must sit on opposite shifter direction groups (even and odd lines).

## Unread or weak sources

- **RV-3032-C7**: the data sheet would not download from JLCPCB or Micro Crystal. The application manual was read from web.archive.org's copy.
- **STCC4**: JLCPCB lists no data sheet. Sensirion's own D1 was read.
- **BGT60LTR11AIP**: Infineon's full data sheet v2.09 link failed. The short data sheet V2.6, AN625 and the autonomous reference-board guide were read.
  The footprint and radome figures are therefore not from a document.
- **MiCS-5524**: the data sheet has 5 pages. It gives no warm-up time and nothing on isolation between heater and sensor.
- **VL53L5CX**: its address change and firmware upload come from memory of ST's UM2884.
