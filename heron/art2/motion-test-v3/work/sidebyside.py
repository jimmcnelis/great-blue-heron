#!/usr/bin/env python3
"""Side-by-side sheets for motion test v3: model output vs the
registered gold target vs the original (unregistered) gold frame,
for the hold and the strike's key beats. Also a blend of model vs
registered gold for the extension frame."""
import os
import numpy as np
from PIL import Image, ImageDraw

ROOT = os.path.expanduser('~/workspace/heron/art2')
V3 = f'{ROOT}/motion-test-v3'
FM3 = f'{ROOT}/finished-art-stills/finish-model-v3'
FM = f'{ROOT}/finished-art-stills/finish-model'
WIN = os.sys.argv[1] if len(os.sys.argv) > 1 else 'ema'
OUT = f'{V3}/sidebyside'
os.makedirs(OUT, exist_ok=True)

def load(p):
    return Image.open(p).convert('RGB')

def sheet(imgs, labels, path, scale=0.5):
    w = int(1024 * scale); h = int(600 * scale)
    S = Image.new('RGB', (w * len(imgs), h + 26), 'white')
    d = ImageDraw.Draw(S)
    for i, (im, lab) in enumerate(zip(imgs, labels)):
        S.paste(im.resize((w, h), Image.LANCZOS), (i * w, 26))
        d.text((i * w + 8, 6), lab, fill='black')
    S.save(path)
    print('wrote', path)

hold_model = load(f'{V3}/frames/hold/hold_frame.png')
hold_reg = load(f'{FM3}/corpus/target/idle_f0030.png')
hold_orig = load(f'{ROOT}/finished-art-stills/audubon_rest.png')
sheet([hold_model, hold_reg, hold_orig],
      ['MODEL v3 hold', 'APPROVED still (registered to rig)', 'APPROVED still (original)'],
      f'{OUT}/hold_compare.png')

for i, beat in ((0, 'standing'), (12, 'coil'), (25, 'release'), (27, 'extension'),
                (34, 'withdrawal'), (45, 'recover')):
    m = load(f'{V3}/frames/strike_{WIN}/f{i:04d}.png')
    g = load(f'{FM3}/corpus/target/strike_f{i:04d}.png')
    o = load(f'{FM}/corpus/target/strike_f{i:04d}.png')
    sheet([m, g, o], [f'MODEL v3 f{i:02d} {beat}', 'gold (registered)', 'gold (original)'],
          f'{OUT}/strike_f{i:04d}_{beat}.png')

# blend: model vs registered gold at extension
m = np.asarray(load(f'{V3}/frames/strike_{WIN}/f0027.png'), dtype=np.float32)
g = np.asarray(load(f'{FM3}/corpus/target/strike_f0027.png'), dtype=np.float32)
Image.fromarray((0.5 * m + 0.5 * g).astype(np.uint8)).save(f'{OUT}/strike_f0027_blend.png')
print('wrote blend')
