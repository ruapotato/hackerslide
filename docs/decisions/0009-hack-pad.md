# 0009 From Linux handheld to hack pad

**Status:** direction decided (David, 2026-11-27). Architecture and parts not yet chosen.

## Context

The Linux handheld reached a checked, unbuilt rev 0.1 at 19.35 mm. Three searches then showed what stands between
it and an N810-class device: no thinner compute module that can simply be ordered, no thin AMOLED in stock with
usable documentation, and a battery market that offers little at 3 A. Thickness, heat and battery life were all
set by the Linux-class processor.

## Decision

- The Linux handheld is kept, complete, on the branch `linux-handheld` (the two-board rev 0.1 as first finished is
  also at tag `rev0.1-design`).
- `main` becomes a **hack pad**: no Linux, no web browser. A microcontroller, "one of the beefiest we can put in
  it" (David), running its own firmware with a terminal and its own interface, able to run MicroPython.
- **As much of a multi-tool as is reasonable**, not a copy of the Flipper Zero: sub-GHz and NFC at least,
  software-defined radio as far as a microcontroller can take it, "as much send and receive as possible".
- MP3 music and audiobook playback from the card.
- A thin, low-power display is to be considered, e-ink among them.

## What carries over from the Linux design

The slider body and its rails, travel stop and hooks; the thumb keyboard with its next layout (N810 rows, Fn
numbers, touchpad, Esc and Tab) and its I2C scanner; charger, fuel gauge and battery fuse; the audio codec and
jack; USB-C; the card slot; the board generators, router and checks.

## Open

Which microcontroller; which radios; which display; the battery (a thinner one becomes useful once the module is
gone); whether one board or two. A parts survey restricted to parts in production with listed stock is under way.

## Rules that still hold

Every part in active production and orderable in ones with visible stock. Transmitting is regulated: the design
will say what each radio is allowed to do and will not pretend otherwise.
