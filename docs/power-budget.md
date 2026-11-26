# Power budget

**Every figure here is an estimate unless it says "datasheet".** Nothing has been measured. The first job of
bring-up is to replace this table with measurements from a module, on a stock IO board or on the carrier itself.

## Supply chain

| Stage | Datasheet facts |
|---|---|
| Battery | Jauch LP675365JU pack: 2800 mAh minimum, 3000 typical, 3.7 V nominal (about 10.4 Wh at minimum capacity), 2 A max charge and discharge (lead-limited), protection trip 4.2-9 A, no thermistor |
| Charger BQ25895 | Input capped at 0.68 / 0.755 / 0.83 A by R12 (470 ohm); input resets to 500 mA at each plug-in; charge current resets to 2.048 A |
| Battery fuse TPS259531 (U13) | 1.86 A typical to the boost and the backlight (RILM 1.1 kohm); 34 mohm |
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

The battery must not be asked for more than its rating: 2 A discharging, 2 A charging (Jauch LP675365JU; both limited by its 26 AWG leads).

**Charging.** Two limits, one of them independent of software:

- Hardware: R12 (470 ohm) caps the charger's input at 0.83 A maximum. Even with the charge-current register at its
  reset value of 2.048 A, the pack then gets at most about 0.83 A x 5 V x 0.9 / 3.0 V = 1.25 A, under its 1.4 A
  rating. This holds as long as the ILIM pin is enabled, which is the charger's reset state and what
  `ti,use-ilim-pin` keeps in the device tree. (With the earlier 300 ohm the pack could have seen about 1.8 A if
  software raised the input limit and left the charge current at its default: found by the schematic review.)
- Software: `ti,charge-current` of 1.4 A or less.

The price is charging speed: about 0.9 A into the pack at 3.7 V, so roughly 3.5 hours from empty.

**Discharging.** U13, a TPS259531 eFuse (David 2026-11-25, replacing the 1.7 A TPS2553; the -531 variant since 2026-11-26 for stock: same chip as the -571 plus an output clamp at 5.5-5.9 V that a 4.4 V rail never reaches), sits between the charger's
system rail and everything it feeds (the 5 V boost and the backlight). RILM = 1.1 kohm sets the limit to 1.86 A
typical (TI SLVSE57 equation 4: 2000 / R + 0.04; the table's two points, 487 ohm 3.87-4.42 A and 1780 ohm
1.09-1.24 A, give about +-7 %, so 1.73-1.99 A). That keeps the draw under the pack's 2 A rating at the top of the
tolerance. The pack's own protection trips at 4.2-9 A, which is a safety cut-out, not a limit to design to.

What happens at the limit: the fuse regulates the current, the limited rail sags, the boost's under-voltage
divider switches the 5 V rail off at 3.0 V, and the module loses power. If the fuse overheats it switches off and
retries; its FLT output (module pin 58, `BATT_OC_N`) is low meanwhile. It drops about 0.07 V at 1.86 A.

What it allows (estimate, 90 % boost efficiency, 0.6 W for the backlight):

| Voltage at the fuse | Power through it at 1.86 A | Left for the module at 5 V |
|---|---|---|
| 3.1 V | 5.8 W | about 4.6 W, 0.9 A |
| 3.7 V (nominal) | 6.9 W | about 5.6 W, 1.1 A |
| 4.2 V (full) | 7.8 W | about 6.5 W, 1.3 A |

So the module can draw roughly **4.5-6.5 W** on battery, where the brief expects 2-3 W under load. That is about
twice the expected load, not the four times the earlier 3 A setting gave: **the module's real peak, above all
while booting on a nearly empty pack, is the first thing to measure.**

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
