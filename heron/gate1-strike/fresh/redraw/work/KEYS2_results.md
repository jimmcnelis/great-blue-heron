# KEYS2 Results — Strike Redraw

Segment: KEYS2 (photo ref for all four = ref_coil.png)
Gates: view pass, bill tip within ~25 units of target (0-1000 coords), bird_sat 42.9-50.9 on the 2048x1152 PNG in redraw/poses/

## RK_TUCK — target (449,823), t39-41
- Status: FAILED
- Attempts: 2
- Attempt 1: measured tip (430,847), bird_sat 56.50 — view: good deep tuck, tight question-mark fold, frill/legs/widest faint rings correct; FAIL on color (sat above band)
- Attempt 2 (file currently in poses/RK_TUCK.png): measured tip (403,856), bird_sat 48.88 — view: neck in a looser S, not the tight tuck, rings small at feet only, head not folded to chest; FAIL on tip (dx -46, dy +33) and pose
- Verdict: FAILED — a1 passed view/tip-per-axis but failed color; a2 passed color but failed tip/pose

## RK_RISEA — target (485,779), t43
- Status: FAILED
- Attempts: 2
- Attempt 1: measured tip (498,482), bird_sat 45.52 — view: head fully risen upright, one leg stepping diagonally, not home stance; FAIL on tip (dy -297) and legs/pose
- Attempt 2 (file currently in poses/RK_RISEA.png): measured tip (482,518), bird_sat 44.18 — view: head still high in upright S, plus a horizontal water wash across the bottom (wrong water state); FAIL on tip (dy -261) and water/pose
- Verdict: FAILED — color passed both times, generator would not keep the head low at one-third rise

## RK_RISEB — target (524,738), t44
- Status: FAILED
- Attempts: 2
- Attempt 1: measured tip (461,538), bird_sat 48.37 — view: clean half-coil S, legs planted, frill and faint foot rings correct, but head at back height; FAIL on tip (dx -63, dy -200)
- Attempt 2 (file currently in poses/RK_RISEB.png): measured tip (447,908), bird_sat 53.81 — view: crouched low with steep bill, overshot below target, color vivid; FAIL on tip (dx -77, dy +170) and color
- Verdict: FAILED — a1 passed color/view basics but tip far high-left; a2 overshot low and failed color

## RK_SETTLE — target (510,836), t57
- Status: FAILED
- Attempts: 2
- Attempt 1: measured tip (473,727), bird_sat 50.75 — view: plausible deep S coil, legs planted, ghost foot rings correct; FAIL on tip (dx -37, dy -109)
- Attempt 2 (file currently in poses/RK_SETTLE.png): measured tip (430,918), bird_sat 49.84 — view: head very low but bill touches the water with a touch ring at the tip (wrong water state for settle; should be ghost rings at feet only); FAIL on tip (dx -80, dy +82) and water
- Verdict: FAILED — color passed both times, tip swung from too high to too low/touching

## Summary
0 of 4 keys passed. All four are FAILED after 2 attempts each (8 generations total); the files in redraw/poses/ for these names are the attempt-2 versions and are NOT verified — do not use them as inputs for breakdowns. Closest calls: RK_TUCK a1 (tip 430,847, view correct, only sat 56.50 failed) and RK_RISEB a1 (sat 48.37, clean view, tip high-left).
