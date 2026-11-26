# i.MX RT1172 hardware-design data set (289 MAPBGA) — summary

Collected 2026-11-26 from public sources only (no sign-in, no purchases). Downloads are in `../src/`, scripts in `../tools/`, results here.
Files beginning with `_` are intermediate parser outputs and logs kept for traceability; `_src_sha256.txt` lists the source files with
SHA-256 prefixes. `png/` holds the page renders that were read by eye.

## Read these four findings first

1. **The RT1172 has no Cortex-M4.** Data sheet Table 1 shows "—" in the M4 row for MIMXRT1172 (A and B, industrial and consumer); confirmed on
   a rendered page, by the part-number key ("2 = Single Core Enhanced Feature") and by the SDK device files. The only peripheral it lacks
   versus the RT1176 is ENET_QOS (1 Gb TSN). It **does** have GPU2D, PXP, MIPI DSI/CSI, LCDIF, 3x CAN-FD and both other Ethernet MACs.
   Dual-core parts are RT1173/1175/1176. Details: `rt1172_vs_rt1176.md`.
2. **MIMXRT1172CVM8A is A silicon; NXP's PCN 202502019I says it is "NOT recommended for new application design"** and names
   MIMXRT1172CVM8B as the replacement. On A silicon erratum ERR052351 says the GPIO_AD, GPIO_LPSR and GPIO_DISP_B2 banks must be powered at
   1.8 V (output drivers degrade over time above 1.98 V). B silicon fixes that but adds ERR052401 (SEMC_CSX1/2/3 too slow for SDRAM —
   use SEMC_CS0, SEMC_CSX0 or SEMC_RDY). The ball map is identical for A and B.
3. **The EVKB is neither 3.3 V-only nor fitted with a 3.3 V flash.** It has a 1.8 V LDO (AMS1117-1.8) feeding VDDA_1P8_IN, VDD_USB_1P8,
   VDDA_ADC_1P8, VDD_MIPI_1P8, NVCC_DISP1 and the flash; the boot flash is a **1.8 V W25Q512NWEIQ** with NVCC_SD2 at 1.8 V. A 3.3 V flash on
   those pads is within the data sheet (NVCC_SD2 3.0-3.6 V; the EVKB has a DNP 0R option for it) but there is no NXP reference for it. The
   chip's own DCDC_ANA 1.8 V output can replace the LDO for on-chip loads only (EVKB jumper/DNP option). Details: `power.md`, `boot.md`.
4. **The SDRAM report is confirmed:** two W9825G6KH (-5I on the EVKB) form one 32-bit bus on a single chip select (SEMC_CS0), no series
   resistors except 0R in the clock at each chip, DQS pad (J2) left floating. Details: `sdram.md`, `sdram.csv`.

## Deliverables

| File | Content | Primary source | Verification |
|---|---|---|---|
| `ballmap.csv` | 289 rows, one per ball | IMXRT1170BIEC Rev 1 Tables 115 + 116 (text layer, parsed by `tools/parse_ds.py`) | count = 289 unique, none unresolved; identical to the same tables in IMXRT1170IEC Rev 5 and IMXRT1170CEC Rev 5; all 289 equal to the data sheet's own ball-map grid (Table 117, `tools/parse_ballmap.py`, 0 mismatches); 150 balls equal to NXP config-tool annotations in 177 EVKB SDK `pin_mux.c` files; 285 balls equal to the EVKB schematic symbol read from PNG crops; every ball has at least one second source; 0 mismatches |
| `pinmux.csv` | 177 pads, ALT0..ALT11, analog functions, functions removed on RT1172, mux/config register addresses, reset default | Zephyr hal_nxp@964eca29 pinctrl dtsi for MIMXRT1176AVM8A with the MIMXRT1173CVM8A (= 1172CVM8A) delete list | compared with MicroPython@69912120 `ports/mimxrt/boards/MIMXRT1176_af.csv` (`_pinmux_xcheck.log`): no functional difference, only naming (127 name-style differences such as FLEXIO1_D00 vs FLEXIO1_FLEXIO00; 9 entries only in MicroPython: ACMPn_OUT x4, NMI_GLUE_NMI x2, REF_CLK_24M/32K, one test signal). Data-sheet reset defaults agree with the ALT column for all pads |
| `rt1172_vs_rt1176.md` | feature differences, feature checklist, CVM8A/DVMAA, A/B silicon | data sheets Table 1, AN14716, PCN, errata | Table 1 confirmed on a rendered page |
| `power.md` | rails, currents, DCDC parts, sequence, reset pins, shared rails, EVKB power tree, decoupling, crystals, consumption | data sheet 4.1-4.2, HDUG Rev 2, EVKB schematic | HDUG capacitor table and data-sheet units confirmed on rendered pages |
| `boot.md` | boot pins, BT_CFG, flash pads, DQS, flash voltage, serial downloader, SWD | data sheet section 5, HDUG, EVKB schematic | — |
| `sdram.md`, `sdram.csv` | EVKB SDRAM wiring, layout rules, 128 MB options, size limits | EVKB schematic + SDK pin table | pad/ball/signal triple agrees between SDK and schematic for all rows |
| `evk_bom_core.csv` | 147 rows of parts around the MCU with refdes, value, sheet | EVKB schematic SPF-55139 C1, read from PNG crops | visual reading only — no BOM spreadsheet was obtained |
| `layout_notes.md` | NXP stack-up/fan-out guidance, EVKB stack-up, JLCPCB facts | HDUG, EVKB documents, JLCPCB pages (2026-11-26) | — |

Marking convention inside the files: **INFERRED** = my deduction from the cited sources; **COMPUTED** = arithmetic on cited numbers; anything
"not obtained / not verified" is listed again below. Nothing was filled in from memory.

## Sources (local file in `../src/`)

| Document | Revision / date | URL | Local file | Note |
|---|---|---|---|---|
| i.MX RT1170 data sheet, industrial, **B silicon** | IMXRT1170BIEC Rev. 1, 05/2025 | https://www.nxp.com/docs/en/data-sheet/IMXRT1170BIEC.pdf | IMXRT1170BIEC.pdf / .txt | primary; public, no login |
| i.MX RT1170 data sheet, consumer, B silicon | IMXRT1170BCEC Rev. 1, 05/2025 | https://www.nxp.com/docs/en/data-sheet/IMXRT1170BCEC.pdf | IMXRT1170BCEC.pdf / .txt | saved, not analysed beyond identification |
| i.MX RT1170 data sheet, industrial, A silicon | IMXRT1170IEC Rev. 5, 01/2024 | https://www.nxp.com/docs/en/data-sheet/IMXRT1170IEC.pdf | IMXRT1170IEC.pdf / .txt | covers MIMXRT1172CVM8A |
| i.MX RT1170 data sheet, consumer, A silicon | IMXRT1170CEC Rev. 5, 01/2024 | https://www.nxp.com/docs/en/data-sheet/IMXRT1170CEC.pdf | IMXRT1170CEC.pdf / .txt | DVMAA parts |
| Migration guide RT1170A to RT1170B | AN14716 Rev. 3.0, 9 July 2026 | https://www.nxp.com/docs/en/application-note/AN14716.pdf | AN14716.pdf / .txt | |
| Chip errata, A silicon | IMXRT1170ACE Rev. 1.6, 24 Oct 2024 | https://www.nxp.com/docs/en/errata/IMXRT1170ACE.pdf | IMXRT1170ACE.pdf / .txt | |
| PCN "i.MX RT1170 Silicon Revision" | 202502019I, 13 Mar 2025 | https://www.nxp.com/pcn/202502019I | not saved (read through a fetch tool that returns a summary) | part-number table quoted in rt1172_vs_rt1176.md |
| Hardware Development Guide MIMXRT1160/1170 | MIMXRT1170HDUG **Rev. 2, 09/2021** | https://community.nxp.com/pwmxy87654/attachments/pwmxy87654/imx-processors/208569/1/MIMXRT1170HDUG.pdf | MIMXRT1170HDUG_community208569.pdf, MIMXRT1170HDUG_rev2.txt | NXP community attachment; nxp.com copy needs login. **Not the latest revision** |
| MIMXRT1170-EVKB schematic | SPF-55139 / SCH-55139 Rev C1, 27 Oct 2022 | https://community.nxp.com/pwmxy87654/attachments/pwmxy87654/Power-Management/2541/1/SPF-55139_c1.pdf | SPF-55139_C1.pdf / .txt | NXP community attachment; official design-file package needs login |
| MIMXRT1170-EVKB layout artwork | LAY-55139 Rev C1, 2022 | https://community.nxp.com/pwmxy87654/attachments/pwmxy87654/imx-processors/207768/1/LAY-55139_C1.pdf | LAY-55139_C1.pdf / .txt | NXP community attachment; artwork films and fab drawing only |
| MIMXRT1170 EVKB Board Hardware User Guide | MIMXRT1170EVKBHUG Rev. 4, 11 June 2024 | https://community.nxp.com/pwmxy87654/attachments/pwmxy87654/imxrt/31740/1/MIMXRT1170EVKBHUG.pdf | MIMXRT1170EVKBHUG.pdf / .txt | NXP community attachment |
| PCN data-sheet Rev 3 notice (distributor copy) | 202207014I | https://www.farnell.com/datasheets/3770909.pdf | farnell_3770909.pdf | saved, not used |
| Zephyr hal_nxp | commit 964eca29f31d7c4a28bc36651060c512ab1ef9e4 (2026-11-26) | https://github.com/zephyrproject-rtos/hal_nxp | hal_nxp_*.dtsi, hal_nxp_*features.h, hal_nxp_MIMXRT1176_fsl_iomuxc.h, hal_nxp_RT1170_PERI_SEMC.h | pinctrl data, SDK headers |
| MicroPython | commit 6991212019fb791617b0382061bfe2c8465d50ba | https://github.com/micropython/micropython | micropython_MIMXRT1176_af.csv, micropython_MIMXRT1170_EVK_pins.csv | AF table cross-check |
| NXP mcux-sdk | commit 8a289764d763ad06e0c3a05c885644ed98b970af | https://github.com/nxp-mcuxpresso/mcux-sdk | mcuxsdk_evkbmimxrt1170_* (dcd.c, xmcd.c, flexspi_nor_config.c/.h, board.h, template pin_mux.c) | EVKB boot data |
| NXP mcux-sdk-examples | commit 52b428258efda7d5bd8a2ace2195ca828356743a | https://github.com/nxp-mcuxpresso/mcux-sdk-examples | ex_*_pin_mux.c, sdk_examples_pin_mux/ (177 files) | ball-number annotations |
| JLCPCB capabilities | read 2026-11-26 | https://jlcpcb.com/capabilities/pcb-capabilities | jlcpcb_capabilities_pcb-capabilities.html | |
| JLCPCB via covering help | "Last updated on Nov 10, 2026" | https://jlcpcb.com/help/article/pcb-via-covering | jlcpcb_help_article_pcb-via-covering.html | |
| JLCPCB free via-in-pad news | Nov 02, 2022 | https://jlcpcb.com/news/free-via-in-pad-6-20-layer-pcbs-pofv | jlcpcb_news_free-via-in-pad-6-20-layer-pcbs-pofv.html | |
| JLCPCB impedance stack-ups | read 2026-11-26 | https://jlcpcb.com/impedance | jlcpcb_impedance.html | only the 1.6 mm tab is in the static page |

NuttX sources were not needed and not fetched.

## Could not be obtained

* **Reference manual IMXRT1170RM** (any revision; PCNs show Rev 5 exists). Login-gated at nxp.com; no community or distributor copy found.
  Effects: the IOMUXC chapter was replaced by Zephyr/MicroPython data; BOOT_CFG bit meanings come from the EVKB schematic's printed table;
  the fuse map, the SEMC chapter's maximum SDRAM size, the function of SEMC_CLKX0/1 and the FlexSPI reset-pin default are not cited.
* **Current HDUG revision.** Only Rev 2 (09/2021) is public. A search-result summary of an NXP community post ("RT1170 HDUG important
  update") says a later revision changes the VDDA_1P8_IN capacitor in Tables 1 and 2 from 0.1 uF to 1 uF; the post itself is behind a bot
  check and was not read, so this is unverified.
* **B-silicon errata document** (only AN14716's summary of the changes).
* **EVKB BOM spreadsheet and board file.** Part values in `evk_bom_core.csv` are read from the schematic drawing; manufacturer part numbers
  for passives, the crystals and the inductor are not in it. EVKB trace lengths and the fan-out per ball row are not known.
* **NXP land pattern for the 289 MAPBGA** (data sheet Figure 55 is an image; not transcribed).
* **JLCPCB 1.2 mm 6-layer impedance stack-up tables and any prices.** No 1.0 mm 6-layer impedance stack-up is listed at all.
* **5 V tolerance:** the data sheet has no 5 V-tolerant pad statement; Table 8 limits every pad to NVCC + 0.3 V. Recorded as "not 5 V tolerant".
* **Per-part ball differences (RT1171/72/73/75/76):** none are documented — the data sheet has a single ball table for all parts. Whether
  the MIPI balls are bonded on RT1171/RT1175 is not stated; for the RT1172 MIPI is a listed feature. GPIO_SNVS pads are GPIO-only (no
  tamper) on the RT1172.
* W25Q128JV and W9825G6KH data-sheet facts (pinouts, flash commands) were out of scope and not collected; SDRAM pin numbers in `sdram.csv`
  are as drawn on the EVKB symbol.

## Where sources disagree

| Topic | Source A | Source B | Used |
|---|---|---|---|
| Cores of the RT1172 | task brief: M7 + M4 | data sheets Table 1, SDK: M7 only | data sheet |
| What RT1172 lacks | task brief: possibly GPU/MIPI/LCDIF/CAN | data sheet: only M4 and ENET_QOS | data sheet |
| Recommended part | task brief: MIMXRT1172CVM8A | PCN 202502019I: A silicon not recommended for new designs, use …CVM8B | flagged |
| IO voltage on GPIO_AD/LPSR/DISP_B2 | data sheets: 3.3 V allowed; EVKB runs them at 3.3 V | errata ERR052351 (A silicon): use 1.8 V | flagged; B silicon removes the conflict |
| EVKB SDRAM speed grade | task brief: W9825G6KH-6 | schematic and EVKBHUG: W9825G6KH-5I | schematic |
| EVKB "3.3 V only" supply | task brief | schematic: external 1.8 V LDO is the default 1.8 V source | schematic |
| DCDC inductor saturation current | data sheet Table 22: 1 A typ | HDUG 3.1: > 1.5 A (EVKB part 1.9 A) | both given |
| DCDC_ANA output capacitance | data sheet Table 22: 33 uF typ; EVKB about 34 uF | HDUG Table 1: 2.2 uF | both given |
| 32.768 kHz crystal | data sheet: optional, tie RTC_XTALI to GND, internal oscillator +-25 % | HDUG Rev 2: "necessary", internal about 40 kHz +-50 % | both given |
| RTC load capacitors | HDUG: follow crystal maker | EVKB: 18 pF footprints DNP | both given |
| NAND boot DATA[2] pad | data sheets (A and B) Table 103: GPIO_EMC_B2_02 | HDUG Table 11 and pin-mux data: GPIO_EMC_B1_02 | B1_02 (data sheet typo; not relevant to this board) |
| HDUG Table 11 tail | lists pads such as GPIO_SD_B0_05, GPIO_AD_B1_13 that do not exist on the RT1170 (left over from RT1050/1060) | data sheet Tables 103-114 | data sheet |
| JTAG_MOD text | DS-A Rev 5: "high = IEEE 1149.1 mode" | DS-B Rev 1 / AN14716: corrected to "low" | board action unchanged (pull down) |
| NVCC_GPIO name | DS-B Table 11 calls it NVCC_AD | everywhere else NVCC_GPIO (AN14716 says the rename will be reverted) | NVCC_GPIO |
| Max 1.8 V-mode voltage of NVCC_GPIO/LPSR/DISP2 | DS-A: 1.95 V | DS-B: 1.98 V | both given |
| JLCPCB via-in-pad | capabilities page: "default for 6-layer and above" | 2022 news post: free on "6-20 layer" boards | both given |

## Method notes

* PDFs were treated as data: `pdftotext -layout`, then scripts run with `python3 -I` from `../tools/` (`parse_ds.py`, `parse_ballmap.py`,
  `xcheck_sdk.py`, `parse_pinctrl.py`, `gen_csv.py`, `gen_sdram_bom.py`, `crop.sh`).
* Pages rendered to PNG and read by eye because text extraction was unreliable or to confirm it: data sheet Table 1 (ordering) and the
  power-mode table units; HDUG Table 1/2 (capacitor columns); EVKB schematic sheets 3, 5, 6, 7, 8, 12, 13, 20, 24, 26, 27 (the schematic
  text layer places pin numbers one line off, so it was not used for connectivity).
* Schematic sheets not examined in detail: 4 (external PMIC), 9-11, 14-19, 21-23, 25. The microSD socket wiring (sheet 11) was not
  transcribed; only its MCU side (USDHC1 on GPIO_SD_B1_00..05, NVCC_SD1 switchable 3.3/1.8 V, 10k pull-ups on CMD and D0) was read on sheet 7.
* In `evk_bom_core.csv` the per-signal assignment of the DNP pull resistors on the JTAG header was read from drawing geometry and is the
  least certain reading in the set.
