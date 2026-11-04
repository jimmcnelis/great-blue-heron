# Heron v1.2 — Motion-Craft Worklist

Written 2026-11-02 against the craft skill at `~/workspace/custom-skills/cartoon-animation-craft/SKILL.md`.
v1.2 is a **corpus and rig revision**: every item below lives in the authored clips, so the
build is new corpus + retrain on the v1.1 architecture (320×240 master grid, 24 fps corpus,
palette snap at decode). No item here changes the model, the presence contract, the ink law
(ink only when caused, drawn procedurally, never by the net), or the blocking law
(idle in the outer thirds, fishing in the middle third).

Frame budgets below are at 24 fps. "Skill rule" names the section of the craft skill the
item implements. Every check is measured off the final rendered preview file or its episode
grids, not off intermediate tensors.

## The worklist

### 1. Timing charts replace the universal smoothstep

- **Skill rule:** Plan on an exposure sheet and chart the spacing.
- **Now:** every keyframe track in `src11/clips.py` interpolates through one generic
  smoothstep (`_ss`). The strike, the wing stretch, and the alert all share the same
  symmetric ease signature, and impacts ease out into contact instead of accelerating in.
- **Work:** give each clip type a declared chart (a per-track spacing function chosen per
  action: favor-leaving, favor-approaching, linear-for-mechanical, or a hand-set key list).
  The strike charts favor-approaching so the beak covers more distance in its final frames
  and stops dead on contact. Gentle moves keep eased ends. No clip enters the corpus
  without its chart recorded in the clip spec.
- **Pass/fail:** spacing audit on the beak tip across all strike clips: distance covered in
  the final 2 frames before water contact ≥ distance covered in the 2 frames before those,
  in 100% of strike clips. Clip specs list a chart for every clip (count charts = count clips).

### 2. Anticipation: the coil becomes a held, loaded pose

- **Skill rule:** Give every action anticipation, an accent, and a hold.
- **Now:** the aim coil (1.6–2.6 s) reaches full depth, then leaks (coil 1.0 → 0.92 and the
  body rocks forward over 0.55 s) before the neck fires. The audience watches the load
  drain away before the shot.
- **Work:** the coil reaches full depth and *stays* there: ≥8 frames at full coil before
  release, with the final 4 frames showing a micro settle *deeper* (1–2 cells of extra
  crouch) rather than a leak. Same treatment, smaller scale, for the takeoff crouch:
  root drop deepens monotonically for ≥6 frames before launch (v1.1 already crouches;
  make it deepen instead of arriving early and waiting).
- **Pass/fail:** beak-tip movement across the final 4 pre-release frames ≤1 cell in every
  strike clip; coil parameter at release = its clip maximum in 100% of strike clips;
  takeoff root_y monotonic (non-increasing in screen terms) across the 6 frames before launch.

### 3. Authored smear on the strike

- **Skill rule:** Smear what moves too fast to draw.
- **Now:** the neck extension fires in ~3 frames with clean shapes throughout. At that
  spacing a crisp neck strobes; the eye loses the fastest, most important move in the show.
- **Work:** author 1–2 smear frames in the rig at peak extension: the neck and head
  elongated along the strike path (a drawn shape, rendered supersampled like everything
  else, on-palette). Optional companion: broken tapering dry-brush streaks in the ink
  layer at the splash, drawn by the sim with the splash event. No post-process blur.
- **Pass/fail:** every strike clip contains ≥1 smear frame at the peak-extension frame,
  verified on pulled frames from the final file; the clip plays clean at speed (reviewer
  watches the strike at full rate and reports no strobe); freeze frame archived as a record.

### 4. Swallow follow-through: the gulp travels

- **Skill rule:** Follow through on everything loose.
- **Now:** the caught fish swings with a decaying pendulum (good) and slides down on the
  gulp, but the neck itself stops dead at the gulp. The action the audience watches hardest
  ends with a full stop.
- **Work:** after the gulp, run a visible settle down the neck: a small bulge or ripple
  traveling from head to body over ~10 frames, while the head does a short toss overshoot
  and decays (≥8 frames of decaying motion after the gulp across neck, head, and plume
  combined). The fish pendulum decay (already in v1.1) stays.
- **Pass/fail:** in every catch clip, bird-region motion in the neck and head persists
  ≥8 frames after the gulp frame with frame-to-frame amplitude non-increasing in at least
  80% of those frames; no frame after the gulp is a hard freeze before the settle completes.

### 5. Landing follow-through: flare, reach, overshoot, late fold

- **Skill rule:** Follow through on everything loose; Build walks and flights as cycles.
- **Now:** v1.1 lands with a root overshoot (touch at +0.8, rebound to −0.4) and a plume
  decay, but the flap freezes mid-sine at touchdown minus 0.3 s and the wing folds on a
  0.5 s schedule keyed to the clock, not to the feet.
- **Work:** end the approach with one authored braking stroke: wings rise high and hold a
  flare for the final ~0.4 s (this replaces the frozen sine value). Legs swing down and
  reach *forward* ≥0.5 s before touchdown (they already swing late; add the forward
  reach). Keep the root overshoot; key the wing fold to the touchdown event so the fold
  *finishes* ≥10 frames after the feet plant.
- **Pass/fail:** frame audit against the landing event log: flare pose present in the
  final 10 frames before touch; both feet forward of their cruise position ≥12 frames
  before touch; root crosses the rest line and returns within 12 frames after touch;
  wing_amt reaches 0 no earlier than 10 frames after touch.

### 6. Flight cycle rebuilt: asymmetric beat, tip lag, glides

- **Skill rule:** Build walks and flights as cycles.
- **Now:** the flap is `58 * sin(2π * 2.1 * t)`: a metronome. Equal up and down halves,
  constant amplitude from the first beat, no wingtip lag, no glide, and it starts the
  instant the body leaves the ground.
- **Work:** author a real cycle in the rig: downstroke occupies 40–45% of the cycle at
  1.8–2.4 Hz; the wingtip is a separate lagged segment trailing the root by 20–40° of
  phase, so the wing bends through the beat; amplitude envelope across each flight
  (first 3 beats deepest, cruise beats smaller, final approach beat becomes the item-5
  flare); glide holds ≥12 frames with wings set in a shallow dihedral on any crossing
  longer than 3 s; on takeoff the first downstroke begins while the feet are still
  planted. Keep v1.1's wins as gates: neck folded in its tight S with the head back at
  the shoulders, legs trailing as two thin near-parallel lines within ±10° of the body axis.
- **Pass/fail:** phase plot of wing root vs tip angles over one full crossing shows the
  tip lagging by 20–40°; downstroke share of cycle within 40–45%; every crossing >3 s
  contains ≥1 glide of ≥12 frames; gate frame pulled mid-flight reads correctly as a
  filled silhouette.

### 7. Held living idles: stillness becomes the performance

- **Skill rule:** Keep holds alive without letting them drift.
- **Now:** idle micro-life is four perpetual sine waves (periods 3.3–6.9 s) layered over
  root, neck, plume, and head. The bird never holds still, which fights both the animal
  (a statue hunter) and the show's own law that stillness is the default.
- **Work:** replace continuous drift with held poses plus discrete events: true holds
  separated by blinks (every 2.5–6 s, as now), occasional head turns, rare weight shifts.
  Breathing, where wanted, is 2–3 irregular slow swells per 20 s idle at ≤1 cell of
  silhouette movement, never a fixed period. Post-action settles still decay and then
  *stop*. Doze becomes its own authored pose (head drooped onto the folded neck), not a
  damped version of the awake idle.
- **Pass/fail:** held-frame fraction (bird-region change under threshold) ≥60% across
  idle clips; every hunting idle contains ≥1 unbroken still stretch ≥2 s; beak-tip path
  length inside holds between 0.5 and 3 cells per second; a periodogram of root_y over a
  20 s idle shows no single dominant period carrying the motion.

### 8. The turn, drawn

- **Skill rule:** Keep a model sheet and stay on model; Animate pose to pose.
- **Now:** the turn-in-place is a horizontal squash sweep (v1), and head turns still use
  the squash cheat in v1.1 (its own report lists this as a remaining cheat).
- **Work:** author the three model orientations the turn passes through (profile,
  three-quarter, reverse profile) as rig poses, and build the turn as a 12–24 frame
  pose-to-pose clip through them, with the head leading and the body following a beat
  later. Head turns get the same treatment at smaller scope: at least one intermediate
  orientation, no squash.
- **Pass/fail:** silhouette area stays within ±5% of the idle silhouette across every
  turn frame; horizontal scale factor within ±10% on every frame (no squash frames);
  three gate frames (one per orientation) pulled from the final file and read correctly
  as silhouettes.

### 9. The alert becomes a take

- **Skill rule:** Give every action anticipation, an accent, and a hold.
- **Now:** the APPROACH alert (~2.3 s) goes to a tall freeze. It has the accent hold but
  no anticipation beat and no settle out, so it reads as a pause rather than a reaction.
- **Work:** rebuild it on the take formula: 3–4 frames of anticipation (the current
  motion checks, the head dips a fraction), a snap to the tall alert pose within
  2–4 frames, the accent held ≥12 frames (the freeze, now earned), then a settle back
  to idle over ~12 frames. Optional variant for a repeat approach inside a short
  window: a double take (glance away, back, away, accent).
- **Pass/fail:** frame audit of every alert clip in the episode: anticipation dip
  present, accent reached within 4 frames of the snap start, accent held ≥12 frames,
  settle ≥8 frames before the next behavior starts.

### 10. Preen clip: new acting beat

- **Skill rule:** Animate pose to pose; Spend drawings like limited animation.
- **Now:** no preen clip exists (named gap in both the v1 and v1.1 reports).
- **Work:** author pose to pose with a chart: head turns to the shoulder (anticipation
  dip first), two nibbling beats with a held pose between them, one shake whose
  follow-through runs through the plume and chest fringe, settle back to idle.
  Total 4–7 s. One new clip type, built entirely from existing rig parts.
- **Pass/fail:** chart recorded in the clip spec; at least 2 held poses of ≥8 frames
  inside the clip; shake follow-through visible in the plume for ≥6 frames after the
  shake peak; silhouette of the nibble pose reads correctly filled black.

### 11. Walk polish: kill the boot

- **Skill rule:** Build walks and flights as cycles.
- **Now:** the mid-swing leg bunches into a brown "boot" blob in freeze frames (v1's
  weakest still), because the folded leg keeps its full width through the swing.
- **Work:** slim the swing profile (fold the shin tighter against the thigh, point the
  toes down at mid-swing) so the swinging leg reads as a folded stilt, not a boot.
  Keep the zero-slip stance (v1 already plants feet exactly, and ripples fire on plants).
- **Pass/fail:** swing-leg silhouette width at mid-swing ≤1.3× the stance-leg width,
  measured on pulled freeze frames from the final file; foot-plant events match ripple
  events 100% in the episode log; stance slip <0.5 cell per frame.

### 12. Line boil: a decision gate, not a work item

- **Skill rule:** Decide about line boil, never inherit it by accident.
- **Now:** v1 shipped incoherent decode flicker (bird-region reconstruction 88.7%),
  which is accidental boil of the worst kind. v1.1 attacks it with capacity and palette
  snap. Deliberate, authored boil (the hand-drawn signature) does not exist anywhere
  in the pipeline.
- **Work:** none in v1.2 unless Jimmy approves it as a separate experiment. If approved:
  implement it as a deterministic post-decode render layer (coherent per-part silhouette
  displacement, ≤1 cell, redrawn every 2–3 frames, off during accents, never on the ink
  layer), never baked into the training corpus.
- **Pass/fail:** the decision (yes/no, and settings if yes) is recorded in the v1.2
  report either way. If built, the held-segment A-B-A flicker metric with boil on stays
  at or below the boil-off number plus 10%, proving the boil is coherent rather than noise.

## Sequencing

1. Items 1 and 2 first: charts and the held coil change every other clip's feel, and
   authoring smears or follow-through on top of the old easing would bake the mush back in.
2. Items 6 and 7 next: the flight cycle and the idle system are the two largest
   corpus shares.
3. Items 3, 4, 5, 8, 9, 10, 11 in any order: each is a bounded clip-level job.
4. Item 12 whenever Jimmy decides; it does not block the retrain.
5. Full QA battery from the skill's measurement section on the finished preview before
   anything is claimed: spacing audit, anticipation audit, held fraction, follow-through
   counts, slip check, flight phase plot, smear coverage, silhouette gate frames, flicker
   metric, and the ink-at-rest check (zero ink in every idle and empty window).


---

## Amendment — Jimmy's rulings, 2026-11-02 (post-v1.1 verdict; binding on v1.2)

1. **Turns are drawn progressively.** If the bird turns around, the animation draws it through real intermediate orientations (head leads, body follows, stepping feet). No squash cheat, no mirror-flip — "not flip the bird card over." The v1.2 rig must natively support the intermediate yaw orientations the movement study specifies.
2. **Good-but-repetitive beats janky-but-random.** Animations can be mostly static: long holds, stillness as the default. Each behavior resolves to one polished signature cycle that repeats verbatim (or 2–3 discrete hand-checked variants — never continuous procedural perturbation of the motion). Variety lives in scheduling — which behavior fires, and when — not in regenerating motion. Corpus consequence: a small set of high-quality authored cycles with a per-cycle quality gate, not a wide distribution of improvised motion.
3. **Cleanup targets from the v1.1 verdict:** fish-eating sequence (real manipulate → head-first flip → swallow phases, per the movement study), leg articulation in the stalk (joint sequencing, no bunching), drawing cleanliness overall. Resolution stays 320×240 (confirmed right for the BOX-3).
4. **The bar (Jimmy, 2026-11-02 15:21): v1.2 is expected to be VASTLY improved in drawing and animation, following the cartooning skill.** Process consequence: v1.2 is authored from the skill + the movement study from frame one (pose space, per-clip timing charts, drawn turn orientations, signature cycles), and it is graded against the skill's measurable audits (timing-chart conformance, anticipation audit, held fraction, silhouette test, flicker metric) BEFORE Jimmy is shown it. A build that fails its own audits goes back, not to Jimmy.
