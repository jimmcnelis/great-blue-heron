# PROPORTION SPEC — the approved bird, measured (Phase A)

The law for the rig rebuild. Source of truth: the two approved Audubon
stills (`audubon_rest.png`, `audubon_strike.png`, 1024×600, untouched).
Segmentation: `gate.py`'s bird_mask (the round-3 gate's HSV rules),
run on the local VM. Landmarks: visual grounding on the stills
(±15–40 px). Rig-side numbers: roster keypoint geometry in design
units (U = 6.667 px/unit), idle statue pose.

**H** = standing height, crown → foot, in each bird's own frame.
Approved rest: H = 561 px (crown y≈27 → foot y≈588). Rig idle: H ≈ 73 units.

## Measured ratios

| Measure | Approved rest | Approved strike | Old rig (idle) | Rig-v2 (idle, measured) |
|---|---|---|---|---|
| Silhouette bbox (px / units) | 788×575, area 96,492 px | 822×526, area 130,946 px | 394×486 px, 33,878 px | 473×492 px, 67,790 px |
| Silhouette aspect (w/h) | 1.37 | 1.56 | 0.81 | 0.96 (pose-bound, see note 1) |
| Torso horizontal extent / H | ~0.80 | — | 0.472 | **0.755** |
| Torso depth / H | ~0.36–0.39 | — | 0.254 | **0.376** |
| Head centre → bill tip / H | 0.30 | — | 0.287 | **0.298** |
| Skull length (nape → bill base) / H | ~0.19–0.22 | — | ~0.14 | ~0.17 (HEAD_S 1.45) |
| Neck width, mid / H | ~0.10 (55–65 px) | — | 0.067 | ~0.095 (tube ×1.40) |
| Plume drop below breast / H | ~0.33 | — | 0.178 | **0.318** |
| Leg hip → foot / H | 0.40 from body exit; 0.51 from body-centre hip | — | 0.54 | unchanged (chart data) |
| Leg IK segments (thigh : shin) | ~0.51 : 0.49 from pivot hip | — | 21.5 : 17.5 (0.55:0.45) | 20.4 : 19.2 |
| Neck curve, breast → head / H | ~0.37 | — | 0.45 | 0.45 (endpoints are chart data, note 2) |

Identity fractions of the approved stills themselves (gate reference):
rest — black 0.2593, rust 0.03564, yellow 0.01667, slate 0.4646 (in band).
strike — black 0.3144, rust 0.0170, yellow 0.00488 (the approved strike
still sits outside the sequence bands — the known f27 disagreement).
Gate bands (from REFINISH_PHASE1_REPORT): idle black 0.252–0.272 /
rust 0.035–0.037 / yellow 0.016–0.018; strike standing frames black
0.2501–0.2653 / rust 0.0335–0.0373 / yellow 0.0155–0.0188.

## The v2 transform (this spec as implemented in the rig)

All changes are in the rig's drawing model — `src13/rig13_r4_v2.py`,
`art2/maskrender_v2.py`, `art2/roster_render_v2.py`. Originals preserved
(`rig13_r4.py` untouched; `roster_render_orig.py` snapshot taken).

- `body_xform`: body length ×1.62 about local x = −2, body depth ×1.45
  (applied after GIRTH to every body-local element: torso, wing,
  breast, hips — one consistent anatomy, plume law intact: the plume
  remains its own channel/layer).
- `BREAST_LOCAL` (12.5, 3.2) → (14.0, 1.8): neck attachment forward/up
  on the torso, as drawn in the approved bird.
- `neck_spine` curve family straightened: control offsets
  (−11·coil−0.5, −1·coil) → (−8·coil−0.5, −1·coil) and
  (−14·coil, +8·coil) → (−9·coil, +5·coil). The approved neck rises in
  a long diagonal S, not the old rig's deep backward bow.
- `HEAD_S` 1.22 → 1.45; `BILL_LEN` 13.8 → 11.8 (skull grows, total
  head → tip held at the spec ratio 0.30 H).
- Neck tube widths ×1.40 (`maskrender_v2.build_mask_stack`).
- Plume skirt offsets ×1.80 (standing branch of `keypoints_for`).
- `leg_ik` segments 21.5 / 17.5 → 20.4 / 19.2.

## Frozen — NOT changed

All chart pose data: root positions, head anchor (hx, hy), coil,
tilts, yaw, leg fx/fy, wing mode, and all timing. Neck endpoints
(breast after the anatomy move, head anchor). HIP_Y, WATER_Y, BOTTOM.
The pose-vector definition, the mask channel order (plume = channel 7),
the crop rule, and the Fix-1 decoder checkpoint.

## Notes

1. **Aspect / head placement.** The approved rest bird's head sits
   ~+310 px forward of its body centroid; the rig statue pose's head
   anchor sits ~+102 px forward of its body centroid (raw px, each
   bird's own frame). That difference is the chart's head anchor
   (hx = 19 units) — pose data, frozen by the brief. It caps the
   aligned silhouette IoU against the approved rest still regardless
   of proportions (see RIG_V2_REPORT for the measured decomposition).
2. **Neck length.** The rig's breast→head span is longer relative to
   H because its head anchor is high (hy = −28) while the approved
   head is lower and forward. Endpoint positions are pose data; the
   rig-side levers (attachment point, curve shape, width) were all set
   to spec.

## Saved masks (this directory, `masks/`)

- `approved_rest_mask.png`, `approved_strike_mask.png` — bird_mask of
  the two approved stills.
- `rig_v1_idle_silhouette.png` — old rig idle mask-stack union (33,878 px).
- `rig_v2_idle_silhouette.png` — rebuilt rig idle mask-stack union (67,790 px).
