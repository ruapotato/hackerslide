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
