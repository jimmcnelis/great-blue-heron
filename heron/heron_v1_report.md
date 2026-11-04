# Heron Simulation v1 — Phase 1 Report

Built 2026-11-02 on the DGX Spark (`~/heron/`). Deliverables mirrored here:
`preview_heron_v1.mp4` (master render), `preview_heron_v1_800x480.mp4` (product-aspect variant),
`qa_contact_sheet.jpg`.

## What was built

- **Rig** (`src/rig.py`): programmatic layered vector rig (PIL, 4× supersampled, majority-downsampled
  to palette indices — colors exact by construction). Authored in a **normalized 120×90 design space**:
  body + folded/stretch/flight wing, tapered Bézier S-neck (upright / coiled / strike presets), head with
  white face, black cap band + plume, blink state, orange dagger (≈ shin length), chest-fringe zigzag,
  black shoulder patch, two 3-segment IK legs (rusty thigh → dark shin → tarsus), two fish (tiny, big).
  Water is **never drawn**: everything below the surface row (just below the knee) is clipped to white.
- **Corpus** (`src/clips.py`, `src/corpus_build.py`): keyframed clips at 12 fps — idles (with head turns,
  look-backs, dips, blinks), one-leg idles, procedural zero-slip walks (1.6 s cycle, ~9.5 cells/s,
  foot-plant events), strikes (1.6–2.6 s aim coil → ~0.15 s strike → toss/swallow with drip window;
  tiny ×6, big ×4, miss ×2 seeds), aim-relax, wing stretches, takeoffs, fly-ins, **turn-in-place clips**
  (squash-sweep facing change), **alert clips** (presence response), and an all-white empty clip.
  Every clip also rendered mirrored. **21,980 frames / 173 clips.**
- **Model** (`src/train.py`): convolutional autoencoder on one-hot palette frames, **latent 48,
  1,949,468 parameters**. Dynamics: PCA-32 on corpus latents (97.65% variance) + per-dimension AR(2)
  fitted on idle residuals. Per the portrait v2.1 lesson, the sim plays **corpus latent trajectories
  only** — no straight-line latent paths; AR(2) noise is added on idle segments only.
- **Simulation** (`src/sim.py`): behavior state machine owns zone logic (idle L/R thirds, fishing in the
  center third), event timing, and the **procedural ink layer** — ripples, splashes and drips are drawn
  by the sim from its own physics events (foot plants, strike, toss, takeoff, landing), only ever onto
  white cells. **The net never generates ink.**
- **Presence** is a first-class input (see interface below); the preview scripts one APPROACH beat.

## Grid / retarget history (cost note, as requested)

The brief was retargeted twice mid-build by Jimmy's decisions: 120×90 → **160×96** (800×480 product,
11:35) → **160×120 master** (BOX-3 first landing, full-bleed 320×240, 11:51). Because the rig, zones and
choreography live in normalized design coordinates, each retarget was a **re-render + retrain, not a
redesign** (~8 min of Spark compute per full cycle). The 160×96 pipeline was completed in full before the
second steer arrived and remains on the Spark (`corpus_*`, `model_*`, `preview_heron_v1_800x480.mp4`) —
the 800×480 product aspect is proven, not just promised. **v1 master is 160×120.**

## Measured results (final 160×120 run)

| Metric | Value |
|---|---|
| Grid | 160×120 palette-indexed, 12-entry palette (11 used in episode) |
| Corpus | 21,980 frames / 173 clips @12 fps |
| Model | 1,949,468 params, latent 48 |
| Val exact-cell accuracy | **97.24%** |
| Val bird-region accuracy | **88.66%** |
| Val fish accuracy | **82.45%** |
| Episode | 1,012 frames = **84.3 s** @12 fps, rendered **320×240 @24 fps** (exact ×2) |
| MP4 near-palette fraction | **1.0** (no color bleed) |
| Ink at rest | **0 cells** — first idle (last 3 s), final idle (last 2.5 s), empty beat (after 1.7 s) |
| Ink causality | step events 12/12 produced ripples; strike/takeoff-class events 4/4 produced ink |
| Zone centroids (of 160 cols) | idle L **37.2**, strike **83.1** (center), idle R **121.2**, alert **37.7**, final idle C **81.4** |
| Fish size in episode | tiny **96** cells vs big **188** cells (≈2×, clearly distinct) |
| Motion continuity | median frame-to-frame change 68 cells; **max segment-join change 516** (takeoff launch onset — real motion, not a snap) |

QA history worth knowing: the first assembled episode had two ~1,500-cell joins where a mirrored
(left-facing) R-zone idle was bracketed by right-facing walk/takeoff clips — an instant facing flip,
confirmed on pulled frames. Fixed properly with rig-authored **turn clips** (walk → turn → idle →
turn → takeoff), plus choosing the takeoff variant that fully exits the frame before the empty beat.
All joins in the shipped preview are ≤516 cells and the bird is fully gone before the empty frame
(join change 0).

Episode contents (in order): idle L (ROOM_EMPTY baseline) → walk to center → strike, tiny fish,
swallow with drips → idle C → wing stretch (center) → walk to R → turn → idle R → turn → takeoff
→ takeoff → empty beat → fly-in → land L →
settle → **APPROACH: alert/head-up acknowledgment** → walk to center → **strike, big fish** (fishes
for its audience) → idle C under PRESENCE_SUSTAINED. (The R-zone takeoff departs rightward and is
fully out of frame before the empty beat.)

## Proposed real-time pacing (preview is ~40× time-compressed; for Jimmy to tune)

| Behavior | Unwatched | While watched (PRESENCE_SUSTAINED) |
|---|---|---|
| Idle hold (stillness dominant) | 2–8 min between events | 1–4 min |
| Micro-life (head turn, blink, dip) | every 4–15 s within idle | same |
| Zone walk (L↔C↔R) | every 3–10 min | every 2–6 min |
| Fishing episode (walk to center, aim 20–90 s, strike) | every 4–12 min | every 1.5–4 min |
| Catch split | ~75% success; of catches ~70% tiny / ~30% big | same |
| Wing stretch | every 15–40 min | every 15–40 min |
| Flight departure / away time | every 45–120 min / away 2–10 min | suppressed while watched |
| APPROACH response | alert within ~0.5 s, hold 2–4 s, then resume (often: go fish) | — |
| ROOM_EMPTY (>2 min no presence) | doze weights: one-leg idle, micro-motion damped | — |
| Night (ambient light low) | display dim → sleep; bird settles | — |

## Presence interface (firmware binding contract — `presence_interface.json` on the Spark)

- `APPROACH` = LD2410-class mmWave presence **rising edge** → alert clip + acknowledgment.
- `PRESENCE_SUSTAINED` = presence flag held ≥5 s → watched pacing column above (fish readily, no doze, no departure).
- `ROOM_EMPTY` = presence flag low for >120 s → unwatched/doze pacing.
- Ambient light (BH1750-class lux) → night dim/sleep. **No camera, no microphone, ever** (design law).
  The mmWave module hides inside the printed case (radar passes through PETG, detects stationary presence, ~$6).

## Honest weaknesses

- **Bird-region reconstruction is 88.7%**, not the headline 97.2% (which is mostly white background):
  silhouette edges soften/flicker by a cell here and there at this grid size. Reads fine at 320×240,
  but it is the first thing a v1.1 capacity bump (latent 64 / wider decoder) should attack.
- **Fish reconstruction 82.4%** — the fish is small; its outline wobbles slightly during the toss.
- **Walk swing leg bunches into a brown "boot" blob in stills** (thigh + folded shin mid-stride).
  Reads as a step in motion; weakest visual element in freeze-frames.
- **Flight cheats**: one large wing (no far-wing separation); the flight neck is extended and elegant,
  not tucked like a real heron's.
- **Stretch wing is a simple slab**; no preen clip exists yet.
- **The turn is a squash-flip** (0.83 s horizontal squash sweep) — effective at this resolution, still a cheat.
- **Alert in the preview is scripted**, not sensor-driven — no hardware exists yet; the interface is
  the deliverable, the binding comes with the firmware phase.
- Doze is currently approximated (one-leg idle + damped micro-motion); no dedicated sleep-droop clip.

## Files

- This VM: `~/workspace/heron/preview_heron_v1.mp4` (320×240 master), 
...[truncated 851 chars]