# Heron v1.3 — PLAN (phase 0, written during the art-direction pause)

Status: **character design PAUSED** at Jimmy's order (2026-11-02 16:00) —
he is settling the art direction directly with Mordecai (candidate round,
same process as v1). This document is everything that does NOT presume the
final drawing: what carries from three versions of learning, what is
discarded, the fresh rig architecture, and the build order that starts the
moment the picked direction arrives.

Charter (Jimmy, 2026-11-02 16:00): "get as close to starting from scratch
as you can with all our learning intact. that should be the next version."

## Kept — rulings and laws (Jimmy's, not negotiable)

- Static-first axiom (2026-11-02 15:18): mostly static, good-but-repetitive
  beats janky-but-random; variety lives in scheduling, never inside a cycle.
- Ink law: water implied, never drawn; black ink only when caused (step
  ripples, strike splash, drips, takeoff churn); zero ink at rest.
- Thirds blocking: bird lives in the 1st/3rd third, fishing in the middle.
- Flat storybook finish; the end-state is "a cartoonist drew and animated
  it" — the 320×240 device grid is a constraint, never an aesthetic.
- The turn is drawn progressively through orientations, never flipped,
  mirrored, or squashed.
- Pose space as the architecture (Jimmy's "yes to pose space" ruling): the
  model performs in pose parameters, a rig draws. This deletes the v1.1
  failure class (pixel bottleneck merging 1-cell legs into a bar).
- Knee-deep water; presence contract (approach → alert; watched → fishes
  more; empty → doze; no camera, no mic, ever); line boil OFF.

## Kept — engineering that was sound (re-derived, not copied)

- Palette-indexed grid; author continuous at 4× supersample, rasterize
  late by majority downsample. (Craft: author continuous, rasterize late.)
- Design space 120×90 on the 320×240 grid; 24 fps; palette-exact output.
- The procedural ink layer as a separate caused-event system.
- Fish as STATE (grip point / orientation / free arc) in all phases —
  v1.2's one unambiguous design win; the toss is data, never a patch.
- Verbatim signature cycles + a scheduling player; per-segment authored
  spacing (no universal ease anywhere).
- Measurable craft gates as a FLOOR (see QA below) — never as the goal.

## Discarded — and why (the failure ledger)

- **v1.2's rig drawing system.** The body was a parametric ellipse, the
  neck a constant-profile tube, the head an ellipse + cap + triangle bill.
  Primitives assembled = "a blue oval with other shapes attached" (Jimmy).
  No shape from src12/rig.py carries over.
- **v1.2's yaw machinery.** Stops were width/height FACTORS scaling one
  drawing, plus area-keeper bulge ellipses. Eye verdict (turn strip):
  mid-turn the bird becomes a front-facing totem — bulge "ears", fringe
  "skirt" — a different creature for ~30 frames. Scaling is not drawing.
- **v1.2's charts as adopted.** movement-charts.yaml was implemented
  literally and produced motion Jimmy grades "slightly better." The study
  and charts remain EVIDENCE; every cycle is re-derived footage-first
  (see CHART_NOTES.md).
- **v1.2's performances and pose corpus** (canon, corpus12, model12).
  The pose model retrains on the new canon only after the canon freezes
  post-verdict; phase 1 does not need it (the player renders authored
  poses directly, as v1.2's preview did).
- **Head-lock by counter-shift.** v1.2 cancelled the walk's root advance
  with a neck_sway offset; the neck buckled into a hunched S for whole
  seconds (walk strip). Steadiness must come from construction (head
  target in world space), not compensation.
- **The flight wing drawing.** A polygon extending backward from the
  shoulder; at profile it hid behind the body and read as a tail fin /
  shark blade (takeoff + landing strips). Flight was the weakest drawn
  thing in v1.2 and it passed every audit. Audits are a floor.

## Fresh rig architecture (src13 — mechanics only, no shapes presumed)

1. **Silhouette-first construction.** Every part is a closed authored
   path (control points smoothed by Catmull-Rom), never a primitive.
   The torso is ONE continuous outline loop — breast, keel, belly, tail
   wedge in a single loop — so masses cannot detach. Feather masses are
   outline events: the folded wing's scalloped rear edge and the tail
   wedge shape the loop itself; interior feather-group lines are a
   second, optional layer in ≤2 additional flat tones.
2. **Neck as a filled outline, not a tube.** Throat edge and nape edge
   are separate authored curves joined into one filled path. The nape
   flows into the body's back line (shared control points); the throat
   carries the chest-plume fringe AS OUTLINE (zigzag points along the
   lower throat/breast — the beard is silhouette, not decoration).
   Width profile is authored per neck state and NARROWS at full strike
   extension (the real extended neck is thinner than the coiled S).
   Neck states (upright / coil / extended / folded-flight) are authored
   edge-curve sets blended in control-point space.
3. **Head as one outline.** Skull + flat crown + brow ridge + face in a
   single path; the bill is a second filled path hinged at the face
   (gape = lower mandible rotating about the hinge, as in v1.2 — that
   mechanism was right). Eye and plume anchors sit on the outline.
   Crown line continues into the bill's top edge (both real photos).
4. **Yaw by construction.** Each of the five stops is a FULL authored
   outline set (torso loop, neck edges, head) with matching control-point
   topology; between stops, interpolate control points — never scale a
   finished drawing. The front stop is authored from the pier footage's
   front frames (narrow body, neck centred and LOW in front of the
   chest, legs close, chest fringe centred).
5. **Legs.** Two-segment IK retained in principle (it worked), but the
   thigh is a filled feathered path continuous with the belly loop;
   ankle fold, toe articulation, and the drawn one-leg tuck carry over
   as behaviors. Stilts stay stilt-thin below the thigh.
6. **Flight wing rebuilt as a drawing problem.** Two-segment wing whose
   surfaces read at profile through the whole beat (area above AND below
   the body line across the stroke); authored 5f-down / 7f-up beat with
   2-frame tip lag (v1.2's genuine rhythmic win, kept as timing, redrawn
   as shapes).
7. **Pose vocabulary** re-derived around the outlines: root, body posture
   (tilt / crouch), neck state blend + head (yaw / pitch / roll / gape),
   body yaw (control-point blend), wing (fold-state set / flight angles),
   legs (foot targets + toe), bulge (throat-outline swelling — an outline
   event, sized to READ at 320 or not claimed), fish state, plume sway,
   blink, smear flag.

## QA — floor plus eyes

- Floor (must pass, reported): turn silhouette within ±5% on every frame
  against the NEW idle; yaw-stop areas within ±5%; idle held fraction
  ≥0.92 in hold windows with zero A-B-A flicker; ink = 0 at rest and
  every mark caused; strike spacing audit (final-2 ≥ first-2 tip travel);
  anticipation (coil at release = max, beak path ≈ 0 in the loaded hold);
  step events = ripple events 100%.
- Eyes (the actual gate): full-speed watch of the test episode at
  320×240 and at 800×480; dense frame strips of every action; the
  filled-silhouette test on the model sheet (black silhouette must be
  nameable as a great blue heron, per the craft skill); and a written
  note wherever the eye disagrees with a passing number.

## Build order when the art pick lands

1. Translate the picked direction into outline control-point sets:
   profile rest + hunting coil first, silhouette test, THEN the five
   stops + flight pose → model sheet (deliverable 1).
2. rig13 code implementing the architecture above against those sets.
3. Phase-1 cycles re-derived per CHART_NOTES.md: idle statue, walk,
   strike, eat (big fish — readability first), settle.
4. Test episode ~20–30 s: idle → walk → strike + full eat → settle.
5. Floor audits + eye review; report leads with the blunt self-critique.
6. STOP. Full canon, pose-model retrain, and any device work wait for
   Jimmy's verdict on the phase-1 drop.

## Questions the art pick needs to answer (for Mordecai's round)

- Palette: current 12 tones, or does the pick shift them (the approved
  flat4 direction used a lighter sky neck and a brighter orange bill)?
- Outline: presence and weight (flat4 carries a consistent dark outline;
  the v1.2 rig's 0.8-unit outline was barely visible at device size).
- Plume beard: how prominent — the footage says it is THE feature.
- Feather detail depth: how many scallop rows on the folded wing (1–3).
- The eye: flat4's big cartoon eye, or the real bird's fierce yellow
  eye with black pupil and brow.
