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

- **The battery must never be asked for more current than it is rated for.** For the chosen cell that is 1.5 A
  discharge and 1.5 A charge. Rev 0.1 limits both in hardware: the charger's input cap for charging, and a current-limited switch (U13,
  1.3 A typical) for discharging. See [power-budget.md](power-budget.md), "Keeping the cell inside its rating".

## Nice to have

- Cellular with T-Mobile Band 71, as a later module. GPS.

## Targets, and where rev 0.1 stands

| Item | Target | Rev 0.1 model | Note |
|---|---|---|---|
| Footprint | 128 x 72 mm | 128 x 72 mm | |
| Thickness | 18-20 mm, thinner is better | 18.65 mm | N810: 14 mm. A thin AMOLED could bring it to about 14.5 mm (estimate), see [decisions/0002](decisions/0002-display.md) |
| Screen | 4-4.3", >= 800x480, capacitive | 4.0", 480x800 | |
| Keyboard | 102 x 29 mm key field + D-pad | as specified, 53 switches | |
| Key clearance | 3-4 mm from top row to screen edge | 3.5 mm | |
| Open height | about 100 mm | 107.9 mm | |
| Battery | 3000-4000 mAh | 2500 mAh | No stocked, documented cell of 3000 mAh fits. See [decisions/0004](decisions/0004-power.md) |
| Ports | 3.5 mm, USB-C, microSD | all three | One USB-C, sink only |

## Out of scope for rev 0.1

Operating system and UI work; keyboard firmware (there is none: the scanner is a fixed-function chip);
cellular; a second USB port.
