# Bird-Completion Geometry Round — Report (rig v2.3)

## Verdict

**Proof (1), mask surface, idle hold vs the approved rest still:**

| rig | raw IoU | bird-only IoU |
|---|---|---|
| v2 (control) | 0.5257 | 0.5642 |
| v2.1 (control) | 0.5501 | 0.5879 |
| v2.2 (control) | 0.6141 | 0.6567 |
| **v2.3 (this round)** | **0.7121** | **0.7656** |

Geometry bought **+0.0981 raw / +0.1088 bird-only** over v2.2 — the
largest single-round gain in the rig's history (placement bought
+0.064). Totals: miss 24,592 → **18,172** (−26%), extra 20,599 →
**13,486** (−35%). The fitted placement also got cleaner: rotation
3° → **0°**, scale 1.175 → 1.20 — the bird now sits at the painting's
attitude on its own geometry instead of being rotated into it.

**0.7121 is still below the 0.85 gate, and the decomposition below
says why in exact terms** — 42.5% of all remaining miss is painted
scenery the environment law forbids the rig to draw. The
scenery-forgiven score is the bird-only number, 0.7656. Three honest
flags ride with the win (§Flags): the torso hull now overshoots the
proportion spec's measured length, the torso's internal row-band
distribution moved *away* from the approved target even as the
outline converged, and the plume's longest painted strands remain
uncovered by the solid fan.

This round was run by two crews: the first was stopped mid-flight by
a parent-side miscommunication (not a failure), the second resumed
from its saved state at full pace. Every number below was reproduced
by the resuming crew from the controls up.

## Controls and pickup verification

- Controls re-run by the resuming crew: v2 0.5257, v2.1 0.5501,
  v2.2 0.6141 raw — exact; v2.3 files at zero geometry delta
  reproduce v2.2's mask stack **pixel-identically, all 8 channels**
  (`controls_results.json`).
- The prior crew's saved incumbent (raw 0.70952 / bird 0.76261,
  stage-4 state of its resumed pass) was re-evaluated before any new
  move: reproduced exactly (`finish_log_v23.jsonl`, tag
  `pickup-check`). Nothing was credited that wasn't re-measured.
- Bake: the winning state was written into `rig13_r4_v23.py`,
  `roster_render_v23.py`, `pose_tracks_v23.json`; a fresh import of
  the baked files reproduces the search build **pixel-identically**
  at 0.7121 / 0.7656 (`bake_results_v23.json`). One bake-script fix
  was needed (a verbatim-string indent mismatch in the rig's
  art-path skull literal; no geometry involved).
- Evidence hygiene, disclosed: during pickup, a stray import briefly
  re-ran the search's first five evaluations, appending exact-value
  duplicates to `search_log_v23.jsonl`. It was killed within stage 1,
  never touched the saved state, and the five duplicate lines were
  removed; the log stands at the prior crew's 317 evaluations. The
  resumption's own 88 evaluations are in `finish_log_v23.jsonl`,
  kept separate for exactly this reason.
- **405 scored evaluations total, every one invariant-checked**;
  one candidate in the whole round was refused by the leg-IK guard
  and never entered the build.

## What the round changed (v2.2 → v2.3 geometry)

- **Torso hull:** belly/keel points dropped (+5.4 on points 7–8 —
  the deep Audubon belly the placement round couldn't reach), crown
  +1.2, tail points pulled inboard (−2.7), per-point outline work
  (tp1y +3.6, tp11y −2.4, tp9x −2.4, tp12x +2.7, tp0x −0.3,
  tp2y/tp5y +0.6, tp9y −0.6). Torso depth 0.424 → 0.409 H
  (approved ~0.36–0.39 — closer).
- **Wing:** top edge +4.0.
- **Plume (still its own channel, ch 7):** the fan was *reshaped*,
  not just moved — length ×0.80, width ×0.70, bottom +3.4,
  translate (6.0, −18.5), per-point pp4y −2.0 / pp6y +10.0. It now
  inks 15,171 px placed (v2.2: 20,424) and covers far more of the
  painted fan: less ink, better aimed.
- **Head:** skull profile bulked around the frozen anchor — nape
  +0.6, crown +0.45, cheek +0.45, hp1y +1.2. HEAD_S and BILL_LEN
  untouched; the bill tip is bit-identical.
- **Legs:** far foot −7.5 → −7.0, near hip x −0.5 (final polish).
  Pose `body_rot_b` −6.75° and hx/hy (36.17 / −26.34) unchanged.

## Stage attribution (sequential climb, both crews)

| stage | raw | bird | Δ raw | Δ bird |
|---|---|---|---|---|
| base (v2.2 geometry) | 0.6141 | 0.6567 | — | — |
| S1 torso groups | 0.6562 | 0.7037 | +0.0421 | +0.0470 |
| S2 torso points | 0.6695 | 0.7193 | +0.0133 | +0.0156 |
| S3 wing | 0.6700 | 0.7198 | +0.0005 | +0.0005 |
| S4 plume reshape | 0.6894 | 0.7414 | +0.0194 | +0.0216 |
| S5 head bulk | 0.6956 | 0.7486 | +0.0062 | +0.0072 |
| S6 legs | 0.6980 | 0.7498 | +0.0024 | +0.0012 |
| S2′ torso re-polish (resume) | 0.7062 | 0.7588 | +0.0082 | +0.0090 |
| S3′ wing (resume) | 0.7087 | 0.7617 | +0.0025 | +0.0029 |
| S4′ plume (resume) | 0.7095 | 0.7626 | +0.0008 | +0.0009 |
| S5′ head closure (finish) | 0.7095 | 0.7626 | +0.0000 | +0.0000 |
| S6′ legs (finish) | 0.7100 | 0.7632 | +0.0005 | +0.0006 |
| S7′ joint polish (finish) | **0.7121** | **0.7656** | +0.0021 | +0.0024 |

The keel drop was the single biggest lever of the round; the plume
reshape second. By the finish pass the surface was flat — head moves
bought exactly nothing (the head had converged in pass 1), and the
last +0.0026 came from joint polish dust. This geometry family is
at its local optimum under this acceptance rule.

## Frozen laws — invariants, all exact

- **Neck channel pixel-identical to v2.2.** Neck arc 32.62 units
  (0.4476 H) in both; neck widths on the channel identical
  (47 / 44 / 35 px at arc t = 0.45 / 0.60 / 0.75). The neck was
  never a search parameter.
- **Breast (442.84, 284.10) and head anchor (526.47, 137.73)
  bit-identical**; bill tip bit-identical; head→bill-tip 0.305 H
  and standing height 71.9 units unchanged; leg segments 20.4 /
  19.2 unchanged; no clipping (bbox x 66–671, y 111–587).
- Pose data and the strike untouched; proportion spec unamended;
  **the canvas decoder was not touched and no canvas was rendered**
  — its retrain remains last, per the order.

One consequence worth naming: neck-zone miss fell 916 → **59** and
head-zone miss 3,599 → **1,530** while the neck channel never
changed a pixel and the head only grew bulk. As in the placement
round, placing the body correctly stops the global fit from
spending neck/head accuracy to chase torso mass.

## Residual decomposition (placed fits, pixels)

Miss by approved-side zone (v2.2 → v2.3):

| zone | approved | miss v2.2 | miss v2.3 |
|---|---|---|---|
| scenery (y≥558) | 8,023 | 7,715 | **7,723** |
| torso/rest | 52,459 | 4,224 | 4,221 |
| legs | 5,293 | 2,224 | 2,366 |
| plume | 10,433 | 5,914 | **2,273** |
| head | 11,784 | 3,599 | 1,530 |
| neck | 8,500 | 916 | **59** |

Extra by rig channel (v2.2 → v2.3): wing 2,928 → 2,649; plume
3,089 → 2,210; neck 2,460 → 2,521; legs (both) 1,772 → 2,045; head
81 → 80; tail 70 → 162; **torso 20,518 → 27,789**. Read that last
line with its twin: extra *landing in the torso zone* fell 13,405
→ **6,630**. The two numbers measure different things — the torso
polygon's own footprint grew (see Flag 1) while the wing and plume
channels vacated ~14,600 px of placed area that used to spray
outside the bird; the union — the only thing IoU prices — improved
on both sides at once (miss −6,420, extra −7,113).

**What the remaining gap is made of, in order:**
1. **Scenery — 7,723 miss (42.5% of all miss).** Painted waterline
   and grass inside the protocol mask. Structural and, per the
   environment law, *correct*: the rig must never draw it. A
   perfect bird still misses all of it.
2. **Torso outline residue — 4,221 miss / 6,630 zone extra.** The
   hull converged hard but is not the painted outline; see Flags
   1–2 for the two ways it differs that the score doesn't show.
3. **Plume strands — 2,273 miss.** The fan now covers the painted
   fan's dense mass; the longest individual strands hang below it
   into paper the solid channel can't ink without paying extras.
4. **Legs — 2,366 miss (+142 vs v2.2, the round's only regression,
   small).** Thin painted sticks from a fringe vs solid polygons;
   the leg levers bought their gain in placement, not zone cover.
5. **Head bulk — 1,530 miss.** Engraved cap/crest/cheek mass around
   a smooth polygon; the profile took what the gate allowed.

## Flags — read before celebrating

**Flag 1 — the torso overshoots the spec's length.** Landmark
torso width is now **0.849 H**; the proportion spec measured the
approved bird at **~0.80 H**. The gate paid for coverage by growing
the hull past the measured bird, and the overlay shows it as a blue
wedge beyond the painted tail line. Torso depth, by contrast,
improved toward spec (0.409 vs ~0.36–0.39). Whether the finished
bird reads too long-bodied is an eye question — Jimmy's eye
supersedes this metric, and this is the first place to look.

**Flag 2 — row bands moved away from target.** The brief named
the middle-band share (approved 0.348, v2.2 0.418) as an aim.
Result: **0.435** — worse. Top/bottom 0.262 / 0.318 (approved
0.281 / 0.371). The torso core centroid sits at (−0.286, +0.114) H
vs approved (−0.356, +0.111): vertical exact, but 0.070 H too far
forward (v2.2: 0.026). Plainly: **the IoU-optimal hull is not the
band-optimal hull.** The acceptance rule priced outline overlap
and the internal distribution paid. If the finish makes the bird
read middle-heavy, this is why, and the remedy is a
band-constrained geometry pass — a different acceptance rule, not
more of this search.

**Flag 3 — the plume trade, restated.** Jimmy ruled the hang
matters (his eye over the metric). The reshaped fan covers the
painted fan far better than v2.2's bib (zone miss 5,914 → 2,273)
*and* its in-frame drop measure is unchanged (0.087 H) — the win
was shape and aim, not a longer skirt. The longest painted strands
remain uncovered (Flag for the finish phase): whether the bird
reads as Audubon's hanging plume still depends on the finish
painting strands from this channel.

## What the decoder retrain (next phase) can and cannot recover

**Can:** the finish model's v2 failure was trained on canvases that
never sat on the bird (canvas↔target IoU ~0.134; decoder self-IoU
0.149–0.21 on recent poses). The rig now presents a silhouette at
0.71 union IoU to the approved mask with the neck, head, and plume
in their true places — correctly-paired training data is the direct
fix for the blurred-average failure, and this round is what makes
those pairs exist.

**Cannot:** (1) scenery — the gate will keep charging it and the
finish must keep not drawing it; (2) plume *strand texture* — the
channel is a tighter fan, but strand-level fidelity is finish
capacity, not geometry; (3) the middle-heavy, forward torso core
(Flag 2) — the decoder will faithfully paint the mass distribution
the rig hands it; (4) engraved head bulk beyond the profile. Expect
the retrain to cash out as temporal stability and likeness of the
finish on correct geometry, not as movement in this gate's number
— the canvas surface has never been this round's measure.

## Files

This directory (`finished-art-stills/rig-v2/geometry-round/`):
- `GEOMETRY_ROUND_REPORT.md` — this report
- `overlay_v23_vs_approved.png` — yellow = agreement, red =
  approved only, blue = rig only
- `rig_v2_3_idle_silhouette.png` — the v2.3 idle-hold mask
- `controls_v23.py`, `controls_results.json`, `controls_run.log`
- `search_v23.py`, `search_log_v23.jsonl`, `search_run_v23.log`,
  `search_state_v23.json` — prior crew's search (317 evals)
- `finish_v23.py`, `finish_log_v23.jsonl`, `finish_run_v23.log` —
  resumption pass (88 evals)
- `winning_params_v23.json` — the winning geometry state
- `bake_v23.py`, `bake_results_v23.json` — bake + faithfulness proof
- `verify_v23.py`, `verify_results_v23.json`, `verify_run_v23.log`

Baked rig files (v2.2 files untouched):
- `src13/rig13_r4_v23.py` — TORSO / WING outlines, art-path skull,
  HIP_NEAR / HIP_FAR
- `art2/roster_render_v23.py` — SKULL_PROFILE, PLUME_OFFS_BASE,
  PLUME_DX / PLUME_DY
- `geometry-round/pose_tracks_v23.json` — hold pose (fxf −7.0)

Approved stills untouched; creature engine untouched; no finish
generations; no training.
