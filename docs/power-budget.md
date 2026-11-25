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

**Discharging: limited in hardware by U13, a TPS2553 current-limited switch** between the charger's system rail
and everything it feeds (the 5 V boost and the backlight). With a 20 kohm setting resistor its limit is 1.215 A
minimum, 1.295 A typical, 1.375 A maximum at 25 degC (TI datasheet SLVS841), so the cell stays below 1.5 A. The cell's
own protection only trips between 2 and 5 A, which is a safety cut-out, not a limit to design to.

What happens at the limit: the limited rail sags, the boost's under-voltage divider switches the 5 V rail off at
3.0 V, and the module loses power. U13's FAULT output (module pin 58, `BATT_OC_N`) goes low while it is limiting.
So the limiter is a backstop. **Software must keep the device below it**: cap CPU frequency and cores, and throttle
on low cell voltage. Costs: the switch drops about 0.11-0.18 V at 1.3 A (85-135 mohm), and it gets hot while limiting.

What the limit allows (estimate, 90 % boost efficiency, 0.6 W for the backlight):

| Cell voltage | Power through the limiter at 1.3 A | Left for the module at 5 V |
|---|---|---|
| 3.1 V | 4.0 W | about 3.1 W, 0.62 A |
| 3.7 V (nominal) | 4.8 W | about 3.8 W, 0.76 A |
| 4.2 V (full) | 5.5 W | about 4.4 W, 0.88 A |

So the module has to stay under roughly **0.6 A at 5 V (3 W)** on battery in the worst case. Whether the Core3566
can boot and browse inside that is the first thing to measure in phase 1. If it cannot:

| Option | Cost |
|---|---|
| A cell with a higher rating, and a larger setting resistor value change on U13 | None found in stock with a datasheet; a custom pack needs a quote |
| TPS61236P boost with a programmable output current and a current monitor (JLCPCB `C130295`) | Needs an inductor rated for its 8 A switch limit and loses the under-voltage divider; a larger redesign |
| Tighter software cap | Slower device |

With USB power connected the charger supplies the system rail, but U13 still limits the system to the same current.

## Risks that follow

1. The module may want more than the discharge limiter allows (about 3 W on battery, worst case). Then the 5 V
   rail drops and the device resets. Measure the real draw; cap it in software.
2. "All day" battery life is not reachable at these figures. Suspend that works is essential: verify RK3566
   suspend on mainline in phase 1.
3. Without a charged cell, a 500 mA USB source cannot boot the module (about 0.4 A available at 5 V).
