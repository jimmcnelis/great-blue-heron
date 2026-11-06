# FLIGHT — choreography spec (measurement only, no drawing)

Sequence: takeoff → flight → landing back home. Playback 12 fps throughout
(1 tick = 1/12 s). Every sequence starts and ends on the exact locked home
frame (`gate1-strike/fresh/home_frame_approval.png`: deep coil, left of
frame, feet at 15.2% / 20.3% of width, waterline 95.2% of height).
Whole bird in frame in every pose, scale never changes, no crop, ever.

Sources: clip frames viewed in `/tmp/choreo_flight/` (strips
`strip_all / strip_0_39 / strip_40_79 / strip_80_119 / strip_takeoff /
strip_landing`); timing truth `heron-movement-study.md` §7 and
`movement-charts.yaml` (`takeoff`, `flight_cycle`, `glide`, `landing`).
Chart frames are at 24 fps — halved below to 12 fps ticks; seconds unchanged.
Where clip and studies disagree, STUDIES WIN and the disagreement is
flagged in §7.

---

## 1. BEAT SHEET

### 1a. What the clip actually does (MEASURED, clip frames 0–119, 12 fps)

| # | Phase (measured) | Clip frames | Seconds | Evidence |
|---|---|---|---|---|
| M1 | Standing prelude, upright alert (NOT home coil, NOT in any chart) | f0–23 | 0.00–1.92 | Upright S-neck, head high, both feet planted; ripples appear under feet from ~f6. Near-still — trim, do not use. |
| M2 | Crouch + neck extension, stepping in place | f24–43 | 2.00–3.58 | Body lowers/pitches forward f24–31; neck extends progressively to fully straight, horizontal, by ~f36–40; legs step/crouch throughout; wings still folded. |
| M3 | Wing unfold + raise (feet still planted) | f44–50 | 3.67–4.17 | Wings lift from folded f44–45 to fully raised, spread high f46–50. |
| M4 | First downstroke + liftoff | f51–54 | 4.25–4.50 | Downstroke f51–53 with feet still on the water; feet leave at ~f53–54. Downstroke-before-liftoff coupling is CORRECT (chart gate). |
| M5 | Airborne, rising — bird exits frame top/right | f55–82 | 4.58–6.83 | Beat 2 f55–59 (up f55, down f57–59). From f56 and through f60–79 the bird is CROPPED — only legs / wingtips / lower body at the top edge. Legs dangle bent the whole time; they never trail straight. Visible wing-down extremes ≈ f58, ~f66–68 (partial), f79–80 → ≈4 airborne beats in 2.92 s ≈ 1.4 Hz (±1 beat, cropped — PARTIAL). |
| M6 | Re-entry + descent | f80–85 | 6.67–7.08 | Bird re-enters from top fully by f82–83, descending, neck already folding to S, legs dangling down. |
| M7 | Flare / braking | f84–89 | 7.00–7.42 | Wings high, spread, held as a brake f84–88; tail spread; legs dangle then reach down/forward f86–89. |
| M8 | Touchdown | ~f89 | 7.42 | Feet plant, legs bent absorbing. NO water, NO ripples at touchdown in the clip (feet on blank ground) — home version must plant in the water at the home marks with ripples. |
| M9 | Wing fold (overlaps steps) | f90–99 | 7.50–8.25 | Wings fold progressively, complete ~f99–100 — ≈10 ticks after touchdown. |
| M10 | Momentum steps | f96–111 | 8.00–9.25 | Two walking step cycles, wings folded, killing forward momentum. Overlaps M9, as the chart intends. |
| M11 | Settle — upright, NOT home | f112–119 | 9.33–9.92 | Stands upright, head high, one-leg-weighted stance, centre-frame (~45% W); ripples reappear only ~f116. Does NOT resolve to the home deep coil or the home spot. |

Clip event span (crouch f24 → settle end f119) = 96 ticks = 8.0 s, of which
the first 2.0 s is an uncharted standing prelude and the airborne middle
(f56–79) is unusable as drawn (cropped).

### 1b. Chart timing converted to 12 fps ticks (CHART)

| Chart | Phase | @24 fps | @12 fps ticks | Seconds |
|---|---|---|---|---|
| takeoff | crouch_deepen | 12 | 6 | 0.50 |
| takeoff | leap_first_beat (downstroke begins feet-planted f1–4@24; legs leave ~f5@24; neck EXTENDS straight) | 12 | 6 | 0.50 |
| takeoff | dangle_and_fold (legs dangle, then swing to trail; neck folds to flight S as the SECOND beat) | 30 | 15 | 1.25 |
| takeoff | climb_beats (3.5 beats, deep amplitude, envelope 1.0/1.0/0.9/0.8) | 42 | 21 | 1.75 |
| **takeoff total** | | **96** | **48** | **4.00** |
| flight_cycle | 1 beat: downstroke 5f / upstroke 7f @24 — NOT a sine; wingtip lags root 2f@24 (= 1 tick) | 12 | 6 | 0.50 (2.0 Hz) |
| glide | wings locked in shallow dihedral, held loop | 24 | 12 | 1.00 |
| landing | approach_glide | 24 | 12 | 1.00 |
| landing | flare (one braking stroke, wings high + held, tail fans) | 12 | 6 | 0.50 |
| landing | legs_reach (dangle FIRST f1–8@24, then reach forward) | 18 | 9 | 0.75 |
| landing | touchdown (compress +0.8, rebound −0.4, rest, @ chart units) | 12 | 6 | 0.50 |
| landing | momentum_steps (two step cycles; ripples on each plant) | 24 | 12 | 1.00 |
| landing | fold_and_unfold (fold finishes ≥10f@24 = 5 ticks after touchdown; neck unfolds to hunting coil only AFTER feet planted) | 30 | 15 | 1.25 |
| **landing total** | | **120** | **60** | **5.00** |

Note on the 5/7 beat at 12 fps: one 6-tick cycle cannot hold 2.5/3.5
ticks. Preserve the ratio over a TWO-beat pair (12 ticks): beat A =
down 3 / up 3, beat B = down 2 / up 4 → pair totals down 5 / up 7,
exactly the chart ratio at exactly 2.0 Hz. All cruise/climb beats are
scheduled in pairs.

### 1c. Proposed sequence beat sheet (the deliverable timeline)

Rows: CHART = from charts; AUTHORED = written for this spec (marked);
MEASURED = clip timing used as supporting evidence only.

| # | Phase | Source | Ticks @12 | Seconds | Cumulative |
|---|---|---|---|---|---|
| 1 | Home hold (exact home frame, held) | AUTHORED (architecture: start on home) | 6 | 0.50 | 0.50 |
| 2 | crouch_deepen | CHART | 6 | 0.50 | 1.00 |
| 3 | leap_first_beat — downstroke starts feet-planted; feet leave tick ~3 of the phase; neck extends straight | CHART (clip M4 agrees on coupling) | 6 | 0.50 | 1.50 |
| 4 | dangle_and_fold — legs dangle ticks 1–7, swing back to trail ticks 8–15; neck folds to flight S across the phase (second beat) | CHART | 15 | 1.25 | 2.75 |
| 5 | climb_beats — 3.5 beats in pairs (see 1b note), deep amplitude, rising path §4 | CHART | 21 | 1.75 | 4.50 |
| 6 | Cruise flight_cycle × 4 beats (2 pairs) at apex, legs trailing straight beyond tail | CHART | 24 | 2.00 | 6.50 |
| 7 | Glide ×1, wings locked shallow dihedral, at apex | CHART | 12 | 1.00 | 7.50 |
| 8 | approach_glide (landing) — descending return arc to above the home spot | CHART + AUTHORED path (§4) | 12 | 1.00 | 8.50 |
| 9 | flare — one braking stroke, wings high and held, tail fanned | CHART (clip M7 agrees in shape) | 6 | 0.50 | 9.00 |
| 10 | legs_reach — dangle first (ticks 1–4), then reach forward (ticks 5–9) | CHART | 9 | 0.75 | 9.75 |
| 11 | touchdown — feet plant IN the water exactly short of the home marks; compress/rebound; splash ripples fire | CHART | 6 | 0.50 | 10.25 |
| 12 | momentum_steps — two step cycles; the second plant lands the feet exactly ON the home marks (15.2% / 20.3% W) | CHART + AUTHORED targeting | 12 | 1.00 | 11.25 |
| 13 | fold_and_unfold — wing fold completes no earlier than tick 5 of this phase's reference (≥5 ticks after touchdown — it completes during steps/fold phase, as in clip M9); neck unfolds S → hunting coil after feet planted | CHART | 15 | 1.25 | 12.50 |
| 14 | Settle to home — neck deepens from hunting coil (coil 0.85) into the exact home deep coil, head lowers to home position, final micro-step alignment if needed; last tick = exact home frame | AUTHORED (clip ends upright — M11 — so this resolve does not exist in the clip) | 12 | 1.00 | 13.50 |
| 15 | Home hold (exact home frame, held) | AUTHORED | 6 | 0.50 | 14.00 |
| | **TOTAL** | | **168** | **14.00** | |

---

## 2. NATURAL DURATION vs PROPOSED

- **Natural (studies):** takeoff 4.00 s + landing 5.00 s = **9.00 s**
  core, takeoff-to-settled, with zero cruise between climb and approach.
  Cruise is a scheduler variable in the studies (flight_cycle loops,
  glide inserted on crossings > 3 s) — there is no fixed natural cruise
  length. With the minimum sensible cruise (1 beat pair, 1.0 s) the
  natural span is ≈ 10.0 s.
- **Clip's own span:** 8.0 s of event (f24–119) inside a 10.0 s encode
  padded with a 2.0 s standing prelude — and it never reaches home, so
  it is not a complete natural performance of this sequence.
- **PROPOSED: 14.00 s = 168 ticks @ 12 fps** — takeoff 48 + cruise
  24 (4 beats) + glide 12 + landing 60 + authored settle-to-home 12 +
  home bookend holds 12. Longer than natural because it buys a readable
  apex (cruise + glide), the return arc, and the mandatory exact-home
  resolve the clip lacks.

---

## 3. KEY POSES (named; source = clip frame or chart phase)

1. **Home / deep coil** — locked approval frame (feet 15.2%/20.3% W,
   waterline 95.2% H). Bookends only; not in the clip.
2. **Crouch** — chart `takeoff.crouch_deepen`; clip equivalent f24–31
   (body lowered, pitched forward, wings folded).
3. **Leap / extended-neck liftoff** — chart `leap_first_beat` (neck
   straight, downstroke begun, feet just leaving); clip f51–54.
4. **Wings-raised extreme** — clip f47–50 (wings high, spread, feet
   planted); chart: top of first beat.
5. **Dangle** — chart `dangle_and_fold` ticks 1–7 (legs hanging below
   body, toes down); clip f55–61 (legs dangle, before cropping wins).
6. **Fold-S downstroke extreme** — chart `flight_cycle` downstroke end
   (flap −52, tip lagging 1 tick @12); clip nearest: f58, f79–80
   (partial, cropped).
7. **Fold-S upstroke extreme** — chart `flight_cycle` upstroke end
   (flap +34, wing slightly folded at top); clip nearest: f55 (neck
   still extended — use chart, not clip, for the neck).
8. **Trail** — chart `flight_cycle.fixed_pose` (legs straight back
   beyond the tail, neck tight S, head at shoulders). NOT in the clip
   anywhere — clip legs dangle bent throughout.
9. **Glide** — chart `glide` (flap +12 shallow dihedral, held).
   Not identifi
...[truncated 6151 chars]