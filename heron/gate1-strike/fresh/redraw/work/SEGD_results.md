# SEGD results — drawn-heron strike REDRAW, segment D (re-coil out of deep tuck)

Color gate (amended CHAIN_SPEC): FAIL if bird_sat < 42.9 or blue/grey shift on view. Home raw = 46.9.
Tip gate: within ~25 units (0-1000) of target AND strictly between cascade neighbours' measured tips where applicable; frill whole; legs planted; no filled water.
Verified anchors: RK_TUCK tip (454,823), RK_EXIT tip (621,824).

## RW_D1 — bd, t45, target tip (562,696)
Canvas: redraw/poses/RK_EXIT.png; home attached.

- Attempt 1: FAILED — tip (417,871) [x -145, y +175]; bird_sat 49.97 (passes color gate). View: color/frill/legs/paper clean, rings wide faint, no filled water — but head lowered far too much, bill near-vertical pointing down to the water, not a high re-coiled S. File: redraw/work/RW_D1_a1_2048.png
- Attempt 2: FAILED — tip (590,589) [x +28, y -107]; bird_sat 47.11 (passes). View: clean re-coiled S, frill whole, legs planted, rings wide faint — but head rose too high into alert height, tip at 58.9% height vs 69.6% target. File: redraw/work/RW_D1_a2_2048.png
- Escalation (fresh full drawing, key-style + neighbour landmarks): FAILED — tip (461,458) [x -101, y -238]; bird_sat 49.86 (passes). View: upright alert heron, neck tall and fully extended upward, framing/body shifted vs home stance, rings small at feet only — not the mid-rise re-coil. File: redraw/work/RW_D1_esc_2048.png
- Status: FAILED (2 attempts + 1 escalation). NOT installed to redraw/poses/RW_D1.png.

## RK_RISEB — KEY (halfway cascade), t44, target tip (524,738)
- Status: NOT ATTEMPTED — STOPPED. Its far reference is RW_D1 (once verified); RW_D1 failed all attempts including escalation, so per cascade rule the dependent poses stop.

## RK_RISEA — KEY (halfway cascade), t43, target tip (485,779)
- Status: NOT ATTEMPTED — STOPPED, dependent on RK_RISEB which was blocked by RW_D1 failure.

## RW_D0 — bd (halfway cascade), t42, target tip (466,800)
- Status: NOT ATTEMPTED — STOPPED, dependent on RK_RISEA which was blocked.

## Summary
0 passed. RW_D1 FAILED (tips 417,871 / 590,589 / esc 461,458; sats 49.97 / 47.11 / 49.86 — all color-pass, all tip/view-fail: edits swung between too-low vertical bill and too-high alert, escalation went fully upright). RK_RISEB, RK_RISEA, RW_D0 not attempted — cascade parent RW_D1 unverified. Nothing installed to redraw/poses/.
