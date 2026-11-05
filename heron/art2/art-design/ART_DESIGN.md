# ART DESIGN — the system under which the heron art is redrawn (design pass, 2026-11-04)

**Status: DESIGN for Jimmy's gate. No drawing has been done under this
design; the species package is NOT edited by it.** Sources: RESET-2026-11-04.md,
CREW_MEMORY.md, the study files in `art2/real-bird-measure/`, the mechanism
(`creature-engine/packages/great-blue-heron/`, gate records in
`art2/rig-v25-gate/`), the device spec, and LEG_CANON.md (companion document).

---

## 0. The reset law (restated — it governs everything below)

- **Truth = the studies + the mechanism. Nothing else.** The studies are the
  measured bird (real-bird-measure: study, addendum, wingbeat calibration,
  atlas of real frames) and the reference library behind them.
- **No pre-reset image is an input to anything** — not a donor, not a target,
  not image-conditioning, not an ink-band source. All earlier art (the two
  approved stills, the keyframe plates, the warp frames, the corpus art) is
  archived history. It is not consulted while drawing.
- **What carries forward is learning only**: the canon numbers, the mechanism,
  the methods proven to work, the failure lessons — and the Audubon manner as
  the WRITTEN style rules in CREW_MEMORY (engraved line and stipple, exact
  field marks, the plume as countable strands, the neck at its full measured
  length, muted paper ground).
- **Order: design → Jimmy gates → draw → Jimmy gates → animate.** This
  document is the design. Fresh poses are specified from the studies and the
  mechanism alone.

## 1. Decisions up front (each is Jimmy's to strike at the gate)

1. **Legs are corrected per LEG_CANON.md** — feet under the body's middle
   (feet-centre 0.50–0.55), emergence 0.53–0.61, per-pose leg configurations.
   The mechanism's traced legs (feet-centre 0.285, one pair for all poses)
   are retired. *Reason: measured this pass against four real frames; the old
   placement is ~0.25 of the body too far back and pose-invariant.*
2. **Every plate is drawn WHOLE, on flat muted paper, at 1024×600.** No
   compositing, no donors, no erasing. *Reason: donor compositing across
   poses is a failed method here (fill test; warp ghosts). Whole-plate
   drawing deletes the entire erase/ghost problem class by construction.*
3. **The ink band is set by the first plate approved under this design** and
   held to ±0.02 for the rest (protocol in §5). No band is inherited from
   any earlier plate. *Reason: the pre-reset strike band came from a demoted
   source and misjudged an honest frame.*
4. **The strike pose in this design is the STANDING SPEAR only** (chord_base
   0.62–0.71). The lunge class (0.77–0.87) is a different pose with body
   pitch and trailing legs; it gets its own sheet later if charted.
   *Reason: the canon splits the classes (addendum §7); blending them is
   how the old peak kept collapsing to a shorter strike.*
5. **Drawing order: ALERT first** (it is the default visible state and the
   ink band-setter), **then COIL, then PEAK.** *Reason: stillness is the
   default state of the living bird (night-stalk still-fraction 0.73), so
   the alert plate is the one that will be looked at most.*
6. **The coil fold is solved by occlusion, not bending** (§3.2): the neck
   lies against itself in drawn layers. *Reason: the fold's centreline
   radius (≈8.6 px) is smaller than the tube halfwidth (≈26 px); no bent
   tube can exist there. A real coil is feathers compressed in layers, and
   it must be DRAWN as layers.*

## 2. The medium, as design constraints

- **Plates are 1024×600** (Waveshare ESP32-P4 panel), authored at native
  resolution, RGB-friendly palette (species palette, 12 entries — color
  ONLY on living things: bird + fish; the world is paper + black ink).
- **Environment law (locked):** water is IMPLIED, never drawn — blank canvas
  until touched, then only FLAT BLACK INK (a ripple at the bill's entry, a
  ring at a foot). Stillness is the default; every mark is caused. No shore
  in frame. The waterline is a horizontal line the BIRD establishes — it
  crosses each leg exactly at the intertarsal joint (LEG_CANON §2.1).
- **Blocking (locked):** the bird LIVES in the 1st or 3rd third of the
  frame; FISHING happens in the MIDDLE third; on the first landing the
  heron FILLS the screen. The three pose sheets below are drawn for the
  middle-third strike configuration and the thirds for standing poses.
- **Designed for a tiny deterministic generator later:** named parts, exact
  anchors, texture tied to arc stations (§3.2) — structure a small model can
  hold, not painterly improvisation that exists in only one frame.
- **Authoring cadence 24 fps** (device spec): the ballistic extension
  (0.10–0.25 s) is 2–6 frames. Consequence for drawing: the PEAK plate must
  read perfectly as a single held frame, because on device it may be on
  screen for only a few frames; the COIL plate must read for ≥4.15 s of
  frozen hold (the measured minimum coil hold, 6bc) without tiring the eye.

## 3. Part decomposition — designed for motion

The bird is six parts: **torso / neck / head / plume / legs / tail**. Each
part below states: what the studies measure it to be · how it deforms across
the pose set · how it must therefore be DRAWN · its overlaps.

### 3.1 Torso — the rigid part

- **Measured:** depth 0.44–0.59 × torso (study §2); a teardrop fuller at the
  rear-top; the neck chain root sits ON the torso outline at the chest
  (mechanism root anchor; the first mechanism draft put it 46 px inside the
  silhouette and made the canon arc unreachable — the root is a torso fact).
- **Deforms:** it does not. The torso is drawn ONCE as a shape and carried
  rigidly; poses change its PITCH only (level at alert/coil; pitched
  ~10–15° over planted feet at peak — qpYk f0028→f0037). The structural
  outline is traced by column extraction with the plume envelope EXCLUDED
  (57-point principle, mechanism iter2): the torso is the body core, never
  the plume's silhouette.
- **Drawn:** slate body (palette `slate`); folded wing over it in
  dark-slate (`darkslate`) scalloped feathers — the scallop pattern is a
  fixed design element of the torso, identical in every pose (it is the
  torso's fingerprint). Two anchor marks live on the torso and must be drawn
  in fixed positions: the **black shoulder patch** at the neck/body junction
  (canonical mark; it sits at the chain root and visually caps the neck's
  base) and the **two thigh pockets** on the belly at 0.53–0.61 along the
  torso, where the legs emerge (LEG_CANON).
- **Overlaps:** neck root tucks UNDER the shoulder patch; plume roots lie
  OVER the breast front; legs emerge from the thigh pockets and pass behind
  the belly line.

### 3.2 Neck — the unfolding part (the heart of the design)

- **Measured:** the neck UNFOLDS; it does not lengthen. Centreline arc ≈0.72
  × torso in standing postures, conserved within ±10% rest→strike (study
  §3.2); the strike is the same 0.72 of neck, unfolded from chord 0.27 to
  chord 0.70. The chain is 20 links on ~20 cervical vertebrae with two bend
  zones — forward bend low (throat, joints 1–6, cap 26°), backward bend high
  (the strike hinge behind the head, joints 13–17, cap 30°; mid joints 7–12
  cap 20°, distal 18–19 cap 22°) — caps frozen in the mechanism.
- **Widths:** at rest a near-uniform tube: tip 0.161 / mid 0.175 / base 0.184
  (study, UR t=75, neck straight up); coiled slightly fuller (mid 0.195,
  base 0.20, qpYk). The mechanism's rest width at the base station is 0.117
  measured at the visible tube where it exits the body — both reads stand:
  draw the free tube at the study profile, the root flare covered by the
  shoulder patch. **Slimming at extension: 0.55–0.65** (mid 0.57, base 0.65,
  qpYk same-bird; mechanism slimming field base 0.595 / mid 0.58 / tip 0.62).
  At peak the extended tube is ≈0.10 wide at mid and UNIFORM (tip = mid =
  44 px, qpYk). Stretch and slim are coupled: extension is drawn as the tube
  narrowing while it unfolds, never as the tube growing.
- **Drawn — the (u, v) rule:** the neck is drawn as a texture sheet in
  station coordinates: u = arc fraction along the centreline (0 at root, 1
  at skull), v = across the tube. Feather marks, hatch, and color zones are
  anchored to (u, v), NOT to page position. Color zones: pale (`pale`) down
  the FRONT of the tube (the throat/chest-fringe side), slate down the back.
  Hatch and stipple run ALONG the tube (parallel to the centreline, constant
  u-bands) so that when the pose slims the tube, marks compress ACROSS it —
  denser, never torn or stretched along its length. This is the
  centreline-correspondence method (proven as transport: corridor 1.00,
  eyes exact, warp spike) applied at DRAWING time instead of as a rescue:
  every pose lays the same (u, v) sheet along its own centreline.
- **The fold (coil):** drawn as LAYERED FEATHER COMPRESSION. Draw order,
  back to front: (1) the descending pass of the S, (2) the fold stack —
  short, stacked, scale-like feather marks, hatching following the fold's
  own compression, (3) the ascending pass OVER it, with an ink seam where
  the tube lies against itself. Continuous hatch lines NEVER cross the
  fold (crossing lines are what wove into moiré in the tube-warp test).
  The two passes overlap in depth across a band ≈2× the tube halfwidth —
  the neck visibly rests ON itself, as the real coil does (atlas_02;
  57Y deep-coil portrait: arc:chord ≥1.90, the S stored in layers).
- **Swallow provision:** the tube must accept a local distension drawing
  (1.20–1.25× aligned, ~1.8× crosswise — grey-sourced, provisional,
  LEG_CANON §3): the (u, v) sheet stretches locally in v around a bolus
  station without redrawing the neck. (Animation-stage concern; noted here
  so the sheet is designed with v-stretch headroom.)
- **Overlaps:** the spear/plume crossing — where the neck crosses the
  breast plume at peak, the plume strands pass BEHIND the neck (warp spike
  read: that is where anatomy puts them). The neck root passes under the
  shoulder patch; the skull end carries the head assembly (§3.3).

### 3.3 Head — one assembly, three attitudes

- **Measured:** head + bill are ONE distal assembly in the mechanism.
  Bill ≈0.23 × torso (median; 0.47–0.58 of bill+head); skull semi-major
  0.052 / semi-minor 0.030; bill tip reach from skull centre 0.27. The eye
  anchor lives IN THE HEAD FRAME (along_bill 0.028, up 0.014) and is known
  exactly for every pose.
- **Drawn:** the head is drawn as a fixed assembly — white face, black brow
  band, the two trailing occipital plume strands (canonical marks), amber
  eye, orange dagger bill (palette `orange`). **The eye is a PLACED
  STRUCTURE at the mechanism anchor, drawn as its own mark (pupil + iris),
  never left to emerge from texture** — in fill spikes 1–2 the eye silently
  never drew; the anchor exists so that cannot happen again.
- **Attitudes (per pose, from real frames):**
  - *Alert:* head high, bill forward and near-level (mechanism head pitch
    offset +55° from the final neck segment).
  - *Coil:* head low at the top of the S, bill angled down toward the water
    (offset +80°) — the poised, watching attitude (atlas_02; qpYk f28).
  - *Peak:* **spear-collinear** — eye→billbase axis within ~2° of the neck
    axis in real frames (57YcyG5VrYI f90; qpYk atlas_03; 6bc atlas_04). The
    bill NEVER flattens away from the spear line, and the head is drawn as
    the spear's continuation, not a weight hanging off it. (This rule is
    what the rejected painter's strike violated; it is the first thing to
    check on the peak plate.)
- **Overlaps:** occipital strands trail behind the skull over the neck's
  back edge; at peak the head assembly overlaps the tube's tip with no seam
  — the (u, v) sheet ends at u = 1 and the head begins.

### 3.4 Plume — its own layer, always strands

- **Measured/law:** the shaggy breast plume is its OWN region/layer (PLUME
  LAW), excluded from the torso trace and from the neck. It hangs from the
  breast front in fine separated strands with free tips.
- **Drawn:** **strands you can count, tips free over paper — a filled shaggy
  mass is a cartoon and fails regardless of numbers** (Jimmy's tell,
  2026-11-04). The strand set is a designed element: fixed strand count and
  fixed root positions along the breast, so the SAME strands appear in every
  pose (they swing and overlap; they are never re-invented per plate). At
  peak the strands pass behind the spearing neck (§3.2). Plume motion in
  animation is a sway (species life-layer: plume_sway 3.3 s period) — the
  drawing gives each strand a root and a length so sway can rotate strands
  about their roots.
- The occipital head plumes (§3.3) are a separate, smaller strand system
  belonging to the head assembly — do not merge the two systems.

### 3.5 Legs — articulated, per pose

- Fully specified in **LEG_CANON.md**. The design rules that bind drawing:
  legs are a 3-point articulated chain (emergence → intertarsal joint →
  foot) with per-pose configurations; exposed total 0.42–0.44 × torso
  (upper 0.21–0.25, lower 0.17–0.22); feet-centre 0.50–0.55 along the torso,
  staggered 0.10–0.19; feet planted and unmoving through a standing strike;
  waterline AT the joint; toes spread and DRAWN whenever the foot is
  visible; thigh mass is rusty body plumage, lower leg dark-brown and
  stilt-thin (≈0.03 → 0.01 torso wide). One leg configuration for all poses
  is the retired bug.

### 3.6 Tail — part of the rear mass

- **Measured role:** the tail + folded wing read as one rear mass; torso
  depth and the rear-top fullness include it. In flight the legs trail
  straight behind the tail as thin near-parallel lines (model_sheet v1.1
  ruling) — flight sheets come later; for the three standing sheets the
  tail is rigid with the torso and pitches with it (rising visibly at peak
  as the body tips over the feet, qpYk f0037).

## 4. Pose design sheets

Common to all three: canvas 1024×600; torso = the gate constant 496.3 px on
canvas (mechanism scale); paper flat and muted; waterline horizontal through
the intertarsal joints; ink per §5; gates measured OFF THE FINISHED PLATE
(grounded landmarks on the final PNG), never off build bookkeeping.

### 4.1 ALERT — the standing watch (drawn first; ink band-setter)

| Quantity | Target | Source |
|---|---|---|
| Neck chord_base | **0.40–0.47** (mechanism design 0.432–0.458) | iter2 gate spot-check; mechanism poses/alert |
| Neck arc | 0.72 (standing conservation) | study §3.2 |
| Neck width at base | 0.117 | iter2 spot-check |
| Head pitch offset | +55° | mechanism poses/alert |
| Head attitude | high, bill forward near-level | atlas_01 (UR standing) |
| Legs | standing band: feet-centre 0.50–0.55, emergence 0.53–0.61, stagger 0.10–0.14 | LEG_CANON §2.2 |
| Torso pitch | level | — |

Per part: torso RIGID · neck DEFORMING (shallow S, the (u,v) sheet at
rest widths) · head ASSEMBLY at alert attitude · plume LAYERED over breast,
strands hanging free · legs ARTICULATED to standing config · tail RIGID.
Variant noted, not drawn in this sheet: the deeper alert coil (chord_base
0.355, UR t=1) — a watchful crouch between alert and coil; if charted later
it reuses this sheet with the coil's first stations.

**The plate must prove:** the same bird the studies describe, at rest,
strands countable, eye placed, feet under the middle. This plate sets the
ink band (§5) and the identity every later plate is checked against — by
the studies' numbers and Jimmy's eye, not by resemblance to any old image.

### 4.2 COIL — the poised S (the fishing readiness)

| Quantity | Target | Source |
|---|---|---|
| Neck chord_base | **0.24–0.30** (deep coil 0.267–0.271) | study §2; iter2 (0.267) |
| Arc : chord | **≥ 1.9** (mechanism 2.18) | addendum §2.3 floor; iter2 |
| Neck arc | 0.72 — the full neck, stored | study §3.2 |
| Bend distribution | forward bend low (throat zone), backward bend high (hinge zone); joint caps frozen | mechanism; skeleton anchor (FARMS note) |
| Head pitch offset | +80°, bill angled down | mechanism poses/deep_coil |
| Legs | feet-centre 0.55, stagger 0.14, emergence 0.60 | LEG_CANON (qpYk f0028) |
| Hold | must read frozen for ≥4.15 s | study §3.1 (6bc poised window) |

Per part: torso RIGID · neck DEFORMING + **LAYERED at the fold** (§3.2 draw
order: descending pass → fold stack → ascending pass, ink seam between) ·
head ASSEMBLY low, watching down the bill · plume LAYERED, strands settling
against the breast · legs ARTICULATED (coil config) · tail RIGID.
The bird fishes from the MIDDLE third in this pose (blocking law).

**The plate must prove:** arc stored visibly in layers — a reader must see
~2× the chord folded into the S without any line crossing the fold; the
head low and patient; nothing about it may read as a bent tube.

### 4.3 PEAK — the standing spear (the payoff frame)

| Quantity | Target | Source |
|---|---|---|
| Neck chord_base | **0.62–0.71** (mechanism 0.673) | study §3.1; addendum §7; iter2 |
| Neck chord76 | **0.49–0.60** (mechanism 0.512) | study §3.1; iter2 |
| Reach factor (peak ÷ coil chord) | **2.3–2.7** (mechanism 2.53) | study §3.1; iter2 |
| Neck arc | 0.70–0.75 (standing class; mechanism 0.678) | addendum §7 |
| Slimming | 0.55–0.65 of rest width; extended tube ≈0.10 wide at mid, uniform | study §3.2 |
| Neck-base width | 0.0685 | iter2 |
| Head | **spear-collinear** (eye→billbase within ~2° of neck axis); pitch offset +26° | warp-spike real-frame check; mechanism |
| Bill | 0.23 long; tip at the water; entry ripple in flat black ink | study §2; environment law |
| Legs | **feet planted, identical stance family as coil**: feet-centre 0.50, stagger 0.19, emergence 0.61; legs slant back ~0.11 of span | LEG_CANON (qpYk f0037) |
| Torso | pitched ~10–15° over the feet, tail risen | qpYk f0037 |
| Timing it must serve | extension 0.10–0.25 s; release profile dip → [~3 / ~12 / ~60 / ~25] | study §3.1; addendum §2.1 |

Per part: torso RIGID, pitched · neck DEFORMING (the (u,v) sheet unfolded
and slimmed — the SAME sheet as coil, stations unmoved) · head ASSEMBLY
collinear · plume LAYERED, strands trailing behind the spear · legs
ARTICULATED (peak config — planted, slanted) · tail RIGID, risen with pitch.
NOT this pose: the lunge (chord_base 0.77–0.87, legs trailing, wings
braking) — separate class, separate future sheet (addendum §2.3).

**The plate must prove:** one straight intent from shoulder to bill tip;
the neck at full measured length (the NECK LAW — never shortened for
composition); the feet exactly where the coil left them; the bill touching
water that is not drawn, marked only by its ripple.

## 5. Paper and ink

- **Paper:** flat, muted, drawn as part of each plate. A plate is
  self-contained: no shared backdrop layer, no tonal-wash background
  borrowed across plates. (A gentle wash INSIDE a plate's own drawing is
  the drawing hand's business; what is banned is a background that exists
  independently of the bird — that independence is what made erasure, and
  its ghosts, possible.)
- **Ink protocol (measurement):** the v3 protocol — paper = corner-median;
  content = summed RGB difference > 55 from paper; black = content with
  mean RGB < 70. Black fraction is reported per finished plate.
- **Ink band:** SET by the first plate Jimmy approves under this design
  (the alert), then held at ±0.02 for coil and peak. No earlier number is a
  band. Two named anti-targets from the failure record: a washout (soft,
  pale, texture without ink structure — motion test v3) and a black cord
  (ink present but structure destroyed — fill test). The band exists to
  catch both; Jimmy's eye decides what the numbers cannot.

## 6. Drawing rules — each traced to the lesson that taught it

| # | Rule | Taught by |
|---|---|---|
| 1 | Draw whole plates per pose. No donors, no compositing, no erasing. | Donor-warp fill FAILED (drawings sit 67–101 px off their rig poses; head coverage 0.31); global-threshold erase left ghosts on tonal wash (warp spike). Whole plates delete both classes. |
| 2 | Truth is the studies + the mechanism. No image — approved or not — is a pose, geometry, or band source. | Stills-as-truth: the pre-canon strike drawing reaches 0.45 vs the bird's 0.62–0.71; every retrofit inherited the gap (RESET). |
| 3 | The fold is drawn as layered feather compression with an occlusion seam — never as a bent tube. | Tube-warp fold is geometrically impossible (inner radius ≈8.6 px < halfwidth ≈26 px) and rendered as woven moiré (warp spike). |
| 4 | Extreme poses (deep coil, true spear) are DRAWN from mechanism + studies, not produced by image-model generation. | The generator's heron prior excludes both: best generated coil arc:chord 1.40 vs ≥1.9 needed; generated peaks kept collapsing to the shorter painter's strike (keyframe pass). |
| 5 | The eye is a placed structure at the mechanism anchor on every plate. | Fill spikes 1–2: the drawn eye silently never drew — the failure was invisible until hunted (spike 3). |
| 6 | Plume = its own layer of countable strands, fixed roots, free tips. A filled mass fails regardless of metrics. | Jimmy's tell (2026-11-04): the cartoon frill vs the real one was visible at a glance when numbers passed. |
| 7 | Verify the placement of EVERY part against the studies — especially the parts nobody is looking at. | The leg carryover: traced once from a painting, inherited through every study and frame, spotted by Jimmy twice (LEG_CANON). |
| 8 | Ink bands come from the work's own approved plates, in order. | The strike band inherited from a demoted source misjudged the warp peak (band-provenance failure, warp spike). |
| 9 | Gates are measured OFF THE FINISHED ARTIFACT — grounded landmarks on the final PNG. | Fill test: build bookkeeping said one thing, the artifact another (head a shard in a paper patch at coverage 0.31–0.40). |
| 10 | One method, one shot: a failed gate stops the work; iterating is Jimmy's decision. | Failure-discipline rules (Jimmy, 2026-11-04) — gates before spend. |
| 11 | Neck texture is station-mapped (u = arc fraction) so the same marks ride the same stations in every pose. | Centreline correspondence WORKED as transport (corridor 1.00, eye 0.6 px — warp spike); the design builds it in at drawing time. |
| 12 | Legs are articulated per pose from measured configs; feet stay planted through a standing strike. | The peak frame's alert-stance feet (Jimmy's catch) + this pass's stance measurements (LEG_CANON). |
| 13 | The waterline sits at the intertarsal joint; water itself is never drawn — only its touch, in flat black ink. | Environment law (locked) + the knee-deep measurement (muskrat wade: joint at the waterline, tibiotarsus dry). |
| 14 | The neck is never shortened, tucked, or foreshortened for composition. It reads long because it IS long (arc 0.72, reach factor 2.3–2.7). | NECK LAW (Jimmy) + the strike arbitration (the old rig reached 45% of the bird). |
| 15 | Stillness is the default drawing state: plates are composed as held frames, not action snapshots. Extension is 2–6 frames at 24 fps; the coil hold is ≥4.15 s. | Night-stalk still-fraction 0.73; 6bc's frozen poised window; Jimmy's animation philosophy ("good but repetitive beats janky but random"). |

## 7. Designed for the motion that comes after (so the plates are not a dead end)

- The strike animation interpolates the neck's (u, v) sheet between the COIL
  and PEAK centreline states under the mechanism's joints; because both
  plates share stations, texture, and anchors, the unfold can be rendered
  as the SAME bird — with the release profile dip → [~3 / ~12 / ~60 / ~25]
  driving the interpolation timing (the real bird spends almost no reach in
  the first half; both earlier profiles that front-loaded were wrong
  against the bird, study §3.1).
- Withdrawal is 3–5× slower than extension when empty; with prey, handling
  (dipping every ~6–8 s) takes over — charts exist in the species package
  (20 charts / 2,004 frames of pose tracks) and are re-based onto these
  plates at the animation stage, not redesigned here.
- Gait, when animated: stalk = frozen head, body steps underneath (head
  stabilization is a NECK behavior the sheet must support: the neck absorbs
  the step), 0.15–0.30 steps/s, freezes 3–6 s; strut = ~1.6 steps/s WITH a
  small head bob, neck high, plumes erected (addendum §3).

## 8. What this design does NOT yet cover (named, with their canon)

- **Flight sheets** (cruise fold, takeoff, landing): canon exists —
  wingbeat cruise 2.7 ± 0.2 Hz, takeoff 2.85 ± 0.2 Hz (WINGBEAT_CALIBRATION);
  takeoff neck EXTENDED at liftoff, fold complete by +0.4–0.5 s; landing in
  6 phases with a LONG asymmetric balance phase (addendum §4; Boga render
  timings ÷6.0). Sheets to be designed when flight is charted.
- **Courtship display sheet:** a NECK behavior — bill-snap → rise →
  bill-skyward stretch → sway, in nuptial plumage (5 specimens in the
  library). Distinct from the wing stretch (bilateral spread, ~0.5 s real
  hold, NO neck component). Not one of the three sheets; do not let the two
  behaviors contaminate each other.
- **Preen sheet:** chart structure exists in the library (4 specimens);
  no pose sheet in this pass.
- **Swallow/handling sheets:** distension provision is designed into the
  neck sheet (§3.2); GBH distension ratio is still grey-sourced and
  provisional (addendum §2.5).
- **The lunge strike:** separate class (addendum §2.3), deferred by
  Decision 4.

## 9. Gaps (named, with what settles them)

- **GAP — GBH leg segment split, n = 1 clean frame.** Settles by: one more
  clean GBH standing profile with full legs visible (Rio Grande wading or
  a wilson placement frame), measured the same way. Until then LEG_CANON's
  pooled band stands. (LEG_CANON §3.)
- **GAP — alert-stance legs.** No clean alert frame's legs measured; alert
  uses the standing band. Settles by: the first alert plate's gate check
  against the band + any alert frame with visible legs in the library.
- **GAP — peak segment lengths.** qpYk f0037's joint read is unstable.
  Settles by: a peak frame with both legs clean (DS-class frames re-measured
  for legs specifically). Placement numbers are NOT gapped — feet and
  emergence at peak are measured.
- **GAP — empty (missed) withdrawal.** No clean specimen in the library
  (addendum §6); affects the strike chart's withdrawal timing, not these
  plates. Settles by: a measured missed strike with empty withdrawal.

## 10. Sources

RESET-2026-11-04.md · CREW_MEMORY.md ·
`art2/real-bird-measure/MOTION_STUDY_REPORT.md` (§2 proportions, §3.1 strike
kinematics, §3.2 neck mechanics, §3.3 handling) ·
`ADDENDUM_REPORT.md` (§2 strikes incl. class split + revised release profile,
§3 gait, §4 flight/landing, §7 canon table) ·
`WINGBEAT_CALIBRATION.md` (cruise 2.7 / takeoff 2.85 Hz; Boga ÷6.0) ·
atlas + atlas_addendum (real frames cited per sheet) ·
`creature-engine/packages/great-blue-heron/` (animal_v25.json — chain, caps,
width profile, slimming field, head assembly, poses; rig_v25.py — torso
loop, root, LEGS-as-error; species.yaml — palette; model_sheet.md —
canonical marks) ·
`art2/rig-v25-gate/iter2/ITER2_REPORT.md` (gate numbers: reach 2.53, coil
0.267, peak 0.673/0.512, alert 0.432) ·
LEG_CANON.md (legs: canon, corrected traces, error table, method) ·
device spec `heron/device-1024x600-spec.md` (panel, cadence, palette role).
