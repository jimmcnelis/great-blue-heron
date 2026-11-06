# COURTSHIP (the display) — choreography spec

*Measurement worker pass, 2026-11-05. NO drawing — measurement and spec only.
Playback 12 fps throughout; seconds = frame / 12. Storage = unique drawings +
timing; held frames repeat for free; ~58 KB per unique drawing
(1024×600 JPEG q82 4:2:2).*

*Method: every one of the 120 clip frames viewed in contact strips
(6 strips × 20 frames); full-resolution spot checks at f9, f10, f44, f55,
f70, f84, f100, f119; bill-tip tracked with an orange-mask pass at stride 5
plus visual reads off the strips. Scratch in `/tmp/choreo_courtship/` only.
There is NO courtship chart in `movement-charts.yaml` — no CHART rows exist
in this spec.*

---

## 1. BEAT SHEET

Clip: 120 frames, 0–119, 0.00–9.92 s. The clip's bird is a **tall upright
stand**, NOT the locked home deep coil — the display is already in progress
when the clip opens, and the clip ends mid-display with no return.

| # | Phase (named from behavior seen) | Clip frames | Seconds | Mark |
|---|---|---|---|---|
| A | Upright stand, bill closed and horizontal, neck in a tall S, feet planted, near-still | f0–f9 | 0.00–0.75 | MEASURED |
| B | **Bill-open call beat** — bill snaps from closed (f9) to wide open in ONE frame (f10), head tips up ~20–30°, gape then slowly narrows; no repeated snapping | f10–f34 | 0.83–2.83 | MEASURED |
| C | Stretch rise — bill closes, neck straightens and extends, head climbs, bill angle steepens toward skyward; bill tip exits the top of frame ≈f44 | f35–f47 | 2.92–3.92 | MEASURED |
| D | **Full skyward stretch, held** — neck fully extended vertical, bill pointing at the sky, posture held with only micro-sway (near-identical f55–f83). Legs/feet/body bottom OUT OF FRAME (see §7) | f48–f83 | 4.00–6.92 | MEASURED (posture); framing violates no-crop law |
| E | Lowering — bill comes down from skyward through ~45° (f84–f85) to horizontal; whole bird back in frame ≈f89–f90 | f84–f94 | 7.00–7.83 | MEASURED |
| F | **Bow** — neck arcs forward and down, head descends below the body line, bill points down, crown plumes flop forward over the head; nadir ≈f105–f112 (bill tip lowest, pointing down/back) | f95–f112 | 7.92–9.33 | MEASURED |
| G | Partial lift out of the bow — head rises slightly, neck still extended down-forward, bill diagonal down-forward. **Clip ends here, mid-beat.** | f113–f119 | 9.42–9.92 | MEASURED (truncation) |
| H | Plume erection as a distinct display beat | — (not in clip) | — | AUTHORED — deep-dive §1.7: Stretch Display = "neck up, bill skyward, **plumes erected**, then head lowered with a moan" [Documented — Mock/Vennesland tradition via Birds Outside My Window; WBU]. In the clip the plumes only trail/hang passively with head angle; they never erect. |
| I | Bill-snapping / clappering as repeated snaps | — (not in clip) | — | AUTHORED if used — deep-dive §1.7 lists "bill-clap duets" in the colony repertoire. The clip shows ONE sustained open-bill hold (phase B), not clappering; a duet is by definition two-bird, so solo clappering is at most a faint echo. Not in the proposed timeline. |
| J | Departure (home coil → display) and Return (display → home coil) | — (not in clip) | — | AUTHORED — see §4 |

**Feet / legs (verified where visible):** feet stay planted in every frame
where they are visible (f0–f47 and f89–f119); no step, lift, or weight-shift
step occurs; both foot rings are present and constant. Feet are
**unverifiable f48–f88** because they are out of frame (§7). Legs law is
satisfied where it can be checked: the display is a planted-feet behavior,
rings stay constant for the whole proposed sequence.

**Bill-tip track** (approx. % of frame width / % of frame height; lower
height % = higher on screen; stride ~10, orange-mask + visual):

| Frame | Bill tip (x%, y%) | Reading |
|---|---|---|
| f0 | (80, 9) | horizontal, closed |
| f10 | (84, 6) | wide open, head tipping up |
| f20 | (81, 9–12) | open, gape narrowing |
| f30 | (80, 8) | nearly closed |
| f40 | (77, 0–2) | rising, tip at top edge |
| f44 | tip out of frame (top) | stretch exceeding frame |
| f60–f80 | (57, 0) | skyward, tip at top edge, cropped framing |
| f84 | (61, 2) | descending from skyward |
| f90 | (68, 24–27) | back in full frame, ~30° up |
| f95 | (75, 47) | bow underway, tip dropping fast |
| f100 | (75, 57) | bow, bill down-left |
| f110 | (67, 68) | bow nadir — tip lowest in clip |
| f119 | (82, 50) | partial lift, still down-forward |

Neck extension reads the same way: tall-S (A) → S straightening (C) →
fully extended vertical, roughly doubling the visible neck length (D) →
re-folding on the way down (E) → extended again but forward-down in the
bow (F–G). The head's total travel is from y≈9 % (bill tip, horizontal)
to the top edge and out (skyward), down to y≈68 % (bow nadir).

---

## 2. NATURAL DURATION + PROPOSED DURATION

**What the sources support:** no source located gives a duration in
seconds for the Stretch Display. What they do support:

- It is a **held posture**, not a motion: deep-dive §1.7 describes it as a
  posture sequence (neck up, bill skyward, plumes erected, *then* head
  lowered) — rise, HOLD, lower.
- The stillness axiom governs everything on this device: deep-dive §3.1,
  "≥90% of all displayed frames are a held pose"; movement study §0/§2,
  the bird is "a statue that occasionally explodes," and in the related
  chart work ≥90 % of displayed frames are a held pose.
- The clip's own display core (f10–f112, bill-open through bow nadir) runs
  8.5 s and is mostly slow motion and hold — even the generated clip
  agrees the display is slow.

**Natural duration (AUTHORED estimate, no source number exists):**
~15–25 s for one full display cycle including the rise, a real hold at
the peak, the lowering, and the bow — i.e. the clip's 8.5 s core is the
display played roughly twice too fast and with its peak hold cut short.

**PROPOSED duration: 20.5 s = 246 ticks at 12 fps**, including departure
and return:

| Proposed phase | Ticks | s | Drawn |
|---|---|---|---|
| P0 Home hold (exact locked home frame) | 6 | 0.50 | home drawing, reused |
| P1 Departure: rise + uncoil, deep coil → upright stand | 24 | 2.00 | on 2s |
| P2 Upright stand settle hold | 12 | 1.00 | hold |
| P3 Bill-open beat: open in 3 ticks, then open-bill hold | 24 | 2.00 | 1s open + hold |
| P4 Stretch rise: neck extends, bill → skyward | 24 | 2.00 | on 2s |
| P5 Plume erection (6 ticks) + SKYWARD HOLD | 48 | 4.00 | erection on 2s + hold |
| P6 Lowering: skyward → horizontal | 24 | 2.00 | on 2s |
| P7 Bow: neck arcs forward-down | 24 | 2.00 | on 2s |
| P8 Bow hold (nadir) | 12 | 1.00 | hold |
| P9 Partial lift out of bow → upright stand | 18 | 1.50 | on 2s |
| P10 Return: re-coil onto the exact home frame | 24 | 2.00 | on 2s |
| P11 Home hold (exact locked home frame) | 6 | 0.50 | home drawing, reused |
| **Total** | **246** | **20.50** | |

Pure-hold ticks: 99 / 246 (40 %); every other tick is a slow on-2s
drawing, so no drawing is ever shown for less than 2 ticks except the
3-tick bill-open. Honest note: this is a *display*, the one sequence
where sustained slow motion is the content — it does not meet the idle's
≥90 % pure-hold fraction, and is not claimed to.

---

## 3. KEY POSES

| Pose | Source |
|---|---|
| K0 HOME — deep coil, bird left of frame, feet at 15.2 % / 20.3 % of width, waterline 95.2 % of height | Locked home frame (`gate1-strike/fresh/home_frame_approval.png`); NOT in the clip |
| K1 Upright stand, bill horizontal and closed, tall S-neck | MEASURED — clip f0 (also f9) |
| K2 Bill-open call pose, gape wide, head tipped up ~25° | MEASURED — clip f10 |
| K3 Rising stretch, S straightening, bill ≈45° up | MEASURED — clip f40–f44 |
| K4 Full skyward stretch — neck vertical and fully extended, bill at the sky | MEASURED posture — clip f70 (clip framing crops the bird; the drawn pose must be whole-bird, feet on the home waterline, neck shortened-in-frame only by composition, never cropped) |
| K4p Plumes ERECTED at the skyward peak (two black plumes raised, chest cascade flared) | AUTHORED — deep-dive §1.7 Stretch Display passage (§1H above); not visible in the clip |
| K5 Lowering mid-pose, bill ≈45° and descending | MEASURED — clip f84–f85 |
| K6 Upright recovered, bill horizontal | MEASURED — clip f89–f90 |
| K7 Bow — neck arched forward-down, head below body line, crown plumes flopped forward | MEASURED — clip f100 |
| K8 Bow nadir — head lowest, bill pointing down/back | MEASURED — clip f110 (nadir band f105–f112) |
| K9 Down-forward extension, partial lift — the clip's final pose | MEASURED — clip f119 |
| K10 Return mid-pose — upright stand sinking, neck re-coiling toward the deep S | AUTHORED — structural reverse of K1→K0 departure (§4) |

Locked identity in every pose, no exceptions: white head, black brow into
exactly two long black plumes, yellow ringed eye, dagger bill, slate body,
ONE black shoulder patch, rusty bend-of-wing + thighs, shaggy chest-plume
cascade, long scaly legs. (The clip itself drifts from this — see §7 —
the drifts are clip defects, not poses.)

---

## 4. DEPARTURE / RETURN

**Departure (AUTHORED, P0–P2, 42 ticks):** home hold (6) → the bird
rises out of the deep coil: neck uncoils upward through the intermediate
S, body comes up to full standing height, head arrives at the K1 upright
stand with bill horizontal; plumes and chest cascade settle last
(2 ticks of lag at the end of the rise) → settle hold (12). Feet never
move; rings constant. Structure mirrors the clip in reverse order of
neck states: the clip *starts* at K1, so the departure is authored to
land exactly on K1 as measured at f0/f9.

**Return (AUTHORED, P9–P11, 48 ticks):** from the bow's partial lift
(K9, measured) the neck re-gathers to the K1 upright stand (P9, 18
ticks) → brief upright settle is folded into P9's end → the bird sinks
and re-coils: body lowers, neck folds back down into the deep S, head
descends to the home head position, plumes/cascade settle last →
lands on the **exact locked home frame** (P10's final drawing IS the
home frame) → home hold (6).

The return is choreographed as the departure's beats **reversed in
structure** (stand → sink/re-coil → home, with the same settle-lag
ending) — it is NOT a literal reverse playback: the bow exit (P9) has
no counterpart in the departure, timings differ (18 + 24 vs 24 + 12),
and every return drawing is its own drawing.

---

## 5. SIZE ESTIMATE

Unique drawings (home frame reused, not re-drawn, not counted):

| Phase | Unique |
|---|---|
| P1 Departure rise (24 ticks on 2s) | 12 |
| P2 Upright settle hold | 1 |
| P3 Bill-open (3 ticks on 1s) + open hold | 3 + 1 = 4 |
| P4 Stretch rise (24 ticks on 2s) | 12 |
| P5 Plume erection (6 ticks on 2s) + skyward hold | 3 + 1 = 4 |
| P6 Lowering (24 ticks on 2s) | 12 |
| P7 Bow (24 ticks on 2s) | 12 |
| P8 Bow hold | 1 |
| P9 Lift out of bow (18 ticks on 2s) | 9 |
| P10 Return re-coil (24 ticks on 2s; final frame = home, reused) | 12 |
| **Total new unique drawings** | **79** |

Arithmetic: 79 × 58 KB = **4,582 KB ≈ 4.58 MB** (4.37 MiB).
Hold-heavy as a display should be: 5 of the 10 phases contribute a
single drawing each or are pure holds, and all slow motion is on 2s.

---

## 6. PROVENANCE

- Source: `courtship_attempt1.mp4`
- Clip: `firmware-living-loop/stageb_clips/courtship.mjpeg` —
  6,015,122 B, md5 `669ed179562a0dc3a4dabf17d10a9e38`
  (re-verified by md5sum on this pass; matches STAGE_B_MANIFEST.md).
- Conversion route per STAGE_B_MANIFEST.md: frames extracted at 12 fps
  (every 2nd frame of the 24 fps source), background-normalized toward
  the approved plate's border median (247, 232, 210), then PIL/libjpeg
  `quality=80, subsampling=1, optimize=True` (the 4:2:2 layout the
  ESP32-P4 decoder requires) via `tools/clip_convert_stageb.py`.
  120 frames, 1024×600, verified in the manifest.

---

## 7. CLIP vs SOURCES — what the clip does that the sources don't support (and vice versa)

**Clip inventions / defects — NOT taken:**

1. **Crop / framing violation (worst defect).** The clip's bird grows /
   the framing pans until the bird no longer fits: bill tip exits the
   top ≈f44–f47, and from ≈f48 to ≈f88 the legs, feet, and body bottom
   are out of frame entirely — roughly 41 frames (3.4 s) of the peak
   display are a partial bird. This breaks the architecture's NO CROP /
   whole-bird law and makes feet unverifiable for a third of the clip.
   **Taken instead:** the K4 skyward posture, redrawn whole-bird at
   home scale with feet on the home waterline.
2. **No plume erection.** The display's named signature (deep-dive §1.7)
   never happens; plumes trail passively. **Taken instead:** authored
   erection beat P5/K4p.
3. **No bill-snapping.** One sustained open-bill hold (f10–f34) is a
   call-like pose, not clappering; and bill-clap in the sources is a
   *duet*. **Taken:** the single bill-open beat only, as measured.
4. **Continuous slow morph instead of holds.** Outside phases A and D
   the clip is in near-constant slow motion, against the stillness
   axiom. **Taken instead:** the beats, re-timed into holds + on-2s
   motion (§2).
5. **Identity drift in the generated clip:** plumage renders much darker
   than the locked slate; the eye reads reddish-brown in the skyward
   close frames (f55, f70) instead of the locked yellow ringed eye; a
   black knob protrudes from the shoulder patch in the cropped frames
   (f55, f70, f84). None of this is carried into the spec.
6. **Clip starts and ends wrong for the architecture:** it opens on a
   tall upright stand (not the home deep coil, and the bird sits larger
   and further right than home) and ends mid-display at f119. Departure
   and return are authored (§4) to close both ends on the exact home
   frame.

**Source behaviors the clip does NOT show — correctly absent:**

7. **No spread wings anywhere in the clip — correct.** The Upright
   Spread-Wing display (deep-dive §1.7) is a two-bird territorial event
   ("held a long time while slowly approaching a rival"), banked as a
   heron↔heron seed: "do NOT schedule it solo." The clip shows no wing
   spread, so there is no spread-wing mismatch to flag in the clip
   itself; none is authored into this sequence either.

**The standing mismatch — sources vs this sequence's existence:**

8. **Solo legitimacy.** Deep-dive §1.7 grades the Stretch Display a
   **nest-site / colony behavior** and recommends: "exclude from the
   creek roster; note as colony content if a rookery scene is ever
   built," allowing only that its "plume-erection + bill-skyward
   silhouette is a plausible rare solo echo in breeding season." This
   device sequence is exactly that authored solo echo — theatre, not
   documented solo behavior. It should be scheduled rare and
   breeding-season-weighted (Feb–Apr, per deep-dive §1.8) if scheduled
   at all, and never presented as ethology.

**What was taken from the clip:** the full beat order and spans (§1) —
upright stand → bill-open → stretch rise → skyward hold → lowering →
bow → partial lift — the planted feet, the constant rings, the folded
wings, and every key pose K1–K9 as measured.

---

## 8. CONFIDENCE

**Partial — mostly authored.** The clip's beats, spans, poses, feet, and
bill/neck track are measured frame-by-frame and solid; but the sequence
as a device behavior rests on authored ground: there is no courtship
chart, no source duration for the display, plume erection is absent
from the clip and supplied from text, departure/return are authored,
and the deep-dive itself grades the Stretch Display a colony behavior
it recommends excluding from the solo roster — so the choreography is
measured, the behavior's solo existence is not.
