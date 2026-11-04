# HERON RIG v2.5 — GEOMETRY GATE REPORT

**Date:** 2026-11-04. **Brief:** `~/workspace/heron/art2/rig-v25-geometry-brief.md`.
**Deliverables in this folder:** `animal_v25.json` (also copied to the species
package), `rig_v25.py` (mechanism + renderer; also copied), `measure_gate.py`
(the measurement pass), `mask_alert.png`, `mask_deep_coil.png`,
`mask_strike_peak.png`, `overlay_strike_peak.png`, `sidebyside_strike_peak.png`.

## VERDICT: GATE NOT PASSED — one decisive miss, reported per the one-shot rule. No re-tuning was done after measurement.

- **Standing strike peak: PASSES every check.**
- **Alert rest: PASSES.**
- **Reach factor (coil→peak): FAILS under every measurement convention** —
  2.24 on the primary read (band 2.3–2.7). The coil is ~0.03–0.04 of chord
  too shallow relative to the peak's reach.
- **Deep coil chord_base sits exactly at its band edge** (0.297 vs ≤0.30,
  primary read) and — stated plainly — **the bare mask cannot settle it**:
  the three neckbase reads bracket the band on both sides (0.226 / 0.297 /
  0.400). See "The neckbase problem" below.
- The mechanism itself is **legal in all three poses** (every joint inside
  its cap), widths pass, and the eye anchor exists in the geometry of every
  pose (spike-3's silent-eye failure cannot recur structurally).

---

## 1. The mechanism (one animal definition)

`animal_v25.json` — body, controller and rendering read the same definition,
per the FARMS discipline:

- **Neck = 20-link chain**, arc budget **0.72 torso** (canon standing band
  0.70–0.75). Segment lengths follow the skeleton mounts: mid-neck elongated
  (weight 0.75 + 0.60·sin(π(i+½)/20); longest link 1.35 units vs 0.75 at the
  ends, ratio ≈ 1.69).
- **Joint limits, two bend zones** (19 joints): throat (1–6) 26°, mid (7–12)
  20°, **hinge (13–17) 30°** — the high backward kink behind the head, the
  strike hinge of the anatomy anchor — distal (18–19) 22°.
- **Width profile from the approved stills** (rest, fraction of torso at
  arc-fractions 0 / .25 / .5 / .75 / 1): 0.117 / 0.112 / 0.102 / 0.088 /
  0.068 — neck-base at the drawing's 0.1167, **not** v2.4's +40% (its base
  read 70 px where the drawing's is 49–57). **Slimming field** at full
  extension ≈ 0.595 at the base (the stills' strike/rest base-width ratio,
  matching the 0.59–0.60 measured slimming canon).
- **Head assembly** rides the chain's end: skull ellipse 0.052 × 0.030
  torso; bill 0.23 torso long, tip reach 0.270 from skull centre; occipital
  plume spike. Dimensions derived from the approved strike still by the same
  grounding method as the motion study, twice, agreeing ≤0.015 torso.
- **Eye anchor** in the head frame: +0.028 torso along the bill, +0.014 up
  from skull centre. Validated against spike-3's amber-cluster find on the
  corpus gold (within ~8 px there).
- **Poses are heading-profile states** of the chain (PCHIP through authored
  knots; segment heading = profile mean over the segment). Torso, legs and
  feet are the approved strike still's own outline, traced once and shared
  by all poses — the torso is one rigid body, as it should be.

**Joint-limit usage (construction check, all legal):**

| Pose | Max joint | Where | Cap |
|---|---|---|---|
| alert | 19.8° | joint 8 (mid) | 20° |
| deep_coil | 28.3° | joint 16 (hinge) | 30° |
| strike_peak | 3.8° | mid-chain | 20–30° |

Full coil joint table (°), frozen build: −1.0, −2.3, −5.1, −17.6, −22.1,
−19.9, −19.3, −18.5, −18.9, −18.9, −17.9, −19.7, −23.5, −9.0, +2.3, +28.3,
+26.6, +18.1, +11.0 — the first reversal spreads across the throat and mid
zones, the fold-back reversal (+28.3°, +26.6°) lands in the hinge zone as
the anatomy says it should; the alert's recovery bend likewise lands in
the hinge zone (joints 15–17: +13.8, +12.9, +8.7).

**Construction disclosures (both made BEFORE any gate measurement, neither
touches a canon band):**
1. The chain root was first placed 46 px inside the torso silhouette; that
   burial made the canon *visible* arc unreachable by construction (max
   0.626 vs the 0.66 floor). Root moved to the breast anchor **on** the
   outline — the convention v2.4 and the still instrument both use.
2. Joint caps were revised once during construction (mid zone 16°→20°,
   throat 24°→26°, hinge 28°→30°): the deepest measured coils accumulate
   ~300–340° of turning, and at a 16° mid cap the canon coil is unreachable
   by construction no matter the pose. Caps were then frozen; poses were
   authored against them (≤90% at authoring, final maxima above).
3. Pose knot sets were iterated at the **design stage only**, against the
   design integrals — that is what authoring a pose is. Once the three
   poses were legal and in-band on design integrals, the knots were
   **frozen**, the masks rendered, and the gate measurement below ran
   **once**. Nothing was adjusted after it.

## 2. Measurement method (the artifact, not the angles)

Landmarks were placed by visual grounding **on the rendered PNGs** — the
motion study's own method — then computed with the study's definitions
(`measure_gate.py`): torso = hull diameter over tail/chest/backtop/belly;
chain ordered skull → centreline stations → neckbase; station-1 = point at
76% of arc **from the skull**; chord76 = |skull − station-1|; arc = visible
centreline length. Centreline stations are edge-pair midpoints (alert,
coil) or grounded band centres (peak). Skull centre = grounded back-of-head
+ 0.052 torso along the grounded bill direction (the bare masks carry no
eye mark — see §4); grounded skull centres agree with the mechanism's to
≤7 px on all three poses.

**Torso:** one rigid outline shared by the masks. Clean per-mask reads:
498.2 px (peak), 494.3 px (alert); the coil's chest read landed on the
protruding throat and was rejected. **TORSO = 496.3 px** used throughout
(ratio sensitivity <1%).

### Per-pose landmark table (px on the 1024×600 canvas, grounded)

| Landmark | strike_peak | alert | deep_coil |
|---|---|---|---|
| tail tip | (117.8, 328.8) | (118.8, 328.8) | (118.8, 325.8) |
| chest front | (603.1, 216.0) | (602.1, 225.0) | (632.8, 219.6)† |
| back top | (429.1, 49.8) | (438.3, 49.8) | (420.9, 50.4) |
| belly bottom | (362.5, 345.6) | (452.6, 343.2) | (394.2, 345.0) |
| skull back | (779.3, 475.8) | (714.8, 39.6) | (687.1, 117.6) |
| bill tip | (875.5, 596.4) | (873.5, 42.0) | (812.0, 210.0) |
| skull centre (derived) | (795.4, 496.0) | (740.6, 40.0) | (707.9, 132.9) |
| centreline stations | (792.6, 469.8), (702.5, 361.2), (646.1, 261.0) | (731.7, 70.8), (733.7, 159.0), (681.9, 263.4) | (699.9, 142.8), (717.8, 219.0), (670.7, 304.5) |
| neckbase — notch read | (614.4, 213.6) | (603.1, 208.8) | (627.7, 211.2) |
| neckbase — blend read | (592.9, 277.2) | (606.2, 252.0) | (583.7, 288.0) |
| neckbase — centreline entry (construction) | (599.8, 229.5) | (601.2, 219.4) | (599.5, 232.7) |

† coil chest read rejected (it is the throat dip, not the torso).

## 3. The neckbase problem (read this before the numbers)

On a feathered bird the neck visibly *enters* the body at a readable
junction. On a bare black silhouette the tube merges into the torso dome
over a long stretch, and three defensible reads of "neckbase" diverge:
**notch** (where the neck's upper outline meets the body outline — the
project's established convention, cf. the still instrument),
**centreline-entry** (where the centreline crosses the torso outline — a
construction value), and **blend** (where the tube's flank visually merges
into the body mass). All three are tabulated for every chord. **The
centreline-entry read is primary**: it is the only one defined identically
for all poses, and it matches how the project's still numbers were built.
The gate's failures below are stated so they hold or fall on their own
merits under each read — the decisive one fails under **all three**.

## 4. Gate checks

| # | Check | Band | Notch | Centreline-entry | Blend | Verdict |
|---|---|---|---|---|---|---|
| 1 | Peak chord_base | 0.62–0.71 | 0.676 | **0.666** | 0.601 | **PASS** (fails only the blend read) |
| 2 | Peak chord76 | 0.49–0.60 | 0.512 | **0.510** | 0.510 | **PASS** (all reads; = the approved still's own 0.512) |
| 3 | Peak arc | 0.66–0.75 | 0.684 | **0.682** | 0.681 | **PASS** (all reads) |
| 4 | Peak neck-base width | 0.0626–0.0765 | — | **0.0665–0.0685** | — | **PASS** (see note) |
| 5 | Alert chord_base | 0.40–0.47 | 0.439 | **0.458** | 0.506 | **PASS** (fails only the blend read) |
| 6 | Rest neck-base width | 0.105–0.129 | — | **0.113–0.124** | — | **PASS** |
| 7 | Coil chord_base | 0.24–0.30 | 0.226 | **0.297** | 0.400 | **EDGE — not robustly settled** (passes only the primary read, at the edge) |
| 8 | Coil arc:chord | ≥ 1.9 | 2.60 | **1.97** | 1.40 | **PASS on primary** (thin margin; fails blend) |
| 9 | Reach factor coil→peak | 2.3–2.7 | 2.99 | **2.24** | 1.50 | **FAIL — under every read** |
| 10 | Joint limits, all poses | within caps | — | max 28.3° / 30° | — | **PASS** |
| 11 | Eye anchor present + recorded | — | — | §5 | — | **DONE** |

**Note on check 4:** the 6%-of-arc base station lies inside the body merge
on the silhouette and cannot be scanned directly (scans there read the
merged blob, 136 px). The nearest clean station (15% of visible arc) reads
**33.0 px = 0.0665** off the mask; taper-corrected to the base station via
the drawn profile it is **0.0685** — inside the band either way, vs v2.4's
equivalent flaw of +40%. Check 6's station is outside the merge and reads
cleanly at three arc fractions (0.113–0.118) plus the grounded-station scan
(0.124).

**Arc caveat:** the measured arcs use 3 grounded centreline stations per
pose; sparse stations cut corners, so measured arc is biased slightly low
(e.g. coil design arc 0.692 vs measured 0.584 — the coil's S is where the
bias bites). Checks 3 and 8 pass despite the bias, not because of it.

## 5. Eye-anchor positions (mechanism, per pose)

The bare masks draw no eye (gate scope); the anchor is geometry, recorded
on every pose as briefed — the fill stage draws from these coordinates and
cannot silently lose the eye the way spikes 1–2 did.

| Pose | Eye anchor (px) | On the overlay |
|---|---|---|
| alert | (754.7, 35.7) | — |
| deep_coil | (723.9, 131.3) | — |
| strike_peak | (811.1, 496.2) | yellow ring on `overlay_strike_peak.png` |

Honest note: on the overlay the ring lands on the still's cheek/bill-base
area, ~40 px below the still's painted eye — the mask's whole head sits
lower than the still's because the mask's spear is the *video* strike
(chord 0.666, shallower) while the still's own strike measures ≈0.605 and
steeper. The anchor is true in the head frame; the head frame's pitch on
this pose does not reproduce the still's head pitch exactly.

## 6. What the mechanism could not reach — honest list

1. **Reach factor 2.3–2.7: not reached.** With the peak at 0.666, the
   family needs a coil chord of 0.247–0.290; the authored coil lands at
   0.297 (primary read). The fold needs roughly 0.03–0.04 more chord depth
   — on the order of 12–18° more accumulated fold, or the fold-back
   completed later along the chain. The joint caps have the headroom
   (hinge max 28.3/30, throat ≤22.1/26); the authored knot set does not use
   it. **Fixing this is a new authoring decision, not something this gate
   run may do to itself.**
2. **The coil's chord is not robustly measurable on a bare mask** (reads
   0.226–0.400). A diving neck's entry point is under-determined by the
   silhouette alone. What would settle it: render the coil with the neck
   over a contrasting body tone (or scribe the centreline) in a future
   pass — a measurement-convention decision for Jimmy.
3. **The coil reads as a moderate coil, not the deepest NatGeo fold** —
   consistent with its band-edge chord. The extreme qpYk fold (chord at
   the 0.24 floor) was not demonstrated.
4. **Visually, the overlay is not yet the same bird at the torso:** the
   torso loop's smoothing inflates the dome above the still's back line
   (visible in the overlay/side-by-side). The torso outline is shared
   construction, not a gated item, but it needs a denser re-trace before
   any likeness judgment — Jimmy's visual pass on the peak overlay should
   weigh the neck (in band, on the still's line of strike) separately from
   the dome (known wart).
5. A small silhouette step shows where the neck tube exits the torso on
   the alert and peak masks — the tube's first links leave the outline at
   a slight angle discontinuity. Cosmetic; belongs to the fill stage.

## 7. Gate outcome

**NOT PASSED** — on check 9 (decisive, fails under every read), with check
7 unresolved-at-the-edge. Everything else passes, including the full peak
suite the arbitration demanded (the 1.83× under-extension is closed:
0.666 vs v2.4's 0.247) and the neck-base width flaw (0.117-class at rest,
slimmed ≈0.60 at peak, vs v2.4's +40%).

**Stopped here, per the brief's one-shot rule.** The path forward, if
Jimmy wants it: re-author only the coil's knot set ~0.04 deeper (the
mechanism and caps already allow it) and re-run this same measurement
pass on the new coil mask alone; plus a ruling on the coil neckbase
convention in §3. No other part of the build needs to change.
