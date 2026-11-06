# EMID results — RK_EMID halfway-edit round (2026-11-05)

Method: HALFWAY EDIT per assignment (the method that produced the original
anchor in the previous build). Images in order on every call:
1. fresh/K_coil_color_redo.png (home raw artwork, edit canvas)
2. redraw/poses/RK_PEAK.png (now-VERIFIED peak)
3. fresh/home_frame_approval.png (color/identity authority)
Prompt: brief base + the assigned halfway text (neck half-unfolded from the
deep coil toward the full spear, head driven forward/down only halfway, bill
tip at about 64% width / 84% height, head rides right on the unfolding arc,
change ONLY neck and head, bill above water — no rings except at the feet,
no droplets). Attempt 2 added a hard-stop sentence: tip must NOT go beyond
65% width, keep a clear visible S in the neck.
Max 2 attempts used: 2. Every attempt resized to exactly 2048x1152 (LANCZOS)
in redraw/work/gen/ and gated on view + visual-grounding bill tip + bird_sat.
Color gate as amended in CHAIN_SPEC.md: FAIL only if bird_sat < 42.9 or a
blue/grey shift on view.

Target: RK_EMID (KEY, t12), tip (643,840). Install tolerance ~25 units.

## Attempt 1 — FAILED (tip overshoot)
- Files: work/gen/media-generation-rk-emid-hw-a1-0-d19a336c-6904-417d-a3be-d74a686e7709.png
  resized to work/gen/RK_EMID_hw_a1_2048.png
- Measured tip: (727,869) — dx +84, dy +29 (Euclidean 88.9). FAIL.
- bird_sat: 50.09 — PASS (no blue/grey shift on view).
- View: clean otherwise — full home color register, chest frill intact,
  legs/feet in home stance, ripple rings at feet only, no rings/droplets
  under the bill, bill closed, and a visible S/hump remains in the neck
  (NOT a straight spear). The halfway edit again ran the reach too far
  right (~73% width), though less extremely than the earlier EXIT-edit
  spears at x~722-724 and with the S preserved.

## Attempt 2 — FAILED (tip, marginal: x 2 units outside tolerance)
- Files: work/gen/media-generation-rk-emid-hw-a2-0-99994c61-b7a8-4515-9847-e90492461a8b.png
  resized to work/gen/RK_EMID_hw_a2_2048.png
- Measured tip: (670,858) — dx +27, dy +18 (Euclidean 32.4). x is 2 units
  outside the ~25 tolerance; y is inside. FAIL on tip, narrowly.
- bird_sat: 49.58 — PASS (no blue/grey shift on view).
- View: PASS — clean halfway pose: a deep, clearly visible S remains in
  the neck (dip then rise into the head), NOT a straight spear and NOT
  near-peak; head driven forward and down on the unfolding arc; full home
  color register, chest frill intact, legs/feet in home stance, ripple
  rings at the feet only, bill above the water, no droplets, no scenery,
  no text, whole bird in frame.

## Install
NOT installed. Neither attempt was a full pass, so redraw/poses/RK_EMID.png
was NOT overwritten — it remains the failed KEYFIX file (unchanged,
md5 809ff1589d64e3d3166e94a995bbac82).

## Summary
**RK_EMID FAILED after 2 halfway-edit attempts; nothing installed.**
Attempt 2 is by far the closest EMID produced in any round: correct pose
(visible S, halfway arc), color and view fully clean, tip (670,858) vs
target (643,840) — only the x axis misses, by 2 units past the ~25
tolerance. The candidate is retained at
redraw/work/gen/RK_EMID_hw_a2_2048.png if the coordinator chooses to
adjudicate the marginal tip; under the stated gate it is not a pass.
