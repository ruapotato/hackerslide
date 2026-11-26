# Boot, flash, serial download and debug — i.MX RT1172

Sources: **DS-B** IMXRT1170BIEC Rev 1 section 5 (p.109-114, Tables 102-112; identical in DS-A Rev 5 apart from the removed SAI1 table);
**HDUG** MIMXRT1170HDUG Rev 2 sections 5-6 and 7.3; **SCH** SPF-55139 C1 sheets 5, 7, 12, 24, 26 (PNG crops read);
**EVKBHUG** MIMXRT1170EVKBHUG Rev 4 section 2.2; SDK flash config `mcux-sdk@8a289764 boards/evkbmimxrt1170/xip/evkbmimxrt1170_flexspi_nor_config.c`;
ball numbers from ballmap.csv, mux numbers from pinmux.csv.
**Not obtained: the reference manual (IMXRT1170RM, login only).** The BOOT_CFG bit meanings below are therefore taken from the table NXP
printed on the EVKB schematic (sheet 24), not from the RM System Boot chapter or the fuse map.

## 1. Boot mode pins

| Signal | Pad | Ball | Supply | Reset state | Source |
|---|---|---|---|---|---|
| BOOT_MODE[0] | GPIO_LPSR_02 | P6 | NVCC_LPSR | ALT0, input, 35k pull-down | DS Table 102, Table 116 |
| BOOT_MODE[1] | GPIO_LPSR_03 | T7 | NVCC_LPSR | ALT0, input, 35k pull-down | DS Table 102, Table 116 |

| BOOT_MODE[1:0] | Boot type | Source |
|---|---|---|
| 00 | Boot from fuses | EVKBHUG Table 2; SCH sheet 24 |
| 01 | Serial downloader | same |
| 10 | Internal boot (boot device chosen by BT_CFG pins or fuses) | same |
| 11 | Reserved | same |

HDUG Table 9: logic 0 = 100k to GND (or rely on the internal 35k pull-down); logic 1 = 4.7k to **NVCC_LPSR**. With fuses configured the
pins can be left open. EVKB: R34/R35 100k to GND, DIP SW1-4 (BOOT_MODE[0]) / SW1-3 (BOOT_MODE[1]) pull to VDD_3V3 through 1k, then 4.7k
series resistors R348/R347 to the pads (so the pads stay usable as GPIO).

## 2. Boot configuration pins (override fuses while BT_FUSE_SEL = 0, i.e. on an unprogrammed part)

DS Table 102. All are High-Z at reset (no internal pull) and **must not float** during development (HDUG Table 9 item 1).

| BT_CFG bit | Pad | Ball | Supply group |
|---|---|---|---|
| 0 | GPIO_DISP_B1_06 | D10 | NVCC_DISP1 |
| 1 | GPIO_DISP_B1_07 | E12 | NVCC_DISP1 |
| 2 | GPIO_DISP_B1_08 | A15 | NVCC_DISP1 |
| 3 | GPIO_DISP_B1_09 | C13 | NVCC_DISP1 |
| 4 | GPIO_DISP_B1_10 | B14 | NVCC_DISP1 |
| 5 | GPIO_DISP_B1_11 | A14 | NVCC_DISP1 |
| 6 | GPIO_DISP_B2_00 | E8 | NVCC_DISP2 |
| 7 | GPIO_DISP_B2_01 | F8 | NVCC_DISP2 |
| 8 | GPIO_DISP_B2_02 | E9 | NVCC_DISP2 |
| 9 | GPIO_DISP_B2_03 | D7 | NVCC_DISP2 |
| 10 | GPIO_DISP_B2_04 | C7 | NVCC_DISP2 |
| 11 | GPIO_DISP_B2_05 | C9 | NVCC_DISP2 |

Meaning for "FlexSPI1 - Serial NOR" as printed on SCH sheet 24 (`png/sch/p24_tbl.png`):

| Bits | Field | Values |
|---|---|---|
| 11 | FLEXSPI_INSTANCE | 0 = FlexSPI1, 1 = FlexSPI2 |
| 10:8 | xSPI_FLASH_TYPE | 0 = boot with default 0x03 read enabled, 1 = reserved, 2 = HyperFlash 1V8, 3 = HyperFlash 3V0, 4 = MXIC octal read, 5 = Micron octal read |
| 7:4 | (device select) | 0000 for FlexSPI serial NOR (SD card row: bit 6 = 1; SEMC NAND row: bit 5 = 1) |
| 3:2 | FLASH_PROBE_TYPE | 0 = QuadSPI NOR, 1 = MXIC octal, 2 = Micron octal, 3 = Adesto octal |
| 1 | ENCRYPT_XIP_EN | |
| 0 | FLASH_AUTO_PROBE_EN | |

**QSPI NOR on FlexSPI1: all twelve BT_CFG bits = 0, BOOT_MODE[1:0] = 10.** EVKB boot-switch table (sheet 24 and EVKBHUG Table 3): QSPI flash =
SW1 "0,0,1,0", SW2 all 0; serial downloader = SW1 "0,0,0,1".
EVKB circuit: each BT_CFG line has a 47k pull-down and reaches its pad through a 22k isolation resistor; DIP switches pull up through 1k
to the rail of the pad (BT_CFG[0..5] to VDD_1V8, [6..9] and [10..11] to VDD_3V3). HDUG Table 9 item 3 recommends 22k isolation resistors on
BT_CFG lines that are shared with other functions and 4.7k on BOOT_MODE.
For a board that only ever boots QSPI NOR: a pull-down on each of the twelve pads is enough (INFERRED from the above; no fuse needs
blowing). If the pads are reused (LCD, SPI, ...), whatever is attached must not pull them high while POR_B is released.
Not established here (needs the RM fuse map): the fuse names/addresses that would replace the pins, and what an unprogrammed part does in
"boot from fuses" mode 00.

## 3. Flash connection (FlexSPI1 port A, primary pinout)

DS Table 104 (p.110-111); balls from DS Table 116; EVKB nets from SCH sheet 7 (`png/sch/p07_sd.png`) and 12 (`png/sch/p12_qspi.png`).

| Pad | Ball | Mux | Function | EVKB net | EVKB flash U23 pin |
|---|---|---|---|---|---|
| GPIO_SD_B2_05 | E14 | ALT1 | FLEXSPI1_A_DQS | FlexSPI_A_DQS, R2135 0R **DNP** -> pad floats | not connected to the QSPI flash |
| GPIO_SD_B2_06 | F17 | ALT1 | FLEXSPI1_A_SS0_B | FlexSPI_A_SS0 | R380 0R -> CS# (pin 1), R165 10k pull-up to FLASH_VCC |
| GPIO_SD_B2_07 | G14 | ALT1 | FLEXSPI1_A_SCLK | FlexSPI_A_CLK | R399 0R -> CLK (pin 6) |
| GPIO_SD_B2_08 | F15 | ALT1 | FLEXSPI1_A_DATA00 | FlexSPI_A_D0 | R386 0R -> DI/IO0 (pin 5) |
| GPIO_SD_B2_09 | H15 | ALT1 | FLEXSPI1_A_DATA01 | FlexSPI_A_D1 | R390 0R -> DO/IO1 (pin 2) |
| GPIO_SD_B2_10 | H14 | ALT1 | FLEXSPI1_A_DATA02 | FlexSPI_A_D2 | R392 0R -> WP#/IO2 (pin 3), R176 33k pull-up DNP |
| GPIO_SD_B2_11 | F16 | ALT1 | FLEXSPI1_A_DATA03 | FlexSPI_A_D3 | R385 0R -> HOLD#/IO3 (pin 7), R171 33k pull-up DNP |

All seven pads are in the **NVCC_SD2** group (ball G13). The 0R parts on the EVKB select between the QSPI and the octal flash footprints;
they are not terminations.

Other pads the ROM can use for FlexSPI1 (DS Table 104/106): port B data GPIO_SD_B2_00..03, B_SCLK GPIO_SD_B2_04, B_DQS GPIO_SD_B1_05 (ALT8),
B_SS0_B GPIO_SD_B1_04 (ALT8), A_SS1_B GPIO_SD_B1_02 (ALT9), B_SS1_B GPIO_SD_B1_03 (ALT9); secondary A_DQS GPIO_EMC_B2_18 (ALT6);
flash reset GPIO_SD_B1_00 (ALT5, GPIO) or secondary GPIO_EMC_B1_40. "ROM does not support boot from FLEXSPI_B port directly. ROM always
seeks a valid Flash Configuration Block from the FLEXSPI_A port" (HDUG note after Table 11).
Caution: GPIO_SD_B1_00 is also USDHC1_CMD (the microSD port on the EVKB). Whether the ROM drives a flash reset pulse there by default is a
fuse-controlled option described in the RM — not verified.

### DQS loopback pad

* DS section 4.5.2.1 / HDUG 7.3: read data can be sampled by (0) an internally looped-back dummy strobe — max **60 MHz** SDR (Table 53);
  (1) a dummy strobe looped back **through the DQS pad** — max **133 MHz** SDR (Table 54); (3) a strobe from the flash (octal parts).
* HDUG 7.3: "for QSPI Flash without a DQS provided by the memory, only the option of FlexSPIn_MCR0[RXCLKSRC] = 0x1 can achieve 133 MHz SDR
  R/W speed, and FlexSPI_DQS pin should be left floating." SCH sheet 7 repeats it: "FlexSPI_DQS PIN need floating (DNP R2135) for QSPI
  Flash RW @133MHz".
* So GPIO_SD_B2_05 (E14) must be left unconnected (no trace stub, nothing else muxed on it) if more than 60 MHz is wanted. The EVKB flash
  configuration block uses `kFlexSPIReadSampleClk_LoopbackFromDqsPad`, `kFlexSpiSerialClk_133MHz`, `kSerialFlash_4Pads`.

### 1.8 V or 3.3 V flash

* Electrically the pad group allows both: NVCC_SD2 = 3.0-3.6 V or 1.65-1.95 V (DS Table 11). The GPIO_SD_B2 bank is the
  EMC/SD/DISP_B1 pad type (DS Table 35/38), which is **not** the pad type hit by erratum ERR052351.
* The FlexSPI timing tables (DS Tables 53-62) give one set of numbers with no split by IO voltage.
* **The EVKB uses a 1.8 V flash**: U23 **W25Q512NWEIQ** (512 Mbit) on FLASH_VCC, and FLASH_VCC = VDD_1V8 through bead L1 ("Flash VCC Option,
  1.8V default"). A 3.3 V option exists as R16 0R (DNP) from VDD_3V3 to FLASH_VCC (SCH sheet 5), so NXP provided for 3.3 V flash on these
  pads. Schematic revision history: "C: Changed Flash part number from W25Q128JWSIQ to W25Q512NWEIQ" — the earlier EVKB fit was also a
  1.8 V part. EVKBHUG Rev 4 lists the older MIMXRT1170-EVK part as S25WP128 (differences table; not checked further).
* A 3.3 V W25Q128JV on NVCC_SD2 = 3.3 V is therefore within the data sheet, but it is **not what the EVKB ships with**, so there is no NXP
  board to copy the flash configuration block from: the EVKB block is written for a 512 Mbit part with 4-byte addressing (read command
  0xEC, sflashA1Size 64 MB) and must be rewritten for a 128 Mbit part. The W25Q128JV side (quad-enable bit, read command, dummy cycles,
  133 MHz at 3.3 V) has to come from the Winbond data sheet — not collected here.

## 4. Serial downloader (first programming)

* HDUG section 5 and Table 8: the ROM serial downloader uses **USB1 (USB OTG1)** as a HID device and **LPUART1**; it polls both until it
  sees 0x5A 0xA6 on UART RXD or the first HID report. "It is strongly recommended for all boards to make at least one of the serial
  downloader ports (USB1 or UART1) available."
* USB1 balls: USB1_DP E17, USB1_DN E16, USB1_VBUS D17 (DS Table 116). USB2 (C17/C16/D16) is not a download port.
* LPUART1: GPIO_AD_24 (L13) TX, GPIO_AD_25 (M15) RX, ALT0 (DS Table 114, HDUG Table 11); CTS/RTS on GPIO_AD_26/27 are listed in DS only.
* Entered with BOOT_MODE[1:0] = 01; a blank flash in internal-boot mode is also expected to fall back to it (INFERRED from general
  i.MX RT behaviour, not read in a source — provide the BOOT_MODE[0] strap).
* B silicon needs SDK 25.06+ flashloader/ROM-API handling and J-Link 8.38+ (AN14716 sections 6-7).
* EVKB USB1 circuit (SCH sheet 20): micro-AB J20; D+/D- through 90 ohm common-mode choke L13 (0R bypass footprints DNP) to E17/E16; ESD array
  U28 RClamp0854P; connector VBUS through bead L39 to 5V_USB_OTG1, which goes **directly** to USB1_VBUS (D17) with 1 uF (no divider);
  ID pin through R201 0R to USB_OTG1_ID (a GPIO_AD pad, sheet 7).

## 5. SWD / JTAG

DS Table 116 defaults (ALT0 after reset), Table 5; HDUG Tables 5-7; SCH sheets 7 and 26.

| Function | Pad | Ball | Reset pull | Board requirement |
|---|---|---|---|---|
| SWD_CLK / JTAG_TCK | GPIO_LPSR_14 | T6 | 35k pull-down | none required |
| SWD_DIO / JTAG_TMS | GPIO_LPSR_15 | U7 | 35k pull-up | none required (10k pull-up allowed) |
| JTAG_TDO | GPIO_LPSR_11 | T5 | High-Z, keeper | no external pull-up or pull-down |
| JTAG_TDI | GPIO_LPSR_12 | U5 | 35k pull-up | optional |
| JTAG_TRSTB | GPIO_LPSR_10 | R5 | 35k pull-up | optional |
| JTAG_MOD | GPIO_LPSR_13 | U6 | 35k pull-down | pull down 4.7k (HDUG) / EVKB R403 10k, or tie to GND |

* All in the NVCC_LPSR group, so the debug probe's VTref is NVCC_LPSR (3.3 V on the EVKB).
* The EVKB uses SWD by default; JTAG needs R187, R208, R195 and R78 removed because LPSR_10/11/12 are shared with other functions (HDUG
  section 5; SCH sheet 7).
* Probe reset: J1 pin 15 (nSRST) -> Schottky D2 -> POR_PIN_RST_B (POR_B, T10). VTref pin 1 through R45 100R to VDD_3V3. Pull-up/pull-down
  footprints on the header are mostly DNP (see evk_bom_core.csv).
* A silicon only: ERR050643 (pull-up pulse on LPSR/AD/DISP_B2 pins during power-up) and ERR052351 (3.3 V on NVCC_LPSR) concern this bank.
