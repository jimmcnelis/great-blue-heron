# HERON RIG v2.5 — GEOMETRY GATE, ITERATION 2 REPORT

**Date:** 2026-11-04. **Authorization:** Jimmy approved this exact iteration
2026-11-04 10:00, after the v2.5 gate failed on reach factor alone.
**Brief:** `~/workspace/heron/art2/rig-v25-geometry-brief.md`; **gate record:**
`~/workspace/heron/art2/rig-v25-gate/GATE_REPORT.md`.
**Deliverables in this folder:** `animal_v25.json` + `rig_v25.py` (iterated
build; also copied to the species package — see §5), `measure_iter2.py`,
`mask_alert.png`, `mask_deep_coil.png`, `mask_strike_peak.png`,
`overlay_strike_peak.png`, `sidebyside_strike_peak.png`.

## VERDICT: PASSED — every iteration criterion met on the one-shot measurement.

- **Reach factor 2.53** (band 2.3–2.7) — was 2.24, the gate's decisive fail.
- **Coil chord_base 0.267** (band 0.24–0.30) — mid-band, at the canon deep-coil
  value ≈0.27; was 0.297 at the band edge.
- **Coil arc:chord 2.18** (≥1.9) — was 1.97, thin margin; now comfortable.
- **Overlay torso back line sits ON the still's back line** (my visual check,
  §4) — the dome is gone.
- The peak, re-measured under the re-traced torso, **stays in band on every
  check** — the torso fix cost the peak nothing.
- All joints legal under the **frozen** caps; alert spot-check passes.

## 1. Measurement (one shot, frozen renders, centreline-entry only)

Protocol identical to the gate pass; the neckbase convention is the one Jimmy
fixed for this iteration (centreline-entry — the mechanism's centreline ×
torso-outline crossing; skull and centreline stations grounded on the rendered
PNGs; TORSO = 496.3 px, the gate's constant). The measurement ran **once**,
after the build was frozen. Nothing was adjusted after it.

| # | Check | Band | Gate build | Iter2 | Verdict |
|---|---|---|---|---|---|
| 1 | Coil chord_base | 0.24–0.30 | 0.297 (edge) | **0.267** | ✅ PASS |
| 2 | Coil arc:chord | ≥ 1.9 | 1.97 | **2.18** | ✅ PASS |
| 3 | **Reach factor coil→peak** | **2.3–2.7** | **2.24 FAIL** | **2.53** | ✅ **PASS** |
| 4 | Peak chord_base | 0.62–0.71 | 0.666 | **0.673** | ✅ PASS |
| 5 | Peak chord76 | 0.49–0.60 | 0.510 | **0.512** | ✅ PASS (= the still's own) |
| 6 | Peak arc | 0.66–0.75 | 0.682 | **0.678** | ✅ PASS |
| 7 | Peak neck-base width | 0.0626–0.0765 | 0.0665–0.0685 | **0.0685** (15% station, gate's method) | ✅ PASS |
| 8 | Alert chord_base (spot-check) | 0.40–0.47 | 0.458 | **0.432** | ✅ PASS |
| 9 | Alert neck-base width (spot-check) | 0.105–0.129 | 0.113–0.124 | **0.117** | ✅ PASS |
| 10 | Joint limits, new coil | within frozen caps | max 28.3°/30° | max 27.6°/30° (see §2) | ✅ PASS |
| 11 | Overlay back line on the still's line | visual | dome above the line | **on the line** (§4) | ✅ PASS |

Grounded landmarks (px, 1024×600) and derived skulls are recorded in
`measure_iter2.py`. Skull cross-checks vs the mechanism: peak 7.5 px, coil
0.7 px, alert 11.1 px (alert is a spot-check; the gate's own grounds agreed
to ≤7 px — see disclosure 4).

## 2. What changed — the coil knots (deepen only)

Descent untouched (s ≤ 0.53 identical to the gate build). The deepening is
exactly the mechanism the gate report pointed at — *the fold-back completed
later along the chain* — plus a deeper bottom dwell:

| s | 0.64 | 0.72 | 0.80 | 0.86 | 0.93 | 1.0 |
|---|---|---|---|---|---|---|
| gate θ | −92 | −124 | −130 | −96 | −58 | −38 |
| iter2 θ | −90 | −128 | −138 | −114 | −78 | −46 |

New coil joint table (°): −1.0, −2.3, −5.1, −17.6, −22.1, −19.9, −19.3,
−18.5, −19.0, −18.8, −16.6, −19.6, **−27.6**, −12.9, −0.6, **+20.3, +23.2,
+20.8, +17.1**. Zone maxima: throat 22.1/26, mid 19.6/20, hinge 27.6/30,
distal 20.8/22 — all legal, caps untouched. Note the shape of the fix: the
fold-back, instead of slamming through two hinge joints (gate: +28.3/+26.6),
now spreads across joints 16–19, and joint 13 takes more of the first
reversal — the chain folds *later and longer*, which is what pulls the skull
~20 px closer to the base. Design values: coil chord 0.306 (gate design,
old torso) → 0.269 (iter2 design); measured 0.267.

The rendered coil reads as a **deep coil**: a tight S with the fold sweeping
low across the breast and the head carried low and close — not the gate
build's moderate fold (viewed: `mask_deep_coil.png`).

Alert and strike_peak knot sets are byte-identical to the gate build.

## 3. What changed — the torso re-trace (15 → 57 points)

Traced from `audubon_strike.png` by per-column extraction (topmost-bird =
back line; solid-core bottom = underside), debug-plotted over the still and
hand-cleaned; the plotted extraction line sits on the wing's visible top
edge along the whole back. Key facts the extraction settled:

- The still's back actually peaks at **y ≈ 66** (shoulder, x ≈ 490) — the
  gate trace's (443, 50) point and its Catmull-Rom overshoot through sparse
  points are what built the dome Jimmy saw. The new loop follows the
  extracted line point-for-point and renders with minimal smoothing
  (n_per 8 → 3).
- The belly follows the **structural underside** (undertail + body core),
  with two broad, flat-bottomed **thigh-feathering masses** (bottoms 319 /
  327) where the still's rust thighs are solid. The plume-strand envelope
  (gate belly: y ≈ 338–344, i.e. the strand tips) is **excluded** — the
  plume is its own layer (PLUME LAW); on the new overlay the skirt zone
  below the belly is paper and strands, as a bare mechanism mask should be.
- Front/breast and chest points kept near the gate's reads so the chain
  root stays on the outline: design neckbases moved ≤6 px (peak
  (599.3, 226.4), coil (598.9, 226.5), alert unchanged (601.2, 219.4)).

**Legs:** leg 1 completely untouched — the front thigh mass (bottom 327)
keeps its traced hip (232, 322) buried. Leg 2's *top anchor only* moved,
(292, 326) → (296, 252): (292, 326) was traced as the point where the black
leg emerges from the *plume envelope*; under the structural belly (y ≈ 260
there) it would float detached. Knee (300, 432) and foot (288, 548) are
unchanged, and the stick still passes within ~5 px of the traced emergence
point.

## 4. The overlay, visually (my check, as briefed)

On `overlay_strike_peak.png`: the mask's top edge tracks the still's back
line from the tail, over the wing, across the shoulder hump, and down to
the neck junction — no red above the painted back anywhere along its run
(the gate overlay showed a continuous red dome standing proud of the back
by up to ~40 px). The belly now ends at the body's structural underside;
the thigh masses sit on the painted thighs. The neck still strikes on the
still's line of strike. Stated plainly: **the torso wart the gate flagged
is fixed; the silhouette is the same bird at the torso now.** What Jimmy's
visual pass should still weigh separately (unchanged by this iteration,
gate-noted): the mask's spear is the *video* strike (chord 0.673) vs the
still's own steeper ≈0.605, so the head sits lower than the painted head
and the eye-anchor ring lands on the cheek/bill-base area, as it did in
the gate overlay. Eye anchors for the record: alert (754.7, 35.7),
deep_coil (704.5, 128.6), strike_peak (811.1, 496.2).

## 5. Species package

Iteration passed, so per the brief the package now carries the iterated
build: `~/workspace/creature-engine/packages/great-blue-heron/animal_v25.json`
and `rig_v25.py` were replaced with the iter2 files (verified byte-identical
after copy). The definition carries `"definition": "rig-v25-mechanism-iter2"`
and an `iteration2_note` recording the knot changes, the frozen caps, and
the re-trace. The gate folder's own copies remain the frozen gate record.

## 6. Construction disclosures

1. **numpy shim:** this environment's numpy is 1.26 (`trapz`); the rig uses
   `trapezoid` (numpy ≥2 name for the identical function). The iter2 rig
   adds a one-line compat alias. No math changed; the gate build's design
   values reproduce exactly under it (verified on a scratch copy before
   any iter2 work).
2. **Knot search at the authoring stage:** several candidate knot sets were
   evaluated on *design integrals only* (the gate build did the same at its
   design stage). Two families were rejected on paper: steepening the
   descent breaks the mid cap (~20.6–21.4 vs 20 — the mid zone is genuinely
   saturated), and the first late-return draft broke joint 12 by 0.6° and
   joint 18 by 0.3°; the frozen set is the softened variant that is legal
   everywhere with margin. The gate measurement then ran once, on the
   frozen renders.
3. **Thigh dips:** the first trace draft rendered the thigh masses as
   narrow pointed fangs (a ~30 px spike read); they were widened and
   flat-bottomed during construction, before the freeze, and re-checked
   column-by-column against the still's extraction reads.
4. **Grounding hygiene:** the peak's first occiput ground sat on top of
   the skull (derived skull 16.6 px off the mechanism — outside the gate's
   own ≤7 px cross-check class); a precise re-ground ("rearmost tip of
   the head") landed 1.2 px from the gate build's ground of the *identical*
   head and is the one used. On the coil, both occiput grounds were
   off-axis (neck-side back edge; the occipital plume tip), so the coil
   skull was derived from the two consistent grounds — bill tip (grounded
   twice, ≤1 px apart) and plume tip — through the definition's head-frame
   offsets; cross-check vs the mechanism: **0.7 px**. The alert derived
   skull sits 11.1 px off the mechanism (the loosest of the three); the
   alert is a spot-check and passes with room (0.432 vs band 0.40–0.47)
   under it.
5. **Extraction outliers:** the per-column back read has isolated paper
   specks (dark flecks at y 37–80 in the scan's margins) — visible in the
   debug plot as floating dots, rejected by hand; the plotted bird line
   itself is continuous and was followed.
6. Nothing else moved: width profile, slimming field, head assembly,
   arc budget, joint caps, root anchor, torso landmarks (the torso-unit
   definition) are all identical to the gate build. No canon was changed,
   no fill or roster work was touched.

## 7. Where this leaves the gate

The v2.5 geometry gate's failed check is closed **on the same bands, the
same convention, and the same one-shot discipline**: reach 2.53, coil
0.267 (canon ≈0.27), arc:chord 2.18, peak suite intact, torso on the
still's line. Remaining before Path-3 fill, per the original gate
definition, is **Jimmy's visual pass** on the peak overlay and masks —
the numbers are his to overrule.
