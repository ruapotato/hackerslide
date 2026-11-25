# Open questions

Phrased so they can be put to viewers. Decisions already taken are in [decisions/](decisions/).

## For the community

1. **Thin or long-lasting?** Rev 0.1 is 18.65 mm with 2500 mAh. A thin AMOLED could reach about 14.5 mm with about
   1850 mAh. Which would you carry?
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
9. **Battery.** The only documented off-the-shelf cell that fits allows 1.5 A. Do you know a 50 x 60 mm cell with
   a datasheet and a higher rating, or a maker who sells custom packs in small numbers?
10. **USB.** One sink-only USB-C port. Is a host port (for a mouse or a drive) worth the hub, the power switch and
    the board space?
11. **Cellular.** Wi-Fi only for now. Band 71 later: which modem?
12. **The underside.** The keyboard PCB is the bottom of the device. Leave it as bare board with artwork, or cover it?

## To verify (collected `TODO(verify)` items)

| Item | Where | How |
|---|---|---|
| Core3566 pin 99 behaviour | `carrier_design.py` | Measure on a module |
| Module mated height (datasheet text is copied from the CM4's) | `config.py` MODULE | Calipers |
| DSI and USB impedance geometry | `carrier_pcb.py` | Fab calculator, once a stack-up is chosen |
| PJ-342 pole assignment | `mklib.py`, audio sheet | Sample and a multimeter |
| Panel tail fold, contact face, pin 1 | display sheet | A real panel |
| J10 polarity against the cell | power sheet | Look at the cell's pigtail |
| MAX17048 land pattern | power sheet | Maxim 90-0065 |
| Keystone Mini land pattern | `mklib.py` | Ask Keystone |
| 1N4148W4 height | `keyboard_design.py` | BORN datasheet |
| Keyboard cable pin order through the real path | `keyboard_link` sheet | Fit mule |
| Does the Core3566 GPIO bank follow pin 78; SD with eMMC | pin matrix | Measure |
| ES8316 interrupt pin behaviour | audio sheet | Driver source and a scope |
| Whether JLCPCB's flex uses rolled-annealed copper | `fab-orders.md` | Their order form |

## Open design items

| Item | Blocks |
|---|---|
| Software power cap that keeps the module under the battery limiter (about 3 W on battery) | Usable device |
| Choose the PCB stack-up and calculate DSI/USB geometry | Carrier routing |
| Top-plate retention lips, button caps, snap hooks on the cell side | Fit mule |

## Decisions that are David's

Body thickness targets; any change to the decision records; licences; spending. The AMOLED step needs him to ask
DisplayModule for the SD5207 start-up sequence.
