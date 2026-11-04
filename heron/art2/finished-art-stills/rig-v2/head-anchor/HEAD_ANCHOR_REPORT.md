# HEAD ANCHOR REPORT — rig v2.1 (head-anchor surgery on the idle hold)

**Date:** 2026-11-03. **Scope:** ONE pose (idle hold) — measure the head anchor off the
approved rest still, move the hold's anchor to it, re-derive the neck so it connects
at the measured length and spec width, re-render through the frozen Fix-1 decoder,
re-measure proof (1) under Phase B's identical protocol.
**Verdict: IMPROVED-BUT-SHORT.** The rig-side (mask) surface improved and is
protocol-certified; the canvas surface is a wash because the frozen decoder —
now the dominant remaining term — follows the re-posed conditioning measurably
worse than it followed v2's. Neither surface is near the 0.85 bar. Details below.

Jimmy's ruling applied throughout (2026-11-03 18:22): *the heron's neck is really
long — it's just who they are.* Neck length was measured off the approved still and
**held**, not traded away to make the geometry easier. No compression,
foreshortening, or tucking anywhere in this work.

---

## 1. The measured anchor (approved rest still, `audubon_rest.png`, untouched)

Anchor definition: the **skull centre** — the rig's head-group rotation origin H,
the point the neck curve terminates at. Located by bill geometry, the one rigid
structure in the head: H = bill_tip − 0.298·H along the bill axis, where 0.298 is
the locked proof-(2) head→tip ratio.

- Standing height H = **562 px** (crown y=26 → waterline y=588; gate mask,
  byte-identical to Phase A's saved mask, area 96,492).
- Bill: saturated-yellow component x 698–823; mask tip **(828, 63)**; axis 3.31°.
- **Anchor H = (660.8, 53.3) px.** Eye measured at (710.9, 46.4) as a cross-check.
- Breast anchor (where the neck tube merges into the torso, centreline DT rule,
  same rule family as Phase A): **(565, 221) px**.
- **Δ anchor − breast = (+95.8, −167.7) px = (+0.170, −0.298) H.**
- Anchor forward of body (torso) centroid: **+284 px** — vs the rig hold's +110 px
  under the identical rule. Phase B's "~+310 vs ~+102" stands confirmed.

Method spread, and why the bill governs: eye-offset method gives (693.7, 56.6) —
rejected because Phase A measured the approved skull *longer* than the rig's
authored skull (0.19–0.22 H vs ~0.17 H), so the rig's eye offset does not transfer;
skull-mass centroid gives (630.6, 54.4) — pulled backward by the nape and plume
bases. The bill is rigid and its length ratio is a locked proof-(2) quantity.

### The neck, measured (Jimmy's long-neck law)
- **Length (breast → head along the centreline curve): 251.5 px = 0.4476 H.**
  (DT≥40 breast-rule sensitivity: 0.510 H — the breast sits deep; the primary rule
  is the one stated above, and the rig is held to it.)
- Shape: arc/chord = 1.30 — the neck rises steeply, pinches back at the nape,
  then runs forward into the skull (S/L hybrid, traced in
  `centreline_overlay.png`).
- Mid-neck width: **51.0 px = 0.0907 H** (perpendicular cross-sections) —
  confirms the spec's ~0.095–0.10 H band; the rig's authored tube (0.095 H) stays.

## 2. What changed (rig v2 → v2.1, hold pose only)

- **Hold anchor: hx 19.0 → 36.17, hy −28.0 → −26.34.** In design units the anchor
  moves (45.0, 19.0) → **(62.17, 20.66)**: almost purely forward (+17.2 units),
  height essentially unchanged. New Δ anchor − breast = (+0.170, −0.298) H —
  the approved bird's own offset, transplanted.
- **Neck curve re-derived.** The v2 world-frame Bezier family can only make length
  by bowing deep backward. First pass with it hit the length (−0.04% err) but at
  chord-RMS 0.202 — a visibly wrong, over-bowed S (see the stage-1 overlay history
  in `solve_results.json`). The v2.1 neck therefore places its control points in
  the **breast→head chord frame** (T along chord, K perpendicular toward the nape,
  K ∝ coil): fitted constants **T1 0.53, K1 +0.364, T2 0.395, K2 −0.805**. Result:
  - **Length held: dense curve 32.62 units vs the 32.93-unit law (−0.9%)** —
    = 0.4476 H in the approved frame; 0.454 of the hold's new standing height
    (71.9 units). The conditioning polyline (5-sample) measures 31.60 units.
  - **Shape: chord-RMS 0.028** against the approved centreline (vs 0.202 first
    pass). `neck_shape_overlay.png` shows the rig spine tracking the approved
    centreline along its whole length. Max tangent step 14.6°, path monotone —
    no kinks, no loops.
  - **Widths on the silhouette: 0.098 H (t=0.45), 0.092 H (t=0.6), 0.073 H
    (t=0.75)** — spec band with the natural taper; approved mid-neck 0.0907 H.
  - **Both of Jimmy's constraints hold simultaneously** — full measured length
    AND spec width. The feared tension did not materialize; nothing was shortened.
- **Nothing else moved.** Part sizes untouched (proof 2's domain); torso bbox
  identical (55.6 × 27.7 units); plume remains its own mask channel; every other
  chart, the strike sequence, timing and trajectories untouched. `roster_charts.py`
  unmodified — the v2.1 pose lives in `pose_tracks_v21.json` (idle chart, frame 0,
  only hx/hy changed from the chart's own serialization).

### Files
- `~/workspace/heron/src13/rig13_r4_v21.py` — rig v2.1 (v2 file preserved untouched).
- `~/workspace/heron/art2/roster_render_v21.py` — renderer copy importing v2.1.
- This directory (`rig-v2/head-anchor/`): `HEAD_ANCHOR_REPORT.md`,
  `approved_measurements.json`, `strike_measurements.json`, `solve_results.json`
  (stage 1), `solve_results2.json` (stage 2, governing), `canvas_measurements.json`,
  `pose_tracks_v21.json`, `rig_v2_1_idle_silhouette.png`, `idle_hold_v21.png`,
  `overlay_v21_vs_approved.png`, `overlay_canvas_v21_vs_approved.png`,
  `neck_shape_overlay.png`, `centreline_overlay.png`,
  `centreline_overlay_strike.png`, and the measuring scripts
  (`necktools.py`, `measure_anchor.py`, `measure_strike.py`, `solve_anchor.py`,
  `solve_anchor2.py`, `measure_canvas.py`).
- Spark job: `~/heron/rigv21/` → render out `~/heron/rigv21_out/idle/f0000.png`,
  rendered with the exact Phase B path (frozen Fix-1 checkpoint
  `~/art2route2_fix/ckpt/last.pt`, `~/heron/venv` python).

A local search was run as a cross-check (63-candidate fast grid around the
anatomical anchor, full protocol on the finalists): **no candidate beat the
anatomical anchor under the full protocol** (locals 0.530–0.538 vs anatomical
0.5501). The adopted anchor is both the measured bird and the best score found —
no IoU-chasing fudge was needed or taken.

## 3. Proof (1) — before / after, identical protocol

Protocol: the shipped `measure_v2.aligned_iou` (rotations 0/±3/±6°, scales
0.8–1.35, translation ±24 px) applied by the same code to every surface.
**Certification: this pipeline reproduces Phase B's mask-surface number for
rig v2 exactly — 0.5257, the value recorded in `work/measure_v2_out.json`**
(RIG_V2_REPORT's "0.526–0.532" spans its two tuning rounds). Phase B never saved
its canvas-threshold script; a probe on the existing v2 canvas identified
luminance T=200 / T=220 as the pair bracketing its reported 0.465–0.491
(this protocol: 0.467 / 0.484), so both are reported for every canvas.

| Surface | Rig v2 | Rig v2.1 | Δ |
|---|---|---|---|
| Mask-stack silhouette IoU | 0.5257 | **0.5501** | **+0.024** |
| Canvas IoU (T=200) | 0.4671 | 0.4467 | −0.020 |
| Canvas IoU (T=220) | 0.4839 | **0.4983** | +0.014 |
| Decoder self-IoU, raw (T=200) | 0.385 | 0.193 | halved |
| Decoder self-IoU, raw (T=220) | 0.433 | 0.210 | halved |

The mask overlay (`overlay_v21_vs_approved.png`) shows the surgery working: the
head and bill now reach the approved bird's right side, and the neck runs through
the approved neck's corridor. Residual mask misses are the legs' splay, the
breast-plume hang, and torso mass placement — body terms, not head terms.

## 4. Landmark re-check (hold, v2.1 vs v2)

| Landmark | v2 | v2.1 | Note |
|---|---|---|---|
| Standing height | 73.6 u | 71.9 u | head rides 1.7 u lower at the new anchor |
| Torso bbox (absolute) | 55.6 × 27.7 u | 55.6 × 27.7 u | **unchanged — part sizes untouched** |
| Torso width / H | 0.755 | 0.773 | ratio shift is the smaller H denominator |
| Torso depth / H | 0.376 | 0.385 | same denominator effect |
| Head→bill tip / H | 0.298 | 0.305 | absolute 21.9 u unchanged (locked ratio) |
| Plume drop / H | 0.318 | 0.325 | spec ~0.33 ✓ |
| Legs | 20.4 / 19.2 | 20.4 / 19.2 | unchanged |
| **Neck length** | **27.37 u = 0.372 H** | **32.62 u = 0.448 H (approved frame)** | **the law, held: +19% longer than v2's neck, −0.9% vs measured** |
| Neck width (mid) | 0.093 H | 0.092–0.098 H | spec 0.095–0.10 ✓ |

Clipping: none (silhouette bbox x 84–671, y 106–587 inside 1024×600).

## 5. Strike still — measured only (NOT re-posed, per scope)

The approved strike still maps onto the chart's contact frames (f26–f28):

- Still: anchor (738.6, 403.6) px, breast (540, 190) px, **Δ = (+0.354, +0.380) H**,
  neck arc **0.565 H** (full-extension lunge; H = the bird's standing 562 px).
- Chart contact (hx 30, hy 20, coil 0.15): Δ = (+0.084, +0.316) H, neck arc 0.329 H.
- **Offset (chart − still) at contact: (−0.269, −0.064) H** — relative to the
  breast, the chart strike's head sits ~0.27 H behind and ~0.06 H above the
  approved strike's, and its neck spans barely half the approved extension.
  Recorded for the future strike work; nothing was changed.

## 6. Residual decomposition — what the remaining gap is made of

1. **The frozen Fix-1 decoder is now the dominant term on the canvas surface.**
   Its self-consistency — canvas vs its *own* conditioning silhouette, raw IoU —
   **halved: 0.39 → 0.19 (T=200), 0.43 → 0.21 (T=220)**. The re-posed conditioning
   is further outside its training distribution, so it paints the new bird
   fainter and further off-silhouette (`idle_hold_v21.png` is visibly washed
   out). The canvas-vs-mask drop grew from 0.04–0.06 (v2) to 0.05–0.10 (v2.1).
   That is why the canvas score is a wash even though the rig genuinely improved:
   **the anchor fix's gains cannot cash out through this decoder.** This prices
   Jimmy's option (2) honestly: a decoder retrain on registered pairs addresses
   exactly this term — worth roughly the 0.05–0.10 canvas-vs-mask drop plus
   whatever the fainter paint costs at threshold.
2. **The rig-side gap is the larger absolute term.** Even a perfect decoder caps
   at the mask surface: 0.5501, i.e. a 0.45 gap remains in body-mass placement
   (torso mass distribution, breast-plume hang, leg splay — visible in the mask
   overlay). The head/neck term this task owned is fixed; the next rig term is
   the body, and 0.85 needs that too. A decoder retrain *alone* cannot clear the
   bar; neither can rig work alone while the decoder halves its own fidelity.

**Bottom line:** anchor surgery did its job and the long neck is in, at full
measured length. Proof (1): mask 0.526 → **0.550**; canvas ~0.47–0.48 → ~0.45–0.50
(threshold-dependent, decoder-bound). Bar 0.85 not cleared on either surface.
The honest next lever is the decoder retrain (option 2), with body-mass rig work
behind it — in that order, because the decoder now taxes every rig improvement.
