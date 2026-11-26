# Risks

Ordered by how much they threaten a working rev 0.1.

| # | Risk | Why it matters | What reduces it |
|---|---|---|---|
| 1 | **The carrier needs a respin** | Unbuilt, unrouted, designed without lab time. The audit found seven blockers in the first draft | The audit and [audit-status.md](audit-status.md); footprint review on paper; power chain tested without the module; expect two revisions |
| 2 | **No mainline device tree for the Core3566, and a panel without a mainline entry** | Display bring-up is new driver work on a module whose vendor says DSI supports "only official displays" | Phase 1 on a stock IO board before ordering the carrier. Radxa CM4 and ArmSoM as fallbacks have their own gaps |
| 3 | **The battery fuse is tight** | The Jauch pack is rated 2 A, so the fuse U13 limits at about 1.86 A: about 5-7 W for everything, depending on battery voltage. A module peak above that drops the 5 V rail and resets the device | Measure the module's real peak at bring-up; cap the CPU frequency or the backlight if needed; a pack with heavier leads later |
| 4 | **Heat in a sealed shell with the back covered** | 2-3 W, plastic prototype, hot spot over the SoC | [thermal.md](thermal.md): PETG, spreader, frequency cap, aluminium later |
| 5 | **Slider durability** | Printed rails, magnet detents of unknown force, and a flex cable with no rated life | Fit mule and a cycling rig; spring-pin fallback pads on the keyboard |
| 6 | **Supply of the display** | 10 units in stock at one vendor | Buy spares; the AMOLED and the 4.3" Focus part as alternatives |
| 7 | **Battery life short of "all day"** | About 3-4 h browsing, estimate | Working suspend; a 6 nm-class SoC in a later board |
| 8 | **Thickness** | 19.35 mm against the N810's 14 mm; David wants it thinner. The jack (5.0 mm) and the battery header (4.9 mm) now set the cavity, with the module (4.5 mm) just under them | Clear the parts under the display tail (0.7 mm); lower jack, battery connector and module (up to 1.4 mm more before the 7.4 mm pack sets it); AMOLED step (about 2.7 mm, estimate) |
| 9 | **Unverified part details** | Jack pole assignment, panel tail fold, connector land patterns, diode height | [footprint-review.md](footprint-review.md); samples before boards |
| 10 | **Part churn** | Module prices rose from $56 to $78-126; every eMMC SKU out of stock | CM4 pin-out keeps other modules possible, within the limits in the pin matrix |
