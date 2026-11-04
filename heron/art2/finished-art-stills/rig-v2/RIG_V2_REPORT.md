# RIG V2 REPORT — rebuild from the approved bird (2026-11-03)

**Outcome: Phase A complete. Phase B complete — proportions rebuilt
and verified on-spec. Proof (1) lands at 0.49 vs the 0.85 target —
far below — so per the brief's stop rule, Phase C was NOT entered and
Phase D was NOT entered. No finish generations were run, no model was
trained, no motion test v3 exists.** The residual gap is measured and
decomposed below; it is not proportions.

Surfaces: segmentation, IoU searches, and landmark measurement ran on
the local VM against files in this workspace. Canvas renders ran on
the DGX Spark (Fix-1 decoder, frozen step-6000 `last.pt`, the exact
`roster_render` batch path, both rigs through the identical code).
Approved stills untouched (sizes/mtimes predate this work; never
written). Originals preserved: `rig13_r4.py` unmodified,
`roster_render_orig.py` snapshot, all v1/v2/round-3 artifacts intact.

## Phase A — proportion spec

`PROPORTION_SPEC.md` + masks in `masks/` (approved rest/strike bird
masks; v1 and v2 idle silhouettes). Headline ratios (H = standing
height): approved torso extent ~0.80 H vs old rig 0.472 H; torso depth
~0.36–0.39 H vs 0.254 H; neck width ~0.10 H vs 0.067 H; plume drop
~0.33 H vs 0.178 H; head→bill-tip 0.30 H vs 0.287 H (already right);
skull small (HEAD_S effectively ~0.14 H vs ~0.19–0.22 H).

## Phase B — the rebuild

Changes (drawing model only; every chart pose value — root, head
anchor hx/hy, coil, tilts, leg fx/fy, timing — frozen):

- `rig13_r4_v2.py`: `body_xform` applies body length ×1.62 about
  local x=−2 and depth ×1.45 to ALL body-local elements (torso, wing,
  breast, hips); `BREAST_LOCAL` (12.5, 3.2)→(14.0, 1.8);
  `neck_spine` curve family straightened (control offsets −11/−14 →
  −8/−9, lift 8→5); `HEAD_S` 1.22→1.45; `BILL_LEN` 13.8→11.8;
  `leg_ik` 21.5/17.5 → 20.4/19.2.
- `maskrender_v2.py`: neck tube widths ×1.40.
- `roster_render_v2.py`: plume skirt offsets ×1.80 (plume stays its
  own channel 7 — the plume law is structural in the mask stack).

53 seed canvases re-rendered on the Spark: `canvas/idle_hold.png` +
`canvas/strike_f0000..f0051.png`. No silhouette clips the frame on
any of the 53.

### Proof (2) — landmark sweep (local VM, keypoint geometry)

Part sizes are now rig law, constant across all 53 poses (min–max):
torso 55.6–56.0 × 26.5–27.7 units; head→bill-tip 21.9 units in every
pose; IK legs 20.4 / 19.2. Idle vs spec: torso width 0.755 H (spec
~0.80), depth 0.376 H (0.36–0.39), head→tip 0.298 H (0.30), plume
drop 0.318 H (~0.33), neck width ~0.095 H (~0.10). Full sweep:
`work/landmark_sweep.json`.

### Proof (1) — idle-hold vs approved rest, aligned silhouette IoU

Measured two ways, because the number depends on the surface:

| Surface | Old rig | Rig v2 |
|---|---|---|
| Mask-stack silhouette (the conditioning geometry; local VM) | 0.410 | **0.526–0.532** |
| Rendered canvas image (Spark render; luminance bird mask, two thresholds) | 0.277–0.319 | **0.465–0.491** |

Reference points: round-3's warp bound 0.406; first coarse search
this session 0.383 (v1 mask). **Target was ≥0.85. Best v2 number:
0.49 (canvas) / 0.53 (mask). Far below target → stop rule fired.**

### Why — the decomposition (measured, not inferred)

1. **Head/neck placement is pose data, and it is the biggest term.**
   In the aligned overlay the BODY overlaps almost completely (the
   gold mass in `work/overlay_v2_vs_approved.png`), while the right
   third scores IoU 0.000 at every alignment: the approved bird's
   head+bill zone (3,628 px) has no rig counterpart. In each bird's
   own frame, the approved head sits ~+310 px forward of its body
   centroid; the rig statue's head anchor sits ~+102 px forward —
   the chart's hx=19. The brief froze chart pose data ("change the
   drawn bird's proportions within those poses"), so this term was
   out of scope by construction. The generative pass that produced
   the approved stills had re-POSED the bird, not just
   re-proportioned it.
2. **The canvas decoder regresses to its training proportions.**
   A rendered canvas vs its OWN conditioning silhouette, raw
   (unaligned) IoU: old rig 0.28–0.33, rig v2 0.38–0.47. The Fix-1
   decoder was trained on old-proportion birds and shrinks the new,
   bigger body inside its crop. This caps the canvas-surface number
   independently of the rig. (Fixing it means retraining the canvas
   decoder on new-proportion samples — a different job from Phase
   D's finish-model retrain.)
3. **Methodological note for the record:** the round-3 gate compared
   generative finishes against rig silhouettes, but the actual
   canvas images sit at raw IoU ~0.3 from those silhouettes. Part of
   the historical "geometry failure" lives in this render path, not
   only in the generator or the proportions.

## Phase C — NOT ENTERED (stop rule)

Zero finish generations run on the new canvases. For the record, the
Phase C hypothesis is not refuted by these numbers: its gate compares
a finish against its own canvas (pose-independent), and proportions
— the variable Jimmy's ruling targeted — are now on-spec. What is
refuted is proof (1)'s 0.85 against the approved REST still, which
mixes pose with proportions.

## Phase D — NOT ENTERED

No training, no motion test v3.

## What would unblock (Jimmy's call, with the measured price of each)

1. **Authorize head-anchor re-derivation** (hx/hy for the statue and
   strike families from the approved stills). This is a pose-data
   change — explicitly outside this brief. It addresses term 1, the
   largest.
2. **Retrain the canvas decoder** on new-proportion samples so
   canvases stop shrinking toward the old body plan. Addresses
   term 2.
3. **Or re-scope proof (1):** replace the 0.85-vs-approved-rest bar
   with a pose-aware criterion and proceed to Phase C as briefed
   (its own stop rule — fewer than half accepted — still protects
   the retrain).

## Files

- `PROPORTION_SPEC.md`, `masks/` (4 masks)
- `canvas/` — 53 rig-v2 canvases (Spark render, pulled back)
- `work/` — `measure_v2.py` + outputs (both tuning rounds),
  `landmark_sweep.json`, overlays (`overlay_v2_vs_approved.png`,
  `overlay_canvas_vs_approved.png`), `pose_tracks_v2.json`,
  `old_rig_idle_canvas.png` (the same-surface baseline), QA JSONs,
  Spark job dirs (`sparkjob/`, `sparkjob_v1/`)
- Code: `~/workspace/heron/src13/rig13_r4_v2.py`,
  `~/workspace/heron/art2/maskrender_v2.py`,
  `~/workspace/heron/art2/roster_render_v2.py`
- Spark (additive only): `~/heron/rigv2/`, `~/heron/rigv2_out/`,
  `~/heron/rigv1/`, `~/heron/rigv1_out/`
