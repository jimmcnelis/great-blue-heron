"""Stride registration v3: smoothed-mass ink bbox, ONE scale for all poses
(carriage ink height 815 canvas px, rise1 class), ink bottoms at canvas
y=1125, shin centroid on the home anchor x. Flat-canvas layers out."""
import numpy as np
from PIL import Image
from scipy.ndimage import uniform_filter
import os, sys
sys.path.insert(0, os.path.expanduser('~/workspace/heron/sequences/flight'))
from flight_composite import measure_paper

BASE = os.path.expanduser('~/workspace/heron/sequences/stride')
OUT = f'{BASE}/registered'
os.makedirs(OUT, exist_ok=True)
FLAT = (244, 233, 215)
FEET_Y = 1125
TARGET_H = 815.0
REF_H = 1775.0  # d2 measured ink height
SCALE = TARGET_H / REF_H  # fallback only

def mass(img):
    a = np.asarray(img.convert('RGB')).astype(float)
    paper = measure_paper(img.convert('RGB'))
    d = np.abs(a - paper).sum(axis=2)
    s = uniform_filter(d, size=31)
    return s > 25

def measure(img):
    m = mass(img)
    ys, xs = np.nonzero(m)
    y1 = ys.max()
    shin = m[max(0, y1-300):y1-60, :]
    sxs = np.nonzero(shin.any(axis=0))[0]
    # weight shin centroid by column ink counts
    counts = shin.sum(axis=0)
    cen = (np.arange(shin.shape[1]) * counts).sum() / max(counts.sum(), 1)
    return xs.min(), xs.max(), ys.min(), y1, cen

def norm_arr(img):
    a = np.asarray(img.convert('RGB')).astype(np.float32)
    paper = measure_paper(img.convert('RGB'))
    return np.clip(a / paper * np.array([246., 235., 219.]), 0, 255).astype(np.uint8)

# home anchor from rise1 (native raw 2096x1184; pipeline: resize to 2048x1152
# (x*0.977), scale 0.80, offset +48) -> canvas_x = 48 + cen*0.977*0.80
r1 = Image.open(os.path.expanduser('~/workspace/heron/sequences/listening/poses/rise1.png'))
_, _, _, _, r1cen = measure(r1)
ANCHOR_X = 48 + r1cen * 0.977 * 0.80
print(f'rise1 shin centroid raw {r1cen:.0f} -> home anchor x {ANCHOR_X:.0f}; SCALE={SCALE:.4f}')

POSES = ['d1_halfrise', 'd2_carriage', 'wa_swing', 'wb_pass', 'wc_swing',
         't1_turn', 't2_frontal', 't3_turn', 't4_left', 't5_sink']
for name in POSES:
    img = Image.open(f'{BASE}/poses/{name}.png')
    x0, x1, y0, y1, cen = measure(img)
    a = norm_arr(img)
    crop = Image.fromarray(a).crop((max(0, x0-6), max(0, y0-6), min(a.shape[1], x1+7), min(a.shape[0], y1+1)))
    sc = SCALE
    bird = crop.resize((round(crop.width * sc), round(crop.height * sc)), Image.LANCZOS)
    canvas = Image.new('RGB', (2048, 1152), FLAT)
    dx = round(ANCHOR_X - (cen - max(0, x0-6)) * sc)
    dy = FEET_Y - round((y1 + 1 - max(0, y0-6)) * sc)
    canvas.paste(bird, (dx, dy))
    canvas.save(f'{OUT}/{name}.png')
    print(f'{name}: ink {x1-x0}x{y1-y0} cen={cen:.0f} -> placed dx={dx} dy={dy} h={bird.height}')
print('done')
