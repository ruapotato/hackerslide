# 8 GB compute module in the CM4 form factor: research report

Read 2026-11-27. Public web only. Downloads are in `/var/tmp/hackerslide-agent/cm8/dl/`.

How each fact was sourced:
- **[P]** read from a primary page: the maker's datasheet, brief, schematic, pin list or store, a distributor page, or the torvalds/linux tree.
- **[S]** secondary: a review, news story or forum post, or a search-engine summary.
- **[E]** my own estimate or inference.

"Carrier" means the existing CM4-format carrier, with its pin use as given in `docs/compute-pin-matrix.md` on branch `hackbrain`.

## 1. Summary table

| Module | SoC / CPU / GPU | RAM | Wireless | 8 GB price (with Wi-Fi) | Stock, 2026-11-27 | Fits the carrier | Idle / load power | Suspend-to-RAM | Mainline DT | Docs | SoC lid / tallest part above carrier |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **Radxa CM4** RM126-D8E64J0R35W28 | RK3576: 4x A72 2.2 GHz + 4x A53, Mali-G52 MC3, 6 TOPS [P] | 1/2/4/8/16 GB [P] | Wi-Fi 6 / BT 5.4, Quectel FCU760K **on USB** through an on-module hub [P schematic] | **$114.99** at Arace at launch [S Liliputing]; $115 [S Notebookcheck 2025-09-06] | **Not verified.** Arace and Allnet (Radxa partners) returned 429/403 to every fetch. Evelta (IN) shows 0 for 8/64 [P, label pairing inferred]. AliExpress is marketplace only | **Yes.** Already a supported stuffing variant (R55-R59) | No module figure. RK3576 board (ROCK 4D): 2.7 W idle, about 7 W CPU stress [S] | Vendor TF-A: "suspend/resume work well" [S Flipper]. Mainline RK3576 suspend reported broken, PCIe suspend missing [S Collabora issue; 2026-03 patch cover letter]. **Must be tested** | **None** (none in 7.4-rc4). The SoC itself is well upstreamed | Schematic v1.20, pin list xlsx, STEP, DXF, placement map [P] | 3.8 / 4.4 mm with 1.5 mm stacking [P from STEP + E] |
| **Raspberry Pi CM4** CM4108000 (SC0675, Lite) | BCM2711: 4x A72 1.5 GHz, VideoCore VI [P] | 1/2/4/8 GB [P] | Wi-Fi 5 / BT 5.0 on SDIO [P] | **$160** list (brief, July 2026) [P]; DigiKey $160 [P] | **DigiKey: 631 in stock**, $160, purchase limit [P]. eMMC SKUs (SC0676/0677/0678) are 0 at DigiKey; SC0676B shows 4 | Mostly. Needs changes (power key, PWM, pin 76; see 4.2) | Datasheet: 400 mA idle (2.0 W), about 1.4 A load (7 W), 8 mA soft-off, 15 uA with GLOBAL_EN low [P]. MNT Reform laptop with CM4: 3.8 W idle (whole system) [S] | **No.** RPi kernel developer: S2R unsupported and unlikely ever [S] | **Yes:** bcm2711-rpi-cm4-io.dts [P] | Full datasheet, design guide, CM4IO KiCad [P] | 5.08 / 5.08 mm (DF40C 1.5 mm stack) [P] |
| **Raspberry Pi CM5** CM5108032 (SC1601) / CM5116xxx | BCM2712: 4x A76 2.4 GHz, VideoCore VII [P] | 2/4/8/16 GB [P] | Wi-Fi 5 / BT 5.0 [P] | **$170** (8 GB Lite CM5108000), **$205** (8/32); 16 GB **$380-415** [P brief Nov 2026] | **DigiKey: 0 for every 8 GB and 16 GB SKU**, backorders not accepted [P]. PiShop CM5108032 out of stock [P] | Mostly. Same changes as CM4 plus the pins in 3.2 | Datasheet: 400 mA idle (2.0 W), about 900 mA typical (4.5 W), budget 5 V 2.5 A; 3 mA soft-off, 1.3 mA with PMIC_EN low [P]. Geerling 2.3 W idle at the wall [S]; Tom's 2.65 W idle / 6.66 W stress [S] | **No** S2R [S]; soft-off at 3 mA, woken by PWR_Button | **No CM5 DT** (only Pi 5 bcm2712-rpi-5-b.dts) [P]; RPi kernel 6.12 needed [P] | Full datasheet (rev 2026-11-19), CM4 to CM5 white paper [P] | 4.94 / 4.94 mm (1.5 mm stack) [P] |
| ArmSoM-CM5 Pro / BPI-CM5 Pro | RK3576 (as Radxa CM4) [P] | 2/4/8/16 GB LPDDR5 or LPDDR4X [P] | Wi-Fi 6 / BT 5.3, Synaptics SYN43752 on SDIO [P] | Store range $36-199, no per-variant price [P]; launch $103 for 8/64 [S] | ArmSoM store: no out-of-stock label on "CM5 Pro 8GB/32GB WiFi" (stock count not shown); "CM5 Basic" out of stock [P] | Partly. Repo audit: no backlight PWM, no I2S mapping, debug UART on other pins | ArmSoM docs: 350 mA @ 4.0 V idle (1.4 W), 1040 mA @ 4.0 V CPU stress (4.2 W), 0.1 mA off [P] | As RK3576 | **Yes:** rk3576-armsom-cm5.dtsi [P] | Schematic, 2D, pin table (Google Drive) [P] | 4.9 mm module thickness [P]; mated about 5.2 mm [E] |
| Pine64 SOQuartz 8 GB (W) | RK3566: 4x A55 1.8 GHz, Mali-G52 2EE [P] | 2/4/8 GB [P] | Wi-Fi 5 / BT 5.0, AzureWave CM256SM [P] | **$74.99** [P] | **Pine64 store: "In stock"** [P]. Pine64 halted Linux-device production until at least mid-2027 [S], so this is remaining stock with no restock | Mostly (pin list checked, 4.4). I2S MCLK on pin 50 (HP_DET on the carrier); PWM on pin 48 unconfirmed | No figure found; same SoC as the Core3566 | Not verified | **Yes:** rk3566-soquartz.dtsi, -cm4.dts [P] | Schematic v1.1, pin list [P] | Not found |
| Radxa CM3 (RK3566) | 4x A55 [S] | up to 8 GB [S] | Wi-Fi 5 option [S] | - | Not checked | 2 CM4-compatible connectors plus a 3rd (SATA/USB3); single HDMI [S]. **Is** CM4-compatible | - | as RK3566 | **Yes:** rk3566-radxa-cm3.dtsi [P] | - | 4.7 mm thick [S] |
| Radxa CM5 (RK3588S2 / RK3582) | 4x A76 + 4x A55, G610 [P] | 4/8/16/32 GB [P] | **No wireless** in the SKU table [P] | - | Allnet 8/64 "sold out" [S] | 3 connectors, CM4-ish [P/S] | RK3588 5.9 W idle in MNT Reform [S] | RK3588 issues [S] | Yes [P] | Brief [P] | - |
| Orange Pi CM4 (RK3566) | 4x A55 [S] | 1/2/4/8 GB [S] | Wi-Fi 5 / BT 5.0 [S] | $46.9 (8/64) at launch [S] | **AliExpress/Amazon only** (marketplace) | 2x100 + extra 24-pin; pin list not public [S] | - | - | **None** [P] | Download links were empty folders [S] | - |
| Orange Pi CM5 (RK3588S) | [S] | up to 16 GB [S] | **None**; no Ethernet PHY [S] | $90 (8/32) [S] | AliExpress only | 3 connectors [S] | - | - | Yes [P] | Empty folders [S] | - |
| Banana Pi BPI-CM4 (A311D) | 4x A73 + 2x A53 [S] | **2/4 GB only** [S] | Wi-Fi 5 option [S] | - | - | - | MNT 3.9 W idle [S] | - | - | - | - |
| Banana Pi BPI-CM6 (SpacemiT K1, RISC-V) | 8x X60 [S] | 8/16 GB [S] | Wi-Fi 5 / BT 4.1 [S] | $67 [S] | Banana Pi store [S] | "Most CM4/CM5 carriers" [S] | - | - | - | - | - |
| Milk-V Mars CM (JH7110) | 4x U74 1.5 GHz [S] | up to 8 GB [S] | option [S] | $84 at launch (2023) [S] | Not checked | 1 HDMI [S] | - | - | - | - | - |
| Seeed reComputer RK3576 module | RK3576 [S] | 4/8 GB [S] | Wi-Fi 6 / BT 5.4 [S] | $280.74 (openelab) [S] | Mouser non-stocked [S]; DigiKey lists only its IO board (0, 18-week lead) [P] | "Works on CM4 IO board" [S] | - | - | - | No public pin list found | - |
| Geniatech XPI-3576-CM5 | RK3576 [S] | 4/8/16 GB [S] | Wi-Fi 6, AP6275S [S] | not published | B2B only [S] | CM5 pin-out, mostly [S] | - | - | - | Not public [S] | - |
| LuckFox Core3576 | RK3576 [S] | 4/8 GB [S] | - | $66.99 [S] | - | **Not CM4: 260-pin SO-DIMM** [S] | - | - | rk3576-luckfox-core3576.dtsi [P] | - | - |

Notes:
- **Raspberry Pi prices.** Rise on 2026-02-02 (+$30 for 8 GB, +$60 for 16 GB, CM4 and CM5 included) [P], then +$40 on 16 GB CM5 in Nov 2026 [S]. DigiKey 16 GB CM5: $377-418, all 0 stock [P].
- **Mouser.** Every fetch timed out or met a bot challenge, so I could not read it.
- **Radxa CM4 availability.** Radxa guarantees the module to at least September 2035 [P brief].

## 2. Performance
- CM5 against CM4: "2-3x faster" (Geerling) [S].
- MNT Reform module benchmarks [S]:
  - sysbench single/multi: CM4 1472 / 5835, RK3588 2455 / 13507.
  - glmark2 1080p: CM4 102, RK3588 1764.
- RK3576: the same A72 core as BCM2711 but at 2.2 GHz instead of 1.5, plus 4x A53. That should put it clearly above a CM4 and somewhat below a CM5 on CPU [E]. Its Mali-G52 MC3 runs on Panfrost in mainline Mesa.
- RK3566 (SOQuartz, Core3566) is the slowest here.

## 3. Raspberry Pi compatibility details

### 3.1 CM4 in this carrier
Pins as the CM4 datasheet gives them:
- **5 V in** on 77-87 (odd pins).
- **3.3 V and 1.8 V outputs** on 84/86 and 88/90, 600 mA each [P].
- **GPIO_VREF (pin 78)** must be tied to 1.8 V or 3.3 V [P].
- **Pin 99 is GLOBAL_EN.** Driving it low switches the module off (15 uA) with no OS shutdown [P].
- **Pin 92 is RUN_PG**, a reset.
- **Pins 80/82 (SCL0/SDA0)** are GPIO44/45, the firmware/DSI1 I2C bus [P].
- **Pins 35/36** are GPIO1/0, the HAT EEPROM bus.
- **SD pins** exist only on Lite modules [P].
- **DSI1**, 4 lanes, is on 175-196 [P].

### 3.2 CM5 pin changes from the CM4
From CM5 datasheet Appendix B and white paper RP-008924 [P]:

| Pin | CM4 | CM5 | Matters here? |
|---|---|---|---|
| 16 | SYNC_IN | Fan_tacho | no |
| 19 | Ethernet nLED1 | Fan_PWM | no |
| **76** | Reserved | **VBAT** (RTC battery, a few uA load) | **yes:** the carrier puts SD-detect on 76 |
| **92** | RUN_PG | **PWR_Button** (short press: wake or shut down; long press: forced off) | **yes:** the carrier's reset net becomes the power button |
| 93 | nRPIBOOT | nRPIBOOT (pulled low briefly if PWR_Button is low at power-up) | minor |
| 94 / 96 | AnalogIP1/0 | CC1 / CC2 (USB-C PD for 5 A) | leave NC |
| **99** | GLOBAL_EN | **PMIC_ENABLE** (hard off, bypasses the OS) | **yes**, as for the CM4 |
| 100 | nEXTRST | CAM_GPIO1 | no |
| 104 / 106 | Reserved | PCIE_DET_nWAKE / PCIE_PWR_EN | no |
| 111 | VDAC_COMP | VBUS_EN for USB 3 | no |
| 128-142 | CAM0 (2-lane) | USB3-0 (134/136 are its USB 2.0 D+/D-) | no (unused) |
| 157-171 | DSI0 (2-lane) | USB3-1 (163/165 are its USB 2.0 D+/D-) | no (unused) |

Other CM5 changes:
- MIPI0/1 are now dual-purpose 4-lane DSI or CSI, so 175-196 still carries DSI.
- Composite video and the ADC inputs are gone.
- **USB on 103/105 is DWC2 only**: no xHCI, and no USB host boot there.
- PCIe clock is no longer AC-coupled.
- On-module ESD protection on HDMI, I2C and CEC was removed.
- PCB is 1.24 mm. Mating part is now Amphenol 10164227-1001A1RLF (1.5 mm stack).
- Budget: 5 V up to 2.5 A.
- GPIO is still 1.8 or 3.3 V via GPIO_VREF.
- DRM/KMS and libcamera only [P].

## 4. What the carrier needs per module

### 4.1 Radxa CM4: smallest change
Pin-checked against Radxa pin list v1.20 [P]:
- Power 77-87, 84/86 (3.3 V), 88/90 (1.8 V), GPIO_VREF on 78 ("1.8v/3.3v input").
- DSI on 175-196, USB2 OTG on 103/105 with ID on 101.
- SDMMC0 on the SD pins with detect on 76, I2C0_M1 on 80/82, I2C6_M3 on 35/36.
- UART0 debug on 51/55, SAI2 on 25/26/27/29/49, PWM1_CH0_M2 on 48, PWRON_L on 99, RESET_L on 92, MASKROM on 93.

All of these match the existing "Radxa CM4" stuffing (R30, R33, R34, R55-R59). Nothing changes on the PCB; to check:
1. **Height.** From Radxa's STEP V1.20: PCB 1.2 mm; tallest top part 1.7 mm (the 12.2 x 13 mm Wi-Fi module); SoC 1.1 mm; bottom parts up to 1.2 mm.
   - With a 1.5 mm stack: SoC lid about 3.8 mm and tallest part about 4.4 mm from the carrier [E].
   - The model uses soc_top=3.60 and mated=4.50 (Core3566): +0.2 mm at the SoC lid, so the thermal pad gets 0.2 mm thinner.
2. **Power.** Peaks are higher than the RK3566: Flipper quotes "<1 W idle, ~4 W heavy load, 10 W TDP" [S]; ArmSoM measured 4.2 W at stress [P]. Size the 5 V boost for at least 2 A peaks [E].
3. **Wi-Fi.** It is on USB (on-module hub), not SDIO. Check its idle draw and behaviour across suspend; WL_nDisable/BT_nDisable on 89/91 can turn it off.
4. **Software.** No mainline DT. Start from rk3576-armsom-cm5.dtsi or the ROCK 4D DT, or use Radxa's vendor 6.1 kernel. Suspend has to be proven in phase 1 (vendor BL31).

### 4.2 Raspberry Pi CM4108000 (8 GB Lite, Wi-Fi)
1. **Power key (pin 99 = GLOBAL_EN).** A user button there is a hard power cut. Add a do-not-fit option to take the button off 99; only the power-path logic should drive 99, for true off.
   - Use pin 41 (PWR_KEY_N) for the OS power key.
   - Add a strap to pin 56 (GPIO3, 1.8 kOhm pull-up on-module [P]) for wake from halt. Wake-on-GPIO3 is general Pi knowledge, not re-read [E]. Pin 56 is free on the carrier.
2. **Backlight PWM (pin 48 = GPIO27).** BCM2711 has no hardware PWM on GPIO27 [E: its PWM is on GPIO 12/13/18/19/40/41/45]. Options:
   - Use pwm-gpio (software PWM).
   - Strap the backlight to GPIO12 (pin 31) or GPIO13 (pin 28), moving LCD_RST_N or TOUCH_RST_N to 48.
3. **Audio (I2S).** Pi PCM is GPIO18 BCLK (pin 49), 19 LRCLK (26), 20 DIN (27), 21 DOUT (25).
   - BCM2711 has **no I2S MCLK.** The ES8316 needs one: GPCLK2 on GPIO6 (pin 30) or GPCLK0 on GPIO4. Verify the Pi PCM strap feeds pin 30 [E].
4. **Pin 76.** Reserved on CM4, so SD-detect there does nothing. Use broken-cd, as on the Core3566.
5. **SD.** Lite modules only. CM4108000 is Lite, so the carrier's microSD is the boot device: good.
6. **I2C.** On 80/82, with a KMS DSI panel driver Linux owns the bus and touch can share it. 35/36 need force_eeprom_read=0.
7. **Display.** DSI1 on 175-189 (2 lanes) works with vc4 DSI. A Linux panel driver is needed for the chosen panel [E].
8. **Height.** The SoC lid is 5.08 mm above the carrier, +1.5 mm against soc_top=3.60. In the 15.0 mm body the 1.1 mm pad goes to about 0. That needs a back cut-out or a reworked stack [E].
9. **Power.** About 1.4 A typical operating at 5 V; a 2 A boost is OK.
10. **Battery.** No suspend. Use halt (8 mA) plus a GLOBAL_EN cut (15 uA), and cold boot instead of resume.

### 4.3 Raspberry Pi CM5 (if it comes back into stock)
- Everything in 4.2, except that pin 92 is now PWR_Button. The carrier's reset button becomes a proper power button (wakes from 3 mA soft-off): an improvement.
- Pin 76 is VBAT. **Do not connect** the SD-detect pull-up there: do-not-fit option or 0 Ohm link. VBAT could take a coin cell or an always-on 3.3 V rail.
- USB on 103/105 is DWC2 only. It is fine for the RP2040 HID; otherwise use USB3-0's USB 2.0 pair on 134/136.
- Boost for 5 V 2.5 A [P].
- SoC lid 4.94 mm (+1.34 mm).
- PWM, MCLK and I2C as for the CM4 (RP1 PWM is on GPIO12-15/18/19 [E, not re-read]).

### 4.4 Others
- **ArmSoM-CM5:** per the repo's 2026-11-24 audit (not re-verified today), it needs R35/R36. It has no PWM on 48 (PWM is on 41) and no I2S mapping, so it needs new straps for PWM and audio, and a debug UART on 54/56.
- **SOQuartz:** pin list v1.0 [P].
  - I2S1_M1 is on 25/26/27/49 with **MCLK on pin 50** (carrier HP_DET).
  - Pin 99 is PMIC_PWRON (matches), 92 is RESETn, UART2 is on 51/55, I2C1 is on 80/82, I2C3 is on 35/36.
  - DSI1 is on 175-196, and GPIO_VREF supplies VCCIO6.
  - Pin 48 is GPIO4_A0; PWM is unconfirmed.

## 5. Recommendation

**Best: Radxa CM4, 8 GB / 64 GB with Wi-Fi 6 (RM126-D8E64J0R35W28), about $115 at launch.**
- It is the only 8 GB module the carrier already supports pin for pin, with no PCB change.
- It is within 0.2 mm of the height budget (measured from Radxa's STEP).
- It is clearly faster than the RK3566: 4x A72 at 2.2 GHz plus 4x A53.
- Power is much lower than the CM5's: 1.4 W idle and 4.2 W stress measured by ArmSoM on the same SoC.
- Full schematic, pin list and 3D model are published; availability is guaranteed to 2035.
- Open items:
  - **Stock was not verified.** Arace and Allnet blocked automated reads, and Evelta shows 0 for 8 GB. Confirm stock at an approved Radxa partner before committing; AliExpress is a marketplace.
  - No mainline DT.
  - Wi-Fi on USB.
  - Suspend needs a phase-1 test.

**Runner-up: Raspberry Pi CM4108000 (CM4 Lite, 8 GB, Wi-Fi), $160.**
- It is the only 8 GB CM4-format module confirmed in stock at an authorized distributor: DigiKey, 631 units, 2026-11-27.
- It has the best documentation and a mainline DT, and its Lite SD pins suit the carrier's microSD.
- Costs: it is the slowest 8 GB option, it has **no suspend-to-RAM**, and its SoC is 1.5 mm taller.
- Carrier changes are those in 4.2.

**Not chosen:**
- **CM5 8/16 GB.** Fastest, but 0 stock at DigiKey and PiShop; highest power; no suspend; 16 GB costs $380+.
- **SOQuartz 8 GB.** In stock and mainline, but end-of-stock and as slow as the Core3566.
- **Orange Pi CM4/CM5.** Marketplace-only and undocumented.
- **Radxa CM5, Orange Pi CM5.** No wireless.
- **BPI-CM4.** Only 4 GB.
- **Seeed and Geniatech RK3576 modules.** Non-stocked or B2B only.
- **LuckFox Core3576.** SO-DIMM, not CM4.
- **RISC-V modules.** Weaker GPU and Linux support.

## 6. Sources
- CM5 datasheet, rel. 4, 19/11/2026: https://datasheets.raspberrypi.com/cm5/cm5-datasheet.pdf [P]
- CM4 datasheet, 30/06/2026: https://datasheets.raspberrypi.com/cm4/cm4-datasheet.pdf [P]
- RP-008924 "Transitioning from CM4 to CM5" [P]
- CM5 brief DS-10 (Nov 2026); CM4 brief DS-8/9/10 (July 2026), on pip-assets.raspberrypi.com [P]
- https://www.raspberrypi.com/news/more-memory-driven-price-rises/ (2026-02-02) [P]
- https://www.cnx-software.com/2026/11/03/when-will-this-stop-the-raspberry-pi-5-16gb-sbc-now-sells-for-385/ [S]
- DigiKey searches and product pages: SC0675, SC0678, SC1601, 8 GB and 16 GB searches [P]
- PiShop CM5108032 [P]
- Radxa CM4: brief rev 1.1, schematic v1.20, pin list v1.20, STP v1.20 (dl.radxa.com); github.com/radxa-docs/docs [P]
- CNX Radxa CM4 2025-09-05 [S]; Notebookcheck [S]; Liliputing [S]; Evelta [P]
- https://docs.armsom.org/armsom-cm5 [P]; armsom.org/product-page/cm5 [P]; CNX BPI-CM5 Pro [S]
- pine64.com SOQuartz 8 GB [P]; wiki.pine64.org SOQuartz and pin list ods [P]; Pine64 production halt (Tom's Hardware, Hackster) [S]
- torvalds/linux master (7.4-rc4) dts listing via the GitHub API [P]
- Jeff Geerling CM5 [S]; Tom's Hardware CM5 review [S]; MNT community module benchmarks [S]; LinuxLinks ROCK 4D [S]
- https://docs.flipper.net/one/cpu-software/rk3576-mainlining (2026-06-10) [S]
- Collabora RK3576/RK3588 suspend issue (unreadable; from a search summary) [S]
- openSUSE bug 1212877 (RPi S2R) [S]
- Radxa CM5 brief rev 1.3 [P]
- CNX Orange Pi CM4/CM5, Geniatech XPI-3576-CM5, BPI-CM6, Radxa CM3 [S]
