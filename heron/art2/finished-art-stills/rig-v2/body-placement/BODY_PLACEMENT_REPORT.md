# Body-Mass Placement Round — Report (rig v2.2)

## Verdict

**Proof (1), mask surface, idle hold vs the approved rest still:**

| rig | mask IoU |
|---|---|
| v2 (control) | **0.5257** |
| v2.1 (control) | **0.5501** |
| **v2.2 (this round)** | **0.6141** |

Controls reproduced exactly before the v2.2 number was read (v2 0.52566,
v2.1 0.55013 in this round's harness — the third independent reproduction
of both). **0.6141 is below the 0.85 gate.** Placement bought +0.064 over
v2.1, and the decomposition below shows placement is now close to its
ceiling: of the remaining gap, ~31% of all miss is painted scenery the
protocol counts but no bird rig can match, the plume-strand term is a
deliberate trade the gate itself arbitrated, and the largest
controllable term is no longer placement at all — it is the torso
hull's *outline shape* (~20.5k extra px), which this round's levers
could not touch. No finish was attempted. The frozen Fix-1 decoder,
rendered for the record only, scores 0.429 on this pose (self-IoU
0.149) — its retrain is last, per Jimmy's ruling, and is untouched here.

## What was measured (approved rest still, Phase A instruments)

All offsets breast-relative, in units of the bird's height H (approved
H = 562 px, rig H = 479.4 px). Full data: `body_measurements.json`,
`body_measurements2.json`.

**Torso mass.** Dense core (≥13 px inside the torso+wing+tail union,
erode-verified against an independent geometric reconstruction of the
hull): approved centroid **(−0.356, +0.111) H**; rig v2.1
**(−0.342, +0.075) H** — the rig's mass sat **0.036 H too high**, x about
right. Row-band shares (top/mid/bottom thirds of the core): approved
0.281/0.348/0.371 (belly-heavy) vs rig 0.275/0.423/0.317 (middle-heavy)
— a distribution difference *inside* the torso, not just placement.

**Plume hang.** Two readings of the painted plume, and they disagree —
this mattered, see §Plume tension. The *dense fan* directly under the
breast (the Phase A reading) bottoms at ~0.33 H. The *full strand set*
(every painted stroke attributable to the plume, extracted by
subtraction against the leg/body masks) has envelope centroid
**(−0.201, +0.253) H**, envelope drop 0.495 H — but the strands fill
only **0.606** of their own envelope; the rest is paper. Rig v2.1's
solid plume polygon: centroid (+0.021, +0.093) H, drop 0.325 H,
14,772 px of solid ink against the strands' 9,886 px of actual ink.

**Legs (anatomy under the skirt, per the plume law).** Painted hip
exits — where the legs emerge from the body fringe — at
**(−0.410, +0.297)** and **(−0.370, +0.297) H**: only 0.040 H apart,
both low. Painted feet stance **0.105 H**, leans −14.4° / −1.6°. Rig
v2.1 silhouette exits: (−0.398, +0.254) / (−0.266, +0.227) — 0.133 H
apart and 0.04–0.07 H too high; stance 0.160 H, feet too far forward.

## The surgery (placement only; sizes frozen; head/neck frozen)

Versioned copies; v2.1 untouched. Search: 154 scored evaluations,
staged coordinate descent under the certified protocol, every
evaluation asserting the neck invariants and leg-IK reachability
(`search_log.json`, `search_v22.py`).

1. **Torso tilt — new pose-gated parameter `body_rot_b` = −6.75°**
   (`src13/rig13_r4_v22.py`): a rigid rotation of all body-local
   outputs about the *transformed breast point*. Rotating about the
   breast is what makes the frozen neck settlement untouchable: the
   breast is the neck's lower endpoint and the head anchor is
   root-relative, so neither can move under this lever, by
   construction (verified below, not just argued). Stage gain:
   0.5501 → 0.5596 at −7.5°, polished to −6.75°. (Positive angles were
   rejected by the IK guard — they lift the hips beyond leg reach.)
2. **Plume translate (+6.0, −17.0) design units** — forward 6, **up**
   17 (`art2/roster_render_v22.py`, `PLUME_DX/PLUME_DY`). Pure
   translation of the offset fan; its shape, spread and channel are
   unchanged. Stage gain: → 0.5941. Direction explained in §Plume
   tension — it is the opposite of the strand-envelope delta, and the
   gate was unambiguous in both directions.
3. **Legs**: `HIP_FAR` local x −1.5 → **+1.5** (far-leg IK base; near
   hip unchanged); hold-pose feet fx: near 6.0 → **5.5**, far
   −5.0 → **−7.5** (`pose_tracks_v22.json`). Stage gain: → 0.6102,
   polish → **0.6141**. Note: the *measured* painted stance
   (fx ≈ −3.6 / −11.1) was evaluated and scored worse — the gate's leg
   optimum is a compromise short of the painted stance, because the
   painted legs emerge from a fringe while the rig's emerge from solid
   mass; exit *height* (the term that was pure placement error) did
   reach the painted value, below.

Scope note: `body_rot_b` is pose-gated (only the hold pose carries it;
every other pose defaults to exact v2.1 behavior). The plume translate
and `HIP_FAR` are rig-wide constants in the v2.2 files — any chart
rendered with v2.2 inherits them. Only the idle hold was rendered or
verified this round.

## Proof and verification

**Alignment fit (v2.2):** rot +3°, scale 1.175, dx +24, dy +12 — the
same fit family as v2/v2.1, no fit gaming. Zero-delta control: the
v2.2 files with all placement deltas at zero reproduce v2.1's 0.5501
exactly, so the file surgery itself changed nothing unintended.

**Frozen head/neck — invariants, all exact:**
- Neck (ch 1) and head (ch 2) mask channels **pixel-identical** to v2.1.
- Breast point (442.84, 284.10) and head anchor (526.47, 137.73)
  **bit-identical**; Δ(anchor − breast) unchanged.
- Neck arc 32.62 units = **0.4476 H** in both (Jimmy's long-neck law);
  neck widths at arc fractions 0.3/0.5/0.7 = 58.6/53.5/40.9
  approved-frame px, **identical** v2.1 → v2.2.
- Standing height 71.9 units and head→bill-tip 0.305 H unchanged; no
  clipping (silhouette bbox x 96–671, y 106–587 inside 1024×600).

**Landmark re-check (pose frame):** torso bbox 55.6×27.7 → 53.9×30.5
units (narrower, deeper — the pitch); torso width/depth over H 0.773/
0.385 → 0.750/0.424; leg segment lengths 20.4/19.2 units unchanged
(part sizes frozen); plume drop 0.325 → 0.089 H (the placement outcome
discussed below, not a size change — the fan's shape is untouched).

**Post-surgery body measurements (same instruments):**
- Torso core centroid (−0.330, **+0.114**) vs approved (−0.356,
  +0.111): the vertical error is closed (was +0.075); 0.026 H of
  forward residual remains. Row bands 0.275/0.418/0.320 vs approved
  0.281/0.348/0.371 — the middle-heavy *internal* distribution persists:
  that is hull shape, not placement.
- Leg exits (−0.365, **+0.302**) / (−0.303, **+0.290**) vs approved
  (−0.410, +0.297) / (−0.370, +0.297): exit heights on target; exits
  still ~0.05 H forward and stance 0.145 H vs painted 0.105 H.

## Residual decomposition (placed fits, pixels)

Totals: miss 28,068 → **24,592**; extra 27,887 → **20,599**.

Miss by approved-side zone (v2.1 → v2.2):

| zone | approved px | miss v2.1 | miss v2.2 |
|---|---|---|---|
| scenery (waterline/grass, y≥558) | 8,023 | 7,830 | **7,715** |
| plume (strand zone) | 10,433 | 2,723 | **5,914** |
| torso/rest of frame | 52,459 | 4,114 | 4,224 |
| head (0.20 H zone) | 11,784 | 7,231 | 3,599 |
| legs | 5,293 | 3,539 | 2,224 |
| neck | 8,500 | 2,631 | 916 |

Extra by rig channel (v2.1 → v2.2): **torso 21,216 → 20,518** (still
the dominant term in the whole comparison), plume 3,597 → 3,089, wing
4,096 → 2,928, neck 2,991 → 2,460, legs 1,412 → 1,772, head 98 → 81,
tail 91 → 70.

Two side-effects worth naming: head-zone miss fell 7,231 → 3,599 and
neck-zone miss 2,631 → 916 **with the head/neck channels pixel-
identical** — pure alignment relief. With the body mass misplaced, the
global fit was spending head/neck accuracy to chase torso mass; placing
the body correctly gave that accuracy back. Bird-only IoU (scenery
band excluded from both masks): 0.5879 → **0.6567**.

**What the remaining 0.236 (1 − 0.6141) is made of, in order:**
1. **Scenery — 7,715 miss (31% of all miss).** Painted waterline
   strokes and grass inside the protocol mask. Structural: a perfect
   bird still misses all of it. Not a rig property.
2. **Torso outline shape — 20,518 extra on the torso channel** (+4,224
   torso-zone miss). Placement is now right (centroid y exact, x
   within 0.026 H); the hull's *outline* — back line, belly curve,
   bulge profile — is a bigger, different shape than the painted
   torso, and the middle-heavy internal distribution (bands above)
   says the same thing from inside. This is part geometry, frozen out
   of a placement round.
3. **Plume strands — 5,914 miss**, deliberately uncovered (see below).
   The strands' own paper gaps (~6,400 px inside their envelope) mean
   even a perfectly placed solid skirt pays ~0.6 fill efficiency
   there.
4. **Head-zone bulk — 3,599 miss.** The zone counts the painted head's
   engraved mass (cap, crest, cheek) around the skull; the smooth
   skull+bill channels place with only 81 extra px but cannot fill
   engraved bulk. Head is frozen; noted, not chased.
5. **Legs — 2,224 miss.** Thin painted sticks emerging from a fringe
   vs the rig's solid emergence; stance compromise above.

Ceiling arithmetic: forgive scenery entirely *and* the plume strands
entirely — both protocol/paint properties, not placement — and the
torso outline + head bulk still cap the raw score near ~0.75–0.78.
**0.85 is not reachable by placement.** The next real lever, if Jimmy
wants one, is a hull-outline (geometry) round; the decoder retrain
already scheduled last does not move this gate at all.

## Plume tension — stated plainly

The brief's expectation (from the v2.1 decomposition) was that the
plume hangs too high/short and should move back-down toward the
painted strands. Measurement complicated that, and the gate settled
it: translating the skirt toward the strand envelope was tried at 30
grid points and **cost IoU at every single one** (monotonically worse
with distance, to 0.487 at the full measured delta). The refine walk
then climbed steadily in the *opposite* direction — up and forward —
for +0.035. Reason: the painted plume is two things — a dense fan
under the breast (real silhouette mass) and long sparse strands
(mostly paper). A solid channel can be one of them; the gate prices
the strands' paper gaps as extras and the fan's mass as coverage, so
the solid skirt belongs on the fan.

Consequence, honestly flagged: **v2.2's plume channel is placed as a
dense bib at the breast (drop 0.089 H), not as the long hanging skirt
in the painting.** The plume *law* is intact — it is still its own
channel/layer, pure translation, shape and spread untouched, legs
still read as anatomy beneath it. But whether the finished bird reads
as Audubon's hanging plume depends on the finish painting strands
*from* this channel — a finish-phase question this silhouette gate
cannot answer. If Jimmy's eye says the hang matters more than the
gate's 0.035, the translate is one line (`PLUME_DX, PLUME_DY`) and the
cost is known exactly. The gate's answer and the trade are both on
the record; nothing was buried.

## Strike implication (measurement only — strike not re-posed)

Nothing in this round re-poses or re-renders the strike. Two filed
facts stand unchanged: the strike charts' neck arc (0.329 H) vs the
strike still's (0.565 H), and this round's constants being rig-wide
(a strike rendered under v2.2 would inherit the plume translate and
far-hip shift; its transfer is unmeasured). The hold-pose finding
that *does* transfer as a hypothesis: the shared `body_xform` carried
a high/back mass bias at rest (−6.75° of breast-pivot pitch was
available and taken) — the strike poses ride the same transform, so
their body attitude plausibly carries the same bias. Testing that is
a strike-round measurement, not an assumption to bake in.

## Canvas (for the record only)

Frozen Fix-1 decoder, v2.2 hold pose, rendered on the Spark
(`idle_hold_v22.png`): canvas IoU **0.429** (T=200) / 0.459 (T=220);
decoder self-IoU vs its own mask **0.149 / 0.172** — worse than
v2.1's 0.19, expected: the decoder has never seen this body attitude
and it is out of scope until its retrain, which Jimmy has scheduled
last. The mask surface is this round's verdict surface, as briefed.

## Files

This directory (`finished-art-stills/rig-v2/body-placement/`):
- `BODY_PLACEMENT_REPORT.md` — this report
- `measure_body.py`, `measure_body2.py` — measurement instruments;
  `body_measurements.json`, `body_measurements2.json` — the numbers
- `approved_plume_strands.npy`, `approved_leg_mask.npy` — extracted
  painted plume/leg masks used by the instruments
- `search_v22.py`, `search_log.json`, `search_run.log`,
  `winning_params.json` — the 154-evaluation search record
- `pose_tracks_v22.json` — the v2.2 hold pose (hx/hy 36.17/−26.34,
  body_rot_b −6.75, leg fx 5.5/−7.5)
- `verify_v22.py`, `verify_results.json`, `verify_stdout.json` —
  controls, invariants, landmarks, decomposition
- `rig_v2_2_idle_silhouette.png` — the v2.2 idle-hold mask
- `overlay_v22_vs_approved.png` — yellow = agreement, red = approved
  only, blue = rig only
- `idle_hold_v22.png`, `canvas_record.json` — decoder canvas, record
  only
- `sparkjob/` — the exact files staged to the Spark for the canvas

Rig/renderer (v2.1 files untouched):
- `src13/rig13_r4_v22.py` — + `body_rot_b` breast-pivot rotation
  (pose-gated, 0 = exact v2.1), `HIP_FAR` +3.0 local x
- `art2/roster_render_v22.py` — + `PLUME_DX/PLUME_DY` = (+6.0, −17.0)

Approved stills untouched; creature engine untouched; no finish
generations; no training.
