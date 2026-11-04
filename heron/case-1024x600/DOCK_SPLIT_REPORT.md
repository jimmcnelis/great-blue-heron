# Dock split — two snap-together halves (2026-11-03)

Jimmy's call: *"build the base as 2 parts that snap together so we can
limit the printing of supports in the cavity."*

The one-piece `dock` remains in the SCAD as the reference solid
(`dock_geometry()`; `part="dock"` exports it byte-identical to before —
516 facets, same bbox, re-verified after the refactor). The two new
parts are **clips of that same solid** at the seam plane, plus snap
hardware, so every finished-dock interface is inherited, not redrawn:

- **`dock_lower`** — everything at/below z = 12: the open-top tub
  (floor, walls, cable exit, pad recesses, frame shelf + its ribs).
- **`dock_upper`** — everything above z = 12: frame slot, lightening
  pocket, top skin, roof ribs.
- Seam plane **z = 12** = the interior cavity's roof line. The whole
  cable path (cavity floor z 2.5, exit z 2.5..10.5, frame shelf) lives
  in the lower half; the exit cut is never touched by the seam.

Exports: `stl-fixed/dock_lower.stl` (680 facets), `stl-fixed/dock_upper.stl`
(356 facets) — each a single connected, edge-manifold mesh (0
non-manifold edges). Geometry package: `dock-split.3mf` (both parts,
one plate footprint, same packaging as heron-case-fixed-v2).

## 1. Cable passage — ray test on the assembled pair

Same test that caught the 2026-11-03 membrane bug: rays from inside
the cavity (y = 60) out the back at slot height z = 6.5, x = −20 / 0 /
+20, against the union of the two new meshes:

| x | one-piece dock | assembled split pair |
|---|---|---|
| −20 | no crossings — OPEN | no crossings — OPEN |
| 0 | no crossings — OPEN | no crossings — OPEN |
| +20 | no crossings — OPEN | no crossings — OPEN |

The exit is fully open in the assembled pair. Vertical seam columns
confirm the halves mate with no gap: through the side wall (x 96,
y 40) material is continuous z 0 → 28 with only the coincident seam
faces at z 12; through a locating pin (x 60, y 74) the column reads
solid to z 15.4 (pin tip), void 15.4 → 15.8 (the designed 0.4 mm
depth clearance), solid above (hole floor) — the pin/hole pair
measures exactly as drawn.

## 2. Interface audit — measured from the meshes, old vs new

| Interface | One-piece | Assembled pair | |
|---|---|---|---|
| Outer envelope | 196.0 × 76.0 × 28.0 | 196.0 × 76.0 × 28.0 | identical |
| Frame slot void at top (z 27) | 185.08 wide (x −91.74..+93.34) | 185.08 | identical |
| Frame rest — shelf top at (0, 61) | z 4.42 | z 4.42 | identical |
| Cable exit width | 48.0 (x −24..+24) | 48.0 | identical |
| Cable exit height | z 2.5..10.5 (8.0) | z 2.5..10.5 (8.0) | identical |
| Rubber-pad recesses (4×) | floor at z 0.6 (0.6 deep) | z 0.6 at all four | identical |
| Slot tilt / floor height / footprint | from shared `dock_geometry()` | same solid, clipped | identical by construction |
| Mesh volume | 148.14 cm³ | 148.52 cm³ | +0.38 = snap hardware (fingers + pins − grooves − holes) |

Deliberate deviations, all inside the cable cavity or on the seam —
**the exterior gains exactly one feature**: two pry notches on the
back face across the seam (10 mm wide × 0.8 mm deep, at x ±70) so a
fingernail or spudger can start the separation. Standalone-part
bounding boxes differ (they're halves): lower reaches z 15.4 (the
locating pins stand on its seam face), upper reaches down to z 4.6
(the snap fingers) — both inside the assembled 196 × 76 × 28 envelope.

## 3. Support claims — measured overhang scans

**Lower — print as-is, bottom on the bed. Support-free.**
Down-facing area off the bed totals ~2,000 mm², but almost all of it
is one face: the frame shelf's underside (~1,500 mm²), a 10°-tilted
plane (0.035 mm of step per 0.2 layer — a staircase, not a ceiling)
hovering 0.8–2.9 mm over the cavity floor, a face the one-piece dock
already printed as-is. Everything else is a micro-bridge: exit roof
192 mm² spanning 4 mm in y; snap-groove top faces ~73 mm² spanning
1.3 mm; pad-recess ceilings are 0.6 mm deep pockets in the bed face.
No support anywhere.

**Upper — print TOP-FACE DOWN (seam face up). Support-free.**
One correction to the obvious orientation: split-face-down is
impossible, because the snap fingers hang *below* the seam — they'd
be under the bed. Top-face down is better anyway: the lightening
pocket opens upward (no bridging at all — in the one-piece print
that pocket's roof was the support problem), the roof ribs stand on
the top skin like walls, the pin holes become shallow recesses off
the top layer, and the fingers print as posts rising from the seam
face. Measured down-facing area in this orientation: **55 mm²,
zero flat ceilings** — just the four snap barbs' cam ramps (~52°
from vertical, 0.9 mm features, standard snap geometry).

## 4. The snap design

- **4 cantilever fingers**, two per side, all on the upper half,
  hanging inside the cavity's side margins (cable channel stays
  clear — fingers occupy x 92.1..94.6 against the walls; the frame
  at z < 12 spans y 44..68 and the fingers sit at y 14..26 and
  30..42, so fingers and frame never meet).
  Per finger: **1.6 mm thick × 12 mm wide**, root embedded in the
  cheek to z 12.5, tip at z 4.6, free length root→barb ≈ 6.3 mm.
- **Barb**: 0.9 mm proud of the finger face (tip at x 94.6 vs wall
  face 94) → **0.6 mm engagement**, **0.6 mm deflection** on
  assembly. Peak strain ≈ 1.5·t·δ/L² ≈ **3.6%** — inside PETG's
  repeated-snap comfort zone. Ramps ~38° both ways: lead-in for
  assembly, cam-out for release.
- **Grooves** (lower side walls): 1.3 mm deep into the 4 mm wall —
  **2.7 mm of wall remains**; 14 mm long (1 mm clearance per side);
  barb tip clears the groove floor by 0.7 mm (never bottoms out).
- **Running clearances**: finger face to wall 0.3 mm; barb z-band
  5.5..6.0 centred in the groove's 4.7..6.9.
- **Locating**: 4 pins on the lower's seam ring (front + back wall
  tops, x ±60) — Ø3.2, 2.6 straight + 0.8 cone tip — into Ø3.6
  holes in the upper: **0.2 mm radial clearance**, 0.4 mm depth
  clearance (ray-verified above). Pins engage 3 mm before the barbs
  snap, so alignment is forced before anything flexes.
- **Assembly**: set the upper on, pins find their holes, press
  until four clicks. **Separation**: firm straight pull — the 38°
  release ramps cam all four barbs out together; the back-seam pry
  notches give a fingernail purchase to start it. No glue, no
  screws, nothing to wear except the barbs themselves.
- **Honest weak points**: retention is a cam fit, tuned for hand
  release, not a lock — a hard yank on a routed cable could pop the
  top (arguably a feature: it pops instead of tearing the frame
  out). Release force can't be measured until it's printed; PETG
  stiffness varies by brand and dryness. If the joint proves too
  soft or too stiff, the knob is one number — barb height in
  `dock_snap_finger()` (tip x 94.6; ±0.2 mm roughly doubles/halves
  the snap feel). The seam reads as a straight 0.0-gap line at
  z 12 — the two halves are clipped from one solid, so the outside
  faces are coplanar by construction.

## 5. What did not change

Bezel and back cover: untouched. The one-piece `dock` part selector
still exports the original solid (re-verified identical after the
refactor). `assembly` / `exploded` previews still use the one-piece
dock. The frame shelf stayed in the lower half exactly where the
one-piece dock has it (measured z 4.42, §2) — it did not need the
roof-ring move the brief suggested, because it already lives at
z 1.7..5.4, entirely below the seam.
