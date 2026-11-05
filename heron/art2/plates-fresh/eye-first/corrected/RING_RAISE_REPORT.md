# RING **LOWERING** REPORT — alert + coil v2 plates (2026-11-04)

**Honest naming first:** this file keeps the assigned name, but the work is the
opposite of a raise. The original brief (raise the rings ~7 px to the colour
transition) was **reversed before any knee2 file was written** — Jimmy's
follow-up clarified "too deep": in the v1 plates the waterline reads *past the
knee, too far up*; the bird is sunk too deep, its legs cut too short. No
raised-ring files exist. What shipped is a **lowering**: the waterline moved
DOWN, with a short run of each leg's own dark shin restored above it.

**Verdict: DONE, clean on both plates.** Each v2 plate reads at 1024×600 as a
heron standing knee-deep — a visible length of dark shin below the feathered
thigh, legs reaching the waterline, ripple rings seated at the leg endings.
Not a return to full legs: the restored shin is ~19 px of dark leg below the
rusty→dark transition, against ~120 px in the full-legged originals.

## What was done (local pixel work only, no generation)

Starting from the v1 knee plates (`plate_1_knee.png`, `coil_2_knee.png` —
both untouched, sha256 verified unchanged):

1. **Old rings erased** back to each plate's own paper (donor paper sampled
   from the same plate, plume strands protected — coil_2's curtain passes
   beside the right ring and is pixel-intact).
2. **Shin restored from the original approved plates' own pixels** — the same
   legs, same columns, rows from the v1 leg ending down 12 more px, with v1's
   own rounded leg ending translated down to close each leg (recentred on
   the shin as it stands at the new depth, so the slanted left legs keep
   their slant).
3. **Rings redrawn** in the plates' own paired-ellipse hand (78×16 outer /
   46×10 inner, same ink, same line weights), centred at the new leg endings,
   arcs passing behind the legs exactly as in v1 and in the originals' foot
   rings.

## Offsets — the rings moved DOWN 12 px on every leg

| plate | leg | ring centre v1 → v2 | leg ending (cut row) v1 → v2 | centre below rusty→dark transition |
|---|---|---|---|---|
| plate_1 (ALERT) | L | (363, 418) → (359, 430) | 422 → 434 | +7 px → +19 px |
| plate_1 (ALERT) | R | (404, 422) → (404, 434) | 426 → 438 | +7 px → +19 px |
| coil_2 (COIL) | L | (362, 419) → (356, 431) | 423 → 435 | +7 px → +19 px |
| coil_2 (COIL) | R | (401, 427) → (402, 439) | 431 → 443 | +7 px → +19 px |

Ring x-centres were recentred by −4/0/−6/+1 px respectively onto the shin as
it actually stands at the new ending (the left legs slant). The vertical move
is exactly **12 px down** on all four legs — a modest length in the class
Jimmy described ("a little too deep"), chosen by eye against the v1 plates,
the full-legged originals, and the library's knee-deep frames: at −8 px the
shin still read as a nub; at −16 px the legs started to read long; −12 px is
where the bird stands *at* the knee in the picture.

## Verification

- **Leg-zone diff vs v1** (threshold as the knee-correction report): plate_1 —
  1,843 px changed, bbox x 318–443, y 409–442; coil_2 — 1,854 px, bbox
  x 315–447, y 410–447. **0 px changed outside the two ring/ending bands** on
  either plate.
- **Seat check on the finished PNGs:** a dark-pixel map of the leg zone shows
  the complete paired ellipses at the new centres and **no ring pixels left
  at the old seats** (the old seats are clean paper outside the legs).
- **Untouched files, sha256 before = after:** `plate_1_knee.png`
  `54d6bb20…`, `coil_2_knee.png` `f722fd64…`, and **peak was never opened for
  writing** — `peak_3_knee.png` still hashes `8825b3c2…`, identical to the
  knee-correction report's record.
- **Eye verdict (mine, full plates at 1024×600 + leg-zone maps):** the birds
  stand in the water instead of on it — feathered thigh, then a believable
  length of dark shin entering rings that sit at the leg endings. No ghost of
  the old ring position, no seam where the shin was extended (the extension
  is the original plate's own shin, continuing its own scale pattern), no
  difference in paper character inside vs outside the edited bands.

## Deliverables

- `plate_1_knee2.png` — sha256 `a3c02028…`
- `coil_2_knee2.png` — sha256 `81783001…`
- This report. (v1 files remain on disk untouched; peak_3_knee.png remains
  the approved peak, as instructed.)

## Disclosure

One judgment call, named: the 12 px depth was my eye's pick within Jimmy's
"a little" — if he reads v2 as now too shallow or still too deep, the same
defined move re-runs at any other depth in the same bands, nothing else on
the plates changes.
