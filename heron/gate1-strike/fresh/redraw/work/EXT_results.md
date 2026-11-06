# EXT results — extension breakdowns RX_1, RX_2, RX_4, RX_5 (2026-11-05)

Method: anchored edits per WORKER_BRIEF.md (canvas = nearer verified drawing,
far neighbour as target reference, home frame attached to every call).
Every attempt resized to exactly 2048x1152 (LANCZOS) in redraw/work/gen/ and
gated on view + visual-grounding bill tip + bird_sat.
Color gate as amended in CHAIN_SPEC.md: FAIL if bird_sat < 42.9 or a
blue/grey shift on view (all attempts below pass the number; none showed a
blue/grey shift).

Measured neighbour tips used for the anti-clone gate (per assignment, NOT the
nominal spec targets):
- HOME (472,848) — canvas for RX_1 = fresh/K_coil_color_redo.png
- RK_EMID (670,858) — redraw/poses/RK_EMID.png
- RK_PEAK (621,931) — redraw/poses/RK_PEAK.png

Gate note: RX_1/RX_2 nominal targets (537,817) / (577,814) sit ABOVE both
neighbour tips in y (the unfolding arc in the measured v1 path), so for those
poses the anti-clone check is read by x-fraction / projection along the
HOME→EMID interval. For RX_5 the assignment explicitly required the tip
strictly between the MEASURED EMID and PEAK tips, which the nominal
(614,957) is not (it overshoots measured PEAK (621,931) on both axes), so
RX_5 was aimed at an adjusted between-point (638,912) and RX_4 at the
halfway point between EMID and RX_5's MEASURED tip.

## RX_1 (537,817), t10 — canvas HOME raw, far ref RK_EMID — FAILED (ESCALATED, not installed)

- Attempt 1 (edit): tip (546,688), bird_sat 47.20. View clean (home register,
  frill intact, home legs, feet rings only) but the head lifted far too high —
  tip 129 units above the nominal y. FAIL on tip.
  File: work/gen/RX_1_a1_2048.png
- Attempt 2 (edit, head pinned low): tip (671,851), bird_sat 50.50. View clean
  but the edit ran all the way to RK_EMID — a near-clone of the far neighbour
  (7 units from (670,858)), far past the nominal target. FAIL anti-clone/tip.
  File: work/gen/RX_1_a2_2048.png
- Escalation (fresh full drawing, ref_coil + both neighbour landmarks):
  tip (547,901), bird_sat 53.94. X is one-third of the way HOME→EMID (37.9%)
  and the projection fraction passes (0.39), but y overshoots BOTH neighbours
  (848/858) by ~45–53 units and is 84 units below the nominal y; the fresh
  drawing is also drawn smaller/shifted with stray faint rings away from the
  feet. Not a full pass. FAIL.
  File: work/gen/RX_1_esc_2048.png
- NOT installed to redraw/poses/RX_1.png.

## RX_2 (577,814), t11 — canvas RX_1 (once verified), far ref RK_EMID — FAILED / BLOCKED (not attempted)

- RX_1 was never verified (see above), so the prescribed canvas does not
  exist. Per the assignment ("canvas RX_1 (once verified)") no generation
  was attempted and nothing was installed. This pose is unblocked the moment
  a verified RX_1 lands; its gate would be: tip between RX_1-verified and
  RK_EMID (670,858), >=15% of the interval from either end, nominal (577,814).

## RX_5 (nominal 614,957; aimed (638,912) between measured neighbours), t14 — PASS, installed

Canvas RK_PEAK, far ref RK_EMID. Drawn BEFORE RX_4 per the assignment.
Requirement: tip strictly between RK_EMID (670,858) and RK_PEAK (621,931),
spear nearly straight, bill tip just above the water, NO touch rings, no
droplets, feet rings only.

- Attempt 1 (edit): tip (632,883), bird_sat 51.52. PASS on every gate:
  - x strictly between 621–670: 77.6% of the way EMID→PEAK (>=15% from
    either end; 11 units clear of PEAK's x vs the 7.4-unit minimum).
  - y strictly between 858–931: 34.2% of the way EMID→PEAK.
  - Projection fraction along EMID→PEAK = 0.48.
  - View: clean — full home color register, frill intact, home leg stance,
    neck a nearly straight spear, touch rings from the PEAK canvas fully
    removed, no rings/droplets at the bill, feet rings only, no scenery/text,
    whole bird in frame.
  File: work/gen/RX_5_a1_2048.png
- Installed to redraw/poses/RX_5.png (2048x1152, verified).

## RX_4 (halfway between RK_EMID and RX_5), t13 — FAILED (ESCALATED, not installed)

Canvas RX_5 (verified, measured (632,883)), far ref RK_EMID (670,858).
Halfway target computed from the MEASURED neighbours: (651,871).

- Attempt 1 (edit): tip (656,733), bird_sat 51.61. View clean, feet rings
  only, but the head rose far above both neighbours (858/883) — projection
  along EMID→RX_5 is negative (outside the segment). FAIL on tip.
  File: work/gen/RX_4_a1_2048.png
- Attempt 2 (edit, head pinned low): tip (633,911), bird_sat 53.49. View
  clean, spear straight, but x is a near-clone of RX_5 (1 unit from its x,
  inside the 15% margin) and y overshoots past RX_5 toward PEAK —
  projection 1.32, outside the segment. FAIL anti-clone/tip.
  File: work/gen/RX_4_a2_2048.png
- Escalation (fresh full drawing, ref_peak + both neighbour landmarks):
  tip (571,816), bird_sat 56.28. Drawn smaller/shifted, neck a coiled S
  rather than a spear, tip outside both neighbours on both axes. FAIL.
  File: work/gen/RX_4_esc_2048.png
- NOT installed to redraw/poses/RX_4.png.

## Summary
**1 of 4 passed: RX_5 PASS (tip (632,883), bird_sat 51.52, installed).
RX_1 FAILED after escalation (best tip (547,901), sat 53.94). RX_4 FAILED
after escalation (escalation tip (571,816), sat 56.28). RX_2 BLOCKED —
not attempted, its prescribed canvas RX_1 was never verified.**
Recurring failure mode in this segment: edits either lift the head far
above the low strike line (RX_1 a1, RX_4 a1) or run the full distance to
the far neighbour (RX_1 a2, RX_4 a2); the "stop at a fraction, head low"
instruction did not hold in either edit direction.
