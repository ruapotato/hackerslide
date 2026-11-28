# Linux handheld or hack pad: risks (Claude's assessment, 2026-11-26)

An opinion based on the two designs as they stand, not a measurement. Neither device has been built.

## Linux handheld (branch `linux-handheld`, rev 0.1 complete and checked)

| Risk | How bad | Why |
|---|---|---|
| The compute module is a black box | High | LuckFox publishes no schematic; one pin used for power-on is documented as an output; the I/O voltage was inferred. If the module does not behave as assumed, the carrier needs a respin and there is nobody to ask |
| Screen driver | Medium | The panel needs a Linux driver entry nobody has written; only 10 panels were in stock |
| Heat | Medium | 2-3 W (estimate) in a sealed plastic case with the keyboard over the back; unmeasured |
| Battery current | Medium | The pack is limited to 2 A, the fuse is set at 1.86 A; whether the module plus screen stays under it at full load is unknown |
| Thickness and battery life | Known cost | 19.4 mm; roughly 3-4 hours of browsing (estimate) |
| Board design | Lower | 4 layers, no BGA of our own: the module carries the hard parts (processor, memory, power) |
| Software | Low | Linux exists; the work is a device tree and two drivers |

## Hack pad (`main`, schematic about half drawn)

| Risk | How bad | Why |
|---|---|---|
| The main board itself | High | Everything the module did is now ours: a 289-ball BGA on a 6-layer board, a 32-bit memory bus at up to 166 MHz, the brain's power-up order. A first board of this kind often needs a second round |
| Memory chip type | Medium-high | The low-power memory chosen for 256 MB has never been shown working on this controller; fallback: the 3.3 V chips NXP uses, 128 MB |
| Radio front ends | High | Six or more radios in a small box, several matching networks not from the makers' reference designs, antennas that need tuning with instruments we do not have |
| SDR | Medium-high | FPGA gateware, a fast differential link, an FPGA with 182 in stock and a 40-week lead time |
| Firmware | High (schedule) | Every driver is written from scratch in Adder and C; Hamnix Micro runs in an emulator only so far |
| Space and pins | Medium | Solved on paper by putting the battery under the board (15.4 mm) and, for the pins, by a helper chip or fewer radios; not yet drawn |
| Heat | Low | Under 1 W flat out (data sheet: 144 mA at 800 MHz) |
| Battery life | Low | Rough estimate: a day or more of mixed use, about 10 hours with the SDR running; standby days to weeks |
| Parts | Low | Everything in stock at JLCPCB or DigiKey, no undocumented module |
| Radio rules | Note | Custom transmitters are not certified; fine for a personal prototype, not for selling |

## Is the hack pad the safer build?

**No, not as currently scoped.** It removes the Linux design's worst unknown (a module without a schematic) and its
heat and battery problems, but replaces them with more work of our own: a much harder main board, many radios and
a whole operating system. The Linux handheld has fewer risks, but its biggest ones are outside our control; the
hack pad has more risks, but every one of them can be checked, tested in stages and fixed by us.

**What would make it the safer build:** a staged first board, the "core" only: brain, memory, power, e-paper,
keyboard, card, audio, USB, plus the two most-wanted radios (sub-GHz and NFC). That board is about as hard as the
Linux carrier plus the BGA, every part of it can be tested with Hamnix Micro on the bench, and it is useful on its own.
The SDR, the other radios and the sensors follow on a second board once the core works. That costs a second order
but turns one large gamble into two smaller ones.
