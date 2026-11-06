# RISE results — drawn-heron strike REDRAW (2026-11-05)

Color gate (amended): FAIL only if bird_sat < 42.9 (paler than home) or a blue/grey shift on view. Richer sats pass but are recorded. Home raw bird_sat = 46.9.
Tip gate: within ~25 units (0-1000 normalized) of target on the 2048x1152 PNG.

## RK_RISEA — KEY, t43, target tip (485,779)
Canvas: redraw/poses/RK_TUCK.png (verified, tip (454,823)); far reference: redraw/poses/RK_EXIT.png; home frame attached to every call.

- Attempt 1: FAILED
  - Measured tip: (513, 546) — x +28, y -233 from target (gate ~25)
  - bird_sat: 53.66 — passes amended color gate (richer than home, recorded)
  - View verdict: Clean drawing, body/legs/frill/color/paper and wide faint rings preserved, no blue/grey shift — but head rose fully to an upright alert posture, not one-third out of the tuck.
  - File (not installed): redraw/work/RK_RISEA_a1_2048.png (gen: media-generation-rk-risea-a1-0-fb8e21c1-878c-4dab-bca0-056e9c34b686.png)

- Attempt 2: FAILED
  - Measured tip: (484, 706) — x -1, y -73 from target (gate ~25)
  - bird_sat: 54.60 — passes amended color gate (richer than home, recorded)
  - View verdict: Clean drawing, body/legs/frill/color/paper and wide faint rings preserved, no blue/grey shift — but head still rose too far; tip sits at 70.6% height instead of 77.9%, neck too fully re-coiled for the first-third rise.
  - File (not installed): redraw/work/RK_RISEA_a2_2048.png (gen: media-generation-rk-risea-a2-0-fd4b7595-6b97-40d7-a975-a676f2ea7d8f.png)

- Status: FAILED after 2 attempts. NOT installed to redraw/poses/.

## RK_RISEB — KEY, t44, target tip (524,738)
- Status: NOT ATTEMPTED — stopped per instructions because RK_RISEA failed twice; RISEB must chain from a verified RISEA canvas, which does not exist.

## Summary
0 passed, 1 failed (RK_RISEA, both attempts overshot the rise — tip too high), 1 not attempted (RK_RISEB, blocked). Nothing installed to redraw/poses/.
