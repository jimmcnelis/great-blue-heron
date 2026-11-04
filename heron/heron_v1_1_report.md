# Heron v1.1 — revision report

Jimmy's three rulings on v1, and what v1.1 did about each. All numbers measured
off the finished build (validation split = held-out clips; QA off the final
preview file and its episode grids). **Jimmy's verdict on this build
(2026-11-02): "1.1 is an improvement. The resolution is good for the BOX-3.
Just need to clean up the drawing and animations now. Eating the fish is
messy. The legs are improved but still clunky. Lots wrong still."** That
verdict is the honest summary of where this lands: the structure and the
resolution are right; the remaining faults are drawing-level, and they are
v1.2's charter (pose space + the movement study), not another pixel pass.

## Ruling 1 — legs too thick, especially in flight

- Whole leg chain thinned in the rig: thigh line 3.4→2.9 design units (still
  rusty, mostly under the body), shin 2.1→1.15, knee knob 1.5→0.95,
  tarsus 1.9→1.05, toes 0.9→0.55.
- Flight legs are no longer IK-drawn: once airborne they render in the rig as
  two single stilt lines, hip→foot, near-parallel, trailing at body height.
  The rig ground truth is exactly right — see `qa_frames_v1_1/` comparison
  crops and the corpus frame at flyin 55%.
- **Where it still fails:** the autoencoder's 15×20 bottleneck cannot hold
  1-cell dark lines through rare, fast poses. In the shipped render the two
  trailing stilts decode as one brown bar (~5 cells thick); in the
  pre-fine-tune model they were an irregular splat. Standing legs, by
  contrast, read as true stilts in every standing gate frame. This is a
  decode limit, not a drawing limit — stated plainly because it is the
  single strongest argument for the pose-space architecture v1.2 adopts.

## Ruling 2 — body too horizontal

- Standing body axis re-pitched to a **−33° diagonal** (chest high, tail low)
  across idle, walk, and one-leg rest; alert stands taller at −39°. Measured
  on the final episode's idle frames by PCA of the body mass: **31.8–32.3°**
  across six samples — inside the 30–40° band of the reference photos.
- The strike coils and fires *from* the diagonal (body rocks to −19° at the
  strike instant, recovers through −26° to the diagonal). Flight stays level,
  with a proper neck fold: in the air the head draws back over the shoulders
  in the tight S a real heron flies with (v1 flew with its neck up).

## Ruling 3 — "smooth like Looney Tunes"

Attacked on all four fronts:

- Master grid 160×120 → **320×240** (BOX-3 native; the preview is 1:1, no upscale).
- Corpus 12 fps → **24 fps**: 43,936 frames / 177 clips (v1: 21,980 / 173).
- Autoencoder ~10× bigger: 18,754,268 params, latent 128 (v1: 1,949,468 / 48),
  trained 40 epochs with stronger rare-class weights, then a guardrailed
  6-epoch fine-tune (strike ×3, takeoff/flyin ×5, turn ×2 oversampled;
  ink and leg-color weights ×1.5). **The fine-tune is the shipped model**
  (`model11f`): it won on validation bird accuracy and, decisively, on the
  two known problem crops — the strike-peak head went from a black balloon
  to a readable head, and the flight legs from a splat to a single bar.
- **Palette-snap at decode is in force** (mode: argmax won the head-to-head
  against RGB-snap, 99.59% vs 99.30% val bird) — every cell of the shipped
  grids is a true palette color by construction; the MP4 itself measures
  0.9937 near-palette (the small residue is video-codec chroma bleed on
  1-cell lines, not off-palette drawing).

Validation reconstruction (held-out clips, shipped fine-tuned model):

| region | v1 (160×120) | v1.1 base | v1.1 shipped (fine-tuned) |
|---|---|---|---|
| all cells | 97.24% | 99.74% | **99.77%** |
| **bird** | **88.66%** | 99.53% | **99.59%** |
| fish | 82.45% | 92.98% | 92.69% |

Target was bird ≥ 95% on validation: **cleared decisively (99.59%)**.
One honest footnote: palette index 11 (fish belly) never survives decode
anywhere in the episode — the thin belly strip is lost to class imbalance;
the fish still read clearly in body/back colors.

## Episode (same arc as v1)

84.3 s at native 320×240, 24 fps: idle left → walk to center → tiny-fish
strike → idle → wing stretch → walk right → turn → flight out → empty beat →
flight in → landing → APPROACH alert → walk to center → watched big-fish
strike → final idle. Thirds blocking held (zone centroids of 320 columns:
idle L 75.5, strike 165.4, idle R 242.5, alert 76.5, final idle C 164.2).
Ink discipline held: **zero ink at rest** in every idle/empty window QA
checked; 12/12 step events and 4/4 splash-class events produced ink.
Fish sizes in the measured frames: tiny 220 cells vs big 467 cells.

## Rendering hygiene (applied this build, measured)

Post-decode cleanup runs in the sim, before ink compositing, so it can never
eat a caused effect:

- **Orphan absorption:** same-color components ≤6 cells that touch neither
  the bird mass nor the beak zone are absorbed into the dominant neighbor
  color. Shipped episode: **9,964 cells removed (4.92/frame)**.
- **Temporal deflicker**, held segments only (idle/alert/empty; fast accents
  untouched by construction, beak zone protected so blinks survive):
  single-frame A-B-A flips **4,678 → 802 (−83%)**; 3,069 cells fixed.
- **Idle-noise reduction:** the latent variation ridden on idle segments was
  cut from 0.55 to 0.30 amplitude after craft QA measured the holds as too
  busy (below). Raw held-segment flicker fell 17% before cleanup.

## Craft QA (checks from the cartoon-animation-craft skill, measured)

- **Anticipation — PASS.** Every strike clip holds its coil at full depth
  for 15 frames before release (skill asks ≥8), with the beak moving
  ~0.5 cells across the final approach frames.
- **Spacing — PASS.** The strike accelerates in: the beak covers ~77 cells
  in its final 2 frames before contact vs ~0.5 cells in the 2 before those.
- **Holds — FAIL, improved but not fixed.** Held fraction of idle frames is
  ~0.25 (skill wants ≥0.60) and the longest unbroken still stretch is
  0.2–0.5 s (skill wants ≥2 s for a hunting bird). The residual motion is
  authored into the corpus idle tracks themselves (continuous sway), not
  just playback noise — a heron whose signature is statue stillness needs
  its idles re-authored around true holds. That is v1.2 work, and the
  movement study already staged in this folder is the right vehicle.
- **Smear audit — none authored (v1.2 item, now measured):** peak beak
  speed at the strike is ~65 cells/frame — the head crosses its own length
  in under a frame, which by the skill's rule wants an authored smear.
- **Follow-through (proxy):** frame-change after the landing decays
  3,519 → ~450 cells over ~8 frames (a real settle), then authored idle
  motion resumes; after the swallow the decay is weak — see the v1.2 notes.
- **Silhouettes:** gate-frame silhouettes (`qa_frames_v1_1/sil_*`) — idle,
  alert, strike, and flight poses are all nameable from silhouette alone.
- **Line boil:** not applied. Decode flicker was treated as a defect and
  cleaned (above); authored boil remains Jimmy's call, per the skill.

## The 800×480 variant — stated plainly

`preview_heron_v1_1_800x480.mp4` is a nearest-neighbor ×2.5 resize of the
final master grids: palette-exact, but a resize. The native 200×120 variant
model was never landed — its first training run blew up mid-run (peak
learning rate 2e-3 destabilized the shallower net: loss 0.083 → 1.85 between
epochs 5 and 10, fish never learned); the rerun at 8e-4 with gradient
clipping was converging cleanly (epoch 20: val bird 98.56%) when the
process was killed externally at epoch 25 with no checkpoint saved. Per the
wrap-up order, it was not relaunched. In v1.2's pose-space architecture the
resolution question evaporates — the rig renders any grid from the same
performance — so this gap closes by design rather than by another training
run.

## Pose data banked for v1.2 (pose space)

`corpus11_poses.npz` + `corpus11_poses.json` (mirrored in this folder; also
on the Spark at `~/heron/`): the per-frame authored pose-parameter stream
for all 43,936 corpus frames — 28 columns (20 rig parameters, 4 leg-target
values, the turn squash factor, and fish/fish-size codes), in design-space
units, frame-aligned with `corpus11_clips.json`. Poses are banked in
authored orientation; mirrored clips pair with `facing = −1` in the clips
JSON. **Verified aligned:** a rebuild with pose dumping reproduced the
shipped corpus bit-identically (0 differing cells; beaks exact), so this
stream is the exact performance the v1.1 models trained on. The pose-space
trainer can start from v1.1's own performances with no re-authoring.

## What v1.2 should hear about the legs and the fish-eating

**Legs.** The drawing is not the problem: the rig's stilts measure right
and the corpus ground truth is clean in every pose Jimmy flagged. Every
leg failure in v1.1 happened in the 15×20 bottleneck — thin dark lines are
the first thing a small latent erases, and no class weighting fully buys
them back (the fine-tune improved splat → bar, not bar → stilts). In pose
space the rig draws the legs every frame and this failure class disappears;
spend the effort instead on the *motion* of the legs: the lifted leg in the
walk still carries a hint of the v1 "boot" in freeze frames (the skill's
fix: slim the swinging leg's profile and point the toes at mid-swing), and
the flight legs, while thin in the drawing, should enter their trail with
a beat of lag behind the body's pitch, not in lockstep.

**Fish-eating.** Jimmy: "eating the fish is messy." He is right, and the
mess has an address: the strike peak and the swallow are the fastest,
rarest poses in the corpus (~0.1% of frames), so they are exactly where
the decoder hedges — the plume/brow thickens into a hood, the eye dot
vanishes, the fish's belly color never survives, and the toss reads as a
pop rather than an arc with weight. The rig's own strike frames are clean
(white face, thin brow line, visible eye), so this is not an authoring
failure either. For v1.2: treat the eat as the signature beat and author
it pose-to-pose — spear, head-shake, toss, catch, and a throat bulge that
travels down the neck as follow-through (our measured follow-through after
the swallow is weak; the current swallow is a dip and a fade). Keep the
fish as its own rig layer with its pendulum swing after the catch. And
note the anticipation is already right: the 15-frame loaded coil and the
explosive spacing measured above are worth preserving exactly.

## Parked for v1.2 (from this build's findings)

Deeper anticipation crouch in the body (current anticipation is neck-only);
authored smear frames for the strike fire and takeoff; follow-through clips
for the swallow settle and landing settle; true held poses in idle (see
Craft QA); preen clip; far wing in flight; a real turn through authored
three-quarter poses instead of the squash cheat; flight wing articulation
(root/tip phase lag, 40–45% downstroke share, glides on long crossings);
legibility floor check for thin parts at the 200×120 product grid (stilt
legs land at ~1.3–1.5 cells there, below the skill's 2–3 cell floor).

## Generalization debt (heron assumptions baked into this build's code)

Per the platform steer — listed, not refactored:

- `rig.py`: the whole heron anatomy is procedural code (body geometry, neck
  Bezier math, IK legs with heron segment lengths, plume, beak, wings) — a
  new species needs a new rig module, not new data. The 12-color palette
  (fish colors included — two species share one codebook), the 120×90
  design space, the water line (y 74) and the below-surface clip-to-white
  rule are all baked into the renderer.
- `clips.py`: the behavior library is heron behavior written as code; zone
  positions {L 27, C 60, R 93}, gait constants, strike fish sizes, and toss
  ballistics are literals — the thirds law is encoded as numbers, not config.
- `corpus_build.py`: mirroring assumes a bilaterally symmetric side-facing
  character; the turn is a horizontal squash remap; the toss patch measures
  beak tips — a heron-fishing interaction baked into the corpus builder.
- `train.py`: mostly species-agnostic; NPAL = 12 and the `*_9` val-split
  naming convention are the baked assumptions.
- `sim.py`: the episode script is a hardcoded heron story arc; the ink
  layer is water-specific (surface ripples, splashes, drips), not a
  pluggable effect system; presence responses are wired to heron behaviors
  in code; ink scaling anchors to the v1 160-wide grid.
- `qa.py`: gates assume heron anatomy (body-axis PCA assumes the neck is a
  different color from the body; fish checks assume palette indices ≥9;
  the water band assumes a surface row).
- Mitigation already in place: the pose bank above is species data, not
  code — parameters, zones, and clip timings for the *performance* now
  exist as a dataset the pose-space engine can consume.

## Files

- `preview_heron_v1_1.mp4` — master preview, native 320×240 (md5 5857d92ff02e2089a447dbb81d977767)
- `preview_heron_v1_1_800x480.mp4` — 800×480 resize of the master grids (md5 c773bcf693b6076cb58c44260e7b02c8)
- `qa_contact_sheet_v1_1.jpg` — segment contact sheet from the final render
- `qa_frames_v1_1/` — QA gate frames + silhouettes pulled from the final preview
- `corpus11_poses.npz` / `corpus11_poses.json` — the banked pose stream
- `qa_results_11.json`, `craft_qa_11f.json`, `model11f_stats.json` — measured QA evidence
- Build lives on the Spark at `~/heron/` (`corpus11*`, `model11*`, `model11f*`, `src11/`);
  v1 code and models untouched. No device work was done.
