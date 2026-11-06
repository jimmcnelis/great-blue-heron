# ESEG results — drawn-heron strike REDRAW, E segment (settle), final wave (2026-11-05)

Color gate (amended): FAIL only if bird_sat < 42.9 (paler than home) or a blue/grey shift on view. Richer sats pass and are tabulated. Home raw bird_sat = 46.9.
Tip gate: within ~25 units (0-1000 normalized) of target on the 2048x1152 PNG. RW_E1 additionally: strictly between RISEB (525,755) and E2 (556,775) on x, >=15% of the interval from either end.
Water law for all E poses: strike rings widest and faintest, ghosting toward calm; feet rings constant; blank paper; no filled water.
Note: the HOME raw file on disk is fresh/K_coil_color_redo.png (the brief's HOME raw artwork); no file named K_coil.png exists in fresh/. It was used as the SETTLE second reference (tip (472,848)).

## RW_E2 — PRE-INSTALLED (no work this wave)
- Viewed first: clean re-coiled S, widest faint rings, frill whole, legs planted, no filled water. Tip (556,775) per assignment.

## RW_E1 — target (540,765), edit of poses/RK_RISEB.png — FAILED
- Attempt 1: tip (592,807), bird_sat 51.10. View clean (identity, frill, legs, faint wide rings) but the head carried well past E2 in both x and y — not between RISEB and E2. File: work/RW_E1_e_a1_2048.png (not installed).
- Attempt 2: media.generate_image returned a tool error and wrote NO file; per the runtime's no-repeat directive the same request was not retried. No measurements exist for a2.
- Status: FAILED. Not installed. The RISEB -> E2 bridge slot remains open.

## RW_E3 — target (556,807), edit of poses/RW_E2.png — PASS (attempt 2)
- Attempt 1: tip (546,858), bird_sat 51.54. View clean; settled too far down (y +51). File: work/RW_E3_e_a1_2048.png.
- Attempt 2: tip (544,815), bird_sat 51.39. View: identity/frill/legs intact, S relaxing, widest-faint ghost rings, no filled water, no blue/grey shift. Within gate (dx -12, dy +8).
- Installed: poses/RW_E3.png

## RW_E4 — target (553,796), edit of RW_E3 — PASS (attempt 2)
- Attempt 1: tip (572,620), bird_sat 53.36. Head rose into a near-alert posture (y -176). File: work/RW_E4_e_a1_2048.png.
- Attempt 2: tip (551,788), bird_sat 52.60. View clean: head stayed low, whisper of a rise, faint wide rings, no filled water. Within gate (dx -2, dy -8).
- Installed: poses/RW_E4.png

## RW_E5 — target (552,810), edit of RW_E4 — FAILED
- Attempt 1: tip (529,849), bird_sat 52.28. Sank too far and drifted left (dy +39). File: work/RW_E5_e_a1_2048.png.
- Attempt 2: tip (540,864), bird_sat 53.91. Sank further still (dy +54), head near the water. File: work/RW_E5_e_a2_2048.png.
- Status: FAILED after 2 attempts — both edits overshot the small sink into a near-home-depth drop. Not installed.

## RW_E6 — target (551,822) — PASS (attempt 2), chained from RW_E4
- Because RW_E5 failed, E6 was edited from the nearest installed neighbour, poses/RW_E4.png (measured tip (551,788)), per the brief's chaining rule.
- Attempt 1: tip (538,878), bird_sat 54.21. Same downward overshoot (dy +56). File: work/RW_E6_e_a1_2048.png.
- Attempt 2: tip (544,817), bird_sat 53.15. View clean: low S, modest sink, wide band of blank paper above the ghost rings, no filled water. Within gate (dx -7, dy -5).
- Installed: poses/RW_E6.png

## RW_E7 — target (550,824), one attempt from RW_E6 — PASS, DISTINCT from E6
- Attempt 1: tip (546,836), bird_sat 55.20. View clean (frill whole, legs planted, faintest wide rings).
- Distinctness: E6 measured tip is (544,817); E7 is (+2,+19) from it — NOT within the ~5-unit clone band in y. E7 is a genuinely distinct drawing, not an E6 hold. Within target gate (dx -4, dy +12).
- Installed: poses/RW_E7.png

## RW_E8 — target (550,823), one attempt from RW_E6 — PASS, DISTINCT from E6
- Attempt 1: tip (554,845), bird_sat 56.25. View clean (identity, frill, legs, ghost rings, no filled water).
- Distinctness: (+10,+28) from E6's (544,817) — NOT a clone. E8 is a distinct drawing, not an E6 hold. Within target gate (dx +4, dy +22).
- Installed: poses/RW_E8.png

## RK_SETTLE — target (510,836), sanctioned halfway edit — FAILED
- Canvas: poses/RW_E8.png (best late-E drawing, distinct); second reference: HOME raw fresh/K_coil_color_redo.png (472,848). Midpoint target (511,836).
- Attempt 1: tip (393,897), bird_sat 57.02. Overshot past HOME itself — head folded nearly to home and lower. File: work/RK_SETTLE_e_a1_2048.png.
- Attempt 2: tip (458,754), bird_sat 56.33. Missed the other way — tip left of home in x but far too high (dy -82); a raised near-home coil, not the low halfway approach. File: work/RK_SETTLE_e_a2_2048.png.
- Status: FAILED after 2 attempts. Not installed. The t57 settle-approach slot remains open.

## Saturation table (bird_sat, all attempts; gate >= 42.9)
| pose | a1 | a2 | installed sat |
|---|---|---|---|
| RW_E1 | 51.10 | (tool error, no file) | — |
| RW_E3 | 51.54 | 51.39 | 51.39 |
| RW_E4 | 53.36 | 52.60 | 52.60 |
| RW_E5 | 52.28 | 53.91 | — |
| RW_E6 | 54.21 | 53.15 | 53.15 |
| RW_E7 | 55.20 | — (one attempt by design) | 55.20 |
| RW_E8 | 56.25 | — (one attempt by design) | 56.25 |
| RK_SETTLE | 57.02 | 56.33 | — |
No attempt failed the color gate; no blue/grey shift seen on any view. All candidates ran richer than home (46.9), trending richer down the segment.

## Summary
PASSED + installed: RW_E3 (544,815), RW_E4 (551,788), RW_E6 (544,817), RW_E7 (546,836, distinct), RW_E8 (554,845, distinct).
FAILED: RW_E1 (overshoot + tool-errored retry), RW_E5 (two downward overshoots), RK_SETTLE (two misses in opposite directions).
E7/E8 verdict: BOTH distinct drawings — neither slot is an E6 hold.
Open slots for the coordinator: RW_E1 (RISEB->E2 bridge), RW_E5 (E4->E6 step; E6 currently bridges from E4 directly), RK_SETTLE (t57).
