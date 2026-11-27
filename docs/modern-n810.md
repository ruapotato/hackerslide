# A modern Nokia N810: what it would take (study, 2026-11-26)

**Status: under consideration, nothing decided.** David asked (2026-11-26) what a third build would take: basically
a modern replica of the N810, aiming for really good battery life, the same footprint and thickness, USB-C,
e-paper or a regular display, and a chip of about 800 MHz-1 GHz with a memory-management unit, so it runs a real
Linux kernel, without the compute module, heat and power problems of the first Linux design. The hack pad work is
kept on branch `hack-pad`; the first Linux design on `linux-handheld`.

## 1. The N810, for reference

| | Nokia N810 (2007) | Source |
|---|---|---|
| Processor | TI OMAP2420, ARM11 at 400 MHz | DeviceBeast, Wikipedia |
| Memory | 128 MB RAM, 256 MB flash, 2 GB internal storage, miniSD slot | DeviceBeast |
| Screen | 4.13", 800 x 480, resistive touch | Mobilarena |
| Radios | Wi-Fi 802.11b/g, Bluetooth 2.0, GPS; no cellular | DeviceBeast |
| Other | slide-out keyboard, D-pad, VGA webcam, stereo speakers, 3.5 mm jack | DeviceBeast; speakers and jack from memory |
| Battery | 1500 mAh | one source only, unconfirmed |
| Size, weight | 128 x 72 x 14 mm, 225-226 g | Mobilarena, DeviceBeast |

## 2. The brain: NXP i.MX 6ULL

| | |
|---|---|
| Part | MCIMX6Y2CVM08AB: Cortex-A7 at 792 MHz, industrial grade, 289-ball BGA 14 x 14 mm, 0.8 mm pitch (the same package type as the hack pad's RT1176) |
| Stock | JLCPCB 13,768 at $10.49 (read 2026-11-26) |
| Memory | external DDR3L or LPDDR2, 16-bit. One 2 Gbit DDR3L chip = 256 MB, twice the N810 (Micron MT41K128M16JT-125:K, JLCPCB 3,867, $18.51; Samsung K4B2G1646F-BYMA, 630, $13.75) |
| Has | LCD controller (parallel RGB), 2D pixel engine, 2 x USB 2.0 OTG with PHY, 2 x SD/eMMC, audio ports (3 x SAI), 4 x I2C, 4 x SPI, 8 x UART, 2 x 12-bit ADC, 2 x CAN, 2 x Ethernet (data sheet IMX6ULLCEC rev 1.3, ordering table) |
| Does not have | MIPI DSI or camera MIPI (parallel only), a GPU. The e-paper controller is only on the Y7 variants, which are out of stock; not needed, because the chosen panel has its own controller |
| 900 MHz | MCIMX6Y2DVM09AB, 0 in stock |

**Power, measured by NXP** (application note AN5345 rev 2, on NXP's evaluation board, NXP's Linux 4.1.15 kernel;
not our board and not mainline):

| State | Total | Of which the memory chip |
|---|---|---|
| Suspend to RAM | 10.7 mW | 10.1 mW (the chip itself 0.56 mW) |
| Idle, screen off | 20.6 mW | 10.8 mW |
| Benchmark at 800 MHz | 375 mW | |
| 480p video at 800 MHz | 498 mW | |

Rough battery estimate (Claude's arithmetic, not measured), for a 1950 mAh cell (7.2 Wh) and an e-paper screen
that uses nothing while still: suspended, about 2-3 weeks once charger, gauge and clock are added; typing in a
terminal or reading with Wi-Fi off, several days; with Wi-Fi in use, roughly a day. The Linux handheld with the
compute module was estimated at 3-4 hours of browsing.

**Software:** mainline Linux supports the i.MX 6ULL well, with u-boot, and suspend-to-RAM is in the mainline power
code for this family (from memory: to confirm). It runs a normal 32-bit ARM distribution, so Debian with apt is
possible. 256 MB is too little for a modern Firefox or Chromium; a light browser would work.

## 2b. If a GPU and 1 GB are wanted (David, 2026-11-26)

- **The i.MX 6ULL tops out at 512 MB in practice:** its memory bus is 16 bits wide, so one chip sets the size; a
  4 Gbit chip (512 MB) is in stock (Samsung K4B4G1646E-BYMA, 1,909 and 1,145, $12-18), an 8 Gbit one (1 GB) is not
  (Micron MT41K512M16HA, 7 at $75). No GPU.
- **A separate GPU chip is not practical.** No small GPU chips are sold on their own; the SPI graphics coprocessors
  (Bridgetek FT812/FT813) are out of stock and are 2D engines that Linux applications cannot use as a GPU.
- **The one chip with a GPU, 1 GB+ and stock: NXP i.MX 8M Mini Quad, MIMX8MM6DVTLZAA** (JLCPCB 859, $22.02):
  4 x Cortex-A53 at 1.8 GHz plus a Cortex-M4, 3D GPU (OpenGL ES 2.0 class) and a 2D GPU, MIPI DSI for LCD panels,
  hardware video decoding, 32-bit memory bus taking LPDDR4, DDR4 or DDR3L (data sheet IMX8MMCEC rev 2). 1 GB = two
  4 Gbit DDR3L chips (about $25-35); LPDDR4 is about $100 a chip with thin stock. Package: 486 balls at **0.5 mm
  pitch**, so a denser, probably 8-layer board. Mainline Linux supports it well, including the GPU through the
  open etnaviv driver (from memory: to confirm).
- **Its power, measured by NXP** (AN12410 rev 0, NXP's board with LPDDR4, NXP's 4.14 kernel): suspend 9.0 mW;
  idle 617 mW with the memory at full speed, 139 mW with the memory clock lowered; audio playback 266-673 mW;
  video about 1.1 W; GPU benchmarks 1.1-1.5 W; CPU benchmarks 1.6-1.8 W. About 7 times the i.MX 6ULL at idle and
  4-5 times at full load, but no heat problem in a pocket, and well under the compute module of the first Linux
  design.
- **Other chips with a GPU:** i.MX 8M Nano with GPU (0-21 in stock), STM32MP157 (41-60), Allwinner H616 (303,
  Mali GPU, thin documentation and weak sleep support), Allwinner A133/R818 (PowerVR GPU without a dependable open
  driver), Rockchip RK3326/PX30 (none in stock).
- **What it means for the device:** a GPU helps an LCD; with e-paper it adds little. So the choice is really
  e-paper + i.MX 6ULL (512 MB, longest battery, easier board) or LCD + i.MX 8M Mini (GPU, 1 GB, about 2.3 mm
  thicker, roughly 8-13 hours of use by Claude's arithmetic, harder board, about $200-400 more per prototype).

## 2c. Fewer layers: a solder-down module, and other low-power displays (2026-11-26, first look)

**Modules.** Stamp-hole ("castellated") modules carry the processor, memory and storage on their own small board
and solder flat onto a simple 2-4 layer main board, which then needs no BGA or memory routing. Seen so far, prices
and stock still to confirm at the distributors:

| Module | Chip | Notes |
|---|---|---|
| MYIR MYC-Y6ULX | i.MX 6UL/6ULL | 140-pin stamp-hole edge; was "from $18" at launch (old article); one variant listed at Mouser $31.25 |
| Forlinx FETMX6ULL-S | i.MX 6ULL | 44 x 35 mm stamp-hole module; price not found |
| Luckfox Core1106 | Rockchip RV1106 (memory inside the chip) | stamp-hole; $27-49 at Waveshare/Luckfox; Rockchip's own kernel rather than mainline |

In the hack pad model the strip beside the battery has 6.8 mm of height, so a module of about 3-3.5 mm would sit
there without making the device thicker. The JLCPCB parts library stocks none of these modules.

**Displays other than e-paper.**

| Display | Size, pixels | Why consider it | Against |
|---|---|---|---|
| Good Display e-paper (current choice) | 4.26", 800 x 480 | the N810's resolution, touch, front light, 1.98 mm | 0.42 s partial updates |
| Sharp memory LCD LS032B7DD02 | 3.2", 336 x 536 | microwatts when still, fast enough for scrolling and games, reflective; a Linux driver for this family was submitted to the kernel in 2024 | smaller and much lower resolution; no light of its own; DigiKey about $38, stock figures conflict |
| Sharp memory LCD LS044Q7DH01 | 4.4", 320 x 240 | N810-like size | coarse (0.28 mm pixels); JLCPCB 122 at $61 |
| Sharp memory LCD LS027B7DH01A | 2.7", 400 x 240 | the screen of the Beepy keyboard handheld (from memory) | small; DigiKey about $29, stock unclear |
| Monochrome LCD like the Flipper Zero's (ST7565-class, 128 x 64) | about 1.4" | very low power | far too small for this device |

## 3. What the board would carry

| Block | Plan | Status |
|---|---|---|
| Brain and memory | i.MX 6ULL, one DDR3L, eMMC 8-32 GB (boot and storage), microSD | DDR3L routing is the main new design risk |
| Power | USB-C, BQ25895 charger, MAX17048 gauge, discharge limiter (all from the earlier designs, all with mainline drivers); 1.35 V memory supply, 1.4 V core supply, 3.3 V buck-boost (TPS63802), from the hack pad | regulators to choose; NXP's reference designs use a power-management chip or discrete regulators |
| Display | e-paper GDEY0426T82-FT01C (4.26", 800 x 480 like the N810, touch, front light, 1.98 mm) over SPI, lid board from the hack pad; or a regular LCD on the parallel RGB port | e-paper needs a small Linux driver for its SSD1677 controller (none found yet); an LCD costs about 2.3 mm and much more battery |
| Keyboard | hack pad layout: N810 rows, Esc, Tab, D-pad, TCA8418 (mainline driver) | drawn on `hack-pad` |
| Audio | ES8316 codec, 3-pole headphone jack (from the hack pad); speaker optional | drawn on `hack-pad` |
| Wi-Fi and Bluetooth | a module with a mainline Linux driver over SDIO | to choose |
| GPS | ATGM336H over a UART | parts known from the hack pad research |
| Camera | not in the first build (the chip has a parallel camera port if wanted later) | |

Most of the hack pad's sheets (power input, keyboard, card, audio, display link, lid board) carry over.

## 4. Thickness

The chip does not set the thickness; the battery, keyboard and display do. The hack pad model gives 15.4 mm with
e-paper and the battery under the board. Reaching the N810's 14 mm needs about 1.4 mm out of: the battery (4.5 mm
now: a 3-3.5 mm cell of the same area gives roughly two-thirds the capacity), the printed back cover (1.2 mm: 0.8
in metal or a thinner moulding), and the clearance over the battery (the BGA and memory chip are about 1.2-1.3 mm).
With a regular LCD instead of e-paper, add about 2.3 mm.

## 5. Cost (rough, no quote)

Parts per board about $50-80 (brain $10.49, memory $14-19, eMMC, Wi-Fi module, charger and gauge, codec,
regulators, keyboard scanner, connectors). First prototype delivered, five boards made and two assembled, about
$700-1,000; the whole effort with revisions about $1,600-2,500. To be redone properly from the schematic, as for
the hack pad (`docs/hack-pad-cost.md`).

## 6. What it would take

1. Confirm the open points above: mainline suspend and power on this chip, a Wi-Fi/Bluetooth module with a
   mainline driver in stock, regulators, eMMC, a thinner battery in stock, the memory chip's layout rules.
2. Schematic: new brain, memory and power sheets; the rest adapted from `hack-pad`.
3. Board layout: 6 layers, BGA and DDR3L; follow NXP's evaluation-board layout and hardware guide closely.
4. Software: u-boot and a device tree, a small DRM driver for the e-paper panel, keyboard and power drivers are
   already in mainline.
5. Enclosure: the hack pad model, adjusted to the chosen stack.
6. Expect two board rounds; the memory layout is the part most likely to need a second.

HackOS stays a project for the Teensy and the hack pad branch.

## 7. Smaller still: a pocket player without a keyboard (David, 2026-11-26, first look)

Same processor (i.MX 6ULL, module or chip), e-paper, no GPU, keyboard possibly dropped; the goal is the smallest,
most power-efficient pocket device that is also a good MP3 and audiobook player.

| | Pocket, 3.7" | Mini, 2.9" | N810 |
|---|---|---|---|
| Panel | Good Display GDEY037T03-FT21: 416 x 240, touch, front light (outline of the touch version 93.0 x 53.0 x 1.48 mm; reseller $17.91) | GDEY029T94-T01: 296 x 128, touch, no light (79.0 x 36.7 x 1.58 mm; reseller $10.20) | 4.13", 800 x 480 |
| Size (Claude's estimate) | about 100 x 60 x 9.5 mm | about 86 x 45 x 9 mm | 128 x 72 x 14 mm |
| Volume | about 45 % of the N810 | about 27 % | |
| Battery that fits | about 1,000 mAh (50 x 50 x 4 mm class) | about 600 mAh | |
| Controls | touch plus side buttons: power, play/pause, previous/next, volume | same | keyboard, D-pad |

Stack (estimate): back 1.0, battery 4.3 with the module beside it under the main board, main board 0.8, connectors
0.3, panel about 2.0, front 0.6 = about 9-9.5 mm. Audio: the ES8316 codec and the 3-pole jack from the hack pad,
plus Bluetooth headphones through a Wi-Fi/Bluetooth module. Rough playback estimate with a wired headset: about
0.1 W in total, so over a day of listening on 1,000 mAh; standby weeks. Panel stock, the module's size, a battery in
stock and the playback power all still to confirm. Rough cost: first prototype about $300-500 delivered.

## 8. A watch, and glasses (David, 2026-11-26, first look)

**Watch** (concept model `mechanical/src/watch.py`, render script `mechanical/render/watch_scene.py`): a case around
the Good Display GDEY0154D67 1.54" e-paper (200 x 200; outline 31.80 x 37.32 x 1.0 mm, touch version a little
thicker) comes to **35.4 x 40.9 x 9.6 mm** without lugs and buttons, about Pebble-sized. Stack: back 1.0, battery
3.8 (200 mAh class, to find), parts 1.0, board 0.8, panel with touch 1.6, cover glass 0.7, clearances and lip 0.7.

The i.MX 6ULL does not suit a watch: asleep it draws about 10 mW, which would empty a 200 mAh cell in about three
days doing nothing. A watch wants a microcontroller, and HackOS fits that:

| Brain (JLCPCB stock 2026-11-26) | Why | Audio to headphones |
|---|---|---|
| Nordic nRF5340 (7 x 7 mm, 4,079-4,325, $7.25-9.24) | Bluetooth LE Audio, very low sleep current, Cortex-M33 (HackOS needs a new target) | LE Audio earbuds only (newer models) |
| Nordic nRF52840 (7 x 7 mm, 35,199, $5.60) | the PineTime/Bangle class; Cortex-M4F, so HackOS's current target | none suitable for music |
| Espressif ESP32-PICO-V3-02 (7 x 7 mm, 2,362, $5.70) | classic Bluetooth audio, so any headphones | works with all headphones, but draws far more |

Rough life (estimate): weeks as a watch; with LE Audio streaming about a day of listening on 200 mAh; with classic
Bluetooth a few hours.

**Glasses:** e-paper cannot work in near-eye optics (it gives off no light). The realistic route is a small OLED
microdisplay (0.5-1") with a beam splitter or prism and a lens, as a clip-on module for existing glasses, driven by
a microcontroller over Bluetooth. Hard parts: the optics (focus distance, eye box, alignment), brightness outdoors,
weight balance; to be researched before any estimate.

## 9. The pocket player with a cellular modem (David, 2026-11-26, first look)

JLCPCB stock read 2026-11-26. US use needs LTE on bands 2, 4/66, 12/13 and, for T-Mobile, 71; each module's band
list still has to be read from its data sheet.

| Module | Type | Size | Stock, price | For | Against |
|---|---|---|---|---|---|
| SIMCom SIM7080G | LTE-M / NB-IoT | 17.6 x 15.7 mm | 2,559, $19.04 | microamps when idle (power-saving mode), small, cheap data plans; slow downloads are fine for audiobooks overnight | about 0.3-1 Mbit/s, no voice calls, slow to reach |
| Quectel EG912U (GL) | LTE Cat 1 | 29 x 25 mm | 280, $16.68 | about 10 Mbit/s, SMS, voice possible; listed idle 1.5 mA | under 300 in stock; US bands to check |
| SIMCom A7670 (SA/G) | LTE Cat 1 | 24 x 24 mm | 76-122, $7-12 | cheap, small | thin stock; US bands to check |
| Quectel EG25-G | LTE Cat 4 | 32 x 29 mm | 31, $40-66 | the PinePhone's modem: proven under mainline Linux with ModemManager, voice and GNSS | price, size; JLCPCB stock thin (DigiKey not checked) |

Wiring: the i.MX 6ULL's second USB port to the modem (Linux drivers and ModemManager are mainline for these
families), a nano-SIM socket (JLCPCB 1,780 at $0.26; no eSIM chip in stock), the modem's audio port to the codec
for calls, an LTE antenna (and the modem's GNSS, which most of these include). Supply straight from the battery
rail with large capacitors: transmit bursts draw several hundred milliamps to about 2 A. A 2.4 mm module fits beside
the battery under the board; the footprint grows to roughly 105-110 x 60 mm or the battery shrinks.

Cost on battery life (rough): a registered Cat 1 modem idling at 1.5-3 mA about doubles standby draw, so standby
falls from 2-3 weeks to about 1 week on 1,000 mAh; LTE-M in power-saving mode costs almost nothing. Carrier notes:
a personal prototype with a certified module generally works on T-Mobile; AT&T and Verizon are stricter about
unknown devices, and voice over LTE depends on the carrier enabling it. Selling one would need FCC and carrier
approval.

## 10. A Linux phone with a real display (David, 2026-11-26, first look)

Calls, texts and 4G data through the Quectel EG25-G (proven on mainline Linux in the PinePhone; JLCPCB stock thin,
DigiKey to check). Two levels:

| | Linux "feature phone" | Linux smartphone |
|---|---|---|
| Brain | i.MX 6ULL module (512 MB, no GPU) | i.MX 8M Mini (1-2 GB, GPU) |
| Display | 3.5-4" LCD on the parallel RGB port, capacitive touch | 5-6" phone LCD over MIPI DSI, capacitive touch |
| Software | a light phone interface (calls, texts, music, terminal, simple apps) | Phosh or Plasma Mobile (they want 2 GB or more; 1 GB is tight) |
| Board | simple main board under a solder-down module | 0.5 mm-pitch BGA, about 8 layers, or a module on board-to-board connectors (thicker) |
| Thickness (estimate) | about 9 mm | about 9-10 mm (the PinePhone, a similar design, is about 9.2 mm: from memory) |
| Battery life (rough) | standby about 2-3 weeks on 2,500 mAh; screen on about 10 h | standby similar if suspend works; screen on about 5-8 h |

Thinness comes from the layout real phones use: the board beside the battery, not under it, with the display on
top of both. Stack: display with touch and cover glass about 2.0 mm, battery about 4.0 mm, back about 0.8 mm,
frame and adhesive about 0.5 mm; a printed case adds about 1-1.5 mm.

**Certification (general information, not legal advice; to confirm with a test lab before anything is sold):**
- A certified module carries its own FCC ID and covers its radio only under its grant conditions (antenna type
  and gain, distance from the body, no other transmitters active alongside it).
- Cellular modules are normally granted for "mobile" use, 20 cm or more from people. A phone held to the head is
  "portable", so the **whole device** needs RF-exposure (SAR) testing, plus an evaluation of the modem, Wi-Fi and
  Bluetooth transmitting together. That makes a phone a whole-device certification, through a permissive change
  on the module's grant or a new FCC ID.
- The device maker is always responsible for the rest: unintentional emissions (Part 15 Subpart B), labelling
  ("Contains FCC ID ..."), and for a handset sold in the US also rules such as hearing-aid compatibility and 911.
- Carriers have their own approvals (PTCRB for AT&T and T-Mobile, Verizon's own programme). Uncertified devices
  can be refused on the network, voice over LTE most of all.
- A handful of units built for development and not sold or marketed is the usual hobby situation; selling even a
  few requires the full set above. Costs of SAR, FCC and carrier testing are typically tens of thousands of
  dollars (rough, from memory).
- In the EU the maker likewise assesses the whole device under the Radio Equipment Directive, using the module's
  reports as input.

## 11. Handset plus base station: long-range radio to a home "repeater" (David, 2026-11-26, first look)

The cellular modem (or no modem at all) lives in a stationary base; the pocket device talks to it over a long-range
licence-free radio in the 902-928 MHz band. Like a cordless phone, with miles instead of metres.

| Link | Modules | Rate | Range (typical, depends on antennas) | Calls |
|---|---|---|---|---|
| Wi-Fi HaLow (802.11ah) | Morse Micro MM6108 modules: their own MF08251/MF08651 (FCC modular approval under Part 15.247, 24 dBm), Quectel FGH100M (FCC and CE), AzureWave AW-HM593; none at JLCPCB, stock elsewhere to check | about 0.15-15 Mbit/s | about 1 km in town, more with line of sight and a roof antenna at the base (to confirm) | ordinary VoIP quality; with a SIP provider number the base needs only internet, no modem |
| LoRa | Ebyte E22-900M22S (JLCPCB 1,310, $7.37), Ai-Thinker Ra-01SH (2,960, $4.58), RAK3172 (336, $8.39); FCC status per module to check | about 0.3-20 kbit/s | 1-2 miles or more at low rates | walkie-talkie quality voice with the Codec2 codec; texts are easy; works with the Meshtastic ecosystem |

The base can be off-the-shelf: a certified LTE router or the home internet connection, plus a HaLow access point
or a LoRa node.

**Why this is easier legally (general information, not legal advice):** the base is stationary, so a cellular
modem in it stays within its "mobile, 20 cm" grant, or the base is a bought, already-certified router. The handset
holds only a Part 15 radio module with modular approval; low-power, low-duty-cycle transmitters near the body can
fall under the FCC's RF-exposure test exemptions (to confirm for the chosen power and distance). For a few units
built for personal use and not sold, FCC Part 15.23 covers home-built Part 15 devices. Selling still needs Part 15
authorization of the whole handset, but no carrier approval and likely no SAR testing, so far cheaper than a phone.

A licensed alternative: amateur radio allows home-built transmitters without certification (with a ham licence),
but forbids encryption and commercial use, so it does not suit everyday phone calls.
