# Operating system: audit of Hamnix's microcontroller era (2026-11-27)

David asked whether the microcontroller operating system Hamnix grew out of is worth reviving as the hack pad's
system. This is a read-only audit of `~/Projects/Hamnix` (history and the last snapshot before commit `288adade`
removed the microcontroller code), of today's Adder compiler, and of today's Hamnix kernel. Nothing in those
repositories was changed. Nothing here was built for ARM: this machine has no ARM toolchain installed, so the
findings on the old tree come from reading source and history.

## Findings

| Question | Finding |
|---|---|
| What was the microcontroller system? | A single program for an emulated Cortex-M3 (QEMU `mps2-an385`): a shell with built-in commands over a 64-file RAM file system and a 16 KB heap. It was written between 2025-12-29 and 2025-12-31 and not developed after that |
| Did it multitask? | No. A process table exists, but nothing switches between processes: the interrupt handlers that would do it are empty loops, and its own test says "we won't actually run as that would require context switches" |
| Did it run on real hardware? | No evidence that it did. The RP2040 and STM32F4 support is marked experimental; a commit notes unresolved link errors on one and too little RAM on the other; the compiler emitted instructions the RP2040 cannot execute |
| Its drivers? | About 17,000 lines written to datasheet register maps, never linked into a build. The libraries that were built (I2C, sensors, displays, networking) simulate their devices |
| Its compiler backend? | No floating point, no 64-bit integers, no register allocation. Today's compiler rejects most of the old source: the language has moved on |
| Can today's Hamnix run without memory protection? | No. Page tables are assumed by the scheduler, program loader, fork and the system-call layer. As built it also needs far more memory: about 47 MB of image and 64 MB of static data |
| What is reusable from today's Hamnix? | The parts with no page-table code: the file-system layer with its namespaces, FAT and tmpfs, the libraries, the command-line programs, and the shell with some rework. The interface between programs and kernel is narrow: about 84 calls |
| Can today's Adder target this chip? | Close. Its LLVM path was made to produce a valid Cortex-M7 object with floating point by changing one line, as an experiment in a scratch folder. Not yet linked or run. It needs a proper third target, register access that the optimiser may not remove, interrupt support, and a start-up runtime |
| Licences | Hamnix and Adder are GPL-3.0-or-later with David as sole author, which combines with this repository's AGPL-3.0. No conflict found. (Not legal advice.) |

## Paths

| Path | Verdict |
|---|---|
| A. Revive the old microcontroller tree | Not recommended: there is no kernel in it to port |
| B. Make today's Hamnix run without memory protection | Not recommended: it amounts to a new kernel that also carries the PC version's weight |
| **C. A new small kernel in today's Adder, reusing Hamnix's file-system layer, libraries, programs and shell** | **Recommended.** It is David's stack end to end and would feel like Hamnix to use |
| D. Adder programs on NuttX or Zephyr | The fallback, and a useful reference for how the chip's peripherals behave |

## First milestones for C

1. Adder "hello" over a serial port on an emulated Cortex-M7 (QEMU `mps2-an500`): the new compiler target,
   start-up code, a timer interrupt, a floating-point test. Then the same on NXP's RT1170 evaluation board with its
   external memory working. QEMU has no model of this chip, so its peripherals need the real board.
2. A kernel core on both: switching between threads, system calls, a guard on each stack, the ported file-system
   layer on a RAM disk, a serial console.
3. The shell over the serial port, running programs from the memory card; then the first e-paper frame and the
   keyboard.

Rough effort, as estimates: two to four weeks for the compiler and runtime, two to three months to a usable shell
on the evaluation board with the card and a display. Radios, sensors and the interface come after that.

## Open technical question

Adder treats every value and pointer as 64 bits. On a 32-bit chip that works, but pointers take twice the memory
and calls are slower. Start that way and measure; a true 32-bit mode is weeks of compiler work.
