# FRAMES60 WORKER BRIEF — read fully before generating anything

Spec: /home/hatch/workspace/heron/gate1-strike/fresh/frames60/POSE_TABLE.md
(your tick rows: tip targets, pose sentences, water states, Δ steps).
Production runs in batches of 5 ticks. You draw ONLY your assigned batch.

## Files
- HOME (attach to EVERY call):
  /home/hatch/workspace/heron/gate1-strike/fresh/home_frame_approval.png
- HOME raw artwork (edit canvas where your brief names it):
  /home/hatch/workspace/heron/gate1-strike/fresh/K_coil_color_redo.png
- Species photo: /home/hatch/workspace/heron/gate1-strike/corrected/prof_d.png
- Approved style drawing:
  /home/hatch/workspace/heron/gate1-strike/corrected/heron_pencil_verified_20261105-1201.png
- Pose photos: /home/hatch/workspace/heron/gate1-strike/corrected/ref_coil.png
  (coil/tuck/settle), ref_peak.png (extension/peak)
- Verified frames from earlier batches live in
  /home/hatch/workspace/heron/gate1-strike/fresh/frames60/raw/ (tNN.png) —
  these are THIS build's drawings and are legal edit canvases / references.
- Your raw output: /home/hatch/workspace/heron/gate1-strike/fresh/frames60/raw/tNN.png
- Your results file:
  /home/hatch/workspace/heron/gate1-strike/fresh/frames60/work/<BATCH>_results.md

## BANNED INPUTS
Never attach or edit ANY file from fresh/poses/, fresh/registered/,
fresh/registered_v2/, or fresh/redraw/ (v1/v2/redraw chains — geometry comes
from the POSE TABLE only). Legal inputs: the home files, corrected/
references, and frames60/raw/ verified frames.

## Generation mechanics (media.generate_image)
Load the media namespace first if needed (tool_search.load_tool_namespace).
- output_format "png", output_dir
  "/home/hatch/workspace/heron/gate1-strike/fresh/frames60/work/gen",
  name = the tick name (e.g. "t01"). The tool returns ~2096x1184; afterwards
  resize the returned file to EXACTLY 2048x1152 (PIL LANCZOS) and save as
  frames60/raw/tNN.png. Measure gates on THAT file.
- KEY (full drawing) call images, in order: home_frame_approval.png,
  prof_d.png, heron_pencil_verified_20261105-1201.png, the pose photo
  (ref_peak or ref_coil).
- BREAKDOWN (edit) call images, in order: the canvas (nearest verified key
  or verified same-chain neighbour), the far neighbour (target reference),
  home_frame_approval.png.
- One call per attempt. Never batch multiple poses into one call.

## Prompt shape
Start from this base and add your pose sentence + landmark sentence:
"Hand-drawn pencil and watercolor study of a great blue heron on warm off-white
paper, matching the FIRST attached image (the home frame) exactly in color and
identity: slate-blue body and neck, warm orange dagger bill, yellow ringed eye,
black brow sweeping into two long black plumes, streaked neck front with a
shaggy filament chest frill, layered slate wing with ONE black shoulder patch,
rusty-brown bend-of-wing and thighs, long scaly grey legs. The bird stands in
the left third of a wide 16:9 frame facing right, whole bird inside the frame
with margin on all sides, legs in the home stance - front foot at about 16.5%
of the frame width, rear foot at about 23%, feet at the waterline about 96.5%
down the frame, small ripple rings at each foot. Blank paper background: no
scenery, no plants, no text, no watermark."
Edit calls prepend: "Edit the FIRST attached image: move the heron's pose
toward the SECOND attached image, stopping at the fraction described. Change
ONLY the neck and head (and the water rings as described). Keep the body, wing,
chest frill, legs, feet, feet rings, framing, paper and the full color register
line-for-line identical to the first image."
Landmark sentence (every call): "The bill tip ends at about <X>% of the frame
width and <Y>% of the frame height." (X = tip_x/10, Y = tip_y/10 from the
POSE TABLE.)
Then the pose sentence + water state from your POSE TABLE rows.

## Gates per drawing (measure, then record)
1. VIEW the PNG (muse.read). Fail on sight: pale/grey wash vs home's color,
   frill cut or missing, legs moved/different stance, bird cropped, scenery,
   text, wrong water state, bill shape wrong, extra birds/limbs.
2. TIP: muse.visual_grounding, format_type "point", object "the tip of the
   heron's bill". It returns 0-1000 coords — compare with the POSE TABLE
   target: keys within ~25 units; breakdowns must ALSO pass the anti-clone
   gate vs neighbours' measured tips (strictly between, ≥15% of interval)
   except the table's starred rows (freeze / peak beat / tuck hold /
   micro-settle), where the tip coincides BY SPEC — there, the drawing must
   still be a genuinely independent rendering (view-check line work differs;
   never submit a copy or a trivially-shifted clone).
3. COLOR: run this and record bird_sat (FAIL if < 42.9):
   python3 -c "import numpy as np; from PIL import Image; im=Image.open('<FILE>').convert('RGB'); hsv=np.asarray(im.convert('HSV')).astype(float); lum=np.asarray(im.convert('L')).astype(float); print('bird_sat', hsv[...,1][lum<210].mean())"
   (Home raw ≈ 46.9. Never paler/bluer than home; never fix color in post.)

## Attempts and escalation (MANDATORY — from the order)
- Breakdown: up to 2 edit attempts. Still failing → escalate to fresh FULL
  drawings (key-style call + both neighbours' tip landmarks in the prompt).
- Key: up to 2 attempts, then fresh full drawings with adjusted landmark
  emphasis.
- Up to 6 TOTAL attempts per slot. A slot still failing at 6: STOP on that
  slot, record it as GAP with all measurements, move to the next tick.
  NEVER absorb a failed slot as a hold or copy a neighbour into its place.

## Results file
Per tick: status (PASS / ESCALATED-PASS / GAP), attempts used, measured tip
(x,y), bird_sat, one-line view verdict. End with a summary line. Be honest —
a reported GAP is useful; a silent bad drawing is not.
