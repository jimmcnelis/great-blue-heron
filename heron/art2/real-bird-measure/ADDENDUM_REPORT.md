# HERON MOTION STUDY — ADDENDUM (2026-11-04)

Measurement pass over the 26 new videos added after the main study (`MOTION_STUDY_REPORT.md`).
Same instruments, same definitions, same validity discipline. Torso = hull-diameter of
tail-tip / chest-front / back-top / belly. Skull = midpoint(eye, back-of-head). Chain =
skull → neck points → neckbase; arc = polyline; station-1 = point at 76% of arc;
chord76 = |skull → station-1|; chord_base = |skull → neckbase|. Near-profile only for
pooled length ratios. Slow-motion or rate-unknown renders contribute ratios/structure
only, never absolute timings. All raw records: `measurements_addendum.json`; annotated
keyframes: `atlas_addendum/` (builder: `work/build_atlas_addendum.py`).

**Method note (differs from the study):** addendum landmark sets carry ONE mid-neck
point, so arc and chord76 on *coiled* frames are floors. On near-straight peak frames
the bias is negligible (57Y peak polyline exceeds the straight chord by 0.4%).

---

## 1. PER-VIDEO VALIDITY TABLE (all 26 new videos)

| Video | Species / content | Rate | Verdict |
|---|---|---|---|
| 57YcyG5VrYI.mp4 | GBH; strikes + closeups (also egret/reed scenes, unused) | Native 29.97 (rip has duplicated frames; local temporal resolution ~15 fps) | **MEASURED** — lunge-plunge peak, crouch coil, deep-coil portrait |
| x65KgB_Vggg.mp4 | GBH stills compilation (nests, juveniles, Ken Burns pans/dissolves) | n/a | **REJECTED** — photo slideshow; no continuous native-rate strike footage despite the title |
| Y1ya7SRPPW4.mp4 | GBH stalking in rain; 2nd bird paler (caution) | Native 29.97 | Qualitative — clean stalk profile; only strike is an oblique lunge (geometry rejected) |
| _0EsuIlSHwM.mp4 | Pale bird — white-morph GBH vs grey heron UNCERTAIN; 640×360, distant | Native 30 | Qualitative only — no numbers pooled (species + resolution) |
| aMPZWB78tKQ.mp4 | GBH upright display stand, then walk with legs hidden by grass | Native 23.98 | Cadence REJECTED (legs hidden); posture note only |
| fb-davesmith-strike.mp4 | GBH at a pond edge, portrait | Native 30 | **MEASURED** — DS1 explosive spear (timing/profile), DS2 slow glean-stab (full geometry) |
| fb-custer-bluegill-log.mp4 | GBH fishing from a log, mostly rear view | Native 29.97 | Timeline measured (handling); geometry rejected (rear view) |
| fb-raney-fellow-fisherman.mp4 | GBH standing/walking in rapids, ~3% of frame width | Native 30 | **REJECTED** — subject too small; no resolvable events |
| fb-weber-duty.mp4 | GBH compilation, ≥3 clips | Native 30 | **MEASURED** — box landing, takeoff + neck-fold timing, prey-dipping; strike closeups timeline-only (body cropped) |
| fb-weber-sashimi.mp4 | GBH tight head/neck crop; strike + catch vs panfish | Rendered 30, slow-motion suspected | Catch CONFIRMED; measurement REJECTED (torso never in frame; slow-mo) |
| fb-samrino-120p-fishing.mp4 | GBH strike + catch, pond | 24 fps render of 120P source — RATE-FLAGGED | Ratios FLOOR ONLY (rear 3/4 view); timings excluded |
| fb-samrino-waterfall-stab.mp4 | GBH lunge-stab at a very large fish; stab-and-abandon | 24 fps render — RATE-FLAGGED | Qualitative (rear 3/4; geometry rejected) |
| fb-samrino-swallow-throat.mp4 | GBH swallowing a small fish | 24 fps render — RATE-FLAGGED | Swallow sequence structure; no distension ratio published (see §2.5) |
| fb-samrino-graceful-awkward.mp4 | GBH frontal mudflat landing | Render 30, rate unverified (~2× suspected) | Landing phases (render-domain) |
| fb-boga-autumn.mp4 | GBH flight through woods → treetop landing | Boga set — RATE-SUSPECT | Validity/structure only |
| fb-boga-2025.mp4 | GBH riverbank flight ending in wings-drooped pose | Boga — RATE-SUSPECT | Validity only; drooped-wings hold noted |
| fb-boga-flyby-landing.mp4 | GBH long flight + branch landing | Boga — RATE-SUSPECT | Landing phases (render-domain) |
| fb-boga-long-flight.mp4 | GBH sustained flight | Boga — RATE-SUSPECT | Wingbeat render-domain only (see §4.1 warning) |
| fb-boga-tree-stretch.mp4 | GBH pine landing + wing-spread hold | Boga — RATE-SUSPECT | **STRETCH measured** (render-domain, §5) |
| fb-boga-stump-sunset.mp4 | GBH misty flight + snag landing at sunset (silhouette) | Boga — RATE-SUSPECT | Landing phases (render-domain) |
| fb-marksmith-landing.mp4 | GBH glide water landing, profile | 29.97, no strong slow-mo evidence | Landing phases (treated real-time, with caution) |
| fb-shapiro-strut.mp4 | GBH walking on lawn, display posture | Native 30 | **MEASURED** — strut cadence |
| fb-pfeifer-pond.mp4 | GBH foraging in shallow pond; brief SWIM ~14–24 s | Native ~29.97 | Validity; swimming note; no strike |
| fb-vanord-underwater-strike.mp4 | GBH plunge past a split-level camera | Native 29.97 | Qualitative leg-entry geometry (no torso ruler) |
| ig-estabrook-night-stalk.mp4 | GBH, IR trail camera, fixed frame | Native 30, real-time CONFIRMED by on-screen clock | Stillness fraction measured; steps too small to count |
| ig-wilson-donriver-stalk.mp4 | Juvenile GBH stalking a shallow creek, near-profile | Native 30 | **MEASURED** — stalk cadence, freezes, head stabilization |

Yield: 4 strikes with usable geometry or timing (DS1, DS2, 57Y, SF-floor), 2 gait
measurements, 5 landing sequences, 1 takeoff, 1 stretch, 1 swallow sequence.
Pooled near-profile GBH strike peaks are now **n = 4** (study 2 + addendum 2).
Still small. Every range below is stated with that n in mind.

---

## 2. TARGET 1 — STRIKES

### 2.1 DS1 — fb-davesmith-strike, event 1 (t ≈ 7.47–7.67 s): the explosive spear

Standing spear at the frame's left edge, near-profile, native 30 fps — but the torso
is cropped out of the portrait frame, so this event yields **timing and release
profile only** (the study's qpYk jab-scene precedent). Head-centre chord per frame
(full series in the JSON): dip frame f15 (192.6 px) → peak f21 (424.4 px).

- **Extension duration = 0.20 s** — inside the study canon [0.10–0.25 s]. CONFIRMED.
- **Release quarter-bins ≈ [2 / 14 / 44 / 40] % (±15).** The first quarter carries
  almost nothing (≈2%) — the study's anti-front-loading finding CONFIRMED a second
  time. But DS1's back half splits 44/40 where the study's 6bc profile was [3/10/78/9]
  — a single Q3 spike. Pooled honestly (n = 2 profiles): the release is **dip →
  slow first half (~15%) → heavy back half (~85%), peak velocity in Q3 but with real
  Q4 weight (25–40%)**. The canon [3/10/78/9] is REVISED to a softer shape:
  **[~3 / ~12 / ~60 / ~25], wide error bars.**
- Withdrawal is ~2–3× slower than extension: 58% of peak chord recovered by +0.40 s,
  then the head stays low for prey handling (small fish held by ~11 s, still being
  repositioned at 19–22 s — window-diff confirms handling, not a second strike).

### 2.2 DS2 — fb-davesmith-strike, event 2 (t ≈ 62.4–66.5 s): the slow glean-stab

The same bird, minutes later, does something different: an already-extended neck
lowers slowly, the bill enters the water at 63.9 s and seizes a small orange-ish
item at the surface; head raised to alert by 66.5 s. **Extension ≈ 1.6 s** — an
order of magnitude slower than the ballistic spear. This is a **separate motor
class (deliberate glean-stab), not a counterexample** to the 0.10–0.25 s canon;
it must never be blended into strike timing. Its peak geometry is valid
(atlas A1/A2):

| frame | chord76/torso | chord_base/torso | arc/torso |
|---|---|---|---|
| f10 alert (61.30 s) | 0.336 | 0.435 | 0.519 |
| **f88 PEAK (63.90 s)** | **0.508** (band 0.44–0.51) | **0.668** | **0.704** |
| f165 alert (66.47 s) | — | 0.394 | — |

Caveats carried openly: the camera is static but the hull-torso is posture-sensitive
(alert frames read 524/583 px vs 454 at peak), so peak chord76 is reported as a
**0.44–0.51 band, central 0.48**, not a point value. Bill ratios are excluded
(bill points down the view axis at contact; tip submerged). Reach factor from the
scene's own alert stance = 0.668/0.435 = **1.54** — this bird never deep-coiled
in this scene, so it is not comparable to the study's 2.6× deep-coil factors.

### 2.3 57Y — 57YcyG5VrYI, plunge (t ≈ 136.5–137.0 s): the lunge, measured properly

Crouch-walk coil (f75) → body pitches at f85 → at f90 the body is horizontal,
legs trailing, neck ramrod-straight, bill at the splash; head submerged f95–105;
wings flare as a brake f110–125; catch confirmed. Near-profile, native 29.97
(the rip duplicates frames, so the duration is a band: **extension ≈ 0.2–0.3 s**
including body pitch; neck-only ~0.15–0.2 s — consistent with canon).

| frame | chord76/torso | chord_base/torso | arc/torso |
|---|---|---|---|
| f75 crouch-walk coil | 0.272 | 0.363 | 0.431 (floor) |
| **f90 PEAK lunge** | **0.662** | **0.870** | **0.874** |

Reach factor 0.870/0.363 = **2.40** — squarely in the study's family (qpYk 2.61,
grey 2.63). The peak EXCEEDS the study's single pooled range — and the study's own
6bc lunge already hinted why: **lunges are a longer class than standing spears.**
The canon now splits explicitly (see §7): standing spears chord_base 0.62–0.71 /
chord76 0.49–0.60; lunges chord_base 0.77–0.87 / chord76 0.60–0.66 (6bc converted
0.60, 57Y direct 0.662).

Bonus from the same video (t = 127.0 s, atlas A6): a tight deep-coil portrait —
torso cropped, but the 2-point chain gives **arc : chord_base ≥ 1.90** (a floor;
the visible S suggests ~2.2–2.5). A coiled neck stores roughly twice its chord in arc.

### 2.4 SF — fb-samrino-120p-fishing (render t ≈ 6.33 s): floor only

Rear 3/4 view (atlas A7 shows the tail toward camera): peak chord76/torso 0.343,
chord_base 0.458 — **floors, not pooled**; the same sequence's tall-stance frame
produces the impossible chord_base/torso 1.369, documenting the oblique failure
mode. Two qualitative facts survive: the strike starts from a **tall, un-coiled
stance** (body pitch substitutes for coil depth — a third strike style beside
spear and plunge), and the catch is confirmed (silvery panfish, withdrawal
from ~7.7 s render).

### 2.5 Supporting strike-adjacent records

- **WF (waterfall-stab):** a second wing-assisted lunge, onto a very large dark
  fish; ~30+ s render of stabbing/handling, then the fish is **abandoned**
  (~40 s) — large-prey give-up is a real behaviour outcome.
- **Sashimi:** strike + panfish catch confirmed at close range; slow-motion
  suspected (extension spans ~12 rendered frames); geometry impossible (crop).
- **Swallow (samrino-swallow-throat, rate-flagged):** the sequence structure is
  the value — crosswise repositioning for tens of seconds (render), head-first
  alignment ~58–70 s, throat entry with max gape at 72 s (atlas A8), bolus transit
  down the neck ~71–79 s, slim by 80 s, gape/head-shake after, drink at 96–98 s.
  For this SMALL fish (~0.25 torso) the visible "bulge" is mostly the fish's own
  width at the throat — **no distension ratio is published**; the study's grey-heron
  1.31/1.53 values (larger prey) remain the only distension canon.
- **Handling durations (new canon material):** bluegill catch→swallow ≈ **45 s**
  (Custer, native rate); repeated prey-dipping before swallowing (Weber-duty,
  40–47 s); big-fish stab-and-abandon ~30+ s render (WF).

### 2.6 Canon verdicts from Target 1

- Peak **chord76 [0.49–0.60] HOLDS for standing spears** (DS2 0.44–0.51 band at the
  low edge — a short-reach glean, not a full-commit spear). Lunges extend the
  pooled envelope to 0.66 — a class refinement, not a break.
- **[3/10/78/9] does NOT hold as written** — revised to [~3/~12/~60/~25] (n = 2).
- Extension 0.10–0.25 s CONFIRMED for ballistic strikes; a slow-stab class (~1.6 s)
  is now documented separately.
- Arc-at-peak 0.70–0.75: DS2 confirms (0.704); 57Y's 0.874 **weakens** strict
  conservation — at a ramrod lunge peak arc ≈ chord_base by geometry, so pooled
  arc-at-peak is now 0.70–0.87. Conservation survives as a standing-posture band.

---

## 3. TARGET 2 — GAIT

### 3.1 Stalk (ig-wilson-donriver-stalk, juvenile, native 30 fps)

Walking bout 118–134 s: **≈3 steps in 15.6 s ≈ 0.2 steps/s (band 0.15–0.30)**,
freezes of **3–6 s** between steps, swing duration **~1–2 s**. Step length is a
coarse estimate, **0.3–0.5 torso** (at the placement instant the feet are only
0.09 torso apart, atlas A9). The decisive finding: **the head does not bob.**
At 0.4 s sampling the head stays fixed in space while the body steps underneath —
the neck absorbs the gait. Stalking = frozen head, moving body, long stillness.

### 3.2 Stillness (ig-estabrook-night-stalk)

Fixed IR trail camera; the on-screen clock (22:48:44 → 22:49:43) proves real-time
rate. Frame-diff **still-fraction = 0.73** across the clip — a quantitative
"stillness is the default" datapoint to set beside the stalk's 3–6 s freezes.
Bird too small for step counting; no cadence claimed.

### 3.3 Strut (fb-shapiro-strut, native 30 fps)

Purposeful lawn walk toward/past a fixed camera: **cadence ≈ 1.6 ± 0.3 steps/s** —
roughly **8× the stalk rate**. Neck held high and vertical, plumes erected
(display posture), and the head shows a **small step-coupled bob** — the exact
opposite coupling from the stalk. Gait is therefore (at least) two modes with
different head rules, not one walk cycle at two speeds.

(aMPZ strut: cadence rejected — legs hidden by grass; upright display posture
only. _0Esu and Y1ya stalks: qualitative support, no pooled numbers.)

---

## 4. TARGET 3 — FLIGHT & LANDING

### 4.1 Wingbeat — UNRESOLVED, with a warning (fb-boga-long-flight)

Dense strip reading (every 2nd frame): upstroke peaks at render 8.87 / 11.04 /
13.41 s, downstroke bottoms at 9.57 / 12.21 s → **render-domain cycle 2.2–2.4 s
(0.42–0.45 Hz)**. A great blue heron cannot sustain flight at 0.44 Hz. The clip
is a high-frame-rate source conformed slow by an unknown factor (~5–6× would give
the expected ~2.5 Hz). **Do not bake 0.44 Hz. Absolute wingbeat frequency remains
an open measurement** — what is needed is one native-rate flight clip with a
verified clock (the Estabrook clock trick) or known-fps metadata. Flap-glide
structure is visible in-render (level-wing glides between bouts), and the neck is
in the folded cruise S throughout. ALL Boga clips inherit this rate suspicion.

### 4.2 Takeoff and the neck fold (fb-weber-duty, native 30 fps) — NEW

A complete perch takeoff, frame-resolved (atlas A11/A12):

- Crouch deepens 19.4–19.9 s; wings open on the perch 20.1–20.3 s;
  first downstroke 20.47 s; **liftoff 20.60 s with the neck EXTENDED forward**,
  near-straight — the bird takes off spear-first, not folded.
- Retraction begins ~20.87 s; **fold essentially complete by +0.4–0.5 s**
  (by 21.1 s), cruise S established; legs come down again 21.5–21.9 s as the
  short hop descends (the clip then cuts to a different bird's landing).
- Same bird, earlier: **defecation at ~15 s, ≈5.5 s before liftoff** (n = 1,
  but a classic pre-flight behaviour worth a behaviour-chart note).

So the takeoff→cruise neck transition is fast and late: extend for the jump,
fold within half a second of leaving the perch.

### 4.3 Landing phase structure (5 sequences)

Consistent six-phase structure everywhere:

1. **Approach** — legs trailing; neck in cruise fold, EXCEPT low/short
   approaches where it rides in a **shallower, longer S** (graceful-awkward).
2. **Legs down** — fully extended well before contact (marksmith: down by 24 s,
   touchdown 29.5 s; flyby: extending from ~98 s, contact ~103 s).
3. **Flare** — wings cupped, body pitches up.
4. **Touchdown.**
5. **Balance phase — LONG.** Wings stay spread with **asymmetric** corrections
   and steps: graceful-awkward ≈9–10 s render of stumbling recovery; marksmith
   ~10 s of wing-assisted running on the water surface; stump-sunset 35–39 s
   render; weber box landing wings-up ~2.5 s on a solid perch (shortest — firm
   footing).
6. **Fold** — graceful-awkward fully folded by ~32 s render; marksmith still
   holding a partial "V" mantle at clip end (50 s) — folds can lag minutes.

The balance phase is a first-class behaviour, not a transition: budget it
several seconds, asymmetric, stepped, surface-dependent.

---

## 5. TARGET 4 — STRETCH (fb-boga-tree-stretch) — gap FILLED, with a correction

What the footage actually shows is **not a neck stretch**. After landing in a
pine (~16–17.5 s render) and settling, the bird opens **both wings together,
symmetrically**, to full horizontal span with primaries fanned, and **holds
≈3.0 s** (19.0–22.0 s render; Boga rate flag applies), then folds over ~1.2 s.
Neck stays up throughout; **no neck-extension component**; no stepping (atlas A10).

Distinguish from the landing-balance spread (§4.3 phase 5): stretch = symmetric
+ static + post-settle; balance = asymmetric + corrective + stepped. The same
family includes the wings-drooped hold that ends fb-boga-2025. The study's
"stretch" gap is therefore filled as a **wing behaviour**: post-landing bilateral
wing-spread hold.

---

## 6. TARGET 5 — REMAINING GAPS

- **Preen:** nothing measurable found in the new set. Gap stands.
- **GBH leg segments:** vanord gives qualitative structure only — on the plunge
  the legs enter **near-vertical (within ~10–15°), staggered in depth** (one foot
  deeper), feet ~15% of frame width apart; the bird then simply walks through
  the frame. No torso ruler exists in the underwater frame, so segment ratios
  remain unmeasured. Gap stands, narrowed.
- **Empty (missed) withdrawal:** still no clean specimen — every measured
  withdrawal carried prey (DS1, DS2, SF) or was cropped (sashimi). Gap stands.
- **Neck slimming (study canon 0.55–0.65):** NOT tested by this addendum — no
  width series was taken on strike frames. Canon stands untested, flagged.
- **Wingbeat frequency:** unresolved (§4.1) — needs a rate-verified flight clip.

---

## 7. UPDATED CANON TABLE — study → addendum

| Quantity | Study canon | Addendum value | Verdict |
|---|---|---|---|
| Peak chord76, standing spear | 0.49–0.60 | 0.49–0.60 (DS2 band 0.44–0.51 is a short-reach glean) | **CONFIRMED** |
| Peak chord76, lunge class | (inside pooled range; 6bc ≈0.60 converted) | **0.60–0.66** (57Y direct 0.662) | **EXTENDED — class split now explicit** |
| Peak chord_base, standing | 0.62–0.77 (pooled) | **0.62–0.71** standing (DS2 0.668) | **REFINED** (0.77 was the lunge) |
| Peak chord_base, lunge | — | **0.77–0.87** (6bc 0.77; 57Y 0.870) | **NEW SUB-RANGE** |
| Release profile (quarter bins) | dip → [3/10/78/9] | dip → **[~3/~12/~60/~25]**, ±wide, n = 2 | **REVISED** — slow start confirmed twice; Q3 spike softened, Q4 carries 25–40% |
| Extension duration, ballistic | 0.10–0.25 s | 0.10–0.25 s (DS1 0.20; 57Y 0.2–0.3 band) | **CONFIRMED** |
| Extension, slow glean-stab | — | **≈1.6 s** (DS2) | **NEW CLASS** — keep out of strike timing |
| Neck arc at peak | conserved 0.70–0.75 | standing 0.70 (DS2 0.704); lunge peak 0.87 → pooled **0.70–0.87** | **WEAKENED** — conservation holds for standing postures; at ramrod peaks arc ≈ chord_base |
| Coil chord_base | deep ≈0.27 | deep ≈0.27 stands; mid-coils measured 0.363 (crouch-walk), 0.435 (alert); coil arc:chord ≥1.90 | **CONFIRMED + filled in** |
| Reach factor (peak/coil chord_base) | ~2.6 | 2.40 (57Y); 1.54 from a non-deep stance (DS2) | **CONFIRMED** family |
| Neck slimming at extension | 0.55–0.65 | not tested | **STANDS, UNTESTED** |
| Stalk gait | — | **0.15–0.30 steps/s; freezes 3–6 s; swing 1–2 s; step ~0.3–0.5 torso; HEAD STABILIZED (no bob)** | **NEW** |
| Strut/walk gait | — | **~1.6 ± 0.3 steps/s; small head-bob coupling; neck high, plumes up** | **NEW** |
| Stillness | (qualitative law) | night-stalk still-fraction **0.73** | **NEW** (quantified) |
| Landing | — | **6 phases; balance phase is LONG (seconds), asymmetric, stepped; legs down well before contact; fold may lag** | **NEW** |
| Takeoff neck | — | **extended at liftoff; fold complete by +0.4–0.5 s**; defecation ~5.5 s prior (n = 1) | **NEW** |
| Wingbeat frequency | — | **UNRESOLVED** — render 0.42–0.45 Hz is rate-corrupted; ~2.5 Hz expected if ~5–6× slow-mo | **OPEN — do not bake the render number** |
| Stretch | gap | **post-landing bilateral wing-spread hold, symmetric, ~3 s render; no neck component** | **FILLED (as a wing behaviour)** |
| Prey handling | (notes) | bluegill catch→swallow **≈45 s**; prey-dipping pre-swallow; big-fish stab-and-abandon; small-fish bolus transit ~8 s render | **NEW** |
| Swallow distension | grey 1.31 / 1.53 | GBH small-fish: no ratio (fish's own width dominates the frame) | **STANDS** (grey values remain the canon) |
| Preen / leg segments / empty withdrawal | gaps | still gaps (leg entry now qualitative: near-vertical, staggered) | **STAND** |

Reference points unchanged: approved art strike chord76 = 0.512 sits inside the
standing-spear range; rig v2.4's 0.247 remains ~45–50% of the real standing
peak and ~37% of the lunge peak. The addendum moves no goalposts in the rig's
favour — it sharpens which real number the rig should be compared against
(standing spear 0.49–0.60 for the standard strike; 0.60–0.66 only if a lunge
class is ever charted).

---

## 8. FILES

- `measurements_addendum.json` — 13 landmark sets, 3 strike timelines, gait /
  flight / landing / handling records, swallow + stretch + underwater records.
- `atlas_addendum/` — 12 annotated keyframes (A1–A12), every one viewed before
  filing. A7 and A8 carry their caveats in their captions.
- `work/` — strips, sheets, motion CSVs, `strip.py`, `build_atlas_addendum.py`.
- Method scripts from the main study were reused unchanged (`landmarks.py`,
  `window_motion.py`, `extract_scan.py`, `scan_motion.py` — the last crashes on
  x65KgB_Vggg.mp4, which turned out to be a slideshow anyway).
