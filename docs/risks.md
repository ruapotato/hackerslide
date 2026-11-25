# Risks

Ordered by how much they threaten a working rev 0.1.

| # | Risk | Why it matters | What reduces it |
|---|---|---|---|
| 1 | **The carrier needs a respin** | Unbuilt, unrouted, designed without lab time. The audit found seven blockers in the first draft | The audit and [audit-status.md](audit-status.md); footprint review on paper; power chain tested without the module; expect two revisions |
| 2 | **No mainline device tree for the Core3566, and a panel without a mainline entry** | Display bring-up is new driver work on a module whose vendor says DSI supports "only official displays" | Phase 1 on a stock IO board before ordering the carrier. Radxa CM4 and ArmSoM as fallbacks have their own gaps |
| 3 | **The module wants more power than the battery limit allows** | The only documented cell is rated 1.5 A. David requires that it is never exceeded, so U13 limits discharge to about 1.3 A, which leaves roughly 3 W for the module on battery in the worst case. Above that the 5 V rail drops and the device resets | Measure the module in phase 1; software power cap; a cell with a higher rating later. See [power-budget.md](power-budget.md) |
| 4 | **Heat in a sealed shell with the back covered** | 2-3 W, plastic prototype, hot spot over the SoC | [thermal.md](thermal.md): PETG, spreader, frequency cap, aluminium later |
| 5 | **Slider durability** | Printed rails, magnet detents of unknown force, and a flex cable with no rated life | Fit mule and a cycling rig; spring-pin fallback pads on the keyboard |
| 6 | **Supply of the display** | 10 units in stock at one vendor | Buy spares; the AMOLED and the 4.3" Focus part as alternatives |
| 7 | **Battery life short of "all day"** | About 2.5-3.5 h browsing, estimate | Working suspend; a 6 nm-class SoC in a later board |
| 8 | **Thickness** | 18.65 mm against the N810's 14 mm; David wants it thinner | AMOLED step (about 14.5 mm, estimate) |
| 9 | **Unverified part details** | Jack pole assignment, panel tail fold, connector land patterns, diode height | [footprint-review.md](footprint-review.md); samples before boards |
| 10 | **Part churn** | Module prices rose from $56 to $78-126; every eMMC SKU out of stock | CM4 pin-out keeps other modules possible, within the limits in the pin matrix |
