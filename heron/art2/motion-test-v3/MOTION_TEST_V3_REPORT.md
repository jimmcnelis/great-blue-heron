# MOTION TEST V3 REPORT — finish model retrained on the settled rig v2.4

**Date:** 2026-11-04 (night) · **Test:** `motion_test_v3.mp4` — 48-frame
idle hold + the strike cycle twice, 152 frames, 24 fps, 1024×600,
same protocol and same four gates as motion tests v1 and v2.
**Method under test:** the pose-conditioned finish model (the v2
architecture and recipe, unchanged) retrained on rig v2.4 — the body
Jimmy ordered settled first, with the decoder retrain LAST and only
once. This was that retrain.

## Verdict

| Gate | v2 (unregistered corpus) | v3 (registered, rig v2.4) | Result |
|---|---|---|---|
| 1 · Fidelity at rest | FAIL — black 0.123 / rust 0.006 / yellow 0.000; IoU 0.654; MAD 53.5 | black **0.126** / rust 0.028 / yellow **0.016 in band**; IoU vs registered approved **0.813**; MAD **32.1** | **FAIL** |
| 2 · Temporal (hold truly still) | PASS — diff 0.0 | **PASS** — 8 runs → 1 hash, max diff 0.0; in-film hold MAD 0.008 | **PASS** |
| 3 · Motion truth | FAIL — no bill to track; withdrawal 7/13 wrong-way over a path that barely moved | release profile **[70/0/29/0]%** vs gold [45/24/14/18]%; endpoint 509 vs gold 563; f25 head smears; withdrawal endpoints agree, wrong-way 5/13 vs gold's own 6/13 | **FAIL** |
| 4 · Sequence consistency | FAIL — model band 0.097–0.147 vs gold 0.231–0.270 | model band **0.070–0.208** vs gold 0.214–0.269; f27 inverted (model's least-black frame where gold carries the saddle) | **FAIL** |

**Do not bake the roster with this model.** One gate passes, three
fail — but the failure has *moved*, and where it moved to is the
measurable result of the night: **the geometry problem is closed;
what remains is ink.** Every structural number improved by a large
factor (registration of the training pairs 0.134 → 0.615; outputs'
agreement with their own rig silhouettes 0.145 → 0.646; rest IoU
0.654 → 0.813; probe losses ~25–35% below v2 at both stages). What
the model still cannot do is reproduce the engraving itself: the
drawings' black mass halves in its hands (black fraction 0.126
against the approved 0.259), fine line averages into soft slate
tone, and the fastest, least-supported poses (release, extension)
come out faint and smeared. Under the fidelity law — *the same
quality in the moving art as the drawn example* — a soft painterly
rendering of the right bird in the right place is still not the
drawing brought to life. That is Jimmy's bar, and this test does
not clear it.

All numbers: `work/metrics_v3.json` (script `work/measure_v3.py`,
the v2 protocol with gold references repointed at the registered
corpus). Registration record: `../finished-art-stills/finish-model-v3/
registration_audit_v3.csv`.

## Phase 1 — the corpus, registered (the v2 failure mode, closed)

Training pairs: the same 79 gold pairs and the same probe holdout
(strike f06/f25/f34/f45) as v2. Two things changed, both ordered:

- **Inputs** are palette canvases rendered from the **rig v2.4 mask
  stacks** (`rig13_r4_v24` + `maskrender_v2.build_mask_stack`, the
  geometry rounds' own construction; poses frozen — idle from the
  v2.4 tracks, strike from the v2 tracks). The input bird *is* the
  settled rig's silhouette: exact by construction. Frame
  correspondence was tested before pairing (gold targets fitted
  against neighbouring rig silhouettes k±2): the discriminating
  frames (f25, f30) peak at their own index — no phase offset.
- **Targets** are the gold finished frames **similarity-registered
  onto each frame's rig silhouette** (uniform scale + rotation +
  translation fitted from bird-mask moments, hill-climbed on IoU;
  the fitter was calibrated first against the geometry rounds' own
  protocol score on the approved idle pair: mine 0.684 raw / 0.731
  bird-only vs their 0.691 / 0.740).

**Registration achieved (all 79 pairs):** mask IoU of target vs rig
silhouette, median **0.395 before → 0.615 after** the fit (bird-only
0.645; min 0.455, max 0.717). Reference points: v2 trained at
canvas↔target IoU median **0.134**; and the ceiling is structural —
the approved rest still itself fits the rig at only 0.684, because
the drawing's internal proportions are not the rig's. The corpus
sits near that ceiling. Registered targets keep their identity
(strike black median 0.251, in the approved band; idle black 0.240,
~0.012 softened by warp resampling — recorded, not hidden).

**Training** (Spark, v2's two-stage recipe verbatim): stage A probe
Charbonnier (EMA) 0.672 → **0.0788** (v2: → 0.101); stage B →
**0.0837** (v2: → 0.133). Checkpoint selection on the held-out
probes, per protocol: raw weights win on probe IoU (0.672 vs EMA
0.650) — the film uses raw. (EMA's probe bill error was better,
13.0 vs 19.7 px; both weight sets' frames are delivered.)

## Gate 1 — fidelity at rest: FAIL

The hold frame is, for the first time, *the bird in the right
place*: white head with black brow and occipital plumes, golden
dagger bill (yellow fraction **0.0163**, inside the approved band
0.016–0.018 — v2 had effectively no bill at 0.0002), rusty thighs,
strand plume, long neck, right paper (MAD 2.3). Mask IoU against
the registered approved still **0.8125**; inside-bird MAD **32.1/255**
(v2: 53.5). Then the law's actual question — is it the *drawing*?
No. The engraving's ink is not there: **black fraction 0.126
against the approved 0.259 (band 0.252–0.272)**, slate swollen to
0.614 against 0.465, rust low at 0.028 against 0.036. The hatching
that carries the approved bird's darkness renders as mid-grey wash;
edges melt; a faint checker texture rides the body (the half-res
stage's signature); the paper carries a soft rectangular tonal
step. It reads on sight as a competent watercolour *of* the bird —
not as Audubon's plate, moving. Fail, of a new kind: v2 failed
shape and marks together; v3 fails marks and texture with the
shape right.

## Gate 2 — temporal: PASS, absolutely

Inference is a pure function, re-proven on the new weights: the
hold canvas run 8 times produced **one unique output hash, max
pairwise pixel difference 0.0** (`frames/determinism.json`). In the
assembled film, hold frames 5 and 40 differ by MAD **0.008**
(identical), and sit 1.16 MAD from the source PNG — codec noise
only, the same signature as v2's pass. A hold is truly still.

## Gate 3 — motion truth: FAIL

There is a bill to track now — the v2 gate's precondition — and the
extension *direction* is a spear, not v1's bow: the neck drives
down to the water in line. The timing and the depth are wrong:

- **Release (f23→f27, bill-centroid-y):** gold descends
  177 → 349 → 440 → 493 → 563 px, increments [172, 90, 53, 70] =
  [44.6, 23.5, 13.8, 18.2]%. The model: 173 → 409 → 410 → 509 →
  509, increments [237, 1, 99, 0] = **[70.3, 0.4, 29.3, 0.0]%** —
  the lunge fires almost entirely in the first interval, stalls,
  steps once more, and stops **~54 px short** of the gold's full
  depth (509 vs 563).
- **The extension frame itself (f27)** is the model's weakest:
  black fraction **0.070** against the gold's 0.371 — a faint,
  hunched ghost at the pose that defines the behaviour (see
  `sidebyside/strike_f0027_extension.png`). At **f25** the head
  and bill smear, with dark fragments floating detached off the
  neck (`sidebyside/strike_f0025_release.png`).
- **Withdrawal (f28→f41)** is the least-bad segment: endpoints
  agree (model 156 vs gold 174), and wrong-way steps are 5/13
  against the gold drawings' own noisy 6/13 on this measure. The
  model's path is two-phase with a plateau at ~410 (f30–f35)
  where the gold retracts more continuously — a difference of
  shape, inside a pass neither side earns cleanly.

Held-out probes score like training frames (IoU vs gold: probes
0.50–0.85, train spots 0.60–0.89) — this is not a generalisation
gap. It is the same averaging that softens the hold, concentrated
where neighbouring canvases change fastest and support is thinnest.

## Gate 4 — sequence consistency: FAIL

No v1-style pop — but the sequence runs at roughly **half the
gold's ink** throughout: model black band (excluding f27)
**0.070–0.208** against gold **0.214–0.269**, and at f27 the
relationship inverts — the gold's black saddle (0.371) meets the
model's palest frame (0.070). One bird, one set of proportions,
all the way through the strike: the proportions now hold (median
IoU of outputs vs their own rig silhouettes **0.646**, against
v2's 0.145); the *marks* do not.

## The carried flag — torso length in motion

The band pass carried a warning: rig torso 0.849 H against the
spec's ~0.80, centroid +0.077 H forward — "if the length still
reads wrong in motion test v3, it is a proportion-spec question."
Measured on a clean surface (largest-component bird mask, scenery
band excluded): the model hold's bird extent ratio (width/height)
is **1.282** against the registered approved bird's **1.297** — a
~1% difference. **The length does not read.** The painted bird's
overall extent matches the approved bird's; whatever the hull's
landmark numbers say, the finish does not wear a long body. This
flag can be retired on the evidence of the hold. (The strike
frames were not separately extent-measured; at their fidelity a
landmark read would be measuring the smear, not the body.)

## What this retrain proved (the part worth keeping)

- **Registration was the geometry problem, and it is solved.**
  Pairs at 0.615 median IoU (ceiling ~0.68) trained a model whose
  outputs sit on the rig (0.646) and on the approved bird at rest
  (0.813) — the blurred-*placement* failure of v2 does not recur.
  The rig-rebuild programme (v2 → v2.4) is vindicated end-to-end:
  the settled body hands the finish correct geometry, and the
  finish now keeps it.
- **Determinism is again absolute** — the stillness the creature
  engine is built on survives the retrain.
- **The remaining failure is isolated and named:** engraved ink —
  black mass, hatch texture, edge hardness — is what a
  deterministic translator trained on ~75 pairs at this recipe
  averages away, worst at fast/rare poses. It is a texture
  problem, not a geometry problem, and no further *geometry* work
  (band passes, IoU searches) will touch it.

## Paths forward (Jimmy's call — none taken here)

1. **Attack the ink directly**: a texture-weighted retrain —
  full-resolution throughout, longer texture phase, losses weighted
  toward dark-line reproduction. This spends another retrain; the
  standing order was retrain ONCE on the settled body, so it needs
  Jimmy's explicit go, knowingly.
2. **Scope the model to what it proves**: standing/hold family and
  slow charts, where its frames are strongest (probe f06 IoU
  0.846, f40 0.890), and keep the strike — the signature behaviour —
  unsolved pending a method that holds line.
3. **Re-decide the finish mechanism for action phases** (as the
  round-3 report framed it): a mask-conditioned fill that paints
  *inside* locked geometry with the approved art's own texture,
  rather than a free translation. A new method, its own go-ahead.

Standing orders honoured: no roster bake, no device work, no
second retrain. The model is **not approved for production**.

## Files

- `motion_test_v3.mp4` — the test film (152 frames).
- `frames/hold/hold_frame.png`, `frames/strike_model/` (the
  selected raw weights), `frames/strike_ema/` — rendered frames.
- `frames/determinism.json` — the gate-2 proof.
- `sidebyside/` — model vs registered gold vs original gold for
  the hold and the strike's six beats, plus the f27 blend.
- `work/metrics_v3.json`, `work/measure_v3.py`,
  `work/assemble_v3.py`, `work/sidebyside.py`.
- Model + corpus: `../finished-art-stills/finish-model-v3/`
  (`MODEL_CARD_V3.md`, `corpus_manifest.csv`,
  `registration_audit_v3.csv`, `finish_model_v3.pt`, training logs
  `trainA.log`/`trainB.log` and checkpoints on the Spark under
  `~/heron/finish-model-v3/`).
