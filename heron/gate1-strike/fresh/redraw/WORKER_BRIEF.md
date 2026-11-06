# REDRAW WORKER BRIEF — read fully before generating anything

Spec: /home/hatch/workspace/heron/gate1-strike/fresh/redraw/CHAIN_SPEC.md (your
pose table, tip targets, water states, gates). This brief = method + mechanics.

## Files
- HOME (attach to EVERY call): /home/hatch/workspace/heron/gate1-strike/fresh/home_frame_approval.png
- HOME raw artwork (edit canvas for RX_1 only): /home/hatch/workspace/heron/gate1-strike/fresh/K_coil_color_redo.png
- Species photo: /home/hatch/workspace/heron/gate1-strike/corrected/prof_d.png
- Approved style drawing: /home/hatch/workspace/heron/gate1-strike/corrected/heron_pencil_verified_20261105-1201.png
- Pose photos: /home/hatch/workspace/heron/gate1-strike/corrected/ref_coil.png (coil/tuck/settle), ref_peak.png (extension/peak)
- Your output dir: /home/hatch/workspace/heron/gate1-strike/fresh/redraw/poses/
- Your results file: /home/hatch/workspace/heron/gate1-strike/fresh/redraw/work/<SEGMENT>_results.md

## BANNED INPUTS
Never attach or edit ANY file from fresh/poses/, fresh/registered/,
fresh/registered_v2/ (the v1/v2 chain). Only: the home files above, corrected/
references, and THIS build's verified drawings in redraw/poses/.

## Generation mechanics (media.generate_image)
- output_format "png", output_dir "/home/hatch/workspace/heron/gate1-strike/fresh/redraw/work/gen",
  name = pose name (lowercase ok). The tool returns ~2096x1184; afterwards run
  python to resize the returned file to EXACTLY 2048x1152 (LANCZOS) and save as
  redraw/poses/<NAME>.png. Measure gates on THAT file.
- KEY (full drawing) call images, in order: home_frame_approval.png, prof_d.png,
  heron_pencil_verified_20261105-1201.png, the pose photo (ref_peak or ref_coil).
- BREAKDOWN (edit) call images, in order: the canvas (nearest verified key or,
  one step deep, a verified breakdown), the far neighbour (target reference),
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
width and <Y>% of the frame height." (X = tip_x/10, Y = tip_y/10 from the spec.)
Then the pose sentence from your assignment (neck shape, head direction, water
state for the pose's fraction).

## Gates per drawing (measure, then record)
1. VIEW the PNG (muse.read). Fail on sight: pale/grey wash vs home's color,
   frill cut or missing, legs moved/different stance, bird cropped, scenery,
   text, wrong water state, bill shape wrong, extra birds/limbs.
2. TIP: muse.visual_grounding, format_type "point", object "the tip of the
   heron's bill". It returns 0-1000 coords on the image - compare with target:
   keys within ~25 units; breakdowns must ALSO pass the anti-clone gate vs
   their neighbours' measured tips (strictly between, >=15% of interval).
3. COLOR: run this and record bird_sat (FAIL if < 42.9):
   python3 -c "import numpy as np; from PIL import Image; im=Image.open('<FILE>').convert('RGB'); hsv=np.asarray(im.convert('HSV')).astype(float); lum=np.asarray(im.convert('L')).astype(float); print('bird_sat', hsv[...,1][lum<210].mean())"
4. Two attempts per pose max. Breakdown failing twice -> ONE escalation attempt
   as a fresh full drawing (key-style call + both neighbours' tip landmarks),
   labelled ESCALATED. Key failing twice -> record FAILED with measurements
   and move on; do not grind.

## Results file
Per pose: status, attempts used, measured tip (x,y), bird_sat, one-line view
verdict. End with a summary line of what passed. Be honest - a reported failure
is useful; a silent bad drawing is not.
