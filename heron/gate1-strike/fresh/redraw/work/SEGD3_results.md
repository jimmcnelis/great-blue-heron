# SEGD3 results — drawn-heron strike REDRAW, segment D round 3 (micro-edits only)

Color gate (amended CHAIN_SPEC): FAIL if bird_sat < 42.9 or blue/grey shift on view. Home raw = 46.9.
Tip gate: within ~25 units (0-1000) of target AND strictly between neighbours' measured tips (>=15% of interval) where applicable; frill whole; legs planted; no filled water.
Verified anchors: RK_TUCK (454,823), RK_RISEB (525,755), RK_EXIT (621,824).
Method this round: MICRO-EDITS from the nearest installed neighbour only; no fresh full drawings; no "halfway" language; small explicit movements; up to 3 attempts per pose. Note: the assignment text for RW_D1 said the head moves "right and down" while its own percentages (75.5% -> 70% height) describe a move UP — attempt 1 followed the word "down" and dropped; later attempts followed the percentages.

## RW_D1 — bd, t45, target tip (562,696)
Canvas: redraw/poses/RK_RISEB.png; home attached (no far reference — round 2's EXIT reference drove overshoot).

- Attempt 1 (assignment wording, "right and down a short step" to 56%/70%): FAILED — tip (558,884) [x -4, y +188]; bird_sat 49.19 (color pass). View: frill whole, legs planted, rings wide faint, no filled water — but head dropped to just above the water, bill near-vertical; the word "down" was followed literally instead of the percentages. File: redraw/work/RW_D1_r3_a1_2048.png
- Attempt 2 (movement restated right-and-slightly-UP, head held high, bill not reaching to water): FAILED — tip (610,486) [x +48, y -210]; bird_sat 47.52 (color pass). View: clean color/frill/legs, rings wide faint — but neck swung into a tall upright S, head at alert-ish height. File: redraw/work/RW_D1_r3_a2_2048.png
- Attempt 3 (movement shrunk: neck stays low/horizontal, only the head end of the S swings a short step right, bill angles a bit more down-forward): FAILED — tip (556,775) [x -6, y +79]; bird_sat 49.13 (color pass). View: the best-looking of the three — re-coiled S nearly restored, frill whole, legs planted, rings widest faint, no filled water — but tip y is 79 below target, outside the ~25 gate. File: redraw/work/RW_D1_r3_a3_2048.png
- Status: FAILED (3 attempts). NOT installed to redraw/poses/RW_D1.png. The three attempts bracket the target in y (884 / 486 / 775) but none landed within 25; a3 is closest in pose quality and x.

## RK_RISEA — KEY, t43, target tip (485,779)
Canvas: redraw/poses/RK_TUCK.png; far ref: redraw/poses/RK_RISEB.png; home attached.

- Attempt 1 ("lift a SHORT step, only about a quarter of the way toward the second image"): FAILED — tip (478,676) [x -7, y -103]; bird_sat 54.27 (color pass). View: frill whole, legs planted, rings wide faint — but head rose well out of the tuck to back height; too much lift. File: redraw/work/RK_RISEA_r3_a1_2048.png
- Attempt 2 (movement shrunk: head barely stirs, stays folded DOWN low against the chest, bill steeply down): PASS — tip (474,769) [x -11, y -10]; bird_sat 54.47 (color pass). Anti-clone: strictly between TUCK (454,823) and RISEB (525,755) on both axes — x at 28% of interval, y at 79% from TUCK / 21% from RISEB, both >=15%. View: head low and folded with a genuine small stir, frill whole, legs planted in home stance, rings wide and faint, no filled water, no blue/grey shift. File: redraw/work/RK_RISEA_r3_a2_2048.png
- Status: PASS (2 attempts). Installed to redraw/poses/RK_RISEA.png (2048x1152). Measured installed tip (474,769).

## RW_D0 — bd, t42, target tip (466,800)
Neighbours: RK_TUCK (454,823) and RK_RISEA as installed this round (474,769).

- Attempt 1 (canvas RK_RISEA, edited DOWNWARD toward the tuck — chosen because RK_RISEA installed first and its tip is ~equidistant; "head settles a short step back down", to 46.5%/80%): FAILED — tip (398,862) [x -68, y +62]; bird_sat 56.31 (color pass). View: frill whole, legs planted, rings widest faint — but the settle overshot past the tuck into a deep drinking dip, bill near-vertical above the water, head swung left. File: redraw/work/RW_D0_r3_a1_2048.png
- Attempt 2 (canvas RK_TUCK, assignment wording: first slight stir, to 47%/80%): FAILED — tip (472,763) [x +6, y -37]; bird_sat 54.79 (color pass). View: clean stir pose, frill whole, legs planted — but tip y is 37 above target and the tip sits essentially AT RK_RISEA's measured height (y 763 vs 769; x within 2 of RISEA's 474): anti-clone fail, the stir ran nearly the full TUCK->RISEA distance. File: redraw/work/RW_D0_r3_a2_2048.png
- Attempt 3 (canvas RK_TUCK, movement shrunk further: uncurl just a fraction, to 46.5%/81%, head deep in tuck below belly line): FAILED — tip (457,826) [x -9, y +26]; bird_sat 54.29 (color pass). View: clean, frill whole, legs planted, rings widest faint — but the measured tip is within 3 units of RK_TUCK's own tip (454,823) on both axes: a TUCK clone, the stir did not register; also fails strict-betweenness in y (826 is below TUCK's 823, outside the TUCK-RISEA interval). File: redraw/work/RW_D0_r3_a3_2048.png
- Status: FAILED (3 attempts). NOT installed to redraw/poses/RW_D0.png. Attempts bracket badly: overshoot-down (398,862), overshoot-up to RISEA (472,763), clone of TUCK (457,826). The ~20-unit TUCK->RISEA x-interval and ~54-unit y-interval leave a very narrow landing band (target 466,800) that the edit model's step granularity keeps jumping over in one direction or the other.

## Summary
1 passed, 2 failed. RK_RISEA PASS — installed at redraw/poses/RK_RISEA.png, measured tip (474,769), bird_sat 54.47. RW_D1 FAILED (tips 558,884 / 610,486 / 556,775; sats 49.19 / 47.52 / 49.13 — all color-pass, all tip-fail; a3 is a clean re-coiled S only 79 low in y). RW_D0 FAILED (tips 398,862 / 472,763 / 457,826; sats 56.31 / 54.79 / 54.29 — all color-pass; overshoot down, overshoot up to the RISEA line, TUCK clone). All attempt files kept in redraw/work/ with the RW_D1_r3_*, RK_RISEA_r3_*, RW_D0_r3_* names above.
