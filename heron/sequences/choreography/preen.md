# PREEN — choreography spec (measurement only, no drawings)

Sequence: **preen** · Playback: **12 fps always** (1 tick = 1 frame = 1/12 s)
Architecture: starts AND ends on the exact locked home frame (colorized deep-coil,
bird left of frame, whole bird in frame, feet at 15.2% / 20.3% of width, waterline
95.2% of height — `gate1-strike/fresh/home_frame_approval.png`). Feet stay planted
through the base sequence; foot rings constant; no ripples (no foot moves).
Timing truth: `heron-movement-study.md` §10 + `movement-charts.yaml` chart `preen`
(240 frames @ 24 fps = 10.0 s). Chart frames halve to 12 fps ticks; seconds unchanged.
Where clip and studies disagree, **studies win** (flagged in §7).

Method: `.mjpeg` split on SOI/EOI → 120 frames (f0–f119, 1024×600) in
`/tmp/choreo_preen/`; contact strips every frame viewed; per-frame bird-region
mean-|Δ| computed as a motion diagnostic; full-res head crops inspected at
f24 / f48 / f72 / f84 for gape, wing state, and tract position.

---

## 1. BEAT SHEET

### 1a. MEASURED — what the clip actually does (12 fps frames, f = frame, s = f/12)

| # | Clip span | s span | What happens (viewed) | Motion Δ |
|---|---|---|---|---|
| M1 | f0–f7 (8 fr) | 0.00–0.67 | Upright alert stand, neck in extended S, bill forward. Near-still — the clip's only quasi-hold. **Not the home coil.** | 0.09–0.53 |
| M2 | f8–f19 (12 fr) | 0.67–1.67 | Head pitches down and turns back toward the chest; neck folds progressively, no 3/4 stop, no anticipation dip separable from the descent. | 1.5→10.3 |
| M3 | f20–f31 (12 fr) | 1.67–2.67 | Deepest chest tuck: head inverted under the neck curve, bill horizontal, pointing back into the chest-plume cascade. Continuous small rocking — no discrete nibble beats, no pause. | 5.2–10.3 |
| M4 | f32–f65 (34 fr) | 2.67–5.50 | Bill works slowly UP the plume cascade from chest to shoulder; head ends high, turned back over the shoulder, bill in the neck/shoulder feathers (clearest f40–f60). One continuous creep with small bobs — no beats, no holds. | 6.0–12.3 |
| M5 | f66–f69 (4 fr) | 5.50–5.83 | Reposition: head swings down/back from shoulder toward the rear flank. | 10.1–11.7 |
| M6 | f70–f85 (16 fr) | 5.83–7.17 | Head buried at the rear flank / folded-wing trailing feathers, bill into the flank. Wing stays **folded** the whole time; head works **over**, never under, the wing. | 9.8–12.6 |
| M7 | f86–f95 (10 fr) | 7.17–8.00 | Withdrawal: head pulls out (peak motion of the clip, Δ 13.5–16.2 at f84–f87) and the neck re-extends upward. Unidirectional — **not a shake**. | 6.7–16.2 |
| M8 | f96–f119 (24 fr) | 8.00–10.00 | Upright stand ≈ f0 pose, slow drift/settle. Δ decays 6.7 → 1.15 but **never reaches 0** — no true hold, and the end pose is upright, **not the home coil**. | 1.2–9.6 |

Measured totals: motion occupies f8–f95 ≈ **7.33 s** of the 10.0 s; bookends are
upright quasi-holds (0.67 s + 2.0 s). Bout boundaries are ±2 frames — the clip's
motion is continuous, with no holds or events to anchor sharper cuts.
Feet: **both planted in all 120 frames** (verified across every strip); rings
constant; no foot lift, no ripple event anywhere in the clip.

### 1b. CHART — `preen` in movement-charts.yaml, converted to 12 fps ticks

| Phase | @24 fr | 12 fps ticks | s | Keys / notes (chart) |
|---|---|---|---|---|
| reach_shoulder | 24 | 12 | 1.00 | head_yaw 120, neck_coil 0.95, head_pitch 18; through the 3/4 head stop; anticipation dip in first 4 fr @24 (= 2 ticks) |
| nibble_beat_1 | 8 | 4 | 0.33 | 2–3 small bill strokes, head_pitch ±3 |
| hold_pose | 16 | 8 | 0.67 | **true hold** |
| nibble_beat_2 | 8 | 4 | 0.33 | same rhythm, further along the tract |
| draw_through | 20 | 10 | 0.83 | one feather drawn through bill; beak_open 0.4 tracks it — the re-zip stroke |
| reposition | 18 | 9 | 0.75 | head_yaw 60, head_pitch 24 → chest (powder-down tract) |
| nibble_chest | 16 | 8 | 0.67 | 2 beats of 8 fr @24 on the chest fringe |
| wing_half_open | 18 | 9 | 0.75 | wing_amt 0.45; head goes UNDER the leading edge |
| nibble_wing | 16 | 8 | 0.67 | 2 beats under the wing |
| shake | 12 | 6 | 0.50 | whole-body shake; plume follow-through ≥ 8 fr @24 (= ≥ 4 ticks) past it |
| settle | 24 | 12 | 1.00 | head_yaw 0, head_pitch 0, neck_coil **0.85** (idle base) |
| tail_hold | 60 | 30 | 2.50 | **true hold** — bout ends in stillness |
| **Chart total** | **240** | **120** | **10.00** | ends on idle base pose (coil 0.85), NOT home |

### 1c. AUTHORED — proposed sequence (see §2, §4 for the authored parts)

Rows in order: **D** = authored departure, chart phases verbatim, **R** = authored
return, closing hold re-based onto the home frame.

| # | Phase | Ticks | s | Source |
|---|---|---|---|---|
| A1 | departure_uncoil | 6 | 0.50 | AUTHORED (§4) |
| A2 | reach_shoulder | 12 | 1.00 | CHART |
| A3 | nibble_beat_1 | 4 | 0.33 | CHART |
| A4 | hold_pose | 8 | 0.67 | CHART (hold) |
| A5 | nibble_beat_2 | 4 | 0.33 | CHART |
| A6 | draw_through | 10 | 0.83 | CHART |
| A7 | reposition | 9 | 0.75 | CHART |
| A8 | nibble_chest | 8 | 0.67 | CHART |
| A9 | wing_half_open | 9 | 0.75 | CHART |
| A10 | nibble_wing | 8 | 0.67 | CHART |
| A11 | shake | 6 | 0.50 | CHART (follow-through ≥ 4 ticks lands inside A12) |
| A12 | settle | 12 | 1.00 | CHART (ends coil 0.85) |
| A13 | recoil_home | 6 | 0.50 | AUTHORED (§4) |
| A14 | closing_home_hold | 30 | 2.50 | CHART tail_hold, re-based: held drawing = exact home frame |
| | **Total** | **132** | **11.00** | |

---

## 2. DURATIONS

- **Clip duration:** 120 frames @ 12 fps = **10.0 s** (action inside it: ≈ 7.33 s, §1a).
- **Chart (natural) duration:** 240 fr @ 24 fps = **10.0 s** = 120 ticks @ 12 fps.
  This is the sequence's natural duration — clip and chart agree on the total
  by coincidence only; their internal structures do not agree at all (§7).
- **Proposed duration: 11.0 s = 132 ticks @ 12 fps.**
  = chart 120 ticks + 6 authored departure ticks + 6 authored re-coil ticks.
- ⚠ **Flag — the re-coil is authored, not charted.** The chart's settle ends at
  `neck_coil 0.85` (idle_hunt base pose) and its tail_hold holds *that* pose.
  Our architecture forbids ending there: the sequence must end on the deep home
  coil. A13 (settle 0.85 → deep home coil) and the re-basing of the tail hold
  onto the home frame (A14) are authored in §4 to close that gap. Nothing else
  in the chart was retimed.

---

## 3. KEY POSES

| Key | Pose | Source |
|---|---|---|
| K0 | **HOME** — deep coil, head low/down, bill down-forward, feet 15.2% / 20.3%, waterline 95.2% | Locked home frame (`home_frame_approval.png`); sequence frame 0 and final frame |
| K1 | Departure mid-uncoil — neck half-raised from deep coil toward hunt coil, head beginning its turn | AUTHORED (§4); no clip/chart source |
| K2 | 3/4 head stop en route to shoulder | CHART reach_shoulder (head_turn machinery); clip analogue ≈ f14 (head half-turned, bill angling down — but clip is heading for the chest, not the shoulder) |
| K3 | Full shoulder reach — head_yaw 120, head_pitch 18, bill at the shoulder tract | CHART reach_shoulder endpoint; clip analogue ≈ f48 (head back over shoulder, bill in plume cascade — reached in the clip only after the chest bout, order reversed, §7) |
| K4 | Nibble beat pose (shoulder) — bill closed on a feather, head_pitch at stroke extreme | CHART nibble_beat_1 / _2; no discrete clip source (clip motion is continuous) |
| K5 | Hold pose — K4 frozen | CHART hold_pose (held drawing) |
| K6 | Draw-through mid — feather along the bill, **beak_open 0.4**, gape visibly tracking the feather | CHART draw_through; **no clip source — absent from the clip** (bill closed in every inspected frame) |
| K7 | Chest / powder-down pose — head at the chest fringe, head_yaw 60, head_pitch 24 | CHART reposition + nibble_chest; clip analogue f24–f30 (deepest tuck, bill horizontal into the plumes) |
| K8 | **OPTIONAL — powder-comb** — near FOOT raised to the chest, folded at the ankle, pectinate (fringed) middle claw out, combing the powder down while the head lowers to meet it | CHART variant `preen_powder_comb`; study §10 (species-signature beat). **Optional replacement for A8 nibble_chest**, same 8 ticks. No clip source (clip feet never lift). Water: this is the sequence's only foot move — the plant at the end of the beat gets **one ripple**; rings otherwise constant |
| K9 | Wing half-open — wing_amt 0.45, head UNDER the leading edge | CHART wing_half_open + nibble_wing; clip f70–f85 is head-at-flank with the wing **closed** — geography analogue only, NOT this pose |
| K10 | Shake peak — whole body at oscillation extreme, plumes/chest fringe displaced | CHART shake; **no clip source — no shake exists in the clip** |
| K11 | Settle at hunt coil — head_yaw 0, head_pitch 0, neck_coil 0.85, plume follow-through decaying | CHART settle; clip analogue ≈ f96 (upright re-extended stand) |
| K12 | Re-coil mid — neck sinking from 0.85 back into the deep home coil, head lowering | AUTHORED (§4); no clip/chart source |
| K0′ | **HOME** (= K0, exact same drawing) | Closing hold A14 |

Identity on every key (locked): white head, black brow into exactly two long
black plumes, yellow ringed eye, dagger bill, slate body, ONE black shoulder
patch, rusty bend-of-wing + thighs, shaggy chest-plume cascade, long scaly legs
with pectinate middle claw. No crop ever.

---

## 4. DEPARTURE / RETURN (authored parts marked)

**DEPARTURE — home → first reach (A1 + head of A2, AUTHORED).**
The chart's reach_shoulder starts from the idle base (coil 0.85); the home
frame is a **deeper** coil with the head held low. Authored departure:
6 ticks in which the neck uncoils from deep home toward hunt depth and the
head lifts and begins to turn, arriving at the chart's reach start state
(coil ≈ 0.95 trajectory, head_yaw 0). The chart's own anticipation dip
(first 2 ticks of A2) then plays as written, and the reach proper turns
through the 3/4 stop (K2) to the shoulder (K3). Feet planted throughout;
no ripple. Total home→shoulder: 18 ticks (1.50 s).

**RETURN — closing settle → exact home frame (A13 + A14, AUTHORED).**
Chart settle (A12) ends at coil 0.85, head forward — the idle base, not home.
Authored re-coil: 6 ticks (A13) in which the neck sinks the remaining depth
into the deep home coil and the head lowers to the home pitch, landing
**exactly** on the home drawing (K0). A14 then holds that exact home frame
for 30 ticks (2.50 s) — the chart's tail_hold duration, re-based from the
idle base pose onto home, so the bout still ends in stillness and the next
sequence can start from the identical frame. Feet planted; rings constant;
no ripple.

---

## 5. SIZE ESTIMATE

Counting rule: 1 unique drawing per tick of motion; a true hold costs
**1** drawing no matter how many ticks it spans.

| Block | Ticks | Unique drawings |
|---|---|---|
| Motion: A1 6 + A2 12 + A3 4 + A5 4 + A6 10 + A7 9 + A8 8 + A9 9 + A10 8 + A11 6 + A12 12 + A13 6 | 94 | 94 |
| hold_pose (A4) | 8 | 1 |
| closing_home_hold (A14) — the home drawing itself | 30 | 1 |
| **Total** | **132** | **96** |

Arithmetic: 96 × 58 KB = **5,568 KB ≈ 5.57 MB**.
Of the 96, the home drawing (K0/K0′) already exists and is shared by every
sequence, so **new drawings = 95 → 95 × 58 KB = 5,510 KB ≈ 5.51 MB** incremental.
Shake follow-through (≥ 4 ticks) is inside A12's 12 motion ticks — no extra cost.
Powder-comb variant (K8 replacing A8): same 8 ticks, same count — **size unchanged**.

---

## 6. PROVENANCE

- Source: **preen_attempt1.mp4** (per `STAGE_B_MANIFEST.md` clip table).
- Clip: `stageb_clips/preen.mjpeg` — **6,435,722 B**, **md5 d63260bf75a786541eca0a88a9b13205**
  (re-verified by md5sum in this pass; 120 frames @ 12 fps, 1024×600).
- Conversion route (per STAGE_B_MANIFEST.md): 12 fps extraction from the 24 fps
  source (every 2nd frame), background-normalized (per-clip border median pulled
  toward the approved plate's (247, 232, 210), deviation damped ×0.35), then
  PIL/libjpeg **q80, subsampling=1** (4:2:2 — the only layout the ESP32-P4 HW
  decoder accepts), optimize=True. Manifest verification: bird is **bit-identical
  after normalization on preen frames 0/60/119** (max |Δ| = 0.000 on all pixels
  ≥ 45 RGB units from background).
- Note: the task brief's planning figure of ~58 KB/drawing at "q82" vs the
  manifest's q80 route — the clip's own measured average is 53,631 B/frame;
  §5 uses the brief's mandated 58 KB planning figure throughout.

---

## 7. STUDY vs CLIP — disagreements, and which was taken

Studies win in every row (per brief). Clip used for bout geography only.

| # | Disagreement | Taken |
|---|---|---|
| 1 | **Structure:** chart = bout-and-pause (4- and 8-tick nibble beats separated by true holds; gate: ≥ 2 holds ≥ 8 fr @24). Clip = one continuous slow sweep — per-frame Δ stays 5–12 for f8–f95 with **zero true holds inside the bout** (only quasi-holds at the upright bookends). | **CHART.** Beat/hold structure authored from the chart; clip supplies only where the head goes, not when it pauses. |
| 2 | **Bout order:** chart goes shoulder → chest → wing. Clip goes chest (f20–f31) → shoulder (f32–f65) → flank (f70–f85). | **CHART order.** |
| 3 | **Draw-through missing:** chart has a 10-tick draw_through with beak_open 0.4 tracking a feather through the bill. Clip: bill **closed in every full-res frame inspected** (f24 / f48 / f72 / f84); no feather is ever isolated or drawn through. | **CHART.** K6 authored from the chart; flagged as having no clip evidence. |
| 4 | **Shake missing:** chart ends the bout with a 6-tick whole-body shake + ≥ 4 ticks plume follow-through. Clip has **no shake anywhere** — its peak motion (f84–f90) is the unidirectional head withdrawal. | **CHART.** K10 authored from the chart. |
| 5 | **Wing:** chart half-opens the wing (wing_amt 0.45) with the head UNDER its leading edge. Clip wing never opens; head works over the closed flank feathers. | **CHART.** K9 is not the clip's flank pose. |
| 6 | **Start/end pose:** clip starts and ends upright (extended S, bill forward, ≈ same pose f0 ≈ f96–f119 — it nearly loops on itself). Chart ends at idle base (coil 0.85). Architecture requires the deep home coil at both ends. | **ARCHITECTURE over both.** Departure and re-coil authored (§4); chart tail_hold re-based onto home. |
| 7 | **Framing/identity:** clip bird sits mid-frame with feet together near frame centre and reads darker/more saturated than the locked identity; home bird is left-of-frame in deep coil. Clip is a timing/geography reference only — never a framing or identity source. | **HOME FRAME / locked identity.** |
| 8 | **Agreements (for the record):** total duration 10.0 s both; three-bout geography (chest, shoulder, flank/wing) both; feet planted throughout both (base sequence); no foot lift in either base version — powder-comb exists only as the chart variant (K8, optional). | Both. |

---

## 8. CONFIDENCE

**PARTIAL.** The clip measure is clean where the clip has signal: bout geography
(chest → shoulder → flank), bout spans, feet-planted, wing-closed, bill-closed,
and the absence of holds/shake/draw-through are all directly viewed and
Δ-corroborated. But the deliverable's *internal* structure — nibble beats,
hold_pose, draw-through, shake, wing half-open, departure, re-coil — has no
clip evidence at all and is authored from the chart onto the clip's geography.
That split is the reason: measured shell, authored beats.
