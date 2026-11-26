# Requirements

From David's brief (2026-11-24) and spec (2026-11-20). "Must" items are his hard requirements.

## Must

- Pocketable Linux handheld in the spirit of the Nokia N810: landscape screen, slide-out QWERTY keyboard with a D-pad.
- Low power and cool running beat CPU speed. It needs to browse the web acceptably.
- 3.5 mm headphone jack and a microSD slot.
- Keyboard slides on rails with magnet detents. No spring.
- Every part in active production. No end-of-life parts.
- Runs mainline-ish Debian/Mobian. A mainline GPU driver is strongly preferred.
- Off-the-shelf compute module on a custom carrier, assembled by the fab. David hand-solders large parts only.
- Form factor and efficiency win over "every blob open" when they conflict.

## Added by David, 2026-11-24

- **The battery must never be asked for more current than it is rated for.** For the chosen pack that is 5.6 A
  discharge and 1.4 A charge. Rev 0.1 limits both in hardware: the charger's input cap (0.83 A maximum, which keeps the pack under
  1.25 A whatever software does) for charging, and an eFuse (U13, about 3.0 A) for discharging. See [power-budget.md](power-budget.md), "Keeping the cell inside its rating".

## Nice to have

- Cellular with T-Mobile Band 71, as a later module. GPS.

## Targets, and where rev 0.1 stands

| Item | Target | Rev 0.1 model | Note |
|---|---|---|---|
| Footprint | 128 x 72 mm | 128 x 74 mm | 2 mm longer for the battery leads and plug (David 2026-11-25) |
| Thickness | 18-20 mm, thinner is better | 20.05 mm | N810: 14 mm. The battery pack sets it: 9.5 mm plus 0.3 mm for swelling. A thin AMOLED could save about 2.7 mm (estimate), see [decisions/0002](decisions/0002-display.md) |
| Screen | 4-4.3", >= 800x480, capacitive | 4.0", 480x800 | |
| Keyboard | 102 x 29 mm key field + D-pad | as specified, 53 switches | |
| Key clearance | 3-4 mm from top row to screen edge | 3.5 mm | |
| Open height | about 100 mm | 109.9 mm | |
| Battery | 3000-4000 mAh | 2800 mAh min, 3000 typical | BAK LP-454965-2P-3M pack. See [decisions/0004](decisions/0004-power.md) |
| Ports | 3.5 mm, USB-C, microSD | all three | One USB-C, sink only |

## Out of scope for rev 0.1

Operating system and UI work; keyboard firmware (there is none: the scanner is a fixed-function chip);
cellular; a second USB port.
