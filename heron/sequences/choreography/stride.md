**DECIDED (Jimmy, 2026-11-05 14:23): HONEST TURNS.** The return is the canonical two-turn form — walk out, turn, walk back, turn into home (~62 drawings / ~3.60 MB / ~15 s class). The backward-steps option is REJECTED. The turn poses + tick map get fully specced in the stride production brief.

# STRIDE (the stalk / walk) — Choreography Measurement Spec

*Measurement and spec only — no drawing. Playback 12 fps throughout; 1 tick = 1 frame @ 12 fps.
Chart timings are movement-charts.yaml @ 24 fps halved to 12 fps ticks; seconds unchanged.
Every sequence starts and ends on the exact locked home frame (deep coil, bird left of frame,
feet at 15.2% / 20.3% of width, waterline 95.2% of height — home_frame_approval.png, viewed).*

---

## 1. BEAT SHEET

### 1a. The old clip, measured (stride.mjpeg, 120 frames @ 12 fps, 10.0 s, frames viewed as contact strips + numbered leg crops)

| # | Phase | Clip frames | Seconds | Source |
|---|-------|-------------|---------|--------|
| M1 | Both feet planted, slow drift / weight shift — the clip's only quasi-hold; the bird still drifts (no true hold) | f0–8 (9 f) | 0.00–0.75 | MEASURED |
| M2 | Step 1 (swing): lift ~f9, ankle fold rises f12–23, advance with tarsus horizontal f24–36, **plant f37** | f9–37 (29 f) | 0.75–3.08 | MEASURED |
| M3 | Body pass over the plant (both feet down, legs scissor slowly) | f38–59 (22 f) | 3.17–4.92 | MEASURED |
| M4 | Step 2 (swing, other leg): lift f60, fold apex f66–71, advance f72–77, **plant f78** | f60–78 (19 f) | 5.00–6.50 | MEASURED |
| M5 | Body pass | f79–92 (14 f) | 6.58–7.67 | MEASURED |
| M6 | Step 3 (swing): lift f93, fold apex f100–104, advance f105–108, **plant f109** | f93–109 (17 f) | 7.75–9.08 | MEASURED |
| M7 | Body pass, **incomplete — clip cuts mid-pass**, trailing foot still planted, no final stance | f110–119 (10 f) | 9.17–9.92 | MEASURED |

**Clip totals: 3 complete steps, 3 plants (f37, f78, f109), 0 freezes, 0 returns.**
Net translation ≈ 0: slate-body centroid x 476 px (f0) → 489 px (f119), +13 px ≈ +1.3% of width —
a tracked / treadmill walk, not a crossing. It does **not** end where a home frame needs it:
f119 is a wide stride stance mid-pass (feet ≈ 18% / 32% of width), neck up, at ~2.5× home scale.

### 1b. Chart timing for one canonical step (step_cycle, 24 f @ 24 fps = 1.0 s → 12 ticks @ 12 fps)

| Phase | @24 fps | 12 fps ticks | Notes |
|-------|---------|--------------|-------|
| weight_commit | 4 | 2 | weight settles on stance leg, body locks |
| lift_fold | 6 | 3 | fold at the ANKLE, foot ≤ ~7 design units, toes DOWN (−55°) |
| advance | 8 | 4 | folded leg swings low; root_x does NOT move |
| place | 6 | 3 | toe-first, toes spread on weight arrival; ripple fires exactly on plant |
| body_pass | (distributed) | (in next step's commit+fold, 5 ticks) | root advances 14 units; **head world-locked** (neck counter-track), thrust only in a freeze |

Freezes are NOT in the cycle (chart + study §4): the scheduler holds between steps. Relocate
(5 alternating steps, 120 f @ 24 = 5.0 s, NO freezes, 60 ticks @ 12) is the brisk walk-off —
a different behavior; the clip is not it (clip steps take 1.4–2.4 s each with long passes).

### 1c. Proposed sequence beat sheet (see §2/§4 for rationale)

| # | Beat | Ticks @12 | Seconds | Source |
|---|------|-----------|---------|--------|
| P1 | Departure: uncoil from home deep-coil to stalk carriage (neck rises, gaze forward) | 12 | 1.00 | AUTHORED |
| P2 | Stalk freeze (fixation) | 6 | 0.50 | CHART (scheduler hold) |
| P3 | Step A (near leg) — commit 2 / fold 3 / advance 4 / place 3 | 12 | 1.00 | CHART |
| P4 | Freeze (head thrust to next fixation inside this hold) | 12 | 1.00 | CHART (scheduler hold) |
| P5 | Step B (far leg) | 12 | 1.00 | CHART |
| P6 | Freeze (long fixation at far stand) | 12 | 1.00 | CHART (scheduler hold) |
| P7 | Return Step A′ — authored backward step, right profile, gaze kept forward | 12 | 1.00 | AUTHORED |
| P8 | Freeze | 6 | 0.50 | AUTHORED hold |
| P9 | Return Step B′ — authored backward step, lands on home foot positions | 12 | 1.00 | AUTHORED |
| P10 | Re-coil / settle — neck sinks back into the deep coil, ends on exact home frame | 12 | 1.00 | AUTHORED |
| | **Total** | **108** | **9.00** | |

Every plant (P3, P5, P7, P9) fires a ripple on the plant tick; ripples persist, spread and
fade across the following freeze — they never pop. Wander is horizontal only, scale fixed,
whole bird always in frame: 2 steps out ≈ +120–140 px at home scale (feet end ≈ 27–33% of
width), 2 steps back restore the home foot positions exactly.

---

## 2. NATURAL DURATION

- **The clip's bout:** 10.0 s buys only 3 steps, no freeze, no departure, no return, and is
  cut mid-pass — it is a fragment of a bout, not a bout.
- **The animal / chart bout (studies win):** one step = 1.0 s (step_cycle); the stalk's
  rhythm is step … freeze … step, and the freezes are where the hunting happens (study §4).
  A representative chart-faithful bout — 3 steps + 2 freezes of ~2 s — is **≈ 7.0 s**, and in
  the animal it is unbounded above (freezes run to minutes; hold durations may stretch by
  repeating held frames, motion never stretches).
- **PROPOSED new duration: 9.0 s = 108 ticks @ 12 fps**, including departure (P1) and
  return (P7–P10). Shorter than the clip, despite doing more: the clip's steps are
  1.4–2.4 s each against the chart's 1.0 s, and its long body-passes are absorbed into
  the chart's distributed pass.

---

## 3. KEY POSES

| Key | Pose | Source |
|-----|------|--------|
| K0 | **Home** — deep coil, head low, bill down, feet 15.2% / 20.3%, waterline 95.2% | Locked home frame (home_frame_approval.png) |
| K1 | **Stalk carriage** — neck risen from the coil, head forward, gaze horizontal; feet still in home stance | AUTHORED (end of P1) |
| K2 | **Weight commit** — weight on stance leg, body lowered a fraction and locked, stepping foot still planted | CHART weight_commit; clip f6–8, f57–59 |
| K3 | **Lift-fold apex** — ankle (intertarsal) flexed, tarsometatarsus tucked under the shin, **toes point DOWN (−55°)**, foot ≤ ~7 design units up, slim profile | CHART lift_fold; clip shape at f20–22, f68–70, f100–102 (with deviations, §7) |
| K4 | **Advance low** — folded leg forward beneath the shin, root_x stationary | CHART advance; clip f27–30, f72–75, f105–107 |
| K5 | **Place** — foot unfolds late, descends toe-first, toes spread as weight arrives; ripple on this tick | CHART place; clip plants f37, f78, f109 |
| K6 | **Body-pass / head-lock** — body translates over the planted foot while the **head stays world-locked**: neck counter-track = −root advance, head world-x displacement ≤ 1 cell for the whole pass; the head thrusts to its next fixation only during the following freeze | CHART body_pass + study §4/§1 (translational saccade). **The clip fails this key (§7); the chart defines it.** |
| K7 | **Freeze fixation** — complete stillness in stalk carriage, gaze nailed; ripples from the last plant spread and fade underneath | CHART (scheduler hold); **absent from the clip** |
| K8 | **Back-step fold** — K3's fold geometry, leg reaching back, gaze and head kept forward/world-locked | AUTHORED (return, §4) |
| K9 | **Re-coil** — neck sinks back to K0's deep coil; final frame is the exact home frame | AUTHORED (P10), ends on K0 |

Head-lock relationship (the signature of the sequence): in every step, head-x is a
**counter-track** to body-x, not a passenger of it. If a finished frame shows the head
translated by the same amount as the body during a pass, the frame is wrong, however
good the legs look.

---

## 4. DEPARTURE / RETURN — the return problem

The clip never solves it: the bird walks in place and is cut mid-pass at a different
stance, scale and posture from home. The architecture forbids ending anywhere but the
exact home frame. The four options, weighed:

- **(a) Walk out + authored turn + walk back.** Canonical, and the turn chart exists
  (72 f @ 24 = 36 ticks, 3.0 s) — but it does not solve the problem once, it solves it
  **twice**: after walking back facing left, the bird stands at home facing LEFT, and
  the home frame faces right, so a second turn (turn_reverse, another 36 ticks) is
  still owed. Cost: 2 turns (~15 + ~6 unique drawings; the 45°/90°/135° yaw stops are
  shared between the two turns) + a left-profile step set (12 unique) ≈ **+33 unique
  drawings and +72 ticks** over the outbound walk, for a ~15 s sequence. The yaw stops
  do amortize across the whole repertoire — but this sequence alone cannot carry them.
- **(b) Walk out facing right, walk back facing left.** A second left-profile step set
  (~12 unique) — and it still strands the bird facing left at home. Without a turn it
  is a flip, which is forbidden (study §8: drawn progressively or not at all); with a
  turn it collapses into (a). **Rejected as stated.**
- **(c) A few backward steps to return.** Cheapest and facing-preserving — and,
  flagged honestly, **not canonical heron behavior**: no source in the study describes
  a deliberate backward walk back to a stand; herons relocate forward (relocate chart)
  or turn. It is a design fiction, contained to 2 steps.
- **(d) End at a new stand.** Considered and rejected outright: the architecture
  **forbids** it — every sequence ends on the exact home frame.

**RECOMMENDED: (c) — two authored backward steps, facing right throughout**
(beats P7–P9 in §1c), choreographed as:

1. P6 freeze at the far stand (12 t): gaze stays locked on the water ahead — the bird
   never takes its eyes off the hunting ground; this fixation is what the back-steps
   serve, and it motivates them on screen.
2. P7 back-step A′ (12 t, chart phase timings 2/3/4/3): near leg folds at the ankle
   (K8, toes down, ≤ ~7 units), reaches BACK, places toe-first behind; ripple on plant.
   Head world-locked (K6 rule) — the neck counter-track runs in reverse.
3. P8 freeze (6 t): ripples spread/fade; head holds.
4. P9 back-step B′ (12 t): far leg repeats K8 and lands **exactly on the home foot
   positions** (15.2% / 20.3%).
5. P10 re-coil (12 t): neck sinks into the deep coil (the departure's poses in authored
   settle order — no foot plants, no ripples, so no reverse-playback violation), plume
   follow-through settles, final frame = home frame, exact.

Why this one: it is the only option that ends facing right, in the home stance, at a
cost this storage-starved project can pay (§5), and its single fiction is small,
flagged, and readable on screen (a bird easing back off a spot it has spoiled, eyes
still on the water). If Jimmy rules the fiction unacceptable, the fallback is (a) at
the cost stated above — his call, not this spec's.

---

## 5. SIZE ESTIMATE

Unique drawings (holds and freezes repeat a drawing for free; ripples are overlay
state on the static plate, not new bird drawings):

| Item | Unique |
|------|--------|
| Departure uncoil P1 — 12 ticks drawn on 2s | 6 |
| Stalk-carriage hold K1/K7 (all freezes reuse it) | 1 |
| Forward step set P3+P5 — near + far steps, 5 new poses each (weight-commit reuses the hold) | 10 |
| Head-thrust fixation variant (P4 freeze) | 2 |
| Backward step set P7+P9 — near + far, 5 new poses each (K8 geometry) | 10 |
| Re-coil P10 — reuses the 6 departure poses in settle order | 0 |
| **Total unique drawings** | **29** |

Arithmetic: 29 × 58 KB = **1,682 KB ≈ 1.68 MB**
(58 KB = measured cost per unique 1024×600 drawing, JPEG q82 4:2:2.)
For contrast, option (a) prices at ≈ 62 unique ≈ 3.60 MB and ~15 s.

---

## 6. PROVENANCE

- Source: **stride_attempt2.mp4** (per STAGE_B_MANIFEST.md, Stage B clip table).
- Clip as measured: `stageb_clips/stride.mjpeg` — **9,836,559 B, md5
  51d9a6a0f1b03fd8ee2d5fff4e7b4b2e** (re-verified locally: byte count and md5 match
  the manifest; 120 frames, 1024×600, SOI-split extraction).
- Conversion route (per STAGE_B_MANIFEST.md): frames extracted at **12 fps (every 2nd
  frame of the 24 fps source)**, **background-normalized** to the approved plate's
  border median, then PIL/libjpeg **quality=80, subsampling=1** (= 4:2:2),
  optimize=True (`tools/clip_convert_stageb.py`).
- Manifest remark, confirmed on viewing: in stride **the bird / drawn water crosses
  the frame borders** — the bill tip touches x=1023 at f56 and f90, and the drawn
  water band spreads to both side borders from ~f30 on. Both violate this
  architecture (NO CROP ever; static marsh plate with ripples only) and are not
  carried into the proposed sequence.

---

## 7. STUDY vs CLIP — disagreements, and which was taken

| # | Disagreement | Clip (measured) | Study / chart | Taken |
|---|--------------|-----------------|---------------|-------|
| 1 | **Head-lock** | Head surfs with the body: during the f42–56 pass, bill-tip x moves **+70 px** while body centroid moves **+62 px** (≈1:1). Same pattern in every pass. | Head world-locked through the pass (≤1 cell), neck counter-tracks root; thrust only in a freeze (study §1, §4; step_cycle gates) | **STUDY** — K6 is defined by the chart; the clip's head behavior is rejected |
| 2 | **Freeze rhythm** | **Zero freezes.** Leg-region frame-to-frame change never approaches 0 in 120 frames; even f0–8 drifts. Motion is continuous. | Step … freeze … step; freezes live between steps, in the scheduler (study §4) | **STUDY** — proposed beats P2/P4/P6/P8 are true holds |
| 3 | **Step tempo** | Steps take 29 / 19 / 17 frames lift→plant (2.42 / 1.58 / 1.42 s), with body-passes of 22 / 14 / 10+ frames between plants | 1 step = 12 ticks (1.0 s), pass distributed inside the next step | **CHART** — proposed steps are 12 ticks |
| 4 | **Foot lift / fold shape** | Toe clearance at fold apex is roughly at the cap (~30–50 px ≈ 5–8% of frame height vs the ≤ ~7-unit cap, by the study's own 21 units ≈ ¼ frame-height conversion) — **but** the fold itself is exaggerated: tarsus carried fully horizontal ~100–120 px above the water for 8–10 frames, and the toes **curl into a claw/loop** (f20, f68) instead of pointing down; the advancing foot is also carried long and flat (f30–36), a near-"boot" | Fold at the ankle, foot tucks slim under the shin, **toes point DOWN (−55°)**, unfold late (study §4; step_cycle anti-boot gate) | **STUDY** — K3/K4 take the chart's slim downward-toe fold; the clip's curl and flat carry are rejected |
| 5 | **Posture & scale** | Upright bird, neck extended up, head horizontal; bird spans ~95% of frame width; bill exits the right border at peaks | Home bird is a deep coil at ~⅓ frame width, head low; sequences start/end on that frame; NO CROP ever | **ARCHITECTURE / STUDY** — clip used for leg timing only; posture and scale come from the home frame, hence authored departure P1 |
| 6 | **Translation** | ≈ 0 net (+13 px body centroid in 10 s) — a treadmill walk; the clip never actually goes anywhere, and ends mid-pass in a wide stance | Wander is real, horizontal, and must resolve home (§4) | **ARCHITECTURE** — proposed sequence makes 2 real steps out and 2 back |
| 7 | **Water** | A drawn water **band** grows across the bottom ~15% of frame and crosses both borders; ripples merge into a surface | Static plate; ripples only — persist, spread, fade; one ripple per plant | **ARCHITECTURE** |
| 8 | **Agreement (for the record)** | Fold IS at the ankle (not a false knee), plants ARE toe-first, steps DO alternate legs, a ripple DOES accompany each plant (f37, f78, f109) | Same (study §4) | Both — these clip traits are kept in K3/K5 |

---

## 8. CONFIDENCE

**Partial.**

- Clean: frame counts, step count (3), plant frames (f37 / f78 / f109), the absence of
  freezes, net translation, border crossings, and the head-surf measurement — all from
  frames viewed directly (full frames, every-6 and every-3 contact strips, numbered
  leg crops for all 120 frames) or from the cited chart lines.
- Approximate: head/body tracking is mask-based (bill-tip x from the orange-bill mask,
  body centroid from the slate mask, sampled every 2 frames) — good to ±~10 px, which
  does not change any conclusion (the head-lock failure is ~70 px, not marginal). The
  foot-lift conversion to design units uses the study's own 21 units ≈ ¼ frame-height
  equivalence and is ±2 units.
- Authored, by design: the departure (P1), both backward steps (P7/P9), and the
  re-coil (P10) have no clip or chart source — they are the price of the home-frame
  architecture, and §4 flags the backward steps' behavioral fiction explicitly.
