# STRIKE SEQUENCE — DENSIFIED BUILD vs LOCKED HOME FRAME — FINAL REPORT

Built 2026-11-05 (~19:20 UTC), crew order: resume + complete densification against
the Jimmy-approved home frame. Working dir: fresh/. Supersedes REPORT.md (v1).

## Deliverables (all in fresh/)

| File | What | Size |
|---|---|---|
| timing.json | 60 ticks, 12 fps, 5.0 s; tick 0–9 and 58–59 = HOME (index 0) | — |
| strike_device_1024x600_20261105-1920.mjpeg | device stream, 30 unique drawings, PIL q82, subsampling=1 | **1,793,427 B (under the 2.5 MB cap)** |
| heron_strike_bird_20261105-1920.mp4 | bird-only preview @12 fps, 2048×1152 → 1280×720 | 1,761,148 B |
| heron_strike_marsh_20261105-1920.mp4 | in-marsh preview (multiply over marsh_plate_pick) @12 fps | 1,801,450 B |
| proof_leg_band_20261105-1920.png | leg band of all 30 chain drawings | — |
| proof_water_continuity_20261105-1920.png | strip: K_peak → W_125 → X1 → W_500 → W_875 → HOME | — |
| registered_v2/ | all 30 registered finals (HOME byte-identical to home_frame_approval.png, md5-verified) | — |
| build_v2.py / normalize_color_v2.py / rebuild_final.py | the pipeline | — |

SOF check: first frame of the MJPEG, luma sampling byte **0x21** (true 4:2:2) ✓.
timing_delivered_v1.json preserved; v1 device stream + registered/ untouched.

## Registration

One uniform transform for the whole chain, fit to the LOCKED home frame:
**scale 0.80, offset (+48, +204)** (replaces v1's 0.88/−61/+127). Validation:
grounded landmarks (bill tip, both feet) land exactly on the home frame's;
thresholded ink-IoU of registered K_coil vs home = 0.959 (th170) / 0.963 (th200)
over the bird bbox (paper texture caps the score, not placement). Registered HOME
is the approval PNG verbatim. Paper normalized per drawing to (245,233,219);
canvas paper is the home frame's own blank patch, so the field is one paper.
Feet, measured per registered frame: front-foot centre 14.97–15.19% of width
(HOME itself: 15.19/20.36 — the approved spec), rear 19.82–20.61%. Legs/feet
planted across all 30 drawings; the whole bird is inside the frame everywhere
(tail margin 3.56% at home).

## Per-interval outcomes (17 planned in-betweens)

Anti-clone gate applied throughout: candidate bill tip strictly between its
neighbours, ≥15% of the interval from either end (t ∈ [0.15, 0.85]), measured
and tabulated; every frame also view-gated by its worker and the coordinator.

**ACCEPTED into the final stream — 2:**
- **X1** (W_250→W_g2_1): tip (592,809), t≈0.48. Coordinator-viewed: clean early
  withdrawal, droplets, frill whole, feet planted. Nits: touch rings wide-ish;
  bill saturation sits slightly toward the home register.
- **X11** (W_g5_3→W_625): tip (489,805), t=0.63. Clean measured pass (69.6/44.7
  vs 15.8 floor); ~28 units off the straight line — the natural tuck arc.
  Measured bird saturation 30.2 = in family (the "pale bill" impression in one
  preview frame was not borne out by measurement).

**ACCEPTED at the tip gate, then REMOVED at final visual QA — 1:**
- **X6** (W_g3_2→W_500): tip (594,732) — passes the distance form of the gate but
  note honestly: projection t=0.883 on an 18-unit interval; the tip sits 2.8 units
  from W_500 vs a 2.7-unit floor, inside tip-grounding noise (±3–5). Its source
  generation also carries the bluest crown in the set, and the colour-normalization
  lift (k=2.09, the strongest) pushed that crown to an electric blue that pops for
  its one tick (verified in preview frame t31 vs raw poses/W_x6.png). Removed
  rather than locally recoloured. Cost of removal: nil measurable — W_g3_2→W_500
  is now a single 18.0-unit step, below the local-median flag threshold; W_g3_2
  absorbs the tick (×3).

**FAILED / clone-rejected — 14 (each reverts to a 2-tick hold or timing step):**
- **X0 peak-exit** (K_peak→W_125, Δ144): 2 attempts, both cloned the target. The
  order's explicit cap applied — the exit is genuinely binary (bill in water /
  bill fully out). One-tick step kept.
- **X2** (Δ36): 3 attempts incl. coordinator reversed-anchor (tip (603,794),
  t=0.083 — clone-side). 
- **X4** (Δ45): 3 attempts incl. coordinator reversed (tip (591,847) — below both
  neighbours).
- **X7** (Δ63): 3 attempts. Best candidate measured tip (596,679), t=0.873 —
  past the 0.85 line, and its body had shifted bluer. (Contrast X6: accepted on
  distance-form + view verdict on a sub-noise interval; disclosed in full.)
- **X8** (Δ96): target clone, then overshoot. **X9** (Δ24): two overshoots past
  target. **X10** (Δ49): two ≈target clones.
- **X13a + X13b** (W_750→W_875, Δ167 — the known gap): 4 attempts — upright
  invention, overshoot past target, W_750 clone with saturated recolour,
  no-diagonal-travel miss. **Still the largest single step in the sequence.**
- **X14** (Δ79): overshoot + spurious second ripple; retry = target clone.
  **X15** (Δ32): target clone, then overshoot. **X16** (Δ11): bracket missed
  both sides. **X17** (Δ26): both attempts below target.
- **X20** (W_g7_6→HOME, Δ82): 3 attempts incl. coordinator with explicit
  tip-height landmark — overshoot past home (full-body recolour), a near miss
  whose head rose off the settle path (508,798), and a coordinator candidate
  whose head plunged ~75 units off-path (536,906). The final step home stands.

The five documented sub-noise intervals (Δ1.4–5.1) were left as held drawings
per orders — no clones manufactured.

Pattern, stated plainly: on fine intervals the edit model clones a neighbour or
overshoots to a stock pose. 20+ generations this pass confirmed round 1's
lesson. Densification landed only where a fractional head position is a pose
the model can actually hold — early withdrawal (X1) and the tuck (X11).

## Bill-tip tables (raw-canvas coordinates, 0–1000 scale)

Anchors: HOME/K_coil (472,848) · E_125 (537,817) · E_250 (577,814) ·
E_500 (643,840) · E_750 (607,922) · E_875 (614,957) · K_peak (596,954) ·
W_125 (602,810) · W_250 (598,823) · W_g2_1 (603,797) · W_g2_2 (601,761) ·
W_250_alt (602,760) · W_g3_1 (600,715) · W_g3_2 (595,716) · W_500 (596,734) ·
W_375 (604,672) · W_g5_1 (587,766) · W_g5_2 (571,784) · W_g5_3 (554,830) ·
W_625 (449,823) · W_750 (447,820) · W_875 (562,696) · W_g7_1 (555,775) ·
W_g7_2 (556,807) · W_g7_3 (553,796) · W_g7_4 (551,822) · W_g7_5 (550,824) ·
W_g7_6 (550,823). New: X1 (592,809) · X11 (489,805).
(E_500's tip x=643 rides right of K_peak's 596 — the known right-riding head on
the unfolding arc; E_* anchors were grounded this session.)

## Per-tick deltas (non-zero steps; flag = >1.5× local median, window ±2)

| tick | step | Δ | disposition |
|---|---|---|---|
| t10 | HOME→E_125 | 72.0 | strike launch (extension, by design fast) |
| t11 | E_125→E_250 | 40.1 | — |
| t12 | E_250→E_500 | 70.9 | — |
| t13 | E_500→E_750 | 89.6 | FLAG — extension acceleration + E_500's known head position; pre-existing verified material |
| t14 | E_750→E_875 | 35.7 | — |
| t15 | E_875→K_peak | 18.2 | — |
| t17 | K_peak→W_125 | 144.1 | FLAG — X0 capped at 2 attempts (order); binary exit; W_125 held 3 ticks so the eye lands after it |
| t20 | W_125→W_250 | 13.6 | — |
| t22 | W_250→X1 | 15.2 | densified ✓ |
| t23 | X1→W_g2_1 | 16.3 | densified ✓ |
| t24 | W_g2_1→W_g2_2 | 36.1 | FLAG — X2 failed (3 attempts) |
| t26 | W_g2_2→W_250_alt | 1.4 | sub-noise hold, by design |
| t28 | W_250_alt→W_g3_1 | 45.0 | FLAG — X4 failed (3 attempts) |
| t29 | W_g3_1→W_g3_2 | 5.1 | sub-noise hold, by design |
| t32 | W_g3_2→W_500 | 18.0 | X6 removed at QA (see above); no flag at this size |
| t34 | W_500→W_375 | 62.5 | FLAG — X7 failed (3 attempts) |
| t35 | W_375→W_g5_1 | 95.5 | FLAG — X8 failed; this is the re-coil dip, the head genuinely dives here |
| t36 | W_g5_1→W_g5_2 | 24.1 | — |
| t38 | W_g5_2→W_g5_3 | 49.0 | — |
| t39 | W_g5_3→X11 | 69.6 | FLAG (marginal, 1.59×) — X11 split Δ105 into 69.6 + 43.9; net improvement, kept |
| t40 | X11→W_625 | 43.9 | — |
| t42 | W_625→W_750 | 3.6 | tuck hold, by design |
| t44 | W_750→W_875 | 169.1 | FLAG — **largest step in the sequence**; X13a/b failed (4 attempts) |
| t45 | W_875→W_g7_1 | 79.3 | FLAG — X14 failed |
| t47 | W_g7_1→W_g7_2 | 32.0 | — |
| t49 | W_g7_2→W_g7_3 | 11.4 | — |
| t51 | W_g7_3→W_g7_4 | 26.1 | FLAG by ratio only (settle median is tiny); absolute size small; X17 failed |
| t53 | W_g7_4→W_g7_5 | 2.2 | — |
| t55 | W_g7_5→W_g7_6 | 1.0 | — |
| t58 | W_g7_6→HOME | 81.9 | FLAG — X20 failed (3 attempts); W_g7_6 held 3 ticks beforehand so it reads as a deliberate final settle |

Timing choices where generation failed: holds lengthened around the biggest
steps (W_125 ×3 after the binary exit; W_g7_6 ×3 before the step home; settle
frames ×2 throughout) so each jump is bracketed by stillness rather than
compounding motion.

## Colour normalization (disclosed, measured)

The delivered chain sat ~15 saturation points below the locked home frame
(mean bird-pixel HSV saturation: HOME 46.5; chain 29.4–33.9). Per the order
(final normalization references the home register), every registered frame
except HOME received a distance-weighted chroma lift aimed at 46.5
(paper pixels untouched). Measured result: chain now 37.7–41.4, internally
tight; residual gap to HOME ≈ 5–9 points — the lift saturates before the
target because low-chroma graphite shading resists gain, and pushing further
distorts hues (it already exposed X6's crown). Honest bottom line: the
boundary step is roughly halved, not zero; HOME remains the richest frame,
which also suits its role as the still. If a zero-step boundary is required,
the remaining lever is regenerating the chain in the home register, not more
gain. X6's outlier correction (22.2 → 34.8) is moot — the frame was removed.

## Laws check

Legs/feet planted via canvas, numerically verified (above); frill whole in
every viewed frame; water continuity monotone (proof strip: rings born at
peak → droplets + spread at W_125/X1 → fading at W_500 → faint at W_875 →
calm + feet rings only at HOME; feet rings constant); blank paper in sequence
frames (marsh appears only in the preview composite); identity anchored on
prof_d + approved drawing + locked home frame on every generation call.

## Bottom line

**30 unique drawings** (28 inherited anchors + X1 + X11), 60 ticks, 5.0 s,
1,793,427-byte device stream — under cap, SOF-verified, first/last frame the
locked home frame itself. Densification succeeded on 2 of 17 intervals
(plus 1 removed at QA); the withdrawal is now on 1s through the early span
and the tuck, but four honest steps remain: the binary peak-exit (Δ144,
capped by order), the re-coil pair (Δ63/Δ96), the W_750→W_875 gap (Δ169,
still the worst), and the final settle home (Δ82). Each carries its measured
reason above. Whether those steps pass Jimmy's lifelike bar is a viewing
judgment on the delivered previews — the numbers say where to look:
t17, t35, t44, t58.
