# Bring-up plan

Phases follow the build series. Each phase lists what to measure and what would stop the next one.

## Phase 1: boot a module on a stock IO board (before any custom board is ordered)

| Do | Measure / record | Why |
|---|---|---|
| Boot Debian/Mobian on the Core3566 on a CM4 IO board | Which kernel, what works | No mainline device tree exists for this module |
| Power at the 5 V input | Idle (screen off and on), browsing, peak, suspend | Replaces every estimate in [power-budget.md](power-budget.md). The cell allows 1.5 A |
| Suspend and resume | Does it suspend on mainline, and at what power | "All day" depends on it |
| Module pin 99 | Voltage, and what a 1k pull to ground does | The power button depends on it |
| Module height | Calipers: carrier surface to the tallest part, on the 1.5 mm stack | Sets the cavity and the thermal gap |
| SoC temperature | Idle, browsing, 10 minutes of full load, bare | Baseline for [thermal.md](thermal.md) |
| Panel on DSI | Write the ST7701 panel entry from Focus's init file; get an image; touch through `goodix` | The largest software unknown on the current design |
| Optional: the AMOLED | Light a DMKDO04301ACA on an adapter | Decides the thin version. Needs the vendor's init sequence |

Stop if: the module cannot suspend, or its peak draw makes the cell unusable, or the panel cannot be made to work.

## Phase 2: fit mule and slider

| Do | Measure / record |
|---|---|
| Print front shell, back shell, tray frame, keycaps (PETG, not PLA) | Do the parts fit; where they bind |
| Tape in the cell, module and a paper carrier | Clearances at the jack, USB-C, card |
| Fit magnets | Detent force closed and open; any drag mid-travel; try other magnet sizes |
| Slider cycling rig with the flex cable (or a stock cable first) | Cycles to first open circuit. Target: more than 36,000 |
| Fold a real panel's tails behind it | Do they reach J4 and J5; which face are the contacts on; pin 1 side |

## Phase 3: keyboard, top plate, flex

| Do | Measure / record |
|---|---|
| Visual check, then power from 3.3 V on the bench | Current: should be microamps |
| I2C scan from any Linux board | Device at 0x34 |
| `tca8418_keypad` with the 6 x 10 keymap | Every key reports once; Ctrl + Shift + letter gives no phantom key |
| Key feel with printed caps | Does a corner press tilt the cap; try the lighter switch versions |
| ESD sanity | Touching the plate and keys does not reset the chip |

## Phase 4: carrier, without the module first

| Step | Check | Expected |
|---|---|---|
| 1 | Resistance VBUS, VSYS, VBAT, +5V to ground | No shorts |
| 2 | USB power, no cell, no module | VSYS about 3.65 V; +5V 5.0 V at TP4; BOOST_PG high |
| 3 | Load +5V at TP4 in steps up to 1 A | Stays within 4.75-5.25 V until the battery limiter acts: measure the current into VSYS_LIM (TP17) at which BATT_OC_N goes low. Expected 1.6-1.8 A |
| 4 | Connect the battery pack (**check polarity first**) | Charge LED on; pack current below 1.4 A |
| 5 | Unplug USB | +5V stays up from the cell; boost turns off near 3.0 V at VSYS |
| 6 | Hold the power button 12-18 s on battery | VSYS drops for about half a second (charger reset) |
| 7 | I2C scan through the test points | 0x6A charger, 0x36 gauge, 0x10 codec |

## Phase 5: carrier with the module

Console on J8 at 1,500,000 baud first. Then, in order: boot from microSD; I2C devices; display and touch;
backlight PWM; keyboard through the flex; audio out, jack detect, mic; charger and gauge drivers with
`ti,use-ilim-pin` and `ti,charge-current`; USB device mode; buttons; slider switch; suspend current of the whole
device; temperatures in the closed shell.
