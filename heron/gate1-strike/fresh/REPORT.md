# SEQUENCE 1 — THE STRIKE (fresh build, 2026-11-05)
## THE HOME FRAME
**K_coil.png is THE HOME FRAME for the entire sequence set** (per Jimmy's amendments, 2026-11-05 13:17 + 13:18): every sequence starts AND ends on this exact drawing. In the delivered (registered) frame: bird in the left third facing right; feet at x = 11.5% (front) and 17.7% (rear) of frame width, waterline at y = 95% of frame height, small ripple rings at each foot; deep-S coil; the strike's touch point lands at x = 49.4% (frame center). Raw home drawing: poses/K_coil.png; registered: registered/K_coil.png.

## Deliverables
- strike_device_1024x600.mjpeg — 28 unique drawings, PIL JPEG q82, subsampling=1 (SOF luma byte verified 0x21 = true 4:2:2), 1,634,382 bytes (1.63 MB — under the 2.5 MB cap). Drawings at 1024x576 letterboxed into 1024x600 with the approved paper (12 px top/bottom) — no distortion.
- timing.json — 60 ticks @ 12 fps = 5.0 s. Phases: coil freeze t0-9; extension t10-15 (0.5 s); peak beat t15-16; withdrawal t17-42; settle t43-59, ending exactly on the home drawing.
- heron_strike_fresh_bird.mp4 / heron_strike_fresh_marsh.mp4 — 1280x720 previews @ 12 fps (marsh = multiply blend over the approved plate, preview only).
- proof_leg_band.png — bottom band of all 28 drawings in playback order: legs/feet in the same place in every row.
- proof_water_continuity.png — peak -> W_250 -> W_500 -> W_750 -> W_g7_3 -> K_coil: ripple born at contact, spreads, fades to ghost, gone at home.
- proof_marsh_strip.png — 8 ticks from the marsh preview.
- poses/ (raw drawings + rejected attempts), registered/ (normalized + registered finals), PLAN.md (rules + full production log).

## What the numbers say
- Unique drawings: 28 (not 60). The extension runs a new drawing per tick (6 ticks). The withdrawal runs 21 drawings over 43 ticks (on 2s) — because the edit model provably cannot place the head at fine intermediate heights on this path (see failures). Total storage is therefore 1.63 MB, well under cap.
- Paper normalized on every frame to the APPROVED drawing's measured paper (244, 242, 238). Composition finished by ONE uniform transform applied identically to all 28 drawings (scale 0.88, shift -3% x / +11% y, feathered onto their own paper): no frame was individually reframed, and no pixel surgery touched any bird.

## Failures and substitutions (plain)
- E_375 and E_625: FAILED under both the halfway method and absolute-landmark prompts (neighbor clones / off-path dip). Not used. The extension runs on the verified grid {E_125, E_250, E_500, E_750, E_875} with accelerating spacing (0.125/0.25/0.5/0.75/0.875/1.0) — physically right for a strike.
- Withdrawal eighths (W_125/375/625/875): all four missed their nominal fractions (head-height snap) but each is a clean, honest pose at a measured fraction (~0.25/0.55/0.74/0.78) with correct water for that fraction; used under those honest fractions. W_250 sits at ~f0.25-0.30 (coordinator retry replaced the worker's ~f0.40 version; the worker's is kept as W_250_alt.png and is itself used in the chain at its honest place ~0.40).
- Peak-exit gap (peak -> first risen pose): no intermediate could be produced by any of three methods (the model reads bill-in/bill-out as binary). The cut steps peak -> W_125 in one tick — the head exits the water fast, as in life.
- G6 gap (W_625 -> W_875): no intermediate (two failed attempts, opposite overshoots). Absorbed as a 2-tick hold.
- Settle: the chained steps were conservative; two extra coordinator steps (W_g7_5, W_g7_6) were added. The final step onto the home drawing is a small visible settle, not an invisible cut.
- E_500's head rides ~8% right of the true coil->peak midpoint (noted in the prior canonical work as well); W_250's bill carries a slight gape (just left the water).
- Composition nit: the tail tip sits at the frame's left edge in the registered framing.
- Rejected during key production: a mirrored coil, peaks with the touch at 66%/86% width, a peak with webbed duck-like feet, an E_750 that was a peak clone. All kept in poses/ for the record.
