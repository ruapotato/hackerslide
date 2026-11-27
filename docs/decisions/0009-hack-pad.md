# 0009 From Linux handheld to hack pad

**Status:** direction decided (David, 2026-11-27). Architecture and parts not yet chosen.

## Context

The Linux handheld reached a checked, unbuilt rev 0.1 at 19.35 mm. Three searches then showed what stands between
it and an N810-class device: no thinner compute module that can simply be ordered, no thin AMOLED in stock with
usable documentation, and a battery market that offers little at 3 A. Thickness, heat and battery life were all
set by the Linux-class processor.

## Decision

- The Linux handheld is kept, complete, on the branch `linux-handheld` (the two-board rev 0.1 as first finished is
  also at tag `rev0.1-design`).
- `main` becomes a **hack pad**: no Linux, no web browser. A microcontroller, "one of the beefiest we can put in
  it" (David), running its own firmware with a terminal and its own interface, able to run MicroPython.
- **As much of a multi-tool as is reasonable**, not a copy of the Flipper Zero: sub-GHz and NFC at least,
  software-defined radio as far as a microcontroller can take it, "as much send and receive as possible".
- MP3 music and audiobook playback from the card.
- A thin, low-power display is to be considered, e-ink among them.

## Added by David, 2026-11-27 (later the same day)

- **Display: e-paper.** The slow refresh is accepted. A waterfall can be drawn as partial updates, column by
  column from the left, with one full clear when it reaches the right edge.
- **Firmware: written from scratch**, by us. Not a concern.
- **Scope grows from radio tool to "tricorder":** as many kinds of sensing as there are well-stocked, currently
  made chips for. Named so far: CO2, and sound below and above hearing as well as within it. A sensor survey
  under the same stock rule is under way.

- **Brain: NXP i.MX RT1176** (David: "probably fine"), with as much RAM as is practical. The chip's memory
  controller takes SDRAM up to 1024 Mbit per chip select (NXP reference manual rev 2 correction); NXP's own
  evaluation board carries 64 MB as two W9825G6KH, and MicroPython's port for that board already uses the 64 MB
  as its heap (`MICROPY_HW_SDRAM_SIZE = 0x4000000`). Plan: 64 MB, the same arrangement, so the port carries over.

- **Sensors (David, 2026-11-27):** keep essentially all the sensors that are well stocked
  ([hack-pad-sensors.md](../hack-pad-sensors.md)). Preference: every part should come from the board assembler's
  own stock, so that ordering boards needs no parts shipped in. Two parts conflict with that and are not yet
  settled: the SDR radio chip (AT86RF215) and the touchpad chip (IQS7211E) are stocked at DigiKey, not JLCPCB.
- **Operating system (David, 2026-11-27):** a new kernel written in today's Adder, using Hamnix's parts where
  they fit and reimplementing where needed ([os-audit-hamnix.md](../os-audit-hamnix.md)). Work starts in an
  emulator (QEMU's Cortex-M7 machine). An NXP evaluation board for bring-up is approved in principle; David buys it.

- **Name (David, 2026-11-27):** the operating system is **HackOS**. It gets its own repository, and the Adder
  compiler work for this chip gets its own repository too, separate from the existing Adder and Hamnix ones.

- **Pointing (David, 2026-11-27):** the display's touch panel, and a D-pad with a centre key on the keyboard.
  The touchpad and its chip are dropped.

- **Display part:** Good Display **GDEY0426T82-FT01C**: 4.26" e-paper, 800 x 480, with capacitive touch (FT6336U,
  I2C) and a front light (7 LEDs). 105.33 x 62.37 x 1.98 mm; display on a 24-pin 0.5 mm cable (SSD1677, SPI),
  touch and front light on 6-pin cables. Good Display's store, read by David on 2026-11-27: $33.68 list ($27.62 on
  sale), **94 in stock**, add to cart. Specification, drawing, FT6336U datasheet and sample code are published.
  To settle from the specification before drawing: the front light's supply. The page gives "series, <= 15 V,
  <= 15 mA" in its table and "2.8-3.3 V" in a safety note.

- **Battery (David, 2026-11-27):** the GlobTek BL1950P4071611S1PCPT (1950 mAh, 4.5 x 61.5 x 76.5 mm, 3.9 A, 317
  at DigiKey) is acceptable as long as it fits the final dimensions.
- **Repositories:** HackOS and the Adder fork go under David's own account (`ruapotato`), public, not the HamnixOS
  organisation. HackOS is AGPL-3.0; the Adder fork keeps Adder's GPL-3.0-or-later.

- **Languages (David, 2026-11-27):** HackOS is a mix of Adder and C. Adder for the kernel core, file systems,
  shell and tools; C for the chip makers' drivers and third-party stacks linked in. This needs Adder to call C
  functions directly, which is being added to the compiler fork.
- **MicroPython dropped (David, 2026-11-27):** Adder is already Python-like, so MicroPython adds little. Open
  question this left: Adder is compiled on a PC, so how are programs written or changed on the device itself?
- **On-device building is a requirement (David, 2026-11-27).** Adder is self-hosted and has its own native
  backend for x86_64; LLVM will not run on the device. So the plan is a native backend for this chip in the Adder
  compiler, so that the compiler itself runs under HackOS. An assessment (structure, size, memory, effort) is
  being written with milestone 2. This is also a reason to fit 128 MB.
- **On-device scripting is the Hamnix shell (David, 2026-11-27).** `hamsh` has variables, globs and control flow,
  and is the everyday way to write and change things on the device. Compiling Adder on the device becomes a later
  extra, not a requirement: without LLVM the compiler's own backend produces code David puts at about five times
  slower, so releases are built on a PC. The shell needs rework where it relies on `fork`
  ([os-audit-hamnix.md](../os-audit-hamnix.md)).

- **Brain: reopened, 2026-11-27.** NXP's documents, read and cross-checked (`hardware/hackpad/data/`), show
  three things that the earlier choice missed: the RT1172 has **one** core, not two (only the RT1173/1175/1176
  carry the 400 MHz second core); the version JLCPCB stocks (CVM8A) is the "A" silicon, which NXP marks not
  recommended for new designs, and an erratum on it needs three of its pin banks at 1.8 V; and NXP's own board
  feeds part of the chip from a separate 1.8 V supply and boots from 1.8 V flash. JLCPCB has no "B" silicon of any
  RT117x. David to choose among: RT1172 A silicon from JLCPCB; RT1176 B silicon from DigiKey (516); or the older
  RT1062 (600 MHz, the Teensy 4 chip, 1,269 at JLCPCB, current silicon).

- **Sourcing widened (David, 2026-11-27):** parts may come from DigiKey as well as JLCPCB's shelf, as long as
  JLCPCB can order them itself and fit them, so that nothing has to be shipped by hand.
- **Brain decided: the RT1176** in its current ("B") silicon: 800 MHz or 1 GHz main core plus the 400 MHz second
  core. Exact part number to be picked from DigiKey's stock. This also reopens the SDR chip, since the wider
  radio chips are stocked at DigiKey: being re-examined.

- **Memory: as much as the chip supports and the board fits (David, 2026-11-27).** What the data says
  (`hardware/hackpad/data/sdram.md`): three chip selects are usable for SDRAM on B silicon (CS0, and CSX0 or RDY
  as the others); each takes two 16-bit chips; with 512 Mbit chips that is 128 MB per select, 384 MB in all.
  Stocked at JLCPCB: W9825G6KH (256 Mbit, 3.3 V, 7,705) and W989D6DBGX6I (512 Mbit, 1.8 V mobile type, 10,792).
  Not yet verified: that the controller runs the 1.8 V mobile type, that several selects share the bus cleanly (no
  NXP board does it), the bus speed with four or six chips, and the standby current of each chip.

- **Display stays e-paper (David, 2026-11-27),** after comparing it with the original colour panel: the colour
  panel would allow a desktop but costs about 5 mm of thickness and most of the battery life. The brain's 2D
  graphics unit and display interface stay unused for now.
- **Memory: similar to the N810, 128 MB, or 256 MB if that is the easier build (David, 2026-11-27).** This replaces
  the "as much as possible" goal above. The chip type and bank arrangement follow from the datasheet checks.

- **Brain part number: MIMXRT1176AVM8B** (DigiKey, read 2026-11-26: 506 in stock, $26.83, Active): current "B"
  silicon, 800 MHz main core plus the 400 MHz second core, automotive temperature grade. The 1 GHz version has no
  stock anywhere (expected August 2027) and the industrial 800 MHz one has 5 pieces. To confirm before ordering:
  the automotive data sheet, which could not be downloaded.
- **SDR radio, now that DigiKey is allowed: Microchip AT86RF215-ZU** (DigiKey 5,390, $7.61) **with a small FPGA**
  (Lattice ICE40LP1K-QN84, DigiKey 182, $6.71; the part the open CaribouLite design uses for the same job). The
  radio's sample port is a 128 Mb/s differential link that no microcontroller pin can take, so the FPGA turns it
  into a byte-wide bus for the brain's camera port. Covers 389.5-510, 779-1020 and 2400-2483.5 MHz, receive and
  send up to +14 dBm, up to 2 MHz wide, two bands at once, and it has packet modems built in. The wide-range
  converter stays, but in front of this chip's 2.4 GHz port, which removes the ghost-signal limit above 1.9 GHz;
  the shortwave detector stays as it was. The SX1255 is dropped. Risk: only 182 of that FPGA, with a 40-week lead.

- **Memory route (2026-11-26, from the datasheet study):** two Winbond W989D6DBGX6I (1.8 V low-power type, 64 MB
  each) give 128 MB on the first select; unfitted positions for two more give 256 MB. Chosen over four of the
  3.3 V chips NXP uses because those cannot reach 256 MB, take seven times the board area and draw about nine
  times the sleep current. The price: NXP has no board with this chip type, the chip asks for one start-up
  command NXP's driver does not send, and both memory pad banks run at 1.8 V. To be tried on the evaluation board
  before the board is ordered; the fallback is the 3.3 V chips at 128 MB.
- **Supporting parts (same study, all read from maker datasheets, all in JLCPCB stock):** 3.3 V converter
  TPS63802; 1.8 V step-down TLV62568 plus quiet 1.8 V LDO TPS7A2018; always-on 3.0 V TPS7A0230 for the clock;
  reset supervisor TPS3840DL30; crystals NDK NX3225GA 24 MHz and Epson FC-135; flash in the 0.8 mm WSON package;
  USB-C socket HRO TYPE-C-31-M-14 (sunk into the board edge, about 1.8 mm above it).
- **Battery plug correction:** the GlobTek pack's plug is Molex Micro-Latch 2.00 mm (51065-0400), not PicoBlade.
  Mating header 53254-0470 (right-angle, through-hole, JLCPCB 928); its height is not verified yet.
- **Headphone jack: no 4-pole socket under 3.0 mm was found in stock.** Lowest in JLCPCB stock is XKB PJ-3255A at
  4.15 mm in an edge notch; 3-pole sunk types exist. Open: accept about 4.2 mm at that spot, or a 3-pole jack
  (no headset microphone), or audio over USB-C only.

- **Headphone jack: 3-pole, sunk into the board, audio out only (David, 2026-11-26).** No headset microphone
  input; the built-in microphones cover recording.

- **David leans toward the hack pad (2026-11-26).** The video still shows both devices and asks the community;
  the Linux handheld stays complete on its branch.
- **Mechanical concept model (Claude's working assumptions, 2026-11-26, for David to confirm; body thickness is
  his decision):** N810 footprint 128 x 72 mm; battery lying under the main board with only parts up to 1.5 mm
  over it and taller parts (up to 2.4 mm) in the 48 mm strip beside it, which is what makes everything fit;
  the display half holds the e-paper panel and a 0.5 mm strip board for its drive circuit beside it. Result:
  **15.4 mm** (keyboard half 11.6, display half 3.4, gap 0.4), from `mechanical/src/hackpad.py`; the stack is
  in `docs/hack-pad-stack.md`. Earlier "13.3 mm" was arithmetic with the battery beside the parts, which does
  not fit (`docs/hack-pad-area.md`).
- **Development board:** David will probably buy a Teensy 4.1 (RT1062, same peripheral family) and keep HackOS
  work on the emulator until then; the NXP EVKB is out of stock nearly everywhere (Amazon about $500).

## What carries over from the Linux design

The slider body and its rails, travel stop and hooks; the thumb keyboard with its next layout (N810 rows, Fn
numbers, touchpad, Esc and Tab) and its I2C scanner; charger, fuel gauge and battery fuse; the audio codec and
jack; USB-C; the card slot; the board generators, router and checks.

## Open

Which microcontroller; which radios; which display; the battery (a thinner one becomes useful once the module is
gone); whether one board or two. A parts survey restricted to parts in production with listed stock is under way.

## Rules that still hold

Every part in active production and orderable in ones with visible stock. Transmitting is regulated: the design
will say what each radio is allowed to do and will not pretend otherwise.
