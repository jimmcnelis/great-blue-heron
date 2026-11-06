# KEYEDITS results — edit-bootstrap round for RK_MIDW, RK_EMID, RK_PEAK

Method (coordinator-directed change): each key edited from the ONE verified
key, redraw/poses/RK_EXIT.png (tip (602,810), bird_sat 49.1), FIRST image =
RK_EXIT.png, home frame attached second as color authority, ONE transformation
per prompt, prompt text exactly as assigned. Max 2 attempts per key; RK_PEAK
got the one authorized ESCALATED third attempt editing
work/keyfix/RK_PEAK_c2.png. Every attempt resized to exactly 2048x1152 and
gated on view + visual-grounding bill tip (target tolerance ~25 units) +
bird_sat (PASS 42.9–50.9). Attempts kept in work/gen/ as <NAME>_ke<N>.png.
Install rule: poses/<NAME>.png overwritten ONLY by a passing candidate.
**No candidate passed all gates — nothing was installed; poses/ still holds
the KEYFIX-round files.**

## RK_MIDW — target tip (596,734), t28 — **FAILED**
- ke1 (work/gen/RK_MIDW_ke1.png): tip (525,755) — dx −71, dy +21; bird_sat
  46.7 (PASS). View: the pose finally reads right — deep S re-coil, head
  down-forward at belly height, NOT upright/alert (the KEYFIX collapse is
  fixed by the edit-bootstrap); bill closed, no droplets, rings wide. Fails
  tip on x only: the re-coil pulled the head ~70 units left of target.
- ke2 (work/gen/RK_MIDW_ke2.png): tip (561,583) — dx −35, dy −151; bird_sat
  47.4 (PASS). View FAIL — head rose too high into a question-mark S above
  belly level; rings spread very wide. Worse than ke1.
- Closest: ke1 — correct pose + sat, single-axis tip miss (x −71).

## RK_EMID — target tip (643,840), t12 — **FAILED**
- ke1 (work/gen/RK_EMID_ke1.png): tip (724,810) — dx +81, dy −30; bird_sat
  49.6 (PASS). View: water state correct (feet rings only, no rings/droplets
  under bill), but the neck went to a FULL straight horizontal spear — the
  "halfway" unfolding overshot; bill slightly open (inherited from RK_EXIT).
- ke2 (work/gen/RK_EMID_ke2.png): tip (722,855) — dx +79, dy +15; bird_sat
  47.7 (PASS). View clean (bill closed, water correct) but the same overshoot:
  tip lands ~72% width both times, not 64%.
- Systematic: editing from EXIT, "unfold further into the spear" runs to full
  horizontal reach; the 64% landmark is overshot by ~80 units on x in both
  attempts. Sat + view are now consistently fine — only reach control fails.

## RK_PEAK — target tip (596,954), t15–16 — **FAILED**
- ke1 (work/gen/RK_PEAK_ke1.png): tip (621,931) — dx +25, dy −23 (nearest tip
  of the round, ~34 units); bird_sat 51.1 (FAIL, 0.2 over band top). View:
  long spear with a slight mid-neck sag (not perfectly one straight line),
  bill closed touching the water, small rings born at the touch point, no
  droplets, no waterline.
- ke2 (work/gen/RK_PEAK_ke2.png): tip (527,951) — dx −69, dy −3; bird_sat
  47.1 (PASS). View PASS — steep straight spear, tip touches, small rings at
  touch, no droplets; but the edit shrank/shifted the bird left, so the tip
  landed at 53% width instead of 60%.
- ke3 **ESCALATED** (work/gen/RK_PEAK_ke3esc.png; canvas =
  work/keyfix/RK_PEAK_c2.png, corrected per brief): tip (570,918) — dx −26,
  dy −36; bird_sat 54.7 (FAIL — the "soften color" instruction backfired; sat
  rose from c2's 52.8 instead of falling toward the band). View: steep spear
  shape kept, tip touches with small rings, no droplets/waterline. Fails sat
  decisively and tip marginally.

## Summary
**0 of 3 keys passed; nothing installed.** Progress vs KEYFIX: MIDW's pose
collapse is solved (ke1 is a true withdrawal S at the right height, sat in
band — only tip x −71); EMID now passes sat + view consistently but the
EXIT-edit overshoots reach to ~72% width on both tries; PEAK produced two
complementary near-misses (ke1: tip near, sat +0.2 over; ke2: sat/view clean,
tip x −69) and the ESCALATED c2 edit made sat worse (54.7). Recurring theme:
the edit model trades tip-x against sat — no attempt yet holds both.
