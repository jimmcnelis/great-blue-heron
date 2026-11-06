# KEYS4 Results — Strike Redraw (edit-correction)

Method: EDIT-CORRECTION on the best existing candidates (kept in redraw/work/gen/).
Each attempt = one media.generate_image edit call, FIRST image = the named canvas,
home frame (fresh/home_frame_approval.png) attached as color authority, ONE
correction only, everything else identical. Max 2 attempts per key. Every attempt
measured: view + visual-grounding bill tip + bird_sat on the 2048x1152 resize in
redraw/work/gen/. Install to redraw/poses/<NAME>.png ONLY on a full pass
(tip within ~25 units of target, bird_sat 42.9-50.9, clean view).

## RK_TUCK — target (449,823), t39-41
- Canvas: KEYS3 candidate k3a3 — redraw/work/gen/RK_TUCK_k3a3_2048.png
  (canvas tip (398,840), bird_sat 49.88; tightest fold, wide faint rings, color in
  band; faults: tip 51 too far left, head hangs forward instead of folding back
  to the chest)
- Correction used (both attempts): "Edit this drawing: fold the head further back
  and down toward the chest, so the bill tip moves from about 40% width / 84%
  height to about 45% width / 82% height and the neck's question-mark fold
  tightens against the body. Keep the legs, body, chest frill, color, paper and
  the wide faint ripple rings exactly the same."
- Status: FAILED — nothing installed
- Attempt 1 (RK_TUCK_k4a1_2048.png; raw media-generation-rk-tuck-k4a1-0-15281867-d659-4766-b2cc-bb1c0591f573.png):
  tip (454,823), bird_sat 52.01 — view: legs/body/frill correct, wide faint rings
  plus feet rings preserved, color reads strong; tip essentially exact
  (dx +5, dy 0), BUT bird_sat 52.01 is above the 42.9-50.9 band and the head
  still hangs forward-down in an open S rather than folding back against the
  chest. FAIL on color and pose (tip PASS).
- Attempt 2 (RK_TUCK_k4a2_2048.png; raw media-generation-rk-tuck-k4a2-0-d5aa073d-1f93-4ee1-a914-6d2889ccdbbe.png):
  tip (337,892), bird_sat 48.13 — view: the fold did tighten into a question-mark
  against the body, but it overshot badly — head folded too far back/down, bill
  near-vertical close to the chest, and the wide faint rings were lost (only
  small feet rings remain). FAIL on tip (dx -112, dy +69) and water.
  Color PASS.
- Verdict: FAILED — closest attempt is k4a1: tip (454,823) vs target (449,823),
  bird_sat 52.01 (1.11 over band), pose still forward-hanging. The two attempts
  bracket the problem: a1 nails the tip but not the fold or the saturation;
  a2 achieves the fold but swings the tip 112 left / 69 low and drops the wide rings.

## RK_SETTLE — target (510,836), t57
- Canvas: KEYS2 round-1 attempt 1 — redraw/work/gen/media-generation-rk-settle-a1-0-438ecbde-d697-4f04-8af3-e0b88394c0c4.png
  (canvas tip (473,727), bird_sat 50.75; plausible deep S coil, ghost rings right,
  but head ~109 too high)
- Correction used (both attempts): "Edit this drawing: lower the head
  substantially into a deeper coil - the bill tip moves from about 47% width /
  73% height down to about 51% width / 84% height, ending slightly higher and
  further forward than a full resting coil, pointing down-forward, NOT touching
  the water. Keep the legs, body, chest frill, color, paper and the faint ghost
  ripple rings exactly the same."
- Status: FAILED — nothing installed
- Attempt 1 (RK_SETTLE_k4a1_2048.png; raw media-generation-rk-settle-k4a1-0-0cd5acac-2ec0-41ef-b325-a23c11122022.png):
  tip (431,912), bird_sat 48.15 — view: clean deep S coil, legs/frill correct,
  faint feet rings only, bill not touching the water; but the head overshot
  low and left — tip well below and behind target. FAIL on tip (dx -79, dy +76).
  Color PASS.
- Attempt 2 (RK_SETTLE_k4a2_2048.png; raw media-generation-rk-settle-k4a2-0-22867e73-08f2-40ff-a1b1-45493eb42bed.png):
  tip (403,901), bird_sat 49.33 — view: clean S coil, legs/frill/ghost feet rings
  correct, bill not touching; head again too low and even further left.
  FAIL on tip (dx -107, dy +65). Color PASS.
- Verdict: FAILED — closest attempt is k4a1: tip (431,912) vs target (510,836),
  bird_sat 48.15. Both edits lowered the head as asked but dragged the tip
  left-and-down past the target instead of down-and-forward to it; the
  down-forward component of the correction is not being rendered.

## Summary
0 of 2 keys passed; nothing installed to redraw/poses/ (RK_TUCK.png and
RK_SETTLE.png remain absent). 4 edit attempts generated and measured, all kept
in redraw/work/gen/ as RK_TUCK_k4a1_2048.png, RK_TUCK_k4a2_2048.png,
RK_SETTLE_k4a1_2048.png, RK_SETTLE_k4a2_2048.png (plus their raw media files).
TUCK's tip can be hit exactly by edit (k4a1, 454,823) but that attempt failed
saturation (52.01) and the folded-to-chest pose; SETTLE's edits both overshoot
low-left, closest k4a1 at (431,912), 79 left / 76 low, sat in band.
