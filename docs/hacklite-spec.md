# HackLite: specification draft (2026-11-27)

**Status: concept, research in progress; nothing drawn or ordered.** Branch `hacklite` (name: David, 2026-11-27).

A small, pocketable HackOS device that runs for days: a small e-ink screen on top, a split thumb keyboard below
whose width sets the device width, a small pointer/nav control between the keyboard halves. The brain is an
existing plug-in microcontroller board (no custom compute module: David), running HackOS.

Being decided (research running): the plug-in board (Teensy 4.1, SparkFun MicroMod Teensy, Arduino Portenta H7,
Raspberry Pi Pico 2 W / Pimoroni Pico Plus 2 W, any in-stock RT1170 board) and the e-ink panel (2.6"-3.5",
at most about 80 mm wide, touch and front light preferred).

First estimates: about 88-90 x 75-80 x 10-12 mm; 0.1-0.3 W in use, so about 1-3 days of use and weeks of standby on
one 7.4 Wh cell (rough).
