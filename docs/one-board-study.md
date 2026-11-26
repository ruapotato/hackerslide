# One board in the keyboard half: study (2026-11-27)

David's idea: make the keyboard's board the whole motherboard, so the display half holds only what must be there.
The two-board design is kept on the branch `rev0.1-two-board` (tag `rev0.1-design`); `main` moves on from here.
**Everything on this page is arithmetic from datasheet heights. Nothing is modelled or laid out yet.**

Heights used: Focus panel 4.25 mm with a 0.8 mm bezel lip; module on its sockets 4.5 mm; headphone jack 5.0 mm;
Jauch pack 7.4 mm plus 0.3 mm for swelling; boards 1.0 mm; printed floors and covers 1.0 mm; key layer above its
board 2.3 mm (switch, cap, top plate); sliding gap 0.4 mm; room behind the panel for its folded tails and their
connectors 2.5 mm. "AMOLED" means a 0.75 mm panel under a 0.7 mm lens with a 0.8 mm back plate, about 3.3 mm for
the whole display half, and no panel has been chosen: see the search results when they are in.

## Three ways to arrange the same parts

| | Today (two boards) | A: battery behind the screen | B: everything in the keyboard half, like the N810 |
|---|---|---|---|
| Display half holds | panel, carrier, module, battery | panel, battery, a small display board | panel and a small display board |
| Keyboard half holds | keys | keys, motherboard, module | keys, motherboard, module, battery |
| Ports are on | the display half | the sliding keyboard half | the keyboard half, which becomes the body you hold |
| Crosses the slider | 8 slow wires | display signals **and battery current** | display signals, touch, backlight power |
| Underside | flat | stepped: deeper under the battery | flat; the module's heat goes straight into the back cover |
| Thickest column | panel 5.05 + gap 2.6 + board 1.0 + cavity 5.5 + floor 1.2 + gap 0.4 + tray 3.6 | lip and panel 5.05 + battery 7.7 + floor 1.0 + gap 0.4 + tray 3.6 | keys 2.3 + board 1.0 + module and jack 5.0 + cover 1.0, gap 0.4, display half 8.6 |
| **With the Focus panel** | **19.35 mm** | **about 17.8 mm** | **about 18.3 mm** |
| **With an AMOLED** | about 15.6-16.3 mm | about 14.4 mm (13.0 with a 6 mm pack) | **about 13.0 mm** |
| Battery it needs | any up to 7.7 mm | any; thinner helps directly | **5 mm or thinner under the board**, or up to 7.7 mm in a 38 mm wide cut-out. The Jauch pack (54 x 68) fits neither |

The N810 is 14 mm.

## What this says

1. **The display is the lever in every arrangement.** With the Focus panel no rearrangement gets below about
   17.8 mm, and B is no better than A.
2. **With an AMOLED, B reaches about 13 mm** and is the cleanest: no battery current through the moving cable, a
   flat back, and the hot part against the outside. It is also how the N810 is built.
3. **B needs a different battery again**: the keyboard's switches sit over the board, so a pack either lies under
   the board (5 mm) or in a cut-out that avoids the keys.
4. **A is the smaller step from today** if no AMOLED can be bought: it keeps the Jauch pack and saves about 1.6 mm,
   at the price of ports on the sliding half and battery current in the cable.

## What it costs, either way

- One new 4-layer board about 125 x 69 mm carrying everything that is on the carrier now, plus the keys. The
  carrier's hand-laid blocks (charger, boost, fuse, USB, display pairs) can be reused; placement and routing are new.
- A new moving cable: two display lanes and clock (six wires with controlled impedance and ground between them),
  touch and control signals, backlight and logic power, about 20-24 conductors instead of 8, on a two-layer flex.
- A small board in the display half for the panel's connectors (and for an AMOLED, its power chip).
- A new enclosure: which half is the body changes.
- The module needs 40 mm of height in a zone that has about 38-40 mm free above the key rows; the body may grow
  1-2 mm taller.

## Decisions this waits on

| Decision | Whose | Waits for |
|---|---|---|
| A or B | David | Whether an AMOLED with stock and documentation exists |
| Display | David | The AMOLED search |
| Battery for B | David | A search for 5 mm packs (or cut-out shapes) in stock |
| Pointing device and final key legends | David | The pointing-device search; see the layout proposal |
