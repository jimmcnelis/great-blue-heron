# ALERT PLATE — BATCH 3 (CANVAS-CONDITIONED) DRAW REPORT

**Date:** 2026-11-04 · **Brief:** canvas-conditioned alert plate, 6 candidates, Jimmy's
choice of route (2026-11-04 12:32), plus his two mid-run rulings: the FRAMING GATE
(12:33) and WATER IS RIPPLES ONLY (12:37).
**Inputs:** RESET-2026-11-04.md + CREW_MEMORY.md + ART_DESIGN.md + LEG_CANON.md +
the corrected mechanism (rig v2.5 iter2, legs per LEG_CANON). NO pre-reset images,
NO batch 1/2 plates as inputs or donors. The canvas is computed fresh from the
mechanism (`work/build_canvas.py` imports `rig_v25`).

## 0. Verdict — GATE NOT FULLY PASSED, but the two named walls are DOWN

**The canvas route broke both geometry walls that killed twelve text-only
candidates.** On the best candidate the eye sits **5.0 px** from the canon anchor
(batch 1 best ≈24–31 px; batch 2 best 31 px; the gate is ≤10) and the ripple
rings sit **0.009 torso** from the joints on both legs (batch 2's seat error was
0.054–0.068; the gate is ±0.01). A second candidate (c1) also passes eye (5.9 px),
seat (0.006), and chord — proof this is the route working, not one lucky draw.

What still fails is the LEG PLACEMENT family, and it fails the same way on every
candidate: emergence reads 0.41–0.55 against the 0.53–0.61 band and the exposed
upper segments run long (0.25–0.32 against 0.21–0.25). The mechanism of the miss
is visible in the numbers: the generator fattens the torso well beyond the
canvas (plate torso lengths T = 585–736 px against the mechanism's 494), and
every torso-relative leg fraction shrinks with it — the painted legs end up
slightly too far back under a too-big body.

**Selected: candidate 3 → `alert_plate.png`.** It passes chord (0.442, in the
aim range), eye (5.0 px), ripple seat (0.009/0.009), ink (0.292 in the
0.260–0.300 band), framing, environment law, and the plume tell. It fails near-leg
emergence (0.477 vs ≥0.53) and upper-segment length (0.297 vs ≤0.25). Both
failures are named, measured, and Jimmy's to judge — accept the plate with its
legs as drawn, or send it back on the legs alone. The eye/seat branch of the
brief ("if the canvas route also fails those, stop") does not trigger: those
gates passed.

## 1. The canvas (`alert_canvas.png` — in the record)

Computed from the corrected mechanism at 1024×600, alert pose, design chord
0.456: torso loop filled slate with a darker folded-wing band; the neck as the
station-mapped tube (rest width profile, station ticks u = 0.1…0.9) around the
alert chain; black shoulder patch at the neckbase (601, 219); the head at canon
proportions — skull ellipse semi-major 0.052·T, eye drawn as a marked ring AT
the mechanism anchor (755, 36), orange bill from a base offset 0.04·T reaching
0.27·T, two occipital strands; the plume as ~14 separate strand curves rooted on
one breast seam; legs hip→joint only, thighs rusty then dark shin, knobs ON the
water height y = 382 (joints (406, 382) near / (358, 382) far).

**Canvas revision, disclosed:** v1 carried a full-width construction guide-line
at the water height (copy saved as `work/canvas_v1_with_guideline.png`).
Candidate 1, painted from v1, inherited the line as a drawn waterline and died
on Jimmy's ripples-only ruling the moment it landed. The line was removed; v2
(the delivered canvas) carries only the two ripple rings at joint height, and
candidates 2–6 were painted from v2 with prompt text that forbids any line,
band, or wash outright.

## 2. Gate table (batch 1/2 protocol: crop-to-aspect + uniform resize; no anisotropic stretch)

| gate | c1 | c2 | **c3 ★** | c4 | c5 | c6 |
|---|---|---|---|---|---|---|
| chord_base 0.40–0.47 | **0.439 ✓** | 0.348 ✗ | **0.442 ✓** | 0.391 ✗~ | 0.364 ✗ | 0.377 ✗ |
| **eye ≤10 px (HARD)** | **5.9 ✓** | 19.8 ✗ | **5.0 ✓** | 11.5 ✗~ | 23.0 ✗ | 24.7 ✗ |
| ripple seat ≤0.01·T, both legs | **0.006/0.006 ✓** | 0.007/0.007 ✓ | **0.009/0.009 ✓** | 0.005/0.006 ✓ | 0.013/0.011 ✗ | 0.005/0.005 ✓ |
| emergence 0.53–0.61 (mech. x-extent) | 0.504/0.459 ✗ | 0.503/0.436 ✗ | 0.477/**0.550** ✗/✓ | 0.504/0.447 ✗ | 0.485/0.431 ✗ | 0.473/0.412 ✗ |
| emergence (projection convention) | 0.509/0.464 | 0.503/0.436 | 0.480/0.551 | 0.508/0.452 | 0.489/0.436 | 0.475/0.415 |
| upper segment 0.21–0.25 | 0.248/0.252 ~ | 0.319/0.321 ✗ | 0.297/0.298 ✗ | 0.250/0.258 ~ | 0.301/0.302 ✗ | **0.214/0.218 ✓** |
| ink content-black 0.260–0.300 | 0.313 ✗ | 0.216 ✗ | **0.292 ✓** | 0.242 ✗ | 0.350 ✗ | 0.287 ✓ |
| ink black/frame (context) | 0.060 | 0.052 | 0.071 | 0.060 | 0.093 | 0.078 |
| framing (margins: crown/right/left px) | 49/138/103 ✓ | 59/94/74 ✓ | 50/84/53 ✓ | 65/90/54 ✓ | 52/61/47 ✓ | 40/62/48 ✓ |
| environment law (ripples only) | **✗ LINE** | ✓ | ✓ | ✓ | ✓ | ✓~ (heavy rings) |
| plume countable strands | ✓ | ✓~ (fan) | ✓ | ✓ | ✓ | ✓~ (swept) |

★ = delivered as `alert_plate.png`. ~ = marginal/within grounding noise or a
qualified pass. Context reads: head assembly occiput→bill-tip (canon 0.322):
c1 0.230, c2 0.307, c3 0.309, c4 0.277, c5 0.277, c6 0.218 — c3's head is the
right OVERALL size as well as correctly seated; c1 and c6 shrank the whole head
even where their eyes landed near the anchor. Feet-centre: by construction from
the corrected alert pose, 0.521 (stated, not measured); c3's drawn joint-centre
reads 0.497 on the same x-extent convention.

## 3. The selected plate in plain words (viewed: plate + all three crops)

**The face:** a SHORT face at last — white cheek, black crown band, the bill a
long level orange dagger. The eye sits exactly where it should, close behind
the bill's base (5.0 px off the canon anchor), and the drawn occiput→eye
fraction is 0.084 against the canon 0.080. One honest tell: the eye itself is
drawn BIG — a round amber ring that stares out of the small head, more
prominent than life. Placement is right; size is the generator's flourish.
Two occipital plume strands trail back with a small decorative curl at the
skull.

**The waterline seat:** there is no waterline. Both dark scaly shins drop
straight into two flat black ripple rings on blank cream paper — the crop shows
two tidy concentric ellipses, centres at one height, nothing below them, no
line, no band, no blue anywhere in the plate. The rings sit at the legs'
bottoms, 5.4 px (0.009 torso) from the joint reads on both legs — inside the
gate, at its edge.

**The rest:** the neck is a clean open S at full length, pale and lightly
spotted in front, slate down the back. The plume hangs from the black shoulder
patch as a curtain of ~20 separate strands, each with its own wispy free tip —
countable, not a mass (crops/plume.png). The torso is deep and high-domed with
a scalloped wing — larger-bodied than the canvas, which is the same inflation
that pulls the leg fractions down. Whole bird inside the frame: crown ~50 px
of headroom, bill tip ~84 px from the right edge, tail ~53 px from the left.

## 4. The other five, briefly

- **c1 — dead on the environment law** (drew the canvas v1 guide-line as a
  full-width waterline; also plume strands trail below ring height and ink
  content 0.313 is over band). Kept in the record because it is the diagnostic
  proof: even on the lined canvas its eye landed 5.9 px and its seat 0.006.
- **c2** — clean water and seat, but chord 0.348 (neck reads tucked), eye
  19.8 px, legs long, ink light (0.216), and the plume sweeps into a horizontal
  fan over the belly instead of hanging.
- **c4** — the near-miss: eye 11.5 px and chord 0.391 both just outside their
  gates, seat excellent (0.005/0.006), plume good; emergence and ink content
  (0.242) also under.
- **c5** — eye 23.0, chord 0.364, seat 0.013/0.011 (the batch's only seat
  failure), ink heavy (0.350); bill tip margin smallest at 61 px but in frame.
- **c6** — the only candidate with both upper segments in band (0.214/0.218)
  and clean seat/ink, but eye 24.7 px, chord 0.377, a shrunken head (0.218),
  and the ripple rings drawn heavy — thick black-and-white target rings with a
  pale halo, lawful in kind but loud.

## 5. Method + prompt drift, disclosed

- Same conditioning route for all six: `media.generate_image` with the canvas
  PNG + directive text. c1 used canvas v1 and text describing "a single
  straight waterline"; Jimmy's 12:37 ruling changed both — c2–c6 used canvas
  v2 and ripples-only text. c4–c6 added one clarifying clause ("hangs DOWN …
  never a horizontal fan") after c2's fan. The drift is Jimmy's correction and
  one observed defect, not silent iteration.
- Measurement protocol identical to batches 1–2 for comparability: torso =
  tail/chest/back-top/belly landmarks; skull centre = grounded occiput +
  0.052·T_p along the bill axis; eye anchor = centre + 0.028·T_p along-bill +
  0.014·T_p perpendicular; ink by the v3 protocol (paper = corner medians,
  content = summed RGB difference > 55, black = content under mean RGB 70).
  Numbers: `work/measure.py`, `work/gate_numbers.txt`.
- Ripple seat per Jimmy's restated gate: |ring centre y − joint y| per leg,
  the joint grounded as the knuckle at the very bottom of the leg where it
  enters its ring. On c3 the grounding's near/far labels came back swapped by
  x; pairs were matched by proximity (joint↔ring of the same leg), which does
  not affect the seat values.
- The ink band remains the batch-3 brief's working band (0.260–0.300 content),
  unsettled until a plate is approved. If Jimmy approves c3, the settled band
  becomes content 0.272–0.312, frame 0.051–0.091, by the design's ±0.02 rule.

## 6. What is in the folder

```
batch3/
├── alert_canvas.png            the structural canvas (v2, ripples only)
├── alert_plate.png             candidate 3, delivered for Jimmy's gate
├── ALERT_DRAW_REPORT_B3.md     this report
├── candidates/                 alert_c1..c6.png (all six, normalized 1024×600)
├── crops/                      head_eye.png · waterline_joint.png · plume.png (×2, from the plate)
├── sidebyside/                 canvas_plate_mask.png (canvas | plate | mechanism mask)
└── work/                       build_canvas.py · normalize.py · measure.py ·
                                gate_numbers.txt · raw generations ·
                                canvas_v1_with_guideline.png · mechanism_mask_alert.png
```

**Next step is Jimmy's gate.** Nothing else drawn this run.
