# ANCHOR PICKS — six pencil-test style candidates for Jimmy's eye-gate

**Round:** Gate 1, step 1 (revised brief, Jimmy 2026-11-05 11:32: "give me 6 choices — distinct from each other").
**Style law for this build:** Blaise pencil-test — graphite on warm paper, monochrome, no Audubon manner, no ink, no color. Water implied: pencil rings at the ankles on the standing poses.
**Method:** every drawing is rendered procedurally in graphite strokes *from the rig's own geometry* (pose canvas first, drawing sits on it), so the fit numbers below are measured off the finished PNGs, not off build bookkeeping. All six pass the geometry gate (IoU ≥ 0.85). Per project law, the numbers are diagnostics — **the pick is Jimmy's eye on style.**
**Style reference:** 4 frames extracted from Jimmy's lion video (work/lion_*.png). The Blaise hand there: fine graphite contour of varying weight, sparse form-hatching in shadow only, a few interior form lines, paper left white.

Canvas design values (rig v2.5, measured): alert chord_base 0.456 · coil chord_base 0.269 (canon 0.27) · peak chord_base 0.666 (canon standing-spear band 0.62–0.71), arc conserved 0.695–0.707.

---

## 1 — ALERT · CONSTRUCTION-HEAVY → `pick1_construction_20261105-163946.png`
- **Pose source:** rig v2.5 `alert` canvas (mask_alert).
- **Fit:** silhouette IoU **0.894** (4 attempts: 3 seed variants + 1 refined).
- **Eye note:** the animator's underdrawing left in — torso ellipse, joint circles stacked through the S-neck, head circle, bill guide overshooting the tip; closest to the raw pencil-test energy of the lion frames.

## 2 — ALERT · CLEAN TIGHT PENCIL → `pick2_clean_20261105-163946.png`
- **Pose source:** rig v2.5 `alert` canvas.
- **Fit:** silhouette IoU **0.922** (4 attempts).
- **Eye note:** the finished end of the spectrum — one controlled line, construction hidden, quiet belly-shadow hatch and a bowed folded-wing line; precise and calm.

## 3 — COIL · SMUDGE-TONAL → `pick3_smudge_20261105-163946.png`
- **Pose source:** rig v2.5 `deep_coil` canvas (chord_base 0.269 — the fold, not a shrink).
- **Fit:** silhouette IoU **0.895** at the soft-tone threshold (4 attempts).
- **Eye note:** shading built from smudged graphite masses with broad stump strokes; darkest under the coil fold; soft and painterly, the eye dot is the only hard point.

## 4 — PEAK STRIKE · HIGH-ENERGY GESTURE → `pick4_gesture_20261105-163946.png`
- **Pose source:** rig v2.5 `strike_peak` canvas (chord_base 0.666, full canon extension, bill tip to the lower-right corner).
- **Fit:** silhouette IoU **0.898** (4 attempts).
- **Eye note:** fast scribble-hatch follows the spear's direction, ghost arcs trail the neck's path — the motion is in the line itself; the most alive of the six.

## 5 — STANDING · MINIMAL LINE → `pick5_minimal_20261105-163946.png`
- **Pose source:** rig v2.5 `alert` canvas.
- **Fit (landmark agreement, per brief):** nearest-ink distance — eye 0.4 px, bill tip 1.3 px, ankles 2.2 px, feet 0.0 px; the two *interior* reference points (skull centre, neckbase) sit 12 px from the nearest line, as they must in an outline drawing. Max surface-landmark error **2.2 px**; mean over all landmarks 3.8 px. (Silhouette IoU also measured: 0.946.)
- **Eye note:** the fewest lines that still read instantly — one flowing contour, one wing curve, an eye dot, two ankle rings; nothing to hide behind.

## 6 — FLIGHT · FULL PENCIL → `pick6_flight_20261105-163946.png`
- **Pose source:** **no flight pose exists in rig v2.5** — the canvas was composed from canon dimensions (torso hull = 1 torso unit, bill 0.23 torso, neck folded at the standing arc budget with the head clear of the breast, legs trailing past the tail, wings in a shallow glide V). Fit is measured against that composed canvas. First composed canvas (rotated standing torso) buried the head and was discarded on the eye read before any drawing was delivered; the delivered canvas is the second composition.
- **Fit:** silhouette IoU **0.909** (5 attempts total across the two canvases).
- **Eye note:** the hand survives the wing — folded neck, spear bill and trailing legs all read in flight; honest weakness: the wing planform runs narrower/more petal-like than a real GBH's broad wing, so this pick tests the *hand* on wings more than the wing shape itself.

---

**Contact sheet:** `picks_sheet_20261105-163946.png` — all six, labeled by number + treatment.
**Status:** delivered for Jimmy's pick. No animation, no training — stopped at the gate as briefed.
