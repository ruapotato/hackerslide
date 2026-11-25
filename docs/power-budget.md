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

## Keeping the cell inside its rating (requirement, David 2026-11-24)

The cell must not be asked for more than its rated 1.5 A, charging or discharging.

**Charging: limited in hardware.** The charger's input is capped at about 1.18 A by R12 and resets to 500 mA at
every plug-in, so the cell sees about 0.6 A until Linux sets `ti,charge-current`, which must be 1.25 A or less
(estimate for the 0.6 A; the caps are datasheet values).

**Discharging: NOT limited in rev 0.1 as drawn. This must be closed before the carrier is ordered.**
The TPS61230 boost will pull whatever the module asks for, up to a 4-6 A switch limit. The cell's own protection
only trips somewhere between 2 and 5 A, which is a safety cut-out, not a limit to design to.

What 1.5 A allows (estimate, 90 % boost efficiency, 0.6 W for the backlight taken from the same rail):

| Cell voltage | Power from the cell at 1.5 A | Left for the module at 5 V |
|---|---|---|
| 3.0 V (boost about to switch off) | 4.5 W | about 3.5 W, 0.70 A |
| 3.7 V (nominal) | 5.55 W | about 4.5 W, 0.89 A |
| 4.2 V (full) | 6.3 W | about 5.1 W, 1.03 A |

So the module has to stay under roughly **0.7 A at 5 V** in the worst case. Options, to decide once the module's
real draw is measured in phase 1:

| Option | How | Cost |
|---|---|---|
| Hardware limit in the boost (recommended to evaluate first) | Replace the TPS61230 with the TPS61236P (JLCPCB `C130295`, 1,084 in stock on 2026-11-24). It has a programmable constant output current: about 124 kohm per amp, so about 180 kohm gives 0.7 A. Its CC pin also reports output current, which the design otherwise cannot measure | A different package and application circuit: the boost block is redrawn and re-audited. When the limit is hit the 5 V rail sags and the module may reset, so it is a backstop, not a way to run |
| Software power cap | Limit CPU frequency and cores so the module stays under the budget; throttle further on low cell voltage from the gauge | No hardware change, but nothing enforces it before Linux is up or if software misbehaves |
| A cell with a higher rating | A 50 x 60 mm cell rated for 3 A or more | None found in stock with a datasheet; a custom pack needs a quote |

A hardware limit plus a software cap that keeps the device below it in normal use is the intended end state.
With USB power connected the charger supplies the system first, so the limit matters on battery.

## Risks that follow

1. The module's peak current may trip the cell's protection, especially near empty. Measure the real peak.
   If it is a problem: a cell with a higher discharge rating, or limit the CPU frequency.
2. "All day" battery life is not reachable at these figures. Suspend that works is essential: verify RK3566
   suspend on mainline in phase 1.
3. Without a charged cell, a 500 mA USB source cannot boot the module (about 0.4 A available at 5 V).
