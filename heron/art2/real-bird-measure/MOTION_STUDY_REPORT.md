# REAL-BIRD CHARACTER + MOTION STUDY — great blue heron, from Jimmy's reference library

2026-11-04 · Measurement only — no fill, no geometry edits, no rig changes.
Method: frames extracted at native fps; landmarks by visual grounding on frames; ratios
normalized by in-frame torso length exactly as STRIKE_MEASURE did (torso = hull-diameter
analogue over tail-tip / chest-front / back-top / belly points). Two chord definitions are
kept distinct throughout: **chord_base** = skull→neck-base-entry distance, and **chord76** =
skull→station-1 (point at 76% of centreline arc) — the definition the art/rig numbers use.
At full extension the neck is near-straight and chord76 ≈ 0.78 × chord_base.
Raw records: `measurements.json`; scripts + motion CSVs in `work/`; frames in `frames/`;
annotated keyframes in `atlas/` (all atlas images viewed by the measurer before filing).

## 1. Per-video validity accounting

| Video | Species | Content used | Strikes present | Strikes measurable | Rejected / flagged |
|---|---|---|---|---|---|
| heron-muskrat-hunt.mp4 (267 s, 29.97 fps) | GBH | Prey handling, dipping bout, wading immersion, standing postures | ~4–5 grabs | **0** (distance + edits — catches happen between cuts) | Strike geometry rejected (bird too small); handling is the value here |
| qpYkzsJIQ4M.mp4 (52 s, 29.97 fps) | GBH | **The canon standing spear (t≈1.5–1.7 s)**, coil baseline, wading gait, head-still segment | 3 scenes | **1** (opening spear: full body, near-profile, legs planted) | t≈21–25 s scene = repeated jabs at a stranded fish; geometry rejected (bird cropped at frame edge, torso ruler unstable 463–771 px). Playback rate of the jab scene uncertain → its timings not used |
| UR4n4gYX2T4.mp4 (83 s, 30 fps) | GBH | Best profile subject in the library: standing proportions, ~50 s prey manipulation, real-time swallow of a long eel-like fish, head-scan holds | 0 (prey already caught when clip opens) | 0 | — |
| oaBwwXsn_K0.mp4 (42 s, ~29.95 fps, portrait) | GBH | Swallow of a deep-bodied fish at very close range: distension, bolus travel, post-swallow gape | 1 (fish already speared by t=2 s) | 0 | **Slow motion (rate unknown)** — all timings flagged; ratios unaffected |
| Z7br9pofYKI.mp4 (55 s, 29.97 fps, portrait) | GBH **juvenile** | ~35 s dipping/repositioning of an oversized fish; swallow; throat distension | 0 | 0 | Handheld camera — timings coarse; juvenile plumage (skeletal proportions near-adult) |
| IVnMX3wbv9U.mp4 (45 s, 23.98 fps) | **GREY heron — reclassified** (see §5) | Wing-assisted lunge catch | 1 | 0 | Oblique angle + probable slow motion; excluded from all GBH pooling |
| 6bcHcoarCU4.mp4 (103 s, 59.94 fps) | GBH | **Lunge strike at 59.94 fps (t≈59.3 s)**, ≥4.15 s frozen coil-hold measured, stalk steps, standing postures, small-fish swallow ~t=74 s | 1 | **1** (lunge — body pitch contributes; flagged wherever used) | t≈22–26 s hunched bill-to-water: drinking or preening, ambiguous — not counted as either |
| P7Yb_koYsoA.mp4 (311 s, 25 fps) | **GREY heron** (cousin — §5, reported separately) | Clean standing spear t≈113.3–114.0 s, stalk crouch, standing proportions, leg segments | ≥3 | **1 clean** + 1 partial (surface stab t≈118.5 s, extension already complete at window start) | Compilation with cuts; several strikes too distant |

**Strikes pooled for GBH canon: 2** (qpYk standing spear; 6bc lunge) + 1 grey strike for the
cousin column. That is a small n — every canon range below is stated wide enough to hold both,
and the geometry pass should treat the *absolute chords* (coil, peak) as the targets, not any
single strike's ratio.

## 2. Character / proportions (GBH unless noted)

All values × torso length. Ranges span the measured frames in `measurements.json`.

- **Neck centreline (arc), total:** **0.70–0.75** (cleanest read: UR t=75 s, neck held
  straight up, 5-point polyline → 0.728). Coiled-pose polylines under-read the S by
  construction and are floors only (0.39–0.45). One suspect-high read (muskrat t=73 s, 0.945)
  is flagged in the records — its torso is probably under-read (tail in grass).
- **Standing coil chord (chord_base):** **0.27–0.36** — deep hunting coil 0.268–0.271
  (qpYk t=1.40 s; grey f78 same), alert coil 0.355 (UR t=1 s). In chord76 units the deep coil
  is ≈ 0.25–0.30 — the corpus idle gold (0.297) and the rig's idle (0.261) both sit in range.
- **Bill:** **0.20–0.31 × torso, pooled median ≈ 0.23.** Bill ≈ 0.47–0.58 of (bill + head);
  (bill + head) = 0.37–0.56 × torso. Bill vs neck run: at strike peak the bill alone is
  ≈ 0.3 of the extended run.
- **Torso depth:** **0.44–0.59 × torso** on horizontal bodies (UR early 0.444, grey stand
  0.494, BC stand 0.588). Steep-pitch frames inflate it (0.667) and are excluded from the range.
- **Legs** (measured on the grey, GY stand t=152 s; GBH legs were water- or grass-hidden in
  every GBH frame — see Gaps): exposed tibiotarsus **0.24–0.25**, tarsometatarsus
  **0.17–0.20**, total exposed leg **0.42–0.44 × torso**. The femur/thigh is inside the body
  plumage in every frame — unmeasurable from video.
- **Neck width (edge-to-edge):** standing unloaded (UR t=75 s): tip 0.161 / mid 0.175 /
  base 0.184 × torso — a near-uniform tube, base only ~14% wider than tip. Coiled (qpYk):
  mid 0.195, base 0.20.
- **Posture atlas:**
  - *Standing alert:* neck up in a shallow S, chord_base 0.36–0.71 depending on how extended
    (UR early 0.355 → UR tall 0.726 chord_base with neck vertical).
  - *Resting coil:* the S quantified — chord collapses to 0.27 while the centreline stays
    ≈ 0.70–0.75; i.e. **at rest the bird stores ~2.6× its chord in arc**. Bends: one forward
    bend low (throat), one backward bend high (the kink behind the head) — visible in
    atlas_02 and the qpYk f28 centreline.
  - *Stalking crouch* (grey, t=234 s): body pitched down ~20°, neck held low and forward,
    chord76 0.220, arc 0.374 (floor), torso depth reads 0.346 (pitch-foreshortened).
  - *Pre-strike coil:* identical to the deep resting coil (qpYk f28: chord_base 0.271);
    6bc's bird struck from a stalk-walk at chord 0.457 and dipped to 0.355 before release.
- **Stance in water — "knee-deep" measured:** muskrat t=124 s, an actively fishing bird:
  waterline sits **exactly at the intertarsal joint** — the full tarsometatarsus (0.17–0.20
  torso) submerged, tibiotarsus dry. Grey at the shore margin: water at the feet only.
  Fishing stance range in the library: **0 → full tarsus; the joint-deep stance is real and
  is the deepest common one.** Body height above waterline in that frame ≈ exposed
  tibiotarsus + torso depth ≈ 0.7 torso.

## 3. Motion

### 3.1 Strike kinematics (the canon section)

Three strikes measured frame-by-frame (full chord(t) samples in `measurements.json`):

| | qpYk spear (GBH) | 6bc lunge (GBH) | P7Yb strike 1 (GREY) |
|---|---|---|---|
| Baseline coil chord_base | 0.271 (standing) | 0.457 walking → 0.355 dip | 0.268 (standing) |
| Peak chord_base / torso | **0.62–0.71** | **0.77** (lunge-inflated) | **0.71** (baseline hull; 0.88 per-frame hull) |
| Extension duration | **0.13 s** | **0.12–0.15 s** | **0.16–0.24 s** (25 fps bound) |
| Reach factor (peak ÷ coil chord) | 2.61 | 1.69 (vs walking) / 2.15 (vs dip) | 2.63 |
| Withdrawal | head stays down (catch) | head stays down ~1 s+ (catch + subdue) | 44% recovered in 0.48 s → full re-coil ≈ 1 s |

- **Phase timings (pooled):** coil hold — from a frozen poised stance, **≥4.15 s measured**
  of 100% below-threshold frames (6bc, 55.0–59.15 s at native fps; the poised window runs
  ~15 s with occasional single steps); a strike can also fire mid-stalk with no freeze.
  Release — a **dip first**: chord *falls* 10–20% for ~0.03–0.05 s as the S begins to unfold
  (qpYk 0.271→0.235; 6bc 0.457→0.355). Extension — **0.10–0.25 s**. Contact — at peak chord.
  Withdrawal — **3–5× slower than extension** when empty; with prey, the head stays down and
  handling takes over (no clean withdrawal exists in the library after a catch).
- **Extension profile (canon):** the release is **middle-loaded, not front-loaded**. The 6bc
  strike (8 samples at 59.94 fps) gives quarter-bins ≈ **[3 / 10 / 78 / 9]%** of total reach
  per quarter of the release window — under 15% of reach in the first half, ~three-quarters
  arriving in the third quarter, short settle. Binning error is ±15 pts (the jump falls
  between two samples), but every measured strike agrees on the shape: dip → slow start →
  explosive middle → peak. qpYk's sparse samples (0% / 46% / 100% of window vs 0% / 46% /
  100% of reach) are consistent with that and inconsistent with a front-loaded curve.
  **Both prior profiles are wrong against the bird: corpus gold [45/24/14/18]% and motion
  test v3's [70/0/29/0]% spend most of the reach in the first quarter; the real bird spends
  almost none there.**
- **Peak run (the geometry target):** chord_base **0.62–0.77 × torso** across GBH strikes
  (0.71 for the grey). Converted to the strike-measure's chord76 units: **≈ 0.49–0.60,
  central ≈ 0.55**. The approved art's 0.512 sits inside the real range. The rig's 0.247
  does not — it reaches ~45% of the real bird's run (the ×1.83 arbitration against the art
  stands, and against the bird it is ×~2.2).

### 3.2 Neck mechanics across states

- **Arc conservation:** the strike is an **unfolding, not a lengthening**. Chord grows
  0.27 → 0.70 while the centreline available is 0.70–0.75 in both states (straight-standing
  arc 0.728 ≈ peak chord 0.70 + residual curve). Arc change rest→strike is **within ±10% of
  zero** — the drawings' +16% arc growth is **not confirmed** on the bird.
- **Slimming (same bird, same shot, qpYk):** extension ÷ coil width — **mid-tube 0.57,
  base 0.65**. Slimming concentrates at mid-tube; the tip at peak (44 px) equals mid (44 px),
  i.e. the extended tube is uniform. Canon **0.55–0.65** — confirms the art (0.59–0.60) and
  the rig (0.62); slimming was never the problem. Length was.
- **Width under extension:** extended neck ≈ 0.10 × torso wide (mid), vs 0.16–0.20 at rest.

### 3.3 Swallowing + prey handling

- **Handling comes first, and it is long:** muskrat kill — dipping bout with a dip every
  ~6–8 s across ~20–30 s before the swallow toss (t≈110–138 s); juvenile Z7br —
  ~35 s of near-continuous dipping/repositioning of an oversized fish (t≈10–45 s); UR —
  ~50 s of dropping, re-grabbing and shaking a long eel-like fish (t≈5–55 s). Dipping is the
  signature handling move: prey dunked repeatedly, presumably to stun, wet and reorient.
- **Distension factor (peak local width ÷ resting width):** **1.20–1.25 at mid-neck** for a
  head-first aligned deep-bodied fish (oaBww: mid 93.6 px vs 75.6 px resting; upper 1.20).
  A fish held crosswise distends the throat locally to **~1.8×** the adjacent empty segment
  (Z7br within-frame). Canon: **1.2–1
...[truncated 7839 chars]