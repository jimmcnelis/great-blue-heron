# art2 keypoint annotation spec (routes 1 & 2 training data)

## Keypoint dict (JSON, coordinates in SOURCE image pixels)

Polygons (lists of [x,y]):
- `plume_poly` — REQUIRED (Jimmy, binding 2026-11-02 22:45): the shaggy
  breast-plume skirt traced as its OWN polygon — the hanging feather mass
  below the breast, around the upper legs. It becomes mask channel 7 and
  must NEVER be merged into torso_poly or the legs. Trace its outer edge
  where it visibly hangs; it may overlap the leg area — that is expected.
- `torso_poly` — torso outline loop, ~8-13 pts, tail -> back -> shoulder ->
  breast -> keel -> belly -> tail underside. Follow the TRUE anatomical
  body line: where the plume skirt hangs below the belly, the torso line
  runs along the body's own edge (tucked above/behind the skirt), NOT
  around the skirt's outer edge.
- `spine` — exactly 5 pts along the neck CENTERLINE, breast (base) -> head.
- `bill_poly` — head outline: skull loop + bill triangle merged as one
  polygon (trace skull around, out along the upper bill to the tip, back
  along the lower bill).
- `wing_poly` — folded: outline of the folded wing mass on the torso
  (front-top at the shoulder, back along the top, rear tip near the tail,
  bottom edge back to the breast-low). Flight frames: the raised wing
  outline, root -> wrist -> tip -> fingered trailing edge -> root.
- `tail_poly` — 3+ pts: tail tip, top base, bottom base.

Points ([x,y]):
- `head_c` — skull center. `bill_tip` — bill tip.
- `hip_n/knee_n/foot_n`, `hip_f/knee_f/foot_f` — leg joints. The "knee" is
  the visible backward-bending joint (intertarsal). Legs are THIN STICKS
  under the plume skirt (Jimmy's standing "legs too thick" defect is the
  plume blending in): place hip at the true hip where the bare leg leaves
  the body (under the skirt), knee/foot on the bare leg only. If the far
  leg is hidden, mirror the near leg and note it in the sample name
  suffix `_fm`.
- `_px_per_unit` — pixel size of one design unit in this source: bird
  standing height (foot -> crown) in px / 62 approx, or torso length
  (breast -> tail along the back) in px / 37. Estimate honestly per frame.
- `_neck_w` — 1.0 unless the neck is visibly extended thin (0.85) or
  compressed thick (1.1).

## Pose vector (JSON list of 12 floats, order fixed)

[coil, neck_w, head_pitch/60, body_tilt/40, yaw/180, bulge_pos, bulge_amp,
 flap/60, flap_tip/30, flight01, gape, plume_sway/3]

Estimate from the frame: coil = neck S depth (1 = deep resting coil,
0 = straight up); head_pitch/body_tilt in degrees by eye; yaw 0 profile,
0.5 three-quarter (store /180 => use raw degrees in slot 5? NO — slot 5 is
yaw/180, so profile=0.0, three-quarter=0.25, front=0.5); bulge 0 unless a
swallow frame; flap for flight frames by eye (negative = wing raised);
gape 0 unless bill open. These are proof-grade estimates — say so in your
route notes.

## Sample building

For each annotated frame: run rembg (isnet-general-use) on a crop around
the bird (crop = keypoint bbox x2) to get alpha, paste alpha back to full
frame size, then:

python3 build_sample.py --image FRAME --alpha ALPHA_PNG --kp KP.json \
    --pose POSE.json --out samples/NAME.npz

Flow propagation (optional, footage route): annotate seed frames every
~1.5-3 s, propagate keypoints to frames in between with OpenCV Farneback
flow sampled at each keypoint; drop propagated samples whose flow
confidence (forward-backward error) is poor. Name them `_prop`.

## Machines

- This VM (local exec): PIL/numpy present; make a venv for cv2/rembg:
  python3 -m venv ~/workspace/heron/art2/venv && pip install
  opencv-python-headless rembg onnxruntime scipy pillow numpy
- MacBook Pro (M1 Max): ssh -i /home/hatch/.ssh/id_ed25519 -o
  IdentitiesOnly=yes -o UserKnownHostsFile=/home/hatch/.ssh/known_hosts
  -o StrictHostKeyChecking=accept-new -o ProxyCommand="python3
  ~/workspace/bin/tailnet_connect.py %h %p" jimmcnelis@100.73.24.7
  Keep SSH commands SHORT; long jobs via nohup + poll. DO NOT disturb
  birdnet-go or the rimworld harness. Preferred host for TRAINING
  (PyTorch-MPS): python3 -m venv ~/heron-art2-venv; pip install torch
  (MPS build) numpy pillow. train_decoder.py auto-selects cuda; on the
  Pro patch DEV selection to mps if cuda absent (torch.backends.mps).
- Spark (fallback for training): ssh ... jim@100.87.138.20 (same options),
  venv ~/heron/venv (torch 2.15 cu132). GPU is busy with house inference —
  expect contention.
