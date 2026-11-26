# SDRAM on SEMC — as built on the MIMXRT1170-EVKB, and how to reach 128 MB

Sources: **SCH** SPF-55139 C1 sheet 8 (MCU side) and sheet 13 (SDRAM), read from PNG crops (`png/sch/p08_emc1.png`, `p08_emc2.png`,
`p08_ser.png`, `p13_u13.png`, `p13_u25.png`, `p13_cke.png`); SDK pin table `mcux-sdk-examples@52b42825
evkbmimxrt1170/driver_examples/semc/sdram/cm7/pin_mux.c` (NXP config-tool output with ball numbers); SDK boot data
`mcux-sdk@8a289764 boards/evkbmimxrt1170/dcd.c` and `xmcd/xmcd.c`; **DS-B** IMXRT1170BIEC Rev 1 section 4.5.1 and Table 116;
**HDUG** Rev 2 section 7.4; register header `hal_nxp@964eca29 mcux/mcux-sdk-ng/devices/RT/RT1170/periph/PERI_SEMC.h`; AN14716 Rev 3.0.
The reference manual was **not obtained**; where it would be the proper source the row says so.
Every signal is listed in `sdram.csv` (63 rows: 57 used by the SDRAM + DQS + 5 pads the SDK example muxes but the SDRAM does not use).

## 1. Topology on the EVKB — confirmed

* Two **W9825G6KH-5I** (U13, U25), each 4M x 4 banks x 16 bit = 256 Mbit; together 64 MB. (The EVKB fits the -5I speed grade, not -6.)
* **One 32-bit data bus, one chip select.** U13 carries SEMC_D0..D15 with DM0 (LDQM) / DM1 (UDQM); U25 carries SEMC_D16..D31 with
  DM2 (LDQM) / DM3 (UDQM). Address A0..A12, BA0/BA1, RAS, CAS, WE, CKE, CLK and **SEMC_CS0** go to both chips in parallel.
* SDK configuration agrees: SEMC_SDRAMCR0 = 0xF32 (port size field = 32 bit, column field = 9 bits), SEMC_BR0 = 0x8000001D (base
  0x80000000, size code 64 MB), XMCD "SDRAM CS0 size: 64MBytes, Port_size: 32-bit, SDRAM clock 198 MHz".
* Supply: the SDRAMs run from SDRAM_3V3 = VDD_3V3 through bead L25 (120 ohm); 22 uF + 4.7 uF + 7 x 0.1 uF at U13, 4.7 uF + 7 x 0.1 uF at
  U25.

## 2. Pad list (summary; details and ball numbers in sdram.csv)

| SEMC signal | Pads (ALT0) | Supply group |
|---|---|---|
| DATA00..07 | GPIO_EMC_B1_00..07 | NVCC_EMC1 |
| DM0 | GPIO_EMC_B1_08 | NVCC_EMC1 |
| ADDR00..09 | GPIO_EMC_B1_09..18 | NVCC_EMC1 |
| ADDR11, ADDR12 | GPIO_EMC_B1_19, _20 | NVCC_EMC1 |
| BA0, BA1 | GPIO_EMC_B1_21, _22 | NVCC_EMC1 |
| ADDR10 | GPIO_EMC_B1_23 | NVCC_EMC1 |
| CAS, RAS, CLK, CKE, WE, CS0 | GPIO_EMC_B1_24, _25, _26, _27, _28, _29 | NVCC_EMC1 |
| DATA08..15 | GPIO_EMC_B1_30..37 | NVCC_EMC1 |
| DM1 | GPIO_EMC_B1_38 | NVCC_EMC1 |
| DQS (loopback) | GPIO_EMC_B1_39 | NVCC_EMC1 |
| DATA16..23 | GPIO_EMC_B2_00..07 | NVCC_EMC2 |
| DM2 | GPIO_EMC_B2_08 | NVCC_EMC2 |
| DATA24..31 | GPIO_EMC_B2_09..16 | NVCC_EMC2 |
| DM3 | GPIO_EMC_B2_17 | NVCC_EMC2 |

Note the non-monotonic address order: ADDR10 is on GPIO_EMC_B1_23, after BA1.
IO supply: NVCC_EMC1 (F6, F7, G6) and NVCC_EMC2 (H6, J6), both **3.3 V** on the EVKB (VDD_3V3). The W9825G6KH is a 3.3 V part, so both
banks must be 3.3 V. These banks are not affected by erratum ERR052351.

## 3. Series resistors and terminations on the EVKB

* **No termination and no series resistors on data, address, DM, BA, RAS/CAS/WE, CKE or CS.**
* **SEMC_CLK: one 0R series resistor per SDRAM**, R365 at U13.CLK and R407 at U25.CLK (the clock net forks to the two resistors).
* R1983..R1989 (0R) sit in series on SEMC_D26..D31 and SEMC_DM3 (GPIO_EMC_B2_11..17). They only isolate DNP branches to audio/Bluetooth
  nets that share those pads (schematic note: "Those 0ohm resistors are used for signal multiplexion usage, should avoid long stub").
* Pull footprints, all DNP: R90 / R145 4.7k from SEMC_CS0 to SDRAM_3V3; R135 / R213 100k from SEMC_CKE to GND.
* **SEMC_DQS (GPIO_EMC_B1_39, ball J2) is not connected to the SDRAM** and is left floating; C91 10 pF to GND is a DNP footprint.
  Schematic note: "SEMC_DQS PIN need floating for SDRAM RW @200MHz". The pad is still muxed to SEMC_DQS with input path forced on
  (`software_input_on: Enable` in the SDK pin table) and SEMC_MCR = 0x10000004 sets DQSMD = 1 ("dummy read strobe loopbacked from DQS
  pad"). Reason in DS Tables 51/52: input setup time 8.67 ns with internal loopback versus 0.6 ns with the DQS pad.

## 4. Layout rules

HDUG Rev 2 section 7.4 and 7.7 (p.19-21):
* Interface runs up to 200 MHz; single-ended impedance 50 ohm.
* "Ideally, route all signals at the same length as the EVK board"; match all signals to +-50 mil.
* Two routing groups: (a) all data lines and DM[x]; (b) all address and control lines. On the 6-layer EVK one group is on the top layer
  referenced to layer 2 (GND), the other on the bottom layer referenced to layer 5 (GND).
* SEMC_DQS left floating.
* No reference-plane gaps under SDRAM signals; ground return vias within 100 mil of signal layer changes; clocks/strobes spaced 2.5 x the
  height above the plane from neighbours.
* **No maximum trace length is given** in the HDUG or the data sheet; the only instruction is to copy the EVK lengths. The actual EVKB
  lengths were not measured (the layout PDF LAY-55139 C1 is artwork only; the board file was not obtained).
* DS-B Table 49: SEMC SYNC output 200 MHz max, TDVO 0.6 ns max, TDHO -0.7 ns min (address/data/DM/CKE/control relative to SEMC_CLK).
  DS Figure 9 covers overshoot/undershoot on the MCU-SDRAM net (not transcribed).

## 5. Reaching 128 MB

### 5a. Second pair of chips on another chip select

SEMC has SDRAM chip selects CS0..CS3. CS0 has its own pad; CS1..CS3 come out on pads whose function is chosen in SEMC_IOCR
(fields MUX_CSX0..3 and MUX_RDY each offer "SDRAM CS1 / CS2 / CS3"; register header PERI_SEMC.h). Pads (pinmux.csv):

| Pad | Ball | Mux | SEMC function | Supply group | Usable for a second SDRAM pair? |
|---|---|---|---|---|---|
| GPIO_EMC_B1_29 | E6 | ALT0 | SEMC_CS0 | NVCC_EMC1 | already used (first pair) |
| GPIO_EMC_B1_41 | L1 | ALT0 | SEMC_CSX0 | NVCC_EMC1 | **yes** |
| GPIO_EMC_B1_40 | K1 | ALT0 | SEMC_RDY | NVCC_EMC1 | **yes** |
| GPIO_AD_26 | L14 | ALT2 | SEMC_CSX1 | NVCC_GPIO | avoid on B silicon |
| GPIO_AD_27 | N16 | ALT2 | SEMC_CSX2 | NVCC_GPIO | avoid on B silicon |
| GPIO_AD_28 | L17 | ALT2 | SEMC_CSX3 | NVCC_GPIO | avoid on B silicon |

* B-silicon erratum **ERR052401** (AN14716 section 5): SEMC_CSX1/2/3 output delay grew and violates Tdvo by about 2.4 ns in SYNC mode;
  "For the SYNC mode memory, use SEMC_CSX0 or SEMC_RDY as a chip select. SDRAM can use SEMC_CS0 as well."
* CSX1..3 are also in the GPIO_AD bank, whose rail may have to be 1.8 V on A silicon (ERR052351) — another reason to stay on EMC_B1_40/41.
* On the EVKB both of those pads go to the NAND flash (SEMC_CSX0, SEMC_RDY, sheet 14); a board without NAND has them free.
* Wiring of the second pair (INFERRED — no NXP board does this): identical to the first pair except CS; data D0..15/DM0..1 to chip 3,
  D16..31/DM2..3 to chip 4. Address/control nets then see four loads and each data net two, so the EVKB point-to-point length-matching
  guidance no longer transfers directly.
* GPIO_EMC_B2_19 / _20 offer SEMC_CLKX0 / CLKX1 (ALT0); what they output is described in the RM — not verified, not used on the EVKB for
  SDRAM.

### 5b. Two larger chips on the same chip select (INFERRED alternative)

SEMC_SDRAMCR0.COL allows 9, 10, 11 or 12 column bits (or 8 with COL8) and the pad set already carries A0..A12 and BA0..BA1, so a pair of
512 Mbit x16 SDRAMs (13 row / 10 column addresses, same 54-pin footprint family) would give 128 MB on CS0 with no extra pads or loads.
This is an inference from the register header and from the address pins present; it is not shown in any NXP document read here, and the
candidate SDRAM's data sheet must be checked for the pinout.

### 5c. Maximum SDRAM size per chip select

* Register limit: SEMC_BRn.MS (memory size) codes run from 4 KB to **4 GB** (PERI_SEMC.h, BR register, "0b10100-0b11111..4GB").
* Address-pin limit (COMPUTED, not quoted): 13 row + 2 bank + at most 12 column bits x 32-bit port = 2^27 words x 4 bytes = 512 MB.
* The reference manual statement of the maximum (IMXRT1170RM, SEMC chapter) could **not be cited**: the RM is behind the NXP login and no
  public copy was found. PCNs show the RM is at Rev 5 (202601006I) — revision known, text not read.
