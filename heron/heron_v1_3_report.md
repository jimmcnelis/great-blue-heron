# Heron v1.3 — Phase 1 report (clean-slate rebuild, art = C naturalist plate)

**Deliverables**
- Model sheet: [model_sheet_v1_3.png](sandbox://workspace/heron/model_sheet_v1_3.png) — naturalist full set (profile rest, hunting coil, yaw 45/90/135/180, flight) + storybook profile rest & coil + silhouette strip.
- Test episode, ONE performance rendered twice at 1024×600, 24 fps, 26.0 s, 624 frames:
  - [preview_heron_v1_3_naturalist.mp4](sandbox://workspace/heron/preview_heron_v1_3_naturalist.mp4) — md5 `964cfb047387e706b0d904577625280f`
  - [preview_heron_v1_3_storybook.mp4](sandbox://workspace/heron/preview_heron_v1_3_storybook.mp4) — md5 `3e02014db14c398e65279746c338e525`
- Contact strips: `v1_3_strip_naturalist.jpg`, `v1_3_strip_storybook.jpg` (12 frames each). Audits: `src13/qa13.json`. Code: `src13/` (rig13, cycles13, ink13, episode13, sheet13). Pose data: `src13/episode13_poses.npz`.

## Self-critique first, in your terms

**Is it still "a blue oval with other shapes attached"? No — and yes, in two places.** The profile bird is no longer an oval: the torso is one loop, but the folded wing now lives inside it as 4 rows of individually layered scallop shingles (7/7/6/6), the tail ends in feather points, the belly has a ragged feather skirt, the beard is IN the silhouette (26 plume strands hanging off the throat — it shows in the silhouette strip), and the legs are near-straight stilts (I fixed the leg math: the visible "thigh" is the tibiotarsus, hip pivot inside the body — the v0 render bowed them 12 units sideways before I caught it). The head is the biggest single win over v1.2: black cap + brow, cream face, a ringed eye you can actually see, plumes sweeping back, bill with a ridge line. Where the oval survives: **the front stop's body is too round** (a ball with two dark wing-bulge spots — nameable, centered, no totem, but it's the weakest panel), and **the flight wing still reads as two dark fins** rather than one broad heron wing — the elbow bend and separated far wing helped; it is not there yet.

**Is the animation better than "slightly better"? I believe the shape of it is right; you judge the degree.** The release sequence (audited + frame-pulled): loaded hold with the beak path at ≤0.14 design units/frame, then 19 units/frame at the snap — a 136× spacing ratio, no leak. The strike now commits: root lunges +3, body tilt goes to 31°, legs rake back against planted feet. The walk plants feet at fixed world points (ripples fire exactly at plant frames: 149/203/257) and the head holds its world x while the body passes under it — steadiness by construction, no v1.2 compensation hunch anywhere (I frame-pulled the walk; the neck never buckles). The swallow bulge FAILED its first eye check exactly the way v1.2's did (audit-true, invisible), so I re-rendered the swallow with amp 0.55→0.9 and a wider profile: it now travels visibly down the throat at crop scale, and is merely subtle at full frame. I am claiming "reads," not "punches."

**Where the eye disagrees with passing numbers (stated, not smoothed):**
- **Held fraction: 0.62 opening / 0.57 closing (pose-exact), below v1.2's 0.950.** The gap is authored, not jitter: both statues carry blinks, one gaze saccade apiece, and a slow plume sway in their tails — every non-identical frame is an event frame, and pixel-identical pairs in the closing statue are 99/174 with zero random flicker. If you want v1.2-grade literal statues, the sway comes out in one line; my call was that a statue whose plumes breathe slightly is more alive. Your ruling either way.
- **Silhouette stop areas deviate up to 23%** (front = 67% of profile area) vs the ±5% canon gate. That gate was an anti-morph device for the v1.2 turn; there is no turn in phase 1, and a front-on heron genuinely foreshortens. Flagging the disagreement rather than quietly inflating the front stop back into a totem.
- **Toss-flip runs 8 frames airborne vs clip-06's measured ~5.** Slightly floaty. One-line fix if it bothers you in motion.
- The wading strike remains the least-grounded behavior (no wading-strike footage exists); its shape follows the study + the measured plunge's phases.

## The style-pack boundary (doctrine, made real)

One rig, one authored performance (624 pose frames), rendered twice. **The creature owns:** all outline control points, the neck spine + width profile, IK legs, yaw stop point-sets, proportions, the fish, and every timing. **The style pack owns only:** palette tone assignment per part, scallop rows (naturalist 4 rows of small shingles w/ outlines vs storybook 2 rows of big masses), plume rendering (26 individual strands vs one zigzag fringe mass), surface detail (nape hatching, throat streaks, bill ridge — naturalist only), eye treatment (ringed+pupil+glint vs flat dot), and outline weight (0.5 vs 0.85). **Neither owns the ink** — ripples/splash/drips are the world's causality system, identical in both cuts. Practical consequence visible in the strips: storybook reads bolder and cleaner at a glance; its beard is much smaller (a fringe tick vs a mane) and its extended neck is a plainer tube. Naturalist carries C's texture. The other pack stays a working alternate, per your ruling.

## Audits (floor, from qa13.json)
Ink in the water zone at rest: **0 px** (the ink layer draws nothing without an event; 9 events total, all caused). Step↔ripple: 3/3 matched. Anticipation: pass (above). Silhouette test: rest/front/flight all nameable from shape alone (sheet, bottom row). Chart-vs-footage: landing/takeoff aren't in this episode (phase-1 scope); strike+eat catch→settled ≈ 7 s shape preserved (contact f326 → statue f448 ≈ 5.1 s of screen time plus the settle blend — slightly brisk vs the measured 7 s; the eat itself, contact→swallow-end ≈ 4.1 s).

## Open items carried forward
1. Front-stop torso roundness; flight-wing breadth — the two drawing debts.
2. 135/180 stops are mirror-authored counterparts of 45/0 (disclosed on the sheet); a real in-motion turn is canon work, not phase 1.
3. **1024×600 vs the 800×480 product spec** — this phase was authored and judged at 1024×600 per your "design it for a larger screen." The rig is normalized, so an 800×480 render is a re-render, not a rebuild — but C-density scallops will shed detail there. Undecided, as agreed.
4. Nothing here trains or ports: full canon, pose model, and device work wait for your verdict on art + style, per the charter.

**Verification statement:** every claim above traces to my own frame pulls (rest/coil/gallery iterations, release strip f322–328, bulge crops f398–422 pre/post fix, both 12-frame strips, the sheet) and the audit script — not to render receipts. The one thing I cannot do from here is watch it play at speed; the motion judgment is yours, as it should be.
