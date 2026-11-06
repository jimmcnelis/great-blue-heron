# MEASUREMENTS — frames60 (accumulates per batch; targets from POSE_TABLE.md)

bird_sat: mean HSV saturation, luminance < 210, measured on the RAW 2048×1152
drawing. Home raw (K_coil_color_redo) ≈ 46.9; gate: ≥ 42.9 and never
paler/bluer than home on view. Tips in 0–1000 normalized coords.

## Batch 1 — t00–t04 (freeze) · GATE 1: 3 of 5 frames, 2 GAPs
| t | target tip | measured tip | Δ from target | bird_sat | attempts | status |
|---|---|---|---|---|---|---|
| 00 | (472,848) | file copy | — | — | — | HOME (locked file) |
| 01 | (472,848) | best (456,803) | 47.8 | 52.0 (best att.) | 6 | **GAP** |
| 02 | (472,848) | (478,836) | 13.4 | 55.9 | 5 | ESCALATED-PASS |
| 03 | (472,848) | (459,830) — coordinator re-measure (460,829) ✓ | 22.2 | 51.5 | 2 | PASS |
| 04 | (472,848) | best (438,776) | 79.6 | 48.6 (best att.) | 6 | **GAP** |

Diagnosis (worker-found, coordinator-confirmed): POSE TABLE targets are in
RAW scale (raw t00 measures (473,850) ✓), but home_frame_approval.png — the
attachment on every call — is the REGISTERED frame (its own tip measures
(403,854) in its frame). Generations anchor to the attached frame's scale and
cluster at tip x≈404, ~68 units left of target; landmark wording sometimes
breaks the anchor (t02/t03) but swings unpredictably (x 388–597 over 24
attempts). Proposed fix for the gap redo + all later batches: attach
K_coil_color_redo.png (raw artwork) as the primary scale/placement anchor,
home_frame_approval.png retained as color/identity authority.
Registered feet: t00 detector [15.24%] (front; target 15.2 ± 0.8 ✓); detector
returns None on t02/t03 (faint-ring limit, as in the redraw) — stance
view-verified on the batch sheet against home.
