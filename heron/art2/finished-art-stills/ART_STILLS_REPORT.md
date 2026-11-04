# ART STILLS REPORT — the Audubon finish (finished-art candidates)

**Date:** 2026-11-03. **Status: STOP — awaiting Jimmy's verdict. Nothing
downstream of the art is built on these.**

**Correction history, stated once:** the first version of this brief
asked for a decoder-stills judgment set; the second for a two-finish
(naturalist vs storybook) comparison. Jimmy's ruling (2026-11-03 11:15)
settled the finish himself — **Audubon, only Audubon** — and the
storybook comparison was cancelled. No storybook image was ever
generated (the correction landed before any generation ran); nothing
was abandoned but the plan. What follows is the Audubon-only job.

## Deliverables (this folder)

- `audubon_rest.png` — hero stand (rest profile at the waterline),
  1024×600.
- `audubon_strike.png` — strike at maximum extension, 1024×600.
- `presentation_sheet.png` — both stills, labeled, side by side.
- Raw generations kept alongside at 2048×1184
  (`media-generation-audubon-rest-0-*.png`,
  `media-generation-audubon-strike2-0-*.png`), plus one rejected strike
  (`audubon_strike_REJECTED_pose-drift_raw.png` — see Weaknesses).

## Method — how these were made

1. **Pose from the proven movement, unchanged.** Each still's pose is a
   canonical chart frame, taken from the movement system Jimmy has
   already approved: rest = `idle_hunt` f30 (the chart's signature
   frame), strike = `strike` f27 (the chart's signature frame, inside
   the f24–38 max-extension/contact window). The Route 2 study render
   of that exact frame served as the pose canvas — geometry, blocking
   and scale come from the charts, not from the generator's imagination.
2. **Finish pass.** A generative image-to-image repaint of that canvas
   under a locked Audubon brief: hand-colored engraving in the manner
   of *Birds of America*, Plate 211 as north star, the full field-mark
   checklist written into the pass, warm ivory plate paper, and only a
   whisper of waterline/reeds at the feet as ground (environment law's
   spirit: the bird is the plate; no scenery scene).
3. **QA gates, applied by eye against the checklist below** — legs,
   plume, field marks, pose truth. The strike failed the pose gate on
   its first pass and was re-run once with an explicit geometry lock;
   the failed pass is kept on disk, not hidden.

Output normalization, disclosed: the generator returns 2048×1184; the
deliverables are downscaled to exactly 1024×600 (a 1.35% anisotropic
aspect normalization — imperceptible, and it keeps the full
composition rather than cropping the bird).

## Audubon reference points used

- **Plate 211 (Havell), Great Blue Heron** — composition research:
  the bird composed as the whole plate; head and bill working at the
  water; long plumes trailing; feet on a low bank with narrow leaves
  echoing the legs; blue water as a foreground band; palette of slate
  blues, soft greys and warm ochres; fine engraved plumage detail with
  clearly separated flight feathers.
- **Audubon's standing-plate treatment** (the sentinel heron plates):
  life-sized bird on plain warm paper, minimal ground, precise
  anatomical line — the rest still follows this.
- **Field-mark truth** from Jimmy's own reference still
  (`reference/real-heron-b.jpg`): bold black brow sweeping into the
  plume, white face, golden eye, dagger bill yellow at the base to an
  orange tip, prominent black shoulder patch, long shaggy breast
  plumes hanging as individual strands, slate body, rusty thighs.

## Field-mark checklist — verification per still

### Rest (`audubon_rest.png`, from idle_hunt f30)
- Slate-blue body/wings ✓ · white head/face ✓
- Black eyebrow stripe → black occipital plume ✓ (long trailing
  strands — Audubon-dramatic, see Weaknesses)
- Yellow-orange dagger bill ✓ · golden eye ✓
- Shaggy breast plume, its own region, hanging in separate strands
  clear of the body silhouette ✓
- Black shoulder patch ✓ (small rusty bend-of-wing spot at its front
  edge — true to the species)
- Rusty-brown thighs ✓
- Legs: two, thin, clearly separated, drawn scale texture ✓
- Blocking: body in the 1st third, bill reaching to the middle ✓
- Pose: the chart's statue stand; the finish softened the neck into a
  gentle Audubon S — disclosed, not hidden.

### Strike (`audubon_strike.png`, from strike f27)
- Pose truth ✓ — one straight diagonal spear from a compact body,
  wings folded flat, head at the far lower-right end, bill tip just
  above the waterline. This is the chart's max-extension geometry.
- Slate-blue body ✓ · white head ✓ · brow stripe → plume ✓
- Dagger bill ✓ (runs yellow rather than orange-tipped)
- Golden eye ✓ · breast plume strands at the chest, own region ✓
- Black shoulder patch — present but OVERSIZED (see Weaknesses)
- Rusty thighs — present but over-saturated/long (see Weaknesses)
- Legs: two, thin, clearly separated ✓
- Blocking: strike head lands mid-to-right at the water — the fishing
  third ✓

## How this finish scales to the roster and the device

**The pipeline, named:** *Audubon finish pass.* For every chart frame:
(1) the movement system renders the frame exactly as today (pose/mask
study); (2) the finish pass repaints it under the same locked brief
used here, with this report's checklist as its acceptance gates;
(3) frames that fail a gate are re-rolled automatically. It is a
**bake-time** pipeline — the ESP32-P4 device still just plays finished
frames, so device cost, memory and frame format do not change at all.

**Honest risks and costs, in the order they will bite:**
1. **Pose drift is real and already proven.** The strike's first pass
   ignored the spear and rebuilt the famous raised-wing Plate 211
   composition instead (kept on disk as the rejected file). A geometry-
   lock prompt fixed it once; across 2,004 frames some percentage
   will drift and need re-rolls — budget a cost multiplier, not a
   single pass. Drift will concentrate exactly where the studies are
   weakest: maximum neck extension, the flight family, the front view.
2. **No temporal-consistency guarantee.** Each frame is repainted
   independently; engraved hatching and feather masses can crawl
   between adjacent frames — the same disease as Route 3's seam swim,
   in a new coat. Mitigations exist (locked brief + seed discipline,
   finishing keyframes and blending between them, or — the robust
   route — training a pose-conditioned finish model on a corpus of
   approved finished frames, seeded by these stills), but none is
   proven yet, and a 3-frame motion test at this finish should be
   gated before any full roster bake.
3. **Throughput.** 2,004 frames of generative repaint is a large,
   slow, metered batch — hours-to-days of generation, not minutes of
   local rendering. The movement studies stay the cheap draft layer;
   the finish is the expensive final coat, applied once, after the
   art is approved.
4. **Identity discipline.** The brief + checklist held the same bird
   across these two poses. Twenty charts include poses (front,
   flight, doze) where the generator has more freedom and the bird can
   wander; the checklist gates are the control, and they are manual
   today.

## Weaknesses — honestly

- **Rest:** the occipital plumes trail longer and more theatrical
  than the real bird's — that is Audubon's own license (his plumes
  stream), but it is a style dial Jimmy may want turned down. The
  fore-neck lacks the real bird's white, black-streaked front; feet
  are barely indicated where the legs meet the water.
- **Strike:** the black shoulder patch ballooned into a black saddle
  over the shoulder/upper back (the study frame's dark shoulder mass,
  amplified), and the rusty thighs run long and hot — more red
  stocking than thigh. The neck is solid slate where a real striking
  bird shows a paler, streaked fore-neck. The head turns slightly
  toward the viewer rather than holding pure profile.
- **Both:** the engraving is a very good modern facsimile of the
  manner, not a period artifact — line is cleaner and more uniform
  than Havell's hand work, and the paper is evenly warm rather than
  foxed. At 1024×600 on the device this reads as a strength; at print
  size it would read as imitation.
- **The spear's bill** in the strike touches the waterline visually
  but throws no ripple — environment law says water speaks only in
  flat black ink when touched; the finish pass used color wash for
  the water band instead. If the ink-only water law is to bind the
  finished art too, that is a brief change for the roster bake, and
  it should be decided with the art verdict.

## What did NOT happen

No retraining, no roster/engine/behavior changes, no storybook work,
no device work. The movement studies are untouched and remain the
pose source. These two stills are candidates for Jimmy's verdict —
if he approves the finish, the finish pass above is the stated route
to the full roster; if he doesn't, nothing has been built on them.
