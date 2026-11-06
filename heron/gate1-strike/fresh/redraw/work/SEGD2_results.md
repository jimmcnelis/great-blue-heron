# SEGD2 results — drawn-heron strike REDRAW, segment D round 2 (halfway-edit cascade)

Color gate (amended CHAIN_SPEC): FAIL if bird_sat < 42.9 or blue/grey shift on view. Home raw = 46.9.
Tip gate: within ~25 units (0-1000) of target AND strictly between cascade neighbours' measured tips; frill whole; legs planted; no filled water.
Verified anchors used: RK_TUCK tip (454,823), RK_RISEB tip (525,755) [file in redraw/poses/], RK_EXIT tip (621,824).
Method this round: halfway edits (canvas + far reference + home frame on every call).

## RK_RISEA — KEY (halfway edit), t43, target tip (485,779)
Canvas: redraw/poses/RK_TUCK.png; far ref: redraw/poses/RK_RISEB.png; home attached.

- Attempt 1 (halfway edit): FAILED — tip (531,815) [x +46, y +36]; bird_sat 51.08 (color pass). View: clean color/frill/legs/paper, rings wide faint — but the edit ran essentially all the way to RISEB (tall S, head high); tip x also beyond RISEB's measured x (525), failing anti-clone. File: redraw/work/RK_RISEA2_a1_2048.png
- Attempt 2 (halfway edit, stronger stop-short wording): FAILED — tip (448,825) [x -37, y +46]; bird_sat 53.76 (color pass). View: clean, rings wide faint — but a near-clone of RK_TUCK (tip within 6 units of TUCK's measured tip); the rise barely happened. File: redraw/work/RK_RISEA2_a2_2048.png
- Escalation (fresh full drawing, key-style + both neighbours' landmarks): FAILED — tip (559,490) [x +74, y -289]; bird_sat 47.47 (color pass). View: upright alert heron, neck tall, head at mid-frame height; also only feet rings (no wide touch rings). Not a mid-rise out of the tuck. File: redraw/work/RK_RISEA2_esc_2048.png
- Status: FAILED (2 attempts + 1 escalation). NOT installed to redraw/poses/RK_RISEA.png. The halfway edit swung between a RISEB clone and a TUCK clone; the fresh draw went fully alert — same failure family as the RISE round (tips 513,546 / 484,706 there).

## RW_D0 — bd (halfway cascade), t42, target tip (466,800)
- Status: NOT ATTEMPTED — STOPPED. Its far reference is RK_RISEA (once verified); RK_RISEA failed all attempts including escalation, so per cascade rule the dependent pose stops.

## RW_D1 — bd (correction halfway), t45, target tip (562,696)
Canvas: redraw/poses/RK_RISEB.png; far ref: redraw/poses/RK_EXIT.png; home attached.
Note: the spec target y (696) sits ABOVE both neighbours' measured y (RISEB 755, EXIT 824) — the re-coil arc peaks here before RW_E1 (558,735); anti-clone judged on x-betweenness + distance from target.

- Attempt 1 (halfway toward EXIT, stop well short): FAILED — tip (621,596) [x +59, y -100]; bird_sat 46.88 (color pass). View: clean re-coiled S, frill whole, legs planted, rings wide-ish — but head rose too high and too far right (x equals EXIT's measured x at alert-ish height). File: redraw/work/RW_D1b_a1_2048.png
- Attempt 2 (slight move only, head down): FAILED — tip (552,842) [x -10, y +146]; bird_sat 48.35 (color pass). View: clean S, rings widest faint — but head dropped nearly to the water, bill near-vertical; a low EXIT-like pose, not the arc peak. File: redraw/work/RW_D1b_a2_2048.png
- Escalation (fresh full drawing, key-style + both neighbours' landmarks): FAILED — tip (528,424) [x -34, y -272]; bird_sat 51.23 (color pass). View: upright alert heron, tall neck, only feet rings — not the mid-height re-coiled S. File: redraw/work/RW_D1b_esc_2048.png
- Status: FAILED (2 attempts + 1 escalation). NOT installed to redraw/poses/RW_D1.png. Same swing as round 1 (417,871 / 590,589 / esc 461,458): edits oscillate between too-high and too-low; fresh draws collapse to upright alert.

## Summary
0 passed, 2 failed (RK_RISEA, RW_D1 — each 2 attempts + 1 escalation, all color-pass, all tip/view-fail), 1 stopped (RW_D0, cascade parent RK_RISEA unverified). Nothing installed to redraw/poses/. Pattern across both D rounds: the edit model cannot hold an intermediate head height in this low-head region — it snaps to one of the two reference poses or to upright alert.
