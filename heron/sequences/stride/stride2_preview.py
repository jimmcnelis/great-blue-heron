"""Stride REDO preview: foot-pinned chart-mechanics schedule.
Layers from registered2/ (foot-anchored). dx in CANVAS px in the table;
device dx = canvas/2. Planted feet stay world-pinned: dx changes only at
pass boundaries, by reach*k (k=0.960; per-pass pin error ~3 device px).
Ends on the flipped home layer (settle), like the v1 preview.
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
LAY = {}
for n in NAMES:
    LAY[n] = np.asarray(Image.open(f'{BASE}/registered2/{n}.png').convert('RGB')
                        .resize((1024, 600))).astype(np.float32)
HOME = np.asarray(Image.open(f'{HB}/seq2-layers/rest_layer.png').convert('RGB')
                  .resize((1024, 600))).astype(np.float32)
HOME_F = HOME[:, ::-1, :].copy()

# (pose, ticks, dx_canvas)
TABLE = [
    ('d1_halfrise', 6, 61), ('d2_carriage', 6, 61),
    # S1 near
    ('wa_swing', 3, 61), ('adv_near', 4, 61), ('plant_near', 3, 61),
    ('pass1_near', 3, 44), ('pass2_near', 2, 214),
    # S2 far
    ('adv_far', 4, 214), ('plant_far', 3, 214),
    ('pass1_far', 3, 181), ('pass2_far', 2, 351), ('pass2_far', 6, 351),
    # S3 near (fold = pass2_far held)
    ('pass2_far', 3, 351), ('adv_near', 4, 351), ('plant_near', 3, 351),
    ('pass1_near', 3, 334), ('pass2_near', 2, 504),
    # S4 far
    ('adv_far', 4, 504), ('plant_far', 3, 504),
    ('pass1_far', 3, 472), ('pass2_far', 2, 642),
    # S5 near
    ('pass2_far', 3, 642), ('adv_near', 4, 642), ('plant_near', 3, 642),
    ('pass1_near', 3, 625), ('pass2_near', 2, 795),
    # S6 far
    ('adv_far', 4, 795), ('plant_far', 3, 795),
    ('pass1_far', 3, 762), ('pass2_far', 2, 932),
    # S7 near
    ('pass2_far', 3, 932), ('adv_near', 4, 932), ('plant_near', 3, 932),
    ('pass1_near', 3, 915), ('pass2_near', 2, 1085),
    # S8 far
    ('adv_far', 4, 1085), ('plant_far', 3, 1085),
    ('pass1_far', 3, 1053), ('pass2_far', 2, 1223),
    # S9 near (no pass — arrival plant)
    ('pass2_far', 3, 1223), ('adv_near', 4, 1223), ('plant_near', 3, 1223),
    # closing far step (near foot pinned)
    ('pass2_near', 2, 1382), ('adv_far', 4, 1382), ('plant_far_short', 3, 1382),
    # turn + sink at far side (turn layers carry their own registration)
    ('t1_turn', 5, 1341), ('t2_frontal', 6, 1341), ('t3_turn', 5, 1341),
    ('t4_left', 5, 1341), ('t5_sink', 6, 1341),
]

def frame(pose, dx_dev):
    lay = LAY[pose]
    if dx_dev:
        shifted = np.empty_like(lay)
        shifted[:] = (244, 233, 215)
        if dx_dev < 1024:
            shifted[:, dx_dev:, :] = lay[:, :1024 - dx_dev, :]
        lay = shifted
    out = lay * P / 255.0
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))

frames = []
ticks = []
for pose, n, dxc in TABLE:
    for _ in range(n):
        frames.append(frame(pose, round(dxc / 2)))
        ticks.append((pose, dxc))
for _ in range(10):
    out = HOME_F * P / 255.0
    frames.append(Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)))
    ticks.append(('HOME_FLIPPED', 0))

print('ticks:', len(ticks) - 10, '=', (len(ticks) - 10) / 12.0, 's (+10 settle frames)')
small = [f.resize((640, 375)) for f in frames]
small[0].save(f'{BASE}/stride2_preview_20261106.gif', save_all=True,
              append_images=small[1:], duration=83, loop=0)
print('gif saved')

# filmstrip: every 6th frame
strip_frames = frames[::6]
cols = 6
rows = (len(strip_frames) + cols - 1) // cols
tw, th = 340, 199
strip = Image.new('RGB', (cols * tw, rows * th), 'white')
for i, f in enumerate(strip_frames):
    strip.paste(f.resize((tw, th)), ((i % cols) * tw, (i // cols) * th))
strip.save('/tmp/stride2_strip.png')
print('strip saved', strip.size, len(strip_frames), 'tiles')
