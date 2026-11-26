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
