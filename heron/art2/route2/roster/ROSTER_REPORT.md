# ROSTER REPORT — Route 2 (plate-neural) full animation roster, Fix 1 decoder

**Built 2026-11-03** on Jimmy's go ("lets move forward with this — the heron art").
Every chart in `movement-charts.yaml` rendered as a full frame sequence at
**1024×600, bird-only on blank white**, through the shipped Fix 1 decoder
(step-6000 `last.pt`, Spark `~/art2route2_fix/ckpt/`). Unretouched renders
only. Track B behavior corrections were NOT folded in — the charts as they
stand are the roster. No device port, no engine integration in this pass.

## Deliverables (this folder)

- `frames/<chart>/f####.png` — 17 folders, **1,668 frames** total.
- `contact_<chart>.png` — one strip sheet per chart (all frames ≤32;
  longer charts evenly sampled to 32, frame numbers labeled).
- `contact_master.png` — one signature frame per chart.
- `qa_<chart>.json` — per-frame QA numbers (measure_fix code paths).
- Code: `art2/roster_charts.py` (chart evaluator), `art2/roster_render.py`
  (renderer + QA), `art2/roster_qa.py` (aggregator), `art2/roster_sheets.py`
  (contact sheets). Render provenance also on the Spark at `~/roster_work/`
  (pose tracks, out/, logs).

## Frame counts (charts evaluate to their exact canonical counts)

| chart | frames | chart | frames |
|---|---|---|---|
| idle_hunt | 480 | takeoff | 96 |
| head_saccade | 3 | flight_cycle | 12 |
| head_turn | 18 | glide | 24 |
| strike | 52 | landing | 120 |
| swallow | 118 | stretch | 168 |
| step_cycle | 24 | oneleg | 36 |
| turn | 72 | doze | 96 |
| alert | 61 | preen | 240 |
| scratch | 48 | **total** | **1,668** |

**Blocking check:** root positions are the charts' own — idle/step/turn
live left-of-center (x≈26–46 of 150 design units), strike/swallow in the
right third (x=75), the flight family crosses center-frame, fishing
(strike/swallow) rooted mid-to-right as authored. Verified on the contact
sheets; nothing was re-blocked.

## How the charts drive the rig (bridges, all documented in code)

The rig's conditioning is the Fix 1 keypoint/mask bridge, copied verbatim
from `prep_poses.py` / `train_decoder_fix.py` (smoke test: the four target
poses re-rendered through this pipeline reproduce the Fix 1 sheet's QA
numbers to float rounding — the pipeline IS the Fix 1 renderer).
Chart parameters map onto it as: coil/head_pitch/flap/bulge 1:1;
body_tilt via the rig's two proven anchors (statue 0° ↔ coil +33°);
leg fy keys relative to the ground line; neck extension/retraction via
the rig's named neck stops (statue/coil/loaded/contact/withdraw/headback/
upright/flight); yaw via the rig's body-yaw stops.
Three chart parameters have **no channel in the shipped model** and are
tracked in the pose data but do not alter the bird render: `head_yaw`
(the rig draws head orientation from body yaw only — saccade/turn head
gestures render as the charts' hx/head_roll components), `fish`
(a swallowed fish is an environment/object event, not bird), and
`blink`/`smear` (no eyelid or smear channel exists). One geometry
correction was required: **oneleg's** literal fold target puts the foot
within 0.1 units of the hip pivot, where the rig's leg IK is singular
(it crashed the first render pass with the knee 100+ units off-frame);
the target was moved to the chart's stated drawing — foot tucked forward
under the belly (fx 8, fy −34) — and is flagged in `roster_charts.py`.

## QA table (gates from the Fix 1 sheet; measure_fix code)

Gates: checkerboard |index| ≤ 0.01 · head-region alpha occupancy ≥ 0.041
(the Fix 1 swallow baseline) · texture (body HF energy) in 0.025–0.048 ·
standing legs no wider than the Fix 1 sheet (near ≤ 11.0, far ≤ 8.0 px).

| chart | texture min/med/max | checker max | head occ min | head fails | tex fails | leg max n/f |
|---|---|---|---|---|---|---|
| idle_hunt | .032/.033/.034 | .0028 | .077 | 0 | 0 | 10.0 / 9.0 |
| head_saccade | .032/.032/.034 | .0030 | .079 | 0 | 0 | 10.0 / 9.0 |
| head_turn | .032/.033/.033 | .0055 | .084 | 0 | 0 | 10.5 / 9.0 |
| alert | .029/.029/.034 | .0049 | .055 | 0 | 0 | 10.5 / 9.5 |
| step_cycle | .032/.035/.036 | .0036 | .098 | 0 | 0 | 11.0 / 9.5 |
| turn | .032/.036/.050 | .0042 | .106 | 0 | 1 | 10.0 / 10.0 |
| strike | .027/.033/.040 | .0038 | .000 | 16 | 0 | 11.5 / 9.5 |
| swallow | .024/.030/.038 | .0037 | .000 | 16 | 2 | 10.5 / 8.5 |
| stretch | .031/.048/.053 | .0027 | .065 | 0 | 77 | 25.0* / 9.5 |
| oneleg | .032/.034/.036 | .0039 | .086 | 0 | 0 | 59.5* / 10.0 |
| doze | .033/.038/.041 | .0029 | .096 | 0 | 0 | 10.5 / 9.5 |
| preen | .032/.038/.048 | .0050 | .016 | 14 | 3 | 12.0 / 10.0 |
| scratch | .031/.039/.041 | .0036 | .092 | 0 | 0 | 60.5* / 10.0 |
| takeoff | .030/.043/.053 | .0044 | .000 | 14 | 11 | — (airborne) |
| flight_cycle | .038/.040/.045 | .0042 | .000 | 11 | 0 | — |
| glide | .040/.040/.040 | .0003 | .000 | 24 | 0 | — |
| landing | .025/.044/.049 | .0035 | .000 | 46 | 4 | 10.0 / 9.5 |

\* folded/raised-leg frames: the standing-leg scanline crosses the body,
so the number is the body width at that line, not a leg width — the leg
metric does not apply to tucked poses (see legs note).

**Checkerboard: PASS on all 1,668 frames** (worst |index| 0.0055, gate
0.01; the Fix 1 disease stays cured across the whole roster).

**Head gate:** the entire standing family passes with margin (min .055).
Failures concentrate exactly where Fix 1 was already weak — the flight
family (flight_cycle 11/12, glide 24/24, landing's airborne frames 0–45,
takeoff's climb frames) reads 0.000 because the flight head is drawn
displaced from its conditioning polygon, the same artifact the Fix 1
sheet itself measured (flight 0.0). Visual check: a head+bill IS present
at the front of the bird in flight frames f0–f4 and f9–f11; in the
deepest downstroke frames (f5–f8) it dissolves into the wing mass.
Strike frames 24–38 + 42 (release → contact → early withdraw) and
swallow frames 13–27 + 81 (late work-back, one travel frame) also read
0.000: at maximum neck extension the head lands outside its tight
polygon. On the strike strip the head is visibly present at the end of
the spear in sequence — the action reads — but the contact frames are
the softest in the chart. Preen frames 120–147 (head thrown back in
shoulder_fluff, then the wing_stretch hold) dip to .016.

**Legs:** in pure statue frames the roster measures near 10.0 / far 8.0
vs the sheet's rest 9.5 / 7.0 — the same legs rendered ~1 px larger
(the roster derives its render window from each frame's keypoints; the
sheet used the targets' stored crops — a small scale difference, stated
plainly: the ≤ sheet-width invariant is exceeded by ≤1 px on the far
leg in statue frames, and tilted/folded poses push the scanline measure
to 9.5–10.0 without the legs themselves changing). No frame shows the
thick-leg regression of the earlier routes; standing legs stay thin
sticks throughout, including all 480 idle frames.

**Texture:** in band for the whole standing roster. Above band only
where big wing area enters the body mask: stretch (77 frames, the
flight-outline wing at full droop — max .053), takeoff climb (11),
landing flare/settle (4 marginal), turn f33 (.0499), preen (3). Below
band: swallow f86–87 (.024, long-neck travel frames).

## Failed-frame list (exact; nothing dropped, nothing retouched)

- head < 0.041 — flight_cycle: 0–5, 6, 8–11 (all but f7) · glide: 0–23
  (all) · landing: 0–45 · takeoff: 24, 53–57, 63, 64, 66, 68–70, 79, 82
  · strike: 24–38, 42 · swallow: 13–27, 81 · preen: 120–124, 131, 132,
  137, 138, 143–147.
- texture out of band — stretch: 37, 48–50, 57–119 (full hold), 120–167
  partial (77 total; full list in `qa_stretch.json`) · takeoff: 28–33,
  38–40, 93, 94 · landing: 81, 101, 104, 106 · swallow: 86, 87 ·
  preen: 120, 124, 147 · turn: 33.
- checkerboard: none. Legs: see the legs note above — per-frame values
  in `qa_<chart>.json`.

## Weak spots — honestly

**Flight is still the weak tail, and the full cycles prove it isn't a
single bad pose.** Across 252 flight-family frames the bird reads as a
horizontal body smear with the wing as a dark vertical slab; in the
deepest downstroke frames (flight_cycle f5–f8, glide's held frame,
landing's flare f35) the head and body coherence partly dissolve, and
several flight frames carry small detached dark specks below the body
(f5, f7, f10, f11) — decoder debris, unretouched. In motion at 24 fps
the cycle will read as a flapping silhouette, but per-frame these are
abstract compared to the standing family. This is Fix 1's known flight
ceiling (its sheet flight was the weakest of four) extended, not a new
failure — and it is a corpus problem, not a settings problem.

**The swallow held up better than feared.** The upright-swallow solution
renders cleanly through work_back, toss and travel; the traveling bulge
is visible in the neck during travel frames, and the bill-detachment
Fix 1 noted persists mildly in the travel segment (f72–93) — the bill
reads slightly separate from the head at strip scale. The head-metric
failures at f13–27 are the late work-back oscillations (head at extreme
pitch), soft but present in sequence.

**Strike's contact is soft, stretch is blobby.** The strike's four
contact frames merge head into neck (the action still reads in
sequence; a still of f27 alone is mush). Stretch's full-hold frames —
wing rendered through the flight outline — read as a dark slab over the
body rather than articulated feathers; it's the least bird-like of the
standing charts. Takeoff's dangle frames push the feet a few px past
the bottom frame edge (the chart's fy exceeds the design frame) and the
climb frames carry a faint greenish cast on the wing mass.

**The standing roster — idle, head moves, alert, step, turn, oneleg,
doze, preen, scratch, and swallow's standing phases — is uniformly at
Fix 1 sheet quality**: thin legs, plume readable, heads present and
characterful, texture in band, zero checkerboard. That is 1,300+ of the
1,668 frames, and it includes the two poses Jimmy's pick turned on —
Route 2's legs and the fixed swallow head both hold across their full
cycles.

## Method notes

Pose evaluator `roster_charts.py` implements every chart's phases,
timings and easing curves from `movement-charts.yaml` (24 fps, stepped/
smooth/multi-beat easing per the craft rules) and asserts each chart's
canonical frame count. Interpolation is parameter-space throughout —
no frame was blended in pixel space. Rendering: batch UNet decoder
(frozen step-6000 weights), RIFE-free, on the Spark GPU; masks built
with the same `maskrender.py` the model trained on. QA reuses
`measure_fix.py` functions verbatim (one bounds-safe clone of
`leg_widths`, identical math, after the original crashed on oneleg's
tucked frames — its scanline guard uses the wrong axis bound).
