# Creature Engine — Architecture

*A pluggable pipeline for generated cartoon creatures. The heron is proof of
concept #1; this document is the design that lets creature #2, #3, … plug in
as data + a thin rig, with no engine changes.*

Jimmy's ruling (2026-11-02): "in the end i want to make these for many
creatures… build the dev pipeline with the ability to plug in a new animal
(or animals), environment, style, behaviors, interactions with the external
environment, and in the case of multiple characters in the same iteration,
their interactions with each other."

---

## 1. The one idea

Everything that makes a creature **that creature** is a **package** — data
files plus two small Python modules (a rig and a clip author). Everything
that makes the pipeline **a pipeline** — keyframe sampling, corpus building,
mirroring, effect compositing, behavior policy, QA measurement — is the
**engine**, and the engine contains no species' name, no species' palette
size, no species' stage dimensions.

The heron v1 code violated this in ~20 specific places (the debt list,
§9). This tree is the seam drawn where v1's own structure said it wanted to
be: v1 already authored poses in a normalized design space, already drew
its water procedurally from events, already treated presence as a state
input. The engine generalizes exactly those three instincts.

## 2. The five package kinds + the scene

```
packages/
  great-blue-heron/   species #1: species.yaml + behaviors.yaml + rig.py + clips.py + model_sheet.md
  heron-fish/         a PROP species (the prey; see §6)
  pond-frog/          species #2 (plug test)     firefly/  species #3 (plug test)
  implied-water/      environment #1            pond-edge/ environment #2
  flat-storybook/     style pack (shared by both scenes)
  thomas-point-lighthouse/  object #1: object.yaml + rig.py + model_sheet.md
  heron-scene/        scene #1                  pond-scene/ scene #2
  heron-lighthouse-scene/  scene #3 (heron + the lighthouse object)
schemas/              versioned JSON Schemas for every document kind
engine/               the species-agnostic core
```

### 2.1 Species package — "everything that makes a creature THAT creature"

`species.yaml` (schema: `schemas/species.schema.json`) declares:

- **design_space** — the normalized stage the rig/clips are authored in
  (heron 120×90; frog 96×72). Character size follows frame height; a stage
  retarget is a re-render, not a redesign (v1 proved this twice in one day).
- **palette** — named entries; index 0 is always the canvas. Names, not
  numbers, are the cross-package currency (`ink`, `body`, `throat`…).
- **pose_params** — every animatable parameter with its neutral default.
  This is the rig's public vocabulary; the keyframe engine speaks only it.
- **rig** — a module exposing `render(pose, ctx) -> (grid, anchors)` and
  `default_pose()`. Rigs draw with `engine/rigcore.Canvas` (supersampled
  design-space primitives + majority downsample) or, during migration,
  adapt an existing rig (the heron's adapter wraps v1 byte-exactly).
  **Anchors** are named tracked points (`beak_tip`, `mouth`) reported per
  frame in grid coordinates — effects and QA audits refer to anchors, never
  to species internals.
- **clips** — a module exposing `build_clip(kind, kwargs, ctx) ->
  (poses, events)`, plus a **roster as data**: name, kind, kwargs, mirror
  flag, train/val split, ambient flag, and named **hooks**. (v1 kept the
  roster in code — `clip_specs()` — and encoded split/zones in clip *names*.
  Both are data now.)
- **life_layer** — the micro-motion that keeps held poses alive, as data:
  `[{param, waveform, period_s, amplitude, damped_by, skip_when}]`. (v1
  hard-coded four sine terms with heron semantics inside its sampler,
  including "statuesque while aiming" as a coil-coupling constant.)
- **behaviors.yaml** — the behavior set (§5).
- **model_sheet.md** — proportions as ratios, canonical marks, the parts
  that may never change shape. A proportion change is a model-sheet change
  and triggers a re-render + re-check of every canonical pose.

### 2.2 Environment package — "the world's laws"

`environment.yaml` (schema: `schemas/environment.schema.json`) declares:

- **canvas_law** — what the world looks like untouched: background, any
  **static marks** (the heron has *none*; the pond has one shore line), and
  **clip planes** (occlusion: the heron's surface plane hides everything
  below it — the water is implied, never drawn).
- **effect_map — the causality table.** Which clip/event types cause which
  procedural marks *in this world*: `step → ripple`, `land → ripple`,
  `snap → ring`, `drips → drips`. It lives in the environment because a
  footstep ripples water but would puff dust on land. Effect *primitives*
  (ripple, splash, drips, ring) are engine code; their *invocation* is
  world data. This generalizes v1's InkSim, whose event→ink mapping was
  hard-coded in the simulator.
- **zones** — named blocking positions in design coordinates, with roles
  (`dwell`, `fishing`, `perch`) and **mirror partners as data** (v1
  hard-coded the L↔R swap in its corpus builder).

### 2.3 Style pack — "the art direction, and its teeth"

`style.yaml` (schema: `schemas/style.schema.json`) names the art direction
(flat storybook), the render rules (supersample 4×, majority downsample,
gradients/dithering/AA-halo forbidden, palette exact by construction), the
**line-boil decision** (off, and *recorded* as a decision — per the craft
skill, boil is chosen, never inherited), and a **qa_checks list**: which
validators run, with what thresholds, at what severity.

The craft skill (`~/workspace/custom-skills/cartoon-animation-craft/`) is
the doctrine; the style pack is its executable subset. New craft knowledge
= a new validator in `engine/qa.py` + one line in a style pack. Never an
engine fork.

### 2.4 Scene — "the composition"

`scene.yaml` (schema: `schemas/scene.schema.json`) is one *iteration*: an
environment + a style + **characters** (species instances), the stage
(grid, fps), the **input bus**, the **interactions**, and an optional
deterministic **episode script** for previews/QA.

Rules the loader enforces: all characters' species must agree on design
space (a species authored for another stage is a variant package);
environment static-mark colors must resolve in some character's palette.

### 2.5 Object package — "the non-living cast" (added 2026-11-02, Jimmy's ruling)

Jimmy: "in addition to creatures there could also be objects — a landmark
like Thomas Point Lighthouse, in some scenes." An **object** is a placed,
named thing with a drawn form of its own: landmarks, structures,
vegetation, vessels. It is none of the existing kinds:

- Not a **species** — no behaviors, no pacing, no life layer, no corpus,
  nothing learned. It never decides anything.
- Not a **prop** — a prop is a lightweight *participant* driven by an
  interaction (the fish). An object is *set dressing with an interface*:
  it stands in the world whether or not any creature interacts with it.
- Not an environment **static mark** — static marks are world law drawn
  by the environment (a shore line). An object has its own palette, its
  own rig, and can be placed in any scene that shares its design space.

`object.yaml` (schema: `schemas/object.schema.json`) declares:

- **kind** — landmark / structure / vegetation / furniture / vessel.
- **palette** — its own named entries; index 0 is the shared scene
  canvas, exactly as species. A landmark is drawn in full, in its real
  colors: it is a thing in the world, not a caused mark, so the
  environment's ink law does not apply to it. (Its *light* is state: a
  beam/glow is drawn only when lit.)
- **state_params** — the object's animatable state, rendered
  deterministically by its rig: `render(state, ctx) -> (grid, anchors)`,
  the species rig contract with state in place of pose. State is set by
  the scene placement, by the input bus/modes (lamp on at night), or by
  an interaction outcome's **`set_state`** — never by the object itself.
- **anchors** — named points other packages refer to (the lantern is a
  beam origin and a look_at target; the waterline is where the
  environment's causality table rings against the piles).
- **affordances** — what creatures may do with it, as data:
  `perch -> gallery`, `look_at -> lantern`, `circle -> lantern`.
  A creature's behavior names the action; the scene resolves it to the
  placed instance's anchor (`Scene.object_affordance` /
  `Scene.object_anchor`).
- **footprint** — extent at scale 1 + where it meets the medium.

Scenes place objects (`objects:` in scene.yaml: instance id, package,
zone or explicit design coords, `scale`, `layer` back/front, state
overrides). The loader enforces design-space agreement and the
shared-background rule; the episode player renders each object once from
its placed state and composites it on the merged palette (objects append
after characters), back layer under the creature tracks, front over
them. The world's clip planes bind objects as they bind creatures — in
implied-water the lighthouse's piles below the surface stay hidden under
the blank, like the heron's feet.

**Object #1: Thomas Point Shoal Lighthouse** — the 1875 screwpile
cottage lighthouse in the Chesapeake off Annapolis: white hexagonal
cottage, red roof, black lantern, gallery perch, rusty piles. Authored
at cartoon scale (~1 heron tall; the model sheet records the lie and
why). Plug test: `plugtest-out/object_test.py` — scene validation,
affordance/anchor resolution, day vs night renders (lamp/beam cells
0 by day, lit at night), and a composite behind a real heron corpus
frame all pass; the full-episode render in that test is skipped only
because the heron-corpus fixture carries no fish track.

## 3. Engine core

| Module | Job | Generalized from |
|---|---|---|
| `package.py` | Load + schema-validate packages/scenes; resolve cross-refs | — (new) |
| `anim.py` | Keyframe tracks (smoothstep), fn tracks, blink helper, sampler with data-driven life layer | v1 `clips.Anim` + `sample_clip` |
| `rigcore.py` | Design-space Canvas: tube/line/poly/ellipse/bezier, clip planes, majority downsample | v1 `rig.py` helpers |
| `corpus.py` | Roster → poses → frames + anchors + events; mirroring; **package hooks** | v1 `corpus_build.py` |
| `effects.py` | Caused-mark runtime (ripple/splash/drips/ring), marks only onto background | v1 `sim.InkSim` |
| `behavior.py` | Pacing policy (competing Poisson processes per mode) + reaction lookup | v1 report's pacing table |
| `episode.py` | Per-character parallel tracks, merged-palette compositing, effects, static marks | v1 `sim.py` episode assembly |
| `qa.py` | Validator registry; style packs select + parameterize | v1 `qa.py` |
| `train.py` | *(not yet extracted — see §10, Phase 4)* conv AE + PCA/AR(2) dynamics | v1 `train.py` |

Data flow: `scene → corpus build (per character) → [trainer] → episode
player / real-time policy player → device export`.

**Hooks, not special cases.** v1's corpus builder contained two heron-only
operations keyed on clip kind (the ballistic fish-toss patch; the turn
squash). In the engine these are *package hooks*: functions in the species'
clips module, named in the roster entry, called as
`hook(frames, anchors, poses, events, entry, render, ctx)`. The engine does
not know they exist. The frog needed zero hooks; the heron needs two.

**Merged palette rule** (multi-character compositing): index 0 (background)
is shared; each character's remaining palette entries append in scene
order. Effect marks take the `ink` entry of the first character that
defines one.

## 4. The event bus — external world as a first-class input

Generalizing `presence_interface.json`:

- **Raw inputs** (scene data): `approach` (edge), `presence_sustained`
  (level), `room_empty` (edge after 120 s), `ambient_light` (level),
  `button` (pulse). Sources are hardware descriptions; the engine only
  needs semantics — firmware binds pins to names.
- **Derived modes**: named, priority-ordered (`night` > `empty` > `watched`
  > `unwatched`). Behavior pacing is keyed by mode.
- **Reactions** (per species, in behaviors.yaml): `trigger → interrupt? +
  play + to_mode + then_weight_boost + cooldown`. The v1 contract —
  APPROACH interrupts to an alert, then fishing is boosted while watched —
  is three lines of data now.

The deliverable to firmware is generated from the scene's input
declarations (Phase 6), replacing v1's simulator writing the JSON as a
side effect.

## 5. The behavior system

Behaviors are **data per species**: id, clip kinds (not instance names),
zones/roles, weight, **pacing = mean seconds between occurrences per
external mode**, cooldown, interruptibility. The policy is competing
Poisson processes (`rate = weight / pacing[mode]`); the baseline behavior
(no pacing) fills the gaps. This made the v1 prose table executable —
measured on the heron package: in one simulated watched hour the heron
fishes 21× vs 2× unwatched and never departs (flight has no watched
pacing entry — suppressed *by data*, not by an if-statement).

## 6. Multi-character interactions

Interactions are **scene data** (schema in scene.yaml): `between`
(instance ids), `roles`, a `trigger` (proximity range / named event /
schedule rate), and **weighted outcomes** — each outcome names what *each*
participant plays (`clip_kind` or behavior) plus shared effect events.
Three forms, in increasing extraction order:

1. **Embedded** (heron↔fish today): the prey is pose state inside the
   predator's clips. The scene still *declares* the interaction — roles,
   outcome split 52.5/22.5/25 (catch-tiny / catch-big / miss, from v1's
   measured catch rates) — so the contract exists before the extraction.
2. **Prop participant**: a lightweight species package with a real rig but
   no independent behavior (`heron-fish` exists in this form now: its
   shape is transcribed onto rigcore; its clips arrive at extraction).
3. **Full co-characters** (frog↔firefly, proven in the plug test): two
   complete species on parallel episode tracks with a proximity-triggered
   interaction whose outcomes switch both tracks (`tongue_snap` + `gone`,
   with the catch ring as a shared event).

## 7. QA as a style-pack contract

Validators implemented: `palette_exactness`, `ink_at_rest` (quiet segment
tails — stillness is the default), `event_causality` (every mapped event
produces marks near *its own* position — v1 checked only the surface band;
an air event like a tongue snap exposed that assumption during the plug
test, and the check was generalized), `join_smoothness`, `held_fraction`
(the skill's ≥60% held-idle rule), `flicker_metric` (A-B-A flips — decode
flicker, the defect the skill separates from authored boil).
Declared-but-not-yet-implemented: `silhouette_test`, `anticipation_audit`
(they report `not_implemented`, never a silent pass; they land with the
Phase-4 QA pack alongside anchor-tracked spacing/smear audits).

## 8. Versioning

Every document carries `schema_version: 1`. Schemas live in `schemas/` as
JSON Schema (draft 2020-12). A v2 schema ships alongside v1; loaders accept
both during migration. Package ids are kebab-case and directory names.

## 9. Generalization debt — what v1/v1.1 baked in

Measured by reading the v1 sources line by line (file:line in the working
notes; summarized here):

1. **Forked trees**: `src/` (v1) vs `src11/` (v1.1) — two divergent copies
   of all seven modules; v1.1 changed grid via env vars and FPS by editing
   constants. One parameterized codebase must replace both.
2. **Grid/design constants in the rig**: `W,H`, `S=H/90`, stage center 60,
   `WATER_Y` compiled into `rig.py`; retargeting meant recompiling the
   bird. (Now: scene + ctx.)
3. **One palette for bird + fish + ink**; fish identified by index range
   (`x >= 9`) in `train.py` eval and `qa.py`. (Now: named palettes per
   species; prey is its own package.)
4. **Pose vocabulary in shared files**: `POSE_PARAMS`/`default_pose` live
   in what reads as engine code but is heron anatomy. (Now: species data.)
5. **Micro-motion semantics hard-coded** in `clips.sample_clip` (coil
   stillness factor 0.75, flying check). (Now: life_layer data.)
6. **Corpus-builder special cases by clip kind**: toss patch + turn squash
   inside `corpus_build._job`. (Now: roster hooks.)
7. **Mirror logic** assumes horizontal flip + L↔R name swap. (Now: env
   mirror partners as data; engine flips generically.)
8. **Trainer constants**: `NPAL=12, LAT=48, H×W=120×160` in `train.py`;
   **val split by clip-name suffix** (`_9`); dynamics fit on `kind=='idle'`
   with a magic kernel of 13. (Phase 4: all from scene + roster metadata —
   `split` and `ambient` fields already exist in the roster for this.)
9. **Simulator script in code**: `sim.py`'s episode is a Python list of
   clip *instance names*; presence handling is woven into its loop; the
   pacing table existed only as report prose. (Now: scene episode_script +
   behaviors.yaml; both transcribed verbatim for the heron.)
10. **InkSim constants**: squash factor 3.1, droplet counts, drip spawn
    every 3rd frame from the beak — heron-tuned numbers inside the
    simulator. (Now: effect primitives + env params; drip cadence is the
    one number still engine-side.)
11. **QA hard-codes**: segment names (`idle_L_0`…), palette size, surface
    band, an absolute ffmpeg path. (Now: style-pack-selected validators.)
12. **`alert_append.py` exists** — alert clips were bolted onto a finished
    corpus by a one-off script because the pipeline had no incremental
    corpus operation. (Engine corpus builds are per-kind selectable;
    a merge/append op is Phase 4.)
13. **The fish has no independent existence** — drawn by the predator's
    rig from pose state; no rig, clips, or track of its own. (§6 ladder.)
14. **Single tracked anchor**: beak tip only; toss + drips depend on it.
    (Now: declared anchors list; heron declares beak_tip + head.)
15. **Load-bearing clip names**: zones/facings encoded in ids
    (`idle_L_1_m`) that sim and QA pattern-match. (Now: roster metadata.)
16. **Absolute paths** (`/home/jim/heron/…`) as defaults in sim/train.
17. **Presence contract as a side artifact**: `sim.py` writes
    `presence_interface.json` with hardware strings inline. (Now: scene
    input declarations; the JSON becomes a generated export.)
18. **Flight/turn cheats live in the rig, undocumented as cheats** (one
    wing, squash turn) — the model sheet now names the canonical form and
    the v1.2 brief owns the gap.

## 10. The staged refactor (follow-on phases — NOT done here)

- **Phase 2 — heron onto rigcore.** Re-express the heron rig with
  `rigcore.Canvas` primitives; parity gate: regenerated corpus frames
  match v1's within a stated cell-diff budget (the adapter's byte-parity
  test in `plugtest-out/parity_test.py` is the template). Kills debt 1–4.
- **Phase 3 — behavior runtime replaces the script.** The real-time player
  (policy + reactions + bus) drives episodes; the scripted episode remains
  as a QA fixture. Kills debt 9, 17.
- **Phase 4 — trainer + full QA pack.** Parameterize `train.py` from
  scene/roster (NPAL per species, latent as scene config, split/ambient
  from roster); incremental corpus append; implement silhouette /
  anticipation / spacing / smear validators from the craft skill. Kills
  debt 8, 11, 12.
- **Phase 5 — extract the fish.** Fish gets clips (drift, held, toss as
  its own track), the strike becomes a literal two-track interaction, and
  outcome weights move from clip-seed ratios to interaction data. Kills
  debt 3, 13.
- **Phase 6 — device export.** From a scene: quantized model + behavior
  tables + generated `presence_interface.json` + effect parameters,
  packaged for the 800×480 S3 target in the device spec. This is where the
  BOX-3 trial consumes the engine.
- **Phase 7 — creature #3 for real** (the cat is the standing candidate):
  authored start-to-finish against the engine as the acceptance test —
  if it needs an engine change, the change is the bug report.

## 11. What the plug test proved

See `PLUG_TEST_REPORT.md`. In one line: two new species (frog, firefly), a
new environment law, and a two-character interaction went from YAML + two
small rig files to a QA-passing episode in one sitting, with zero engine
edits after the packages were written — and the one engine change the test
*did* force (event-causality checking near the event, not just at the
surface) was a v1 assumption surfacing, now generalized for every future
creature.
