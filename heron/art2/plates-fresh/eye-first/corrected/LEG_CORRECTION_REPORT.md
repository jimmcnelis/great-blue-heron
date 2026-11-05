# LEG CORRECTION REPORT — knee-deep, all three approved plates (2026-11-04)

**Verdict: CLEAN on all three plates.** Each corrected plate reads at 1024×600 as if
originally drawn knee-deep — legs end at the intertarsal joint, one ripple ring per
leg seated at the joint, blank plate paper below, no ghosts, no seams. Peak's
bill-tip rings are bit-identical to the master (0 changed pixels right of x=600).
**The originals were never modified** — sha256 before = after on all three masters:

| master | sha256 |
|---|---|
| ranked/plate_1.png | `9da53949ddcbeafc07cce3b84f34124cee304f985acf3bd746cf73644e4c2f99` |
| coil/ranked/coil_2.png | `88b14dcec7c7c1e2cb26231cc07129994f60629587fc0c5cfbf2d268cfca8cc5` |
| peak/ranked/peak_3.png | `0944555e7850eafdd7a420819651ac208a9ff6c68a0085c8dbcd63ab77e12550` |

Corrected copies: `plate_1_knee.png` · `coil_2_knee.png` · `peak_3_knee.png`
(+ `<plate>_sidebyside.png`, original | corrected, in this folder).
Method + measurements: `work-knee/knee_correct.py`, `work-knee/measure_fix_out_knee.json`,
`work-knee/seat_check.json`.

## Method (same pipeline, per plate — local pixel work only, no generation)

1. **Joints found on the artifact**, two ways that agree: per-leg windowed tracking of the
   rusty→dark transition / width profile, then red-crosshair markers viewed at 3×.
2. **Erase**: a corridor along each shin (half-width 17 px; 19 on peak) + a full ellipse
   over each foot-ring pair, dilated 1 px to eat antialias fringe. Plume strands inside
   the erase footprint were *protected* (bluish mid-tone strokes subtracted from the mask) —
   coil_2's plume passes within ~6 px of the right ring and is untouched.
3. **Paper fill**: donor paper transplanted from the same plate's clean bottom-left
   (non-paper fraction ≤0.17%), mirror-tiled, re-tinted row-by-row to the local paper
   tone beside the legs, feathered 1.6 px. The cleared zone's tone is the plate's own.
4. **Rings redrawn in the plates' own hand**: paired concentric ellipses (outer thin,
   inner bolder — the feet's motif), slight radius jitter, supersampled 4×. Sizes matched
   to the plates' actual foot-ring proportions: 78×16 outer / 46×10 inner (alert, coil);
   86×17 / 50×10 (peak, whose foot rings run larger). Ink sampled from the plates' rings.
5. **Endings sculpted, not sliced**: the last rows of each leg are rounded off
   (quarter-ellipse cap; 5 rows alert/coil, 9 on peak) so the joint rounds *into* the ring.
   Original thigh/knuckle pixels are restored *over* the rings, so the arcs pass behind
   the leg — exactly how the plates' own foot rings behave.

## Per plate

### plate_1_knee.png (ALERT)
- **Removed**: both dark scaly shins below the joints (left leg slanted, right vertical),
  both feet, and both ripple-ring pairs at the feet.
- **Kept**: rusty thighs through the transition + ~7 px of the dark knuckle, which now
  enters the ring. Joints (rusty→dark transition): L (363, 411), R (404, 415).
- **Rings**: centres (363, 418) / (404, 422) — x-offset **0 px** from the leg centrelines;
  y-centre sits at the middle of the drawn knuckle (+7 below the colour transition).
  Independent seat check on the finished PNG: arc tips land **−1 px** from drawn position
  on both rings; outer-arc row centroids 417.6 / 421.7 vs centres 418 / 422 (≤0.4 px).
- **Confined diff**: 5,978 px changed; bbox x 293–454, y 409–563; **0 px outside the leg
  zone** (legs' columns + ring span, ≥61 px below the belly line at y=348).

### coil_2_knee.png (COIL)
- **Removed**: same inventory — both shins, feet, foot rings.
- **Kept**: thighs + knuckle nubs. Joints: L (362, 412), R (401, 420).
- **Rings**: centres (362, 419) / (401, 427) — x-offset **0 px**; arc tips **−1 / 0 px**
  from drawn; arc row centroids 418.5 / 426.4 vs 419 / 427 (≤0.6 px).
- **Confined diff**: 6,178 px; bbox x 291–454, y 410–562; **0 px outside the leg zone**.
  The plume curtain sweeping past the right leg is pixel-intact (strand protection).

### peak_3_knee.png (PEAK)
- **Removed**: both shins *below the drawn knuckles*, both feet, both foot-ring pairs.
- **Kept**: the scaly upper segment and the whole knuckle on each leg (this plate draws
  the intertarsal joint as an explicit creased knuckle; it now sits in the ring, rounded
  underside sculpted). Knuckle centres: L (334, 418), R (383, 423).
- **Rings**: centres (334, 419) / (383, 424) — offset from knuckle centres **(0, +1) px**;
  arc tips **−1 px** both; arc row centroids 418.3 / 423.4 vs 419 / 424 (≤0.7 px).
- **Bill-tip rings: untouched** — 0 changed pixels anywhere right of x=600.
- **Confined diff**: 5,966 px; bbox x 289–451, y 409–560; **0 px outside the leg zone**.

## Eye verdict (mine, at native 1024×600 and at 3× leg-zone crops)

All three read as single untouched plates. The waterline sits at the joints; the strike
room the law exists for is visible in peak — the spear works below the line while the
bird stands at it. I found no ghost of any removed shin or foot ring, no seam in any
cleared zone, and no difference in paper character inside vs outside the edited area.

## Disclosures

- **Ring placement convention**: on alert/coil the drawn anatomy has no separate knuckle
  bulge — the "joint" is the rusty→dark transition, and the ring centre is seated 7 px
  below it so the short dark knuckle the plates themselves draw sits *in* the waterline
  instead of the feathered tip hovering at the ring's top arc. On peak the centre is the
  knuckle's own centre (+1 px). If Jimmy wants the waterline exactly on the colour
  transition instead, that's a 7 px ring shift on two plates — a small, defined change.
- **Iteration history** (one method, refined in place, not re-rolls): pass 1 drew rings
  too tall (a foot-ring measurement contaminated by the foot bulb: 119×32 incl. the foot)
  and left a 1-px shin sliver on peak; pass 2 fixed sizes but left faint ghost arcs of the
  old foot rings flanking the feet and a flat slice on peak's knuckles; pass 3 (shipped)
  enlarged the foot erase to the rings' full span and sculpted the rounded endings.
- The first-pass foot measurement error is worth remembering: a dark-pixel bbox around a
  foot measures foot + both ellipses + the neighbour's interlock. Ring sizes here were
  finally set from the ellipses' own proportions, verified on the finished plates.
- Donor paper came from each plate itself (bottom-left field); no external texture,
  no generative fill, no compositing from any other image or pose.
