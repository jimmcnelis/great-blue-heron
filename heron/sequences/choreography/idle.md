# IDLE — choreography spec (measurement only, no drawing)

**Sequence:** IDLE — the hunt idle: stillness with a working head.
**Architecture:** plays over the static marsh plate; starts AND ends on the locked
home frame (colorized deep-coil drawing, bird left of frame, whole bird in frame,
feet at 15.2% / 20.3% of width, waterline at 95.2% of height —
`gate1-strike/fresh/home_frame_approval.png`). Playback 12 fps throughout.
Storage = unique drawings + timing; held frames repeat for free.
Legs planted throughout; no crop ever; the bird never leaves the home pose
except for micro head events (see §4).

---

## 1. Beat / event sheet

### 1a. Proposed event script (NEW — chart-based, re-based onto the home deep coil)

Base pose for every hold = the locked home drawing itself (deep coil, head down
at the water). The chart's base (`idle_hunt`: neck_coil 0.85, body_tilt −33) is
**replaced** by the home pose; chart head-event values (head_yaw / head_roll)
are re-based as gaze/roll offsets from the home fixation. All motion is
head-only: neck coil, body, and legs never move; feet stay planted at
15.2% / 20.3% for all 300 ticks. Chart frame counts are 24 fps; ticks below
are 12 fps (halved, with rounding noted). Items marked **AUTHORED** are
adaptations, not chart values.

| Ticks (12 fps) | Dur | Event | Source / notes |
|---|---|---|---|
| 0–43 | 44 | hold_fixate (home) | chart hold_fixate 71@24 ≈ 36 ticks, re-stretched (holds may stretch; motion may not) |
| 44–45 | 2 | **blink** | chart blink 3@24 → 2 ticks (tick 1 = BLINK_CLOSED, tick 2 = home) |
| 46–85 | 40 | hold_fixate | chart 66@24 ≈ 33, re-stretched |
| 86–87 | 2 | **gaze_saccade_right** — head_yaw → +35, ballistic, full travel, no ease | chart 3@24 → 2 ticks (1 intermediate + target) |
| 88–143 | 56 | hold_fixate (at +35) | chart 93@24 ≈ 47, re-stretched |
| 144–146 | 3 | **head_roll_tilt** — head_roll → +14°, a lean, not a saccade | chart 6@24 = 3 ticks exactly |
| 147–186 | 40 | hold_tilted (the glare cock, held) | chart 66@24 ≈ 33, re-stretched |
| 187–189 | 3 | head_roll_release — roll → 0 | chart 6@24 = 3 ticks exactly |
| 190–191 | 2 | **gaze_saccade_back** — head_yaw → 0, ballistic | chart 3@24 → 2 ticks; passes through the saccade intermediate, reused |
| 192–227 | 36 | hold_fixate | chart 97@24 ≈ 49, shortened — the scan (below) is funded from holds |
| 228–235 | 8 | **slow scan** — head_yaw 0 → −35, eased (the ONLY eased head move in the canon) | **AUTHORED**: from variant `idle_hunt_c` (24@24 = 12 ticks, → −50); compressed to 8 ticks / −35 so the held-fraction gate survives (see §2) |
| 236–251 | 16 | hold at scan end (−35) | **AUTHORED** hold; scan-end pose held, not eased back |
| 252–253 | 2 | gaze_saccade_return — head_yaw → 0, ballistic | **AUTHORED** (the animal snaps back from a scan); passes through scan pose −18, reused |
| 254–277 | 24 | hold_fixate | — |
| 278–279 | 2 | **blink** | chart blink 3@24 → 2 ticks; same BLINK_CLOSED drawing |
| 280–299 | 20 | hold_fixate (home) — final tick IS the home drawing | chart closing hold 63@24 ≈ 32, shortened |

**Totals:** 300 ticks; motion ticks = 24 (2 blink + 2 saccade + 3 tilt + 3 release
+ 2 saccade + 8 scan + 2 return + 2 blink); held ticks = 276;
**held fraction = 276/300 = 0.92 — exactly at the chart gate (≥ 0.92).**
No periodic component anywhere: event spacing is irregular by construction
(44 / 40 / 56 / 40 / 36 / 16 / 24 / 20-tick holds).

### 1b. The clip's measured behavior — the REJECTED model

Measured on `idle1_norm.mjpeg` (120 frames @ 12 fps, frames extracted and
landmark-tracked; bill tip tracked by bill-orange mask, head by template
match, motion by inter-frame mean-abs-difference, MAD):

- **Pose is not the home pose.** The clip bird is upright and alert — neck up,
  head high (top of head y ≈ 33), bird spanning x ≈ 35–886 (~83% of frame
  width), roughly centred. The home bird is a deep coil, left of frame, head
  down at the water. The clip cannot serve as this sequence's base or as pose
  reference for it.
- **Near-still only at the head of the clip.** Adjacent-frame MAD ≈ 0.2 for
  frames 0–27; the first transition ≥ 1.0 is at frame 28. Near-held transitions
  (MAD < 0.5): **28/119 = 24%** — against the chart's ≥ 92% held gate.
- **One slow continuous rise-and-fall dominates.** Bill-tip y: 57 px (f0) →
  wobbles ≤ 2 px through ~f28 → rises steadily to **y ≈ 0–8 at f48–60** →
  falls back through f64–76 → settles at y ≈ 72–75 for f76–119, i.e. ~15–18 px
  *below* and ~10 px left of its start. Bill-centroid y total excursion
  ≈ 70 px (≈ 26 → ≈ 97). Mask (bird) area grows 108,933 → 113,413 px (+4.1%)
  across the clip — the pose itself morphs (neck uncoils, then over-coils),
  it does not purely oscillate.
- **Period / amplitude (the "breathing"):** one full rise-and-fall takes
  ≈ 72 frames ≈ **6.0 s**; FFT of the mask-area and centroid series puts the
  dominant components at **0.2 Hz (5.0 s period)** and 0.1 Hz (the single
  10 s trend) — squarely in the study §2's indictment of v1.1's sine family
  (periods 3.3–6.9 s). Bill-tip vertical amplitude ≈ 57 px on the up-stroke,
  ≈ 74 px total range. A small residual sway (± ~5 px at the bill centroid)
  persists to the last frame; the clip never reaches a true hold after f28.
- **The head leaves the frame.** Around f48–64 the rising head reaches and
  crosses the top edge (bill-pixel count collapses to 41 at f56 — most of the
  bill is out of frame). Direct violation of the architecture's whole-bird /
  no-crop law.
- **It does not loop.** f119 → f0 MAD = **14.29**, ~70× the opening
  adjacent-frame MAD (~0.2); no sampled lag returns to baseline (lag-MAD
  minimum 7.8 at lag 12, rising to ~13–14). Template match confirms the end
  pose is a *different* pose (head settled dx −16, dy +12 vs f0, NCC 0.85
  from f72 on). There is no loop point, internal or at the ends.
- **Zero chart events.** No blink, no saccade, no head-roll anywhere in the
  120 frames — all motion is continuous.

## 2. Duration

- **Natural duration (chart):** `idle_hunt` canonical = 480 frames @ 24 fps =
  **20.0 s** = 240 ticks at 12 fps.
- **Clip duration:** 10.0 s (120 frames) — its own length, rejected with its model.
- **Proposed duration: 25.0 s = 300 ticks.**

Justification. The player's still already covers infinite holds, so this
sequence does not exist to fill time — it exists as the one authored *event
window*: the difference between a statue and a hunting bird is seven discrete
events, and those events need animal-scale fixations around them or they read
as fidgeting. The chart's own laws then fix the length: motion may never
stretch, only holds may; and the held-fraction gate (≥ 0.92) must hold. The
re-based script carries 24 motion ticks (the halved chart events plus the
AUTHORED scan from `idle_hunt_c`); at the chart's natural 240 ticks that is a
held fraction of 216/240 = 0.90 — a gate failure. Keeping every chart event
*and* the scan *and* the gate requires total ≥ 24 / 0.08 = **300 ticks**, so
the extra 5.0 s is bought entirely as hold time (the one currency the chart
allows). Event density lands at 7 events / 25 s, in scale with the real
bird's seconds-long fixations (study §2, §5). And a 25 s idle never traps
the viewer: inter-sequence pauses and the still are the player's runtime
choice at every sequence boundary.

## 3. Key poses (unique drawings)

| Pose | Drawings | Source |
|---|---|---|
| HOME — deep coil, head down at water | 1 (existing, locked, shared by all sequences) | `home_frame_approval.png` |
| BLINK_CLOSED — eyelid closed over the yellow ringed eye | 1 (reused by both blinks) | chart `blink` phases. **The clip cannot supply this** — it contains no blink and the wrong pose |
| SACCADE_MID_R — head_yaw ≈ +18 (ballistic intermediate) | 1 (reused by saccade_back) | chart `gaze_saccade_right` (full travel, no ease; intermediate is a drawn pass-through, not an ease) |
| SACCADE_R — head_yaw +35 fixation | 1 (also the base orientation for the tilted poses) | chart `gaze_saccade_right` target |
| TILT_MID — yaw +35, roll ≈ +7 | 1 (reused by release) | chart `head_roll_tilt` |
| TILT_FULL — yaw +35, roll +14, the sideways glare cock | 1 (held for the 40-tick hold_tilted) | chart `head_roll_tilt` target / `hold_tilted` |
| SCAN_1…4 — head_yaw −9 / −18 / −26 / −35 | 4 (each held 2 ticks across the scan; SCAN_4 doubles as the hold-at-scan-end pose; SCAN_2 is reused as the saccade-return intermediate) | **AUTHORED** from variant `idle_hunt_c` slow scan |

**Total: 9 new unique drawings + the shared home drawing.**
Every non-home pose must be drawn *on the home bird* — same deep coil, same
left-of-frame scale and placement, identity locked (white head, black brow
into exactly two long black plumes, yellow ringed eye, dagger bill, slate
body, one black shoulder patch, rusty accents, shaggy chest plumes). The clip
supplies **none** of these poses: wrong base pose, wrong framing, no events.

## 4. Departure / return

- **Departure: none.** The bird never leaves the home pose. Body, neck coil,
  and legs are identical in all 300 ticks; only the head works — two blinks,
  three ballistic gaze saccades, one head-roll tilt out and back, one slow
  scan. Feet never move; no ripple, no step, no repositioning.
- **Return: trivially home on every hold.** Because holds *are* the home
  drawing (or a named event pose held verbatim) and every event chain ends
  back at head_yaw 0 / roll 0, the sequence is on the exact home frame at
  ticks 0–43, 46–85, 192–227, 254–277 and 280–299 — and its final tick is
  the home drawing, so the handoff to the player's still is frame-exact.

How this sequence differs from the home still: the still is a statue; the
idle is a statue that blinks, looks, and cocks its head at glare. Nothing in
the frame changes except the head, and the head changes only seven times in
25 seconds — each change fast (2-tick saccades), slow-leaning (the tilt), or
deliberately eased (the one scan), separated by fixations long enough to
forget the last event before the next lands. That eventfulness-at-statue-scale
is the entire justification for the sequence's existence next to the still:
played between behaviors it keeps the bird *hunting*; the still alone, held
indefinitely by the player, is the same bird at rest between hunts. If the
events were removed, this sequence would be a 25-second copy of the still
and should not be stored at all.

## 5. Size estimate

- New unique drawings: 9 × 58 KB = **522 KB = 0.522 MB** (≈ 0.51 MiB).
- Counting the home drawing as if stored with this sequence: 10 × 58 KB =
  580 KB = 0.58 MB — but the home drawing is shared platform-wide (it is the
  player's still and every sequence's first/last frame), so the marginal
  storage of IDLE is **0.52 MB**.
- The full 300 ticks (25.0 s) are produced from these 10 drawings; all
  276 held ticks repeat a drawing for free.
- This is the smallest sequence in the set by construction: no body motion,
  no new body poses, every return path reuses its outbound drawings.

## 6. Provenance

- Source clip: `attempt1.mp4` (Stage A file), reused as-is per
  `STAGE_B_MANIFEST.md`; measured here in its normalized variant
  **`idle1_norm.mjpeg`** — background-normalized option asset (per-clip
  background pulled to the approved plate's border median (247, 232, 210)),
  route per `STAGE_B_MANIFEST.md` / `tools/clip_convert_stageb.py`: frames
  extracted at 12 fps (every 2nd frame of the 24 fps source), PIL/libjpeg
  encode, 4:2:2 (subsampling=1).
- Clip measured: 120 frames @ 12 fps, 1024×600, **6,520,692 B, md5
  `29bfb138e90a3fe23a8496dd76722fb7`** (md5 re-verified on disk this pass;
  manifest average frame 54,339 B).
- Companion micro-loop (noted, not measured): **idle2 / `attempt2.mp4`**,
  Stage A reuse file, 12 frames, **1,011,709 B, md5
  `910e8fdad928203cc6a609c5926c2048`**.
- Timing truth: `heron-movement-study.md` §2 (the hunt idle) and §5 (head
  movements); chart `idle_hunt` (+ variant `idle_hunt_c`) in
  `movement-charts.yaml`.
- Measurement scratch: `/tmp/choreo_idle/` (extracted frames, contact
  strips `contact12.png` / `contact24.png` — viewed this pass).

## 7. Study vs clip — the disagreement and the ruling

The study (heron-movement-study.md §2) abolishes the breathing model in
terms: v1.1's idle was "four perpetual sine waves… the bird breathes like a
metronome and never once holds still. The animal is the opposite: stillness
punctuated by events." The chart enforces it — `idle_hunt` contains *only*
discrete events, with gates: held fraction ≥ 0.92, no periodic component
anywhere.

The measured clip is the abolished model, and the numbers convict it on
every gate: held fraction ≈ 0.24 (near-held transitions 28/119) vs ≥ 0.92
required; a dominant periodic component at ≈ 0.2 Hz / ~5–6 s sway period
with ≈ 57–74 px bill-tip amplitude vs *no periodic component* required;
zero of the chart's events present. It additionally fails this project's
architecture on grounds the study never had to consider: its base pose is
an upright alert bird, not the locked home coil; its head exits the top of
the frame around f48–64; and it does not even loop (f119→f0 MAD 14.29,
ending in a visibly different, deeper-coiled pose), so it fails as a loop
on its own terms too.

**Ruling applied: the study wins, completely.** The clip's motion model is
rejected; nothing from the clip — no pose, no timing, no sway — carries
into the proposed sequence. The spec in §1a is built solely from the
`idle_hunt` chart (plus the AUTHORED `idle_hunt_c` scan), re-based onto the
locked home drawing. The clip survives only as documentation in §1b and as
the Stage A provenance record in §6.

## 8. Confidence

**Partial.** The clip measurements are real and direct (frames extracted
and landmark-tracked this pass; md5 re-verified; contact strips and key
frames viewed) — that half is clean. The event script is chart-derived but
not chart-verbatim: the re-basing onto the deep home coil (vs the chart's
0.85 hunting coil), the 24→12 fps rounding, the scan compression
(12 ticks / −50° → 8 ticks / −35°), the AUTHORED scan-return saccade, and
the hold re-stretch to 300 ticks are authored adaptations that no drawing
or render has yet validated — in particular whether a 2-tick saccade and a
1-drawing blink read cleanly on the home bird at 12 fps, and whether the
tilt/scan poses can be drawn on the deep coil without disturbing the locked
identity. Grade accordingly: trust the rejection numbers; treat the script
as a spec to be eye-gated at first drawing, not as measured fact.
