# DENSIFY PASS — STATUS AT HOLD (2026-11-05, ~13:45)

**HOLD ruling (Jimmy, 13:43): "no dont crop. redo the first frame for my approval before doing more animation sequences."**
No reassembly was started or finalized. timing.json, strike_device_1024x600.mjpeg, both previews, and registered/ remain exactly as delivered. The color-redraw amendment is SUPERSEDED — the colorized, whole-bird home frame is a separate approval piece, NOT part of this pass.

## Stage reached: measurement / groundwork only
No in-between drawings have been generated yet (zero intervals attempted, zero attempts wasted). The generation crew was never dispatched — the hold landed during groundwork. What is banked:

### 1. Bill-tip anchor table (visual grounding, 0–1000 normalized, raw poses)
| drawing | tip (x,y) | drawing | tip (x,y) |
|---|---|---|---|
| K_peak | (596, 954) | W_g5_2 | (571, 784) |
| W_125 | (602, 810) | W_g5_3 | (554, 830) |
| W_250 | (598, 823) | W_625 | (449, 823) |
| W_g2_1 | (603, 797) | W_750 | (447, 820) |
| W_g2_2 | (601, 761) | W_875 | (562, 696) |
| W_250_alt | (602, 760) | W_g7_1 | (555, 775) |
| W_g3_1 | (600, 715) | W_g7_2 | (556, 807) |
| W_g3_2 | (595, 716) | W_g7_3 | (553, 796) |
| W_500 | (596, 734) | W_g7_4 | (551, 822) |
| W_375 | (604, 672) | W_g7_5 | (550, 824) |
| W_g5_1 | (587, 766) | W_g7_6 | (550, 823) |
| K_coil (home, raw) | (472, 848) | | |

### 2. Interval work plan (all REMAINING — none attempted)
Attempts planned (Δ = bill-tip distance between anchors, 0–1000 units):
- X0 peak→W_125 (Δ144) — peak-exit, ≤2 attempts per the original order
- X1 W_250→W_g2_1 (Δ27) · X2 W_g2_1→W_g2_2 (Δ36) · X4 W_250_alt→W_g3_1 (Δ45)
- X6 W_g3_2→W_500 (Δ18) · X7 W_500→W_375 (Δ63) · X8 W_375→W_g5_1 (Δ96)
- X9 W_g5_1→W_g5_2 (Δ24) · X10 W_g5_2→W_g5_3 (Δ49) · X11 W_g5_3→W_625 (Δ105)
- X13a/X13b W_750→W_875 (Δ167 — largest jump in the chain; two in-betweens at the thirds, per the even-spacing amendment)
- X14 W_875→W_g7_1 (Δ79) · X15 W_g7_1→W_g7_2 (Δ32) · X16 W_g7_2→W_g7_3 (Δ11) · X17 W_g7_3→W_g7_4 (Δ26)
- X20 W_g7_6→home (Δ82) — target reference becomes the NEW approved home frame when it lands (geometry to be re-measured from it)

Skipped as sub-noise (tips within ~5 units AND poses near-identical on viewing; an in-between there is unmeasurable by the anti-clone gate):
W_g2_2→W_250_alt (Δ1.4) · W_g3_1→W_g3_2 (Δ5.1) · W_625→W_750 (Δ3.6 — a near-identical deep-tuck hold) · W_g7_4→W_g7_5 (Δ2.2) · W_g7_5→W_g7_6 (Δ1.4)

### 3. Findings banked for the resumption
- **The crop is the assembly transform, not the drawings.** The delivered registration (scale 0.88, offset −61/+127 px) was re-derived independently from two grounded point pairs on W_500 (raw vs registered: solved scale 0.885 x / 0.865 y, offsets −62/+124–128 — the logged transform confirmed). It scales the bird down and shifts it, pushing the tail/body to the frame edge in the registered cut. All raw poses in poses/ are full-frame and uncropped, so every densified in-between (raw-canvas edits) survives whatever new registration the approved home frame dictates.
- **W_750→W_875 is the smoothness problem interval** (Δ167 tip travel, incl. the head rising out of the deep tuck); W_625/W_750 are a near-static tucked hold (viewed: same question-mark fold, yellow eye + warm bill present in both).
- **Color register (viewed, for the record):** K_coil's bill and eye read pale/washed next to W_500, W_625, W_750, W_875, where the yellow ringed eye and warm orange bill are clearly present — consistent with Jimmy's "the beginning frame has no color." The fix belongs to the separate home-frame approval piece.
- Paper normalization + registration replication was validated against registered/W_500.png (bird placement matches; margins differ only in paper grain) — the pipeline is ready to re-run under a new registration when the approved home frame lands.

## On resumption (when Jimmy approves the new home frame)
1. Re-measure the new home frame's tip + feet; rebuild X20's target from it.
2. Dispatch the interval plan above (nearer-neighbor edit chains + numeric water forcing, anti-clone gate on measured tips).
3. Reassemble under the NEW registration (whole bird in frame) with the approved home frame as first/last drawing; per-tick bill-tip delta table for withdrawal/settle per the even-spacing amendment.
