# Power budget

**Every figure here is an estimate unless it says "datasheet".** Nothing has been measured. The first job of
bring-up phase 1 is to replace this table with measurements from a module on a stock IO board.

## Supply chain

| Stage | Datasheet facts |
|---|---|
| Battery | BAK LP-454965-2P-3M pack: 2800 mAh minimum, 3000 typical, 3.7 V nominal (about 10.4 Wh at minimum capacity), 1.4 A max charge, 5.6 A max continuous discharge, protection trips at 12-16 A, 10k thermistor lead |
| Charger BQ25895 | Input capped at about 1.18 A by R12; input resets to 500 mA at each plug-in; charge current resets to 2.048 A |
| Discharge limiter TPS2553 | 1.61 / 1.70 / 1.80 A to the boost and the backlight |
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

**Charging.** The charger's input resets to 500 mA at every plug-in (its adapter detection is disconnected), so
the pack sees about 0.6 A until Linux sets `ti,charge-current`, which must be **1.4 A or less**; from then on the
charger regulates that current itself. R12 also caps the input at about 1.18 A (the 0.6 A is an estimate; the caps
are datasheet values).

**Discharging.** U13, a TPS2553 current-limited switch, sits between the charger's system rail and everything it
feeds (the 5 V boost and the backlight). With R66 = 15 kohm its limit is 1.61 A minimum, 1.70 A typical, 1.80 A
maximum (TI datasheet SLVS841), less than a third of the pack's rating. The pack's own protection trips at
12-16 A, which is a safety cut-out, not a limit to design to.

What happens at the limit: the limited rail sags, the boost's under-voltage divider switches the 5 V rail off at
3.0 V, and the module loses power. U13's FAULT output (module pin 58, `BATT_OC_N`) goes low while it is limiting.
So it is a backstop: software should keep the device below it. Costs: the switch drops about 0.14-0.24 V at
1.7 A (85-135 mohm) and gets hot while limiting.

What the limiter allows (estimate, 90 % boost efficiency, 0.6 W for the backlight):

| Voltage at the limiter | Power through it at 1.7 A | Left for the module at 5 V |
|---|---|---|
| 3.1 V | 5.3 W | about 4.2 W, 0.84 A |
| 3.7 V (nominal) | 6.3 W | about 5.1 W, 1.0 A |
| 4.2 V (full) | 7.1 W | about 5.9 W, 1.2 A |

So the module can draw roughly **4-6 W** on battery, where the brief expects 2-3 W under load. 1.7 A is the highest
setting the TPS2553 has; the pack itself would allow three times that. If measurements show the module needs
more, replace U13 with an eFuse that goes to about 4 A (for example TPS2595, in stock at JLCPCB as `C2155775`,
not yet evaluated).

With USB power connected the charger supplies the system rail, and U13 limits the system to the same current.

## Risks that follow

1. A module peak above the discharge limiter (about 4 W on battery, worst case) drops the 5 V rail and resets
   the device. Measure the real peak in phase 1.
2. "All day" active use is not reachable at these figures. Suspend that works is essential: verify RK3566
   suspend on mainline in phase 1.
3. Without a charged cell, a 500 mA USB source cannot boot the module (about 0.4 A available at 5 V).
