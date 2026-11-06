# KEYS2 FIX Results — Strike Redraw (edit-correction round)

Method: each fix = one media.generate_image EDIT call, FIRST image = named canvas,
home frame attached as color authority, ONE specific correction, rest held identical.
Max 2 attempts per key. Gates: view pass, bill tip within ~25 units of target
(0-1000 coords), bird_sat 42.9-50.9 on the 2048x1152 candidate.
Round-1 failed poses were moved to redraw/work/rejected/ before starting.

## RK_SETTLE — target (510,836), t57
- Status: FAILED
- Canvas: fresh/K_coil_color_redo.png (home raw artwork)
- Attempt 1 (work/gen/RK_SETTLE_fix_a1_2048.png): tip (461,656), bird_sat 47.24 —
  view: color/frill/legs fine and faint wide ghost rings present near 60% width,
  but the edit lifted the head into an upright S, far above the deep coil;
  FAIL on tip (dx -49, dy -180)
- Attempt 2 (work/gen/RK_SETTLE_fix_a2_2048.png): tip (438,801), bird_sat 48.40 —
  view: head stayed low in a deep coil, but the bill points steeply down and the
  tip sits far left of target; the wide ghost rings near 60% width did not appear
  (feet rings only); FAIL on tip (dx -72, dy -35) and water
- Verdict: FAILED — color passed both times; a1 overshot the raise, a2 kept the
  head low but swung the tip left/down. The small forward shift (47%->51% width)
  was never achieved.

## RK_TUCK — target (449,823), t39-41
- Status: FAILED
- Canvas: round-1 attempt 1 (work/gen/media-generation-rk-tuck-a1-0-09c2a153-....png;
  pose correct, tip (430,847), bird_sat 56.50)
- Attempt 1 (work/gen/RK_TUCK_fix_a1_2048.png): tip (429,845), bird_sat 56.43 —
  view: deep tuck pose/composition preserved exactly, frill/legs/wide faint rings
  intact; FAIL on color only — the desaturation barely registered (56.50 -> 56.43)
- Attempt 2 (work/gen/RK_TUCK_fix_a2_2048.png): tip (428,851), bird_sat 34.71 —
  view: pose still preserved, but color overshot pale/washed (bill lost its warm
  orange, body reads grey); FAIL on color (below band) and tip dy +28
- Verdict: FAILED — pose and tip were right in both attempts; the two color edits
  bracket the band (56.4 high, 34.7 low) without landing in 42.9-50.9. The editor
  cannot dose desaturation finely enough via prompt wording alone.

## RK_RISEA — target (485,779), t43
- Status: FAILED (BLOCKED — no valid canvas)
- Attempts: 0
- Assigned canvas was the FIXED redraw/poses/RK_TUCK.png; RK_TUCK failed both fix
  attempts and was never installed, so no verified canvas exists. Editing from the
  failed vivid TUCK or a rejected round-1 pose would violate the fix method
  (install only on pass; unverified drawings are not valid inputs). Not attempted.

## RK_RISEB — target (524,738), t44
- Status: FAILED (BLOCKED — no valid canvas)
- Attempts: 0
- Assigned canvas was the FIXED redraw/poses/RK_RISEA.png, which depends on the
  fixed RK_TUCK; the chain broke at RK_TUCK. Not attempted.

## Summary
0 of 4 keys fixed/installed. RK_SETTLE failed on tip placement in both directions;
RK_TUCK failed on color dosing alone (pose/tip correct both times — it is one
calibrated desaturation step away); RK_RISEA and RK_RISEB are blocked behind the
unfixed RK_TUCK. Nothing was installed to redraw/poses/ in this round.
Candidates retained in redraw/work/gen/ (RK_SETTLE_fix_a1/a2_2048.png,
RK_TUCK_fix_a1/a2_2048.png).
