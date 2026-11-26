# Power, reset and clocks — i.MX RT1172 (289 MAPBGA)

Document keys used below:
* **DS-B** = IMXRT1170BIEC Rev. 1, 05/2025 (industrial, B silicon). **DS-A** = IMXRT1170IEC Rev. 5, 01/2024. Sections 4.1.3-4.2.6 were
  diffed between the two: Tables 11, 12, 22, 28, 29, section 4.2.1 and Table 4 are the same except where noted.
* **HDUG** = MIMXRT1170HDUG Rev. 2, 09/2021 (community copy; a later revision exists but was not obtained — see README).
* **SCH** = MIMXRT1170-EVKB schematic SPF-55139 C1 (27 Oct 2022); values read from 400-500 dpi PNG crops in `png/sch/`.
* **AN14716** Rev 3.0, **ERRATA-A** = IMXRT1170ACE Rev 1.6.

## 1. Supply balls, voltage, maximum current

Voltage: DS-B Table 11 (p.28-29). Maximum current: DS-B Table 12 (p.30). Balls: DS-B Table 115 (p.116-117). Internal LDO data: Tables 17-21.

| Rail | Balls | Voltage (min-max) | Max current | Kind | EVKB connection (SCH sheet) |
|---|---|---|---|---|---|
| DCDC_IN | M5, N5 | 3.0-3.6 V | 1000 mA | input | VDD_3V3 through J19 (R194 5 mohm shunt DNP) (6) |
| DCDC_IN_Q | L5 | not listed separately in Table 11 | — | input | shorted to DCDC_IN (6) |
| DCDC_LP / DCDC_LN | T3,U3 / T4,U4 | switch nodes | — | inductor | L15 4.7 uH between LP and LN (6) |
| DCDC_DIG | K8, K9, L8 | DCDC 1.0 V output, 0.6-1.375 V, 25 mV steps; load typ 150 / max 850 mA (Table 22) | 850 mA | output | to VDD_SOC_IN via R1853 0R + J14 (6) |
| DCDC_DIG_SENSE | L7 | sense | — | input | VDD_SOC_IN via R2106 0R (6) |
| DCDC_ANA | M7, M8 | DCDC 1.8 V output, 1.5-2.275 V; load typ 80 / max 150 mA (Table 22) | 150 mA | output | net DCDC_1V8_OUT via R1851 0R + J23 (6) |
| DCDC_ANA_SENSE | M6 | sense | — | input | DCDC_1V8_OUT via R2134 0R (6) |
| DCDC_GND | K6, K7, L6 | 0 V | — | ground | GND |
| DCDC_PSWITCH | P3 | DCDC_IN domain; must be < 0.5 V before power-up, rise >= 1 ms after DCDC_IN | — | control | R396 30k from MCU_DCDC_IN, C286 0.22 uF to GND (6) |
| DCDC_MODE | N4 | strap | — | control | R398 4.7k to GND (R397 4.7k pull-up DNP), C287 0.1 uF (6) |
| VDD_SOC_IN | H8,H9,H10,J8,J9,J10,K10 | 1.1-1.15 V (M7 800 MHz), 1.0-1.15 V (600 MHz), 0.9-1.15 V (240 MHz), 0.8-1.15 V standby; abs max 1.2 V | 850 mA | input | from DCDC_DIG (6) |
| VDD_LPSR_IN | R12 | 3.0-3.6 V | 75 mA | input | VDD_3V3 via R222 0R, J49 (6) |
| VDD_LPSR_ANA | P12 | 1.8 V internal LDO output (Table 21: 75 mA, cap 4.7 uF) | — | cap only | C290 4.7 uF (6) |
| VDD_LPSR_DIG | P11 | internal LDO output 0.7-1.15 V (Table 20: 50 mA, cap 2.2 uF) | — | cap only | C296 2.2 uF (6) |
| VDD_SNVS_IN | U12 | 2.4-3.6 V | 1 mA | input | VLDO_3V3 (always on) via D9 RB521S30; coin cell option via D10 (6) |
| VDD_SNVS_ANA | U14 | internal LDO output 1.65-1.95 V (Table 17: 1 mA, cap 2.2 uF) | — | cap only | C293 2.2 uF; also feeds NVCC_SNVS (6) |
| VDD_SNVS_DIG | T14 | internal LDO output 0.81-0.95 V (Table 18: cap 0.22 uF) | — | cap only | C107 0.22 uF (6) |
| NVCC_SNVS | U11 | 1.65-1.95 V only | formula | input | tied to VDD_SNVS_ANA, C305 0.1 uF (6) |
| VDDA_1P8_IN | M11 | 1.71-1.89 V | 100 mA | input | net ADC_1V8_IN: VDD_1V8 (LDO) by default through J56 1-2 + L27 bead; DCDC_1V8_OUT on J56 2-3 (6) |
| VDDA_1P0 | N11 | internal LDO_PLL output 0.9-1.2 V (Table 19: 70 mA, cap 2.2 uF) | — | cap only | C276 2.2 uF; feeds VDD_MIPI_1P0 via R1848 0R (6, 8) |
| VDDA_ADC_1P8 | K15 | 1.65-1.95 V | 10 mA | input | ADC_1V8_IN, C117 1 uF (6) |
| VDDA_ADC_3P3 | J13 | 3.0-3.6 V | 2 mA (row shared with ADC_VREFH) | input | VDD_3V3 via L28 bead, C257 1 uF, C245 0.1 uF (6) |
| ADC_VREFH | G16 | 1.0-1.89 V | (see above) | input | VDD_VREFH = VDD_1V8 via J116, C347 2.2 uF (6) |
| VDD_USB_1P8 | H12 | 1.65-1.95 V | 50 mA | input | VDD_1V8 via L30 bead (L29 from DCDC_1V8_OUT DNP), C270 1 uF (8) |
| VDD_USB_3P3 | G12 | 3.0-3.6 V | 60 mA | input | VDD_3V3 via L31 bead, C244 1 uF (8) |
| USB1_VBUS / USB2_VBUS | D17 / D16 | 2.4-5.5 V (abs max 5.6 V) | — | sense input | directly 5V_USB_OTG1 / OTG2, 1 uF each (C252, C251) (8) |
| VDD_MIPI_1P8 | F9 | 1.65-1.95 V | 4 mA | input | VDD_1V8 via L32 bead (L33 DNP), C119 1 uF (8). Unused: 10k to GND (Table 6) |
| VDD_MIPI_1P0 | F10 | 0.9-1.1 V | 30 mA | input | VDDA_1P0 via R1848 0R, C272 1 uF (8). Unused: 10k to GND (Table 6) |
| NVCC_EMC1 | F6, F7, G6 | 3.0-3.6 or 1.65-1.95 V | Imax = N x C x V x 0.5F | input | VDD_3V3; C235 4.7 uF, C239 2.2 uF (8) |
| NVCC_EMC2 | H6, J6 | 3.0-3.6 or 1.65-1.95 V | formula | input | VDD_3V3; C241 4.7 uF, C265 2.2 uF (8) |
| NVCC_GPIO (GPIO_AD bank) | M12 | 3.0-3.6 or 1.65-1.98 V (DS-B; DS-A 1.95) | formula | input | VDD_3V3; C345 4.7 uF, C258 2.2 uF (7) |
| NVCC_LPSR | P7 | 3.0-3.6 or 1.65-1.98 V | formula | input | VDD_3V3; C256 2.2 uF (7) |
| NVCC_DISP1 | D12 | 3.0-3.6 or 1.65-1.95 V | formula | input | VDD_1V8; C285 2.2 uF (7) |
| NVCC_DISP2 | E7 | 3.0-3.6 or 1.65-1.98 V | formula | input | VDD_3V3; C327 2.2 uF (7) |
| NVCC_SD1 | D14 | 3.0-3.6 or 1.65-1.95 V | formula | input | NVCC_SD (3.3 V default, 1.8 V selected by SD1_VSELECT through analog switch U311 NX3L1G53GT) via R375 0R; C242 2.2 uF (5, 7) |
| NVCC_SD2 | G13 | 3.0-3.6 or 1.65-1.95 V | formula | input | FLASH_VCC = 1.8 V default (L1 bead from VDD_1V8; R16 0R to VDD_3V3 DNP); C254 2.2 uF (5, 7) |
| VSS | 34 balls (see ballmap.csv) | 0 V | — | ground | GND |

The NVCC formula row: N = number of IO pins on the rail, C = load capacitance, V = IO voltage, F = clock rate (DS-A Table 12; in DS-B the
formula text did not come out of the text layer — not re-checked by rendering).

Absolute maximum (DS-B Table 8): 3.3 V rails 3.96 V, 1.8 V rails 1.98 V, VDD_SOC_IN 1.2 V (overshoot within 1.4 V / 20 ms per AN14716 App. A),
VBUS 5.6 V, any pad -0.5 V to NVCC+0.3 V (no 5 V-tolerant pads).

## 2. Which rails may share one 3.3 V supply

* Data sheet rule (DS 4.2.1.1): VDD_SNVS_IN must come up first **or be shorted with VDD_LPSR_IN and DCDC_IN**. So VDD_SNVS_IN, VDD_LPSR_IN,
  DCDC_IN (+DCDC_IN_Q) may be one 3.3 V net. VDD_USB_3P3, VDDA_ADC_3P3 and the 3.3 V NVCC rails hang off the same 3.3 V (EVKB does this,
  with 120 ohm beads on USB_3P3 and ADC_3P3).
* 1.8 V is still needed for: VDDA_1P8_IN (100 mA max), VDD_USB_1P8 (50 mA), VDDA_ADC_1P8 (10 mA), VDD_MIPI_1P8 (4 mA, if MIPI used) and
  ADC_VREFH. NVCC_SNVS takes its 1.8 V from VDD_SNVS_ANA.
* **The EVKB is not a 3.3 V-only design by default.** It has an external AMS1117-1.8 LDO (U1, VDD_3V3 -> VDD_1V8) that feeds all the 1.8 V
  inputs above plus NVCC_DISP1 and the flash. The chip's own DCDC_ANA 1.8 V output (net DCDC_1V8_OUT) is wired only as an alternative:
  J56 position 2-3 for VDDA_1P8_IN/VDDA_ADC_1P8, and DNP beads L29 (USB_1P8) and L33 (MIPI_1P8). (The EVKB hardware guide's "OPT1. Internal DCDC POWER
  (default) / OPT2. External PMIC" refers to the core supply, not to this 1.8 V choice.)
* Using DCDC_ANA as the only 1.8 V source is therefore a supported option, with two limits from DS Table 22 / section 4.2.4: it may power
  **on-chip loads only** (no external flash, level shifters or SDRAM from it), and the load must stay under 150 mA — the Table 12 maxima of
  the four 1.8 V inputs add up to 164 mA, so the data sheet asks to "add currents for active modules per use case" (the sum is COMPUTED here).
* A-silicon caveat (ERRATA-A ERR052351): NVCC_GPIO, NVCC_LPSR and NVCC_DISP2 above 1.98 V degrade the output drivers over time; NXP's
  workaround is 1.8 V on those three rails. Fixed on B silicon (AN14716). See rt1172_vs_rt1176.md section 4.
* Do not leave NVCC_GPIO / NVCC_LPSR / NVCC_DISP2 unpowered: about 500 uA leakage per bank from VDDA_1P8_IN (AN14716 App. A item 11).

## 3. How the EVKB powers the chip (SCH sheets 3, 5, 6)

1. 5 V input -> 5V_SYS. U33 UM1750S-00 LDO (R269 464k / R268 200k, Vfb 1 V) makes VLDO_3V3, always on -> VDD_SNVS_3V3 -> D9 -> VDD_SNVS_IN.
2. The chip's SNVS domain starts and drives PMIC_ON_REQ (U9) high. PMIC_ON_REQ -> J71 -> R266 10k / C168 0.22 uF -> EN of U39 MP2143DJ buck
   (L22 1 uH, R280 180k / R279 40.2k, Vfb 0.6 V; "Current 3A") -> DCDC_3V3 -> J41 -> VDD_3V3.
3. VDD_3V3 feeds DCDC_IN (J19), VDD_LPSR_IN (R222), the 3.3 V NVCC rails, USB_3P3, ADC_3P3, and U1 AMS1117-1.8 -> VDD_1V8.
4. DCDC_PSWITCH rises through R396 30k / C286 0.22 uF (6.6 ms time constant, COMPUTED; DS asks for a total RC delay of 5-40 ms and at
   least 1 ms from DCDC_IN at 3.0 V to PSWITCH at 0.5 x DCDC_IN). The internal DCDC then makes DCDC_DIG (-> VDD_SOC_IN) and DCDC_ANA.
5. Reset: U35 UM805RE supervisor (VCC = VLDO_3V3) has its manual-reset input driven through diodes D12/D11 by POR_BUTTON and WDOG_B, and its
   RESET output pulls the buck's EN low — the EVKB resets by power-cycling VDD_3V3. POR_B itself (T10) has only C115 0.1 uF to GND and a DNP
   100k pull-up R215 to VDD_SNVS_ANA; it is driven open-drain (74LVC07 U361 at VDD_1V8, R2090 100k pull-up to VDD_1V8) from the debug probe
   reset, SW9 and optionally U356 UM803RS (R1900 DNP) (sheet 27). The JTAG header nSRST reaches POR_B through Schottky D2.

## 4. Internal DCDC external parts

| Item | Data sheet (DS Table 22, p.41-42) | HDUG Rev 2 section 3.1 | EVKB (SCH sheet 6) |
|---|---|---|---|
| Inductor | 4.7 uH typ, saturation current 1 A typ | about 4.7 uH, saturation > 1.5 A, ESR < 0.1 ohm | L15 4.7 uH, "ISAT=1.9A, RDC=91mohm" |
| DCDC_DIG capacitance | 66 uF typ (plus HF caps per HDUG) | "about 66 uF, includes all capacitors on DCDC_DIG_X and VDD_SOC_IN" | DCDC_DIG: 2.2 + 10 + 22 + 0.1 uF; VDD_SOC_IN: 22 + 4.7 + 0.1 + 1 + 1 + 4.7 + 4.7 uF (total about 72.6 uF nominal, COMPUTED) |
| DCDC_ANA capacitance | 33 uF typ | 2.2 uF only in Table 1 | 2.2 + 10 + 22 + 0.1 uF (34.3 uF nominal, COMPUTED) |
| DCDC_IN | — | 0.1 + 4.7 + 22 uF | C102 0.1, C277 4.7, C294 22 uF |
| Switching frequency | — | about 1.5 MHz | — |
| Over-current detect | 1.5 A typ (register selectable 1.5 / 2 A) | — | — |
| Low DCDC_IN detect | 2.6 V typ, 2.8 V max | reset IC threshold must be above 2.6 V | — |

Source disagreement: inductor saturation current is "1 A typ" in the data sheet and "> 1.5 A" in the HDUG; the EVKB part is 1.9 A.
DCDC_ANA output capacitance is 33 uF in the data sheet and on the EVKB but only 2.2 uF in HDUG Table 1.
Bypassing the DCDC (not this design): DCDC_PSWITCH and DCDC_MODE to GND, other DCDC balls unconnected (DS Table 6).

## 5. Power-up / power-down sequence and reset pins

DS section 4.2.1 (p.37-39), Figure 4 order: VDD_SNVS_IN -> (VDD_SNVS_ANA, VDD_SNVS_DIG internal) -> VDD_LPSR_IN -> (VDD_LPSR_ANA,
VDD_LPSR_DIG internal) -> DCDC_IN -> 1 ms -> DCDC_PSWITCH -> VDDA_1P8 -> VDD_SOC_IN -> ONOFF.

* VDD_SNVS_IN first, or shorted with VDD_LPSR_IN and DCDC_IN. A coin cell on SNVS must be connected before other supplies.
* RC delay DCDC_IN -> DCDC_PSWITCH: total 5-40 ms; DCDC_IN must reach 3.0 V within 0.3 x RC; at least 1 ms from DCDC_IN stable to PSWITCH at
  0.5 x DCDC_IN; PSWITCH below 0.5 V before ramp.
* Slew rate of other domains 360 V/s to 36 kV/s. VDD_LPSR_DIG before VDD_SOC_IN (up), VDD_SOC_IN down no later than VDD_LPSR_DIG.
* No back-feed from 1.8 V parts into the 3.3 V supply. USB VBUS and VDDA_ADC_3P3 are outside the sequence.
* Do not drive an IO whose NVCC rail is off (4.2.1.3).
* **POR_B** (T10): internal 100k pull-up to the SNVS domain; an external pull-up may only go to VDD_SNVS_ANA; must be held low until the last
  rail is valid if it is used to release the MCU; otherwise the internal POR (threshold 0.75 V on VDD_SOC_IN / VDD_LPSR_DIG, Table 16) takes
  over. NXP recommends an external reset IC with threshold above 2.6 V (DS Table 4; HDUG Table 10).
* **ONOFF** (U10): on-chip pull-up and debounce; short press to GND = on / interrupt, about 5 s = forced off; may be left open; a 4.7k-10k
  series resistor is allowed (HDUG Table 10). EVKB: button SW6 to GND, C207 0.1 uF, pull-up R325 100k DNP.
* **PMIC_ON_REQ** (U9): push-pull output from the SNVS domain, high by default ("Output high", DS Table 116); EVKB uses it as the buck enable.
* **PMIC_STBY_REQ** (T9): output, low by default; EVKB routes it only to the optional PMIC.
* **WAKEUP** (T8): SNVS GPIO with pull-up; EVKB user button SW7 to GND, C208 0.1 uF.
* **TEST_MODE** (T11): tie to GND (DS Table 4; EVKB ties it directly to GND).
* SNVS-domain pads are 1.8 V and weak; GPIO_SNVS_xx switch to tamper function in SNVS mode even on non-tamper parts (HDUG Table 3, ERR051122).

## 6. Decoupling per rail (HDUG Rev 2 Table 1, "on-chip DCDC regulators are used", p.2-3)

Checked against rendered pages `png/HDUG_rev2_p-02.png`, `-03.png`. 0402 X5R; 22 uF is 0603 X5R.

| Rail | 0.1 uF | 0.22 uF | 1 uF | 2.2 uF | 4.7 uF | 22 uF | Placement note |
|---|---|---|---|---|---|---|---|
| DCDC_IN | 1 | | | | 1 | 1 | 0402 under M5, N5; 0603 close |
| DCDC_ANA | | | | 1 | | | under M7 |
| DCDC_ANA_SENSE | 1 | | | | | | under M6 |
| DCDC_DIG | | | | 1 | | 1 | 0402 under K8 |
| DCDC_DIG_SENSE | 1 | | | | | | under L7 |
| VDDA_1P8_IN | 1 | | | | | | under M11 (a later HDUG revision reportedly changes this to 1 uF — see README) |
| VDD_SOC_IN | 1 | | 2 | | 2 | 1 | 0402 under H8, H10, J8, J10, K10 |
| VDD_LPSR_IN | | | | | 1 | | under R12 |
| VDD_LPSR_ANA | | | | | 1 | | under P12 |
| VDD_LPSR_DIG | | | | 1 | | | under P11 |
| VDD_SNVS_IN | | | 1 | | | | under U12 |
| VDD_SNVS_ANA | | | | 1 | | | under U14 |
| VDD_SNVS_DIG | | 1 | | | | | under T14 |
| VDD_USB_1P8 | | | 1 | | | | under H12; 120 ohm @100 MHz bead from 1V8 |
| VDD_USB_3P3 | | | 1 | | | | under G12; 120 ohm bead from 3V3 |
| VDDA_ADC_1P8 | | | 1 | | | | under K15 |
| VDDA_ADC_3P3 | | | 1 | | | | under J13 |
| VDDA_1P0 | | | | 1 | | | under N11 |
| VDD_MIPI_1P8 | | | 1 | | | | under F9; bead from 1V8 |
| VDD_MIPI_1P0 | | | 1 | | | | under F10; source is VDDA_1P0 |
| NVCC_SD1 | | | | 1 | | | under D14 |
| NVCC_SD2 | | | | 1 | | | under G13 |
| NVCC_EMC1 | | | | 1 | 1 | | 2.2 uF under F6, F7 |
| NVCC_EMC2 | | | | 1 | 1 | | 2.2 uF under H6, J6 |
| NVCC_GPIO | | | | 1 | 1 | | 2.2 uF under M12 |
| NVCC_DISP1 | | | | 1 | | | under D12 |
| NVCC_DISP2 | | | | 1 | | | under E7 |
| NVCC_LPSR | | | | 1 | | | under P7 |
| NVCC_SNVS | 1 | | | | | | under U11 |
| ADC_VREFH | | | | 1 | | | under G16 |
| USB1_VBUS / USB2_VBUS | | | 1 each | | | | under D17 / D16 |

The EVKB follows this table and adds 10 uF + 22 uF on DCDC_ANA and 10 uF on DCDC_DIG (see section 4 and evk_bom_core.csv).
Ripple limit: below 5 % Vp-p on VDD_xxx, VDD_xxx_IN, VDDA_1P0, VDD_xxx_ANA, VDD_xxx_DIG (HDUG Table 3).

## 7. Crystals

**24 MHz (XTALI U16 / XTALO T16)** — required: "The SDK software requires 24 MHz on XTALI/XTALO" (DS Table 4); an external 24 MHz clock
into XTALI is the alternative (level must not exceed VDD_LPSR_ANA).
* DS Table 28 (p.45): load capacitance "see crystal manufacturer's recommendation"; pin parasitic 1.5 pF typ / 2.0 pF max; series resistor
  0 typ; feedback resistor not needed in low-power mode, 1 Mohm in high-gain mode; start-up 250 us typ; supply current 0.5 mA (low power) /
  1.3 mA (high gain). The oscillator is off at power-up and is enabled by ROM/firmware.
* HDUG Table 4: fundamental-mode crystal; typical 80 ohm ESR with max drive level 250 uW, or 50 ohm ESR with 200 uW, are acceptable; lower
  ESR is better; USB needs +-100 ppm (Ethernet +-50 ppm).
* EVKB: Y4 24 MHz 4-pad, schematic note "ESR<=60OHM, +-20PPM, CL=8PF, -30~85C"; C316 = C317 = 4.7 pF; R189 1 Mohm DNP (SCH sheet 6).

**32.768 kHz (RTC_XTALI T13 / RTC_XTALO U13)** — sources disagree on whether it is required:
* DS Table 4 / Table 6: optional. Without a crystal tie RTC_XTALI to GND and leave RTC_XTALO open; the internal 32 kHz ring oscillator
  (tolerance +-25 % in DS-A Rev 5 / DS-B) is then used. "NXP recommends using an external crystal."
* HDUG Rev 2 section 4: "For RT1170, it is necessary to use 32.768-kHz and 24-MHz crystals for the hardware design" — and the same table
  describes the fallback as "approximately 40 kHz", "+-50 %".
* Requirements when fitted: max ESR 100 kohm, no external bias resistor, leakage to rails > 100 Mohm, load capacitors per crystal maker
  reduced for parasitics (HDUG Table 4, DS Table 4). DS Table 29: parasitic 1.5 / 2.0 pF, amplitude 0.6 V, start-up 500 ms typ.
* EVKB: Y5 32.768 kHz fitted; load capacitors C109 / C110 (18 pF) are **DNP** (SCH sheet 6).

## 8. Current consumption (DS-B Table 14, single core = RT1172; p.35-37; "typical", supplies at 3.3 V, code in ITCM, IO not included)

Units were confirmed on a rendered page (`png/BIEC_table14-035.png`); the text layer drops the micro sign.

| Mode | DCDC_IN 25 C / 105 C | VDD_LPSR_IN 25 / 105 C | VDD_SNVS_IN 25 / 105 C | Total power 25 / 105 C |
|---|---|---|---|---|
| Set point 1 active: M7 800 MHz, 1.1 V + FBB, all PLLs and peripherals on | 123 / 319.8 mA | 36.3 / 40.8 uA | 4 / 12 uA | 406.0 / 1055.5 mW |
| Set point 0 active: M7 600 MHz, 1.0 V | 75.9 / 120.8 mA | 36.3 / 40.7 uA | 3.9 / 11.6 uA | 250.6 / 398.8 mW |
| Set point 5 active: M7 240 MHz, 0.9 V | 41.5 / 67.5 mA | 36.1 / 40.7 uA | 3.9 / 10.8 uA | 137.1 / 222.9 mW |
| Set point 7 active: M7 200 MHz, 0.9 V, PLLs gated | 24.3 / 48.2 mA | 36.1 / 40.6 uA | 3.9 / 10.5 uA | 80.3 / 159.2 mW |
| Set point 1 standby suspend | 4.2 / 22.2 mA | 27.4 / 30.4 uA | 3.9 / 10.3 uA | 13.96 / 73.39 mW |
| Set point 0 standby suspend | 3.1 / 16.8 mA | 27.3 / 29.6 uA | 3.9 / 10.3 uA | 10.33 / 55.57 mW |
| Set point 5 standby suspend | 2.4 / 12.9 mA | 27.3 / 29.3 uA | 3.9 / 10.2 uA | 8.02 / 42.70 mW |
| Set point 10 standby suspend (0.8 V, RBB) | 1.9 / 8.6 mA | 27.1 / 29.2 uA | 3.9 / 10.2 uA | 6.37 / 28.51 mW |
| Set point 15 standby suspend (M7 off, DCDC off, LPSR LDOs on) | 26.3 / 44.2 uA | 0.423 / 3.5 mA | 3.8 / 10.1 uA | 1.495 / 11.73 mW |
| SNVS (only SNVS powered, RTC alive) | 0 | 0 | 3.9 / 10.2 uA | 12.87 / 33.66 uW |

Maximum (worst-case design figure) is Table 12: DCDC_IN 1000 mA "for chip at 125 C" (see section 1). Typical wake-up: SNVS to ROM exit
8.54 ms; standby set points to overdrive run about 7-8 ms (DS Table 15).
Standby current also flows in whatever the board hangs on the rails; SNVS pin leakage notes are in AN13104 (not fetched).
