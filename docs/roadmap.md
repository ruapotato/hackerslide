# Roadmap

Phases tied to the build series. Costs are estimates; nothing has been quoted or bought.

| Phase | Episode | Work | Exit test | Estimate |
|---|---|---|---|---|
| 0 | 1 | This repository: audited design, draft boards, enclosure model | Community review | - |
| 1 | 2 | Boot the module on a stock IO board; measure power, suspend, heat; light the panel | [bring-up-plan.md](bring-up-plan.md) phase 1 | $180-250: module $84, IO board, panel $77, tools |
| 2 | 3-4 | Fit mule and slider: prints, magnets, cycling rig | Slider survives the cycle test | $40-80 |
| 3 | 5-6 | Keyboard, top plate and flex cable, two revisions | Every key works; feel chosen | $150-250 |
| 4 | 7-9 | Carrier, two revisions, including a second module | Boots, charges, plays audio, suspends in the shell | $500-1,000 |
| 5 | 10 | Looks-like build: resin or MJF shell | A device to hold | $200-300 |
| - | - | Contingency, about 20 % | | $200-400 |

Total: about $1,300-2,300 (estimate; the earlier handoff said $1,300-2,200).

## After rev 0.1

- **Thin version:** AMOLED, about 14.5 mm. Needs the panel lit in phase 1 or 2.
- **820 board:** a more efficient SoC if a module becomes buyable; cellular with Band 71; a host USB port.
- **Shell:** CNC aluminium for a small batch; injection moulding only with real Crowd Supply volume.

## Before any fab order

1. Finish the routing: one connection on the keyboard; on the carrier the 72 open connections, and deliberately the
   power loops, DSI and USB ([routing-status.md](routing-status.md)).
2. Human review: [carrier-board.md](carrier-board.md) checklist and [footprint-review.md](footprint-review.md).
3. Gerbers and assembly files.
