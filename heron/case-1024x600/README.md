# Heron 7″ creature frame — case + low dock

> **2026-11-04 — BOARD IN HAND, PROTOTYPE REVISION APPLIED.** The
> physical 7B Rev1.1 differs from several assumptions below (all USB
> is on one short edge; mics are back-facing at the corners; the kit
> speaker is an enclosed box). Verdicts + evidence:
> `RECONCILIATION-2026-11-04.md`. What changed + new print files:
> `REVISION-2026-11-04.md` and **`stl-proto2/`** (print those, not
> `stl/`, for the prototype frame; the dock is unchanged). The
> UNVERIFIED table below is kept for the record — hole pattern, USB
> position and mic positions are now VERIFIED (see the reports).

A picture-frame desk case for the **Waveshare ESP32-P4-WIFI6-Touch-LCD-7B**
(SKU 32510, BASIC — no camera), per Jimmy's form call: *stands like the
ESP32-S3-BOX-3 in its dock — upright, slight recline — but LOW.* The frame's
bottom edge sits **5 mm** off the desk; the glass's bottom edge ≈ **33 mm**
off the desk (that number is set by the panel's own bezel + the case chin,
not by a tall stand). Colour: the rose's violet — the previews are rendered
in it; the plastic colour is whatever filament you load.

Three printed parts, no supports:

| Part | File | Size (mm) | ~Filament* |
|---|---|---|---|
| Bezel tray (front frame) | `stl/bezel.stl` / `.3mf` | 183.5 × 131.4 × 16.2 | 85–95 g |
| Back cover | `stl/back.stl` / `.3mf` | 183.5 × 131.4 × 2.9 | 52–58 g |
| Low dock | `stl/dock.stl` / `.3mf` | 196 × 76 × 28 | 80–95 g |
| Fit-check corner | `stl/fit_corner.stl` | 80 × 80 × 16.2 | ~20 g |
| Hole-pattern plate | `stl/hole_plate.stl` | 179 × 112 × 1.6 | ~33 g |

\* sliced estimates at 4–5 walls / 20% infill from the verified mesh
volumes (83 / 49 / 149 cm³); the dock is the swing factor. Total for the
case ≈ **220–245 g** — a bit over the 150–200 g planning number in the
spec, because the frame is a full tray, not a clip-on bezel.

Parametric source: `src/heron_case.scad` (OpenSCAD). Every dimension that
matters is a named parameter at the top of the file. Regenerate with
`openscad -o out.stl -D part="bezel" src/heron_case.scad`
(part = bezel | back | dock | fit_corner | hole_plate | assembly | exploded).

---

## Dimensions — what is verified and what is NOT

### Verified (official Waveshare sources, fetched 2026-11-02)

| Dimension | Value | Source |
|---|---|---|
| Panel (glass/module) outline | **164.28 × 99.17 mm** | Waveshare product page, Display Specifications table |
| Active display area | **154.58 × 86.42 mm** | same table |
| SKU 32510 = BASIC (no camera) | — | Waveshare docs (docs.waveshare.com/ESP32-P4-WIFI6-Touch-LCD-7B) |
| Microphones | dual onboard MEMS (ES7210 echo-cancel) | product page, "What's On Board" #23 |
| Speaker | **loose accessory** on a PH2.0 header — *not* onboard | product page #10 + package list |
| HLK-LD2410C module size | **16 × 22 mm** | Hi-Link's own product page/manual (note: the 35 × 40 mm figure floating around is a *carrier-board* variant; the radar pocket here fits the bare module with room to spare) |

Design consequences: the display window is cut to active area + 1 mm and
centred on the panel (active area is centred on this module — standard,
and the window has margin if it's off by a mm). The panel is **captured
by the bezel lip and the back cover**, exactly like a picture in a frame.

### ⚠ UNVERIFIED — designed with clearance, must be checked at fit-check

Waveshare publishes an outline *drawing* for this board, but no numeric
hole pattern / connector coordinates in any text source we could reach
(product page, official docs, resellers). So:

| Feature | Assumption in the model | How it's covered |
|---|---|---|
| PCB mounting-hole pattern | placeholder pitch **155 × 88 mm**, Ø3.2 (`hole_pitch_x/y`, `hole_dia`) | The case does **not** depend on it. The back cover carries four 0.6 mm locating nubs at the placeholder pitch — harmless if wrong. Print `hole_plate`, lay it on the real PCB, and set the real numbers if you ever want true standoffs. |
| Total stack thickness (panel+PCB+tallest part) | **13 mm** (`stack_t`), pocket cut 13.8 deep | Measure the real stack; if > 13.8, bump `stack_t` and re-export bezel + back. |
| USB-C position on the board edge | centred (`usbc_x = 0`) | The cable path is a **46 mm-wide** notch + a full-width hollow chin raceway, so any edge position within ±20 mm of centre works. If the port is on a short edge or the back, tell Mordecai — the notch moves with one parameter. |
| Mic positions | holes at **±58 mm** in the chin (`mic_x`, toggle `mic_holes`) | Eyeball the real mic ports against the chin when the board lands; adjust `mic_x` or set `mic_holes=false` and drill the printed chin instead (it's solid 2.4 mm there). |
| RESET / BOOT buttons + power switch | assumed on a PCB edge, inside the case | Set the power switch ON before closing the case. If the buttons land on the bottom edge they'll be inside the chin/dock — flagged for the fit check; flashing is over the permanently-routed USB-C anyway. |
| BH1750 breakout size | GY-302 type, ~32 × 15 mm (typical, unverified) | Ledge + up-facing 16 × 6 slot in the top band; ledge is oversized. |

---

## Design notes

- **Form**: bezel tray + screw-on back cover + separate low dock. The
  frame drops into the dock's tilted slot (10° recline, `tilt`) and is
  held by gravity + a snug slot (0.8 mm clearance) — same idea as the
  BOX-3 stand, no fasteners. Footprint 196 × 76 mm; the frame's centre of
  mass sits well inside it.
- **Cable**: right-angle USB-C plugs into the board inside the case, runs
  in the hollow **chin raceway**, drops through the frame's bottom notch
  into the dock's interior channel, and exits the **back of the dock**
  (48 mm slot). Nothing hangs off the frame's silhouette.
- **Cooling** (~3 W): 30-slot vent field + top row in the back cover,
  six chimney slots through the top band, and the dock holds the frame's
  back clear of the desk. (Exact SoC position is under the vent field's
  span; the field is deliberately broad.)
- **Speaker**: the kit's loose speaker tapes inside the back cover over
  the slot grille at lower-left (foam tape; position approximate — it's
  behind a grille field, exact spot isn't critical).
- **Radar provision (deferred sensor)**: inside the chin, a pocket with
  locating ribs holds an LD2410C flat against a **1.2 mm thin section**
  (30 × 18 window) in the front face — radar-transparent, no reprint when
  the sensor arrives. Window sits left of centre; mics are at the chin
  ends. The chin is why the frame has a "forehead-in-reverse" — it also
  gives the creature a face.
- **Light provision (deferred sensor)**: BH1750 ledge inside the top of
  the pocket + up-facing window slot in the top band.
- **Case hardware — M3 throughout**: the back cover closes with
  **4 × M3×8 screws into brass heat-set inserts** (pilot Ø4.3 mm, in the
  bezel's corner blocks). Heat-set chosen over self-tap: this cover will
  come off more than once (sensors bolt on later), and inserts don't chew
  up PETG/PLA the way self-tappers do. Jimmy's M3 kit covers the screws;
  inserts are the standard M3×5.7 type.

## Print settings

- **Final: PETG** (Jimmy's ruling). **Prototype: PLA** — see the delta
  section below; the STLs are the same files either way.
- Layer 0.2 mm, walls 4–5 (wall stock is 2.0–2.4 mm, so it's mostly
  perimeter anyway), infill 20% gyroid on the dock, 15–20% elsewhere.
- Orientations (all support-free):
  - **Bezel**: front face **down** on the bed, pocket up.
  - **Back cover**: outer face **down**, rim up.
  - **Dock**: bottom **down**, slot up. The internal cavity roof has two
    printed ribs; a whisper of sag inside is invisible and harmless.
- Bed: X1 Carbon textured PEI is fine for both plastics; PETG wants the
  usual care (dry filament, no glue-stick needed on textured PEI).

## PLA prototype vs PETG final — the fit delta

The SCAD tolerances are the **PETG-final** values
(`fit_clear = 0.6` per side on the panel pocket, Ø3.4 screw clearances,
Ø4.3 insert pilots). PLA shrinks less than PETG (~0.2–0.3% vs ~0.3–0.6%;
across 165 mm that's roughly **0.3–0.5 mm total**), so expect from the
PLA prototype:

- Panel pocket: fits ~0.2–0.3 mm **looser** per side than the PETG final
  will (good — prototype errs roomy; foam tape takes it up).
- Dock slot: similarly a touch looser; the frame may rock a hair more
  than the final will.
- Insert pilots and screw holes print ~0.1–0.2 mm **tighter** in PLA:
  inserts will feel snug going in — that's normal, and the PETG final
  will be the easier fit. Don't judge insert fit by the prototype.
- If you'd rather preview the *final* fit from the PLA run, set
  `fit_clear = 0.35` before exporting — that pre-shrinks the clearances
  to roughly what PETG will give you at 0.6. One number, top of the file.

## Assembly order

1. Print `fit_corner` + `hole_plate` first (next section) and verify.
2. Press/solder the 4 heat-set inserts into the bezel corners.
3. Set the board's power switch **ON**. Plug the right-angle USB-C in.
4. Lay the board into the bezel pocket (glass against the bezel lip;
   a strip of thin foam tape on the lip makes it snug and silent).
   Route the cable into the chin raceway. Fit the speaker (tape inside
   back cover over the grille) and plug its PH2.0 lead in.
5. *(When sensors arrive: LD2410C into the chin pocket, BH1750 onto its
   ledge — both from inside, no new prints.)*
6. Back cover on, 4 × M3×8. Don't gorilla them — snug is enough.
7. Drop the frame into the dock; feed the cable out the dock's back.
8. Stick 4 rubber pads (Ø10 recesses in the dock floor) if it slides.

## Fit-check plan (do this when the board lands, before the full set)

1. **`fit_corner.stl` (~20 g, ~35 min)** — one real corner of the bezel.
   Check: panel corner slides into the pocket with light finger pressure
   (target: no force, no rattle); an M3 insert presses into the pilot
   and holds; chin depth vs the board's bottom edge; mic holes vs the
   real mic ports (mark the error on the print, read `mic_x` off it).
2. **Measure the stack**: calipers on panel+PCB+tallest component.
   Must be ≤ 13.8 mm, else bump `stack_t`.
3. **`hole_plate.stl` (~33 g)** — lay it on the PCB. If the 4 holes sit
   on the real holes, the placeholder pitch was luck; if not, measure
   the true pitch, set `hole_pitch_x/y`, re-export the back cover only.
4. **USB-C**: note the port's edge + offset from centre; must be within
   ±20 mm of centre on the bottom edge for the stock notch, else set
   `usbc_x`.
5. Only then print bezel + back + dock for real.

## Verification done on this design (2026-11-02)

- All STLs load and are **watertight/manifold** (trimesh).
- Bounding boxes match design intent: bezel & back 183.4 × 131.3 mm;
  dock exactly 196.0 × 76.0 × 28.0 mm.
- Dock cross-sections ray-checked at several heights: front/back cheeks
  solid, slot void 24.3 mm wide at the top (frame 18.4 + clearance, at
  tilt), cable cavity + rear exit connected.
- Renders are OpenSCAD preview renders in the case colour (rose violet):
  `renders/assembly_front.png`, `assembly_back.png`, `exploded.png`,
  `dock.png`. The dark panel in them is a dummy — the real glass is
  blacker and glossier, obviously.
