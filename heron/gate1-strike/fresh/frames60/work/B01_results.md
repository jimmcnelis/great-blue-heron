# B01 Results — FRAMES60 Batch 1 (t01–t04, freeze)

Target for all four: bill tip (472,848), 0–1000 coords; accept within ~30 units. bird_sat FAIL if < 42.9.
Method: KEY-style full drawings, images in order home_frame_approval.png, prof_d.png, heron_pencil_verified_20261105-1201.png, ref_coil.png; base prompt + landmark sentence (47.2% / 84.8%) + freeze pose sentence; adjusted landmark emphasis on escalation attempts per brief. Each slot drawn from its own independent calls — no copies.

## t01 — GAP
- Status: GAP (6 attempts, none passed the tip gate)
- Attempts used: 6
- Measured tips / bird_sat per attempt:
  - a1 (456,803) sat 52.0 — dist ~47.8, tip too high
  - a2 (404,857) sat 55.6 — x too far left (registered scale)
  - a3 (511,824) sat 51.3 — x overshoot
  - a4 (426,832) sat 50.0 — x too far left
  - a5 (404,855) sat 46.7 — x too far left (registered scale)
  - a6 (597,827) sat 53.5 — x far overshoot, legs stance also off
- Best attempt: a1, tip (456,803), bird_sat 52.0
- View verdict (best attempt): color/identity correct (slate body, orange bill, yellow ringed eye, frill whole, blank paper, feet rings) but head held too high — tip 45 units above target.
- No file saved to raw/ for t01.

## t02 — ESCALATED-PASS
- Status: ESCALATED-PASS (passed on attempt 5, after adjusted landmark emphasis)
- Attempts used: 5
- Measured tips / bird_sat per attempt:
  - a1 (427,823) sat 49.5
  - a2 (499,766) sat 56.6 — head too high, rear foot off stance
  - a3 (388,925) sat 49.7 — tip too low/left, extra ripple ring at bill tip (wrong water state)
  - a4 (493,812) sat 49.8 — dist ~41.7, tip too high
  - a5 (478,836) sat 55.9 — PASS, dist ~13.4
- Accepted: tip (478,836), bird_sat 55.9
- View verdict: home color/identity matched, frill whole, legs in home stance, whole bird in frame, blank paper, small ripple rings at each foot only.
- Saved: frames60/raw/t02.png (2048x1152)

## t03 — PASS
- Status: PASS
- Attempts used: 2
- Measured tips / bird_sat per attempt:
  - a1 (447,814) sat 50.4 — dist ~42.0
  - a2 (459,830) sat 51.5 — PASS, dist ~22.2
- Accepted: tip (459,830), bird_sat 51.5
- View verdict: home color/identity matched, frill whole, legs in home stance, whole bird in frame, blank paper, small ripple rings at each foot.
- Saved: frames60/raw/t03.png (2048x1152)

## t04 — GAP
- Status: GAP (6 attempts, none passed the tip gate)
- Attempts used: 6
- Measured tips / bird_sat per attempt:
  - a1 (404,855) sat 49.0 — x too far left (registered scale)
  - a2 (438,776) sat 48.6 — tip too high
  - a3 (404,855) sat 49.2 — x too far left (registered scale)
  - a4 (400,866) sat 49.9 — x too far left
  - a5 (404,856) sat 48.3 — x too far left (registered scale)
  - a6 (546,819) sat 57.5 — x overshoot; view also fails (stray whisker-like plumes beside the bill, legs stance shifted)
- Best attempt: a2, tip (438,776), bird_sat 48.6 (dist ~79.9 — no attempt came close on both axes; the model repeatedly anchored to the registered home scale, tip x ≈ 400–405)
- View verdict (typical attempts): color/identity and frill correct, blank paper, feet rings present, but tip anchored ~68 units left of target at the registered scale.
- No file saved to raw/ for t04.

## Summary
Batch B01: 2 of 4 slots filled — t02 ESCALATED-PASS (5 attempts, tip 478,836, sat 55.9), t03 PASS (2 attempts, tip 459,830, sat 51.5); t01 GAP (6 attempts, best tip 456,803, sat 52.0) and t04 GAP (6 attempts, best tip 438,776, sat 48.6). Root cause noted for the parent: the attached home_frame_approval.png is the registered (scaled 0.80) frame — its own measured tip is (403,854) — while the POSE TABLE targets are in raw scale (t00 raw measures (473,850)); most generations anchor to the attached frame's scale and land at x≈404, and landmark-emphasis swings overshoot unpredictably.
