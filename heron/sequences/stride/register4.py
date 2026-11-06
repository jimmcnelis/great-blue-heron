"""Stride registration v4 (walk redo): register3 pipeline (paper-normalize,
fixed scale, ink bottoms at FEET_Y) but each pose is pasted so its ANCHOR
FOOT — measured by visual grounding on the raw drawing — lands at A_REF.
The schedule builder then supplies per-tick dx so a planted foot stays
world-pinned while the body passes over it (stride.md step_cycle / K6).
Anchors (raw px in the 1184-wide drawings, grounded 2026-11-06):
  far foot = left foot in the near-chain drawings (~398), etc. per POSES.
"""
import numpy as np
from PIL import Image
from scipy.ndimage import uniform_filter
import os, sys
sys.path.insert(0, os.path.expanduser('~/workspace/heron/sequences/flight'))
from flight_composite import measure_paper

BASE = os.path.expanduser('~/workspace/heron/sequences/stride')
OUT = f'{BASE}/registered2'
os.makedirs(OUT, exist_ok=True)
FLAT = (244, 233, 215)
FEET_Y = 1125
SCALE = 815.0 / 1775.0

def mass(img):
    a = np.asarray(img.convert('RGB')).astype(float)
    paper = measure_paper(img.convert('RGB'))
    d = np.abs(a - paper).sum(axis=2)
    return uniform_filter(d, size=31) > 25

# name -> (anchor foot raw x, A_REF canvas target)
POSES = {
    'd1_halfrise':     (398, 250),   # far foot
    'd2_carriage':     (398, 250),   # far foot
    'wa_swing':        (398, 250),   # far (planted)
    'adv_near':        (397, 250),   # far
    'plant_near':      (399, 250),   # far; near lands +159 canvas in layer
    'pass1_near':      (892, 420),   # near (planted); trailing far -333
    'pass2_near':      (462, 250),   # near
    'adv_far':         (462, 250),   # near (planted)
    'plant_far':       (461, 250),   # near; far lands +143 canvas in layer
    'pass1_far':       (914, 420),   # far (planted); trailing near -348
    'pass2_far':       (494, 250),   # far
    'plant_far_short': (465, 250),   # near; far lands +106 canvas in layer
}

for name, (fx, aref) in POSES.items():
    img = Image.open(f'{BASE}/poses/{name}.png')
    m = mass(img)
    ys, xs = np.nonzero(m)
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    a = np.asarray(img.convert('RGB')).astype(np.float32)
    paper = measure_paper(img.convert('RGB'))
    a = np.clip(a / paper * np.array([246., 235., 219.]), 0, 255).astype(np.uint8)
    crop = Image.fromarray(a).crop((max(0, x0 - 6), max(0, y0 - 6),
                                    min(a.shape[1], x1 + 7), min(a.shape[0], y1 + 1)))
    bird = crop.resize((round(crop.width * SCALE), round(crop.height * SCALE)),
                       Image.LANCZOS)
    dx = round(aref - (fx - max(0, x0 - 6)) * SCALE)
    dy = FEET_Y - round((y1 + 1 - max(0, y0 - 6)) * SCALE)
    canvas = Image.new('RGB', (2048, 1152), FLAT)
    canvas.paste(bird, (dx, dy))
    canvas.save(f'{OUT}/{name}.png')
    print(f'{name}: anchor raw {fx} -> {aref}; placed dx={dx} dy={dy}')

# turn poses: reuse the register3 layers unchanged
for name in ('t1_turn', 't2_frontal', 't3_turn', 't4_left', 't5_sink'):
    Image.open(f'{BASE}/registered/{name}.png').save(f'{OUT}/{name}.png')
print('turn layers copied; done')
