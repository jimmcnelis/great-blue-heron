# Heron Finish Model, Round 3 — Phase 1 Report: Geometry-Gated Re-Finish

**Date:** 2026-11-03 · **Verdict: STOP RULE FIRES. Phase 2 (retrain + motion test v3) was NOT entered.**

- **Accepted pairs: 0 of 53 canvases.** Every canvas failed the geometry gate; the best frame under the
  best brief also failed the identity gate on all 53.
- **Best silhouette IoU ever observed: 0.5048** (strike_f0038, campaign) against a bar of **0.90**.
- **Across all 140 generative finishes ever measured for this corpus** (79 v1 gold + 61 round-3),
  **no frame has ever passed the geometry and identity gates simultaneously.**

The bar can now be re-decided with numbers in hand, which is what the stop rule exists for.

---

## 1. The gates, and one measurement decision that had to be made

The brief's gates: (a) GEOMETRY — content-mask IoU ≥ 0.90 AND centroid within 10 px; (b) IDENTITY —
black/rust/yellow fractions inside the approved bands (idle: black 0.252–0.272, rust 0.035–0.037,
yellow 0.016–0.018; strike standing frames f00–23 + f40–51 from v1 metrics: black 0.2501–0.2653,
rust 0.0335–0.0373, yellow 0.0155–0.0188). Identity fractions were computed with v1's exact
protocol (full content mask, paper-distance > 55).

**Measurement decision (flagged plainly):** the seed canvases are *sparse stipple studies* — the
canvas bird is ~23k dark pixels scattered inside a ~34k-pixel silhouette, while any finished bird
is a solid ~50–100k-pixel shape. A raw pixel-mask IoU between the stipple and a solid bird is
mathematically capped near 0.25 no matter how perfectly the finish traces the pose, so it cannot
be the judged dimension. The gate was therefore measured on **filled silhouettes**, as the brief's
own wording directs ("measure overlap of the silhouette — the judged dimension"):

- Canvas side: the rig silhouette rebuilt from the chart pose itself
  (`roster_charts` → `roster_render.kp_master` → `maskrender.build_mask_stack`, union of 8 channels).
- Finished side: the segmented bird-only mask (v1 content mask, largest component + attached
  components ≥ 200 px, clipped above the waterline).
- Gate script: `work/gate.py` (numpy/PIL/scipy, run on files in this workspace). It reproduces the
  v1 gold frames' known character (identity passes, geometry far off) and the approved strike
  still's documented out-of-band fractions, so the instrument is calibrated against the record.

Sanity bound worth knowing: the **approved bird itself**, bbox-warped onto the rig silhouette,
scores only **IoU 0.406**. The approved drawing's proportions and the rig's pose geometry are
different shapes; even a perfect tracing *of the approved bird* could not clear 0.90 against the
rig silhouette. The gate as specified demands a finish that traces the *rig*, in the approved
*bird's* identity — which is exactly what was attempted.

## 2. What was tried

Pilot first (4 canvases: idle_hold, strike_f0000, strike_f0012, strike_f0027), three brief families,
all using the same generative finishing service that produced the v1 gold frames:

| Brief | Inputs | Geometry instruction | IoU range (4 pilot frames) | Identity |
|---|---|---|---|---|
| A — v1-style | canvas + approved rest still | subordinated ("never sacrifice the approved drawing") | 0.198–0.270 | 2/4 pass |
| B — canvas-only tracing | canvas only | "treat as a tracing; outline EXACTLY; stay small; do not recompose" + identity described in text + per-frame pose caption | 0.335–0.441 | 0/4 pass |
| C — silhouette stencil | canvas + rig-silhouette PNG | "fill the black silhouette EXACTLY as a hard stencil" | 0.147–0.366 | 0/4 pass |

Brief B measured best on geometry, so it was run as attempt 1 across the remaining 49 canvases
(the campaign). The approved reference still was deliberately excluded from B and C: with it in
the prompt, its composition wins completely (brief A reproduces the v1 failure almost exactly).

## 3. Results — full IoU distribution, every finish ever measured

| Set | n | IoU min | IoU median | IoU max | Identity pass | Geometry pass | Both |
|---|---|---|---|---|---|---|---|
| v1 gold pairs (brief A family) | 79 | 0.060 | 0.241 | 0.263 | 64/79 | 0/79 | 0 |
| Round-3 pilot, brief A | 4 | 0.198 | — | 0.270 | 2/4 | 0/4 | 0 |
| Round-3 pilot, brief B | 4 | 0.335 | — | 0.441 | 0/4 | 0/4 | 0 |
| Round-3 pilot, brief C | 4 | 0.147 | — | 0.366 | 0/4 | 0/4 | 0 |
| Round-3 campaign, brief B | 49 | 0.171 | 0.381 | **0.505** | 0/49 | 0/49 | 0 |
| **All** | **140** | 0.060 | — | **0.505** | — | — | **0** |

Best-per-canvas (each canvas's best attempt): min 0.171, median 0.381, max 0.505, mean 0.382.
Full per-canvas record — best IoU, centroid delta (dx, dy, distance), attempts made/measured,
identity fractions of the best frame, status — is in **`registration_audit_v2.csv`** (53 rows).
Every attempt is archived under `attempts/` and logged in `work/attempts_log.csv` (63 rows).
`corpus_manifest_v2.csv` contains the header only: there are no accepted pairs to manifest, and
`target/` is empty.

**Why the generator misses:** under every brief it redraws the bird at **1.5–2.9× the silhouette
area** (finished birds 44k–97k px vs ~32–34k px silhouettes) with deeper bodies, thicker necks,
and added feet/toes the rig doesn't draw. Brief B's tracing language roughly halved the overshoot
vs v1 (median IoU 0.241 → 0.381) but the redraw is structural, not a tail event: 140 samples, a
flat distribution, and a hard ceiling at ~0.50. The two gates also trade off against each other —
the identity-tuned v1 brief passes identity and fails geometry; the geometry-tuned brief B
improves geometry and fails identity on 53/53 best frames (black runs 0.27–0.33, rust up to 0.05,
yellow down to 0.008). No prompt variant held both.

## 4. Stop-rule accounting — and an honest caveat

The brief's stop rule: if ~20%+ of canvases end stuck (cap of 12 attempts exhausted), stop before
retraining and report the distribution. **53 of 53 canvases (100%) are unaccepted**, so the rule
fires in substance by an enormous margin.

Caveat, stated plainly: the per-canvas 12-attempt caps were **not** exhausted. Round 3 made 62
generation calls (61 images; pilot canvases 3 attempts each, campaign canvases 1, strike_f0001 2
calls) against a cap budget of 636. Canvases are therefore recorded in the audit as
`not_accepted`, not `stuck` under the cap definition. The reason for not burning the cap: after
140 measured finishes across three brief families the distribution is flat (median 0.38, max
0.505, zero joint gate passes, and a 0.406 structural bound for the approved bird's own shape).
The remaining ~570 calls would refine the second decimal of a distribution whose top end sits
0.40 below the bar; the per-attempt success probability is not measurably different from zero.
If the bar is re-decided, the honest numbers for that decision are the ones above.

**Service errors (disclosed):** 1 generation call lost in round 3 — strike_f0001 attempt 1,
`integrity_check_failed` — retried successfully (its measured IoU 0.352, identity fail). No other
losses. (Historical context: v1 lost 17 attempts to service errors.)

## 5. What re-deciding the bar would have to reckon with

These are the options the numbers leave open; choosing among them is Jimmy's call, and none was
taken here:

1. **Lower the geometry bar.** Even at IoU ≥ 0.50, exactly 1 of 53 best frames qualifies — and it
   fails identity. A bar near 0.38 (the median) would "accept" frames whose birds are ~1.5× the
   rig's size with different proportions; training on them re-creates the v2 blur in milder form.
2. **Change the canvas↔bird relationship upstream** — e.g., re-derive the rig geometry from the
   approved bird's proportions, so a tracing of the approved identity *can* register. This is a
   roster/canvas change, outside this brief's constraints (and the warp path remains rejected:
   warping finished targets into canvas geometry was explicitly ruled out).
3. **Change the finishing mechanism** — a mask-conditioned fill (silhouette as a hard constraint,
   identity painted inside it) rather than a free generative redraw. That is not "the same
   generative finishing approach" this round was specified to use, so it needs its own go-ahead.

## 6. Surfaces & integrity

- Generation: the media generation pipeline (image-edit generations run by child crews; files
  landed directly in this workspace under `pilot/` and `campaign/`).
- Measurement: `work/gate.py` on files in this workspace (local VM, numpy/PIL/scipy). Rig
  silhouettes pre-rendered to `work/silhouettes/` from the art2 roster modules.
- **No training was run; the Spark was not used; nothing was installed or flashed.**
- **All v2 artifacts are untouched** — every round-3 file lives under `refinish-corpus/`
  (`canvas/` holds copies of the seed canvases; originals unmodified).

## 7. Deliverables

- `registration_audit_v2.csv` — per-canvas gate record (53 rows).
- `corpus_manifest_v2.csv` — header only (0 accepted pairs).
- `attempts/` — all 61 round-3 generated frames, named `<pair>_a<n>.png`.
- `work/gate.py`, `work/attempts_log.csv`, `work/campaign_measure_tmp.jsonl`,
  `work/v1_gold_measure.jsonl`, `work/pose_captions.json`, `work/silhouettes/` — instruments
  and raw measurements behind every number above.
- This report. Phase 2 deliverables (FINISH_MODEL_V3_REPORT.md, motion-test-v3/) do not exist,
  per the stop rule.
