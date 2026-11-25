# HackerSlide 810: handoff notes (2026-11-24)

> **Superseded in part.** These notes describe the first build-out. A design audit followed the same day
> ([audit-2026-11-24.md](audit-2026-11-24.md)); the current state and the decisions taken since are in
> [audit-status.md](audit-status.md). Sections 2 (how to regenerate) and 9 (sources) are still accurate.

These notes are for whoever picks up the rev 0.1 hardware build-out next. They assume you have read none of
the earlier work. The original brief asked for docs, three KiCad boards, a parametric enclosure, renders and a
sourced BOM. **About half of that exists.** This file lists what is done, what is still draft, how to
regenerate everything, and what we found that changes the original plan.

Nothing in this repository has been built, fabricated or tested.

---

## 1. Status by deliverable

| Deliverable | State | Notes |
|---|---|---|
| `LICENSE` (AGPL-3.0), `README.md` | Done (README is a stub) | README still needs the status, renders and "how to help" sections |
| `hardware/scripts/` generator | Done, working | Netlist as Python, then KiCad 9 schematic + PCB. See section 2 |
| `hardware/lib/` (symbols, footprints) | Done, **footprints need a human check** | Drawn from datasheet dimensions by `mklib.py`. `SOURCES.md` (source + license per item) not written yet |
| `hardware/carrier/` | **DRAFT - NEEDS HUMAN REVIEW** | Schematic complete. ERC clean. Parts placed, **not routed** (449 unrouted connections). DRC: rules clean (silkscreen warnings only), schematic parity clean |
| `hardware/keyboard/` (Alps SKSWCFE010 variant) | **DRAFT - NEEDS HUMAN REVIEW** | ERC clean. Parts placed. At handoff a Freerouting run was in progress but had not finished; the committed board is **unrouted** |
| Keyboard, Keystone 5135 dome variant | Not generated | Run `keyboard_design.py dome ../keyboard-5135` + `keyboard_pcb.py dome ...` (support is in the code, but it has never been run) |
| `hardware/keyboard-topplate/` | Done (mechanical PCB) | ERC/DRC clean (silk warnings: 0.6 mm Fn legends are below JLC's 0.8-1.0 mm recommendation) |
| Gerbers, drill, pick-and-place, JLC BOM exports | **Not done** | Wait until routing is done and reviewed |
| `mechanical/src/` (CadQuery) | Done, fit-mule level | `config.py` drives every dimension. Collision check passes with the device closed and open |
| `mechanical/stl/`, `step/`, `renders/` | Done | Renders: closed, open, exploded, section through the SoC, open with the front shell hidden |
| `docs/` (requirements, architecture, decision records, pin matrix, power budget, thermal, carrier-board, keyboard, enclosure, bring-up, risks, open questions, roadmap) | **Not written** | The findings that belong in them are summarised in sections 5-8 below. Write them from these notes |
| `bom/bom.csv`, `purchasing.md`, `fab-orders.md` | **Not written** | The `LCSC` and `MPN` fields are already on every schematic symbol, and the prices checked so far are in section 6 |
| Board renders (KiCad 3D) | Not done | `kicad-cli pcb render` should work headless |

There are 13 `TODO(verify)` markers in the sources: `grep -rn "TODO(verify)" hardware mechanical`.

---

## 2. How to regenerate everything

### Tools used

| Tool | Version | Used for |
|---|---|---|
| KiCad (`kicad-cli` + the `pcbnew` Python module) | 9.0.2, with the KiCad 9 symbol/footprint/3D libraries | schematics, PCBs, ERC/DRC |
| Python | 3.13 | everything |
| CadQuery | 2.8.0, in a venv | enclosure |
| OpenSCAD | 2021.01 | PNG renders, through `xvfb-run` |
| Freerouting | **2.1.0** jar (newer jars need Java 25) | optional autorouting |
| Java | OpenJDK 21 | Freerouting |

On Debian trixie: `apt install kicad kicad-symbols kicad-footprints kicad-packages3d openscad xvfb python3-venv default-jre`.

```sh
python3 -m venv .venv && .venv/bin/pip install cadquery openpyxl scikit-image scipy pillow
```

(scikit-image, scipy and pillow are for `hardware/scripts/gridroute.py`, the grid router added on 2026-11-24.)

The KiCad scripts run with the **system** `python3`, because that is where the `pcbnew` module lives. Only the
enclosure needs the venv.

### Boards (order matters)

```sh
hardware/scripts/build_all.sh          # mklib -> keyboard sch+pcb -> carrier sch+pcb -> top plate, then ERC/DRC
# with autorouting (slow, overwrites the tracks):
ROUTE=1 FREEROUTING_JAR=/path/to/freerouting-2.1.0.jar hardware/scripts/build_all.sh
```

The individual steps:

1. `mklib.py` writes `hardware/lib/hackerslide.kicad_sym` and `hackerslide.pretty/`.
2. `<board>_design.py` writes the schematic, the project/library tables and `netlist.json`. kigen generates
   deterministic UUIDs, so the diffs stay small.
3. `<board>_pcb.py` places the footprints with pcbnew and saves `.kicad_pcb`, then writes the design rules and
   net classes into `.kicad_pro`.
4. `check.sh DIR NAME OUTDIR` runs ERC, then DRC with `--schematic-parity`, and prints a summary.

**Important:** these boards are generated from code. Once a human starts routing or editing a board in the
KiCad GUI, stop running its generator, or the hand edits will be overwritten. From then on, edit the KiCad
files directly. The design scripts are still the most readable record of the circuit intent.

kigen's schematic style puts a global label on every pin, so the sheets read as netlists rather than drawings.
They are correct (the KiCad netlist export matches the generator netlist exactly) but not pretty. A reviewer
may want to redraw the key sheets by hand.

### Enclosure and renders

```sh
cd mechanical/src
../../.venv/bin/python hackerslide.py     # parts -> ../stl ../step, scene STLs -> ../renders/scene, ../collision-report.json
python3 render.py ..                      # PNGs via OpenSCAD under xvfb-run (private displays :391-:399)
```

---

## 3. Known issues and next steps (in order)

1. **Write `docs/`** from sections 5-8: one decision record per section-3 decision (including the rejected
   options), `compute-pin-matrix.md`, `open-questions.md` and the rest. The community-review video depends on
   these.
2. **Write `bom/`**: generate `bom.csv` from the `LCSC`/`MPN` symbol fields, re-query every price, and record
   the URL and the date checked. JLCPCB's parts search is a public JSON endpoint:
   `POST https://jlcpcb.com/api/overseas-pcb-order/v1/shoppingCart/smtGood/selectSmtComponentList` with body
   `{"keyword": "C80200", "currentPage": 1, "pageSize": 5}`. It needs no account.
3. **Replace the display panel** (the Focus panel is NRND and out of stock, see section 5). The carrier display
   sheet, the panel FPC pinout and the enclosure panel envelope all follow from that choice.
4. **Footprint review against the drawings**: the DF40 socket (its geometry is copied from the Raspberry Pi
   CM4IO footprint, and module pad positions were verified numerically against the CM4 drawing), the Keystone
   5135 dome pattern (not verified), the Sunlord inductors, and the TPS61230/ES8316 thermal pads.
5. **Carrier fixes before routing:** add the two corner notches for the body screws (the enclosure model
   assumes 4.6 mm notches at the carrier corners on the KiCad x=0 side; the PCB does not have them yet). Move
   the microSD connector J7 down to clear the top notch. Choose a TRRS jack with a detect switch. Move the
   hall sensor U10 or use a larger magnet: it is about 10 mm from any tray magnet, which is too far for a
   DRV5032. Decide on the SD_PWR_ON load switch.
6. **Route the carrier by hand**, or autoroute and then fix it by hand. Route DSI (100 ohm differential) and USB
   (90 ohm differential) on a verified JLC stackup. The net-class widths and gaps now in `carrier_pcb.py` are
   placeholders. Escape the DF40 0.4 mm-pitch pads carefully. Keep the 5 V boost and charger loops tight.
7. **Route the keyboard**, generate the dome variant, then export Gerbers and JLC CPL/BOM for all three boards.
8. **Enclosure:** snap hooks on the battery side (only two screws exist, on the module side), a cable path
   for the keyboard FFC service loop through the slider, a copper shim pocket under the SoC, and button
   actuators.
9. README with renders, then the community-review video material.

---

## 4. Decisions reserved for David (raise them, do not decide them)

- **License additions**: whether to add CERN-OHL-S-2.0 for the hardware alongside AGPL-3.0. Not done; ask him.
- **Any change to a section-3 decision.** Where we found a problem, the carrier implements a proposal (marked
  in the code) and it is listed in section 5 for his approval. This applies to: the carrier codec instead of
  RK809 audio, the USB hub, and battery-beside-module.
- **Body thickness**: the model comes out at **21.0 mm** with a 3000 mAh-class 7.5 mm cell beside the module.
  About 18.4 mm is possible with a 5 mm cell (roughly 1800-2000 mAh). About 26 mm results if the battery is
  stacked under the module as section 3.7 describes. `config.BATTERY` and `config.BATTERY_LAYOUT` switch
  between these.
- **Spending**: nothing has been bought or quoted. The purchasing list is a document to write; David orders.

---

## 5. Findings that change or question section 3 of the brief

1. **3.5 Audio: the RK809 codec is not on the CM4 connector.** No CM4-format module exposes codec pins (Core3566
   datasheet ch.4; CM4 datasheet). The carrier therefore has its own codec: Everest **ES8316** over I2S, with a
   mainline driver (`snd-soc-es8316`, as used in the Pinebook Pro). The I2S pins differ between modules
   (Core3566 I2S3_M1, Radxa CM4 SAI2 on the Pi PCM pins, and ArmSoM SAI pins that differ again), so the carrier
   has 0-ohm straps: R50-R54 fitted for Core3566, R55-R59 DNP for CM4-PCM/Radxa. ArmSoM-CM5 audio is not
   supported in rev 0.1. Alternative to discuss: a USB audio codec on the hub, which works with any module but
   uses more power.
2. **3.2 Display: the Focus LCDs E43GB-I-MW405-C is "Not Recommended for New Designs" and out of stock** on
   focuslcds.com ($66.86, checked 2026-11-24). DigiKey says it is "no longer available". That conflicts with
   the every-part-in-production rule. Its specs (ILI9806E, which has a mainline panel driver; GT911 touch;
   2-lane DSI; 20-pin + 8-pin 0.5 mm FPCs; 8-LED backlight at 12.8 V) were used for the draft. The datasheet
   also contradicts itself: 40 mA typical backlight current versus 30 mA absolute maximum. The draft drives
   20.4 mA. Waveshare 4.3" DSI: it is controlled through an I2C MCU at 0x45 (a Pi-touchscreen-style bridge).
   Nothing found shows it working on RK3566, so treat it as a risky prototype option.
3. **3.1 Module:**
   - The LuckFox Core3566 is now **$77.99-125.99** (luckfox.com, 2026-11-24), up from $55.99-126.99.
   - Its Wi-Fi has no onboard antenna: a U.FL antenna is needed (one is included with the Wi-Fi SKU).
   - There is no mainline device tree for the Core3566. LuckFox's datasheet says DSI supports "only official
     displays".
   - Mainline alternatives worth adding to the decision record: **BigTreeTech CB2** (RK3566, CM4 form factor,
     mainline DT) and **LuckFox Core3576** (mainline DT; form factor TODO(verify)).
   - The Radxa CM4 (RK3576) has an optional third connector but follows the CM4 numbering closely on the two
     main connectors.
   - ArmSoM-CM5 / BPI-CM5 Pro differs a lot in the GPIO area: debug UART on pins 54/56, pin 78 is VRTC.
   - Geniatech XPI-3576-CM5: no public pinout or price.
4. **3.3 Keyboard:**
   - Every candidate module exposes exactly one USB 2.0 port on the common pins, so a USB-HID keyboard needs
     a hub on the carrier (CH334R). A USB mux (FSUSB42) keeps USB-C usable for flashing in device mode.
   - Alternative: a TI **TCA8418** I2C keypad scanner (mainline `tca8418_keypad`, 8x10 matrix, $0.94 at JLC).
     It removes the RP2040, the flash and the hub. The carrier already routes I2C + KB_INT to the keyboard FPC,
     so both options stay possible.
   - The Alps SKSWCFE010 is stocked at JLC (C255576, $0.128 at 50, 2026-11-24), so it can be fab-assembled.
   - The Keystone 5135 is not at JLC. These domes are not soldered (they need ENIG plus Keystone 5200 adhesive
     spacer), and 7 mm domes on a 7.25 mm row pitch leave 0.25 mm between them.
5. **3.4 Power:**
   - The module takes 5 V only (4.75-5.25 V), so the carrier needs a 1S-to-5 V boost (TPS61230: 2.1 A at 5 V
     from 3.3 V) after the BQ25895. That costs about 8-10% conversion loss (estimate).
   - The BQ27441 has only 86 units at JLC. The MAX17048 (no sense resistor, mainline `max17040` driver,
     25k units in stock) is the alternative.
6. **3.7 Body:**
   - The open device comes out about **108 mm** tall, not ~100 mm, once the 3.5 mm key clearance and the tray
     end wall are kept.
   - With the keyboard closed, the back shell, which is the thermal path, is covered by the tray. Heat has to
     leave through the front and the sides.
   - A battery stacked under the module cannot meet 18-20 mm (see section 4).

---

## 6. Prices checked so far (2026-11-24; JLC = JLCPCB parts API, qty-1 price unless noted)

| Part | Source | Price | Note |
|---|---|---|---|
| LuckFox Core3566 (all SKUs) | luckfox.com | $77.99-125.99 | per-SKU mapping not shown |
| Focus E43GB-I-MW405-C | focuslcds.com | $66.86 | NRND, out of stock |
| BQ25895RTWR C80200 | JLC | $1.72 | ext. part |
| BQ27441DRZR-G1A C473397 | JLC | $5.74 | 86 in stock |
| TPS61230DRCR C139626 / TPS61169DCKR C71045 | JLC | $1.65 / $0.40 | |
| ES8316 C365735 / CH334R C4154405 / FSUSB42MUX C11355 | JLC | $0.91 / $0.49 / $0.29 | |
| DF40C-100DS-0.4V(51) C597931 (x2) | JLC | $1.05 each | 16.7k stock |
| RP2040 C2040 / W25Q128JVSIQ C97521 | JLC | $1.09 / $2.16 | flash is a basic part |
| SKSWCFE010 C255576 (x53) | JLC | $0.128 @50 | DigiKey $0.243 @100 |
| Keystone 5135 | DigiKey | $0.3635 @100 | 84 in stock |
| Jauch LP705176JS 3000 mAh 78x51.8x7.8 | DigiKey | $21.59 | active; too long to sit beside the module; no air shipping |
| Generic 755060 3000 mAh 7.5x50x60 | pishop.us | $15.95 | out of stock, no datasheet |

The JLC codes for all passives are in `hardware/scripts/parts.py` and on each symbol.

**Recomputed per-unit Wi-Fi prototype (estimate):**
- module $78-126
- panel $67-74
- carrier (about $20 of parts, plus a share of the 4-layer PCB, assembly and extended-part fees for a run of 5) $40-60
- keyboard plus top plate plus caps $30-60
- battery $16-22
- enclosure $5-20 FDM / $30-80 resin or MJF
- misc (FFC, antenna, magnets, inserts, screws) $10-20

Total: **about $250-440** (FDM) or **$275-440** (resin). The original estimates were $220-330, later
$250-380.

**R&D, re-estimated:**
- boot phase $170-230
- fit mule and slider $40-80
- keyboard, 2 revs, $150-250
- carrier, 2 revs including a second module, $500-1,000 (each 4-layer assembled run carries about 25
  extended-part fees of $3)
- looks-like build $200-300
- contingency about 20%

Total: **about $1,300-2,200** (estimate; no fab quotes were placed).

---

## 7. Compute pin matrix summary (CM4 pin numbers)

Sources: the LuckFox Core3566 datasheet, the Raspberry Pi CM4/CM5 datasheets, the Radxa CM4 schematic v1.20
(pages 21-23) and the ArmSoM-CM5 pin list (2024-04-22).

| Function | Pins used | Core3566 | Radxa CM4 (RK3576) | ArmSoM-CM5 | Note |
|---|---|---|---|---|---|
| 5 V in / 3.3 V, 1.8 V out | 77-87 odd / 84,86 / 88,90 | yes | yes | yes | |
| GPIO_VREF | 78 | VREF | VREF | **VRTC** | R30 0R, DNP for ArmSoM |
| DSI 4-lane | 175-196 (DSI1 position) | DSI1 | DSI | DSI | the only common DSI. Panel uses 2 lanes |
| USB 2.0 OTG | 101,103,105 | yes | yes | yes | the only common USB |
| SD card | 57-75 | yes | yes | yes | card detect on 76: not on Core3566 |
| I2C A (touch) | 80/82 | I2C1 | I2C0_M1 | I2C5_M3 | |
| I2C B (charger, gauge, codec, keyboard) | 35/36 | I2C3_M1 | I2C6_M3 | I2C4_M3 | |
| Debug UART | 55 TX / 51 RX | UART2 | UART0 | **54/56** | DNP straps R35/R36 for ArmSoM |
| I2S | 25,26,27,29,30,49 | I2S3_M1 | SAI2 (Pi PCM) | **other pins** | straps, see 5.1 |
| Backlight PWM | 48 | PWM14_M0 | PWM1_CH0_M2 | TODO(verify) | |
| Power button | 99 | GLOBAL_EN | PWRON_L | PWRON_L | TODO(verify) Core3566 behaviour |
| GPIOs (touch int/rst, LCD rst/TE, chg/gauge int, KB int/rst/boot, vol, slider, USB_SEL, codec IRQ) | 24,28,31,34,37,38,39,40,41,44,45,46,47,50 | GPIO | GPIO | GPIO (by name) | voltage domain per pin TODO(verify) on ArmSoM |
| Geniatech XPI-3576-CM5 | - | - | - | - | pinout not public |

---

## 8. Open questions (phrased for viewers)

1. Is 21 mm thick acceptable for a 3000 mAh battery, or would you rather have about 18 mm and roughly 2000 mAh?
2. The Focus panel we picked is being discontinued. Which in-production 4-4.3" DSI panel with a mainline driver
   would you use?
3. LuckFox Core3566, BigTreeTech CB2, or something else: does a mainline device tree matter more than price?
4. Should the keyboard be an RP2040 USB keyboard (flexible firmware) or a TCA8418 I2C scanner (simpler,
   mainline, no hub)?
5. Tact switches (Alps SKSW) or metal domes (Keystone 5135): which feel do you want on camera?
6. Audio: an ES8316 I2S codec with per-module straps, or a USB audio chip that works with any module?
7. Is the proposed layout (number row, Fn legends on the plate, D-pad on the left) right? What would you
   change?
8. How should a slider survive daily use: printed rails, metal rails, or a bought slide mechanism without a
   spring?
9. Should the tray's empty upper half hold a second battery?
10. How should a sealed handheld shed 2-3 W when the keyboard covers its back: a metal front frame, side vents,
    or a heat spreader into the tray?
11. Wi-Fi only for v1, or a Band 71 modem (e.g. Quectel EC25-AF, TODO(verify)) designed in from the start? The
    hub already reserves USB port 2.
12. Should the hardware also be licensed CERN-OHL-S, alongside AGPL-3.0?

---

## 9. Source documents used (open them; not redistributed here)

- LuckFox Core3566 datasheet: https://files.luckfox.com/wiki/Core3566/Core3566-datasheet.pdf
- Raspberry Pi CM4 / CM5 datasheets: https://datasheets.raspberrypi.com/cm4/cm4-datasheet.pdf ,
  https://datasheets.raspberrypi.com/cm5/cm5-datasheet.pdf ; CM4IO KiCad: https://datasheets.raspberrypi.com/cm4io/CM4IO-KiCAD.zip
- Radxa CM4 schematic: https://dl.radxa.com/cm4/docs/hw/radxa_cm4_schematic_v1.20.pdf
- ArmSoM-CM5 docs and pin list: https://documentation-armsom.vercel.app/armsom-cm5
- Focus panel spec: https://focuslcds.com/wp-content/uploads/2025/08/E43GB-I-MW405-C_Spec.pdf ; app note FAN4225
- Hirose DF40 catalogue (receptacle land pattern, page 4); TI datasheets for BQ25895, BQ27441-G1, TPS61230,
  TPS61169, TCA8418 (ti.com/lit/ds/symlink/<part>.pdf); ES8316 datasheet (LCSC C365735); Alps SKSW (LCSC
  C255576 datasheet, page 2); Keystone catalogue page 97 (https://www.keyelco.com/userAssets/file/K75p97.pdf)
- JLCPCB capabilities: https://jlcpcb.com/capabilities/pcb-capabilities
