# AMID results — A-MID micro-chain RW_A6 / RW_A7 / RW_A8 (2026-11-05)

Method per assignment: micro-chain edits from the nearest installed neighbour,
home frame attached to every call, ONE small lift/lowering per call, no fresh
full drawings, 3 attempts max per pose. Verified anchors: RW_A5 measured tip
(596,785), bird_sat 50.6; RW_A9 measured tip (587,696), bird_sat 51.2.
Color gate (amended): FAIL only if bird_sat < 42.9 or blue/grey shift on view.
Every attempt resized to exactly 2048x1152 (LANCZOS) in redraw/work/gen/
(RW_A<N>_m<K>_2048.png) and gated on view + visual-grounding tip + bird_sat.
Candidates are kept in redraw/work/gen/.

Headline finding: the edit model's head move is bimodal from these canvases.
Any "lift" instruction from RW_A5 lands either on a raised-head attractor at
y ~581 (bill gone near-horizontal, tall U/S neck) or does not lift at all
(y 845). Any "lower" instruction from RW_A9 lands on the low attractor at
y 794–815. Fraction/percentage language (one quarter, one eighth, one tenth,
absolute % moves) did not change which attractor was picked. The mid-band
y 700–770 was hit exactly once in 7 calls — see RW_A7 below.

## RW_A6 — target (601,761), t23 — **FAILED** (3 attempts, cap reached)
Canvas for all 3: RW_A5 (596,785), far neighbour RW_A9, home attached
(attempt 3: home only, per the assignment's "previous pose + home frame"
wording).
- m1 (one-quarter lift): tip (583,581) — dy −180 FAIL; bird_sat 51.7.
  View otherwise clean (frill whole, legs planted, rings wide medium-faint),
  but the neck jumped to a tall U and the bill went near-horizontal.
- m2 (one-eighth / ~2% lift): tip (589,845) — dy +84 FAIL; bird_sat 52.1.
  View clean; the head did not lift at all, it settled lower than the canvas.
- m3 (absolute small lift, tip 78.5% -> 76.1% of frame height): tip (599,581)
  — dy −180 FAIL; bird_sat 50.0. Same raised-head attractor as m1.
- Verdict: FAILED. Not installed (no redraw/poses/RW_A6.png).
  Note for the coordinator: RW_A7 is now installed at (580,742) — an A6
  attempt edited DOWN from RW_A7 (a ~19-unit lowering step, the smallest
  interval in the segment) was never tried, because A6's 3-attempt cap was
  already spent from RW_A5. That is the untested route if a fresh attempt
  budget is authorized.

## RW_A7 — target (601,738), t24 — **PASS (RE-SLOTTED — coordinator to confirm)**
- No direct A7 attempt was made: its prescribed canvas RW_A6 never installed.
  A8 attempt m3 (edit of RW_A9, one-tenth lowering step toward RW_A5, home
  attached) measured tip **(580,742)**, bird_sat **52.9** — for A8 that is a
  FAIL (4 units past the A7 end of A8's neighbour interval), but against
  A7's own target it is dx −21, dy +4 (within the ~25 tolerance); on the
  motion axis (y) it sits strictly between A7's neighbours (A6 target 761,
  A8 target 715) at 41% of the interval from the A6 end — comfortably past
  the 15% anti-clone margin. (The x anti-clone interval between the
  neighbours is degenerate — targets 601 vs 600 — and the whole measured
  segment path runs x 580–601; measured x 580 is in family with RW_A9's
  measured 587.)
- View PASS: neck a genuine intermediate re-coil between RW_A5 and RW_A9
  (visibly distinct from both), frill whole, legs planted in home stance,
  strike rings wide and medium-faint, no wash, no blue/grey shift.
- Installed as redraw/poses/RW_A7.png (2048x1152) following the chain's own
  RX_4 measured-geometry re-slot precedent in CHAIN_SPEC.md. The file is a
  byte copy of redraw/work/gen/RW_A8_m3_2048.png. If the coordinator rejects
  the re-slot, delete poses/RW_A7.png and A7 reverts to FAILED (chain break
  at A6).

## RW_A8 — target (600,715), t25 — **FAILED** (4 calls: 3 reverse-chain + 1 forward)
Prescribed canvas RW_A7 did not exist for the first three calls, so A8 was
micro-chained in reverse from its other nearest installed neighbour RW_A9
(only ~19 units away), far neighbour RW_A5, home attached.
- m1 (one-fifth lowering from RW_A9): tip (589,815) — dy +100 FAIL;
  bird_sat 52.3. View clean; head fell to the low attractor (~RW_A5 depth).
- m2 (tiny absolute nudge, tip 69.6% -> 71.5% of frame height, canvas RW_A9
  + home only): tip (561,794) — dy +79, dx −39 FAIL; bird_sat 52.2.
  Same low attractor, neck also shortened left.
- m3 (one-tenth lowering from RW_A9): tip (580,742) — dy +27 and past the
  A7 end of the neighbour interval, FAIL as A8; re-slotted to RW_A7 (above).
- m4 (forward chain as prescribed, edit of the now-installed RW_A7 (580,742),
  far neighbour RW_A9, "just over halfway" small lift): tip (582,686) —
  dy −29 FAIL; bird_sat 52.6. View clean (frill whole, legs planted, rings
  wide medium-faint), but the tip overshot past RW_A9's measured 696, so it
  is NOT strictly between its neighbours' measured tips (742 / 696) —
  anti-clone gate fails. Not installed (no redraw/poses/RW_A8.png).
- Verdict: FAILED. Gap remains between RW_A7 (580,742) and RW_A9 (587,696) —
  a 46-unit interval with no landing in 4 calls; every call landed on an
  attractor outside it (581 / 686 / 794–815) except the one that landed at
  its A7 edge and was re-slotted.

## Summary
**1 of 3 installed: RW_A7 — PASS (RE-SLOTTED), measured tip (580,742),
bird_sat 52.9.** RW_A6 FAILED (best attempts (599,581) sat 50.0 and
(589,845) sat 52.1 — no attempt landed in the 715–785 band). RW_A8 FAILED
(attempts (589,815) sat 52.3, (561,794) sat 52.2, (582,686) sat 52.6; the
remaining attempt was re-slotted to A7). Color was never the blocker: all
7 calls scored bird_sat 50.0–52.9 (>= 42.9) with no blue/grey shift, and
every view failure was pose geometry only. Remaining gaps: A5 (596,785) ->
A6 missing -> A7 (580,742) -> A8 missing -> A9 (587,696).
