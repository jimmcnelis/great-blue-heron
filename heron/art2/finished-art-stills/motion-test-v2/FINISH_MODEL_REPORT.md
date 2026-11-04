# FINISH MODEL REPORT — motion test v2

**Date:** 2026-11-03 · **Test:** `motion_test_v2.mp4` — 48-frame idle
hold + the strike cycle twice, 152 frames, 24 fps, 1024×600, same
protocol and same bars as motion test v1.
**Method under test:** the pose-conditioned finish model
(`../finish-model/MODEL_CARD.md`) — a deterministic U-Net translator
trained on the 79 gold canvas→finished pairs, replacing the per-frame
generative finish pass that failed v1.

## Verdict

| Gate | v1 (generative pass) | v2 (finish model) | Result |
|---|---|---|---|
| 1 · Fidelity at rest | PASS | black 0.123 / rust 0.006 / yellow 0.000 (approved: 0.259 / 0.036 / 0.017); IoU vs approved drawing 0.654; inside-bird MAD 53.5/255 | **FAIL** |
| 2 · Temporal (hold truly still) | FAIL — inside-bird consecutive diff median 19.1/255 | **0.0** — determinism proven (8 runs → 1 hash, max pairwise diff 0.0) | **PASS** |
| 3 · Motion truth | FAIL — release 53/31/12/4 % vs chart 25/35/40; withdrawal 5/13 wrong-way | release increments +4.6/−18.8/−99.4/+65.9 px (noise — no bill to track); withdrawal 7/13 wrong-way over a path that barely moves (278→394 vs gold 481→88) | **FAIL** |
| 4 · Sequence consistency | FAIL — f27 black 0.314 pops vs band 0.250–0.265 | no pop — but only because nothing is reproduced: model band 0.097–0.147 vs gold band 0.231–0.270; model f27 = 0.077 | **FAIL** |

**Do not bake the roster with this model.** One gate passed — the one
the pivot was structurally guaranteed to pass — and it matters (see
"What the pivot proved"). The other three fail, and they fail for a
reason that is measured, named, and not the model's fault: **the seed
corpus is not pose-registered** (below).

All numbers: `work/metrics_v2.json` (script `work/measure_v2.py`, the
v1 protocol verbatim plus bill-centroid paths).

## Gate 1 — fidelity at rest: FAIL

The model's hold frame is the approved drawing's soft echo: slate mass
in approximately the right place, rusty thighs present, warm paper
right (paper MAD 2.5/255) — but the drawing itself is absent. The
white head, black brow and occipital plumes, golden eye and dagger
bill are smeared away (yellow fraction 0.0002 vs the approved 0.0167 —
there is effectively no bill). Mark fractions vs the approved rest
drawing (band from v1's 26 accepted repaints): black **0.123** (band
0.252–0.272), rust **0.006** (band 0.035–0.037), slate **0.641**
(approved 0.465 — everything collapsed into body colour). Mask IoU vs
the approved drawing 0.654; mean absolute difference inside the bird
**53.5/255**. Under the fidelity law — *what is brought to life must
look exactly like these drawings* — this frame fails on sight, and the
numbers agree with the eye.

## Gate 2 — temporal: PASS, structurally

The pivot's core mechanism works exactly as designed. Inference is a
pure function: the hold canvas run 8 times produced **one unique
output hash with max pairwise pixel difference 0.0**
(`determinism.json`). The 48-frame hold in the test film is therefore
bit-identical frames (in-film check: extracted hold frame vs source
frame MAD 1.18, codec noise only) — inside-bird consecutive diff
**0.0/255**, against v1's shimmering 19.1/255 median. A hold is truly
still, and any repeated canvas anywhere in any future sequence yields
the identical finished frame. This property is now proven available
whenever a *registered* corpus exists to train on.

## Gate 3 — motion truth: FAIL

There is no bill to track: the model's strike outputs carry almost no
yellow, so the bill-centroid path is a centroid of smudge. Release
increments across f23→f27: **+4.6 / −18.8 / −99.4 / +65.9 px** —
non-monotonic noise, against the chart's accelerating 25/35/40 % and
even against v1's flawed-but-real 53/31/12/4 %. Withdrawal: **7 of 13
steps the wrong way**, and the path's total range (bill-y 278→394)
shows the model bird never performs the withdrawal the canvas performs
(gold: 481→88). Median mask IoU between model outputs and their own
input canvases: **0.145** — the outputs do not follow the rig's
geometry; they sit in an averaged in-between geometry (see root
cause). Probe frames (never trained on) vs gold: mask IoU 0.56–0.68,
black fraction ≈0.11–0.14 vs gold 0.23–0.27, mean bill error
≈158–166 px. Training-frame spot checks are no better (f27 IoU
0.373) — this is not a generalisation gap.

## Gate 4 — sequence consistency: FAIL

The f27 pop is gone, but vacuously: the model's entire strike sequence
runs at roughly half the gold black fraction (band **0.097–0.147** vs
gold **0.231–0.270**, f27 model 0.077 vs gold 0.314). A sequence that
reproduces nothing cannot pop — and cannot pass. The consistency the
gate exists to protect (one bird, one set of proportions, all the way
through the strike) is absent along with the fidelity.

## Root cause — the corpus is not pose-registered

Registration audit over all 79 gold pairs (canvas bird vs target bird,
content masks; `../finish-model/registration_audit.csv`, script
`work/registration_audit.py`):

- **Mask IoU: median 0.134, best pair 0.148.** The finished bird
  barely overlaps the bird in its own study canvas.
- **Scale: target bird 1.42× taller, 2.51× wider, 4.30× the area**
  (medians) than its canvas.
- **Placement: centroid shifted (+35, −63) px** median; idle pairs
  (+127, −63).

The generative pass was briefed, in writing, to lock geometry ("keep
the pose, position, size and silhouette of the bird in the first image
exactly"). It redrew each bird at its own scale and placement anyway.
Motion test v1's gate measured *identity within the finished frames* —
marks, proportions, paper — and the pass genuinely passed that; nobody
measured canvas↔target geometric agreement until this build. So the
79 "pairs" are 79 drawings of the right bird in approximately the
right pose, at the wrong size in the wrong place, each disagreeing
differently.

A deterministic translator trained on contradictory geometry has no
consistent function to learn: neighbouring strike canvases are nearly
identical while their targets are independently redrawn, so the loss
is minimised by the average — slate and rust masses at averaged
positions, detail washed out. Both training stages plateaued at
probe Charbonnier ≈0.10–0.13, which *is* the pairs' mutual
disagreement, and train frames score like held-out probes. **More
steps, a bigger model, or a different loss would not have fixed this;
the supervision itself contradicts.** This is stated as the tripwire
requires: with this corpus, exact likeness is not achievable by this
method — proven by the audit numbers above, not asserted.

## What the pivot proved (the part worth keeping)

- **Determinism is real and total** (gate 2): the boil is a property
  of per-frame generation, and it is *gone* the moment finishing is a
  fixed function of the canvas. That was the pivot's bet, and it held.
- The training/inference machinery works end-to-end at 1024×600 on the
  Spark (two-stage fit, checkpoint selection on held-out probes,
  deterministic render) and is reusable unchanged on a registered
  corpus.
- The registration audit itself is now part of the toolkit: any future
  corpus can be gated *before* training, in minutes, instead of after
  a day of compute.

## Paths forward (Jimmy's call)

1. **Build registered gold, then retrain this model.** Re-finish the
   53 seed canvases with the generative pass, but gate every accepted
   frame on geometry as well as identity: content-mask IoU vs its
   canvas ≥ ~0.90 and centroid within ~10 px, regenerate until it
   passes. The pass demonstrably holds identity; it was simply never
   held to geometry. Then the same translator, same protocol, same
   four gates. This is the only path that keeps both halves of the
   fidelity law — the same drawings *and* locked geometry. Cost: a
   generation campaign with rejection sampling (geometry gating will
   reject more frames than v1's identity-only gate did), then ~1.5 h
   of training.
2. **Warp the targets into canvas geometry and retrain.** Fast and
   needs no new generation — but the finished frames would then live
   in the study canvases' composition (bird roughly 40 % smaller,
   lower in the frame), which contradicts the approved plates, the two
   approved stills could no longer appear as themselves, and warping
   resamples the approved art. It also cannot fix the redraw's
   *internal* proportion drift (neck length, head size) with any
   global transform. Recorded for completeness; in my judgement it
   fails the fidelity law by construction.
3. **Accept a hybrid for holds only**: use this model (or the approved
   stills directly) for static holds — where determinism already
   delivers perfection — and keep hunting for an action-phase method.
   Partial; the strike is the signature behaviour and stays unsolved.

Recommendation (mine, labelled as such): **path 1** — it is the only
one that does not ask Jimmy to lower either bar he set.

## Honest limits

- 79 pairs, two pose families (hold + one strike cycle). Even a
  registered rebuild of this corpus covers nothing else; flight,
  swallow and other charts each need their own approved, registered
  finished frames before any roster bake.
- The two approved stills disagree with each other at f27 (black
  saddle). A registered corpus inherits that disagreement; arbitrating
  it is an art decision, not a training decision.
- The model's paper is right and its colour masses are placed by the
  canvas to within the corpus's (broken) registration — evidence the
  conditioning pathway works and the failure sits in the data, where
  this report puts it.

## Files

- `motion_test_v2.mp4` — the test film (152 frames).
- `frames/hold/hold_frame.png`, `frames/strike_model/` (selected
  weights), `frames/strike_ema/` — the rendered frames.
- `determinism.json` — the gate-2 proof.
- `work/metrics_v2.json`, `work/measure_v2.py`, `work/assemble.py`,
  `work/registration_audit.py` — measurement record and scripts.
- Model, corpus, audit data: `../finish-model/` (`MODEL_CARD.md`,
  `corpus_manifest.csv`, `registration_audit.csv`, `finish_model.pt`).
