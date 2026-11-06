# Heron LINE LOOP — ESP32-P4-WIFI6-Touch-LCD-7B

A great blue heron drawn as **one continuous black line** on plate
paper (247,232,210), living on the board. No video, no image assets:
the firmware re-draws the line into an RGB565 framebuffer every frame
at 12 fps, so the whole show costs a few KB and storage is a non-issue
by construction.

Jimmy's spec (2026-11-04): "a single line to draw the bird, more or
less" — one outline from tail, over the back, up the neck, around the
head and bill, down the throat, along the breast and belly, with the
legs as down-and-back excursions of the same line. The only lift is a
tiny eye curl. No drawn water — only flat black ripple rings at her
feet when she strikes, steps, takes off or lands, expanding and fading.

## Behaviors (the designed living loop)

Shuffle-bag, exactly the living-loop scheduler's rules: preen ×3,
stride ×3, strike ×2, stretch ×2, miss ×2, flight ×1, courtship ×1 per
bag, reshuffled with an anti-repeat guard; idle holds of 20–90 s
between behaviors. Every behavior starts and ends at the home stance.

- **idle** — breathing sway, stillness first
- **preen** — head back over the back, nibbling tremor
- **stride** — stalk right with head stabilized, a long freeze, cautious retreat home
- **strike** — coil → aim → 0.18 s unfold to the water, ripples, withdraw
- **miss** — a shorter stab beside the mark, a head-shake, slow scan back
- **stretch** — wing and same-side leg sweep back, neck long and level
- **flight** — crouch, takeoff, a scaled-down circuit (0.62× = she flies
  up and away), turn, return leg with a glide, turn, flare, land at home
- **courtship** — rise on straight legs, bill snapped skyward, slow sway

## Rig (one bird, one anchor — positions cannot jump)

- Home anchor measured from the approved alert plate: hip origin
  (328,335), feet (343,546) front / (307,546) rear, bird faces right.
- Pose = interpolated keyframes of `hl_params` (hip offset, body pitch,
  facing, 5-point neck control polygon, head pitch, neck width, wing
  state, feet, scale). The neck keeps its full length; strikes UNFOLD
  it (coil → spear) rather than lengthening it — the kink in the
  lower-middle neck is the hinge, per the rig v2.5 work.
- Legs: ankle at 49% of the leg, slight backward bow that grows as the
  leg compresses; feet are planted world positions in stance behaviors.
- Wingbeat: 2.85 Hz takeoff/climb, 2.7 Hz cruise, 1.7 Hz landing flare,
  piecewise-integrated phase (no snap at rate changes).

## Layout

- `main/heron_line.c/.h` — pose math, outline builder, scheduler,
  rasterizer. Plain C, no allocation, no platform calls.
- `main/main.c` — the proven Stage A display path (BSP 1.0.4 +
  esp_lvgl_port/LVGL 9.3.0, image descriptor presented under the
  display lock, RGB565). The board sits rotated 180° in its case and
  reads upright as configured — no rotation/mirror flags.
- `host/` — host proof renderer linking the SAME `heron_line.c`:
  `host_heron still <behavior> <t> <out.ppm>`,
  `host_heron loopstream`, `host_heron sched <seed> <seconds>`.
- Partitions: 4 MB factory app, nothing else needed — no assets.

## Timing

TRUE timing by default. For a bench demo, build with
`-DHL_PROOF_SPEED=1` (or define it in `main/main.c`): idle holds
compress to 2–5 s; behaviors still play at authored speed.

## Build & flash (on the Studio)

1. `scp -r -i ~/.ssh/id_ed25519_mordecai -o IdentitiesOnly=yes jim@<spark-lan-ip>:~/heron-line-loop ~/heron-line-loop`
   (also copy `managed_components/` and `dependencies.lock` from
   `~/heron-living-loop` if present — that preserves the BSP patch)
2. `cd ~/heron-line-loop`
3. `. ~/esp-idf55/export.sh` then `idf.py build`
4. `idf.py -p /dev/cu.usbmodem83401 flash monitor`
