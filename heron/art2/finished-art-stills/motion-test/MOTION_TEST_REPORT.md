# MOTION TEST REPORT — the Audubon finish, in motion

**Date:** 2026-11-03. **Status: TEST COMPLETE — awaiting Jimmy's motion
verdict. No roster bake was run; nothing downstream was touched.**

**The two questions this test answers (per the fidelity law):**
1. Does the finish move without crawling?
2. Is the moving bird *exactly* the bird in the approved drawings?

**Short answers:** (1) The bird does not crawl — its geometry, marks and
proportions are measurably fixed — but the engraved linework itself is
redrawn every frame, so the surface *boils* in place. (2) Standing and
holding: yes, to within a few pixels and ±0.01 of mark proportion. In
the strike's action phases: no — the release's spacing shape is wrong,
the withdrawal's rise is broken in the middle, and the approved strike
frame itself does not match the proportions of the frames around it.
**Readiness verdict: do NOT bake the roster with this pass.** Detail
and the recommended pivot below.

## Deliverables (this folder)

- `motion_test.mp4` — 1024×600, 24 fps, 131 frames, 5.46 s: idle hold
  (27 finished frames in chart order), then the full strike cycle
  twice. Sequence manifest in `work/sequence_manifest.txt`.
- `frames/idle/` — 27 finished hold frames (chart frames listed below;
  f0030 is the approved drawing itself).
- `frames/strike/` — all 52 chart frames finished (f0027 is the
  approved drawing itself).
- `raw/` — every raw 2048×1184 generation, unedited.
- `rejected/` — every rejected attempt, named with its reason.
- `work/metrics.json` — full per-frame measurements; `work/measure.py`
  and `work/montages.py` — the measurement and QA-sheet code;
  `work/qa_idle_sheet.png`, `work/qa_strike_sheet.png`,
  `work/diff_f00*.png` — visual evidence.

## What was rendered, and how

**Idle hold.** The chart's first phase (`hold_fixate`, frames 0–70) is
a true hold: the study canvases across it are *byte-identical files*
(verified by hash — the movement layer contributes zero motion). The
approved rest frame is chart f30. Protocol: each frame was finished by
asking the generator to reproduce the approved drawing exactly, as a
fresh impression of the same plate (brief: `work/brief_idle.txt`).
**Deviation, disclosed:** 17 of 43 idle generation attempts returned
service errors and were not repeated, so the finished set is the 26
that completed, plus the approved original — chart frames 8, 9, 11,
12, 13, 15, 16, 18, 19, 20, 23, 24, 25, 29, 30 (approved), 31, 34, 35,
36, 37, 38, 40, 41, 45, 46, 47, 49, sequenced in chart order (27
frames ≈ 1.1 s at 24 fps instead of the planned 48 ≈ 2.0 s). Because
the canvases are identical, the missing chart numbers carry no pose
information — every finished frame is an independent repaint of the
same drawing, which is exactly what the crawl measurement needs.

**Strike cycle.** All 52 chart frames, finished from their study
canvases. Two protocols:
- **v1 (2 frames, both rejected):** canvas + *both* approved stills as
  references. The generator copied the strike still's composition and
  ignored the canvas (f24 and f36 both came back as the contact pose).
  Kept in `rejected/` as the pose-drift evidence.
- **v2 (all 51 generated frames):** canvas + the *rest* still only
  (identity without a competing pose), an explicit geometry lock, and
  a per-frame pose caption taken from the chart's phases (brief:
  `work/brief_strike_v2.txt`). Five frames were re-rolled once with
  strengthened captions (v3): f24 and f33 and f35 improved and were
  kept; f25 and f34 kept their v2 versions. All superseded attempts
  are in `rejected/`.
- f27 in the sequence is `audubon_strike.png` itself, as required.

**The fish** does not appear: in the movement system the fish is an
object-layer event, not part of the bird render (the study canvases
contain no fish), and the brief forbade inventing one. The grab dwell
is therefore a bill closing at the water, which is what the canvases
author.

**Water disturbance:** at and after contact the brief required the
plate manner — fine engraved ripple rings at the bill tip on contact
frames (visible f24 v1, f27, f28) and engraved drip lines through the
withdrawal (visible f30–f38, including drip trails under the raised
bill at f36–f40). The water itself stays the approved wash band.

## Fidelity — is it exactly the bird? (measured, vs the approved stills)

Method: per-frame content masks (color distance from each frame's own
paper estimate), color-class fractions inside the mask, and a bill
centroid (the yellow bill is the hardest-edged mark on the bird).
Mask areas include the waterline band, so masks are used only as
*relative* measures; the bill centroid and color fractions are the
hard numbers. Full data: `work/metrics.json`.

**Idle reproductions (n = 26) vs the approved rest drawing:**
- Silhouette overlap (mask IoU): median **0.843**, range 0.820–0.860.
- Mask area ratio: 0.989–0.999 of the original. Composition centroid
  wander: **SD 0.44 px (x), 0.56 px (y)** — the drawing does not drift.
- Bill centroid: x 694–708, y 85–94 across reproductions; the approved
  original itself sits at (694, 99) — the reproductions cluster
  *tighter* than the original's own offset. Bill size: 1,635–1,800 px
  (original 1,677).
- Mark proportions (fraction of the bird): black 0.252–0.272 (approved
  0.259) · rust 0.035–0.037 (0.0356) · bill-yellow 0.016–0.018
  (0.0167). The shoulder patch stays the rest still's small patch in
  every frame; the thighs stay the rest still's short rust.
- Hatch quantity (high-frequency energy): 10.24–10.68, SD 0.11 — the
  *amount* of engraving is constant even though the strokes move.
- Paper: per-frame paper color matches the original; paper-region
  difference vs the original ≈ 2.0 / 255 — the plate ground is
  effectively identical.

**Strike frames:** the standing family (coil, loaded hold, recover —
40 of 52 frames) holds the same identity: black fraction 0.250–0.265,
rust 0.034–0.037, bill-yellow 0.015–0.019, bill carriage height
75–95 px — statistically the idle bird. By eye across the 52-frame QA
sheet: same bird, same small shoulder patch, same thighs, thin legs,
plume as its own strand region, in every frame. No frame produced a
cousin, a second animal, text, or a wing-spread recomposition after
the v1 protocol was abandoned.

**The f27 paradox, stated plainly:** the approved strike drawing is
the *least* consistent frame in its own sequence. Its measured
proportions — black fraction 0.314, rust 0.017, bill-yellow 0.005 —
sit far outside the family band above, because (as the stills report
flagged and Jimmy approved as presented) its black shoulder patch is
a saddle and its head turns toward the viewer. The generated frames
hold the *rest* drawing's proportions, per the brief. In the MP4
there is a visible pop at f27: one frame of a slightly different bird
inside an otherwise uniform sequence. This is not a generation
failure; it is two approved drawings that do not perfectly agree with
each other, meeting in motion for the first time.

## Temporal consistency — does it crawl?

- **Structure: no crawl.** Centroid wander under 0.6 px, area ratio
  within ±1%, mark fractions within ±0.01, bill within ±7 px, across
  26 independent repaints of an identical canvas.
- **Surface: continuous boil.** Consecutive-frame difference inside
  the bird: median **19.1 / 255** (range 10.9–32.4), vs 1.8 / 255 on
  the paper. The amplified difference images (`work/diff_f0029.png`
  etc.) show exactly where the change lives: every engraved hatch
  stroke and feather edge is redrawn each frame; the silhouette and
  the paper do not move. At 24 fps the bird stands perfectly still
  and *shimmers* — classic hand-drawn line boil, whether or not it
  was invited. Under the fidelity law's wording — "looks exactly like
  these drawings" — a boiling surface is not the drawing; it is a new
  impression of it, 24 times a second. (If Jimmy ever *wants* line
  boil as a living-print effect, this pass produces it for free. As an
  exactness matter, it is a fail.)

## Motion truth — does the chart's movement survive?

Bill height (centroid y, px; standing ≈ 85, contact = 491 in f27):

- **Release (f23→f27):** 92 → 305 → 429 → 476 → 491. Monotonic ✓ —
  but the increments are **213 / 124 / 47 / 15**, where the chart
  authors an *accelerating* 25% / 35% / 40% (≈ +100 / +140 / +160).
  The dive is front-loaded: most of the travel happens in the first
  frame and the spear decelerates into contact — the opposite of the
  chart's spacing, and the straight diagonal spear geometry exists
  only in f27 itself; f24–f26 read as a deepening bow. The chart's own
  spacing gate therefore **fails** on the finished sequence.
- **Grab dwell (f28–f29):** 481, 500 — at the water ✓.
- **Withdrawal (f28→f41):** 481 → 500 → 418 → 340 → 335 → 357 → 391 →
  197 → 92 → 84 → 93 → 78 → 94 → 88. The head lingers at the water
  through f34, dips *down* again at f33–f34 (5 of 13 steps move the
  wrong way), then completes the entire rise in two frames (largest
  single step 195 px, f34→f35). The chart authors a smooth
  decelerating rise; the finished sequence gives dwell-then-pop.
  **Fail.**
- **Coil / loaded hold / recover (40 frames):** bill height 75–95 px
  throughout — the held carriage is as stable in the strike's standing
  frames as in the idle hold. ✓

Root cause, evidenced by the v1 rejections and the re-roll pattern:
the generator treats any strong reference (or a weak canvas — the
study renders are faintest exactly at maximum extension, per the
roster report) as an invitation to stage one of a few canonical heron
compositions. It resolves *poses it recognizes* (standing, drinking)
and interpolates poorly between them. Prompt geometry locks and
captions improved matters; they did not fix the action phases.

## Generation accounting (for the bake estimate)

This test: **101 generation attempts** → 100 finished frame slots
(27 idle incl. the approved original, 52 strike incl. the approved
original), 9 rejected attempts kept on disk, 17 idle attempts lost to
service errors. Wall clock ≈ 40 minutes in parallel batches of 4–6
(~25–60 s per generation). First-attempt success: idle protocol 60%
(26/43, errors excluded from quality blame — they returned nothing),
strike v2 51/51 usable, 5 frames re-rolled once for pose accuracy.

A 2,004-frame roster bake at these rates means roughly **2,600–3,400
generations, ~18–30 hours of generation wall-clock**, plus a gating
pass over every frame (the stills' gates are manual today; the
bill-centroid and fraction checks above are automatable and would
have to be built), plus re-roll labor concentrated exactly where the
pass is weakest — flight, front view, max extension. And after all of
it, the product would still boil on every frame and still break the
action-phase spacing. **The bake is not blocked by cost; it is
blocked by the two failures above. Do not bake.**

## Recommendation — the pivot

**Train a pose-conditioned finish model on approved finished frames**
(the alternative the stills report named), seeded by this test:

- **Corpus already exists.** The 2 approved stills + this test's 77
  gate-passed finished frames are paired with their exact study
  canvases — a ready training set for the standing family, with this
  report's measurements as the acceptance gates.
- **Why it fixes the failures:** the model is conditioned on the
  rig's pose/mask (the Route 2 bridge already produces it), so
  geometry lock is by construction, not by prompt; the same pose
  yields the same drawing, so holds go truly still and the boil
  collapses toward model noise, which a paired-frame consistency
  loss can drive down deliberately; action phases inherit the
  chart's geometry because the conditioning *is* the chart's
  geometry.
- **What it takes:** corpus prep from this test's pairs (hours),
  training on the Spark at the Fix-1 precedent's scale (6,000 steps,
  hours), then re-running *this exact test protocol* — same windows,
  same measurements — against the model's output before any roster
  commitment. Flight/front/extension frames remain corpus-limited
  and would need approved stills of their own first (the production
  order already requires Jimmy's art verdict per family anyway).
- **Cheaper partial measures, priced for completeness:** (a) a
  hold-freeze policy — finish one frame per hold phase and repeat it
  (standard cel practice; kills the hold boil completely, does
  nothing for action phases); (b) finish keyframes only and blend
  between them (engraving lines ghost under crossfade — likely worse
  than the boil); (c) accept the boil as the plate's living-print
  character — an aesthetic decision only Jimmy can make.

## My visual verdict

The idle hold is genuinely beautiful and genuinely the approved bird:
same drawing, same marks, standing in its waterline, with a faint
engraved shimmer over the plumage. The strike plays as the same bird
bowing to the water and rising again — identity never breaks — but it
does not yet play as the chart's strike: the spear's acceleration is
missing, the rise stumbles in the middle, and the approved contact
frame pops against its neighbors. The finish pass has proven it can
hold a likeness at rest. It has not proven it can *move* that likeness
through an action. That is what the pivot is for.

## Limitations of this test

One hold window and one action chart were tested (the two the brief
named); flight, front view and the swallow were not — the stills
report already rates them weaker. Mask-based fractions include the
waterline band and are comparative, not anatomical. The idle segment
of the MP4 is 27 frames (1.1 s) rather than 48 (2.0 s) for the reason
disclosed above. Measurements were taken at the delivered 1024×600
(the finish pass generates at 2048×1184 and is downscaled, the same
1.35% aspect normalization the approved stills carry).
