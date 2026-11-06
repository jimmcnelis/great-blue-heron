"""Stride v3 preview: same poses/table as v2, but dx RAMPS across each
pass + the next step's fold (chart: body_pass is distributed) instead of
stepping at pose boundaries. v2's dx steps were up to +85 device px in a
single tick (pass1->pass2) = the lurch Jimmy saw as jerky on device.
Ramp windows: near steps 7 ticks, far steps 8, closing step 9.
Per-tick dx (canvas) is linear inside a window, constant elsewhere.
"""
import numpy as np
from PIL import Image
import os, sys
sys.path.insert(0, os.path.expanduser('~/workspace/heron/sequences/flight'))
from flight_composite import plate as plate2048

BASE = os.path.expanduser('~/workspace/heron/sequences/stride')
HB = os.path.expanduser('~/workspace/heron')
P = np.asarray(Image.fromarray(plate2048().astype(np.uint8)).resize((1024, 600))).astype(np.float32)
NAMES = ['d1_halfrise', 'd2_carriage', 'wa_swing', 'adv_near', 'plant_near',
         'pass1_near', 'pass2_near', 'adv_far', 'plant_far', 'pass1_far',
         'pass2_far', 'plant_far_short',
         't1_turn', 't2_frontal', 't3_turn', 't4_left', 't5_sink']
LAY = {n: np.asarray(Image.open(f'{BASE}/registered2/{n}.png').convert('RGB')
       .resize((1024, 600))).astype(np.float32) for n in NAMES}
HOME = np.asarray(Image.open(f'{HB}/seq2-layers/rest_layer.png').convert('RGB')
                  .resize((1024, 600))).astype(np.float32)
HOME_F = HOME[:, ::-1, :].copy()

# segments: (pose, ticks, mode, target)  mode H=hold current dx, R=ramp toward
# target across this segment (ramps chain across consecutive R segments)
SEGS = [
    ('d1_halfrise', 6, 'H', 61), ('d2_carriage', 6, 'H', 61),
    # S1 near (ramp window: pass 5 + 2 into adv_far)
    ('wa_swing', 3, 'H', 61), ('adv_near', 4, 'H', 61), ('plant_near', 3, 'H', 61),
    ('pass1_near', 3, 'R', 214), ('pass2_near', 2, 'R', 214), ('adv_far', 2, 'R', 214),
    # S2 far (window: pass 5 + 3 into the freeze hold)
    ('adv_far', 2, 'H', 214), ('plant_far', 3, 'H', 214),
    ('pass1_far', 3, 'R', 351), ('pass2_far', 2, 'R', 351), ('pass2_far', 3, 'R', 351),
    ('pass2_far', 3, 'H', 351),
    # S3 near
    ('pass2_far', 3, 'H', 351), ('adv_near', 4, 'H', 351), ('plant_near', 3, 'H', 351),
    ('pass1_near', 3, 'R', 504), ('pass2_near', 2, 'R', 504), ('adv_far', 2, 'R', 504),
    # S4 far
    ('adv_far', 2, 'H', 504), ('plant_far', 3, 'H', 504),
    ('pass1_far', 3, 'R', 642), ('pass2_far', 2, 'R', 642),
    # S5 near
    ('pass2_far', 3, 'R', 642), ('adv_near', 4, 'H', 642), ('plant_near', 3, 'H', 642),
    ('pass1_near', 3, 'R', 795), ('pass2_near', 2, 'R', 795), ('adv_far', 2, 'R', 795),
    # S6 far
    ('adv_far', 2, 'H', 795), ('plant_far', 3, 'H', 795),
    ('pass1_far', 3, 'R', 932), ('pass2_far', 2, 'R', 932),
    # S7 near
    ('pass2_far', 3, 'R', 932), ('adv_near', 4, 'H', 932), ('plant_near', 3, 'H', 932),
    ('pass1_near', 3, 'R', 1085), ('pass2_near', 2, 'R', 1085), ('adv_far', 2, 'R', 1085),
    # S8 far
    ('adv_far', 2, 'H', 1085), ('plant_far', 3, 'H', 1085),
    ('pass1_far', 3, 'R', 1223), ('pass2_far', 2, 'R', 1223),
    # S9 near (no pass; fold + swing + arrival plant)
    ('pass2_far', 3, 'R', 1223), ('adv_near', 4, 'H', 1223), ('plant_near', 3, 'H', 1223),
    # closing far step (ramp over fold + advance + plant)
    ('pass2_near', 2, 'R', 1382), ('adv_far', 4, 'R', 1382), ('plant_far_short', 3, 'R', 1382),
    # turn + sink
    ('t1_turn', 5, 'H', 1341), ('t2_frontal', 6, 'H', 1341), ('t3_turn', 5, 'H', 1341),
    ('t4_left', 5, 'H', 1341), ('t5_sink', 6, 'H', 1341),
]

# expand to per-tick dx: find ramp chains (consecutive R segments with the
# same target), interpolate linearly from the dx at chain start to target.
ticks = []  # (pose, dx_canvas_float)
cur = 61.0
i = 0
while i < len(SEGS):
    pose, n, mode, target = SEGS[i]
    if mode == 'H':
        for _ in range(n):
            ticks.append((pose, float(target)))
        cur = float(target)
        i += 1
    else:
        chain = []
        total = 0
        j = i
        while j < len(SEGS) and SEGS[j][2] == 'R' and SEGS[j][3] == target:
            chain.append(SEGS[j])
            total += SEGS[j][1]
            j += 1
        start = cur
        k = 0
        for (p2, n2, _, _) in chain:
            for _ in range(n2):
                k += 1
                ticks.append((p2, start + (target - start) * k / total))
        cur = float(target)
        i = j
print('ticks:', len(ticks), '=', len(ticks) / 12.0, 's')

def frame(pose, dxc):
    lay = LAY[pose]
    dx = round(dxc / 2)
    if dx:
        sh = np.empty_like(lay)
        sh[:] = (244, 233, 215)
        if dx < 1024:
            sh[:, dx:, :] = lay[:, :1024 - dx, :]
        lay = sh
    return Image.fromarray(np.clip(lay * P / 255.0, 0, 255).astype(np.uint8))

frames = [frame(p, d) for p, d in ticks]
for _ in range(10):
    frames.append(Image.fromarray(np.clip(HOME_F * P / 255.0, 0, 255).astype(np.uint8)))
small = [f.resize((640, 375)) for f in frames]
small[0].save(f'{BASE}/stride3_preview_20261106.gif', save_all=True,
              append_images=small[1:], duration=83, loop=0)
print('gif saved')
# strip every 6th
sf = frames[::6]
cols = 6
rows = (len(sf) + cols - 1) // cols
strip = Image.new('RGB', (cols * 340, rows * 199), 'white')
for k, f in enumerate(sf):
    strip.paste(f.resize((340, 199)), ((k % cols) * 340, (k // cols) * 199))
strip.save('/tmp/stride3_strip.png')
print('strip saved')
# dump per-tick table for the firmware .inc generator
with open(f'{BASE}/stride3_ticks.csv', 'w') as f:
    for p, d in ticks:
        f.write(f'{p},{d:.2f}\n')
print('ticks csv saved')
