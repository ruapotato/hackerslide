# Risks

Ordered by how much they threaten a working rev 0.1.

| # | Risk | Why it matters | What reduces it |
|---|---|---|---|
| 1 | **The carrier needs a respin** | Unbuilt, unrouted, designed without lab time. The audit found seven blockers in the first draft | The audit and [audit-status.md](audit-status.md); footprint review on paper; power chain tested without the module; expect two revisions |
| 2 | **No mainline device tree for the Core3566, and a panel without a mainline entry** | Display bring-up is new driver work on a module whose vendor says DSI supports "only official displays" | Phase 1 on a stock IO board before ordering the carrier. Radxa CM4 and ArmSoM as fallbacks have their own gaps |
| 3 | **Battery supply and the battery fuse** | The BAK pack's Farnell stock and price are unconfirmed. The fuse U13 limits at about 3.0 A (about 8-10 W for the module), set by the battery connector's 3 A rating; a peak above that resets the device | Confirm the pack can be bought; measure the module's peak in phase 1. See [power-budget.md](power-budget.md) |
| 4 | **Heat in a sealed shell with the back covered** | 2-3 W, plastic prototype, hot spot over the SoC | [thermal.md](thermal.md): PETG, spreader, frequency cap, aluminium later |
| 5 | **Slider durability** | Printed rails, magnet detents of unknown force, and a flex cable with no rated life | Fit mule and a cycling rig; spring-pin fallback pads on the keyboard |
| 6 | **Supply of the display** | 10 units in stock at one vendor | Buy spares; the AMOLED and the 4.3" Focus part as alternatives |
| 7 | **Battery life short of "all day"** | About 3-4 h browsing, estimate | Working suspend; a 6 nm-class SoC in a later board |
| 8 | **Thickness** | 20.05 mm against the N810's 14 mm; David wants it thinner. The 9.5 mm battery pack now sets it | AMOLED step (saves about 2.7 mm, estimate) together with a thinner battery |
| 9 | **Unverified part details** | Jack pole assignment, panel tail fold, connector land patterns, diode height | [footprint-review.md](footprint-review.md); samples before boards |
| 10 | **Part churn** | Module prices rose from $56 to $78-126; every eMMC SKU out of stock | CM4 pin-out keeps other modules possible, within the limits in the pin matrix |
