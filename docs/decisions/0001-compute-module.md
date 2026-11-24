# 0001 Compute module

**Status:** default chosen in the brief (LuckFox Core3566). Alternatives remain open questions.

## Context

Low power and cool running matter more than speed; it must browse the web; mainline Linux with an open GPU driver
is strongly preferred; the module is bought, not designed. A key goal was a carrier that also takes RK3576
modules, so a buyer can choose battery life or power.

## Options

| Option | For | Against |
|---|---|---|
| **LuckFox Core3566** (RK3566, 4x A55, Mali-G52 with Panfrost) | CM4 format; $84 with Wi-Fi (2026-11-24); modest heat | No mainline device tree; vendor says DSI supports "only official displays"; no schematic published; all eMMC SKUs out of stock |
| Radxa CM4 (RK3576) | Follows the CM4 pin-out closely; more power | No mainline device tree yet; hotter |
| ArmSoM-CM5 / BPI-CM5 Pro (RK3576) | Mainline device tree | Pin-out differs: no backlight PWM or audio on this carrier |
| BigTreeTech CB2 (RK3566) | Mainline device tree | Not drop-in: 200 mA 3.3 V rail, no PWM on pin 48, I2S elsewhere |
| Waveshare Core3566 | Assumed the same module resold | Was out of stock |
| Pine64 SOQuartz | Best mainline support | Pine64 halted Linux hardware production |
| Raspberry Pi CM4/CM5, RK3588 modules | - | Too hot and power-hungry for a sealed pocket device |
| Olimex iMX8MP, Variscite DART-MX8M-MINI, i.MX 93, SpacemiT K1 | - | Hotter, quote-only, no 3D GPU, or immature (from the brief) |
| Solder-down RK3566 (Boardcon CM3566, 2.8 mm) | About 2.3 mm thinner | Quote-only; no upgrade path; no mainline device tree |
| Solder-down Qualcomm QCM6490 (Thundercomm, Quectel) | 6 nm, strong mainline support, Band 71 on one variant | Quote-only or about EUR 500 each in reel quantities; private design documents; 600+ pad packages. Researched 2026-11-24 |

## Choice

LuckFox Core3566 on a carrier whose pins were verified for it and for the Radxa CM4
([compute-pin-matrix.md](../compute-pin-matrix.md)).

## Why

It is the cheapest in-stock CM4-format RK3566 with on-module Wi-Fi, and the CM4 format keeps the RK3576 path.

## What the audit changed

The "common pin subset" holds for Core3566 and Radxa CM4 only. ArmSoM-CM5 needs different stuffing and loses
backlight PWM and audio. The CB2 is not compatible.

## What would change this

Phase-1 measurements showing the Core3566 cannot suspend or cannot drive the panel; a mainline device tree
appearing for another module; a QCM6490-class module becoming buyable in small numbers with public documents.
