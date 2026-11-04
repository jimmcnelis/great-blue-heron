# Heron v1.3 — r3 report (swallow fix + leanness, on Jimmy's r2 verdicts)

**Jimmy's r2 rulings, all three executed:** style = **Naturalist** (Storybook stays a working alternate pack, not re-rendered this round); "when it swallows the fish its neck should be straight and upward"; "he's a little too fat… maybe just leaner and not longer" — girth only, length untouched, plus leaner legs.

**Deliverables**
- Test episode, Naturalist only (1024×600, 24 fps, 26.0 s, 624 frames): [preview_heron_v1_3_naturalist_r3.mp4](sandbox://workspace/heron/preview_heron_v1_3_naturalist_r3.mp4) — md5 `ee55d1f356b72a3a1d7ad2d247e8d5f6`
- Model sheet: [model_sheet_v1_3_r3.png](sandbox://workspace/heron/model_sheet_v1_3_r3.png) — md5 `e3d945b7563596e85a2ce03f96d008c1` (rest / coil / front / flight at the new proportions, rear-up + straight-neck swallow panels, silhouette strip)
- Swallow strips: `v1_3_swallow_strip_r3.jpg` (8 labelled full frames, re-catch → done) and `v1_3_swallow_crops_r3.jpg` (native-res neck crops, bulge_pos 0.08 → 0.80). Episode strip: `v1_3_strip_naturalist_r3.jpg`. Audits: `src13/qa13_r3.json`. Code: `src13/cycles13_r3.py` (new), `src13/episode13_r3.py`, `src13/sheet13_r3.py`; `rig13.py` edited (girth + legs). `cycles13.py` untouched — it remains the r2 performance record.

## 1. The swallow — neck straight and upward

The r2 swallow played on the re-catch pose (head back, neck still S-curved over a 13.5 u chord leaning 32.7° off vertical). The study says what the bird does (§6, phases 5–6): head back, **neck straightens toward vertical**, bulge travels down the straightened neck. Jimmy's ruling is the same sentence. The rework, frames 390–447 only:

- **390–401 — the rear-up (new):** the bird lifts out of the re-catch crouch into an authored UPRIGHT pose — body tilt back to statue's 16°, coil 0.7 → 0.03, head anchor solved numerically to sit 0.4 u ahead of the breast anchor on a 25.0 u chord, head pitch −16° → +2°. The fish stays gripped head-first through the whole lift. The straightening is the motion, not a cut.
- **402–431 — the swallow proper:** r2's bulge profile unchanged (pos 0.05 → 0.92, amp peak 0.9, gape pulses kept), now descending the vertical column; head pitch carries only a ±1.2° working tremor.
- **432–447 — settle:** 16 frames back to the statue. **Borrowed, stated plainly: r2's settle had 24 frames; 8 of them paid for the rear-up.** Everything outside 390–447 is pose-identical to r2 — audited by direct dict comparison, **zero frames differ** outside the window; ink events identical; toss still 8 frames airborne.

**Measured straightness** (neck spine vs the breast→head chord, pose geometry):
- Bulge window 402–431: chord **0.94° from vertical** (max = mean; the column does not sway), max spine deviation from the chord **0.48 u = 3.2 px** at master res.
- r2 equivalents: **32.67°** and **4.72 u = 31.5 px**. The old swallow's neck leaned a third of the way to horizontal with a deep S; the new one is a column with a 3-pixel bow.

**Rendered bulge descent** (not pose data — measured off the shipped frames): the bulge's shadow slice, isolated by excess-mask against the identical upright pose at amp 0 (f430), is present f403–f427 and its centroid travels **row 233 → row 298, ≈65 px down the neck** at full frame, peaking at ~2,300 excess px mid-descent. In the crop strip the traveling band + local swell reads at f409 → f415 → f421 → f427 without magnification tricks.

## 2. Torso — leaner, NOT longer

One constant in `body_xform`: local girth axis × **0.88** about the hip pivot (profile/three-quarter: local Y; front stop: local X, where girth reads as width). Because every body-space drawing — torso loop, wing scallops, shoulder patch, breast anchor, hips, front panels — passes through that one transform, everything stays seated; nothing was re-authored per-part.

| measure (profile rest, torso loop PCA) | r2 | r3 | Δ |
|---|---|---|---|
| length | 35.58 u | 35.58 u | **0 — untouched, exactly** |
| girth | 18.55 u | 16.33 u | **−12.0%** |
| length : girth | 1.918 | 2.179 | +13.6% — **flagged, see below** |

**The flag Jimmy asked for:** the ratio moved +13.6%, purely as arithmetic — same length over a 12%-slimmer height. If the bird now reads too *long*, it's this number talking, not a length change; the correction back is a one-constant nudge (0.90–0.92) whenever he says so.

Front stop: torso loop width 14.40 u (96 px) → 12.69 u (85 px), the same −12%. But the front *silhouette* bounding box only moved 118 → 114 px — because the widest things in the front view are the head plumes, which are head-local and were not scaled. The torso is slimmer; the front read stays plume-bound until the antennae nit (r2's top front-view debt, unchanged) is fixed.

## 3. Legs — leaner everywhere

Thigh widths 3.6/2.1 → 2.9/1.65 u; shank half-widths 0.62/0.40 → 0.47/0.30 u; joint disc 0.95 → 0.72 u; flight trailing segments thinned ~20% the same way. Leg *lengths* untouched (IK l1/l2 unchanged). Measured on the rest silhouette at master res, near leg, same scan rows both rounds:

| scan row | r2 | r3 | Δ |
|---|---|---|---|
| y=62 u (lower thigh) | 17 px | 14 px | −18% |
| y=68 u (shank) | 15 px | 12 px | −20% |
| y=71 u (shank, near waterline) | 9 px | 7 px | −22% |

Standing proportions (unchanged by this round, reported for the record): hip→foot 38.4 u against 72.8 u standing height in the coiled rest pose — the length budget was already lanky; what read "fat" was thickness, and thickness is what moved. In the sheet's flight panel the trailing legs are now two fine lines instead of r2's tapered bars.

## Audits (qa13_r3.json)

Pose identity outside the swallow window: **0 frames differ**. Held fractions 0.618 opening / 0.571 closing — identical to r2. Strike audits identical (loaded-hold tip path 0.14, release peak 19.05, contact tip [83.9, 87.3]). Ink at rest f60: 75 px, identical to r2 — all of it the bird's own eye/brow; the water is blank, as required.

## Blunt residuals

- **The bulge in a single frozen frame still reads as a traveling band + local swell, not a fat lump.** In motion, and stepping the crop strip, the descent is unmistakable (and now measured at ~65 px of travel). If Jimmy wants it to punch in a still, the next lever is contrast, not size — same conclusion as r2, now on a straight neck.
- **The straight neck is a solved pose, not a rig verb.** UPRIGHT is one authored pose (coil 0.03 + head anchor over the breast). The canon's other swallow (tiny fish) must reuse this pose or re-solve the anchor; noted here so it isn't rediscovered the hard way.
- **The settle is brisker** (16 vs 24 frames) — the price of the rear-up, disclosed above. In the strip it reads fine; at speed it's Jimmy's call.
- **Front view:** the plume antennae remain the widest thing on the bird and now the *only* thing keeping the front read wide. Still the top front-view nit, untouched this round.
- Flight remains a shape without a beat cycle; held fractions, toss timing (8 f airborne vs the measured ~5), and the wading strike's grounding are unchanged from r2's ledger. No canon work was done this round, per the brief.

**Verification statement:** every number above comes from my own runs this round — before/after proportion measurements on the same code path, the pose-identity diff, per-frame spine geometry, the excess-mask descent measured off the shipped PNG frames, and my own pulls of the swallow strip, the native-res crops, and the model sheet. The one thing I still cannot do from here is watch it play at speed; the motion judgment is Jimmy's.
