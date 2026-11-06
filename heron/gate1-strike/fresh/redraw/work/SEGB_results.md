# SEGB results — B-segment strike redraw (RK_MIDW, RW_B1, RW_B3–RW_B9, RW_C1) (2026-11-05)

Method: MICRO-CHAIN per assignment — each pose an edit of the immediately
preceding INSTALLED pose (canvas first, far neighbour second, home frame
third on every call). No fresh full drawings used in this segment. Up to
3 attempts per pose (task rule: fail twice → one retry with smaller-step
fraction language), then FAILED and chain continued from last installed
pose. Gates: view (frill whole, legs planted in home stance, no filled
water, no blue/grey shift), measured bill tip within ~25 units of target
(brief tolerance), bird_sat ≥ 42.9 (amended color gate). All candidates
kept in redraw/work/gen/ as <NAME>_b_a<N>_2048.png, resized 2048x1152
LANCZOS before measuring. Anchors as given: RW_A9 (587,696),
RW_B2 (591,672), RK_TUCK (454,823).

## RK_MIDW — target (596,734), t28 — **FAILED** (3 attempts)
- Canvas: RW_A9.
- a1: tip (579,814) — dy +80 FAIL; sat 52.8. View clean (deepened S,
  wide medium-faint rings); head dipped far too much.
- a2 (smaller-step wording): tip (598,856) — dy +122 FAIL; sat 52.5.
  View clean; dip overshot further.
- a3 (edit of a1 upward, target lies between A9 and a1): tip (584,648)
  — dy −86 FAIL; sat 54.1. View clean; rise overshot.
- Verdict: FAILED. poses/RK_MIDW.png NOT overwritten — it still holds
  the old failed file (timestamp 19:54, untouched).

## RW_B1 — target (600,703), t29 — **PASS** (attempt 2, installed)
- Canvas: RW_A9 (RK_MIDW failed; chain continued from last installed).
- a1: tip (588,647) — dy −56 FAIL; sat 51.3. Rise overshot.
- a2: tip (587,706) — dx −13, dy +3, within tolerance; sat 52.1.
  View PASS — frill whole, legs in home stance, wide medium-faint
  rings, no filled water. Neck shape visibly distinct from RW_A9
  (tighter upper S, steeper bill) — the A9→B1 target interval is a
  documented path wiggle (MIDW (596,734) → B1 (600,703) → B2 (591,672)),
  so the small-interval rule (visible neck change, not a clone) was
  applied instead of strict-between.
- a3 (tried to shift tip right for a cleaner margin): tip (608,548)
  FAIL — rose into a raised S, rings ballooned. a2 installed.
- Installed: redraw/poses/RW_B1.png (2048x1152).

## RW_B3 — target (596,719), t31 — **PASS** (attempt 2, installed)
- Canvas: RW_B2 (591,672).
- a1: tip (572,845) — dy +126 FAIL; sat 52.7. Descent overshot, rings
  enlarged.
- a2 (quarter-step wording, rings held at canvas size): tip (574,739)
  — dx −22, dy +20, within tolerance; sat 52.4. View PASS — head
  turned down into the re-coil dip, neck S visibly deepened vs B2,
  frill whole, legs planted, rings wide medium-faint at canvas size.
- Installed: redraw/poses/RW_B3.png (2048x1152).

## RW_B4 — target (587,766), t32 — **FAILED** (3 attempts)
- Canvas: RW_B3 (574,739).
- a1: tip (589,879) — dy +113 FAIL; sat 53.6.
- a2 (edit of a1 upward): tip (567,572) — dy −194 FAIL; sat 53.2.
- a3 (bill-tilt only, head kept in place): tip (577,869) — dy +103
  FAIL; sat 53.7.
- All views clean; the 739→766 band was jumped over in both directions
  every time (landings 879 / 572 / 869). FAILED.

## RW_B5 — target (579,775), t33 — **PASS** (attempt 2, installed)
- Canvas: RW_B3 (RW_B4 failed).
- a1: tip (570,832) — dy +57 FAIL; sat 53.7; rings also shrank.
- a2 (one-eighth-bill-length wording, rings held): tip (562,779) —
  dx −17, dy +4, within tolerance; sat 53.1. View PASS — deeper U in
  the neck vs B3, frill whole, legs planted, rings wide medium-faint.
- Installed: redraw/poses/RW_B5.png (2048x1152).

## RW_B6 — target (571,784), t34 — **PASS** (attempt 1, installed)
- Canvas: RW_B5 (562,779).
- a1: tip (567,798) — dx −4, dy +14, within tolerance; sat 55.0.
  View PASS — rings now widest and faint as specified, frill whole,
  legs planted, no filled water; tip moved +19 in y from B5 with a
  slightly relaxed S (small-interval neck/water change, not a clone).
- Installed: redraw/poses/RW_B6.png (2048x1152).

## RW_B7 — target (562,807), t35 — **FAILED** (3 attempts)
- Canvas: RW_B6 (567,798).
- a1: tip (480,827) — dx −82 FAIL for B7; sat 55.7. View clean, neck
  folded toward the tuck. NOTE FOR COORDINATOR: this candidate landed
  essentially ON the RW_C1 target (485,826) — file
  work/gen/RW_B7_b_a1_2048.png. A re-slot (RX_4 precedent) could fill
  C1, but C1's assigned canvas was RW_B9, so it was NOT installed as
  C1 by this worker.
- a2 (no-swing wording, TUCK far ref): tip (470,783) — dx −92 FAIL;
  sat 55.8. Folded left again.
- a3 (far ref switched to RW_B5 to anchor x): tip (556,852) — dy +45
  FAIL; sat 55.4. x landed, y dropped past.
- Verdict: FAILED.

## RW_B8 — target (554,830), t36 — **PASS** (attempt 1, installed)
- Canvas: RW_B6 (RW_B7 failed).
- a1: tip (559,848) — dx +5, dy +18, within tolerance; sat 56.2.
  View PASS — frill whole, legs planted, rings widest/faint, no
  filled water; head settled lower-left from B6, neck long and low.
- Installed: redraw/poses/RW_B8.png (2048x1152).

## RW_B9 — target (520,828), t37 — **FAILED** (3 attempts)
- Canvas: RW_B8 (559,848).
- a1: tip (514,908) — dy +80 FAIL; sat 58.3. x landed (−6) but the
  bill went vertical down to the rings; rings shrank under the tip.
- a2 (swing left at constant height): tip (539,769) — dy −59 FAIL;
  sat 57.8. Neck raised into an S instead.
- a3 (edit of a1 upward): tip (563,758) — dx +43, dy −70 FAIL;
  sat 57.8.
- Verdict: FAILED. The leftward swing at constant height was never
  landed — attempts split between dropping to ~908 and rising to
  ~760.

## RW_C1 — target (485,826), t38 — **FAILED** (3 attempts)
- Canvas: RW_B8 (RW_B9 failed); far reference RK_TUCK (454,823).
- a1: tip (521,662) — dy −164 FAIL; sat 58.0. Swung up into a tight S.
- a2 (flat low arc, neck stays long): tip (478,779) — dx −7, dy −47
  FAIL; sat 58.2. Closest attempt; x on target, y 47 high.
- a3 (edit of a2 downward): tip (488,893) — dy +67 FAIL; sat 58.4.
  x perfect (+3), y overshot down.
- Verdict: FAILED. See the RW_B7 a1 note above — a clean candidate at
  (480,827), sat 55.7, already exists in work/gen/ if the coordinator
  wants the re-slot option.

## Summary
**5 of 10 passed and installed: RW_B1 (587,706) sat 52.1, RW_B3
(574,739) sat 52.4, RW_B5 (562,779) sat 53.1, RW_B6 (567,798) sat 55.0,
RW_B8 (559,848) sat 56.2.** FAILED: RK_MIDW, RW_B4, RW_B7, RW_B9,
RW_C1 (3 attempts each, all views clean, all sats ≥ 52.5 — color was
never the blocker; no blue/grey shift seen in any attempt).
Chain gaps: MIDW (t28), B4 (t32), B7 (t35), B9 (t37), C1 (t38);
installed chain runs A9 → B1 → B2 → B3 → B5 → B6 → B8 → (RK_TUCK).
Systematic finding, same as SEGA: downward head moves are bimodal —
the edit model either holds height or drops the tip to the 845–908
band, and upward corrections overshoot to 550–670; the 766–830 target
band was landed only when the target step was ≤ ~35 units from the
canvas tip (B5, B6, B8). Saturation also drifts richer along the
chain (B8/B9/C1 attempts 56–58 vs home 46.9): not a failure under the
amended gate (paler/bluer is the named defect) and no blue/grey shift
was seen, but the coordinator may want to eyeball B8 next to home.
