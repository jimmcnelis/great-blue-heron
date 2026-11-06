"""Stride registration v2: one scale factor for all poses (drawn relative
heights preserved), carriage ink height = 800 canvas px (rise1 class),
ink bottoms on canvas y=1125, feet-band centroid on the home anchor x.
Outputs flat-canvas layers (2048x1152) in registered/."""
import numpy as np
from PIL import Image
import os, sys
sys.path.insert(0, os.path.expanduser('~/workspace/heron/sequences/flight'))
from flight_composite import measure_paper

BASE = os.path.expanduser('~/workspace/heron/sequences/stride')
OUT = f'{BASE}/registered'
os.makedirs(OUT, exist_ok=True)
FLAT = (244, 233, 215)
FEET_Y = 1125
TARGET_H_D2 = 800

def ink(img):
    a = np.asarray(img.convert('RGB'))
    paper = measure_paper(img.convert('RGB'))
    m = np.abs(a.astype(float) - paper).sum(axis=2) > 60
    ys, xs = np.nonzero(m)
    band = m[ys.max()-50:ys.max()+1, :]
    bxs = np.nonzero(band.any(axis=0))[0]
    return a, (xs.min(), xs.max(), ys.min(), ys.max()), (bxs.min(), bxs.max(), bxs.mean())

def normalize(img):
    a = np.asarray(img.convert('RGB')).astype(np.float32)
    paper = measure_paper(img.convert('RGB'))
    return np.clip(a / paper * np.array([246., 235., 219.]), 0, 255).astype(np.uint8)

# home anchor x: rise1 raw feet centroid -> canvas (48 + 0.8*x)
r1 = Image.open(os.path.expanduser('~/workspace/heron/sequences/listening/poses/rise1.png')).convert('RGB').resize((2048, 1152))
_, _, (_, _, r1_centroid) = ink(r1)
ANCHOR_X = 48 + 0.8 * r1_centroid
print(f'home anchor x = {ANCHOR_X:.0f} (rise1 feet centroid raw {r1_centroid:.0f})')

POSES = ['d1_halfrise', 'd2_carriage', 'wa_swing', 'wb_pass', 'wc_swing',
         't1_turn', 't2_frontal', 't3_turn', 't4_left', 't5_sink']
data = {}
for name in POSES:
    img = Image.open(f'{BASE}/poses/{name}.png')
    a, (x0, x1, y0, y1), (fx0, fx1, fcen) = ink(img)
    data[name] = (img, x0, x1, y0, y1, fcen)
    print(f'{name}: ink {x1-x0}x{y1-y0} feet centroid {fcen:.0f}')

scale = TARGET_H_D2 / (data['d2_carriage'][4] - data['d2_carriage'][3])
print(f'scale = {scale:.4f}')
for name in POSES:
    img, x0, x1, y0, y1, fcen = data[name]
    a = normalize(img)
    crop = Image.fromarray(a).crop((x0, y0, x1 + 1, y1 + 1))
    bird = crop.resize((round(crop.width * scale), round(crop.height * scale)), Image.LANCZOS)
    canvas = Image.new('RGB', (2048, 1152), FLAT)
    dx = round(ANCHOR_X - (fcen - x0) * scale)
    dy = FEET_Y - bird.height
    canvas.paste(bird, (dx, dy))
    canvas.save(f'{OUT}/{name}.png')
    print(f'{name}: placed dx={dx} dy={dy} size={bird.size}')
print('done ->', OUT)
