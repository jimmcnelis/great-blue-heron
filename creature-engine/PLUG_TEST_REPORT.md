# Plug Test Report — creature #2 (and #3) through the engine

Run 2026-11-02 on this VM (no Spark needed; no torch — the trainer stage is
Phase 4 and was not part of this test). All commands from
`~/workspace/creature-engine/`.

## What was plugged in

| Piece | Package | New code written |
|---|---|---|
| Frog | `packages/pond-frog/` | species.yaml, rig.py (rigcore shapes), clips.py (6 clip kinds), behaviors.yaml, model sheet |
| Firefly | `packages/firefly/` | species.yaml, rig.py (glow dot), clips.py (4 kinds), behaviors.yaml |
| Pond Edge | `packages/pond-edge/` | environment.yaml only — a *different law*: one static shore line, no clip plane, a water band for caused marks |
| Scene | `packages/pond-scene/` | scene.yaml — 2 characters, input bus, 1 proximity interaction, smoke episode |

Deliberate differences from the heron, to stress the seams: stage 96×72
(heron: 120×90), grid 96×72 (heron: 160×120), a static mark (heron: none),
no clip plane (heron: surface plane), air events (heron: surface only),
a second full character.

## Results (measured)

**Validation:** both scenes schema-validate and load:
`pond-scene: chars=[frog, firefly] env=pond-edge style=flat-storybook design=96x72` ·
`heron-scene: chars=[heron, fish] roster=87 palette=12`.

**Corpus build** (`engine.run corpus`): frog **886 frames / 21 clips**,
firefly **258 frames / 5 clips**, wall time **3.9 s**. Zero engine edits
after the package files were written.

**Episode** (`engine.run episode`): **201 frames @ 12 fps** —
frog idles → firefly drifts in on a parallel track → frog alerts → tongue
snap (firefly track switches to `gone` at the catch frame) → croak → hop
to the left perch (landing event → ripple in the water band) → settle.
Outputs: `plugtest-out/pond-episode/episode.mp4`, `episode_grids.npy`,
`episode_log.json`, `contact_sheet.jpg` (visually verified: frog reads as
a frog at display size; tongue, throat sac, mid-hop leg extension, catch
ring all legible).

**QA** (`engine.run qa`, style pack = the heron's flat-storybook pack,
reused unchanged):

| Check | Result | Measured |
|---|---|---|
| palette_exactness | pass | 11 merged values, all < palette size 11 |
| ink_at_rest | pass | 0 ink cells in quiet tails (idle/gone segments) |
| event_causality | pass | 2/2 mapped events produced marks (snap ring, land ripple) |
| join_smoothness | pass | max join 89 vs median change 13.5 (limit 10×) |
| held_fraction | pass (warn-level) | 0.653 held in idles (skill floor: 0.60) |
| flicker_metric | pass (warn-level) | 0.07 A-B-A flips / 1000 cell-frames |
| silhouette_test, anticipation_audit | not_implemented | reported honestly; Phase-4 QA pack |

**Behavior policy** (`engine.run schedule`, 1 simulated hour):
frog unwatched → 90 triggers (65 croak, 25 hop); frog **watched → 229**
(182 croak, 47 hop): the pond gets chatty for an audience, from pacing
data alone. Heron package through the same code: unwatched → fish 2,
flight 3; **watched → fish 21, flight 0** (suppressed by absence of a
watched pacing entry) — the v1 report's prose table, executable.

**Heron adapter parity** (`plugtest-out/parity_test.py`): engine-built
`idle_L_0` frame 0 is **byte-identical** to a direct v1 render; mirrored
variant is the exact flip; the `toss_patch` hook consumed the toss event
(meta events: splash, drips) and the fish renders post-catch; the
`turn_squash` hook narrows the bird 59 → 8 → 58 cells across the turn.

## Where the seam held, where it tore

**Held:** package loading/validation; design-space/grid independence;
roster-as-data with mirroring/splits; hooks (frog needed none, heron's two
v1 special cases became package code without touching v1); parallel
multi-character tracks + merged palette; effects through a foreign
environment's causality table; behavior pacing/modes; QA pack reuse across
species.

**Tore (all fixed in the engine or the data, none in a species):**
1. `event_causality` inherited v1's assumption that marks live at the
   surface — the tongue snap's ring is in the air. Generalized: marks are
   checked near the event's own position. (Debt-list material; fixed.)
2. QA style params collided with data kwargs (`segments`) — renamed the
   style param to `segment_filter`.
3. `ink_at_rest` initially audited action-segment tails (a landing ripple
   is *supposed* to be there) — now filtered to quiet segment kinds, as
   v1's hand-written QA implicitly did.
4. Two schema defects of mine, caught by the validator doing its job
   (`frames` shape; `play` map shape) — schemas were fixed, packages
   needed no changes.

**Not exercised (by design, stated plainly):** the trainer stage (no torch
on this VM; Phase 4 parameterizes v1's `train.py`); the heron corpus
through the engine at full scale (parity was proven on 3 representative
clips incl. both hooks; a full 173-clip build is a Phase-2/4 run on the
Spark); real-time (unscripted) episode playback — the policy sampler is
proven, the player loop is Phase 3.
