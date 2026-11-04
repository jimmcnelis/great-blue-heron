# Heron v1.2 — pose space (report)

**Delivered:** `preview_heron_v1_2.mp4` (320×240, 24 fps, 1,941 frames, 80.9 s,
md5 b2b23f9ca117b1565d15fc6bcc729387) + `preview_heron_v1_2_800x480.mp4` +
`qa_contact_sheet_12.jpg` (yaw stops / eating sequence / turn sequence) +
`qa_results_12.json` + `model12_stats.json` + `episode12_meta.json`.
Sources: `src12/` (rig.py, clips.py, corpus_build.py, train.py, sim.py,
craft_qa.py), built and rendered on the DGX Spark (`~/heron/src12/`).
v1/v1.1 files untouched.

## Architecture — what changed

v1.1 learned PIXELS (a conv autoencoder over rendered frames). v1.2 learns
POSE: an MLP autoencoder (34 continuous pose params + fish code → latent 24
→ decode) whose latent space is the rig's own parameter space. The rig
renders; the model never touches a pixel at playback. The shipped episode
plays AUTHORED pose trajectories (the canon) verbatim — Jimmy's axiom:
good but repetitive beats janky but random; variety lives in scheduling
(which clip, which zone, how long the holds), never inside a clip.

Canon: 27 signature cycles, 3,243 frames, each authored as a timing chart
from `movement-charts.yaml` — no universal ease anywhere; every segment
names its own spacing (the strike's release uses explicit per-frame
fractions 25/35/40; saccades are linear-ballistic; holds are literal frame
repeats). Corpus with zone-offset scheduling copies: 7,393 pose rows.

## What the rig gained (src12/rig.py vs src11)

- **Yaw, drawn**: five authored orientation stops (0/45/90/135/180°) with
  body width/height factors, neck-base migration and centring at front,
  folded-wing side bulges at front, hip spread, tail swing, a far eye that
  appears as the head turns. Two construction bugs found and fixed by
  measurement: the body tilt now flips sign with facing (before, yaw 180
  put the neck base 11 units lower and +260 PALE cells — it was not a
  mirror), and a cubic-bezier weight typo (3(1−t)t³ for 3(1−t)t²) that had
  been dragging every neck and plume curve toward the frame origin.
  After fixes, yaw 180 mirrors yaw 0 to 237 differing cells above the
  legs (the residue is world-anchored feet + fringe tooth phase).
- **beak_open**: a real gape — the bill opens across the last two release
  frames (~1/30 s before impact, as measured in the literature) and
  closes ON the fish (a grab, not a spear).
- **Fish as state, in all phases**: (grip point along the bill,
  orientation crosswise↔head-first, authored free-arc). The v1.1
  corpus-builder toss patch is abolished — the toss is chart data,
  anchored through the rig's own beak-tip readout.
- **neck_bulge_pos/amp**: a localized bulge travels the neck tube during
  swallow_travel (width multiplier, gaussian along the tube).
- **flap_tip**: wingtip tracked separately, lagging the root by exactly
  2 frames; the flight beat is authored 5f down / 7f up (2.0 Hz), not a
  sine.
- **Toes** (leg_*.toe): trailing in swing, flat at plant, curled in the
  one-leg tuck — and the tuck is DRAWN (foot folded up under the belly),
  where v1.1's hide_near made the leg vanish. look_back is retired;
  looking back is head_yaw drawn through its 3/4 stops.
- **Plume mass**: the chest fringe (the kayak bird's shaggy "beard")
  widens and lengthens toward front views, per footage batch 2.

## Measured footage adopted (Jimmy's pier/kayak/patio library, 9 clips + 1 still)

- **Landing tightened**: chart-canonical 120f → **84f**. The real bird is
  settled in ~2.3–3.5 s. Structure kept: glide, flare, legs reach,
  touchdown, wings MANTLED ~0.7 s for balance (footage #5), momentum
  step, fold last. (Deviation from the charts, flagged per the steers:
  measurement wins.)
- **Swallow redistributed inside its canonical 118f**: the toss-flip's
  airborne window is ~6 frames (footage #6 measured ~0.2 s airborne —
  do not stretch it) and head-work (work_back + head_back) tightened
  26f → 20f (measured 0.6–0.8 s). Catch→settled across strike+swallow
  ≈ 170f ≈ the measured ~7 s. The neck bulge could NOT be resolved in
  the footage — it stays chart-canonical, flagged as such.
- **Takeoff** (footage #7, three measured takeoffs consistent): brief
  gather, neck STRETCHES STRAIGHT during the first beat before folding,
  feet clear ~0.7–0.9 s in, legs trail. Departure ink = churned patch +
  expanding ring persisting 7+ s — implemented as the InkSim churn spec.
- **Turn validated**: real 90° turn ≈ 2.3–2.8 s, head leading by
  0.5–1.0 s through a genuine 3/4 — consistent with the 72f canonical
  180°. The clip's front/3/4 frames are the rig's stop reference
  (narrow body, centred neck, legs close).
- **Ruffle** (patio #3) and **balance wing-flick** (kayak #5) added to
  the canon as signature cycles; the ruffle plays in the episode after
  landing.
- **Stillness floor**: 15+ s statue holds measured (dock edge) —
  idle_hunt's holds are built to run that long in scheduling.
- **Swimming** (footage #8/#9) and the **plunge strike** (footage #6)
  are real behaviors of this bird but outside the sim's scene law
  (a standing bird in the shallows); noted here for a possible future
  swim-in entrance variant. Not in the core loop.
- The wading neck-spear strike and a resolvable bulge swallow remain
  unfilmed; the wading strike stays chart-canonical.

## Self-grading — the skill's audits, run on the finished build

All numbers measured on rendered frames / pose tracks by
`src12/craft_qa.py` (full dump: `qa_results_12.json`). v1.1's known
failures alongside, per the gate instructions.

| Audit | Gate | v1.2 | v1.1 |
|---|---|---|---|
| Yaw stops silhouette area | ±5% of profile | **−3.8% … +0.5%** PASS | no yaw existed (facing faked) |
| Turn: area on EVERY frame | ±5% | **max 4.94%** PASS (worst frame = the 1-frame saccade transient) | turn was a squash cheat |
| Turn: head world-yaw error through pivots | ≤10° | **0.0°** (counter-stabilized by construction) | n/a |
| Strike spacing (final-2 vs first-2 tip travel) | final ≥ first | **106.3 ≥ 30.2 cells** PASS | no spacing audit existed |
| Anticipation: coil at release = clip max | = | **1.0 = 1.0** PASS; beak path across loaded hold **0.0 cells** | anticipation LEAKED (coil decayed 1.0→0.92, body rocked 0.55 s early) |
| Smear frames per strike | exactly 1 | **1** | n/a |
| Beak open at contact | ≥0.9 | **1.0** | bill could not open at all |
| Idle held fraction | ≥0.92 (chart) / ≥0.60 (skill) | **0.950** | idle was 4 perpetual sine waves — never held |
| Flicker in hold window (A-B-A / 1000) | ~0 | **0.0** | one-cell edge flicker throughout |
| Flight: tip lag | 2 frames | **2** | flap was a pure 2.1 Hz sine, no tip lag |
| Flight: downstroke share | 40–45% | **41.7%** | metronome sine |
| Swallow: bulge visible run | ≥12 consecutive frames | **20**, pos monotonic ✓ | no bulge existed |
| Swallow: fish orientation at head_back | 0 (head-first) | **0.0** ✓, fish inside from frame 70 | 5 of 7 eating phases missing/faked — "eating the fish is messy" |
| Walk: foot-lift apex | ≤8 units | **7.0** | 21 units — "the marching step" |
| Walk: head world-x drift during body passes | ≤1 cell (chart) | **0.0 cells** both passes | head rode the body |
| One-leg: leg-cell ratio tucked vs standing | no vanish | **1.005** (fully drawn) | leg vanished (hide_near) |
| Scratch: foot↔head distance | <6 units | **3.8** | scratch absent |
| Doze vs idle silhouette difference | must differ | **0.425** of bird cells | doze absent |
| Landing gates (flare late, feet forward ≥12f, fold ≥10f after touch) | all | **PASS** (fold completes 39f after touch) | landing froze a flap mid-sine |
| Takeoff gates (downstroke before feet-off, dangle ≥8f) | all | **PASS** (dangle 19f, neck stretch 0.45) | liftoff beat skipped |
| Ink at rest (below-surface INK, no marks alive) | 0 | **0**; 33 caused events (18 ripple / 3 splash / 5 ring / 6 drip / 1 churn) | ink at rest 0 ✓ (kept) |
| Blocking (span centroid x) | thirds law | L 0.21–0.25, C 0.48–0.52, R turn 0.70, fishing at C ✓ | zones on law ✓ (kept) |

**No audit ships failing.** Two measurement notes: the turn's 4.94%
worst frame is the gaze-saccade frame (the turned head foreshortens) —
inside the gate but with the thinnest margin in the battery; and the
flight loop-wrap delta (17.2°) is exactly one authored downstroke step,
i.e. the cycle's own spacing, not a discontinuity.

## The learned model (honest numbers)

Pose-space MLP autoencoder: 41,018 params (34 pose dims + fish code →
latent 24), trained on 6,697 pose rows; held-out = five ENTIRE clips
never trained (swallow_tiny, turn_reverse, glide, balance_flick,
idle_hunt_c; 696 frames). Roundtrip (decode a held-out pose → render →
compare with the direct render): **cell accuracy 97.8%, bird-cell
accuracy 75.1%**. Worst reconstructed params: head_yaw (RMSE 8.4°),
root_x (6.8), yaw (4.4°).

Context that matters: v1.1's 99.53% bird figure was frame-level
validation on same-distribution pixel data; v1.2's 75.1% is whole
UNSEEN CHOREOGRAPHIES reconstructed through a 24-dim bottleneck — a
deliberately harder test, and the number that would govern a future
generative player. The shipped preview does not pass through the
autoencoder: it plays the authored canon exactly, so episode fidelity
is the audit table above, not this section.

## Episode (80.9 s)

idle@L → walk → tiny strike + full eating → idle → stretch → walk →
**TURN@R** → takeoff (facing left) → empty (churn ring persists) →
landing@L → ruffle → statue → **APPROACH alert** → watched walk →
big strike + THE eating sequence → closing statue with the slow scan.
Presence events: ROOM_EMPTY f1052, APPROACH f1352, PRESENCE_SUSTAINED
f1376 (episode12_meta.json has the full span/ink log).

## Honest remaining weaknesses

- **The bulge is subtle at 320×240.** It measures correctly (amp >0.2
  for 20 consecutive frames, traveling monotonically) and reads as a
  thickening low in the neck on inspection, but it does not pop at
  this grid. If Jimmy wants it unmistakable, the fix is a rig change
  (amp scale), not a chart change.
- **Front stop is the least characterful.** Head small, beak a
  foreshortened wedge — true to the pier footage's front frames, but
  the bird's personality lives in profile. The turn passes through
  front in ~15 frames, so exposure is brief.
- **Head-lock reads oddly in stills.** The walk's translational hold
  is measured perfect (0.0 cells), but a freeze frame shows the neck
  compressed as the body passes under the locked head. In motion it
  reads as the stalk; in a still it reads as a tuck.
- **The strike's body stays statuesque** (chart: body rock ≤3°). The
  neck does all the acting. Real birds commit more shoulder; the chart
  is the law I was given, flagged for a possible v1.3 chart revision.
- **Pose-model generalization (75.1%)** is the weakest number in the
  build — see the model section. The canon-first architecture was
  chosen precisely so this number doesn't gate what Jimmy watches.
- **Line boil: OFF, not built** (Jimmy's option, default off per the
  brief). Nothing in the corpus or renders is boiled.

## Files

- `preview_heron_v1_2.mp4`, `preview_heron_v1_2_800x480.mp4`
- `qa_contact_sheet_12.jpg`, `qa_results_12.json`, `model12_stats.json`,
  `episode12_meta.json`, `model12.pt`
- `src12/` — rig.py / clips.py / corpus_build.py / train.py / sim.py /
  craft_qa.py (mirrored on the Spark at `~/heron/src12/`, with
  corpus12_poses.npz + anchors12.json + run logs)
