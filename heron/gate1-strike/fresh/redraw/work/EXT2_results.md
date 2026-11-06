# EXT2 results — drawn-heron strike REDRAW, extension segment round 2 (2026-11-05)

Worker EXT2. Method per assignment: HALFWAY EDITS for all poses (canvas +
far reference attached, "move the pose HALFWAY from the first image toward
the second", home frame also attached to every call). Verified neighbour
tips used for gates: HOME (472,848), RK_EMID (670,858), RX_5 (632,883),
RK_PEAK (621,931). Pass required: tip strictly between the measured
neighbours, >=15% of the interval from either end, within ~30 of the stated
target; color gate (bird_sat >= 42.9, no blue/grey shift on view); clean
view (frill whole, legs planted in home stance, whole bird in frame).
Every attempt resized to exactly 2048x1152 (LANCZOS) in redraw/work/gen/
and gated on view + visual-grounding bill tip + bird_sat. All attempts
pass the color number; none showed a blue/grey shift.
Order followed: RX_2, then RX_1 (blocked if RX_2 fails), then RX_4.

## RX_2 (577,814), t11 — canvas HOME raw (K_coil_color_redo.png), far ref RK_EMID — FAILED (ESCALATED, not installed)

Interval HOME (472,848) -> RK_EMID (670,858): x must lie in ~502–640
(>=15% from either end).

- Attempt 1 (halfway edit): tip (774,793), bird_sat 50.40. View clean —
  home register, frill whole, legs planted, feet rings only, head low —
  but the edit ran far PAST the far neighbour (104 units beyond EMID's x).
  FAIL tip / anti-clone. File: work/gen/RX_2_e2_a1_2048.png
- Attempt 2 (halfway edit, stop pinned hard, head low): tip (683,832),
  bird_sat 50.44. View clean, head low on the strike line, feet rings
  only — but x sits 13 units beyond EMID (670), a near-clone of the far
  neighbour, ~106 units from the target. FAIL tip / anti-clone.
  File: work/gen/RX_2_e2_a2_2048.png
- Escalation (fresh full drawing, ref_peak + both neighbour landmarks):
  tip (614,584), bird_sat 48.10. X is between the neighbours but the head
  LIFTED far above the strike line — y is 230 units above the target and
  ~264 above both neighbours' y; the bird is also drawn smaller/shifted.
  FAIL tip + view. File: work/gen/RX_2_e2_esc_2048.png
- NOT installed to redraw/poses/RX_2.png.
- Same round-1 failure family: edits run to/past the far neighbour;
  the fresh drawing lifts the head toward alert.

## RX_1 (537,817), t10 — BLOCKED (not attempted)

- RX_2 was never verified, so per the assignment ("If RX_2 fails, RX_1 is
  blocked") no generation was attempted and nothing was installed. Its
  prescribed far reference, RX_2 (once verified), does not exist.

## RX_4 (RE-DERIVED target (651,871)), t13 — canvas RK_EMID, far ref RX_5 — FAILED (ESCALATED, not installed)

Neighbours RK_EMID (670,858) and RX_5 (632,883); target is their midpoint.
Projection fractions computed along the EMID->RX_5 segment.

- Attempt 1 (halfway edit): tip (643,928), bird_sat 54.51. View clean —
  near-straight spear driving down, frill whole, legs planted, feet rings
  only, bill above water — but the dive overshot RX_5: y 45 units past
  RX_5's y, projection 1.34 (outside the segment), 57.6 units from target.
  FAIL tip. File: work/gen/RX_4_e2_a1_2048.png
- Attempt 2 (halfway edit, head held up at halfway height): tip (629,906),
  bird_sat 54.54. View clean, spear straight, feet rings only — but again
  past RX_5 on both axes (x 3 beyond RX_5, y 23 beyond), projection 1.33,
  41.3 units from target. FAIL tip / anti-clone.
  File: work/gen/RX_4_e2_a2_2048.png
- Escalation (fresh full drawing, ref_peak + both neighbour landmarks):
  tip (678,877), bird_sat 53.23. X 8 units beyond EMID (outside the
  interval on the far side); view also fails — bird drawn larger/shifted
  with a different leg stance (feet flat, toes splayed, not the home
  stance) and a kinked S-neck rather than a straight spear. FAIL tip +
  view. File: work/gen/RX_4_e2_esc_2048.png
- NOT installed to redraw/poses/RX_4.png.

## Summary
**0 of 3 passed. RX_2 FAILED after escalation (best edit tip (683,832),
sat 50.44; escalation tip (614,584), sat 48.10). RX_1 BLOCKED — not
attempted, RX_2 never verified. RX_4 FAILED after escalation (best edit
tip (643,928), sat 54.51; escalation tip (678,877), sat 53.23). Nothing
installed to redraw/poses/.**
Recurring failure mode, same as round 1: halfway edits do not stop at
halfway — on the horizontal unfolding arc they run to/past the far
neighbour (RX_2), and on the short diving arc EMID->RX_5 they overshoot
past RX_5 toward PEAK (RX_4, projections 1.33–1.34 on both edits); the
fresh-drawing escalations break other gates (head lifted to (614,584)
for RX_2; wrong stance/scale and x beyond EMID for RX_4).
