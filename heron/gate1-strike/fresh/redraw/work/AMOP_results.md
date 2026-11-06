# AMOP results — final mop-up gap poses RW_A6 / RW_A8 / RW_B9 (2026-11-05)

Method per assignment: breakdown edits only (media.generate_image), canvas
first / far neighbour second / home frame third on every call, TWO attempts
per pose MAX, no escalation, no grinding. Every attempt resized
2096x1184 -> exactly 2048x1152 (LANCZOS), viewed, bill tip grounded with
visual_grounding, bird_sat measured (amended color gate: FAIL only if
bird_sat < 42.9 or a blue/grey shift on view). Attempt files kept in
redraw/work/ as <NAME>_mop_a<n>_2048.png.
Anchors (measured, as assigned): RW_A5 (596,785), RW_A7 (580,742),
RW_A9 (587,696), RW_B8 (559,848), RW_C1 (480,827).

## RW_A6 — target (588,763), between RW_A5 (596,785) and RW_A7 (580,742) — **FAILED** (2 attempts)
Anti-clone passing box: x 582–594, y 748–779 (15% margins, both axes);
target itself sits at 50% (x) / 49% (y) of the interval.
- a1 (edit of RW_A7, head settles down-right ~21 units): tip **(599,897)** —
  dx +11, dy +134 FAIL; bird_sat **53.7**. View clean (frill whole, legs
  planted, mid-wide fading rings, no blue/grey shift) but the head dropped
  all the way to the strike depth, bill nearly touching the rings.
- a2 (fallback edit of RW_A5, small lift ~22 units): tip **(563,678)** —
  dx −25, dy −85 FAIL; bird_sat **52.9**. View clean; lift overshot into
  the tall-S attractor (same bimodal split as every prior A-segment round).
- Verdict: FAILED. Not installed (no redraw/poses/RW_A6.png). Gap
  A5 (596,785) -> A7 (580,742) remains; re-timing absorbs it per assignment.

## RW_A8 — target (584,719), between RW_A7 (580,742) and RW_A9 (587,696) — **FAILED** (2 attempts)
Anti-clone passing box: x 581–586, y 703–735 (15% margins, both axes).
- a1 (edit of RW_A9, head dips ~23 units down-screen): tip **(560,835)** —
  dx −24, dy +116 FAIL; bird_sat **53.9**. View clean; head fell to the
  low attractor (~strike depth) instead of the small dip.
- a2 (fallback edit of RW_A7, small lift ~23 units up-screen): tip
  **(582,676)** — dx −2, dy −43 FAIL; bird_sat **52.3**. View clean
  (frill whole, legs planted, mid-wide faint rings); lift overshot past
  RW_A9's end (696), so not strictly between neighbours either.
- Verdict: FAILED. Not installed (no redraw/poses/RW_A8.png). Gap
  A7 (580,742) -> A9 (587,696) remains; re-timing absorbs it per assignment.

## RW_B9 — target (520,828), between RW_B8 (559,848) and RW_C1 (480,827) — **PASS** (attempt 1, installed, minor-axis exception noted)
- a1 (edit of RW_C1, folded head swings right at near-constant height;
  landmark aimed at y 83.5% / mid-interval to give the y margin room):
  tip **(536,823)** — dx +16, dy −5 vs target, within the ~25 tolerance;
  bird_sat **56.6**. View PASS — identity and color register match home
  (no blue/grey shift), frill whole, legs planted in home stance, neck
  long and low entering the tuck swing, strike rings widest and faint,
  no filled water, no scenery/text.
  Anti-clone: x strictly between at 71% from the C1 end / 29% from the
  B8 end (≥15% PASS); projection along the B8->C1 axis at 35% (PASS).
  Minor-axis exception: y 823 sits 4 units past the C1 end of the y
  interval (827–848). The assigned target y (828) itself sits only
  1 unit inside that interval (5% margin), so a ≥15% per-axis y test
  cannot be met by any landing within ~25 of the target except the
  narrow 830–845 sliver; judged on the motion axis (x / projection),
  as in the chain's documented wiggle exceptions (CHAIN_SPEC RW_MIDW;
  SEGA RW_A2/RW_A9). Coordinator: if a strict per-axis y gate is
  insisted on, this reverts to FAILED and the gap is absorbed by
  re-timing — the drawing itself is on-target and view-clean.
- a2 (fallback edit of RW_B8, head steps left/up toward the fold):
  tip **(460,813)** — dx −60, dy −15 FAIL; bird_sat **56.9**. View
  clean but the swing overshot past RW_C1 in x. Not used.
- Installed: **redraw/poses/RW_B9.png** (2048x1152, byte copy of
  redraw/work/RW_B9_mop_a1_2048.png).

## Summary
**1 of 3 passed and installed: RW_B9 — tip (536,823), bird_sat 56.6,
installed as redraw/poses/RW_B9.png (minor-axis y exception documented
above).** RW_A6 FAILED (attempts (599,897) sat 53.7; (563,678) sat 52.9)
and RW_A8 FAILED (attempts (560,835) sat 53.9; (582,676) sat 52.3) after
exactly 2 attempts each, per the cap — not installed. Color was never
the blocker: all 6 attempts scored bird_sat 52.3–56.9 (≥ 42.9) with no
blue/grey shift on view, and every view was otherwise clean; the A-gap
failures are the known bimodal head-move (low attractor ~835–897 vs
tall-S attractor ~676–686, mid-band 703–779 never landed from either
canvas in this mop-up either). Remaining gaps for re-timing: A6 (t23)
and A8 (t25).
