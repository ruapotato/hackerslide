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

1. Routing is complete on both boards ([routing-status.md](routing-status.md)); the pair geometry is calculated for
   JLCPCB's JLC04101H-3313 stack-up, which therefore has to be the one ordered.
2. Review: done by scripts and independent AI reviewers, not by a person ([review-2026-11-25.md](review-2026-11-25.md)).
   What is left can only be settled with parts in hand; each such item has a bench step in
   [bring-up-plan.md](bring-up-plan.md). The first boards are prototypes: expect a second revision.
3. Order a few of each connector and the pack first, lay them on a 1:1 print, and measure the pack plug's polarity.
4. Gerbers and assembly files: `fab_outputs.sh`, then `gerber_check.py`.
