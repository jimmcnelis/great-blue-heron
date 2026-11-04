# Track B living-bird phase — report (2026-11-03)

Scope: the three Track B charts the roster lacked, a creature-engine
behavior package implementing the deep-dive's corrected ethogram, and
one measured simulated day with a watchable preview. Decoder: Fix-1
step-6000 (`~/art2route2_fix/ckpt/last.pt` on the Spark), same render
and QA path as the accepted roster. Line boil OFF. No device port.

## 1. Charts added (roster now 20 charts, 2,004 frames)

Builders: `~/workspace/heron/art2/roster_charts_trackb.py`.
Registered in `~/workspace/heron/movement-charts.yaml` (full entries
with phases, gates, variants). Frames + `qa_<chart>.json` in the
roster tree; contact strips `contact_<chart>.png`; `qa_summary.json`
regenerated over all 20 charts.

### relocate — 120 f (post-strike walk-off, root 40 → 95)
- Checkerboard **PASS** (max |index| 0.0072, gate 0.01). Head
  **PASS** (min occupancy 0.077, gate 0.041; zero failed frames).
- Texture: frames 0–100 in band; **f101–119 dip to 0.019–0.025**
  (band floor 0.025) — the final step, at root 95. This is a
  position effect, not a chart defect: the canonical root-95
  translations measure the same (strike_at_R min 0.0188,
  swallow_at_R 0.018, takeoff_at_R 0.015). Visually the last step
  reads identical to the rest of the walk.
- Legs: near max 13.0 px (gate 11; canonical strike measures 11.5),
  62/120 frames flag the raw per-frame gate — the metric is noisy
  roster-wide (accepted idle_hunt flags 174/480) and the far-leg
  flags here are the folded-swing measurement artifact (max 62.5;
  shipped oneleg 59.5 and scratch 60.5 are the same class). Strip
  verdict: the gait reads — alternating plants, folded swing leg,
  toe-first places, statue stagger at both ends.
- **Two authoring defects were caught and fixed before delivery:**
  (1) the first build world-locked the head (a step_cycle
  convention) — over 55 units the neck stretched back toward the
  start stand; caught on the contact strip. (2) The first fix wrote
  hx as a world coordinate; hx is root-relative, that render
  collapsed (texture ≈ 0.001) and was discarded. Delivered chart:
  head carried with the body at the statue offset with a per-step
  bob. Both failures are documented in the chart entry and the
  builder's docstring.

### body_shake — 152 f (standalone shake, statue at root 40)
- Checkerboard **PASS** (0.0042). Head **PASS** (min 0.092 — the
  strongest head metric of the three new charts; zero fails).
  Texture **PASS** on all frames (0.0328–0.0413).
- Legs: near 11.0 (at gate), far 10.5 (gate 8) — in family with the
  shipped statue charts (strike 9.5, alert 9.5, doze 9.5 far).
- Visual: erection reads as a modest puff (plume_sway 1.8 kept
  moderate against out-of-distribution risk); the shake itself
  (root ±0.7, head_roll ±5, 16 f period) is subtle in stills and
  reads in motion. **Bridge gap (documented in the chart):** the
  ethogram's wing in-out beat has no folded-mode channel in the
  shipped art bridge — same class as head_yaw/fish/blink. The shake
  is carried by root/head/plume channels.

### strike_miss — 64 f (the common strike outcome, ~44%)
- Checkerboard **PASS** (0.0043). Texture **PASS** (0.0261–0.0397).
- Head metric fails on **frames 24–38, 42, 46, 48, 54** — the
  max-neck-extension window, the same signature as canonical strike
  (16 failed frames in the same window): at full extension the head
  renders thin inside its conditioning polygon; head and bill are
  visibly present in sequence on the contact strip. Named, not
  dropped.
- Legs 11.5/9.5 with 11 flagged frames — numerically identical to
  strike, as expected: frames 0–27 are strike's own code path, and
  the withdrawal geometry is shared. No fish keys anywhere; the
  grab dwell closes the gape on nothing, then a 12 f head-shake
  (3 decaying oscillations) before recovery.

## 2. Behavior package

In the species package (engine core untouched — **no engine gap
found**; the gaps are all in the art bridge, listed in §4):

- `packages/great-blue-heron/behaviors_trackb.yaml` — every Track B
  parameter as data: held-frame target, lognormal gap/bout/strike
  distributions, success 0.56, big-fish share 0.13 of hits,
  relocation probability and mandate, satiation windows, tide
  rate band (×0.75–×1.45), light weights, maintenance order and
  early-stop probabilities, alert ladder, flight caps. The v1
  `behaviors.yaml` is untouched; its watched-mode pacing boosts are
  explicitly NOT carried over (deep-dive §3.4: theatre knobs).
- `packages/great-blue-heron/scheduler_trackb.py` — the day
  scheduler: world model (light phases, semidiurnal tide), a
  frame-classified timeline (held frames derived from each chart's
  own phase data; holds counted, never expanded), bout machinery
  for hunt/loaf/maintenance, the strike sequence (hit/miss → big
  check → drink beat → relocation), flight moves, the graded
  alert ladder, and scripted disturbance inputs.
- `packages/great-blue-heron/sim_day.py` — measurement + preview
  assembly (measurement is taken off the scheduler timeline, never
  off the sampled preview).

Sim geography (an honest stage, forced by a bridge limit proven
visually this phase): the yaw-180 bridge renders the bird facing
RIGHT — there is no westward profile in the shipped art. So the day
plays between the creek stand (root 40, strike family native) and
the east stand (root 95, strike family as +55 translations);
ground travel east is the relocate walk, returns west are flights
(takeoff_at_R → flight_cycle/glide → landing at root 40). Twelve
root-translated asset renders were made for the sim and QA'd by the
same path (`roster/sim_assets/`, frames + `qa_*.json`).

## 3. Simulated day — measured (seed 20261015, sim date Oct 15)

Full log: `roster/sim_day_log.json` (includes the event stream).
Preview: `roster/sim_day_preview.mp4` — 1024×600, 24 fps, 16,336
frames, 680.7 s (11 min 21 s), 70.7 MB, verified by ffprobe and by
frame pulls (stands sit in the 1st/3rd thirds, captions track sim
clock + behavior + light/tide; the flight frames show the roster's
known weak tail, rendered as-is).

| Target (deep-dive) | Measured | Verdict |
|---|---|---|
| Held frames ≥ 90% of the day (§3.1) | **98.83%** (2,049,254 / 2,073,603) | PASS |
| Strike success ≈ 0.56 [Hodgens] (single-day band 0.46–0.66) | **0.368** (7 hits / 19 strikes, 12 misses) | **MISS** — see note |
| Strikes ≈ 4/h of hunting [Hodgens] (design band 3–6) | **3.17/h** (19 strikes / 6.0 hunt-hours) | PASS |
| Hunting 30–50% of waking hours [Brandman] | **48.6%** (359.8 of 740 waking min) | PASS (top end) |
| Relocation after ~every strike [Warrick] (≥ 0.80) | **1.00** (19/19: 10 walks, 9 flights) | PASS |
| Maintenance 2–5 bouts/day, ordered stretch → shake → preen | **2 bouts**, both full sequences (+scratch tail) | PASS |

Note on the success MISS: the model draws hits at p = 0.56 by
construction; 7-or-fewer hits in 19 strikes is a ≈ 4.6% draw — an
unlucky day, reported as measured, not re-seeded. A 7-day ensemble
(seeds 20261016–22, same frozen design) gives success median 0.50,
range 0.35–0.82. The ensemble's other medians: held 98.6%
(98.2–99.3), strikes/hunt-hour 3.28 (2.96–4.07 — one day a whisker
under the band), hunt share 0.346 (0.231–0.476 — one day under the
band), relocation share 0.88, maintenance bouts 2 (1–4).

Rest of the day's log: bouts — hunt 11, loaf 7, maintenance 2.
Minutes by behavior — doze 698, hunt 356, inter-bout gaps 274,
loaf 105, maintenance 2.7, flight 2.3, relocate 0.8, alert 0.2.
Flights: 12 moves — 9 relocation, 2 discretionary reposition (the
0–3/day band is for discretionary flight), 1 flush. Shakes after
landing: 9 of 12 (p = 0.7). Drinks: **0** — no big fish this day
(0 big hits against ≈ 1.4 expected; Poisson luck). Alert ladder,
from the three scripted disturbances: brief → freeze-check only;
sustained → freeze-check + alert; escalating → freeze-check + flush
(the bird was at the east stand, where escalation caps at flush —
no alert chart is rendered for that stand; disclosed in §4).
Inter-bout gaps: median 10.6 min, p90 39.4, max 46.1 (design
lognormal median 16; measured lower because gaps are capped by
scripted events and light-phase boundaries).

Tuning disclosure: after a first measured pass, three
estimate-grade knobs were adjusted — strike-gap median 13 → 11 min,
maintenance base weight 0.22 → 0.5, maintenance refractory
150 → 120 min — then the design was frozen; the reported day and
ensemble use the frozen configuration throughout.

## 4. Gaps and disclosures

- **Engine core: no gap found, no edits made.** Everything this
  phase needed fit in package data + package code.
- **Art-bridge gaps (pre-existing, now documented in the charts):**
  no render channels for head_yaw, fish, blink, smear (smear is
  carried in pose data only); no folded-wing in-out channel
  (body_shake); no westward profile (yaw-180 renders facing right —
  sim geography designed around it).
- Freeze-check is assembled from alert frames 0–7 + a hold of
  frame 7 + settle frames 43–60 (creek stand); at the east stand
  it is a statue hold, and escalation there caps at flush.
- The drink beat is a replay of swallow frames 12–29 (the neck-dip
  segment); it did not occur on the measured day.
- Doze and one-leg exits are hard cuts in this proof — the charts
  define exits as reversed keys for the engine player; no exit
  charts were rendered.
- Scripted disturbances are processed at decision points: the
  07:04 brief disturbance fired ≈ 7 min late, when the running
  loaf bout ended. A live input path would interrupt; this proof's
  scheduler polls.
- stretch_at_stand ends 2 units off the statue root (the chart's
  authored weight_shift); body_shake therefore starts with a
  2-unit hinge. Visible only as a slight settle into the shake.
- The preview is bird-layer only: ink effects (ripples, splashes)
  are the engine episode player's layer and are not composited
  here. Preview frames carry a small burned-in caption (sim clock,
  behavior, light/tide) — a proof annotation, not device art.
  Sampling convention: action clips at full 24 fps; idle/doze
  cycles 1 frame per 4 s; holds 1 frame per 30 sim-seconds.
