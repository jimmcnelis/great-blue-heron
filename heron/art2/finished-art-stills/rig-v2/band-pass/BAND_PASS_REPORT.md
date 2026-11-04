# Band-Constrained Geometry Pass — rig v2.3 → v2.4

**Verdict: CONTRACT MET — v2.4 is baked.** The band profile improved
decisively inside the floors: total band-profile error **0.1594 →
0.0272 (−83%)**, middle band **0.4349 → 0.3680** (approved 0.348),
at raw IoU **0.6907** (floor 0.69) and bird-only **0.7402** (floor
0.74). The winner is the best floor-satisfying candidate among 299
invariant-checked evaluations, and the trade curve below shows the
floors cost almost nothing at the margin — below them, only 0.004
more band error exists.

**The honest exception, stated up front:** the SECONDARY aims did
not come along. The core centroid is still too far forward (+0.077 H
vs v2.3's +0.0705 — marginally worse, not better), and the landmark
torso length did not come back: **0.85 H**, unchanged from v2.3,
against the spec's ~0.80 H. Both searches ran a dedicated secondary
polish stage under a band guard; inside the IoU floors there was no
affordable move. The band win was bought with outline growth low and
rearward (extra pixels), not with a shorter or further-back hull.
What the decoder inherits is a bird with the approved bird's *mass
distribution* carried by a hull that is still ~6% too long. Read the
three surfaces below and judge accordingly.

Same judge throughout: `geometry-round/geo_common.py` + the v2.2
body-measurement instrument, unchanged. Pose = the v2.3 idle pose.

## Controls (reproduced before any search)

| rig | raw IoU | bird-only |
|---|---|---|
| v2 | 0.5257 | 0.5642 |
| v2.1 | 0.5501 | 0.5879 |
| v2.2 | 0.6141 | 0.6567 |
| v2.3 | 0.7121 | 0.7656 |

All four reproduce (controls_results_v24.json). A zero-delta build
on the baked v2.3 files is pixel-identical to roster_render_v23's
own build, and reads band error 0.1594, bands 0.2615/0.4349/0.3180,
centroid (−0.2855, +0.1136), torso length 0.849 H — the defect as
briefed.

## The winning numbers — all three surfaces

| surface | approved | v2.3 | **v2.4** |
|---|---|---|---|
| raw IoU | — | 0.7121 | **0.6907** |
| bird-only IoU | — | 0.7656 | **0.7402** |
| band 0 (top third) | 0.281 | 0.2615 | **0.2781** |
| band 1 (middle) | 0.348 | 0.4349 | **0.3680** |
| band 2 (bottom) | 0.371 | 0.3180 | **0.3667** |
| total band error (L1) | 0 | 0.1594 | **0.0272** |
| centroid x (H rel. breast) | −0.356 | −0.2855 (+0.0705 fwd) | −0.2790 (**+0.0770 fwd**) |
| centroid y | +0.111 | +0.1136 (+0.0026) | +0.1189 (+0.0079) |
| torso length (landmark) | ~0.80 H | 0.849 H | **0.849 H** |
| torso depth | — | 0.409 H | 0.409 H |

Per-band errors: top 0.019 → **0.003**, middle 0.087 → **0.020**,
bottom 0.053 → **0.004**. The middle-heavy build is gone as a
distribution: the core now reads top-light, belly-heavy, like the
approved bird. What did NOT change is the extent that carries it.

**The delta (8 knobs, torso channel only):** bottom-line group
+1.2 (points 8–11 down), keel group +0.6, and per-point moves
tp2y +0.6, tp3y −1.8, tp4y +0.6, tp6x +2.7, tp7y −3.3, tp9y +0.6.
Head, neck, legs, hips, plume, pose: untouched.

## What the bands cost in IoU — the measured trade curve

299 invariant-ok evaluations (search 115 + probes 64 + climb 120).
Best band error any candidate reached, by floor pair:

| floors (raw / bird-only) | best band err | middle band | reached at |
|---|---|---|---|
| v2.3's own level (0.7121 / 0.7656) | 0.1513 | 0.431 | 0.7128 / 0.7661 |
| 0.705 / 0.755 | 0.1281 | 0.419 | 0.7081 / 0.7605 |
| 0.700 / 0.750 | 0.0833 | 0.396 | 0.7008 / 0.7515 |
| **contract floors 0.69 / 0.74 (exact)** | **0.0272** | **0.368** | **0.6907 / 0.7402 = v2.4** |
| no floors at all | 0.0229 | 0.366 | 0.6897 / 0.7391 |

Readings:

- At v2.3's IoU level the bands are essentially immovable (best
  0.1513 vs 0.1594): the IoU-optimal hull and the band profile
  genuinely fight — that is the defect, measured.
- The price is convex: the first half of the gain (→ 0.083) costs
  ~0.011 raw; the second half costs another ~0.010; the last scrap
  below the floors (→ 0.023) buys almost nothing. The contract
  floors sit right at the knee.
- Total price paid: raw −0.0214, bird-only −0.0254 — essentially the
  full budget the floors allow, for 5.9× less band error than the
  brief's starting point.

## How the search ran (and a lesson in lever pricing)

1. **Main descent** (greedy, band rule): keel-first, as ordered by
   the previous round's habits. It spent the whole IoU budget on the
   keel and stalled at band error 0.0948, floors pinned — every
   later group knob was unaffordable by the time it was tried.
2. **Exchange-rate probes** (single-knob, from the v2.3 base)
   repriced every lever. The keel is a mid-pack lever (efficiency
   0.052). The real levers: **t_bl — one +1.2 step = band error
   −0.0600** at −0.011 raw — and a set of near-free per-point moves
   (tp3y, tp9y, tp11y, tp5x, tp6x: −0.005…−0.011 each at ≤0.0014 raw).
3. **Climb** (cheapest-first, per-move bleed cap): t_bl first, then
   the probe-ranked points. 0.0994 after one move; 0.0439 after the
   cheap points; 0.0280 at convergence; the pooled-log best
   (tp7y −3.3 variant) rechecked and adopted: **0.0272**.

Neither search's secondary polish (centroid/length under a band
guard) found an acceptable move at the floor boundary.

## Residual decomposition (mask surface)

| zone | miss v2.3 → v2.4 | extra v2.3 → v2.4 |
|---|---|---|
| scenery (structural — the law forbids drawing it) | 7,723 → 7,723 | 43 → 43 |
| torso/rest | 4,221 → 4,266 | 6,630 → **9,048** |
| plume | 2,273 → **1,410** | — (channel pixel-identical) |
| head | 1,530 → 1,530 | 2,320 → 2,320 |
| legs | 2,366 → 2,342 | 802 → 988 |
| neck | 59 → 65 | 2,167 → 2,167 |
| **totals** | **18,172 → 17,336** | **13,486 → 18,114** |

The IoU cost is an *extra-side* cost, concentrated in the torso
channel's own footprint (extra 27,789 → 33,346): the redistributed
hull inks more outside the painted bird, low and rearward, where
the painted outline is fringe. Coverage actually *improved* (miss
−836), including an un-asked bonus: plume-zone miss fell 863 px
because the deepened belly now underlies more of the painted plume
region (the plume channel itself never moved). The overlay
(overlay_v24_vs_approved.png) shows it: overwhelmingly yellow, a
deeper blue belly/back mass, the red plume strands still hanging
below the belly line — the long strands remain a finish-phase
question, exactly as flagged in v2.2 and v2.3.

## Frozen laws — verified on the baked files

- neck channel **pixel-identical** to v2.2 and v2.3; arc 32.62
  units; widths 47/44/35 px — NECK LAW holds
- head anchor (526.47, 137.73) and breast (442.84, 284.10)
  **bit-identical**; bill tip identical (bill length kept)
- head and plume channels pixel-identical to v2.3; legs and pose
  untouched; strike untouched; decoder untouched
- bake faithfulness: a fresh import of the baked v2.4 modules
  reproduces the search build's mask stack pixel-identically and
  the winning scores exactly (bake_results_v24.json)

## What the decoder inherits — honest read

The mass is right now; the extent is not. The eroded-core
distribution the decoder will paint over matches the approved
bird's build to within 0.02 per band — top light, middle moderate,
belly heavy — so the *weight* of the painted bird should finally
sit where Audubon's sits. But the hull handing over that mass is
still 0.85 H long (spec ~0.80) with its core centroid 0.077 H
forward, and it carries +4.6k extra pixels of low/rear overhang the
finish will have to feather into fringe or trim. If the retrained
decoder paints the hull it's given, expect a bird with the right
belly and balance, wearing a slightly long body — the same tail
overshoot Jimmy's eye flagged in v2.3's overlay, now with the
distribution fixed underneath it. Neither band passes nor IoU
searches found a way to shorten this hull without paying outline
fit neither budget allows; if the length still reads wrong in
motion test v3, it is a proportion-spec question (revisit the
torso polygon's tail anchor), not another search of this kind.

## Files

Baked (canonical positions; record copies in this folder):
`src13/rig13_r4_v24.py`, `art2/roster_render_v24.py`,
`band-pass/pose_tracks_v24.json` (identical to v2.3 — pose frozen).

In this folder: this report, overlay_v24_vs_approved.png,
rig_v2_4_idle_silhouette.png, trade_curve_v24.png/.json,
controls_results_v24.json, winning_params_v24.json (+_prev and
_search variants), search/probe/climb logs (.jsonl + run logs),
probe_results_v24.json, climb_results_v24.json,
bake_results_v24.json, verify_results_v24.json, and the harness
(band_core.py, controls/search/probe/climb/adopt/bake/verify/
trade_curve scripts). v2.3 files untouched.
