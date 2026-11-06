# EXTREM results — extension poses RX_2, RX_1 built in the RE-COIL direction (2026-11-05)

Worker EXTREM. Method per assignment: RE-COIL edits (canvas = the more
extended verified pose, far reference = the home raw artwork), home frame
attached to every call as color/identity authority (image order: canvas,
far reference, home_frame_approval.png). NO fresh full drawings.
Every attempt resized to exactly 2048x1152 (LANCZOS) in redraw/work/gen/
and gated on view + visual-grounding bill tip + bird_sat.
Color gate as amended in CHAIN_SPEC.md: FAIL if bird_sat < 42.9 or a
blue/grey shift on view (both attempts pass the number; neither showed a
blue/grey shift).

Verified neighbour tips (measured, per assignment):
- HOME (472,848) — raw canvas fresh/K_coil_color_redo.png
- RK_EMID (670,858) — redraw/poses/RK_EMID.png

Gate note (carried from EXT_results.md): the RX_1/RX_2 nominal targets
(537,817) / (577,814) sit ABOVE both neighbour tips in y (the unfolding
arc in the measured v1 path), so the anti-clone check is read by
x-fraction / projection along the HOME->EMID interval; a pass must still
land near the nominal target (prior rounds used ~25-30 units) and the
head must stay low WITHOUT diving.

## RX_2 (577,814), t11 — canvas RK_EMID, far ref HOME raw — FAILED (not installed)

Interval HOME (472,848) -> RK_EMID (670,858): x must lie in ~502-640
(>=15% from either end).

- Attempt 1 (re-coil HALFWAY back toward the home coil; tip stated
  67%/86% -> 58%/81%): tip (431,895), bird_sat 50.78. View clean — home
  register, frill whole, legs planted in home stance, whole bird in
  frame, feet rings only, bill above water. But the edit over-re-coiled
  PAST HOME in x (431 < 472, outside the interval on the home side) and
  the head dropped to y 895, bill pointing nearly straight down —
  167 units from target. FAIL tip.
  File: work/gen/RX_2_extrem_a1_2048.png
- Attempt 2 (same target, smaller move stressed, bill kept diagonal
  down-right like EMID, "do NOT fully re-coil"): tip (615,906),
  bird_sat 51.01. View clean on all listed items (frill whole, legs
  planted, whole bird in frame, feet rings only, no blue/grey shift);
  x-fraction passes — 72.2% of the way HOME->EMID, 27.8% clear of the
  EMID end, projection along HOME->EMID = 0.74. But the head DIVED:
  y 906 is 92 units past the target y (814) and below BOTH neighbours
  (848/858); total distance from target 99.5 units. The pose reads as a
  downward dive, which the assignment explicitly excluded ("does NOT
  dive"). FAIL tip / pose.
  File: work/gen/RX_2_extrem_a2_2048.png
- Retry NOT taken: the assignment allows ONE retry with a smaller
  stated fraction only if BOTH attempts overshoot toward EMID.
  Attempt 1 overshot toward/past HOME (x 431) and attempt 2 dived
  below the strike line (y 906) — the stated condition is not met, so
  no third attempt was made.
- NOT installed to redraw/poses/RX_2.png.

## RX_1 (537,817), t10 — canvas RX_2 (once installed), far ref HOME raw — BLOCKED (not attempted)

- RX_2 was never verified/installed, so the prescribed canvas does not
  exist. Per the assignment ("edit of RX_2 (once installed)") no
  generation was attempted and nothing was installed.

## Summary
**0 of 2 passed. RX_2 FAILED after 2 attempts (a1 tip (431,895),
sat 50.78 — over-re-coiled past HOME; a2 tip (615,906), sat 51.01 —
x-fraction good but head dived 92 units past target y). RX_1 BLOCKED —
not attempted, RX_2 never verified.**
Failure mode in the re-coil direction: the fraction problem is now in
Y, not X — attempt 1 collapsed the neck fully into the coil with the
bill vertical, and attempt 2 held the horizontal position but let the
head sink far below the low strike line toward the water. Neither
attempt held "low and forward, halfway, bill diagonal" in both axes
at once. A further attempt would need a fresh coordinator ruling (the
both-overshoot-toward-EMID retry condition was not met here).
