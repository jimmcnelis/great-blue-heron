"""Stride preview: schedule + dx ramp, composited over the plate at device
size. Ends on the flipped home layer (the settle state)."""
import numpy as np
from PIL import Image
import os, sys
sys.path.insert(0, 'sequences/flight')
from flight_composite import plate as plate2048

BASE = 'sequences/stride'
P = np.asarray(Image.fromarray(plate2048().astype(np.uint8)).resize((1024, 600))).astype(np.float32)

def layer(name):
    a = np.asarray(Image.open(f'{BASE}/registered/{name}.png').convert('RGB').resize((1024, 600))).astype(np.float32)
    return a

LAY = {n: layer(n) for n in ['d1_halfrise','d2_carriage','wa_swing','wb_pass','wc_swing',
                             't1_turn','t2_frontal','t3_turn','t4_left','t5_sink']}
HOME = np.asarray(Image.open('seq2-layers/rest_layer.png').convert('RGB').resize((1024, 600))).astype(np.float32)
HOME_F = HOME[:, ::-1, :].copy()

TRAVEL = 672  # device px (canvas 1344)
STEP = TRAVEL / 5.0

def frame(pose, dx, flip_home=False):
    if flip_home:
        lay = HOME_F
        out = lay * P / 255.0
        return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
    lay = LAY[pose]
    if dx:
        shifted = np.full_like(lay, 244.0)  # FLAT approx (244,233,215) per channel below
        shifted[:] = (244, 233, 215)
        if dx < lay.shape[1]:
            shifted[:, dx:, :] = lay[:, :lay.shape[1]-dx, :]
        lay = shifted
    out = lay * P / 255.0
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))

frames = []
def add(pose, n, dx, flip_home=False):
    for _ in range(n):
        frames.append(frame(pose, round(dx), flip_home))

# departure
add('d2_carriage', 0, 0)  # placeholder no-op
frames = []
HOME_DEV = HOME
def add_home(n, dx=0):
    for _ in range(n):
        out = HOME_DEV * P / 255.0
        frames.append(Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)))
add_home(6)
add('d1_halfrise', 6, 0)
add('d2_carriage', 6, 0)
# walk: 5 steps; dx in device px
dx = 0.0
swings = ['wa_swing', 'wc_swing', 'wa_swing', 'wc_swing', 'wa_swing']
for s in range(5):
    base = dx
    # swing phase 7t: dx += 30%
    for t in range(7):
        frames.append(frame(swings[s], round(base + STEP*0.30*(t+1)/7)))
    # pass phase 5t: dx += 70%
    for t in range(5):
        frames.append(frame('wb_pass', round(base + STEP*0.30 + STEP*0.70*(t+1)/5)))
    dx += STEP
    if s == 1:
        for t in range(6):  # hunting freeze
            frames.append(frame('d2_carriage', round(dx)))
# turn at far side
for pose, n in [('t1_turn', 5), ('t2_frontal', 6), ('t3_turn', 5), ('t4_left', 5)]:
    add(pose, n, TRAVEL)
# settle
add('t5_sink', 6, TRAVEL)
for _ in range(10):
    frames.append(frame(None, 0, flip_home=True))

print('frames:', len(frames), '=', len(frames)/12.0, 's')
small = [f.resize((640, 375)) for f in frames]
small[0].save(f'{BASE}/stride_preview_20261106.gif', save_all=True, append_images=small[1:], duration=83, loop=0)
print('gif saved')
