# Case-vs-board reconciliation — 2026-11-04

**Subject:** the printed/designed case in this folder vs the physical
Waveshare **ESP32-P4-WIFI6-Touch-LCD-7B, Rev1.1** Jimmy unboxed
2026-11-04 (silkscreen-verified in his photo: "ESP32-P4-WIFI6-Touch-LCD-7B,
1024x600 Pixels, Rev1.1", ESP32-P4-Core, Flash 32MB — the correct BASIC
board; the CAMERA FPC socket is **empty**, so the no-camera rule holds).

**Sources:** Jimmy's three photos (board back full view; speaker +
top-edge close-up; accessories) and his hands-on fit test; the case
source (`src/heron_case.scad`) and README; Waveshare's official product
page (incl. the "outline dimensions" drawing), docs.waveshare.com
("What's On Board" / Hardware Description), and the Resources page.
Orientation note: the board's **back-view right edge is the frame's
front-view LEFT wall** — edges mirror between the photo and the case.

**Jimmy's rulings folded in:** (2026-11-04 15:08–15:09) side plug-in is
fine for the prototype → the dock's hidden cable route is a
final-version refinement, not a prototype blocker; the mission was
upgraded from verdict-only to *apply the prototype revision and
regenerate print files* — see `REVISION-2026-11-04.md` and
`stl-proto2/`. The dock stands unchanged for the prototype.

## Verdict table

| # | Item | Verdict | Evidence |
|---|------|---------|----------|
| 1 | PCB outline vs tray cavity | **FITS** (+ parameter fix #1b) | Official outline drawing: PCB envelope **164.00 × 97.00 mm**; case pocket is 165.48 × 100.37 (panel 164.28 × 99.17 + 0.6/side). The PCB is smaller than the panel it rides on in both axes, so the tray that captures the panel captures the board. Jimmy's hands-on concurs: "seems like it would fit in the tray." The catch is the edge connectors (item 2), not the outline. |
| 1b | Mounting-hole pattern | **PARAMETER FIX — applied** | Drawing: hole pitch **156.00 × 89.00** (case carried a 155 × 88 PLACEHOLDER per the README's UNVERIFIED table). `hole_pitch_x/y` now 156/89; affects only the back cover's locating nubs + `hole_plate`. Hole *diameter* is not dimensioned in the drawing (nubs don't use it; hole_plate keeps M3-class Ø3.2). |
| 2 | Right-edge connectors vs tray wall + safe removal | **REDESIGN (prototype-scoped) — applied** | **Jimmy's hands-on (primary evidence):** the USB stack on the board's right edge catches/sticks against the tray wall; he judges he'd **damage the connectors taking the board back out**. Geometry explains it: the stack's faces sit at/past the 164.00 envelope edge (drawing; photos) while the pocket allows only ~0.74 mm/side. Fix in `stl-proto2/`: full relief **window** in that tray wall (frame-y 28–117, through the wall behind the slab) + matching **notch** in the back cover incl. its rim — drop-in/lift-out with zero connector contact. The JST edge gets the same insurance (photo: housings protrude past the laminate; RESET/BOOT in the corner). |
| 3 | Power/flashing port position | **REDESIGN — resolved by ruling + item 2** | The design assumed a USB-C on the **bottom edge within ±20 mm of centre** (`usbc_x = 0`, 46 mm chin notch + raceway). Reality (docs "What's On Board" #14–16 + drawing): the power/flashing Type-C **"USB" (#15)** is on the board's **right short edge**, centre **28.85 mm from the bottom corner** (chained dims 13.57 + 15.28), between USB-OTG Type-A (#14, above) and USB-TO-UART Type-C (#16, below; also power/debug-capable). Delta: a different edge entirely (~90° and a full edge away) — in frame coords the port sits on the LEFT wall, ≈51.5 mm above the frame's bottom. The chin route cannot reach it. Per Jimmy's ruling the prototype plugs in **through the side window**; the chin raceway/notch remain in the geometry for the final version (item 7b). |
| 4 | Speaker | **REDESIGN — plan dropped for the prototype** | The case planned a *loose* speaker taped inside the back cover over a slot grille at the chin-left. The kit's speaker (Jimmy's photos) is an **enclosed dual-driver box** — one active + one passive radiator, four mounting ears, PH2.0 2-wire lead to the SPK header. No official dimensions are published (product page, docs, and resources checked; it appears only as a package accessory). Boxes of this class run ~13–20 mm thick against the ~8 mm of clear depth behind the PCB inside the closed frame — **it does not fit inside the frame**. Prototype: grille deleted, speaker lives external on its lead. Final version: a dock bay or deeper back, designed from a ruler read of the box. |
| 5 | Stack height vs 13 mm assumption | **FITS as assumed** (one ruler item open) | Tallest back features (photos + standard part heights): USB-A ≈7.0–7.6 mm above the PCB at the *edge* (freed entirely by the cover notch); PH2.0 GPIO housings ≈6 mm; RTC holder + cell ≈5 mm; C6 module ≈3 mm; TF slot ≈2.6 mm; camera FPC socket ≈1.5 mm (empty). Worst-point estimate, glass → USB-A top ≈ 12.9 mm < the 13.8 mm pocket. `stack_t` left at 13 — bumping it on an unverified number would change tray depth and break the (settled) dock slot fit. **Open:** Waveshare publishes no panel-module thickness; total stack is a ruler item (or settled by the `fit_corner` print). |
| 6 | Mic positions vs chin holes | **PARAMETER FIX — applied** | Case: holes at ±58 mm in the front chin slab (`mic_x`), assuming front-facing mics. Reality (photo): MIC1/MIC2 sit at the PCB's **bottom corners on the back face** (|x| ≈ 74 ± 3 mm from centre), behind the panel's bottom edge and **facing backward** — wrong position *and* wrong face; the chin holes could never have served them. Fix: `mic_holes = false` (solid chin = the README's drill-later fallback). A final version would port the *back cover* at the corners. |
| 7a | Dock — does the slot still serve? | **UNCHANGED** | The frame's external dimensions survive the revision exactly (183.48 × 131.37 × 18.4 mm — SCAD echo + mesh bounds), and no dock parameter changed. Both relief windows start at frame-y ≥ 28, above the dock slot's grip zone, so the dock still grips solid wall. The dock Jimmy already printed is the dock the prototype uses. |
| 7b | Dock — cable path | **Prototype: side plug (Jimmy's ruling). Final: route exists, dock exit unmoved** | Prototype power enters at the frame's left edge through the window — the dock's channel/exit are simply unused, not blockers. For the final version the hidden route *is* geometrically workable without touching the dock: power enters the left edge at frame-y ≈ 51.5; a future vertical raceway inside the left wall drops the cable into the existing full-width chin raceway → the frame's bottom notch → the dock's internal cavity → the existing raised back exit (slot z 9–17, sill 9.0 mm). No exit relocation needed; the raceway is a frame-side change for the final-version pass. |
| 7c | Dock — ON/OFF switch access | **SERVED by the item-2 window** | The board's ON/OFF switch is on the same right edge, at frame-y ≈ 109 — inside the relief window's 28–117 span. It stays reachable with the case closed and the frame docked, so the design no longer depends on the README's original note ("set the power switch ON before closing") — that note remains good practice, not a requirement. |

## What the sources could not settle — needs a ruler on the physical parts

1. **Speaker box L×W×H, including the mounting ears** — decides its
   final-version home (dock bay vs deeper back). Not published
   anywhere official; photo scale can't settle thickness.
2. **Total stack thickness** (glass front → tallest point on the
   back) — the panel-module thickness is in no fetched source.
   Settles whether `stack_t = 13` is final or bumps for the final
   version. (The `fit_corner` print is the cheap stand-in test.)
3. **USB-A centre offset + proud height** beyond the drawing's
   chain — only needed if the final version wants a *fitted* port
   opening instead of the prototype's generous window.
4. **PCB-to-panel centring** (assumed centred, ±1.1 mm) — confirmed
   in practice by `hole_plate` (156 × 89) laid on the real board.

## Bottom line

**The design is ADAPTABLE — and the adaptation is done.** The printed
frame parts from the shipped set are **superseded** for the prototype:
their solid side walls are exactly what Jimmy's hands-on test flagged,
and no parameter change to them was possible without reprinting the
tray anyway. The **printed dock is fully reusable, unchanged**. The
board itself fits the tray outline comfortably; everything that fouled
was on the edges, and the edges are now open where they need to be.
Print `stl-proto2/` (hole_plate + fit_corner first) and the prototype
is hardware-true everywhere the sources could reach — the four ruler
items above are all final-version refinements, not prototype blockers.
