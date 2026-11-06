# STRIKE SEQUENCE — production plan (fresh build, 2026-11-05)
## Keys (LOCKED, verified)
- K_coil.png — deep S coil, frozen home pose; feet at x~16%/23% of width
- K_peak.png — full extension, bill tip at water x~59.5% (raw; uniform stage registration at assembly scales whole drawings by 0.88 + shifts -3% x so the touch lands at 50.0% — applied IDENTICALLY to every frame, never cutting into the bird)
- E_500.png — extension halfway (head rides ~8% right of true midpoint; noted, acceptable)
- W_500.png — withdrawal halfway (droplets + spreading ripple, PASS)
## Method (edit-anchored breakdown recursion)
- Every new pose = an EDIT of the NEARER verified neighbor as canvas, with the FAR neighbor as the target reference. Prompt: "Edit the canvas: move the pose halfway toward the target. Change ONLY the neck/head (and the water state described). Keep body, wing, chest frill, LEGS, FEET, feet rings, framing and paper EXACTLY as the canvas — line for line." Never generate a fresh whole drawing for a step; never do pixel surgery/grafts over the bird.
- Water: extension = feet rings only (no touch rings until the peak). Withdrawal fraction f (0=peak, 1=coil): f0-0.1 droplets falling, tight strong rings; 0.1-0.3 rings spreading, clear; 0.3-0.6 wide, medium-faint; 0.6-0.85 widest, faint; 0.85-1 ghost, nearly calm; f=1 calm. Feet rings constant everywhere.
- Identity anchors on every call: prof_d.png (species photo), heron_pencil_verified_20261105-1201.png (approved drawing, tone). Reference paths: /home/hatch/workspace/heron/gate1-strike/corrected/
- Gate each frame by VIEWING it: pose halfway between its neighbors (head position!), legs/feet/frill identical to canvas, water state right for its fraction, no color, no text, no scenery, no splash. A frame that fails twice with the same defect: report it, use the closest honest pose, move on.
- Naming: extension E_<fraction*1000>.png (E_500 done), withdrawal W_<fraction*1000>.png (W_500 done). Fractions: extension in 16ths of coil->peak; withdrawal in 32nds of peak->coil.
- Output dir for ALL new poses: /home/hatch/workspace/heron/gate1-strike/fresh/poses/
## Timeline (60 ticks @ 12 fps = 5.0 s)
- t0-9 coil freeze (K_coil) | t10-14 extension (E_125,E_3125,E_5625,E_8125,K_peak) | t15-16 peak hold | t17-42 withdrawal (26 ticks, fractions 2..31/32 + 64ths in the settle) | t43-59 settle (17 ticks, last tick = K_coil exactly)
- Unique drawings in the cut: ~47 (coil + 4 ext + peak + ~25 wd + ~16 settle). The full library built is larger (alternates).
## Assembly (coordinator, later)
- Tone-normalize paper to the approved drawing; uniform stage registration (0.88 scale, -3% x) for touch-at-center; timing.json; device MJPEG (PIL q82 subsampling=1, SOF luma 0x21); previews; leg-band + water proofs.

## RULE AMENDMENT (Jimmy, 2026-11-05 13:17) — recorded, no change to this build
- The legs-planted rule applies ONLY within Sequence 1 (this strike). Later sequences may move their legs as their action requires.
- BUT every sequence in the set must START with the legs in the same position as Sequence 1's start.
- => K_coil.png is the CANONICAL HOME STANCE anchor for the whole set: the opening drawing of Sequence 1, from which every future sequence's first frame must take its stance. Home stance description: bird in the left third facing right; two scaly legs vertical-ish, ankle joints at mid-leg; front foot at x~16% of frame width, rear foot at x~23%, both at the waterline near the bottom edge (feet y~95-97% of frame height), small ripple rings at each foot; deep-S coil above.

## RULE AMENDMENT 2 (Jimmy, 2026-11-05 13:18) — recorded, this build already complies
- EVERY sequence in the set starts AND ends on the SAME frame — THE HOME FRAME = Sequence 1's opening drawing, K_coil.png (the whole bird: stance, position, pose).
- This strike already ends on its exact starting drawing (final tick = K_coil), so: compliant, no change.
- For future sequences: mid-sequence content is free (legs may move in non-strike sequences) but must always resolve back to the home frame.

## Production log — extension eighths (2026-11-05)
- E_125 PASS (worker). E_875 PASS via coordinator absolute-landmark rescue (reads ~f0.90; bill closed, gap above water, no rings).
- E_375 FAILED both methods (halfway asks snapped to neighbors; landmark rescue dipped off-path). E_625 FAILED both methods (canvas clone, then E_750 clone). Per two-fail rule: NOT regenerated. SUBSTITUTION: the extension timeline runs on the verified grid {E_125, E_250, E_500, E_750, E_875, peak} — 6 extension ticks (t10-15), peak beat 2 ticks total (t15-16), spacing .125/.25/.5/.75/.875/1.0 (accelerating — physically right for a strike).
- W_250: worker version sat at ~f0.40 with an over-wide ripple; coordinator retry (long spear, first kink, tight ripple, droplets) verified at ~f0.25-0.30 and REPLACED it; worker version kept as W_250_alt.png.
- LESSON (workers + coordinator agree): on small head-travel intervals the edit model reads "halfway" as binary — first attempts clone the canvas, corrected retries clone the target. Mitigation: fewer, larger steps per interval + absolute landmarks; the timing map absorbs the rest.

## Production log — assembly (2026-11-05, coordinator)
- Library final: 28 unique drawings (see REPORT.md). Extension complete on the verified grid; withdrawal = anchors at honest fractions + chained micro-steps (G2/G3/G5/G7 complete, G7 extended by coordinator steps 5-6; G1 impossible — binary bill-in/out; G6 absorbed as a hold).
- Assembly: paper normalized to the APPROVED drawing (244,242,238); uniform registration scale 0.88 / offset (-61,+127) px, feathered; device stream 1,634,382 bytes, SOF luma 0x21 verified; timing.json 60 ticks; previews + proofs built and VIEWED by the coordinator (leg band aligned on all 28 rows; water strip monotonic; marsh strip reads as one drawing, touch at ~49-50%).
