# Route 2 — PLATE-NEURAL (naturalist fine-art) proof notes

## PLUME AMENDMENT (Jimmy, binding 2026-11-02 22:45) — applied

Jimmy, reviewing route 1's sheet: the shaggy breast plume was being blended
into the body/leg cutouts, fattening the body and the legs ("legs too
thick" since v1 — the plume is the cause). Binding pipeline terms, applied
here in full:

- **Plume statement: the plume is keyed to its own conditioning channel
  (mask channel 7, from a dedicated `plume_poly` in every annotation),
  rendered as a distinct region hanging over the legs. It is never merged
  into the torso or leg masks: `torso_poly` follows the true anatomical
  body line tucked above/behind the skirt (in this build: the fitted torso
  ellipse's lower edge raised ~12% on standing birds), hip points sit at
  the true hip under the skirt, and the leg channels are the bare thin
  sticks only. Honest limit: the plume is NOT an independently articulated
  layer in this architecture — it has no skeleton of its own; in motion it
  would move only as the pose vector + masks drive it (plume_sway slot
  aside), i.e. its motion would be pose-driven, not simulated.**
- What was done: plume bounding region grounded per plate (20/20), added
  as `plume_poly` to every kp file; ALL 20 samples rebuilt against the
  updated 8-channel maskrender (mask shape (8,512,512); plume channel
  populated in every sample, 3.0k–14.3k px per sample crop; QA sheet
  qa_masks8.png shows the plume region hanging over thin-stick legs with
  the torso tucked above it). Plate rgb/alpha unchanged — the full bird,
  plume included, is still the appearance target; only conditioning split.
- The first training run (7-channel blended samples, Spark) was KILLED at
  ~step 400 and DISCARDED per the amendment; the retrain below uses only
  the rebuilt 8-channel set.

## Corpus
- Plates generated: 20 (media.generate_image), ALL kept — 0 rejected.
  The generator held one hand across the whole set: graphite/watercolour-wash
  naturalist plate, slate blue-grey plumage, white face, black brow + long
  black head plume, yellow-orange dagger bill, rusty thighs, black shoulder
  patch, shaggy breast plumes. No plate drifted on bill colour or lost the
  plume, so the planned reject/regenerate loop never fired. (Honest caveat:
  "graphite" reads partly as ink/wash in the renders — but it is the SAME
  wash hand in all 20, which is what the decoder needs.)
- Coverage: rest/statue profile ×4 (rest_a–d), hunting coil ×2 (coil_a/b),
  strike-reach ×1 (strike_a), swallow stance ×2 (swallow_a/b, neck fully
  extended; swallow_b was prompted with a mid-neck fish bulge and shows one),
  front ×2 (front_a/b), three-quarter ×3 (threeq_a/b/c), walk ×2 (walk_a/b),
  flight upstroke ×2 (flight_up_a/b), flight downstroke ×2 (flight_down_a/b).
- Several plates carry pseudo-text plate inscriptions along the bottom edge
  (coil_a, front_b, swallow_a, walk_a) and walk_b has a drawn ground shadow.
  The alpha derivation (below) excluded both — verified on the QA overlay
  sheet (qa_overlays.png): no text pixels and no shadow in any alpha.

## Annotation (per KEYPOINTS.md)
- Keypoints were located with a visual-grounding pass (points for bill tip,
  skull centre, 4 neck-centreline points, both legs' hip/knee/foot, tail tip;
  bounding boxes for torso, wing, skull, tail), converted from normalised to
  source pixels (kp_raw.json → build_kp.py).
- Polygons are constructed, not hand-traced: torso/wing = 12/10-point
  ellipses fitted to their grounded boxes; bill_poly = convex hull of the
  skull box corners + bill tip; tail_poly = tail tip + tail-box base corners.
  This is coarser than the hand-traced polygons KEYPOINTS.md describes —
  proof-grade, and the main known annotation weakness of this run.
- Spine = the 5 grounded centreline points (breast → head). Flight plates:
  far leg mirrored from the near leg with a small offset (legs trail as one
  mass). Front plates: tail is a token triangle at the torso base (no tail
  is visible from the front).
- Alpha: luminance+saturation threshold against the near-white paper,
  morphological close, connected-component cleanup (largest component +
  neighbours >1% of its area near the bird) — no rembg needed; plates are
  clean. Verified visually per plate.
- Pose vectors are eye estimates per KEYPOINTS.md (coil/yaw/flap/head-pitch
  read from each plate). The two swallow plates show the head tossed back
  (real swallowing posture), so their head_pitch slot is ≈ −0.9/−0.83 while
  the rig's target swallow keeps the head level — a train/test mismatch to
  watch in the output.
- Samples built: 20 .npz via the shared build_sample.py. NOTE: the shipped
  build_sample.py crashes on the scalar keys (_px_per_unit/_neck_w/_bulge_*)
  that its own scalars block reads — maskrender.xform_points tries to
  transform them as points. Samples were built through run_build_sample.py,
  a driver that monkeypatches xform_points in memory to pass scalar keys
  through; the shared files on disk were not modified, and the sample
  format is byte-for-byte the shared builder's.

## Training
- Host: MacBook Pro (PyTorch-MPS) was tried first per plan; the process
  repeatedly stalled at 0% CPU before step 200 (MPS/fork dataloader hang)
  and was killed — birdnet-go on the Pro was never touched. Training moved
  to the fallback host, the DGX Spark (~/heron/venv, torch 2.15.0+cu132,
  CUDA + bf16 autocast), where it ran cleanly.
- SHARED-CODE BUG (affects both neural routes): train_decoder.py's UNet
  crashes as shipped — `Block(rev[i] * 2, rev[i+1])` assumes symmetric
  widths, but widths (48,96,192,384,384) make the level-2 skip concat 576
  channels, not 768. One-line fix applied to the training copies only:
  `Block(rev[i] + rev[i+1], rev[i+1])`. Same widths, depth, and block
  design — the architecture is unchanged; the shipped line simply could
  not execute. Route 1 will hit the identical crash and need the identical
  fix for the comparison to stay apples-to-apples.
- Run 1 (7-channel blended samples): killed at ~step 400 under the plume
  amendment and discarded — no outputs from it are used anywhere.
- Run 2 (the real one): rebuilt 8-channel samples, updated train_decoder
  (input channels auto-sized: 8 mask + 12 pose = 20). Params: steps 4000,
  batch 6, lr 2e-4, seed 7 (trainer defaults). 18 train / 2 val samples
  (the trainer's 12% split). ~2.7 s/step on the Spark (shared with house
  inference). The one-line skip-concat fix described above was applied to
  this run's copy too (the updated shipped file still carries the bug at
  its line 53).
- TRAINING RESULTS: DONE, 4000 steps. **Best val 0.0907** (best.pt, from an
  early-middle eval point). Curve: val 0.1010 @200 → 0.0957 @1000 → 0.0966
  @2000 → 0.0985 @2400 → 0.1006 @4000, while train fell 0.083 → 0.017.
  Textbook overfitting on 18 training samples: the val floor is reached by
  ~step 1000–1600 and the remaining 2400 steps mostly memorise. (Val is
  only 2 samples, so read 0.0907 as ±noisy.) Full log: train_v2.log.
  Checkpoint: Spark ~/art2route2_v2/ckpt/best.pt.

## Inference
- train_decoder.py infer with ckpt/best.pt on the Spark, fixed trainer
  copy, art2 = the updated shared set (8-channel targets incl. plume).
  Outputs in out/: master_rest.png, master_front.png, master_swallow.png,
  master_flight.png (+ raw_<pose>.png 512 crops). No retouching, no seed
  selection — the decoder is deterministic; what is in out/ is the single
  run's output.

## Per-pose read of the four target renders
Honest summary first: the decoder learned the plate PALETTE (soft
blue-grey watercolour wash) and rough mask-following silhouettes, but the
fine-art texture does NOT survive — no graphite hatching, no feather
detail, and none of the field markings (black brow/plume, shoulder patch,
yellow bill) read at master size. A regular checkerboard (transposed-conv
artefact) is laid over everything. This is a silhouette proof, not a
texture proof.

- rest (best of the four): recognisable heron — S-neck, body, tail, and
  THIN legs (the plume fix shows: legs are sticks, and one fades out
  mid-shin and resumes — alpha dropout). Head is mush: the bill renders as
  a detached dark dash floating right of the skull, not joined to it. The
  plume region reads as a slightly darker shag at the breast, not as
  distinct hanging feathers.
- front: frontal mass with two thin legs and a long neck, but the head
  resolves as TWO dark blobs — the decoder learned front_a's odd crest
  tufts as twin horns; there is no face and no bill. A greenish glitch
  patch sits on the chest. The darker skirt over the leg tops is the one
  place the plume channel visibly separates.
- swallow (the money pose — it fails): body and long thin legs are fine,
  but the fully-extended neck renders as a thin vertical smear with NO
  head and NO bill (a dot at the top), and the fish bulge does not read at
  all — no widening anywhere along the neck. Two compounding causes: both
  swallow training plates toss the head back (pitch ≈ −0.9) while the rig
  target holds it level, and with only 2 swallow samples the neck channel
  never got enough signal to hold a head at the end of a straight neck.
- flight (weakest): a dark ink-blot. The raised-wing mass, a bill spike to
  the right, and a rear paddle where the trailing legs merge are all
  roughly where the mask puts them, but there is no wing structure, and a
  stray detached blob floats below the body (alpha hallucination).

## Limits
What breaks first in motion is the head/neck system, and swallow already
proves it in a still: any pose far from the corpus's centre of mass
(straight neck, level head) loses the head entirely, so a strike or a
swallow in animation would smear. Second: identity drift across poses is
real and visible — rest, front and flight could be three different birds
(front even invents twin crest-horns from one plate's quirk), because the
20 plates are 20 invented birds and nothing in the conditioning ties them
together except palette. Third: fine detail is below this decoder's floor
at proof scale — 18 training samples against a ~29M-param UNet gives
val-plateau by ~step 1200 and memorisation after; graphite hatching,
feather barbs and the black/yellow markings are exactly the high-frequency
content that dies first, and the checkerboard artefact would crawl in
motion. Fourth: the plume, though correctly separated into its own
channel (legs are thin in every render — Jimmy's defect is fixed
structurally), renders as a soft darkening rather than hanging strands,
and it is not an articulated layer: it would move only as the pose drives
it. Corpus gaps to close for a full build: swallow needs plates with the
head LEVEL on a straight neck (and a mid-swallow series showing the bulge
travelling), flight needs more than 4 plates and cleaner wing geometry,
front needs plates without crest anomalies. Cost to full build, per
behaviour: a behaviour is only as good as its plate family — budget
~8–15 consistent plates per behaviour (strike sequence, swallow sequence,
walk cycle, flight cycle, idle variants), i.e. roughly 60–100 plates for
the heron's core repertoire, each needing the same keypoint+plume
annotation (~10 min/plate with the grounding pipeline), plus a training
set an order of magnitude larger before texture survives. As a route,
plate-neural buys the finest source art of the three routes and the
weakest pose generalisation; its realistic role may be as the texture
donor on top of a pose-faithful route rather than the driver.
