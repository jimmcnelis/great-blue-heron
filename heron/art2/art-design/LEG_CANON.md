# LEG CANON — measured legs for the fresh art (design pass, 2026-11-04)

**Status: DESIGN, not applied.** The species package is NOT edited by this
document. Jimmy gates this canon; only then do the corrected traces go into
the mechanism. Until then, every leg number in the package is provisional
(CREW_MEMORY: "Leg traces are the known-bad part").

## 1. What was wrong — quantified

The mechanism's legs (`rig_v25.py`, `LEGS`, drawn identically in every pose)
are pixel traces taken from a pre-reset still, not from the bird:

| Quantity | Mechanism (rig v2.5, visible legs) | Real bird (this pass) | Error |
|---|---|---|---|
| Feet-centre along torso (tail→chest) | **0.285** (feet at 0.231 / 0.340) | **0.50–0.55** (coil 0.550, peak 0.498, stand 0.504) | **−0.21 to −0.27 of torso span — feet sit ~a quarter of the body too far toward the tail** |
| Leg emergence along torso | 0.22 / 0.35 (exits at x≈230 / 292 of loop 125–605) | **0.53–0.61** (coil 0.600, peak 0.611, stand 0.531) | **−0.26 to −0.31 — the whole leg apparatus hangs too far back** |
| Upper segment (emergence→joint) | 0.20–0.21 | 0.21 (GBH, see §2) | ≈ correct |
| Lower segment (joint→foot) | 0.235–0.243 | 0.215 (GBH) / 0.170–0.198 (grey) | **+0.02 to +0.07 too long** |
| Total exposed leg | 0.44–0.46 | 0.42–0.44 | +0.01 to +0.03 long |
| Pose dependence | **NONE — one fixed pair for alert, coil, and peak** | Feet stay planted for a standing spear; stagger widens 0.14 → 0.19 and the legs slant back at peak | The invariance itself is the error at peak |

How the error survived: the legs were traced once, early, onto a painting,
and every later frame inherited them unverified — through the gate overlays
(where Jimmy first spotted them) and into the warp frames (where he spotted
them again). The lesson is general and is written into the design as a rule:
**verify placement of every part against the studies, especially the parts
nobody is looking at.** (CREW_MEMORY, failure lessons.)

Note on the buried hip: leg 2's traced hip (296, 252) sits inside the body
core; its visible length is measured from the belly exit (≈292, 326), not
from the traced point. The buried-hip total (0.598) is not a leg length and
is not used anywhere in this canon.

## 2. The corrected canon — measured this pass

All lengths × torso length (study definition: hull diameter over
tail-tip / chest-front / back-top / belly points). Fractions along the torso
are tail→chest projections on near-profile frames. Grounding noise ≈ ±0.03.

### 2.1 Segment ratios

| Source | Upper (emergence→joint) | Lower (joint→foot) | Total exposed | Joint fraction of exposed |
|---|---|---|---|---|
| GBH, qpYk coil f0028 (standing, near-profile) | **0.214** | **0.215** | **0.428** | 0.50 |
| Grey heron, GY stand, study measurements.json (`legs_grey_GY_stand`) | 0.240–0.254 | 0.170–0.198 | 0.424–0.438 | 0.55–0.57 |
| **DESIGN BAND (pooled)** | **0.21–0.25** | **0.17–0.22** | **0.42–0.44** | **0.50–0.57** |

Reading notes:

- The GBH frame and the grey frames agree on the total (0.42–0.44) and
  disagree mildly on the split (GBH even, grey upper-heavy). The design band
  holds both; a second clean GBH standing read would narrow it (see §5 GAP).
- The femur/thigh is inside the body plumage in every frame — unmeasurable
  from video (study §2). "Upper segment" here = the EXPOSED leg from feather
  emergence to the intertarsal joint, i.e. the visible tibiotarsus. Do not
  draw a visible femur; the thigh mass is body plumage, rusty-colored
  (species palette `rusty`), and the leg emerges from it.
- The lower segment is the tarsometatarsus. It is dark brown
  (species palette `leg`), scaly, thin — "stilt-thin" (model_sheet.md).
- **Waterline rule (canon, study §2 + muskrat wade record):** "knee-deep" =
  the waterline sits EXACTLY at the intertarsal joint. Full tarsometatarsus
  submerged, tibiotarsus dry. On plates the waterline crosses the leg AT the
  joint; everything below it is underwater and is NOT drawn — the water is
  implied, and only its touch (a ripple/entry mark, flat black ink) is drawn
  (environment law, CREW_MEMORY).
- Underwater structure (vanord f0180, viewed): legs enter near-vertical
  (within ~10–15°), staggered in depth; feet spread WIDE on the bottom with
  toes clearly splayed. Toe spread is a drawing rule: feet are not stubs —
  draw spread toes at the foot, visible whenever the foot is above the
  waterline (mudflat/standing plates) and as the entry mark's shape at the
  waterline.
- A foot in soft mud spreads wider still (ig-weber-legs-mud, INVENTORY.md) —
  same rule, mudflat variant.

### 2.2 Stance placement — the corrected traces

Fractions are along the torso, tail = 0, chest = 1, on near-profile frames:

| Pose | Feet-centre | Near foot | Far foot | Stagger | Emergence | Source |
|---|---|---|---|---|---|---|
| Standing / coil | **0.55** | 0.62 | 0.48 | 0.14 | 0.60 | qpYk f0028 (coil, same bird as the peak) |
| Standing (compact coil) | **0.50** | 0.55 | 0.45 | 0.10 | 0.53 | 6bc BC_stand key (feet + torso only; legs occluded by rocks — segments excluded) |
| Strike peak (standing spear) | **0.50** | 0.59 | 0.40 | 0.19 | 0.61 | qpYk f0037 (peak, same bird) |
| Stalk step placement | feet 0.09 apart at placement | — | — | — | — | wilson f0097 + addendum gait record (feet 0.09 torso apart at placement instant) |

Design rules from these numbers:

1. **Feet live under the middle of the body, never under the tail.**
   Feet-centre 0.50–0.55 in every standing pose. The old 0.285 is retired.
2. **Feet are staggered, never side by side.** Near foot ahead of far foot
   by 0.10–0.19 of torso span; stagger WIDENS at peak (0.19) as the body
   pitches over planted feet.
3. **At a standing spear the feet DO NOT MOVE.** Coil → peak, feet-centre
   moves 0.55 → 0.50 (within noise of unchanged); what changes is the body
   pitch and the leg slant (emergence 0.60–0.61, feet 0.50: the legs angle
   BACK from emergence to feet by ~0.11 of span at peak).
4. **Per-pose leg configurations are mandatory.** One leg pair for all poses
   is the bug. Each pose sheet (ART_DESIGN.md) carries its own leg config;
   the animator interpolates emergence, joint, and foot independently
   between poses — the legs are a 3-point articulated chain, not a decal.
5. **Legs are thin.** Widths from the mechanism's render (hip→joint 16→11 px,
   joint→foot 7→5 px on a 496 px torso, i.e. ≈0.03 → 0.01 torso) are
   consistent with the real bird's stilt look and are kept as the drawing
   width rule. Flight: legs trail straight behind the tail as thin
   near-parallel lines (model_sheet.md, v1.1 ruling: legs too thick in
   flight before — keep them thin).

### 2.3 Corrected traces for the mechanism (to be applied after Jimmy's gate)

Expressed in the mechanism's own convention (1024×600 canvas, torso = 496.3 px,
torso loop x-extent 125–605, tail at left). These replace `LEGS` in
`rig_v25.py`. Values are computed from the design bands, not traced from any
image:

- **Standing / coil pair:** emergence at 0.60 of span → x ≈ 413 (near) and
  x ≈ 365 (far, emergence 0.50 — far leg emerges slightly behind near, as in
  the frames); joint at emergence + upper segment (0.21 torso ≈ 104 px)
  downward, near-vertical; foot at feet-centre 0.55 (x ≈ 389) ± stagger/2
  (near +0.07 → x ≈ 423, far −0.07 → x ≈ 356), y = waterline/ground line.
  Lower segment 0.21 torso ≈ 104 px, joint→foot.
- **Peak pair:** emergence 0.61 (x ≈ 418 near, 0.50 → x ≈ 365 far); feet-centre
  0.50 (x ≈ 365), stagger 0.19 (near x ≈ 411, far x ≈ 320); legs slanting back
  from emergence to feet; body pitched over the feet (the torso pitch is a
  body parameter, not a leg parameter — the legs stay planted while the
  torso rotates around them).
- **Alert pair:** standing band (feet-centre 0.50–0.55, emergence 0.53–0.61)
  until an alert-specific leg read exists (see §5 GAP). Do NOT reuse the
  coil pair silently — the alert sheet records the band, and the first
  alert plate drawn under the design must be checked against it.

Waterline on every plate: horizontal line through the intertarsal joints
(the joints, not the feet — the feet are below it, underwater, undrawn).
On mudflat/standing plates with no water, the ground line passes through
the feet with spread toes drawn.

## 3. What this canon does NOT claim (gaps)

- **GBH segment split, n = 1 clean frame.** The pooled band (upper 0.21–0.25,
  lower 0.17–0.22) is honest but wide; a second clean GBH standing read
  (Rio Grande wading 323d3DNrxnc, or a wilson stalk placement) would narrow
  it. Until then, draw at the band CENTRE (upper 0.23, lower 0.20) and do not
  present the split as tighter than it is.
- **Alert-stance legs:** no clean alert-stance leg frame was measured
  (BC_stand is a compact-coil stand; UR tall frames are neck-up but legs
  hidden). Alert uses the standing band, flagged.
- **Peak segment lengths:** qpYk f0037's joint ground is unstable and its
  torso denominator is pitch-inflated (0.380 total vs 0.428 at coil on the
  same bird) — peak segment lengths are NOT published from that frame.
  Peak uses the standing segment band + the feet/emergence placement.
- **GBH swallow distension:** still grey-sourced (1.31/1.53); no clean GBH
  ratio (addendum §2.5). Provisional wherever used.
- **Femur:** unmeasurable from video; never draw a visible femur segment.

## 4. Sources

- Study: `art2/real-bird-measure/MOTION_STUDY_REPORT.md` §2 (legs, knee-deep),
  `measurements.json` (`legs_grey_GY_stand`, immersion record).
- Addendum: `ADDENDUM_REPORT.md` §3 (gait), §6 (leg gap), `measurements_addendum.json`
  (`underwater_record`, `gait_records`).
- Inventory: `reference-footage/INVENTORY.md` (leg material list).
- This pass (new measurements, method in §5): qpYkzsJIQ4M f0028 (coil) and
  f0037 (peak), 6bc BC_stand key, vanord f0180 (underwater structure),
  wilson f0097 (step placement, corroborates addendum 0.09).
- Mechanism (the error): `creature-engine/packages/great-blue-heron/rig_v25.py`
  (`LEGS`, `TORSO_LOOP`, `TORSO_PX`), gate constant torso = 496.3 px
  (`rig-v25-gate/iter2/ITER2_REPORT.md`).

## 5. Method note (so the numbers can be re-checked)

Landmarks by visual grounding on the frames; torso = max pairwise distance
among tail-tip / chest-front / back-top / belly (study definition);
fractions = projections onto the tail→chest axis (near-horizontal bodies;
for the diagonal wilson frame, the placement separation only is used).
Segment lengths are straight-line emergence→joint and joint→foot. Noise
≈ ±0.03 on fractions, ±0.02 on segment ratios. Frames: qpYk f0028/f0037 are
the study's own extracted frames (`frames/qpYkzsJIQ4M_0.5-7.0/`); BC_stand
is `frames/keys/BC_stand.jpg`; vanord f0180 is
`frames/fb-vanord-underwater-strike_0.0-16.0/f0180.jpg`; wilson f0097 is
`frames/ig-wilson-donriver-stalk_118.0-134.0/f0097.jpg`.
