# Heron v1.3 — CHART RE-DERIVATION NOTES (phase 0)

Timings re-derived FOOTAGE-FIRST from the measured library
(`~/workspace/heron/reference/footage/README.md` — 9 clips + 1 still of
Jimmy's own bird). Where footage is silent, the movement study
(`heron-movement-study.md`) and `movement-charts.yaml` are evidence, not
law: v1.2 adopted them literally and earned "slightly better."
Each entry: measured truth → what v1.2 did → the eye's verdict on v1.2
(frame strips pulled from `preview_heron_v1_2.mp4`, 2026-11-02) → the
v1.3 derivation. Nothing here presumes the final drawing.

## Idle / statue

- Measured: 15+ s motionless at the dock edge (clip 01, 42.7–58 s);
  micro head events only. Event vocabulary across the library: blinks,
  3-frame gaze saccades, a held sideways glare-cock, an inspection peck
  at the deck (clip 05), the ruffle as an occasional statue-breaker.
- v1.2: 480f script (holds + blink/saccade/roll script) — content right.
- Eye: the EPISODE sliced the script (264f opening, 48f later), so the
  statue the viewer got was arbitrary fragments. Scheduling flaw, not a
  chart flaw.
- v1.3: author holds as schedulable units (statue scripts of complete
  event arcs); never slice mid-script. Holds stay literal repeats —
  static-first is the animal truth, not a compromise.

## Walk / stalk

- Measured: dock crossing ≈25 s (clip 01) — steps are SLOW with long
  freezes; head level and spatially steady; breast plumes swing; on the
  kayak (clip 02) careful placement with body-pitch corrections.
- Study: step…freeze…step; swing folds at the ankle (not a backward
  knee); foot lift ≈7 units; head locked while the body passes under.
- v1.2: 24f steps, 6f inter-step freezes, stride 14; head-lock by
  neck_sway counter-shift (audit: 0.0 cells of head drift — a pass).
- Eye: FAIL. The counter-shift buckles the neck into a hunched,
  preening-looking S for whole seconds (walk strip rows 2–4), and 6f
  freezes at a brisk stride read as a stutter, not a stalk.
- v1.3: keep the 24f step mechanics and the ≤8-unit lift; freezes
  18–48f as SCHEDULING (the cycle stays pure); head steadiness by
  construction — the head holds a world-space target and the neck
  outline solves to it; pace from footage (a zone crossing should take
  ~6–10 s of screen time, mostly frozen).

## Strike (wading)

- Measured: NOT FILMED wading. The filmed strike (clip 06) is a perch
  PLUNGE: ≥6 s aim, whole-body launch, entry 0.6–0.8 s after launch.
  Scene law keeps the wading neck-spear; its timings stay study-based
  and are flagged as the least-grounded numbers in the canon.
- Study: coil deepen (monotonic, no leak) → loaded hold (beak-tip
  ~still) → release ≤4f accelerating → grab (bill opens ~1 frame before
  contact, closes ON the fish).
- v1.2: chart-faithful; audits pass (spacing 106 ≥ 30 cells; 1 smear).
- Eye: the extended neck renders as a wide pale PLANK — a kite-shaped
  wedge from body to water with a tiny head at the end; and the body
  stays statuesque (rock ≤3°), so the strike reads as a statue tipping
  a plank, not a hinge snapping. At 320 wide the splash ink carries
  more of the moment than the bird does.
- v1.3: neck outline narrows with extension (authored width profile);
  the body commits — a real forward rock of the whole torso at release
  (the study's own lead/lag allows the body to follow the neck; the
  ≤3° cap was v1.2's over-literal reading); keep the release spacing
  and the bill timing exactly.

## Eat (after a wading catch)

- Measured (clip 06 phases): grapple ≈1 s; toss airborne ≈0.2 s
  (~5f at 24 fps); re-catch head-first; swallow head-work 0.6–0.8 s;
  catch→settled ≈7 s total (perch context).
- Study §6 phase order: secure-shake → dip → toss-flip → work-back →
  head-back → traveling bulge → settle with beak claps.
- v1.2: all phases present; toss 6–8f (right); bulge 20f monotonic.
- Eye: (a) the bulge is INVISIBLE at 320×240 — it audited and did not
  read; (b) during work-back the fish dangles below the bill like a
  leaf instead of lying along the bill axis; (c) the dip overshoots
  into a bow; (d) at tiny-fish size the entire eat is a speck moving
  near a statue — unreadable.
- v1.3: bulge becomes an outline-level throat swelling sized to read,
  or the sequence lets head-back + claps carry the swallow and stops
  claiming a bulge; fish rides the bill axis, half-shadowed by the
  gape; dip shallower; phase-1 test uses the BIG fish (readability
  first, tiny is a scheduling variant).

## Turn

- Measured (clip 01): 90° in ≈2.3–2.8 s; head leads by 0.5–1.0 s; body
  follows through a genuine 3/4; front is a PASS-THROUGH.
- v1.2: 72f for 180°; audits pass (area max dev 4.94%, head world-yaw
  error 0.0°). BUT the pivot feet never travel — the fx "shift" patch
  in src12/clips.py sets each foot's fx to its own current value (a
  no-op); only a small lift is drawn.
- Eye: FAIL. The body morphs through a front-facing totem (bulge-ellipse
  ears, fringe skirt) that occupies ~30 frames; feet stay glued. It is
  a rotation of a drawing, not an animal turning.
- v1.3: turns are authored outline sets per stop (PLAN §4); feet
  re-plant around the pivot with authored fx/fy per step, alternating;
  prefer 90° turns in scheduling (the measured behavior — the 180°
  remains available); head lead 12–24f before the body starts.

## Alert

- Measured: head-up snap from statue (kayak clip 02 upright phase;
  patio clip 03 freezes).
- v1.2: 4f check-dip, 3f snap, 36f held accent with one saccade, 18f
  settle. Structure right.
- Eye: not isolated in strip review — flagged WATCH item for phase 1
  (settle may read as a slow slump; check at full speed).

## Takeoff

- Measured (clips 07/08/09, three consistent): gather ≈0.4 s; neck
  stretches STRAIGHT during the launch; feet clear 0.7–0.9 s after the
  first beat; 2–3 deep beats and the bird is GONE; churn ring 7+ s.
- v1.2: 96f, 7 beats, long near-vertical climb out of frame.
- Eye: FAIL twice — duration (floaty vs the measured snap) and drawing
  (wings read as a rear fin; trailing legs dominate like a comet).
- v1.3: ≈48–60f in-episode (gather ~10f, 3 beats, exit); full
  crossings, when wanted, are a separate flight cycle + glide
  insertion, not a stretched takeoff. Wing drawing rebuilt (PLAN §6).

## Landing

- Measured (clips 01/04/05): appearance→settled ≈2.3 s; flare ≈0.5 s
  with wings HIGH and legs dangling as thin lines; touchdown; wings
  MANTLED ≈0.7 s for balance; two fold beats; statue by ≈3.5 s.
- v1.2: 84f with that structure.
- Eye: timings fine; drawings failed (flare = one blade; mantle = the
  blue egg at its purest). Keep the timing skeleton, redraw the shapes.

## Flight (crossings)

- Study: authored beat 5f down / 7f up at ~2 Hz, tip lag 2f, glide
  ≥12f inserted on crossings >3 s, neck folded tight S, legs trailing
  as thin near-parallel lines.
- v1.2: rhythm implemented and audited (tip lag 2f, downstroke 41.7%).
- Eye: rhythm unjudgeable — the wing shape never reads. Redraw first,
  then re-judge the rhythm at full speed.

## Ruffle / balance flick / preen / doze / one-leg

- Ruffle measured ≈3 s hunched shake (clip 03): v1.2's fluff was an
  interior wing nudge (wing_amt 0.16) that barely reads — fluff must
  change the SILHOUETTE. Re-derive as an outline event.
- Balance flick (clip 05, ~31 s): half-open wing while repositioning —
  keep as a micro-behavior, timing as authored in v1.2 was fine.
- Preen / doze / one-leg: no footage, no strip evidence of failure
  beyond the shared drawing system; they re-author with the new rig in
  the full canon (post-verdict), timings from the study as evidence.

## Open items the footage cannot settle (stated plainly)

- Wading strike timings (unfilmed) — study-based, flagged.
- Bulge visibility (unresolvable in footage) — a drawing decision.
- The front stop's exact look — pier front frames exist (clip 01,
  35–37 s) and are the authority over any chart description.
