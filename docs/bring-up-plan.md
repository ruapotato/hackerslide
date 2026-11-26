# Bring-up plan

Phases follow the build series. Each phase lists what to measure and what would stop the next one.

## Phase 1: boot a module on a stock IO board (before any custom board is ordered)

| Do | Measure / record | Why |
|---|---|---|
| Boot Debian/Mobian on the Core3566 on a CM4 IO board | Which kernel, what works | No mainline device tree exists for this module |
| Power at the 5 V input | Idle (screen off and on), browsing, peak, suspend | Replaces every estimate in [power-budget.md](power-budget.md). The battery fuse allows about 3.0 A from the pack, which is roughly 2 A at 5 V |
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

## Debug access on the carrier

Everything needed to see what the board is doing without a microscope. Positions and expected readings of every
pad are in [test-points.md](test-points.md), with pictures of both sides.

| Aid | Where | Use |
|---|---|---|
| Serial console | J8 (JST-SH 3-pin, Raspberry Pi Debug Probe lead fits) and pads TP34 (TX out of the module), TP35 (RX into it), TP5 (ground) for a plain USB-serial adapter | 3.3 V, **1,500,000 baud** 8N1 on the Core3566 (the boot ROM, U-Boot and the kernel all talk here). Cross the wires: TP34 to the adapter's RX. Many CP2102 and all FT232/CH340 adapters do 1.5 Mbaud; older PL2303 do not. `picocom -b 1500000 /dev/ttyUSB0` |
| Lamps | D13 green: +5V is up (charger, fuse and boost all pass power). D1 red: charging; blinking at 1 Hz means a charger fault. D2 green: module activity | First thing to look at |
| Rails | TP1 VBUS, TP3 VBAT, TP2 VSYS, TP17 VSYS_LIM (after the fuse), TP4 +5V, TP11 +3V3, TP12 +1V8 | Follow the power from left to right; the first rail that is missing names the block at fault |
| System I2C | TP36 SCL, TP37 SDA, TP5 ground | Charger 0x6A, gauge 0x36, codec 0x10, keyboard 0x34. Any 3.3 V I2C adapter can scan the bus while the module is held in reset (SW5), as long as +3V3 is up |
| BOOT and RESET | SW4, SW5 | SW4 held at power-on: USB loader on the USB-C port (`rkdeveloptool`), so a module with a broken image can be reflashed in place |
| Hard power-off option | C90, R91, D9 (not fitted) | Fit them if a module cannot be woken after `poweroff`: holding the power button then cuts the battery fuse for a moment |

The board can be powered with no pack (USB only) and with no module, so each block is brought up on its own.

## Phase 4: carrier, without the module first

| Step | Check | Expected |
|---|---|---|
| 0 | Before anything is plugged in: with a meter on the **loose pack plug**, find which contact is positive and which the thermistor (about 10k to the negative lead), and compare with the +, T, - marks at J10 | Red lead on the + mark. If not, move the crimp contacts in the plug housing; do not plug it in. Reversed, the pack would destroy the charger |
| 1 | Resistance VBUS, VSYS, VBAT, VSYS_LIM, +5V to ground | No shorts (hundreds of ohms or more) |
| 2 | USB power, no pack, no module | VSYS about 3.65 V; VSYS_LIM the same; +5V 5.0 V at TP4; D13 lit; BOOST_PG high |
| 3 | Load +5V at TP4 in steps up to 0.5 A | Stays within 4.75-5.25 V. (On USB alone the input limit of 0.5-0.83 A is what gives way first) |
| 4 | Connect the pack | D1 lit; pack current below 1.4 A; TP8 between 30 and 74 % of TP7 |
| 5 | With the pack: load +5V up to 2 A, then find the fuse limit with a load on VSYS_LIM (TP17) | +5V holds; the fuse limits near 3.0 A (2.6-3.4 A) and BATT_OC_N goes low; it retries by itself |
| 6 | Unplug USB | +5V stays up from the pack; the boost turns off near 3.0 V at VSYS |
| 7 | Hold the power button 12-18 s on battery | VSYS drops for about half a second (charger reset) |
| 8 | I2C scan at TP36/TP37 (needs 3.3 V on TP11 from a bench supply through 100 ohm, since there is no module) | 0x6A charger, 0x36 gauge, 0x10 codec |

## Phase 5: carrier with the module

Before fitting the module on the new carrier, on any stock CM4 carrier: measure the idle voltage of module pin 55
(UART TX) and pin 80 (I2C). Both must be 3.3 V; the carrier's pull-ups R40/R41 and the console level assume it.

Console on J8 or TP34/TP35 at 1,500,000 baud first: the boot ROM prints there before anything else works, so a
silent console with D13 lit and 3.3 V on TP11 points at the console wiring, not at the module. Then, in order:
boot from microSD; I2C devices; display and touch; backlight PWM; keyboard through the flex; audio out, jack
detect, mic; charger and gauge drivers with `ti,use-ilim-pin` and `ti,charge-current`; USB device mode; buttons;
slider switch; suspend current of the whole device; temperatures in the closed shell.
