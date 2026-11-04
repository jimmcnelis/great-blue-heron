# MODEL CARD — the heron finish model v3 (pose-conditioned, deterministic)

**Built:** 2026-11-04 (night), DGX Spark (GB10), at Jimmy's order —
the decoder retrain held LAST until the rig body settled (rig
v2.4, band pass complete), then run once.

**Status: NOT APPROVED FOR PRODUCTION — motion test v3 FAILED
gates 1, 3 and 4 (see `../../motion-test-v3/MOTION_TEST_V3_REPORT.md`).**
The geometry half of the v2 failure is fixed and proven; the
engraving's ink is not reproduced. Do not bake the roster with
these weights.

## What changed vs v2 (data only — architecture and recipe verbatim)

- **Inputs:** palette canvases rendered from the **rig v2.4 mask
  stacks** (8 part channels, fixed palette, painter-order
  composite) instead of the old Route-2 stipple canvases. The
  input bird is the settled rig's silhouette, exact by
  construction.
- **Targets:** the same 79 gold finished frames, each
  **similarity-registered onto its frame's rig silhouette**
  (moment fit + IoU hill-climb; fitter calibrated against the
  geometry protocol: 0.684 vs their 0.691 on the approved idle
  pair). Pair registration: **median IoU 0.615** (bird-only
  0.645; min 0.455 / max 0.717) vs v2's 0.134. Structural ceiling
  ≈ 0.68 (the approved still's own fit to the rig).
- Same U-Net (19.9M), same losses (Charbonnier + Sobel ×0.5 +
  Laplacian ×0.25), same identical-warp augmentation, same probe
  holdout (strike f06/f25/f34/f45), same two stages.

## Training (as run, Spark `~/heron/finish-model-v3/`)

- Stage A (512×304, batch 8, lr 2e-4, 3,600 steps): probe
  Charbonnier EMA 0.672 → **0.0788** (v2: 0.101).
- Stage B (1024×608, batch 4, lr 8e-5, 900 steps): → **0.0837**
  (v2: 0.133).
- Checkpoint selection on probes: **raw** weights (probe IoU
  0.672) over EMA (0.650); EMA kept and rendered alongside.

## Measured character (motion test v3)

- Determinism absolute: 8 runs → 1 hash, max pairwise diff 0.0.
- Rest fidelity: IoU 0.813 vs the registered approved still;
  yellow in band; black 0.126 vs approved 0.259 — the ink halves.
- Geometry lock: outputs vs their own rig silhouettes, median
  IoU 0.646 (v2: 0.145).
- Weakest at fast/rare poses: f27 black 0.070 vs gold 0.371;
  f25 head/bill smear. Probes ≈ train frames — a capacity/texture
  limit, not a generalisation gap.

## Files

- `build_corpus.py` — corpus construction + registration.
- `registration_audit_v3.csv` — per-pair fit record (79 rows).
- `corpus/` + `corpus_manifest.csv` — the 79 registered pairs.
- `train_finish.py`, `infer_finish.py` — the v2 scripts, verbatim.
- `finish_model_v3.pt` — stage-B final checkpoint (raw + EMA).
- `render_v3/` — the test render (hold + both strike weight sets).
