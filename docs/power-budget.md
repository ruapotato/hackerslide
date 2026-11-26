# Power budget

**Every figure here is an estimate unless it says "datasheet".** Nothing has been measured. The first job of
bring-up phase 1 is to replace this table with measurements from a module on a stock IO board.

## Supply chain

| Stage | Datasheet facts |
|---|---|
| Battery | BAK LP-454965-2P-3M pack: 2800 mAh minimum, 3000 typical, 3.7 V nominal (about 10.4 Wh at minimum capacity), 1.4 A max charge, 5.6 A max continuous discharge, protection trips at 12-16 A, 10k thermistor lead |
| Charger BQ25895 | Input capped at 0.68 / 0.755 / 0.83 A by R12 (470 ohm); input resets to 500 mA at each plug-in; charge current resets to 2.048 A |
| Battery fuse TPS259571 (U13) | About 3.0 A to the boost and the backlight (RILM 680 ohm); 34 mohm |
| Boost TPS61230 | 5.02 V; on above 3.31 V, off below 3.01 V at its input; about 2.3 A available at 3.0 V in |
| Module | Needs 4.75-5.25 V; supplies 3.3 V and 1.8 V, 600 mA each |

## Load estimate

| Load | Idle, screen on | Browsing | Suspend | Basis |
|---|---|---|---|---|
| Module (RK3566, RAM, Wi-Fi) | 0.9 W | 1.5-2.5 W | 0.09 W | One forum figure of 0.92 W idle and 0.09 W suspend for RK3566 boards; "2-3 W under load" from the brief |
| Backlight at full | 0.6 W | 0.6 W | 0 | 12.8 V x 40 mA = 0.51 W at the LEDs, about 85 % driver efficiency |
| Panel logic, touch | 0.15 W | 0.15 W | 0 | Panel datasheet: 38 mA typical at 3.3 V, touch 8 mA |
| Codec, keyboard, gauge, charger quiescent | 0.03 W | 0.05 W | 0.001 W | Datasheet standby currents |
| Boost and module regulator losses | 10 % | 10 % | boost idle about 0.5 mW | Estimate |
| **At the cell** | **about 1.9 W** | **about 2.5-3.6 W** | **about 0.1 W** | |

## What that means

| | Estimate, at 10.4 Wh |
|---|---|
| Idle, screen on at full brightness | about 5 h |
| Browsing | about 3-4 h |
| Suspend | about 4 days |
| Battery current when browsing | 0.7-1.0 A average at 3.7 V |

For reference, the N810 ran about 4 hours of active use on 5.5 Wh, which is about 1.4 W for the whole device.

## Keeping the cell inside its rating (requirement, David 2026-11-24)

The battery must not be asked for more than its rating: 5.6 A discharging, 1.4 A charging.

**Charging.** Two limits, one of them independent of software:

- Hardware: R12 (470 ohm) caps the charger's input at 0.83 A maximum. Even with the charge-current register at its
  reset value of 2.048 A, the pack then gets at most about 0.83 A x 5 V x 0.9 / 3.0 V = 1.25 A, under its 1.4 A
  rating. This holds as long as the ILIM pin is enabled, which is the charger's reset state and what
  `ti,use-ilim-pin` keeps in the device tree. (With the earlier 300 ohm the pack could have seen about 1.8 A if
  software raised the input limit and left the charge current at its default: found by the schematic review.)
- Software: `ti,charge-current` of 1.4 A or less.

The price is charging speed: about 0.9 A into the pack at 3.7 V, so roughly 3.5 hours from empty.

**Discharging.** U13, a TPS259571 eFuse (David 2026-11-25, replacing the 1.7 A TPS2553), sits between the charger's
system rail and everything it feeds (the 5 V boost and the backlight). RILM = 680 ohm sets the limit to about
3.0 A (TI SLVSE57: 487 ohm gives 3.87-4.42 A, 1780 ohm 1.09-1.24 A; about 2020 / R). That is just over half the
pack's 5.6 A rating, and it is also the rating of the battery connector with the pack's 22 AWG leads (Molex 5268:
3.0 A), which is why it is not set higher. The pack's own protection trips at 12-16 A, which is a safety cut-out,
not a limit to design to.

What happens at the limit: the fuse regulates the current, the limited rail sags, the boost's under-voltage
divider switches the 5 V rail off at 3.0 V, and the module loses power. If the fuse overheats it switches off and
retries; its FLT output (module pin 58, `BATT_OC_N`) is low meanwhile. It drops about 0.1 V at 3 A.

What it allows (estimate, 90 % boost efficiency, 0.6 W for the backlight):

| Voltage at the fuse | Power through it at 3.0 A | Left for the module at 5 V |
|---|---|---|
| 3.1 V | 9.3 W | about 7.8 W, 1.6 A |
| 3.7 V (nominal) | 11.1 W | about 9.4 W, 1.9 A |
| 4.2 V (full) | 12.6 W | about 10.8 W, 2.0 A (the boost's own limit) |

So the module can draw roughly **8-10 W** on battery, where the brief expects 2-3 W under load.

**Hard power-cycle option.** The fuse's enable pin has an unfitted network (C90, R91, D9): fitted, holding the
power button for about 3 s cuts the limited rail, and with it the module's 5 V, for about 6-8 s. It exists because
the Core3566 may have no way to be woken after `poweroff` (pin 99 looks like an output); see
[open-questions.md](open-questions.md). Values are a starting point for the bench.

With USB power connected the charger supplies the system rail, and U13 limits the system to the same current.

## Risks that follow

1. A module peak above the discharge limiter (about 4 W on battery, worst case) drops the 5 V rail and resets
   the device. Measure the real peak in phase 1.
2. "All day" active use is not reachable at these figures. Suspend that works is essential: verify RK3566
   suspend on mainline in phase 1.
3. Without a charged cell, a 500 mA USB source cannot boot the module (about 0.4 A available at 5 V).
