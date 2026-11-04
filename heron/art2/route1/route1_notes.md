# Route 1 — Footage-Neural (photographic) — proof notes

Pose-conditioned UNet decoder (shared `train_decoder.py`) trained on
segmented REAL footage of Jimmy's own heron. All four output stills in
`out/` are direct decoder output from a single inference run — no
retouching, no seed cherry-picking (the model is deterministic; there
is no seed to pick).

**Amendment compliance (Jimmy, binding 2026-11-02 22:45):** the first
route-1 run was trained on 7-channel samples in which the breast
plume was blended into the torso/leg masks. That run is DISCARDED in
full (samples, checkpoint, outputs). Everything below describes the
rebuilt pipeline: **19 samples rebuilt** with the plume as its own
conditioning channel (see "Plume" section).

## Plume statement

The shaggy breast plume is keyed to its own conditioning channel
(mask channel 7, from a hand-traced `plume_poly` in every annotation)
and is never merged into the torso or leg masks. Torso outlines follow
the true anatomical body line, tucked above/behind the skirt; hips sit
at the true hip under the skirt and knees/feet on the bare leg only,
so the leg channels are the thin sticks Jimmy specified. Segmentation
alpha is unchanged — the full bird, plume included, stays in the
rgb/alpha targets; only the conditioning masks changed. In the
outputs the decoder does render the plume as a distinct region: in
rest and swallow it appears as the darker hanging mass at the breast
front, over where the legs emerge, visibly separate from the torso
fill above it. Honest limit: in this architecture the plume is NOT an
independently articulated layer — it has no dynamics of its own; its
shape and motion would be whatever the pose conditioning implies
(pose-driven via the rig's plume_sway value and the mask geometry),
not separately simulated, and it cannot lag, swing, or settle
independently of the pose that carries it.

## Corpus accounting

Color sources only. The 7 night-IR clips were EXCLUDED from this route:
they are monochrome, and mixing them into a color decoder's training
targets would teach it grey/noise color — they remain valid geometry
reference for other work, but not for a photographic color route.

| source | frames sampled | annotated | samples built |
|---|---|---|---|
| kayak-heron-day-02.mp4 (blue-hour color, 42.3 s) | 14 (t = 2,5,8,11,14,17,20,23,27,31,34,36,38,40 s) | 14 | 12 |
| pier-heron-sunrise-04.mp4 (sunrise color, 11.6 s) | 6 (t = 2, 4.4, 5, 6, 8, 10 s) | 6 | 5 |
| real-heron-a.jpg / real-heron-b.jpg (photographer stills) | 2 | 2 | 2 |
| **total** | **22** | **22** | **19** |

All 22 annotations were re-annotated under the amendment (plume_poly
added; torso/leg points corrected) and all 19 kept samples rebuilt
with 8-channel masks; the same 3 frames remain excluded for
segmentation failure (below).

Coverage of the day clip spans the full recorded behaviour: statue/
peck at the bow, the stern→bow walk, upright alert (t=27), coiled
crouch (t=31), strike-lean (t=36), deep crouch (t=38–40). No frame was
dropped for jetski/dock occlusion — the bird is on the kayak, not
behind it, in all 14 — but see segmentation failures below.

Segmentation (rembg isnet-general-use on a crop around the bird,
largest-CC kept, then alpha restricted to the dilated union of the
hand-annotated part masks — now including the plume channel — to
strip kayak-seat/paddle contamination):

- Raw rembg yield: 22/22 frames produced a mask, but 3 were unusable
  as training targets and dropped by a uniform coverage rule (raw
  alpha covering < 45% of the annotated mask union): **day_20**
  (0.21 — rembg missed the pale body against the pale jetski),
  **day_34** (0.09 — rembg latched onto a seat fragment, bird missed),
  **sun_5** (0.40 — front landing frame, post-occluded, blobby).
  Segmentation yield into samples: 19/22 = 86%.
- Matte repair (disclosed): in 7 kept samples rembg failed to matte
  the pale HEAD against bright jetski/sky (mean alpha inside the
  annotated head channel < 60/255 — day_23, day_27, day_31, day_36,
  day_38, sun_2, sun_6; day_38's neck too). The head is present in the
  source RGB; only the matte failed. For those channels only, alpha
  was repaired as max(rembg alpha, feathered hand-annotated head/neck
  mask). No RGB pixel was altered or synthesized — the repair only
  decides which existing photo pixels belong to the bird.

Stills' role (disclosed): real-heron-a/b are photographer-grade GBH
portraits from the supplied reference set; they may not be Jimmy's
bird. They are 2 of 19 samples but carry nearly ALL of the fine
feather texture in the corpus — the footage bird is only ~130–200 px
tall (day) and ~60–90 px (sunrise), so at the 512×512 sample scale the
footage contributes pose/palette, the stills contribute what little
true plumage detail exists. Both stills are profile, extended-neck,
and both carry the long breast-plume band that anchors channel 7.

Corpus gaps (stated plainly): there are NO color front-view frames and
NO color swallow/bulge frames anywhere in the corpus, and color flight
exists only as two tiny sunrise silhouettes (~60 px, texture-free).
The front and swallow target outputs are therefore pure
extrapolations from profile data; the swallow's only swallow-specific
signal is the conditioning mask's bulge deformation (bulge_pos 0.44,
bulge_amp 0.80 from the kept rig pose).

Annotations: 22 keypoint sets per KEYPOINTS.md (plume_poly included,
per the amended spec), read off labeled grid overlays
(route1/work/g_*.png); pose vectors are proof-grade estimates by eye,
as the spec allows. Two shared-code workarounds were needed, neither
editing a shared file: (1) `build_sample.py` crashes on the documented
`_px_per_unit`/`_neck_w` scalar keys — route1/work/build_one.py wraps
it with a monkeypatch that passes underscore keys through;
(2) the shared UNet crashes in its second up-block for widths
(48,96,192,384,384) (skip-concat channel count) — the Spark host copy
carries a one-line fix (Block(rev[i]+rev[i+1], rev[i+1])); identical
widths/depth/head; diff at route1/work/trainer_patch.diff.

## Training (amended run)

- Host: DGX Spark (CUDA, torch 2.15 cu132). The preferred Pro/MPS
  host deadlocked under two concurrent decoder trainings in the
  earlier session (both processes hung at 0% CPU inside an MPS
  copy/wait, stack-verified), so the brief's Spark fallback was used.
- Params: shared trainer defaults — AdamW lr 2e-4, OneCycle, batch 6,
  seed 7; 17 train / 2 val split (of 19 samples); input channels 20
  (8 mask + 12 pose), auto-sized by the trainer.
- Log (route1/train.log): val 0.1219 @200 → 0.1200 @400 → 0.1086 @600
  → 0.1132 @800 → 0.1107 @1000 → 0.1099 @1200 → 0.1111 @1400 →
  **0.1079 @1600 (best)** → 0.1105 @1800 → 0.1103 @2000.
- **Final val loss: 0.1079** (best checkpoint, step 1600). Training
  was stopped at step ~2000 of 4000 after val plateaued at
  0.108–0.111 for 1400 steps (GB10 shared with live house inference
  and, for part of the run, route 2's own Spark training); inference
  used best.pt per the shared trainer's protocol. Still an
  undertrained proof — roughly half the planned steps.

## Per-pose honest read (out/master_<pose>.png)

- **rest**: head, bill and coiled neck read clearly (the darkest,
  best-defined head of any route-1 output so far); the plume renders
  as a distinct darker mass hanging at the breast front, separate
  from the pale torso fill — the amendment's separation is visible.
  But the body is a washed, semi-transparent grey smear and the legs
  have nearly dissolved: the thin-stick leg channels carry so little
  alpha mass in training that the decoder barely commits to them.
- **front**: the weakest output. A dark frontal blob with the neck
  and head dissolving upward into white and only ghost legs below.
  No front-view training data exists; the plume channel at least
  keeps the breast mass centred, but this remains a guess wearing a
  silhouette.
- **swallow**: best body color of the set — a slate-blue torso fill
  close to true GBH coloring, upright neck, dark plume mass at the
  breast. The neck bulge is subtle (the neck reads slim, bulge
  barely swelling) and the legs are again nearly absent below the
  plume.
- **flight**: a dark smudge with a raised-wing suggestion; geometry
  is the least resolved of the four. Two 60-px silhouette samples
  taught almost nothing.

Compared with the discarded blended run: the wild per-pose hue
failures are gone (no green swallow, no purple flight — the palette
is now a stable muted brown/grey/slate across all four poses, which
the cleaner channel separation plausibly earned), and the failure
mode moved to alpha weakness: everything is faint, and the thin legs
Jimmy asked for are the first thing the decoder drops. Silhouette
fidelity at the body also slipped slightly vs the blended run — with
the torso mask tucked above the skirt, the body the decoder paints is
smaller, and at this training depth it under-fills even that.

## Limits of this route

What breaks first in motion: the legs and the alpha. The amended
masks did their structural job — plume, torso and legs now reach the
decoder as separate regions, and the palette stopped swinging between
poses — but the thin-stick legs carry so little area in every training
target that the decoder renders them at near-zero alpha even in
stills; animated, they would strobe in and out of existence step by
step, and the plume, rendered as a soft dark mass whose shape is
wholly pose-implied, would drag across them with no lag or settle of
its own. Behind that, the texture problem is unchanged and structural:
the footage bird is 130–200 px tall, so even a perfectly trained
version of this decoder upscales 3–4× beyond the information in
Jimmy's own footage, and the only high-detail source — two stills
that may not be his bird — would increasingly overwrite his bird's
actual plumage with a stranger's. The corpus gaps are not fixable by
training longer: zero color front-view frames means the front pose
can never be more than a guess no matter the step count; zero color
swallow frames means the bulge will always be bare geometry with
invented texture; color flight is two 60-px silhouettes. Cost to full
build: the training itself is cheap once a GPU is uncontended (the
full 4000 steps ≈ 2 h at the contended rate seen here, ≈ 35–50 min
alone on the Spark) — the real cost is corpus: a usable photographic
route needs closer color footage of this bird (a few minutes of
zoomed 1080p+ across alert/walk/crouch, any front three-quarter
views, one real swallow, one takeoff/landing at range), roughly
150–400 annotated samples instead of 19, legs weighted harder in the
loss (or a leg-alpha floor) so thin structures survive, and a
temporal-consistency term the shared trainer does not have. With
tonight's corpus, more steps would sharpen the smear; they would not
make it a photograph.
