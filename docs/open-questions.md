# Open questions

Phrased so they can be put to viewers. Decisions already taken are in [decisions/](decisions/).

## For the community

1. **Thin or long-lasting?** Rev 0.1 is 20.05 mm with a 2800 mAh pack that can deliver 5.6 A. A thin AMOLED and a
   thinner cell could reach about 14.5 mm with about 1850 mAh. Which would you carry?
2. **Which screen?** The 4.0" Focus panel has a mainline-ready controller but is thick (4.25 mm). The 4.39"
   AMOLED is 0.75 mm but needs two new drivers and an extra power chip. Do you know a thin 4" DSI panel that is
   in production, sold in ones, and has a mainline driver?
3. **Which module?** LuckFox Core3566 (cheap, no mainline device tree), Radxa CM4 (RK3576, more power), or
   something else in CM4 format? Does a mainline device tree matter more than price?
4. **A phone-class chip?** A Qualcomm QCM6490 would be faster and far more efficient, and has good mainline
   support, but its solder-down modules are quote-only with private documents. Does anyone know a way for a
   small open project to buy and design with one?
5. **Keys: tact switches or metal domes?** And 2.4 N, 1.8 N or 1.6 N?
6. **The layout.** Number row, Fn legends on the plate, D-pad on the left: what would you change?
7. **How should a slider last?** Printed rails or metal? Is a 1.9 mm rolling loop in a 0.07 mm flex enough, or
   would you use sliding spring contacts and no cable at all?
8. **Heat.** How should a sealed handheld shed 2-3 W when the keyboard covers its back?
9. **Battery.** Cells of this size are mostly rated for 0.6-1 times their capacity; we use a 9.5 mm two-cell BAK
   pack to get 5.6 A. Do you know a thinner 50 x 68 mm cell with a datasheet rated for 4 A or more, or a maker who
   sells custom packs in small numbers?
10. **USB.** One sink-only USB-C port. Is a host port (for a mouse or a drive) worth the hub, the power switch and
    the board space?
11. **Cellular.** Wi-Fi only for now. Band 71 later: which modem?
12. **The underside.** The keyboard PCB is the bottom of the device. Leave it as bare board with artwork, or cover it?

## Settled without parts (2026-11-25)

| Item | Outcome |
|---|---|
| Stack-up and pair geometry | JLCPCB JLC04101H-3313. DSI 0.10 / 0.15 mm = 100 ohm, USB 0.12 / 0.12 mm = 89 ohm, by field solution (`hardware/scripts/impedance.py`) |
| Module height, SoC position | From LuckFox's 3D model: 4.50 mm mated, SoC lid 3.6 mm. The cavity leaves 1.0 mm over the module; the thermal pad is 1.9 mm |
| Module sockets and spacers against the module | LuckFox's model laid over the board: within 0.04 mm |
| MAX17048, JST SH, Molex 5268, Wuerth spacer land patterns | Match their drawings ([footprint-review.md](footprint-review.md)) |
| 1N4148W4 height | 0.55 mm max; the real limit under a pressed keycap is 0.77 mm |
| Panel and touch pin order | Match the Focus LCDs specification |
| Battery never drawn beyond its rating | eFuse at 3.0 A against a 5.6 A rating; charge capped at 1.25 A in hardware against 1.4 A |
| Current in the power copper | `hardware/scripts/power_paths.py`: see [carrier-board.md](carrier-board.md) |
| Crosstalk between auto-routed signals | `hardware/scripts/coupling.py`: see [carrier-board.md](carrier-board.md) |
| Device-tree requirements | Collected in [device-tree.md](device-tree.md) |
| Fabrication files show what the board files show | `hardware/scripts/gerber_check.py`, an independent Gerber reader |

## Still open: design

| Item | Blocks |
|---|---|
| Confirm the BAK pack can be bought (Farnell 2401855) and at what price | Purchasing |
| Keystone Mini dome land pattern | Only the dome keyboard variant, which is not part of rev 0.1 |
| Whether JLCPCB's flex uses rolled-annealed copper | Flex life; cycle-test the cable |
| Top-plate retention lips, button caps, snap hooks on the cell side | Fit mule |

## Decisions that are David's

Body thickness targets; any change to the decision records; licences; spending. The AMOLED step needs him to ask
DisplayModule for the SD5207 start-up sequence.

## Only a real part can settle these

None of them stops the first boards from being made: the "If it goes the wrong way" column is what the board
already provides. See [review-2026-11-25.md](review-2026-11-25.md) for where each came from, and
[bring-up-plan.md](bring-up-plan.md) for the bench steps.

| Question | How to settle it | If it goes the wrong way |
|---|---|---|
| Battery plug polarity. The documents agree: the pack datasheet shows red, yellow (thermistor), black with red at Molex circuit 1, and J10 is wired that way. What a document cannot show is whether the pack that arrives was assembled to its drawing | Voltmeter on the loose pack connector before the first plug-in | Move the crimp contacts in the plug housing before it is ever plugged in. This is the one check that must not be skipped: reversed, the pack destroys the charger |
| Do the pack's leads turn within 2.6 mm of its end, and does the plug fit the space kept for it over the top strip? | Fit check with the real pack | The leads are re-dressed or shortened; the header itself has room for the mated plug |
| Pack thermistor beta (TH1 value assumes 3380) | Resistance at 25 and 45 degC | The charge temperature window shifts by a few degrees; the divider resistors at TS are changed to suit |
| PJ-342: four poles as its circuit diagram says, or three as its outline drawing suggests? | Continuity with a TRRS plug in a sample jack | Headphones work either way; the microphone needs four poles. Straps R60-R63 select the sleeve terminal |
| Core3566 pin 99: enable input, output, or unconnected? Does RUN_PG restart a powered-off module? | Measurements listed in the review, on any carrier | The power button also reaches a GPIO (pin 41) and the charger's /QON; fit C90, R91, D9 for a hard power cycle |
| Core3566 I/O voltage on pins 21, 51, 55, 80, 82 (the SoC's PMU I/O bank): 3.3 V or 1.8 V? | Idle voltage on pin 80 or 55. If 1.8 V: R40/R41, the debug UART level and D2 are wrong | Measure before the module goes on this carrier. At 1.8 V: refit R40/R41 to +1V8 by wire, use a 1.8 V serial adapter, leave D2 out |
| Core3566 SD pins with eMMC fitted; USB device mode without a VBUS-detect pin | On a stock carrier | The no-eMMC module is the one specified; USB device mode can take VBUS presence from the charger |
| BQ25895 "USB100" 2-minute timer with a dead battery and no module | Bench: does charging continue past a few minutes | Plug in with the module fitted, or with a pack that is not flat |
| Core3566 heights (SoC lid, tallest inductor) and SoC position: taken from LuckFox's STEP model | Calipers | 1.0 mm of air over the module in the model; the thermal pad thickness follows the measured gap |
| Display tail reach to J4 (nominally 0.7 mm of slack) and tail thickness | Fit check with the real panel | J4 can be re-placed in the generator (one coordinate) for a second revision; 1.6 mm is free under a tail |
