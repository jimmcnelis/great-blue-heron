# FILL TEST v2.5 — Path-3 fill on the settled rig v2.5

**Date:** 2026-11-04 · **Test:** one full strike cycle on rig v2.5
(build `rig-v25-mechanism-iter2`), 143 frames, 1024×600, 24 fps:
alert hold 2 s → coil-in → coil hold → dip (2 fr) → release (5 fr,
0.208 s, dip-then-quarter-bins [3/12/60/25]) → peak hold → withdrawal
→ settle hold. **Fill:** spike 1's recipe corrected per the brief —
body/legs = the approved strike still at identity (the v2.5 torso is
traced from it and rigid in all poses); neck = donor gold warped
tube-to-tube (arc × cross fraction, donor rig spine → v2.5 chain);
head = donor gold warped by the head-frame similarity into the head
assembly (skull ellipse + occipital spike + crest fan), head+bill
ONE assembly, no separate head registration; bill drawn from the
mechanism triangle with spike 1's extracted colour profile; eye
drawn at the mechanism eye anchor on every frame and pixel-verified;
per-region structural-ink remap; global trim to the band.

## Verdict

| Gate | Criteria | Result |
|---|---|---|
| 1 · Hold fidelity | black ∈ [0.252, 0.272]; IoU ≥ 0.80 vs approved rest still; MAD ≤ 32.1 | **FAIL** — black **0.2650 ✓**; IoU **0.4355 ✗** (registration ceiling itself 0.5371); MAD **81.34 ✗** |
| 2 · Strike truth | peak chord76 ∈ [0.49, 0.60] measured off the filled frames; bill present & intact at peak and through withdrawal | **FAIL** — bill **present & intact ✓** (pixel-verified, peak and withdrawal); chord76 **not measurable** off the filled frames: the filled neck does not reach the head as continuous content |
| 3 · Sequence consistency | black fraction in ~[0.21, 0.27] on ALL frames | **PASS** — 0.2604–0.2651 across all 143 frames |
| 4 · Temporal | second render byte-identical | **PASS** — full re-render, per-frame md5 identical |

**Two gates pass, two fail. The fill is not approved for the
roster.** What the passes are worth: the ink *level* is now a
carried property of the sequence (no v3-style washout anywhere),
determinism is absolute, the drawn bill survives the whole cycle,
and the eye — the spikes' silent failure — is drawn and
pixel-verified on every sampled frame. What fails is placement:
donor texture anchored on the donors' *rig* geometry lands tens of
pixels off the donors' *drawn* features at exactly the poses that
matter. Spike 3 measured that disagreement (drawn head 67–101 px
beyond the rig head at f0027); this build re-learned it from the
fill side.

## Gate 1 — hold fidelity: FAIL

Measured on frozen frame f0010 with the v3/spike-1 instrument:

| measure | this build | gate / reference |
|---|---|---|
| black fraction | **0.2650** | [0.252, 0.272] ✓ (approved rest original 0.2593) |
| slate fraction | 0.4729 | approved 0.4646 — close |
| rust fraction | 0.0063 | approved 0.0356 — legs (see below) |
| yellow fraction | 0.0053 | approved 0.0167 |
| IoU vs approved rest, re-registered onto the v2.5 alert silhouette | **0.4355** | ≥ 0.80 ✗ |
| — the registration's own ceiling (fit IoU, still → alert silhouette) | 0.5371 | — |
| IoU vs the registered rest gold on the v2.4 basis (spike 1's basis) | 0.1204 | spike 1 scored 0.8586 on its own geometry |
| MAD vs re-registered rest still, inside bird union | **81.34** | ≤ 32.1 ✗ |

Two separable components, stated plainly:

1. **A gate/geometry mismatch.** The approved rest drawing fitted
   onto the v2.5 alert silhouette reaches only IoU 0.5371 — the
   v2.5 alert stance (deep-S neck hung in front of the strike
   still's torso) is not the rest drawing's stance, so *no* fill
   could pass the 0.80 IoU bar on this basis. Spike 1's 0.8586 was
   measured on the geometry the still had been registered onto.
2. **Real fill damage inside the union** (what pushes 0.5371 down
   to 0.4355 and MAD to 81): the head paste region is mostly donor
   paper (head coverage 0.31 at alert), printing a pale rectangular
   patch behind the head with the crest strands cut at its straight
   edges; the legs sample the still ~a leg-width beside its drawn
   legs and render pale (rust 0.006 vs 0.036 is the numeric
   fingerprint); a paper-tone lobe of the torso trace hangs under
   the rear body where the trace encloses blank plate.

Visual read of the hold (frames viewed): the torso is the approved
bird — hard engraved wing, black saddle, strand plume, rust at the
thighs — because it *is* the still. The neck hangs in its alert U
filled half with white (the donor idle neck's pale side smeared
across the tube) and half with dark slate; the head rides at the
top inside its pale patch, crest streaming, the drawn bill a clean
golden dagger, the amber eye sitting on the face where the
mechanism put it. It reads as a collage of the right bird, not as
the drawing alive.

## Gate 2 — strike truth: FAIL (bill ✓, chord76 unmeasurable)

Pixel landmarks on the frozen peak frames (f0094/f0095 identical):

- **Bill: present and intact.** One dominant yellow component,
  409 px; extreme tip pixel at (872, 591); tip distance from the
  pixel-derived skull 126.3 px vs the mechanism's 133.3 px (the
  extreme *yellow-class* pixel sits ~7 px inside the drawn
  triangle's outline-coloured tip). Through withdrawal the bill
  component persists as the dominant yellow mass on every sampled
  frame (409 → 418 → 414 → 450 → 444 px, f0095–f0118), with the
  eye's 62 px amber ring as the constant second component. The
  failure Jimmy caught in v3 — the beak dissolving — does not
  recur.
- **Eye: found where the mechanism put it.** Amber cluster 62 px,
  centroid 0.4 px from the predicted anchor; skull back-derived
  from it.
- **chord76: NOT MEASURABLE off the filled frames.** The centreline
  walk through the filled neck corridor breaks at its first step:
  there is no continuous filled content from the skull along the
  neck. Along the mechanism centreline at peak the filled corridor
  (content within the tube corridor, waterline excluded) spans
  only x 587–692 of the tube's x 587–800 run — the distal third of
  the neck is paper and a dark cord. The design chord76 is 0.516
  (in band) and the spear's *endpoint* is pixel-true (pixel tip
  reach ÷ torso = 0.255 vs the assembly's 0.27 bill reach), but
  the gate as briefed measures the drawn tube, and the drawn tube
  is not there. FAIL, recorded as unmeasurable rather than
  estimated.

**What the bird looks like at peak, in plain words:** the body is
Audubon's bird, leaning into the strike. From its breast a thin
black cord — not a neck — runs diagonally down, floating in a
wide pale empty tube-shape, and ends well short of the head. The
head is a black shard inside a pale rectangular patch of donor
paper. Below the shard, exactly where the mechanism aims it, the
golden bill spears down to the water with the little amber eye
bead at its base. The line of the strike is right; the bill is
right; everything between the breast and the bill is broken.

## Gates 3 + 4 — PASS

- Black fraction per frame, all 143: **min 0.2604, max 0.2651** —
  inside [0.21, 0.27] everywhere, no washout, no saddle blowout.
  Achieved by the global trim (one pass on every frame) — at a
  regional cost detailed below.
- **Determinism:** the entire sequence re-rendered; all 143
  frames byte-identical (md5). The settle hold returns to the
  exact hold frame (f0130 ≡ f0010, same md5).

## The eye — spike 3's failure, closed and verified

The eye is drawn at the mechanism anchor on every frame (dark
pupil disc + amber ring). Pixel check on sampled frames (10, 80,
90, 95, 108, 130): centre pixel = pupil (RGB 18, 15, 12) on all;
6/6 ring samples pass the amber iris test on all. At peak the
independent landmark extractor finds the 62 px amber cluster
0.4 px from the anchor. **Disclosure:** the iris *colour* is spike
1's fallback (176, 128, 44), not an extracted median — my
head-channel-restricted extraction found no ≥15 px cluster on the
idle gold (spike 3's wide-zone test found 72 px on the same
frame; the restriction was too tight). The colour passes the
evidence-based iris test the drawings themselves pass.

## Per-region donor coverage (honest)

| region | coverage | what it means |
|---|---|---|
| neck (all sampled frames) | 0.987–1.000 | warp samples land inside the donor neck/head channels — but at peak the donor neck's *content* is blue-slate (lum > 70), so coverage is not ink |
| head — alert / settle | 0.307 | 69% of the head region (ellipse + spike + fan) is donor paper |
| head — coil-in / coil hold | 0.167 / 0.644 | fan mostly empty while the head is low |
| head — release / peak | 0.398 | the pale patch around the shard |
| head — withdrawal | 0.755 | best case, still a quarter paper |

Peak regional black as landed: neck 0.1795 (remap target 0.0786 —
see below), head 0.2206 (target 0.0633), torso 0.2566 (the still's
own, unremapped).

## Why it failed — three defects, one root

1. **The crest fan was a design error.** A straight-edged wedge
   0.30 torso long behind the skull, pasted at full alpha: mostly
   donor paper (coverage above), its edges slicing the donor's
   crest strands mid-line. It prints as a rectangular patch on
   every frame.
2. **The leg paste missed the legs.** The v2.5 leg traces sit
   ~a leg-width off the still's drawn legs, so identity sampling
   took paper. (The geometry gate's overlay showed the same small
   offset; at texture scale it is the whole leg.)
3. **The ink architecture fought itself.** Regional targets were
   the donors' regional blacks rescaled by 0.262/donor-total.
   At peak that collapses the neck target to 0.0786 and the head
   to 0.0633 (gold f0027's ink lives in its saddle, not its neck),
   so the regional remaps *lightened* neck and head; the global
   trim then re-darkened everything uniformly to hold 0.262 —
   gate 3 passes, regional truth does not. There is also a real
   tension in the gates as briefed: the gold family's own peak
   frame carries black 0.371, above gate 3's ~0.27 ceiling
   (v3's gate-4 gold band quietly excluded that frame).

**Root cause, one sentence:** every donor-side anchor in this
build — spine, head frame, channel masks — came from the donor's
*rig pose*, and spike 3 already proved the drawings disagree
with their rigs by 4–15 px along the neck and 67–101 px at the
head at full extension; spike 1 avoided the trap because its
donors were similarity-*fitted to the target silhouette from
pixels* before pasting. Tube-to-tube warping anchored on rig
spines inherits the full registration error, and at peak it
concentrates exactly where the bird moves fastest.

## Missing pieces (not attempted — next step is Jimmy's call)

- **Donor-side drawn landmarks.** The neck warp and head
  placement must anchor on each donor's *drawn* centreline/head
  (extractable with spike 3's detectors), not its rig pose.
  Settled by: the same two-frame spike (hold + f0027-class peak)
  with drawn-anchored warps — peak corridor continuity (the
  centreline walk completes) and head coverage ≥ 0.8 would prove
  the anchor fix before any sequence is built.
- **An ink rule that does not rescale regionals toward zero.**
  Targets from a reference whose regional distribution is itself
  the goal (spike 1 used the gate frame's own gold), plus a
  ruling on the peak-frame ink level (gold's 0.371 saddle vs the
  sequence band's 0.27 ceiling) — the two cannot both hold.
- **Gate 1's basis.** IoU ≥ 0.80 against the rest still is not
  reachable on the v2.5 alert silhouette (ceiling 0.5371) — the
  gate needs re-basing to the geometry the fill actually serves,
  or the alert pose needs re-examination against the rest
  drawing. A measurement question, settled by the fit number
  already in this report.

## Files

- `fill_test_v25.mp4` — the frozen test film (143 fr, 5.96 s).
- `frames/` — all 143 frozen frames.
- `sidebyside/hold_vs_rest.png` — mine | rest re-registered |
  original approved rest still.
- `sidebyside/peak_vs_strike.png` — mine | strike re-registered |
  original approved strike still.
- `fill25.py` — the build, as run (single shot; the render was
  frozen before any measurement; the only post-freeze edits were
  to the *measurement* script's landmark instruments, disclosed
  in `measure25.py`).
- `measure25.py`, `work/metrics_fill25.json`,
  `work/render_log.json` (per-frame donors, targets, coverage,
  eye checks), `work/peak_head_neck_crop.png`,
  `work/hold_head_crop.png`.

Standing orders honoured: geometry untouched, no roster render,
no canon changes, no re-render after measurement began. **The
fill is not approved for production. The next step is Jimmy's
call.**
