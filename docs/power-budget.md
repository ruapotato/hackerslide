# Power budget

**Every figure here is an estimate unless it says "datasheet".** Nothing has been measured. The first job of
bring-up phase 1 is to replace this table with measurements from a module on a stock IO board.

## Supply chain

| Stage | Datasheet facts |
|---|---|
| Cell | PKCELL LP785060: 2500 mAh typical, 3.7 V nominal (9.25 Wh), 1.5 A max charge, 1.5 A max continuous discharge, protection trips between 2 and 5 A |
| Charger BQ25895 | Input capped at about 1.18 A by R12; input resets to 500 mA at each plug-in; charge current resets to 2.048 A |
| Boost TPS61230 | 5.02 V; on above 3.31 V, off below 3.01 V at VSYS; about 2.3 A available at 3.0 V in |
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

| | Estimate |
|---|---|
| Idle, screen on at full brightness | about 4.5 h |
| Browsing | about 2.5-3.5 h |
| Suspend | about 3-4 days |
| Cell current when browsing | 0.7-1.0 A average at 3.7 V |
| Cell current at a 2 A module peak near empty | about 3.7 A: **above the cell's 1.5 A rating and inside its protection trip window** |

For reference, the N810 ran about 4 hours of active use on 5.5 Wh, which is about 1.4 W for the whole device.

## Risks that follow

1. The module's peak current may trip the cell's protection, especially near empty. Measure the real peak.
   If it is a problem: a cell with a higher discharge rating, or limit the CPU frequency.
2. "All day" battery life is not reachable at these figures. Suspend that works is essential: verify RK3566
   suspend on mainline in phase 1.
3. Without a charged cell, a 500 mA USB source cannot boot the module (about 0.4 A available at 5 V).
