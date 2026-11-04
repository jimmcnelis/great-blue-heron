# Heron art restart — Phase 1: three route option proofs

**Date:** 2026-11-02 (overnight). **Status: STOP — awaiting Jimmy's pick. Nothing
has been built beyond proof scale; no episode re-render; no canon.**

Jimmy's verdict on v1.3 r4 ("the art itself is still not good. it looks
unreal... start over with the art, keep the animation work") closed the
vector-primitive drawing lineage. This phase proofs three replacement
rendering routes. Every still below is produced by the REAL machinery of its
route, driven by the SAME kept animation pose data — the four target poses
(rest profile, front, the UPRIGHT swallow at cycles13_r4 episode frame 415,
flight) come from the existing rig/cycles unchanged, so the comparison is
rendering, not posing. No output was retouched.

**Sheets (full 1024×600 masters + 100% crop sheets):**
- `model_sheet_art2_route1.png` / `crops_art2_route1.png`
- `model_sheet_art2_route2.png` / `crops_art2_route2.png`
- `model_sheet_art2_route3.png` / `crops_art2_route3.png`

Per-route working notes: `art2/route1/route1_notes.md`,
`art2/route2/route2_notes.md`, `art2/route3/route3_notes.md`.

## The plume ruling, and how each route honored it

Mid-phase, Jimmy ruled (2026-11-02 22:45) that the shaggy breast plume must
be segmented as its OWN region — never blended into body or leg masks; body
outline and leg thickness come from the true silhouette under the plumage
(legs are thin sticks under the skirt; the plume is the historical cause of
the "legs too thick" defect). The shared conditioning stack was rebuilt to
8 part channels (channel 7 = plume) and both neural routes discarded their
first runs and rebuilt every sample under the ruling. Per route:

- **Route 1:** plume is keyed to its own conditioning channel; the decoder
  renders it as a distinct darker region hanging at the breast, separate
  from the torso fill. It is NOT an independently articulated layer — its
  motion would be pose-driven only, with no lag/settle of its own.
- **Route 2:** plume in its own channel in all 20 rebuilt samples; legs are
  thin in every render (the defect is fixed structurally). The plume
  renders as a soft darkening rather than hanging strands, and likewise is
  not an articulated layer.
- **Route 3:** **cannot separate the plume as shipped in this proof.** The
  torso part is traced from donor-B's visible silhouette, so the skirt mass
  rides inside the torso part at the breast front; there is no plume
  cutout layer. (Its legs, cut as keypoint tubes, ARE the true thin
  sticks.) A full build on this route would need a dedicated plume part,
  cut and warped as its own layer over the legs. Stated plainly per the
  ruling — not silently shipped.

## Route 1 — FOOTAGE-NEURAL (photographic)

Pose-conditioned UNet decoder (~25M params; conditioning = 8 part-mask
channels + the 12-dim pose vector) trained on segmented real footage.

- **Corpus:** 19 samples — 12 frames from the one color day clip
  (kayak-heron-day-02), 5 sunrise landing frames, and the 2 high-detail
  reference stills (disclosed: photographer-grade, likely not Jimmy's
  bird — they carry most of the fine texture). IR clips excluded (they
  would poison color). 3 sampled frames failed segmentation and were
  dropped. First (blended-mask) run discarded under the plume ruling; all
  22 annotations re-done; retrained from scratch. Final val loss 0.1079
  (best step 1600; training stopped ~step 2000/4000 under GB10 contention
  with the house models — disclosed in the notes).
- **Coordinator's verified read:** ghostly, washed, semi-transparent
  smudges. Poses are recognizable — the swallow's torso is a genuinely
  GBH-like slate, the plume reads as its own region — but there is no
  feather texture at any zoom, and the thin-stick legs render at near-zero
  alpha and nearly vanish. It does not meet the stills bar; the proof's
  value is showing the corpus (a 130–200 px-tall bird) is the binding
  constraint, not the architecture.
- **Limits (verbatim from route1_notes.md):** What breaks first in motion:
  the legs and the alpha. The amended masks did their structural job —
  plume, torso and legs now reach the decoder as separate regions, and the
  palette stopped swinging between poses — but the thin-stick legs carry
  so little area in every training target that the decoder renders them at
  near-zero alpha even in stills; animated, they would strobe in and out
  of existence step by step, and the plume, rendered as a soft dark mass
  whose shape is wholly pose-implied, would drag across them with no lag
  or settle of its own. Behind that, the texture problem is unchanged and
  structural: the footage bird is 130–200 px tall, so even a perfectly
  trained version of this decoder upscales 3–4× beyond the information in
  Jimmy's own footage, and the only high-detail source — two stills that
  may not be his bird — would increasingly overwrite his bird's actual
  plumage with a stranger's. The corpus gaps are not fixable by training
  longer: zero color front-view frames means the front pose can never be
  more than a guess no matter the step count; zero color swallow frames
  means the bulge will always be bare geometry with invented texture;
  color flight is two 60-px silhouettes. Cost to full build: the training
  itself is cheap once a GPU is uncontended (the full 4000 steps ≈ 2 h at
  the contended rate seen here, ≈ 35–50 min alone on the Spark) — the
  real cost is corpus: a usable photographic route needs closer color
  footage of this bird (a few minutes of zoomed 1080p+ across alert/walk/
  crouch, any front three-quarter views, one real swallow, one
  takeoff/landing at range), roughly 150–400 annotated samples instead of
  19, legs weighted harder in the loss (or a leg-alpha floor) so thin
  structures survive, and a temporal-consistency term the shared trainer
  does not have. With tonight's corpus, more steps would sharpen the
  smear; they would not make it a photograph.

## Route 2 — PLATE-NEURAL (naturalist fine-art)

Identical decoder architecture and conditioning; corpus is generated
graphite/naturalist plates of a great blue heron matched to the footage
bird's markings.

- **Corpus:** 20 plates generated, 20 kept, 0 rejected (one consistent
  hand, markings held: slate blue-grey, white face, black brow/plume,
  yellow-orange bill, rusty thighs). All 20 samples rebuilt under the
  plume ruling. Training: 4,000 steps, batch 6, on the Spark (the MacBook
  Pro MPS attempt stalled at 0% CPU and was abandoned; BirdNET untouched).
  Best val 0.0907 (val = 2 samples — read as noisy; val plateaued ~step
  1200, train fell to 0.017: memorisation after the plateau).
- **Coordinator's verified read:** silhouettes follow the poses and the
  legs are properly thin, but the fine-art texture does NOT survive the
  decoder — output is soft grey wash with a visible checkerboard artifact
  throughout. The swallow fails outright (head essentially vanishes on the
  straight neck; bulge doesn't read), and the front invents twin
  crest-horns from one plate's quirk. Identity drifts between poses.
- **Limits (verbatim from route2_notes.md):** What breaks first in motion
  is the head/neck system, and swallow already proves it in a still: any
  pose far from the corpus's centre of mass (straight neck, level head)
  loses the head entirely, so a strike or a swallow in animation would
  smear. Second: identity drift across poses is real and visible — rest,
  front and flight could be three different birds (front even invents twin
  crest-horns from one plate's quirk), because the 20 plates are 20
  invented birds and nothing in the conditioning ties them together except
  palette. Third: fine detail is below this decoder's floor at proof
  scale — 18 training samples against a ~29M-param UNet gives
  val-plateau by ~step 1200 and memorisation after; graphite hatching,
  feather barbs and the black/yellow markings are exactly the
  high-frequency content that dies first, and the checkerboard artefact
  would crawl in motion. Fourth: the plume, though correctly separated
  into its own channel (legs are thin in every render — Jimmy's defect is
  fixed structurally), renders as a soft darkening rather than hanging
  strands, and it is not an articulated layer: it would move only as the
  pose drives it. Corpus gaps to close for a full build: swallow needs
  plates with the head LEVEL on a straight neck (and a mid-swallow series
  showing the bulge travelling), flight needs more than 4 plates and
  cleaner wing geometry, front needs plates without crest anomalies. Cost
  to full build, per behaviour: a behaviour is only as good as its plate
  family — budget ~8–15 consistent plates per behaviour (strike sequence,
  swallow sequence, walk cycle, flight cycle, idle variants), i.e.
  roughly 60–100 plates for the heron's core repertoire, each needing the
  same keypoint+plume annotation (~10 min/plate with the grounding
  pipeline), plus a training set an order of magnitude larger before
  texture survives. As a route, plate-neural buys the finest source art
  of the three routes and the weakest pose generalisation; its realistic
  role may be as the texture donor on top of a pose-faithful route rather
  than the driver.

## Route 3 — PART-COMPOSITE (no neural net)

Part textures cut from segmented real frames, TPS-warped by the pose rig's
keypoints, composited in rig draw order; the swallow neck widened by the
kept r4 fish-profile bulge rule. Seams deliberately left visible.

- **Donors:** one donor does almost everything — `real-heron-b.jpg`
  (643×900 standing profile; disclosed: photographer-grade, may not be
  Jimmy's bird) supplies torso, folded wing, tail, head/bill, neck and
  both legs for rest/swallow/flight (all downscaled 0.5–0.9×). Flight
  wings: the IR frontal braking fan from kayak-heron-night-05 @ t=12.7 s,
  slate-tinted by one global harmonization (sunrise color flight frames
  rejected: ~60 px bird, ~6× upscale). Front: entirely patio-heron-night-03
  @ t=16 s — the only real frontal source, IR, ~100 px-wide bird, legs
  upscaled ~3×.
- **Coordinator's verified read:** rest and swallow are genuinely
  photographic — real feather texture, correct markings, thin legs, the
  breast plume mass reading at the front. Faults are visible and were
  disclosed by the builder: rest's neck sits straighter than the rig's
  coil and the folded wing double-registers; the swallow's neck junction
  tears (white wedge at the breast in the 100% crop) and the bulge is
  indistinguishable from warp compression; flight's wing is a blurred
  slab with a notch and a hard far-wing edge; front is a pale blown blob
  — indefensible, shown anyway, and a corpus failure (100 px IR), not a
  code failure.
- **Limits (verbatim from route3_notes.md):** What breaks first in motion:
  this route re-warps every part from scratch on every frame, so nothing
  is temporally stable — the alpha-feathered seams will swim frame to
  frame as each TPS field is re-solved from slightly different keypoints,
  and the neck–torso tear already visible in the still swallow pose will
  open and close like a hinge whenever the coil changes, because the neck
  and torso are independent warps that only agree at the shared
  spine-base point, not along a shared edge. Texture stretching is the
  second failure: a part photographed in one configuration (the donor-B
  neck nearly straight) is rubber-sheeted into configurations it never
  had (rest's deep coil, flight's folded neck), so feather detail smears
  along the bend and compresses across it, worst exactly where the eye
  looks — the neck. Third, the corpus is the ceiling: there is exactly
  one usable high-resolution profile donor, one ~100 px-wide blown-out IR
  frontal, and one motion-blurred IR wing fan, so any pose the donors
  don't already resemble (front, extreme coil, spread wing in profile) is
  manufactured by the warp, not photographed. Cost to a full build: a
  donor library per part per orientation — at minimum several clean
  frames each of profile / three-quarter / frontal bodies, necks in
  coil / S / extended states, folded and spread wings in color, and legs
  in stance and trail — plausibly 30–60 curated, keypointed donor frames
  before motion even starts, plus per-frame re-warp cost and a
  seam-management pass this proof deliberately did not build.
  **Coordinator's plume addendum (Jimmy's ruling, 22:45):** as noted
  above, this proof has no separate plume layer — the plume rides inside
  the torso part. Route 3's full build must add the plume as its own
  cutout layer, or it fails the ruling by construction.

## Machine split (as run)

Per Jimmy's resource note, the MacBook Pro was used where it worked:
Route 2's training was attempted there first (PyTorch-MPS) and stalled at
0% CPU; it was moved to the Spark fallback and completed there. Route 1
trained on the Spark (CUDA). Corpus prep (extraction, segmentation,
annotation, compositing) ran on this VM. BirdNET-Go and Grace's harness on
the Pro were not disturbed. Disclosure: Spark training contended with the
house 32B and the voice A2 job — Route 1's run stopped early at a val
plateau because of it (noted in its log); Route 2's completed all 4,000
steps.

## Tooling disclosure

The first-cut shared trainer shipped with a skip-connection channel
bookkeeping bug and could not execute as written; both neural routes
trained with the identical correction in their training copies (same
widths, depth, block design and conditioning — the comparison is
architecture-fair). Details in the route notes.

## Coordinator's bottom line (facts, not a pick)

- Only Route 3's profile poses (rest, swallow) carry real feather texture
  at 100% crop tonight. Neither neural route meets the "texture, not
  shapes" bar at proof scale — both are corpus-starved (19–20 samples),
  and both say so themselves.
- Route 3's ceiling is its donor library (one great profile donor; front
  and flight are corpus-poor); Route 1's ceiling is footage resolution
  and coverage of Jimmy's actual bird; Route 2's ceiling is pose
  generalisation and identity drift, though its notes float a hybrid:
  plate art as texture donor on top of a pose-faithful route.
- The plume ruling is honored structurally by Routes 1–2 (own channel,
  thin legs in every render) and NOT yet by Route 3 (needs a plume cutout
  layer in a full build).
- All three routes keep the animation work untouched: the same cycles and
  pose parameters drove every still. The winner gets the full build;
  nothing here is canon.

**STOP for Jimmy's verdict.**

---

## Director's notes

- **2026-11-03 07:13 — Jimmy:** "route 2 gets the legs right more than the other 2 routes." Verified against the crops: Route 3's photographic legs read as thick pillars; Route 1's nearly vanish; Route 2's are thin, separated sticks in correct proportion — the standing leg-treatment standard for whichever route or hybrid is built.
- **2026-11-03 07:16 — Jimmy (route pick): "Route 2 wins — fix its texture and the swallow head."** Route 2 (plate-neural, naturalist fine-art) is the art route going forward; Routes 1 and 3 are closed as renderers. Fix build dispatched on the three named defects: decoder texture (soft wash + checkerboard), the swallow pose losing its head, identity drift — with Route 2's leg treatment as a protected, measured invariant.
