# KEYFIX results — candidate-selection round for RK_EMID, RK_PEAK, RK_MIDW

Method per WORKER_BRIEF + task brief: round-1 failures moved to
work/rejected/<NAME>_round1.png first. Then up to 3 fresh full-drawing
candidates per key (key-style calls: home + prof_d + pencil verified +
ref_peak; RK_MIDW also + ref_coil), each resized to exactly 2048x1152 and
gated on view + visual-grounding bill tip (target tolerance ~25 units) +
bird_sat (PASS 42.9–50.9). Candidate files kept in work/keyfix/<NAME>_c<N>.png.
No 4th candidate was generated for any key.

## RK_EMID — target tip (643,840), t12 — **FAILED** (no candidate passed)
- c1: tip (595,660) upper / (582,677) lower mandible (grounding returned both;
  bill slightly open) — dx −48, dy −180 vs target; bird_sat 52.5 (FAIL, over
  band); view FAIL — head held too high, not driven forward-down; S-bend
  present, feet rings only, home stance and color register otherwise fine.
- c2: tip (611,827) — dx −32, dy −13; bird_sat 54.1 (FAIL); view clean —
  half-coiled S-bend remaining, bill closed, rings only at feet, home stance.
  Nearest tip of the three (~35 units) but sat 3.2 over the band top.
- c3: tip (656,770) — dx +13, dy −70; bird_sat 50.8 (PASS, near top of band);
  view clean — clear S-bend remaining, spear NOT straight, bill closed and
  well above water, rings only at feet, home legs/frill. Fails tip on y only.
- Installed: **c3** as poses/RK_EMID.png, marked FAILED — closest to passing
  (2 of 3 gates pass; single-axis tip error). c2 is the runner-up if the
  coordinator prefers tip proximity over the sat band.

## RK_PEAK — target tip (596,954), t15–16 — **FAILED** (no candidate passed)
- c1: tip (505,932) — dx −91, dy −22; bird_sat 51.3 (FAIL); view FAIL — neck
  bent in an S (not one straight spear), bill slightly open, and a drawn
  waterline running across the whole frame (water-law violation).
- c2: tip (525,918) — dx −71, dy −36; bird_sat 52.8 (FAIL); view PASS — one
  straight STEEP spear, bill tip touches the surface with the first small
  rings born at the touch point (plus a few small splash flecks), no
  waterline, body well left in home stance. Fails the two numeric gates only.
- c3: tip (544,933) — dx −52, dy −21; bird_sat 52.7 (FAIL); view FAIL — neck
  dips/bends instead of one straight spear, bill slightly open, splash at the
  touch point and a faint drawn waterline. Tip nearest of the three
  (~56 units) but repeats the round-1 bent-spear failure.
- Installed: **c2** as poses/RK_PEAK.png, marked FAILED — the only candidate
  with the correct spear + water state; its failures are quantitative
  (tip 71 left / 36 high, sat 1.9 over band).

## RK_MIDW — target tip (596,734), t28 — **FAILED** (no candidate passed)
- c1: tip (445,254) — dx −151, dy −480; bird_sat 48.2 (PASS); view FAIL —
  upright alert heron with head high, not a withdrawal pose; bill closed, NO
  blue wash (water law obeyed), rings only at feet.
- c2: tip (442,287) — dx −154, dy −447; bird_sat 52.9 (FAIL); view FAIL —
  upright alert pose again; bill closed, no wash.
- c3: tip (461,295) — dx −135, dy −439; bird_sat 49.4 (PASS); view FAIL —
  upright alert pose a third time; bill closed, no wash, feet rings only.
- Installed: **c3** as poses/RK_MIDW.png, marked FAILED — closest tip
  distance of the three (~459 units) and passes sat + water law, but the pose
  is wrong. Systematic failure: all three candidates collapsed to the upright
  alert/home bird — the "head held HIGH + question-mark S" language plus the
  coil reference reads as the alert pose, and the 60%/73% tip landmark was
  ignored in every attempt. The blue-wash failure from round 1 did NOT recur.

## Summary
**0 of 3 keys passed.** All three installed files are the closest candidate of
their round and are marked FAILED — none should be treated as verified.
Cross-cutting: bird_sat ran hot in 6 of 9 candidates (51.3–54.1, all over the
50.9 band top); EMID is one axis away (c3: dy −70 with sat/view clean); PEAK's
shape is solved in c2 but lands ~70 units left with hot sat; MIDW needs a
different prompt strategy (the current language reliably produces the alert
pose) rather than more attempts of the same kind.
