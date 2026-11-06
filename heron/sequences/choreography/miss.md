# REPLACED by LISTENING (Jimmy, 2026-11-05 23:30) — retained for the record; do not build.

# MISS — Choreography Spec (Sequence: the strike that catches nothing, Sequence 1's twin)

*Measurement + spec only — no drawing. Playback 12 fps throughout. Every sequence
starts AND ends on the exact locked home frame (deep coil, bird left of frame,
feet at 15.2% / 20.3% of width, waterline at 95.2% of height —
`gate1-strike/fresh/home_frame_approval.png`, viewed for this spec).*

*Method: the 120-frame .mjpeg was split on JPEG SOI markers into
`/tmp/choreo_miss/f000.jpg`–`f119.jpg` (1024×600). Contact strips viewed at
stride 6 (0.5 s) and stride 3 (0.25 s) across the whole clip; stride 1
(every frame) across f15–32 (descent), f66–96 (sweep + withdrawal) and
f94–119 (settle). A per-frame mean-abs-difference pass (vs f0 and vs previous
frame) corroborated every phase boundary below. Bill tip was ground-located
on f20, f26, f29 (see §7). Chart frame counts are the YAML's 24 fps budgets
halved to 12 fps ticks; seconds are unchanged by the conversion.*

---

## 1. BEAT SHEET

Two truths are tabulated side by side: what the old generated clip actually
does (MEASURED), and the `strike_miss` chart timing that governs the rebuild
(CHART). The proposed rebuild column is in §2. Where the clip and the chart
conflict, the chart wins (§7).

### 1a. The old clip, as measured (MEASURED)

| # | Phase (clip) | Clip frames | Seconds | What is actually on screen |
|---|---|---|---|---|
| M1 | Upright stand / fixation | f0–16 (17 f) | 0.00–1.42 | Bird stands TALL, neck in an upright S, bill horizontal. Near-still (frame-to-frame diff ≈0.03–0.12). This is an alert stand, **not** a coil: no coil-deepen is visible, the bird never loads. |
| M2 | Descent (the clip's only "strike") | f17–29 (13 f) | 1.42–2.50 | Head arcs slowly down, neck folds, bill tip reaches the water at ≈f28–29; first contact ripple f29–30. Slow and *decelerating* (see §7) — no smear frame, bill reads closed the whole way down. |
| M3 | Head-down dwell at the water | f30–70 (41 f) | 2.50–5.92 | Bill tip held in/at the water, head down, only micro-adjustments (frame-to-frame diff 0.11–0.59, vs 3–7 during real motion). Concentric ripples at bill and both feet. A 3.4 s probe/hold the chart does not contain. |
| M4 | Forward sweep / second lunge | f71–82 (12 f) | 5.92–6.92 | From the dwell, the neck stretches forward low and the bill skims through the surface, throwing the clip's only real splash (peak f78–80, wake trailing right), bill clear of the water by ≈f81–82. **No such phase exists in the chart.** |
| M5 | Withdrawal | f83–93 (11 f) | 6.92–7.83 | Head rises smoothly and monotonically, neck re-coils toward the upright S, drips fall from the empty bill (visible f84–96). **No head-shake oscillation is present** — the rise never reverses or sways side to side. Slight beak opening ≈f93–95. |
| M6 | Upright settle | f94–119 (26 f) | 7.83–10.00 | Settles into the same upright alert stand it started from; ripples spread and fade. Final frame f119 is the upright stand, **not** the deep-coil home frame (f119 still differs substantially from f0 in the diff pass, and neither resembles home). |

Clip total: 120 frames, 10.0 s — of which ≈5.9 s (M1+M3+M6 ≈ 84 frames) is
near-still padding and double-dip structure around a strike that, in the
chart, takes 2.7 s.

Legs in the clip: the feet never step, lift, or re-plant in any phase
(stride-1 strips f15–96, stride-3 full clip) — the stance is static
throughout; only the ripples around the planted feet evolve.

### 1b. The chart, converted to 12 fps (CHART — governs the rebuild)

Source: `movement-charts.yaml`, chart `strike_miss` (64 frames @ 24 fps =
2.7 s), itself the `strike` chart with `fish: none`; study
`heron-movement-study.md` §3 (strike) and §6 (handling — a miss skips
handling entirely and returns to the loaded hold).

| # | Phase | @24 fps | @12 fps ticks | Seconds | Mark |
|---|---|---|---|---|---|
| C1 | coil_deepen | 12 | 6 | 0.50 | CHART |
| C2 | loaded_hold (hold: true) | 12 | 6 | 0.50 | CHART |
| C3 | release — beak-tip spacing 25% / 60% / 100% cumulative (YAML strike chart: 25/35/40 per-frame), beak opens on the final approach frames (chart frames 3–4 @24), smear on chart frame 3, splash event at contact | 4 | 2 | 0.17 | CHART |
| C4 | grab_dwell — bill closes on **nothing** (`fish: none`); the ONLY pre-withdrawal difference from a catch | 2 | 1 | 0.08 | CHART |
| C5 | withdrawal — empty bill, decelerating rise, drips event spans the phase | 12 | 6 | 0.50 | CHART |
| C6 | head_shake — 3 oscillations, `neck_sway` ±1.6 decaying to 0 | 12 | 6 | 0.50 | CHART |
| C7 | recover_to_coil | 10 | 5 | 0.42 | CHART |
| | **Chart total** | **64** | **32** | **2.67** | |

Gate inherited from the chart: chart frames 0–27 @24 fps (coil + hold +
release, i.e. through contact) are pose-identical to the strike — a miss is
a catch until the bill comes up empty. In 12 fps terms: every tick through
grab_dwell must match Sequence 1's corresponding ticks.

---

## 2. NATURAL DURATION + PROPOSED DURATION

**Natural duration: 2.7 s (32 ticks).** That is the chart's full
strike_miss behavior, coil-deepen through recover, at the animal's timing
per study §3: the release is a blink (0.17 s), withdrawal ≈0.5 s, and on a
miss the bird shakes the water off and simply waits again — there is no
handling tail (§6 phases 1–7 are all catch-only).

**Proposed duration: 5.0 s = 60 ticks** — deliberately identical to
Sequence 1 (the strike, 5.0 s / 60 ticks). Justification:

- The miss must read as the strike's **twin**: identical until contact.
  Sequence 1 buys its 5.0 s with a long coil freeze and a slow
  withdrawal/settle. The miss matches the total and mirrors the freeze
  placement (home hold up front + stretched loaded hold) so a viewer who
  has just seen a catch gets the same rhythm and cannot call the outcome
  before the bill rises empty.
- The stretch is bought **only with holds** (the scheduler's one legal
  lever; held frames repeat a drawing for free): +28 ticks, all of them
  hold ticks. **No motion phase is stretched** — every motion phase runs
  at exactly its chart tick count.

| Proposed # | Phase | Ticks | Seconds | Basis |
|---|---|---|---|---|
| P1 | home_hold — the locked home frame, held | 12 | 1.00 | AUTHORED hold (twin-matching freeze; the scheduler's idle statue) |
| P2 | coil_deepen | 6 | 0.50 | CHART (C1) |
| P3 | loaded_hold — chart 6 ticks stretched to 16 (hold: true, free) | 16 | 1.33 | CHART + AUTHORED stretch |
| P4 | release (spacing 25/60/100%, beak opens on the approach tick, smear, splash at contact) | 2 | 0.17 | CHART (C3) |
| P5 | grab_dwell — bill closes on water, `fish: none` | 1 | 0.08 | CHART (C4) |
| P6 | withdrawal — empty, decelerating, drips | 6 | 0.50 | CHART (C5) |
| P7 | head_shake — 3 oscillations, ±1.6 decaying to 0 | 6 | 0.50 | CHART (C6) |
| P8 | recover_to_coil — ends on the exact home frame | 5 | 0.42 | CHART (C7) + AUTHORED final landing (§4) |
| P9 | home settle hold — home frame again; contact ripples finish spreading/fading here | 6 | 0.50 | AUTHORED hold |
| | **Total** | **60** | **5.00** | |

Note on the release at 12 fps: the chart's 4 frames @24 compress to 2
ticks. Tick 1 carries the 25%→60% travel with the beak still closed;
tick 2 carries 100%/contact, the beak-open (the ~1/30 s pre-impact opening
of study §3 lands inside this tick), the authored smear, and the splash
event. The smear and the opening are not optional extras — they are what
the 24 fps frames 3–4 contained, folded into the contact tick.

---

## 3. KEY POSES (drawing production list)

Clip-frame references are MEASURED from the old clip; chart references are
the governing source where the clip disagrees (§7).

1. **HOME-COIL** — the locked home frame itself (deep coil, bill down-right,
   feet planted, ripples at both feet). Not in the clip — the clip never
   visits this pose. Source: `home_frame_approval.png`. Used by P1, P8
   (final tick), P9.
2. **COIL-MAX / LOADED** — end of coil_deepen: coil at its maximum, gaze
   nailed, beak-tip movement ≤1 cell across the whole loaded hold. Chart
   C1/C2. (The clip has no equivalent — its f0–16 stand is upright and
   unloaded; do NOT draw from it.)
3. **RELEASE-MID (60%)** — hinge half-straightened, head on the unfolding
   arc, bill still closed. Chart C3 tick 1.
4. **CONTACT-SMEAR (100%)** — full extension, authored smear, beak OPEN,
   bill tip at the waterline, splash event fires. Chart C3 tick 2. In the
   clip the nearest frame is f29 (tip at water) — but the clip's tip
   arrives slow and closed, so f29 is a position reference only, never a
   pose reference.
5. **GRAB-EMPTY** — same extension as the catch's grab pose, bill now
   CLOSED on water, no fish anywhere in frame. Chart C4. This is the
   first frame in which miss ≠ catch.
6. **WITHDRAWAL-MID** — head halfway up on a decelerating rise, neck
   re-coiling, empty bill, drips leaving the tip. Chart C5. Clip
   corroboration: the rising head and falling drips at f86–90 are the
   clip's one chart-shaped passage.
7. **SHAKE-A / SHAKE-B / SHAKE-C** — head_shake extremes: neck_sway +1.6,
   −1.6, then a decaying pair (±≈0.8, ±≈0.3), 3 oscillations in 6 ticks,
   ending at sway 0. Chart C6. **Entirely absent from the clip** — no
   clip frame may be used for these.
8. **RECOVER-MID** — neck re-coiling from shake-neutral toward the deep
   coil, body rock settling (body settles ≈2 ticks after the neck at
   12 fps, per the strike chart's lead/lag halved), plume follow-through
   decaying. Chart C7.
9. **HEAD-DOWN DWELL (clip-only, REJECTED)** — clip f30–70: bill held at
   the water for 3.4 s. Recorded here so production knows it exists in
   the old asset and must NOT be reproduced; the chart has no such phase.
10. **FORWARD SWEEP (clip-only, REJECTED)** — clip f78–80: bill skimming
    forward through the surface with a splash wake. The clip's biggest
    splash, and uncharted; must NOT be reproduced (§7).

Poses 1–8 are the complete production list: 8 named poses, expanded by the
in-between drawings counted in §5.

---

## 4. DEPARTURE / RETURN

Home IS the deep coil, so departure is minimal — this is the smallest
departure in the repertoire. Precisely what moves:

**Departure (P1→P3), AUTHORED from the chart + home-frame ruling** (the
clip cannot show it — it starts upright):

- **Feet/legs: nothing.** Both feet stay planted at 15.2% / 20.3% of
  width on the 95.2% waterline for the entire sequence. No step, no
  re-plant, therefore no foot-plant ripple events in this sequence at all.
- **Body:** a subtle rock forward over the feet during coil_deepen —
  body_tilt −33° → −30° (strike chart keys), total rock ≤3°, per study §3
  ("the body rocks subtly forward over the feet — loading the hinge").
- **Neck/head:** the only real mover. From the home deep coil the neck
  sinks its final increment to coil maximum (the chart's last-4-frames
  @24 "settle deeper" = the final 2 ticks here), gaze locked on the
  target point mid-frame. Then absolute stillness: the loaded hold.
- **Plumes/chest cascade:** follow-through only; peaks ≈1–2 ticks after
  the neck reaches full coil (strike chart lead/lag, halved).
- **Water:** nothing new. The home frame's foot ripples persist; no
  ripple is born until the contact splash.

**Return (P6→P9):**

- Withdrawal (CHART) brings the empty bill up on a decelerating rise;
  drips fall from the tip across the phase and the contact splash's
  ripples begin spreading — they persist and fade across P7–P9, never
  popping out.
- Head_shake (CHART) happens at the top of the rise, neck_sway ±1.6
  decaying through 3 oscillations to exactly 0.
- Recover_to_coil (CHART timing, AUTHORED landing): the neck re-coils to
  the deep coil and the body's ≤3° rock settles back. Adaptation flag:
  the YAML recover keys end at `neck_coil: 0.85` (idle_hunt's base), but
  the architecture's home ruling overrides — the final tick of P8 is the
  **exact locked home drawing**, feet, waterline, framing and ripples as
  in frame 0. P9 then holds that drawing while the last ripples fade.

---

## 5. SIZE ESTIMATE

Unique drawings = proposed ticks − held repeats:

| Phase | Ticks | Held repeat ticks | Unique drawings |
|---|---|---|---|
| P1 home_hold | 12 | 11 (home drawing repeats) | 1 (the locked home drawing — shared, already exists) |
| P2 coil_deepen | 6 | 0 | 6 |
| P3 loaded_hold | 16 | 15 (repeats P2's final drawing) | 0 new |
| P4 release | 2 | 0 | 2 |
| P5 grab_dwell | 1 | 0 | 1 |
| P6 withdrawal | 6 | 0 | 6 |
| P7 head_shake | 6 | 0 | 6 |
| P8 recover_to_coil | 5 | 0 | 5 (final tick IS the home drawing: 4 new + 1 reuse) |
| P9 home settle hold | 6 | 6 (home repeats) | 0 new |
| **Total** | **60** | **34** | **26 unique (25 new + the shared home drawing)** |

Arithmetic: 26 × 58 KB = **1,508 KB ≈ 1.51 MB**.
Incremental cost if the shared home drawing is not charged to this
sequence: 25 × 58 KB = 1,450 KB ≈ 1.45 MB.

(The head_shake ticks are counted as all-unique: at 6 ticks for 3 decaying
oscillations no two ticks share a sway value. Ripple states are an effects
layer over the drawings, not separate drawings.)

---

## 6. PROVENANCE

- Source: `miss_attempt1.mp4` (per `STAGE_B_MANIFEST.md` clip table).
- Clip: `firmware-living-loop/stageb_clips/miss.mjpeg` — 6,771,964 B,
  md5 `7a49c6ac04e7df9213b0e6f2387676ea` (re-verified by md5sum for this
  spec; matches the manifest and the task brief). 120 frames @ 12 fps,
  1024×600, average frame 56,433 B, max 61,364 B (manifest).
- Conversion route (per STAGE_B_MANIFEST.md): frames extracted at 12 fps
  (every 2nd frame of the 24 fps source), background-normalized toward the
  approved plate's border median (247, 232, 210), then PIL/libjpeg
  `quality=80, subsampling=1, optimize=True`
  (`tools/clip_convert_stageb.py`) — the 4:2:2 layout the ESP32-P4 JPEG
  driver requires. (The brief's "q82" storage figure of ~58 KB/drawing is
  the planning rate used in §5; the clip itself was encoded q80.)
- Timing truth: `heron-movement-study.md` §3 + §6;
  `movement-charts.yaml` charts `strike` and `strike_miss`.

---

## 7. STUDY vs CLIP — every disagreement, and which was taken

1. **Start pose.** Clip: upright alert stand, neck tall (f0–16). Study/
   chart + architecture: the sequence starts from the (deep) coil — and
   in this build, from the exact home frame. **Took: chart/home.**
   The clip's opening 1.4 s is unusable as choreography.
2. **Release speed and shape.** Clip: 13 frames (1.08 s) of descent,
   f17–29. Chart: 4 frames @24 = 2 ticks (0.17 s). Bill-tip positions
   ground-located at stride 1 on the descent (1024×600 px): f20 tip
   ≈(843, 154); f26 tip ≈(683, 466); f29 tip ≈(658, 509). Travel:
   f20→f26 ≈351 px over 6 frames, then f26→f29 ≈50 px over 3 frames —
   the clip **decelerates** into contact. The chart demands the opposite:
   accelerating spacing (25% / 60% / 100% cumulative), most distance in
   the last frames, per study §3's hinge physics ("starts off apparently
   slow, then extends really, really fast"). **Took: chart.** The clip's
   descent is a slow dip, not a strike.
3. **Smear + beak-open.** Clip: no smear frame anywhere; bill reads
   closed through descent and contact (stride-1, f17–32). Chart: smear
   on release frame 3 @24, beak opens on the final approach frames
   (bill opens ~1/30 s before impact, study §3). **Took: chart** — both
   are folded into the contact tick of the 2-tick release (§2 note).
4. **The 3.4 s head-down dwell.** Clip f30–70 holds the bill at the water
   for 41 frames. Chart grab_dwell is 2 frames @24 = 1 tick. Nothing in
   study §3 supports a post-contact probe-hold on a miss ("withdrawal is
   empty and is followed by a small head-shake and an immediate return
   to the loaded hold"). **Took: chart.** Dwell rejected (pose 9, §3).
5. **The forward sweep.** Clip f71–82: a second, uncharted lunge — neck
   extended forward low, bill skimming the surface, the clip's only real
   splash (peak f78–80). The chart has exactly one release and one
   splash event, at contact. A double-dip miss would also break the
   twin gate (Sequence 1 has one strike). **Took: chart.** Sweep
   rejected (pose 10, §3); the rebuild's splash belongs at P4 contact,
   at the dwell-free strike point.
6. **Head-shake.** Clip: none — withdrawal f83–93 is a smooth monotonic
   rise (stride-1 viewed; the only event is a slight beak opening
   ≈f93–95 plus drips). Chart: head_shake, 12 frames @24 = 6 ticks, 3
   oscillations, neck_sway ±1.6 decaying to 0, between withdrawal and
   recover; study §3 confirms the shake is what a miss does. **Took:
   chart.** The shake is CHART-only; nothing in the clip may seed it.
7. **End pose.** Clip f119: upright alert stand, and the diff pass shows
   the bird never returns even to its own f0 pose cleanly (it settles
   nearby, still upright). Architecture: every sequence ends on the
   exact home frame. **Took: architecture/home** — return authored in §4.
8. **Recover target.** Chart recover_to_coil keys end at neck_coil 0.85
   (idle base). Architecture's home is the deep coil. **Took:
   architecture** for the final landing only; recover's tick count (5)
   is the chart's. Flagged in §4.
9. **Where the clip AGREES** (kept as corroboration, not source): the
   empty bill on withdrawal with drips falling across the rise
   (f83–96 ≈ chart C5 + its drips event); legs planted and static
   throughout (consistent with the home-stance legs law); ripples that
   persist, spread and fade rather than popping (f30–119); no fish in
   any frame (`fish: none` throughout, as the chart's gate demands).

---

## 8. CONFIDENCE

**Partial.**

- The clip measurement itself is clean: phase boundaries (f17, f30, f71,
  f83, f94) are corroborated independently by the frame-difference pass
  and by stride-1 viewing, and the bill-tip track is ground-located, not
  eyeballed.
- But the clip is structurally unfaithful to the behavior — wrong start
  and end poses, a decelerating 1.08 s "strike," a 3.4 s dwell and a
  second lunge the studies do not contain, and no head-shake at all.
  The rebuild's choreography is therefore chart-led: coil, release,
  grab, withdrawal, shake and recover timings and poses are CHART, the
  departure/return and the twin-matching hold stretches are AUTHORED
  from the architecture and Sequence 1's pacing, and only the
  withdrawal/drips passage and the static legs are genuinely
  clip-corroborated. A spec for this sequence cannot be a clean measure
  of its clip, because the clip does not perform the behavior.
