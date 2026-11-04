# MODEL CARD — the heron finish model (pose-conditioned, deterministic)

**Built:** 2026-11-03, DGX Spark (GB10), at Jimmy's decision — the pivot
from the generative finish pass after motion test v1 failed temporal
consistency and action-phase motion truth.

**Status: NOT APPROVED FOR PRODUCTION — motion test v2 FAILED gates 1,
3 and 4 (see `../motion-test-v2/FINISH_MODEL_REPORT.md`).** The
mechanism is proven (gate 2, determinism, passes absolutely); the
training corpus is not pose-registered, so exact likeness was not
learnable from it. Do not bake the roster with these weights.

## What it is

A deterministic paired image translator: Route-2 study canvas in
(1024×600) → finished Audubon frame out (1024×600). There is **no
sampling anywhere in the pipeline** — no diffusion steps, no noise
input, no dropout at inference. The same canvas produces the same
finished frame on every run — verified empirically: 8 runs of the hold
canvas produced **1 unique output hash, max pairwise pixel difference
0.0** (`../motion-test-v2/determinism.json`). That is the structural
property the generative pass could not give: holds are truly still and
neighbouring frames share one bird by construction, not by prompt
discipline.

## Architecture

- U-Net encoder–decoder with skip connections; residual blocks
  (GroupNorm + SiLU) at four scales (64/128/256/512 channels), one
  self-attention block at the 64×38 bottleneck; 19.9M parameters.
- Input padded 600→608 px high (reflect) so every scale divides
  evenly; output cropped back to 1024×600, tanh head.
- Losses (the Fix-1 family, chosen because they protect engraved
  linework): Charbonnier pixel loss + Sobel gradient L1 (×0.5) +
  Laplacian high-frequency L1 (×0.25). **No adversarial term** — a
  discriminator rewards plausible invention; this model's job is to
  reproduce *these* drawings, not plausible ones.
- Augmentation: identical-warp — the same random affine (±10 px,
  ±2 % scale, ±0.6°) + smooth elastic (≤6 px) warp applied to canvas
  AND target, so output geometry is trained to move in lockstep with
  input geometry. No colour augmentation: paper tone and mark colours
  are part of the drawing's identity.

## Training (as run)

Two stages on the Spark (`~/heron/venv`, torch 2.15.0+cu132):

- **Stage A — bulk fit, half resolution** (512×304): batch 8, lr 2e-4,
  3,600 steps, ~59 min. Held-out probe Charbonnier (EMA weights):
  0.665 → **0.101**.
- **Stage B — full-res texture phase** (1024×608): initialised from
  stage A's final weights; batch 4, lr 8e-5, 900 steps, ~32 min.
  Probe Charbonnier: 0.167 → **0.133**.

Both raw and EMA weights were rendered for the test; the set used was
selected on the held-out probe frames (mask IoU vs gold: **raw 0.626**
vs EMA 0.543) — selection, not assumption. `finish_model.pt` is the
stage-B final checkpoint (contains both weight sets; inference selects
between them).

The probe loss plateaued at ≈0.10–0.13 in both stages. That plateau is
not under-training: it is the measured disagreement between the pairs
themselves (see the registration finding below). Train-frame spot
checks score as badly as held-out probes (strike f27, a *training*
frame: mask IoU vs its gold target 0.373) — the model cannot fit pairs
whose geometry contradicts the neighbouring pairs.

## Corpus

`corpus_manifest.csv` — **79 gold pairs**, every finished Audubon
frame in existence at build time:

- 52 strike pairs: each Route-2 strike canvas ↔ its gate-passed
  finished frame from motion test v1, including the approved strike
  still itself (f27).
- 27 idle pairs: the single hold canvas (byte-identical across
  idle_hunt chart frames 0–70, md5-verified) ↔ the 27 finished hold
  repaints, including the approved rest still itself (chart f30).

**Held out (probe, never trained on):** strike f06 (standing), f25
(release), f34 (withdrawal), f45 (recover). Training pairs: 75.

**Augmentation from the unfinished roster: NOT used.** The other
1,925 canvases have no finished targets and no trustworthy way to make
any (the only finish process that exists produced the 79).
Pseudo-labelling them would train the model on unapproved art.

## ⚠️ The registration finding (why the test failed)

The corpus pairs are **not geometrically registered**. Measured over
all 79 pairs (`registration_audit.csv`, script
`../motion-test-v2/work/registration_audit.py`):

- Canvas-bird ↔ target-bird content-mask IoU: **median 0.134**, best
  pair 0.148. The bird in the finished frame barely overlaps the bird
  in its own canvas.
- Target bird vs canvas bird: **1.42× taller, 2.51× wider, 4.30× the
  mask area** (medians).
- Centroid offset (target − canvas): median **(+35, −63) px**; idle
  pairs (+127, −63).

The generative pass was briefed to lock geometry ("keep the pose,
position, size and silhouette exactly"); it redrew each bird at its
own scale and placement anyway. Motion test v1's gate measured
identity — marks and proportions *inside* the finished frames — and
passed it; canvas↔target geometric agreement was never measured until
this audit. A deterministic translator trained on these pairs is being
asked to satisfy two contradictory mappings at once, so it converges
to their average: correct colour masses in roughly averaged positions,
drawing detail washed out. **No step budget fixes contradictory
supervision.** Any future finish-model attempt must start from a
registered corpus (paths in the v2 report).

## What 79 pairs would limit, even registered

- Two pose families only (standing/hold + one strike cycle). Flight,
  swallow, front view are outside the corpus; the model must not be
  trusted there without new approved stills.
- The two approved stills disagree with each other in the strike
  (f27's oversized black saddle, black fraction 0.314 vs the sequence
  band 0.231–0.270). A model trained on both reproduces both,
  including the disagreement. Only Jimmy can arbitrate between two
  approved drawings.

## Inference

```
cd ~/heron/finish-model
~/heron/venv/bin/python infer_finish.py train_outB
```

(Checkpoint defaults to `<out_dir>/ckpt_final.pt`.) Deterministic:
eval mode, fixed weights, no sampling. Renders the hold frame and all
52 strike canvases under both weight sets (`strike_model/`,
`strike_ema/`), after running the hold canvas 8× for the determinism
proof (`determinism.json`).

## Files

- `train_finish.py` — model, data, losses, two-stage training loop.
- `infer_finish.py` — deterministic inference + test render.
- `corpus/` + `corpus_manifest.csv` — the 79 gold pairs (md5s listed).
- `registration_audit.csv` — per-pair canvas↔target geometry deltas.
- `finish_model.pt` — stage-B final checkpoint (raw + EMA weights).
- Training also lives on the Spark under `~/heron/finish-model/`
  (`train_outA/`, `train_outB/`, `trainA.log`, `trainB.log`).
