# WARP SPIKE REPORT — coil + peak from the approved alert plate

Built 2026-11-04, one build per frame, no iteration. Method: the approved
alert plate (`keyframes-v25/keyframe_alert.png`) is the base and the ONLY
donor; its neck tube was warped station-by-station (arc-fraction ×
cross-fraction) from its own drawn centreline onto the v2.5 mechanism's
visible chain; the head was pasted as one assembly, eye-anchored; old
neck/head content outside the target pose was erased by inpainting; warped
neck luminance was quantile-remapped to the donor neck's own distribution.
Scripts + bookkeeping: `work/build_warp.py`, `work/book_coil.json`,
`work/book_peak.json`.

**Donor discipline (Jimmy's rulings, 2026-11-04 11:13/11:14):**
`keyframe_peak.png` was NOT used anywhere — not as target, not as donor, not
for its head. `audubon_strike.png` contributed nothing but the peak ink-band
reference (its measured 0.3144) and a side-by-side panel. The plume on both
frames is the alert plate's own strand work, preserved in place, never
pasted over as a mass (see Plume verdict).

## VERDICTS

**warp_coil.png — FAIL as a plate.** The geometry gate passes (grounded
chord_base 0.269, grounded arc:chord 1.97), the corridor is continuous, the
plume passes Jimmy's tell — but the composite carries two defects no gate
number can excuse: a **ghost of the alert S-neck survives as a slate
silhouette** behind/above the coil (the erase step's global content
threshold cannot see the plate's low-contrast tonal wash), and the **U-fold
self-overlaps into a woven moiré band** where the fold's centreline radius
(≈8.6 px) is smaller than the tube's own halfwidth (≈26 px). The head meets
the neck through a visibly banded column. This frame is not shippable art;
it is a successful geometry proof wrapped in a failed composite.

**warp_peak.png — FAIL as a plate, but the system works.** Geometry, head,
eye and plume all pass; the spear itself reads as engraving along its whole
shaft. It fails on ink family (0.275 vs the 0.304–0.324 band), on the same
**ghost echo** (a soft slate silhouette trails the spear's upper edge — the
old alert neck, un-erased), and on one small un-erased rectangle of donor
background at the spear's root. Of the two frames, this is the one whose
failures are all in the erase/ink layer, not in the warp.

## THE PEAK HEAD — provenance (required statement)

The peak head was built **entirely from the ALERT PLATE's head**: the drawn
head (crown, crest plumes, white cheek, amber eye, bill) was cut as one
assembly in an eye-anchored frame, rotated **+52.1°** (from its drawn bill
direction 1.6° to the mechanism's spear direction **53.7°**), and placed so
the drawn eye lands on the mechanism's eye anchor (811.1, 496.2) — measured
error **0.6 px** (visual grounding) / 1.9 px (amber cluster). Nothing was
borrowed from the rejected strike keyframe or from the Audubon strike
still's head.

The attitude — bill continuing the spear line at entry — was set by the real
frames, checked before building:

- **qpYkzsJIQ4M t=1.70 s** (NatGeo standing spear, GBH;
  `real-bird-measure/atlas/atlas_03_strike_peak_qpYk.jpg`): neck, head and
  bill form one straight strike line into the water.
- **57YcyG5VrYI f90, t=136.97 s** (GBH lunge-plunge,
  `real-bird-measure/frames/57YcyG5VrYI_134.0-150.0/f0090.jpg`): the whole
  bird is one smooth spear; head indistinguishable in line from the neck;
  measured eye→billbase axis ≈11° vs neck axis ≈9° — collinear.
- **6bcHcoarCU4 t=59.42 s** (GBH lunge; `atlas/atlas_04_lunge_6bc.jpg`):
  same rule — the bill enters as the continuation of the neck, never
  flattened away from the spear line.

The mechanism's head frame (bill 53.7°, on the neckbase→skull chord line at
53°, tip on that line extended) matches that rule, so it was used as-is.
The alert head re-pitched honestly into that attitude — no missing piece
needed naming on the head itself.

## GATE TABLE (torso = 496.3 px throughout)

| Gate | Coil | Peak |
|---|---|---|
| 1. Landmarks | **PASS** — grounded chord_base **0.269** (band 0.24–0.30); grounded arc:chord **1.97** (≥1.9). By construction the tube is the mechanism chain (0.269 / 2.58). | **PASS by construction, with a reading caveat** — the drawn tube is the mechanism chain: chord_base **0.666** (band 0.62–0.71), chord76 **0.516** (band 0.49–0.60); grounded bill tip (885, 581) and eye corroborate the construction. Raw grounded occiput/neckbase reads give chord_base 0.588 — the same landmark-convention gap the keyframe report documented on pitched heads (its grounded strikes read 0.39–0.45 against their own geometry). |
| 2. Corridor continuity | **PASS numerically, FAIL visually** — content fraction 1.00 at all 40 stations, breast→skull; but the fold band is moiré, not feathers (see stretch). | **PASS** — content fraction 1.00 at all 40 stations; shaft reads continuous (crop `peak_shaft.png`). |
| 3. Head coverage ≥0.8 | **0.857 PASS** (skull ellipse + bill, from build bookkeeping) | **0.795 — marginal MISS** (0.005 under the line) |
| 4. Eye at anchor ≤~10 px | **PASS by grounding: 6.1 px.** The amber-cluster test reports 25.9 px — on this frame it locks onto bill-orange, not the eye; the grounded eye and the crop both show the drawn eye at the anchor. Disclosed, not hidden. | **PASS: 0.6 px** (grounding), 1.9 px (amber test). |
| 5. Ink in family | **0.2495 — marginal MISS** (band 0.252–0.272; short by 0.0025) | **0.275 — MISS** (band 0.304–0.324) |
| 6. Stretch map | reported below | reported below |

Coverage caveat (both frames): with the occipital-plume spike included, the
coverage figure drops to 0.44 (coil) / 0.41 (peak). The spike region in the
donor is a sparse FAN of separated strands over paper — most of its pixels
are legitimately paper in the drawing itself. The solid-part figure
(0.857 / 0.795) is the honest one; the spike figure is reported because the
brief asked for the head region whole.

Ink note (peak): the band was derived from `audubon_strike` (0.3144), a
plate that is ink-heavy everywhere — torso, wash, background. This frame's
base is the alert plate (0.2646) and its neck was remapped to the alert
neck's own ink; nothing in the honest donor set carries the strike still's
extra ~0.04 of whole-frame black. Reaching the band would have required
importing ink from the demoted still or a global trim — the two moves the
rulings forbid. Named here as a band-provenance problem, not a warp failure.

## STRETCH MAP (gate 6)

Arc stretch is **0.916× uniformly** on both frames by construction
(u-normalized mapping; donor arc 374.6 px → target visible arc 343.1 px).
The donor alert neck is LONGER than both targets — there is no arc stretch
problem anywhere in this spike, including the peak spear (the original
brief's worry, donor run 0.45 → 0.67, belonged to the rejected donor).

Cross-direction (target halfwidth ÷ donor halfwidth, per arc decile):

- **Coil:** 0.52 → 0.95 → 0.75 (root→tip). All compression; worst at the
  root (the coil tube is slimmest where it leaves the breast). The real
  damage is not cross-stretch but **turning**: the target fold turns
  38–44° per decile through the U while the donor S turns 16–37°, and the
  fold's minimum centreline radius is **8.6 px against a ~26 px
  halfwidth** — the tube's inner edge would need negative length, so the
  two passes of the fold paint over each other. In plain words: in the fold
  the engraving does NOT survive — the fine wavy feather-lines of the donor
  cross-hatch into a woven moiré band (`crops/coil_fold.png`). Along the
  descending and ascending passes away from the fold bottom, the hatching
  still reads as engraving.
- **Peak:** 0.31 → 0.55 → 0.46 — hard slimming everywhere (the spear is
  drawn at canon spear widths, roughly half the alert neck's), worst at the
  root (0.31). Turning is gentle (3–8° per decile). In plain words: along
  the spear the engraving **still reads as engraving** — the donor's fine
  stipple-and-hatch compresses across the shaft and stays legible as
  engraved feather texture the whole way down (`crops/peak_shaft.png`);
  nothing tears, nothing washes pale (the quantile remap held the neck's
  ink: the shaft is the darkest continuous element in the frame).

## PLUME VERDICT (Jimmy's tell, 2026-11-04 11:14)

**Both frames PASS the tell.** The breast plume on both frames is the alert
plate's own work, preserved in place as its own layer: fine, separated
strands hanging naturally, tips free over paper — the same strands as the
approved plate (`crops/plume_alert.png` vs `crops/plume_coil.png` /
`crops/plume_peak.png`). Nowhere does the plume read as a filled mass or a
blob; nothing of the rejected strike plate's cartoon frill exists in either
frame. Where the coil tube and the spear cross the plume's right edge, the
strands pass behind the neck, which is where anatomy puts them.

## DISCLOSURES

1. **The ghost (both frames, the headline defect).** The alert plate's
   background is a tonal wash, not flat paper; large areas of the drawn
   S-neck sit within the global content threshold's blind spot (summed RGB
   difference ≤55 from corner paper). The erase step therefore left the old
   neck in place as a soft slate silhouette — behind the coil's head (with
   a hard-edged un-erased notch), trailing the spear's upper edge on peak,
   plus one small rectangle at the spear's root. The missing piece for the
   warp route is a **local-background model** (per-region paper estimation),
   not a better warp. Not attempted: one-shot discipline.
2. **Legs (both frames).** The alert plate's legs, kept in place. Exact for
   coil (the rig's coil legs are the alert legs); for peak the rig poses a
   stepping leg with no honest donor texture (its only donor was the
   rejected plate), so the standing legs were kept and the deviation is
   disclosed rather than papered over.
3. **The eye was not re-drawn on either frame.** The head patch is
   eye-anchored, so the donor's drawn eye lands on the target anchor by
   construction (peak 0.6 px; coil 6.1 px). The brief's re-draw fallback
   was not needed.
4. **Coil head junction.** The head assembly is honest and complete (amber
   eye, crest, bill all present and correctly pitched at 26.3°), but where
   it meets the tube there is a vertically banded column — the warped
   tube's root stations compressed against the torso edge. Together with
   the fold moiré, the coil's neck is the weakest drawing in the spike.
5. **Peak bill tip** lands at ≈(885, 581–593), crossing the waterline wash
   near the frame's bottom edge — geometrically what the mechanism orders
   (tip reach 0.27 torso from the skull); the wash there is the alert
   plate's own, kept deliberately.
6. **Numbers provenance.** Black fractions by the v3 protocol (corner-median
   paper, content = summed diff >55, black = content with mean RGB <70).
   Corridor, coverage and stretch figures come from the build's own
   bookkeeping masks (`work/book_*.json`). Landmark values were measured on
   the finished PNGs by independent visual grounding, not taken from the
   build.

## WHAT THIS SPIKE SETTLES

- The mechanism correspondence works as a texture transport: corridor 1.00
  on both frames, chords on target, the head lands eye-exact, and a 0.31×
  cross-compression still reads as engraving along the spear. The fill
  test's failure mode (donors anchored to rig poses, distal third paper) is
  gone — anchoring to the DRAWING's own centreline fixed it.
- The warp route's remaining enemies are not geometric: (a) erasing a donor
  out of a tonal-wash plate needs local background modeling; (b) the deep
  fold's inner radius is smaller than the tube — no tube warp can fix that;
  the fold needs its own treatment (a fold-specific donor region or a drawn
  fold), which is a decision above this spike's pay grade.
- Peak is one erase-fix and one ink decision away from a real plate. Coil
  additionally needs the fold solved.

## FILES

- `warp_coil.png`, `warp_peak.png` — the two frames.
- `sidebyside/coil_warp_mask_alert.png` — warp | mechanism mask | alert plate.
- `sidebyside/peak_warp_mask_strikestill.png` — warp | mechanism mask | approved strike still (identity reference only).
- `crops/coil_neck_head.png`, `crops/peak_neck_head.png` — neck corridor + head, enlarged.
- `crops/peak_shaft.png` — the spear mid-shaft at 2.2× (engraving read).
- `crops/coil_fold.png` — the fold at 2.2× (the moiré, shown not hidden).
- `crops/plume_alert.png`, `crops/plume_coil.png`, `crops/plume_peak.png` — Jimmy's tell, same window, 2.2×.
- `work/` — build script, mechanism/donor dumps, bookkeeping JSONs, QC crops.
