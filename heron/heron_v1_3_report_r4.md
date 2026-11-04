# Heron v1.3 — Round 4 report (Naturalist)

**Deliverables** (all in `~/workspace/heron/`):
- `preview_heron_v1_3_naturalist_r4.mp4` — full episode, 1024×600, 624 f, 26.0 s, md5 `d1c4e9b5056106cecfb3c0c0e8dc96a0`
- `v1_3_swallow_strip_r4.jpg` / `v1_3_swallow_crops_r4.jpg` — the swallow, full frames + native-res neck crops
- `v1_3_feather_crops_r4.jpg` — r3-vs-r4 before/after crops (belly hem + tail, wing + beard + head, swallow neck, flight wing)
- `model_sheet_v1_3_r4.png` — the six-pose sheet in the new hand
- `src13/qa13_r4.json` — full audit numbers
- Sources: `src13/rig13_r4.py`, `cycles13_r4.py`, `episode13_r4.py`, `sheet13_r4.py` (workspace + mirrored to Spark `~/heron/src13/`)

## Direction change (ledger honesty)

This round's art pass follows Jimmy's 2026-11-02 21:14 refinement — "more like a
fine art drawing, less like cartoon" and "turn that dial." The drawn surface was
pushed to the **naturalist-plate end**: fine hatched tonal modeling over flat
fills, observed slightly-irregular contours, feather groups rendered as layered
individual feathers with barb suggestion. This refines the earlier "cartoonist
drew it" end-state ruling for the SURFACE only; animation/timing craft
(signature cycles, holds, anticipation) is untouched — every pose, timing, and
choreography element is frozen from r3 (audit below).

## 1. The swallow bulge — "a fish, not a ball"

**Rig change** (`rig13_r4.draw_neck` + `cycles13_r4`): the spherical Gaussian
widening (peak width multiplier 2.44×, σ 0.22) is replaced by a traveling
**fish profile**: asymmetric along the neck — a blunt head end (the leading,
downhill end) and a long tapering tail — with the peak width multiplier cut to
**1.76×** and the travel amplitude trimmed 0.9 → 0.8 in `bulge_amp`. The bulge
path, gape pulses, head tremor, and the solved UPRIGHT neck are untouched.

**Measured on the renders** (identical method both versions: per-row neck-run
width excess vs the version's own f430 post-swallow baseline, neck box
x 400–590, rows 170–325, head and breast excluded; peak frame is f415 in both):

| | r3 | r4 |
|---|---|---|
| Excess width across neck at peak | **47 px** | **22 px** |
| Swelling length along neck (rows ≥ 6 px excess) | 155 px | 140 px |
| Excess area (sum of width excess) | 4,715 | 1,891 (−60%) |
| Across : along ratio | 0.30 | **0.16** |
| Travel (centroid, strong frames) | 73.3 px (f407–422) | 95.9 px (f404–421) |

The lump is less than half as wide across the neck, carries 60% less total
swelling, and is twice as elongated proportionally — a slug sliding down the
gullet, not a ball. It still travels the full neck (both methods and the crops
agree the descent spans the column; the travel figures differ because the new
profile's mass weighting starts higher — reported as measured, not rounded to
a story). See `v1_3_swallow_crops_r4.jpg`: at f415 the r4 neck shows a slim
elongated thickening where r3 showed a round swelling.

## 2. Plumage rework — the triangles are gone

The old "⚠ strand" primitive (a straight tapered triangle) drew every fringe.
It is replaced system-wide by a **feather primitive**: a curved shaft, a vane
whose width profile swells mid-feather and closes to a soft rounded tip,
optional barb ticks, and deterministic per-feather jitter in length, width,
angle, and bend. A `fringe()` row builder overlaps feathers so hems read as a
feather bed, and an `embed` parameter pulls feather bases inside the body mass
so only rounded tips break the edge line. Audit of every fringe the rig draws:

- **Belly hem** (the named complaint): 41 overlapping feathers, bases embedded
  1.5 u inside the belly, tips forming a fine ragged edge. Before/after in
  `v1_3_feather_crops_r4.jpg` panel 1 — r3's row of triangles vs r4's hem.
- **Breast beard — RESTORED**: the great blue heron's shaggy breast plumes now
  hang in three layered rows of individual feathers (dark back layer, pale
  front layer with shafts and barbs), lengths irregular 5.5–14 u. Panel 2.
- **Tail fan**: six real feathers, staggered lengths, merged into the rear
  silhouette (anchors pulled inside the torso).
- **Wing coverts**: the flat scallop "petals" are now four rows of individual
  covert feathers in graded tones with tone-matched shafts/barbs; the black
  shoulder patch ends in feather tips instead of a hard polygon edge.
- **Neck hackles**: modeled with two fine throat lines and dense short nape
  hatching instead of flat tube shading.
- **Head plumes**: the occipital plumes are three narrow individual feathers;
  four fine skull modeling strokes added.
- **Front view (yaw 90)**: the breast column hem and belly skirt are feather
  fringes, not strand triangles.
- **Flight**: covert rows on the raised wing are feathers; the belly fringe
  and tail fan use the same system.

## 3. General art pass — the dial turned

- **Torso tonal modeling** (new): a lit band under the back edge, a pale
  breast patch, and a hatched shadow mass along the belly, modeled like a
  drawing — light and shadow, not cel bands. The torso is no longer a flat
  slate oval with a scallop decal.
- **Contours**: torso and wing outlines now carry a slight observed
  irregularity (`_rough`, deterministic, sub-unit amplitude) instead of
  perfect machine curves.
- **Legs**: thighs are smooth tapered forms (interpolated half-widths, front
  edge fuller than back) instead of straight quads, with three rows of
  scallop scale ticks on the thigh.
- Everything else (bill, eye, fish, ink) is unchanged — the ink language was
  already the plate's language.

**Process note, disclosed because it cost real time:** the first torso-modeling
implementation pasted its overlay wholesale inside the torso mask from a
white-based canvas, which silently erased a strip of the torso and made the
new belly fringe look detached. Found by layer ablation, fixed by seeding the
overlay from the body canvas. The shipped renders do not have the defect; the
fix is commented in `draw_torso_modeling`.

## Frozen-contract audit (qa13_r4.json)

- **Pose-parameter diffs vs r3 outside frames 390–447: ZERO** (empty list).
  Inside the window, 29 frames differ — exactly the bulge-amplitude frames.
- Pose diffs vs the phase-1 cycles outside the window: also zero.
- UPRIGHT neck: chord **0.94°** from vertical, max spine deviation 0.48 u —
  the r3 solution intact.
- Held fractions unchanged: opening statue **0.618**, closing statue **0.571**.
- Fish airborne frames: **8** (the toss untouched). Strike contact identical.
- GIRTH = 0.88 and torso length untouched; leaner legs untouched (the leg
  change is surface only — same hip/foot/knee geometry).
- **Ink at rest (f60): 74 pure-ink px vs r3's 75.** One pixel, explained: the
  differing mask pixels sit at x 347–348, y 233–240 — the edge of a ripple
  ring beside the redrawn tail fan, where the art change flipped one
  majority-downsample cell adjacent to the ring. The ink events themselves
  are untouched (9 events, same frames, same shapes); this is a resampling
  artifact of the art change, not an ink change. Flagged rather than hidden.

## Honest residuals

1. The swallow neck still shows faint horizontal banding from the bulge's
   shadow-slice rendering (visible in the f415 crop) — much reduced with the
   slimmer profile, not eliminated.
2. In flight, the belly fringe reads as small scallop dots at glancing
   angles; acceptable at episode scale, worth a look in the sheet's flight
   panel.
3. Front view: the occipital plumes stick out sideways like antennae — the
   geometry is inherited from r3; real feathers made it slightly more
   visible, not less.
4. The bulge's along-neck length at the ≥6 px threshold measures about the
   same as r3 (140 vs 155 px) — the win is across and total swelling, as
   tabled. Judging by the crops, the shape change is clear.

## STOP

Canon build remains gated. Awaiting Jimmy's verdict on: the slimmer fish
bulge, the feather system (belly hem + restored beard above all), and the
fine-art dial position.
