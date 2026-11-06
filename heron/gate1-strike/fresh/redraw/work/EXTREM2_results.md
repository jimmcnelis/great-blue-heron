# EXTREM2 results — strike launch RX_1, RX_2 via SMALL-FRACTION edits of the coil (2026-11-05)

Worker EXTREM2. Method per assignment: canvas = HOME raw artwork
(fresh/K_coil_color_redo.png) for BOTH poses, far reference = RK_PEAK
(redraw/poses/RK_PEAK.png), home frame attached to every call as
color/identity authority (image order: canvas, far reference,
home_frame_approval.png). Fractions stated against the FULL coil-to-peak
span. Every attempt resized to exactly 2048x1152 (LANCZOS) in
redraw/work/gen/ and gated on view + visual-grounding bill tip + bird_sat.
Color gate as amended in CHAIN_SPEC.md: FAIL if bird_sat < 42.9 or a
blue/grey shift on view. All four attempts pass the sat number; none
showed a blue/grey shift on view.

Verified neighbour tips (per assignment):
- HOME (472,848) — raw canvas fresh/K_coil_color_redo.png
- RK_PEAK (621,931) — redraw/poses/RK_PEAK.png (far reference)
- RK_EMID (670,858) — redraw/poses/RK_EMID.png (upper gate bound)

Gate applied per assignment: view (frill whole, legs planted in home
stance, whole bird in frame at the home scale), tip strictly between
HOME (472,848) and RK_EMID (670,858) and within ~30 of target,
bird_sat >= 42.9, no blue/grey shift.

## RX_1 (537,817), t10 — FAILED (not installed)

- Attempt 1 (ONE SIXTH of the way coil -> spear; tip stated 54%/82%):
  tip (584,893), bird_sat 50.08. View clean — home register, frill
  whole, legs planted in home stance, whole bird in frame at home
  scale, feet rings only, bill above water, no droplets, no blue/grey
  shift. But the head DIVED: y 893 is 76 units below target y (817)
  and below BOTH neighbours (848/858), toward the PEAK y (931);
  distance from target 89.4 units. FAIL tip (overshoot toward spear
  in y).
  File: work/gen/RX_1_e2_a1_2048.png
- Attempt 2 (smaller fraction per overshoot rule: ONE EIGHTH; tip
  stated 54%/82%, head kept high, not diving): tip (613,850),
  bird_sat 52.44. View FAIL on water: extra touch rings drawn under
  the bill tip (assignment requires feet rings only). Tip also fails:
  x 613 is 76 units past target x (537), distance from target 82.9
  units — the neck ran out to a near-spear despite the smaller stated
  fraction. FAIL view + tip.
  File: work/gen/RX_1_e2_a2_2048.png
- NOT installed to redraw/poses/RX_1.png.

## RX_2 (577,814), t11 — FAILED (not installed)

- Attempt 1 (ONE THIRD of the way coil -> spear; tip stated 58%/81%):
  tip (669,927), bird_sat 52.00. View clean on the listed items
  (frill whole, legs planted, whole bird in frame, feet rings only,
  bill above water, no blue/grey shift) — but the pose is the full
  spear itself: tip lands essentially on RK_PEAK (621,931), 145.7
  units from target, head driven down to y 927. FAIL tip (massive
  overshoot toward spear).
  File: work/gen/RX_2_e2x_a1_2048.png
- Attempt 2 (smaller fraction per overshoot rule: ONE QUARTER; tip
  stated 58%/81%, neck kept mostly coiled, head high and level):
  tip (693,739), bird_sat 51.58. View clean on the listed items
  (frill whole, legs planted, whole bird in frame at home scale,
  feet rings only, bill above water, no blue/grey shift) — but the
  tip overshot in BOTH axes the other way: x 693 is PAST RK_EMID
  (670), so it is not strictly between HOME and RK_EMID at all, and
  y 739 is 75 units ABOVE target (814), above both neighbours; the
  neck stretched long and horizontal. Distance from target 138.1
  units. FAIL tip.
  File: work/gen/RX_2_e2x_a2_2048.png
- NOT installed to redraw/poses/RX_2.png.

## Summary
**0 of 2 passed. RX_1 FAILED (a1 tip (584,893), sat 50.08 — head dived
76 below target; a2 tip (613,850), sat 52.44 — forbidden touch rings +
82.9 from target). RX_2 FAILED (a1 tip (669,927), sat 52.00 — full
spear at the peak, 145.7 from target; a2 tip (693,739), sat 51.58 —
past RK_EMID in x, 138.1 from target). Nothing installed.**
Failure mode in the coil-forward direction is the mirror of EXTREM's
re-coil failure: the model will not hold a small intermediate neck
extension from the coil canvas — attempt 1 dives or spears fully,
and the smaller-fraction retry trades the dive for either extra
touch rings (RX_1) or a long horizontal stretch past EMID (RX_2).
Color was never the problem (all sats 50.08-52.44, no blue/grey
shift); geometry/water discipline was. A further attempt needs a
fresh coordinator ruling.
