# STRIKE MEASUREMENT — whose neck is right at full extension?

Measurement ONLY. No fill, no geometry edits, no rig changes, no roster work.
Instruments: spike 3's `drawn_landmarks.py` (DL) reused unmodified for corpus
frames; a pose-free standalone measurer (bill → eye → skull → skeleton
centreline) for the approved stills, validated against DL on the golds first.
All lengths in px on each image's own canvas unless stated.

## 1. RATIOS TABLE — neck run (station-1 → skull)

| subject | chord (px) | arc (px) | torso ref (px) | run ÷ torso (chord) | run ÷ torso (arc) |
|---|---|---|---|---|---|
| **Approved STRIKE still** (standalone) | 257.7 | 278.9 | 503.5 | **0.512** | 0.554 |
| Corpus gold strike f0027 (DL) | 200.8 | 201.5 | 387.3 | **0.518** | 0.520 |
| **Rig v2.4 strike f0027** | 109.7 | 111.2 | 443.9 (poly) | **0.247** | 0.250 |
| Rig f0027, alt. torso ruler (uniform-on-silhouette 508.3) | 109.7 | 111.2 | 508.3 | 0.216 | 0.219 |
| **Approved REST still** (standalone) — control | 200.8 | 266.1 | 488.4 | 0.411 | 0.545 |
| Corpus idle gold f0030 (DL) — control | 126.5 | 173.3 | 425.6 | 0.297 | 0.407 |
| Rig idle (DL control pose) | 115.7 | 157.0 | 443.9 (poly) | 0.261 | 0.354 |

Headline ratios:

- **Approved vs gold (strike): 0.512 vs 0.518 — agreement within ~1%.** The
  generated gold f0027 *is* the approved strike still's neck, at corpus scale
  (raw-chord scale check: 257.7 / 200.8 = 1.283 vs the registration audit's
  1/0.7748 = 1.291 — within 1%).
- **Approved vs rig (strike): 0.512 vs 0.247 → the approved run is 2.07× the
  rig's** (2.37× on the alt torso ruler). In the shared corpus canvas
  (spike 3's framing): drawn 200.8 vs rig 109.7 = **1.83×**.
- **Control (rest/idle): drawn ↔ rig agree.** DL idle gold vs rig idle:
  chord ratio 1.09, arc ratio 1.10 — the same agreement spike 3's control
  showed (landmark deltas 3–23 px). Standalone-vs-DL on the idle gold reads
  +30% on chord (a definitional gap on coiled poses — station-window
  centroids vs an anatomical centreline — see §5); the rest still vs the
  idle gold *within the standalone method* agrees to ~2% (0.411 vs 0.403),
  so the control chain is consistent inside each method.

### The strike family across the extension (DL drawn chord vs rig chord)

Rig chart phases (rig run by frame): coil plateau ≈ 48–51 (f0011–f0025) →
fire f0026 → **extension plateau 109.7 (f0026–f0029)** → withdrawal
(f0030–f0038) → re-extension to 110.1 at f0051 (looping chart).

| frame | phase (rig) | drawn chord | rig chord | drawn ÷ rig |
|---|---|---|---|---|
| f0020 | coil | — (detector failure, see §5) | 48.4 | — |
| f0025 | last coil frame | 138.8 | 50.5 | **2.75** |
| f0027 | plateau (approved anchor) | 200.8 | 109.7 | **1.83** |
| f0029 | plateau end | 93.9 | 109.7 | **0.86** |
| f0034 | withdrawal | 75.5 | 31.9 | **2.37** |

**The gold-vs-rig ratio is NOT uniform — it swings 0.86–2.75.** The golds are
not phase-locked to the rig: at f0025 the drawing is already committed down
to the water while the rig still holds its coil; at f0029 the drawing is
already recoiling while the rig still holds full extension. Landmark seating
on f0025/f0029 was verified by eye on annotated overlays
(`overlay_strike_f0025.png`, `overlay_strike_f0029.png`) — the scatter is in
the drawings, not the detector. At the plateau's anchor frame (f0027, the
approved still's own frame) the overshoot is 1.83×.

### Extension factors (strike ÷ rest, within each subject)

| subject | reach (chord) factor | centreline (arc) factor |
|---|---|---|
| Corpus drawings (DL) | **1.59** | 1.16 |
| Approved stills (standalone) | 1.28 * | 1.05 |
| **Rig v2.4** | **0.95** | **0.71** |

\* the stills' chord factor is understated by the standalone coil-chord
reading (+30% on coiled poses); the DL-consistent estimate sits nearer the
drawings' 1.59. The arc factors are the anatomically honest ones: a real
neck's centreline barely grows when it unfolds (drawings +16%, stills +5%) —
unfolding converts the S-curve into *reach*. **The rig does the opposite of
both: its strike tube (111.2) is 29% SHORTER than its own idle tube (157.0),
and its reach does not grow at all (0.95).**

## 2. WIDTH PROFILES — is the rig's strike tube also too wide?

Neck tube width (px) at the rig stations, full extension (f0027):

| station | gold (drawn) | rig footprint | Δ |
|---|---|---|---|
| s1 (base) | 36 | 33 | −3 |
| s2 (mid) | 26 | 28 | +2 |
| s3 | 25 | 25 | 0 |

At matched run fractions (0 / 0.25 / 0.5 / 0.75): gold 36/26/24/24 vs rig
33/29/26/22 — same story. The approved strike still's mid-run widths,
scaled to canvas px (÷1.283), read 23–25 at mid-run vs the gold's 24–26 —
agreement. (Standalone fraction endpoints sit at slightly different arc
positions than DL's station windows: its base point reads 27 vs 36 and its
near-head point 14 vs 24; mid-run, the load-bearing comparison, matches.)

**Slimming factors — width at extension ÷ width standing (mid-tube):**

| subject | slimming factor |
|---|---|
| Corpus drawings (station s2: 26 ÷ 44) | **0.59** |
| Approved stills (standalone, mid-run: 32 ÷ 53, scale-free) | **0.60** |
| Rig v2.4 (station s2: 28 ÷ 45) | **0.62** |
| Rig pose parameter `neck_w` (0.62 at strike ÷ 1.00 at idle) | 0.62 |

**Width verdict: NO — the rig's strike footprint is not too wide, and it is
not a fixed tube.** The pose track already slims the tube at extension
(`neck_w` 1.00 → 0.62), the measured footprint slimming (0.62) matches both
drawing sets (≈0.6), and at f0027 the rig's absolute station widths sit
within 3 px of the gold's at every station. The extension failure is
purely one of LENGTH. One genuine width discrepancy exists, at the other
end of the chart: at **idle**, the rig's neck-base width (s1: 70) is ~40%
wider than the drawing's (49) — a standing-pose base flare difference, not
an extension error. (Widths at f0025/f0029 diverge between gold and rig,
but that is the phase mismatch of §1, not tube modelling: they are
measuring different moments of the strike.)

## 3. VERDICT

**(a) — Approved ≈ corpus gold (long). The rig's strike pose is
under-extended.**

- The approved strike still's normalized neck run (0.512 of torso) matches
  the corpus gold's (0.518) to ~1%. The generated drawings did not drift:
  at the anchor frame they carry the approved still's own proportions.
- The rig delivers about half of that: normalized 0.247 (0.216 on the
  least favourable torso ruler). **The shortfall: 91 px in the shared
  corpus canvas (rig 109.7 vs drawing 200.8 — the rig's strike run needs
  ×1.83), equivalently ≈0.27 torso-lengths, equivalently the rig reaching
  48% of the approved proportion.** In arc terms it is worse: the rig's
  strike tube is shorter than its own idle tube.
- Phase caveat, stated plainly: the approved strike still is the terminal
  moment of a strike (bill tip touching the water); f0027 is the plateau's
  middle. The poses are not the identical instant — but their normalized
  runs agree to ~1% anyway, so the caveat does not move the verdict.
- What follows from this (a rig strike-track extension of the neck, or
  accepting the drawings' phase behaviour) is Jimmy's next decision.
  Nothing here was changed.

## 4. REAL BIRD — Harry (survey first; no usable multi-state set exists)

Survey of all DWARF material on hand (UniFi Protect not touched — shelved
by Jimmy's order):

| source | contents | Harry? |
|---|---|---|
| `~/workspace/dwarf/sky-2026-11-03/park_wide_final.jpg` (local) | wide frame, midnight, dock light | **YES — profile, head down on the lift beam** (~90 px body) |
| Spark `dusk-2026-11-03/` — 101 wide frames, 16:55–18:34 EST | lift in daylight → dark | Daylight frames: lift EMPTY. **One night frame (wide_225301, 17:53 EST) shows him** on the beam, hunched/rear view, green night image (~100 px) |
| Spark `dusk-2026-11-03/` — ~101 tele frames | water surface, then black | No — tele was aimed at the water |
| Spark `dawn-2026-11-04/` — 136 frames (tele + late wide) | tele = featureless green glow pool; wide = empty lift in daylight | No (he never showed at dawn) |
| Spark `frames-2026-11-03/` stills | tele = water surface; wide = the lift, daylight | No — lift empty |
| Spark `aim2/`, `brighten-*/`, `sky1/`, local `probe/` smoke frames | stream/aim/exposure tests, water/sky/black | No |
| Spark `m31-session*/` | astro FITS sessions | No |

**Conclusion, plainly: no usable multi-state Harry frames exist, so no
real-bird extension or slimming factor can be measured.** The only two
frames that contain him are both green night wide-lens frames, both in
head-down/coiled feeding postures — one neck state, not two — at a scale
where his whole body is ~90–100 px and the neck tube ≈5 px wide (a width
reading would carry ±40%+ error; see crops `harry_park_wide_final_crop.png`,
`harry_dusk_wide_225301_crop.png`). The park frame does confirm, at the
qualitative level, that his foraging posture folds the neck down over the
beam — it says nothing quantitative about extension.

**What would settle it:** one dusk session with the DWARF **tele** stream
aimed at the lift while Harry fishes, grabbing frames across a single
strike (standing alert → strike → head-down). At ~20 ft the tele FOV puts
him at several hundred px (neck run 100+ px, tube widths 15–30 px), which
supports both factors at roughly ±10%. A phone/telephoto burst from the
pier during a strike would serve as well. Until such frames exist, the
real-bird column of the table stays empty by evidence, not by omission.

## 5. METHOD, NORMALIZATION, CAVEATS

- **Corpus frames** measured with spike 3's `drawn_landmarks` unmodified
  (bill = yellow class, eye = amber iris cluster, skull = head-mass
  centroid ≤55 px from eye, stations = content centroids at the rig's
  spine stations). Validation: it reproduces spike 3's f0027 numbers
  *exactly* (drawn 200.8, rig 109.7, ratio 1.83).
- **Rig geometry** from `roster_render_v24.kp_master` on the corpus's own
  pose tracks (strike poses = `pose_tracks_v2.json`, the exact poses
  build_corpus used; idle = `pose_tracks_v24` idle hold). Run = spine[1] →
  head_c: chord = straight distance; arc = the spine polyline through
  spine[2..4]. Rig neck widths scanned on the neck channel (stack ch 1)
  perpendicular to the spine at the stations / run fractions.
- **Approved stills** measured pose-free: plate mask = the project's own
  gate protocol (`build_corpus.bird_mask` shape; threshold raised to 100
  to shed the plates' soft shadow wash — the bird's features are
  high-contrast and unaffected); bill from the yellow component, head
  centre from bill geometry, eye = amber cluster nearest the head centre,
  skull as in DL; neck centreline = shortest skeleton path (pure step
  length) from skull to the torso DT-core; station-1 = the point at the
  rig's own station definition (bezier t≈0.24 from the breast anchor B,
  B = first sustained 2.2× width/DT flare). Cross-validated on the golds:
  strike arc agreement +1%, chord −8% vs DL. One trap found and avoided:
  hole-filling the mask fills the paper pocket enclosed by
  body/neck/bill/water in the strike pose and destroys the measurement —
  masks are used unfilled.
- **Normalization reference = torso hull length**, measured three ways and
  reported openly because they spread ±14%: the rig's torso polygon hull
  (443.9, constant across strike poses); a uniform mask algorithm
  (cut at station-1, erode-8 core, reconstruct, hull diameter) applied
  per image (gold f0027 387.3, approved strike 503.5, approved rest
  488.4, idle gold 425.6); the same algorithm on the rig silhouette
  (508.3 strike / 465.8 idle — it over-reads clean silhouettes by
  absorbing tail/wing mass). The verdict survives every ruler: the rig
  sits at 0.216–0.247 vs the approved 0.512. Within the corpus, raw px
  are also directly comparable (one canvas, one scale, by construction);
  the stills' scale vs the corpus was verified against the registration
  audit's fitted scales (strike 0.7748, idle 0.8347).
- **Definitional caveat (coiled poses):** on a coiled/S neck, DL's
  station-window chord reads ~30% shorter than the anatomical-centreline
  method (the windows cut the S's corners and station-1 sits high).
  All coiled-pose comparisons in this report are made *within* one
  method; the strike comparison — the question asked — is unaffected,
  because at full extension the tube is nearly straight and the two
  methods agree to 1–8%.
- **f0020 drawn extraction failed** (the validated detector finds no
  yellow bill mass in that gold — bill fell back to rig, eye not found);
  the frame is excluded from the drawn family rather than measured with a
  fallback. f0034's drawn *station widths* are contaminated (withdrawal
  fold crosses the scan lines); its run, anchored on a found eye, is
  reported with that flag.
- Idle s3 widths are contaminated on both sides (scan crosses into the
  head/plume mass); mid-tube s2 is the clean width comparison at rest.
- Harry frames: DWARF wide stream is 1280×720; all Harry sightings are
  in the green dock-light (night) exposure.

## Deliverables in this folder

- `STRIKE_MEASURE_REPORT.md` — this report
- `landmarks_approved_strike.png` — landmark overlay on the approved
  strike still (viewed: centreline tracks the drawn tube, eye/base/tip
  seated) · `landmarks_approved_rest.png` — same for the rest still
- `overlay_strike_f0025.png`, `overlay_strike_f0029.png` — DL landmark
  overlays evidencing the family phase scatter
- `harry_park_wide_final_crop.png`, `harry_dusk_wide_225301_crop.png` —
  the only two Harry frames in existence, cropped
- `corpus_results.json`, `stills_results.json` — full numeric records
- `measure_core.py`, `measure_corpus.py`, `measure_stills.py`,
  `make_overlays.py` — the instruments (measurement only)
