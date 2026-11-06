# STRETCH — Choreography Spec (measurement only, no drawing)

Sequence: **STRETCH** — the canonical same-side wing+leg stretch.
Playback: **12 fps always**. 1 tick = 1 frame at 12 fps = 1/12 s.
Storage model: unique drawings + timing; a held frame repeats one drawing for free.
Home frame (locked, start AND end of every sequence): colorized deep-coil drawing,
bird in left of frame, whole bird in frame, feet at **15.2% / 20.3% of width**,
waterline at **95.2% of height** — `gate1-strike/fresh/home_frame_approval.png` (viewed).
Bird identity (locked): white head, black brow into exactly two long black plumes,
yellow ringed eye, dagger bill, slate body with scalloped folded-wing covert rows,
ONE black shoulder patch, rusty bend-of-wing + thighs, shaggy chest-plume cascade,
long scaly legs, ankle (intertarsal) joint mid-leg. **NO CROP ever.**

**Side that stretches (AUTHORED choice, see §3): the NEAR (camera) side** — near wing +
near leg together. Stance leg = far leg; its foot never moves.

---

## 1. BEAT SHEET

### 1a. MEASURED — what the supplied clip actually does (120 frames @ 12 fps, 10.0 s)

Frames extracted by splitting the .mjpeg on `b'\xff\xd8'` (PIL decode, 120 frames
verified, 1024×600); contact strips at every 3rd and every 6th frame viewed;
frame-to-frame mean-abs-diff computed over all 120 frames (values cited below).

| # | Measured event | Clip frames | Seconds | Evidence |
|---|---|---|---|---|
| M1 | Initial stand, near-static. Tall upright neck, wings folded, both feet planted. This is NOT the home coil (bird is centred, much larger, neck up). | f0–f6 | 0.00–0.50 | diffPrev 0.07–0.64; strips f0/f3/f6 identical posture |
| M2 | Motion onset. Body repositions/darkens, wings still folded; no readable discrete weight-shift or head-tuck beat. | f7–f14 | 0.58–1.17 | diffPrev jumps to 4.02 at f7 and climbs steadily |
| M3 | **Both** wings begin opening; simultaneously one leg lifts in a small balance step — foot flexed up under the body (f18–f24, legs crop viewed) — and **re-plants by ~f27**. The leg never extends back. | f15–f27 | 1.25–2.25 | strips f15/f18/f21/f24/f27; key frame f18 viewed full-size |
| M4 | Both-wing spread continues to full span, neck extending UP to vertical, head up. Wings reach full spread ≈f42; wingtips touch the frame edges (crop risk in the source art). | f28–f41 | 2.33–3.42 | strips f30–f42; key frame f42 viewed full-size |
| M5 | Full-spread settle — still drifting, not yet a hold. | f42–f49 | 3.50–4.08 | diffPrev falls 6.24 → 2.67 |
| M6 | **TRUE HOLD (the only one in the clip)** — full both-wing spread, neck vertical. | f50–f67 (18 frames) | 4.17–5.58 | diffPrev ≤1.83, mostly <1.0 from f59; diff-vs-f0 flat ≈53.1 |
| M7 | Wing fold + neck lowers and begins tucking. Fold starts f68. | f68–f89 | 5.67–7.42 | diffPrev 3.52 at f68, peaks ≈14 at f72–f82 |
| M8 | Terminal tuck / settle drift — **unfinished**. Wings folded, head carried down into a low tucked coil; motion never stops (diffPrev decays 8.5 → 2.4 but never reaches hold values). Clip ENDS here. | f90–f119 | 7.50–9.92 | diff-vs-f0 at f119 = 24.2 (end pose ≠ start pose); strips f90–f117 |

**Where the clip ends:** mid-settle, head tucked down, wings folded — the return to the
clip's own starting pose is NOT in the clip, and the end pose is not the home frame
either (wrong position, wrong scale, neck/head still drifting).

### 1b. CHART — canonical timing (movement-charts.yaml `stretch`, 168 frames @ 24 fps = 7.0 s; halved to 12 fps ticks, seconds unchanged)

| Phase | @24 fps | 12 fps ticks | Seconds | Chart content |
|---|---|---|---|---|
| weight_shift | 18 | 9 | 0.75 | Weight commits to the stance leg; body rises slightly |
| tuck_head | 12 | 6 | 0.50 | Head/neck settle into the tucked perched position |
| wing_extend | 24 | 12 | 1.00 | Same-side wing extends DOWN and OUT; feathers fan in 3 steps (chart frames 8/16/24 @24 = ticks 4/8/12) |
| leg_extend | 18 | 9 | 0.75 | Same-side leg extends BACK until segments align with the body line, toes stretching open; leg ends at body height behind |
| full_hold | 48 | **24** | 2.00 | TRUE hold — no drift (gate) |
| leg_retract | 12 | 6 | 0.50 | Leg returns |
| wing_fold | 18 | 9 | 0.75 | Wing folds |
| settle | 18 | 9 | 0.75 | Ends on idle base pose; plume follow-through ≥6 frames (@24; ≥3 ticks @12 — spec keeps ≥6 ticks, see §4) |
| **Total** | **168** | **84** | **7.0** | Gates: wing+leg SAME side; full_hold is a true hold |

Study §10 (heron-movement-study.md): same-side wing+leg form [21][22]; held 5–15 s in
Grey Heron observations — that range is for the animal's **total behavior**.

### 1c. AUTHORED — proposed beat sheet for this sequence (home → home)

| # | Phase | Source | Ticks @12 | Seconds | Notes |
|---|---|---|---|---|---|
| A0 | HOME frame | locked plate | (frame 0) | — | Exact home drawing; shared, not a new drawing |
| A1 | departure | AUTHORED | 6 | 0.50 | Home coil → chart idle-base posture; weight begins committing (§4) |
| A2 | weight_shift | CHART | 9 | 0.75 | Weight fully on far (stance) leg |
| A3 | tuck_head | CHART | 6 | 0.50 | Neck settles to tucked perched position |
| A4 | wing_extend | CHART | 12 | 1.00 | NEAR wing down+out; fan steps at ticks 4/8/12 of the phase |
| A5 | leg_extend | CHART | 9 | 0.75 | NEAR leg back to body height, segments aligned, toes open |
| A6 | full_hold | CHART | 24 | 2.00 | **ONE drawing**, repeated 24 ticks |
| A7 | leg_retract | CHART | 6 | 0.50 | Near foot returns to its EXACT home plant; ripple on plant |
| A8 | wing_fold | CHART | 9 | 0.75 | Near wing folds back to scalloped covert rows |
| A9 | settle | CHART | 9 | 0.75 | To idle base pose; plume follow-through ≥6 ticks |
| A10 | settle_to_home | AUTHORED | 6 | 0.50 | Idle base → deep home coil; final tick = exact HOME frame (§2, §4) |
| | **Total** | | **96 ticks** | **8.0 s** | |

Alternate (one line): variant `stretch_warble` — both wings raised above the back +
neck fully vertical, 120 frames @24 = 60 ticks @12 = 5.0 s (rise/hold/fold/settle);
not specced here — but note the supplied clip is far closer to this variant than to
the canonical form (§7).

---

## 2. NATURAL DURATION + PROPOSED DURATION

- **Natural duration: 7.0 s** — the chart's canonical value (168 @24), inside the
  animal's documented 5–15 s total-behavior range (study §10, Grey Heron [22]).
  The clip's 10.0 s encode also falls in that range numerically, but it is a
  different variant with an unfinished terminal drift, so it is **not** duration
  evidence for the canonical form. Studies win.
- **Proposed duration: 8.0 s = 96 ticks @ 12 fps**, including departure + return.
  - Chart core A2–A9 = 84 ticks / 7.0 s, internal timings untouched.
  - **+6 ticks departure (A1)** and **+6 ticks home settle (A10)**, authored.
- ⚠ **FLAG — ending mismatch:** the chart's 7.0 s ends at **idle base pose**
  (neck_coil 0.85, chart settle keys). Our sequence must end on the **deep home
  coil**. A10 is authored to close that gap: neck deepens from idle coil to the
  home coil, head/bill come down to the home angle, chest-plume cascade settles,
  and the **final tick is the exact locked home drawing** (same drawing as frame 0,
  reused — not a near-copy).

---

## 3. KEY POSES

Canonical poses (the ones to be drawn). "Near" = camera side.

| Pose | Source | Description |
|---|---|---|
| HOME | locked plate | Deep coil, bird left of frame, feet 15.2% / 20.3% W, waterline 95.2% H. Start + end. |
| DEPARTURE_BASE | AUTHORED (A1 end) | Home coil eased to chart idle-base posture; stretch-side (near) foot unweighting, stance (far) foot planted. |
| WEIGHT_COMMIT | CHART weight_shift end | All weight on the FAR leg; body risen slightly; near foot light, still at its home plant. Stance foot does not move from here on. |
| TUCKED | CHART tuck_head end | Head/neck in the tucked perched position (neck_coil 0.95, head_pitch 10 per chart keys). |
| FAN_1 / FAN_2 / FAN_3 | CHART wing_extend ticks 4 / 8 / 12 | Near wing progressively down+out; trailing-edge scallops open in 3 fan steps; FAN_3 = wing fully extended, feathers fully fanned. Far wing stays folded. |
| LEG_ALIGN | CHART leg_extend end | Near leg extended straight BACK at body height, segments aligned with the body line, toes stretched open. Ankle joint visibly mid-leg in the aligned line. |
| FULL_STRETCH_HOLD | CHART full_hold | FAN_3 + LEG_ALIGN simultaneously, **same (near) side**; tucked head. This single drawing is held 24 ticks. |
| LEG_REPLANT | CHART leg_retract end (plant point AUTHORED) | Near foot back down at its EXACT home position (20.3% W — see side note below); ripple ring fires at this plant. |
| WING_FOLDED | CHART wing_fold end | Near wing refolded; scalloped covert rows + the ONE black shoulder patch restored. |
| SETTLE_IDLE | CHART settle end | Idle base pose; plumes still settling (follow-through ≥6 ticks across A9). |
| HOME_RETURN | AUTHORED (A10 end) | Exact locked home drawing. Pose distance to frame 0 = 0. |

**Which leg/wing stretches — NEAR side (AUTHORED).** The chart names the moving leg
generically (`leg_step`) and only gates "wing and leg extended are on the SAME side";
the clip contains no leg extension to copy (§7). Near side is chosen because it is the
only side whose wing fan and back-extended leg line are fully visible in profile —
a far-side stretch would be occluded by the body. Assignment against the home frame:
**stance leg = far leg, home foot at 15.2% W (never moves); stretching leg = near leg,
home foot at 20.3% W (leaves, and must return to exactly 20.3% W).**

Clip-reference poses (measured, for provenance/comparison only — NOT canonical keys):
CLIP_TALL_STAND (f0), CLIP_STEP_LIFT (f21–f24, balance step, foot flexed under body),
CLIP_WARBLE_FULL (f42–f67, both wings spread, neck vertical), CLIP_TUCKED_END (f119,
head-down drift, unfinished).

---

## 4. DEPARTURE / RETURN

### Departure — home coil → behavior (parts marked)

- **[AUTHORED] A1 departure (6 ticks):** deep home coil → chart idle-base posture.
  Neck eases from the home deep coil toward the hunting/base coil; body unweights
  the near side. No foot moves in this part; both ripple rings persist at the feet.
- **[CHART] A2 weight_shift (9 ticks):** weight commits fully to the far (stance)
  leg; body rises slightly. Near foot lightens but stays at its home plant until
  leg_extend. Stance foot never moves again for the whole sequence.
- **[CHART] A3 tuck_head (6 ticks):** head/neck settle into the tucked perched
  position — the last departure beat before extension.

### Return — behavior → home coil (authored from the chart; the clip cuts off, §1a M8)

- **[CHART] A7 leg_retract (6 ticks):** near leg comes down/forward from body
  height; **[AUTHORED plant detail]** the near foot re-plants at its EXACT home
  position (20.3% W, waterline 95.2% H) at the end of this phase and **that plant
  gets its ripple ring**; the stance foot's ripple has persisted throughout.
- **[CHART] A8 wing_fold (9 ticks):** near wing folds; covert rows re-lay, black
  shoulder patch returns to its folded position.
- **[CHART] A9 settle (9 ticks):** returns to idle base pose; plume follow-through
  ≥6 ticks (chart specifies ≥6 frames @24 = 3 ticks @12; this spec holds the
  stronger ≥6 ticks so the cascade visibly settles before the home deepen).
- **[AUTHORED] A10 settle_to_home (6 ticks):** idle base → deep home coil — neck
  sinks into the full S, head/bill drop to the home angle, chest-plume cascade
  comes to rest. **Final tick = the exact locked HOME drawing.** No new end pose
  may be drawn for this tick; it reuses the home drawing so the loop point is exact.

Water law throughout: ripple rings at the feet persist; the stretching foot carries
no ripple while extended behind at body height (it is out of the water); only its
re-plant (A7) earns a new ring.

---

## 5. SIZE ESTIMATE

Counting rule: one unique drawing per tick of motion; a true hold costs ONE drawing
no matter how many ticks it repeats; the HOME drawing already exists as the locked
plate and is reused at both ends (0 new drawings).

| Part | Ticks | Unique drawings |
|---|---|---|
| A1 departure (authored) | 6 | 6 |
| A2 weight_shift | 9 | 9 |
| A3 tuck_head | 6 | 6 |
| A4 wing_extend | 12 | 12 |
| A5 leg_extend | 9 | 9 |
| A6 full_hold | 24 | **1** |
| A7 leg_retract | 6 | 6 |
| A8 wing_fold | 9 | 9 |
| A9 settle | 9 | 9 |
| A10 settle_to_home (authored) | 6 | 6 |
| HOME (start/end, shared) | — | 0 |
| **Total** | **96 ticks** | **73** |

Arithmetic: motion ticks = 96 − 24 (hold) = 72 unique, + 1 hold drawing = **73 unique drawings**.
Size: 73 × 58 KB = **4,234 KB ≈ 4.23 MB** (decimal MB; ≈4.04 MiB).
The hold is the saving: without it the sequence would cost 96 drawings ≈ 5.57 MB;
the 24-tick hold as one drawing saves 23 drawings ≈ 1.33 MB.

---

## 6. PROVENANCE

- Source video: **stretch_attempt1.mp4** (per STAGE_B_MANIFEST.md clip table).
- Clip: `firmware-living-loop/stageb_clips/stretch.mjpeg` — **6,843,508 B**,
  **md5 d04835f445fc2c30e3a0914e0eca7c76** (re-verified on disk during this pass;
  matches the task brief and the manifest), 120 frames @ 12 fps, 1024×600.
- Conversion route (per STAGE_B_MANIFEST.md): frames extracted at 12 fps (every 2nd
  frame of the 24 fps source), background-normalized toward the approved plate's
  border median (247, 232, 210), then PIL/libjpeg **quality=80, subsampling=1
  (4:2:2), optimize=True** via `tools/clip_convert_stageb.py` — the proven Stage A
  route (the ffmpeg MJPEG encoder is a known failure on the ESP32-P4).
  Manifest lists this clip's average frame as 57,029 B, consistent with the
  ~58 KB/drawing costing figure used in §5.
- Timing truth: `heron-movement-study.md` §10 + `movement-charts.yaml` chart
  `stretch` (and variant `stretch_warble`). Clip disagreements were resolved in
  favor of the studies (§7).

---

## 7. STUDY vs CLIP — disagreements (studies win in every case)

1. **Form: clip = warble-like, chart canonical = same-side.** The clip spreads
   **BOTH** wings symmetrically to full span with the neck extended fully UP —
   the `stretch_warble` family (study §10 second form). The canonical chart form
   is ONE wing (same side as the leg) extending DOWN and OUT with the head tucked.
   **Took: chart.** The clip is not usable as choreography reference for the
   canonical sequence beyond its hold/fold timing texture.
2. **Leg: the v1.1 failure mode, repeated.** Study/chart require the same-side leg
   extended BACK to body height, segments aligned, toes open. The clip has **no leg
   extension at all** — only a small balance step (foot lifts flexed under the body
   f15–f26, re-plants ~f27, both feet planted for the entire spread and hold).
   This is exactly the flagged "wing-only stretch with no leg" failure.
   **Took: chart** (leg_extend A5, 9 ticks, authored from chart keys).
3. **Head/neck: opposite directions.** Chart: tuck_head into the perched tuck
   before extension. Clip: neck extends UP to vertical and stays up through the
   hold; the tuck only appears as part of the terminal collapse (M8).
   **Took: chart.**
4. **Hold: present but wrong pose, and shorter.** Chart full_hold = 24 ticks
   (2.0 s) of true hold at full same-side stretch. Clip's only true hold is
   f50–f67 = 18 ticks (1.5 s) at the warble pose, preceded by 8 ticks of drift
   (M5) — a hold that arrives late and holds the wrong shape. The chart's gate
   ("full_hold is a true hold, no drift") is met by the clip's M6 window in
   stillness terms only. **Took: chart** (24 ticks, one drawing).
5. **Return: missing in the clip.** Chart runs leg_retract → wing_fold → settle
   to idle base. The clip folds its wings (M7) but then drifts for 30 ticks into
   an unfinished head-down tuck (M8) and stops — no leg retract (nothing to
   retract), no settle endpoint, end pose ≠ start pose (diff 24.2).
   **Took: chart + authored A10** (§4). ⚠ The parent brief's note "the return is
   NOT in the clip" is confirmed in substance: the wing fold is present, the
   *return to pose* is not.
6. **Framing/scale: clip violates the sequence architecture.** Clip bird is
   centred and large; at full spread the wingtips reach the frame edges. The
   locked architecture requires the home-frame scale/position (bird left of
   frame, whole bird in frame, NO CROP). **Took: architecture.** ⚠ Layout check
   owed at draw time: FULL_STRETCH_HOLD extends the leg BACK (toward the left
   edge, where the home framing leaves the least margin) — the full-stretch
   drawing must be verified whole-in-frame at home scale before admission.
7. **Duration:** clip encode 10.0 s vs chart 7.0 s. The clip's extra time is its
   slow onset morph (M2) and unfinished terminal drift (M8), not behavior.
   **Took: chart** 7.0 s core; proposed 8.0 s with authored departure/home-settle.

No disagreement on: feathers fanning as the wing opens (visible in the clip's
spread, M4 — consistent with the chart's fan steps, though the clip fans both
wings continuously rather than one wing in 3 steps).

---

## 8. CONFIDENCE

**Partial — clip measured cleanly, canonical choreography mostly authored.**

- The clip measurement itself is solid: all 120 frames decoded and viewed as
  strips + full-size keys + leg crops, with frame-diff numbers backing every
  span boundary in §1a (onset f7, hold f50–f67, fold onset f68, unfinished end).
- But the canonical same-side wing+leg stretch **does not occur in the clip** —
  the clip is a both-wing warble with no leg extension and an opposite neck
  action. Every canonical phase timing therefore comes from the chart
  (halved 24→12 fps), the side assignment (near) is an authored choice the
  chart leaves open, and the departure (A1) + home settle (A10) are authored
  to satisfy the home-frame architecture. Nothing in §§1c/3/4 should be read
  as measured from footage.
