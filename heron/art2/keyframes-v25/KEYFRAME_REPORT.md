# KEYFRAME REDRAW ON THE MECHANISM — REPORT

Run: 2026-11-04. Task: three keyframe plates at 1024×600 drawn ON the rig v2.5
mechanism poses (alert, deep coil, strike peak), in the approved stills' own
recipe and identity. NO animation. These plates go to Jimmy's approval gate.

**Verdicts up front**

| Plate | Filed file | Verdict |
|---|---|---|
| ALERT | `keyframe_alert.png` (= candidates/alert_c3.png) | **Meets landmark band + ink band.** One disclosed defect: eye/head sit 19 px from the mechanism's eye anchor (nominal tolerance ~10 px). |
| DEEP COIL | `keyframe_coil.png` (= candidates/coil_c3.png, best candidate) | **DOES NOT MEET the landmark band** — no coil candidate did. Filed as best candidate only; gap named below. |
| STRIKE PEAK | `keyframe_peak.png` (= candidates/peak_c2.png, best ink/identity candidate) | **DOES NOT MEET the landmark band** — no peak candidate did. Filed as best candidate only; gap named below. |

Generation budget used: 18 candidates (6 per pose — the agreed cap). No band
was lowered anywhere in this run.

---

## 1. Method — how the stills' recipe was reproduced

The approved stills' own records (`finished-art-stills/ART_STILLS_REPORT.md`
and the locked generation brief `finished-art-stills/motion-test/work/brief_strike_v2.txt`)
show the recipe that produced `audubon_rest.png` / `audubon_strike.png`:

1. A monochrome pose canvas (a study render of the pose) is given to
   `media.generate_image` as the first input image — image-to-image repaint.
2. A locked Audubon brief supplies identity: field-mark checklist, "Audubon's
   Plate 211 as north star," and a GEOMETRY LOCK paragraph (the canvas is the
   only source of pose/position/scale; do not recompose).
3. Generation at 2048×1184, then a **direct downscale to 1024×600** (the same
   ~1.35% anisotropic normalization the approved stills carry).

This run reproduced that recipe exactly, with the pose canvases built from the
**rig v2.5 mechanism itself** (build `rig-v25-mechanism-iter2`, species package
`animal_v25.json` / `rig_v25.py`; masks from `rig-v25-gate/iter2/`):

- **Pose canvases** (`work/build_canvas.py`, outputs in `work/`): for each pose,
  the mechanism's own silhouette, neck chain stations, head assembly and eye
  anchor were rendered from the package solver. Two canvas flavours were used:
  a **flat slate silhouette** on the stills' paper tone, and a **tonal wash**
  version (distance-transform shading + dark edge) — the wash is the flavour
  that unlocked geometry in the earlier work. Annotated reference renders
  (chain/stations/anchors marked) were kept for measurement only and never
  sent to the generator.
- **Identity conditioning, three routes tried:**
  (a) both approved stills attached as identity images (the stills' recipe);
  (b) text-only identity — the locked brief's field-mark checklist with NO
  stills attached;
  (c) a resume/edit pass starting from a finished candidate, with the pose
  study introduced as a new reference (peak only).
- **The v3 finish model was NOT used** (it failed on ink — watercolor wash,
  black 0.126 — in motion test v3; forbidden for these plates by the brief).

**Measurements** (all off the drawn 1024×600 frames):

- *Ink*: the motion-test-v3 `measure_v3.py` protocol — content mask = pixels
  differing from the corner-median paper by >55 summed RGB; black fraction =
  content pixels with mean RGB < 70 over content pixels. Reference points
  measured this run: `audubon_rest` black = **0.2593** (alert/coil band
  0.252–0.272 per the brief); `audubon_strike` black = **0.3144** → peak band
  applied as ±0.010 → **[0.304, 0.324]** (derivation disclosed; the gold-corpus
  family peaks ≈0.36–0.38 are context, but per the task the band is taken from
  the approved strike still's own fraction).
- *Neck landmarks*: the rig's centreline-entry protocol — visual-grounding
  points for bill tip, occiput (rearmost skull), eye, breast/neckbase, and
  centreline stations at 25/50/75% head→body; skull = occiput + 0.052·torso
  along the bill direction; chain = [skull, stations…, neckbase]; torso =
  496.3 px (the gate constant). **Protocol validation: run on the iter2 peak
  mask it reproduces the gate's own published peak chord_base (0.673).**
- *Eye*: amber test on a crop around the mechanism's eye anchor (R>110,
  55<G<195, B<115, R−B>45, R≥G), connected components ≥8 px; the nearest
  plausible iris cluster's distance to the anchor is reported. Borderline
  alert cases were re-measured at the raw 2048×1184 resolution (same result)
  and confirmed by viewing enlarged head crops.

Mechanism reference values (design): alert chord_base 0.456, eye anchor
(754.7, 35.7); coil chord_base 0.269, arc:chord 2.58, eye anchor (704.5, 128.6);
peak chord_base 0.666, chord76 0.516, eye anchor (811.1, 496.2).

---

## 2. Measurement table — all candidates

Bands: alert chord_base 0.40–0.47 · coil chord_base 0.24–0.30 AND arc:chord ≥1.9 ·
peak chord_base 0.62–0.71 AND chord76 0.49–0.60 · ink alert/coil 0.252–0.272,
peak 0.304–0.324 · eye within ~10 px of anchor.

### ALERT

| Cand | Route | Black | chord_base | Eye dist (px) | Read |
|---|---|---|---|---|---|
| c1 | flat canvas + stills | 0.2501 ✗ | — (still-copy family, IoU vs rest 0.747) | — | a repaint of audubon_rest, not the mechanism pose |
| c2 | flat canvas + stills | 0.2477 ✗ | — (IoU vs rest 0.793) | — | same |
| **c3** | **wash canvas, text identity** | **0.2646 ✓** | **0.456 ✓** | **19.0 ✗** | **SELECTED** — strongest identity read of the run |
| c4 | wash canvas, text identity (rerun) | 0.2521 ✓ | 0.395 ✗ (0.005 under floor) | 24.7 ✗ | head carried too far right |
| c5 | flat canvas, text identity | 0.2835 ✗ | — (ink decides) | ~16 (moot) | over-inked |
| c6 | wash canvas, text identity (rerun) | 0.2595 ✓ | 0.424 ✓ | 13.1 ✗ | feet splayed flat on the water in a wide walking stance; bill over-orange, lore blemish |

### DEEP COIL

| Cand | Route | Black | chord_base | arc:chord | Eye dist | Read |
|---|---|---|---|---|---|---|
| c1 | flat canvas + stills | 0.2674 ✓ | — | — | — | screened out on silhouette IoU (0.460, family-lowest) before landmark measurement — disclosed |
| c2 | wash canvas + stills | 0.2757 ✗ | 0.432 ✗ | 1.27 ✗ | — | loose S, head at shoulder height |
| **c3** | **wash canvas, text identity** | **0.2609 ✓** | **0.391 ✗** | **1.35 ✗** | **50.8 ✗** | **best ink-passing coil — filed as best candidate, NOT passing**; one leg mid-step |
| c4 | wash + deep-coil brief | 0.2514 ✗ (0.0006 under) | 0.366 ✗ | 1.01 ✗ | none at anchor | head bowed straight down at the water — wrong fold topology |
| c5 | flat canvas + deep-coil brief | 0.2497 ✗ | — (ink decides) | — | — | same bowed-head topology by eye |
| c6 | wash + stills + deep-coil brief | 0.2893 ✗ | 0.301 (0.001 over ceiling) | 1.40 ✗ | ~194 ✗ | closest chord of any coil, but the head hangs to the water and the body is the strike still's (oversized black saddle) |

**Coil gap, named:** every generator route draws either a loose alert S
(chord 0.39–0.43) or a vertical head-bow (arc:chord ≈1.0). The mechanism's deep
fold — chord 0.24–0.30 with arc:chord ≥1.9, head held at the breast with the
bill pointing forward-down — was never produced. Best arc storage achieved:
1.40. The deep compressed fold sits outside the image model's heron prior;
no wording tried (three brief variants, two canvas flavours, with/without
stills) moved it into band.

### STRIKE PEAK

| Cand | Route | Black | chord_base | chord76 | Eye dist | Read |
|---|---|---|---|---|---|---|
| c1 | flat canvas + stills | 0.3129 ✓ | — (IoU vs strike 0.827) | — | — | repaint of audubon_strike |
| **c2** | **wash canvas + stills** | **0.3216 ✓** | **0.453 ✗** | **0.361 ✗** | **72.8 ✗** | **filed as best ink/identity candidate, NOT passing — it is effectively the approved strike drawing again** |
| c3 | wash canvas, text identity | 0.2407 ✗ | — | — | — | neck drawn as a smooth arc (drinking pose) |
| c4 | wash + stills + "reach farther" | 0.3110 ✓ | — (IoU vs strike 0.825) | — | — | still-copy again; the wording did not extend the reach |
| c5 | wash + rest still only + anti-arc brief | 0.2400 ✗ | 0.498 ✗ | 0.426 ✗ | ~25 ✗ | **geometry-best peak** — head lowest/rightest of any candidate, but ink washed out and the neck still curves |
| c6 | resume/edit of c2 + pose study | 0.3180 ✓ | 0.527 ✗ | 0.414 ✗ | ~57 ✗ | the edit preserved ink/identity but did not move the head to the study's position (chord reads differ c2↔c6 partly by landmark placement variance, ±~0.04) |

**Peak gap, named:** with the stills attached, the generator reproduces the
approved strike composition — and **the approved strike drawing itself
measures chord_base ≈0.45 by this protocol**, i.e. the mechanism's spear
(0.62–0.71) is genuinely ~40% longer than the reach drawn in the approved
still (this is the iter2 disclosure surfacing in the art). Without the stills
the generator reaches a little farther (0.498) but the ink washes out
(0.240 vs the 0.304 floor) and the neck bends into an arc instead of the
straight spear. No route produced ink + straight spear + full reach together.

---

## 3. The filed plates, in plain words

- **keyframe_alert.png** — A tall sentinel heron at the waterline, slate-blue
  engraved plumage, white head with the black brow sweeping into long plumes,
  golden eye, shaggy breast-plume strands hanging clear of the body, two thin
  dark legs among a few reeds. It reads unmistakably as **the same bird as
  audubon_rest** — same hatch character, same head pattern, same restrained
  colors. Neck geometry matches the mechanism's alert design exactly
  (chord_base 0.456 vs design 0.456). Known defect: the whole head sits ~19 px
  right-and-down of the mechanism's head position (eye 19.0 px from anchor vs
  the ~10 px nominal).
- **keyframe_coil.png** (best candidate, NOT passing) — The same bird, ink and
  identity in family, but the "coil" is only a gentle S: the head rides at
  shoulder height and one leg is caught mid-step. It does **not** show the
  mechanism's deep fold — head pulled down to the breast, neck storing 2.6×
  its chord in arc. Chord 0.391 vs the 0.24–0.30 band; arc:chord 1.35 vs ≥1.9.
- **keyframe_peak.png** (best candidate, NOT passing) — Essentially the
  approved strike drawing re-rendered: fully extended-looking strike over the
  waterline, ink and identity exactly in family — because it *is* the still's
  composition. Against the mechanism it falls ~100 px short: chord 0.453 vs
  0.62–0.71, the head landing well above and left of the mechanism's strike
  point.

## 4. Disclosures

1. **Peak ink band derivation:** the brief's gold-family peaks measure
   ≈0.36–0.38, but per the task instruction the band was taken from the
   approved strike still's own measured fraction (0.3144 ± 0.010 →
   [0.304, 0.324]). Under the gold-family band, c2/c6 would also fail ink;
   under the applied band they pass ink and fail geometry. Either way peak
   does not pass.
2. **Alert eye tolerance:** the selected alert plate meets the two hard bands
   (landmarks, ink). Its eye misses the nominal ~10 px tolerance at 19.0 px.
   The stop rule in the brief triggers on (a)+(b); the eye miss is disclosed
   here rather than silently absorbed, and it is Jimmy's call at the gate
   whether 19 px is acceptable — in an animation build the head is a separate
   assembly the rig positions, so the offset is a plate defect, not a rig
   defect.
3. **Screened candidates:** coil_c1 was excluded on silhouette IoU before
   landmark measurement (family-lowest 0.460); alert_c1/c2, peak_c1/c4 are
   still-copy repaints identified by IoU vs the stills (0.75–0.85) and were
   not landmark-measured; alert_c5 and coil_c5 failed ink outright and were
   not landmark-measured. All 18 candidates are preserved in `candidates/`.
4. **Landmark measurement noise:** grounding points carry ±10–20 px placement
   variance on soft features (breast point, stations); chord values carry
   roughly ±0.04. No verdict in this run turns on a margin that small except
   coil_c6's chord (0.301 vs a 0.30 ceiling) — and it fails decisively on
   arc:chord, ink and eye regardless.
5. **What the run established about routes:** (i) attaching the stills locks
   composition to the stills — identity is guaranteed but so is the stills'
   geometry; (ii) text-only identity preserves identity and ink at alert
   (c3/c6) — the stills were not needed there — but cannot hold peak ink;
   (iii) prompt wording ("reach farther", "deep tight U") does not move
   geometry measurably; (iv) the tonal wash canvas outperforms the flat
   silhouette on every pose. Closing the coil and peak gaps would need a
   conditioning route stronger than reference-image guidance (e.g. true
   control-style img2img, or a composite build: mechanism-true neck/head
   region generated separately and married to the torso plate) — **not
   attempted here; that is a decision for Jimmy, and nothing downstream of
   these plates is authorized.**

Files: `keyframe_alert.png`, `keyframe_coil.png`, `keyframe_peak.png`,
`candidates/` (18), `sidebyside/` (each filed plate beside its nearest
approved still), `work/` (canvases, build script, raw generations, metrics).
