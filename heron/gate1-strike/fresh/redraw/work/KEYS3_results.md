# KEYS3 Results — Strike Redraw (candidate selection)

Method: CANDIDATE SELECTION. Up to 3 fresh full-drawing candidates per key
(key-style calls per WORKER_BRIEF: home, prof_d, pencil-verified, ref_coil),
every candidate measured (view + visual-grounding bill tip + bird_sat on the
2048x1152 resize). Install only a PASSING candidate (tip within ~25 units of
target, bird_sat 42.9-50.9, clean view). All candidates kept in redraw/work/gen/
as <NAME>_k3a<N>_2048.png.

## RK_TUCK — target (449,823), t39-41
- Status: FAILED — nothing installed
- Candidates: 3
- k3a1 (RK_TUCK_k3a1_2048.png): tip (420,872), bird_sat 51.25 — view: head
  lowered forward-down in an open S, NOT folded back to the chest; a touch ring
  sits under the bill tip (wrong water for the tuck; should be widest faint
  rings, nearly calm); frill/legs fine. FAIL on tip (dx -29, dy +49), color
  (51.25 above band), pose and water.
- k3a2 (RK_TUCK_k3a2_2048.png): tip (403,856), bird_sat 48.58 — view: loose S,
  head hangs forward of the body, not the tight question-mark tuck; ripple
  rings small at the feet only, no wide faint rings. FAIL on tip (dx -46,
  dy +33) and pose/water. Color PASS.
- k3a3 (RK_TUCK_k3a3_2048.png): tip (398,840), bird_sat 49.88 — view: tightest
  fold of the three and wide faint rings present across the waterline, frill
  and legs correct, but the head still hangs forward rather than folded back
  to the chest and the tip swung far left. FAIL on tip (dx -51, dy +17).
  Color PASS.
- Verdict: FAILED — color now lands in band (2 of 3, vs round 1's vivid 56.5),
  but every candidate's tip landed left of target (dx -29/-46/-51) and none
  achieved the head-folded-to-chest tuck; the generator keeps placing the
  tucked head forward-down instead of back against the chest.

## RK_SETTLE — target (510,836), t57
- Status: FAILED — nothing installed
- Candidates: 3
- k3a1 (RK_SETTLE_k3a1_2048.png): tip (412,743), bird_sat 47.99 — view: head
  raised in an upright S, well above the home coil; horizontal water-wash
  strokes across the bottom (wrong water; should be faint ghost rings only).
  FAIL on tip (dx -98, dy -93), pose and water. Color PASS.
- k3a2 (RK_SETTLE_k3a2_2048.png): tip (462,625), bird_sat 49.33 — view: clean
  drawing, frill/legs/faint feet rings correct, but the head is fully raised
  in an alert upright S — the opposite of the near-home settle. FAIL on tip
  (dx -48, dy -211) and pose. Color PASS.
- k3a3 (RK_SETTLE_k3a3_2048.png): tip (463,600), bird_sat 49.33 — view: clean,
  feet ghost rings correct, head fully raised upright again. FAIL on tip
  (dx -47, dy -236) and pose. Color PASS.
- Verdict: FAILED — color passed all three, but the generator would not keep
  the head low near the home coil: all three tips landed high (dy -93/-211/
  -236). Same failure mode as KEYS2 fresh attempts and the KEYS2FIX edit from
  home (which swung high or low); the subtle "slightly higher/forward than
  home" delta is not being rendered — fresh draws default to a raised head.

## Summary
0 of 2 keys passed; nothing installed to redraw/poses/ (RK_TUCK.png and
RK_SETTLE.png remain absent). 6 candidates generated and measured, all kept in
redraw/work/gen/. Pattern across both keys: color is now reliable in band
(5 of 6 candidates), but bill-tip placement is not — TUCK tips cluster
30-50 units left of target with the head forward instead of folded, and
SETTLE heads default to fully raised (tips 93-236 units too high).
