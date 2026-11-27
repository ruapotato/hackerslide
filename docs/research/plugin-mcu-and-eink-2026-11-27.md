# Plug-in MCU module and small e-ink panel for the HackOS hack pad

Read 2026-11-27. All web content is read-only public pages. Downloads (untrusted) are in `/var/tmp/hackerslide-agent/mcumod/dl/`. E-ink detail notes are in `/var/tmp/hackerslide-agent/mcumod/eink-notes.md`.

Markers:
- **[P]** read from a primary page: the maker's page, the maker's datasheet, or the store.
- **[S]** secondary: a search snippet, retailer copy, a press article or a forum post.
- **[E]** my estimate.
- **[NR]** not read, because the page was blocked or rate-limited.

Several Shopify stores (Pimoroni, Electro-Smith, store.arduino.cc on a second visit, OpenMV) returned HTTP 429 all session, so their stock is **[NR]**.

---

## Part 1: plug-in microcontroller modules

### HackOS port effort key
- **Same:** the existing `thumbv7em-none-eabihf` build, with existing i.MX RT1062 board support.
- **Same ISA, new BSP:** the Cortex-M7 target is unchanged, but the clocks, pins, LPSPI and LPUART drivers need redoing for a different chip family.
- **New port:** a new compiler target (`thumbv8m.main-none-eabihf` for M33, `riscv32imafc` for ESP32-P4) plus a full BSP.

### Comparison table

| Module | Chip / core | HackOS | Clock | On-chip RAM | Ext. RAM on module | Flash | Wireless | Display I/F | SD | USB | Size (mm) | Mounting, stack on carrier | Active / sleep current | Price, stock (2026-11-27) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **PJRC Teensy 4.1** | NXP i.MX RT1062 (MIMXRT1062DVJ6B), Cortex-M7 [P] | **Same** (existing target) | 600 MHz [P] | 1 MB (512K TCM + 512K OCRAM) [P] | **none fitted**. Pads for 1-2 x 8 MB QSPI PSRAM (APS6404L), so 8 or 16 MB; a 16 MB chip (COM-29556) is also offered [P] | 8 MB [P] | none. 10/100 Ethernet PHY (DP83825) fitted [P] | LPSPI x3, FlexIO; RT1062 has LCDIF but its pins are not broken out on Teensy [E]. SPI e-ink is fine | micro-SD socket, 4-bit SDIO [P] | device 480 M + host port (5 pins) [P] | 61 x 17.8 (2.4 x 0.7 in) [P SparkFun] | 0.1 in through-hole pins, not castellated. Lying flat on short pins: about 4-5 mm above the carrier (PCB plus USB-B/SD socket); on sockets 8-11 mm [E] | ~100 mA at 600 MHz (PJRC states this for 4.0) [P]. Chip-only RT1060 figures from NXP AN12245 at 3.3 V are in the RT1062 power section below [P]. Teensy "off" (VBAT/RTC): 84-96 uA [S forum] | SparkFun DEV-16771 **$31.50, in stock** [P]. Adafruit has discontinued Teensy; SparkFun is now the exclusive maker and seller [P Adafruit page + blog] |
| **PJRC Teensy 4.0** | RT1062 (DVL6B), Cortex-M7 [P] | **Same** (new pin map only) | 600 MHz [P] | 1 MB [P] | none, no PSRAM pads | 2 MB [P] | none | LPSPI, FlexIO | SDIO on 8 bottom pads, no socket [P] | device + 2 host pads [P] | 35.6 x 17.8 (1.4 x 0.7 in) [P SparkFun] | through-hole pins plus bottom pads; flat about 4 mm [E] | ~100 mA at 600 MHz [P] | SparkFun DEV-15583 **$23.80, in stock** [P] |
| **SparkFun MicroMod Teensy Processor** | RT1062, Cortex-M7 [P] | **Same ISA, small BSP delta** (same chip, different pin map, 16 MB flash) | 600 MHz [P] | 1 MB [P] | none | 16 MB [P] | none | 2 x SPI, I2S [P] | 1 SDIO port to carrier [P] | host + device 480 M [P] | 22 x 22 (M.2 2222) [S SparkFun learn] | M.2 MicroMod (E-key) connector, 4.2 mm standard height, screw plus reflowable standoff. About 6 mm above the carrier [S/E]. A lower connector is possible but not standard | not published; about the same as Teensy [E] | SparkFun DEV-16402 **$24.95, in stock** [P]. Carrier needs an M.2 connector and standoff |
| Embedded Artists iMX RT1176 uCOM | i.MX RT1176, Cortex-M7 1 GHz + M4 400 MHz [P] | Same ISA, **new BSP** (RT117x clocks, PMU and LPSPI differ) | 1000/400 MHz [P] | 2 MB [P] | 32 MB SDRAM [P] | 16 MB QSPI [P] | optional Murata 1XK/1ZM [P] | **MIPI DSI**, plus LCDIF on the chip [P] | 2 x SD 3.0 [P] | 2 x HS OTG [P] | 42 x 45 [P] | 2 x DF40C-100 + 2 x DF40C-40 board-to-board connectors. Mated 1.5-4 mm (DF40 family) plus module, so about 4-6 mm [E] | not stated [P] | **Maker: "Request a Quote" only** [P]. Mouser EAC00381 (IT version) about INR 10,656 (~$125), 3 in stock [S snippet]. Dev kit 239 EUR [P] |
| Embedded Artists iMX RT1064 uCOM | RT1064, Cortex-M7 600 MHz [P] | Same ISA, small BSP delta (RT1064 = RT1062 + 4 MB in-package flash) | 600 MHz | 1 MB [P] | 32 MB SDRAM [P] | 4 MB on-chip [P] | optional Murata 1XK [P] | parallel RGB [P] | yes | yes | 42 x 45 [P] | 2 x DF40C-100 [P] | not stated | **quote only** [P]. Kit 269 EUR |
| Embedded Artists iMX RT1062 OEM | RT1062 528 MHz [P] | Same ISA, small BSP delta | 528 MHz | 1 MB | 32 MB SDRAM [P] | 16 MB QSPI [P] | none [P] | parallel RGB [P] | 2 x uSDHC [P] | 2 x HS OTG [P] | 68 x 30 [P] | 200-pin SODIMM, so about 5+ mm and too tall [E] | not stated | **quote only** [P]. Kit 169 EUR |
| OpenMV Cam RT1062 (camera board, not a module) | RT1062 600 MHz [P SparkFun] | Same ISA, new pin map | 600 MHz | 1 MB [P] | 32 MB SDRAM [P] | 16 MB [P] | Wi-Fi [P] | SPI etc. | yes | yes | ~36 x 45 with lens [E] | pin headers | idle 100 mA, active 130 mA at 5 V [P SparkFun]; deep sleep ~30 uA [S OpenMV docs] | SparkFun SEN-25035 $150, page says both "In stock" and "Backorder" [P]. Too expensive and bulky |
| Arduino Portenta H7 (ABX00042) | STM32H747XI, Cortex-M7 480 MHz + M4 240 MHz [P] | Same ISA (M7 is `thumbv7em-none-eabihf`), **new BSP** (all-ST peripherals) | 480/240 MHz [P] | 1 MB [chip, E] | 8 MB SDRAM [P] | 16 MB QSPI NOR [P] | Murata 1DX Wi-Fi + BT [P] | 2-lane **MIPI DSI** on the HD connector; DisplayPort over USB-C [P] | yes (SDMMC) | USB-C HS [P] | 66.04 x 25.40 (MKR) [S] | 2 x 80-pin Hirose HD connectors underneath, so about 3-5 mm mated plus parts on top; also MKR headers [P/E] | deep sleep **0.67 mA** at 3.7 V; max 230 mA at 5 V [P datasheet] | Arduino store **EUR 78.51** (sale, list EUR 120.80), "Add to cart" shown, no stock count [P] |
| Arduino Portenta H7 Lite (ABX00045) | STM32H747XI [P datasheet] | as above | 480/240 | 1 MB | 8 MB SDRAM [P] | 16 MB QSPI [P] | **none** [P] | MIPI DSI [P] | yes | yes | same as H7 | same as H7 | similar to H7 [E] | store and Mouser not readable **[NR]** |
| Electro-Smith Daisy Seed (STM32H7 board) | STM32H750IB, Cortex-M7 [S PlatformIO] | Same ISA, new BSP | 480 MHz [P] | 1 MB [chip, E] | **64 MB SDRAM** [P] | 8 MB QSPI [S] | none | SPI, no LCD pins | SD interface [P] | micro-USB + OTG pins [P] | 51 x 18 [P drawing] | 2 x 20 0.1 in through-hole pins; 8.4 mm tall in the drawing with headers [P] | not published | **[NR]** (store 429) |
| Raspberry Pi Pico 2 W | RP2350, 2 x Cortex-M33 or 2 x Hazard3 RISC-V [P] | **New port** (ARMv8-M or RISC-V) | 150 MHz [P] | 520 KB [P] | **none** | 4 MB [P] | CYW43439 Wi-Fi + BT 5.2 [P] | SPI, 12 PIO state machines [P] | via SPI/PIO only | USB 1.1 host/device [P] | 51 x 21 x 1 mm PCB, single-sided [P] | **castellated, solders flat** [P]. Antenna keep-out needed. About 3-4 mm total incl. RP2350 and RM2 can [E] | Pico 2 (non-W) at 5 V VBUS: low-power states P1.x **148-233 uA**, RUN low 388 uA, CoreMark 9.4 mA, hello_usb 12.7 mA [P Pico 2 datasheet] | **Out of stock**: Adafruit 6087 $7.00, SparkFun DEV-27345 $7.70, PiShop SC1633 $7.00 [P] |
| Pimoroni Pico Plus 2 W | RP2350B, M33/RISC-V [S] | New port | 150 MHz | 520 KB | **8 MB PSRAM** [S] | 16 MB [S] | RM2 module (CYW43439) [S] | SPI, PIO | via SPI/PIO | USB-C | 53 x 21 x 8.3-9 (incl. connectors) [S] | Pico footprint, castellated [S] | not read | Pimoroni **[NR]** (429). Sibling Pico Plus 2 (no Wi-Fi) is out of stock at Adafruit [P] |
| Waveshare ESP32-P4-Module | ESP32-P4NRW32X, 2 x RISC-V HP 400 MHz + LP core [P] | **New port** (RISC-V) | 400 MHz [P] | 768 KB HP SRAM + 8 KB TCM [P Espressif] | **32 MB PSRAM in package** [P] | 16 or 32 MB [P] | ESP32-C6 (Wi-Fi 6, BT 5) companion on the module [P] | **MIPI DSI**, parallel RGB [P Espressif] | SDIO 3.0 host [P] | USB 2.0 HS OTG [P] | 25 x 25 [P] | castellated, 1 mm pitch, 88 pads, solders flat, about 3 mm [P/E] | chip only, 3.3 V [P datasheet]: 400 MHz dual-core while loop 69-112 mA; 40 MHz 19-37 mA; light sleep 0.075-0.8 mA; **deep sleep 12 uA**; off 1 uA | Waveshare $9.99-$10.99, stock not shown [P] |
| Other RT117x/RT106x SoMs (TQ TQMa117xL LGA, Somlabs VisionSOM SODIMM, Forlinx/MYIR) | RT1170/RT1060 | Same ISA, new BSP | | | SDRAM | | | | | | | LGA (solder-down) or SODIMM | | quote or distributor only; not pursued [S] |

### RT1062 power, chip-level (NXP AN12245, RT1060 EVK, 3.3 V, 25 C) [P]

DCDC_IN + VDD_HIGH_IN, code in RAM:

| Mode | Current |
|---|---|
| 600 MHz overdrive | 73.6 mA |
| 528 MHz | 58.7 mA |
| 132 MHz | 18.2 mA |
| 24 MHz low-power run | 3.0 mA |
| System Idle | 10.9 mA |
| Low-Power Idle | 1.59 mA |
| Suspend | 0.24 mA |
| SNVS only | 0.016 mA |

The Teensy board adds its 3.3 V regulator, flash and LEDs. The Teensy 4.1 also adds the Ethernet PHY, which must be held in power-down. The Teensy On/Off pin can drop to SNVS: the e-ink keeps its image, and a key press wakes it with a cold boot.

**What "days of runtime" needs [E]:** at 600 MHz the board draws about 100 mA, about 10 h per 1000 mAh. For days, HackOS should:
- drop to 24-132 MHz while typing,
- use Low-Power Idle (about 2-3 mA at board level, [E]) between key presses,
- go to SNVS/off when idle for a while.

This is a firmware task, not a module choice. The ESP32-P4 and RP2350 have better documented sleep, but both need a new port.

### Recommendation

**Best: PJRC Teensy 4.1 (SparkFun DEV-16771, $31.50, in stock).**
- **HackOS effort:** zero. HackOS already has a Teensy 4.1 build target and runs on the same Cortex-M7 target as QEMU.
- **Memory:** 1 MB SRAM is plenty for an SPI e-ink framebuffer (a 320x240 1-bpp frame is 9.6 KB; 2-bpp is 19.2 KB). 8 MB flash, plus one or two solder-on PSRAM chips (8 or 16 MB) if HackOS wants a heap or file cache.
- **Storage:** the micro-SD socket is already fitted.
- **Display:** LPSPI suits UC8253/SSD1685 panels.
- **Fit:** 17.8 mm wide, so it fits between or under the two thumb-keyboard halves.
- **Risks:**
  - Single source. SparkFun is now the only maker and seller, and Adafruit has dropped it.
  - No wireless.
  - Through-hole pins, not castellated, so flat mounting means about 4-5 mm stack [E] with short pins or soldering the pads to the carrier.
  - The Ethernet PHY costs power unless held in reset. SparkFun lists no "NE" variant.
- **If thinness beats SD and PSRAM:** the Teensy 4.0 (35.6 x 17.8 mm, $23.80, in stock) is the same HackOS target. It has 2 MB flash and SD on bottom pads only.

**Runner-up: SparkFun MicroMod Teensy Processor (DEV-16402, $24.95, in stock).**
- Same RT1062, so only a pin-map and flash-config change in HackOS.
- 16 MB flash, 22 x 22 mm.
- A real plug-in socket (M.2), so the module can be swapped for a future MicroMod processor without redesigning the carrier.
- Costs about 6 mm stack height with the standard 4.2 mm connector, and needs the connector and standoff on the carrier.

**Not recommended now:**
- **i.MX RT1176 uCOM:** excellent (1 GHz, 32 MB SDRAM, Cortex-M7, MIPI DSI), but quote-only from Embedded Artists, with only a handful at Mouser [S]. That fails the orderable rule, and 42 x 45 mm on DF40 is overkill for an SPI e-ink.
- **Portenta H7:** same ISA and has Wi-Fi, but needs a whole new STM32 BSP, costs about EUR 79-121, and deep sleep is 0.67 mA.
- **Pico 2 W / Pico Plus 2 W:** castellated and thin, but out of stock at all three US resellers checked, and a new ISA port.
- **ESP32-P4:** best sleep figures, 32 MB PSRAM, cheap and thin, but a RISC-V port with Wi-Fi through the C6 companion. Keep it as the long-term alternative if HackOS ever gains a RISC-V target.

---

## Part 2: small e-ink panels (2.6-3.7", SPI)

Full table and sources are in `eink-notes.md`. Everything there was read from maker pages, maker datasheets or flyers, Good Display's store (buy-lcd.com; buyepaper.com redirects there), and DigiKey for PDi [P].

**Stock caveat [S/E]:** the Good Display store widget shows "0 in stock" until a variant is picked. The quantities below come from a hidden `stock` field in the page HTML ("qty"), so they are probably real but not certain.

| Part | Diag | Res / PPI | Outline W x H x T (mm) | Active area (mm) | Touch / front-light variants (thickness) | Full / partial | IC | $ / qty |
|---|---|---|---|---|---|---|---|---|
| GD GDEY0266T90H | 2.66" | 360x184 / 152 | 72.50 x 37.11 x 1.0 | 60.05 x 30.69 | none | 2 s / 0.3 s | SSD1685 (1-bit) | 5.17 / 55 |
| GD GDEY027T91 | 2.7" | 264x176 / 117 | 70.42 x 45.8 x 1.0 | 57.29 x 38.19 | -T21 touch 1.425; -FT11 touch + front light 2.1 | 3 / 0.3 s | SSD1680 | 5.93 / 59 |
| GD GDEY029T94 | 2.9" | 296x128 / 112 | 79.0 x 36.7 x 1.2 | 66.90 x 29.06 | -T01 touch 1.575; -FL03 front light 2.01; -FT01 both 2.15 (qty 0) | 3 / 0.3 s | SSD1680 | 6.24 / 39 |
| GD GDEY029T71H | 2.9" | 384x168 / 144.5 | 79.98 x 35.57 x 1.0 | 67.58 x 29.57 | none | 2 / 0.3 s | SSD1685 (1-bit) | 6.32 / 56 |
| **GD GDEY031T10** (GDEQ031T10 is end-of-life) | 3.1" | 320x240 / 129 | 73.8 x 53.24 x 0.93 | 62.72 x 47.04 | **-T21 cap touch (FT6336U, I2C), 1.526 mm, $13.59, qty 39**; no front light (custom only) | 3 / 0.4 s | UC8253, 4 grey | 10.16 / 59 |
| GD GDEM035T81 | 3.5" | 384x184 / 122 | 91.75 x 45.03 x 0.9 | 79.68 x 38.18 | none listed | 2 / 0.3 s | SSD1685 | 8.11 / 83 |
| GD GDEY037T03 (reference only) | 3.7" | 416x240 / 130 | 92.99 x 53.0 x 1.0 | 81.54 x 47.04 | -T02 touch 1.48; -FL21 front light 1.65; -FT21 both 2.125 ($16.31 / 48) | 2 / 0.3 s | UC8253 | 8.93 / 157 |
| Waveshare 3.52" | 3.52" | 360x240 / 123 | 54.41 x 84.70 x 0.87 (wiki: 80.68 long side) | 74.51 x 49.67 | none | 1.5 s / unclear | UC8253c | HAT $18.99, stock not shown |
| Waveshare 3.7" | 3.7" | 480x280 / 150 | 54.9 x 93.3 x 0.78 | 47.32 x 81.12 | none | 3 / 0.3 s | SSD1677 | HAT $28.99, stock not shown |
| Waveshare 2.9" Touch HAT | 2.9" | 296x128 | HAT 89.1 x 42.7 | 66.89 x 29.05 | built-in touch (ICNT86) | 3 / 0.3-0.6 s | n/s | $24.99, stock not shown |
| PDi E2290KS061 | 2.9" | 384x168 / 144 | 79.48 x 35.57 x 0.85 | 67.58 x 29.57 | none | fast update | PDi internal timing controller (iTC) | stock not checked |
| PDi E2340KS0G1 | 3.4" | **456x392 / 177** | 72.5 x 69.0 x 0.8 | 65.44 x 56.25 | none | fast update | iTC | DigiKey $31.82, **0 stock, 20-week lead time** |
| PDi E2370KS0C1 / TP370PGH01 | 3.7" | 416x240 / 130 | 92.99 x 53.0 x 0.85 (touch version 1.49) | 81.54 x 47.04 | P-cap touch | fast update | iTC | not checked |

E Ink does not sell these sizes direct, so it gets no row. PDi panels need PDi's own driver sequence (PDi_EPD library), not the Solomon/UltraChip command sets.

### Picks

1. **Good Display GDEY031T10 (3.1", 320x240), with the GDEY031T10-T21 cap-touch version.**
   - At 73.8 x 53.2 mm it fits the 80 mm limit in either orientation.
   - It has the most pixels of any orderable panel that fits: 76.8k, against 64-66k for the 2.9" strips.
   - The 4:3 shape gives about 13 text lines against about 7 on the strips.
   - 0.4 s partial refresh, 4 grey levels, SPI UC8253.
   - The touch version is 1.53 mm thick and costs $13.59; both versions show stock.
   - No front-light part exists at this size.
2. **Good Display GDEY029T71H (2.9", 384x168, 144.5 PPI).**
   - The sharpest panel that fits 80 mm in landscape, and only 35.6 mm tall, which leaves room for the keyboard.
   - Fastest refresh (0.3 s partial, 2 s full) and cheapest at $6.32.
   - 1-bit only, with no touch or front light. Same-outline touch (-T01) or front-light (-FL03) parts exist only at 296x128 (GDEY029T94).
   - PDi E2290KS061 is a second source with the same glass size.

**Watch:** PDi E2340KS0G1 (3.4", 456x392, 72.5 x 69 mm) is the best fit on paper but has no stock. GDEY037T03-FT21 is the only touch-plus-front-light option at this resolution, but it fits only if mounted in portrait (53 mm wide).

---

## Sources (all read 2026-11-27)

**Teensy and RT1062**
- PJRC Teensy 4.1 / 4.0 / PSRAM pages: pjrc.com/store/teensy41.html, teensy40.html, psram.html
- SparkFun DEV-16771, DEV-15583, DEV-16402, SEN-25035, DEV-27345
- Adafruit 4622 (Teensy discontinued at Adafruit), 6087, 6244; Adafruit blog 2026-01-12
- NXP AN12245 (RT1060 power): `dl/nxp/an12245.pdf`
- PJRC forum thread on T4.x RTC power [S]

**Embedded Artists**
- embeddedartists.com/products/imx-rt1176-ucom/, imx-rt1064-ucom/, imx-rt1062-oem/
- Mouser EAC00381 snippet [S]

**Portenta and Daisy**
- Arduino store ABX00042 page
- Portenta H7 datasheet: `dl/portenta/h7.pdf`
- Daisy Seed datasheet v1.0.5: `dl/daisy/seed.pdf`

**Pico and ESP32-P4**
- Raspberry Pi Pico 2 page; Pico 2 W and Pico 2 datasheets: `dl/pico/`
- Pimoroni Pico Plus 2 W specs via search snippets of the Pimoroni and CNX pages [S]
- PiShop SC1633
- Espressif ESP32-P4 page and datasheet: `dl/esp/p4.pdf`
- Waveshare ESP32-P4-Module page and wiki

**E-ink:** see `eink-notes.md`.
