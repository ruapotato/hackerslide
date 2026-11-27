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

## Milestone 1 reached (2026-11-27)

HackOS lives at https://github.com/ruapotato/hackos (AGPL-3.0) and needs the `cortex-m7` branch of
https://github.com/ruapotato/adder (GPL-3.0-or-later, a fork of HamnixOS/adder). One command builds the compiler and
the image and runs them on QEMU's Cortex-M7 machine: 44 checks pass (start-up, serial output, a timer interrupt and
a system-call handler written in Adder, double-precision and 64-bit arithmetic, register access, fault reporting).
Emulator only; nothing has touched the i.MX RT1170. Found on the way: Adder's `volatile` read 8 bytes where 4 were
asked for, now fixed on the LLVM path; and Hamnix's RAM file system compiled unchanged and passed a create, write,
read, rename, list and delete test in the emulator, as a scratch experiment.

Cost of Adder's 64-bit values on this 32-bit chip, measured: about 1.3 to 1.8 times the code size of equivalent C in
ordinary code, 3 times in call-heavy stubs, and pointers in structures take 8 bytes. Affordable with 64 MB.

## Milestone 2 result (2026-11-26, emulator only)

Pushed to `ruapotato/hackos` (main) and `ruapotato/adder` (branch `cortex-m7`). `make test` passes from a clean build.

- Kernel: preemptive threads, mutexes with priority inheritance, semaphores, condition variables, message queues,
  31 system calls (Hamnix's numbers where shared), memory-protection guards, a heap, faults that end only the
  faulting thread, Hamnix's tmpfs running unmodified under a new descriptor layer, an interactive console monitor.
- Compiler: void results, read-only string literals, size options, and `extern "C"` in both directions.
- C alongside Adder is proven with Sensirion's unmodified SHT4x driver (BSD-3-Clause) called from Adder.
- Size: 81 KB of kernel code at -O2, 48 KB optimised for size.
- Limits: no program loader or processes yet; user threads are not isolated from each other; every non-empty tmpfs
  file costs at least 128 KB (Hamnix's chunk size); `fs/vfs.ad` was not portable and was replaced.
- On-device compiling: judged feasible; a Thumb-2 back end is estimated at 4,000-5,500 lines and self-compiling
  needs roughly 25-45 MB of RAM. An estimate, not a test.
- Proposed milestone 3: processes, loader and exec, pipes, hamsh over the serial console, then FAT.

## Milestone 3 result (2026-11-26, emulator only)

Pushed to `ruapotato/hackos` and `ruapotato/adder` (`cortex-m7`). `make test` passes from a clean build.

- HackOS boots to Hamnix's `hamsh` on the serial console as an unprivileged process and runs programs loaded from
  files: `echo cat ls cp rm mkdir wc head grep`, pipelines, redirection, a script file.
- Processes are position-independent ELF files, each in its own memory block that the protection unit fences off
  from the kernel and from other processes (tested by faulting on purpose). `rfork` is implemented as vfork.
- Hamnix's shell and FAT code are copied unmodified apart from one 41-line patch shrinking the shell's static
  arenas; tmpfs now costs about 8 KB for a file's first byte instead of 131 KB (recorded 7-line patch).
- FAT32 on a RAM disk mounted at `/sd`: read, create, append, truncate, remove, run a program from it.
- Size: kernel code 128 KB at -O2, 76 KB optimised for size. Smallest process: 10 KB plus a 16 KB kernel stack.
- Limits: a process's memory is fixed at start and is read/write/execute throughout; FAT is 8.3 names on write,
  no mkdir or rename; the shell's namespace and job-control commands were not tried; nothing has run on hardware.
- Proposed milestone 4: drivers for the real chip. This QEMU has no i.MX RT model, so keyboard and e-paper stacks
  would be developed on emulated devices, vendor drivers against register models, and the boot header and clock
  setup on host-side checkers, until an evaluation board is on the bench.

## Teensy 4.1 target (2026-11-26, not run on hardware)

Pushed to `ruapotato/hackos`. `make BOARD=teensy41` builds a .hex for the Teensy loader that boots to the same shell
(console on Serial1, pins 0/1, 115200; LED blinks once running). Drivers for the serial port, GPIO, pin mux, clocks,
I2C, SPI and the SD card, written against NXP's register definitions; the SD driver passes against QEMU's own SD
model, the others against register models written from the reference manual; the boot header, every register
constant and every pin setting are checked by script. The checks found and fixed two kernel bugs that would have
stopped the board. Fits the Teensy's 1 MB of RAM for one shell and four-program pipelines; a second shell needs
PSRAM. Bring-up checklist: `docs/boards/teensy41.md` in the hackos repo. Every hardware-facing part is untested.

## First real-board target: Adafruit Feather nRF52840 Express (2026-11-27, not run on hardware)

David decided HackOS becomes a multi-board microcontroller OS, starting on a board he owns. Pushed to
`ruapotato/hackos`: `make BOARD=feather-nrf52840` gives a `.uf2` for drag-and-drop flashing (double-tap reset,
drive FTHR840BOOT; the image starts after Adafruit's bootloader and Nordic's SoftDevice, which stay untouched).
Console on the TX/RX pins at 115200 through a 3.3 V USB-serial adapter; red LED blinks once running. The unchanged
image boots and runs a 52-command shell session in Renode's nRF52840 emulator (37 checks pass). Programs run in
place from flash so the shell plus five-program pipelines fit in 256 KB of RAM, with smaller shell limits. No
compiler change was needed; double-precision floats use LLVM's software routines (BSD/Apache compiler-rt).
Guide: `docs/boards/feather-nrf52840.md` in the hackos repo; porting notes for RP2040/RP2350: `docs/porting.md`.
