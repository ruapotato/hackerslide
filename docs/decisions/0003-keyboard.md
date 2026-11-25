# 0003 Keyboard, scanner and cable

**Status:** decided (David, 2026-11-24).

## Context

A custom keyboard of 102 x 29 mm plus a D-pad, about 50 switches, with a second PCB as top plate holding printed
keycaps. The brief proposed an RP2040 scanner presenting USB HID, with I2C as fallback.

## Scanner

| Option | For | Against |
|---|---|---|
| RP2040, USB HID | Flexible firmware; works in the bootloader | Every module has one USB port, so it forced a hub and a mux on the carrier; flash, crystal; firmware to write; USB keeps the host awake |
| **TI TCA8418, I2C** | Mainline driver, no firmware; $1.18, 30,000 in stock; four signal wires; removes six ICs across both boards | 8 x 10 matrix needs a folded mapping; no keyboard in the bootloader; Fn layer lives in the Linux keymap |
| ADP5588/5589, LM8323, MAX7360, TCA8424 | - | Not stocked, dearer, or not usable from the device tree |

**Choice: TCA8418.** David left it to the designer's recommendation.

## Switches

Alps SKSWCFE010 (fab-assembled) is the default. Keystone 5135 domes are to be compared on camera, and the dome
board exists as a placed draft, but Keystone's own lands do not fit the key pitch, so ours are non-standard and unverified. See [keyboard.md](../keyboard.md).

## Stack

**The keyboard PCB is the tray floor** (David, 2026-11-24). It took the keyboard layer from 5.6 to 3.6 mm and the
device from 20.65 to 18.65 mm. Consequences: all parts on the top side, low-profile diodes, a 125 x 69 mm board,
a bare board as the device's underside.

## Cable

| Option | For | Against |
|---|---|---|
| Stock 0.5 mm flat cable | Off the shelf | Rated for 5-10 mm bend radius; the loop is under 2 mm |
| **Our own 0.07 mm flex circuit from the PCB fab** | Same fab, drawn in KiCad; loop radius is 27 x thickness against a 10-15 x guideline | No life rating from the fab; must be cycle-tested |
| Sliding spring contacts, keyboard connected only when open | No moving cable | Pins dislike side-drag; needs a bus switch and driver re-initialisation; dust |

**Choice: the flex circuit**, with spring-pin landing pads on the keyboard as an experiment.

## What would change this

The flex failing its cycle test; a need for a keyboard before Linux boots.
