# Heron case — prototype revision spec (2026-11-04 evening)

Written after Jimmy unboxed the board and photographed it (main chat,
2026-11-04 19:52 UTC). Supersedes the fit assumptions in this folder's
README.md where they conflict. Jimmy's prototype rulings, same evening:
**do not seat the board in the current tray; side plug is fine for the
prototype; dock stands as-is; printer is free — he wants the print
started, hardware in hand.**

## Verified from Jimmy's photos (read 2026-11-04 ~20:35 UTC)

- Board silkscreen: **ESP32-P4-WIFI6-Touch-LCD-7B, 1024x600 Pixels,
  Rev1.1**, ESP32-P4-Core, Flash 32MB. This IS the correct BASIC board.
- **CAMERA FPC socket is empty — no camera module fitted.** The
  no-camera rule is satisfied; the mic exception stands (MIC1 bottom-left
  corner, MIC2 bottom-right corner of the PCB).
- **Right edge carries the whole USB stack + power**: top to bottom —
  C6-UART header, ON/OFF power switch, USB-OTG (full-size USB-A socket,
  the tallest part on that edge), USB-C, USB TO UART. Nothing about USB
  is on the bottom edge.
- Left edge: I2C / UART / CAN / RS485 JST connectors protrude past the
  PCB outline. Bottom edge: two GPIO breakout headers + TF card slot.
- **Speaker is an enclosed dual-driver box** with four mounting ears and
  a 2-wire lead (plugs into the SPK header, top-left of the board) —
  not the loose driver the case planned to tape inside the back cover.
- Kit bag (photo 3): USB cables + a multicolour GPIO jumper harness.

## What this breaks in the current case (README.md, 2026-11-02 design)

1. `usbc_x = 0` centred + 46 mm chin notch + hollow chin raceway +
   dock channel cable route — **wrong edge entirely.** The design bet
   USB-C was near bottom-centre; it is on the right edge.
2. Speaker "tapes inside the back cover over the slot grille" —
   **wrong form factor.** The enclosed box needs a measured home or an
   external mount; it will not live in that spot.
3. Tray extraction: Jimmy's hands-on verdict — outline seems to fit the
   tray, but the right-edge stack would foul the wall and levering on
   the connectors risks damage taking it back out. A tray the board can
   enter but not safely leave is a trap, not a fit.

## Prototype revision (scope locked by Jimmy's rulings)

- **Bezel tray**: cut a right-side relief window in the tray wall sized
  for the full right-edge stack (USB-A, USB-C, UART, power switch) so
  the board drops in and lifts out vertically with no contact on the
  connectors, and the plugs + switch stay accessible from the side.
  Side-plug prototype: cable plugs in at the side, visible — the hidden
  chin/dock cable route is a final-version refinement, NOT a prototype
  blocker.
- **Back cover**: matching right-edge clearance so the cover closes
  without pressing on the USB-A socket's height.
- **Dock: untouched.** It grips the frame, not the board; Jimmy ruled
  the side plug acceptable, so no dock change for the prototype.
- **Speaker box**: no geometry until it is measured (verify inputs
  before building). Default prototype option if it doesn't fit the
  back-cover depth: external mount under/behind the frame rather than
  forcing it inside.

## The only measurements that unlock print-ready files

Jimmy has the hardware in hand; these three ruler reads are the gate:

1. **Speaker box**: length × width × height, including the mounting
   ears.
2. **Right-edge stack**: distance from the board's top-right corner to
   the centre of the USB-A socket, and how far the USB-A socket stands
   proud of the PCB (above its face / past its edge).
3. **PCB outline** width × height — confirmatory only; Jimmy already
   reports the outline seems to fit the tray (183.5 mm wide), so if
   this one is skipped the revision proceeds on the panel outline
   (164.28 × 99.17 mm) already verified from Waveshare.

## Hold points (unchanged)

- No flashing: bench power-on in factory state only, per
  `../board-arrival-checklist-2026-11-04.md` §3. Firmware still waits
  on the ankle-plate art package, which is not yet approved.
- Do not seat the board in the current printed tray.
