# SEGA results — Segment A withdrawal breakdowns RW_A1..RW_A9 (2026-11-05)

Method: anchored edits per WORKER_BRIEF, chained from the VERIFIED key
RK_EXIT (redraw/poses/RK_EXIT.png, measured tip (621,824), bird_sat 49.1).
Each pose = edit of the previous VERIFIED pose in the chain, home frame
attached to every call. No verified downstream key exists (RK_MIDW is
unverified), so the home frame served as the far reference (the re-coil
direction of travel). Every attempt resized to exactly 2048x1152 (LANCZOS)
in redraw/work/gen/ and gated on view + visual-grounding bill tip +
bird_sat. Color gate as amended in CHAIN_SPEC.md: FAIL only if
bird_sat < 42.9 or a blue/grey shift on view. Tip tolerance ~25 units
per the brief's key/breakdown practice.
Candidates kept in redraw/work/gen/ as RW_A<N>_a1/a2/esc_2048.png.

## Anti-clone gate note (applies to the whole segment)
The spec's own tip path wiggles in this segment (EXIT (621,824) measured ->
A1 (600,817) -> A2 (598,823) -> A3 (601,808); A8 (600,715) -> A9 (595,716)),
so the targets themselves are NOT strictly between their neighbours on
both axes (same situation the CHAIN_SPEC documents as an exception at
RW_MIDW). The gate was therefore applied as: tip within ~25 of target,
genuinely distinct from the canvas neighbour, on the target path. Where a
pose failed, the chain continued from the last verified pose and the gap
is noted.

## RW_A1 — target (600,817), t18 — **FAILED** (2 edits + 1 escalation)
- a1 (edit of RK_EXIT): tip (603,789) — dx +3, dy −28, just outside
  tolerance in y; bird_sat 48.4 (PASS). View PASS — droplets still
  falling, tight rings at the strike point, frill whole, legs in home
  stance, no wash. Head simply rose a touch too much.
- a2 (edit of RK_EXIT): tip (609,865) — dx +9, dy +48 FAIL; bird_sat
  51.3. View clean, but the head stayed at exit depth (bill closed).
- esc (fresh full drawing): tip (532,824) — dx −68 FAIL; bird_sat 51.0.
  View FAIL — bird shrank and shifted left, neck in a deep S re-coil,
  stance changed.
- Verdict: FAILED. Gap in the chain between RK_EXIT and RW_A2.

## RW_A2 — target (598,823), t19 — **PASS** (attempt 2, installed)
- Canvas: RK_EXIT (RW_A1 failed; chain continued from last verified).
- a1: tip (544,854) — dx −54, dy +31 FAIL; bird_sat 50.2. View otherwise
  clean (droplets ending, rings spreading); the recoil pulled the head
  too far left.
- a2: tip (618,832) — dx +20, dy +9, within tolerance; bird_sat 50.4.
  View PASS — neck low and extended as at exit, droplets ending (a few
  last drops), rings spreading wider and fainter, frill whole, legs in
  home stance, no filled water/wash.
- Installed: redraw/poses/RW_A2.png (2048x1152).
- Anti-clone: vs EXIT (621,824) and A3 target (601,808), x is between at
  exactly 15% of the interval from the EXIT end; the y interval is
  degenerate at this path wiggle (target y 823 sits 1 unit from EXIT's
  824) and the measured y (832) sits 8 units past the EXIT end —
  documented wiggle exception, as at RW_MIDW.

## RW_A3 — target (601,808), t20 — **FAILED** (2 edits + 1 escalation)
- Canvas: RW_A2.
- a1: tip (561,845) — dx −40, dy +37 FAIL; bird_sat 50.1. View clean
  otherwise (no droplets, rings spreading wide); kink overshot left/down.
- a2: tip (599,770) — dx −2, dy −38 FAIL; bird_sat 51.7. View clean;
  head lifted too far.
- esc (fresh): tip (476,832) — dx −125 FAIL; bird_sat 50.4. View FAIL —
  bird shrank/shifted left, deep S.
- Verdict: FAILED. Gap between RW_A2 and RW_A4.

## RW_A4 — target (603,797), t21 — **FAILED** (2 edits + 1 escalation)
- Canvas: RW_A2 (RW_A3 failed).
- a1: tip (590,747) — dx −13, dy −50 FAIL; bird_sat 50.8. View clean
  (rings spreading clear); lift overshot.
- a2: tip (608,853) — dx +5, dy +56 FAIL; bird_sat 50.9. View clean;
  head stayed at exit depth.
- esc (fresh): tip (503,773) — dx −100 FAIL; bird_sat 50.5. View FAIL —
  feet splayed with toes drawn, stance changed, deep S.
- Verdict: FAILED.

## RW_A5 — target (602,778), t22 — **FAILED** (2 edits + 1 escalation)
- Canvas: RW_A2.
- a1: tip (557,537) — dx −45, dy −241 FAIL; bird_sat 50.0. View FAIL —
  full tall-S re-coil, far beyond the pose.
- a2: tip (617,845) — dx +15, dy +67 FAIL; bird_sat 50.6. View clean
  but the head stayed low.
- esc (fresh): tip (554,516) FAIL; bird_sat 46.8 (passes floor). View
  FAIL — upright raised neck, no strike-point rings at all.
- Verdict: FAILED.

## RW_A6 — target (601,761), t23 — **FAILED** (2 edits + 1 escalation)
- Canvas: RW_A2.
- a1: tip (575,650) — dx −26, dy −111 FAIL; bird_sat 50.0. View clean
  apart from the overshoot (neck kinked into a high S).
- a2: tip (591,672) — dx −10, dy −89 FAIL; bird_sat 50.7. Same failure.
- esc (fresh): tip (585,842) — dx −16, dy +81 FAIL; bird_sat 48.9.
  View clean, but the head sits at exit depth, not lifted.
- Verdict: FAILED.

## RW_A7 — target (601,738), t24 — **FAILED** (2 edits + 1 escalation)
- Canvas: RW_A2.
- a1: tip (586,546) — dx −15, dy −192 FAIL; bird_sat 50.0. Tall S.
- a2: tip (608,893) — dx +7, dy +155 FAIL; bird_sat 51.0. Head driven
  down past the canvas depth, bill nearly touching the rings.
- esc (fresh): tip (556,829) — dx −45, dy +91 FAIL; bird_sat 53.0
  (passes the amended floor; no blue/grey shift on view).
- Verdict: FAILED.

## RW_A8 — target (600,715), t25 — **FAILED** (2 edits + 1 escalation)
- Canvas: RW_A2.
- a1: tip (602,652) — dx +2, dy −63 FAIL; bird_sat 49.6. View clean
  apart from lift overshoot; strike rings read smaller than the
  wide/medium-faint spec.
- a2: tip (583,800) — dx −17, dy +85 FAIL; bird_sat 52.3. Head stayed low.
- esc (fresh): tip (479,694) — dx −121 FAIL; bird_sat 50.8. View FAIL —
  bird shrank and shifted left into an S.
- Verdict: FAILED.

## RW_A9 — target (595,716), t26-27 — **PASS** (attempt 2, installed)
- Canvas: RW_A2 (RW_A8 failed).
- a1: tip (596,785) — dx +1, dy +69 FAIL; bird_sat 50.6. View clean
  (settling S, wide medium-faint rings); head too low.
- a2: tip (587,696) — dx −8, dy −20, within tolerance; bird_sat 51.2.
  View PASS — head near-still and settling, neck softening into the
  re-coil S, wide medium-faint rings at the strike point, frill whole,
  legs in home stance, no droplets, no wash.
- Installed: redraw/poses/RW_A9.png (2048x1152).
- Anti-clone: neighbours are a gap (RW_A8 FAILED) and the unverified
  RW_MIDW; against the spec targets the measured tip is not strictly
  between on either axis (path wiggle A8 (600,715) -> A9 (595,716) ->
  MIDW (596,734)) — documented exception; the pose itself is a genuine
  settling S, not a clone of the canvas (tip moved 31 left / 136 up
  from RW_A2's measured (618,832)).

## Summary
**2 of 9 passed and installed: RW_A2 (tip (618,832), bird_sat 50.4) and
RW_A9 (tip (587,696), bird_sat 51.2).** RW_A1, RW_A3, RW_A4, RW_A5,
RW_A6, RW_A7, RW_A8 FAILED after 2 edits + 1 fresh-draw escalation each.
Systematic finding for the coordinator: from the low, extended EXIT/A2
canvas, the edit model's lift is bimodal — it either holds the head at
exit depth (y 800–893) or jumps to a tall S (y 516–672); the 715–808
target band was landed only twice in 21 attempts. Fresh-draw escalations
systematically shrink/shift the bird left (tip x 476–585) and deepen the
S, so they never rescued a mid-band pose. Color was never the blocker:
every attempt's bird_sat was 46.8–53.0 (all ≥ 42.9) with no blue/grey
shift on view, and view failures were pose/stance only. The installed
chain has gaps at A1 and A3–A8; RW_A9 was chained from RW_A2 across the
gap, as instructed.
